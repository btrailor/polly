"""
Semantic Cache — Query→Response caching with semantic similarity.

Provides fast response lookup for semantically equivalent queries,
reducing LLM costs and latency.
"""

from .semantic_cache import SemanticCache, CacheHit, CacheStats

__all__ = ["SemanticCache", "CacheHit", "CacheStats"]
