# RAG & Routing (OpenSpec)

Source of truth for retrieval-augmented generation and hybrid local/cloud routing. Full architecture: [docs/RAG_ROUTING_ARCHITECTURE.md](../../../docs/RAG_ROUTING_ARCHITECTURE.md).

## RAG

- **Hybrid search:** Semantic (ChromaDB, nomic-embed-text) + keyword (BM25). Reciprocal Rank Fusion (RRF); title boosting.
- **Use:** Query expansion (pattern learner, domain detection) → RAG search → optional compression → score/context → routing decision and LLM call.
- **Config:** Thresholds for "high quality" context; top-k and context size. Metadata tracking, source attribution.
- **Compression (NEW - Wave 1):** Optional LLMLingua compression of RAG context chunks (2x-10x token reduction). Config: `compression.rag_context.enabled`, `compression.rag_context.ratio`.

## Routing

- **Router v2 (Phase 11):** Three-tier confidence — Fast / Balanced / Thorough. Task complexity (1–10), budget-aware model selection, fallback chains.
- **Hybrid local/cloud:** When RAG context is strong, route to local Ollama; otherwise cloud. Saves ~40–70% on API cost. Settings UI: threshold sliders, presets (Aggressive Local, Balanced, Conservative Cloud).

## Incremental Indexing (Core Framework Refinement)

- **`index_single_document(filepath, source_type)`** — Upserts a single file into ChromaDB without full rebuild. Used by `KnowledgeWriter` after saving a new note. Chunks via `MarkdownChunker`, embeds via Ollama, upserts to collection, updates BM25 index if hybrid search is enabled.
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Providers

- Anthropic, OpenAI, GitHub Models, Grok, Perplexity, Gemini, Mistral. Budget manager: daily/monthly limits, cost tracking.
- **Planned:** Provider Registry (per-provider enable/disable toggle, health tracking), OpenRouter gateway, "Polly" intelligent routing mode.

## Autonomy Metrics (Core Framework Refinement)

- **`core/autonomy_metrics.py`** — SQLite tracking (shares `~/.polly/usage.db` with BudgetManager). Tables: `knowledge_writes`, `routing_decisions`. Queries: `get_snapshot()`, `get_recent_writes()`, `get_routing_trend()`.
- **Dashboard API:** `GET /api/settings/autonomy/snapshot`, `/recent-writes`, `/routing-trend`
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Reference

- [docs/RAG_ROUTING_ARCHITECTURE.md](../../../docs/RAG_ROUTING_ARCHITECTURE.md) — Diagrams, components, config, troubleshooting
- [docs/README_RAG_DOCS.md](../../../docs/README_RAG_DOCS.md), [RAG_TROUBLESHOOTING_QUICK_REFERENCE.md](../../../docs/RAG_TROUBLESHOOTING_QUICK_REFERENCE.md)
