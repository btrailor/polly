# Tasks: Context Distillation Layer Implementation

## Overview
Ordered implementation steps for adding Ollama-based context distillation to Polly's query pipeline.

**Principle:** Backend core module first, then pipeline integration, then settings UI.

**Estimated scope:** ~500 lines across 12 files (2 new, 10 modified)

**Dependency:** Phase 0 (Semantic Response Cache) should be implemented first. Distillation skips on cache hits.

---

## Task 1: Add Configuration
**Goal:** Add context distillation config to config.yaml and core/config.py

### Subtasks:
1. Add `context_distillation` section to `config.yaml`:
   ```yaml
   context_distillation:
     enabled: true
     model: "llama3.2:3b"
     target_ratio: 0.4
     min_tokens: 2000
     max_distill_time_ms: 2000
     distill_rag: true
     distill_gathered: true
     cloud_only: true
   ```

2. Add `context_distillation` to `DEFAULT_CONFIG` in `core/config.py`

### Files:
- `config.yaml`
- `core/config.py`

### Validation:
- [ ] Config loads without errors
- [ ] Default values accessible via `config.get("context_distillation")`

---

## Task 2: Create OllamaDistillStrategy
**Goal:** Implement Ollama-based compression strategy alongside existing LLMLingua

**File:** `core/compression/ollama_strategy.py` (~150 lines)

### Subtasks:
1. **Class skeleton:**
   ```python
   class OllamaDistillStrategy:
       def __init__(self, ollama_host, model="llama3.2:3b")
       async def compress(text, target_ratio, context_type, domain, retrieval_tier) -> CompressionResult
       def _build_distill_prompt(context, domain, retrieval_tier, target_ratio) -> str
       async def _call_ollama(prompt, system, max_tokens) -> str
   ```

2. **Distillation prompt template:**
   - General template with domain-specific rules
   - Sigils (code): preserve code blocks verbatim
   - Scrolls (writing): preserve arguments and structure
   - Signals (audio): preserve timestamps and speakers
   - Default: balanced summarization

3. **Ollama API call:**
   - POST to `{ollama_host}/api/generate`
   - Use configured model (llama3.2:3b)
   - Set `max_tokens` based on `len(text) * target_ratio`
   - Handle connection errors, timeouts gracefully

4. **Return CompressionResult:**
   - Same dataclass as LLMLinguaCompressor returns
   - Fields: compressed_text, original_tokens, compressed_tokens, compression_ratio, metadata

### Validation:
- [ ] compress() returns shorter text than input
- [ ] Code blocks preserved verbatim in Sigils mode
- [ ] Connection error returns original text (graceful fallback)
- [ ] Timeout returns original text (graceful fallback)
- [ ] CompressionResult format matches LLMLingua's

---

## Task 3: Create ContextDistiller Module
**Goal:** Implement core ContextDistiller class with singleton pattern

**File:** `core/context_distiller.py` (~200 lines)

### Subtasks:
1. **Module-level singleton:**
   ```python
   _instance = None
   def init_context_distiller(ollama_host, config) -> ContextDistiller
   def get_context_distiller() -> Optional[ContextDistiller]
   ```

2. **DistillResult and DistillStats dataclasses**

3. **ContextDistiller.__init__():**
   - Accept ollama_host, config
   - Create OllamaDistillStrategy instance
   - Store config values (target_ratio, min_tokens, max_distill_time_ms)
   - Initialize stats counters

4. **ContextDistiller.distill(context, domain, retrieval_tier, context_type):**
   - Call OllamaDistillStrategy.compress() with timeout
   - Track timing and compression ratio
   - Return DistillResult
   - On timeout/error: return DistillResult with original text and ratio=1.0

5. **ContextDistiller.should_distill(context_length, route_type):**
   - Return False if disabled
   - Return False if route_type is "local" and cloud_only is True
   - Return False if context_length < min_tokens
   - Return True otherwise

6. **ContextDistiller.get_stats():**
   - Return DistillStats from accumulated counters

### Validation:
- [ ] Singleton pattern works (init/get)
- [ ] distill() returns compressed text
- [ ] distill() respects timeout
- [ ] should_distill() returns correct booleans for all scenarios
- [ ] get_stats() returns accumulated metrics

---

## Task 4: Register Strategy with Compression Manager
**Goal:** Make OllamaDistillStrategy available through existing compression infrastructure

**File:** `core/compression/compressor.py`

