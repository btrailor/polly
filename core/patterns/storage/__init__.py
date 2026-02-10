"""
Pattern storage backends.

Provides pluggable storage for the PatternEngine:
- JSONBackend: Fast file-based storage with in-memory cache
- Mem0Backend: Semantic search via Mem0 adaptive memory
"""

from .base import StorageBackend
from .json_backend import JSONBackend
from .mem0_backend import Mem0Backend

__all__ = ["StorageBackend", "JSONBackend", "Mem0Backend"]
