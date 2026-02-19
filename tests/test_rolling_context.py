"""
Tests for Rolling Context Window.
Tests ingest, decay, amplification, eviction, and bin-packing.
"""

import pytest

from core.context.relevance_scorer import RelevanceScorer, ScoredEntry
from core.context.rolling_context import RollingContext, _extract_key_terms, _detect_reference


def _make_entry(
    content="Test content about token counting",
    source="rag",
    raw_score=0.8,
    composite_score=0.7,
    token_count=50,
) -> ScoredEntry:
    """Helper to create a ScoredEntry for testing."""
    entry = ScoredEntry(
        content=content,
        source=source,
        raw_score=raw_score,
        composite_score=composite_score,
        token_count=token_count,
        metadata={"domain": "general"},
    )
    return entry


def _default_config():
    return {
        "decay_per_turn": 0.85,
        "eviction_turns": 5,
        "amplification_reset": True,
    }


class TestRollingContextIngest:
    """Test entry ingestion."""

    def test_ingest_adds_entries(self):
        rc = RollingContext(_default_config())
        entries = [_make_entry(content="Entry A"), _make_entry(content="Entry B")]
        rc.ingest(entries)
        assert len(rc.entries) == 2

    def test_ingest_deduplicates(self):
        """Same content should not be added twice."""
        rc = RollingContext(_default_config())
        entry1 = _make_entry(content="Same content", composite_score=0.5)
        entry2 = _make_entry(content="Same content", composite_score=0.8)
        rc.ingest([entry1])
        rc.ingest([entry2])
        assert len(rc.entries) == 1
        # Should keep the higher score
        assert rc.entries[0].composite_score == 0.8

    def test_ingest_different_content(self):
        """Different content should both be stored."""
        rc = RollingContext(_default_config())
        rc.ingest([_make_entry(content="Content A")])
        rc.ingest([_make_entry(content="Content B")])
        assert len(rc.entries) == 2

    def test_ingest_extracts_key_terms(self):
        """Ingested entries should have key_terms populated."""
        rc = RollingContext(_default_config())
        entry = _make_entry(content="The `TokenCounter` class handles budget allocation for Polly.")
        rc.ingest([entry])
        assert len(rc.entries[0].key_terms) > 0

    def test_ingest_sets_token_count(self):
        """Entries with token_count=0 should get counted during ingest."""
        rc = RollingContext(_default_config())
        entry = _make_entry(content="Hello world", token_count=0)
        rc.ingest([entry])
        assert rc.entries[0].token_count > 0


class TestRollingContextDecay:
    """Test per-turn decay behavior."""

    def test_decay_reduces_score(self):
        """Unreferenced entries should have reduced scores after a turn."""
        rc = RollingContext(_default_config())
        entry = _make_entry(content="Unreferenced entry about xyz123", composite_score=1.0)
        rc.ingest([entry])

        original_score = rc.entries[0].composite_score
        rc.on_new_turn("Something else entirely", "A different response")
        assert rc.entries[0].composite_score < original_score

    def test_decay_rate(self):
        """Score should be multiplied by decay_rate each turn."""
        config = _default_config()
        config["decay_per_turn"] = 0.80
        rc = RollingContext(config)
        entry = _make_entry(content="Unreferenced unique content xyz999", composite_score=1.0)
        rc.ingest([entry])

        rc.on_new_turn("Unrelated query", "Unrelated response")
        assert abs(rc.entries[0].composite_score - 0.80) < 0.05

    def test_amplification_resets_recency(self):
        """Referenced entry should get reference_count incremented and turns_since_reference reset."""
        rc = RollingContext(_default_config())
        entry = _make_entry(
            content="The `TokenCounter` provides accurate budget counting",
            composite_score=0.8,
        )
        rc.ingest([entry])

        # Simulate a turn that references token counting
        rc.on_new_turn("How does TokenCounter work?", "TokenCounter counts tokens accurately.")
        assert rc.entries[0].reference_count >= 1
        assert rc.entries[0].turns_since_reference == 0


