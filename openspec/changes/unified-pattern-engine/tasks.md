# Unified Pattern Engine — Tasks

**Last Updated:** February 2026  
**Priority:** P0 — Foundation (blocks integration-contracts and library-extraction)  
**Estimated Effort:** 1.5–2 weeks

---

## Task Overview

| # | Task | Est. | Status |
|---|------|------|--------|
| 1 | Create `core/patterns/` package structure | 0.5d | ✅ Done |
| 2 | Implement `Pattern` data model and `PatternType` enum | 0.5d | ✅ Done |
| 3 | Implement `StorageBackend` protocol and `JSONBackend` | 1d | ✅ Done |
| 4 | Implement `Mem0Backend` | 1d | ✅ Done |
| 5 | Migrate `ConceptExtractor` from `learners/patterns.py` | 1d | ⏭️ Skipped (engine uses regex; spaCy extraction deferred) |
| 6 | Implement `PatternEngine` core (learn, search, lifecycle) | 2d | ✅ Done |
| 7 | Migrate scorer logic from `Polly._get_patterns_for_prompt()` | 0.5d | ✅ Done |
| 8 | Implement data migration from old format | 0.5d | ✅ Done |
| 9 | Update `core/polly.py` to use `PatternEngine` | 1d | ✅ Done |
| 10 | Update `core/rag.py` to use `PatternEngine` | 0.5d | ✅ Done |
| 11 | Update `core/domains.py` to use `PatternEngine` | 0.5d | ✅ Done |
| 12 | Update `interfaces/server.py` pattern endpoints | 0.5d | ✅ Done |
| 13 | Rename PIL → Compact Format in code and docs | 0.5d | ✅ Done |
| 14 | Archive old pattern files | 0.25d | ⬜ (old files preserved for reference) |
| 15 | Write tests for PatternEngine | 1d | ✅ Done (30 tests, all passing) |
| 16 | Update `openspec/specs/patterns/spec.md` | 0.5d | ✅ Done |

---

## Detailed Task Descriptions

### 1. Create `core/patterns/` package structure

Create the directory structure:
```
core/patterns/
├── __init__.py          # Exports: PatternEngine, Pattern, PatternType, PatternQuery
├── models.py
├── engine.py
├── extractor.py
├── scorer.py
├── storage/
│   ├── __init__.py
│   ├── base.py
│   ├── json_backend.py
│   └── mem0_backend.py
└── migration.py
```

**Files:** New package creation  
**Tests:** N/A (structural)

### 2. Implement `Pattern` data model and `PatternType` enum

Create `core/patterns/models.py`:
- `Pattern` dataclass with all unified fields (see design.md)
- `PatternType` enum with all type values
- `PatternQuery` dataclass for search
- `to_dict()` / `from_dict()` serialization
- JSON-compatible datetime handling

**Files:** `core/patterns/models.py`  
**Tests:** `tests/root/test_pattern_models.py`

### 3. Implement `StorageBackend` protocol and `JSONBackend`

Create `core/patterns/storage/base.py`:
- `StorageBackend` Protocol class

Create `core/patterns/storage/json_backend.py`:
- `JSONBackend` implementing the protocol
- Migrate JSON read/write logic from `learners/patterns.py`
- Atomic file writes (write to temp, rename)
- In-memory cache with dirty tracking

**Files:** `core/patterns/storage/base.py`, `core/patterns/storage/json_backend.py`  
**Tests:** `tests/root/test_pattern_json_backend.py`

### 4. Implement `Mem0Backend`

Create `core/patterns/storage/mem0_backend.py`:
- `Mem0Backend` implementing the protocol
- Migrate Mem0 integration from `core/pattern_learning.py`
- Lazy Mem0 initialization
- Map `Pattern` → Mem0 memory format (content=description, metadata=serialized fields)
- Map Mem0 search results → `Pattern` objects (no more anonymous class)

**Files:** `core/patterns/storage/mem0_backend.py`  
**Tests:** `tests/root/test_pattern_mem0_backend.py` (with Mem0 mock)

### 5. Migrate `ConceptExtractor` from `learners/patterns.py`

Create `core/patterns/extractor.py`:
- `ConceptExtractor` class
- Migrate `TECHNICAL_TERMS` whitelist (500+ terms)
- Migrate `DOMAIN_STOP_WORDS`
- Migrate spaCy-based concept extraction logic
- Migrate noun phrase extraction
- Migrate keyword extraction (lighter weight)
- Keep spaCy lazy-loaded