### Subtasks:
1. Add `"ollama_distill"` to `CompressionStrategy` type:
   ```python
   CompressionStrategy = Literal["auto", "llmlingua", "llm_summary", "ollama_distill"]
   ```

2. Update `get_strategy_for_context()` to include ollama_distill option:
   ```python
   "rag_context": "ollama_distill"  # or keep "llmlingua" based on config
   ```

3. Update `compress_with_strategy()` to handle `"ollama_distill"` strategy

**File:** `core/compression/manager.py`

4. Add `distill_context()` method as entry point for the distillation pipeline

### Validation:
- [ ] "ollama_distill" strategy recognized
- [ ] Strategy selection works based on config
- [ ] Existing "llmlingua" and "llm_summary" strategies unchanged

---

## Task 5: Integrate Distiller into Polly Init Sequence
**Goal:** Add _init_context_distiller() to Polly.__init__

**File:** `core/polly.py`

### Subtasks:
1. Add `_init_context_distiller()` method:
   - Import `init_context_distiller` from `core.context_distiller`
   - Get config from `self.config`
   - Initialize with Ollama host from config
   - Wrap in try/except (non-critical)

2. Call `_init_context_distiller()` in `__init__` sequence:
   - After semantic cache init
   - Before router init

### Validation:
- [ ] Distiller initializes when enabled
- [ ] Distiller skipped when disabled
- [ ] Polly starts normally if distiller init fails
- [ ] Log messages confirm init status

---

## Task 6: Add Distillation Step to Query Pipeline
**Goal:** Distill RAG context and gathered context before cloud routing

**File:** `core/polly.py`

### Subtasks:
1. After context assembly (~L2011), before cloud router call (~L2140), add distillation block:
   - Check `should_distill()` with context length and route type
   - Distill `rag_context` if `distill_rag` config is True
   - Distill `gathered_context` if `distill_gathered` config is True
   - Reconstruct `augmented_system` with distilled components

2. Add `_rebuild_augmented_system()` helper:
   - Reconstructs the system prompt with distilled context strings
   - Preserves base prompt, domain prompt, RAG header/footer unchanged

3. Add distillation to Wave 3 sub-query pipeline (`core/split_router.py`):
   - Distill per-sub-query RAG context before cloud-routed sub-queries
   - Same should_distill() check

4. Track distillation metrics:
   - Log compression ratio and timing
   - Feed to AutonomyMetrics

### Files:
- `core/polly.py`
- `core/split_router.py` (optional — Wave 3 sub-queries)

### Validation:
- [ ] Distillation runs for cloud-routed queries with large context
- [ ] Distillation skipped for local routes
- [ ] Distillation skipped for small contexts (< min_tokens)
- [ ] Distillation skipped on cache hits (Phase 0)
- [ ] augmented_system reconstructed correctly with distilled context
- [ ] Pipeline continues normally if distillation fails

---

## Task 7: Extend AutonomyMetrics
**Goal:** Track distillation statistics in AutonomySnapshot

**File:** `core/autonomy_metrics.py`

### Subtasks:
1. Add distillation fields to `AutonomySnapshot`:
   ```python
   distillation_count: int = 0
   distillation_tokens_saved: int = 0
   distillation_avg_ratio: float = 0.0
   distillation_avg_time_ms: float = 0.0
   ```

2. Update `get_snapshot()` to query distillation stats from ContextDistiller

### Validation:
- [ ] AutonomySnapshot includes distillation fields
- [ ] Stats populate when distillation is active
- [ ] Stats are zero when distillation is inactive

---

## Task 8: Add Server API Endpoints
**Goal:** Add distillation stats and settings endpoints

### Subtasks:
1. **Stats endpoint** (`interfaces/server.py`):
   ```python
   @app.get("/polly/distillation/stats")
   async def get_distillation_stats():
       distiller = get_context_distiller()
       if not distiller:
           return {"error": "Distiller not initialized"}
       return asdict(distiller.get_stats())
   ```

2. **Settings endpoints** (`interfaces/settings_api.py`):
   ```python
   @app.get("/polly/settings/context-distillation")
   @app.put("/polly/settings/context-distillation")
   ```

### Files:
- `interfaces/server.py`
- `interfaces/settings_api.py`

### Validation:
- [ ] GET /polly/distillation/stats returns DistillStats JSON
- [ ] GET/PUT settings endpoints work
- [ ] All endpoints handle distiller-not-initialized gracefully

---

## Task 9: Add Settings UI
**Goal:** Add distillation controls to Electron settings

