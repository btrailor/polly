# Code Library & Development Philosophy — Tasks

**Created:** February 2026  
**Order:** Backend before frontend. Library before philosophy (library is higher leverage). Within each wave, tasks are parallelizable.

---

## Priority Summary

| Priority                           | What                                                                                     | Rationale                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **High leverage (build first)**    | Library registry + module format, pattern extraction workflow, philosophy guided process | Foundation for everything else; the thinking exercise produces better projects |
| **Medium leverage (build second)** | Multi-model routing for library, AI Slop review skill, slash command system              | Optimization and UX layer                                                      |
| **Lower leverage (build later)**   | Library sharing, philosophy templates, automated drift detection                         | Network effects and polish                                                     |

---

## Wave 1 — Library Foundation (Backend, 1–2 weeks)

### Task 1: Library Models & Registry I/O

**Files:** `core/code_library/__init__.py`, `core/code_library/models.py`, `core/code_library/registry.py`

**Steps:**

1. [ ] Create `core/code_library/` package
2. [ ] Define `LibraryModule`, `ExtractionCandidate`, `LibrarySearchResult`, `ModuleCategory` dataclasses in `models.py`
3. [ ] Implement `RegistryIO` class in `registry.py`:
   - `load(path) -> dict` — Parse `registry.yml`
   - `save(registry, path)` — Write `registry.yml`
   - `add_module(registry, module)` — Add entry
   - `remove_module(registry, name)` — Remove entry
   - `update_module(registry, name, updates)` — Update entry
4. [ ] Handle first-run: create `_polly/library/` directory structure and empty `registry.yml` if not present
5. [ ] Write tests: `tests/test_code_library_models.py`, `tests/test_registry_io.py`

**Acceptance:** Registry can be created, loaded, modified, and saved. All module categories represented.

---

### Task 2: CodeLibraryManager Core

**Files:** `core/code_library/manager.py`  
**Depends on:** Task 1

**Steps:**

1. [ ] Implement `CodeLibraryManager.__init__()` — load registry, validate library path
2. [ ] Implement CRUD operations:
   - `list_modules()` with filters (category, domain, language, tags)
   - `get_module()` — load SKILL.md + metadata
   - `create_module()` — create directory, write SKILL.md, write scripts/references/assets, update registry
   - `update_module()` — modify files and registry
   - `delete_module()` — remove directory and registry entry
3. [ ] Implement usage tracking:
   - `record_usage()` — increment `times_used`, update `last_used`
   - `get_stats()` — aggregate statistics
4. [ ] Implement SKILL.md parser:
   - Parse YAML frontmatter + markdown body
   - Validate required fields (name, description)
   - Extract metadata section
5. [ ] Wire into `core/polly.py` — `_init_code_library()` method
6. [ ] Write tests: `tests/test_code_library_manager.py`

**Acceptance:** Full CRUD lifecycle for library modules. SKILL.md files parsed correctly. Stats computed.

---

### Task 3: Library RAG Integration

**Files:** `core/code_library/manager.py` (extend), `core/rag.py` (modify)  
**Depends on:** Task 2

**Steps:**

1. [ ] Create `code-library` ChromaDB collection in RAG initialization
2. [ ] Index modules: embed SKILL.md content + script summaries into `code-library` collection with metadata (name, category, languages, domain, tags)
3. [ ] Implement `search()` method in `CodeLibraryManager`:
   - RAG semantic search against `code-library` collection
   - Fallback: tag matching + name matching for non-semantic queries
   - Merge and rank results
4. [ ] Incremental indexing: index new modules when created, remove when deleted
5. [ ] Write tests: `tests/test_code_library_search.py`

**Acceptance:** `/library search "retry logic"` returns relevant modules. New modules are searchable immediately after creation.

---

### Task 4: Library REST API

**Files:** `interfaces/library_api.py`, `interfaces/server.py` (register routes)  
**Depends on:** Tasks 2, 3

**Steps:**

