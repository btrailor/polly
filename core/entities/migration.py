"""
Migrate from learners/graph.py JSON format to EntityStore SQLite.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .models import Entity, EntityType, Relationship, RelationshipType, entity_id
from .store import EntityStore

logger = logging.getLogger(__name__)

TYPE_MAP = {
    "concept": EntityType.CONCEPT,
    "tool": EntityType.TOOL,
    "pattern": EntityType.PATTERN,
    "framework": EntityType.FRAMEWORK,
    "project": EntityType.PROJECT,
    "person": EntityType.PERSON,
    "file": EntityType.FILE,
    "organization": EntityType.ORGANIZATION,
}


def migrate_from_json(json_path: Path, store: EntityStore) -> Dict[str, int]:
    """Migrate entities and relationships from knowledge_graph.json to SQLite."""
    stats = {"entities": 0, "relationships": 0, "errors": 0}
    path = Path(json_path).expanduser()
    if not path.exists():
        logger.info(f"No graph file at {path} — skip migration")
        return stats

    backup = path.with_suffix(".json.v1_backup")
    if not backup.exists():
        shutil.copy2(path, backup)
        logger.info(f"Backed up graph to {backup}")

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to read graph JSON: {e}")
        stats["errors"] += 1
        return stats

    for e in data.get("entities", []):
        try:
            et_str = e.get("entity_type", "concept")
            et = TYPE_MAP.get(et_str, EntityType.CONCEPT)
            created = e.get("created_at", datetime.now().isoformat())
            updated = e.get("updated_at", datetime.now().isoformat())
            try:
                created_dt = datetime.fromisoformat(created)
            except (ValueError, TypeError):
                created_dt = datetime.now()
            try:
                updated_dt = datetime.fromisoformat(updated)
            except (ValueError, TypeError):
                updated_dt = datetime.now()
            entity = Entity(
                id=e.get("id") or entity_id(e["name"], et.value),
                name=e["name"],
                entity_type=et,
                description=e.get("description", ""),
                domains=e.get("domains", []),
                aliases=e.get("aliases", []),
                metadata=e.get("metadata", {}),
                mention_count=1,
                source_count=1,
                last_seen=updated_dt,
                created=created_dt,
            )
            store.upsert_entity(entity)
            stats["entities"] += 1
        except Exception as ex:
            logger.warning(f"Skip entity {e.get('name')}: {ex}")
            stats["errors"] += 1

    for r in data.get("relationships", []):
        try:
            rt_str = r.get("relationship_type", "related_to")
            try:
                rt = RelationshipType(rt_str)
            except ValueError:
                rt = RelationshipType.RELATED_TO
            created = r.get("created_at", datetime.now().isoformat())
            try:
                created_dt = datetime.fromisoformat(created)
            except (ValueError, TypeError):
                created_dt = datetime.now()
            rel = Relationship(
                source_id=r["source_id"],
                target_id=r["target_id"],
                relationship_type=rt,
                strength=r.get("strength", 1.0),
                context=r.get("context", ""),
                mention_count=1,
                created=created_dt,
                last_seen=created_dt,
            )
            store.upsert_relationship(rel)
            stats["relationships"] += 1
        except Exception as ex:
            logger.warning(f"Skip relationship: {ex}")
            stats["errors"] += 1

    store.recompute_all_authority()
    logger.info(f"Entity migration: {stats['entities']} entities, {stats['relationships']} relationships")
    return stats
