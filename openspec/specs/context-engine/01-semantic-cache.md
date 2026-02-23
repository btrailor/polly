# OpenSpec: Semantic Cache Layer

**Status:** ✅ Implemented (Phase A complete)  
**Priority:** P1 — Highest ROI  
**Related:** `core/rag.py`, `core/polly.py`, `core/context/token_counter.py`  
**Motivation:** Redis 2026 prediction — semantic caching delivers up to 73% cost reduction and 15x faster responses for cache hits. Polly currently has zero caching between query intake and LLM call.

---

## Problem

Every query Polly receives follows the full pipeline regardless of whether an equivalent query was answered moments ago:

```
Query → embed (Ollama) → ChromaDB search → context assembly → LLM call → response
```

There is no recognition that "What is Finite and Infinite Games about?" and "Can you summarise Finite and Infinite Games?" are semantically equivalent to a recently-answered query. The full pipeline runs, paying full embedding + LLM cost every time.

This is the largest single gap between Polly's current architecture and the Redis "context engine" model.

---

## Proposed Solution

A **semantic cache layer** sits in front of the full query pipeline. On every incoming query:

1. Embed the query using the same embedding model already in use (`nomic-embed-text` via Ollama).
2. Search the cache store for a near-match (cosine similarity ≥ threshold).
3. If hit: return the cached response immediately. Log the cache hit.
4. If miss: run the full pipeline, then store `{query_embedding, query_text, response, metadata}` in the cache.

---

## Architecture

### New File: `core/cache/semantic_cache.py`

```python
class SemanticCache:
    """
    Semantic cache for query→response pairs.
    
    Stores embeddings + responses in a lightweight ChromaDB collection
    (~/.polly/semantic_cache). Returns cached responses for semantically
    equivalent queries above a similarity threshold.
    """

    def __init__(
        self,
        db_path: str,               # ~/.polly/semantic_cache
        embed_fn: Callable,         # same embed_text() used by UnifiedRAG
        similarity_threshold: float = 0.92,
        max_entries: int = 500,
        ttl_hours: int = 24,
    ): ...

    def lookup(self, query: str) -> Optional[CacheHit]: ...
    def store(self, query: str, response: str, metadata: dict) -> None: ...
    def invalidate(self, older_than_hours: int = None) -> int: ...
    def stats(self) -> CacheStats: ...
```

### New File: `core/cache/__init__.py`

Exports `SemanticCache`, `CacheHit`, `CacheStats`.

### Integration Point: `core/polly.py` — `chat()` method

```python
# BEFORE full pipeline — semantic cache lookup
if self.semantic_cache:
    hit = self.semantic_cache.lookup(query)
    if hit:
        logger.info(f"Semantic cache hit (similarity={hit.similarity:.3f})")
        # Return cached response with cache-hit metadata
        yield hit.response
        self._record_cache_hit(hit)
        return

# ... full pipeline runs on miss ...

# AFTER response generated — store in cache
if self.semantic_cache and response:
    self.semantic_cache.store(query, response, metadata={
        "domains": domains,
        "persona": persona,
        "model": model_used,
        "timestamp": datetime.now().isoformat(),
    })
```

### New Init: `core/polly.py` — `_init_semantic_cache()`

Called after `_init_rag()`. Uses the same ChromaDB path prefix as RAG but a dedicated collection. Reuses the existing `embed_text()` function from `UnifiedRAG`.

---

## Data Model

### CacheHit

```python
@dataclass
class CacheHit:
    query: str               # Original cached query
    response: str            # Cached response text
    similarity: float        # Cosine similarity to lookup query
    age_hours: float         # How old the cached entry is
    metadata: dict           # Domain, persona, model at cache time
    cache_key: str           # ChromaDB document ID
```

### CacheStats

```python
@dataclass
class CacheStats:
    total_entries: int
    hit_count: int           # Lifetime hits (persisted)
    miss_count: int          # Lifetime misses (persisted)
    hit_rate: float          # hit_count / (hit_count + miss_count)
    tokens_saved: int        # Estimated: avg_response_tokens * hit_count
    oldest_entry_hours: float
    newest_entry_hours: float
```

---

## Storage

The cache uses a dedicated ChromaDB collection at `~/.polly/semantic_cache/`. This is separate from the RAG vector store (`~/.polly/chroma_db/`) to prevent contamination.

Hit/miss counters and `tokens_saved` estimates are persisted to the existing usage SQLite database (`~/.polly/usage.db`) in a new `semantic_cache_stats` table.

---

## Configuration

```yaml
# config/config.yaml — new section
semantic_cache:
  enabled: true
  similarity_threshold: 0.92    # Cosine similarity for cache hit (0.0-1.0)
  max_entries: 500               # LRU eviction above this count
  ttl_hours: 24                  # Entries older than this are stale
  exclude_personas: []           # Personas that should never be cached (e.g., "scribe")
  exclude_domains: []            # Domains that should never be cached
  min_response_tokens: 50        # Don't cache very short responses (likely errors)
```

### Threshold Guidance

| Threshold | Behaviour |
|-----------|-----------|
| 0.98+ | Near-exact match only — very safe, low hit rate |
| 0.92–0.97 | Recommended — equivalent intent, different phrasing |
| 0.85–0.91 | Aggressive — risk of false positives on topic changes |
| < 0.85 | Not recommended — too many false positives |

