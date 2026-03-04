# Polly Roadmap (OpenSpec)

**Authority:** This file is the OpenSpec source of truth for tiers and phase plan.  
**Status:** See [status.md](status.md). **Detail:** [docs/planning/phases/](../../../docs/planning/phases/), [archive/root-docs/MASTER_ROADMAP.md](../../../archive/root-docs/MASTER_ROADMAP.md) (reference).

---

## Tiers Overview

| Tier  | Name                    | Progress       | Notes                                                                        |
| ----- | ----------------------- | -------------- | ---------------------------------------------------------------------------- |
| **0** | Foundation & UI         | ✅ 100%        | Phases 0.5, 1, 3, 4, 5                                                       |
| **1** | Core Intelligence       | ~92%           | 15+ phases done; 23.5 ✅; 12a ✅ ~95%; 12b ✅; 16c ✅; 22 frontend remaining |
| **2** | Packaging & Permissions | 📋 Not started | Phase 9, signing, UI polish                                                  |
| **3** | Knowledge Platform      | 📋 Not started | Knowledge graph advanced, capture, maturity lifecycle, canvas, publishing    |
| **4** | Polish & Autonomy       | 📋 Not started | Phase 18 onboarding, Phase 19 data autonomy, analytics                       |
| **5** | Distributed & Mobile    | 📋 Not started | DRM, mobile companion, advanced communication                                |

Tier docs: [docs/planning/tiers/](../../../docs/planning/tiers/).

---

## Phase List (Status)

### Tier 0 ✅

| Phase | Name                 | Status |
| ----- | -------------------- | ------ |
| 0.5   | Obsidian-Inspired UI | ✅     |
| 1     | Configuration System | ✅     |
| 3     | Backend Server       | ✅     |
| 4     | Electron Application | ✅     |
| 5     | Secrets Manager      | ✅     |

### Tier 1

| Phase    | Name                           | Status                    | OpenSpec / Notes                                                                                                                                                                                                                                              |
| -------- | ------------------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.5      | Domain Configuration           | ✅                        |                                                                                                                                                                                                                                                               |
| 2a       | RAG Optimization               | ✅                        |                                                                                                                                                                                                                                                               |
| 2b       | Pattern Compression            | ✅                        |                                                                                                                                                                                                                                                               |
| 11       | Multi-Model Routing & Personas | ✅                        | 11a, 11b, 11c                                                                                                                                                                                                                                                 |
| 11c      | Compression UI                 | ✅                        |                                                                                                                                                                                                                                                               |
| 13a      | Pattern Learning Core          | ✅                        |                                                                                                                                                                                                                                                               |
| 14       | Mental Models                  | ✅                        |                                                                                                                                                                                                                                                               |
| 16       | Native Notes Frontend          | ✅                        |                                                                                                                                                                                                                                                               |
| 16c      | AI Note Creation               | ✅                        | Full stack: backend (knowledge_writer, save-quick/save-scribe/save-message APIs) + frontend (AI Note modal, Quick Save, Generate with Scribe)                                                                                                                 |
| 16e      | TOC & Templates                | ✅                        |                                                                                                                                                                                                                                                               |
| 21       | Knowledge Base Deduplication   | ✅                        | Being absorbed into Knowledge Quality Pipeline                                                                                                                                                                                                                |
| 22       | Teaching Mode                  | 🔄 ~75%                   | Backend done; frontend includes Learning page center area redesign + meta-pedagogy. [changes/learning-and-administrator-profiles/](../changes/learning-and-administrator-profiles/)                                                                           |
| 23       | Curriculum Learning System     | ✅                        | All 6 sub-phases                                                                                                                                                                                                                                              |
| **23.5** | **Security Hardening**         | ✅ Substantially complete | Capability Broker, Pyodide sandbox, allowlist, CORS, audit. Analysis: [phase-23.5/PHASE23.5_ANALYSIS.md](../../../docs/planning/phases/phase-23.5/PHASE23.5_ANALYSIS.md)                                                                                      |
| 12a      | Knowledge Graph Basic          | ✅ ~95%                   | Implemented via knowledge-graph-navigation + knowledge-graph-refinement changes. Backend: all graph endpoints, entity extraction on save, Garden API. Frontend: Cytoscape.js graph page, Browse list, Garden view, filters, navigation. Spec updates pending. |
| 12b      | Knowledge Graph Advanced       | ✅                        | After 12a; 3 waves complete (March 2026). `core/entities/retriever.py`, `core/entities/intelligence.py`. [changes/knowledge-graph-advanced/](../changes/knowledge-graph-advanced/)                                                                            |

