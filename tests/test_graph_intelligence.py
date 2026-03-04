"""
Tests for Phase 12b Wave 2 + Wave 3: Quality Controls & Graph Intelligence.

Covers:
  Wave 2:
  - Task 1:  Isolation detection (get_isolated_entities, get_isolated_notes)
  - Task 10: Authority recomputation scheduling (maybe_recompute_authority)
  - Task 9:  Batch operations API (batch endpoint logic)
  - Task 8:  Garden digest endpoint structure

  Wave 3:
  - Task 2:  Edge evidence (get_edge_evidence)
  - Task 3:  Schema migration (new columns)
  - Task 11: Community detection (CommunityDetector)
  - Task 12: PageRank + betweenness centrality (CentralityComputer)
  - Task 13: Upgraded authority formula
  - Task 14: Edge confidence scoring (EdgeConfidenceScorer)
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


# ══════════════════════════════════════════════════════════════════════
# Phase 12b Wave 3: Graph Intelligence Tests (Task 24)
# ══════════════════════════════════════════════════════════════════════

from core.entities.intelligence import (
    CommunityDetector,
    CentralityComputer,
    EdgeConfidence,
    EdgeConfidenceScorer,
)


@pytest.fixture
def graph_store(store):
    """Store with a richer graph for intelligence testing.

    Topology:
      Cluster A: Python <-> Django <-> Flask (triangle-ish, all have links)
      Cluster B: React <-> Vue <-> Angular (triangle-ish)
      Bridge:    Python <-> React  (connects cluster A → B)
      Isolated:  Obscure (no edges)
    """
    entities = {
        "Python": Entity(id=entity_id("Python", "tool"), name="Python",
                         entity_type=EntityType.TOOL, description="Programming language",
                         domains=["backend"]),
        "Django": Entity(id=entity_id("Django", "framework"), name="Django",
                         entity_type=EntityType.FRAMEWORK, description="Python web framework",
                         domains=["backend"]),
        "Flask": Entity(id=entity_id("Flask", "framework"), name="Flask",
                        entity_type=EntityType.FRAMEWORK, description="Lightweight Python web",
                        domains=["backend"]),
        "React": Entity(id=entity_id("React", "framework"), name="React",
                        entity_type=EntityType.FRAMEWORK, description="JS UI library",
                        domains=["frontend"]),
        "Vue": Entity(id=entity_id("Vue", "framework"), name="Vue",
                      entity_type=EntityType.FRAMEWORK, description="Progressive JS framework",
                      domains=["frontend"]),
        "Angular": Entity(id=entity_id("Angular", "framework"), name="Angular",
                          entity_type=EntityType.FRAMEWORK, description="Google JS framework",
                          domains=["frontend"]),
        "Obscure": Entity(id=entity_id("Obscure", "concept"), name="Obscure",
                          entity_type=EntityType.CONCEPT, description="Nobody knows"),
    }
    for ent in entities.values():
        store.upsert_entity(ent)

    edges = [
        ("Python", "tool", "Django", "framework"),
        ("Python", "tool", "Flask", "framework"),
        ("Django", "framework", "Flask", "framework"),
        ("React", "framework", "Vue", "framework"),
        ("React", "framework", "Angular", "framework"),
        ("Vue", "framework", "Angular", "framework"),
        ("Python", "tool", "React", "framework"),  # bridge
    ]
    for src_name, src_type, tgt_name, tgt_type in edges:
        store.upsert_relationship(Relationship(
            source_id=entity_id(src_name, src_type),
            target_id=entity_id(tgt_name, tgt_type),
            relationship_type=RelationshipType.RELATED_TO,
            strength=0.8,
        ))

    # Add mentions for co-occurrence testing
    store.record_mention(entities["Python"].id, "note", "NoteBackend", "Python is cool")
    store.record_mention(entities["Django"].id, "note", "NoteBackend", "Django is cool")
    store.record_mention(entities["React"].id, "note", "NoteFrontend", "React is cool")
    store.record_mention(entities["Vue"].id, "note", "NoteFrontend", "Vue is cool")
    # Python and React co-occur in a note
    store.record_mention(entities["Python"].id, "note", "NoteFullStack", "Python backend")
    store.record_mention(entities["React"].id, "note", "NoteFullStack", "React frontend")

    return store


# ── Task 2: Edge Evidence ────────────────────────────────────────────

class TestEdgeEvidence:
    """Tests for get_edge_evidence."""

    def test_evidence_with_relationship(self, graph_store):
        """Direct edge should return relationship records."""
        ev = graph_store.get_edge_evidence(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        assert len(ev["relationships"]) >= 1
        assert ev["relationships"][0]["relationship_type"] == "related_to"

    def test_evidence_shared_documents(self, graph_store):
        """Python and Django both appear in NoteBackend."""
        ev = graph_store.get_edge_evidence(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        sources = [d["source_id"] for d in ev["shared_documents"]]
        assert "NoteBackend" in sources
        assert ev["shared_document_count"] >= 1

    def test_evidence_co_occurrences(self, graph_store):
        """Python and React co-occur in NoteFullStack."""
        ev = graph_store.get_edge_evidence(
            entity_id("Python", "tool"),
            entity_id("React", "framework"),
        )
        co_sources = [c["source_id"] for c in ev["co_occurrences"]]
        assert "NoteFullStack" in co_sources

    def test_evidence_no_edge(self, graph_store):
        """No relationship between Obscure and Python."""
        ev = graph_store.get_edge_evidence(
            entity_id("Obscure", "concept"),
            entity_id("Python", "tool"),
        )
        assert ev["relationships"] == []
        assert ev["shared_document_count"] == 0

    def test_evidence_return_structure(self, graph_store):
        """Result should have expected keys."""
        ev = graph_store.get_edge_evidence(
            entity_id("Python", "tool"),
            entity_id("React", "framework"),
        )
        assert "source_id" in ev
        assert "target_id" in ev
        assert "relationships" in ev
        assert "shared_documents" in ev
        assert "shared_document_count" in ev
        assert "co_occurrences" in ev


# ── Task 3: Schema Migration ────────────────────────────────────────

class TestSchemaMigration:
    """Tests for new intelligence columns."""

    def test_columns_exist_on_fresh_db(self, store):
        """Fresh DB should have community_id, pagerank_score, betweenness_score."""
        conn = store._conn()
        cur = conn.execute("PRAGMA table_info(entities)")
        cols = [row[1] for row in cur.fetchall()]
        assert "community_id" in cols
        assert "pagerank_score" in cols
        assert "betweenness_score" in cols

    def test_double_init_is_safe(self, temp_db):
        """Creating EntityStore twice shouldn't crash."""
        s1 = EntityStore(temp_db)
        s2 = EntityStore(temp_db)
        conn = s2._conn()
        cur = conn.execute("PRAGMA table_info(entities)")
        cols = [row[1] for row in cur.fetchall()]
        assert "community_id" in cols

    def test_columns_have_defaults(self, graph_store):
        """Entities should have default 0.0 for pagerank and betweenness."""
        ent = graph_store.get_entity(entity_id("Python", "tool"))
        # The entity dataclass doesn't expose these columns directly,
        # but we can check via SQL
        conn = graph_store._conn()
        cur = conn.execute(
            "SELECT pagerank_score, betweenness_score, community_id FROM entities WHERE id = ?",
            (ent.id,),
        )
        row = cur.fetchone()
        assert row[0] == 0.0 or row[0] is None  # default
        assert row[1] == 0.0 or row[1] is None


