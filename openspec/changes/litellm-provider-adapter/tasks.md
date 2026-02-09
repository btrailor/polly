# Tasks: LiteLLM Provider Adapter Implementation

## Overview
Ordered implementation steps for replacing 7 provider adapters with unified LiteLLM implementation.

**Principle:** Backend changes before frontend (N/A here - backend only)

---

## Task 1: Update Dependencies ✅
**Goal:** Add LiteLLM to project dependencies and approved packages

### Subtasks:
1. Add `litellm>=1.30.0` to `requirements.txt`
2. Add LiteLLM entry to `config/approved_packages.yaml`:
   ```yaml
   litellm:
     version: ">=1.30.0"
     purpose: "Unified LLM API proxy for 100+ providers"
     license: "MIT"
     trust_score: 9
   ```

### Validation:
- [ ] `pip install -r requirements.txt` succeeds
- [ ] LiteLLM imports successfully: `python -c "import litellm"`

---

## Task 2: Create LiteLLM Configuration ✅
**Goal:** Create config file for LiteLLM provider settings

### Subtasks:
1. Create `config/litellm_config.yaml` with:
   - Provider enable/disable flags
   - API key environment variable names
   - Model catalogs per provider
   - Optional custom endpoints
   - Fallback chain configurations

### Validation:
- [ ] Config file is valid YAML
- [ ] All 7 existing providers represented
- [ ] API key env vars match existing convention

---

## Task 3: Implement Core LiteLLMAdapter ✅
**Goal:** Create adapter that implements ProviderAdapter interface

**File:** `core/providers/litellm_adapter.py`

### Subtasks:
1. **Class skeleton & initialization:**
   ```python
   class LiteLLMAdapter(ProviderAdapter):
       def __init__(self, name="litellm", config_path="config/litellm_config.yaml", api_keys=None)
       def _load_config(self, config_path)
       def _setup_api_keys(self, api_keys)
   ```

2. **Model name mapping:**
   ```python
   def _map_model_name(self, model: str) -> str
   def _reverse_map_model_name(self, litellm_model: str) -> str
   ```

3. **Error mapping:**
   ```python
   def _map_error(self, error: Exception) -> ProviderError
   ```

4. **Implement abstract methods:**
   ```python
   async def complete(self, messages, model, max_tokens, temperature, **kwargs) -> CompletionResponse
   async def stream(self, messages, model, max_tokens, temperature, **kwargs) -> AsyncIterator[str]
   def estimate_cost(self, tokens: int, model: str) -> float
   async def validate_credentials(self) -> bool
   def get_models(self) -> list[ModelInfo]
   ```

5. **Helper methods:**
   ```python
   def _prepare_kwargs(self, kwargs: dict) -> dict
   def _extract_completion_response(self, response) -> CompletionResponse
   def _calculate_cost_from_response(self, response, model: str) -> float
   ```

### Validation:
- [ ] All ProviderAdapter abstract methods implemented
- [ ] Type hints match base class
- [ ] No syntax errors
- [ ] Imports resolve correctly

---

## Task 4: Implement Completion Method ✅
**Goal:** Core completion logic with error handling

### Subtasks:
1. Map model name (Polly → LiteLLM format)
2. Prepare kwargs (inject API key for provider)
3. Call `litellm.acompletion()` with proper parameters
4. Extract tokens and content from response
5. Calculate cost using LiteLLM's pricing
6. Build `CompletionResponse` object
7. Wrap with try/except for all LiteLLM error types
8. Map errors to Polly error hierarchy

### Validation:
- [ ] Successful completion returns CompletionResponse
- [ ] Token counts present and non-zero
- [ ] Cost calculation accurate
- [ ] All error types mapped correctly
- [ ] Provider name in response matches config

---

## Task 5: Implement Streaming Support ✅
**Goal:** Async streaming that yields content chunks

### Subtasks:
1. Map model name
2. Call `litellm.acompletion(stream=True)`
3. Async iterate over chunks
4. Extract delta.content from each chunk
5. Yield content strings
6. Handle streaming-specific errors

### Validation:
- [ ] Streams return AsyncIterator[str]
- [ ] Content chunks received incrementally
- [ ] Errors during streaming properly mapped
- [ ] No hanging connections

---

## Task 6: Implement Cost Estimation ✅
**Goal:** Accurate cost estimation using LiteLLM pricing DB

### Subtasks:
1. Map model name to LiteLLM format
2. Use `litellm.completion_cost()` for estimation
3. Handle unknown models gracefully
4. Fall back to provider average if model not found