---

## Cache Invalidation Strategy

1. **TTL:** Entries older than `ttl_hours` are stale. Checked at lookup time; stale hits are discarded and treated as misses.
2. **LRU eviction:** When `max_entries` is reached, oldest-accessed entries are removed.
3. **Knowledge base change:** When `rag.index_single_document()` is called (new note or code file indexed), any cached responses whose metadata domain overlaps with the indexed file's domain are invalidated. This prevents serving a cached response after the underlying knowledge has changed.
4. **Manual:** `POST /api/cache/clear` endpoint — full or domain-scoped.

---

## Exclusion Rules

Some queries must never be served from cache:

- **Streaming-sensitive:** If the user is in a persona mode that expects real-time response (e.g., Scribe mode during live writing sessions).
- **Time-sensitive queries:** Queries containing temporal markers ("today", "now", "current", "latest", "this week") are excluded. Detected via regex on the query text.
- **Short conversational queries:** Queries under 5 tokens (greetings, acknowledgements) are excluded — they're too cheap to bother caching.
- **Agentic actions:** Any query that triggers a tool call or knowledge write is not cached (the action must execute).

---

## Integration with Pattern Learning

When a cache hit occurs, record it as a `ROUTING_OUTCOME` pattern in the `PatternEngine`:

```python
# Cache hit = confirmed high-quality response for this query type
self.pattern_engine.learn_from_cache_hit(
    query=query,
    similarity=hit.similarity,
    original_query=hit.query,
)
```

This creates a feedback loop: frequent cache hits for a query type reinforce the associated `QueryChunkPattern` chunks, making future retrievals faster even after the cache expires.

---

## API

```
GET  /api/cache/stats          — CacheStats JSON
POST /api/cache/clear          — Invalidate all or by domain
GET  /api/cache/entries?limit= — List recent cache entries (debug)
```

---

## Metrics (tracked in usage.db)

| Metric | Description |
|--------|-------------|
| `cache_hits` | Count of cache hits per session |
| `cache_misses` | Count of cache misses per session |
| `cache_hit_rate` | Rolling 7-day hit rate |
| `tokens_saved_est` | Estimated tokens saved (avg response len × hits) |
| `avg_hit_similarity` | Average cosine similarity of cache hits |
| `avg_hit_age_hours` | Average age of entries at hit time |

---

## Implementation Phases

### Phase A — Core Cache (implement first)
- `core/cache/semantic_cache.py` — `SemanticCache` class with ChromaDB backend
- `core/polly.py` — `_init_semantic_cache()`, lookup before pipeline, store after response
- `config/config.yaml` — `semantic_cache` section with defaults

### Phase B — Invalidation & Exclusions
- TTL invalidation at lookup
- LRU eviction when `max_entries` exceeded
- Temporal query exclusion regex
- Knowledge-base-change invalidation hook in `rag.index_single_document()`

### Phase C — Observability & API
- `usage.db` `semantic_cache_stats` table
- `/api/cache/stats` and `/api/cache/clear` endpoints
- Pattern engine feedback loop on hits

---

## Files Touched

| File | Change |
|------|--------|
| `core/cache/__init__.py` | New — exports |
| `core/cache/semantic_cache.py` | New — SemanticCache implementation |
| `core/polly.py` | Add `_init_semantic_cache()`, cache lookup/store in `chat()` |
| `config/config.yaml` | Add `semantic_cache:` section |
| `interfaces/server.py` | Add `/api/cache/stats`, `/api/cache/clear` endpoints |
| `~/.polly/usage.db` | New `semantic_cache_stats` table (migration) |

---

## Implementation Notes

### Phase A — Completed
- `core/cache/__init__.py` — created, exports `SemanticCache`, `CacheHit`, `CacheStats`
- `core/cache/semantic_cache.py` — implemented with ChromaDB backend, TTL, LRU eviction, temporal exclusion
- `core/polly.py` — `_init_semantic_cache()`, lookup before pipeline, store after response
- `config/config.yaml` — `semantic_cache:` section added with defaults (`enabled: false`)
- `interfaces/settings_api.py` — `/api/settings/semantic-cache` GET/POST + `/api/settings/semantic-cache/stats`
- `electron-app/src/renderer/index.html` — Semantic Cache section added to AI Features settings panel (toggle + 3 sliders)
- `electron-app/src/renderer/app.js` — localStorage restore on load, save included in `saveAIFeaturesSettings()`

### Phase B — Pending
- Knowledge-base-change invalidation hook in `rag.index_single_document()`
- Temporal query exclusion regex (partial — structure in place)

### Phase C — Pending
- Pattern engine feedback loop on hits
- `/api/cache/clear` endpoint

---

## Success Criteria

- [ ] Cache hit rate ≥ 15% after 1 week of normal use
- [ ] Cache hit response latency < 200ms (vs. 2–8s for full pipeline)
- [ ] Zero false positives observed (no cached response served for a genuinely different query)
- [ ] Tokens saved estimate visible in UI stats
- [ ] Cache correctly invalidated when a related note is updated
