# Design: System-Wide Semantic Response Cache

## Overview
Add a semantic response cache that intercepts queries early in Polly's query pipeline, returns cached responses for semantically similar queries, and tracks token savings through AutonomyMetrics. Uses Polly's existing ChromaDB instance for vector similarity search and SQLite (`usage.db`) for full response storage.

## Architecture

### Component Diagram
```
POST /polly/query
    |
Polly.query()
    |
Domain Detection (L1504)
    |
[NEW] SemanticCache.check() ← ChromaDB cosine similarity + metadata filter
    |                            |
    |--- CACHE HIT -----------> Return CacheResult (response from SQLite)
    |                            + record route_type='cache' in AutonomyMetrics
    |
    |--- CACHE MISS
    |
RAG Search (L1624)
    |
... full pipeline ...
    |
LLM Response (L2356)
    |
[NEW] SemanticCache.store() → ChromaDB upsert + SQLite insert
    |
Return response
```

### Storage Architecture
```
~/.polly/chroma_db/           (shared PersistentClient)
  ├── notes                   (existing)
  ├── codebase                (existing)
  ├── documents               (existing)
  ├── patterns                (existing)
  └── semantic_cache          [NEW] query embeddings + metadata

~/.polly/usage.db             (shared SQLite)
  ├── routing_decisions       (existing - AutonomyMetrics)
  ├── knowledge_writes        (existing - AutonomyMetrics)
  └── cached_responses        [NEW] full response text + metadata
```

### Key Design Decisions

#### 1. Shared ChromaDB Instance
**Decision:** Cache collection lives in the shared `~/.polly/chroma_db` PersistentClient alongside existing RAG collections.

**Rationale:**
- Single ChromaDB process, no extra memory overhead
- Consistent with how notes, codebase, documents, and patterns collections are managed
- Uses same `rag.embed_text()` pipeline (Ollama `nomic-embed-text`)

**Impact:**
- Must initialize after RAG (needs ChromaDB client and embed_text function)
- Collection created via `get_or_create_collection("semantic_cache", metadata={"hnsw:space": "cosine"})`

#### 2. SQLite Sidecar for Full Responses
**Decision:** Store full response text in SQLite (`cached_responses` table in `usage.db`), not in ChromaDB.

**Rationale:**
- ChromaDB documents are optimized for embedding search, not large text storage
- Full LLM responses can be 10K+ characters; ChromaDB stores only first ~2K for embedding
- SQLite is already used for AutonomyMetrics and BudgetManager in the same DB
- Enables efficient cleanup (DELETE with TTL/FIFO queries)

**Impact:**
- Cache check = ChromaDB query (fast vector search) → SQLite fetch (by cache_id)
- Cache store = ChromaDB upsert (embedding + metadata) + SQLite insert (full response)

#### 3. Pipeline Insertion Point
**Decision:** Cache check after domain detection (L1514), before RAG search (L1624).

**Rationale:**
- Domain info available for metadata filtering (improves cache precision)
- Skips ~95% of pipeline cost on cache hit (RAG, context gathering, LLM call)
- Early enough to provide maximum latency savings
- Late enough to have domain context for the cache key

**Impact:**
- Cache check receives: query text, detected domain, active persona, query mode
- On hit: returns CacheResult immediately, skips entire pipeline remainder
- On miss: pipeline continues normally; response stored after completion

#### 4. Cache Key Strategy
**Decision:** Semantic embedding + metadata filtering (not exact string match).

**Components:**
- **Embedding:** Query text embedded via `rag.embed_text()` for cosine similarity
- **Metadata filters:** Domain, persona, mode must match exactly
- **Similarity threshold:** Configurable (default 0.92) — queries must be ≥92% similar

**Rationale:**
- "What's the weather" and "how's the weather today" should hit same cache entry
- Domain filter prevents cross-domain false positives (a coding question should never match a writing question)
- Persona filter ensures persona-specific responses stay scoped
- 0.92 threshold balances hit rate vs precision (tunable in settings)

#### 5. Invalidation Strategy
**Decision:** Event-driven invalidation + TTL + FIFO eviction.

