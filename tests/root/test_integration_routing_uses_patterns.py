"""
Integration test: router consults ROUTING_OUTCOME patterns and outcomes can be recorded.

Verifies pattern→router and router→pattern feedback (integration-contracts).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.patterns import PatternEngine
from core.patterns.models import Pattern, PatternQuery, PatternType, generate_pattern_id
from core.router_v2 import IntelligentRouterV2


def test_router_apply_patterns_stores_patterns():
    """apply_patterns() stores patterns for use in next route() (PatternConsumer)."""
    router = IntelligentRouterV2()  # No API keys → empty providers
    pid = generate_pattern_id("routing_outcome", "route_general_anthropic_claude")
    pattern = Pattern(
        id=pid,
        pattern_type=PatternType.ROUTING_OUTCOME,
        name="route_general_claude",
        description="Claude for general",
        confidence=0.7,
        metadata={"model": "claude-sonnet-4-20250514", "provider": "anthropic", "task_type": "general"},
    )
    router.apply_patterns([pattern], {"query": "test"})
    assert router._routing_patterns is not None
    assert len(router._routing_patterns) == 1
    assert router._routing_patterns[0].pattern_type == PatternType.ROUTING_OUTCOME


def test_routing_outcome_recorded_and_searchable(tmp_path: Path):
    """Recording a ROUTING_OUTCOME pattern makes it searchable for router hint."""
    engine = PatternEngine(tmp_path / "patterns.json")
    name = "route_simple_anthropic_claude-sonnet-4"
    pid = generate_pattern_id("routing_outcome", name)
    engine.learn(
        Pattern(
            id=pid,
            pattern_type=PatternType.ROUTING_OUTCOME,
            name=name,
            description="claude-sonnet-4 for simple",
            confidence=0.5,
            metadata={
                "model": "claude-sonnet-4-20250514",
                "provider": "anthropic",
                "task_type": "simple_query",
                "persona": None,
            },
        )
    )
    results = engine.search(
        PatternQuery(pattern_types=[PatternType.ROUTING_OUTCOME], min_confidence=0.3, limit=5)
    )
    assert len(results) >= 1
    assert any(p.pattern_type == PatternType.ROUTING_OUTCOME for p in results)
