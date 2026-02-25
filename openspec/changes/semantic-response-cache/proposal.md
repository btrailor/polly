# Proposal: System-Wide Semantic Response Cache

## What
Add a semantic response cache to Polly that intercepts queries before they hit the LLM pipeline, returns cached responses when a semantically similar query has been answered before, and tracks token savings as part of Polly's progressive autonomy metrics.

This is **Phase 0** of a four-phase Copilot integration and token conservation plan.

## Why
**Current state:** Every query — even repeated or near-identical ones — flows through the full pipeline: domain detection, RAG search, retrieval classification, context gathering, system prompt building, conversation assembly, routing, and LLM completion. There is no deduplication of semantically equivalent queries.

- LiteLLM's built-in cache is configured but **disabled** (`cache_enabled: false` in `litellm_config.yaml`)
- No semantic caching exists anywhere in the system
- Users frequently ask similar questions (e.g., "what's the weather" → "how's the weather today")
- Cloud LLM calls are the single largest cost driver

**Problem:**
1. **Wasted tokens:** Semantically identical queries burn fresh tokens every time
2. **Unnecessary latency:** Full pipeline (~2-5s for cloud calls) even when an identical answer exists
3. **No visibility:** No tracking of how many queries could have been served from cache
4. **No foundation:** Future phases (context distillation, Copilot FIM, Programmer persona) will amplify token usage without a conservation layer

**Solution:** A ChromaDB-backed semantic cache that:
- Embeds queries using Polly's existing `rag.embed_text()` (Ollama `nomic-embed-text`)
- Matches against previous queries using cosine similarity
- Filters by domain, persona, and mode metadata for precision
- Stores full responses in SQLite (`usage.db`) to avoid bloating ChromaDB
- Integrates with AutonomyMetrics for token savings tracking

**Benefits:**
1. **Immediate cost reduction:** Cache hits skip the entire LLM pipeline (zero tokens consumed)
2. **Sub-100ms responses:** Cache hits return in <100ms vs 2-5s for cloud calls
3. **Progressive autonomy signal:** Cache hit rate becomes a measurable autonomy metric
4. **Foundation for Phases 1-3:** Establishes the caching infrastructure that context distillation and Copilot integration will build on
5. **Shared infrastructure:** Uses existing ChromaDB instance and embedding pipeline (no new dependencies)

## Scope

### Backend (Python)
- **New file:** `core/semantic_cache.py` (~250 lines) — SemanticCache class with singleton pattern
- **Modified:** `core/polly.py` — Cache check insertion (~L1515), cache store (~L2357), init method
- **Modified:** `core/config.py` — Add `semantic_cache` to DEFAULT_CONFIG
- **Modified:** `config.yaml` — Add `semantic_cache:` configuration section
- **Modified:** `core/autonomy_metrics.py` — Extend AutonomySnapshot with cache stats
- **Modified:** `core/knowledge_writer.py` — Add cache invalidation on knowledge writes
- **Modified:** `core/rag.py` — Add cache invalidation on reindex
- **Modified:** `interfaces/server.py` — Add `GET /polly/cache/stats` endpoint
- **Modified:** `interfaces/settings_api.py` — Add cache settings GET/PUT endpoints

### Frontend (Electron)
- **Modified:** `electron-app/src/renderer/index.html` — Cache toggle, threshold slider, clear button, stats in AI Features section
- **Modified:** `electron-app/src/renderer/app.js` — Load/save/setup functions for cache settings

### Storage
- **ChromaDB collection:** `semantic_cache` in shared `~/.polly/chroma_db` (alongside notes, codebase, documents, patterns)
- **SQLite table:** `cached_responses` in existing `~/.polly/usage.db` (alongside routing_decisions, knowledge_writes)

## Four-Phase Roadmap Context

This proposal is Phase 0 of a planned four-phase Copilot integration and token conservation strategy:

| Phase | Name | Purpose | Status |
|-------|------|---------|--------|
| **0** | **Semantic Response Cache** | **System-wide query dedup + token savings tracking** | **This proposal** |
| 1 | Context Distillation Layer | Local Ollama compresses code context before remote calls | Planned |
| 2 | GitHub Copilot Completions API | Native FIM (fill-in-the-middle) for inline code completion | Planned |
| 3 | Programmer Persona + Code Routing | Modes: complete/explain/refactor/generate/debug/review | Planned |

Each phase is independently valuable and incrementally deployable. Phase 0 provides the caching foundation that all subsequent phases benefit from.

## Non-Goals
- Caching streaming responses (only completed responses are cached)
- Caching conversation-dependent queries (multi-turn context makes cache hits unreliable)
- Replacing LiteLLM's built-in cache (this operates at a higher level — full Polly responses, not raw LLM calls)
- Caching local Ollama responses (negligible cost; only cloud-routed responses are cached)
- Implementing Phases 1-3 (those are future proposals)
