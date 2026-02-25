# Tasks: Semantic Response Cache Implementation

## Overview
Ordered implementation steps for adding a system-wide semantic response cache to Polly.

**Principle:** Backend changes before frontend. Core module first, then pipeline integration, then settings UI.

**Estimated scope:** ~450 lines across 12 files (1 new, 11 modified)

---

## Task 1: Add Configuration
**Goal:** Add semantic cache config to config.yaml and core/config.py

### Subtasks:
1. Add `semantic_cache` section to `config.yaml`:
   ```yaml
   semantic_cache:
     enabled: true
     similarity_threshold: 0.92
     ttl_hours: 24
     max_entries: 500
     min_query_length: 10
     cache_cloud_only: true
   ```

2. Add `semantic_cache` to `DEFAULT_CONFIG` in `core/config.py`:
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

### Files:
- `config.yaml`
- `core/config.py`

### Validation:
- [ ] Config loads without errors
- [ ] Default values accessible via `config.get("semantic_cache")`
- [ ] Missing config section falls back to defaults gracefully

---

## Task 2: Create SemanticCache Module
**Goal:** Implement core `SemanticCache` class with singleton pattern

**File:** `core/semantic_cache.py` (~250 lines)

### Subtasks:
1. **Module-level singleton pattern:**
   ```python
   _instance: Optional['SemanticCache'] = None
   
   def init_semantic_cache(chroma_client, embed_fn, db_path, config) -> 'SemanticCache':
       global _instance
       _instance = SemanticCache(chroma_client, embed_fn, db_path, config)
       return _instance
   
   def get_semantic_cache() -> Optional['SemanticCache']:
       return _instance
   ```

2. **CacheResult and CacheStats dataclasses:**
   - CacheResult: response_text, original_query, similarity, domain, persona, model_used, tokens_saved_in, tokens_saved_out, cached_at, cache_id
   - CacheStats: total_entries, hits, misses, hit_rate, total_tokens_saved, estimated_cost_saved, oldest_entry_age_hours

3. **SemanticCache.__init__():**
   - Accept chroma_client, embed_fn, db_path, config
   - Create ChromaDB collection via `get_or_create_collection("semantic_cache", metadata={"hnsw:space": "cosine"})`
   - Open SQLite connection to db_path
   - Call `_ensure_table()` to create cached_responses table
   - Store config values (threshold, ttl, max_entries, min_query_length)
   - Initialize hit/miss counters

4. **SemanticCache._ensure_table():**
   - CREATE TABLE IF NOT EXISTS cached_responses (cache_id, query_text, response_text, domain, persona, mode, model_used, tokens_in, tokens_out, cost, created_at, last_hit_at, hit_count)
   - CREATE INDEX on domain, created_at

5. **SemanticCache.check(query, domain, persona, mode):**
   - Return None if len(query) < min_query_length
   - Embed query via embed_fn
   - Query ChromaDB with metadata filter {domain, persona, mode}, n_results=1
   - If no results or distance > (1 - threshold): increment miss counter, return None
   - Fetch full response from SQLite by cache_id
   - Check TTL (if expired, delete entry, return None)
   - Update last_hit_at and hit_count in SQLite
   - Increment hit counter
   - Return CacheResult

6. **SemanticCache.store(query, response_text, domain, persona, mode, model_used, tokens_in, tokens_out, cost):**
   - Embed query via embed_fn
   - Generate UUID cache_id
   - INSERT into SQLite cached_responses
   - Upsert into ChromaDB (id, embedding, document=query[:2000], metadata)
   - Call _evict_if_needed()
   - Return cache_id

7. **SemanticCache.invalidate_domain(domain):**
   - ChromaDB get(where={"domain": domain}) → get ids
   - ChromaDB delete(ids=ids)
   - SQLite DELETE WHERE cache_id IN (ids)
   - Return count

8. **SemanticCache.clear():**
   - Delete all from ChromaDB collection (delete collection + recreate)
   - SQLite DELETE FROM cached_responses
   - Reset hit/miss counters
   - Return count

9. **SemanticCache.get_stats():**
   - Query SQLite for total_entries, sum(tokens_in + tokens_out) as total_tokens_saved, sum(cost), min(created_at)
   - Combine with in-memory hit/miss counters
   - Return CacheStats

