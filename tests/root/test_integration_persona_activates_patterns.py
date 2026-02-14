"""
Integration test: persona activation propagates to pattern engine (integration-contracts).

Verifies that when a persona is set active, the pattern engine receives it and
attributes learned patterns to that persona.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.patterns import PatternEngine
from core.patterns.models import PatternType


def test_persona_activation_propagates_to_pattern_engine(tmp_path):
    """Setting active persona on pattern engine causes learned patterns to be attributed."""
    engine = PatternEngine(tmp_path / "patterns.json")
    engine.set_active_persona("architect", "plan")
    engine.learn_from_query("How do I design an API?", ["sigils", "scrolls"], "You could use OpenAPI.")
    engine.learn_from_query("Design a schema for users.", ["sigils", "scrolls"], "Here is a schema.")
    engine.learn_from_query("API design patterns.", ["sigils", "scrolls"], "REST and GraphQL.")
    all_p = list(engine.json_backend.load_all().values())
    assert len(all_p) >= 1
    for p in all_p:
        assert p.metadata.get("persona") == "architect"
        assert p.metadata.get("mode") == "plan"


def test_switch_persona_changes_attribution(tmp_path):
    """Switching persona changes attribution of subsequently learned patterns."""
    engine = PatternEngine(tmp_path / "patterns.json")
    engine.set_active_persona("scribe", "capture")
    engine.learn_from_query("Save this as a note.", ["scrolls"], "Saved.")
    engine.set_active_persona("professor", "socratic")
    engine.learn_from_query("What is recursion?", ["scrolls"], "Recursion is...")
    scribe_patterns = engine.get_persona_patterns("scribe", limit=10)
    professor_patterns = engine.get_persona_patterns("professor", limit=10)
    assert any(p.metadata.get("persona") == "scribe" for p in scribe_patterns)
    assert any(p.metadata.get("persona") == "professor" for p in professor_patterns)
