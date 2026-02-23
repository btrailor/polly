# Query Pipeline Performance Optimizations — Tasks

**Priority:** P2 — Quality-of-life improvement (not blocking, but meaningfully improves UX)
**Estimated Effort:** 3-5 days
**Dependencies:** Scalable Memory Layers (complete), routing fixes (complete, commit `5381ae8`)

---

## Phase 1: Measurement Baseline (Task 1)

### Task 1: Create benchmark script

**Goal:** Establish reproducible latency measurements before and after each optimization.

**Steps:**
- [ ] Create `scripts/benchmark_query.py` that:
  - Sends 10 queries to `/polly/query` (non-streaming) via `httpx`
  - Measures wall-clock time per query (total, first-token if streaming)
  - Reports p50, p95, min, max for cold (first query) and warm (subsequent)
  - Outputs results as JSON for comparison
- [ ] Run baseline benchmark and save results to `scripts/benchmark_baseline.json`

**Files:** `scripts/benchmark_query.py` (new)
**Verification:** Script runs and produces reproducible numbers matching ~7-10s steady-state

---

## Phase 2: Hot Path Optimizations (Tasks 2-3)

These target the critical path — `_gather_context` latency that directly affects first-token time.

### Task 2: Parallelize MemoryRetriever tier searches

**Goal:** Run stable/episodic/working tier Mem0 searches concurrently instead of sequentially.

**Steps:**
- [ ] Refactor `MemoryRetriever.retrieve()` at `core/memory/retriever.py:124` to use `concurrent.futures.ThreadPoolExecutor(max_workers=3)`
- [ ] Submit all three `self.store.read()` calls as futures
- [ ] Collect results with `as_completed()`, preserving tier labels
- [ ] Merge + deduplicate as before
- [ ] Add unit test: mock `store.read()` with `time.sleep(1)` per tier, verify total time < 2s
- [ ] Run benchmark — expect `_gather_context` to drop from ~6s to ~2.5s
- [ ] Investigate Ollama serialization: if parallel embedding doesn't help (Ollama queues internally), document finding and evaluate single-search-with-post-filter as alternative

**Files:** `core/memory/retriever.py`
**Verification:** Benchmark shows measurable improvement. 114 existing tests pass.

### Task 3: Add embedding result cache

**Goal:** Cache Mem0 search results for repeated/similar queries within a session.

**Steps:**
- [x] Add `_cache: Dict[str, Tuple[float, List[MemoryEntry]]]` to `MemoryRetriever`
- [x] Cache key: `sha256(f"{query}:{tier}:{limit}")` — exact match only (no fuzzy)
- [x] TTL: 300 seconds (configurable via `config.yaml` at `memory.retrieval.cache_ttl`)
- [x] Max entries: 64 (LRU eviction, configurable via `memory.retrieval.cache_max_entries`)
- [x] Add `invalidate(tier: Optional[MemoryTier] = None)` method
- [x] Wire invalidation: called from `Polly._on_session_end()` after `SessionExtractor.extract_and_store()` completes (no bidirectional coupling to `TieredMemoryStore`)
- [ ] Add unit tests: cache hit, cache miss, TTL expiry, invalidation on write
- [ ] Run benchmark with repeated query — expect near-zero latency on second call

**Files:** `core/memory/retriever.py`, `core/polly.py`
**Verification:** Benchmark shows ~0s memory retrieval for repeated queries. Cache invalidation test passes.

**Implementation note — surgical invalidation available:**
`invalidate()` accepts an optional `tier: MemoryTier` argument. Calling
`memory_retriever.invalidate(MemoryTier.STABLE)` evicts only entries for that
tier, leaving the others warm. This is useful if a future code path writes to
a single tier mid-session (e.g. a promoted working memory or a manual
`TieredMemoryStore.write()` call) and only that tier's cached results need
refreshing. See `core/memory/retriever.py` — `MemoryRetriever.invalidate()`
for the full contract.

---

## Phase 3: Startup Optimizations (Tasks 4-5)

### Task 4: Ollama model warm-up on server start

**Goal:** Eliminate the ~5-10s cold-start penalty on first query by pre-loading Ollama models.

**Steps:**
- [ ] Add `@app.on_event("startup")` handler in `interfaces/server.py`
- [ ] Fire-and-forget `asyncio.create_task()` that sends:
  - `POST /api/generate` with `{"model": "qwen2.5:7b", "prompt": "hi", "options": {"num_predict": 1}}`
  - `POST /api/embeddings` with `{"model": "nomic-embed-text:latest", "prompt": "warmup"}`
