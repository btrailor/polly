"""
Compression module for extending conversation context retention.

This module provides compression utilities that reduce token usage by 50-100x
while preserving semantic meaning.

Phase 11c: Basic compression (50x)
Phase 23: Advanced compression (100x) with embeddings

New in Wave 1:
- LLMLingua strategy for fast algorithmic compression (2x-10x)
- Strategy-based compression (auto, llmlingua, llm_summary)
- RAG context compression integration
"""

from .compressor import ConversationCompressor, CompressedConversation, CompressionStrategy
from .manager import CompressionManager

# Lazy import for LLMLingua (optional dependency)
try:
    from .llmlingua_strategy import LLMLinguaCompressor, CompressionResult
    __all__ = [
        "ConversationCompressor",
        "CompressedConversation",
        "CompressionManager",
        "CompressionStrategy",
        "LLMLinguaCompressor",
        "CompressionResult"
    ]
except ImportError:
    # LLMLingua not installed, only export base classes
    __all__ = [
        "ConversationCompressor",
        "CompressedConversation",
        "CompressionManager",
        "CompressionStrategy"
    ]