1. [ ] Create `interfaces/library_api.py` with endpoints:
   - `GET /api/library/modules` — list with filters
   - `GET /api/library/modules/<name>` — detail
   - `POST /api/library/modules` — create
   - `PUT /api/library/modules/<name>` — update
   - `DELETE /api/library/modules/<name>` — delete
   - `POST /api/library/search` — search
   - `GET /api/library/stats` — statistics
2. [ ] Register routes in `interfaces/server.py`
3. [ ] Add library path to config: `config.yaml` → `library` section
4. [ ] Write API tests

**Acceptance:** All library CRUD and search operations accessible via REST.

---

## Wave 2 — Pattern Extraction & Library Growth (Backend, 1–2 weeks)

### Task 5: Pattern Recognition & Extraction Engine

**Files:** `core/code_library/extractor.py`  
**Depends on:** Task 2

**Steps:**

1. [ ] Implement `LibraryExtractor` class:
   - `suggest_extractions(code, file_path)` — Analyze code for reuse patterns
   - `extract_module(candidate)` — Transform code into library module
2. [ ] Extraction pipeline:
   - Strip project-specific details (hardcoded paths, specific API keys, project names)
   - Parameterize configuration (replace constants with config parameters)
   - Generate SKILL.md with when-to-use/when-not-to-use guidance
   - Create reference implementations in detected languages
   - Tag with domain (infer from project context or ask user)
3. [ ] Integration with existing `CodePatternExtractor` (in `learners/code_patterns.py`):
   - High-confidence code patterns flagged as extraction candidates
   - Pattern → Library promotion pipeline
4. [ ] Multi-model routing: extraction uses free/budget models; abstraction design uses frontier
5. [ ] Write tests: `tests/test_code_library_extractor.py`

**Acceptance:** Given a code file with retry logic, extractor produces a clean, parameterized library module with SKILL.md.

---

### Task 6: Pattern → Library Promotion Pipeline

**Files:** `core/code_library/extractor.py` (extend), `core/pattern_learning.py` (modify), `learners/patterns.py` (modify)  
**Depends on:** Task 5

**Steps:**

1. [ ] Add `library_usage` pattern type to PatternLearner
2. [ ] Add promotion check in PatternLearner:
   - When a code pattern's confidence exceeds threshold (default 0.8), flag as library candidate
   - When a code pattern has been seen in 3+ different files/projects, flag as extraction candidate
3. [ ] Implement promotion workflow:
   - PatternLearner flags candidate → user confirmation (or auto-extract if configured)
   - Extraction runs → new module created
   - Pattern linked to module in registry (provenance)
4. [ ] Track library usage as patterns:
   - When a module is applied (`record_usage()`), create/update `library_usage` pattern
5. [ ] Add `auto_extract` config option with confidence threshold
6. [ ] Write tests

**Acceptance:** A pattern that reaches high confidence triggers a library extraction suggestion. Library usage is tracked as patterns.

---

### Task 7: AI Slop Review Skill

**Files:** `core/code_library/reviewer.py`, `_polly/library/prompts/code-review/SKILL.md` (bootstrap)  
**Depends on:** Task 2

**Steps:**

1. [ ] Implement `CodeReviewer` class:
   - `review(code, context)` → structured review result
   - Check categories: unnecessary abstraction, boilerplate bloat, inconsistent patterns, missing error handling, over-commenting, dependency creep
   - Return structured dict with issues found, severity, suggestions
2. [ ] Create bootstrap `code-review` SKILL.md in library:
   - Review criteria as structured instructions
   - Examples of good vs. bad patterns
3. [ ] Multi-model routing: basic rule checks use free tier; nuanced review uses frontier
4. [ ] Integration point: review runs automatically on new library extractions if `review_on_extract` is true
5. [ ] The review skill itself learns: track which review suggestions are accepted/rejected by the user, adjust weights
6. [ ] Add `/library review` endpoint to library API
7. [ ] Write tests: `tests/test_code_reviewer.py`

**Acceptance:** Review pass identifies at least 3 of the 6 check categories. Review runs automatically on extraction when configured.

---

### Task 8: Module Application (Instantiation)

**Files:** `core/code_library/manager.py` (extend)  
**Depends on:** Task 2

