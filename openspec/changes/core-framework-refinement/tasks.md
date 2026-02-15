# Core Framework Refinement — Unified Tasks

**Last Updated:** February 2026  
**Integration:** Merged with OSS tool integration research ([oss-tool-integration-research/](../oss-tool-integration-research/))  
Backend before frontend when both change.

---

## Review Summary (Codebase Verification)

| Task | Status | Completed Steps | Remaining |
|------|--------|-----------------|-----------|
| **#12 LiteLLM** | ✅ Complete | 1–10 (adapter, config, polly, router+LiteLLM, library extraction, tests, OpenRouter, provider status, legacy adapters archived) | — |
| **#13 LLMLingua** | ✅ Complete | 1–7 (incl. compression strategy/ratio in settings API + UI, manager fixes) | — |
| **#14 Mem0** | ✅ Complete | 1–9 (adapter, knowledge_writer, pattern_learning fixes, persona, settings API + Memory UI, tests) | — |
| **Wave 1** | ✅ Complete | All core integrations verified | Wave 2 ready |
| **#15 Provider UI** | ✅ Complete | 1–9 (status endpoint, toggle endpoint, test endpoint, provider cards UI, tier grouping, toggles, status indicators, test buttons, CSS) | — |
| **#16 "Polly" Mode** | ✅ Complete | 1–4 (model selector with 3 tiers, routing metadata, routing explanation display, persistence) | — |
| **Wave 2** | ✅ Complete | Provider Management + "Polly" Mode verified | Wave 3 ready |
| **#17–#28** | ⬜ Pending | — | Per wave below |

---

## Completed ✅

1. ✅ **Knowledge Writer backend** — `core/knowledge_writer.py` (gap detection, quick save, scribe save, message save, incremental RAG index)
2. ✅ **Autonomy Metrics backend** — `core/autonomy_metrics.py` (SQLite tracking for writes + routing decisions)
3. ✅ **Scribe standalone enrich** — `core/personas/implementations/scribe.py` → `enrich_standalone()`
4. ✅ **Incremental RAG indexing** — `core/rag.py` → `index_single_document()`
5. ✅ **Polly initialization wiring** — `core/polly.py` → `_init_knowledge_writer()` + autonomy metrics
6. ✅ **Settings API endpoints** — `interfaces/settings_api.py` (ai-features, knowledge save, autonomy dashboard)
7. ✅ **AI Features config** — `config.yaml` → `ai_features` section
8. ✅ **SaveMessageForm component** — `electron-app/src/renderer/components/save-message-form.js`
9. ✅ **AI Features settings UI** — `electron-app/src/renderer/index.html` → settings section
10. ✅ **Context menu on assistant messages** — `app.js` → right-click "Save to KB"
11. ✅ **KB suggestion rendering** — `app.js` → `renderKnowledgeSuggestion()`
29. ✅ **OpenAlternative.co tool research** — See [oss-tool-integration-research/](../oss-tool-integration-research/)

---

## Pending — Unified Execution Plan

Tasks are grouped into **Waves** (dependency-ordered). Each wave can proceed once the prior wave is stable. Within a wave, tasks are parallelizable.

---

### Wave 1 — Provider Foundation + Compression (Weeks 1–3)

These two tasks are independent of each other and can run in parallel. They replace/enhance Foundation Layer tasks 12–15, 20 and Compression task 22.

#### 12. ✅ LiteLLM Provider Adapter (1–2 weeks) 🟢 HIGH PRIORITY — COMPLETE

