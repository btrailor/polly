# Knowledge Graph Advanced (Phase 12b) — Proposal

**Tier:** 1 (Core Intelligence)  
**Scope:** Backend + Frontend  
**Status:** Designed, not started  
**Created:** March 2026  
**Depends On:** Phase 12a (✅ ~95%), Entity Model Unification (✅), Integration Contracts (✅)  
**Blocks:** Phase 12c (Active Maintenance), Phase 12d (Library Integration)

---

## What We're Doing

Making the knowledge graph useful for retrieval and discovery — not just visualization. Three pillars:

1. **Graph-aware retrieval** — Entity-graph traversal as a third RAG strategy alongside semantic search and BM25, with authority scoring integrated into RRF fusion
2. **Quality controls** — Isolated note detection, batch merge/delete, garden maintenance digests
3. **Graph intelligence** — Community detection, centrality measures, confidence scoring on edges, path-finding API, reasoning transparency ("why this connection?")

## Why

### The Current Problem

Phase 12a built a solid knowledge graph with 650-line EntityStore (SQLite), entity extraction, Cytoscape.js visualization, and a full garden API. But the graph is **read-only decoration** — it doesn't improve query results or actively maintain knowledge quality:

- **Authority scores are computed but never used.** `recompute_authority()` calculates a 4-factor score (mentions, sources, relationships, recency) but RAG search (`UnifiedRAG`, `HybridSearcher`) never consults it. High-authority entities don't boost search results.
- **Graph structure is invisible to retrieval.** Queries use semantic search (ChromaDB) + keyword (BM25) via RRF. The entity graph with its relationships, paths, and clusters is never traversed during retrieval. A query about "Freire" won't discover notes connected 2 hops away through shared concepts.
- **No proactive quality maintenance.** Isolated notes accumulate silently. No weekly digest tells the user "you have 30 orphan notes." The garden view exists but requires manual inspection.
- **No graph algorithms.** Path-finding exists in EntityStore but isn't exposed via API. No community detection, no PageRank, no betweenness centrality. The graph can't answer "what are the central concepts in my vault?" or "show me topic clusters."
- **Edge quality is uniform.** All co-occurrence relationships get strength 0.5. No confidence scoring, no multi-factor analysis. Users can't ask "why does Polly think these are connected?"

### What We Get

- **Better query results:** Authority-boosted RRF means high-quality hub notes surface first. Graph traversal discovers related content that vector similarity misses.
- **Knowledge health:** Automatic isolation detection, weekly maintenance digests, batch operations for cleanup.
- **Graph intelligence:** Community clusters reveal topic structure. Centrality identifies hub concepts. Path-finding shows how ideas connect.
- **Reasoning transparency:** Users understand and can adjust why connections exist.

## Scope

### In Scope (3 waves)

**Wave 1: Graph-Aware Retrieval (~1 week)**

- Authority scoring as third signal in HybridSearcher RRF
- Entity-graph traversal retrieval strategy (query → extract entities → traverse 2-3 hops → return connected content)
- Graph context injection in `_gather_context()` / `_format_rag_context()`
- Path-finding API endpoint

**Wave 2: Quality Controls (~1 week)**

- Isolated note detection and flagging (0-2 connections)
- Batch merge/delete operations via garden API
- Authority recomputation scheduling (background, periodic)
- Garden maintenance digest endpoint (weekly summary: orphans, merge candidates, enrichment targets)
- Inbox state for unconnected notes

**Wave 3: Graph Intelligence & Reasoning (~1 week)**

- Community detection (label propagation — pure Python, no networkx dependency)
- PageRank / betweenness centrality augmenting authority scores
- Edge confidence scoring (multi-factor: semantic similarity, keyword overlap, temporal proximity, co-occurrence count)
- "Why this connection?" API endpoint (factor breakdown + evidence snippets)
- Frontend: path highlighting, community cluster coloring, confidence display on edges

### Out of Scope

- LLM-based entity extraction (richer relationship types — deferred to 12c)
- Augmented writing panel (real-time related content during composition — 12c)
- Smart summarization layers (weekly/monthly synthesis — 12c)
- Library integration (book entity bridging — 12d)
- 3D graph view
- GraphML/JSON export

## Reference

- Spec: [openspec/specs/knowledge-graph/spec.md](../../specs/knowledge-graph/spec.md)
- 12a implementation: [openspec/changes/knowledge-graph-navigation/](../knowledge-graph-navigation/), [openspec/changes/knowledge-graph-refinement/](../knowledge-graph-refinement/)
- Entity model: [openspec/changes/entity-model-unification/](../entity-model-unification/)
- Existing code: `core/entities/store.py` (649 lines), `core/hybrid_search.py` (508 lines), `core/rag.py` (1522 lines), `core/knowledge_graph/` (1044 lines)
- Phase 12 planning: [docs/planning/phases/other/PHASE12_KNOWLEDGE_GRAPH.md](../../../docs/planning/phases/other/PHASE12_KNOWLEDGE_GRAPH.md)
- Tier 1 doc: [docs/planning/tiers/TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md)
