# Library Extraction — Tasks

**Last Updated:** February 2026  
**Priority:** P2 — Depends on all P0 and P1 changes  
**Estimated Effort:** 3–4 weeks (1 library per week, personas slower)

---

## Task Overview

| # | Task | Est. | Depends | Status |
|---|------|------|---------|--------|
| 1 | Create `libs/` directory structure and monorepo setup | 0.5d | — | ⬜ |
| 2 | Extract `polly-routing` | 3d | integration-contracts | ⬜ |
| 3 | Extract `polly-patterns` | 2d | unified-pattern-engine | ⬜ |
| 4 | Extract `polly-compression` | 2d | — | ⬜ |
| 5 | Extract `polly-entities` | 3d | entity-model-unification | ⬜ |
| 6 | Extract `polly-personas` | 4d | All above | ⬜ |
| 7 | Update `core/polly.py` imports | 1d | Tasks 2–6 | ⬜ |
| 8 | Update all other consumers | 1d | Task 7 | ⬜ |
| 9 | Verify full test suite passes | 1d | Task 8 | ⬜ |
| 10 | Write library READMEs | 1d | Tasks 2–6 | ⬜ |
| 11 | Update architecture spec | 0.5d | All above | ⬜ |

---

## Detailed Task Descriptions

### 1. Create `libs/` directory and monorepo setup

- Create `libs/` directory at project root
- Set up `pyproject.toml` or equivalent for monorepo workspace
- Configure Python path so `polly_routing`, `polly_patterns`, etc. are importable
- Option A (simple): Use `pip install -e libs/polly-routing` for each
- Option B (workspace): Use `pdm` or `poetry` workspace feature
- Update `.gitignore` if needed

**Files:** `libs/`, root config  
**Tests:** Verify import paths work

### 2. Extract `polly-routing`

**Steps:**
1. Create `libs/polly-routing/polly_routing/` package
2. Move `core/router_v2.py` → `polly_routing/router.py`
   - Remove Polly-specific config parsing
   - Accept provider configs as constructor args
   - Keep `PatternConsumer` protocol integration (accepts patterns, doesn't import `PatternEngine`)
3. Move `core/providers/base.py` → `polly_routing/providers/base.py`
4. Move `core/providers/litellm_adapter.py` → `polly_routing/providers/litellm.py`
5. Move `core/budget_manager.py` → `polly_routing/budget.py`
6. Create `polly_routing/models.py` (ModelConfig, TaskAnalysis, RouteDecision)
7. Create `polly_routing/__init__.py` with public exports
8. Create `libs/polly-routing/pyproject.toml` with dependencies
9. Create adapter in `core/` that imports from library and adds Polly-specific config
10. Update `core/polly.py` router initialization
11. Move relevant tests to `libs/polly-routing/tests/`
12. Verify existing tests pass

**Note:** `core/router.py` (v1) gets archived — not extracted. Its functionality was superseded by v2.

### 3. Extract `polly-patterns`

**Steps:**
1. Create `libs/polly-patterns/polly_patterns/` package
2. Move `core/patterns/` → `polly_patterns/` (after unified-pattern-engine)
   - `models.py`, `engine.py`, `extractor.py`, `scorer.py`
   - `storage/` subdirectory
3. Remove Polly-specific domain references from pattern types
   - `PatternType` enum stays generic
   - Domain-specific pattern types (DOMAIN_PRIORITY) stay but aren't hardcoded to Sigils/Signals/etc.
4. Create `libs/polly-patterns/pyproject.toml`
5. Update `core/polly.py` to import from `polly_patterns`
6. Move relevant tests

### 4. Extract `polly-compression`

**Steps:**
1. Create `libs/polly-compression/polly_compression/` package
2. Move `core/compression/` → `polly_compression/`
   - `manager.py`, `compressor.py`, `llmlingua_strategy.py`
3. Rename "compact format" references (if not done in unified-pattern-engine)
4. Remove any Polly-specific config parsing
5. Create `libs/polly-compression/pyproject.toml`
6. Update `core/polly.py` to import from `polly_compression`
7. Move relevant tests

### 5. Extract `polly-entities`

**Steps:**
1. Create `libs/polly-entities/polly_entities/` package
2. Move `core/entities/` → `polly_entities/` (after entity-model-unification)
   - `models.py`, `store.py`, `extractor.py`, `context.py`
3. Ensure no Polly-specific domain assumptions in entity types
4. Create `libs/polly-entities/pyproject.toml`
5. Update `core/polly.py` to import from `polly_entities`
6. Move relevant tests

### 6. Extract `polly-personas`

**Steps:**
1. Create `libs/polly-personas/polly_personas/` package
2. Move `core/personas/base.py` → `polly_personas/base.py`
3. Move `core/personas/manager.py` → `polly_personas/manager.py`
4. Move `core/personas/models.py` → `polly_personas/models.py`
5. **Critical:** Abstract Polly dependencies:
   - Router dependency → accept via Protocol (any object with `route()` and `execute()`)
   - RAG dependency → accept via Protocol (any object with `search()`)
   - SkillManager → accept via Protocol or make optional
   - LearningTracker → accept via Protocol or make optional
6. Move persona implementations (Architect, Scribe, Professor):
   - These are the most Polly-coupled parts
   - Option A: Keep in library as reference implementations
   - Option B: Keep in `core/personas/implementations/` as Polly-specific
   - **Recommended:** Option A with Protocol-based dependency injection
7. Move persona YAML definitions
8. Create `libs/polly-personas/pyproject.toml`
9. Update `core/polly.py` to import from `polly_personas`
10. Move relevant tests

### 7. Update `core/polly.py` imports

After all libraries extracted, do a single pass through `core/polly.py`:
- Replace all `from core.X import Y` with `from polly_X import Y` for extracted modules
- Verify initialization chain works with library imports
- Run full test suite

### 8. Update all other consumers

Files that import from extracted modules:
- `interfaces/server.py` — imports Pattern, PersonaManager, etc.
- `interfaces/settings_api.py` — imports config-related types
- `interfaces/memory_api.py` — imports Mem0Adapter
- `core/knowledge_writer.py` — imports PersonaManager types
- Any other `core/` files that import from extracted modules

### 9. Verify full test suite passes

- Run `pytest tests/` from project root
- Run each library's tests independently: `pytest libs/polly-routing/tests/`
- Verify no circular imports
- Verify no broken import paths
- Run linting

### 10. Write library READMEs

Each library gets a README with:
- What it does (1 paragraph)
- Installation instructions
- Quick usage example
- Public API reference (brief)
- Link to full Polly docs

### 11. Update architecture spec

Update `openspec/specs/architecture/spec.md`:
- Document monorepo library structure
- Update component diagram to show library boundaries
- Document dependency graph between libraries
- Note that libraries are internal packages (not published to PyPI)

---

## Verification Criteria

1. Each library independently importable: `from polly_routing import IntelligentRouter`
2. Each library has passing tests in isolation
3. No circular dependencies between libraries
4. `core/polly.py` works with library imports
5. Full application test suite passes
6. Each library has README with usage examples
7. No Polly-specific hardcoded values in library code (domains, paths, etc.)

---

## Future Considerations

After extraction is stable:

1. **PyPI publishing** — If libraries prove useful, publish to PyPI for external use
2. **Separate repositories** — If libraries diverge in release cadence, split to separate repos
3. **Versioning** — Adopt semver per library when API stability is important
4. **Documentation** — Sphinx/MkDocs per library for detailed API docs

These are explicitly NOT in scope for this change — noted here for context.
