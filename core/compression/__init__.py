"""
Compression module for extending conversation context retention.

This module provides compression utilities that reduce token usage by 50-100x
while preserving semantic meaning.

Phase 11c: Basic compression (50x)
Phase 23: Advanced compression (100x) with embeddings
"""

from .compressor import ConversationCompressor, CompressedConversation
from .manager import CompressionManager

__all__ = ["ConversationCompressor", "CompressedConversation", "CompressionManager"]
