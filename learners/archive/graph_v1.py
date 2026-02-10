"""
Apollo Personal Knowledge Graph
Builds connections between concepts, files, and patterns

This creates a web of understanding that grows with you,
connecting ideas across your five domains.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Union
from collections import defaultdict
import json
import re
import logging

logger = logging.getLogger(__name__)


def _domains_to_strings(domains) -> List[str]:
    """Convert domains to list of strings, handling both DomainType enums and strings."""
    if not domains:
        return []
    
    result = []
    for d in domains:
        if hasattr(d, 'value'):  # DomainType enum
            result.append(d.value)
        elif isinstance(d, str):
            result.append(d)
        else:
            logger.warning(f"Unknown domain type: {type(d)}")
    return result


@dataclass
class Entity:
    """A node in the knowledge graph."""
    id: str
    name: str
    entity_type: str  # "concept", "project", "tool", "pattern", "person", "file"
    description: str = ""
    domains: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """An edge in the knowledge graph."""
    source_id: str
    target_id: str
    relationship_type: str  # "related_to", "uses", "implements", "inspires", "part_of"
    strength: float = 1.0  # 0-1, based on co-occurrence and explicit links
    context: str = ""  # Why they're related
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeGraph:
    """
    A personal knowledge graph that:
    - Extracts entities from your notes and code
    - Builds relationships from explicit links and co-occurrence
    - Enables graph-based queries ("what connects X to Y?")
    - Grows and refines over time
    """

    # Entity types to extract
    ENTITY_TYPES = {
        'concept': [
            'infinite game', 'finite game', 'constraint', 'emergence',
            'systems thinking', 'polymathic', 'popular education'
        ],
        'tool': [
            'norns', 'supercollider', 'docker', 'obsidian', 'ollama',
            'python', 'rust', 'lua', 'javascript'
        ],
        'pattern': [
            'factory', 'observer', 'state machine', 'callback', 'async'
        ],
        'framework': [
            'freire', 'pedagogy', 'design thinking', 'agile'
        ]
    }

    def __init__(self, storage_path: Path, auto_link_threshold: float = 0.7):
        self.storage_path = Path(storage_path)
        self.auto_link_threshold = auto_link_threshold

        # Graph storage
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []

        # Indexes for efficient lookup
        self._entity_by_name: Dict[str, str] = {}  # name -> id
        self._relationships_from: Dict[str, List[Relationship]] = defaultdict(list)
        self._relationships_to: Dict[str, List[Relationship]] = defaultdict(list)

        # Co-occurrence tracking for auto-linking
        self._cooccurrence: Dict[Tuple[str, str], int] = defaultdict(int)

        self._load_graph()

    def _load_graph(self):
        """Load graph from storage."""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())

                for e in data.get('entities', []):
                    entity = Entity(
                        id=e['id'],
                        name=e['name'],
                        entity_type=e['entity_type'],
                        description=e.get('description', ''),
                        domains=e.get('domains', []),
                        aliases=e.get('aliases', []),
                        metadata=e.get('metadata', {}),
                        created_at=datetime.fromisoformat(e.get('created_at', datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(e.get('updated_at', datetime.now().isoformat()))
                    )
                    self.entities[entity.id] = entity
                    self._entity_by_name[entity.name.lower()] = entity.id
                    for alias in entity.aliases:
                        self._entity_by_name[alias.lower()] = entity.id

                for r in data.get('relationships', []):
                    rel = Relationship(
                        source_id=r['source_id'],
                        target_id=r['target_id'],
                        relationship_type=r['relationship_type'],
                        strength=r.get('strength', 1.0),
                        context=r.get('context', ''),
                        created_at=datetime.fromisoformat(r.get('created_at', datetime.now().isoformat()))
                    )
                    self.relationships.append(rel)
                    self._relationships_from[rel.source_id].append(rel)
                    self._relationships_to[rel.target_id].append(rel)

                self._cooccurrence = {
                    tuple(k.split('|')): v
                    for k, v in data.get('cooccurrence', {}).items()
                }

                logger.info(f"Loaded graph with {len(self.entities)} entities, {len(self.relationships)} relationships")

            except Exception as e:
                logger.error(f"Error loading graph: {e}")

    def save_graph(self):
        """Save graph to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'entities': [
                {
                    'id': e.id,
                    'name': e.name,
                    'entity_type': e.entity_type,
                    'description': e.description,
                    'domains': e.domains,
                    'aliases': e.aliases,
                    'metadata': e.metadata,
                    'created_at': e.created_at.isoformat(),
                    'updated_at': e.updated_at.isoformat()
                }
                for e in self.entities.values()
            ],
            'relationships': [
                {
                    'source_id': r.source_id,
                    'target_id': r.target_id,
                    'relationship_type': r.relationship_type,
                    'strength': r.strength,
                    'context': r.context,
                    'created_at': r.created_at.isoformat()
                }
                for r in self.relationships
            ],
            'cooccurrence': {
                f"{k[0]}|{k[1]}": v
                for k, v in self._cooccurrence.items()
            }
        }

        self.storage_path.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved graph with {len(self.entities)} entities")

    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = "",
        domains = None,
        aliases: List[str] = None
    ) -> Entity:
        """Add or update an entity in the graph."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains) if domains else []
        
        entity_id = self._normalize_id(name)

        if entity_id in self.entities:
            # Update existing
            entity = self.entities[entity_id]
            entity.updated_at = datetime.now()
            if description:
                entity.description = description
            if domain_strs:
                entity.domains = list(set(entity.domains + domain_strs))
            if aliases:
                entity.aliases = list(set(entity.aliases + aliases))
                for alias in aliases:
                    self._entity_by_name[alias.lower()] = entity_id
        else:
            # Create new
            entity = Entity(
                id=entity_id,
                name=name,
                entity_type=entity_type,
                description=description,
                domains=domain_strs,
                aliases=aliases or []
            )
            self.entities[entity_id] = entity
            self._entity_by_name[name.lower()] = entity_id
            for alias in (aliases or []):
                self._entity_by_name[alias.lower()] = entity_id

        return entity

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str = "related_to",
        strength: float = 1.0,
        context: str = ""
    ) -> Optional[Relationship]:
        """Add a relationship between entities."""
        source_id = self._find_entity_id(source)
        target_id = self._find_entity_id(target)

        if not source_id or not target_id:
            logger.warning(f"Could not find entities for relationship: {source} -> {target}")
            return None

        # Check if relationship already exists
        for rel in self._relationships_from[source_id]:
            if rel.target_id == target_id and rel.relationship_type == relationship_type:
                # Update strength
                rel.strength = min(rel.strength + 0.1, 1.0)
                return rel

        # Create new relationship
        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength,
            context=context
        )
        self.relationships.append(rel)
        self._relationships_from[source_id].append(rel)
        self._relationships_to[target_id].append(rel)

        return rel

    def extract_entities_from_text(self, text: str, domains = None) -> List[Entity]:
        """Extract and add entities from text content."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains) if domains else []
        
        extracted = []
        text_lower = text.lower()

        # Extract known entity types
        for entity_type, keywords in self.ENTITY_TYPES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entity = self.add_entity(
                        name=keyword.title(),
                        entity_type=entity_type,
                        domains=domain_strs
                    )
                    extracted.append(entity)

        # Extract [[wiki-style links]] from Obsidian
        wiki_links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text)
        for link in wiki_links:
            entity = self.add_entity(
                name=link,
                entity_type='concept',
                domains=domain_strs
            )
            extracted.append(entity)

        # Track co-occurrence for auto-linking
        for i, e1 in enumerate(extracted):
            for e2 in extracted[i+1:]:
                pair = tuple(sorted([e1.id, e2.id]))
                self._cooccurrence[pair] += 1

        return extracted

    def build_auto_links(self):
        """Create relationships based on co-occurrence patterns."""
        for pair, count in self._cooccurrence.items():
            if count >= 3:  # Minimum co-occurrence threshold
                strength = min(count / 10, 1.0)
                if strength >= self.auto_link_threshold:
                    self.add_relationship(
                        source=pair[0],
                        target=pair[1],
                        relationship_type="co_occurs_with",
                        strength=strength,
                        context=f"Appeared together {count} times"
                    )

    def get_entity(self, name_or_id: str) -> Optional[Entity]:
        """Get an entity by name or ID."""
        entity_id = self._find_entity_id(name_or_id)
        return self.entities.get(entity_id)

    def get_related(
        self,
        entity: str,
        relationship_types: List[str] = None,
        max_depth: int = 1
    ) -> List[Tuple[Entity, Relationship]]:
        """Get entities related to the given entity."""
        entity_id = self._find_entity_id(entity)
        if not entity_id:
            return []

        results = []
        visited = {entity_id}
        to_visit = [(entity_id, 0)]

        while to_visit:
            current_id, depth = to_visit.pop(0)

            if depth >= max_depth:
                continue

            # Get outgoing relationships
            for rel in self._relationships_from.get(current_id, []):
                if relationship_types and rel.relationship_type not in relationship_types:
                    continue

                target = self.entities.get(rel.target_id)
                if target and rel.target_id not in visited:
                    results.append((target, rel))
                    visited.add(rel.target_id)
                    to_visit.append((rel.target_id, depth + 1))

            # Get incoming relationships
            for rel in self._relationships_to.get(current_id, []):
                if relationship_types and rel.relationship_type not in relationship_types:
                    continue

                source = self.entities.get(rel.source_id)
                if source and rel.source_id not in visited:
                    results.append((source, rel))
                    visited.add(rel.source_id)
                    to_visit.append((rel.source_id, depth + 1))

        return results

    def find_path(self, source: str, target: str, max_depth: int = 5) -> Optional[List[Entity]]:
        """Find a path between two entities."""
        source_id = self._find_entity_id(source)
        target_id = self._find_entity_id(target)

        if not source_id or not target_id:
            return None

        # BFS to find shortest path
        visited = {source_id}
        queue = [(source_id, [source_id])]

        while queue:
            current_id, path = queue.pop(0)

            if current_id == target_id:
                return [self.entities[eid] for eid in path]

            if len(path) >= max_depth:
                continue

            # Get all connected entities
            connected = set()
            for rel in self._relationships_from.get(current_id, []):
                connected.add(rel.target_id)
            for rel in self._relationships_to.get(current_id, []):
                connected.add(rel.source_id)

            for next_id in connected:
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))

        return None

    def get_context_for_query(self, query: str, domains = None, n_entities: int = 5) -> str:
        """Get relevant graph context for a query."""
        # Convert domains to strings
        domain_strs = _domains_to_strings(domains) if domains else []
        
        # Extract entities mentioned in query
        mentioned = self.extract_entities_from_text(query, domain_strs)

        if not mentioned:
            return ""

        context_parts = ["## Relevant Knowledge Graph Context\n"]

        for entity in mentioned[:3]:
            context_parts.append(f"\n### {entity.name} ({entity.entity_type})")
            if entity.description:
                context_parts.append(f"{entity.description}")

            related = self.get_related(entity.id, max_depth=1)
            if related:
                context_parts.append("\nRelated:")
                for rel_entity, rel in related[:5]:
                    context_parts.append(f"- {rel_entity.name} ({rel.relationship_type})")

        # Check for cross-domain connections
        if len(mentioned) >= 2:
            path = self.find_path(mentioned[0].id, mentioned[1].id)
            if path and len(path) > 2:
                context_parts.append(f"\nConnection path: {' → '.join(e.name for e in path)}")

        return "\n".join(context_parts)

    def _normalize_id(self, name: str) -> str:
        """Normalize a name to an ID."""
        return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

    def _find_entity_id(self, name_or_id: str) -> Optional[str]:
        """Find entity ID from name or ID."""
        if name_or_id in self.entities:
            return name_or_id

        return self._entity_by_name.get(name_or_id.lower())

    def get_stats(self) -> Dict:
        """Get graph statistics."""
        return {
            'entities': len(self.entities),
            'relationships': len(self.relationships),
            'entity_types': {
                et: sum(1 for e in self.entities.values() if e.entity_type == et)
                for et in set(e.entity_type for e in self.entities.values())
            }
        }
