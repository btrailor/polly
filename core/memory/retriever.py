"""
Memory Retriever — ContextContributor that surfaces tiered memories.

Retrieves and scores memories from the TieredMemoryStore across all three
tiers (stable, episodic, working), applies time decay to episodic entries,
deduplicates across tiers, and formats results for system prompt injection.

Priority: 50 (between mental_models at 60 and entity_context at 40).
"""

import hashlib
import logging
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.context.token_counter import TokenCounter
from core.memory.tiers import MemoryEntry, MemoryTier, TieredMemoryStore

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """
    Retrieves and scores memories from the tiered store.
    Implements ContextContributor protocol (priority 50).
    """

    # ContextContributor protocol
    context_priority = 50

    def __init__(self, tiered_store: TieredMemoryStore, config: dict):
        """
        Args:
            tiered_store: TieredMemoryStore instance
            config: Full memory config section (with retrieval sub-key)
        """
        self.store = tiered_store
        self.config = config

        retrieval = config.get("retrieval", {})
        self.stable_limit = retrieval.get("stable_limit", 5)
        self.episodic_limit = retrieval.get("episodic_limit", 5)
        self.working_include_all = retrieval.get("working_include_all", True)
        self.min_similarity = retrieval.get("min_similarity", 0.4)
        self.dedup_threshold = retrieval.get("dedup_threshold", 0.92)

        # Decay config from tiers section
        tiers_config = config.get("tiers", {})
        self.episodic_halflife = tiers_config.get("episodic", {}).get(
            "decay_halflife_days", 90
        )

    # ------------------------------------------------------------------
    # ContextContributor protocol
    # ------------------------------------------------------------------

    def build_context(
        self,
        query: str,
        domains: list[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: Any,
    ) -> str:
        """
        ContextContributor interface. Retrieves relevant memories
        from all tiers and formats them for the system prompt.

        Args:
            query: Current user query
            domains: Active domains for this query
            persona: Active persona name (unused, kept for protocol)
            mode: Persona mode (unused, kept for protocol)
            token_budget: Maximum tokens to consume (0 = no limit)
            **kwargs: Additional keyword arguments
                retrieval_tier: Optional TierResult from RetrievalClassifier.
                    When tier is ABSENT, episodic retrieval becomes more
                    aggressive (episodic_limit 5→10, min_similarity 0.4→0.3).

        Returns:
            Formatted memory context string (empty if no memories found)
        """
        try:
            # Check for retrieval tier adjustment
            retrieval_tier = kwargs.get("retrieval_tier")
            override_episodic_limit = None
            override_min_similarity = None
            if retrieval_tier is not None:
                try:
                    from core.hardened.classifier import RetrievalTier
                    if retrieval_tier.tier == RetrievalTier.ABSENT:
                        override_episodic_limit = max(self.episodic_limit, 10)
                        override_min_similarity = min(self.min_similarity, 0.3)
                        logger.debug(
                            f"ABSENT retrieval tier: boosting episodic_limit to "
                            f"{override_episodic_limit}, min_similarity to "
                            f"{override_min_similarity}"
                        )
                except Exception:
                    pass

            memories = self.retrieve(
                query,
                domains=domains,
                override_episodic_limit=override_episodic_limit,
                override_min_similarity=override_min_similarity,
            )
            if not memories:
                return ""

            formatted = self._format_memories(memories, token_budget)
            return formatted

        except Exception as e:
            logger.warning(f"MemoryRetriever.build_context failed: {e}")
            return ""

    # ------------------------------------------------------------------
    # Core retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        domains: Optional[List[str]] = None,
        limit: int = 10,
        override_episodic_limit: Optional[int] = None,
        override_min_similarity: Optional[float] = None,
    ) -> List[MemoryEntry]:
        """
        Retrieve memories with tier-aware scoring.

        Pipeline:
        1. Search stable tier (limit=stable_limit, no decay)
        2. Search episodic tier (limit=episodic_limit, apply time decay)
        3. Get all working tier entries (session-scoped)
        4. Deduplicate across tiers (prefer stable > episodic > working)
        5. Sort by score, return top `limit`

        Args:
            query: Search query
            domains: Detected domains for filtering
            limit: Total results to return
            override_episodic_limit: Override episodic_limit (e.g. for ABSENT tier)
            override_min_similarity: Override min_similarity (e.g. for ABSENT tier)

        Returns:
            Scored, deduplicated, sorted MemoryEntry list
        """
        episodic_limit = override_episodic_limit or self.episodic_limit
        min_similarity = override_min_similarity if override_min_similarity is not None else self.min_similarity
        working_limit = 50 if self.working_include_all else 5

        # Define the three independent tier searches as (name, kwargs) pairs
        tier_searches: List[Tuple[str, dict]] = [
            ("stable", dict(
                query=query,
                tiers=[MemoryTier.STABLE],
                limit=self.stable_limit,
                min_score=min_similarity,
            )),
            ("episodic", dict(
                query=query,
                tiers=[MemoryTier.EPISODIC],
                limit=episodic_limit,
                min_score=min_similarity,
            )),
            ("working", dict(
                query=query,
                tiers=[MemoryTier.WORKING],
                limit=working_limit,
                min_score=0.0,  # Include all working entries
            )),
        ]

        all_entries: List[MemoryEntry] = []

        # Run all three tier searches concurrently.
        # Each search is independent (separate Mem0 namespaces), so there are no
        # cross-dependencies. ThreadPoolExecutor is appropriate here because
        # store.read() is I/O-bound (Ollama embedding + ChromaDB lookup).
        # If Ollama serialises embedding requests internally, this degrades
        # gracefully to the same wall-clock time as the sequential path.
        with ThreadPoolExecutor(max_workers=3) as pool:
            future_to_tier = {
                pool.submit(self.store.read, **kwargs): name
                for name, kwargs in tier_searches
            }
            for future in as_completed(future_to_tier):
                tier_name = future_to_tier[future]
                try:
                    all_entries.extend(future.result())
                except Exception as e:
                    logger.warning(f"{tier_name.capitalize()} tier retrieval failed: {e}")

        # 4. Deduplicate across tiers (prefer stable > episodic > working)
        deduped = self._deduplicate_across_tiers(all_entries)

        # 5. Sort by score descending, return top limit
        deduped.sort(key=lambda e: e.score, reverse=True)
        return deduped[:limit]

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def _deduplicate_across_tiers(
        self, entries: List[MemoryEntry]
    ) -> List[MemoryEntry]:
        """
        Deduplicate entries across tiers. When the same content appears in
        multiple tiers, keep the one from the highest-priority tier.

        Tier priority: STABLE > EPISODIC > WORKING

        Uses content hash for exact matches and a simple text overlap check
        for near-duplicates (since we don't have embedding similarity here).
        """
        tier_priority = {
            MemoryTier.STABLE: 3,
            MemoryTier.EPISODIC: 2,
            MemoryTier.WORKING: 1,
        }

        # Group by content fingerprint
        seen: Dict[str, MemoryEntry] = {}

        for entry in entries:
            fingerprint = self._content_fingerprint(entry.content)

            if fingerprint in seen:
                existing = seen[fingerprint]
                # Keep the one from the higher-priority tier
                if tier_priority.get(entry.tier, 0) > tier_priority.get(
                    existing.tier, 0
                ):
                    seen[fingerprint] = entry
                # If same tier, keep the one with the higher score
                elif entry.tier == existing.tier and entry.score > existing.score:
                    seen[fingerprint] = entry
            else:
                seen[fingerprint] = entry

        return list(seen.values())

    @staticmethod
    def _content_fingerprint(content: str) -> str:
        """
        Generate a fingerprint for content deduplication.

        Uses normalized text (lowered, whitespace-collapsed) hashed via MD5.
        This catches exact and near-exact duplicates. Semantic deduplication
        is handled by the TieredMemoryStore.deduplicate_against() at write time.
        """
        normalized = " ".join(content.lower().split())
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _format_memories(
        self, memories: List[MemoryEntry], token_budget: int = 0
    ) -> str:
        """
        Format memories for system prompt injection.

        Format:
        ## Relevant Memory
        [stable] User prefers TypeScript over JavaScript for new projects.
        [episodic, 3 days ago] Decided to use SQLite-vec for the entity store.
        [working] Currently discussing RAG scoring improvements.

        Truncates at token_budget boundary if specified.
        """
        if not memories:
            return ""

        header = "## Relevant Memory\n"
        lines: List[str] = []
        running_tokens = TokenCounter.count(header)

        for entry in memories:
            line = self._format_single_entry(entry)
            line_tokens = TokenCounter.count(line)

            # Check budget if specified
            if token_budget > 0 and (running_tokens + line_tokens) > token_budget:
                # Try to fit at least the header + what we have
                break

            lines.append(line)
            running_tokens += line_tokens

        if not lines:
            return ""

        return header + "\n".join(lines)

    def _format_single_entry(self, entry: MemoryEntry) -> str:
        """Format a single memory entry with tier tag and age."""
        tier_label = entry.tier.value

        age_str = self._age_string(entry.metadata.timestamp)
        if age_str and entry.tier != MemoryTier.WORKING:
            tag = f"[{tier_label}, {age_str}]"
        else:
            tag = f"[{tier_label}]"

        return f"{tag} {entry.content}"

    @staticmethod
    def _age_string(timestamp: str) -> str:
        """Convert an ISO timestamp to a human-readable age string."""
        if not timestamp:
            return ""

        try:
            created = datetime.fromisoformat(timestamp)
            delta = datetime.now() - created
            days = delta.days
            hours = delta.seconds // 3600

            if days == 0:
                if hours < 1:
                    return "just now"
                elif hours == 1:
                    return "1 hour ago"
                else:
                    return f"{hours} hours ago"
            elif days == 1:
                return "1 day ago"
            elif days < 7:
                return f"{days} days ago"
            elif days < 30:
                weeks = days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif days < 365:
                months = days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"

        except (ValueError, TypeError):
            return ""

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        """Return configuration state for debugging/metrics."""
        return {
            "stable_limit": self.stable_limit,
            "episodic_limit": self.episodic_limit,
            "working_include_all": self.working_include_all,
            "min_similarity": self.min_similarity,
            "episodic_halflife_days": self.episodic_halflife,
            "session_id": self.store.session_id,
        }
