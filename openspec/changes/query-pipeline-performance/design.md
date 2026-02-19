# Query Pipeline Performance Optimizations — Design

## Current Performance Profile

Measured timing breakdown for a steady-state query (warm Ollama, indexed RAG):

```
RAG search:              0.3-1.6s  (warm/cold)
_gather_context:         3.4-6.6s  (3 sequential Mem0 embedding calls via Ollama)
Wave3/routing/etc:       0.0s      (all fast, in-memory)
LLM first token:         1.1-1.7s  (GPT-4o via GitHub Models)
Streaming:               varies    (depends on response length)
Post-yield (inline):     ~0s       (conversation history + rolling context)
Background tasks:        ~30-40s   (fire-and-forget, doesn't block response)
```

The dominant bottleneck is `_gather_context` at 3.4-6.6s, which is almost entirely 3 sequential
Mem0 `search()` calls, each requiring an Ollama embedding round-trip (~2s each).

## Optimization 1: Parallelize Memory Tier Searches

### Problem

`MemoryRetriever.retrieve()` (`core/memory/retriever.py:124-199`) queries three tiers sequentially:

```python
# Current: ~6s total (3 × ~2s each)
stable_results = self.store.read(query, tier=MemoryTier.STABLE, ...)    # ~2s
episodic_results = self.store.read(query, tier=MemoryTier.EPISODIC, ...) # ~2s
working_results = self.store.read(query, tier=MemoryTier.WORKING, ...)   # ~2s
```

Each `read()` call goes through Mem0 → ChromaDB → Ollama (for embedding). The three tiers are
independent namespaces with no cross-dependencies.

### Approach

Use `concurrent.futures.ThreadPoolExecutor` to run all three searches in parallel:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def retrieve(self, query, domains=None, limit=10, ...):
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(self.store.read, query, tier=MemoryTier.STABLE, ...): "stable",
            pool.submit(self.store.read, query, tier=MemoryTier.EPISODIC, ...): "episodic",
            pool.submit(self.store.read, query, tier=MemoryTier.WORKING, ...): "working",
        }
        results = {}
        for future in as_completed(futures):
            tier_name = futures[future]
            results[tier_name] = future.result()

    all_entries = results["stable"] + results["episodic"] + results["working"]
    return self._deduplicate_across_tiers(all_entries)
```

**Expected improvement:** 6s → ~2.5s (limited by the slowest single search + thread overhead).

**Concern — Ollama contention:** All three searches embed simultaneously through the same Ollama
instance. If Ollama serializes embedding requests internally, parallelization may not help. Need to
measure. If Ollama does serialize, the alternative is a single Mem0 search across all tiers with
post-filtering (requires Mem0 API investigation).

### Files Changed

- `core/memory/retriever.py` — `retrieve()` method rewritten with thread pool

---

## Optimization 2: Embedding Cache

### Problem

Every `_gather_context()` call embeds the query through Ollama to search Mem0, even if the same or
similar query was just asked. Follow-up questions in a conversation often share substantial semantic
overlap with previous queries.

### Approach

Add an LRU cache keyed on (query_text, tier, limit) that stores Mem0 search results:

```python
from functools import lru_cache
from hashlib import sha256
import time