10. **SemanticCache._evict_if_needed():**
    - SELECT count(*) FROM cached_responses
    - If > max_entries: SELECT cache_id ORDER BY created_at ASC LIMIT (count - max_entries)
    - Delete from ChromaDB and SQLite

11. **SemanticCache._cleanup_expired():**
    - Calculate cutoff = time.time() - (ttl_hours * 3600)
    - SELECT cache_id FROM cached_responses WHERE created_at < cutoff
    - Delete from ChromaDB and SQLite

### Validation:
- [ ] Singleton init/get pattern works
- [ ] ChromaDB collection created with cosine space
- [ ] SQLite table created with correct schema
- [ ] check() returns CacheResult for similar query above threshold
- [ ] check() returns None for dissimilar query
- [ ] check() returns None for same query but different domain/persona
- [ ] store() creates entries in both ChromaDB and SQLite
- [ ] invalidate_domain() removes only domain-specific entries
- [ ] clear() removes all entries
- [ ] TTL enforcement works
- [ ] FIFO eviction works
- [ ] All exceptions caught gracefully (cache is non-critical)

---

## Task 3: Integrate Cache into Polly Init Sequence
**Goal:** Add `_init_semantic_cache()` to Polly.__init__ between RAG and router

**File:** `core/polly.py`

### Subtasks:
1. Add `_init_semantic_cache()` method:
   - Import `init_semantic_cache` from `core.semantic_cache`
   - Get cache config from `self.config`
   - If enabled: call `init_semantic_cache(rag.chroma_client, rag.embed_text, db_path, config)`
   - Wrap in try/except (cache failure should not prevent startup)

2. Call `_init_semantic_cache()` in `__init__` between RAG init (~L69) and router init (~L74)

### Files:
- `core/polly.py`

### Validation:
- [ ] Cache initializes when enabled in config
- [ ] Cache skipped when disabled in config
- [ ] Polly starts normally if cache init fails
- [ ] Log messages confirm init success/skip/failure

---

## Task 4: Add Cache Check to Query Pipeline
**Goal:** Check cache after domain detection, return cached response on hit

**File:** `core/polly.py`

### Subtasks:
1. After domain detection (~L1514), add cache check block:
   - Get semantic cache via `get_semantic_cache()`
   - If cache exists and enabled: call `cache.check(query, domain, persona, mode)`
   - On hit: record cache hit in autonomy metrics, format and return response immediately

2. Add `_format_cache_response(cache_result)` helper method:
   - Build response dict matching normal pipeline output format
   - Include `"cache_hit": True`, `"cache_similarity": result.similarity` in metadata
   - Include `"provider": "cache"` or `"provider": result.model_used + " (cached)"`

3. Add `_record_cache_hit(cache_result)` helper method:
   - Record routing decision with route_type='cache' in AutonomyMetrics
   - Log cache hit with similarity score

### Files:
- `core/polly.py`

### Validation:
- [ ] Cache check runs after domain detection
- [ ] Cache hit returns response immediately (skips rest of pipeline)
- [ ] Cache miss continues pipeline normally
- [ ] Cache hit response format matches normal response format
- [ ] Autonomy metrics records cache hit

---

## Task 5: Add Cache Store to Post-Processing
**Goal:** Store successful cloud responses in cache after completion

**File:** `core/polly.py`

### Subtasks:
1. In post-processing block (~L2357), add cache store logic:
   - Only store if cache enabled AND route_type is cloud AND not conversation-dependent
   - Get semantic cache, call `cache.store(...)` with query, response, metadata
   - Wrap in try/except (store failure should not affect response delivery)

2. Determine `is_conversation_dependent`:
   - Check if conversation history length > 1 (i.e., messages beyond the current query)
   - If yes, skip cache store

### Files:
- `core/polly.py`

### Validation:
- [ ] Cloud responses stored in cache
- [ ] Local (Ollama) responses NOT stored
- [ ] Conversation-dependent queries NOT stored
- [ ] Store failure does not affect response delivery
- [ ] Stored entries retrievable via subsequent cache check

---

## Task 6: Add Cache Invalidation Hooks
**Goal:** Invalidate cache entries when underlying knowledge changes

