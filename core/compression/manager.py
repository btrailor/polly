"""
Compression manager for conversation lifecycle management.

Handles when and how conversations are compressed, stored, and loaded.
Also provides strategy-based compression for RAG context and other use cases.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Literal, Callable, Tuple
import logging

from core.context.token_counter import TokenCounter
from .compressor import ConversationCompressor, CompressionStrategy

logger = logging.getLogger(__name__)


class CompressionManager:
    """
    Manage conversation compression lifecycle
    
    Responsibilities:
    - Determine when conversations should be compressed
    - Compress and store old messages
    - Load compressed context when needed
    - Manage compression database
    """
    
    # Compression thresholds
    COMPRESSION_THRESHOLD = 10  # Compress after 10 exchanges (20 messages)
    COMPRESSION_AGE_HOURS = 24  # Or after 24 hours
    KEEP_RECENT_COUNT = 10  # Keep last 10 messages uncompressed
    
    def __init__(self, db_path: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize compression manager
        
        Args:
            db_path: Path to SQLite database (default: ~/.polly/compression.db)
            config: Configuration dict for compression settings
        """
        if db_path is None:
            polly_dir = Path.home() / ".polly"
            polly_dir.mkdir(exist_ok=True)
            db_path = str(polly_dir / "compression.db")
        
        self.db_path = db_path
        self.config = config or {}
        self.compressor = ConversationCompressor(config=self.config.get("compression", {}))
        self._current_conversation_id: Optional[str] = None
        # SRS cache: (message_count_at_last_compute, srs_value)
        self._srs_cache: Optional[Tuple[int, float]] = None
        self._init_database()
    
    def _init_database(self):
        """Initialize compression database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create compression table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_compression (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    compressed_data TEXT NOT NULL,
                    original_tokens INTEGER,
                    compressed_tokens INTEGER,
                    compression_ratio REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(conversation_id)
                )
            """)
            
            # Create index for fast lookup
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_compression_conversation 
                ON conversation_compression(conversation_id)
            """)
            
            conn.commit()
            logger.info(f"Initialized compression database at {self.db_path}")
    
    def compute_srs(
        self,
        conversation_history: List[Dict],
        embed_fn: Callable[[str], List[float]],
        window_size: int = 6,
    ) -> float:
        """
        Compute Semantic Redundancy Score (SRS) for a conversation (Spec 04).

        Returns a float 0.0–1.0:
            0.0 = completely redundant (all messages cluster around centroid)
            1.0 = completely novel (high variance from centroid)

        Uses caching: recomputes only when message count changes.
        """
        message_count = len(conversation_history)

        # Return cached value if message count unchanged
        if self._srs_cache is not None and self._srs_cache[0] == message_count:
            return self._srs_cache[1]

        # Need at least 4 substantive messages
        texts = [
            msg["content"] for msg in conversation_history
            if msg.get("content") and len(msg["content"]) > 20
        ]
        if len(texts) < 4:
            srs = 1.0  # Too short — don't compress
            self._srs_cache = (message_count, srs)
            return srs

        try:
            import numpy as np

            embeddings = np.array([embed_fn(text) for text in texts])
            centroid = embeddings.mean(axis=0)
            centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)

            distances = []
            for emb in embeddings:
                emb_norm = emb / (np.linalg.norm(emb) + 1e-9)
                cosine_sim = float(np.dot(emb_norm, centroid_norm))
                cosine_dist = 1.0 - cosine_sim
                distances.append(cosine_dist)

            recent_distances = distances[-window_size:]
            srs = float(np.mean(recent_distances))
            self._srs_cache = (message_count, srs)

            compression_cfg = self.config.get("compression", {})
            if compression_cfg.get("semantic_trigger", {}).get("log_srs", False):
                logger.info(f"SRS={srs:.4f} ({len(texts)} messages, window={window_size})")
            else:
                logger.debug(f"SRS={srs:.4f} ({len(texts)} messages, window={window_size})")

            return srs

        except Exception as e:
            logger.warning(f"SRS computation failed: {e}")
            srs = 1.0  # Fail safe: don't compress
            self._srs_cache = (message_count, srs)
            return srs

    def should_compress(
        self,
        conversation_history: List[Dict],
        conversation_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        embed_fn: Optional[Callable] = None,
    ) -> bool:
        """
        Determine whether conversation should be compressed (Spec 04).

        Decision logic (in priority order):
        1. HARD MINIMUM: Never compress below min_messages (default 10).
        2. SEMANTIC TRIGGER (primary, if embed_fn provided):
           Compress if SRS < redundancy_threshold AND count >= min_for_semantic.
        3. STRUCTURAL FALLBACK (always active):
           Compress if count > hard_count_threshold OR age threshold met.
        """
        message_count = len(conversation_history)
        exchange_count = message_count // 2

        compression_cfg = self.config.get("compression", {})

        # 1. Hard minimum — never compress very short conversations
        min_messages = compression_cfg.get("min_messages", 10)
        if message_count < min_messages:
            return False

        # 2. Semantic trigger (primary path when embed_fn available)
        semantic_cfg = compression_cfg.get("semantic_trigger", {})
        if embed_fn is not None and semantic_cfg.get("enabled", True):
            min_for_semantic = semantic_cfg.get("min_messages", 12)
            if message_count >= min_for_semantic:
                try:
                    window_size = semantic_cfg.get("window_size", 6)
                    srs = self.compute_srs(conversation_history, embed_fn, window_size)
                    threshold = semantic_cfg.get("redundancy_threshold", 0.15)
                    if srs < threshold:
                        logger.info(
                            f"Semantic compression trigger: SRS={srs:.3f} "
                            f"< threshold={threshold:.3f} ({message_count} messages)"
                        )
                        return True
                    else:
                        logger.debug(
                            f"Semantic trigger not met: SRS={srs:.3f} "
                            f">= threshold={threshold:.3f}"
                        )
                except Exception as e:
                    logger.warning(f"Semantic trigger error: {e}. Falling back to structural.")

        # 3. Structural fallback — always active
        hard_threshold = compression_cfg.get("message_threshold", self.COMPRESSION_THRESHOLD)
        if exchange_count > hard_threshold * 2:
            logger.debug(
                f"Structural compression trigger: {exchange_count} exchanges "
                f"> hard threshold {hard_threshold * 2}"
            )
            return True

        if created_at:
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            age_threshold = compression_cfg.get("age_hours", self.COMPRESSION_AGE_HOURS)
            age_count = compression_cfg.get("age_count_threshold", self.COMPRESSION_THRESHOLD)
            if age_hours > age_threshold and exchange_count > age_count:
                logger.debug(
                    f"Age compression trigger: {age_hours:.1f}h > {age_threshold}h "
                    f"and {exchange_count} exchanges > {age_count}"
                )
                return True

        return False
    
    def compress_conversation(
        self,
        conversation_history: List[Dict],
        conversation_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Compress old messages in conversation
        
        Args:
            conversation_history: Full conversation history
            conversation_id: Unique conversation identifier
            metadata: Additional conversation metadata
        
        Returns:
            Dict with 'compressed' data and 'recent' uncompressed messages
        """
        # Keep recent messages uncompressed
        if len(conversation_history) <= self.KEEP_RECENT_COUNT:
            logger.info("Conversation too short to compress")
            return {
                'compressed': None,
                'recent': conversation_history
            }
        
        old_messages = conversation_history[:-self.KEEP_RECENT_COUNT]
        recent_messages = conversation_history[-self.KEEP_RECENT_COUNT:]
        
        # Compress old messages
        logger.info(f"Compressing {len(old_messages)} messages from conversation {conversation_id}")
        compressed = self.compressor.compress(old_messages, type="conversation", metadata=metadata)
        
        # Store in database
        self._store_compressed(conversation_id, compressed)
        
        logger.info(
            f"Compressed {compressed['token_stats']['original']} → "
            f"{compressed['token_stats']['compressed']} tokens "
            f"({compressed['token_stats']['ratio']:.1f}x compression)"
        )
        
        return {
            'compressed': compressed,
            'recent': recent_messages
        }
    
    # ContextContributor (integration-contracts): priority 10
    context_priority = 10

    def set_current_conversation(self, conversation_id: Optional[str]) -> None:
        """Set the conversation ID used by build_context for compressed summary."""
        self._current_conversation_id = conversation_id

    def build_context(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: object,
    ) -> str:
        """Build compressed conversation summary for system prompt (ContextContributor)."""
        cid = self._current_conversation_id or kwargs.get("conversation_id")
        if not cid:
            return ""
        compressed = self._get_compressed(cid)
        if not compressed:
            return ""
        try:
            summary = self.compressor.decompress(compressed)
            if not summary:
                return ""
            result = f"\n\n## Conversation Summary\n\n{summary}\n"
            if token_budget > 0 and TokenCounter.count(result) > token_budget:
                result = TokenCounter.truncate(result, token_budget)
            return result
        except Exception as e:
            logger.debug(f"Could not decompress for context: {e}")
            return ""

    def load_context(
        self,
        conversation_id: str,
        recent_messages: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Load conversation context with compression
        
        Args:
            conversation_id: Conversation identifier
            recent_messages: Recent uncompressed messages (optional)
        
        Returns:
            List of messages with compressed history as system message
        """
        messages = []
        
        # Load compressed version from database
        compressed = self._get_compressed(conversation_id)
        
        if compressed:
            # Decompress to natural language summary
            summary = self.compressor.decompress(compressed)
            
            # Add as system message
            messages.append({
                "role": "system",
                "content": f"Conversation history summary:\n\n{summary}",
                "compressed": True
            })
            
            logger.debug(f"Loaded compressed context for conversation {conversation_id}")
        
        # Add recent messages
        if recent_messages:
            messages.extend(recent_messages)
        
        return messages
    
    def _store_compressed(self, conversation_id: str, compressed: Dict):
        """Store compressed conversation in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO conversation_compression 
                (conversation_id, version, compressed_data, original_tokens, 
                 compressed_tokens, compression_ratio, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                compressed['version'],
                json.dumps(compressed),
                compressed['token_stats']['original'],
                compressed['token_stats']['compressed'],
                compressed['token_stats']['ratio'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def _get_compressed(self, conversation_id: str) -> Optional[Dict]:
        """Get compressed conversation from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT compressed_data FROM conversation_compression
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            
            return None
    
    def get_compression_stats(self, conversation_id: str) -> Optional[Dict]:
        """
        Get compression statistics for a conversation
        
        Returns:
            Dict with compression stats or None if not compressed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT original_tokens, compressed_tokens, compression_ratio, created_at
                FROM conversation_compression
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'original_tokens': row[0],
                    'compressed_tokens': row[1],
                    'compression_ratio': row[2],
                    'compressed_at': row[3]
                }
            
            return None
    
    def delete_compressed(self, conversation_id: str):
        """Delete compressed conversation from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM conversation_compression
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            conn.commit()
            logger.info(f"Deleted compressed conversation {conversation_id}")
    
    def list_all_compressed(self) -> List[Dict]:
        """
        List all compressed conversations
        
        Returns:
            List of dicts with conversation info
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id, original_tokens, compressed_tokens, 
                       compression_ratio, created_at
                FROM conversation_compression
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            
            return [
                {
                    'conversation_id': row[0],
                    'original_tokens': row[1],
                    'compressed_tokens': row[2],
                    'compression_ratio': row[3],
                    'compressed_at': row[4]
                }
                for row in rows
            ]
    
    def get_total_compression_savings(self) -> Dict:
        """
        Calculate total compression savings across all conversations
        
        Returns:
            Dict with total savings stats
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_conversations,
                    SUM(original_tokens) as total_original,
                    SUM(compressed_tokens) as total_compressed,
                    AVG(compression_ratio) as avg_ratio
                FROM conversation_compression
            """)
            
            row = cursor.fetchone()
            
            if row and row[0] > 0:
                total_original = row[1] or 0
                total_compressed = row[2] or 0
                tokens_saved = total_original - total_compressed
                
                return {
                    'total_conversations': row[0],
                    'total_original_tokens': total_original,
                    'total_compressed_tokens': total_compressed,
                    'tokens_saved': tokens_saved,
                'average_ratio': row[3] or 0,
                'percent_saved': (tokens_saved / total_original * 100) if total_original > 0 else 0
            }
        
        return {
            'total_conversations': 0,
            'total_original_tokens': 0,
            'total_compressed_tokens': 0,
            'tokens_saved': 0,
            'average_ratio': 0,
            'percent_saved': 0
        }
    
    # ========== Strategy-Based Compression (New) ==========
    
    def compress_text(
        self,
        text: str,
        strategy: Optional[CompressionStrategy] = None,
        target_ratio: float = 0.5,
        context_type: str = "rag_context"
    ) -> Dict:
        """
        Compress arbitrary text using specified strategy.
        
        This is the main entry point for RAG context compression.
        
        Args:
            text: Text to compress
            strategy: Compression strategy (None = use config default)
            target_ratio: Target compression ratio for LLMLingua
            context_type: Type of content
        
        Returns:
            Dict with compressed text and metrics
        """
        # Get strategy from config if not specified
        if strategy is None:
            compression_config = self.config.get("compression", {})
            strategy = compression_config.get("strategy", "auto")
        
        # Compress using strategy
        result = self.compressor.compress_with_strategy(
            text=text,
            strategy=strategy,
            target_ratio=target_ratio,
            context_type=context_type
        )
        
        logger.debug(
            f"Compressed {result['original_tokens']} → {result['compressed_tokens']} tokens "
            f"using {result.get('strategy', 'unknown')} strategy "
            f"({result['compression_ratio']:.2f}x ratio)"
        )
        
        return result
    
    def is_compression_enabled(self, context_type: str = "rag_context") -> bool:
        """
        Check if compression is enabled for given context type.
        
        Args:
            context_type: Type of content
        
        Returns:
            True if compression is enabled
        """
        compression_config = self.config.get("compression", {})
        
        if context_type == "rag_context":
            rag_config = compression_config.get("rag_context", {})
            return rag_config.get("enabled", False)
        elif context_type == "conversation":
            # Conversation compression is always available (existing feature)
            return True
        
        return False
    
    def get_compression_ratio(self, context_type: str = "rag_context") -> float:
        """
        Get configured compression ratio for context type.
        
        Args:
            context_type: Type of content
        
        Returns:
            Compression ratio (0.1-1.0)
        """
        compression_config = self.config.get("compression", {})
        
        if context_type == "rag_context":
            rag_config = compression_config.get("rag_context", {})
            return rag_config.get("ratio", 0.5)
        
        return 0.5  # Default