**Source:** `learners/patterns.py` lines 24–530 (approximately)  
**Files:** `core/patterns/extractor.py`  
**Tests:** `tests/root/test_concept_extractor.py`

### 6. Implement `PatternEngine` core

Create `core/patterns/engine.py`:
- `PatternEngine` class (see design.md for full API)
- Learning methods: `learn()`, `learn_from_query()`, `learn_from_compressed()`, `learn_domain_priorities()`, `learn_code_patterns()`
- Search methods: `search()`, `search_semantic()`, `get_conceptual_patterns()`, `get_domain_priorities()`
- Lifecycle methods: `decay()`, `prune()`, `save()`, `export()`
- Stats: `get_stats()`
- Dual-write to all active backends

**Key migration sources:**
- `learn_from_query()` ← `learners/patterns.PatternLearner.record_query()` + `.extract_concepts()` + `.learn_conceptual_patterns()`
- `learn_from_compressed()` ← `learners/patterns.PatternLearner.learn_from_compressed()`
- `learn_domain_priorities()` ← `learners/patterns.PatternLearner.learn_domain_priorities()`
- `search()` ← keyword/type filtering from both implementations
- `search_semantic()` ← `core/pattern_learning.PatternLearner.search_patterns()`

**Files:** `core/patterns/engine.py`  
**Tests:** `tests/root/test_pattern_engine.py`

### 7. Migrate scorer logic from `Polly._get_patterns_for_prompt()`

Create `core/patterns/scorer.py`:
- `PatternScorer` class
- Migrate scoring algorithm from `Polly._get_patterns_for_prompt()` (confidence, occurrences, recency, domain match, keyword match)
- Make scoring criteria configurable
- Used by `PatternEngine.get_patterns_for_prompt()`

**Source:** `core/polly.py` `_get_patterns_for_prompt()` method (~80 lines of scoring logic)  
**Files:** `core/patterns/scorer.py`  
**Tests:** `tests/root/test_pattern_scorer.py`

### 8. Implement data migration from old format

Create `core/patterns/migration.py`:
- `migrate_from_v1(old_json_path: Path, engine: PatternEngine)` function
- Read old `~/.polly/patterns.json` format
- Map old `Pattern` fields to new `Pattern` model:
  - `pattern_type` → `PatternType` enum
  - `name` → `name`
  - `description` → `description`
  - `confidence` → `confidence`
  - `examples` → `examples`
  - `occurrences` → `occurrences`
  - `last_seen` → `last_seen`
  - `domains` → `domains`
  - `metadata` → `metadata`
- Handle query patterns, conceptual patterns, domain priorities separately
- Create backup of old file before migration
- Log migration stats

**Files:** `core/patterns/migration.py`  
**Tests:** `tests/root/test_pattern_migration.py`

### 9. Update `core/polly.py` to use `PatternEngine`

This is the largest consumer migration.

**Changes:**
1. `_init_learners()`:
   - Replace `PatternLearner` + `Mem0PatternLearner` instantiation with single `PatternEngine`
   - Keep `KnowledgeGraph`, `LearningTracker`, `CurriculumManager` unchanged
   - Pass `PatternEngine` to `DomainEngine` instead of old `PatternLearner`

2. `_init_rag()`:
   - Pass `self.pattern_engine` instead of `self.pattern_learner`

3. `_get_patterns_for_prompt()`:
   - Replace entire method body with `self.pattern_engine.get_patterns_for_prompt()`
   - Remove anonymous `_Mem0Pattern` class bridge

4. `query()` method:
   - Query expansion: `self.pattern_engine.get_conceptual_patterns(concept)` instead of manual iteration
   - Domain priority learning: `self.pattern_engine.learn_domain_priorities()` instead of `self.pattern_learner.learn_domain_priorities()`
   - RAG boosting: use `self.pattern_engine.search()` instead of iterating `.patterns.values()`
   - Post-response learning: `self.pattern_engine.learn_from_query()` instead of `self.pattern_learner.record_query()`
   - Save: `self.pattern_engine.save()` instead of `self.pattern_learner.save_patterns()`

5. `_try_compress_conversation()`:
   - Update `learn_from_compressed()` call to use `self.pattern_engine`

6. Stats/export methods:
   - Update `get_pattern_stats()`, `get_patterns_for_concept()`, `get_domain_collection_weights()`, `export_patterns()` to delegate to `self.pattern_engine`