**Steps:**

1. [ ] Implement `apply_module()`:
   - Read module scripts and templates
   - Adapt to target project conventions (indentation, naming, language variant)
   - Write files to target path
   - Record usage
2. [ ] Template variable system:
   - `{{project_name}}`, `{{author}}`, `{{date}}`, custom variables
   - Prompt user for missing variables
3. [ ] Dependency resolution: if module depends on other modules, warn or auto-apply
4. [ ] Add `POST /api/library/apply/<name>` endpoint
5. [ ] Write tests

**Acceptance:** Applying a module creates project-ready files in the target directory. Dependencies are checked.

---

## Wave 3 — Development Philosophy (Backend, 1 week)

### Task 9: Philosophy Models & Spectrum Config

**Files:** `core/philosophy/__init__.py`, `core/philosophy/models.py`, `config/philosophy_spectrums.yaml`  
**Depends on:** None (parallel with Waves 1–2)

**Steps:**

1. [ ] Create `core/philosophy/` package
2. [ ] Define `SpectrumPosition`, `DevelopmentPhilosophy` dataclasses
3. [ ] Create `config/philosophy_spectrums.yaml` with 6 default spectrums:
   - Open ↔ Constrained
   - Friendly ↔ Powerful
   - Convention ↔ Configuration
   - Local ↔ Cloud
   - Build ↔ Buy
   - MVP ↔ Architecture
4. [ ] Implement spectrum loader: parse YAML, validate, return structured data
5. [ ] Write tests: `tests/test_philosophy_models.py`

**Acceptance:** Spectrum definitions loaded and validated. Custom spectrums can be added.

---

### Task 10: PhilosophyManager & Guided Process

**Files:** `core/philosophy/manager.py`, `core/philosophy/guided_process.py`  
**Depends on:** Task 9

**Steps:**

1. [ ] Implement `PhilosophyManager`:
   - `get_spectrums()`, `add_spectrum()`
   - `init_philosophy()` — from guided process responses
   - `load_philosophy()` / `save_philosophy()` — markdown I/O
   - `get_philosophy_context()` — generate persona prompt context
2. [ ] Implement `GuidedProcess`:
   - Phase 1: Project Framing questions
   - Phase 2: Spectrum Positioning (generate contextual prompts per spectrum)
   - Phase 3: Philosophy Document Generation (markdown)
3. [ ] Philosophy markdown parser: read existing `development-philosophy.md` back into `DevelopmentPhilosophy`
4. [ ] Wire into `core/polly.py` — load philosophy on startup if present
5. [ ] Write tests: `tests/test_philosophy_manager.py`

**Acceptance:** Guided process produces a valid `development-philosophy.md`. Existing documents can be loaded and modified.

---

### Task 11: Philosophy → Persona Integration

**Files:** `core/personas/manager.py` (modify), `core/philosophy/manager.py` (extend)  
**Depends on:** Task 10

**Steps:**

1. [ ] Add philosophy context injection to persona system prompt builder
   - Position after theme context, before skills
   - Render spectrum positions and non-negotiables as natural language
2. [ ] Add `philosophy_context` parameter to persona activation flow
3. [ ] Implement `check_alignment()`: compare code patterns (from pattern learner) against philosophy positions
4. [ ] Implement `suggest_review()`: check review cadence, prompt user if due
5. [ ] Write tests

**Acceptance:** Active philosophy is visible in persona system prompts. Alignment check produces meaningful comparison.

---

### Task 12: Philosophy REST API

**Files:** `interfaces/philosophy_api.py`, `interfaces/server.py` (register routes)  
**Depends on:** Tasks 10, 11

**Steps:**

1. [ ] Create `interfaces/philosophy_api.py` with endpoints:
   - `GET /api/philosophy/spectrums` — list spectrums
   - `POST /api/philosophy/spectrums` — add custom spectrum
   - `POST /api/philosophy/init` — start guided process
   - `GET /api/philosophy/current` — get current philosophy
   - `PUT /api/philosophy/current` — update philosophy
   - `POST /api/philosophy/check` — alignment check