### Subtasks:
1. **KnowledgeWriter invalidation** (`core/knowledge_writer.py`):
   - In `_save_note()`, after successful write, call `get_semantic_cache().invalidate_domain(domain)`
   - Wrap in try/except (invalidation failure should not affect knowledge write)
   - Log invalidation count

2. **RAG reindex invalidation** (`core/rag.py`):
   - After `index_notes()` completes, call `get_semantic_cache().clear()`
   - After `index_codebase()` completes, call `get_semantic_cache().clear()`
   - Wrap in try/except
   - Log clear operation

### Files:
- `core/knowledge_writer.py`
- `core/rag.py`

### Validation:
- [ ] Knowledge write triggers domain invalidation
- [ ] RAG reindex triggers full cache clear
- [ ] Invalidation/clear failures do not affect primary operations
- [ ] Log messages confirm invalidation actions

---

## Task 7: Extend AutonomyMetrics
**Goal:** Add cache statistics to AutonomySnapshot and get_snapshot()

**File:** `core/autonomy_metrics.py`

### Subtasks:
1. Add cache fields to `AutonomySnapshot` dataclass:
   ```python
   cache_hits: int = 0
   cache_misses: int = 0
   cache_hit_rate: float = 0.0
   cache_tokens_saved: int = 0
   cache_cost_saved: float = 0.0
   ```

2. Update `get_snapshot()` to query cache stats:
   - Import `get_semantic_cache` from `core.semantic_cache`
   - If cache exists, call `cache.get_stats()` and populate snapshot fields
   - Wrap in try/except (cache unavailable should not break metrics)

3. Accept `route_type='cache'` in `record_routing_decision()`:
   - Ensure existing logic handles the new route_type gracefully

### Files:
- `core/autonomy_metrics.py`

### Validation:
- [ ] AutonomySnapshot includes cache fields
- [ ] get_snapshot() returns cache stats when cache is active
- [ ] get_snapshot() returns zero cache stats when cache is inactive
- [ ] route_type='cache' recorded correctly in routing_decisions table

---

## Task 8: Add Server API Endpoints
**Goal:** Add cache stats and clear endpoints to FastAPI server

### Subtasks:
1. **Stats endpoint** (`interfaces/server.py`):
   ```python
   @app.get("/polly/cache/stats")
   async def get_cache_stats():
       cache = get_semantic_cache()
       if not cache:
           return {"error": "Cache not initialized"}
       stats = cache.get_stats()
       return asdict(stats)
   ```

2. **Clear endpoint** (`interfaces/server.py`):
   ```python
   @app.delete("/polly/cache/clear")
   async def clear_cache():
       cache = get_semantic_cache()
       if not cache:
           return {"error": "Cache not initialized"}
       count = cache.clear()
       return {"cleared": count}
   ```

3. **Settings endpoints** (`interfaces/settings_api.py`):
   ```python
   @app.get("/polly/settings/semantic-cache")
   async def get_cache_settings():
       return config.get("semantic_cache", {})
   
   @app.put("/polly/settings/semantic-cache")
   async def update_cache_settings(settings: dict):
       # Validate and save to config
       # Reinitialize cache if threshold/ttl changed
   ```

### Files:
- `interfaces/server.py`
- `interfaces/settings_api.py`

### Validation:
- [ ] GET /polly/cache/stats returns CacheStats JSON
- [ ] DELETE /polly/cache/clear empties the cache
- [ ] GET /polly/settings/semantic-cache returns current config
- [ ] PUT /polly/settings/semantic-cache updates config
- [ ] All endpoints handle cache-not-initialized gracefully

---

## Task 9: Add Settings UI
**Goal:** Add cache controls to Electron settings in AI Features section

### Subtasks:
1. **HTML** (`electron-app/src/renderer/index.html`):
   - Add to AI Features section:
     - Toggle: "Enable Semantic Cache" (checkbox)
     - Slider: "Similarity Threshold" (0.80-0.99, step 0.01, shows value)
     - Button: "Clear Cache"
     - Stats label: "{n} entries, {tokens} tokens saved"

2. **JavaScript** (`electron-app/src/renderer/app.js`):
   - `loadCacheSettings()`: GET /polly/settings/semantic-cache → populate UI
   - `saveCacheSettings()`: Read UI values → PUT /polly/settings/semantic-cache
   - `clearCache()`: DELETE /polly/cache/clear → update stats label
   - `refreshCacheStats()`: GET /polly/cache/stats → update stats label
   - Wire up event listeners for toggle, slider, clear button
   - Refresh stats when AI Features section is expanded

