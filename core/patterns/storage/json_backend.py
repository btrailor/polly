"""
JSON file storage backend for the Pattern Engine.

Provides fast in-memory pattern storage backed by a JSON file.
This is the primary storage backend — always active.

Migrated from learners/patterns.py PatternLearner._load_patterns / .save_patterns
and core/pattern_learning.py PatternLearner._load_patterns / ._save_patterns.
"""

from __future__ import annotations

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import (
    DomainPriorityPattern,
    Pattern,
    PatternQuery,
    PatternType,
    QueryChunkPattern,
)

logger = logging.getLogger(__name__)


class JSONBackend:
    """
    JSON file storage with in-memory cache.

    All reads come from the in-memory cache (populated at init).
    Writes are buffered and flushed to disk on explicit flush() or save().
    Atomic writes via temp-file-then-rename to prevent corruption.
    """

    def __init__(self, json_path: Path):
        self.json_path = Path(json_path).expanduser()
        self.json_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory caches
        self._patterns: Dict[str, Pattern] = {}
        self._query_chunk_patterns: Dict[str, QueryChunkPattern] = {}
        self._domain_priority_patterns: Dict[str, DomainPriorityPattern] = {}
        self._query_history: List[Dict[str, Any]] = []
        self._dirty = False

        # Load existing data
        self._load()

    # ========== StorageBackend interface ==========

    def save(self, pattern: Pattern) -> None:
        """Save or update a single pattern in the cache."""
        self._patterns[pattern.id] = pattern
        self._dirty = True

    def save_batch(self, patterns: List[Pattern]) -> None:
        """Save multiple patterns."""
        for p in patterns:
            self._patterns[p.id] = p
        self._dirty = True

    def load_all(self) -> Dict[str, Pattern]:
        """Return all patterns from cache."""
        return dict(self._patterns)

    def delete(self, pattern_id: str) -> bool:
        """Delete a pattern by ID."""
        if pattern_id in self._patterns:
            del self._patterns[pattern_id]
            self._dirty = True
            return True
        return False

    def search(self, query: PatternQuery) -> List[Pattern]:
        """Search patterns by structured query criteria."""
        results: List[Pattern] = []

        for pattern in self._patterns.values():
            # Filter by pattern types
            if query.pattern_types:
                pt = pattern.pattern_type
                if isinstance(pt, str):
                    try:
                        pt = PatternType(pt)
                    except ValueError:
                        continue
                if pt not in query.pattern_types:
                    continue

            # Filter by domains
            if query.domains:
                if not pattern.domains or not set(pattern.domains) & set(query.domains):
                    continue

            # Filter by minimum confidence
            if pattern.confidence < query.min_confidence:
                if not query.include_decayed:
                    continue

            # Text matching (keyword-based — semantic search is Mem0Backend's job)
            if query.text:
                text_lower = query.text.lower()
                searchable = f"{pattern.name} {pattern.description}".lower()
                keywords_match = any(
                    word in searchable for word in text_lower.split()
                )
                if not keywords_match:
                    continue

            results.append(pattern)

        # Sort by confidence desc, then occurrences desc
        results.sort(key=lambda p: (p.confidence, p.occurrences), reverse=True)
        return results[: query.limit]

    def search_semantic(self, text: str, limit: int = 10) -> List[Pattern]:
        """JSON backend does not support semantic search — returns []."""
        return []

    def flush(self) -> None:
        """Write all cached data to disk."""
        if not self._dirty and self.json_path.exists():
            return
        self._save()
        self._dirty = False

    # ========== Specialized pattern accessors ==========

    @property
    def query_chunk_patterns(self) -> Dict[str, QueryChunkPattern]:
        return self._query_chunk_patterns

    @property
    def domain_priority_patterns(self) -> Dict[str, DomainPriorityPattern]:
        return self._domain_priority_patterns

    @property
    def query_history(self) -> List[Dict[str, Any]]:
        return self._query_history

    def save_query_chunk_pattern(self, pattern: QueryChunkPattern) -> None:
        self._query_chunk_patterns[pattern.pattern_id] = pattern
        self._dirty = True

    def save_domain_priority_pattern(self, pattern: DomainPriorityPattern) -> None:
        self._domain_priority_patterns[pattern.pattern_id] = pattern
        self._dirty = True

    def append_query_history(self, entry: Dict[str, Any]) -> None:
        self._query_history.append(entry)
        # Keep bounded
        if len(self._query_history) > 1000:
            self._query_history = self._query_history[-1000:]
        self._dirty = True

    # ========== Internal I/O ==========

    def _load(self) -> None:
        """Load all data from JSON file into memory."""
        if not self.json_path.exists():
            logger.info(f"No existing pattern file at {self.json_path} — starting fresh")
            return

        try:
            raw = json.loads(self.json_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to read patterns file: {e}")
            return

        # Load unified patterns
        for p_data in raw.get("patterns", []):
            try:
                pattern = Pattern.from_dict(p_data)
                self._patterns[pattern.id] = pattern
            except Exception as e:
                logger.warning(f"Skipping malformed pattern: {e}")

        # Load query→chunk patterns
        for qcp_data in raw.get("query_chunk_patterns", []):
            try:
                qcp = QueryChunkPattern.from_dict(qcp_data)
                self._query_chunk_patterns[qcp.pattern_id] = qcp
            except Exception as e:
                logger.warning(f"Skipping malformed query_chunk_pattern: {e}")

        # Load domain priority patterns
        for dpp_data in raw.get("domain_priority_patterns", []):
            try:
                dpp = DomainPriorityPattern.from_dict(dpp_data)
                self._domain_priority_patterns[dpp.pattern_id] = dpp
            except Exception as e:
                logger.warning(f"Skipping malformed domain_priority_pattern: {e}")

        # Load query history
        self._query_history = raw.get("query_history", [])[-1000:]

        logger.info(
            f"Loaded patterns from {self.json_path}: "
            f"{len(self._patterns)} patterns, "
            f"{len(self._query_chunk_patterns)} query→chunk, "
            f"{len(self._domain_priority_patterns)} domain priority"
        )

    def _save(self) -> None:
        """Write all cached data to disk atomically."""
        data = {
            "patterns": [p.to_dict() for p in self._patterns.values()],
            "query_chunk_patterns": [
                qcp.to_dict() for qcp in self._query_chunk_patterns.values()
            ],
            "domain_priority_patterns": [
                dpp.to_dict() for dpp in self._domain_priority_patterns.values()
            ],
            "query_history": self._query_history[-1000:],
            "metadata": {
                "version": "3.0",  # Unified engine version
                "saved_at": datetime.now().isoformat(),
                "counts": {
                    "patterns": len(self._patterns),
                    "query_chunk_patterns": len(self._query_chunk_patterns),
                    "domain_priority_patterns": len(self._domain_priority_patterns),
                },
            },
        }

        # Atomic write: write to temp file, then rename
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            tmp_fd = tempfile.NamedTemporaryFile(
                mode="w",
                dir=self.json_path.parent,
                suffix=".tmp",
                delete=False,
            )
            json.dump(data, tmp_fd, indent=2)
            tmp_fd.close()
            Path(tmp_fd.name).replace(self.json_path)
            logger.debug(f"Saved {len(self._patterns)} patterns to {self.json_path}")
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
            # Try to clean up temp file
            try:
                Path(tmp_fd.name).unlink(missing_ok=True)
            except Exception:
                pass