2. [ ] Register routes in `interfaces/server.py`
3. [ ] Add philosophy config to `config.yaml`
4. [ ] Write API tests

**Acceptance:** Philosophy CRUD and guided process accessible via REST.

---

## Wave 4 — Slash Commands & Frontend (1–2 weeks)

### Task 13: Slash Command Registry (Backend)

**Files:** `core/commands/__init__.py`, `core/commands/registry.py`, `core/commands/library_commands.py`, `core/commands/philosophy_commands.py`, `core/commands/meta_commands.py`  
**Depends on:** Tasks 4, 12

**Steps:**

1. [ ] Create `core/commands/` package
2. [ ] Implement `SlashCommandRegistry`:
   - `register()` — register command with handler, persona, description, args
   - `execute()` — parse command string, dispatch to handler
   - `list_commands()` — list available commands
   - `autocomplete()` — suggest completions for partial input
3. [ ] Implement library commands: `/library search`, `/library extract`, `/library apply`, `/library review`, `/library stats`
4. [ ] Implement philosophy commands: `/philosophy init`, `/philosophy review`, `/philosophy check`, `/philosophy spectrum`
5. [ ] Implement meta commands: `/model status`, `/model route`, `/cost report`
6. [ ] Add `POST /api/commands/execute` and `GET /api/commands/list` endpoints
7. [ ] Wire slash command detection into chat input processing
8. [ ] Write tests: `tests/test_slash_commands.py`

**Acceptance:** `/library search retry` in chat returns library results. All commands listed in `/help` or autocomplete.

---

### Task 14: Library UI (Frontend)

**Files:** `electron-app/src/renderer/` (new library page components)  
**Depends on:** Task 4

**Steps:**

1. [ ] Add Library page to ribbon navigation (new icon)
2. [ ] Implement module browser:
   - Grid/list view toggle
   - Category tabs (patterns, components, prompts, workflows)
   - Search bar (connected to `/api/library/search`)
   - Module cards with name, description, languages, usage count, confidence badge
3. [ ] Implement module detail view:
   - Rendered SKILL.md (markdown)
   - Scripts listing
   - Usage history
   - "Apply to project" button (Phase 17 dependency for full functionality)
4. [ ] Implement library stats sidebar:
   - Total modules by category
   - Most/least used
   - Recently added
5. [ ] Empty state: guidance when library is empty ("Polly will build your library as you work")
6. [ ] Write frontend tests

**Acceptance:** Library page displays modules with search and filtering. Module detail shows full SKILL.md content.

---

### Task 15: Philosophy UI (Frontend)

**Files:** `electron-app/src/renderer/` (philosophy components in settings or standalone)  
**Depends on:** Task 12

**Steps:**

1. [ ] Add Philosophy section to Settings (or standalone page accessible from settings)
2. [ ] Implement guided flow UI:
   - Phase 1: Project framing form (description, audience, target, horizon)
   - Phase 2: Spectrum sliders with contextual prompts
   - Phase 3: Preview generated document
3. [ ] Implement philosophy viewer:
   - Rendered `development-philosophy.md`
   - Spectrum visualization (bar chart or radar chart)
   - Edit button to re-enter guided flow
4. [ ] Review prompt: banner or notification when review is due
5. [ ] Write frontend tests

**Acceptance:** User can complete guided flow and see generated philosophy. Spectrum positions visualized.

---

### Task 16: Slash Command UI (Frontend)

**Files:** `electron-app/src/renderer/app.js` (modify chat input)  
**Depends on:** Task 13

**Steps:**

1. [ ] Detect `/` prefix in chat input
2. [ ] Show autocomplete dropdown with available commands
3. [ ] Display command results:
   - Library search results → inline card list
   - Stats → formatted table
   - Philosophy check → alignment report panel
   - Review → annotated code view or report panel
4. [ ] Handle multi-step commands (e.g., `/philosophy init` starts guided flow)
5. [ ] Write frontend tests

**Acceptance:** Typing `/` in chat shows command autocomplete. Results displayed appropriately per command type.

---

## Wave 5 — Polish & Integration (1 week)

