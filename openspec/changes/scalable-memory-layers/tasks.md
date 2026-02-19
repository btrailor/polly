# Tasks: Scalable Memory Layers + Rolling Relevance-Weighted Context

**Last Updated:** 2026-02-18
**Priority:** P1 — Core intelligence infrastructure
**Estimated Effort:** 13-18 days
**Depends On:** Mem0 Adaptive Memory (complete), Hardened Knowledge Infrastructure (complete), Integration Contracts (complete)

---

## Task Overview

| # | Task | Est. | Status |
|---|------|------|--------|
| 1 | Add configuration sections | 0.5d | ✅ Complete |
| 2 | Token counter service | 1d | ✅ Complete |
| 3 | Replace approximate token counting across codebase | 0.5d | ✅ Complete |
| 4 | Budget allocator | 1.5d | ✅ Complete |
| 5 | Update ContextContributor protocol | 0.5d | ✅ Complete |
| 6 | Tiered memory store | 1.5d | ✅ Complete |
| 7 | Memory retriever (ContextContributor) | 1.5d | ✅ Complete |
| 8 | Relevance scorer | 1d | ✅ Complete |
| 9 | Rolling context window | 2d | ✅ Complete |
| 10 | Session-end extraction pipeline | 2d | ✅ Complete |
| 11 | Pipeline integration in polly.py | 1.5d | ✅ Complete |
| 12 | Wire retrieval classifier into main path | 0.5d | ✅ Complete |
| 13 | Fix mental model persona name mismatch | 0.25d | ✅ Complete |
| 14 | Testing — unit tests | 1d | ✅ Complete (84/84 tests) |
| 15 | Testing — integration and session lifecycle | 1d | ✅ Complete (28/28 tests) |
| 16 | Testing — quality validation | 0.5d | ⬜ Deferred (requires running server) |
| 17 | Documentation and spec updates | 0.5d | ✅ Complete |

**Total: ~17.25 days**
**Completed: 16/17 tasks (~94%). Task 16 deferred to manual QA.**

---

## Phase 1: Token Budget Foundation (Tasks 1-5)

### Task 1: Add Configuration Sections

**Est:** 0.5 days
**Files:** `config.yaml`, `core/config.py`

Add `memory` and `context_budget` configuration to both the YAML config and DEFAULT_CONFIG.

**Subtasks:**
- [ ] Add `memory` section to `config.yaml` with extraction, tiers, and retrieval config
- [ ] Add `context_budget` section to `config.yaml` with response_reserve, model_context_windows, sections, relevance_weights, and rolling config
- [ ] Add corresponding entries to `DEFAULT_CONFIG` in `core/config.py` (after existing `"compression"` key, ~line 61)
- [ ] Add `tiktoken` to `requirements.txt`
- [ ] Verify config loads: `PollyConfig().get("memory.tiers.stable.collection")` returns `"memory_stable"`
- [ ] Verify config loads: `PollyConfig().get("context_budget.sections.rag.priority")` returns `4`

**Verification:**
- [ ] `python -c "from core.config import get_config; c = get_config(); print(c.get('memory.provider'))"` prints `"mem0"`
- [ ] `python -c "from core.config import get_config; c = get_config(); print(c.get('context_budget.rolling.decay_per_turn'))"` prints `0.85`
- [ ] No import errors or config load failures

---

### Task 2: Token Counter Service

**Est:** 1 day
**Files:** `core/context/token_counter.py` (new, ~100 lines)

Create the `core/context/` package and implement `TokenCounter`.

**Subtasks:**
- [ ] Create `core/context/__init__.py`
- [ ] Create `core/context/token_counter.py` with `TokenCounter` class
- [ ] Implement `count(text, model_id)`:
  - Lazy-import `tiktoken`
  - Map model IDs to encodings: `gpt-4*`, `gpt-3.5*` → `cl100k_base`; `claude-*` → `cl100k_base`; `llama*`, `ollama*` → fallback
  - Cache tokenizer instances in module-level dict
  - Fallback: `len(text) / 3.5` (rounded up) if tiktoken unavailable
- [ ] Implement `truncate(text, max_tokens, model_id)`:
  - Binary search for token boundary
  - Prefer sentence boundary truncation (split on `. `, `\n`, `; `)
  - Return truncated text
