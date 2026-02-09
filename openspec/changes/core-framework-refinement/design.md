# Core Framework Refinement — Design

**Last Updated:** February 2026  
**Integration:** OSS tool integration findings merged from [oss-tool-integration-research/](../oss-tool-integration-research/)

---

## Implemented Components

### Knowledge Writing System (`core/knowledge_writer.py`)

Central orchestrator for all chat-to-KB writes. Converges all write paths through a single `_save_note()` method.

**Classes:**
- `KnowledgeGap` — Detected gap between local RAG and cloud response
- `NoteCreateResult` — Result of a note creation operation
- `KnowledgeWriter` — Main orchestrator (singleton via `init_knowledge_writer()`)

**Write Paths:**
1. **Gap detection** (`detect_knowledge_gap()`) — Compares RAG results vs cloud response using heuristic concept extraction. No LLM call. Returns `KnowledgeGap` when gap score exceeds configurable threshold.
2. **Quick save** (`quick_save()`) — Structured markdown with auto-generated frontmatter, no LLM call. Auto-detects domain via keyword matching or `DomainEngine`.
3. **Scribe-assisted save** (`scribe_save()`) — Routes through `ScribePersona.enrich_standalone()` for wiki-linking and template-based formatting. Falls back to quick save on failure.
4. **Per-message save** (`save_message()`) — Context menu on assistant messages → quick or scribe mode.

**Common Infrastructure (`_save_note()`):**
1. Determine active notes source (native or Obsidian) via `NotesSourceManager`
2. Normalize filename, build path under domain folder
3. Deduplicate via `notes_dedup`
4. Write file
5. Incremental RAG index via `rag.index_single_document()`
6. Record metric via `AutonomyMetrics`

**Config (`config.yaml` → `ai_features`):**
```yaml
ai_features:
  knowledge_suggestions:
    enabled: true
    style: "inline"         # "subtle" | "inline" | "ask_first"
    min_gap_score: 0.5
  autonomy_dashboard:
    enabled: true
    show_in_status_bar: true
```

### Autonomy Metrics (`core/autonomy_metrics.py`)

SQLite-based tracking (shares `~/.polly/usage.db` with BudgetManager).

**Tables:**
- `knowledge_writes` — Every note saved from chat (title, domain, source_type, cloud_provider, gap_score, estimated_future_savings)
- `routing_decisions` — Every routing decision (route_type: local/cloud/split, provider, rag_coverage, tokens_used, cost, local_pct)

**Queries:**
- `get_snapshot(days)` → `AutonomySnapshot` (writes count, writes by source, tokens saved, local/cloud routing %, total queries)
- `get_recent_writes(limit)` → List of recent knowledge writes
- `get_routing_trend(days, bucket_days)` → Weekly buckets of local vs cloud %

### Incremental RAG Indexing (`core/rag.py` → `index_single_document()`)

Single-file upsert into ChromaDB without full rebuild. Used by KnowledgeWriter after saving a new note.

### Scribe Standalone Enrich (`core/personas/implementations/scribe.py`)

`enrich_standalone(content, title, domain, conversation_history)` — Direct enrichment without going through full Capture → Organize pipeline. Returns enriched content + metadata for preview modal.

### Settings API (`interfaces/settings_api.py`)

New endpoints:
- `GET/PUT /api/settings/ai-features` — AI feature toggles
- `POST /api/settings/knowledge/save-quick` — Quick save
- `POST /api/settings/knowledge/save-scribe` — Scribe save
- `POST /api/settings/knowledge/save-message` — Per-message save
- `GET /api/settings/autonomy/snapshot` — Dashboard metrics
- `GET /api/settings/autonomy/recent-writes` — Recent writes
- `GET /api/settings/autonomy/routing-trend` — Routing trend

### Frontend

- **SaveMessageForm** (`electron-app/src/renderer/components/save-message-form.js`) — Inline form for saving messages to KB
- **AI Features settings** — Toggle section in Settings with knowledge suggestion controls
- **Context menu** — Right-click on assistant messages → "Save to KB"
- **Suggestion rendering** — `renderKnowledgeSuggestion()` for AI-suggested writes

---

## Designed — With OSS Tool Integration

### Provider Layer: LiteLLM Adapter (replaces custom Provider Registry)

**Original plan:** Build custom `core/provider_registry.py` with `ProviderState` dataclass, `ProviderRegistry` class, per-provider toggle, health tracking, and custom `openrouter_provider.py`.

**New plan:** Use **LiteLLM** (MIT, ~18k stars) as unified provider layer. LiteLLM already provides everything the custom Provider Registry would have built:

