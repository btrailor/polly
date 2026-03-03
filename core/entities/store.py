"""
SQLite-backed entity storage with graph operations.

Replaces JSON-based KnowledgeGraph from learners/graph.py.
"""

from __future__ import annotations

import json
import logging
import math
import sqlite3
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import Entity, EntityQuery, EntityType, Relationship, RelationshipType

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT DEFAULT '',
    aliases TEXT DEFAULT '[]',
    domains TEXT DEFAULT '[]',
    tags TEXT DEFAULT '[]',
    mention_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    authority_score REAL DEFAULT 0.0,
    last_seen TEXT NOT NULL,
    created TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_authority ON entities(authority_score DESC);
CREATE INDEX IF NOT EXISTS idx_entities_domains ON entities(domains);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    context TEXT DEFAULT '',
    bidirectional INTEGER DEFAULT 0,
    mention_count INTEGER DEFAULT 1,
    created TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    UNIQUE(source_id, target_id, relationship_type)
);
CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id);
CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(relationship_type);

CREATE TABLE IF NOT EXISTS entity_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    context TEXT DEFAULT '',
    created TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mentions_entity ON entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_mentions_source ON entity_mentions(source_type, source_id);
"""


def _entity_from_row(row: tuple, cols: List[str]) -> Entity:
    d = dict(zip(cols, row))
    d["aliases"] = json.loads(d["aliases"] or "[]")
    d["domains"] = json.loads(d["domains"] or "[]")
    d["tags"] = json.loads(d["tags"] or "[]")
    d["metadata"] = json.loads(d["metadata"] or "{}")
    for dt in ("last_seen", "created"):
        try:
            d[dt] = datetime.fromisoformat(d[dt])
        except (ValueError, TypeError):
            d[dt] = datetime.now()
    try:
        d["entity_type"] = EntityType(d["entity_type"])
    except ValueError:
        d["entity_type"] = EntityType.CONCEPT
    return Entity(**d)


def _entity_to_row(entity: Entity) -> tuple:
    return (
        entity.id,
        entity.name,
        entity.entity_type.value,
        entity.description or "",
        json.dumps(entity.aliases),
        json.dumps(entity.domains),
        json.dumps(entity.tags),
        entity.mention_count,
        entity.source_count,
        entity.authority_score,
        entity.last_seen.isoformat(),
        entity.created.isoformat(),
        json.dumps(entity.metadata),
    )


class EntityStore:
    """SQLite-backed entity storage with graph operations."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            for stmt in SCHEMA.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(stmt)
        logger.debug(f"EntityStore initialized at {self.db_path}")

    # === CRUD ===

    def upsert_entity(self, entity: Entity) -> Entity:
        """Insert or update. If exists, merge and increment mention_count."""
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT id, mention_count, source_count FROM entities WHERE id = ?",
                (entity.id,),
            )
            row = cur.fetchone()
            if row:
                eid, mentions, sources = row
                conn.execute(
                    """
                    UPDATE entities SET
                        name = ?, entity_type = ?, description = ?,
                        aliases = ?, domains = ?, tags = ?,
                        mention_count = mention_count + ?,
                        source_count = source_count + 1,
                        last_seen = ?, metadata = ?
                    WHERE id = ?
                    """,
                    (
                        entity.name,
                        entity.entity_type.value,
                        entity.description,
                        json.dumps(entity.aliases),
                        json.dumps(entity.domains),
                        json.dumps(entity.tags),
                        max(0, entity.mention_count),
                        entity.last_seen.isoformat(),
                        json.dumps(entity.metadata),
                        entity.id,
                    ),
                )
                entity.mention_count = mentions + max(1, entity.mention_count)
                entity.source_count = sources + 1
            else:
                conn.execute(
                    """
                    INSERT INTO entities (
                        id, name, entity_type, description, aliases, domains, tags,
                        mention_count, source_count, authority_score, last_seen, created, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    _entity_to_row(entity),
                )
                if entity.mention_count == 0:
                    entity.mention_count = 1
                if entity.source_count == 0:
                    entity.source_count = 1
            conn.commit()
        self.recompute_authority(entity.id)
        return entity

    def upsert_relationship(self, relationship: Relationship) -> Relationship:
        """Insert or update relationship. If exists, increment mention_count and update strength."""
        with self._conn() as conn:
            cur = conn.execute(
                """
                SELECT id, mention_count, strength FROM relationships
                WHERE source_id = ? AND target_id = ? AND relationship_type = ?
                """,
                (
                    relationship.source_id,
                    relationship.target_id,
                    relationship.relationship_type.value,
                ),
            )
            row = cur.fetchone()
            if row:
                rid, mentions, old_strength = row
                new_strength = min(1.0, old_strength * 0.9 + relationship.strength * 0.1)
                conn.execute(
                    """
                    UPDATE relationships SET
                        strength = ?, mention_count = mention_count + ?,
                        context = COALESCE(NULLIF(?, ''), context), last_seen = ?
                    WHERE id = ?
                    """,
                    (
                        new_strength,
                        relationship.mention_count,
                        relationship.context,
                        relationship.last_seen.isoformat(),
                        rid,
                    ),
                )
                relationship.strength = new_strength
                relationship.mention_count = mentions + relationship.mention_count
            else:
                conn.execute(
                    """
                    INSERT INTO relationships (
                        source_id, target_id, relationship_type, strength, context,
                        bidirectional, mention_count, created, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        relationship.source_id,
                        relationship.target_id,
                        relationship.relationship_type.value,
                        relationship.strength,
                        relationship.context,
                        1 if relationship.bidirectional else 0,
                        relationship.mention_count,
                        relationship.created.isoformat(),
                        relationship.last_seen.isoformat(),
                    ),
                )
            conn.commit()
        return relationship

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        cur = self._conn().execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
        row = cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return _entity_from_row(row, cols)

    def get_entity_by_name(self, name: str, entity_type: Optional[EntityType] = None) -> Optional[Entity]:
        name_lower = name.lower().strip()
        if entity_type is not None:
            cur = self._conn().execute(
                "SELECT * FROM entities WHERE LOWER(name) = ? AND entity_type = ?",
                (name_lower, entity_type.value),
            )
        else:
            cur = self._conn().execute("SELECT * FROM entities WHERE LOWER(name) = ?", (name_lower,))
        row = cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return _entity_from_row(row, cols)

    def delete_entity(self, entity_id: str) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM entity_mentions WHERE entity_id = ?", (entity_id,))
            conn.execute("DELETE FROM relationships WHERE source_id = ? OR target_id = ?", (entity_id, entity_id))
            conn.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            conn.commit()

    def record_mention(self, entity_id: str, source_type: str, source_id: str, context: str = "") -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO entity_mentions (entity_id, source_type, source_id, context, created) VALUES (?, ?, ?, ?, ?)",
                (entity_id, source_type, source_id, context, datetime.now().isoformat()),
            )
            conn.execute(
                "UPDATE entities SET mention_count = mention_count + 1, last_seen = ? WHERE id = ?",
                (datetime.now().isoformat(), entity_id),
            )
            conn.commit()

    # === Search ===

    def search(self, query: EntityQuery) -> List[Entity]:
        params: List[Any] = []
        clauses: List[str] = ["1=1"]

        if query.text:
            clauses.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ?)")
            t = f"%{query.text.lower()}%"
            params.extend([t, t])
        if query.entity_types:
            placeholders = ",".join("?" * len(query.entity_types))
            clauses.append(f"entity_type IN ({placeholders})")
            params.extend([et.value for et in query.entity_types])
        if query.domains:
            # domains stored as JSON array; match any of the given domains (OR)
            domain_conds = " OR ".join("domains LIKE ?" for _ in query.domains)
            clauses.append(f"({domain_conds})")
            params.extend(f"%{d}%" for d in query.domains)
        if query.min_authority > 0:
            clauses.append("authority_score >= ?")
            params.append(query.min_authority)

        sql = "SELECT * FROM entities WHERE " + " AND ".join(clauses) + " ORDER BY authority_score DESC LIMIT ?"
        params.append(query.limit)

        conn = self._conn()
        cur = conn.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [_entity_from_row(row, cols) for row in cur.fetchall()]

    # === Graph operations ===

    def _get_neighbor_rels(self, entity_id: str) -> List[Tuple[Relationship, str]]:
        """Get all relationships (out and in) for an entity. Returns (rel, other_id)."""
        out: List[Tuple[Relationship, str]] = []
        with self._conn() as conn:
            for direction, col in (("source_id", "target_id"), ("target_id", "source_id")):
                cur = conn.execute(
                    f"""
                    SELECT source_id, target_id, relationship_type, strength, context, bidirectional, mention_count, created, last_seen
                    FROM relationships WHERE {direction} = ?
                    """,
                    (entity_id,),
                )
                for row in cur.fetchall():
                    rel = Relationship(
                        source_id=row[0],
                        target_id=row[1],
                        relationship_type=RelationshipType(row[2]),
                        strength=row[3],
                        context=row[4] or "",
                        bidirectional=bool(row[5]),
                        mention_count=row[6],
                        created=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                        last_seen=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
                    )
                    other = row[1] if direction == "source_id" else row[0]
                    out.append((rel, other))
        return out

    def get_related(
        self,
        entity_id: str,
        max_hops: int = 1,
        min_strength: float = 0.3,
    ) -> List[Tuple[Entity, Relationship]]:
        """Get entities related to this one, up to max_hops."""
        results: List[Tuple[Entity, Relationship]] = []
        visited: set = {entity_id}
        frontier: deque = deque([(entity_id, 0)])
        seen_pairs: set = set()

        while frontier:
            eid, hop = frontier.popleft()
            if hop >= max_hops:
                continue
            for rel, other_id in self._get_neighbor_rels(eid):
                if rel.strength < min_strength:
                    continue
                if other_id in visited:
                    continue
                key = (eid, other_id, rel.relationship_type.value)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                ent = self.get_entity(other_id)
                if ent:
                    results.append((ent, rel))
                    visited.add(other_id)
                    frontier.append((other_id, hop + 1))

        return results

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_hops: int = 4,
    ) -> Optional[List[Tuple[Entity, Relationship]]]:
        """Shortest path between two entities (BFS). Returns list of (Entity, Relationship) from source toward target."""
        if source_id == target_id:
            e = self.get_entity(source_id)
            return [(e, None)] if e else None  # type: ignore

        visited = {source_id}
        queue: deque = deque([(source_id, [])])

        while queue:
            current, path = queue.popleft()
            if len(path) >= max_hops:
                continue
            for rel, other_id in self._get_neighbor_rels(current):
                if other_id in visited:
                    continue
                visited.add(other_id)
                new_path = path + [(other_id, rel)]
                if other_id == target_id:
                    out: List[Tuple[Entity, Relationship]] = []
                    prev_id = source_id
                    for (eid, r) in new_path:
                        ent = self.get_entity(eid)
                        if ent and r:
                            out.append((ent, r))
                    return out
                queue.append((other_id, new_path))
        return None

    def get_cross_domain_bridges(self, domain_a: str, domain_b: str, limit: int = 10) -> List[Entity]:
        """Entities that have domains containing both domain_a and domain_b, or that link entities in both."""
        conn = self._conn()
        cur = conn.execute(
            """
            SELECT * FROM entities
            WHERE domains LIKE ? AND domains LIKE ?
            ORDER BY authority_score DESC
            LIMIT ?
            """,
            (f"%{domain_a}%", f"%{domain_b}%", limit),
        )
        cols = [d[0] for d in cur.description]
        return [_entity_from_row(row, cols) for row in cur.fetchall()]

    # === Authority ===

    def recompute_authority(self, entity_id: Optional[str] = None) -> None:
        """Recompute authority for one entity or all."""
        conn = self._conn()

        if entity_id:
            cur = conn.execute(
                "SELECT MAX(mention_count), MAX(source_count) FROM entities"
            )
            row = cur.fetchone()
            max_mentions = (row[0] or 0) or 1
            max_sources = (row[1] or 0) or 1
            cur = conn.execute(
                "SELECT id, mention_count, source_count, last_seen FROM entities WHERE id = ?",
                (entity_id,),
            )
            row = cur.fetchone()
            if not row:
                return
            eid, mentions, sources, last_seen = row
            cur2 = conn.execute(
                "SELECT COUNT(*) FROM relationships WHERE source_id = ? OR target_id = ?",
                (eid, eid),
            )
            rel_count = cur2.fetchone()[0]
            cur2 = conn.execute("SELECT MAX(cnt) FROM (SELECT COUNT(*) AS cnt FROM relationships GROUP BY source_id)")
            max_rel = (cur2.fetchone()[0] or 0) or 1
            try:
                ls = datetime.fromisoformat(last_seen) if last_seen else datetime.now()
            except (ValueError, TypeError):
                ls = datetime.now()
            days_ago = (datetime.now() - ls).days
            recency = max(0.0, 1.0 - days_ago / 90.0)
            authority = (
                0.4 * math.log(mentions + 1) / math.log(max_mentions + 1)
                + 0.3 * math.log(sources + 1) / math.log(max_sources + 1)
                + 0.2 * (rel_count / max_rel)
                + 0.1 * recency
            )
            conn.execute("UPDATE entities SET authority_score = ? WHERE id = ?", (min(1.0, authority), eid))
            conn.commit()
            return

        cur = conn.execute("SELECT MAX(mention_count), MAX(source_count) FROM entities")
        row = cur.fetchone()
        max_mentions = (row[0] or 0) or 1
        max_sources = (row[1] or 0) or 1
        cur = conn.execute("SELECT MAX(cnt) FROM (SELECT COUNT(*) AS cnt FROM relationships GROUP BY source_id)")
        max_rel = (cur.fetchone()[0] or 0) or 1

        cur = conn.execute("SELECT id, mention_count, source_count, last_seen FROM entities")
        now = datetime.now()
        updates = []
        for row in cur.fetchall():
            eid, mentions, sources, last_seen = row
            cur2 = conn.execute(
                "SELECT COUNT(*) FROM relationships WHERE source_id = ? OR target_id = ?",
                (eid, eid),
            )
            rel_count = cur2.fetchone()[0]
            try:
                ls = datetime.fromisoformat(last_seen) if last_seen else now
            except (ValueError, TypeError):
                ls = now
            days_ago = (now - ls).days
            recency = max(0.0, 1.0 - days_ago / 90.0)
            authority = (
                0.4 * math.log(mentions + 1) / math.log(max_mentions + 1)
                + 0.3 * math.log(sources + 1) / math.log(max_sources + 1)
                + 0.2 * (rel_count / max_rel)
                + 0.1 * recency
            )
            updates.append((min(1.0, authority), eid))
        for score, eid in updates:
            conn.execute("UPDATE entities SET authority_score = ? WHERE id = ?", (score, eid))
        conn.commit()

    def recompute_all_authority(self) -> None:
        self.recompute_authority(None)

    # === Stats ===

    def get_stats(self) -> Dict[str, Any]:
        with self._conn() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM entities")
            entities = cur.fetchone()[0]
            cur = conn.execute("SELECT COUNT(*) FROM relationships")
            rels = cur.fetchone()[0]
            cur = conn.execute(
                "SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type"
            )
            by_type = dict(cur.fetchall())
        return {
            "entities": entities,
            "relationships": rels,
            "entity_types": by_type,
        }

    def get_top_entities(self, limit: int = 20, entity_type: Optional[EntityType] = None) -> List[Entity]:
        if entity_type is not None:
            cur = self._conn().execute(
                "SELECT * FROM entities WHERE entity_type = ? ORDER BY authority_score DESC LIMIT ?",
                (entity_type.value, limit),
            )
        else:
            cur = self._conn().execute(
                "SELECT * FROM entities ORDER BY authority_score DESC LIMIT ?",
                (limit,),
            )
        cols = [d[0] for d in cur.description]
        return [_entity_from_row(row, cols) for row in cur.fetchall()]

    # === Garden Operations ===

    def get_mentions_for_source(self, source_id: str, source_type: str) -> List[Dict[str, Any]]:
        """Get all entity mentions for a given source (note, conversation, etc.)."""
        conn = self._conn()
        cur = conn.execute(
            """
            SELECT em.entity_id, em.context, e.name, e.entity_type, e.authority_score
            FROM entity_mentions em
            JOIN entities e ON em.entity_id = e.id
            WHERE em.source_type = ? AND em.source_id = ?
            ORDER BY e.authority_score DESC
            """,
            (source_type, source_id),
        )
        results = []
        for row in cur.fetchall():
            results.append({
                "entity_id": row[0],
                "context": row[1],
                "name": row[2],
                "entity_type": row[3],
                "authority_score": row[4],
            })
        return results

    def move_mentions(self, source_id: str, target_id: str) -> int:
        """Move all mentions from source entity to target entity (for merging)."""
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM entity_mentions WHERE entity_id = ?",
                (source_id,),
            )
            count = cur.fetchone()[0]
            
            conn.execute(
                "UPDATE entity_mentions SET entity_id = ? WHERE entity_id = ?",
                (target_id, source_id),
            )
            
            conn.execute(
                "UPDATE entities SET mention_count = mention_count + ? WHERE id = ?",
                (count, target_id),
            )
            
            conn.commit()
        return count

    def prune_weak_relationships(self, threshold: float = 0.3) -> int:
        """Remove relationships below strength threshold."""
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM relationships WHERE strength < ?",
                (threshold,),
            )
            count = cur.fetchone()[0]
            
            conn.execute(
                "DELETE FROM relationships WHERE strength < ?",
                (threshold,),
            )
            
            conn.commit()
        logger.info(f"Pruned {count} weak relationships (threshold={threshold})")
        return count

    def prune_stale_entities(self, days_threshold: int = 180) -> int:
        """Remove entities not seen in X days with low mention counts."""
        cutoff = (datetime.now() - timedelta(days=days_threshold)).isoformat()
        with self._conn() as conn:
            cur = conn.execute(
                """
                SELECT COUNT(*) FROM entities 
                WHERE last_seen < ? AND mention_count < 3
                """,
                (cutoff,),
            )
            count = cur.fetchone()[0]
            
            cur = conn.execute(
                """
                SELECT id FROM entities 
                WHERE last_seen < ? AND mention_count < 3
                """,
                (cutoff,),
            )
            stale_ids = [row[0] for row in cur.fetchall()]
            
            for entity_id in stale_ids:
                self.delete_entity(entity_id)
            
            conn.commit()
        logger.info(f"Pruned {count} stale entities (>{days_threshold} days, <3 mentions)")
        return count

    def remove_relationship(self, source_id: str, target_id: str, relationship_type: Optional[RelationshipType] = None) -> bool:
        """Remove a specific relationship between two entities."""
        with self._conn() as conn:
            if relationship_type:
                cur = conn.execute(
                    "DELETE FROM relationships WHERE source_id = ? AND target_id = ? AND relationship_type = ?",
                    (source_id, target_id, relationship_type.value),
                )
            else:
                cur = conn.execute(
                    "DELETE FROM relationships WHERE source_id = ? AND target_id = ?",
                    (source_id, target_id),
                )
            deleted = cur.rowcount > 0
            conn.commit()
        return deleted

    # === Isolation Detection (Phase 12b Wave 2) ===

    def get_isolated_entities(self, max_connections: int = 2) -> List[Dict[str, Any]]:
        """Return entities with <= max_connections total relationships.

        Includes: entity info, connection_count, last_mentioned_at.
        Ordered by connection_count ASC, then authority ASC.
        """
        conn = self._conn()
        cur = conn.execute(
            """
            SELECT e.id, e.name, e.entity_type, e.authority_score, e.mention_count,
                   e.last_seen,
                   COALESCE(rc.cnt, 0) AS connection_count
            FROM entities e
            LEFT JOIN (
                SELECT entity_id, COUNT(*) AS cnt
                FROM (
                    SELECT source_id AS entity_id FROM relationships
                    UNION ALL
                    SELECT target_id AS entity_id FROM relationships
                )
                GROUP BY entity_id
            ) rc ON rc.entity_id = e.id
            WHERE COALESCE(rc.cnt, 0) <= ?
            ORDER BY connection_count ASC, e.authority_score ASC
            """,
            (max_connections,),
        )
        results = []
        for row in cur.fetchall():
            results.append({
                "id": row[0],
                "name": row[1],
                "entity_type": row[2],
                "authority_score": row[3],
                "mention_count": row[4],
                "last_seen": row[5],
                "connection_count": row[6],
            })
        return results

    def get_isolated_notes(self, max_entity_connections: int = 2) -> List[Dict[str, Any]]:
        """Return notes where ALL extracted entities have <= max_entity_connections.

        A note is 'isolated' if none of its entities are well-connected.
        Returns: note path (source_id), entity_count, max_connection_count.
        """
        conn = self._conn()
        # For each note (source_type='note'), get its entities and their connection counts.
        # A note is isolated if its max entity connection count <= threshold.
        cur = conn.execute(
            """
            SELECT em.source_id,
                   COUNT(DISTINCT em.entity_id) AS entity_count,
                   MAX(COALESCE(rc.cnt, 0)) AS max_connection_count
            FROM entity_mentions em
            LEFT JOIN (
                SELECT entity_id, COUNT(*) AS cnt
                FROM (
                    SELECT source_id AS entity_id FROM relationships
                    UNION ALL
                    SELECT target_id AS entity_id FROM relationships
                )
                GROUP BY entity_id
            ) rc ON rc.entity_id = em.entity_id
            WHERE em.source_type = 'note'
            GROUP BY em.source_id
            HAVING MAX(COALESCE(rc.cnt, 0)) <= ?
            ORDER BY max_connection_count ASC, entity_count ASC
            """,
            (max_entity_connections,),
        )
        results = []
        for row in cur.fetchall():
            results.append({
                "source_id": row[0],
                "entity_count": row[1],
                "max_connection_count": row[2],
            })
        return results

    # === Authority Scheduling (Phase 12b Wave 2) ===

    def _ensure_metadata_table(self) -> None:
        """Create metadata key-value table if not exists."""
        with self._conn() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.commit()

    def _get_metadata(self, key: str) -> Optional[str]:
        """Get a metadata value by key."""
        self._ensure_metadata_table()
        conn = self._conn()
        cur = conn.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def _set_metadata(self, key: str, value: str) -> None:
        """Set a metadata value."""
        self._ensure_metadata_table()
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()

    def maybe_recompute_authority(self, interval_hours: int = 24) -> bool:
        """Recompute authority for all entities if last recompute was > interval_hours ago.

        Returns True if recomputation ran, False if skipped.
        """
        last_str = self._get_metadata("last_authority_recompute")
        if last_str:
            try:
                last = datetime.fromisoformat(last_str)
                if (datetime.now() - last) < timedelta(hours=interval_hours):
                    logger.debug("Authority recompute skipped (still fresh)")
                    return False
            except (ValueError, TypeError):
                pass  # Invalid timestamp, recompute anyway

        logger.info("Running scheduled authority recomputation")
        self.recompute_authority(None)
        self._set_metadata("last_authority_recompute", datetime.now().isoformat())
        return True