- [ ] Implement `_get_tokenizer(model_id)` with import error handling
- [ ] Implement `_estimate_tokens(text)` fallback

**Verification:**
- [ ] `TokenCounter.count("Hello world", "gpt-4")` returns ~2 tokens
- [ ] `TokenCounter.count("def foo():\n    return 42", "gpt-4")` returns accurate count (verify against tiktoken directly)
- [ ] `TokenCounter.count("test", "llama3.2:latest")` uses fallback estimator
- [ ] `TokenCounter.truncate("a" * 10000, 100, "gpt-4")` returns text with ~100 tokens
- [ ] Works if tiktoken is not installed (graceful fallback)

---

### Task 3: Replace Approximate Token Counting

**Est:** 0.5 days
**Files:** `core/compression/manager.py`, `core/rag.py`, `core/polly.py`

Replace `len(text) // 4` and similar approximations with `TokenCounter.count()`.

**Subtasks:**
- [ ] `core/compression/manager.py`: Find all `len(text) // 4` or similar patterns, replace with `TokenCounter.count(text)`
- [ ] `core/rag.py:1222` (`format_context` method): Replace character-based `max_tokens * 4` limit with `TokenCounter.truncate()`
- [ ] `core/polly.py`: Find any token estimation in the query pipeline, replace with `TokenCounter.count()`
- [ ] Import `TokenCounter` in each modified file
- [ ] Verify no regressions: existing compression thresholds still trigger at similar points (may need to adjust thresholds slightly since counts will be more accurate)

**Verification:**
- [ ] `grep -r "len.*//.*4" core/` returns no token-estimation hits in modified files
- [ ] Polly starts without errors
- [ ] A test query produces a response (basic sanity)

---

### Task 4: Budget Allocator

**Est:** 1.5 days
**Files:** `core/context/budget_allocator.py` (new, ~200 lines)

Implement the priority-based section budget allocator.

**Subtasks:**
- [ ] Create `core/context/budget_allocator.py`
- [ ] Implement `SectionBudget` and `BudgetPlan` dataclasses
- [ ] Implement `BudgetPlan.remaining(section)` and `BudgetPlan.report_usage(section, tokens)`
- [ ] Implement `BudgetAllocator.__init__(config)` — load section configs from `context_budget.sections`
- [ ] Implement `BudgetAllocator.allocate(model_context_window, conversation_tokens, model_id)`:
  - Calculate available = model_context_window - response_reserve - conversation_tokens
  - Call `_solve_allocation(available, sections)`
  - Return `BudgetPlan`
- [ ] Implement `_solve_allocation(available, sections)`:
  - Pass 1: Allocate min_tokens for all sections by priority order. If budget is exhausted before all mins are met, lower-priority sections get 0.
  - Pass 2: Distribute remaining budget proportionally by `target_pct`. Cap at `max_tokens`.
  - Pass 3: Any surplus from capped sections redistributed to uncapped sections.
- [ ] Handle edge case: available < sum of all minimums (squeeze lowest-priority sections)
- [ ] Handle edge case: very large context windows (caps prevent over-allocation; surplus goes to overflow)

**Verification:**
- [ ] Allocate with 200K window, 2K conversation → all sections get their max (capped)
- [ ] Allocate with 8K window, 4K conversation → only 2K available → priorities 1-2 get mins, others get squeezed
- [ ] Allocate with 16K window, 2K conversation → 12K available → distributed proportionally within min/max
- [ ] `BudgetPlan.remaining("rag")` returns correct value after `report_usage("rag", 500)`

---

### Task 5: Update ContextContributor Protocol

**Est:** 0.5 days
**Files:** `core/polly.py`, `core/mental_models.py`, `core/compression/manager.py`, `core/entities/context_builder.py` (if exists), `core/patterns/` (PatternEngine)

Add optional `token_budget` parameter to `build_context()` across all ContextContributors.