- [ ] Read model names from `config.yaml` (`models.local.chat_models` and `models.local.embedding_model`) instead of hardcoding
- [ ] 30s timeout per request, catch all exceptions (Ollama may not be running)
- [ ] Log success/failure at INFO level
- [ ] Add `startup.warmup_ollama: true` flag to `config/config.yaml` (default true)
- [ ] Test: start server, verify first query latency matches steady-state in benchmark

**Files:** `interfaces/server.py`, `config/config.yaml`
**Verification:** First-query benchmark shows no cold-start premium.

### Task 5: Parallelize independent `__init__` steps

**Goal:** Reduce server startup time by running independent init steps concurrently.

**Steps:**
- [ ] Audit all 13 `_init_*` methods in `core/polly.py` for shared state dependencies
- [ ] Document dependency graph (which steps read instance vars set by other steps)
- [ ] Group into 3 phases of independent steps (see design.md)
- [ ] Create `async _init_parallel(self)` method using `asyncio.gather()` + `asyncio.to_thread()`
- [ ] Replace sequential init calls in `__init__` with `asyncio.run(self._init_parallel())`
- [ ] Run full test suite to verify no init ordering bugs
- [ ] Benchmark startup time before/after

**Files:** `core/polly.py`, `interfaces/server.py`
**Verification:** Startup time reduced. All 114 tests pass. Manual smoke test of all features.

**Risk:** High — hidden dependencies between init steps may cause subtle bugs. Consider deferring
this task if the other optimizations provide sufficient improvement.

---

## Phase 4: Background Task Optimizations (Tasks 6-7)

These don't affect user-visible latency but reduce resource consumption.

### Task 6: Batch entity extraction

**Goal:** Process query and response through spaCy in a single `nlp.pipe()` call.

**Steps:**
- [ ] Add `batch_extract_and_store(items: List[Tuple[str, str]], source_id, domains)` to `EntityExtractor`
- [ ] Refactor internal extraction to use `self.nlp.pipe(texts)` for batch processing
- [ ] Update `_post_response_background()` in `core/polly.py` to call batch method
- [ ] Add unit test: batch method produces same entities as two individual calls
- [ ] Measure background thread duration before/after

**Files:** `core/entities/extractor.py`, `core/polly.py`
**Verification:** Same entities extracted. Background duration reduced.

### Task 7: Evaluate pattern engine Mem0 backend

**Goal:** Determine if Mem0 backend for patterns adds value. Remove or batch if not.

**Steps:**
- [ ] Search codebase for all `mem0_backend.search()` calls
- [ ] For each call, check if it's doing semantic search (benefits from embeddings) or type/confidence filtering (JSON backend can handle)
- [ ] If semantic search is unused: remove Mem0 backend from `PatternEngine.__init__()` and `learn()`
- [ ] If partially used: make Mem0 save deferred (batch at session end via `SessionExtractor`)
- [ ] Update tests if backend is removed
- [ ] Measure background thread duration — expect ~25s reduction if Mem0 backend fully removed

**Files:** `core/patterns/engine.py`, `core/patterns/storage/mem0_backend.py`
**Verification:** Pattern functionality unchanged (search, learn, confidence decay all work). Background tasks faster.

---

## Phase 5: Validation (Task 8)

### Task 8: Final benchmark and documentation

**Goal:** Measure combined impact and update project docs.

**Steps:**
- [ ] Run full benchmark suite with all optimizations applied
- [ ] Compare against `scripts/benchmark_baseline.json`
- [ ] Update `openspec/specs/project/status.md` with performance numbers
- [ ] Update `openspec/specs/project/roadmap.md` to mark this change complete
- [ ] Run full test suite (114 memory/routing tests + any new tests added)

**Files:** `openspec/specs/project/status.md`, `openspec/specs/project/roadmap.md`
**Verification:** Target metrics met (2-3s steady-state). All tests pass.

---

## Task Priority Order

If time is limited, implement in this order for maximum impact:

1. **Task 2** (parallel tier searches) — Biggest single win, ~3.5s saved on every query
2. **Task 3** (embedding cache) — Near-zero cost for follow-up questions
3. **Task 4** (Ollama warm-up) — Trivial to implement, eliminates cold-start
4. **Task 7** (Mem0 backend evaluation) — Small effort, potentially large background savings
5. **Task 6** (batch entity extraction) — Moderate win for background thread
6. **Task 5** (parallel init) — Highest risk, moderate reward
7. **Tasks 1, 8** (benchmark/docs) — Supporting infrastructure

---

## Coordination Notes

- **Scalable Memory Layers:** This change optimizes the retrieval path introduced there. No architectural conflicts.
- **Semantic Response Cache** (if implemented later): Would sit above these optimizations — cached responses bypass the entire pipeline.
- **Context Distillation Layer** (if implemented later): Would reduce the volume of context fed to the budget allocator, complementing these speed improvements.
