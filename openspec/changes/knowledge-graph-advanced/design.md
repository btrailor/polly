# Knowledge Graph Advanced (Phase 12b) — Design

**Last Updated:** March 2026

---

## Architecture Overview

Phase 12b adds three layers on top of the 12a foundation:

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (Electron)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Graph Page (existing Cytoscape.js)                    │  │
│  │  + Community cluster coloring                          │  │
│  │  + Path highlighting between nodes                     │  │
│  │  + Edge confidence tooltip / "Why?" modal              │  │
│  │  + Isolation badges in browse list                     │  │
│  │  + Garden digest panel                                 │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ↓ HTTP
┌──────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│                                                              │
│  ┌─────────────────────────────────────────┐                 │
│  │  NEW: Graph Intelligence Layer          │                 │
│  │  core/entities/intelligence.py          │                 │
│  │  • CommunityDetector (label propagation)│                 │
│  │  • CentralityComputer (PageRank, betw.) │                 │
│  │  • EdgeConfidenceScorer (multi-factor)  │                 │
│  │  • IsolationDetector                    │                 │
│  └──────────────┬──────────────────────────┘                 │
│                 │                                             │
│  ┌──────────────┴──────────────────────────┐                 │
│  │  NEW: Graph Retriever                   │                 │
│  │  core/entities/retriever.py             │                 │
│  │  • GraphRetriever (ContextContributor)  │                 │
│  │  • Entity extraction from query         │                 │
│  │  • Multi-hop traversal                  │                 │
│  │  • Authority-weighted result scoring    │                 │
│  └──────────────┬──────────────────────────┘                 │
│                 │                                             │
│  ┌──────────────┴──────────────────────────┐                 │
│  │  MODIFIED: Hybrid Search                │                 │
│  │  core/hybrid_search.py                  │                 │
│  │  + Authority rank as 3rd RRF signal     │                 │
│  │  + Entity match boost                   │                 │
│  └──────────────┬──────────────────────────┘                 │
│                 │                                             │
│  ┌──────────────┴──────────────────────────┐                 │
│  │  EXISTING: EntityStore (SQLite)         │                 │
│  │  core/entities/store.py                 │                 │
│  │  + get_isolated_entities() (new)        │                 │
│  │  + get_community_graph() (new)          │                 │
│  │  + get_edge_evidence() (new)            │                 │
│  └─────────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Wave 1: Graph-Aware Retrieval

### 1A. Authority Scoring in RRF

**Where:** `core/hybrid_search.py` — `HybridSearcher.reciprocal_rank_fusion()`

The existing RRF combines two signals:

```
score(d) = 1/(k + rank_semantic) + 1/(k + rank_keyword)
```

Add authority as a weighted third signal:

```
score(d) = 1/(k + rank_semantic) + 1/(k + rank_keyword) + α * authority_score(d)
```

Where `authority_score(d)` is looked up from `EntityStore` by matching entities in the document's metadata against the entity graph.

**Implementation:**

- `HybridSearcher` gains an optional `entity_store: EntityStore` parameter
- New method `_compute_authority_ranks(doc_ids: list[str]) -> dict[str, float]` — batch-queries EntityStore for entities mentioned in each document, returns max authority score per doc
- `reciprocal_rank_fusion()` adds authority rank to the RRF sum when entity_store is available
- Config weight `rag.authority_weight` (default: `0.3`) controls `α`
- Backward compatible: when no entity_store, behavior unchanged

### 1B. Graph Traversal Retriever

**New file:** `core/entities/retriever.py`

A `ContextContributor` (per integration-contracts protocol) that retrieves context through graph traversal rather than vector similarity:

```python
class GraphRetriever:
    """ContextContributor that retrieves content via entity graph traversal."""

    priority = 45  # Between memory (50) and RAG (30)

    def contribute(self, query: str, token_budget: int = 0) -> list[ContextItem]:
        # 1. Extract entities from query (reuse EntityExtractor.extract_entities_only())
        # 2. Match against EntityStore (fuzzy name matching)
        # 3. For each matched entity, traverse 2-3 hops via get_related()
        # 4. Collect entity_mentions → source documents
        # 5. Score by: hop distance (closer = better), entity authority, relationship strength
        # 6. Deduplicate against semantic search results
        # 7. Return as ContextItems within token budget
```

**Key design decisions:**

- Max hops configurable: `rag.graph_traversal.max_hops` (default: 2)
- Minimum relationship strength threshold: `rag.graph_traversal.min_strength` (default: 0.3)
- Cross-domain traversal enabled by default (core value of graph-based discovery)
- Results tagged with `source_type: "graph_traversal"` for transparency

