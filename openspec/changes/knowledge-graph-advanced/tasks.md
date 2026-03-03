# Knowledge Graph Advanced (Phase 12b) — Tasks

**Last Updated:** March 2026  
**Priority:** P1 — Tier 1 completion  
**Estimated Effort:** 2.5–3 weeks (3 waves)

---

## Task Overview

| #   | Task                                                                            | Wave | Est.  | Status | Depends    |
| --- | ------------------------------------------------------------------------------- | ---- | ----- | ------ | ---------- |
| 1   | Add `get_isolated_entities()` and `get_isolated_notes()` to EntityStore         | 2    | 0.5d  | ⬜     | —          |
| 2   | Add `get_edge_evidence()` to EntityStore                                        | 3    | 0.5d  | ⬜     | —          |
| 3   | Schema migration: `community_id`, `pagerank_score`, `betweenness_score` columns | 3    | 0.25d | ⬜     | —          |
| 4   | Authority scoring as 3rd RRF signal in HybridSearcher                           | 1    | 1d    | ✅     | —          |
| 5   | GraphRetriever (ContextContributor for graph traversal)                         | 1    | 1.5d  | ✅     | —          |
| 6   | Wire GraphRetriever + authority into polly.py                                   | 1    | 0.5d  | ✅     | 4, 5       |
| 7   | Path-finding API endpoint                                                       | 1    | 0.25d | ✅     | —          |
| 8   | Garden maintenance digest endpoint                                              | 2    | 1d    | ⬜     | 1          |
| 9   | Batch operations endpoint                                                       | 2    | 0.5d  | ⬜     | —          |
| 10  | Authority recomputation scheduling                                              | 2    | 0.5d  | ⬜     | —          |
| 11  | Community detection (label propagation)                                         | 3    | 1d    | ⬜     | 3          |
| 12  | PageRank + betweenness centrality                                               | 3    | 1d    | ⬜     | 3          |
| 13  | Upgrade authority formula to use PageRank                                       | 3    | 0.5d  | ⬜     | 12         |
| 14  | Edge confidence scoring (multi-factor)                                          | 3    | 1d    | ⬜     | 2          |
| 15  | "Why this connection?" API endpoint                                             | 3    | 0.5d  | ⬜     | 14         |
| 16  | Communities API endpoint                                                        | 3    | 0.25d | ⬜     | 11         |
| 17  | Frontend: isolation badges in browse list                                       | 2    | 0.5d  | ⬜     | 1, 8       |
| 18  | Frontend: garden digest panel                                                   | 2    | 0.5d  | ⬜     | 8          |
| 19  | Frontend: community cluster coloring toggle                                     | 3    | 0.5d  | ⬜     | 11, 16     |
| 20  | Frontend: path highlighting between nodes                                       | 3    | 0.5d  | ⬜     | 7          |
| 21  | Frontend: edge confidence tooltip + "Why?" modal                                | 3    | 0.5d  | ⬜     | 15         |
| 22  | Config entries (`knowledge_graph` section)                                      | 1    | 0.25d | ✅     | —          |
| 23  | Tests: GraphRetriever + authority RRF                                           | 1    | 1d    | ✅     | 4, 5, 6    |
| 24  | Tests: intelligence module (community, centrality, confidence)                  | 3    | 1d    | ⬜     | 11, 12, 14 |
| 25  | Tests: quality controls (isolation, digest, batch)                              | 2    | 0.5d  | ⬜     | 1, 8, 9    |
| 26  | Update specs (knowledge-graph, rag, architecture)                               | —    | 0.5d  | ⬜     | All        |

---

## Wave 1: Graph-Aware Retrieval (~1 week)

Tasks: 4, 5, 6, 7, 22, 23

### Task 4: Authority Scoring as 3rd RRF Signal

**File:** `core/hybrid_search.py`

Modify `HybridSearcher` to accept an optional `entity_store: EntityStore` and inject authority into RRF:

1. Add `entity_store` parameter to `HybridSearcher.__init__()`
2. New method `_compute_authority_ranks(doc_ids: list[str]) -> dict[str, float]`:
   - For each document, extract its source path from metadata
   - Query `EntityStore` for entities mentioned in that document (via `entity_mentions` table)
   - Return the max authority score among matched entities for each doc
