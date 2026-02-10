"""
Storage backend protocol for the Pattern Engine.

Defines the interface that all storage backends must implement.
The PatternEngine can use multiple backends simultaneously
(e.g., JSON for fast lookup + Mem0 for semantic search).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..models import Pattern, PatternQuery


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for pattern storage backends."""

    def save(self, pattern: "Pattern") -> None:
        """Save or update a single pattern."""
        ...

    def save_batch(self, patterns: List["Pattern"]) -> None:
        """Save multiple patterns efficiently."""
        ...

    def load_all(self) -> Dict[str, "Pattern"]:
        """Load all patterns into memory. Returns {id: Pattern}."""
        ...

    def delete(self, pattern_id: str) -> bool:
        """Delete a pattern by ID. Returns True if deleted."""
        ...

    def search(self, query: "PatternQuery") -> List["Pattern"]:
        """Search patterns by structured query criteria."""
        ...

    def search_semantic(self, text: str, limit: int = 10) -> List["Pattern"]:
        """
        Semantic similarity search.

        Backends without semantic support should return [].
        """
        ...

    def flush(self) -> None:
        """Flush any pending writes to persistent storage."""
        ...
