"""
Integration test: context gathering produces ordered context from all contributors.

Verifies ContextContributor protocol: mental models, entity context, patterns, compression
contribute in priority order (integration-contracts).
"""

from __future__ import annotations

from pathlib import Path

import pytest

def test_context_contributors_sorted_by_priority(tmp_path):
    """Simulated gather: contributors sorted by context_priority descending."""
    from core.mental_models import MentalModelManager
    from core.entities import EntityStore, EntityContextBuilder
    from core.patterns import PatternEngine
    from core.compression import CompressionManager

    mm = MentalModelManager(str(tmp_path / "mm.yaml"), compressor=None)
    db_path = tmp_path / "entities.db"
    store = EntityStore(db_path)
    builder = EntityContextBuilder(store)
    engine = PatternEngine(tmp_path / "patterns.json")
    comp = CompressionManager(db_path=str(tmp_path / "compression.db"))

    contributors = [
        (mm.context_priority, mm),
        (builder.context_priority, builder),
        (engine.context_priority, engine),
        (comp.context_priority, comp),
    ]
    contributors.sort(key=lambda x: x[0], reverse=True)
    priorities = [p for p, _ in contributors]
    assert priorities == [60, 40, 20, 10]
    assert all(hasattr(c, "build_context") for _, c in contributors)
