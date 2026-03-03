"""
Tests for Phase 12b Wave 1: Graph-Aware Retrieval.

Covers:
  - Task 4:  Authority scoring in HybridSearcher RRF
  - Task 5:  GraphRetriever ContextContributor
  - Task 7:  Path-finding API endpoint (unit-level)
  - Task 6:  Wiring verification (import-level)
  - Task 22: Config presence
  - Backward compatibility: zero authority_weight falls back cleanly
"""

import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from core.entities import (
    Entity,
    EntityStore,
    EntityType,
    EntityExtractor,
    Relationship,
    RelationshipType,
    entity_id,
    EntityQuery,
    GraphRetriever,
)
from core.hybrid_search import HybridSearcher, ScoredResult


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
def extractor(store):
    return EntityExtractor(store, use_spacy=False)


@pytest.fixture
def populated_store(store):
    """Store with entities, relationships, and mentions for testing."""
    # Create entities
    python = Entity(
        id=entity_id("Python", "tool"),
        name="Python",
        entity_type=EntityType.TOOL,
        domains=["engineering"],
        authority_score=0.8,
    )
    django = Entity(
        id=entity_id("Django", "framework"),
        name="Django",
        entity_type=EntityType.FRAMEWORK,
        domains=["engineering"],
        authority_score=0.6,
    )
    fastapi = Entity(
        id=entity_id("FastAPI", "framework"),
        name="FastAPI",
        entity_type=EntityType.FRAMEWORK,
        domains=["engineering"],
        authority_score=0.7,
    )
    docker = Entity(
        id=entity_id("Docker", "tool"),
        name="Docker",
        entity_type=EntityType.TOOL,
        domains=["engineering", "devops"],
        authority_score=0.5,
    )
    unrelated = Entity(
        id=entity_id("Watercolor", "concept"),
        name="Watercolor",
        entity_type=EntityType.CONCEPT,
        domains=["art"],
        authority_score=0.3,
    )

    for e in [python, django, fastapi, docker, unrelated]:
        store.upsert_entity(e)

    # Create relationships
    store.upsert_relationship(Relationship(
        source_id=python.id, target_id=django.id,
        relationship_type=RelationshipType.RELATED_TO, strength=0.9,
    ))
    store.upsert_relationship(Relationship(
        source_id=python.id, target_id=fastapi.id,
        relationship_type=RelationshipType.RELATED_TO, strength=0.85,
    ))
    store.upsert_relationship(Relationship(
        source_id=django.id, target_id=docker.id,
        relationship_type=RelationshipType.RELATED_TO, strength=0.4,
    ))

    # Create mentions (simulate indexed notes)
    conn = store._conn()
    mentions = [
        (python.id, "note", "vault/python-overview.md", "Python is a versatile language", datetime.now().isoformat()),
        (python.id, "note", "vault/python-tips.md", "Advanced Python tips", datetime.now().isoformat()),
        (django.id, "note", "vault/django-guide.md", "Django web framework guide", datetime.now().isoformat()),
        (fastapi.id, "note", "vault/fastapi-setup.md", "FastAPI async setup", datetime.now().isoformat()),
        (docker.id, "note", "vault/docker-compose.md", "Docker compose patterns", datetime.now().isoformat()),
        (unrelated.id, "note", "vault/watercolor-techniques.md", "Watercolor painting", datetime.now().isoformat()),
    ]
    for entity_id_val, stype, sid, ctx, created in mentions:
        conn.execute(
            "INSERT OR IGNORE INTO entity_mentions (entity_id, source_type, source_id, context, created) VALUES (?, ?, ?, ?, ?)",
            (entity_id_val, stype, sid, ctx, created),
        )
    conn.commit()

    return store


@pytest.fixture
def retriever(populated_store, extractor):
    config = {
        "knowledge_graph": {
            "graph_traversal": {
                "enabled": True,
                "max_hops": 2,
                "min_strength": 0.3,
                "contributor_priority": 45,
            }
        }
    }
    return GraphRetriever(populated_store, extractor, config)


# ── ScoredResult authority field ─────────────────────────────────────

class TestScoredResultAuthority:
    """Task 4: authority_score field exists on ScoredResult."""

    def test_default_authority_score_is_zero(self):
        r = ScoredResult(doc_id="test")
        assert r.authority_score == 0.0

    def test_authority_score_settable(self):
        r = ScoredResult(doc_id="test", authority_score=0.75)
        assert r.authority_score == 0.75


# ── Authority scoring in HybridSearcher ──────────────────────────────