### 1C. Path-Finding API

**New endpoint:** `GET /polly/graph/path`

```
GET /polly/graph/path?from={entity_id}&to={entity_id}&max_hops=4
→ { path: [entity1, rel, entity2, rel, entity3], length: 2, strength: 0.75 }
```

Exposes existing `EntityStore.find_path()` — no new algorithm needed, just an API surface.

### 1D. Wiring into polly.py

- Register `GraphRetriever` in `_init_context_contributors()` (after entity store init)
- Pass `entity_store` to `HybridSearcher` constructor in `_init_rag()`
- The `_gather_context()` dual-path already iterates `ContextContributor` list — GraphRetriever slots in automatically

---

## Wave 2: Quality Controls

### 2A. Isolation Detection

**New method on EntityStore:**

```python
def get_isolated_entities(self, max_connections: int = 2) -> list[dict]:
    """Return entities with <= max_connections relationships."""
```

**New method on EntityStore:**

```python
def get_isolated_notes(self, max_entity_connections: int = 2) -> list[dict]:
    """Return notes whose entities are all isolated (no well-connected entities)."""
```

These power the inbox/flagging system. Notes with only isolated entities are candidates for review.

### 2B. Garden Maintenance Digest

**New endpoint:** `GET /polly/graph/garden/digest`

Returns a structured weekly summary:

```json
{
  "period": "2026-02-22 to 2026-03-01",
  "isolated_notes": [
    { "path": "...", "entity_count": 1, "connection_count": 0 }
  ],
  "merge_candidates": [
    { "entities": ["React", "ReactJS"], "similarity": 0.95 }
  ],
  "enrichment_targets": [
    { "path": "...", "reason": "mentioned 5 entities but only 1 extracted" }
  ],
  "connection_suggestions": [
    { "entity": "Freire", "unlinked_in": ["note1.md", "note2.md"] }
  ],
  "stats": {
    "total_entities": 450,
    "total_relationships": 1200,
    "avg_authority": 0.35
  }
}
```

Combines data from existing garden endpoints (`/garden/stats`, `/garden/suggestions`) into one digest payload. Frontend renders as a card/panel in the garden view.

### 2C. Batch Operations Enhancement

Extend existing `/polly/graph/garden/merge` and `/polly/graph/garden/prune` with batch mode:

```
POST /polly/graph/garden/batch
{
  "operations": [
    {"type": "merge", "entities": ["id1", "id2"], "keep": "id1"},
    {"type": "delete", "entities": ["id3"]},
    {"type": "connect", "source": "id4", "target": "id5", "type": "RELATED_TO"}
  ]
}
```

Executes within a single SQLite transaction for atomicity.

### 2D. Authority Recomputation Scheduling

Add a background task that recomputes authority scores periodically:

- On server startup (if last computation > 24h ago)
- After batch operations (merge, delete, prune)
- Configurable interval in `config.yaml`: `knowledge_graph.authority_recompute_interval_hours` (default: 24)

Store last recomputation timestamp in `~/.polly/entities.db` metadata table.

---

## Wave 3: Graph Intelligence & Reasoning

### 3A. Community Detection

**New file:** `core/entities/intelligence.py`

Label propagation algorithm (pure Python, no networkx):

```python
class CommunityDetector:
    def detect_communities(self, entity_store: EntityStore) -> dict[str, int]:
        """
        Label propagation: each node starts with unique label,
        iteratively adopts most common neighbor label.
        Returns {entity_id: community_id}.
        """
```

Results stored in a new `community_id` column on the `entities` table. Recomputed alongside authority scores.

**API:** `GET /polly/graph/communities` → list of communities with member entities, domain distribution, top concepts.

### 3B. Centrality Measures

In `core/entities/intelligence.py`:

```python
class CentralityComputer:
    def pagerank(self, entity_store: EntityStore, damping: float = 0.85, iterations: int = 100) -> dict[str, float]:
        """Power iteration PageRank over the entity graph."""

    def betweenness_centrality(self, entity_store: EntityStore, sample_size: int = 100) -> dict[str, float]:
        """Approximate betweenness centrality via random sampling."""
```

PageRank replaces/augments the log-ratio authority formula. Betweenness identifies bridge entities connecting different topic clusters.

Results stored as additional columns on `entities`: `pagerank_score`, `betweenness_score`. The composite authority formula becomes:

