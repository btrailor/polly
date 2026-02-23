# OpenSpec: Context Quality Observability

**Status:** ✅ Implemented  
**Priority:** P6 — Enables iteration on all other systems  
**Related:** `core/polly.py`, `core/context/budget_allocator.py`, `~/.polly/usage.db`, `interfaces/server.py`  
**Motivation:** Redis's 2026 guidance is explicit: you cannot optimise what you don't measure. Polly has routing outcome recording and budget reporting in debug logs but no persistent, queryable metrics on context system performance. Without this, every other improvement in this spec series operates blind.

---

## Problem (Detailed)

Currently, context system behaviour is only observable through:

1. **Debug logs** — `logger.debug(f"Budget-aware context: {len(parts)} entries selected...")` — ephemeral, not queryable
2. **BudgetPlan.summary()** — produces a human-readable string logged at debug level, not persisted
3. **Routing outcome patterns** — records which model was used, not which context contributed to quality

There is no persistent record of:
- Which contributors fired on each query and how many tokens they used
- What the budget utilisation rate was per section
- Which query types have poor retrieval quality (low context precision)
- Whether the RollingContext is actually helping (do referenced entries improve responses?)
- Cache hit rates (once semantic cache is implemented)
- SRS values at compression time

Without this data, the choice of `direct_threshold: 0.72`, `decay_per_turn: 0.85`, `target_pct` values in budget allocator, and mental model activation thresholds are all set by intuition and cannot be tuned systematically.

---

## Proposed Solution

A lightweight **Context Quality Ledger** — a set of new tables in the existing `~/.polly/usage.db` SQLite database that record structured per-turn context metrics. A query API and a UI panel expose these metrics for inspection and trend analysis.

---

## Data Schema

### Table: `context_turns`

One row per turn (query/response pair).

```sql
CREATE TABLE IF NOT EXISTS context_turns (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id          TEXT NOT NULL,
    turn_number         INTEGER NOT NULL,
    timestamp           DATETIME NOT NULL,
    query_length_tokens INTEGER,
    response_length_tokens INTEGER,
    domains             TEXT,           -- JSON array of detected domains
    persona             TEXT,
    model_used          TEXT,
    routing_confidence  TEXT,           -- "fast" | "balanced" | "thorough"
    cache_hit           BOOLEAN NOT NULL DEFAULT 0,
    cache_similarity    REAL,           -- cosine similarity if cache hit
    total_context_tokens INTEGER,       -- total tokens sent in context
    budget_utilisation  REAL,           -- total_used / total_allocated (0-1)
    srs_at_turn         REAL,           -- Semantic Redundancy Score if computed
    decomposed          BOOLEAN NOT NULL DEFAULT 0,  -- Wave 3 decomposition fired
    sub_query_count     INTEGER         -- if decomposed
);
```

### Table: `context_contributor_turns`

One row per contributor per turn. Captures what each system contributed.

```sql
CREATE TABLE IF NOT EXISTS context_contributor_turns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id         INTEGER NOT NULL REFERENCES context_turns(id),
    contributor     TEXT NOT NULL,      -- "mental_models" | "memory" | "entities" | "patterns" | "compression" | "rag"
    items_returned  INTEGER,            -- number of ScoredEntry items returned (post spec-02)
    tokens_allocated INTEGER,
    tokens_used     INTEGER,
    utilisation     REAL,               -- tokens_used / tokens_allocated
    top_score       REAL,               -- highest composite_score in this contributor's items
    avg_score       REAL,               -- mean composite_score
    items_selected  INTEGER,            -- items that made it through bin-packing
    items_evicted   INTEGER             -- items returned but not selected (over budget)
);
```

### Table: `context_rag_turns`

Dedicated RAG metrics per turn (richer than the contributor table).

```sql
CREATE TABLE IF NOT EXISTS context_rag_turns (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id             INTEGER NOT NULL REFERENCES context_turns(id),
    chunks_retrieved    INTEGER,
    chunks_used         INTEGER,        -- chunks whose content appeared in response
    chunks_unused       INTEGER,        -- chunks retrieved but not referenced
    top_chunk_score     REAL,
    avg_chunk_score     REAL,
    hybrid_enabled      BOOLEAN,
    pattern_boosted     INTEGER,        -- chunks that received a positive boost
    pattern_penalised   INTEGER,        -- chunks that received a negative penalty
    collections_searched TEXT,          -- JSON array of collection names
    retrieval_tier      TEXT            -- "DIRECT" | "ADJACENT" | "ABSENT"
);
```

---

## Recording Metrics

### In `polly.py` — at end of each `chat()` turn

```python
async def _record_context_metrics(
    self,
    session_id: str,
    turn_number: int,
    query: str,
    response: str,
    domains: List[str],
    persona: Optional[str],
    model_used: str,
    budget_plan: Optional[BudgetPlan],
    cache_hit: Optional[CacheHit],
    rag_chunks: List[Chunk],
    contributor_results: List[ContributorMetrics],
    srs: Optional[float],
    decomposed: bool,
    sub_query_count: int,
):
    """
    Write one row to context_turns and one row per contributor to
    context_contributor_turns. Non-blocking: runs in background thread.
    """
    ...
```

`ContributorMetrics` is a lightweight dataclass populated during `_gather_context()`:

```python
@dataclass
class ContributorMetrics:
    contributor: str
    items_returned: int
    tokens_allocated: int
    tokens_used: int
    top_score: float
    avg_score: float
    items_selected: int
    items_evicted: int
```

### In `_gather_context()` — instrument each contributor call

After each `build_context_items()` call, create a `ContributorMetrics` record. After bin-packing, compute `items_selected` and `items_evicted` per contributor.

### Non-blocking write

