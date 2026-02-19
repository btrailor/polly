"""
Token Counter Service for Polly.

Provides accurate token counting using tiktoken for cloud models
and character-based estimation for local/Ollama models.
Used by the budget allocator and all context contributors.
"""

import math
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Cache tokenizer instances per model family
_tokenizers: dict = {}
_tiktoken_available: Optional[bool] = None


def _check_tiktoken() -> bool:
    """Check if tiktoken is available (lazy, cached)."""
    global _tiktoken_available
    if _tiktoken_available is None:
        try:
            import tiktoken  # noqa: F401
            _tiktoken_available = True
        except ImportError:
            _tiktoken_available = False
            logger.info("tiktoken not installed — using character-based token estimation")
    return _tiktoken_available


def _model_to_encoding(model_id: str) -> Optional[str]:
    """
    Map a model ID to a tiktoken encoding name.

    Returns None for models that don't have tiktoken support
    (e.g., Ollama/local models), which triggers the fallback estimator.
    """
    model_lower = model_id.lower()

    # OpenAI models → cl100k_base (GPT-4, GPT-4o, GPT-3.5-turbo)
    if any(prefix in model_lower for prefix in ("gpt-4", "gpt-3.5", "gpt-3", "o1-", "o3-")):
        return "cl100k_base"

    # Anthropic Claude models → cl100k_base (approximate, within ~5%)
    if "claude" in model_lower:
        return "cl100k_base"

    # OpenAI models via GitHub Models (e.g., "openai/gpt-4o")
    if model_lower.startswith("openai/"):
        return "cl100k_base"

    # Anthropic via GitHub Models (e.g., "anthropic/claude-3.5-sonnet")
    if model_lower.startswith("anthropic/"):
        return "cl100k_base"

    # Local/Ollama models — no tiktoken support
    # Includes: llama*, mistral*, phi*, qwen*, gemma*, etc.
    return None


class TokenCounter:
    """
    Accurate token counting for budget allocation.

    Uses tiktoken for cloud models (OpenAI, Anthropic approximate),
    falls back to character-based estimation for Ollama models.
    """

    @staticmethod
    def count(text: str, model_id: str = "gpt-4") -> int:
        """
        Count tokens in text for the given model.

        Args:
            text: Input text
            model_id: Model identifier (e.g., "gpt-4", "claude-sonnet",
                      "llama3.2:latest")

        Returns:
            Token count (int)
        """
        if not text:
            return 0

        tokenizer = TokenCounter._get_tokenizer(model_id)
        if tokenizer is not None:
            try:
                return len(tokenizer.encode(text))
            except Exception as e:
                logger.debug(f"tiktoken encode failed for model {model_id}: {e}")
                return TokenCounter._estimate_tokens(text)

        return TokenCounter._estimate_tokens(text)

    @staticmethod
    def truncate(text: str, max_tokens: int, model_id: str = "gpt-4") -> str:
        """
        Truncate text to fit within max_tokens.
        Truncates at sentence boundaries when possible.

        Args:
            text: Input text
            max_tokens: Maximum allowed tokens
            model_id: Model identifier for accurate counting

        Returns:
            Truncated text (may be unchanged if already within budget)
        """
        if not text:
            return text

        current_tokens = TokenCounter.count(text, model_id)
        if current_tokens <= max_tokens:
            return text

        # Binary search for the right character position
        low, high = 0, len(text)
        best = 0

        while low <= high:
            mid = (low + high) // 2
            candidate = text[:mid]
            count = TokenCounter.count(candidate, model_id)

            if count <= max_tokens:
                best = mid
                low = mid + 1
            else:
                high = mid - 1

        truncated = text[:best]

        # Try to truncate at a natural boundary (sentence, newline, semicolon)
        # Look back from the truncation point for a clean break
        boundaries = [". ", "\n", "; ", ".\n", "? ", "! "]
        best_boundary = -1

        for boundary in boundaries:
            idx = truncated.rfind(boundary)
            if idx > best_boundary and idx > len(truncated) * 0.5:
                # Only use boundary if it's in the latter half of the text
                # (don't throw away most of the content for a clean break)
                best_boundary = idx + len(boundary)

        if best_boundary > 0:
            truncated = truncated[:best_boundary]

        return truncated

    @staticmethod
    def _get_tokenizer(model_id: str):
        """
        Get or create cached tokenizer for model family.

        Returns None if tiktoken is unavailable or model has no
        tiktoken mapping (triggers fallback estimator).
        """
        if not _check_tiktoken():
            return None

        encoding_name = _model_to_encoding(model_id)
        if encoding_name is None:
            return None

        if encoding_name not in _tokenizers:
            try:
                import tiktoken
                _tokenizers[encoding_name] = tiktoken.get_encoding(encoding_name)
                logger.debug(f"Cached tiktoken encoding '{encoding_name}' for model family")
            except Exception as e:
                logger.warning(f"Failed to load tiktoken encoding '{encoding_name}': {e}")
                return None

        return _tokenizers[encoding_name]

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Fallback estimation for models without tiktoken support.

        Uses len(text) / 3.5 (slightly more conservative than /4).
        This overestimates slightly, which is safer for budget allocation
        than underestimating.
        """
        return math.ceil(len(text) / 3.5)
