# Entity Model Unification — Tasks

**Last Updated:** February 2026  
**Priority:** P0 — Foundation (parallel with unified-pattern-engine)  
**Estimated Effort:** 1.5–2 weeks

---

## Task Overview

| # | Task | Est. | Status |
|---|------|------|--------|
| 1 | Create `core/entities/` package structure | 0.25d | ✅ Done |
| 2 | Implement `Entity`, `Relationship`, `EntityType` models | 0.5d | ✅ Done |
| 3 | Implement SQLite schema and `EntityStore` CRUD | 1.5d | ✅ Done |
| 4 | Implement `EntityStore` graph operations (traversal, path, bridges) | 1d | ✅ Done |
| 5 | Implement `EntityStore` authority scoring | 0.5d | ✅ Done |
| 6 | Implement `EntityExtractor` with spaCy pipeline | 1.5d | ✅ Done |
| 7 | Implement `EntityContextBuilder` | 0.5d | ✅ Done |
| 8 | Implement data migration from JSON format | 0.5d | ✅ Done |
| 9 | Update `core/polly.py` to use new entity system | 1d | ✅ Done |
| 10 | Wire entity extraction into query pipeline | 0.5d | ✅ Done |
| 11 | Archive old `learners/graph.py` | 0.25d | ✅ Done |
| 12 | Write tests | 1.5d | ✅ Done (8 tests in test_entity_system.py) |
| 13 | Update `openspec/specs/knowledge-graph/spec.md` | 0.5d | ✅ Done |

---

## Detailed Task Descriptions

### 1. Create `core/entities/` package structure

```
core/entities/
├── __init__.py          # Exports: EntityStore, Entity, Relationship, EntityType, EntityExtractor, EntityContextBuilder
├── models.py
├── store.py
├── extractor.py
├── context.py
└── migration.py
```

### 2. Implement data models

`core/entities/models.py`:
- `Entity` dataclass (see design.md)
- `EntityType` enum (concept, tool, language, framework, project, person, file, pattern, book, topic, organization)
- `Relationship` dataclass
- `RelationshipType` enum
- `EntityQuery` dataclass
- `to_dict()` / `from_dict()` for all models
- Deterministic ID generation: `entity_id(name, entity_type)` → stable hash

**Tests:** `tests/root/test_entity_models.py`

### 3. Implement SQLite schema and `EntityStore` CRUD

`core/entities/store.py`:
- Database initialization with schema creation
- `upsert_entity()` — INSERT OR UPDATE with mention_count increment
- `upsert_relationship()` — INSERT OR UPDATE with strength recalculation
- `get_entity()`, `get_entity_by_name()`
- `delete_entity()` — cascade delete relationships and mentions
- `search()` — parameterized SQL query from `EntityQuery`
- `record_mention()` — insert into entity_mentions
- Transaction support for batch operations

**Database:** `~/.polly/entities.db`  
**Tests:** `tests/root/test_entity_store_crud.py`

### 4. Implement graph operations

`core/entities/store.py` (continued):
- `get_related(entity_id, max_hops, min_strength)` — BFS traversal
- `find_path(source_id, target_id, max_hops)` — shortest path via BFS
- `get_cross_domain_bridges(domain_a, domain_b, limit)` — entities with relationships in both domains
- `get_neighbors(entity_id)` — direct connections (1-hop)
- `get_entity_cluster(entity_id, max_size)` — connected component up to max_size

**Tests:** `tests/root/test_entity_store_graph.py`

### 5. Implement authority scoring

`core/entities/store.py` (continued):
- `recompute_authority(entity_id)` — formula:
  ```
  authority = 0.4 * log(mention_count + 1) / log(max_mentions + 1)
            + 0.3 * log(source_count + 1) / log(max_sources + 1)
            + 0.2 * relationship_count / max_relationships
            + 0.1 * recency_score  # 1.0 for today, decays over 90 days
  ```
- `recompute_all_authority()` — batch recompute (periodic maintenance)
- Authority influences search ranking and context priority

**Tests:** `tests/root/test_entity_authority.py`

### 6. Implement `EntityExtractor`

`core/entities/extractor.py`:

**Pipeline:**
1. **spaCy NER** — Extract PERSON, ORG, GPE, PRODUCT named entities
2. **Noun phrase extraction** — Extract candidate concepts via spaCy noun_chunks
3. **Technical term matching** — Match against 500+ term whitelist (migrated from `learners/patterns.py`)
4. **Entity type classification** — Classify extracted names by type using keyword lists + NER labels
5. **Co-occurrence relationship detection** — Within 3-sentence windows, detect pairs and create RELATED_TO relationships
6. **Deduplication** — Merge entities with matching names or aliases

**Source migration:**
- spaCy extraction logic from `learners/patterns.py` `_extract_concepts_spacy()`
- Technical terms from `learners/patterns.py` `TECHNICAL_TERMS`
- Regex patterns from `learners/graph.py` `ENTITY_TYPES` (upgraded to supplement, not replace, NLP)

**Key design decisions:**
- spaCy model loaded lazily (same as current `learners/patterns.py` behavior)
- Falls back to regex-only if spaCy not installed
- Entity store upsert handles dedup (same name + type = same entity, increment mention)

**Tests:** `tests/root/test_entity_extractor.py`

### 7. Implement `EntityContextBuilder`

