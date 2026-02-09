# Tasks: Open-Source Tool Integration

**Change:** `oss-tool-integration-research`  
**Depends on:** Phase 23.5 (Security Hardening) for Tier 2 tasks  
**Estimated total:** 8–12 weeks across all tiers  
**Integrated into:** [core-framework-refinement/tasks.md](../core-framework-refinement/tasks.md) — see unified execution plan there

> **NOTE:** This file contains the original OSS-specific task breakdown. The **authoritative unified plan** that merges these tasks with existing Core Framework Refinement work is in [core-framework-refinement/tasks.md](../core-framework-refinement/tasks.md). Refer to that file for execution ordering, wave structure, and conflict resolutions.

---

## Tier 1 — Immediate Integrations (4–6 weeks)

These three integrations are independent and can be started in parallel.

### Task 1: LiteLLM Provider Adapter (1–2 weeks) 🟢 HIGH PRIORITY

**What:** Replace planned Provider Registry, OpenRouter gateway, and custom provider implementations with LiteLLM unified API.

**Replaces roadmap items:**
- Provider Registry (`core/provider_registry.py`)
- OpenRouter Gateway (`core/providers/openrouter_provider.py`)
- Per-provider health tracking (built into LiteLLM)

**Steps:**
1. [ ] Add `litellm` to `requirements.txt` and `config/approved_packages.yaml`
2. [ ] Create `core/providers/litellm_adapter.py`:
   - Wrap `litellm.completion()` and `litellm.acompletion()` for async
   - Map Polly's model config → LiteLLM model strings
   - Integrate with existing `BudgetManager` (intercept cost callbacks)
   - Implement fallback chain using LiteLLM's `fallbacks` parameter
3. [ ] Create `config/litellm_config.yaml`:
   - Model definitions (provider, model name, API key reference)
   - Fallback chains matching Polly's Fast/Balanced/Thorough tiers
   - Budget limits per model/provider
4. [ ] Migrate `interfaces/server.py` LLM calls to use adapter
5. [ ] Migrate Ollama calls to use LiteLLM's Ollama provider
6. [ ] Update Router v2 (`core/router.py` or equivalent) to use LiteLLM for model selection
7. [ ] Update settings API to expose LiteLLM provider status
8. [ ] Test: All existing providers work via LiteLLM (Anthropic, OpenAI, Gemini, Mistral, Grok, Perplexity, Ollama)
9. [ ] Update `config/config.yaml` docs with new provider config format

**Backend files affected:** `core/providers/`, `interfaces/server.py`, `config/`, `requirements.txt`  
**Frontend files affected:** Settings UI (provider status display)

---

### Task 2: LLMLingua Compression Integration (1 week) 🟢 HIGH PRIORITY

**What:** Add LLMLingua as an algorithmic compression option alongside existing LLM-based compression.

**Enhances roadmap items:**
- Compression system (`core/compression/compressor.py`)
- RAG context optimization
- PIL Expansion (token efficiency)

**Steps:**
1. [ ] Add `llmlingua` to `requirements.txt` and `config/approved_packages.yaml`
2. [ ] Create `core/compression/llmlingua_strategy.py`:
   - Implement `compress(text, target_ratio)` using LLMLingua-2
   - Support both prompt compression and context compression modes
   - Configurable compression ratio (2x default, up to 10x)
3. [ ] Update `core/compression/compressor.py`:
   - Add strategy selection: `llm_summary` (existing) vs `llmlingua` (new)
   - Default to LLMLingua for RAG context compression (faster, no LLM call needed)
   - Keep LLM summary for conversation compression (better quality for summaries)
4. [ ] Add compression step in `core/rag.py`:
   - After retrieval, before LLM call: compress retrieved chunks via LLMLingua
   - Configurable: enable/disable, compression ratio
5. [ ] Update `config/config.yaml`:
   - `compression.strategy: "llmlingua"` (or `"llm_summary"` or `"auto"`)
   - `compression.llmlingua.ratio: 2` (configurable)
6. [ ] Update compression settings UI to show strategy selection
7. [ ] Test: Compare token usage before/after; verify quality maintained

