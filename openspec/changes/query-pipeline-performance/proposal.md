# Query Pipeline Performance Optimizations

## What

Reduce Polly's query-to-first-token latency from the current ~7-10s steady-state down to ~2-3s through parallelization, caching, warm-up, and consolidation of the hot path.

## Why

After the initial performance fix (commit `5381ae8`) that moved blocking work off the event loop and deferred post-response tasks to background threads, response time dropped from ~55s to ~7-17s. This was a critical fix, but the remaining ~7-10s steady-state latency is still dominated by a few identifiable bottlenecks that can be addressed with targeted optimizations:

1. **Sequential Mem0 tier searches (~6s):** The `MemoryRetriever.retrieve()` method queries stable, episodic, and working tiers one after another. Each search requires an Ollama embedding call (~2s each). These are independent queries against independent tier namespaces and can run concurrently.

2. **No embedding cache:** Identical or near-identical queries re-embed through Ollama every time. Short-term caching of embedding vectors would eliminate redundant compute for follow-up questions and repeated queries within a session.

3. **Cold-start penalty on first query:** Ollama models are not loaded into memory until first use. The first query pays a ~5-10s penalty for model loading on top of the normal latency. A startup warm-up ping would shift this cost to server boot time.

4. **Sequential `__init__` steps:** All 13 initialization steps in `Polly.__init__()` run sequentially despite many being independent (e.g., domain init, RAG init, router init, mental models init). Parallelizing independent init steps would reduce server startup time.

5. **Duplicate entity extraction:** `extract_and_store()` is called twice in the background thread — once for the query, once for the response. A single call processing both texts together would halve spaCy overhead.

6. **Pattern engine dual-backend overhead:** The pattern engine saves to both JSON and Mem0 backends. The Mem0 backend is already partially disabled (skipped for ROUTING_OUTCOME). Evaluating whether Mem0 adds value for any pattern type could simplify the engine and eliminate a slow write path entirely.

## Scope

### In Scope
- Parallelize `MemoryRetriever.retrieve()` tier searches using `concurrent.futures`
- Add an LRU embedding cache in front of Mem0 search calls
- Add Ollama model warm-up during server startup
- Parallelize independent `__init__` steps
- Batch entity extraction (query + response in one call)
- Evaluate and potentially remove Mem0 backend from pattern engine

### Out of Scope
- Replacing Mem0 as the memory persistence layer (that's a much larger architectural change)
- Reducing `_gather_context` contributor count (the ContextContributor pipeline is architecturally important)
- GPU/hardware-level optimizations for Ollama
- Switching embedding models (nomic-embed-text is already fast; the bottleneck is sequential calls, not per-call speed)
- Response streaming optimizations (LLM streaming is already efficient)

## Impact

| Metric | Current | Target |
|--------|---------|--------|
| Steady-state first-token latency | ~7-10s | ~2-3s |
| Cold-start first query | ~12-15s | ~7-10s (warm-up shifts cost to boot) |
| Server startup time | ~4-6s | ~3-4s (parallel init) |
| Background thread duration | ~30-40s | ~20-25s (batched extraction) |

## Files Affected

- `core/memory/retriever.py` — Parallelize tier searches
- `core/polly.py` — Embedding cache, init parallelization, entity extraction batching, warm-up call
- `core/entities/extractor.py` — Batch extraction method
- `core/patterns/engine.py` — Mem0 backend evaluation
- `interfaces/server.py` — Warm-up trigger on startup
- `core/patterns/storage/mem0_backend.py` — Potential removal or demotion

## Dependencies

- **Scalable Memory Layers** (complete) — This change optimizes the memory retrieval path that was introduced there.
- **Mem0** — The embedding cache sits between our code and Mem0's search API. No changes to Mem0 itself.
- **Ollama** — Warm-up requires a lightweight generate/embed call at startup. Ollama must be running.

## Risks

- **Cache staleness:** Embedding cache could return stale results if memory is updated between queries. Mitigated by short TTL (session-scoped or 5-minute expiry).
- **Ollama warm-up failure:** If Ollama isn't running at startup, the warm-up should fail gracefully without blocking server boot.
- **Thread pool contention:** Parallelizing tier searches with `concurrent.futures.ThreadPoolExecutor` shares the thread pool with other `asyncio.to_thread()` calls. May need a dedicated pool for Mem0 searches.
- **Init parallelization ordering:** Some init steps have hidden dependencies. Need careful analysis of what can truly run in parallel.