### Cross-Cutting: Core Framework Refinement

| Component                        | Status  | OpenSpec / Notes                                                                        |
| -------------------------------- | ------- | --------------------------------------------------------------------------------------- |
| Knowledge Writing                | ✅      | `core/knowledge_writer.py`, settings API, frontend                                      |
| Autonomy Metrics                 | ✅      | `core/autonomy_metrics.py`, dashboard API                                               |
| Incremental RAG Index            | ✅      | `rag.index_single_document()`                                                           |
| AI Features Config + UI          | ✅      | `config.yaml`, settings toggles                                                         |
| Provider Management UI           | ✅      | Settings → Providers page with toggles, status, test buttons                            |
| "Polly" Routing Mode             | ✅      | Model selector with 3 tiers (Fast/Balanced/Thorough), routing explanations              |
| Query Decomposition              | ✅      | `core/query_decomposition.py` (467 lines), complexity scoring, sub-query generation     |
| Split Routing + Synthesis        | ✅      | `core/split_router.py` (453 lines), `core/synthesis.py` (380 lines), parallel execution |
| Knowledge Enrichment Integration | ✅      | Gap detection in `polly.py`, suggestion-card.js, persona_actions in chat responses      |
| Autonomy Dashboard               | 🔄 ~40% | Backend complete (`autonomy_metrics.py`, 3 API endpoints); frontend dashboard not built |
| Enhanced Auto-Linking            | 🔄 ~35% | BacklinksIndex (516 lines), sync integration; write-back, broken link detection pending |
| RAG Optimization                 | 📋      | Not started                                                                             |
| Persona Memory for Enrichment    | 🔄 ~25% | Memory read path works; write-back/preference recording pending                         |
| SKILL ↔ Mental Model             | 📋      | Not started                                                                             |
| Agent Swarms / Nexus             | 📋      | Replaces original Orchestrator; see Phase 24a–24e                                       |
| BookLore Library                 | 📋      | Not started                                                                             |

Change folder: [changes/core-framework-refinement/](../changes/core-framework-refinement/)

### Cross-Cutting: Architecture Integration (NEW — Feb 2026)

Comprehensive audit and remediation of architectural gaps between Polly's core systems. Discovered that pattern learning, entity extraction, knowledge graph, compression, mental models, and personas operate as islands with fragile or missing integration. Four-phase remediation plan:

| Phase | Name                     | Priority     | Status  | Change Folder                                                             |
| ----- | ------------------------ | ------------ | ------- | ------------------------------------------------------------------------- |
| A.1   | Unified Pattern Engine   | P0           | ✅ Done | [changes/unified-pattern-engine/](../changes/unified-pattern-engine/)     |
| A.2   | Entity Model Unification | P0           | ✅ Done | [changes/entity-model-unification/](../changes/entity-model-unification/) |
| B     | Integration Contracts    | P1 (after A) | ✅ Done | [changes/integration-contracts/](../changes/integration-contracts/)       |
| C     | Library Extraction       | P2 (after B) | 📋 Next | [changes/library-extraction/](../changes/library-extraction/)             |

**Key deliverables:**