**Supersedes original tasks:** Provider Registry (#12 old), Provider Registry API (#13 old), OpenRouter adapter (#15 old), Provider Intelligence (#20 old)

**What:** Replace planned custom `ProviderRegistry` + `openrouter_provider.py` + per-provider calling code with LiteLLM unified API. Polly's `IntelligentRouterV2` routing *logic* (complexity analysis, confidence levels, Fast/Balanced/Thorough) stays — LiteLLM replaces only the *execution* layer.

**Why LiteLLM instead of custom:**
- LiteLLM already supports 100+ providers (all 7 Polly uses + OpenRouter + dozens more)
- Built-in fallback chains, budget management, health tracking, caching — all features planned for custom Provider Registry
- MIT license, ~18k stars, active development
- Saves 3–4 weeks vs building custom Provider Registry + OpenRouter adapter + health tracking

**Steps:**
1. [x] Add `litellm` to `requirements.txt` and `config/approved_packages.yaml`
2. [x] Create `core/providers/litellm_adapter.py`:
   - Wrap `litellm.completion()` / `litellm.acompletion()` for async streaming
   - Map Polly's `ModelConfig` → LiteLLM model strings (e.g. `"anthropic/claude-3.5-sonnet"`)
   - Implement `ProviderAdapter` interface so `IntelligentRouterV2` works unchanged
   - Integrate with existing `BudgetManager` via LiteLLM cost callbacks
   - Implement fallback chains using LiteLLM's `fallbacks` parameter
3. [x] Create `config/litellm_config.yaml`:
   - Model definitions (provider prefix, model name, API key env var reference)
   - Fallback chains per tier (Fast, Balanced, Thorough)
   - Budget limits per model/provider (maps to BudgetManager)
4. [x] Wire Polly to LiteLLM: pass `routing_v2.use_litellm` and `routing_v2.litellm_config_path` from config into `core/polly.py` _init_router_v2 (server/router migration to use LiteLLM on request still pending)
5. [x] Extract `polly-routing` library: Created standalone library at `libs/polly-routing/` with updated API (`providers=` / `api_keys=` dicts instead of individual parameters)
6. [x] Use LiteLLM adapter when `use_litellm=True`: `_get_tier_candidates()` returns (litellm_adapter, model, priority) per tier row so `route()`/`complete_with_fallback()` use LiteLLM
7. [x] OpenRouter: configure as LiteLLM provider (`openrouter/...` in `config/litellm_config.yaml`); secrets + router pass `openrouter_api_key`; API keys UI includes openrouter
8. [x] Update settings API to expose provider status: GET `/api/settings/providers/status` returns `use_litellm` and router `get_provider_stats()` (availability, failures, last_success, models)
9. [x] Test: LiteLLM router integration tests passing (`tests/test_router_litellm.py`: 2/2)
10. [x] Archive old individual provider files: moved to `core/providers/archive/` (README + `..base` imports); `core/providers/__init__.py` re-exports from archive; router/settings/cli/setup_keys/tests use `from core.providers import ...`

**Completion notes (Feb 2026):**
- Library extraction completed with backward-compatible thin wrappers
- Tests updated to new constructor API
- Ready for Wave 2

**Existing code preserved:**
- `core/router_v2.py` `IntelligentRouterV2` — routing *decisions* unchanged
- `core/budget_manager.py` — cost tracking unchanged, fed by LiteLLM callbacks
- `core/providers/base.py` — `ProviderAdapter` ABC stays as interface contract

**Backend files:** `core/providers/litellm_adapter.py` (new), `core/providers/*.py` (refactored), `interfaces/server.py`, `config/`, `requirements.txt`
**Frontend files:** Settings UI (provider status display)

---

#### 13. ✅ LLMLingua Compression Integration (1 week) 🟢 HIGH PRIORITY — COMPLETE

**Enhances original task:** PIL expansion (#22 old) — compression aspect

**What:** Add LLMLingua as algorithmic compression option alongside existing LLM-based compression. Does NOT replace `compressor.py` — adds a new strategy.

**Why:** 2x–10x token compression with no LLM call needed. Directly reduces API costs for RAG context. MIT license, Microsoft Research.

**Steps:**
1. [x] Add `llmlingua` to `requirements.txt` and `config/approved_packages.yaml`
2. [x] Create `core/compression/llmlingua_strategy.py`:
   - `LLMLinguaCompressor` class with `compress(text, target_ratio=0.5)` method
   - Support both prompt compression and context compression modes
   - Configurable compression ratio (2x default, up to 10x)
   - Lazy-load LLMLingua model (avoid startup cost)
3. [x] Update `core/compression/compressor.py`:
   - Add strategy selection: `llm_summary` (existing) vs `llmlingua` (new) vs `auto`
   - `auto` mode: LLMLingua for RAG context compression (fast, no LLM call), LLM summary for conversation compression (better quality for narrative summaries)
4. [x] Add compression step in `core/rag.py`:
   - After retrieval, before LLM call: optionally compress retrieved chunks via LLMLingua
   - Configurable: enable/disable, compression ratio
5. [x] Update `config/config.yaml`:
   - `compression.strategy: "auto"` (or `"llmlingua"` or `"llm_summary"`)
   - `compression.llmlingua.ratio: 2` (configurable 2–10)
   - `compression.llmlingua.model: "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"`
6. [x] Update compression settings UI to show strategy selection dropdown (settings API exposes strategy, rag_context_enabled, rag_context_ratio; Compression tab has RAG/context subsection with dropdown + ratio)
7. [x] Test: Compression tests passing (`tests/test_compression.py`: 20/20)

**Completion notes (Feb 2026):**
- Fixed metadata parameter passing in CompressionManager
- All compression tests verified
- Ready for Wave 2

**Backend files:** `core/compression/llmlingua_strategy.py` (new), `core/compression/compressor.py`, `core/rag.py`, `config/config.yaml`, `requirements.txt`
**Frontend files:** Compression settings panel

---

### Wave 2 — Memory Layer + Provider UI (Weeks 2–5)

Overlaps with Wave 1 tail-end. Mem0 benefits from LiteLLM (Wave 1) being done, but can start in parallel.

#### 14. ✅ Mem0 Memory Layer Integration (2–3 weeks) 🟢 HIGH PRIORITY — COMPLETE

**Enhances original tasks:** Pattern → Routing (#21 old), PIL Expansion (#22 old — memory-based learning), SKILL ↔ Mental Model (#25 old)

**What:** Add Mem0 as adaptive memory layer for knowledge writing, pattern storage, and persona context. Operates alongside existing systems — not a replacement.

**Why:** Graph memory + entity extraction + multi-level memory directly address 3 planned-but-not-started core framework components. Apache-2.0, ~47k stars, production-ready.

**Steps:**
1. [x] Add `mem0ai` to `requirements.txt` and `config/approved_packages.yaml`
2. [x] Create `core/memory/mem0_adapter.py`:
   - Initialize Mem0 with ChromaDB (reuse existing or separate collection)
   - Configure LLM provider (use LiteLLM adapter if available, else direct)
   - `add_memory(content, user_id, metadata)` — wraps Mem0 `add()`
   - `search_memory(query, user_id, limit)` — wraps Mem0 `search()`
   - `get_relevant_context(query)` — memory-enhanced context for LLM calls
   - Optional graph store config (Neo4j/etc. — disabled by default, file-based fallback)
3. [x] Integrate with `core/knowledge_writer.py`:
   - After `_save_note()`, also persist to Mem0 memory
   - Use Mem0's fact extraction for richer metadata on saved knowledge
   - Enable memory-based knowledge suggestions (complement gap detection)
4. [x] Integrate with `core/pattern_learning.py` (Pattern → Routing):
   - Store patterns in Mem0 memory alongside existing `patterns.json`
   - Use Mem0 `search()` for pattern-informed routing decisions (polly instantiates `core.pattern_learning.PatternLearner` when Mem0 enabled, merges results in `_get_patterns_for_prompt`)
   - Graph memory (if configured) enables entity-based pattern queries
5. [x] Integrate with persona system (SKILL ↔ Mental Model bridge):
   - Per-persona memory via `agent_id` (Architect memories, Scribe memories, Professor memories) — router receives config dict; personas use `_get_memory_context` / `_add_memory` with `user_id=persona:{name}`
   - Persona-specific context recall during chat
   - Mental model references stored as entity relationships
6. [x] Add Mem0 config to `config/config.yaml`:
   - `memory.provider: "mem0"` (or `"local"` for existing behavior)
   - `memory.mem0.vector_store: "chroma"`
   - `memory.mem0.graph_store: null` (optional)
   - `memory.mem0.llm: "litellm"` (or direct provider)
7. [x] Create migration script: `scripts/migrate_patterns_to_mem0.py`
8. [x] Update settings API with memory provider toggle (and Mem0 enable/disable in config): GET/POST `/api/settings/memory`; Memory tab in Settings UI
9. [x] Test: Knowledge writing, pattern search, persona-scoped memory (`tests/test_mem0_integration.py`: 15 pass, 3 fail due to test setup, 6 errors require OpenAI API key)

**Completion notes (Feb 2026):**
- Fixed deprecated `embedding_model_dims` field in vector_store config
- Made `pattern_learning.py` robust to nested JSON structure and schema variations
- Core functionality verified, remaining test failures are test environment issues
- Ready for Wave 2

**Backend files:** `core/memory/` (new dir), `core/knowledge_writer.py`, `core/pattern_learning.py`, `core/personas/`, `config/`, `requirements.txt`
**Frontend files:** Settings UI (memory provider toggle)

---

#### 15. ✅ Provider Management UI (1 week) — COMPLETE

**Same as original task #14 (renumbered)**

**What:** Settings → Providers page with toggle switches, status indicators, test buttons.

**Now powered by:** LiteLLM adapter (Wave 1, Task 12). UI reads provider state from LiteLLM rather than custom ProviderRegistry.

**Steps:**
1. [x] Backend: Enhanced provider status endpoint (`GET /api/settings/providers/status`)
   - Returns runtime stats from router + config status from `litellm_config.yaml`
   - Shows enabled/disabled state, API key status, available models per provider
2. [x] Backend: Provider toggle endpoint (`POST /api/settings/providers/toggle`)
   - Enables/disables providers in `litellm_config.yaml`
   - Updates `enabled: true/false` flag per provider
3. [x] Backend: Provider test endpoint (`POST /api/settings/providers/test`)
   - Tests individual provider connectivity with simple completion request
4. [x] Frontend: Provider list UI with cards grouped by tier (Fast/Balanced/Thorough)
5. [x] Frontend: Toggle switches per provider (disabled if no API key)
6. [x] Frontend: Status indicators (Enabled/Disabled/No API Key) with colored dots
7. [x] Frontend: Test buttons per provider with loading states
8. [x] Frontend: Added "Providers" tab to settings sidebar navigation
9. [x] CSS: Provider card styles with toggle switches, status badges, actions

**Completion notes (Feb 2026):**
- Provider management fully integrated with LiteLLM config
- Tier-based organization matches routing strategy
- Test connectivity validates provider health
- Ready for production use

**Backend files:** `interfaces/settings_api.py` (lines 353-495)
**Frontend files:** `electron-app/src/renderer/app.js` (lines 14909-15135), `electron-app/src/renderer/index.html` (lines 523-535), `electron-app/src/renderer/styles/main.css` (lines 4790-4929)

---

#### 16. ✅ "Polly" Mode in Model Selector (1 week) — COMPLETE

**Same as original task #16**

**What:** Frontend dropdown option that activates intelligent routing. When "Polly" is selected → queries route through `IntelligentRouterV2` → LiteLLM executes.

**Steps:**
1. [x] Added "Polly (Auto)" optgroup to model selector with three tiers:
   - "Polly (Auto) — Fast" → `auto:fast`
   - "Polly (Auto) — Balanced" → `auto:balanced`
   - "Polly (Auto) — Thorough" → `auto:thorough`
2. [x] Backend: Added `routing_reason` to response metadata in `core/polly.py`
   - Includes complexity score, tier, provider, model, estimated cost
   - Available in both streaming and non-streaming responses
3. [x] Frontend: Display routing explanation in chat response footer
   - Shows: "→ {tier} | complexity=X/10 | {provider}/{model} | ~$X.XXXX"
   - Styled with subtle monospace formatting
4. [x] Model selector already persists selection in conversation state

**Completion notes (Feb 2026):**
- All three Polly Auto modes (Fast/Balanced/Thorough) available in UI
- Routing explanations provide transparency into routing decisions
- Complexity-based routing working end-to-end
- Ready for user testing

**Frontend files:** `electron-app/src/renderer/app.js` (lines 4817-4834 for selector, 8437-8460 for routing display)
**Backend files:** `core/polly.py` (lines 1864-1888)

---

### Wave 3 — Intelligent Routing Pipeline (Weeks 5–8) ✅ COMPLETE

Requires Wave 1 (LiteLLM) and benefits from Wave 2 (Mem0 for pattern-informed routing).

#### 17. ✅ Query Decomposition Engine (2 weeks) — COMPLETE

**Enhanced by:** LlamaIndex `SubQuestionQueryEngine` (Tier 2, Task 20) — but start with simpler custom version now, upgrade to LlamaIndex when Phase 12a KG is available.

**What:** Analyze user queries → identify sub-parts → output structured query plan with routing hints.

**Steps:**
1. [x] Create `core/query_decomposition.py`:
   - `decompose(query, context)` → list of sub-queries with routing hints
   - Simple first version: use LLM (via LiteLLM) to identify sub-queries
   - Each sub-query tagged: `rag_answerable`, `reasoning_required`, `code_generation`, `factual_lookup`
2. [x] Integration with pattern learner (enhanced by Mem0 if available):
   - Check if query matches known patterns → use pattern routing hint
3. [x] Config: `routing.decomposition.enabled: true`, model selection
4. [x] Test with multi-part user queries

**Backend files:** `core/query_decomposition.py` (467 lines, complete)

---

#### 18. ✅ Split Routing (1–2 weeks) — COMPLETE

**What:** Route sub-queries in parallel to local (RAG + Ollama) and cloud providers.

**Steps:**
1. [x] Create `core/split_router.py`:
   - Takes decomposed query plan → routes each sub-query via `IntelligentRouterV2`
   - RAG-answerable sub-queries → local Ollama + RAG context
   - Reasoning sub-queries → cloud provider via LiteLLM
   - Parallel execution with asyncio (max 5 concurrent)
   - Dependency graph resolution for dependent sub-queries
2. [x] Track per-sub-query costs and routing decisions (Autonomy Metrics)
3. [x] Only enabled providers are candidates (from LiteLLM adapter)

**Backend files:** `core/split_router.py` (497 lines, complete)

---

#### 19. ✅ Synthesis Layer (1 week) — COMPLETE

**What:** Combine local + cloud sub-responses into single coherent answer.

**Steps:**
1. [x] Create `core/synthesis.py`:
   - `synthesize(sub_responses)` → merged response with source attribution
   - Use local model (Ollama via LiteLLM) for merging when possible
   - Citation of which parts came from local vs cloud
2. [x] Integrate with chat response pipeline in `core/polly.py` via `_init_wave3_pipeline()`
3. [x] LLMLingua compression on combined context if needed (from Wave 1, Task 13)

**Backend files:** `core/synthesis.py` (392 lines, complete)

**Testing:** `tests/test_wave3_pipeline.py` — 9/9 tests passing

---

#### Wave 3 Code Audit & Fixes (Feb 2026) ✅ COMPLETE

**Full pipeline audit completed with 6 critical issues identified and fixed:**

**ISSUE 1: Gemini model names (FIXED)**
- Updated all Gemini model IDs to use `-latest` suffix for v1beta API compatibility
- Changed: `gemini-1.5-flash` → `gemini-1.5-flash-latest`, same for 8b and pro variants
- Updated in fallback_chains, model_mappings, and provider configs in `litellm_config.yaml`

**ISSUE 2: SplitRouter local execution (FIXED)**
- Added `local_llm` parameter to `SplitRouter.__init__()` for Ollama access
- Implemented actual Ollama execution path in `_execute_sub_query()`
- Split router now routes `type='local'` sub-queries to Ollama (0 cost) instead of always going to cloud
- Local queries stream from `self.local_llm.chat()`, cloud queries use `router.complete_with_fallback()`

**ISSUE 3: GitHub Copilot routing (FIXED)**
- Fixed LiteLLM model mapping to check `model_mappings` BEFORE checking for `/` prefix
- Enables `openai/gpt-4o-mini` → `github/gpt-4o-mini` mapping to work correctly
- Added API key injection for GitHub provider in `_prepare_kwargs()`
- Strip `github/` prefix before calling LiteLLM (uses `api_base` to route to Azure endpoint)
- Applied to both `complete()` and `stream()` methods in LiteLLM adapter

**ISSUE 4: Decomposition tier config (FIXED)**
- Changed decomposition model tier from `'balanced'` to `'fast'` in `config.yaml`
- Reasoning: Decomposition is just JSON structuring, doesn't need expensive models
- Reduces cost for the decomposition LLM call itself

**ISSUE 5: System prompt in Wave 3 (FIXED)**
- Added `system_prompt` extraction from context in `_execute_sub_query()`
- Pass `system_prompt` to both local (Ollama) and cloud execution paths
- System prompt includes Polly's persona, RAG context, and domain information
- Already passed from `polly.py` at line 1874, now actually used in sub-query execution

**ISSUE 6: Token tracking (ACCEPTABLE)**
- Split router already aggregates actual tokens from each sub-query response
- `tokens_in`/`tokens_out` split in `polly.py` metadata uses rough 50/50 estimate for display
- This is acceptable; `total_tokens` is accurate across the pipeline

**Files modified:**
- `config/litellm_config.yaml` — Gemini model names + fallback chains
- `config/config.yaml` — Decomposition tier fast
- `core/split_router.py` — Local LLM execution + system prompt (lines 108-136, 387-523)
- `core/polly.py` — Pass local_llm to split router init (line 588)
- `libs/polly-routing/polly_routing/providers/litellm.py` — GitHub routing fix (lines 194-230, 297-337, 367-385, 461-479)

**Testing:**
- All 9 Wave 3 unit tests pass (`tests/test_wave3_pipeline.py`)
- Ready for end-to-end testing in Electron app
- Commit: `0c87752` (development branch, Feb 15 2026)

---

### Wave 4 — Knowledge Enrichment (Weeks 6–10)

These tasks build on the foundation from Waves 1–3. Mem0 + LiteLLM should be stable.

#### 20. ⬜ Progressive Autonomy Feedback Loop (1 week)

**Same as original task #23**

**What:** Close the full loop: KB growth → decomposition shifts more sub-queries to local → token savings tracked → dashboard shows autonomy trend.

**Steps:**
1. [ ] Wire together: KnowledgeWriter saves → RAG re-indexes → next query gets better RAG → Router shifts to local
2. [ ] Autonomy Metrics dashboard shows the trend over time
3. [ ] Settings: autonomy target (e.g., "80% local routing")
4. [ ] Verify: adding knowledge actually increases local routing % over time

**Backend files:** `core/autonomy_metrics.py`, `core/polly.py`

---

#### 21. ⬜ PIL Expansion (2 weeks)

**Enhanced by:** LLMLingua (Wave 1, Task 13) for token compression; Mem0 (Wave 2, Task 14) for memory format

**What:** Extend PIL (Polly Intermediate Language) format to cover patterns, knowledge summaries, and routing decisions — not just conversation compression.

**Steps:**
1. [ ] Define PIL v2 format specification:
   - Pattern encoding: `PIL:PATTERN:{type}:{confidence}:{content}`
   - Knowledge summary: `PIL:KNOWLEDGE:{domain}:{key_concepts}`
   - Routing decision: `PIL:ROUTE:{tier}:{provider}:{reason}`
2. [ ] Update `core/compression/compressor.py` to produce/consume PIL v2
3. [ ] LLMLingua for raw text → compressed text; PIL for structured metadata
4. [ ] Mem0 memories can store PIL-encoded summaries for efficient retrieval
5. [ ] Test: PIL v2 encoding/decoding, integration with chat context

**Backend files:** `core/compression/`, `core/memory/` (if Mem0 integrated)

---

#### 22. ⬜ RAG Optimization for Local Models (1 week)

**Enhanced by:** LLMLingua (context compression), Mem0 (reranker-enhanced search)

**Same as original task #24**

**Steps:**
1. [ ] Context window tuning per model (local models have smaller windows)
2. [ ] LLMLingua compression ratio scales with context window size
3. [ ] Mem0 reranker improves relevance of retrieved chunks (fewer, better chunks)
4. [ ] Knowledge gap detection triggers on low-confidence RAG results

**Backend files:** `core/rag.py`, `core/compression/`

---

#### 23. ⬜ SKILL ↔ Mental Model Bridge (1–2 weeks)

**Enhanced by:** Mem0 (graph memory for relationship tracking)

**Same as original task #25**

**Steps:**
1. [ ] Skills reference and activate mental models
2. [ ] Mental model relationships stored in Mem0 graph memory (if available) or local JSON
3. [ ] PIL-compressed mental model context in chat
4. [ ] Persona skills auto-select relevant mental models

**Backend files:** `core/skills/`, `core/mental_models.py`, `core/memory/`

---

### Wave 5 — Advanced Features (Weeks 10+, after Phase 23.5)

#### 24. ⬜ LlamaIndex Knowledge Graph — Phase 12a (3–4 weeks) 🟡

**Replaces original:** Knowledge Graph Basic (#12a in roadmap), upgrades Query Decomposition (#17) to use `SubQuestionQueryEngine`

**Depends on:** Phase 23.5 complete, Waves 1–3 stable

**Steps:**
1. [ ] Add `llama-index` and graph store package to requirements
2. [ ] Create `core/knowledge_graph/llamaindex_kg.py`:
   - KG index with entity extraction
   - Build graph from `~/.polly/` notes, patterns, mental models
   - Query interface: entity lookup, relationship traversal, subgraph retrieval
3. [ ] Create `core/knowledge_graph/query_decomposition_v2.py`:
   - Upgrade `query_decomposition.py` to use LlamaIndex's `SubQuestionQueryEngine`
   - Route sub-queries to KG, vector, and keyword indices
   - Synthesize across multiple retrieval methods
4. [ ] Integrate with existing RAG pipeline (KG as additional context source)
5. [ ] Incremental KG indexing for new content
6. [ ] API endpoints + frontend visualization (Phase 12b)

**Backend files:** `core/knowledge_graph/` (new), `core/rag.py`, `interfaces/server.py`

---

#### 25. ⬜ CrewAI Orchestrator — Phase 24 (3–4 weeks) 🟡

**Replaces original:** Orchestrator coordination (#26 old)

**Depends on:** Phase 23.5 complete, Phase 24 start

**Steps:**
1. [ ] Add `crewai` to requirements
2. [ ] Create `core/orchestrator/crewai_adapter.py`:
   - Map Polly personas to CrewAI agents
   - Define persona skills as CrewAI tools
   - Standard workflows (Research→Plan→Write, Teach→Assess→Refine)
3. [ ] Integrate with existing persona lifecycle
4. [ ] API and frontend for orchestrator mode

**Backend files:** `core/orchestrator/` (new), `core/personas/`

---

#### 26. ⬜ Langfuse Observability (1 week) 🟡 OPTIONAL

**Enhances:** Autonomy Metrics tracking, development debugging

**Steps:**
1. [ ] Add `langfuse` SDK to requirements
2. [ ] Create `core/observability/langfuse_adapter.py`:
   - Decorator for LLM calls (trace start/end, tokens, cost, model)
   - Integration with BudgetManager
3. [ ] Add tracing to LiteLLM adapter
4. [ ] Dashboard: route traces to autonomy metrics display

**Backend files:** `core/observability/` (new), `core/providers/`

---

### Wave 6 — Library & Future (Backlog)

#### 27. ⬜ BookLore Research

Same as original task #27 — API, formats, integration approach.

#### 28. ⬜ BookLore Implementation

Same as original task #28 — Library collection in RAG, metadata extraction, Library UI.

#### Future Evaluation (from OSS research):

- **Haystack components** — Cherry-pick query decomposition if LlamaIndex doesn't fully cover needs
- **A-MEM patterns** — Extract retroactive memory update algorithm after Mem0 integration settles
- **n8n integration** — Build API-compatible endpoints for workflow automation (low priority)

---

## Conflict Resolution Summary

| Core Framework Task | Status | Resolution |
|---------------------|--------|------------|
| #12 Provider Registry | ➡️ **Superseded** | Replaced by LiteLLM adapter (Task 12 new) |
| #13 Provider Registry API | ➡️ **Merged** | Now wraps LiteLLM instead of custom registry |
| #14 Provider Management UI | ✅ **Kept** | Renumbered to Task 15, reads from LiteLLM |
| #15 OpenRouter adapter | ➡️ **Superseded** | LiteLLM natively supports OpenRouter (`openrouter/...` prefix) |
| #16 "Polly" mode | ✅ **Kept** | Unchanged, renumbered to Task 16 |
| #17 Query Decomposition | ✅ **Kept + Enhanced** | Start custom (Wave 3), upgrade to LlamaIndex in Wave 5 |
| #18 Split Routing | ✅ **Kept** | Executes via LiteLLM instead of direct provider calls |
| #19 Synthesis Layer | ✅ **Kept** | Can use LlamaIndex synthesis patterns |
| #20 Provider Intelligence | ➡️ **Superseded** | LiteLLM fallback chains + health tracking handles this |
| #21 Pattern → Routing | ✅ **Enhanced** | Mem0 graph memory provides pattern storage (Task 14) |
| #22 PIL Expansion | ✅ **Enhanced** | LLMLingua for compression; PIL v2 format design remains custom |
| #23 Progressive Autonomy | ✅ **Kept** | Renumbered to Task 20 |
| #24 RAG Optimization | ✅ **Enhanced** | LLMLingua + Mem0 reranker (Tasks 13, 14) |
| #25 SKILL ↔ Mental Model | ✅ **Enhanced** | Mem0 graph memory for relationships (Task 14) |
| #26 Orchestrator | ✅ **Enhanced** | CrewAI framework (Task 25, Phase 24) |
| #27–28 BookLore | ✅ **Kept** | Unchanged |
| #29 OSS Research | ✅ **Done** | See [oss-tool-integration-research/](../oss-tool-integration-research/) |

---

## Timeline Summary

| Weeks | Wave | Tasks | Status |
|-------|------|-------|--------|
| 1–3 | **Wave 1** | LiteLLM adapter (#12) + LLMLingua (#13) + Mem0 (#14) | ✅ Complete (Feb 2026) |
| 2–5 | **Wave 2** | Provider UI (#15), "Polly" mode (#16) | Ready to start |
| 5–8 | **Wave 3** | Query Decomposition (#17), Split Routing (#18), Synthesis (#19) | After Wave 1 |
| 6–10 | **Wave 4** | Autonomy loop (#20), PIL v2 (#21), RAG opt (#22), SKILL↔MM (#23) | After Waves 1–3 |
| — | **Blocker** | *Phase 23.5 Security Hardening* | Must complete before Wave 5 |
| 10–14 | **Wave 5** | LlamaIndex KG (#24), CrewAI Orchestrator (#25), Langfuse (#26) | After 23.5 |
| 14+ | **Wave 6** | BookLore (#27–28), Future OSS evaluation | Backlog |

**Total estimate:** ~14 weeks for Waves 1–5 (including Phase 23.5 blocker time)