**Subtasks:**
- [ ] Update `build_context()` signature in all contributors to accept `token_budget: int = 0`
- [ ] `core/mental_models.py` — `MentalModelManager.build_context()`: If `token_budget > 0`, use `TokenCounter.truncate()` on output
- [ ] `core/compression/manager.py` — `CompressionManager.build_context()`: If `token_budget > 0`, truncate compressed summary
- [ ] Entity context builder: Add `token_budget` parameter, truncate if needed
- [ ] Pattern engine: Add `token_budget` parameter, truncate if needed
- [ ] All changes are backward-compatible (default `token_budget=0` means no limit)

**Verification:**
- [ ] `mental_model_manager.build_context("test query")` still works (no budget = no truncation)
- [ ] `mental_model_manager.build_context("test query", token_budget=200)` returns output within ~200 tokens
- [ ] All existing tests pass (backward-compatible change)

---

## Phase 2: Tiered Memory Store (Tasks 6-7)

### Task 6: Tiered Memory Store

**Est:** 1.5 days
**Files:** `core/memory/tiers.py` (new, ~200 lines), `core/memory/__init__.py` (modified)

Implement the three-tier memory abstraction over Mem0.

**Subtasks:**
- [ ] Create `core/memory/tiers.py`
- [ ] Implement `MemoryTier` enum (STABLE, EPISODIC, WORKING)
- [ ] Implement `MemoryEntry` dataclass with content, tier, metadata, score, token_count
- [ ] Implement `MemoryMetadata` dataclass with tier, domain, persona_source, timestamp, salience, reference_count, last_referenced, source_type, session_id, tags
- [ ] Implement `TieredMemoryStore.__init__(mem0_adapter, config)`:
  - Store reference to Mem0 adapter
  - Generate session_id from timestamp
  - Configure tier collection names from config
- [ ] Implement `TieredMemoryStore.write(content, tier, metadata)`:
  - Set `user_id` based on tier: `tier:stable`, `tier:episodic`, `tier:working:{session_id}`
  - Set `agent_id` to `"polly"`
  - Call `self.mem0.add_memory(content, user_id=..., agent_id=..., metadata=...)`
  - Return memory ID
- [ ] Implement `TieredMemoryStore.read(query, tiers, limit, domain_filter, min_score)`:
  - For each requested tier, call `self.mem0.search_memory(query, user_id=..., limit=...)`
  - Parse results into `MemoryEntry` objects
  - Apply domain_filter if specified
  - Apply min_score threshold
  - Return merged results
- [ ] Implement `TieredMemoryStore.flush_working()`:
  - Delete all memories with `user_id=tier:working:{session_id}`
- [ ] Implement `TieredMemoryStore.update_reference(memory_id)`:
  - Increment reference_count in metadata
  - Update last_referenced timestamp
  - Call `self.mem0.update_memory(memory_id, ...)`
- [ ] Implement `TieredMemoryStore.deduplicate_against(content, tier)`:
  - Search tier with content as query, limit=3
  - If any result has similarity >= 0.92, return its ID
  - Return None otherwise
- [ ] Update `core/memory/__init__.py` — export `TieredMemoryStore`, `MemoryTier`, `MemoryEntry`

**Verification:**
- [ ] Write to stable tier → read back with matching query → returned
- [ ] Write to working tier → flush_working → read returns empty
- [ ] Write duplicate content → deduplicate_against returns existing ID
- [ ] Domain filter excludes non-matching entries
- [ ] min_score threshold excludes low-scoring entries

---

### Task 7: Memory Retriever (ContextContributor)

**Est:** 1.5 days
**Files:** `core/memory/retriever.py` (new, ~250 lines)

Implement the tiered retriever as a ContextContributor.

**Subtasks:**
- [ ] Create `core/memory/retriever.py`
- [ ] Implement `MemoryRetriever.__init__(tiered_store, config)`:
  - Store reference to tiered store
  - Load retrieval config (limits, thresholds)
  - Set PRIORITY = 50
- [ ] Implement `MemoryRetriever.build_context(query, token_budget)`:
  - Call `self.retrieve(query)`
  - Format results via `_format_memories()`
  - Truncate to `token_budget` if specified
  - Return formatted string
- [ ] Implement `MemoryRetriever.retrieve(query, domains, limit)`:
  - Search stable tier (limit=`stable_limit`, no decay)
  - Search episodic tier (limit=`episodic_limit`, apply time decay)
  - Get all working tier entries
  - Deduplicate across tiers (prefer stable > episodic > working for same content)
  - Sort by score
  - Return top `limit` entries