- ✅ Audit complete — 10 integration issues documented
- ✅ Merge two incompatible `PatternLearner` classes into unified `PatternEngine`
- ✅ Shared `Entity` model across knowledge graph, pattern engine, Mem0
- ✅ Knowledge graph restructured from JSON to SQLite with real graph operations
- 📐 Cross-system protocols: `PatternConsumer`, `EntityProvider`, `PersonaAware`, `ContextContributor`
- 📐 Persona composition with patterns, entities, and mental models
- 📐 Routing feedback loop (patterns inform routing, outcomes feed patterns)
- 📐 Conversation synchronization between Electron and Python
- 📐 Extract 5 libraries: `polly-routing`, `polly-patterns`, `polly-compression`, `polly-entities`, `polly-personas`
- ✅ Rename PIL → Compact Format (honest naming)
- ✅ Spec reconciliation: status markers on prioritized specs, architecture spec updated with actual data flow, vision headers on unimplemented specs (agent-swarms, drm, mobile, communication, publishing, canvas, analytics, data-autonomy, onboarding). See [architecture-integration-audit tasks](../../changes/architecture-integration-audit/tasks.md) Tasks 6–9.

Master reference: [changes/architecture-integration-audit/](../changes/architecture-integration-audit/)

**Dependency note:** Phase A (P0) is complete. Phase B (Integration Contracts) is next; it builds on the unified pattern engine and entity model. Phase B should precede Phase 23.5 (Security) since the integration contracts will define the systems that security hardens.

### Cross-Cutting: Hardened Knowledge Infrastructure (NEW — Feb 2026)

Defense-in-depth infrastructure layer for Polly's query pipeline. Formalizes and unifies existing fragments of retry logic, error handling, validation, and observability into a coherent hardened system.

| Wave | Name                                                      | Status  | Components                                                                                 |
| ---- | --------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------ |
| 1    | Observable Failure Modes + Retry Manager                  | ✅ Done | `core/hardened/failure.py`, `core/hardened/retry_manager.py`, `config/retry.yaml`          |
| 2    | Dual-Phenomenology Validation + Three-Tier Classification | ✅ Done | `core/hardened/validator.py`, `core/hardened/classifier.py`, `config/validation.yaml`      |
| 3    | Performance Metrics + Observability                       | ✅ Done | `core/hardened/performance.py`, `core/hardened/dashboard.py`                               |
| 4    | Persistent State + Schema Migration                       | ✅ Done | `core/hardened/db.py`, `core/hardened/migration.py`, `migrations/001_initial_hardened.sql` |

**Key deliverables:**

- ✅ Explicit failure taxonomy with FailureCategory enum, FailureFactory, FailureLogger
- ✅ Unified RetryManager with circuit breaker, exponential backoff, operation-specific policies
- ✅ DualValidator: independent provenance (source trust) + content (quality/epistemological alignment) checks
- ✅ RetrievalClassifier: DIRECT / ADJACENT / ABSENT three-tier system
- ✅ PerformanceTracker with p50/p90/p95/p99 percentile stats
- ✅ PerformanceDashboard with degradation detection
- ✅ MigrationManager with forward-only SQL migrations
- ✅ Constitutional check reconciliation: epistemological enrichment, not content filtering (per ethics spec)
- ✅ All tables in `~/.polly/hardened.db` with WAL mode

Change folder: [changes/hardened-knowledge-infrastructure/](../../changes/hardened-knowledge-infrastructure/)

### Cross-Cutting: Scalable Memory Layers (NEW — Feb 2026)

Tiered memory persistence and rolling relevance-weighted context assembly for Polly's query pipeline. Built on top of Mem0, adds three-tier memory (stable/episodic/working), strict token budget management, 5-component relevance scoring with decay, and session-end fact extraction.