class TestAuthorityRRF:
    """Task 4: Authority scoring integrated into RRF fusion."""

    def test_init_defaults(self):
        hs = HybridSearcher()
        assert hs.entity_store is None
        assert hs.authority_weight == 0.3

    def test_init_custom_params(self):
        mock_store = MagicMock()
        hs = HybridSearcher(entity_store=mock_store, authority_weight=0.5)
        assert hs.entity_store is mock_store
        assert hs.authority_weight == 0.5

    def test_authority_disabled_when_weight_zero(self):
        hs = HybridSearcher(authority_weight=0.0)
        scores = hs._compute_authority_scores(["doc1"], {"doc1": {"filepath": "test.md"}})
        assert scores == {}

    def test_authority_disabled_when_no_store(self):
        hs = HybridSearcher(authority_weight=0.3)
        scores = hs._compute_authority_scores(["doc1"], {"doc1": {"filepath": "test.md"}})
        assert scores == {}

    def test_authority_bonus_increases_score(self):
        """Documents with entity authority should rank higher."""
        mock_store = MagicMock()
        mock_store.get_mentions_for_source.return_value = [
            {"entity_id": "e1", "authority_score": 0.9}
        ]

        hs = HybridSearcher(entity_store=mock_store, authority_weight=0.5)

        semantic = [("doc1", 0.8), ("doc2", 0.8)]
        keyword = []
        metadata = {
            "doc1": {"filepath": "vault/important.md"},
            "doc2": {"filepath": "vault/other.md"},
        }

        # doc1 gets authority; doc2 doesn't
        def mentions_side_effect(path, stype):
            if "important" in path:
                return [{"authority_score": 0.9}]
            return []

        mock_store.get_mentions_for_source.side_effect = mentions_side_effect

        results = hs.reciprocal_rank_fusion(semantic, keyword, set(), metadata)

        # doc1 with authority should score higher than doc2
        doc1_score = next(s for did, s, _ in results if did == "doc1")
        doc2_score = next(s for did, s, _ in results if did == "doc2")
        assert doc1_score > doc2_score, "Authority boost should increase document score"

    def test_authority_score_in_breakdown(self):
        """RRF breakdown should include authority_score."""
        mock_store = MagicMock()
        mock_store.get_mentions_for_source.return_value = [{"authority_score": 0.5}]

        hs = HybridSearcher(entity_store=mock_store, authority_weight=0.3)

        results = hs.reciprocal_rank_fusion(
            [("doc1", 0.7)], [], set(),
            {"doc1": {"filepath": "test.md"}},
        )

        _, _, breakdown = results[0]
        assert "authority_score" in breakdown
        assert breakdown["authority_score"] == 0.5

    def test_backward_compat_no_entity_store(self):
        """Without entity_store, RRF should work exactly as before."""
        hs = HybridSearcher()  # No entity_store
        semantic = [("doc1", 0.9), ("doc2", 0.7)]
        keyword = [("doc2", 5.0), ("doc3", 3.0)]
        metadata = {
            "doc1": {"filepath": "a.md"},
            "doc2": {"filepath": "b.md"},
            "doc3": {"filepath": "c.md"},
        }

        results = hs.reciprocal_rank_fusion(semantic, keyword, set(), metadata)
        assert len(results) == 3
        # All authority_scores should be 0
        for _, _, breakdown in results:
            assert breakdown["authority_score"] == 0.0


# ── GraphRetriever ContextContributor ──────────────────────────────

class TestGraphRetriever:
    """Task 5: GraphRetriever as ContextContributor."""

    def test_priority(self, retriever):
        assert retriever.context_priority == 45

    def test_disabled_returns_empty(self, populated_store, extractor):
        config = {
            "knowledge_graph": {
                "graph_traversal": {"enabled": False}
            }
        }
        r = GraphRetriever(populated_store, extractor, config)
        results = r.retrieve("Python Django")
        assert results == []

    def test_retrieve_finds_direct_matches(self, retriever):
        """Entities directly mentioned in query should be found."""
        results = retriever.retrieve("Python overview")
        assert len(results) > 0
        source_paths = [r.source_path for r in results]
        assert any("python" in p.lower() for p in source_paths)

    def test_retrieve_traverses_relationships(self, retriever):
        """Should find related entities via graph traversal."""
        results = retriever.retrieve("Python frameworks")
        source_paths = [r.source_path for r in results]
        # Should find Django and FastAPI via Python relationships
        has_related = any("django" in p.lower() or "fastapi" in p.lower() for p in source_paths)
        assert has_related, f"Expected traversal to find Django/FastAPI, got: {source_paths}"

    def test_hop_distance_scoring(self, retriever):
        """Direct matches (hop 0) should score higher than distant ones."""
        results = retriever.retrieve("Python")
        if len(results) >= 2:
            hop0 = [r for r in results if r.hop_distance == 0]
            hop1 = [r for r in results if r.hop_distance > 0]
            if hop0 and hop1:
                assert max(r.traversal_score for r in hop0) >= max(r.traversal_score for r in hop1)

    def test_deduplication_by_source_path(self, retriever):
        """Each source path should appear at most once."""
        results = retriever.retrieve("Python Django")
        source_paths = [r.source_path for r in results]
        assert len(source_paths) == len(set(source_paths)), "Duplicate source paths found"

    def test_max_results_limit(self, retriever):
        results = retriever.retrieve("Python", max_results=2)
        assert len(results) <= 2

    def test_build_context_returns_markdown(self, retriever):
        """build_context should return formatted markdown."""
        ctx = retriever.build_context("Python", domains=["engineering"])
        if ctx:
            assert "Graph-Connected Context" in ctx
            assert "Python" in ctx

    def test_build_context_empty_for_unknown(self, retriever):
        """Unknown entities should produce empty context."""
        ctx = retriever.build_context("xyzzymagnetic", domains=[])
        assert ctx == ""

    def test_build_context_token_budget(self, retriever):
        """Token budget should limit output length."""
        full = retriever.build_context("Python", domains=["engineering"], token_budget=0)
        limited = retriever.build_context("Python", domains=["engineering"], token_budget=20)
        if full:
            assert len(limited) <= len(full)

    def test_fuzzy_match_fallback(self, populated_store, extractor):
        """When exact extraction fails, fuzzy matching should still work."""
        config = {
            "knowledge_graph": {
                "graph_traversal": {"enabled": True, "max_hops": 1, "min_strength": 0.3}
            }
        }
        r = GraphRetriever(populated_store, extractor, config)
        # Use a query that likely won't match exact extraction but contains "docker"
        matches = r._fuzzy_match_query_words("using docker containers")
        assert len(matches) > 0
        assert any("Docker" in m.name for m in matches)

    def test_relationship_chain_populated(self, retriever):
        """Traversal results should have relationship chain info."""
        results = retriever.retrieve("Python")
        traversed = [r for r in results if r.hop_distance > 0]
        for r in traversed:
            assert len(r.relationship_chain) > 0, f"Expected chain for hop {r.hop_distance}"