`core/entities/context.py`:
- `build_context(query, domains, max_entities, include_relationships, include_cross_domain)`:
  1. Extract entities from query text (lightweight — keyword match, no full NLP)
  2. Look up matching entities in store
  3. Get related entities (1-hop) for each match
  4. If multiple domains detected, call `get_cross_domain_bridges()`
  5. Sort by authority score
  6. Format as structured context string:
     ```
     ## Knowledge Graph Context
     
     **Key Entities:**
     - Python (tool, authority: 0.85): Used in Polly backend, Sigils domain
       → related to: FastAPI (uses), Docker (uses), ...
     
     **Cross-Domain Connections:**
     - "constraint" bridges Grids (systems thinking) and Signals (audio synthesis)
     ```

**Tests:** `tests/root/test_entity_context.py`

### 8. Data migration

`core/entities/migration.py`:
- Read `~/.polly/knowledge_graph.json`
- Parse old `Entity` format → new `Entity` model
- Parse old `Relationship` format → new `Relationship` model
- Handle the hardcoded entity lists — don't migrate as entities, let real extraction discover them naturally
- Migrate user-created entities and relationships
- Backup old JSON before migration
- Log: entities migrated, relationships migrated, duplicates merged

**Tests:** `tests/root/test_entity_migration.py`

### 9. Update `core/polly.py`

**Changes in `_init_learners()`:**
```python
# Before
from learners.graph import KnowledgeGraph
self.knowledge_graph = KnowledgeGraph(graph_path)

# After
from core.entities import EntityStore, EntityExtractor, EntityContextBuilder
entity_db = Path(self.config.get("entities.db_path", "~/.polly/entities.db")).expanduser()
self.entity_store = EntityStore(entity_db)
self.entity_extractor = EntityExtractor(self.entity_store)
self.entity_context = EntityContextBuilder(self.entity_store)
```

**Changes in `query()`:**
```python
# Before
graph_context = self.knowledge_graph.get_context_for_query(query, detected_domains)

# After
graph_context = self.entity_context.build_context(query, domain_names)
```

```python
# Before (post-response)
self.knowledge_graph.extract_entities_from_text(query, detected_domains)
self.knowledge_graph.extract_entities_from_text(full_response, detected_domains)

# After
self.entity_extractor.extract_and_store(query, "query", conversation_id, domain_names)
self.entity_extractor.extract_and_store(full_response, "response", conversation_id, domain_names)
```

**Changes in `get_stats()`:**
```python
# Before
if self.knowledge_graph:
    stats['graph'] = self.knowledge_graph.get_stats()

# After
if self.entity_store:
    stats['graph'] = self.entity_store.get_stats()
```

**Changes in `save_state()`:**
```python
# Before
if self.knowledge_graph:
    self.knowledge_graph.save_graph()

# After
# No explicit save needed — SQLite writes are immediate
# But recompute authority periodically:
if self.entity_store:
    self.entity_store.recompute_all_authority()
```

### 10. Wire entity extraction into query pipeline

Beyond the basic query integration (Task 9), connect to:
- **Knowledge Writer**: When notes are saved, extract entities from note content
- **Compression**: When conversations are compressed, extract entities from compressed summaries
- **Notes indexing**: When notes are indexed for RAG, also extract entities

These are integration hooks — add the calls but keep them optional:
```python
# In KnowledgeWriter._save_note()
if self.entity_extractor:
    self.entity_extractor.extract_and_store(content, "note", file_path, [domain])
```

### 11. Archive old `learners/graph.py`

- Move `learners/graph.py` → `learners/archive/graph_v1.py`
- Remove `KnowledgeGraph` import from `learners/__init__.py`
- Verify no other files import from `learners.graph`

### 12. Write tests

Test suite:
- `tests/root/test_entity_models.py` — model serialization, ID generation
- `tests/root/test_entity_store_crud.py` — CRUD operations, upsert semantics
- `tests/root/test_entity_store_graph.py` — traversal, path finding, bridges
- `tests/root/test_entity_authority.py` — scoring algorithm, recomputation
- `tests/root/test_entity_extractor.py` — NLP extraction, term matching, co-occurrence
- `tests/root/test_entity_context.py` — context building, formatting
- `tests/root/test_entity_migration.py` — v1 JSON → v2 SQLite

### 13. Update knowledge-graph spec

Update `openspec/specs/knowledge-graph/spec.md`:
- Reflect new SQLite architecture
- Update entity model documentation
- Mark authority scoring as ✅ Implemented (basic) or 🔧 Partial
- Mark anti-slop quality pipeline as 📐 Designed (deferred to Phase 12a-ext)
- Mark visualization as 💭 Vision
- Update integration points to reflect actual connections

---

## Verification Criteria

1. **No references** to `learners.graph.KnowledgeGraph` in active code
2. **SQLite database** created at `~/.polly/entities.db` with proper schema
3. **Entity extraction** produces meaningful results from real queries (not just regex matches)
4. **Graph traversal** can find paths between related entities
5. **Cross-domain bridges** identified when entities span domains
6. **Authority scores** computed and influencing context ranking
7. **Context in prompt** is richer than old `get_context_for_query()` output
8. **Data migration** preserves existing entities and relationships
9. **All existing tests pass** (knowledge-graph-related tests updated)