| Phase | Name                               | Status  | Components                                                                                                                                                                                               |
| ----- | ---------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Token Budget Foundation            | ✅ Done | `core/context/token_counter.py`, `core/context/budget_allocator.py`, tiktoken integration, ContextContributor `token_budget` param                                                                       |
| 2     | Tiered Memory Store                | ✅ Done | `core/memory/tiers.py` (stable/episodic/working → Mem0), `core/memory/retriever.py` (ContextContributor priority 50)                                                                                     |
| 3     | Rolling Relevance-Weighted Context | ✅ Done | `core/context/relevance_scorer.py` (5-component scoring), `core/context/rolling_context.py` (decay, amplification, bin-packing)                                                                          |
| 4     | Extraction & Wiring                | ✅ Done | `core/memory/extractor.py` (session-end extraction, local/cloud model selection), `core/polly.py` integration (budget allocation, dual-path \_gather_context, retrieval tier wiring, cleanup extraction) |
| 5     | Testing & Documentation            | ✅ ~90% | 112/112 tests passing (7 test files). Documentation updates in progress. Manual quality validation deferred.                                                                                             |

**Key deliverables:**

- ✅ Accurate token counting via tiktoken (replaced all `len//4` approximations)
- ✅ 3-pass budget allocator: guarantee minimums → proportional distribution → cap and redistribute
- ✅ TieredMemoryStore with namespaced Mem0 storage (`tier:stable`, `tier:episodic`, `tier:working:{session_id}`)
- ✅ MemoryRetriever as ContextContributor (priority 50) with cross-tier search
- ✅ 5-component relevance scoring: recency, similarity, frequency, source_priority, type_bonus
- ✅ Per-turn decay/amplification with greedy bin-packing in RollingContext
- ✅ SessionExtractor with tiered model selection (local llama3.2 for simple, Claude Haiku for complex)
- ✅ Retrieval classifier integration: ADJACENT score adjustment (×0.7), ABSENT memory boosting
- ✅ Mental model persona name fix (`"teacher"` → `"professor"`)
- ✅ Backward compatible (`token_budget=0` means no limit)

Change folder: [changes/scalable-memory-layers/](../../changes/scalable-memory-layers/)

### Cross-Cutting: Code Library & Development Philosophy

| Component                          | Status | OpenSpec / Notes                                                           |
| ---------------------------------- | ------ | -------------------------------------------------------------------------- |
| Library Models & Registry          | 📋     | `core/code_library/models.py`, `registry.py`                               |
| CodeLibraryManager                 | 📋     | `core/code_library/manager.py` — CRUD, search, stats                       |
| Library RAG Integration            | 📋     | `code-library` ChromaDB collection                                         |
| Library REST API                   | 📋     | `interfaces/library_api.py`                                                |
| Pattern Extraction Engine          | 📋     | `core/code_library/extractor.py`                                           |
| Pattern → Library Promotion        | 📋     | Integration with `core/pattern_learning.py`                                |
| AI Slop Review Skill               | 📋     | `core/code_library/reviewer.py` + bootstrap SKILL.md                       |
| Module Application                 | 📋     | Apply/instantiate modules in projects                                      |
| Philosophy Models & Spectrums      | 📋     | `core/philosophy/models.py`, `config/philosophy_spectrums.yaml`            |
| PhilosophyManager & Guided Process | 📋     | `core/philosophy/manager.py`, `guided_process.py`                          |
| Philosophy → Persona Integration   | 📋     | System prompt injection                                                    |
| Philosophy REST API                | 📋     | `interfaces/philosophy_api.py`                                             |
| Slash Command System               | 📋     | `core/commands/registry.py` — `/library`, `/philosophy`, `/model`, `/cost` |
| Library UI                         | 📋     | Electron library page                                                      |
| Philosophy UI                      | 📋     | Settings / standalone guided flow                                          |
| Multi-Model Library Routing        | 📋     | Free tier for extraction, frontier for design                              |