3. In `reciprocal_rank_fusion()`, add authority as a weighted additive term:
   ```python
   authority_bonus = self.authority_weight * authority_scores.get(doc_id, 0.0)
   final_score = rrf_score + authority_bonus
   ```
4. Config weight `rag.authority_weight` (default `0.3`), loadable from config dict
5. Backward compatible: if `entity_store` is None, skip authority computation entirely

**Tests:** `tests/test_graph_retriever.py` — RRF with/without authority, score ordering verification  
**Acceptance:** High-authority documents rank higher than equivalent low-authority documents in RRF output

---

### Task 5: GraphRetriever (ContextContributor)

**New file:** `core/entities/retriever.py`

Implement `GraphRetriever` as a `ContextContributor` (per integration-contracts protocol):

```python
class GraphRetriever:
    name = "graph_retriever"
    priority = 45  # Between memory (50) and RAG patterns (30)

    def __init__(self, entity_store: EntityStore, entity_extractor: EntityExtractor, config: dict):
        self.entity_store = entity_store
        self.extractor = entity_extractor
        self.max_hops = config.get('knowledge_graph', {}).get('graph_traversal', {}).get('max_hops', 2)
        self.min_strength = config.get('knowledge_graph', {}).get('graph_traversal', {}).get('min_strength', 0.3)

    def contribute(self, query: str, domain: str = None, token_budget: int = 0) -> list[dict]:
        # 1. Extract entities from query text (extract_entities_only — no storage)
        # 2. Fuzzy-match against EntityStore.search()
        # 3. For each matched entity: EntityStore.get_related(max_hops, min_strength)
        # 4. Collect entity_mentions for traversed entities → source document paths
        # 5. Score results by: 1/(hop_distance+1) * entity.authority * relationship.strength
        # 6. Deduplicate by source path
        # 7. Format as ContextItems, respecting token_budget
        # 8. Tag with source_type="graph_traversal" for transparency
```

Key details:

- Uses `EntityExtractor.extract_entities_only()` for zero-storage query parsing
- Traversal respects `min_strength` to skip weak edges
- Results include the traversal path (for transparency in responses)
- Returns empty list if no entities match (graceful degradation)

**Tests:** `tests/test_graph_retriever.py` — entity matching, multi-hop traversal, budget limiting, empty query  
**Acceptance:** Query about a well-connected entity returns related notes discovered only through graph structure (not found by semantic search alone)

---

### Task 6: Wire GraphRetriever + Authority into polly.py

**File:** `core/polly.py`

1. In `_init_rag()` (or equivalent initialization): pass `self.entity_store` to `HybridSearcher` constructor
2. In `_init_context_contributors()`: instantiate and register `GraphRetriever` with `priority=45`
3. The existing `_gather_context()` dual-path already iterates contributors — no changes needed there

**Files:** `core/polly.py`  
**Tests:** Integration test confirming graph retrieval appears in context  
**Acceptance:** A query returns context items with `source_type="graph_traversal"` when entities match

---

### Task 7: Path-Finding API Endpoint

**File:** `interfaces/server.py`

New endpoint exposing existing `EntityStore.find_path()`:

```
GET /polly/graph/path?from={entity_id}&to={entity_id}&max_hops=4
```

Response:

```json
{
  "found": true,
  "path": [
    {
      "entity": { "id": "...", "name": "Freire", "type": "PERSON" },
      "role": "start"
    },
    { "relationship": { "type": "INSPIRES", "strength": 0.8 } },
    {
      "entity": { "id": "...", "name": "Critical Pedagogy", "type": "CONCEPT" },
      "role": "intermediate"
    },
    { "relationship": { "type": "RELATED_TO", "strength": 0.6 } },
    {
      "entity": { "id": "...", "name": "Autonomy", "type": "CONCEPT" },
      "role": "end"
    }
  ],
  "length": 2,
  "total_strength": 0.48
}
```

**Tests:** Basic path found, no path found, invalid entity IDs  
**Acceptance:** Frontend can request and render path between two clicked nodes

---

### Task 22: Config Entries

**File:** `config.yaml`

Add `knowledge_graph` section with all Wave 1-3 defaults (see design.md for full schema). All features default to enabled but with conservative parameters.

**Tests:** Config loads without error; defaults applied when keys missing  
**Acceptance:** `config.yaml` documents all 12b configuration options

---

### Task 23: Tests — GraphRetriever + Authority RRF

