"""
LLMLingua compression strategy for RAG context compression.

Uses LLMLingua-2 for fast, algorithmic prompt compression without LLM calls.
Achieves 2x-10x token reduction while preserving semantic meaning.

Reference: https://arxiv.org/abs/2310.06201
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Result of compression operation"""
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    metadata: Dict[str, Any]


class LLMLinguaCompressor:
    """
    LLMLingua-2 compression for RAG context and prompts.
    
    Features:
    - Fast algorithmic compression (no LLM call needed)
    - 2x-10x token reduction
    - Configurable compression ratio
    - Lazy model loading (avoid startup cost)
    - CPU/CUDA support
    
    Usage:
        compressor = LLMLinguaCompressor(target_ratio=0.5)
        result = compressor.compress(text)
        print(f"Compressed {result.original_tokens} → {result.compressed_tokens} tokens")
    """
    
    def __init__(
        self,
        target_ratio: float = 0.5,
        model_name: str = "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
        device: str = "cpu"
    ):
        """
        Initialize LLMLingua compressor.
        
        Args:
            target_ratio: Target compression ratio (0.1-1.0)
                         0.5 = 2x compression, 0.1 = 10x compression
            model_name: HuggingFace model name for LLMLingua
            device: "cpu" or "cuda"
        """
        self.target_ratio = max(0.1, min(1.0, target_ratio))
        self.model_name = model_name
        self.device = device
        
        # Lazy loading - don't load model until first compress() call
        self._llm_lingua = None
        self._model_loaded = False
    
    def _load_model(self):
        """Lazy load LLMLingua model"""
        if self._model_loaded:
            return
        
        try:
            from llmlingua import PromptCompressor
            
            logger.info(f"Loading LLMLingua model: {self.model_name} on {self.device}")
            self._llm_lingua = PromptCompressor(
                model_name=self.model_name,
                device_map=self.device,
                use_llmlingua2=True  # Use LLMLingua-2 (better quality)
            )
            self._model_loaded = True
            logger.info("LLMLingua model loaded successfully")
            
        except ImportError:
            logger.error(
                "LLMLingua not installed. Run: pip install llmlingua\n"
                "Falling back to no compression."
            )
            self._model_loaded = False
        except Exception as e:
            logger.error(f"Failed to load LLMLingua model: {e}")
            self._model_loaded = False
    
    def compress(
        self,
        text: str,
        target_ratio: Optional[float] = None,
        context_type: str = "rag_context"
    ) -> CompressionResult:
        """
        Compress text using LLMLingua.
        
        Args:
            text: Text to compress
            target_ratio: Override default compression ratio
            context_type: Type of content ("rag_context", "prompt", "conversation")
        
        Returns:
            CompressionResult with compressed text and metrics
        """
        # Handle empty input
        if not text or not text.strip():
            return CompressionResult(
                compressed_text="",
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=1.0,
                metadata={"error": "empty_input"}
            )
        
        # Load model on first use
        self._load_model()
        
        # If model failed to load, return uncompressed
        if not self._model_loaded or self._llm_lingua is None:
            original_tokens = self._count_tokens(text)
            return CompressionResult(
                compressed_text=text,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                metadata={"error": "model_not_loaded", "fallback": True}
            )
        
        # Use provided ratio or default
        ratio = target_ratio if target_ratio is not None else self.target_ratio
        ratio = max(0.1, min(1.0, ratio))
        
        try:
            # Count original tokens
            original_tokens = self._count_tokens(text)
            
            # Compress using LLMLingua
            compressed_result = self._llm_lingua.compress_prompt(
                text,
                rate=ratio,  # Target compression rate
                force_tokens=[],  # No forced tokens
                drop_consecutive=True,  # Drop consecutive similar tokens
                use_context_level_filter=True,  # Context-aware filtering
                use_token_level_filter=True,  # Token-level filtering
                target_token=-1  # Use rate instead of target token count
            )
            
            compressed_text = compressed_result["compressed_prompt"]
            compressed_tokens = self._count_tokens(compressed_text)
            
            # Calculate actual compression ratio
            actual_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
            
            logger.debug(
                f"LLMLingua compressed {original_tokens} → {compressed_tokens} tokens "
                f"(target: {ratio:.2f}, actual: {actual_ratio:.2f})"
            )
            
            return CompressionResult(
                compressed_text=compressed_text,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                compression_ratio=actual_ratio,
                metadata={
                    "target_ratio": ratio,
                    "context_type": context_type,
                    "model": self.model_name,
                    "device": self.device
                }
            )
        
        except Exception as e:
            logger.error(f"LLMLingua compression failed: {e}")
            # Fallback: return uncompressed
            original_tokens = self._count_tokens(text)
            return CompressionResult(
                compressed_text=text,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                metadata={"error": str(e), "fallback": True}
            )
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count.
        
        Uses simple heuristic: 1 token ≈ 4 characters.
        For more accurate counting, could use tiktoken.
        """
        return len(text) // 4
    
    def is_available(self) -> bool:
        """Check if LLMLingua is available and loaded"""
        self._load_model()
        return self._model_loaded and self._llm_lingua is not None


def create_compressor(config: Dict[str, Any]) -> LLMLinguaCompressor:
    """
    Factory function to create LLMLingua compressor from config.
    
    Args:
        config: Configuration dict with llmlingua settings
    
    Returns:
        Configured LLMLinguaCompressor instance
    """
    llmlingua_config = config.get("llmlingua", {})
    
    return LLMLinguaCompressor(
        target_ratio=config.get("rag_context", {}).get("ratio", 0.5),
        model_name=llmlingua_config.get(
            "model",
            "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
        ),
        device=llmlingua_config.get("device", "cpu")
    )
