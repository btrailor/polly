# Continuation Prompt: Polly Core Framework Refinement — Implementation Phase

Copy everything below the line into a new agent session.

---

## Context

I'm building **Polly**, an edge-native personal AI system (Electron + Python backend). We've completed planning for the **Core Framework Refinement** — the cross-cutting work that makes Polly unique — including an OSS tool integration research phase.

### What's been implemented so far:
- **Knowledge Writing** — `core/knowledge_writer.py`: Chat-to-KB writing with gap detection, quick save, Scribe-assisted save, per-message context menu save, incremental RAG indexing
- **Autonomy Metrics** — `core/autonomy_metrics.py`: SQLite tracking of knowledge writes + routing decisions for a progressive autonomy dashboard
- **Incremental RAG** — `core/rag.py` → `index_single_document()`: Single-file upsert into ChromaDB without full rebuild
- **Scribe Standalone Enrich** — Scribe persona exposes direct enrichment for KnowledgeWriter
- **AI Features Settings** — Frontend toggles + backend config for knowledge suggestions and autonomy dashboard
- **Full Settings API** — Endpoints for knowledge saves, AI features, autonomy dashboard metrics
- **OSS Tool Research** — 13 tools evaluated across 7 categories; findings integrated into unified plan

### What's designed and ready to implement (unified plan):

The implementation is organized into **6 Waves** — see `openspec/changes/core-framework-refinement/tasks.md` for the full plan:

**Wave 1 (Weeks 1–3) — Provider Foundation + Compression:**
- **LiteLLM Adapter** — Replace 7 individual provider files + planned Provider Registry with unified `litellm.completion()` API. MIT license. Supports all Polly's providers + OpenRouter + 100+ more.
- **LLMLingua Compression** — Add algorithmic 2x–10x compression alongside existing LLM-based compression. MIT license.

**Wave 2 (Weeks 2–5) — Memory Layer + Provider UI:**
- **Mem0 Memory Layer** — Adaptive memory for knowledge writing, patterns, and personas. Apache-2.0. Graph memory + entity extraction + multi-level memory.
- **Provider Management UI** — Settings page powered by LiteLLM adapter
- **"Polly" Mode** — Model selector dropdown for intelligent routing

**Wave 3 (Weeks 5–8) — Intelligent Routing Pipeline:**
- Query Decomposition Engine → Split Routing → Synthesis Layer

**Wave 4 (Weeks 6–10) — Knowledge Enrichment:**
- Progressive Autonomy Feedback Loop, PIL v2, RAG Optimization, SKILL ↔ Mental Model bridge

**Wave 5 (After Phase 23.5) — Advanced Features:**
- LlamaIndex Knowledge Graph (Phase 12a), CrewAI Orchestrator (Phase 24), Langfuse Observability

**Wave 6 — Backlog:**
- BookLore Library, Haystack components, A-MEM patterns, n8n integration

### Key reference files:
- `openspec/changes/core-framework-refinement/proposal.md` — What we're doing and why
- `openspec/changes/core-framework-refinement/design.md` — Detailed design of implemented + planned components (with OSS integration architecture)
- `openspec/changes/core-framework-refinement/tasks.md` — **AUTHORITATIVE unified task list** with wave structure, conflict resolutions, and timeline
- `openspec/changes/oss-tool-integration-research/design.md` — Full OSS tool evaluation matrix (13 tools, 7 categories)
- `openspec/specs/project/status.md` — Current project status
- `openspec/specs/project/roadmap.md` — Full roadmap with Core Framework Refinement section
- `openspec/config.yaml` — Project context and rules

### Existing provider code to understand:
- `core/providers/base.py` — `ProviderAdapter` ABC (7 concrete implementations in same dir)
- `core/router_v2.py` — `IntelligentRouterV2` (routing decisions — this STAYS)
- `core/router.py` — `IntelligentRouter`, `UnifiedLLM` (older router)
- `core/budget_manager.py` — Cost tracking
- `core/compression/compressor.py` — Current compression system
- `core/pattern_learning.py` — Pattern learner (~900 lines)
- `core/knowledge_writer.py` — Knowledge writing orchestrator

## Your Task

Start implementing **Wave 1** of the unified plan:

### 1. LiteLLM Provider Adapter
- Create `core/providers/litellm_adapter.py`
- Map all 7 existing provider files to LiteLLM model strings
- Implement `ProviderAdapter` interface so `IntelligentRouterV2` works unchanged
- Integrate with `BudgetManager` via cost callbacks
- Create `config/litellm_config.yaml`

### 2. LLMLingua Compression
- Create `core/compression/llmlingua_strategy.py`
- Update `core/compression/compressor.py` with strategy selection
- Add compression step in RAG pipeline (`core/rag.py`)

### Important rules:
- Follow OpenSpec workflow (see `openspec/README.md` and `openspec/config.yaml`)
- Backend before frontend
- All integrations must be **additive and optional** — existing functionality must work without new dependencies
- Config-driven: everything toggleable in `config/config.yaml`
- Update `requirements.txt` and `config/approved_packages.yaml`
- Test that existing providers still work after migration