**New file:** `tests/test_graph_retriever.py`

Tests for Tasks 4, 5, 6:

- Authority RRF scoring: docs with high-authority entities rank higher
- Authority RRF backward compat: no entity_store → identical behavior
- GraphRetriever: entity extraction from query → graph traversal → context items
- GraphRetriever: respects max_hops and min_strength config
- GraphRetriever: respects token_budget
- GraphRetriever: empty query / no matching entities → empty results
- GraphRetriever: deduplicate across multiple traversal paths
- Integration: GraphRetriever registered and contributes in \_gather_context flow

**Target:** 20+ tests, all passing

---

## Wave 2: Quality Controls (~1 week)

Tasks: 1, 8, 9, 10, 17, 18, 25

### Task 1: EntityStore Isolation Methods

**File:** `core/entities/store.py`

Add two new methods:

```python
def get_isolated_entities(self, max_connections: int = 2) -> list[dict]:
    """Return entities with <= max_connections total relationships.
    Includes: entity info, connection_count, last_mentioned_at.
    Ordered by connection_count ASC, then authority ASC."""

def get_isolated_notes(self, max_entity_connections: int = 2) -> list[dict]:
    """Return notes where ALL extracted entities have <= max_entity_connections.
    A note is 'isolated' if none of its entities are well-connected.
    Returns: note path, entity_count, max_connection_count."""
```

Implementation: SQL queries joining `entities` → `relationships` (COUNT) → `entity_mentions` (source grouping).

**Tests:** `tests/test_graph_intelligence.py` — isolated with 0 connections, borderline with exactly threshold, well-connected excluded  
**Acceptance:** Garden digest can report isolated notes accurately

---

### Task 8: Garden Maintenance Digest Endpoint

**File:** `interfaces/server.py`

New endpoint:

```
GET /polly/graph/garden/digest?days=7
```

Assembles a comprehensive quality report by calling existing garden methods + new isolation methods:

1. `get_isolated_notes()` → isolated notes list
2. Existing suggestion logic from `/garden/suggestions` → merge candidates, connection suggestions
3. `entity_store.search()` with low authority → enrichment targets (notes with entities but few connections)
4. Existing `/garden/stats` data → summary statistics
5. Delta computation: compare current stats vs. stored stats from N days ago

Response: structured JSON (see design.md for full schema).

**Files:** `interfaces/server.py`, optionally a helper in `core/entities/store.py` for stats persistence  
**Tests:** `tests/test_graph_intelligence.py` — digest returns expected structure; empty vault returns empty lists  
**Acceptance:** Frontend can render a "Knowledge Health" card from this endpoint

---

### Task 9: Batch Operations Endpoint

**File:** `interfaces/server.py`

New endpoint:

```
POST /polly/graph/garden/batch
{
  "operations": [
    {"type": "merge", "entities": ["id1", "id2"], "keep": "id1"},
    {"type": "delete", "entities": ["id3"]},
    {"type": "connect", "source": "id4", "target": "id5", "relationship_type": "RELATED_TO", "strength": 0.7}
  ]
}
```

- Executes all operations in a single SQLite transaction
- Returns per-operation success/failure status
- Triggers authority recomputation after batch completes
- Reuses existing `EntityStore` methods: `move_mentions()` (merge), `delete()`, `upsert_relationship()` (connect)

**Tests:** Batch with mixed operations, partial failure handling, transaction rollback  
**Acceptance:** User can select multiple entities in garden UI and perform bulk cleanup

---

### Task 10: Authority Recomputation Scheduling

**File:** `core/entities/store.py` (or new helper)

Add periodic recomputation:

1. New `metadata` table in entities.db: `key TEXT PRIMARY KEY, value TEXT`
2. Store `last_authority_recompute` timestamp
3. New method `maybe_recompute_authority(interval_hours: int = 24) -> bool`:
   - Check if last recompute was > interval_hours ago
   - If so, call `recompute_authority()` for all entities, update timestamp
   - Return whether recomputation ran
4. Called from server startup and after batch operations
5. Config: `knowledge_graph.authority_recompute_interval_hours` (default: 24)

**Tests:** Recomputes when stale, skips when fresh, handles missing metadata row  
**Acceptance:** Authority scores stay current without manual intervention

---

### Task 17: Frontend — Isolation Badges

**File:** `electron-app/src/renderer/app.js`