**Three invalidation triggers:**
1. **Knowledge writes:** When KnowledgeWriter saves new knowledge, invalidate cache entries in the affected domain (knowledge has changed, cached answers may be stale)
2. **RAG reindex:** When notes or codebase are reindexed, clear all cache entries (underlying context has changed)
3. **TTL expiry:** Entries older than `ttl_hours` (default: 24h) are not returned and are cleaned up periodically

**Eviction:**
- `max_entries` cap (default: 500) with FIFO eviction (oldest entries removed first)
- Cleanup runs on store operations (lazy eviction)

#### 6. What Gets Cached
**Decision:** Only cloud-routed, single-turn, completed responses.

**Cached:**
- Queries routed to cloud providers (Anthropic, OpenAI, Gemini, etc.)
- Single-turn queries (no conversation history dependency)
- Completed (non-streaming) final response text

**Not cached:**
- Local Ollama responses (negligible cost, not worth cache overhead)
- Conversation-dependent queries (multi-turn context makes similarity unreliable)
- Streaming responses (cache serves complete text; streaming is reconstructed)
- Error responses

#### 7. Cache Hit Indicator
**Decision:** Subtle metadata indicator in the response, shown in the model/provider display area.

**Implementation:**
- Response metadata includes `"cache_hit": true` and `"cache_similarity": 0.96`
- Frontend displays "Served from cache" in the provider info area (where it currently shows "via Anthropic" etc.)
- No intrusive banners or notifications

## API Design

### SemanticCache Class

```python
from dataclasses import dataclass
from typing import Optional
import time
import sqlite3
import uuid
import logging

logger = logging.getLogger(__name__)

# Singleton
_instance: Optional['SemanticCache'] = None

def init_semantic_cache(chroma_client, embed_fn, db_path: str, config: dict) -> 'SemanticCache':
    """Initialize the semantic cache singleton."""
    global _instance
    _instance = SemanticCache(chroma_client, embed_fn, db_path, config)
    return _instance

def get_semantic_cache() -> Optional['SemanticCache']:
    """Get the semantic cache singleton (None if not initialized)."""
    return _instance


@dataclass
class CacheResult:
    """Result from a cache hit."""
    response_text: str
    original_query: str
    similarity: float
    domain: str
    persona: str
    model_used: str
    tokens_saved_in: int
    tokens_saved_out: int
    cached_at: float        # Unix timestamp
    cache_id: str


@dataclass
class CacheStats:
    """Cache statistics for metrics and UI."""
    total_entries: int
    hits: int
    misses: int
    hit_rate: float          # 0.0 - 1.0
    total_tokens_saved: int
    estimated_cost_saved: float
    oldest_entry_age_hours: float


class SemanticCache:
    """
    Semantic response cache using ChromaDB for similarity search
    and SQLite for full response storage.
    
    Integrates with Polly's existing ChromaDB instance and usage.db.
    """
    
    def __init__(
        self,
        chroma_client,          # PersistentClient from UnifiedRAG
        embed_fn,               # rag.embed_text() function
        db_path: str,           # Path to usage.db
        config: dict            # semantic_cache config section
    ):
        """
        Initialize semantic cache.
        
        Args:
            chroma_client: Shared ChromaDB PersistentClient
            embed_fn: Embedding function (rag.embed_text)
            db_path: Path to ~/.polly/usage.db
            config: Config dict with keys: enabled, similarity_threshold,
                    ttl_hours, max_entries
        """
    
    def check(
        self,
        query: str,
        domain: str,
        persona: str,
        mode: str = "standard"
    ) -> Optional[CacheResult]:
        """
        Check cache for a semantically similar query.
        
        Args:
            query: The user's query text
            domain: Detected domain (sigils, signals, scrolls, etc.)
            persona: Active persona name
            mode: Query mode (standard, wave3, etc.)
        
        Returns:
            CacheResult if hit found above threshold, None otherwise
        """
    
    def store(
        self,
        query: str,
        response_text: str,
        domain: str,
        persona: str,
        mode: str,
        model_used: str,
        tokens_in: int,
        tokens_out: int,
        cost: float
    ) -> str:
        """
        Store a query-response pair in the cache.
        
        Args:
            query: The original query text
            response_text: The full LLM response text
            domain: Detected domain
            persona: Active persona name
            mode: Query mode
            model_used: The model that generated the response
            tokens_in: Input tokens consumed
            tokens_out: Output tokens consumed
            cost: Cost in USD
        
        Returns:
            cache_id: UUID of the stored entry
        """
    
    def invalidate_domain(self, domain: str) -> int:
        """
        Invalidate all cache entries for a domain.
        Called when KnowledgeWriter saves new knowledge.
        
        Returns:
            Number of entries invalidated
        """
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        Called on RAG reindex or manual clear from settings.
        
        Returns:
            Number of entries cleared
        """
    
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics for metrics and UI display.
        """
    
    # Private methods
    def _ensure_table(self):
        """Create cached_responses table if not exists."""
    
    def _evict_if_needed(self):
        """FIFO eviction when max_entries exceeded."""
    
    def _cleanup_expired(self):
        """Remove entries older than ttl_hours."""
```

### SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS cached_responses (
    cache_id TEXT PRIMARY KEY,           -- UUID
    query_text TEXT NOT NULL,            -- Original query
    response_text TEXT NOT NULL,         -- Full LLM response
    domain TEXT NOT NULL,                -- Domain at time of query
    persona TEXT NOT NULL,               -- Persona at time of query
    mode TEXT NOT NULL DEFAULT 'standard',
    model_used TEXT NOT NULL,            -- Model that generated response
    tokens_in INTEGER NOT NULL,          -- Input tokens consumed
    tokens_out INTEGER NOT NULL,         -- Output tokens consumed
    cost REAL NOT NULL,                  -- Cost in USD
    created_at REAL NOT NULL,            -- Unix timestamp
    last_hit_at REAL,                    -- Last time this entry was returned
    hit_count INTEGER DEFAULT 0          -- Number of times served from cache
);

CREATE INDEX IF NOT EXISTS idx_cached_responses_domain ON cached_responses(domain);
CREATE INDEX IF NOT EXISTS idx_cached_responses_created ON cached_responses(created_at);
```

### ChromaDB Collection Schema

```python
# Collection setup
collection = chroma_client.get_or_create_collection(
    name="semantic_cache",
    metadata={"hnsw:space": "cosine"}
)

# Document structure (per entry)
collection.upsert(
    ids=[cache_id],
    embeddings=[query_embedding],        # Pre-computed via rag.embed_text()
    documents=[query_text[:2000]],       # First 2K chars for ChromaDB storage
    metadatas=[{
        "domain": domain,
        "persona": persona,
        "mode": mode,
        "created_at": timestamp,
        "cache_id": cache_id             # Links to SQLite row
    }]
)

# Query structure
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1,
    where={
        "$and": [
            {"domain": {"$eq": domain}},
            {"persona": {"$eq": persona}},
            {"mode": {"$eq": mode}}
        ]
    }
)
```

## Data Flow

### 1. Cache Check (on every query)
```
Polly.query() after domain detection
    |
SemanticCache.check(query, domain, persona, mode)
    |
embed_fn(query) → query_embedding
    |
ChromaDB collection.query(
    query_embeddings=[query_embedding],
    where={domain, persona, mode},
    n_results=1
)
    |
If distance <= (1 - similarity_threshold):
    |
    SQLite: SELECT response_text, ... FROM cached_responses WHERE cache_id = ?
    |
    UPDATE cached_responses SET last_hit_at = ?, hit_count = hit_count + 1
    |
    Return CacheResult
Else:
    Return None (cache miss)
```

### 2. Cache Store (after successful LLM response)
```
Polly.query() post-processing block (~L2357)
    |
SemanticCache.store(query, response, domain, persona, mode, model, tokens, cost)
    |
embed_fn(query) → query_embedding
    |
Generate cache_id (UUID)
    |
SQLite: INSERT INTO cached_responses (...)
    |
ChromaDB: collection.upsert(ids=[cache_id], embeddings=[...], metadatas=[...])
    |
_evict_if_needed() → remove oldest if > max_entries
    |
Return cache_id
```

### 3. Cache Invalidation (on knowledge change)
```
KnowledgeWriter._save_note() after successful write
    |
SemanticCache.invalidate_domain(domain)
    |
ChromaDB: collection.get(where={"domain": domain}) → ids
    |