### Task 17: Multi-Model Routing for Library Operations

**Files:** `core/code_library/manager.py` (extend), `config/config.yaml` (add routing config)  
**Depends on:** LiteLLM adapter (Task #12 in core-framework-refinement)

**Steps:**

1. [ ] Define task types for library operations (extraction, formatting, indexing, review, abstraction_design, documentation)
2. [ ] Add model routing config to `config.yaml` → `model_routing.library_operations`
3. [ ] Wire library operations to use appropriate model tier via LiteLLM
4. [ ] Cost tracking: library operations reported separately in `/cost report`
5. [ ] Write tests

**Acceptance:** Library extraction uses free model by default. Abstraction design uses frontier. Cost is tracked.

---

### Task 18: Progressive Refinement & Library Learning

**Files:** `core/code_library/manager.py` (extend)  
**Depends on:** Tasks 5, 6

**Steps:**

1. [ ] When a module is used (`apply_module()`):
   - Track edge cases encountered
   - Offer to update implementation based on new usage context
   - Expand language support if applied in a new language
   - Update SKILL.md with better documentation
2. [ ] Confidence scoring:
   - New modules start at 0.5
   - Confidence increases with usage (+0.05 per use, cap at 1.0)
   - Confidence decreases with disuse (2% decay per month after 90 days)
3. [ ] Provenance chain: track which project spawned the module and all projects that used it
4. [ ] Write tests

**Acceptance:** Module confidence updates on use and decays on disuse. Usage provenance tracked.

---

## Future Waves (Lower Leverage — Build Later)

### Task 19: Library Sharing & Export (Tier 5)

- Export modules as standalone Agent Skills directories
- Import modules from external sources
- DRM integration for sharing across mesh
- Not blocked — can proceed independently when needed

### Task 20: Philosophy Templates

- Pre-built philosophies for common project types (SaaS, CLI tool, personal project, game, library)
- User can start from template and customize

### Task 21: Automated Spectrum Drift Detection

- Continuous comparison of code patterns against philosophy
- "Your code diverged from your philosophy" notifications
- Requires pattern learning integration + code analysis pipeline

### Task 22: Library Module Versioning

- Semantic versioning for modules
- Changelog tracking per module
- Rollback capability

---

## Dependencies Summary

```
Wave 1 (Library Foundation)
  Task 1: Models & Registry ──→ Task 2: Manager ──→ Task 3: RAG ──→ Task 4: REST API
                                    │
                                    └──→ Task 8: Application

Wave 2 (Extraction & Growth) — depends on Wave 1
  Task 5: Extractor ──→ Task 6: Pattern → Library Pipeline
  Task 7: AI Slop Review (parallel with 5)

Wave 3 (Philosophy) — can parallel Waves 1–2
  Task 9: Models & Config ──→ Task 10: Manager ──→ Task 11: Persona Integration ──→ Task 12: REST API

Wave 4 (Commands & UI) — depends on Waves 1–3
  Task 13: Slash Commands ──→ Task 16: Command UI
  Task 14: Library UI (depends on Task 4)
  Task 15: Philosophy UI (depends on Task 12)

Wave 5 (Polish) — depends on Waves 1–4
  Task 17: Multi-Model Routing
  Task 18: Progressive Refinement

External Dependencies:
  - LiteLLM adapter (core-framework-refinement Task #12) — for multi-model routing
  - Phase 17 (Monaco Code Workspace) — for full /library extract and /library apply UX
  - Phase 25 (Programmer Persona) — primary library producer/consumer
```

---

## Effort Estimate

| Wave      | Effort        | Can Parallel With |
| --------- | ------------- | ----------------- |
| Wave 1    | 1–2 weeks     | Wave 3            |
| Wave 2    | 1–2 weeks     | —                 |
| Wave 3    | 1 week        | Wave 1            |
| Wave 4    | 1–2 weeks     | —                 |
| Wave 5    | 1 week        | —                 |
| **Total** | **4–7 weeks** |                   |

Waves 1 and 3 can run in parallel, bringing effective timeline to **3–6 weeks** for core functionality.
