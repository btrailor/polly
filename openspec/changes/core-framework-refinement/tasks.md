# Core Framework Refinement — Unified Tasks

**Last Updated:** February 2026  
**Integration:** Merged with OSS tool integration research ([oss-tool-integration-research/](../oss-tool-integration-research/))  
Backend before frontend when both change.

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

#### 12. ⬜ LiteLLM Provider Adapter (1–2 weeks) 🟢 HIGH PRIORITY

**Supersedes original tasks:** Provider Registry (#12 old), Provider Registry API (#13 old), OpenRouter adapter (#15 old), Provider Intelligence (#20 old)

**What:** Replace planned custom `ProviderRegistry` + `openrouter_provider.py` + per-provider calling code with LiteLLM unified API. Polly's `IntelligentRouterV2` routing *logic* (complexity analysis, confidence levels, Fast/Balanced/Thorough) stays — LiteLLM replaces only the *execution* layer.

**Why LiteLLM instead of custom:**
- LiteLLM already supports 100+ providers (all 7 Polly uses + OpenRouter + dozens more)
- Built-in fallback chains, budget management, health tracking, caching — all features planned for custom Provider Registry
- MIT license, ~18k stars, active development
- Saves 3–4 weeks vs building custom Provider Registry + OpenRouter adapter + health tracking

**Steps:**
1. [ ] Add `litellm` to `requirements.txt` and `config/approved_packages.yaml`
2. [ ] Create `core/providers/litellm_adapter.py`:
   - Wrap `litellm.completion()` / `litellm.acompletion()` for async streaming
   - Map Polly's `ModelConfig` → LiteLLM model strings (e.g. `"anthropic/claude-3.5-sonnet"`)
   - Implement `ProviderAdapter` interface so `IntelligentRouterV2` works unchanged
   - Integrate with existing `BudgetManager` via LiteLLM cost callbacks
   - Implement fallback chains using LiteLLM's `fallbacks` parameter
3. [ ] Create `config/litellm_config.yaml`:
   - Model definitions (provider prefix, model name, API key env var reference)
   - Fallback chains per tier (Fast, Balanced, Thorough)
   - Budget limits per model/provider (maps to BudgetManager)
4. [ ] Migrate `interfaces/server.py` LLM calls to use LiteLLM adapter
5. [ ] Migrate existing provider adapters:
   - `anthropic_provider.py` → LiteLLM `"anthropic/..."` prefix
   - `openai_provider.py` → LiteLLM `"openai/..."` prefix (direct)
   - `gemini_provider.py` → LiteLLM `"gemini/..."` prefix
   - `github_provider.py` → LiteLLM mapping
   - `grok_provider.py` → LiteLLM mapping
   - `mistral_provider.py` → LiteLLM `"mistral/..."` prefix
   - `perplexity_provider.py` → LiteLLM `"perplexity/..."` prefix
   - Ollama → LiteLLM `"ollama/..."` prefix
6. [ ] Update `IntelligentRouterV2.complete_with_fallback()` to use LiteLLM adapter
7. [ ] OpenRouter: configure as LiteLLM provider (`"openrouter/..."` prefix) — replaces need for custom `openrouter_provider.py`
8. [ ] Update settings API to expose provider status from LiteLLM
9. [ ] Test: All existing providers work through LiteLLM (Anthropic, OpenAI, Gemini, Mistral, Grok, Perplexity, Ollama)
10. [ ] Archive old individual provider files (keep as reference, import from litellm_adapter)

**Existing code preserved:**
- `core/router_v2.py` `IntelligentRouterV2` — routing *decisions* unchanged
- `core/budget_manager.py` — cost tracking unchanged, fed by LiteLLM callbacks
- `core/providers/base.py` — `ProviderAdapter` ABC stays as interface contract

**Backend files:** `core/providers/litellm_adapter.py` (new), `core/providers/*.py` (refactored), `interfaces/server.py`, `config/`, `requirements.txt`
**Frontend files:** Settings UI (provider status display)

---

#### 13. 🔄 LLMLingua Compression Integration (1 week) 🟢 HIGH PRIORITY — IN PROGRESS

**Enhances original task:** PIL expansion (#22 old) — compression aspect

**What:** Add LLMLingua as algorithmic compression option alongside existing LLM-based compression. Does NOT replace `compressor.py` — adds a new strategy.

**Why:** 2x–10x token compression with no LLM call needed. Directly reduces API costs for RAG context. MIT license, Microsoft Research.

**Steps:**
1. [ ] Add `llmlingua` to `requirements.txt` and `config/approved_packages.yaml`
2. [ ] Create `core/compression/llmlingua_strategy.py`:
   - `LLMLinguaCompressor` class with `compress(text, target_ratio=0.5)` method
   - Support both prompt compression and context compression modes
   - Configurable compression ratio (2x default, up to 10x)
   - Lazy-load LLMLingua model (avoid startup cost)
3. [ ] Update `core/compression/compressor.py`:
   - Add strategy selection: `llm_summary` (existing) vs `llmlingua` (new) vs `auto`
   - `auto` mode: LLMLingua for RAG context compression (fast, no LLM call), LLM summary for conversation compression (better quality for narrative summaries)
4. [ ] Add compression step in `core/rag.py`:
   - After retrieval, before LLM call: optionally compress retrieved chunks via LLMLingua
   - Configurable: enable/disable, compression ratio
5. [ ] Update `config/config.yaml`:
   - `compression.strategy: "auto"` (or `"llmlingua"` or `"llm_summary"`)
   - `compression.llmlingua.ratio: 2` (configurable 2–10)
   - `compression.llmlingua.model: "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"`
6. [ ] Update compression settings UI to show strategy selection dropdown
7. [ ] Test: Compare token usage before/after; verify answer quality maintained

**Backend files:** `core/compression/llmlingua_strategy.py` (new), `core/compression/compressor.py`, `core/rag.py`, `config/config.yaml`, `requirements.txt`
**Frontend files:** Compression settings panel

---

### Wave 2 — Memory Layer + Provider UI (Weeks 2–5)

Overlaps with Wave 1 tail-end. Mem0 benefits from LiteLLM (Wave 1) being done, but can start in parallel.

#### 14. ⬜ Mem0 Memory Layer Integration (2–3 weeks) 🟢 HIGH PRIORITY

**Enhances original tasks:** Pattern → Routing (#21 old), PIL Expansion (#22 old — memory-based learning), SKILL ↔ Mental Model (#25 old)

**What:** Add Mem0 as adaptive memory layer for knowledge writing, pattern storage, and persona context. Operates alongside existing systems — not a replacement.

**Why:** Graph memory + entity extraction + multi-level memory directly address 3 planned-but-not-started core framework components. Apache-2.0, ~47k stars, production-ready.

**Steps:**
1. [ ] Add `mem0ai` to `requirements.txt` and `config/approved_packages.yaml`
2. [ ] Create `core/memory/mem0_adapter.py`:
   - Initialize Mem0 with ChromaDB (reuse existing or separate collection)
   - Configure LLM provider (use LiteLLM adapter if available, else direct)
   - `add_memory(content, user_id, metadata)` — wraps Mem0 `add()`
   - `search_memory(query, user_id, limit)` — wraps Mem0 `search()`
   - `get_relevant_context(query)` — memory-enhanced context for LLM calls
   - Optional graph store config (Neo4j/etc. — disabled by default, file-based fallback)
3. [ ] Integrate with `core/knowledge_writer.py`:
   - After `_save_note()`, also persist to Mem0 memory
   - Use Mem0's fact extraction for richer metadata on saved knowledge
   - Enable memory-based knowledge suggestions (complement gap detection)
4. [ ] Integrate with `core/pattern_learning.py` (Pattern → Routing):
   - Store patterns in Mem0 memory alongside existing `patterns.json`
   - Use Mem0 `search()` for pattern-informed routing decisions
   - Graph memory (if configured) enables entity-based pattern queries
5. [ ] Integrate with persona system (SKILL ↔ Mental Model bridge):
   - Per-persona memory via `agent_id` (Architect memories, Scribe memories, Professor memories)
   - Persona-specific context recall during chat
   - Mental model references stored as entity relationships
6. [ ] Add Mem0 config to `config/config.yaml`:
   - `memory.provider: "mem0"` (or `"local"` for existing behavior)
   - `memory.mem0.vector_store: "chroma"`
   - `memory.mem0.graph_store: null` (optional)
   - `memory.mem0.llm: "litellm"` (or direct provider)
7. [ ] Create migration script: `scripts/migrate_patterns_to_mem0.py`
8. [ ] Update settings API with memory provider toggle
9. [ ] Test: Knowledge writing, pattern search, persona-scoped memory

**Backend files:** `core/memory/` (new dir), `core/knowledge_writer.py`, `core/pattern_learning.py`, `core/personas/`, `config/`, `requirements.txt`
**Frontend files:** Settings UI (memory provider toggle)

---

#### 15. ⬜ Provider Management UI (1 week)

**Same as original task #14 (renumbered)**

**What:** Settings → Providers page with toggle switches, status indicators, test buttons.

**Now powered by:** LiteLLM adapter (Wave 1, Task 12). UI reads provider state from LiteLLM rather than custom ProviderRegistry.

**Steps:**
1. [ ] Provider list from LiteLLM model config
2. [ ] Toggle enable/disable per provider
3. [ ] Status indicators (connected/disconnected/rate-limited)
4. [ ] API key entry/test per provider
5. [ ] Provider health display

**Backend files:** `interfaces/settings_api.py` (new endpoints)
**Frontend files:** Settings UI provider management section

---

#### 16. ⬜ "Polly" Mode in Model Selector (1 week)

**Same as original task #16**

**What:** Frontend dropdown option that activates intelligent routing. When "Polly" is selected → queries route through `IntelligentRouterV2` → LiteLLM executes.

**Steps:**
1. [ ] Add "Polly (Auto)" option to model selector dropdown in `app.js`
2. [ ] When selected, chat requests go to router endpoint (not direct provider)
3. [ ] Display routing explanation in response metadata (which provider was chosen and why)
4. [ ] Persist selection in electron-store

**Frontend files:** `app.js`, `index.html`
**Backend files:** `interfaces/server.py` (routing endpoint)

---

### Wave 3 — Intelligent Routing Pipeline (Weeks 5–8)

Requires Wave 1 (LiteLLM) and benefits from Wave 2 (Mem0 for pattern-informed routing).

#### 17. ⬜ Query Decomposition Engine (2 weeks)

**Enhanced by:** LlamaIndex `SubQuestionQueryEngine` (Tier 2, Task 20) — but start with simpler custom version now, upgrade to LlamaIndex when Phase 12a KG is available.

**What:** Analyze user queries → identify sub-parts → output structured query plan with routing hints.

**Steps:**
1. [ ] Create `core/query_decomposition.py`:
   - `decompose(query, context)` → list of sub-queries with routing hints
   - Simple first version: use LLM (via LiteLLM) to identify sub-queries
   - Each sub-query tagged: `rag_answerable`, `reasoning_required`, `code_generation`, `factual_lookup`
2. [ ] Integration with pattern learner (enhanced by Mem0 if available):
   - Check if query matches known patterns → use pattern routing hint
3. [ ] Config: `routing.decomposition.enabled: true`, model selection
4. [ ] Test with multi-part user queries

**Backend files:** `core/query_decomposition.py` (new)

---

#### 18. ⬜ Split Routing (1–2 weeks)

**What:** Route sub-queries in parallel to local (RAG + Ollama) and cloud providers.

**Steps:**
1. [ ] Create `core/split_router.py`:
   - Takes decomposed query plan → routes each sub-query via `IntelligentRouterV2`
   - RAG-answerable sub-queries → local Ollama + RAG context
   - Reasoning sub-queries → cloud provider via LiteLLM
   - Parallel execution with asyncio
2. [ ] Track per-sub-query costs and routing decisions (Autonomy Metrics)
3. [ ] Only enabled providers are candidates (from LiteLLM adapter)

**Backend files:** `core/split_router.py` (new)

---

#### 19. ⬜ Synthesis Layer (1 week)

**What:** Combine local + cloud sub-responses into single coherent answer.

**Steps:**
1. [ ] Create `core/synthesis.py`:
   - `synthesize(sub_responses)` → merged response with source attribution
   - Use local model (Ollama via LiteLLM) for merging when possible
   - Citation of which parts came from local vs cloud
2. [ ] Integrate with chat response pipeline in `interfaces/server.py`
3. [ ] LLMLingua compression on combined context if needed (from Wave 1, Task 13)

**Backend files:** `core/synthesis.py` (new)

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
| 1–3 | **Wave 1** | LiteLLM adapter (#12) + LLMLingua (#13) in parallel | Ready to start |
| 2–5 | **Wave 2** | Mem0 memory (#14), Provider UI (#15), "Polly" mode (#16) | Ready to start |
| 5–8 | **Wave 3** | Query Decomposition (#17), Split Routing (#18), Synthesis (#19) | After Wave 1 |
| 6–10 | **Wave 4** | Autonomy loop (#20), PIL v2 (#21), RAG opt (#22), SKILL↔MM (#23) | After Waves 1–3 |
| — | **Blocker** | *Phase 23.5 Security Hardening* | Must complete before Wave 5 |
| 10–14 | **Wave 5** | LlamaIndex KG (#24), CrewAI Orchestrator (#25), Langfuse (#26) | After 23.5 |
| 14+ | **Wave 6** | BookLore (#27–28), Future OSS evaluation | Backlog |

**Total estimate:** ~14 weeks for Waves 1–5 (including Phase 23.5 blocker time)