| Planned Custom Component | LiteLLM Equivalent |
|--------------------------|-------------------|
| `ProviderRegistry.get_enabled_providers()` | `litellm.model_list` / `litellm.get_model_info()` |
| `ProviderState.health_status` | LiteLLM health checks, automatic retry logic |
| `ProviderState.available_models` | LiteLLM model discovery per provider |
| `toggle_provider()` | Config-driven enable/disable in `litellm_config.yaml` |
| `openrouter_provider.py` | `"openrouter/model-name"` prefix (native support) |
| Fallback chains | `litellm.completion(fallbacks=[...])` |
| Budget management | `litellm.BudgetManager` + Polly's `BudgetManager` adapter |
| Per-provider cost tracking | LiteLLM cost callbacks |

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                   Polly Backend                         │
│                                                         │
│  User Query                                             │
│     ↓                                                   │
│  IntelligentRouterV2 (UNCHANGED — routing decisions)    │
│     ↓  decides: provider + model + tier                 │
│  LiteLLM Adapter (NEW — replaces individual providers)  │
│     ↓  litellm.completion("anthropic/claude-3.5-sonnet")│
│     ↓  litellm.completion("ollama/llama3")              │
│     ↓  litellm.completion("openrouter/meta-llama/...")   │
│  BudgetManager ← cost callback from LiteLLM            │
│  AutonomyMetrics ← routing decision + cost logged       │
└─────────────────────────────────────────────────────────┘
```

**Key decision:** `IntelligentRouterV2` stays as-is. It handles Polly's unique routing logic (complexity analysis, confidence tiers, RAG coverage assessment). LiteLLM replaces only the *execution* layer — the 7 individual `*_provider.py` files and the planned `openrouter_provider.py`.

**Existing code preserved:**
- `core/router_v2.py` → `IntelligentRouterV2` (routing decisions)
- `core/router.py` → `IntelligentRouter`, `UnifiedLLM` (older router, kept for compatibility)
- `core/budget_manager.py` → cost tracking
- `core/providers/base.py` → `ProviderAdapter` ABC (interface contract, now implemented by LiteLLM adapter)

---

### Compression: LLMLingua Strategy (enhances existing compressor) — IN PROGRESS

**Original plan:** Extend PIL format for patterns, knowledge summaries, routing decisions.

**New plan:** Add **LLMLingua** (MIT, Microsoft Research) as an algorithmic compression strategy *alongside* the existing LLM-based compression. PIL format expansion remains custom work.

**Architecture:**

```
core/compression/
├── __init__.py
├── compressor.py          # Strategy selector (existing, updated)
├── manager.py             # Compression manager (existing)
└── llmlingua_strategy.py  # NEW: LLMLingua-2 compression

Strategy selection:
  "auto" (default):
    ├── RAG context compression → LLMLingua (fast, no LLM call, 2x–10x reduction)
    └── Conversation compression → LLM summary (better narrative quality)
  "llmlingua": Always use LLMLingua
  "llm_summary": Always use existing LLM-based compression
```

**Integration point in RAG pipeline:**

```
Query → RAG Search → Retrieved Chunks ──→ [LLMLingua Compress] ──→ LLM Call
                                              ↑ optional step
                                              2x–10x token reduction
```

**Implementation Details:**

1. **LLMLingua Strategy Module** (`core/compression/llmlingua_strategy.py`):
   - `LLMLinguaCompressor` class with lazy model loading
   - `compress(text, target_ratio)` method for prompt/context compression
   - Configurable compression ratio (0.1-1.0, default 0.5 = 2x compression)
   - Device selection (CPU/CUDA)
   - Token counting for metrics

2. **Compression Manager Updates** (`core/compression/manager.py`):
   - Add `compress_with_strategy(text, strategy, ratio)` method
   - Strategy enum: `auto`, `llmlingua`, `llm_summary`
   - Auto mode: detect context type and route to appropriate compressor

3. **RAG Integration** (`core/rag.py`):
   - Optional compression step in `search()` method after retrieval
   - Config-driven: `compression.rag_context.enabled`
   - Compress chunk content before formatting
   - Track token savings in search results metadata

4. **Configuration Schema** (`config/config.yaml`):
   ```yaml
   compression:
     strategy: "auto"  # "auto" | "llmlingua" | "llm_summary"
     
     rag_context:
       enabled: true
       ratio: 0.5  # 2x compression (1.0 = no compression, 0.1 = 10x)
     
     conversation:
       strategy: "llm_summary"  # Force LLM for conversation compression
     
     llmlingua:
       model: "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
       device: "cpu"  # or "cuda" if available
   ```

5. **Token Tracking**:
   - Before/after token counts in search results
   - Compression ratio metrics
   - Cost savings estimation

---

### Memory: Mem0 Adaptive Memory Layer (enhances knowledge + patterns)

**Original plan:** Build Pattern → Routing integration, PIL expansion (memory aspects), SKILL ↔ Mental Model bridge — all from scratch.

**New plan:** Use **Mem0** (Apache-2.0, ~47k stars) as adaptive memory layer. Provides graph-based entity relationships, multi-level memory, and reranker-enhanced search that directly support multiple planned components.

**Architecture:**

```
core/memory/
├── __init__.py
└── mem0_adapter.py         # NEW: Wraps Mem0 Python SDK