Change folder: [changes/code-library-and-dev-philosophy/](../changes/code-library-and-dev-philosophy/)
Specs: [code-library](../code-library/spec.md), [dev-philosophy](../dev-philosophy/spec.md)

### Tier 2: Packaging & Permissions

| Phase | Name                                               | Status | OpenSpec / Notes                                                                      |
| ----- | -------------------------------------------------- | ------ | ------------------------------------------------------------------------------------- |
| 9     | macOS Permissions                                  | 📋     |                                                                                       |
| 17    | Code Workspace (Monaco)                            | 📋     | [changes/phase-17-monaco-code-workspace/](../changes/phase-17-monaco-code-workspace/) |
| 24a   | Agent Swarms: Nexus Foundation                     | 📋     | [agent-swarms](../agent-swarms/spec.md); 23.5 complete — unblocked                    |
| 24b   | Agent Swarms: Multi-Agent Workflows                | 📋     | [agent-swarms](../agent-swarms/spec.md); After 24a                                    |
| 24c   | Agent Swarms: Execution Contexts                   | 📋     | [agent-swarms](../agent-swarms/spec.md); After 24a                                    |
| 24d   | Agent Swarms: Template UI + Progressive Disclosure | 📋     | [agent-swarms](../agent-swarms/spec.md); After 24b                                    |
| 24e   | Agent Swarms: Advanced Features                    | 📋     | [agent-swarms](../agent-swarms/spec.md); After 24d, DRM optional                      |

### Tier 3: Knowledge Platform (NEW)

| Phase   | Name                                   | Status  | Spec                                          | Dependencies                                                                                                             |
| ------- | -------------------------------------- | ------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 12a-ext | Knowledge Graph + Quality Pipeline     | ✅ ~95% | [knowledge-graph](../knowledge-graph/spec.md) | Phase 23.5 — Implemented via knowledge-graph-navigation + knowledge-graph-refinement                                     |
| 12b-ext | Knowledge Quality Controls             | ✅      | [knowledge-graph](../knowledge-graph/spec.md) | 12a-ext — Phase 12b complete (March 2026): 3 waves, 91 tests, graph intelligence + community detection + edge confidence |
| 12c     | Active Maintenance + Augmented Writing | 📋      | [knowledge-graph](../knowledge-graph/spec.md) | 12b-ext                                                                                                                  |
| 25a     | BookLore: Book Management + Parsing    | 📋      | [library](../library/spec.md)                 | 12a-ext (entity extraction)                                                                                              |
| 25b     | BookLore: Library RAG                  | 📋      | [library](../library/spec.md)                 | 25a                                                                                                                      |
| 25c     | BookLore: Knowledge Graph Integration  | 📋      | [library](../library/spec.md)                 | 25b, 12a-ext                                                                                                             |
| 25d     | BookLore: Highlights + Annotations     | 📋      | [library](../library/spec.md)                 | 25c                                                                                                                      |
| 30      | Capture System Foundation              | 📋      | [capture](../capture/spec.md)                 | 12a-ext (entity extraction)                                                                                              |
| 30a     | Smart Routing + Advanced Capture       | 📋      | [capture](../capture/spec.md)                 | 30                                                                                                                       |
| 31      | PARA + Maturity Lifecycle              | 📋      | [capture](../capture/spec.md)                 | 30                                                                                                                       |
| 32      | Review Workflows                       | 📋      | [capture](../capture/spec.md)                 | 31                                                                                                                       |
| 33      | BAD Canvas                             | 📋      | [canvas](../canvas/spec.md)                   | 12a-ext, RAG                                                                                                             |
| 34      | Publishing Pipeline (POSE)             | 📋      | [publishing](../publishing/spec.md)           | 31 (maturity), Scribe                                                                                                    |
| 34a     | Multi-Platform Publishing              | 📋      | [publishing](../publishing/spec.md)           | 34                                                                                                                       |

### Tier 4: Polish & Autonomy

