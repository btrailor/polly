"""Tests for unified entity system (EntityStore, EntityExtractor, EntityContextBuilder)."""

import tempfile
from pathlib import Path

import pytest

from core.entities import (
    Entity,
    EntityStore,
    EntityType,
    EntityExtractor,
    EntityContextBuilder,
    Relationship,
    RelationshipType,
    entity_id,
    EntityQuery,
)


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


def test_entity_id_deterministic():
    assert entity_id("Python", "tool") == entity_id("Python", "tool")
    assert entity_id("Python", "tool") != entity_id("Python", "language")


def test_upsert_entity(store):
    e = Entity(
        id=entity_id("Docker", "tool"),
        name="Docker",
        entity_type=EntityType.TOOL,
        domains=["signals"],
    )
    store.upsert_entity(e)
    got = store.get_entity(e.id)
    assert got is not None
    assert got.name == "Docker"
    store.upsert_entity(e)
    got2 = store.get_entity(e.id)
    assert got2.mention_count >= 1


def test_upsert_relationship(store):
    e1 = Entity(id="e1", name="A", entity_type=EntityType.CONCEPT)
    e2 = Entity(id="e2", name="B", entity_type=EntityType.CONCEPT)
    store.upsert_entity(e1)
    store.upsert_entity(e2)
    rel = Relationship(source_id="e1", target_id="e2", relationship_type=RelationshipType.RELATED_TO)
    store.upsert_relationship(rel)
    related = store.get_related("e1", max_hops=1)
    assert len(related) == 1
    assert related[0][0].id == "e2"


def test_search(store):
    e = Entity(id="x", name="Python", entity_type=EntityType.TOOL, authority_score=0.8)
    store.upsert_entity(e)
    results = store.search(EntityQuery(text="python", limit=5))
    assert len(results) >= 1
    results = store.search(EntityQuery(entity_types=[EntityType.TOOL], limit=5))
    assert any(r.name == "Python" for r in results)


def test_extract_and_store(extractor, store):
    entities = extractor.extract_and_store(
        "Using docker and norns for audio", "test", "src_1", ["signals"]
    )
    assert len(entities) >= 2
    stats = store.get_stats()
    assert stats["entities"] >= 2


def test_context_builder(store):
    e = Entity(
        id="c1",
        name="constraint",
        entity_type=EntityType.CONCEPT,
        domains=["grids"],
        authority_score=0.7,
    )
    store.upsert_entity(e)
    builder = EntityContextBuilder(store)
    ctx = builder.build_context("constraint systems", ["grids"])
    assert "constraint" in ctx
    assert "grids" in ctx or "Knowledge" in ctx


def test_authority_recompute(store):
    e = Entity(id="a1", name="Auth", entity_type=EntityType.CONCEPT, mention_count=5)
    store.upsert_entity(e)
    store.recompute_authority("a1")
    got = store.get_entity("a1")
    assert got.authority_score >= 0


def test_get_cross_domain_bridges(store):
    e = Entity(
        id="b1",
        name="Bridge",
        entity_type=EntityType.CONCEPT,
        domains=["grids", "signals"],
        authority_score=0.6,
    )
    store.upsert_entity(e)
    bridges = store.get_cross_domain_bridges("grids", "signals", limit=5)
    assert len(bridges) >= 1
    assert bridges[0].name == "Bridge"