Mem0 Memory ←→ KnowledgeWriter  (knowledge persistence + fact extraction)
Mem0 Memory ←→ PatternLearner   (pattern storage + graph queries)
Mem0 Memory ←→ PersonaManager   (per-persona context via agent_id)
Mem0 Memory ←→ MentalModels     (entity relationships via graph memory)
```

**How Mem0 enhances each component:**

| Component | Current | With Mem0 |
|-----------|---------|-----------|
| **KnowledgeWriter** | Saves markdown files + ChromaDB index | Also persists to Mem0 with entity extraction + relationship tracking |
| **PatternLearner** | `patterns.json` flat file, 4 types | Mem0 graph memory: entity nodes + relationship edges, semantic search |
| **PersonaManager** | Session state only | Per-persona memories: Architect remembers planning context, Scribe remembers writing style, Professor remembers learning progress |
| **MentalModels** | `mental_models.json` | Graph relationships between models, skills, and patterns via Mem0 entities |
| **RAG** | ChromaDB + BM25 hybrid search | Additional Mem0 search with reranker for memory-enhanced context |

**Mem0 is additive, not replacing:**
- `patterns.json` continues to work (Mem0 is optional, config-driven)
- `core/rag.py` keeps existing ChromaDB/BM25 pipeline
- Mem0 provides a parallel memory layer that enhances results when enabled

---

### Future: LlamaIndex Knowledge Graph (Phase 12a)

LlamaIndex's KG index provides entity extraction, triple storage (subject-predicate-object), and graph querying — exactly what Phase 12a (Knowledge Graph Basic) needs.

LlamaIndex also provides `SubQuestionQueryEngine` which decomposes complex queries into sub-queries routed to different indices — directly implementing the planned Query Decomposition engine.

**Architecture (Phase 12a):**

```
core/knowledge_graph/
├── llamaindex_kg.py           # KG index, entity extraction, graph queries
└── query_decomposition_v2.py  # SubQuestionQueryEngine wrapper

Query → Decomposition → Sub-queries → [KG Index, Vector Index, Keyword Index]
                                            ↓           ↓              ↓
                                       KG results  ChromaDB results  BM25 results
                                            ↓           ↓              ↓
                                       Synthesis → Merged Response with Citations
```

---

### Future: CrewAI Orchestrator (Phase 24)

CrewAI's role-based agent framework maps directly to Polly's persona system:

| Polly Persona | CrewAI Agent Role |
|--------------|-------------------|
| Architect | Planning agent — goal: structured plans, tools: code analysis, project planning |
| Scribe | Writing agent — goal: research and writing, tools: wiki-linking, template-guide |
| Professor | Teaching agent — goal: education, tools: curriculum generation, assessment |

This is Phase 24 work, blocked by Phase 23.5 security hardening.

---

## Impact Summary

- **Backend:** Waves 1–4 add 3 new adapters (`litellm_adapter.py`, `llmlingua_strategy.py`, `mem0_adapter.py`) + refactor existing provider files + new modules for decomposition, split routing, synthesis. All additive — existing code preserved.
- **Frontend:** "Polly" mode dropdown, provider management settings, compression strategy selector, memory provider toggle. All in Settings UI.
- **Pending backend (Waves 5+):** `core/knowledge_graph/`, `core/orchestrator/`, `core/observability/`
- **Config:** New `integrations:` section in `config.yaml`, new `config/litellm_config.yaml`
- **Dependencies:** `litellm`, `llmlingua`, `mem0ai` (Tier 1); `llama-index`, `crewai`, `langfuse` (Tier 2)

---

## Reference

- OSS tool research: [oss-tool-integration-research/](../oss-tool-integration-research/) — Full evaluation of 13 tools across 7 categories
- Existing specs: `openspec/specs/rag/spec.md`, `openspec/specs/patterns/spec.md`, `openspec/specs/personas/spec.md`
- Existing code: `core/router_v2.py`, `core/providers/`, `core/compression/`, `core/knowledge_writer.py`