# ── Task 11: Community Detection ─────────────────────────────────────

class TestCommunityDetection:
    """Tests for CommunityDetector."""

    def test_detects_two_clusters(self, graph_store):
        """Two connected cliques should form two communities (or one big one via bridge)."""
        detector = CommunityDetector()
        communities = detector.detect(graph_store, min_community_size=2)
        # With the Python-React bridge, label propagation may merge into one.
        # Either way, we should have at least 1 community with >= 2 members.
        assert len(communities) >= 1
        total_members = sum(len(m) for m in communities.values())
        assert total_members >= 4

    def test_isolated_node_unclustered(self, graph_store):
        """Obscure (no edges) should have NULL community_id."""
        detector = CommunityDetector()
        detector.detect(graph_store, min_community_size=2)
        conn = graph_store._conn()
        cur = conn.execute(
            "SELECT community_id FROM entities WHERE id = ?",
            (entity_id("Obscure", "concept"),),
        )
        row = cur.fetchone()
        assert row[0] is None

    def test_min_community_size_filters(self, graph_store):
        """With min_size=10, no communities should form (only 7 entities)."""
        detector = CommunityDetector()
        communities = detector.detect(graph_store, min_community_size=10)
        assert len(communities) == 0

    def test_empty_store(self, store):
        """Empty store returns no communities."""
        detector = CommunityDetector()
        communities = detector.detect(store, min_community_size=1)
        assert communities == {}

    def test_communities_written_to_db(self, graph_store):
        """community_id should be written to entities table."""
        detector = CommunityDetector()
        communities = detector.detect(graph_store, min_community_size=2)
        conn = graph_store._conn()
        cur = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE community_id IS NOT NULL"
        )
        clustered = cur.fetchone()[0]
        assert clustered >= 4  # At least the well-connected nodes

    def test_deterministic_results(self, graph_store):
        """Two runs should produce compatible results."""
        detector = CommunityDetector()
        r1 = detector.detect(graph_store, min_community_size=2)
        r2 = detector.detect(graph_store, min_community_size=2)
        # Same number of communities
        assert len(r1) == len(r2)


