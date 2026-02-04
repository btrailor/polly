"""
Compression manager for conversation lifecycle management.

Handles when and how conversations are compressed, stored, and loaded.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import logging

from .compressor import ConversationCompressor

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
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize compression manager
        
        Args:
            db_path: Path to SQLite database (default: ~/.polly/compression.db)
        """
        if db_path is None:
            polly_dir = Path.home() / ".polly"
            polly_dir.mkdir(exist_ok=True)
            db_path = str(polly_dir / "compression.db")
        
        self.db_path = db_path
        self.compressor = ConversationCompressor()
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
    
    def should_compress(
        self, 
        conversation_history: List[Dict],
        conversation_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> bool:
        """
        Check if conversation should be compressed
        
        Args:
            conversation_history: Current conversation messages
            conversation_id: Optional conversation ID
            created_at: Optional conversation start time
        
        Returns:
            True if conversation should be compressed
        """
        # Check message count
        message_count = len(conversation_history)
        exchange_count = message_count // 2  # Two messages per exchange
        
        if exchange_count > self.COMPRESSION_THRESHOLD * 2:
            logger.debug(
                f"Conversation has {exchange_count} exchanges "
                f"(threshold: {self.COMPRESSION_THRESHOLD})"
            )
            return True
        
        # Check age if created_at provided
        if created_at:
            age = datetime.now() - created_at
            age_hours = age.total_seconds() / 3600
            
            if (age_hours > self.COMPRESSION_AGE_HOURS and 
                exchange_count > self.COMPRESSION_THRESHOLD):
                logger.debug(
                    f"Conversation is {age_hours:.1f} hours old "
                    f"(threshold: {self.COMPRESSION_AGE_HOURS})"
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
        compressed = self.compressor.compress(old_messages, metadata)
        
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
