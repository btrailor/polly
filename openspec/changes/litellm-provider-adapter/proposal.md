# Proposal: LiteLLM Provider Adapter

## What
Replace Polly's 7 individual provider adapter files with a unified `LiteLLMAdapter` that wraps LiteLLM's API while maintaining full compatibility with `IntelligentRouterV2`.

## Why
**Current state:** 7 separate provider files (`anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `mistral_provider.py`, `grok_provider.py`, `perplexity_provider.py`, `github_provider.py`), each implementing the `ProviderAdapter` ABC with 400-500 lines of similar code:
- API client initialization
- Error mapping to Polly's error hierarchy
- Token counting and cost calculation
- Streaming support
- Model catalog management

**Problem:**
1. **Maintenance burden:** Changes to error handling, logging, or response format require updating 7 files
2. **Code duplication:** ~70% of each provider's code is identical (error mapping, cost calculation)
3. **New provider overhead:** Adding a new provider requires 400+ lines of boilerplate
4. **Testing complexity:** 7 separate test suites with overlapping coverage

**Solution:** LiteLLM provides a unified interface to 100+ providers with automatic:
- Error normalization (OpenAI-compatible errors)
- Token counting via tiktoken
- Cost tracking with built-in pricing database
- Streaming support
- Automatic retries and fallbacks

**Benefits:**
1. **90% code reduction:** Single 300-line `LiteLLMAdapter` vs 7 × 400 lines
2. **Zero breaking changes:** Maintains `ProviderAdapter` interface; `IntelligentRouterV2` unchanged
3. **Easy expansion:** Adding new providers = configuration change only
4. **Better error handling:** LiteLLM normalizes provider-specific errors
5. **Automatic updates:** LiteLLM team maintains provider integrations and pricing

## Scope

### Backend (Python)
- **New file:** `core/providers/litellm_adapter.py`
- **Modified:** `requirements.txt`, `config/approved_packages.yaml`
- **Modified:** `core/router_v2.py` (only initialization - uses LiteLLMAdapter instead of individual adapters)
- **Deprecated (not deleted):** Existing 7 provider files remain for backward compatibility

### Frontend
- **No changes:** This is purely a backend refactor

### Related Phase
- **Tier 2, Phase 11 (Multi-Provider System):** Enhances existing multi-provider routing with unified implementation
- **Phase 23.5 (Security Hardening):** Adds LiteLLM to approved packages

## Migration Strategy
1. **Phase 1:** Implement `LiteLLMAdapter` alongside existing providers
2. **Phase 2:** Update router initialization to use `LiteLLMAdapter`
3. **Phase 3:** Test against all 7 providers
4. **Phase 4 (optional):** Deprecate old provider files after validation period

## Non-Goals
- Changing the `ProviderAdapter` ABC interface
- Modifying `IntelligentRouterV2` routing logic
- Altering budget tracking mechanisms
- Breaking changes to existing API contracts
