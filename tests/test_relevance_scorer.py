"""
Tests for Relevance Scorer.
Tests composite scoring, weight contributions, and domain/tier effects.
"""

import pytest

from core.context.relevance_scorer import RelevanceScorer, ScoredEntry


def _make_entry(
    content="Test content",
    source="rag",
    raw_score=0.8,
    domain="general",
    reference_count=0,
    turns_since_reference=0,
    timestamp="",
) -> ScoredEntry:
    """Helper to create a ScoredEntry for testing."""
    entry = ScoredEntry(
        content=content,
        source=source,
        raw_score=raw_score,
        composite_score=0.0,
        token_count=10,
        metadata={"domain": domain, "timestamp": timestamp},
        reference_count=reference_count,
        turns_since_reference=turns_since_reference,
    )
    return entry


def _default_config():
    return {
        "retrieval_similarity": 0.35,
        "recency": 0.25,
        "reference_frequency": 0.15,
        "domain_affinity": 0.15,
        "tier_weight": 0.10,
    }


class TestRelevanceScorerBasic:
    """Test basic scoring behavior."""

    def test_score_in_valid_range(self):
        """Composite score should always be in [0, 1]."""
        scorer = RelevanceScorer(_default_config())
        entry = _make_entry(raw_score=0.9, source="rag")
        score = scorer.score(entry)
        assert 0.0 <= score <= 1.0

    def test_score_stored_on_entry(self):
        """Score should be stored on entry.composite_score."""
        scorer = RelevanceScorer(_default_config())
        entry = _make_entry()
        score = scorer.score(entry)
        assert entry.composite_score == score

    def test_higher_raw_score_gives_higher_composite(self):
        """All else equal, higher raw_score should produce higher composite."""
        scorer = RelevanceScorer(_default_config())
        entry_low = _make_entry(raw_score=0.2)
        entry_high = _make_entry(raw_score=0.9)
        score_low = scorer.score(entry_low)
        score_high = scorer.score(entry_high)
        assert score_high > score_low


class TestRelevanceScorerWeights:
    """Test that weight components contribute proportionally."""

    def test_weights_sum_to_one(self):
        scorer = RelevanceScorer(_default_config())
        total = sum(scorer.weights.values())
        assert abs(total - 1.0) < 0.01

    def test_weights_auto_normalize(self):
        """Weights that don't sum to 1.0 should be normalized."""
        config = {
            "retrieval_similarity": 0.70,
            "recency": 0.50,
            "reference_frequency": 0.30,
            "domain_affinity": 0.30,
            "tier_weight": 0.20,
        }
        scorer = RelevanceScorer(config)
        total = sum(scorer.weights.values())
        assert abs(total - 1.0) < 0.01


class TestRelevanceScorerDomain:
    """Test domain affinity effects."""

    def test_matching_primary_domain_boosts_score(self):
        """Entry with domain matching query_domains[0] should score higher."""
        scorer = RelevanceScorer(_default_config())
        entry_match = _make_entry(domain="sigils")
        entry_nomatch = _make_entry(domain="other")
        score_match = scorer.score(entry_match, query_domains=["sigils"])
        score_nomatch = scorer.score(entry_nomatch, query_domains=["sigils"])
        assert score_match > score_nomatch

    def test_no_domains_gives_moderate_affinity(self):
        """With no query domains, all entries get moderate domain affinity."""
        scorer = RelevanceScorer(_default_config())
        entry = _make_entry(domain="sigils")
        score = scorer.score(entry, query_domains=[])
        assert 0.0 < score <= 1.0


class TestRelevanceScorerTierWeight:
    """Test tier weight component."""

    def test_working_memory_highest_tier_weight(self):
        """memory:working should have highest tier weight (1.0)."""
        scorer = RelevanceScorer(_default_config())
        entry_working = _make_entry(source="memory:working", raw_score=0.5)
        entry_entity = _make_entry(source="entity", raw_score=0.5)
        score_working = scorer.score(entry_working)
        score_entity = scorer.score(entry_entity)
        # Working memory should score higher due to tier weight
        assert score_working > score_entity

    def test_rag_has_high_tier_weight(self):
        """RAG should have tier weight 0.8."""
        scorer = RelevanceScorer(_default_config())
        entry_rag = _make_entry(source="rag", raw_score=0.5)
        entry_pattern = _make_entry(source="pattern", raw_score=0.5)
        score_rag = scorer.score(entry_rag)
        score_pattern = scorer.score(entry_pattern)
        assert score_rag > score_pattern


class TestRelevanceScorerRecency:
    """Test recency scoring component."""

    def test_recently_referenced_scores_higher(self):
        """Entry referenced this turn should score higher than one not referenced."""
        scorer = RelevanceScorer(_default_config())
        entry_recent = _make_entry(reference_count=3, turns_since_reference=0)
        entry_stale = _make_entry(reference_count=1, turns_since_reference=5)
        score_recent = scorer.score(entry_recent, current_turn=5)
        score_stale = scorer.score(entry_stale, current_turn=5)
        assert score_recent > score_stale


class TestRelevanceScorerReferenceFrequency:
    """Test reference frequency component."""

    def test_frequently_referenced_scores_higher(self):
        """Entry referenced 5 times should score higher than entry referenced 1 time."""
        scorer = RelevanceScorer(_default_config())
        entry_frequent = _make_entry(reference_count=5, turns_since_reference=0)
        entry_rare = _make_entry(reference_count=1, turns_since_reference=0)
        score_freq = scorer.score(entry_frequent, current_turn=5)
        score_rare = scorer.score(entry_rare, current_turn=5)
        assert score_freq > score_rare


class TestRelevanceScorerMentalModelNormalization:
    """Test score normalization for different source types."""

    def test_mental_model_score_normalized(self):
        """Mental model scores (0-100) should be normalized to 0-1."""
        scorer = RelevanceScorer(_default_config())
        entry = _make_entry(source="mental_model", raw_score=50.0)
        score = scorer.score(entry)
        assert 0.0 <= score <= 1.0
