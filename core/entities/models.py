"""
Unified Entity and Relationship data models.

Shared across knowledge graph, pattern engine, Mem0, and future consumers.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


def entity_id(name: str, entity_type: str) -> str:
    """Deterministic stable ID from name and type."""
    normalized = re.sub(r"[^a-z0-9]+", "_", name.lower().strip())
    raw = f"{entity_type}:{normalized}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


class EntityType(str, Enum):
    CONCEPT = "concept"
    TOOL = "tool"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    PROJECT = "project"
    PERSON = "person"
    FILE = "file"
    PATTERN = "pattern"
    BOOK = "book"
    TOPIC = "topic"
    ORGANIZATION = "organization"
    # Legacy / co-occurrence
    CO_OCCURS_WITH = "co_occurs_with"


class RelationshipType(str, Enum):
    RELATED_TO = "related_to"
    USES = "uses"
    IMPLEMENTS = "implements"
    PART_OF = "part_of"
    INSPIRES = "inspires"
    TEACHES = "teaches"
    DEPENDS_ON = "depends_on"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    AUTHORED_BY = "authored_by"
    CO_OCCURS_WITH = "co_occurs_with"  # Legacy from old graph


@dataclass
class Entity:
    """A node in Polly's knowledge graph."""

    id: str
    name: str
    entity_type: EntityType

    description: str = ""
    aliases: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    mention_count: int = 0
    source_count: int = 0
    authority_score: float = 0.0
    last_seen: datetime = field(default_factory=datetime.now)
    created: datetime = field(default_factory=datetime.now)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value if isinstance(self.entity_type, EntityType) else self.entity_type,
            "description": self.description,
            "aliases": self.aliases,
            "domains": self.domains,
            "tags": self.tags,
            "mention_count": self.mention_count,
            "source_count": self.source_count,
            "authority_score": self.authority_score,
            "last_seen": self.last_seen.isoformat() if isinstance(self.last_seen, datetime) else self.last_seen,
            "created": self.created.isoformat() if isinstance(self.created, datetime) else self.created,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        d = dict(data)
        for dt in ("last_seen", "created"):
            v = d.get(dt)
            if isinstance(v, str):
                try:
                    d[dt] = datetime.fromisoformat(v)
                except (ValueError, TypeError):
                    d[dt] = datetime.now()
            elif v is None:
                d[dt] = datetime.now()
        et = d.get("entity_type", "concept")
        if isinstance(et, str):
            try:
                d["entity_type"] = EntityType(et)
            except ValueError:
                d["entity_type"] = EntityType.CONCEPT
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Relationship:
    """An edge in the knowledge graph."""

    source_id: str
    target_id: str
    relationship_type: RelationshipType

    strength: float = 1.0
    context: str = ""
    bidirectional: bool = False
    mention_count: int = 1
    created: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value if isinstance(self.relationship_type, RelationshipType) else self.relationship_type,
            "strength": self.strength,
            "context": self.context,
            "bidirectional": self.bidirectional,
            "mention_count": self.mention_count,
            "created": self.created.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        d = dict(data)
        for dt in ("created", "last_seen"):
            v = d.get(dt)
            if isinstance(v, str):
                try:
                    d[dt] = datetime.fromisoformat(v)
                except (ValueError, TypeError):
                    d[dt] = datetime.now()
        rt = d.get("relationship_type", "related_to")
        if isinstance(rt, str):
            try:
                d["relationship_type"] = RelationshipType(rt)
            except ValueError:
                d["relationship_type"] = RelationshipType.RELATED_TO
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class EntityQuery:
    """Query for searching entities."""

    text: Optional[str] = None
    entity_types: Optional[List[EntityType]] = None
    domains: Optional[List[str]] = None
    min_authority: float = 0.0
    limit: int = 20
    include_relationships: bool = False
    max_hops: int = 1