**Backend files affected:** `core/compression/`, `core/rag.py`, `config/config.yaml`, `requirements.txt`  
**Frontend files affected:** Compression settings panel

---

### Task 3: Mem0 Memory Layer Integration (2–3 weeks) 🟢 HIGH PRIORITY

**What:** Add Mem0 as adaptive memory layer for knowledge writing, pattern storage, and persona context.

**Enhances roadmap items:**
- Knowledge Writing (`core/knowledge_writer.py`)
- Pattern → Routing (new capability)
- PIL Expansion (memory-based learning)
- SKILL ↔ Mental Model connections

**Steps:**
1. [ ] Add `mem0ai` to `requirements.txt` and `config/approved_packages.yaml`
2. [ ] Create `core/memory/mem0_adapter.py`:
   - Initialize Mem0 with ChromaDB (reuse Polly's existing ChromaDB) or separate collection
   - Configure LLM provider (use LiteLLM adapter from Task 1 if available)
   - Implement `add_memory(content, user_id, metadata)` — wraps Mem0 `add()`
   - Implement `search_memory(query, user_id, limit)` — wraps Mem0 `search()`
   - Implement `get_relevant_context(query)` — memory-enhanced context for LLM calls
3. [ ] Integrate with `core/knowledge_writer.py`:
   - After saving knowledge to file, also persist to Mem0 memory
   - Use Mem0's fact extraction for richer metadata
   - Enable memory-based knowledge suggestions
4. [ ] Integrate with `core/pattern_learning.py`:
   - Store patterns in Mem0 graph memory (if Neo4j/graph configured)
   - Fall back to existing `patterns.json` if graph not available
   - Use Mem0 search for pattern-informed routing decisions
5. [ ] Integrate with persona system:
   - Per-persona memory sessions (Architect memories, Scribe memories, Professor memories)
   - Use `agent_id` parameter to scope memories by persona
6. [ ] Add Mem0 config to `config/config.yaml`:
   - `memory.provider: "mem0"` (or `"local"` for existing behavior)
   - `memory.mem0.vector_store: "chroma"` (reuse existing)
   - `memory.mem0.graph_store: null` (optional, for advanced users)
   - `memory.mem0.llm: "litellm"` (use LiteLLM if integrated)
7. [ ] Create migration script: `scripts/migrate_patterns_to_mem0.py`
   - Read `patterns.json` → insert into Mem0 memory
   - Preserve pattern types, timestamps, and metadata
8. [ ] Update settings API with memory provider toggle
9. [ ] Test: Knowledge writing with Mem0, pattern search, persona-scoped memory

**Backend files affected:** `core/memory/` (new), `core/knowledge_writer.py`, `core/pattern_learning.py`, `core/personas/`, `config/`, `requirements.txt`  
**Frontend files affected:** Settings UI (memory provider toggle)

---

## Tier 2 — Phase-Aligned Integrations (after Phase 23.5)

### Task 4: LlamaIndex Knowledge Graph — Phase 12a (3–4 weeks) 🟡

**What:** Use LlamaIndex's KG index for Phase 12a (Knowledge Graph Basic).

**Steps:**
1. [ ] Add `llama-index` and `llama-index-graph-stores-neo4j` (or simple graph store) to requirements
2. [ ] Create `core/knowledge_graph/llamaindex_kg.py`:
   - Initialize KG index with entity extraction
   - Build graph from existing notes and knowledge base
   - Query interface: entity lookup, relationship traversal, subgraph retrieval
3. [ ] Create `core/knowledge_graph/query_decomposition.py`:
   - Use LlamaIndex's `SubQuestionQueryEngine`
   - Decompose complex queries into sub-queries routed to KG, vector, and keyword indices
   - Synthesize responses from multiple retrievals
4. [ ] Integrate with existing RAG pipeline:
   - Add KG retrieval as additional context source alongside ChromaDB and BM25
   - Fusion scoring across all retrieval methods
5. [ ] Build knowledge graph from existing data:
   - Script to index `~/.polly/` notes, patterns, mental models into KG
   - Incremental indexing for new content
6. [ ] API endpoints: `GET /api/knowledge-graph/entities`, `/relationships`, `/query`
7. [ ] Frontend: Knowledge graph visualization (optional, Phase 12b)

**Depends on:** Phase 23.5 complete, Tasks 1–3 ideally done  
**Backend files affected:** `core/knowledge_graph/` (new), `core/rag.py`, `interfaces/server.py`

---

### Task 5: CrewAI Orchestrator — Phase 24 (3–4 weeks) 🟡

**What:** Use CrewAI for Phase 24 (Orchestrator Mode) multi-persona collaboration.

**Steps:**
1. [ ] Add `crewai` to requirements
2. [ ] Create `core/orchestrator/crewai_adapter.py`:
   - Map Polly personas to CrewAI agents (Architect → planning agent, Scribe → writing agent, Professor → teaching agent)
   - Define persona skills as CrewAI tools
   - Implement task delegation workflows
3. [ ] Define standard workflows:
   - Research → Plan → Write (Architect + Scribe collaboration)
   - Teach → Assess → Refine (Professor + Scribe collaboration)
   - Full project workflow (all three personas)
4. [ ] Integrate with existing persona lifecycle
5. [ ] API: `POST /api/orchestrator/run-workflow`
6. [ ] Frontend: Orchestrator mode toggle and workflow status

**Depends on:** Phase 23.5, Phase 24 start  
**Backend files affected:** `core/orchestrator/` (new), `core/personas/`

---

### Task 6: Langfuse Observability (1 week) 🟡

**What:** Add LLM call tracing for development, debugging, and autonomy metrics.

**Steps:**
1. [ ] Add `langfuse` to requirements
2. [ ] Create `core/observability/langfuse_adapter.py`:
   - Decorator for LLM calls (trace start/end, tokens, cost, model)
   - Integration with BudgetManager for unified cost tracking
3. [ ] Add tracing to LiteLLM adapter (if Task 1 done) or existing LLM calls
4. [ ] Configure: self-hosted Langfuse server or cloud (optional)
5. [ ] Dashboard: Route traces to autonomy metrics display

**Depends on:** None (independent), but more valuable after Task 1  
**Backend files affected:** `core/observability/` (new), `core/providers/`

---

## Tier 3 — Future Evaluation

### Task 7: Haystack Query Decomposition Components 🟡

- Cherry-pick Haystack's query expansion and decomposition components if LlamaIndex doesn't fully cover needs in Task 4.
- Evaluate after Phase 12a implementation.

### Task 8: A-MEM Memory Evolution Patterns 🟡

- Extract A-MEM's retroactive memory update algorithm for pattern learner enhancement.
- Verify license before incorporating code.
- Evaluate after Mem0 integration (Task 3) to identify remaining gaps.

### Task 9: n8n Workflow Integration 🟡

- Build n8n-compatible REST API endpoints for Polly.
- Create custom n8n node package.
- Low priority; evaluate at Tier 3+ based on user demand.

---

## Summary Timeline

| Week | Tasks | Status |
|------|-------|--------|
| 1–2 | Task 1 (LiteLLM) + Task 2 (LLMLingua) in parallel | Ready to start |
| 2–4 | Task 3 (Mem0) — can overlap with Task 1 completion | Ready to start |
| 5–6 | Testing, stabilization, settings UI updates | — |
| — | *Phase 23.5 Security Hardening* | Blocker for Tier 2 |
| 7–10 | Task 4 (LlamaIndex KG) — Phase 12a | After 23.5 |
| 11–14 | Task 5 (CrewAI Orchestrator) — Phase 24 | After 23.5 |
| Anytime | Task 6 (Langfuse) — low effort, independent | Optional |

---

## Definition of Done

- [ ] All Tier 1 tools integrated and tested
- [ ] `requirements.txt` and `approved_packages.yaml` updated
- [ ] `config/config.yaml` has integration configuration section
- [ ] Settings UI has toggles for each integration
- [ ] Existing functionality preserved (all integrations are additive/optional)
- [ ] OpenSpec specs updated: `rag/spec.md`, `patterns/spec.md`, `architecture/spec.md`
- [ ] This change folder archived after Tier 1 completion