ChromaDB: collection.delete(ids=ids)
    |
SQLite: DELETE FROM cached_responses WHERE cache_id IN (...)
    |
Log: "Invalidated {n} cache entries for domain {domain}"
```

### 4. Full Cache Clear (on RAG reindex)
```
rag.index_notes() or rag.index_codebase() completion
    |
SemanticCache.clear()
    |
ChromaDB: collection.delete(where={})  # or delete + recreate
    |
SQLite: DELETE FROM cached_responses
    |
Log: "Cleared all cache entries (RAG reindex)"
```

## Configuration

### config.yaml Addition
```yaml
semantic_cache:
  enabled: true
  similarity_threshold: 0.92    # 0.0-1.0, higher = stricter matching
  ttl_hours: 24                 # Cache entry lifetime
  max_entries: 500              # Maximum cached responses (FIFO eviction)
  min_query_length: 10          # Skip caching for very short queries
  cache_cloud_only: true        # Only cache cloud-routed responses
```

### core/config.py DEFAULT_CONFIG Addition
```python
"semantic_cache": {
    "enabled": True,
    "similarity_threshold": 0.92,
    "ttl_hours": 24,
    "max_entries": 500,
    "min_query_length": 10,
    "cache_cloud_only": True,
}
```

## Pipeline Integration

### Polly.__init__ (init sequence)
```python
# After RAG init (L69), before router init (L74)
def _init_semantic_cache(self):
    """Initialize semantic response cache using shared ChromaDB."""
    try:
        from core.semantic_cache import init_semantic_cache
        cache_config = self.config.get("semantic_cache", {})
        if cache_config.get("enabled", True):
            rag = self.rag  # Already initialized at L69
            init_semantic_cache(
                chroma_client=rag.chroma_client,
                embed_fn=rag.embed_text,
                db_path=os.path.join(self.data_dir, "usage.db"),
                config=cache_config
            )
            logger.info("Semantic cache initialized")
        else:
            logger.info("Semantic cache disabled in config")
    except Exception as e:
        logger.warning(f"Failed to initialize semantic cache: {e}")
```

### Polly.query() — Cache Check (~L1515)
```python
# After domain detection, before RAG search
cache_result = None
if self.config.get("semantic_cache", {}).get("enabled", False):
    from core.semantic_cache import get_semantic_cache
    cache = get_semantic_cache()
    if cache:
        cache_result = cache.check(
            query=query,
            domain=detected_domain,
            persona=active_persona.name,
            mode=query_mode
        )
        if cache_result:
            # Record as cache hit in autonomy metrics
            self._record_cache_hit(cache_result)
            return self._format_cache_response(cache_result)
```

### Polly.query() — Cache Store (~L2357)
```python
# After successful cloud LLM response, in post-processing block
if (self.config.get("semantic_cache", {}).get("enabled", False)
    and route_type != "local"
    and not is_conversation_dependent):
    from core.semantic_cache import get_semantic_cache
    cache = get_semantic_cache()
    if cache:
        try:
            cache.store(
                query=query,
                response_text=response_text,
                domain=detected_domain,
                persona=active_persona.name,
                mode=query_mode,
                model_used=model_used,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost
            )
        except Exception as e:
            logger.warning(f"Failed to store cache entry: {e}")
```

## AutonomyMetrics Integration

### Extended AutonomySnapshot
```python
@dataclass
class AutonomySnapshot:
    # ... existing fields ...
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    cache_tokens_saved: int = 0
    cache_cost_saved: float = 0.0
```

### route_type Extension
```python
# In AutonomyMetrics.record_routing_decision()
# Existing route_types: 'local', 'cloud', 'split'
# New route_type: 'cache'
# When route_type='cache': tokens_saved tracked, cost_saved tracked
```

## Settings UI Integration

### Electron Settings (AI Features section)
```
[x] Enable Semantic Cache
    Similarity Threshold: [====|======] 0.92
    [Clear Cache] (42 entries, 1,234 tokens saved)