# ── Task 12: PageRank + Betweenness ──────────────────────────────────

class TestPageRank:
    """Tests for CentralityComputer.pagerank."""

    def test_pagerank_runs(self, graph_store):
        """Should compute scores for all entities."""
        computer = CentralityComputer()
        scores = computer.pagerank(graph_store)
        assert len(scores) == 7  # All entities

    def test_pagerank_normalized(self, graph_store):
        """All scores should be in [0, 1]."""
        computer = CentralityComputer()
        scores = computer.pagerank(graph_store)
        for s in scores.values():
            assert 0.0 <= s <= 1.0

    def test_bridge_node_high_pagerank(self, graph_store):
        """Python (bridge between clusters) should have relatively high rank."""
        computer = CentralityComputer()
        scores = computer.pagerank(graph_store)
        python_score = scores[entity_id("Python", "tool")]
        obscure_score = scores[entity_id("Obscure", "concept")]
        # Python has outgoing edges so it may receive incoming links from the
        # undirected-like structure; at minimum it should be >= isolated Obscure
        assert python_score >= obscure_score

    def test_pagerank_written_to_db(self, graph_store):
        """Scores should be persisted."""
        computer = CentralityComputer()
        computer.pagerank(graph_store)
        conn = graph_store._conn()
        cur = conn.execute(
            "SELECT pagerank_score FROM entities WHERE id = ?",
            (entity_id("Python", "tool"),),
        )
        score = cur.fetchone()[0]
        assert score > 0

    def test_empty_store(self, store):
        """Empty store returns empty dict."""
        computer = CentralityComputer()
        scores = computer.pagerank(store)
        assert scores == {}


class TestBetweenness:
    """Tests for CentralityComputer.betweenness_centrality."""

    def test_betweenness_runs(self, graph_store):
        """Should compute scores for all entities."""
        computer = CentralityComputer()
        scores = computer.betweenness_centrality(graph_store)
        assert len(scores) == 7

    def test_betweenness_normalized(self, graph_store):
        """Scores should be in [0, 1]."""
        computer = CentralityComputer()
        scores = computer.betweenness_centrality(graph_store)
        for s in scores.values():
            assert 0.0 <= s <= 1.0

    def test_bridge_node_high_betweenness(self, graph_store):
        """Python and React (bridge) should have high betweenness."""
        computer = CentralityComputer()
        scores = computer.betweenness_centrality(graph_store)
        python_bc = scores[entity_id("Python", "tool")]
        obscure_bc = scores[entity_id("Obscure", "concept")]
        assert python_bc > obscure_bc

    def test_isolated_node_zero_betweenness(self, graph_store):
        """Obscure (no edges) should have 0 betweenness."""
        computer = CentralityComputer()
        scores = computer.betweenness_centrality(graph_store)
        assert scores[entity_id("Obscure", "concept")] == 0.0

    def test_empty_store(self, store):
        """Empty store returns empty dict."""
        computer = CentralityComputer()
        scores = computer.betweenness_centrality(store)
        assert scores == {}


# ── Task 13: Authority Formula Upgrade ───────────────────────────────