### Subtasks:
1. **HTML** (`electron-app/src/renderer/index.html`):
   - Toggle: "Enable Context Distillation"
   - Slider: "Compression Ratio" (0.2-0.8, step 0.05)
   - Model selector: dropdown with available Ollama models
   - Stats label: "X distillations, Y tokens saved"

2. **JavaScript** (`electron-app/src/renderer/app.js`):
   - `loadDistillationSettings()`: GET settings → populate UI
   - `saveDistillationSettings()`: Read UI → PUT settings
   - `refreshDistillationStats()`: GET stats → update label
   - Wire up event listeners

### Files:
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/app.js`

### Validation:
- [ ] Toggle enables/disables distillation
- [ ] Slider adjusts target ratio
- [ ] Stats label updates
- [ ] Settings persist across restart

---

## Task 10: Testing — Core Distillation
**Goal:** Verify distillation produces valid compressed output

### Test Cases:
1. **Basic distillation:**
   - Input 8,000 chars of RAG context
   - Distill with target_ratio=0.4
   - Verify output is 30-50% of original size

2. **Code preservation (Sigils domain):**
   - Input RAG context containing Python code blocks
   - Verify code blocks appear verbatim in distilled output
   - Verify surrounding text is summarized

3. **Graceful fallback:**
   - Stop Ollama → distill → verify original text returned
   - Set timeout to 1ms → distill → verify original text returned

4. **Skip conditions:**
   - Context < min_tokens → should_distill returns False
   - Route type "local" → should_distill returns False
   - Disabled in config → should_distill returns False

5. **Domain-specific prompts:**
   - Verify Sigils prompt contains code preservation rules
   - Verify Scrolls prompt contains writing-specific rules

### Validation:
- [ ] All test cases pass
- [ ] Compression ratios within expected range
- [ ] No crashes on any failure mode

---

## Task 11: Testing — Pipeline Integration
**Goal:** End-to-end test in query pipeline

### Test Cases:
1. **Full flow:** Query → cache miss → RAG → distill → cloud → response → cache store
2. **Cache hit:** Query → cache hit → skip distillation entirely
3. **Local route:** Query → route to Ollama → skip distillation
4. **Small context:** Query → small RAG result → skip distillation
5. **Wave 3:** Multi-part query → sub-query distillation for cloud-routed parts

### Validation:
- [ ] Distillation integrates cleanly with full pipeline
- [ ] No regressions to existing query flow
- [ ] Metrics tracked accurately

---

## Task 12: Testing — Quality Validation
**Goal:** Verify distillation doesn't degrade response quality

### Test Cases:
1. Send 10 representative queries with and without distillation
2. Compare cloud LLM responses side-by-side
3. Check for:
   - Missing key facts in distilled version
   - Code snippets corrupted by distillation
   - Answers that are correct but less specific
4. Adjust target_ratio if quality degradation detected

### Validation:
- [ ] No critical information lost in distillation
- [ ] Code examples preserved accurately
- [ ] Response quality comparable (manual evaluation)

---

## Task 13: Documentation & Specs Update
**Goal:** Update relevant docs

### Subtasks:
1. Update architecture spec with distillation layer
2. Update project status
3. Add changelog entry
4. Archive this change folder

### Validation:
- [ ] All specs updated
- [ ] Changelog entry added

---

## Dependency Order

```
Task 1 (Config)
    ↓
Task 2 (OllamaDistillStrategy)
    ↓
Task 3 (ContextDistiller Module)
    ↓
Task 4 (Register with Compression Manager)
    ↓
Task 5 (Polly Init Integration)
    ↓
Task 6 (Pipeline Integration)
    ↓
Task 7 (AutonomyMetrics)
    ↓
Task 8 (Server Endpoints)
    ↓
Task 9 (Settings UI)
    ↓
Tasks 10-12 (Testing) ← can run in parallel
    ↓
Task 13 (Docs)
```

---

## Coordination Notes

### Depends on Phase 0 (Semantic Cache):
- Distillation is skipped on cache hits
- Cache stores the final response (post-distillation cloud response)
- Both phases share AutonomyMetrics integration

### Feeds into Phase 2 (Copilot FIM):
- Copilot FIM sends code context (prefix + suffix); the file header portion can be distilled
- Same OllamaDistillStrategy can compress code context for FIM requests

### Feeds into Phase 3 (Programmer Persona):
- Programmer persona's cloud-routed modes (refactor, generate, debug, review) benefit from distillation
- Explain mode (local Ollama) skips distillation automatically (cloud_only: true)
