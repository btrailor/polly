"""Tests for ContextContributor protocol implementors (integration-contracts)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.protocols import ContextContributor


class TestContextContributorProtocol:
    """Verify each context contributor has build_context and context_priority."""

    def test_entity_context_builder_has_contract(self, temp_db):
        from core.entities import EntityStore, EntityContextBuilder

        store = EntityStore(temp_db)
        builder = EntityContextBuilder(store)
        assert isinstance(builder, ContextContributor)
        assert hasattr(builder, "build_context")
        assert hasattr(builder, "context_priority")
        assert builder.context_priority == 40
        ctx = builder.build_context("test query", ["sigils"])
        assert isinstance(ctx, str)

    def test_mental_model_manager_has_contract(self):
        from core.mental_models import MentalModelManager

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "mental_models.yaml"
            mgr = MentalModelManager(str(path), compressor=None)
            assert hasattr(mgr, "build_context")
            assert hasattr(mgr, "context_priority")
            assert mgr.context_priority == 60
            ctx = mgr.build_context("test query", [])
            assert isinstance(ctx, str)

    def test_pattern_engine_has_contract(self, tmp_path):
        from core.patterns import PatternEngine

        engine = PatternEngine(tmp_path / "patterns.json")
        assert hasattr(engine, "build_context")
        assert hasattr(engine, "context_priority")
        assert engine.context_priority == 20
        ctx = engine.build_context("test query", [])
        assert isinstance(ctx, str)

    def test_compression_manager_has_contract(self, tmp_path):
        from core.compression import CompressionManager

        mgr = CompressionManager(db_path=str(tmp_path / "compression.db"))
        assert hasattr(mgr, "build_context")
        assert hasattr(mgr, "context_priority")
        assert mgr.context_priority == 10
        ctx = mgr.build_context("test query", [])
        assert isinstance(ctx, str)


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)
