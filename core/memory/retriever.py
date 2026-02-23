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
import time
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
        # Search result cache
        # ------------------------------------------------------------------
        # Keyed on sha256(query:tier:limit) → (inserted_at, List[MemoryEntry])
        # Avoids redundant Ollama embedding round-trips for repeated queries
        # within the same conversation.  TTL and size are configurable.
        retrieval_cfg = config.get("retrieval", {})
        self._cache_ttl: int = retrieval_cfg.get("cache_ttl", 300)       # seconds
        self._cache_max: int = retrieval_cfg.get("cache_max_entries", 64)
        self._cache: Dict[str, Tuple[float, List[MemoryEntry]]] = {}

    # ------------------------------------------------------------------
    # Search result cache helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cache_key(query: str, tier: MemoryTier, limit: int) -> str:
        """Stable cache key for a (query, tier, limit) triple."""
        raw = f"{query}:{tier.value}:{limit}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _cache_get(self, key: str) -> Optional[List[MemoryEntry]]:
        """Return cached results if present and not expired, else None."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        inserted_at, results = entry
        if time.monotonic() - inserted_at > self._cache_ttl:
            del self._cache[key]
            return None
        return results

    def _cache_put(self, key: str, results: List[MemoryEntry]) -> None:
        """Insert results into the cache, evicting the oldest entry if full."""
        if len(self._cache) >= self._cache_max:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
        self._cache[key] = (time.monotonic(), results)

    def invalidate(self, tier: Optional[MemoryTier] = None) -> None:
        """
        Invalidate cached search results.

        Called by Polly._on_session_end() after new memories have been
        written so that the next query sees fresh results.

        Args:
            tier: If given, only invalidate entries for that tier,
                  leaving all other tiers' cached results warm.
                  If None (default), clear the entire cache.

        Surgical use:
            Pass a specific tier when only that tier's data has changed
            mid-session, e.g. after a targeted write or a working-memory
            promotion.  Example::

                polly.memory_retriever.invalidate(MemoryTier.STABLE)

            This evicts only STABLE-tier cache entries; EPISODIC and
            WORKING entries remain cached and avoid redundant Ollama
            embedding calls on the next query.

            The full-cache form (no argument) is the safe default and is
            what _on_session_end() uses, since session-end extraction can
            write to both STABLE and EPISODIC tiers.
        """
        if tier is None:
            cleared = len(self._cache)
            self._cache.clear()
            logger.debug(f"MemoryRetriever cache cleared ({cleared} entries)")
        else:
            keys_to_drop = [
                k for k, (_, results) in self._cache.items()
                if results and results[0].tier == tier
            ]
            # Also drop entries whose key encodes the tier name (fast path for
            # empty-result entries where we can't inspect results[0].tier)
            tier_marker = f":{tier.value}:"
            keys_to_drop += [
                k for k in self._cache
                if k not in keys_to_drop and tier_marker in k
            ]
            for k in keys_to_drop:
                self._cache.pop(k, None)
            logger.debug(
                f"MemoryRetriever cache invalidated {len(keys_to_drop)} "
                f"entries for tier={tier.value}"
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

        # Check cache before spawning threads.  Build cache keys now so we
        # can populate the cache for misses inside the executor callback.
        tier_enum_map = {
            "stable": MemoryTier.STABLE,
            "episodic": MemoryTier.EPISODIC,
            "working": MemoryTier.WORKING,
        }

        uncached_searches: List[Tuple[str, dict]] = []
        for name, kwargs in tier_searches:
            tier_enum = tier_enum_map[name]
            cache_key = self._cache_key(query, tier_enum, kwargs["limit"])
            cached = self._cache_get(cache_key)
            if cached is not None:
                logger.debug(f"MemoryRetriever cache hit: tier={name}")
                all_entries.extend(cached)
            else:
                uncached_searches.append((name, kwargs))

        # Run only the uncached tier searches concurrently.
        if uncached_searches:
            with ThreadPoolExecutor(max_workers=len(uncached_searches)) as pool:
                future_to_name = {
                    pool.submit(self.store.read, **kwargs): name
                    for name, kwargs in uncached_searches
                }
                for future in as_completed(future_to_name):
                    name = future_to_name[future]
                    tier_enum = tier_enum_map[name]
                    kwargs = next(kw for n, kw in uncached_searches if n == name)
                    try:
                        results = future.result()
                        cache_key = self._cache_key(query, tier_enum, kwargs["limit"])
                        self._cache_put(cache_key, results)
                        all_entries.extend(results)
                    except Exception as e:
                        logger.warning(f"{name.capitalize()} tier retrieval failed: {e}")

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