class TestRollingContextEviction:
    """Test entry eviction after unreferenced turns."""

    def test_eviction_after_threshold(self):
        """Entry should be evicted after eviction_turns unreferenced turns."""
        config = _default_config()
        config["eviction_turns"] = 3
        rc = RollingContext(config)
        entry = _make_entry(content="Will be evicted xyz_unique_123", composite_score=0.5)
        rc.ingest([entry])

        # Simulate 3 unreferenced turns
        for _ in range(3):
            rc.on_new_turn("Completely unrelated topic abc", "Also unrelated response def")

        assert len(rc.entries) == 0

    def test_referenced_entry_not_evicted(self):
        """Entry that is referenced should not be evicted."""
        config = _default_config()
        config["eviction_turns"] = 3
        rc = RollingContext(config)
        entry = _make_entry(
            content="The `BudgetAllocator` distributes tokens across sections",
            composite_score=0.8,
        )
        rc.ingest([entry])

        # Turns 1-2: unrelated
        rc.on_new_turn("Unrelated stuff abc123", "More unrelated def456")
        rc.on_new_turn("Still unrelated ghi789", "Yep unrelated jkl012")
        # Turn 3: reference it
        rc.on_new_turn("How does BudgetAllocator work?", "The BudgetAllocator distributes tokens.")

        assert len(rc.entries) == 1
        assert rc.entries[0].reference_count >= 1


class TestRollingContextBinPacking:
    """Test budget-aware bin-packing selection."""

    def test_select_within_budget(self):
        """Selected entries should fit within section budget."""
        rc = RollingContext(_default_config())
        entries = [
            _make_entry(content=f"Entry {i}", source="rag", token_count=100, composite_score=0.9 - i * 0.1)
            for i in range(5)
        ]
        rc.ingest(entries)

        selected = rc.select({"rag": 250})
        total_tokens = sum(e.token_count for e in selected.get("rag", []))
        assert total_tokens <= 250

    def test_select_highest_scored_first(self):
        """Higher-scored entries should be selected first."""
        rc = RollingContext(_default_config())
        entries = [
            _make_entry(content="Low score entry", source="rag", token_count=50, composite_score=0.3),
            _make_entry(content="High score entry", source="rag", token_count=50, composite_score=0.9),
        ]
        rc.ingest(entries)

        selected = rc.select({"rag": 60})  # Only room for one
        assert len(selected["rag"]) == 1
        assert selected["rag"][0].composite_score == 0.9

    def test_select_multiple_sections(self):
        """Entries should be grouped by section and independently budgeted."""
        rc = RollingContext(_default_config())
        rc.ingest([
            _make_entry(content="Memory entry", source="memory:stable", token_count=50, composite_score=0.8),
            _make_entry(content="RAG entry", source="rag", token_count=50, composite_score=0.7),
        ])

        selected = rc.select({"memory": 100, "rag": 100})
        assert len(selected.get("memory", [])) == 1
        assert len(selected.get("rag", [])) == 1

    def test_select_empty_budget(self):
        """Zero budget should return empty list for that section."""
        rc = RollingContext(_default_config())
        rc.ingest([_make_entry(content="Some entry", source="rag")])
        selected = rc.select({"rag": 0})
        assert selected["rag"] == []

    def test_look_ahead_finds_smaller_entry(self):
        """Look-ahead should find a smaller entry when the next one doesn't fit."""
        rc = RollingContext(_default_config())
        rc.ingest([
            _make_entry(content="Big entry", source="rag", token_count=200, composite_score=0.9),
            _make_entry(content="Small entry", source="rag", token_count=30, composite_score=0.5),
        ])

        # Budget only fits the small one
        selected = rc.select({"rag": 50})
        assert len(selected["rag"]) == 1
        assert selected["rag"][0].token_count == 30


class TestExtractKeyTerms:
    """Test key term extraction utility."""

    def test_backtick_terms(self):
        terms = _extract_key_terms("Use the `TokenCounter` to count tokens.")
        assert "tokencounter" in terms

    def test_long_words(self):
        terms = _extract_key_terms("The allocator distributes resources efficiently.")
        assert "allocator" in terms or "distributes" in terms or "efficiently" in terms

    def test_empty_content(self):
        terms = _extract_key_terms("")
        assert terms == []

    def test_max_10_terms(self):
        """Should return at most 10 terms."""
        long_text = " ".join([f"UniqueWord{i}LongEnough" for i in range(50)])
        terms = _extract_key_terms(long_text)
        assert len(terms) <= 10


class TestDetectReference:
    """Test reference detection utility."""

    def test_reference_detected(self):
        entry = _make_entry(content="The `TokenCounter` class in Polly handles budget allocation")
        entry.key_terms = ["tokencounter", "allocation", "budget"]
        assert _detect_reference(entry, "How does TokenCounter handle the budget?") is True

    def test_no_reference(self):
        entry = _make_entry(content="The `TokenCounter` class handles budget allocation")
        entry.key_terms = ["tokencounter", "allocation", "budget"]
        assert _detect_reference(entry, "What is the weather today?") is False

    def test_empty_key_terms(self):
        entry = _make_entry(content="Some content")
        entry.key_terms = []
        assert _detect_reference(entry, "Any text") is False
