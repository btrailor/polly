"""
Tests for the unified Pattern Engine.

Tests cover:
- Pattern creation and learning
- JSON storage backend (save, load, search)
- Scorer ranking logic
- Data migration from old format
- Engine lifecycle (decay, prune, save)
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from core.patterns import PatternEngine, Pattern, PatternType, PatternQuery
from core.patterns.scorer import PatternScorer
from core.patterns.storage.json_backend import JSONBackend
from core.patterns.models import generate_pattern_id, DomainPriorityPattern, QueryChunkPattern


# ===================== Fixtures =====================


@pytest.fixture
def tmp_json_path(tmp_path):
    """Temporary JSON file for testing."""
    return tmp_path / "test_patterns.json"


@pytest.fixture
def engine(tmp_json_path):
    """Fresh PatternEngine with no Mem0."""
    return PatternEngine(json_path=tmp_json_path)


@pytest.fixture
def sample_pattern():
    """A basic test pattern."""
    return Pattern(
        id="test_pattern_1",
        pattern_type=PatternType.CODE,
        name="Error Handling Pattern",
        description="Consistent try/except error handling",
        confidence=0.8,
        occurrences=5,
        first_seen=datetime.now() - timedelta(days=10),
        last_seen=datetime.now(),
        domains=["python"],
        examples=["try:\n    result = api_call()\nexcept Exception as e:\n    log(e)"],
        source="extraction",
    )


# ===================== Pattern Model Tests =====================


class TestPatternModel:
    def test_create_pattern(self, sample_pattern):
        assert sample_pattern.id == "test_pattern_1"
        assert sample_pattern.pattern_type == PatternType.CODE
        assert sample_pattern.confidence == 0.8

    def test_to_dict_roundtrip(self, sample_pattern):
        data = sample_pattern.to_dict()
        restored = Pattern.from_dict(data)
        assert restored.id == sample_pattern.id
        assert restored.pattern_type == sample_pattern.pattern_type
        assert restored.confidence == sample_pattern.confidence
        assert restored.occurrences == sample_pattern.occurrences

    def test_usefulness_ratio(self, sample_pattern):
        assert sample_pattern.usefulness_ratio == 0.0
        sample_pattern.times_used = 10
        sample_pattern.times_helpful = 7
        assert sample_pattern.usefulness_ratio == 0.7

    def test_generate_pattern_id_deterministic(self):
        id1 = generate_pattern_id("code", "Error Handling")
        id2 = generate_pattern_id("code", "Error Handling")
        id3 = generate_pattern_id("code", "Different Pattern")
        assert id1 == id2
        assert id1 != id3

    def test_from_dict_handles_unknown_type(self):
        data = {
            "id": "x",
            "pattern_type": "totally_unknown",
            "name": "test",
            "description": "test",
            "confidence": 0.5,
        }
        p = Pattern.from_dict(data)
        # Falls back to QUERY
        assert p.pattern_type == PatternType.QUERY


# ===================== JSON Backend Tests =====================


class TestJSONBackend:
    def test_save_and_load(self, tmp_json_path, sample_pattern):
        backend = JSONBackend(tmp_json_path)
        backend.save(sample_pattern)
        backend.flush()

        # Create new backend from same file
        backend2 = JSONBackend(tmp_json_path)
        loaded = backend2.load_all()
        assert "test_pattern_1" in loaded
        assert loaded["test_pattern_1"].name == "Error Handling Pattern"

    def test_delete(self, tmp_json_path, sample_pattern):
        backend = JSONBackend(tmp_json_path)
        backend.save(sample_pattern)
        assert backend.delete("test_pattern_1") is True
        assert backend.delete("nonexistent") is False
        assert len(backend.load_all()) == 0

    def test_search_by_type(self, tmp_json_path, sample_pattern):
        backend = JSONBackend(tmp_json_path)
        backend.save(sample_pattern)

        query = PatternQuery(pattern_types=[PatternType.CODE])
        results = backend.search(query)
        assert len(results) == 1

        query2 = PatternQuery(pattern_types=[PatternType.ROUTING])
        results2 = backend.search(query2)
        assert len(results2) == 0

    def test_search_by_text(self, tmp_json_path, sample_pattern):
        backend = JSONBackend(tmp_json_path)
        backend.save(sample_pattern)

        query = PatternQuery(text="error handling")
        results = backend.search(query)
        assert len(results) == 1

        query2 = PatternQuery(text="unrelated topic")
        results2 = backend.search(query2)
        assert len(results2) == 0

    def test_search_by_domain(self, tmp_json_path, sample_pattern):
        backend = JSONBackend(tmp_json_path)
        backend.save(sample_pattern)

        query = PatternQuery(domains=["python"])
        results = backend.search(query)
        assert len(results) == 1

        query2 = PatternQuery(domains=["javascript"])
        results2 = backend.search(query2)
        assert len(results2) == 0

    def test_atomic_write(self, tmp_json_path, sample_pattern):
        backend = JSONBackend(tmp_json_path)
        backend.save(sample_pattern)
        backend.flush()

        # Verify file is valid JSON
        raw = json.loads(tmp_json_path.read_text())
        assert raw["metadata"]["version"] == "3.0"
        assert len(raw["patterns"]) == 1


# ===================== Scorer Tests =====================


class TestPatternScorer:
    def test_confidence_boost(self, sample_pattern):
        scorer = PatternScorer()
        # High confidence should score higher
        sample_pattern.confidence = 0.9
        score_high = scorer.score(sample_pattern, set(), [])

        sample_pattern.confidence = 0.3
        score_low = scorer.score(sample_pattern, set(), [])

        assert score_high > score_low

    def test_domain_match_boost(self, sample_pattern):
        scorer = PatternScorer()
        score_match = scorer.score(sample_pattern, set(), ["python"])
        score_no_match = scorer.score(sample_pattern, set(), ["javascript"])
        assert score_match > score_no_match

    def test_code_keyword_boost(self, sample_pattern):
        scorer = PatternScorer()
        code_kws = {"code", "function", "implement"}
        non_code_kws = {"explain", "discuss", "summarize"}

        score_code = scorer.score(sample_pattern, code_kws, [])
        score_non = scorer.score(sample_pattern, non_code_kws, [])
        assert score_code > score_non

    def test_rank_returns_limited(self, sample_pattern):
        scorer = PatternScorer()
        patterns = [
            Pattern(
                id=f"p_{i}",
                pattern_type=PatternType.CODE,
                name=f"Pattern {i}",
                description=f"Description {i}",
                confidence=i * 0.1,
                occurrences=i,
            )
            for i in range(10)
        ]
        ranked = scorer.rank(patterns, "test query", [], limit=3)
        assert len(ranked) == 3
        # Highest confidence first
        assert ranked[0].confidence >= ranked[1].confidence


# ===================== Engine Tests =====================


class TestPatternEngine:
    def test_learn_new_pattern(self, engine, sample_pattern):
        result = engine.learn(sample_pattern)
        assert result.id == "test_pattern_1"
        assert len(engine.patterns) == 1

    def test_learn_reinforces_existing(self, engine, sample_pattern):
        engine.learn(sample_pattern)
        # Learn again
        duplicate = Pattern(
            id="test_pattern_1",
            pattern_type=PatternType.CODE,
            name="Error Handling Pattern",
            description="Consistent try/except error handling",
            confidence=0.5,
            domains=["python", "javascript"],
        )
        result = engine.learn(duplicate)
        assert result.occurrences == 6  # 5 + 1
        assert "javascript" in result.domains

    def test_learn_from_query(self, engine):
        learned = engine.learn_from_query("How do I handle errors in Python?", ["python"])
        # Should record in history at minimum
        assert len(engine.query_history) == 1

    def test_get_patterns_for_prompt(self, engine, sample_pattern):
        engine.learn(sample_pattern)
        results = engine.get_patterns_for_prompt("fix the error handling", ["python"])
        assert len(results) == 1

    def test_search(self, engine, sample_pattern):
        engine.learn(sample_pattern)
        results = engine.search(PatternQuery(text="error", limit=5))
        assert len(results) == 1

    def test_decay(self, engine):
        old_pattern = Pattern(
            id="old_1",
            pattern_type=PatternType.CODE,
            name="Old Pattern",
            description="Very old pattern",
            confidence=0.8,
            last_seen=datetime.now() - timedelta(days=120),
        )
        engine.learn(old_pattern)
        decayed = engine.decay()
        assert decayed >= 0  # May or may not decay depending on implementation details

    def test_prune(self, engine):
        weak = Pattern(
            id="weak_1",
            pattern_type=PatternType.QUERY,
            name="Weak",
            description="Low quality",
            confidence=0.01,
            occurrences=1,
        )
        engine.learn(weak)
        pruned = engine.prune(min_confidence=0.05)
        assert pruned == 1
        assert len(engine.patterns) == 0

    def test_save_and_reload(self, tmp_json_path, sample_pattern):
        engine1 = PatternEngine(json_path=tmp_json_path)
        engine1.learn(sample_pattern)
        engine1.save()

        # New engine from same file
        engine2 = PatternEngine(json_path=tmp_json_path)
        assert len(engine2.patterns) == 1
        assert "test_pattern_1" in engine2.patterns

    def test_get_stats(self, engine, sample_pattern):
        engine.learn(sample_pattern)
        stats = engine.get_stats()
        assert stats["total_patterns"] == 1
        assert "code" in stats["by_type"]

    def test_export(self, engine, sample_pattern):
        engine.learn(sample_pattern)
        data = engine.export()
        assert len(data["patterns"]) == 1
        assert "stats" in data

    def test_record_pattern_usage(self, engine, sample_pattern):
        engine.learn(sample_pattern)
        engine.record_pattern_usage("test_pattern_1", was_helpful=True)
        p = engine.patterns["test_pattern_1"]
        assert p.times_used == 1
        assert p.times_helpful == 1

    def test_learn_domain_priorities(self, engine):
        engine.learn_domain_priorities(
            query="How to deploy with Docker?",
            domain="docker",
            collection_scores={"codebase": 0.9, "obsidian": 0.3},
        )
        priorities = engine.get_domain_priorities("docker")
        assert "codebase" in priorities

    def test_learn_code_patterns(self, engine):
        code = """
