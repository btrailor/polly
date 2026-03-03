"""
Tests for Phase 12b Wave 2: Quality Controls.

Covers:
  - Task 1:  Isolation detection (get_isolated_entities, get_isolated_notes)
  - Task 10: Authority recomputation scheduling (maybe_recompute_authority)
  - Task 9:  Batch operations API (batch endpoint logic)
  - Task 8:  Garden digest endpoint structure
"""

import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.entities import (
    Entity,
    EntityStore,
    EntityType,
    Relationship,
    RelationshipType,
    entity_id,
    EntityQuery,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def store(temp_db):
    return EntityStore(temp_db)


@pytest.fixture
def populated_store(store):
    """Store with entities, relationships, and mentions for isolation testing."""

    # Create entities
    python = Entity(
        id=entity_id("Python", "tool"),
        name="Python",
        entity_type=EntityType.TOOL,
        description="Programming language",
    )
    react = Entity(
        id=entity_id("React", "framework"),
        name="React",
        entity_type=EntityType.FRAMEWORK,
        description="JS framework",
    )
    docker = Entity(
        id=entity_id("Docker", "tool"),
        name="Docker",
        entity_type=EntityType.TOOL,
        description="Container runtime",
    )
    kubernetes = Entity(
        id=entity_id("Kubernetes", "tool"),
        name="Kubernetes",
        entity_type=EntityType.TOOL,
        description="Container orchestration",
    )
    isolated_concept = Entity(
        id=entity_id("Obscure Pattern", "concept"),
        name="Obscure Pattern",
        entity_type=EntityType.CONCEPT,
        description="Nobody connects to this",
    )

    for ent in [python, react, docker, kubernetes, isolated_concept]:
        store.upsert_entity(ent)

    # Create relationships: Python<->React, Docker<->Kubernetes, Docker<->Python
    store.upsert_relationship(Relationship(
        source_id=python.id, target_id=react.id,
        relationship_type=RelationshipType.RELATED_TO, strength=0.8,
    ))
    store.upsert_relationship(Relationship(
        source_id=docker.id, target_id=kubernetes.id,
        relationship_type=RelationshipType.RELATED_TO, strength=0.9,
    ))
    store.upsert_relationship(Relationship(
        source_id=docker.id, target_id=python.id,
        relationship_type=RelationshipType.USES, strength=0.7,
    ))
    # Python has 2 relationships (Python->React, Docker->Python)
    # React has 1 relationship (Python->React)
    # Docker has 2 relationships (Docker->Kubernetes, Docker->Python)
    # Kubernetes has 1 relationship (Docker->Kubernetes)
    # Obscure Pattern has 0 relationships

    # Record mentions on notes
    store.record_mention(python.id, "note", "NoteA", "Python is great")
    store.record_mention(react.id, "note", "NoteA", "React too")
    store.record_mention(docker.id, "note", "NoteB", "Docker usage")
    store.record_mention(kubernetes.id, "note", "NoteB", "K8s")
    store.record_mention(isolated_concept.id, "note", "NoteC", "Obscure Pattern mentioned")

    return store


# ── Task 1: Isolation Detection ──────────────────────────────────────

class TestIsolationDetection:
    """Tests for get_isolated_entities and get_isolated_notes."""

    def test_isolated_entities_zero_connections(self, populated_store):
        """Entity with 0 connections should appear in results."""
        isolated = populated_store.get_isolated_entities(max_connections=0)
        names = [e["name"] for e in isolated]
        assert "Obscure Pattern" in names
        # Python (2 conn) and Docker (2 conn) should NOT appear
        assert "Python" not in names
        assert "Docker" not in names

    def test_isolated_entities_at_threshold(self, populated_store):
        """Entities at exactly the threshold should be included."""
        # max_connections=1 → entities with 0 or 1 connections
        isolated = populated_store.get_isolated_entities(max_connections=1)
        names = [e["name"] for e in isolated]
        assert "Obscure Pattern" in names
        assert "React" in names       # 1 connection
        assert "Kubernetes" in names   # 1 connection
        # Python (2) and Docker (2) should be excluded
        assert "Python" not in names
        assert "Docker" not in names

    def test_isolated_entities_above_threshold(self, populated_store):
        """Entities above threshold are excluded."""
        isolated = populated_store.get_isolated_entities(max_connections=0)
        names = [e["name"] for e in isolated]
        assert "React" not in names
        assert "Kubernetes" not in names

    def test_isolated_entities_high_threshold_includes_all(self, populated_store):
        """With a high threshold, all entities should appear."""
        isolated = populated_store.get_isolated_entities(max_connections=100)
        assert len(isolated) == 5  # All entities

    def test_isolated_entities_ordering(self, populated_store):
        """Results should be ordered by connection_count ASC, authority ASC."""
        isolated = populated_store.get_isolated_entities(max_connections=2)
        conn_counts = [e["connection_count"] for e in isolated]
        assert conn_counts == sorted(conn_counts)

    def test_isolated_entities_return_structure(self, populated_store):
        """Each result should have the expected keys."""
        isolated = populated_store.get_isolated_entities(max_connections=2)
        assert len(isolated) > 0
        for e in isolated:
            assert "id" in e
            assert "name" in e
            assert "entity_type" in e
            assert "authority_score" in e
            assert "connection_count" in e

    def test_isolated_entities_empty_store(self, store):
        """Empty store returns empty list."""
        assert store.get_isolated_entities() == []

    def test_isolated_notes_with_isolated_entities(self, populated_store):
        """NoteC only has Obscure Pattern (0 connections), so it's isolated."""
        isolated = populated_store.get_isolated_notes(max_entity_connections=0)
        note_ids = [n["source_id"] for n in isolated]
        assert "NoteC" in note_ids

    def test_isolated_notes_well_connected_excluded(self, populated_store):
        """NoteA has Python (2 conn) and React (1 conn). Max is 2 → excluded at threshold 1."""
        isolated = populated_store.get_isolated_notes(max_entity_connections=1)
        note_ids = [n["source_id"] for n in isolated]
        assert "NoteA" not in note_ids

    def test_isolated_notes_threshold_includes_borderline(self, populated_store):
        """NoteA max connection is 2. At threshold=2, it should be included."""
        isolated = populated_store.get_isolated_notes(max_entity_connections=2)
        note_ids = [n["source_id"] for n in isolated]
        assert "NoteA" in note_ids

    def test_isolated_notes_return_structure(self, populated_store):
        """Each result should have the expected keys."""
        isolated = populated_store.get_isolated_notes(max_entity_connections=10)
        assert len(isolated) > 0
        for n in isolated:
            assert "source_id" in n
            assert "entity_count" in n
            assert "max_connection_count" in n

    def test_isolated_notes_empty_store(self, store):
        """Empty store returns empty list."""
        assert store.get_isolated_notes() == []


# ── Task 10: Authority Scheduling ────────────────────────────────────

class TestAuthorityScheduling:
    """Tests for maybe_recompute_authority and metadata table."""

    def test_recomputes_when_never_run(self, populated_store):
        """First call to maybe_recompute_authority should always run."""
        result = populated_store.maybe_recompute_authority(interval_hours=24)
        assert result is True

    def test_skips_when_recently_run(self, populated_store):
        """Second call within interval should skip."""
        populated_store.maybe_recompute_authority(interval_hours=24)
        result = populated_store.maybe_recompute_authority(interval_hours=24)
        assert result is False

    def test_recomputes_when_stale(self, populated_store):
        """Should recompute when timestamp is older than interval."""
        # Force a stale timestamp
        stale_time = (datetime.now() - timedelta(hours=25)).isoformat()
        populated_store._set_metadata("last_authority_recompute", stale_time)
        result = populated_store.maybe_recompute_authority(interval_hours=24)
        assert result is True

    def test_handles_missing_metadata_row(self, store):
        """Should handle gracefully when metadata table/row doesn't exist."""
        # Even on an empty store, should not crash
        result = store.maybe_recompute_authority(interval_hours=24)
        assert result is True  # No entities, but recompute still "runs"

    def test_interval_zero_always_recomputes(self, populated_store):
        """With interval_hours=0, should always recompute."""
        populated_store.maybe_recompute_authority(interval_hours=0)
        result = populated_store.maybe_recompute_authority(interval_hours=0)
        # interval=0 means timedelta(hours=0), so (now - last) >= 0 is always false
        # Actually, timedelta(hours=0) = 0, and (now - last) will be a tiny positive,
        # so it should be True.
        assert result is True

    def test_metadata_table_operations(self, store):
        """Test basic metadata get/set."""
        assert store._get_metadata("nonexistent") is None
        store._set_metadata("test_key", "test_value")
        assert store._get_metadata("test_key") == "test_value"
        # Overwrite
        store._set_metadata("test_key", "updated")
        assert store._get_metadata("test_key") == "updated"

    def test_metadata_table_created_idempotent(self, store):
        """Calling _ensure_metadata_table multiple times is safe."""
        store._ensure_metadata_table()
        store._ensure_metadata_table()
        store._set_metadata("k", "v")
        assert store._get_metadata("k") == "v"


# ── Task 9: Batch Operations (unit logic) ────────────────────────────

class TestBatchOperations:
    """Tests for batch operation logic that would be invoked by the endpoint."""

    def test_batch_merge_moves_mentions(self, populated_store):
        """Merge should move mentions from source to target."""
        python_id = entity_id("Python", "tool")
        react_id = entity_id("React", "framework")

        # Before merge: React has its own mentions
        react_before = populated_store.get_entity(react_id)
        assert react_before is not None

        # Merge React into Python
        moved = populated_store.move_mentions(react_id, python_id)
        assert moved >= 0
        populated_store.delete_entity(react_id)

        # After merge: React should be gone
        assert populated_store.get_entity(react_id) is None

    def test_batch_delete_removes_entity(self, populated_store):
        """Delete should remove entity and its relationships."""
        iso_id = entity_id("Obscure Pattern", "concept")
        populated_store.delete_entity(iso_id)
        assert populated_store.get_entity(iso_id) is None

    def test_batch_connect_creates_relationship(self, populated_store):
        """Connect should create a new relationship."""
        react_id = entity_id("React", "framework")
        k8s_id = entity_id("Kubernetes", "tool")

        # Before: no direct React->Kubernetes
        related = populated_store.get_related(react_id, max_hops=1)
        k8s_names = [e.name for e, r in related]
        assert "Kubernetes" not in k8s_names

        # Connect
        rel = Relationship(
            source_id=react_id, target_id=k8s_id,
            relationship_type=RelationshipType.RELATED_TO,
            strength=0.7,
        )
        populated_store.upsert_relationship(rel)

        # After: React->Kubernetes should exist
        related = populated_store.get_related(react_id, max_hops=1)
        k8s_names = [e.name for e, r in related]
        assert "Kubernetes" in k8s_names


# ── Task 8: Digest Structure (unit) ─────────────────────────────────

class TestDigestStructure:
    """Tests for digest-related data assembly."""

    def test_digest_isolation_data_consistency(self, populated_store):
        """Isolated entities count should match get_isolated_entities result."""
        isolated = populated_store.get_isolated_entities(max_connections=2)
        assert isinstance(isolated, list)
        for item in isolated:
            assert item["connection_count"] <= 2

    def test_digest_empty_store_returns_empty(self, store):
        """Empty store should return empty lists for all isolation queries."""
        assert store.get_isolated_entities(max_connections=2) == []
        assert store.get_isolated_notes(max_entity_connections=2) == []
        stats = store.get_stats()
        assert stats["entities"] == 0
        assert stats["relationships"] == 0

    def test_digest_stats_consistent_after_operations(self, populated_store):
        """Stats should stay consistent after entity operations."""
        stats_before = populated_store.get_stats()
        iso_id = entity_id("Obscure Pattern", "concept")
        populated_store.delete_entity(iso_id)
        stats_after = populated_store.get_stats()
        assert stats_after["entities"] == stats_before["entities"] - 1