In the graph browse list (`renderGraphSidebar()`):

- When rendering each note entry, check if `connection_count <= isolation_threshold`
- Show ⚠️ icon + "Isolated" tooltip for flagged notes
- Add filter toggle: "Show isolated only" in the filter panel
- Count badge on filter: "12 isolated"

Data source: `/graph/list` already returns connection counts per note. Frontend just needs to apply threshold display logic.

**Tests:** Manual — verify badge appears for low-connection notes  
**Acceptance:** User can visually identify isolated notes at a glance

---

### Task 18: Frontend — Garden Digest Panel

**File:** `electron-app/src/renderer/app.js`

Render the `/graph/garden/digest` response in the Garden view:

- "Knowledge Health" summary card at top of Garden view
- Sections: Isolated Notes (count + list), Merge Candidates (grouped pairs), Connection Suggestions, Stats Summary
- "Review" button on each section to jump to relevant items
- "Refresh" button to re-fetch digest
- Collapse/expand for each section

**Tests:** Manual — verify panel renders, sections collapse, review buttons navigate  
**Acceptance:** User sees actionable knowledge health summary in Garden view

---

### Task 25: Tests — Quality Controls

**New file or extend:** `tests/test_graph_intelligence.py`

Tests for Tasks 1, 8, 9, 10:

- Isolation detection: zero connections, at threshold, above threshold
- Isolated notes: all entities isolated → note flagged; one well-connected entity → note not flagged
- Digest endpoint: returns valid structure; empty store → empty lists
- Batch operations: merge + delete + connect in single call; rollback on invalid operation
- Authority scheduling: recomputes when stale; skips when fresh

**Target:** 15+ tests, all passing

---

## Wave 3: Graph Intelligence & Reasoning (~1 week)

Tasks: 2, 3, 11, 12, 13, 14, 15, 16, 19, 20, 21, 24

### Task 2: Entity Edge Evidence Method

**File:** `core/entities/store.py`

New method:

```python
def get_edge_evidence(self, source_id: str, target_id: str) -> dict:
    """Return evidence for why two entities are connected.
    Returns: relationship records, shared mentions (notes both appear in),
    co-occurrence context snippets from entity_mentions."""
```

Queries `relationships` table for direct edges + `entity_mentions` for shared source documents. Returns raw data that EdgeConfidenceScorer will analyze.

**Tests:** Edge with evidence, edge without evidence, no edge  
**Acceptance:** "Why this connection?" endpoint can source its data

---

### Task 3: Schema Migration

**File:** `core/entities/store.py` (in `_init_db()`)

Add columns via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`:

- `entities.community_id INTEGER DEFAULT NULL`
- `entities.pagerank_score REAL DEFAULT 0.0`
- `entities.betweenness_score REAL DEFAULT 0.0`

Safe migration: `ALTER TABLE` with defaults, wrapped in try/except for idempotency. No data loss.

**Tests:** Fresh DB creates columns; existing DB adds columns; double-run is safe  
**Acceptance:** Intelligence module can read/write new columns

---

### Task 11: Community Detection

**New file:** `core/entities/intelligence.py`

Implement `CommunityDetector` using label propagation (pure Python):

```python
class CommunityDetector:
    def detect(self, entity_store: EntityStore, min_community_size: int = 3) -> dict[int, list[str]]:
        """Label propagation community detection.
        1. Load all entities + relationships from EntityStore
        2. Initialize each node with unique label
        3. Iterate: each node adopts most common neighbor label (random tie-break)
        4. Converge when no labels change (or max 50 iterations)
        5. Filter out communities smaller than min_community_size
        6. Write community_id back to entities table
        Returns {community_id: [entity_ids]}
        """
