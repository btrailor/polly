"""
Unified Entity Model and Knowledge Graph for Polly.

Shared entity model used by knowledge graph, pattern engine, and future consumers.
SQLite-backed storage with graph operations (traversal, path finding, cross-domain bridges).

Usage:
    from core.entities import EntityStore, Entity, EntityType, EntityExtractor, EntityContextBuilder

    store = EntityStore(Path("~/.polly/entities.db"))
    extractor = EntityExtractor(store)
    extractor.extract_and_store(text, "query", source_id, domains)
    context = EntityContextBuilder(store).build_context(query, domain_names)
"""

from .models import (
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
    EntityQuery,
    entity_id,
)
from .store import EntityStore
from .extractor import EntityExtractor
from .context import EntityContextBuilder

__all__ = [
    "EntityStore",
    "Entity",
    "EntityType",
    "Relationship",
    "RelationshipType",
    "EntityQuery",
    "EntityExtractor",
    "EntityContextBuilder",
    "entity_id",
]