| Phase | Name                                                           | Status | Spec                                                             | Dependencies                                                |
| ----- | -------------------------------------------------------------- | ------ | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| 18    | Onboarding & Progressive Reveal                                | 📋     | [onboarding](../onboarding/spec.md)                              | Tier 3 features exist                                       |
| 19    | Data Autonomy & Export                                         | 📋     | [data-autonomy](../data-autonomy/spec.md)                        | 12a-ext, 16                                                 |
| 13b   | User Profile System                                            | 📋     |                                                                  | Phase 13a                                                   |
| 25    | Code Architecture System                                       | 📋     | Phase 25 detail                                                  | Phase 17 (Code Workspace)                                   |
| 26    | Project Management & Planning                                  | 📋     | Phase 26 detail                                                  | Phase 24a (Agent Swarms)                                    |
| 27    | Designer Persona: Foundation + Generate Mode                   | 📋     | [personas](../personas/spec.md), [design](../design/spec.md)     | Phase 17 (partial — p5.js pipeline works without Monaco)    |
| 27a   | Designer: p5.js Pipeline + Lucide Icons + Design Systems       | 📋     | [changes/designer-profile/](../changes/designer-profile/)        | Phase 27                                                    |
| 27b   | Designer: Theme→Generator Integration + Feature Images         | 📋     | [themes](../themes/spec.md), [publishing](../publishing/spec.md) | 27a, [themes](../themes/spec.md)                            |
| 27c   | Designer: Intelligence (Consistency, Variation, Cross-Project) | 📋     |                                                                  | 27b                                                         |
| 27d   | Aesthetic Theme Engine                                         | 📋     | [themes](../themes/spec.md)                                      | Phase 11 (Personas); Phase 27 for full Designer integration |
| 28    | Open Polly Tools (Plugin Ecosystem)                            | 📋     | Phase 28 detail                                                  | Phase 24a, Phase 23.5                                       |
| 29    | Built-in Browser + DevTools                                    | 📋     | Phase 29 detail                                                  | Phase 17, Phase 27                                          |
| 35    | Analytics & Insights                                           | 📋     | [analytics](../analytics/spec.md)                                | 12a-ext, 30, 31                                             |
| 35a   | Visualization + Reflective Features                            | 📋     | [analytics](../analytics/spec.md)                                | 35                                                          |

### Tier 5: Distributed & Mobile (NEW)

| Phase | Name                                                        | Status | Spec                                                                                                                                       | Dependencies              |
| ----- | ----------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------- |
| 36    | DRM Phase 1: Peer Discovery (mDNS)                          | 📋     | [drm](../drm/spec.md)                                                                                                                      | Phase 23.5 (security)     |
| 36a   | DRM Phase 2: Automatic Distribution                         | 📋     | [drm](../drm/spec.md)                                                                                                                      | 36                        |
| 36b   | DRM Phase 3: Model Specialization                           | 📋     | [drm](../drm/spec.md)                                                                                                                      | 36a, Query Decomposition  |
| 36c   | DRM Phase 4: Advanced Features                              | 📋     | [drm](../drm/spec.md)                                                                                                                      | 36b                       |
| 36d   | DRM Phase 5: Remote Mesh (Cloudflare Tunnels + Ed25519 PKI) | 📋     | [drm](../drm/spec.md)                                                                                                                      | 36a                       |
| 36e   | DRM Phase 6: Meshtastic Gateway (LoRa resilience)           | 📋     | [drm](../drm/spec.md)                                                                                                                      | 36a                       |
| 37    | Mobile Companion Phase 1: Chat Relay                        | 📋     | [mobile](../mobile/spec.md)                                                                                                                | 36 (or REST fallback)     |
| 37a   | Mobile Companion Phase 2: Capture                           | 📋     | [mobile](../mobile/spec.md)                                                                                                                | 37, 30 (capture system)   |
| 37b   | Mobile Companion Phase 3: DRM Integration                   | 📋     | [mobile](../mobile/spec.md)                                                                                                                | 37a, 36a                  |
| 20a   | Email Intelligence + Triage/Compose Modes                   | 📋     | [communication](../communication/spec.md); [changes/learning-and-administrator-profiles/](../changes/learning-and-administrator-profiles/) | Phase 9 (Permissions)     |
| 20b   | Calendar & Action Items + Schedule/Remind Modes             | 📋     | [communication](../communication/spec.md)                                                                                                  | Phase 9, 20a              |
| 20c   | Progressive Communication Autonomy                          | 📋     | [communication](../communication/spec.md)                                                                                                  | 20b, Phase 13a (Patterns) |