- [ ] Implement `_apply_time_decay(entry)`:
  - Parse timestamp from entry metadata
  - Calculate days since write
  - Apply `exp(-ln(2) * days / halflife_days)` decay factor
  - Multiply entry's raw score by decay factor
  - Stable tier: factor = 1.0, Working tier: factor = 1.0
- [ ] Implement `_format_memories(memories, token_budget)`:
  - Format header: `## Relevant Memory`
  - Each entry: `[tier, age] content`
  - Use `TokenCounter` to stay within budget
  - Return formatted string

**Verification:**
- [ ] `build_context("test")` returns formatted string with memories from all tiers
- [ ] Episodic entries from 90 days ago have ~50% of their original score
- [ ] Working tier entries appear with full score regardless of age
- [ ] Deduplication: same content in stable and episodic → stable version kept
- [ ] `token_budget=500` → output is within ~500 tokens
- [ ] Empty tiers → returns empty string

---

## Phase 3: Rolling Relevance-Weighted Context (Tasks 8-9)

### Task 8: Relevance Scorer

**Est:** 1 day
**Files:** `core/context/relevance_scorer.py` (new, ~150 lines)

Implement the composite relevance scorer.

**Subtasks:**
- [ ] Create `core/context/relevance_scorer.py`
- [ ] Implement `ScoredEntry` dataclass with content, source, raw_score, composite_score, token_count, key_terms, metadata, reference_count, last_referenced_turn, turns_since_reference
- [ ] Implement `RelevanceScorer.__init__(config)`:
  - Load weights from `context_budget.relevance_weights`
  - Validate weights sum to 1.0 (warn if not, normalize)
- [ ] Implement `RelevanceScorer.score(entry, query_domains, current_turn)`:
  - Calculate each component score
  - Compute weighted sum
  - Clamp to [0, 1]
  - Set `entry.composite_score`
  - Return composite score
- [ ] Implement `_retrieval_similarity(entry)`:
  - RAG/Mem0 scores (0-1): pass through
  - Mental model scores (0-100): divide by 100
  - Unknown sources: use raw_score as-is
- [ ] Implement `_recency_score(entry, current_turn)`:
  - Referenced this session: `max(0, 1 - (turns_since_reference * 0.15))`
  - Not referenced this session: use timestamp with tier-appropriate decay
- [ ] Implement `_reference_frequency_score(entry)`:
  - `min(reference_count / 5, 1.0)`
- [ ] Implement `_domain_affinity_score(entry, query_domains)`:
  - Primary domain match: 1.0
  - Secondary domain match: 0.6
  - General/cross: 0.4
  - No match: 0.1
- [ ] Implement `_tier_weight_score(entry)`:
  - Source-based fixed weights per design doc

**Verification:**
- [ ] Score of entry with all perfect components → ~1.0
- [ ] Score of entry with all zero components → ~0.0
- [ ] Changing only recency (referenced 5 turns ago vs 0 turns) produces meaningful score difference
- [ ] Domain mismatch produces lower score than domain match
- [ ] Working memory entry scores higher than equivalent episodic entry (tier weight)

---

### Task 9: Rolling Context Window

**Est:** 2 days
**Files:** `core/context/rolling_context.py` (new, ~250 lines)

Implement the per-turn decay/amplification and bin-packing system.

**Subtasks:**
- [ ] Create `core/context/rolling_context.py`
- [ ] Implement `RollingContext.__init__(config)`:
  - Load decay_rate, eviction_turns, amplification_reset from config
  - Initialize empty entries list and turn_count
- [ ] Implement `RollingContext.ingest(new_entries)`:
  - For each new entry, check content hash against existing entries
  - If duplicate: update existing entry's score if new score is higher
  - If new: add to entries list
  - Extract and cache `key_terms` for each new entry
- [ ] Implement `RollingContext.on_new_turn(query, response)`:
  - Increment turn_count
  - For each entry, call `_detect_reference(entry, query + " " + response)`
  - Referenced entries: reset recency to 1.0, increment reference_count, reset turns_since_reference to 0
  - Unreferenced entries: increment turns_since_reference, multiply composite_score's recency component by decay_rate
  - Evict entries with turns_since_reference >= eviction_turns
  - Re-score all remaining entries