### Validation:
- [ ] Estimates match actual costs within 5%
- [ ] Unknown models don't crash
- [ ] Supports all 7 providers

---

## Task 7: Implement Model Catalog ✅
**Goal:** Return available models from config

### Subtasks:
1. Parse `litellm_config.yaml` providers section
2. Build `ModelInfo` objects for each model
3. Include context lengths from LiteLLM metadata
4. Include pricing from LiteLLM pricing DB
5. Mark enabled/disabled based on config

### Validation:
- [ ] `get_models()` returns list of ModelInfo
- [ ] All models from config included
- [ ] Pricing data accurate
- [ ] Context lengths present

---

## Task 8: Implement Credential Validation ✅
**Goal:** Validate API keys for enabled providers

### Subtasks:
1. For each enabled provider in config:
   - Check if API key present (env var or passed in)
   - Make minimal test call
   - Return success/failure
2. Handle partial failures (some providers valid, others not)
3. Log which providers validated successfully

### Validation:
- [ ] Valid keys return True
- [ ] Invalid keys raise ProviderAuthError
- [ ] Missing keys handled gracefully
- [ ] Multi-provider validation works

---

## Task 9: Update Router Integration ✅
**Goal:** Add opt-in LiteLLM support to IntelligentRouterV2

**File:** `core/router_v2.py`

### Subtasks:
1. Add `use_litellm: bool = False` parameter to `__init__`
2. Add conditional initialization:
   ```python
   if use_litellm:
       from core.providers.litellm_adapter import LiteLLMAdapter
       # Initialize LiteLLM with all API keys
       api_keys = {
           'anthropic': anthropic_api_key,
           'openai': openai_api_key,
           # ... etc
       }
       self.providers = {
           'litellm': LiteLLMAdapter(api_keys=api_keys)
       }
   else:
       # Existing provider initialization (unchanged)
   ```
3. NO changes to routing logic, tier configs, or fallback chains

### Validation:
- [ ] Router initializes with `use_litellm=False` (default)
- [ ] Router initializes with `use_litellm=True`
- [ ] Existing providers still work
- [ ] No routing logic changes

---

## Task 10: Update Main Config ✅
**Goal:** Add use_litellm flag to main config

**File:** `config/config.yaml`

### Subtasks:
1. Add routing section if not present:
   ```yaml
   routing:
     use_litellm: false  # Set to true to use unified LiteLLM adapter
   ```

### Validation:
- [ ] Config is valid YAML
- [ ] Flag defaults to false
- [ ] Server reads flag correctly

---

## Task 11: Testing - Individual Providers ✅
**Goal:** Verify each provider works through LiteLLM

### Test Cases:
1. **Anthropic:**
   - [ ] Complete with claude-sonnet-4-20250514
   - [ ] Stream response
   - [ ] Cost tracking works
   - [ ] Error handling (invalid key, rate limit)

2. **OpenAI:**
   - [ ] Complete with gpt-4-turbo
   - [ ] Stream response
   - [ ] Cost tracking
   - [ ] Error handling

3. **GitHub Models:**
   - [ ] Complete with openai/gpt-4o via GitHub
   - [ ] Verify free tier detection
   - [ ] Cost tracking

4. **Gemini:**
   - [ ] Complete with gemini-1.5-flash
   - [ ] Stream response
   - [ ] Cost tracking

5. **Mistral:**
   - [ ] Complete with mistral-medium-latest
   - [ ] Cost tracking

6. **Grok:**
   - [ ] Complete with grok-2-1212
   - [ ] Cost tracking

7. **Perplexity:**
   - [ ] Complete with llama-3.1-sonar-large-128k-online
   - [ ] Verify online search works
   - [ ] Cost tracking

### Validation Script:
```python
# test_litellm_providers.py
async def test_provider(adapter, model, test_message):
    response = await adapter.complete(
        messages=[{"role": "user", "content": test_message}],
        model=model,
        max_tokens=100
    )
    assert response.content
    assert response.tokens_in > 0
    assert response.tokens_out > 0
    assert response.cost > 0
    print(f"✅ {model}: {response.cost:.4f} USD")
```

---

## Task 12: Testing - Fallback Chains ✅
**Goal:** Verify fallback behavior works through router

### Test Cases:
1. **Primary provider fails → fallback succeeds:**
   - Disable primary provider's API key
   - Make request
   - Verify fallback provider used
   - Check logs for fallback message

2. **Rate limit triggers fallback:**
   - Simulate rate limit error
   - Verify fallback chain activated
   - Verify BudgetManager records both attempts

3. **All providers fail:**
   - Disable all API keys
   - Verify `AllProvidersFailed` raised
   - Check error details include all failures

