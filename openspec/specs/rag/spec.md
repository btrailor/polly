# RAG & Routing (OpenSpec)

Source of truth for retrieval-augmented generation and hybrid local/cloud routing. Full architecture: [docs/RAG_ROUTING_ARCHITECTURE.md](../../../docs/RAG_ROUTING_ARCHITECTURE.md).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Hybrid search (ChromaDB + BM25) | ✅ Implemented | `core/rag.py` |
| RAG context compression (LLMLingua) | ✅ Implemented | `core/compression/llmlingua_strategy.py` |
| Pattern-aware retrieval (chunk boosting) | ✅ Implemented | PatternEngine + RAG integration |
| Incremental indexing (index_single_document) | ✅ Implemented | core-framework-refinement |
| Multi-collection unified retrieval | 📐 Designed | Spec-only; library collection planned |
| Entity-graph retrieval | 📐 Partial | Entity context in _gather_context; KG retrieval planned |
| Authority scoring in RRF | 💭 Vision | knowledge-graph spec |
| DRM node routing | 💭 Vision | drm spec |
| Agent swarm context | 💭 Vision | agent-swarms spec |

## RAG

- **Hybrid search:** Semantic (ChromaDB, nomic-embed-text) + keyword (BM25). Reciprocal Rank Fusion (RRF); title boosting.
- **Use:** Query expansion (pattern learner, domain detection) → RAG search → optional compression → score/context → routing decision and LLM call.
- **Pattern-aware retrieval (integration-contracts):** Pattern engine supplies query→chunk and domain→collection patterns. Chunk boosting and collection weighting use learned patterns; router v2 can use ROUTING_OUTCOME patterns to prefer models that performed well for similar tasks.
- **Config:** Thresholds for "high quality" context; top-k and context size. Metadata tracking, source attribution.
- **Compression (NEW - Wave 1):** Optional LLMLingua compression of RAG context chunks (2x-10x token reduction). Config: `compression.rag_context.enabled`, `compression.rag_context.ratio`.

### Planned: Multi-Collection Unified Retrieval
ChromaDB organized into separate collections (`notes`, `code`, `library`) with configurable source-type weighting. Smart routing determines which collections to search per query. Library results weighted below personal notes by default (0.3) to prevent drowning user-generated content. See [library spec](../library/spec.md).

### Planned: Entity Graph Retrieval
Third retrieval strategy alongside semantic and keyword. Entity-graph traversal enables precise queries: "Find all discussions where X and Y discussed Z" → graph intersection query. Connection depth limits (2–3 hops). Spans all source types — notes, books, captures, code. See [knowledge-graph spec](../knowledge-graph/spec.md).

### Planned: Authority Scoring in RRF
Authority score (from knowledge graph connection metrics) added as a weight in Reciprocal Rank Fusion. High-authority notes boosted in search results. High inbound connections = authoritative hub → retrieval priority. Book content authority derived from user engagement (annotations, note references).

## Routing

- **Router v2 (Phase 11):** Three-tier confidence — Fast / Balanced / Thorough. Task complexity (1–10), budget-aware model selection, fallback chains.
- **Hybrid local/cloud:** When RAG context is strong, route to local Ollama; otherwise cloud. Saves ~40–70% on API cost. Settings UI: threshold sliders, presets (Aggressive Local, Balanced, Conservative Cloud).

### Planned: DRM Node Routing
DRM adds a node-routing tier above existing model/provider routing. Before selecting a model, the system selects which node should handle the task. Query → DRM Router (which node?) → Node Router (which model?). See [drm spec](../drm/spec.md).

### Planned: Agent Swarm Context
When an Agent Swarm is active, RAG behavior adapts:
- **Swarm-scoped retrieval:** Searches filtered by the active workflow's domain context and agent needs.
- **Cross-agent context sharing:** If Agent A retrieved relevant chunks, the Nexus passes them to Agent B instead of re-querying.
- **Agent memory:** Shared workflow context (what each agent produced, what decisions were made) available to subsequent agents in the pipeline.
- **Knowledge graph traversal:** Agents can request entity-graph queries scoped to their capability needs.
- See [agent-swarms spec](../agent-swarms/spec.md).

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
- Knowledge graph: [knowledge-graph spec](../knowledge-graph/spec.md)
- DRM: [drm spec](../drm/spec.md)