---

## Dependency Graph (Simplified)

```
Tier 1 (current)
  ├── Architecture Integration (P0: Pattern Engine + Entity Model) ← START HERE
  │     ├── A.1 Unified Pattern Engine (no dependencies)
  │     ├── A.2 Entity Model Unification (parallel with A.1)
  │     ├── B. Integration Contracts (after A.1 + A.2)
  │     └── C. Library Extraction (after B, ongoing)
  │
  └── Phase 23.5 (Security) ─── prerequisite for Tiers 2-5 (benefits from A.1+A.2)
        │
        ├── Tier 2: Agent Swarms (after 23.5)
        │     ├── 24a (Nexus Foundation) → 24b (Multi-Agent Workflows) → 24d (Template UI)
        │     │     └── 24c (Execution Contexts, extends Capability Broker)
        │     └── 24e (Advanced: DRM integration, pattern learning, custom agents)
        │
        ├── Tier 3: Knowledge Platform
        │     ├── 12a-ext (Knowledge Graph + Quality) ← foundation for everything
        │     │     ├── 12b-ext (Quality Controls)
        │     │     │     └── 12c (Active Maintenance)
        │     │     ├── 25a (BookLore: Management) → 25b (Library RAG) → 25c (Graph Integration) → 25d (Highlights)
        │     │     ├── 30 (Capture Foundation)
        │     │     │     ├── 30a (Smart Routing)
        │     │     │     ├── 31 (PARA + Maturity)
        │     │     │     │     ├── 32 (Review Workflows)
        │     │     │     │     └── 34 (Publishing) → 34a (Multi-Platform)
        │     │     │     └── 37a (Mobile Capture)
        │     │     └── 33 (BAD Canvas)
        │     └── Tier 4: Polish & Autonomy
        │           ├── 18 (Onboarding) — after Tier 3 features exist
        │           ├── 19 (Data Autonomy)
        │           ├── 35 (Analytics) → 35a (Visualization)
        │           ├── 25 (Code Architecture) — after Phase 17
        │           ├── 26 (Project Management) — after Phase 24a
        │           ├── 27 (Designer Foundation) → 27a (p5.js + Lucide + Design Systems)
        │           │     ├── 27b (Theme→Generator + Feature Images)
        │           │     │     └── 27c (Intelligence: consistency, variation, cross-project)
        │           │     └── 27d (Aesthetic Theme Engine) ← can start independently (schema + persona integration)
        │           ├── 28 (Open Polly Tools) — after Phase 24a, 23.5
        │           └── 29 (Browser + DevTools) — after Phase 17, 27
        │
        └── Tier 5: Distributed (can parallel with Tiers 2-3)
              ├── 36 (DRM mDNS Discovery) → 36a (Distribution) → 36b (Specialization) → 36c (Advanced)
              │     ├── 36d (Remote Mesh: Cloudflare Tunnels + Ed25519 PKI)
              │     └── 36e (Meshtastic Gateway: LoRa resilience)
              ├── 37 (Mobile Chat) → 37a (Mobile Capture) → 37b (Mobile DRM)
              └── 24e (Agent Swarms Advanced) ← uses DRM for distributed agent execution
```