- [ ] Implement `_detect_reference(entry, text)`:
  - Compare entry.key_terms against tokens in text
  - Case-insensitive comparison
  - Threshold: >= 2 matching terms, or >= 1 if entry has <= 3 total terms
  - Return bool
- [ ] Implement `_extract_key_terms(content)`:
  - Capitalized words (likely proper nouns/entities)
  - Terms in backticks (code references)
  - Terms > 6 chars that aren't in a common-word stoplist
  - Deduplicate, return list of max 10 terms
- [ ] Implement `RollingContext.select(section_budgets)`:
  - Group entries by source section (memory, rag, mental_models, entities)
  - For each section with a budget:
    - Sort entries by composite_score descending
    - Greedy take: add entries until budget exhausted
    - Look-ahead of 5: if next doesn't fit, check 5 smaller entries
  - Return `{section_name: [selected entries]}`
- [ ] Implement `RollingContext.get_state()`:
  - Return serializable dict with entry count, turn count, per-section counts, top scores

**Verification:**
- [ ] Ingest 10 entries → entries list has 10 items
- [ ] Ingest duplicate → entries list still has 10 (updated, not duplicated)
- [ ] on_new_turn with query mentioning entry A → A's reference_count increases
- [ ] on_new_turn with query NOT mentioning entry B → B's score decreases
- [ ] After 5 unreferenced turns → entry evicted
- [ ] Amplification: reference resets turns_since_reference to 0
- [ ] select with budget 1000 → selected entries' total tokens <= 1000
- [ ] select prefers higher-scored entries over lower-scored
- [ ] Look-ahead: if high-score entry doesn't fit, a smaller lower-score entry is taken instead

---

## Phase 4: Extraction and Wiring (Tasks 10-13)

### Task 10: Session-End Extraction Pipeline

**Est:** 2 days
**Files:** `core/memory/extractor.py` (new, ~300 lines)

Implement the session-end fact extraction and tier write-back.

**Subtasks:**
- [ ] Create `core/memory/extractor.py`
- [ ] Implement `ExtractedFact` dataclass with content, tier, source_type, domain, salience, tags
- [ ] Implement `ExtractionResult` dataclass with stable_count, episodic_count, skipped_count, model_used, duration_ms
- [ ] Implement `SessionExtractor.__init__(tiered_store, config, budget_manager)`:
  - Store references
  - Load extraction config (cloud_threshold, models, max_cost)
- [ ] Implement `SessionExtractor.extract_and_store(conversation_history, compression_summary, session_metadata)`:
  - Call `_assess_session_value()` to determine model tier
  - Build extraction prompt with `_build_extraction_prompt()`
  - Call extraction model with `_call_extraction_model()`
  - Classify facts with `_classify_tier()`
  - Deduplicate with `_deduplicate()`
  - Write to tiered store
  - Flush working tier
  - Return ExtractionResult
- [ ] Implement `_assess_session_value(conversation_history, session_metadata)`:
  - Check domain count, complexity signals, decision count, exchange count
  - Return "cloud" or "local"
- [ ] Implement `_build_extraction_prompt(conversation_history, compression_summary)`:
  - Use extraction prompt template from design doc
  - Include last N messages (default 30) to keep prompt bounded
  - Include compression_summary.decisions and focus_topics as pre-extracted signals
  - Request JSON array output
- [ ] Implement `_call_extraction_model(prompt, model_tier)`:
  - Local: POST to Ollama API with configured local_model
  - Cloud: Use router_v2 or direct Anthropic call with claude-haiku, budget-capped
  - Parse JSON response into ExtractedFact list
  - On parse failure: attempt regex extraction for key-value patterns
  - On total failure: return empty list with warning
- [ ] Implement `_classify_tier(fact)`:
  - Validate/override model's tier classification using keyword rules
  - Skip facts with salience < 0.3
- [ ] Implement `_deduplicate(facts)`:
  - For each fact, call `tiered_store.deduplicate_against(content, tier)`
  - If duplicate found with same content: skip
  - If duplicate found with different content (contradiction): update existing
  - If no duplicate: keep for writing