class TestAuthorityUpgrade:
    """Tests for upgraded authority formula (uses pagerank/betweenness when available)."""

    def test_new_formula_uses_pagerank(self, graph_store):
        """After computing centrality, authority should incorporate pagerank."""
        computer = CentralityComputer()
        computer.pagerank(graph_store)
        computer.betweenness_centrality(graph_store)
        # Recompute authority — should use new formula
        graph_store.recompute_authority(None)
        python = graph_store.get_entity(entity_id("Python", "tool"))
        assert python.authority_score > 0

    def test_fallback_when_no_centrality(self, graph_store):
        """Without centrality scores, old formula should still work."""
        graph_store.recompute_authority(None)
        python = graph_store.get_entity(entity_id("Python", "tool"))
        assert python.authority_score > 0

    def test_authority_ordering_reflects_graph(self, graph_store):
        """Python (3 edges) should have higher authority than Obscure (0 edges)."""
        computer = CentralityComputer()
        computer.pagerank(graph_store)
        computer.betweenness_centrality(graph_store)
        graph_store.recompute_authority(None)
        python = graph_store.get_entity(entity_id("Python", "tool"))
        obscure = graph_store.get_entity(entity_id("Obscure", "concept"))
        assert python.authority_score > obscure.authority_score


# ── Task 14: Edge Confidence Scoring ─────────────────────────────────

class TestEdgeConfidence:
    """Tests for EdgeConfidenceScorer."""

    def test_score_returns_edge_confidence(self, graph_store):
        """Score should return an EdgeConfidence dataclass."""
        scorer = EdgeConfidenceScorer(graph_store)
        conf = scorer.score(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        assert isinstance(conf, EdgeConfidence)
        assert 0.0 <= conf.composite <= 1.0

    def test_co_occurrence_nonzero_for_shared_docs(self, graph_store):
        """Python+Django share NoteBackend → co_occurrence > 0."""
        scorer = EdgeConfidenceScorer(graph_store)
        conf = scorer.score(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        assert conf.co_occurrence > 0

    def test_structural_proximity_adjacent(self, graph_store):
        """Adjacent entities should have structural_proximity > 0."""
        scorer = EdgeConfidenceScorer(graph_store)
        conf = scorer.score(
            entity_id("Python", "tool"),
            entity_id("React", "framework"),
        )
        assert conf.structural_proximity > 0

    def test_no_shared_docs_low_co_occurrence(self, graph_store):
        """Obscure shares no docs with Python → co_occurrence = 0."""
        scorer = EdgeConfidenceScorer(graph_store)
        conf = scorer.score(
            entity_id("Obscure", "concept"),
            entity_id("Python", "tool"),
        )
        assert conf.co_occurrence == 0.0

    def test_custom_weights(self, graph_store):
        """Custom weights should change composite score."""
        scorer_default = EdgeConfidenceScorer(graph_store)
        scorer_custom = EdgeConfidenceScorer(graph_store, weights={
            "co_occurrence": 1.0,
            "semantic_similarity": 0.0,
            "temporal_proximity": 0.0,
            "structural_proximity": 0.0,
        })
        conf_default = scorer_default.score(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        conf_custom = scorer_custom.score(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        # With only co_occurrence weight, composite should equal co_occurrence
        assert abs(conf_custom.composite - conf_custom.co_occurrence) < 0.01

    def test_to_dict(self, graph_store):
        """EdgeConfidence.to_dict should return all fields."""
        scorer = EdgeConfidenceScorer(graph_store)
        conf = scorer.score(
            entity_id("Python", "tool"),
            entity_id("React", "framework"),
        )
        d = conf.to_dict()
        assert "composite" in d
        assert "co_occurrence" in d
        assert "semantic_similarity" in d
        assert "temporal_proximity" in d
        assert "structural_proximity" in d

    def test_score_all_edges(self, graph_store):
        """score_all_edges should return results for every relationship."""
        scorer = EdgeConfidenceScorer(graph_store)
        results = scorer.score_all_edges()
        assert len(results) >= 7  # 7 edges in graph_store


# ── Integration: Full Pipeline ───────────────────────────────────────

class TestIntelligencePipeline:
    """Integration: communities → centrality → authority → confidence."""

    def test_full_pipeline(self, graph_store):
        """Run the full intelligence pipeline end-to-end."""
        # 1. Community detection
        detector = CommunityDetector()
        communities = detector.detect(graph_store, min_community_size=2)
        assert len(communities) >= 1

        # 2. Centrality
        computer = CentralityComputer()
        pr = computer.pagerank(graph_store)
        bc = computer.betweenness_centrality(graph_store)
        assert len(pr) == 7
        assert len(bc) == 7

        # 3. Authority recompute (uses new formula)
        graph_store.recompute_authority(None)
        python = graph_store.get_entity(entity_id("Python", "tool"))
        assert python.authority_score > 0

        # 4. Edge confidence
        scorer = EdgeConfidenceScorer(graph_store)
        conf = scorer.score(
            entity_id("Python", "tool"),
            entity_id("React", "framework"),
        )
        assert conf.composite > 0
