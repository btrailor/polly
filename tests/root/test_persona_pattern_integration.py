"""Tests for persona↔pattern integration (integration-contracts Task 4)."""

from __future__ import annotations

from datetime import datetime

import pytest

from core.patterns import PatternEngine
from core.patterns.models import Pattern, PatternType, generate_pattern_id


@pytest.fixture
def pattern_engine(tmp_path):
    return PatternEngine(tmp_path / "patterns.json")


def test_set_active_persona_sets_context(pattern_engine):
    pattern_engine.set_active_persona("architect", "plan")
    assert pattern_engine._active_persona == "architect"
    assert pattern_engine._active_mode == "plan"


def test_learn_from_query_attributes_active_persona(pattern_engine):
    pattern_engine.set_active_persona("scribe", "capture")
    # learn_from_query creates conceptual patterns only for cross-domain pairs after 3+ occurrences
    for _ in range(3):
        pattern_engine.learn_from_query(
            "How do I save a note?",
            ["scrolls", "sigils"],
            "You can save by clicking Save or using the shortcut.",
        )
    all_p = list(pattern_engine.json_backend.load_all().values())
    assert len(all_p) >= 1
    for p in all_p:
        assert p.metadata.get("persona") == "scribe"
        assert p.metadata.get("mode") == "capture"


def test_get_patterns_for_prompt_boosts_persona_patterns(pattern_engine):
    # Create a pattern attributed to architect
    pid = generate_pattern_id("conceptual", "design_pattern")
    p_arch = Pattern(
        id=pid,
        pattern_type=PatternType.CONCEPTUAL,
        name="design pattern",
        description="User often asks about design",
        confidence=0.6,
        occurrences=2,
        last_seen=datetime.now(),
        domains=["sigils"],
        examples=[],
        metadata={"persona": "architect"},
    )
    pattern_engine.learn(p_arch)
    pattern_engine.set_active_persona("architect", "plan")
    ranked = pattern_engine.get_patterns_for_prompt("design systems", ["sigils"], limit=5)
    assert len(ranked) >= 1
    # Architect-attributed pattern should appear (boosted)
    names = [p.name for p in ranked]
    assert "design pattern" in names


def test_get_persona_patterns_returns_only_that_persona(pattern_engine):
    pid1 = generate_pattern_id("query", "q1")
    p1 = Pattern(
        id=pid1,
        pattern_type=PatternType.QUERY,
        name="query one",
        description="Query",
        confidence=0.5,
        occurrences=1,
        last_seen=datetime.now(),
        domains=[],
        examples=[],
        metadata={"persona": "scribe"},
    )
    pattern_engine.learn(p1)
    pid2 = generate_pattern_id("query", "q2")
    p2 = Pattern(
        id=pid2,
        pattern_type=PatternType.QUERY,
        name="query two",
        description="Query",
        confidence=0.5,
        occurrences=1,
        last_seen=datetime.now(),
        domains=[],
        examples=[],
        metadata={"persona": "architect"},
    )
    pattern_engine.learn(p2)
    scribe_patterns = pattern_engine.get_persona_patterns("scribe", limit=10)
    architect_patterns = pattern_engine.get_persona_patterns("architect", limit=10)
    assert any(p.name == "query one" for p in scribe_patterns)
    assert any(p.name == "query two" for p in architect_patterns)
    assert not any(p.name == "query two" for p in scribe_patterns)
    assert not any(p.name == "query one" for p in architect_patterns)