```
authority = 0.4 * pagerank + 0.3 * log(mentions) + 0.2 * betweenness + 0.1 * recency
```

### 3C. Edge Confidence Scoring

**New method on EntityStore or intelligence.py:**

```python
class EdgeConfidenceScorer:
    def score_edge(self, source_id: str, target_id: str) -> EdgeConfidence:
        """
        Multi-factor confidence scoring:
        - semantic_similarity: cosine similarity of entity descriptions/contexts (from ChromaDB if available)
        - co_occurrence_count: number of documents both entities appear in
        - temporal_proximity: how close in time were they first/last co-mentioned
        - structural_proximity: shortest path length in graph (inverse)
        """
```

Returns `EdgeConfidence` dataclass with per-factor scores and weighted composite.

### 3D. "Why This Connection?" API

**New endpoint:** `GET /polly/graph/edge/explain?source={id}&target={id}`

```json
{
  "confidence": 0.78,
  "factors": {
    "co_occurrence": { "score": 0.9, "detail": "Co-occur in 12 notes" },
    "semantic_similarity": {
      "score": 0.72,
      "detail": "Descriptions are 72% similar"
    },
    "temporal_proximity": {
      "score": 0.65,
      "detail": "First mentioned 3 days apart"
    },
    "structural_proximity": { "score": 0.85, "detail": "1 hop apart in graph" }
  },
  "evidence": [
    {
      "source": "notes/philosophy.md",
      "snippet": "...Freire's concept of praxis connects to..."
    }
  ]
}
```

### 3E. Frontend Enhancements

- **Community cluster coloring:** Each community gets a color; nodes tinted by community membership. Toggle between domain coloring and community coloring.
- **Path highlighting:** Click two nodes → highlight shortest path with animated edges.
- **Confidence on edges:** Edge thickness already exists (strength); add tooltip showing confidence breakdown. Click edge → "Why?" modal with factor scores.
- **Isolation badges:** In browse list, flag notes with ⚠️ icon when isolated (0-2 connections).

---

## Configuration

New `config.yaml` entries:

```yaml
knowledge_graph:
  # Wave 1: Retrieval
  authority_weight: 0.3 # Weight of authority signal in RRF (0.0 to disable)
  graph_traversal:
    enabled: true
    max_hops: 2
    min_strength: 0.3

  # Wave 2: Quality
  authority_recompute_interval_hours: 24
  isolation_threshold: 2 # Notes with <= N entity connections flagged as isolated

  # Wave 3: Intelligence
  community_detection:
    enabled: true
    algorithm: label_propagation # Only option for now (pure Python)
    min_community_size: 3
  centrality:
    enabled: true
    pagerank_damping: 0.85
    pagerank_iterations: 100
    betweenness_sample_size: 100
  edge_confidence:
    weights:
      co_occurrence: 0.35
      semantic_similarity: 0.25
      temporal_proximity: 0.15
      structural_proximity: 0.25
```

---

## New Files

| File                               | Purpose                                                                        |
| ---------------------------------- | ------------------------------------------------------------------------------ |
| `core/entities/retriever.py`       | GraphRetriever — ContextContributor for graph-based retrieval                  |
| `core/entities/intelligence.py`    | CommunityDetector, CentralityComputer, EdgeConfidenceScorer, IsolationDetector |
| `tests/test_graph_retriever.py`    | Tests for GraphRetriever                                                       |
| `tests/test_graph_intelligence.py` | Tests for community detection, centrality, confidence scoring                  |

## Modified Files

| File                               | Changes                                                                                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `core/hybrid_search.py`            | Authority rank as 3rd RRF signal                                                                                                      |
| `core/entities/store.py`           | `get_isolated_entities()`, `get_isolated_notes()`, `get_edge_evidence()`, `community_id`/`pagerank_score`/`betweenness_score` columns |
| `core/polly.py`                    | Register GraphRetriever, pass entity_store to HybridSearcher                                                                          |
| `interfaces/server.py`             | New endpoints: `/graph/path`, `/graph/garden/digest`, `/graph/garden/batch`, `/graph/communities`, `/graph/edge/explain`              |
| `config.yaml`                      | `knowledge_graph` section                                                                                                             |
| `electron-app/src/renderer/app.js` | Community coloring, path highlighting, confidence tooltips, isolation badges                                                          |

## Migration

- New columns (`community_id`, `pagerank_score`, `betweenness_score`) added via `ALTER TABLE` with defaults — no data migration needed
- First authority recomputation with new formula runs at startup after upgrade
- All new features guarded by config flags — can be disabled individually