**Verification:**
- [ ] Extract from a conversation with a stated preference → produces stable fact
- [ ] Extract from a conversation with a decision → produces episodic fact
- [ ] Extract from trivial conversation → empty or minimal facts list
- [ ] Session value assessment: single-domain, 5 exchanges → "local"
- [ ] Session value assessment: multi-domain, 25 exchanges with decisions → "cloud"
- [ ] JSON parse failure → graceful recovery, returns empty list
- [ ] Ollama down → graceful failure, returns empty list
- [ ] Deduplication: extract same preference twice → only one stored

---

### Task 11: Pipeline Integration in polly.py

**Est:** 1.5 days
**Files:** `core/polly.py`

Wire everything into the main orchestration pipeline.

**Subtasks:**
- [ ] **Init sequence** (~line 130): Initialize `TieredMemoryStore`, `MemoryRetriever`, `SessionExtractor`, `BudgetAllocator`, `RelevanceScorer`, `RollingContext` after Mem0 init
  - All wrapped in try/except for graceful degradation
  - Log success/failure for each component
- [ ] **`_gather_context()` refactor** (~line 834):
  - Accept `budget_plan: BudgetPlan` parameter
  - Add `memory_retriever` as contributor at priority 50
  - Pass `token_budget` from budget_plan to each contributor
  - Score results via `relevance_scorer`
  - Ingest into `rolling_context`
  - Select via `rolling_context.select(section_budgets)`
  - Report usage to budget_plan
  - Return assembled string
- [ ] **`query()` budget allocation** (~line 1887):
  - Before `_gather_context()`, call `budget_allocator.allocate()`:
    - Get model context window from config (based on routing decision)
    - Count conversation_tokens with `TokenCounter`
    - Get `budget_plan`
  - Pass budget_plan to `_gather_context()`
  - Use budget_plan for RAG context truncation (section "rag")
- [ ] **Turn tracking** (after response generation):
  - Call `self.rolling_context.on_new_turn(user_query, response_text)`
- [ ] **Session-end hook**:
  - Add `_on_session_end()` async method
  - Called from appropriate lifecycle event (app shutdown, session timeout, explicit close)
  - Calls `session_extractor.extract_and_store()`
  - Calls `tiered_store.flush_working()`
  - Register with SIGTERM/SIGINT handlers and/or add to server shutdown hooks in `interfaces/server.py`
- [ ] **Graceful degradation**: If any new component fails to initialize:
  - Memory retriever missing: skip memory section, redistribute budget
  - Budget allocator missing: fall back to current unbounded assembly
  - Rolling context missing: fall back to current concatenation
  - Session extractor missing: skip extraction at session end
  - Log all fallbacks at WARNING level

**Verification:**
- [ ] Polly starts successfully with all new components
- [ ] Polly starts successfully with Mem0 disabled (graceful degradation)
- [ ] A query returns a response with budget-allocated context
- [ ] `_gather_context()` includes memory retriever output when available
- [ ] Turn tracking runs after each response (verify via debug logging)
- [ ] Session-end extraction runs on shutdown (verify via logging)
- [ ] No regressions: existing queries produce comparable-quality responses

---

### Task 12: Wire Retrieval Classifier Into Main Path

**Est:** 0.5 days
**Files:** `core/polly.py` (~line 1857), `core/hardened/classifier.py`

Address the existing TODO at `polly.py:1869` to use classification results for scoring and retrieval behavior.

**Subtasks:**
- [ ] In `query()` after `RetrievalClassifier.classify()` (~line 1857-1884):
  - Pass `classification.tier` to `RelevanceScorer` as context for RAG result scoring
  - DIRECT: RAG raw_scores used as-is
  - ADJACENT: RAG raw_scores multiplied by 0.7
  - ABSENT: Increase episodic_limit from 5 to 10 in memory retriever, decrease min_similarity from 0.4 to 0.3
- [ ] Use `classification.tier` for prompt language selection:
  - DIRECT: "Prioritize the following information from your knowledge base"
  - ADJACENT: "The following information may be relevant but is not a direct answer"
  - ABSENT: "No directly relevant information was found. Use your general knowledge and the following context for background"
- [ ] Remove the TODO comment at line 1869