### Files:
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/app.js`

### Validation:
- [ ] Toggle enables/disables cache
- [ ] Slider adjusts threshold with live value display
- [ ] Clear button empties cache and updates stats
- [ ] Stats label shows current entry count and tokens saved
- [ ] Settings persist across app restart

---

## Task 10: Add Cache Hit Indicator to Chat UI
**Goal:** Show subtle indicator when response was served from cache

### Subtasks:
1. In the chat message rendering logic, detect `cache_hit: true` in response metadata
2. Display "Served from cache" in the provider/model info area (where it shows "via Anthropic" etc.)
3. Optionally show similarity score: "Served from cache (96% match)"
4. Use muted/subtle styling (not a banner or alert)

### Files:
- `electron-app/src/renderer/app.js` (message rendering)
- `electron-app/src/renderer/index.html` (if CSS needed)

### Validation:
- [ ] Cache hits show "Served from cache" indicator
- [ ] Normal responses show provider name as usual
- [ ] Indicator styling is subtle and non-intrusive

---

## Task 11: Testing — Core Cache Operations
**Goal:** Verify cache check/store/invalidate/clear work correctly

### Test Cases:
1. **Store and retrieve:**
   - Store a query-response pair
   - Check with identical query → should return CacheResult
   - Verify response_text matches

2. **Semantic similarity:**
   - Store "What is the weather today?"
   - Check "How's the weather right now?" → should hit (similar meaning)
   - Check "Explain quantum computing" → should miss (different topic)

3. **Metadata filtering:**
   - Store entry with domain="sigils", persona="Architect"
   - Check same query with domain="scrolls" → should miss
   - Check same query with persona="Scribe" → should miss
   - Check same query with domain="sigils", persona="Architect" → should hit

4. **TTL enforcement:**
   - Store entry with created_at = (now - ttl - 1 hour)
   - Check → should miss (expired)

5. **FIFO eviction:**
   - Set max_entries=3
   - Store 4 entries
   - Verify oldest entry evicted, newest 3 remain

6. **Domain invalidation:**
   - Store entries in "sigils" and "scrolls"
   - Invalidate "sigils"
   - Verify "sigils" entries gone, "scrolls" entries remain

7. **Full clear:**
   - Store multiple entries
   - Clear all
   - Verify both ChromaDB and SQLite empty

### Validation:
- [ ] All test cases pass
- [ ] No data leaks between ChromaDB and SQLite
- [ ] Counters (hits, misses) accurate

---

## Task 12: Testing — Pipeline Integration
**Goal:** End-to-end test of cache in the query pipeline

### Test Cases:
1. **Cache miss → store → cache hit flow:**
   - Send query → should be cache miss → full pipeline → response stored
   - Send same query → should be cache hit → fast response
   - Verify hit response matches original

2. **Conversation-dependent skip:**
   - Send query with conversation history → should NOT be cached

3. **Local route skip:**
   - Send query routed to Ollama → should NOT be cached

4. **Knowledge write invalidation:**
   - Cache a response in "sigils" domain
   - Write knowledge in "sigils" domain
   - Check same query → should miss (invalidated)

5. **RAG reindex clear:**
   - Cache multiple responses
   - Trigger notes reindex
   - Verify all cache entries cleared

6. **Settings toggle:**
   - Disable cache in settings
   - Send query → should NOT check cache
   - Enable cache → should resume caching

### Validation:
- [ ] Full cache lifecycle works end-to-end
- [ ] Cache does not interfere with normal pipeline
- [ ] Invalidation triggers work in real pipeline context
- [ ] Settings changes take effect immediately

---

## Task 13: Testing — Edge Cases
**Goal:** Verify graceful handling of failure scenarios

### Test Cases:
1. **Ollama down (embedding unavailable):**
   - Stop Ollama
   - Send query → should gracefully skip cache, continue pipeline
   - Start Ollama → cache should resume working

2. **ChromaDB corruption:**
   - Delete cache collection
   - Send query → should recreate collection or skip gracefully

3. **SQLite locked:**
   - Simulate concurrent access → should handle with retry or skip

4. **Very short query:**
   - Send "hi" (below min_query_length) → should skip cache

5. **Empty response:**
   - Ensure empty LLM responses are NOT cached

6. **Cache at capacity:**
   - Fill to max_entries → verify FIFO eviction works on next store

### Validation:
- [ ] All failure modes handled gracefully
- [ ] No crashes or data corruption
- [ ] Log warnings for all error paths
- [ ] Pipeline continues normally on any cache failure

---

## Task 14: Documentation & Specs Update
**Goal:** Update relevant OpenSpec docs to reflect new feature

### Subtasks:
1. Update `openspec/specs/architecture/spec.md`:
   - Add semantic cache to system architecture diagram
   - Document cache layer in query pipeline

2. Update `openspec/specs/project/status.md`:
   - Add semantic response cache as completed feature

3. Add entry to `docs/status/CHANGELOG.md`:
   ```markdown
   ## YYYY-MM-DD - Semantic Response Cache (Phase 0)
   - Added system-wide semantic response cache
   - ChromaDB-backed query similarity matching
   - SQLite sidecar for full response storage
   - Event-driven cache invalidation (knowledge writes, RAG reindex)
   - Cache stats in AutonomyMetrics dashboard
   - Settings UI with toggle, threshold slider, clear button
   ```

4. Archive `openspec/changes/semantic-response-cache/`

### Validation:
- [ ] All specs updated
- [ ] Changelog entry added
- [ ] Change folder archived

---

## Task 15: Final Validation
**Goal:** Comprehensive end-to-end testing

### Test Scenarios:
1. **Normal operation:**
   - [ ] Cache initializes on startup
   - [ ] First query: cache miss → full pipeline → response cached
   - [ ] Second similar query: cache hit → fast response
   - [ ] Different query: cache miss → normal pipeline

2. **Settings:**
   - [ ] Toggle on/off works
   - [ ] Threshold slider adjusts matching sensitivity
   - [ ] Clear button empties cache
   - [ ] Stats label updates

3. **Invalidation:**
   - [ ] Knowledge write invalidates domain entries
   - [ ] RAG reindex clears all entries

4. **Metrics:**
   - [ ] AutonomySnapshot shows cache stats
   - [ ] route_type='cache' appears in routing_decisions
   - [ ] Tokens saved tracked accurately

5. **Resilience:**
   - [ ] Cache failure doesn't break queries
   - [ ] Ollama down → graceful fallback
   - [ ] Config missing → defaults applied

### Success Criteria:
- All cloud-routed, single-turn queries cached on completion
- Cache hits return in <100ms
- Zero regressions to existing pipeline
- Token savings visible in metrics
- Settings UI fully functional
- All failure modes graceful

---

## Rollout Plan

### Immediate (Implementation):
- [ ] Implement Tasks 1-10
- [ ] Test Tasks 11-13
- [ ] Document Task 14
- [ ] Validate Task 15
- Default: `enabled: true` (cache is non-intrusive, failures are graceful)

### Post-Launch Tuning:
- [ ] Monitor cache hit rate for first week
- [ ] Adjust similarity_threshold based on false positive/negative rates
- [ ] Adjust ttl_hours based on knowledge update frequency
- [ ] Adjust max_entries based on storage usage

### Future Phases:
- **Phase 1 (Context Distillation):** Cache compressed context to avoid re-compressing identical code blocks
- **Phase 2 (Copilot FIM):** Cache frequently requested completions for the same code patterns
- **Phase 3 (Programmer Persona):** Persona-specific cache partitioning for code operations

---

## Dependency Order

```
Task 1 (Config)
    ↓
Task 2 (Core Module)
    ↓
Task 3 (Init Integration)
    ↓
Task 4 (Cache Check) ──→ Task 5 (Cache Store)
    ↓                        ↓
Task 6 (Invalidation Hooks)  │
    ↓                        ↓
Task 7 (AutonomyMetrics) ←───┘
    ↓
Task 8 (Server Endpoints)
    ↓
Task 9 (Settings UI) ──→ Task 10 (Cache Hit Indicator)
    ↓
Tasks 11-13 (Testing)
    ↓
Task 14 (Docs)
    ↓
Task 15 (Final Validation)
```

Tasks 4 and 5 can be implemented in parallel. Tasks 11-13 can run in parallel.
