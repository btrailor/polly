"""
Relevance Scorer — unified scoring for heterogeneous context entries.

Computes composite relevance scores that normalize across different source
systems (RAG cosine similarity, Mem0 scores, mental model activation scores,
pattern engine scores) into a single 0-1 range.

Components:
  - Retrieval similarity (raw score normalized per source)
  - Recency (turn-based or time-based decay)
  - Reference frequency (how often re-accessed)
  - Domain affinity (match with current query domains)
  - Tier weight (fixed weight by source type)
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScoredEntry:
    """A context entry with composite relevance score."""

    content: str
    source: str  # "memory:stable", "memory:episodic", "memory:working", "rag", "mental_model", "entity", "pattern"
    raw_score: float  # Original score from source system
    composite_score: float  # Unified relevance score (0-1)
    token_count: int  # Cached token count
    key_terms: list = field(default_factory=list)  # Terms for reference detection
    metadata: dict = field(default_factory=dict)  # Source-specific metadata

    # Rolling context state (mutated by RollingContext)
    reference_count: int = 0  # Times referenced in current session
    last_referenced_turn: int = 0
    turns_since_reference: int = 0

    # For deduplication in rolling context
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash and self.content:
            import hashlib

            normalized = " ".join(self.content.lower().split())
            self.content_hash = hashlib.md5(
                normalized.encode("utf-8")
            ).hexdigest()


# Source type → score normalization range
_SOURCE_SCORE_RANGES: Dict[str, tuple] = {
    "rag": (0.0, 1.0),  # Already cosine similarity 0-1
    "memory:stable": (0.0, 1.0),  # Mem0 cosine similarity 0-1
    "memory:episodic": (0.0, 1.0),  # Mem0 cosine similarity 0-1
    "memory:working": (0.0, 1.0),  # Mem0 cosine similarity 0-1
    "mental_model": (0.0, 100.0),  # Activation score 0-100
    "entity": (0.0, 1.0),  # Normalized
    "pattern": (0.0, 1.0),  # Normalized
}

# Source type → fixed tier weight
_TIER_WEIGHTS: Dict[str, float] = {
    "memory:working": 1.0,
    "rag": 0.8,
    "memory:stable": 0.6,
    "mental_model": 0.5,
    "memory:episodic": 0.4,
    "entity": 0.3,
    "pattern": 0.3,
}


class RelevanceScorer:
    """
    Computes composite relevance scores for context entries
    from heterogeneous sources.
    """

    def __init__(self, config: dict):
        """
        Args:
            config: context_budget.relevance_weights section
        """
        self.weights = {
            "retrieval_similarity": config.get("retrieval_similarity", 0.35),
            "recency": config.get("recency", 0.25),
            "reference_frequency": config.get("reference_frequency", 0.15),
            "domain_affinity": config.get("domain_affinity", 0.15),
            "tier_weight": config.get("tier_weight", 0.10),
        }

        # Validate weights sum to ~1.0
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(
                f"Relevance weights sum to {weight_sum:.3f}, expected 1.0. "
                f"Normalizing."
            )
            for key in self.weights:
                self.weights[key] /= weight_sum

    def score(
        self,
        entry: ScoredEntry,
        query_domains: Optional[List[str]] = None,
        current_turn: int = 0,
    ) -> float:
        """
        Compute composite relevance score.

        Formula:
          composite = (w1 * retrieval_similarity)
                    + (w2 * recency_score)
                    + (w3 * reference_frequency_score)
                    + (w4 * domain_affinity_score)
                    + (w5 * tier_weight_score)

        All component scores normalized to 0-1 range.
        Composite clamped to [0, 1].

        Args:
            entry: Context entry to score
            query_domains: Detected domains for affinity calculation
            current_turn: Current conversation turn number

        Returns:
            Composite score (0-1). Also sets entry.composite_score.
        """
        if query_domains is None:
            query_domains = []

        sim = self._retrieval_similarity(entry)
        rec = self._recency_score(entry, current_turn)
        ref = self._reference_frequency_score(entry)
        dom = self._domain_affinity_score(entry, query_domains)
        tier = self._tier_weight_score(entry)

        composite = (
            self.weights["retrieval_similarity"] * sim
            + self.weights["recency"] * rec
            + self.weights["reference_frequency"] * ref
            + self.weights["domain_affinity"] * dom
            + self.weights["tier_weight"] * tier
        )

        # Clamp to [0, 1]
        composite = max(0.0, min(1.0, composite))

        entry.composite_score = composite
        return composite

    def _retrieval_similarity(self, entry: ScoredEntry) -> float:
        """
        Normalize raw scores from different sources to 0-1.

        RAG scores (already 0-1 from cosine): pass through
        Mem0 scores (already 0-1 from cosine): pass through
        Mental model scores (0-100 activation): divide by 100
        Pattern/entity scores (variable): pass through (assumed 0-1)
        """
        source = entry.source
        raw = entry.raw_score

        score_range = _SOURCE_SCORE_RANGES.get(source)
        if score_range is None:
            # Unknown source — assume 0-1 range
            return max(0.0, min(1.0, raw))

        lo, hi = score_range
        if hi == lo:
            return 0.5  # Can't normalize, return midpoint

        # Normalize to 0-1
        normalized = (raw - lo) / (hi - lo)
        return max(0.0, min(1.0, normalized))

    def _recency_score(self, entry: ScoredEntry, current_turn: int) -> float:
        """
        Score based on how recently entry was referenced.

        If referenced this session:
          recency = max(0, 1 - (turns_since_reference * 0.15))
        If not referenced this session (from memory retrieval):
          recency based on timestamp metadata with tier-appropriate decay
        """
        # If it's been referenced in the session, use turn-based recency
        if entry.reference_count > 0:
            return max(0.0, 1.0 - (entry.turns_since_reference * 0.15))

        # Not referenced this session — use timestamp if available
        timestamp = entry.metadata.get("timestamp", "")
        if timestamp:
            try:
                created = datetime.fromisoformat(timestamp)
                days_old = (datetime.now() - created).total_seconds() / 86400.0

                # Working memory is always fresh
                if entry.source == "memory:working":
                    return 1.0

                # Stable memory has very slow decay
                if entry.source == "memory:stable":
                    # Halflife of 365 days for recency component
                    return math.exp(-math.log(2) * days_old / 365.0)

                # Episodic memory decays faster
                if entry.source == "memory:episodic":
                    # Halflife of 90 days
                    return math.exp(-math.log(2) * days_old / 90.0)

                # Other sources (RAG, mental models) — moderate decay
                return math.exp(-math.log(2) * days_old / 180.0)

            except (ValueError, TypeError):
                pass

        # No timestamp, no references — use current turn as proxy
        # New entry this turn gets full recency
        if current_turn == 0:
            return 0.8

        return 0.5  # Default moderate recency for unknown age

    def _reference_frequency_score(self, entry: ScoredEntry) -> float:
        """
        Score based on how often entry has been referenced.
        reference_frequency = min(reference_count / 5, 1.0)
        """
        return min(entry.reference_count / 5.0, 1.0)

    def _domain_affinity_score(
        self,
        entry: ScoredEntry,
        query_domains: List[str],
    ) -> float:
        """
        Score based on domain match between entry and current query.

        Entry domain in query_domains[0] (primary): 1.0
        Entry domain in query_domains[1:] (secondary): 0.6
        Entry domain is "general" or "cross": 0.4
        Entry domain not in query_domains: 0.1
        """
        entry_domain = entry.metadata.get("domain", "general")

        if not query_domains:
            # No domain info — everything gets moderate affinity
            return 0.4

        if entry_domain in ("general", "cross"):
            return 0.4

        if entry_domain == query_domains[0]:
            return 1.0

        if entry_domain in query_domains[1:]:
            return 0.6

        return 0.1

    def _tier_weight_score(self, entry: ScoredEntry) -> float:
        """
        Fixed score by source type.

        memory:working   -> 1.0
        rag              -> 0.8
        memory:stable    -> 0.6
        mental_model     -> 0.5
        memory:episodic  -> 0.4
        entity/pattern   -> 0.3
        """
        return _TIER_WEIGHTS.get(entry.source, 0.3)
