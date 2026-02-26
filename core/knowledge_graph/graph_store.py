"""
Polly Entity Graph Store — LlamaIndex PropertyGraphStore Bridge (Wave 5, Task 24)

Adapts the existing SQLite-backed EntityStore to LlamaIndex's PropertyGraphStore
protocol. No data is duplicated: all reads go directly to entities.db.

This is a live view — queries reflect the current state of the EntityStore.
Writes route back through EntityStore.upsert_entity/upsert_relationship.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence

from core.entities.models import Entity, EntityQuery, EntityType, Relationship, RelationshipType
from core.entities.store import EntityStore

logger = logging.getLogger(__name__)


def _make_entity_node(entity: Entity):
    """Convert Entity → LlamaIndex EntityNode (lazy import to avoid hard dep at module load)."""
    from llama_index.core.graph_stores.types import EntityNode
    return EntityNode(
        name=entity.name,
        label=entity.entity_type.value,
        properties={
            "id": entity.id,
            "description": entity.description or "",
            "authority_score": entity.authority_score,
            "domains": entity.domains,
            "aliases": entity.aliases,
            "mention_count": entity.mention_count,
        },
    )


def _make_relation(rel: Relationship, source_name: str, target_name: str):
    """Convert Relationship → LlamaIndex Relation."""
    from llama_index.core.graph_stores.types import Relation
    return Relation(
        label=rel.relationship_type.value,
        source_id=source_name,
        target_id=target_name,
        properties={
            "strength": rel.strength,
            "context": rel.context or "",
            "bidirectional": rel.bidirectional,
            "mention_count": rel.mention_count,
        },
    )


class PollyEntityGraphStore:
    """
    Adapter: EntityStore (SQLite) → LlamaIndex PropertyGraphStore protocol.

    This class does NOT inherit from PropertyGraphStore directly (to avoid
    mandatory heavy LlamaIndex imports at module load time). Instead it
    implements the same interface and is duck-typed into LlamaIndex contexts.

    Supported operations:
        get_nodes(node_ids)           → List[LabelledNode]
        get_rel_map(nodes, depth)     → List[Relation]
        upsert_nodes(nodes)           → delegates to EntityStore
        upsert_relations(relations)   → delegates to EntityStore
        get_schema()                  → entity types + rel types as text

    Unsupported (raises NotImplementedError):
        structured_query (Cypher)     → use ChromaVectorStore for vector search
    """

    supports_structured_queries: bool = False
    supports_vector_queries: bool = False

    def __init__(self, entity_store: EntityStore) -> None:
        self.entity_store = entity_store

    # ---- LlamaIndex PropertyGraphStore interface ----

    def get_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Fetch EntityNode objects by ID or top-N by authority.

        If node_ids is provided, look up each entity by name (LlamaIndex uses
        names as node identifiers). Falls back to top-authority entities when
        no IDs given.
        """
        from llama_index.core.graph_stores.types import EntityNode

        nodes: List[EntityNode] = []

        if node_ids:
            for nid in node_ids:
                # LlamaIndex uses entity name as node_id
                entity = self.entity_store.get_entity_by_name(nid)
                if entity is not None:
                    nodes.append(_make_entity_node(entity))
        else:
            # Return top-50 by authority score
            q = EntityQuery(text="", limit=50, min_authority=0.0)
            entities = self.entity_store.search(q)
            nodes = [_make_entity_node(e) for e in entities]

        return nodes

    def get_rel_map(
        self,
        graph_nodes: Optional[List[Any]] = None,
        depth: int = 1,
        limit: int = 30,
        ignore_rels: Optional[List[str]] = None,
    ) -> List[Any]:
        """
        Return Relation objects for the given nodes up to `depth` hops.

        Delegates to EntityStore.get_related() for each node.
        """
        ignore_rels = ignore_rels or []
        seen: set = set()
        all_relations: List[Any] = []

        nodes_to_traverse = graph_nodes or []
        if not nodes_to_traverse:
            return []

        for node in nodes_to_traverse:
            name = getattr(node, "name", None) or getattr(node, "id", None)
            if not name:
                continue
            entity = self.entity_store.get_entity_by_name(name)
            if entity is None:
                continue

            try:
                related = self.entity_store.get_related(
                    entity.id, max_hops=depth, min_strength=0.3
                )
            except Exception as e:
                logger.debug(f"get_rel_map: get_related failed for '{name}': {e}")
                continue

            for related_entity, rel in related:
                if rel is None:
                    continue
                if rel.relationship_type.value in ignore_rels:
                    continue
                key = (entity.name, related_entity.name, rel.relationship_type.value)
                if key in seen:
                    continue
                seen.add(key)
                all_relations.append(
                    _make_relation(rel, entity.name, related_entity.name)
                )
                if len(all_relations) >= limit:
                    return all_relations

        return all_relations

    def upsert_nodes(self, nodes: List[Any]) -> None:
        """Write LlamaIndex EntityNode objects back to EntityStore."""
        from llama_index.core.graph_stores.types import EntityNode

        for node in nodes:
            if not isinstance(node, EntityNode):
                continue
            props = node.properties or {}
            entity_id = props.get("id") or node.name
            try:
                etype = EntityType(node.label)
            except ValueError:
                etype = EntityType.CONCEPT

            entity = Entity(
                id=entity_id,
                name=node.name,
                entity_type=etype,
                description=props.get("description", ""),
                authority_score=float(props.get("authority_score", 0.0)),
                domains=list(props.get("domains") or []),
                aliases=list(props.get("aliases") or []),
                mention_count=int(props.get("mention_count", 1)),
            )
            try:
                self.entity_store.upsert_entity(entity)
            except Exception as e:
                logger.warning(f"upsert_nodes: failed to upsert entity '{node.name}': {e}")

    def upsert_relations(self, relations: List[Any]) -> None:
        """Write LlamaIndex Relation objects back to EntityStore."""
        for rel in relations:
            props = rel.properties or {}
            # Resolve source/target entity IDs from names
            src_entity = self.entity_store.get_entity_by_name(rel.source_id)
            tgt_entity = self.entity_store.get_entity_by_name(rel.target_id)
            if src_entity is None or tgt_entity is None:
                logger.debug(f"upsert_relations: skipping — entity not found ({rel.source_id} → {rel.target_id})")
                continue
            try:
                rel_type = RelationshipType(rel.label)
            except ValueError:
                rel_type = RelationshipType.RELATED_TO
            relationship = Relationship(
                source_id=src_entity.id,
                target_id=tgt_entity.id,
                relationship_type=rel_type,
                strength=float(props.get("strength", 1.0)),
                context=props.get("context", ""),
                bidirectional=bool(props.get("bidirectional", False)),
            )
            try:
                self.entity_store.upsert_relationship(relationship)
            except Exception as e:
                logger.warning(f"upsert_relations: failed for {src_entity.id} → {tgt_entity.id}: {e}")

    def delete(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Delete entities by name."""
        if entity_names:
            for name in entity_names:
                entity = self.entity_store.get_entity_by_name(name)
                if entity:
                    try:
                        self.entity_store.delete_entity(entity.id)
                    except Exception as e:
                        logger.warning(f"delete: failed to delete entity '{name}': {e}")

    def get_schema(self, refresh: bool = False) -> str:
        """Return entity types and relationship types as a human-readable schema string."""
        entity_types = [et.value for et in EntityType]
        rel_types = [rt.value for rt in RelationshipType]
        try:
            stats = self.entity_store.get_stats()
            entity_count = stats.get("entities", 0)
            rel_count = stats.get("relationships", 0)
        except Exception:
            entity_count = rel_count = "?"

        return (
            f"Knowledge Graph Schema\n"
            f"Entities: {entity_count} total | Types: {', '.join(entity_types)}\n"
            f"Relationships: {rel_count} total | Types: {', '.join(rel_types)}\n"
        )

    def structured_query(
        self,
        query: str,
        param_map: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Cypher/structured queries not supported — raises NotImplementedError."""
        raise NotImplementedError(
            "PollyEntityGraphStore does not support Cypher queries. "
            "Use ChromaVectorStore for vector search."
        )

    # Alias for LlamaIndex compatibility
    query = structured_query

    def persist(self, persist_dir: str, fs: Any = None) -> None:
        """No-op: EntityStore persists to SQLite automatically."""
        pass

    def from_persist_dir(self, persist_dir: str, fs: Any = None) -> "PollyEntityGraphStore":
        """No-op: EntityStore is already persisted to SQLite."""
        return self

    def __repr__(self) -> str:
        try:
            stats = self.entity_store.get_stats()
            return f"<PollyEntityGraphStore {stats.get('entities', 0)} entities, {stats.get('relationships', 0)} relationships>"
        except Exception:
            return "<PollyEntityGraphStore>"
