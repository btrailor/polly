# Entity Model Unification — Design

**Last Updated:** February 2026

---

## Architecture Overview

```
core/entities/
├── __init__.py          # Public API: EntityStore, Entity, Relationship, EntityType
├── models.py            # Entity, Relationship, EntityType, EntityQuery
├── store.py             # EntityStore — SQLite-backed storage + graph operations
├── extractor.py         # EntityExtractor — unified extraction pipeline
├── context.py           # EntityContextBuilder — builds prompt context from graph
└── migration.py         # Migrate from learners/graph.py JSON format
```

Replaces:
- `learners/graph.py` (archived to `learners/archive/graph_v1.py`)
- Entity extraction code scattered across `learners/patterns.py` and `core/memory/mem0_adapter.py`

---

## Data Model

### `Entity`

```python
@dataclass
class Entity:
    """A node in Polly's knowledge graph.
    
    Represents any identifiable concept, tool, person, project, or artifact
    that Polly knows about. Shared across all systems.
    """
    id: str                          # Deterministic hash of (name, entity_type) or UUID
    name: str                        # Canonical name
    entity_type: EntityType          # Enum: see below
    
    # Description & context
    description: str = ""            # What this entity is
    aliases: list[str] = field(default_factory=list)  # Alternative names
    
    # Domain & classification
    domains: list[str] = field(default_factory=list)  # Which Polly domains
    tags: list[str] = field(default_factory=list)      # Free-form tags
    
    # Quality & authority
    mention_count: int = 0           # Times referenced in user content
    source_count: int = 0            # Number of distinct sources mentioning this
    authority_score: float = 0.0     # 0.0–1.0, computed from mention_count + source_count + recency
    last_seen: datetime = field(default_factory=datetime.now)
    created: datetime = field(default_factory=datetime.now)
    
    # Extensible metadata
    metadata: dict[str, Any] = field(default_factory=dict)
```

### `EntityType`

```python
class EntityType(str, Enum):
    CONCEPT = "concept"       # Abstract idea (infinite games, constraint, emergence)
    TOOL = "tool"             # Software tool (Docker, Obsidian, spaCy)
    LANGUAGE = "language"     # Programming language (Python, Rust, Lua)
    FRAMEWORK = "framework"   # Framework/library (FastAPI, React, PyTorch)
    PROJECT = "project"       # User's project
    PERSON = "person"         # Person referenced in notes
    FILE = "file"             # File or document
    PATTERN = "pattern"       # Cross-reference to Pattern system
    BOOK = "book"             # Book (for BookLore integration)
    TOPIC = "topic"           # Learning topic
    ORGANIZATION = "organization"  # Company, group, institution
```

### `Relationship`

```python
@dataclass
class Relationship:
    """An edge in the knowledge graph."""
    source_id: str                    # Entity ID
    target_id: str                    # Entity ID
    relationship_type: RelationshipType  # Enum: see below
    
    strength: float = 1.0            # 0.0–1.0, based on co-occurrence + explicit
    context: str = ""                # Why they're related
    bidirectional: bool = False      # True for "related_to", false for "uses"
    
    mention_count: int = 1           # Co-occurrence count
    created: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
```

### `RelationshipType`

```python
class RelationshipType(str, Enum):
    RELATED_TO = "related_to"       # General relationship
    USES = "uses"                   # A uses B (tool usage)
    IMPLEMENTS = "implements"       # A implements B (concept realization)
    PART_OF = "part_of"            # A is part of B
    INSPIRES = "inspires"          # A inspires B (cross-domain)
    TEACHES = "teaches"            # A teaches B (learning context)
    DEPENDS_ON = "depends_on"      # A depends on B
    CONTRADICTS = "contradicts"    # A contradicts B (epistemological)
    EXTENDS = "extends"            # A extends B
    AUTHORED_BY = "authored_by"    # Content authored by person
```

### `EntityQuery`

```python
@dataclass
class EntityQuery:
    """Query for searching entities."""
    text: Optional[str] = None             # Keyword/name search
    entity_types: Optional[list[EntityType]] = None
    domains: Optional[list[str]] = None
    min_authority: float = 0.0
    limit: int = 20
    include_relationships: bool = False     # Also return connected entities
    max_hops: int = 1                       # Relationship traversal depth
```

---

## SQLite Schema

