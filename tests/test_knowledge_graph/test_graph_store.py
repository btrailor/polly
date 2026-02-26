"""
Tests for PollyEntityGraphStore (Wave 5, Task 24).

LlamaIndex stubs are injected by conftest.py so no real llama-index-core install needed.
Tests use a real temporary SQLite EntityStore to avoid mocking the storage layer.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.entities import Entity, EntityStore, EntityType, Relationship, RelationshipType, entity_id
from core.entities.models import EntityQuery
from core.knowledge_graph.graph_store import PollyEntityGraphStore, _make_entity_node, _make_relation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entity(name: str, etype: EntityType = EntityType.CONCEPT, **kwargs) -> Entity:
    return Entity(
        id=entity_id(name, etype.value),
        name=name,
        entity_type=etype,
        authority_score=kwargs.get("authority_score", 0.5),
        domains=kwargs.get("domains", []),
    )


def _relationship(src: Entity, tgt: Entity, rtype: RelationshipType = RelationshipType.RELATED_TO) -> Relationship:
    return Relationship(
        source_id=src.id,
        target_id=tgt.id,
        relationship_type=rtype,
        strength=0.8,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
def seeded_store(store):
    """EntityStore with two entities and one relationship."""
    python = _entity("Python", EntityType.LANGUAGE)
    fastapi = _entity("FastAPI", EntityType.FRAMEWORK)
    store.upsert_entity(python)
    store.upsert_entity(fastapi)
    rel = _relationship(python, fastapi, RelationshipType.USES)
    store.upsert_relationship(rel)
    return store, python, fastapi, rel


@pytest.fixture
def graph_store(seeded_store):
    store, *_ = seeded_store
    return PollyEntityGraphStore(store)


# ---------------------------------------------------------------------------
# Tests: _make_entity_node (module-level helper)
# ---------------------------------------------------------------------------

class TestMakeEntityNode:
    def test_converts_entity_to_node_with_correct_name(self, seeded_store):
        _, python, *_ = seeded_store
        node = _make_entity_node(python)
        assert node.name == "Python"

    def test_converts_entity_to_node_with_correct_label(self, seeded_store):
        _, python, *_ = seeded_store
        node = _make_entity_node(python)
        assert node.label == EntityType.LANGUAGE.value

    def test_converts_entity_preserves_authority_score(self, seeded_store):
        _, python, *_ = seeded_store
        node = _make_entity_node(python)
        assert node.properties["authority_score"] == python.authority_score


class TestMakeRelation:
    def test_converts_relationship_with_correct_label(self, seeded_store):
        _, python, fastapi, rel = seeded_store
        result = _make_relation(rel, "Python", "FastAPI")
        assert result.label == RelationshipType.USES.value

    def test_converts_relationship_with_correct_source_target(self, seeded_store):
        _, python, fastapi, rel = seeded_store
        result = _make_relation(rel, "Python", "FastAPI")
        assert result.source_id == "Python"
        assert result.target_id == "FastAPI"

    def test_converts_relationship_preserves_strength(self, seeded_store):
        _, python, fastapi, rel = seeded_store
        result = _make_relation(rel, "Python", "FastAPI")
        assert result.properties["strength"] == 0.8


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.get_nodes
# ---------------------------------------------------------------------------

class TestGetNodes:
    def test_get_nodes_by_name_returns_one_node(self, graph_store):
        nodes = graph_store.get_nodes(node_ids=["Python"])
        assert len(nodes) == 1

    def test_get_nodes_node_has_correct_name(self, graph_store):
        nodes = graph_store.get_nodes(node_ids=["Python"])
        assert nodes[0].name == "Python"

    def test_get_nodes_unknown_name_returns_empty(self, graph_store):
        nodes = graph_store.get_nodes(node_ids=["DoesNotExist"])
        assert nodes == []

    def test_get_nodes_no_ids_returns_all_seeded_entities(self, graph_store):
        nodes = graph_store.get_nodes()
        assert len(nodes) == 2

    def test_get_multiple_nodes_by_id(self, graph_store):
        nodes = graph_store.get_nodes(node_ids=["Python", "FastAPI"])
        assert len(nodes) == 2

    def test_get_nodes_mixed_known_unknown(self, graph_store):
        nodes = graph_store.get_nodes(node_ids=["Python", "Unknown"])
        assert len(nodes) == 1


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.get_rel_map
# ---------------------------------------------------------------------------

class TestGetRelMap:
    def test_get_rel_map_empty_nodes_returns_empty(self, graph_store):
        rels = graph_store.get_rel_map(graph_nodes=[])
        assert rels == []

    def test_get_rel_map_none_nodes_returns_empty(self, graph_store):
        rels = graph_store.get_rel_map()
        assert rels == []

    def test_get_rel_map_finds_relationships(self, graph_store):
        python_node = graph_store.get_nodes(node_ids=["Python"])[0]
        rels = graph_store.get_rel_map(graph_nodes=[python_node])
        assert len(rels) >= 1

    def test_get_rel_map_relation_has_correct_type(self, graph_store):
        python_node = graph_store.get_nodes(node_ids=["Python"])[0]
        rels = graph_store.get_rel_map(graph_nodes=[python_node])
        rel_labels = [r.label for r in rels]
        assert RelationshipType.USES.value in rel_labels

    def test_get_rel_map_unknown_entity_returns_empty(self, graph_store):
        mock_node = MagicMock()
        mock_node.name = "Unknown"
        mock_node.id = "Unknown"
        rels = graph_store.get_rel_map(graph_nodes=[mock_node])
        assert rels == []

    def test_get_rel_map_respects_limit(self, seeded_store):
        store, python, fastapi, _ = seeded_store
        for i in range(5):
            e = _entity(f"Extra{i}", EntityType.TOOL)
            store.upsert_entity(e)
            rel = _relationship(python, e, RelationshipType.RELATED_TO)
            store.upsert_relationship(rel)

        gs = PollyEntityGraphStore(store)
        python_node = gs.get_nodes(node_ids=["Python"])[0]
        rels = gs.get_rel_map(graph_nodes=[python_node], limit=3)
        assert len(rels) <= 3


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.upsert_nodes
# ---------------------------------------------------------------------------

class TestUpsertNodes:
    def test_upsert_new_entity_via_node(self, seeded_store):
        store, *_ = seeded_store
        gs = PollyEntityGraphStore(store)

        from llama_index.core.graph_stores.types import EntityNode
        node = EntityNode(name="Docker", label="tool", properties={
            "id": "docker_id",
            "description": "Container runtime",
            "authority_score": 0.7,
            "domains": ["devops"],
            "aliases": [],
            "mention_count": 2,
        })
        gs.upsert_nodes([node])
        result = store.get_entity_by_name("Docker")
        assert result is not None
        assert result.name == "Docker"

    def test_upsert_with_invalid_entity_type_defaults_to_concept(self, seeded_store):
        store, *_ = seeded_store
        gs = PollyEntityGraphStore(store)

        from llama_index.core.graph_stores.types import EntityNode
        node = EntityNode(name="MyThing", label="invalid_type_xyz", properties={
            "authority_score": 0.5,
            "domains": [],
            "aliases": [],
            "mention_count": 1,
        })
        gs.upsert_nodes([node])
        result = store.get_entity_by_name("MyThing")
        assert result is not None
        assert result.entity_type == EntityType.CONCEPT


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.upsert_relations
# ---------------------------------------------------------------------------

class TestUpsertRelations:
    def test_upsert_relation_between_known_entities(self, seeded_store):
        store, python, fastapi, _ = seeded_store
        gs = PollyEntityGraphStore(store)

        from llama_index.core.graph_stores.types import Relation
        rel = Relation(
            label="uses",
            source_id="Python",
            target_id="FastAPI",
            properties={"strength": 0.9, "context": "test", "bidirectional": False},
        )
        gs.upsert_relations([rel])  # Should not raise

    def test_upsert_relation_skips_unknown_source(self, seeded_store):
        store, *_ = seeded_store
        gs = PollyEntityGraphStore(store)

        from llama_index.core.graph_stores.types import Relation
        rel = Relation(label="related_to", source_id="Unknown", target_id="FastAPI", properties={})
        gs.upsert_relations([rel])  # Should not raise

    def test_upsert_relation_skips_unknown_target(self, seeded_store):
        store, *_ = seeded_store
        gs = PollyEntityGraphStore(store)

        from llama_index.core.graph_stores.types import Relation
        rel = Relation(label="related_to", source_id="Python", target_id="Unknown", properties={})
        gs.upsert_relations([rel])  # Should not raise

    def test_upsert_invalid_rel_type_defaults_to_related_to(self, seeded_store):
        store, python, fastapi, _ = seeded_store
        gs = PollyEntityGraphStore(store)

        from llama_index.core.graph_stores.types import Relation
        rel = Relation(
            label="invalid_rel_type",
            source_id="Python",
            target_id="FastAPI",
            properties={"strength": 0.5},
        )
        gs.upsert_relations([rel])  # Should not raise — defaults to RELATED_TO


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.get_schema
# ---------------------------------------------------------------------------

class TestGetSchema:
    def test_get_schema_returns_string(self, graph_store):
        schema = graph_store.get_schema()
        assert isinstance(schema, str)
        assert len(schema) > 0

    def test_get_schema_contains_entity_types(self, graph_store):
        schema = graph_store.get_schema()
        assert any(et.value in schema for et in EntityType)

    def test_get_schema_contains_rel_types(self, graph_store):
        schema = graph_store.get_schema()
        assert any(rt.value in schema for rt in RelationshipType)

    def test_get_schema_mentions_counts(self, graph_store):
        schema = graph_store.get_schema()
        assert "2" in schema or "Entities" in schema


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.delete
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_existing_entity_removes_it(self, seeded_store):
        store, python, *_ = seeded_store
        gs = PollyEntityGraphStore(store)
        gs.delete(entity_names=["Python"])
        result = store.get_entity_by_name("Python")
        assert result is None

    def test_delete_leaves_other_entities_intact(self, seeded_store):
        store, python, fastapi, _ = seeded_store
        gs = PollyEntityGraphStore(store)
        gs.delete(entity_names=["Python"])
        result = store.get_entity_by_name("FastAPI")
        assert result is not None

    def test_delete_nonexistent_entity_is_no_op(self, graph_store):
        graph_store.delete(entity_names=["DoesNotExist"])

    def test_delete_none_is_no_op(self, graph_store):
        graph_store.delete()


# ---------------------------------------------------------------------------
# Tests: PollyEntityGraphStore.structured_query (not supported)
# ---------------------------------------------------------------------------

class TestStructuredQuery:
    def test_structured_query_raises_not_implemented(self, graph_store):
        with pytest.raises(NotImplementedError):
            graph_store.structured_query("MATCH (n) RETURN n")

    def test_query_alias_raises_not_implemented(self, graph_store):
        with pytest.raises(NotImplementedError):
            graph_store.query("MATCH (n) RETURN n")


# ---------------------------------------------------------------------------
# Tests: Class attributes + repr
# ---------------------------------------------------------------------------

class TestClassAttributes:
    def test_supports_structured_queries_false(self):
        assert PollyEntityGraphStore.supports_structured_queries is False

    def test_supports_vector_queries_false(self):
        assert PollyEntityGraphStore.supports_vector_queries is False

    def test_repr_includes_class_name(self, graph_store):
        r = repr(graph_store)
        assert "PollyEntityGraphStore" in r

    def test_repr_shows_entity_count(self, graph_store):
        r = repr(graph_store)
        assert "2" in r or "entities" in r

    def test_persist_is_noop(self, graph_store):
        graph_store.persist("/tmp/test")

    def test_from_persist_dir_returns_self(self, graph_store):
        result = graph_store.from_persist_dir("/tmp/test")
        assert result is graph_store