Metrics writes go to a background `asyncio.Task` or `concurrent.futures.ThreadPoolExecutor` to avoid adding latency to the main query path. If the write fails (disk full, lock contention), log a warning and continue — metrics are never critical path.

---

## Query API

```
GET /api/metrics/context?days=7
```

Returns aggregated context metrics for the last N days:

```json
{
  "period_days": 7,
  "total_turns": 142,
  "cache_hit_rate": 0.18,
  "avg_budget_utilisation": 0.74,
  "avg_total_context_tokens": 3840,
  "contributor_breakdown": [
    {"contributor": "rag",           "avg_tokens_used": 1200, "avg_utilisation": 0.80, "avg_items_selected": 4.2},
    {"contributor": "memory",        "avg_tokens_used": 420,  "avg_utilisation": 0.62, "avg_items_selected": 2.1},
    {"contributor": "mental_models", "avg_tokens_used": 580,  "avg_utilisation": 0.91, "avg_items_selected": 2.8},
    {"contributor": "patterns",      "avg_tokens_used": 180,  "avg_utilisation": 0.45, "avg_items_selected": 1.2},
    {"contributor": "entities",      "avg_tokens_used": 210,  "avg_utilisation": 0.55, "avg_items_selected": 1.8}
  ],
  "rag_quality": {
    "avg_chunks_retrieved": 5.2,
    "avg_chunks_used": 2.8,
    "chunk_utilisation_rate": 0.54,
    "avg_pattern_boosted": 1.4
  },
  "routing": {
    "fast_pct": 0.31,
    "balanced_pct": 0.52,
    "thorough_pct": 0.17
  }
}
```

```
GET /api/metrics/context/turns?limit=20&session_id=...
```

Returns raw turn-level metrics for debugging.

```
GET /api/metrics/context/trends?metric=cache_hit_rate&days=30
```

Returns time-series data for a specific metric — used by the UI to render trend charts.

---

## UI Integration

A **Context Health** panel in the Settings or Analytics page (extending the existing autonomy metrics dashboard):

- **Budget utilisation bar chart** — per contributor, showing how much of their allocated budget is actually used. A contributor consistently at < 40% utilisation suggests its budget allocation is too generous.
- **Chunk utilisation rate trend** — over last 30 days. A declining trend suggests the knowledge base is growing stale or query patterns are shifting.
- **Cache hit rate** — once semantic cache (spec-01) is implemented.
- **Contributor token cost breakdown** — doughnut chart showing what percentage of context tokens each contributor consumes on average.
- **SRS trend at compression** — scatter plot of SRS values at the moment compression fired. Should cluster well below the threshold. Points far above threshold indicate structural triggers compressing unnecessarily.

---

## Derived Quality Signals

Beyond raw metrics, compute two derived signals:

### 1. Context Precision Proxy

```
context_precision_proxy = chunks_used / chunks_retrieved
```

If this falls below 0.4 over a 7-day window, it means more than 60% of retrieved RAG content is consistently unused. This is the primary signal for triggering a review of retrieval thresholds, chunk size, or collection composition.

### 2. Contributor Efficiency Score

```
contributor_efficiency = (tokens_used / tokens_allocated) * avg_items_selected_rate
```

A contributor with 0.3 efficiency means it uses only 30% of its budget and rarely has items selected by bin-packing. This contributor's `target_pct` in the `BudgetAllocator` config should be reduced.

Both signals are surfaced as health indicators in the UI with traffic-light colouring (green/yellow/red).

---

## Alerting

Simple threshold-based alerts logged to the application logger at WARN level (not user-facing notifications — this is an observability tool for development):

- `cache_hit_rate < 0.05` after 7 days of use → log: "Semantic cache hit rate low — check similarity threshold"
- `chunk_utilisation_rate < 0.35` → log: "RAG chunk precision low — review n_results or chunk_size"  
- `avg_budget_utilisation < 0.50` → log: "Context budget underutilised — consider reducing response_reserve or adjusting section target_pct"
- `memory contributor avg_utilisation < 0.30` → log: "Memory contributor consistently underutilised — Mem0 may have sparse content or similarity threshold may be too high"

---

## Files Touched

| File | Change |
|------|--------|
| `~/.polly/usage.db` | New tables: `context_turns`, `context_contributor_turns`, `context_rag_turns` |
| `core/polly.py` | Add `_record_context_metrics()`, `ContributorMetrics` dataclass; instrument `_gather_context()` and `chat()` |
| `interfaces/server.py` | Add `/api/metrics/context`, `/api/metrics/context/turns`, `/api/metrics/context/trends` |
| `electron-app/src/renderer/` | Context Health panel in analytics/settings page |

---

## Implementation Notes

### Completed
- `core/context_metrics.py` — `ContextMetrics` class with SQLite tables (`context_turns`, `context_contributor_turns`) in `~/.polly/usage.db`
- `core/polly.py` — metrics initialised on startup, `_record_context_metrics()` called after each turn with contributor breakdown and budget utilisation
- `interfaces/server.py` — `/api/metrics/context` (aggregate) and `/api/metrics/context/turns` (per-turn history) endpoints

### Not Yet Done
- `/api/metrics/context/trends` endpoint
- UI Context Health panel in Electron app
- `context_rag_turns` table (RAG-level granularity)

---

## Success Criteria

- [x] Every turn writes metrics to `context_turns` and `context_contributor_turns` within 50ms
- [x] `/api/metrics/context` returns correctly aggregated data
- [ ] `context_precision_proxy` and `contributor_efficiency` are computable from stored data
- [x] Metrics writes never block or slow the main query path (background thread confirmed)
- [ ] Trend charts render in the UI for cache hit rate and chunk utilisation rate
- [ ] Derived quality signals fire correctly against test data with known properties