```sql
-- Entity storage
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT DEFAULT '',
    aliases TEXT DEFAULT '[]',        -- JSON array
    domains TEXT DEFAULT '[]',        -- JSON array
    tags TEXT DEFAULT '[]',           -- JSON array
    mention_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    authority_score REAL DEFAULT 0.0,
    last_seen TEXT NOT NULL,
    created TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'        -- JSON object
);

CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_authority ON entities(authority_score DESC);

-- Relationship storage
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL REFERENCES entities(id),
    target_id TEXT NOT NULL REFERENCES entities(id),
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    context TEXT DEFAULT '',
    bidirectional INTEGER DEFAULT 0,
    mention_count INTEGER DEFAULT 1,
    created TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    UNIQUE(source_id, target_id, relationship_type)
);

CREATE INDEX idx_rel_source ON relationships(source_id);
CREATE INDEX idx_rel_target ON relationships(target_id);
CREATE INDEX idx_rel_type ON relationships(relationship_type);

-- Mention tracking (which sources mention which entities)
CREATE TABLE IF NOT EXISTS entity_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    source_type TEXT NOT NULL,        -- "note", "query", "response", "code", "book"
    source_id TEXT NOT NULL,          -- File path, conversation ID, etc.
    context TEXT DEFAULT '',          -- Surrounding text
    created TEXT NOT NULL
);

CREATE INDEX idx_mentions_entity ON entity_mentions(entity_id);
CREATE INDEX idx_mentions_source ON entity_mentions(source_type, source_id);
```

**Database location:** `~/.polly/entities.db` (new, separate from other SQLite databases)

---

## EntityStore

```python
class EntityStore:
    """SQLite-backed entity storage with graph operations.
    
    Replaces JSON-based KnowledgeGraph from learners/graph.py.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    # === CRUD ===
    
    def upsert_entity(self, entity: Entity) -> Entity:
        """Insert or update an entity. If exists, merge and increment mention_count."""
        ...
    
    def upsert_relationship(self, relationship: Relationship) -> Relationship:
        """Insert or update a relationship. If exists, increment mention_count and update strength."""
        ...
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        ...
    
    def get_entity_by_name(self, name: str, entity_type: Optional[EntityType] = None) -> Optional[Entity]:
        """Get entity by name (case-insensitive), optionally filtered by type."""
        ...
    
    def delete_entity(self, entity_id: str) -> None:
        """Delete entity and all its relationships."""
        ...
    
    # === Search ===
    
    def search(self, query: EntityQuery) -> list[Entity]:
        """Search entities by query criteria."""
        ...
    
    def get_related(self, entity_id: str, max_hops: int = 1, min_strength: float = 0.3) -> list[tuple[Entity, Relationship]]:
        """Get entities related to a given entity, up to N hops."""
        ...
    
    def find_path(self, source_id: str, target_id: str, max_hops: int = 4) -> Optional[list[tuple[Entity, Relationship]]]:
        """Find shortest path between two entities (BFS)."""
        ...
    
    def get_cross_domain_bridges(self, domain_a: str, domain_b: str, limit: int = 10) -> list[Entity]:
        """Find entities that bridge two domains."""
        ...
    
    # === Authority ===
    
    def recompute_authority(self, entity_id: Optional[str] = None) -> None:
        """Recompute authority scores. If entity_id given, just that one; otherwise all.
        
        Authority = f(mention_count, source_count, relationship_count, recency)
        """
        ...
    
    # === Stats ===
    
    def get_stats(self) -> dict:
        """Get graph statistics (entity count, relationship count, domain distribution)."""
        ...
    
    def get_top_entities(self, limit: int = 20, entity_type: Optional[EntityType] = None) -> list[Entity]:
        """Get top entities by authority score."""
        ...
```

---

## EntityExtractor

```python
class EntityExtractor:
    """Unified entity extraction pipeline.
    
    Consolidates extraction from three systems:
    1. spaCy NLP (primary) — from learners/patterns.py ConceptExtractor
    2. Technical term matching — from learners/patterns.py TECHNICAL_TERMS
    3. Regex patterns — from learners/graph.py (upgraded with NLP)
    
    Optional LLM-based extraction for high-value content (e.g., saved notes).
    """
    
    def __init__(self, entity_store: EntityStore, use_spacy: bool = True):
        self.store = entity_store
        self._nlp = None  # Lazy-loaded spaCy
    
    def extract_and_store(
        self,
        text: str,
        source_type: str,
        source_id: str,
        domains: Optional[list[str]] = None,
        extract_relationships: bool = True
    ) -> list[Entity]:
        """Extract entities from text and store them.
        
        Pipeline:
        1. spaCy NER for named entities (people, orgs, tools)
        2. Noun phrase extraction for concepts
        3. Technical term matching for tools/frameworks/languages
        4. Co-occurrence analysis for relationships
        5. Upsert entities and relationships to store
        6. Record mentions for authority tracking
        
        Returns list of extracted entities.
        """
        ...
    
    def extract_entities_only(self, text: str) -> list[Entity]:
        """Extract entities without storing (for preview/dry-run)."""
        ...
    
    def extract_relationships_from_cooccurrence(
        self,
        entities: list[Entity],
        window_size: int = 3  # sentences
    ) -> list[Relationship]:
        """Detect relationships from entity co-occurrence in text."""
        ...
```