class CachedMemoryRetriever(MemoryRetriever):
    """MemoryRetriever with short-lived result caching."""

    def __init__(self, *args, cache_ttl: int = 300, cache_size: int = 64, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache: Dict[str, Tuple[float, List[MemoryEntry]]] = {}
        self._cache_ttl = cache_ttl  # seconds
        self._cache_size = cache_size

    def _cache_key(self, query: str, tier: str, limit: int) -> str:
        return sha256(f"{query}:{tier}:{limit}".encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[List[MemoryEntry]]:
        if key in self._cache:
            ts, results = self._cache[key]
            if time.monotonic() - ts < self._cache_ttl:
                return results
            del self._cache[key]
        return None

    def _put_cache(self, key: str, results: List[MemoryEntry]):
        if len(self._cache) >= self._cache_size:
            # Evict oldest entry
            oldest = min(self._cache, key=lambda k: self._cache[k][0])
            del self._cache[oldest]
        self._cache[key] = (time.monotonic(), results)
```

**Cache invalidation:** Clear cache entries for a tier when new memories are written to that tier.
The `TieredMemoryStore.write()` method should call `retriever.invalidate(tier)`.

**Expected improvement:** Follow-up queries in the same topic go from ~6s to ~0.01s for the
memory retrieval portion. First query in a new topic is unchanged.

### Files Changed

- `core/memory/retriever.py` — Add caching layer (subclass or mixin)
- `core/memory/tiers.py` — `write()` triggers cache invalidation on the retriever

---

## Optimization 3: Ollama Model Warm-Up

### Problem

Ollama lazy-loads models into GPU/CPU memory on first use. The first query after server startup
pays an additional ~5-10s penalty for model loading. Currently, `_init_router()` explicitly skips
the availability check (`polly.py:184`: "Skip availability check at init to avoid blocking/hanging").

### Approach

After all init steps complete, fire a lightweight background warm-up request:

```python
# In interfaces/server.py, after app startup
@app.on_event("startup")
async def warmup_ollama():
    """Warm up Ollama models by sending a trivial request."""
    import asyncio
    async def _warmup():
        try:
            import aiohttp
            ollama_url = "http://localhost:11434/api/generate"
            # Minimal generate to force model load
            async with aiohttp.ClientSession() as session:
                await session.post(ollama_url, json={
                    "model": "qwen2.5:7b",
                    "prompt": "hi",
                    "options": {"num_predict": 1}
                }, timeout=aiohttp.ClientTimeout(total=30))
            # Also warm up embedding model
            embed_url = "http://localhost:11434/api/embeddings"
            async with aiohttp.ClientSession() as session:
                await session.post(embed_url, json={
                    "model": "nomic-embed-text:latest",
                    "prompt": "warmup"
                }, timeout=aiohttp.ClientTimeout(total=30))
            logger.info("Ollama models warmed up")
        except Exception as e:
            logger.warning(f"Ollama warm-up failed (non-blocking): {e}")
    # Fire and forget — don't block server startup
    asyncio.create_task(_warmup())
```

**Expected improvement:** First-query latency drops from ~12-15s to ~7-10s (same as steady-state).
Server startup is not blocked — warm-up runs in the background.

### Files Changed

- `interfaces/server.py` — Add `startup` event handler
- `config/config.yaml` — Optional `warmup.enabled` flag

---

## Optimization 4: Parallel `__init__` Steps

### Problem

`Polly.__init__()` (`core/polly.py:44-136`) runs 13 initialization steps sequentially. Total init
time is ~4-6s. Many steps are independent:

```
Independent groups:
  Group A: _init_domains, _init_rag, _init_dedup
  Group B: _init_learners, _init_mental_models, _init_skills
  Group C: _init_notes_sync (independent, I/O-bound)

Sequential dependencies:
  _init_router → _init_wave3_pipeline (wave3 needs router_v2)
  _init_router → _init_memory_context (memory retriever needs config from router)
  _init_compression → _init_personas (personas may use compression)
  _init_rag → _init_knowledge_writer (knowledge writer needs RAG)
```

### Approach

Use `asyncio.gather()` for independent groups, preserving sequential order for dependent steps:

```python
async def _init_async(self):
    # Phase 1: Independent I/O-bound init steps
    await asyncio.gather(
        asyncio.to_thread(self._init_domains),
        asyncio.to_thread(self._init_rag),
        asyncio.to_thread(self._init_dedup),
        asyncio.to_thread(self._init_learners),
        asyncio.to_thread(self._init_notes_sync),
    )
    # Phase 2: Steps depending on Phase 1
    await asyncio.gather(
        asyncio.to_thread(self._init_router),
        asyncio.to_thread(self._init_compression),
        asyncio.to_thread(self._init_mental_models),
        asyncio.to_thread(self._init_skills),
    )
    # Phase 3: Steps depending on Phase 2
    await asyncio.gather(
        asyncio.to_thread(self._init_wave3_pipeline),
        asyncio.to_thread(self._init_personas),
        asyncio.to_thread(self._init_knowledge_writer),
        asyncio.to_thread(self._init_memory_context),
    )
```

**Risk:** Hidden shared state between init steps. Requires careful analysis of which steps read or
mutate instance variables set by other steps. Need thorough testing.

**Expected improvement:** Init time drops from ~4-6s to ~2-3s (limited by the slowest step in each
phase).

### Files Changed

- `core/polly.py` — `__init__` refactored, new `_init_async()` method
- `interfaces/server.py` — Call `await polly._init_async()` during startup

---

## Optimization 5: Batch Entity Extraction

### Problem

`_post_response_background()` calls `extract_and_store()` twice:

```python
# core/polly.py:2627-2633
self.entity_extractor.extract_and_store(query, "query", source_id, domain_ids)
self.entity_extractor.extract_and_store(full_response, "response", source_id, domain_ids)
```

Each call runs the full spaCy NER pipeline (model load check, tokenization, NER, noun chunk
extraction). The spaCy `nlp()` call is the expensive part (~1-3s per text). Processing both texts
in a single `nlp.pipe()` batch would be faster.

### Approach

Add a `batch_extract_and_store()` method to `EntityExtractor`:

```python
def batch_extract_and_store(
    self,
    items: List[Tuple[str, str]],  # (text, source_type) pairs
    source_id: str,
    domains: Optional[List[str]] = None,
) -> List[Entity]:
    """Extract entities from multiple texts in one spaCy pipeline pass."""
    self._ensure_nlp()
    texts = [text for text, _ in items]
    all_entities = []

    # Process all texts in one pipe() call
    for doc, (text, source_type) in zip(self.nlp.pipe(texts), items):
        entities = self._extract_from_doc(doc, text, source_type, domains)
        all_entities.extend(entities)

    # Deduplicate and store
    unique = self._deduplicate(all_entities)
    self._store_entities(unique, source_id, domains)
    return unique
```

**Expected improvement:** Background thread entity extraction drops from ~11s to ~6-7s.

### Files Changed

- `core/entities/extractor.py` — Add `batch_extract_and_store()`, refactor `_extract_from_doc()`
- `core/polly.py` — `_post_response_background()` uses batch method

---

## Optimization 6: Pattern Engine Backend Consolidation

### Problem

`PatternEngine.learn()` (`core/patterns/engine.py:121-179`) saves to two backends:
- **JSON backend** — In-memory + file persistence. Fast (~1ms).
- **Mem0 backend** — Embedding + LLM extraction + ChromaDB write. Slow (~25s).

The Mem0 backend is already skipped for `ROUTING_OUTCOME` patterns (the most common type). For the
remaining pattern types (`QUERY_DOMAIN`, `TOOL_USAGE`, `ERROR_RECOVERY`), the Mem0 semantic search
capability is rarely used — patterns are typically searched by type and confidence threshold, which
the JSON backend handles efficiently.

### Approach

1. **Audit Mem0 pattern searches:** Grep for `mem0_backend.search()` calls and evaluate whether
   the semantic search capability is actually used vs. simple type+confidence filtering.
2. **If unused:** Remove Mem0 backend from pattern engine entirely. Keep JSON-only.
3. **If partially used:** Make Mem0 save async/deferred (batch at session end) rather than per-pattern.

### Decision Criteria

- If `mem0_backend.search()` is called <5 times in the codebase and all calls could be served by
  JSON backend filtering → remove Mem0 backend.
- If semantic search over patterns provides measurable routing quality improvement → keep but batch.

### Files Changed

- `core/patterns/engine.py` — Remove or batch Mem0 backend calls
- `core/patterns/storage/mem0_backend.py` — Potential removal or demotion to optional

---

## Summary of Expected Impact

| Optimization | Current | Target | Effort |
|-------------|---------|--------|--------|
| 1. Parallel tier searches | ~6s | ~2.5s | Small |
| 2. Embedding cache | ~6s (repeat) | ~0s (repeat) | Small |
| 3. Ollama warm-up | +5-10s first query | +0s first query | Trivial |
| 4. Parallel init | ~4-6s startup | ~2-3s startup | Medium |
| 5. Batch entity extraction | ~11s background | ~6-7s background | Small |
| 6. Backend consolidation | ~25s background | ~0s background | Small-Medium |

Combined steady-state improvement: **~7-10s → ~2-3s** first-token latency.

## Testing Strategy

- **Benchmarks:** Add a `scripts/benchmark_query.py` that measures first-token latency across
  10 queries (first cold, then warm). Run before and after each optimization.
- **Unit tests:** Each optimization gets targeted tests (parallel retriever, cache hit/miss/invalidation,
  batch extraction correctness).
- **Integration:** Existing 114 tests must continue passing.
- **Manual QA:** Verify streaming UX is not degraded by parallel work.