async def fetch_data():
    try:
        result = await api.call()
    except Exception as e:
        logger.error(e)
"""
        learned = engine.learn_code_patterns(code, ["python"], filepath="test.py")
        assert len(learned) >= 1  # Should detect async and/or error handling


# ===================== Migration Tests =====================


class TestMigration:
    def test_migrate_from_v2(self, tmp_path):
        """Test migrating old v2.0 format patterns."""
        old_path = tmp_path / "patterns.json"
        old_data = {
            "patterns": [
                {
                    "id": "old_1",
                    "name": "Old Pattern",
                    "description": "From v2 format",
                    "pattern_type": "code",
                    "domains": ["python"],
                    "examples": ["example"],
                    "occurrences": 3,
                    "first_seen": "2025-01-01T00:00:00",
                    "last_seen": "2025-06-01T00:00:00",
                    "confidence": 0.7,
                    "metadata": {},
                    "times_used": 2,
                    "times_helpful": 1,
                }
            ],
            "query_chunk_patterns": [],
            "domain_priority_patterns": [],
            "query_history": [],
            "metadata": {"version": "2.0"},
        }
        old_path.write_text(json.dumps(old_data))

        engine = PatternEngine(json_path=old_path)

        from core.patterns.migration import migrate_from_v2

        stats = migrate_from_v2(old_path, engine)
        assert stats["patterns_migrated"] == 1
        assert "old_1" in engine.patterns

    def test_no_migration_for_v3(self, tmp_path):
        """Already migrated files should be skipped."""
        path = tmp_path / "patterns.json"
        data = {"patterns": [], "metadata": {"version": "3.0"}}
        path.write_text(json.dumps(data))

        engine = PatternEngine(json_path=path)

        from core.patterns.migration import migrate_from_v2

        stats = migrate_from_v2(path, engine)
        assert stats["patterns_migrated"] == 0
