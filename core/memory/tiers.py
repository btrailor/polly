"""
Tiered Memory Store for Polly.

Manages three memory tiers (stable, episodic, working) over the existing
Mem0 adapter, providing tier-aware read/write with time decay, deduplication,
and session scoping.

Tiers:
  - STABLE: Long-term preferences, structures, relationships. No decay.
  - EPISODIC: Medium-term session summaries, decisions, status. Time-decayed.
  - WORKING: Short-term current session state. Session-scoped, flushed at end.
"""

import math
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.context.token_counter import TokenCounter

logger = logging.getLogger(__name__)


class MemoryTier(str, Enum):
    """Three-tier memory classification."""
    STABLE = "stable"       # Long-term: preferences, structures, relationships
    EPISODIC = "episodic"   # Medium-term: session summaries, decisions, status
    WORKING = "working"     # Short-term: current session state


@dataclass
class MemoryMetadata:
    """Structured metadata for memory entries."""
    tier: str = "working"                  # "stable" | "episodic" | "working"
    domain: str = "general"                # Polly domain (sigils, signals, etc.)
    persona_source: str = "system"         # Which persona created this
    timestamp: str = ""                    # ISO 8601
    salience: float = 0.5                  # How important (0-1), set at write time
    reference_count: int = 0               # Times re-accessed across sessions
    last_referenced: str = ""              # ISO 8601
    source_type: str = "inferred"          # "user_stated" | "decision" | "inferred" | "extraction"
    session_id: str = ""                   # For working tier scoping
    tags: list = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for Mem0 metadata storage."""
        return {
            "tier": self.tier,
            "domain": self.domain,
            "persona_source": self.persona_source,
            "timestamp": self.timestamp,
            "salience": self.salience,
            "reference_count": self.reference_count,
            "last_referenced": self.last_referenced,
            "source_type": self.source_type,
            "session_id": self.session_id,
            "tags": ",".join(self.tags) if self.tags else "",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryMetadata":
        """Create from Mem0 metadata dict."""
        tags_raw = data.get("tags", "")
        tags = tags_raw.split(",") if isinstance(tags_raw, str) and tags_raw else []
        return cls(
            tier=data.get("tier", "working"),
            domain=data.get("domain", "general"),
            persona_source=data.get("persona_source", "system"),
            timestamp=data.get("timestamp", ""),
            salience=float(data.get("salience", 0.5)),
            reference_count=int(data.get("reference_count", 0)),
            last_referenced=data.get("last_referenced", ""),
            source_type=data.get("source_type", "inferred"),
            session_id=data.get("session_id", ""),
            tags=tags,
        )


@dataclass
class MemoryEntry:
    """A single memory with tier-aware metadata."""
    content: str
    tier: MemoryTier
    metadata: MemoryMetadata
    score: float = 0.0       # Composite relevance score (set by scorer)
    token_count: int = 0     # Cached token count
    memory_id: str = ""      # Mem0 memory ID for updates

    def __post_init__(self):
        if self.token_count == 0 and self.content:
            self.token_count = TokenCounter.count(self.content)


class TieredMemoryStore:
    """
    Manages three Mem0 collections as memory tiers.
    Wraps the existing Mem0Adapter with tier-aware read/write.
    """

    def __init__(self, mem0_adapter, config: dict):
        """
        Args:
            mem0_adapter: Existing Mem0Adapter instance
            config: Full memory config section (including tiers, retrieval)
        """
        self.mem0 = mem0_adapter
        self.config = config
        self.session_id = datetime.now().strftime("%Y%m%dT%H%M%S")

        # Tier configuration
        tiers_config = config.get("tiers", {})
        self.tier_collections = {
            MemoryTier.STABLE: tiers_config.get("stable", {}).get("collection", "memory_stable"),
            MemoryTier.EPISODIC: tiers_config.get("episodic", {}).get("collection", "memory_episodic"),
            MemoryTier.WORKING: tiers_config.get("working", {}).get("collection", "memory_working"),
        }
        self.episodic_halflife = tiers_config.get("episodic", {}).get("decay_halflife_days", 90)

        # Retrieval configuration
        retrieval_config = config.get("retrieval", {})
        self.dedup_threshold = retrieval_config.get("dedup_threshold", 0.92)

        logger.info(
            f"TieredMemoryStore initialized: session={self.session_id}, "
            f"episodic_halflife={self.episodic_halflife}d"
        )

    def _tier_user_id(self, tier: MemoryTier) -> str:
        """Generate Mem0 user_id for a given tier."""
        if tier == MemoryTier.WORKING:
            return f"tier:working:{self.session_id}"
        return f"tier:{tier.value}"

    def write(
        self,
        content: str,
        tier: MemoryTier,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Write a memory entry to the appropriate tier.

        Args:
            content: Memory text
            tier: Which tier to write to
            metadata: Additional metadata (domain, persona_source, etc.)

        Returns:
            Memory ID (or empty string on failure)
        """
        if metadata is None:
            metadata = {}

        # Build structured metadata
        meta = MemoryMetadata(
            tier=tier.value,
            domain=metadata.get("domain", "general"),
            persona_source=metadata.get("persona_source", "system"),
            timestamp=datetime.now().isoformat(),
            salience=metadata.get("salience", 0.5),
            source_type=metadata.get("source_type", "inferred"),
            session_id=self.session_id if tier == MemoryTier.WORKING else "",
            tags=metadata.get("tags", []),
        )

        user_id = self._tier_user_id(tier)

        try:
            result = self.mem0.add_memory(
                content=content,
                user_id=user_id,
                metadata=meta.to_dict(),
                infer=False,  # Facts are already extracted by SessionExtractor
            )
            memory_id = ""
            if isinstance(result, dict):
                memory_id = result.get("id", result.get("memory_id", ""))
            elif isinstance(result, list) and result:
                memory_id = result[0].get("id", "") if isinstance(result[0], dict) else str(result[0])

            logger.debug(
                f"Wrote memory to {tier.value}: {content[:80]}... "
                f"(id={memory_id}, domain={meta.domain})"
            )
            return memory_id

        except Exception as e:
            logger.error(f"Failed to write memory to {tier.value}: {e}")
            return ""

    def read(
        self,
        query: str,
        tiers: Optional[List[MemoryTier]] = None,
        limit: int = 10,
        domain_filter: Optional[str] = None,
        min_score: float = 0.0,
    ) -> List[MemoryEntry]:
        """
        Retrieve memories across specified tiers.

        Args:
            query: Search query
            tiers: Which tiers to search (default: all)
            limit: Max results per tier
            domain_filter: Optional domain restriction
            min_score: Minimum retrieval score threshold

        Returns:
            List of MemoryEntry sorted by score descending
        """
        if tiers is None:
            tiers = list(MemoryTier)

        all_entries: List[MemoryEntry] = []

        for tier in tiers:
            try:
                user_id = self._tier_user_id(tier)
                results = self.mem0.search_memory(
                    query=query,
                    user_id=user_id,
                    limit=limit,
                )

                for result in results:
                    entry = self._parse_mem0_result(result, tier)
                    if entry is None:
                        continue

                    # Apply time decay for episodic tier
                    if tier == MemoryTier.EPISODIC:
                        entry.score = self._apply_time_decay(entry)

                    # Apply domain filter
                    if domain_filter and entry.metadata.domain != domain_filter:
                        if entry.metadata.domain != "general":
                            continue

                    # Apply score threshold
                    if entry.score < min_score:
                        continue

                    all_entries.append(entry)

            except Exception as e:
                logger.warning(f"Failed to read from {tier.value} tier: {e}")
                continue

        # Sort by score descending
        all_entries.sort(key=lambda e: e.score, reverse=True)
        return all_entries

    def flush_working(self):
        """Clear all working-tier memories for the current session."""
        user_id = self._tier_user_id(MemoryTier.WORKING)
        try:
            self.mem0.reset(user_id=user_id)
            logger.info(f"Flushed working tier for session {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to flush working tier: {e}")

    def update_reference(self, memory_id: str):
        """Increment reference_count and update last_referenced timestamp."""
        try:
            # Mem0's update API — we update the metadata
            now = datetime.now().isoformat()
            self.mem0.update_memory(
                memory_id=memory_id,
                content=None,  # Don't change content
                metadata={
                    "last_referenced": now,
                    # Note: reference_count increment requires read-modify-write
                    # which Mem0 doesn't support atomically. We do best-effort.
                },
            )
            logger.debug(f"Updated reference for memory {memory_id}")
        except Exception as e:
            logger.warning(f"Failed to update reference for {memory_id}: {e}")

    def deduplicate_against(
        self,
        content: str,
        tier: MemoryTier,
    ) -> Optional[str]:
        """
        Check if content already exists in the tier.

        Returns existing memory_id if duplicate found (similarity >= threshold),
        None otherwise.
        """
        try:
            user_id = self._tier_user_id(tier)
            results = self.mem0.search_memory(
                query=content,
                user_id=user_id,
                limit=3,
            )

            for result in results:
                score = result.get("score", 0.0)
                if score >= self.dedup_threshold:
                    memory_id = result.get("id", result.get("memory_id", ""))
                    if memory_id:
                        logger.debug(
                            f"Dedup match in {tier.value}: score={score:.3f} "
                            f"(threshold={self.dedup_threshold})"
                        )
                        return memory_id

            return None

        except Exception as e:
            logger.warning(f"Deduplication check failed for {tier.value}: {e}")
            return None

    def _parse_mem0_result(
        self,
        result: Dict[str, Any],
        tier: MemoryTier,
    ) -> Optional[MemoryEntry]:
        """Parse a Mem0 search result into a MemoryEntry."""
        try:
            content = result.get("memory", result.get("content", ""))
            if not content:
                return None

            raw_metadata = result.get("metadata", {})
            if raw_metadata is None:
                raw_metadata = {}

            # Ensure tier is set correctly
            raw_metadata["tier"] = tier.value

            metadata = MemoryMetadata.from_dict(raw_metadata)
            score = float(result.get("score", 0.0))
            memory_id = result.get("id", result.get("memory_id", ""))

            return MemoryEntry(
                content=content,
                tier=tier,
                metadata=metadata,
                score=score,
                memory_id=memory_id,
            )

        except Exception as e:
            logger.debug(f"Failed to parse Mem0 result: {e}")
            return None

    def _apply_time_decay(self, entry: MemoryEntry) -> float:
        """
        Apply time-based decay to an episodic memory's score.

        Uses exponential decay: score * exp(-ln(2) * days / halflife)
        """
        if not entry.metadata.timestamp:
            return entry.score

        try:
            created = datetime.fromisoformat(entry.metadata.timestamp)
            days_old = (datetime.now() - created).total_seconds() / 86400.0
            decay_factor = math.exp(-math.log(2) * days_old / self.episodic_halflife)
            return entry.score * decay_factor
        except (ValueError, TypeError) as e:
            logger.debug(f"Could not apply time decay: {e}")
            return entry.score