# ── GraphRetriever import verification ───────────────────────────────

class TestGraphRetrieverImports:
    """Task 6: Verify GraphRetriever is properly exported."""

    def test_import_from_entities_package(self):
        from core.entities import GraphRetriever
        assert GraphRetriever is not None

    def test_import_direct(self):
        from core.entities.retriever import GraphRetriever, GraphTraversalResult
        assert GraphRetriever is not None
        assert GraphTraversalResult is not None


# ── EntityStore.find_path (used by Task 7 API) ──────────────────────

class TestFindPath:
    """Task 7: find_path used by the path-finding API endpoint."""

    def test_find_path_self(self, populated_store):
        """Path from entity to itself should return single-element list."""
        eid = entity_id("Python", "tool")
        path = populated_store.find_path(eid, eid)
        assert path is not None
        assert len(path) == 1

    def test_find_path_direct_neighbor(self, populated_store):
        """Should find 1-hop path between related entities."""
        path = populated_store.find_path(
            entity_id("Python", "tool"),
            entity_id("Django", "framework"),
        )
        assert path is not None
        assert len(path) >= 1

    def test_find_path_two_hops(self, populated_store):
        """Python → Django → Docker should be a 2-hop path."""
        path = populated_store.find_path(
            entity_id("Python", "tool"),
            entity_id("Docker", "tool"),
            max_hops=3,
        )
        assert path is not None
        assert len(path) >= 2

    def test_find_path_no_connection(self, populated_store):
        """Unconnected entities should return None."""
        path = populated_store.find_path(
            entity_id("Python", "tool"),
            entity_id("Watercolor", "concept"),
            max_hops=4,
        )
        assert path is None

    def test_find_path_max_hops_too_short(self, populated_store):
        """If max_hops is too short, should fail to find path."""
        path = populated_store.find_path(
            entity_id("Python", "tool"),
            entity_id("Docker", "tool"),
            max_hops=1,
        )
        # Docker is 2 hops away; max_hops=1 should not reach it
        assert path is None


# ── Config verification ──────────────────────────────────────────────

class TestConfig:
    """Task 22: Config entries present."""

    def test_config_yaml_has_knowledge_graph(self):
        import yaml
        with open("config.yaml", "r") as f:
            cfg = yaml.safe_load(f)
        assert "knowledge_graph" in cfg
        kg = cfg["knowledge_graph"]
        assert "authority_weight" in kg
        assert "graph_traversal" in kg
        assert kg["graph_traversal"]["enabled"] is True
        assert "max_hops" in kg["graph_traversal"]
        assert "min_strength" in kg["graph_traversal"]
        assert "contributor_priority" in kg["graph_traversal"]


# ── GraphTraversalResult dataclass ───────────────────────────────────

class TestGraphTraversalResult:

    def test_fields(self):
        from core.entities.retriever import GraphTraversalResult
        e = Entity(
            id="test", name="Test", entity_type=EntityType.CONCEPT,
            authority_score=0.5,
        )
        r = GraphTraversalResult(
            entity=e,
            source_path="vault/test.md",
            source_type="note",
            context_snippet="Some context",
            hop_distance=1,
            traversal_score=0.42,
            relationship_chain=["RELATED_TO"],
        )
        assert r.entity.name == "Test"
        assert r.hop_distance == 1
        assert r.traversal_score == 0.42
        assert r.relationship_chain == ["RELATED_TO"]

    def test_default_chain(self):
        from core.entities.retriever import GraphTraversalResult
        e = Entity(id="t", name="T", entity_type=EntityType.CONCEPT, authority_score=0.1)
        r = GraphTraversalResult(
            entity=e, source_path="x.md", source_type="note",
            context_snippet="", hop_distance=0, traversal_score=0.1,
        )
        assert r.relationship_chain == []