**Verification:**
- [ ] DIRECT query → RAG results appear with original scores in context
- [ ] ADJACENT query → RAG results appear with reduced scores
- [ ] ABSENT query → memory retrieval is more aggressive (more episodic results)
- [ ] Prompt header varies by tier classification

---

### Task 13: Fix Mental Model Persona Name Mismatch

**Est:** 0.25 days
**Files:** `core/mental_models.py`

Fix the `"teacher"` vs `"professor"` mismatch in default mental model definitions.

**Subtasks:**
- [ ] In `_get_default_models()`, find all models with `"teacher"` in `active_for_personas`
- [ ] Replace `"teacher"` with `"professor"` in each occurrence
- [ ] Affected models (expected): Pedagogy of Liberation, Socratic Method, Reverse Engineering, and any others with `"teacher"` in their persona list
- [ ] Verify the Professor persona is registered as `"professor"` in PersonaManager (confirm the correct name)

**Verification:**
- [ ] `grep -n "teacher" core/mental_models.py` — no remaining `"teacher"` in `active_for_personas` fields (may still appear in descriptions, which is fine)
- [ ] Activate Professor persona → pedagogy mental models now appear in context (previously would not due to name mismatch)

---

## Phase 5: Testing and Documentation (Tasks 14-17)

### Task 14: Testing — Unit Tests

**Est:** 1 day
**Files:** `tests/test_token_counter.py`, `tests/test_budget_allocator.py`, `tests/test_tiered_memory.py`, `tests/test_relevance_scorer.py`, `tests/test_rolling_context.py`, `tests/test_session_extractor.py`

**Subtasks:**
- [ ] **TokenCounter tests:**
  - Accuracy within 5% of tiktoken for code, prose, mixed content
  - Truncation produces output within specified budget
  - Graceful fallback when tiktoken unavailable
- [ ] **BudgetAllocator tests:**
  - All sections get at least min_tokens when budget allows
  - No section exceeds max_tokens
  - Priority ordering under pressure (small budget)
  - Surplus redistribution when sections are capped
  - report_usage tracking
- [ ] **TieredMemoryStore tests (requires Mem0 mock):**
  - Write to each tier → read back
  - Working tier flush clears only working entries
  - Deduplication at 0.92 threshold
  - Domain filtering
- [ ] **RelevanceScorer tests:**
  - Composite score in [0, 1]
  - Weight contributions proportional to config
  - Domain affinity affects score
  - Tier weight affects score
- [ ] **RollingContext tests:**
  - Ingest → entries stored
  - Decay reduces scores per turn
  - Amplification resets recency
  - Eviction after configured turns
  - Bin-packing respects budgets
  - Look-ahead selection
- [ ] **SessionExtractor tests (requires Ollama mock):**
  - Preference extraction → stable tier
  - Decision extraction → episodic tier
  - Session value assessment routing
  - JSON parse failure recovery
  - Deduplication against existing memory

**Verification:**
- [ ] All unit tests pass: `python -m pytest tests/test_token_counter.py tests/test_budget_allocator.py tests/test_tiered_memory.py tests/test_relevance_scorer.py tests/test_rolling_context.py tests/test_session_extractor.py -v`

---

### Task 15: Testing — Integration and Session Lifecycle

**Est:** 1 day
**Files:** `tests/test_memory_integration.py`

**Subtasks:**
- [ ] **Full pipeline test:** Query → memory retrieval → RAG → budget allocation → rolling context → response
  - Verify response is generated
  - Verify total context tokens within budget
  - Verify memory section present in context when memories exist
- [ ] **Session lifecycle test:**
  - Start session → state a preference → 5 exchanges → session end
  - Verify extraction produces stable fact
  - Start new session → query related to preference → verify memory retrieved
- [ ] **Decay test:**
  - Submit 3 queries about topic A
  - Submit 5 queries about topic B (no mention of A)
  - Verify topic A context has decayed or been evicted
  - Verify topic B context is prominent
- [ ] **Budget enforcement test:**
  - Artificially inflate RAG results + mental models to exceed model context window
  - Verify budget allocator truncates gracefully
  - Verify response is still generated
- [ ] **Backward compatibility test:**
  - Disable Mem0 → verify pipeline falls back to current behavior
  - Verify Scribe persona enrichment preferences still work (separate namespace)