7. `save_state()`:
   - `self.pattern_engine.save()` instead of `self.pattern_learner.save_patterns()`

**Files:** `core/polly.py`  
**Tests:** Existing tests in `tests/root/` should pass after migration

### 10. Update `core/rag.py` to use `PatternEngine`

**Changes:**
- Constructor: accept `pattern_engine: Optional[PatternEngine]` instead of `pattern_learner`
- Code pattern extraction: call `self.pattern_engine.learn_code_patterns()` instead of `self.pattern_learner.extract_code_patterns()`
- Update type hints

**Files:** `core/rag.py`  
**Tests:** `tests/root/test_rag_*.py`

### 11. Update `core/domains.py` to use `PatternEngine`

**Changes:**
- `set_pattern_learner()` → `set_pattern_engine()`
- Update domain priority lookups to use new API
- Update type hints

**Files:** `core/domains.py`  
**Tests:** `tests/root/test_domain*.py`

### 12. Update `interfaces/server.py` pattern endpoints

**Changes:**
- Update `/polly/patterns/*` endpoints to use `polly.pattern_engine`
- Update response models if Pattern serialization format changed
- Ensure backward compatibility with frontend expectations

**Files:** `interfaces/server.py`  
**Tests:** `tests/root/test_server_*.py`

### 13. Rename PIL → Compact Format in code and docs

**Changes in code:**
- `core/compression/compressor.py`: Update docstrings and comments referencing "PIL" to "Compact Format"
- `core/mental_models.py`: Update `_compressed` field comment, docstrings
- Keep the actual compression logic identical — only branding changes

**Changes in specs:**
- `openspec/specs/compression/spec.md`: Rename "PIL" section to "Compact Format"
- `openspec/specs/mental-models/spec.md`: Update PIL references
- Add note explaining: "Previously referred to as 'PIL (Polly Internal Language)'. Renamed to 'Compact Format' to accurately describe the field-abbreviation encoding used for mental models in system prompts."

**Files:** `core/compression/compressor.py`, `core/mental_models.py`, 2 spec files  
**Tests:** N/A (cosmetic)

### 14. Archive old pattern files

- Move `learners/patterns.py` → `learners/archive/patterns_v1.py`
- Move `core/pattern_learning.py` → `core/archive/pattern_learning_v1.py`
- Update `learners/__init__.py` if needed
- Remove old imports from any `__init__.py` files
- Keep `learners/code_patterns.py` if it's used independently (verify)

**Files:** File moves + import cleanup  
**Tests:** Verify no import errors

### 15. Write tests for PatternEngine

Create comprehensive test suite:
- `tests/root/test_pattern_models.py` — data model serialization
- `tests/root/test_pattern_json_backend.py` — JSON storage operations
- `tests/root/test_pattern_mem0_backend.py` — Mem0 integration (mocked)
- `tests/root/test_concept_extractor.py` — concept extraction
- `tests/root/test_pattern_scorer.py` — relevance scoring
- `tests/root/test_pattern_engine.py` — full engine operations
- `tests/root/test_pattern_migration.py` — v1→v2 migration

**Coverage targets:**
- `Pattern` model: serialization, validation, type conversion
- `JSONBackend`: save, load, search, delete, concurrent access
- `Mem0Backend`: save, search, semantic search, lazy init
- `ConceptExtractor`: concept extraction, keyword extraction, technical terms
- `PatternEngine`: learn, search, decay, prune, multi-backend coordination
- `Migration`: old format parsing, field mapping, backup creation

### 16. Update `openspec/specs/patterns/spec.md`

Update the patterns spec to reflect:
- New unified data model
- Single `PatternEngine` class (not two learners)
- Storage backend architecture
- Updated integration points
- Mark 9 planned use cases with accurate status (implemented vs designed vs vision)

---

## Verification Criteria

After all tasks complete:

1. **No references** to `learners/patterns.PatternLearner` or `core/pattern_learning.PatternLearner` in active code
2. **Single `PatternEngine`** instance in `Polly.__init__()` replaces both old learners
3. **No anonymous classes** — Mem0 results properly mapped to `Pattern` model
4. **All existing tests pass** (pattern-related tests may need updates)
5. **Data migration succeeds** on existing `~/.polly/patterns.json`
6. **Semantic search works** when Mem0 is configured
7. **Domain priority learning** still functions correctly
8. **Code pattern extraction** still functions correctly
9. **Concept extraction** still uses spaCy with technical term whitelist