---

## EntityContextBuilder

```python
class EntityContextBuilder:
    """Build prompt context from the knowledge graph.
    
    Replaces KnowledgeGraph.get_context_for_query() with richer graph-aware context.
    """
    
    def __init__(self, store: EntityStore):
        self.store = store
    
    def build_context(
        self,
        query: str,
        domains: list[str],
        max_entities: int = 10,
        include_relationships: bool = True,
        include_cross_domain: bool = True
    ) -> str:
        """Build knowledge graph context for system prompt.
        
        Steps:
        1. Extract entities from query
        2. Find matching entities in store (by name, alias, keyword)
        3. Get related entities (1 hop)
        4. If multiple domains, find cross-domain bridges
        5. Format as structured context block
        
        Returns formatted string for prompt injection.
        """
        ...
```

---

## Integration with PatternEngine

The `Pattern` model (from unified-pattern-engine) has an `entity_refs: list[str]` field. This connects patterns to entities:

```python
# When learning a pattern, also extract and link entities
def learn_from_query(self, query, domains, response):
    patterns = self._extract_patterns(query, response)
    
    # Extract entities and get their IDs
    entities = self.entity_extractor.extract_and_store(query + response, "query", conv_id, domains)
    entity_ids = [e.id for e in entities]
    
    # Link entities to patterns
    for pattern in patterns:
        pattern.entity_refs = entity_ids
    
    # Save patterns
    for pattern in patterns:
        self.learn(pattern)
```

This linkage enables future features:
- "What patterns involve concept X?" — join Pattern.entity_refs with Entity.id
- "What concepts does this pattern connect?" — resolve entity_refs to Entity objects
- Graph-based pattern discovery — find patterns that bridge entity clusters

---

## Migration from `learners/graph.py`

### Data Migration

1. Read `~/.polly/knowledge_graph.json`
2. For each old `Entity`:
   - Map fields to new `Entity` model
   - Assign `entity_type` from old `entity_type` string
   - Set initial `authority_score` based on existing relationship count
   - Store in new SQLite database
3. For each old `Relationship`:
   - Map to new `Relationship` model
   - Set `strength` from old value (or default)
4. Create backup of old JSON file
5. Log migration stats

### Code Migration

1. Create `core/entities/` package
2. Implement all classes
3. Update `core/polly.py`:
   - Replace `self.knowledge_graph = KnowledgeGraph(graph_path)` with `self.entity_store = EntityStore(db_path)` + `self.entity_extractor = EntityExtractor(self.entity_store)`
   - Replace `self.knowledge_graph.get_context_for_query()` with `self.context_builder.build_context()`
   - Replace `self.knowledge_graph.extract_entities_from_text()` with `self.entity_extractor.extract_and_store()`
4. Archive `learners/graph.py`
5. Update `interfaces/server.py` if any graph endpoints exist

---

## What This Enables

| Feature | Before | After |
|---------|--------|-------|
| Entity extraction quality | Regex matching ~30 terms | spaCy NER + 500+ technical terms + NLP |
| Entity storage | JSON file, no queries | SQLite with indexes, efficient queries |
| Graph operations | Basic dict lookup | BFS traversal, path finding, cross-domain bridges |
| Authority scoring | None | mention_count + source_count + recency formula |
| Relationship discovery | Manual co-occurrence dict | Automated co-occurrence within sentence windows |
| Cross-domain synthesis | Mentioned in every spec, never implemented | `get_cross_domain_bridges(domain_a, domain_b)` |
| Pattern↔Entity links | None | `Pattern.entity_refs` → `Entity.id` |
| Context in prompt | Basic entity mention list | Structured graph context with relationships |
| Foundation for Phase 12a | Would require rewrite | Direct extension of this system |