**Verification:**
- [ ] All integration tests pass
- [ ] No regressions in existing test suite: `python -m pytest tests/ -v`

---

### Task 16: Testing — Quality Validation

**Est:** 0.5 days

Manual testing to verify response quality is maintained or improved.

**Subtasks:**
- [ ] Submit 10 representative queries across different domains (Sigils, Scrolls, Signals, etc.)
- [ ] Compare response quality with budget-constrained context vs previous unbounded context
- [ ] Verify no critical information lost due to budget truncation
- [ ] Verify memory retrieval adds relevant context (not noise)
- [ ] Verify decay/amplification produces intuitive behavior in multi-turn conversations
- [ ] Check extraction quality: review `~/.polly/` for stored memories after test sessions
- [ ] Adjust relevance_weights or budget allocations if quality issues detected

**Verification:**
- [ ] Responses are comparable or better quality to current system
- [ ] No user-visible degradation
- [ ] Extracted memories are accurate and useful

---

### Task 17: Documentation and Spec Updates

**Est:** 0.5 days
**Files:** `openspec/specs/architecture/spec.md`, `openspec/specs/project/status.md`, `openspec/specs/project/roadmap.md`

**Subtasks:**
- [ ] Update `openspec/specs/architecture/spec.md`:
  - Add tiered memory store to component list
  - Add context budget allocator to data flow diagram
  - Add rolling context to query pipeline description
- [ ] Update `openspec/specs/project/status.md`:
  - Add Scalable Memory Layers entry under "Current Priority"
  - Update Core Framework status (Persona Memory now has infrastructure)
- [ ] Update `openspec/specs/project/roadmap.md`:
  - Add as cross-cutting change
  - Note dependency relationship with Context Distillation Layer
- [ ] Update `openspec/changes/IMPLEMENTATION_STATUS.md`:
  - Add scalable-memory-layers entry with status

**Verification:**
- [ ] All spec references are accurate
- [ ] Status reflects actual implementation state

---

## Dependency Order

```
Task 1 (Config)
    ↓
Task 2 (TokenCounter) → Task 3 (Replace approximate counting)
    ↓
Task 4 (BudgetAllocator)
    ↓
Task 5 (ContextContributor protocol update)
    ↓
Task 6 (TieredMemoryStore)     ←── can partially overlap with Task 4
    ↓
Task 7 (MemoryRetriever)
    ↓
Task 8 (RelevanceScorer)       ←── can partially overlap with Task 7
    ↓
Task 9 (RollingContext)
    ↓
Task 10 (SessionExtractor)     ←── can partially overlap with Task 9
    ↓
Task 11 (Pipeline integration) ←── depends on ALL of Tasks 4-10
    ↓
Task 12 (Classifier wiring)    ←── depends on Task 8 (scorer) + Task 11
Task 13 (Mental model fix)     ←── independent, can happen anytime
    ↓
Tasks 14-16 (Testing)          ←── can run in parallel with each other
    ↓
Task 17 (Docs)
```

---

## Coordination Notes

### Complements: Context Distillation Layer

The context distillation layer (specced separately) compresses content after this change selects what to include. They stack:

```
Budget Allocator → selects context within budget
                        ↓
Context Distillation → compresses selected context for cloud calls
                        ↓
Cloud LLM → receives budget-constrained + distilled context
```

If both are implemented, distillation operates on already-budget-constrained context — the input is already the most relevant subset, making distillation more effective.

### Complements: Semantic Response Cache

Cache hits (Phase 0) skip the entire memory/context/budget pipeline. Cache misses benefit from better context assembly. No conflicts.

### Feeds Into: Persona-Specific Memory

This change provides the tiered memory infrastructure. A follow-up change can add:
- Professor: teaching history, topic mastery tracking per user
- Architect: decision logs, architectural patterns learned
- Scribe: migration from current flat `persona:scribe` namespace to tiered store
- Per-persona extraction templates for session-end pipeline

### Impact on Core Framework Wave 4

This change directly addresses Wave 4 item #24 "Persona Memory for Enrichment" (~25% complete) by providing the missing memory infrastructure. After this change, persona memory is ~60% complete (infrastructure done, persona-specific policies pending).