```

**Components:**
- Toggle: Enable/disable cache
- Slider: Similarity threshold (0.80 - 0.99, step 0.01)
- Clear button: Calls `DELETE /polly/cache/clear`
- Stats label: Entry count + tokens saved (refreshed on section open)

### API Endpoints
```
GET  /polly/settings/semantic-cache     → current config
PUT  /polly/settings/semantic-cache     → update config
GET  /polly/cache/stats                 → CacheStats JSON
DELETE /polly/cache/clear               → clear all entries
```

## Files to Create/Modify

### New Files
1. `core/semantic_cache.py` (~250 lines)

### Modified Files
1. `core/polly.py` — _init_semantic_cache(), cache check (~L1515), cache store (~L2357), _record_cache_hit(), _format_cache_response()
2. `core/config.py` — Add semantic_cache to DEFAULT_CONFIG
3. `config.yaml` — Add semantic_cache section
4. `core/autonomy_metrics.py` — Extend AutonomySnapshot, add cache stats to get_snapshot()
5. `core/knowledge_writer.py` — Call invalidate_domain() in _save_note()
6. `core/rag.py` — Call clear() after index_notes() / index_codebase()
7. `interfaces/server.py` — GET /polly/cache/stats, DELETE /polly/cache/clear
8. `interfaces/settings_api.py` — GET/PUT /polly/settings/semantic-cache
9. `electron-app/src/renderer/index.html` — Cache settings UI
10. `electron-app/src/renderer/app.js` — Cache settings JS

### Unchanged Files (Important!)
- `core/router.py` — NO changes (Router V1)
- `libs/polly-routing/` — NO changes (Router V2)
- `core/rag.py` collections — NO changes to existing RAG collections
- `core/budget_manager.py` — NO changes (budget tracking unchanged)
- `core/query_decomposition.py` — NO changes (Wave 3 pipeline)
- `core/split_router.py` — NO changes

## Edge Cases

### 1. Ollama Down
**Scenario:** Embedding model unavailable when cache check is attempted.
**Handling:** `embed_text()` fails → catch exception → treat as cache miss → log warning → pipeline continues normally.

### 2. Conversation-Dependent Queries
**Scenario:** User says "tell me more about that" — depends on conversation history.
**Handling:** Queries with conversation history length > 1 are not cached and not checked against cache. The `is_conversation_dependent` flag is set when conversation context is present.

### 3. Stale Cache After Knowledge Update
**Scenario:** User saves a note, then asks a question the note would affect.
**Handling:** KnowledgeWriter calls `invalidate_domain()` after every successful write. RAG reindex calls `clear()`. Both are synchronous and complete before the next query can check cache.

### 4. Persona Change Mid-Session
**Scenario:** User switches persona; cached responses from previous persona shouldn't match.
**Handling:** Persona is part of the metadata filter. A cache entry stored under "Architect" will never match a query made under "Scribe".

### 5. ChromaDB Collection Corruption
**Scenario:** ChromaDB data corrupted or missing.
**Handling:** `get_or_create_collection()` handles missing collection. If query/upsert fails, catch exception → treat as miss/skip store → log error. Cache is non-critical; failure is always graceful.

### 6. Very Short Queries
**Scenario:** "hi" or "thanks" — too short for meaningful semantic matching.
**Handling:** `min_query_length` config (default: 10 chars). Queries shorter than this skip cache check entirely.

## Testing Strategy

### Unit Tests
1. Cache check returns CacheResult for similar query (similarity > threshold)
2. Cache check returns None for dissimilar query
3. Cache check returns None for same query but different domain
4. Cache store creates entries in both ChromaDB and SQLite
5. Invalidate_domain removes only entries for that domain
6. Clear removes all entries
7. TTL expiry works (entries past TTL not returned)
8. FIFO eviction works (oldest removed when max_entries exceeded)
9. CacheStats calculations correct

### Integration Tests
1. Full query pipeline with cache miss → store → cache hit flow
2. Knowledge write triggers domain invalidation
3. RAG reindex triggers full clear
4. Settings UI toggle enables/disables cache
5. Stats endpoint returns accurate numbers

## Success Metrics

1. Cache hit rate > 10% within first week of usage
2. Sub-100ms response time for cache hits
3. Zero pipeline regressions (cache miss path unchanged)
4. Token savings visible in AutonomyMetrics dashboard
5. No data loss on cache corruption (graceful fallback)
6. Settings UI functional (toggle, threshold, clear, stats)