Note: DRM Phase 1 (peer discovery) is independent infrastructure and can start in parallel with Tiers 2–3. Agent Swarms Phase 24a–24b can begin as soon as 23.5 completes and can proceed in parallel with Knowledge Platform work. Phase 24e (Advanced) benefits from DRM but doesn't require it.

---

## Learning Profile & Administrator Profile (Cross-Cutting)

Touches Phase 22 (Teaching), Phase 18 (Onboarding), Phase 20 (Communication), and Personas:

| Component                          | Phase  | Depends On              |
| ---------------------------------- | ------ | ----------------------- |
| Learning page center area redesign | 22     | Phase 22 frontend       |
| Meta-pedagogy prompt injectors     | 22     | Personas infrastructure |
| Competency tracking                | 22, 18 | Prompt injectors        |
| Persona introductions              | 18     | Personas infrastructure |
| Administrator Triage mode          | 20a    | Email API integration   |
| Administrator Compose mode         | 20a    | Triage, RAG             |
| Administrator Schedule mode        | 20b    | Calendar API (Phase 9)  |
| Administrator Remind mode          | 20b    | Email + Calendar        |
| Communication slash commands       | 20a    | Slash command registry  |
| Voice matching                     | 20a    | Sent email access       |

See [changes/learning-and-administrator-profiles/](../changes/learning-and-administrator-profiles/) for proposal, design, and tasks.

---

## Constitutional Epistemology (Foundation Layer)

Not a phase — a foundation. The constitutional layer is the deepest system prompt layer, present in every conversation, every persona, every mode. It defines _how_ Polly thinks, not what topics are available.

| Component                                            | Depends On           | Notes                                                                        |
| ---------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------- |
| Constitutional prompt layer (`core/constitutional/`) | Persona system       | Deepest prompt injection — hardcoded, non-configurable                       |
| Constitutional mental models tier                    | Mental models system | Always-active models: Cui Bono, Historical Construction, Structural Analysis |
| RAG knowledge priorities                             | RAG system           | Priority seeding for structural/historical knowledge                         |
| Inoculation pedagogy                                 | Teaching system      | Professor teaches _about_ harmful ideologies as inoculation                  |

**Implementation note:** The constitutional layer can be implemented immediately — it's a prompt constant injected into `PersonaManager.build_system_prompt()`. No new infrastructure required. The mental models tier and RAG priorities are enhancements that deepen the foundation over time.

See [changes/constitutional-epistemology/](../changes/constitutional-epistemology/) for proposal and design. See [ethics spec](../ethics/spec.md) for full specification.

---

## Backlog & Reference Docs

- **Feature backlog:** [archive/root-docs/FEATURES_TO_BUILD.md](../../../archive/root-docs/FEATURES_TO_BUILD.md)
- **Roadmap analysis:** [archive/root-docs/ROADMAP_ANALYSIS_AND_NEXT_STEPS.md](../../../archive/root-docs/ROADMAP_ANALYSIS_AND_NEXT_STEPS.md)
- **Brain dumps / planning:** [archive/root-docs/BRAIN_DUMP_2026-01-31.md](../../../archive/root-docs/BRAIN_DUMP_2026-01-31.md), [planning/investigations/](../../../planning/investigations/), [archive/](../../../archive/)
- **Design philosophy:** [docs/planning/DESIGN_PHILOSOPHY.md](../../../docs/planning/DESIGN_PHILOSOPHY.md)

When starting a phase, create an OpenSpec change under [openspec/changes/](../changes/) (e.g. `phase-23.5-security-hardening/`) with `proposal.md`, `design.md`, `tasks.md`, then implement and update [status.md](status.md) and this roadmap.

**Phase 17 (Code Workspace):** Monaco path is the chosen approach (no VSCode/Void fork). See [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md) for decision and audit runbook; active change: [changes/phase-17-monaco-code-workspace/](../changes/phase-17-monaco-code-workspace/).