```

Key details:

- Pure Python — no networkx, igraph, or scipy dependency
- Relationship `strength` used as edge weight (stronger = more influence on label adoption)
- Nodes with no edges get `community_id = NULL` (unclustered)
- Deterministic iteration order (sorted entity IDs) for reproducibility

**Tests:** Known graph topology → expected clusters; disconnected components; single-node communities filtered  
**Acceptance:** Community IDs visible in entity API responses and frontend

---

### Task 12: PageRank + Betweenness Centrality

**File:** `core/entities/intelligence.py`

```python
class CentralityComputer:
    def pagerank(self, entity_store: EntityStore, damping: float = 0.85, iterations: int = 100) -> dict[str, float]:
        """Power iteration PageRank.
        1. Load adjacency from EntityStore (directed: source→target relationships)
        2. Initialize all ranks to 1/N
        3. Iterate: rank(v) = (1-d)/N + d * Σ(rank(u)/out_degree(u)) for u→v
        4. Normalize to [0, 1]
        5. Write pagerank_score to entities table
        """

    def betweenness_centrality(self, entity_store: EntityStore, sample_size: int = 100) -> dict[str, float]:
        """Approximate betweenness via random source sampling.
        1. Sample min(sample_size, N) random source nodes
        2. BFS from each source → shortest paths to all reachable nodes
        3. Count path-through for each intermediate node
        4. Normalize by sample size
        5. Write betweenness_score to entities table
        """
```

Both are pure Python, operating on adjacency lists loaded in bulk from EntityStore.

**Tests:** Known graph → expected PageRank ordering; star graph → center has max betweenness; empty graph → all zeros  
**Acceptance:** PageRank scores stored and queryable; top entities by PageRank match intuitive importance

---

### Task 13: Upgrade Authority Formula

**File:** `core/entities/store.py`

Replace current `recompute_authority()` formula:

```python
# Current: 0.4*log(mentions) + 0.3*log(sources) + 0.2*(rel_count/max) + 0.1*recency
# New:     0.4*pagerank + 0.3*log(mentions) + 0.2*betweenness + 0.1*recency
```

- If `pagerank_score` and `betweenness_score` are populated (non-zero), use the new formula
- If not populated (intelligence module hasn't run yet), fall back to old formula
- This makes the transition seamless — first run uses old formula, subsequent runs use graph-informed formula

**Tests:** New formula with populated scores; fallback with zero scores; score ordering matches expectation  
**Acceptance:** Authority scores reflect graph-structural importance, not just mention counts

---

### Task 14: Edge Confidence Scoring

**File:** `core/entities/intelligence.py`

```python
@dataclass
class EdgeConfidence:
    composite: float                    # Weighted final score [0, 1]
    co_occurrence: float               # How many shared documents
    semantic_similarity: float          # Description/context cosine similarity (if available)
    temporal_proximity: float           # 1 / (1 + days_between_first_mentions)
    structural_proximity: float         # 1 / (1 + shortest_path_length)

class EdgeConfidenceScorer:
    def __init__(self, entity_store: EntityStore, weights: dict = None):
        self.weights = weights or {
            'co_occurrence': 0.35, 'semantic_similarity': 0.25,
            'temporal_proximity': 0.15, 'structural_proximity': 0.25
        }

    def score(self, source_id: str, target_id: str) -> EdgeConfidence:
        """Compute multi-factor edge confidence."""