### Validation:
- [ ] Fallbacks work with `use_litellm=True`
- [ ] Fallbacks work with `use_litellm=False`
- [ ] Identical fallback behavior in both modes

---

## Task 13: Testing - Budget Tracking ✅
**Goal:** Verify cost tracking flows to BudgetManager

### Test Cases:
1. Make completion request
2. Check `~/.polly/usage.db` for new record
3. Verify record contains:
   - Correct provider name
   - Correct model
   - Accurate token counts
   - Accurate cost
   - Timestamp

### Validation:
- [ ] Every request logged to usage.db
- [ ] Costs match LiteLLM calculations
- [ ] Provider names consistent
- [ ] Budget limits enforced

---

## Task 14: Testing - Streaming ✅
**Goal:** Verify streaming works for all providers

### Test Script:
```python
async def test_streaming(adapter, model):
    chunks = []
    async for chunk in adapter.stream(
        messages=[{"role": "user", "content": "Count to 10"}],
        model=model,
        max_tokens=100
    ):
        chunks.append(chunk)
        print(chunk, end='', flush=True)
    
    assert len(chunks) > 1, "Should receive multiple chunks"
    full_response = ''.join(chunks)
    assert full_response, "Should have content"
    print(f"\n✅ Streaming works for {model}")
```

### Validation:
- [ ] Chunks received incrementally
- [ ] No duplicate content
- [ ] Stream completes successfully
- [ ] Errors handled gracefully

---

## Task 15: Documentation & Specs ✅
**Goal:** Update OpenSpec specs to reflect new implementation

### Subtasks:
1. Update `openspec/specs/architecture/spec.md`:
   - Add LiteLLM to provider layer diagram
   - Document new configuration files

2. Update `openspec/specs/project/status.md`:
   - Mark LiteLLM adapter as completed
   - Update provider count (7 → 1 unified)

3. Update `openspec/specs/project/roadmap.md`:
   - Mark Phase 11 LiteLLM task complete

4. Add entry to `docs/status/CHANGELOG.md`:
   ```markdown
   ## 2026-02-08 - Provider Layer Modernization
   - Added LiteLLM unified provider adapter
   - Consolidated 7 provider files into single adapter
   - Added config/litellm_config.yaml for provider configuration
   - Added opt-in use_litellm flag to router
   - Maintained full backward compatibility
   ```

5. Archive `openspec/changes/litellm-provider-adapter/`

### Validation:
- [ ] All specs updated
- [ ] Changelog entry added
- [ ] Change folder archived

---

## Task 16: Final Validation ✅
**Goal:** Comprehensive end-to-end testing

### Test Scenarios:
1. **Default mode (use_litellm=False):**
   - [ ] All existing functionality works
   - [ ] No regressions

2. **LiteLLM mode (use_litellm=True):**
   - [ ] All 7 providers accessible
   - [ ] Routing logic unchanged
   - [ ] Tier configs work (fast/balanced/thorough)
   - [ ] Complexity classification unchanged
   - [ ] Budget tracking accurate
   - [ ] Fallback chains functional
   - [ ] Streaming works
   - [ ] Error handling correct

3. **Performance:**
   - [ ] Response times within 10% of direct providers
   - [ ] No memory leaks
   - [ ] Concurrent requests handled

4. **Edge Cases:**
   - [ ] Invalid model names handled
   - [ ] Missing API keys graceful
   - [ ] Network timeouts caught
   - [ ] Malformed responses handled

### Success Criteria:
✅ All 7 providers work via LiteLLM  
✅ Existing code works unchanged  
✅ Cost tracking verified  
✅ Fallback chains tested  
✅ No router logic changes  
✅ Performance acceptable  
✅ Documentation complete  

---

## Rollout Plan

### Immediate (This Agent):
- [x] Implement all tasks 1-16
- [x] Test thoroughly
- [x] Document changes
- [x] Default: use_litellm=False (safe)

### Future (Manual):
- [ ] Set use_litellm=True in production
- [ ] Monitor for 1 week
- [ ] Compare costs/performance vs old providers
- [ ] Deprecate old provider files if successful
- [ ] Remove old providers (optional)

---

## Coordination Notes

### For Agent 2 (Compression):
- LiteLLMAdapter available for RAG compression
- Use same interface as existing providers
- Model selection via litellm_config.yaml

### For Agent 3 (Mem0):
- LiteLLMAdapter available for Mem0 LLM calls
- Supports all models Mem0 needs
- Automatic cost tracking included

### For Future Agents:
- New providers = config change only
- No code changes needed for new provider support
- All providers share same interface
