"""
Mem0 semantic storage backend for the Pattern Engine.

Provides semantic search over patterns via Mem0 adaptive memory.
Optional — only active when Mem0 is configured in user config.

Migrated from core/pattern_learning.py PatternLearner (Mem0 integration).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models import Pattern, PatternQuery, PatternType

logger = logging.getLogger(__name__)


class Mem0Backend:
    """
    Mem0-backed semantic pattern storage.

    Stores pattern descriptions as Mem0 memories with structured metadata.
    Provides semantic search that JSON backend cannot.
    Lazy-initializes Mem0 on first use.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Full application config dict with memory.mem0 settings.
        """
        self._config = config
        self._mem0 = None  # Lazy-loaded
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """Lazy-initialize Mem0. Returns True if available."""
        if self._initialized:
            return self._mem0 is not None

        self._initialized = True
        try:
            from core.memory.mem0_adapter import Mem0Adapter

            self._mem0 = Mem0Adapter(self._config)
            logger.info("Mem0Backend: Mem0 adapter initialized for pattern storage")
            return True
        except ImportError:
            logger.debug("Mem0Backend: mem0ai package not installed")
            return False
        except Exception as e:
            logger.warning(f"Mem0Backend: Failed to initialize Mem0: {e}")
            return False

    # ========== StorageBackend interface ==========

    def save(self, pattern: Pattern) -> None:
        """Save a pattern to Mem0 as a memory."""
        if not self._ensure_initialized():
            return

        try:
            content = f"Pattern [{pattern.pattern_type.value if isinstance(pattern.pattern_type, PatternType) else pattern.pattern_type}]: {pattern.description}"
            metadata = {
                "type": "pattern",
                "pattern_id": pattern.id,
                "pattern_type": pattern.pattern_type.value if isinstance(pattern.pattern_type, PatternType) else pattern.pattern_type,
                "confidence": pattern.confidence,
                "occurrences": pattern.occurrences,
                "domains": pattern.domains,
                "source": pattern.source,
            }
            # Merge selected metadata from pattern
            for key in ("model", "task", "persona", "mode"):
                if key in pattern.metadata:
                    metadata[key] = pattern.metadata[key]

            self._mem0.add_memory(
                content=content,
                user_id="patterns",
                metadata=metadata,
            )
        except Exception as e:
            logger.debug(f"Mem0Backend: Failed to save pattern (non-critical): {e}")

    def save_batch(self, patterns: List[Pattern]) -> None:
        """Save multiple patterns. Mem0 doesn't have batch API, so iterate."""
        for p in patterns:
            self.save(p)

    def load_all(self) -> Dict[str, Pattern]:
        """
        Mem0 doesn't support load-all efficiently.
        Returns empty — the JSON backend is the source of truth for full loads.
        """
        return {}

    def delete(self, pattern_id: str) -> bool:
        """Mem0 memory deletion by pattern_id is not directly supported. Returns False."""
        # Future: could search by pattern_id metadata and delete
        return False

    def search(self, query: PatternQuery) -> List[Pattern]:
        """
        Structured search. Mem0's strength is semantic search,
        so this delegates to search_semantic for text queries
        and returns [] for purely structured queries.
        """
        if query.text:
            return self.search_semantic(query.text, limit=query.limit)
        return []

    def search_semantic(self, text: str, limit: int = 10) -> List[Pattern]:
        """
        Semantic similarity search via Mem0.

        Returns Pattern objects constructed from Mem0 search results.
        No more anonymous duck-typed bridge class.
        """
        if not self._ensure_initialized():
            return []

        try:
            results = self._mem0.search_memory(
                query=text,
                user_id="patterns",
                limit=limit,
            )

            patterns: List[Pattern] = []
            for r in results:
                meta = r.get("metadata", {})

                # Parse pattern_type
                pt_str = meta.get("pattern_type", "query")
                try:
                    pattern_type = PatternType(pt_str)
                except ValueError:
                    pattern_type = PatternType.QUERY

                # Parse timestamp
                timestamp_str = meta.get("timestamp", "")
                try:
                    last_seen = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    ) if timestamp_str else datetime.now()
                except (ValueError, TypeError):
                    last_seen = datetime.now()

                # Extract description from memory content
                memory_text = r.get("memory", "")
                # Strip "Pattern [type]: " prefix if present
                description = memory_text
                if "]: " in description:
                    description = description.split("]: ", 1)[1]

                # Build domains list
                domains = meta.get("domains", [])
                if isinstance(domains, str):
                    domains = [domains]

                pattern = Pattern(
                    id=meta.get("pattern_id", f"mem0_{hash(memory_text) & 0xFFFFFFFF:08x}"),
                    pattern_type=pattern_type,
                    name=description[:60] + "..." if len(description) > 60 else description,
                    description=description,
                    confidence=float(meta.get("confidence", 0.5)),
                    occurrences=int(meta.get("occurrences", 1)),
                    first_seen=last_seen,
                    last_seen=last_seen,
                    domains=domains,
                    metadata={
                        k: v
                        for k, v in meta.items()
                        if k not in ("type", "pattern_id", "pattern_type", "confidence",
                                     "occurrences", "domains", "source", "timestamp")
                    },
                    source="mem0",
                )
                patterns.append(pattern)

            return patterns

        except Exception as e:
            logger.debug(f"Mem0Backend: Semantic search failed (non-critical): {e}")
            return []

    def flush(self) -> None:
        """Mem0 writes are immediate — nothing to flush."""
        pass