```

- `co_occurrence`: count shared source documents in `entity_mentions` / max co-occurrence in graph
- `semantic_similarity`: cosine similarity of entity `description` fields (use simple TF-IDF or context overlap if no embeddings available)
- `temporal_proximity`: based on `created_at` of first mentions for each entity
- `structural_proximity`: `find_path()` length, inverted (closer = higher)
- Weights configurable via `knowledge_graph.edge_confidence.weights` in config

**Tests:** Known co-occurrence → expected score; no shared documents → low co_occurrence; adjacent nodes → high structural  
**Acceptance:** Every edge in the graph can report a multi-factor confidence score

---

### Task 15: "Why This Connection?" API Endpoint

**File:** `interfaces/server.py`

```
GET /polly/graph/edge/explain?source={entity_id}&target={entity_id}
```

Response (see design.md for full schema):

- `EdgeConfidence` scores from Task 14
- Evidence snippets from `get_edge_evidence()` (Task 2) — shared documents, context snippets
- Human-readable explanations for each factor

**Tests:** Explain existing edge; explain non-existent edge → 404; invalid IDs → 400  
**Acceptance:** Frontend "Why?" modal can display full factor breakdown

---

### Task 16: Communities API Endpoint

**File:** `interfaces/server.py`

```
GET /polly/graph/communities
```

Response:

```json
{
  "communities": [
    {
      "id": 1,
      "members": [{ "id": "...", "name": "...", "type": "CONCEPT" }],
      "size": 12,
      "domains": { "philosophy": 5, "technology": 4, "education": 3 },
      "top_entities": [{ "name": "Freire", "pagerank": 0.42 }]
    }
  ],
  "unclustered_count": 15
}
```

Data source: `entities` table `community_id` column + aggregation.

**Tests:** Communities returned with members; empty graph → empty list  
**Acceptance:** Frontend can render community-colored graph

---

### Task 19: Frontend — Community Cluster Coloring

**File:** `electron-app/src/renderer/app.js`

- New toggle in graph controls: "Color by: Domain | Community"
- When "Community" selected, fetch `/graph/communities` and assign a color per community
- Unclustered nodes shown in gray
- Legend updates to show community IDs/labels instead of domains
- Community boundaries: draw convex hulls or background blobs around cluster members (Cytoscape.js compound nodes or overlay)

**Tests:** Manual — toggle between domain/community coloring; verify cluster visual grouping  
**Acceptance:** Topic clusters visually identifiable

---

### Task 20: Frontend — Path Highlighting

**File:** `electron-app/src/renderer/app.js`

- When two nodes are selected (shift-click), fetch `/graph/path` and highlight the result
- Highlighted edges get animated dash pattern + accent color
- Intermediate nodes get a glow/ring effect
- "N hops" label shown on path overlay
- Clear path button or click elsewhere to dismiss
- If no path found, show toast: "No path between these entities within 4 hops"

**Tests:** Manual — select two nodes, verify path animates; no path shows message  
**Acceptance:** User can discover non-obvious conceptual connections

---

### Task 21: Frontend — Edge Confidence and "Why?" Modal

**File:** `electron-app/src/renderer/app.js`

- Edge hover shows tooltip: strength value + confidence score
- Edge click opens "Why this connection?" modal
- Modal layout: confidence meter bar, 4 factor bars (co_occurrence, semantic, temporal, structural), evidence snippets list
- Fetch from `/graph/edge/explain` on click
- Loading state while fetching
- Close on overlay click or Escape

**Tests:** Manual — click edge, verify modal renders with factor scores; close works  
**Acceptance:** User understands why any two entities are connected

---

### Task 24: Tests — Intelligence Module

**New file:** `tests/test_graph_intelligence.py`

Tests for Tasks 11, 12, 13, 14:

- Community detection: two disconnected cliques → two communities; fully connected → one community; min_size filtering
- PageRank: star graph center highest; linear chain has gradient; isolated nodes equal
- Betweenness: bridge node between two clusters scored highest; leaf nodes near zero
- Authority formula: new formula with pagerank/betweenness; fallback when scores are zero
- Edge confidence: known co-occurrence/temporal/structural values → expected composite
- Edge confidence: configurable weights change composite score
- Integration: full pipeline (detect communities → compute centrality → score edges → recompute authority)

**Target:** 25+ tests, all passing

---

## Task 26: Update Specs

**Files:** `openspec/specs/knowledge-graph/spec.md`, `openspec/specs/rag/spec.md`, `openspec/specs/architecture/spec.md`, `openspec/specs/project/status.md`, `openspec/specs/project/roadmap.md`

Update implementation status markers. Move 12b from 📋 to ✅. Document new retrieval strategy in RAG spec. Add knowledge_graph config to architecture spec.

---

## Execution Order

**Wave 1** (can start immediately):

1. Task 22 (config) — unblocks everything
2. Tasks 4 + 5 in parallel (authority RRF + GraphRetriever)
3. Task 7 (path API) — independent
4. Task 6 (wiring) — after 4 + 5
5. Task 23 (tests) — after 4 + 5 + 6

**Wave 2** (after Wave 1, or partially parallel):

1. Task 1 (isolation methods) — independent
2. Task 10 (scheduling) — independent
3. Tasks 8 + 9 (digest + batch endpoints) — after 1
4. Tasks 17 + 18 (frontend) — after 8
5. Task 25 (tests) — after 1 + 8 + 9

**Wave 3** (after Wave 2, or partially parallel with Wave 2 backend):

1. Tasks 2 + 3 (evidence + schema) — independent
2. Tasks 11 + 12 in parallel (communities + centrality)
3. Task 13 (authority upgrade) — after 12
4. Task 14 (confidence scoring) — after 2
5. Tasks 15 + 16 (API endpoints) — after 14, 11
6. Tasks 19 + 20 + 21 (frontend) — after 15, 16, 7
7. Task 24 (tests) — after 11, 12, 14

**Finally:** Task 26 (spec updates) — after all waves complete
