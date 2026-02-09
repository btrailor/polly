# Design: LiteLLM Provider Adapter

## Overview
Create a unified provider adapter using LiteLLM that maintains compatibility with Polly's existing `ProviderAdapter` interface and `IntelligentRouterV2` routing system.

## Architecture

### Component Diagram
```
IntelligentRouterV2
    ↓
LiteLLMAdapter (implements ProviderAdapter)
    ↓
LiteLLM Library
    ↓
[Anthropic, OpenAI, Gemini, Mistral, Grok, Perplexity, GitHub Models]
```

### Key Design Decisions

#### 1. Interface Compatibility
**Decision:** `LiteLLMAdapter` implements the existing `ProviderAdapter` ABC without modifications.

**Rationale:**
- Zero breaking changes to `IntelligentRouterV2`
- Backward compatibility maintained
- Can run alongside existing providers during migration

**Impact:**
- Must map LiteLLM responses to `CompletionResponse` format
- Must translate Polly error types from LiteLLM exceptions
- Must implement all abstract methods: `complete()`, `stream()`, `estimate_cost()`, `validate_credentials()`, `get_models()`

#### 2. Model Naming Convention
**Decision:** Use LiteLLM's provider-prefixed format internally, map from Polly's format at adapter boundary.

**Mapping Strategy:**
```python
POLLY_TO_LITELLM_MODELS = {
    # Anthropic
    "claude-3-haiku-20240307": "anthropic/claude-3-haiku-20240307",
    "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514",
    "claude-opus-4-20250514": "anthropic/claude-opus-4-20250514",
    
    # OpenAI
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gpt-4o": "openai/gpt-4o",
    
    # GitHub Models (use OpenAI models via GitHub)
    "openai/gpt-4o-mini": "github/gpt-4o-mini",
    "openai/gpt-4o": "github/gpt-4o",
    
    # Gemini
    "gemini-1.5-flash": "gemini/gemini-1.5-flash",
    "gemini-1.5-flash-8b": "gemini/gemini-1.5-flash-8b",
    "gemini-1.5-pro": "gemini/gemini-1.5-pro",
    
    # Mistral
    "mistral-small-latest": "mistral/mistral-small-latest",
    "mistral-medium-latest": "mistral/mistral-medium-latest",
    "mistral-large-latest": "mistral/mistral-large-latest",
    
    # Grok (xAI)
    "grok-2-1212": "xai/grok-2-1212",
    
    # Perplexity
    "llama-3.1-sonar-small-128k-online": "perplexity/llama-3.1-sonar-small-128k-online",
    "llama-3.1-sonar-large-128k-online": "perplexity/llama-3.1-sonar-large-128k-online",
    "llama-3.1-sonar-huge-128k-online": "perplexity/llama-3.1-sonar-huge-128k-online",
}
```

#### 3. Error Mapping
**Decision:** Map LiteLLM exceptions to Polly's error hierarchy at adapter boundary.

**Mapping:**
```python
# LiteLLM → Polly Error Mapping
litellm.AuthenticationError → ProviderAuthError
litellm.RateLimitError → ProviderRateLimitError
litellm.Timeout → ProviderTimeoutError
litellm.APIConnectionError → ProviderConnectionError
litellm.APIError → ProviderAPIError
litellm.ServiceUnavailableError → ProviderConnectionError
```

#### 4. Cost Tracking Integration
**Decision:** Use LiteLLM's built-in cost calculation, pipe to BudgetManager via existing pattern.

**Implementation:**
- LiteLLM provides `response_cost` in completion response
- Fall back to LiteLLM's `completion_cost()` function if not present
- Pass to BudgetManager through router's existing `record_usage()` flow

**Rationale:**
- LiteLLM maintains up-to-date pricing database
- Automatic updates when providers change pricing
- Consistent with existing budget tracking flow

#### 5. Streaming Support
**Decision:** Wrap LiteLLM's streaming API with async iterator.

**Implementation:**
```python
async def stream(self, messages, model, max_tokens, temperature, **kwargs):
    litellm_model = self._map_model_name(model)
    
    response = await litellm.acompletion(
        model=litellm_model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
        **self._prepare_kwargs(kwargs)
    )
    
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

#### 6. Configuration Management
**Decision:** Create separate `config/litellm_config.yaml` for LiteLLM-specific settings.

**Structure:**
```yaml
providers:
  anthropic:
    enabled: true
    api_key_env: "ANTHROPIC_API_KEY"
    models: [...]
  
  openai:
    enabled: true
    api_key_env: "OPENAI_API_KEY"
    models: [...]

# Optional: Custom base URLs for self-hosted
custom_endpoints:
  ollama:
    base_url: "http://localhost:11434"
  openrouter:
    base_url: "https://openrouter.ai/api/v1"

# Optional: Fallback configurations
fallback_chains:
  fast: ["anthropic/claude-3-haiku-20240307", "openai/gpt-3.5-turbo"]
  balanced: ["anthropic/claude-sonnet-4-20250514", "openai/gpt-4-turbo"]
  thorough: ["anthropic/claude-opus-4-20250514", "openai/gpt-4o"]
```

#### 7. Router Integration Strategy
**Decision:** Add opt-in flag to use LiteLLM, default to existing providers.

**Implementation in router_v2.py:**
```python
def __init__(self, ..., use_litellm: bool = False):
    if use_litellm:
        # Single unified adapter
        self.providers = {
            'litellm': LiteLLMAdapter(config_path='config/litellm_config.yaml')
        }
    else:
        # Existing provider initialization
        if anthropic_api_key:
            self.providers['anthropic'] = AnthropicAdapter(anthropic_api_key)
        # ... etc
```

**Rationale:**
- Safe migration path
- Easy rollback if issues arise
- Can A/B test performance
- NO changes to routing logic itself

## API Design

### LiteLLMAdapter Class

```python
class LiteLLMAdapter(ProviderAdapter):
    """
    Unified provider adapter using LiteLLM
    
    Supports 100+ providers through LiteLLM's unified API while
    maintaining compatibility with Polly's ProviderAdapter interface.
    """
    
    def __init__(
        self,
        name: str = "litellm",
        config_path: str = "config/litellm_config.yaml",
        api_keys: Optional[Dict[str, str]] = None
    ):
        """
        Initialize LiteLLM adapter
        
        Args:
            name: Adapter name (default: "litellm")
            config_path: Path to litellm_config.yaml
            api_keys: Optional dict of provider API keys
                     (falls back to environment variables)
        """
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete via LiteLLM
        
        Maps model name, calls litellm.acompletion(), 
        returns CompletionResponse
        """
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion tokens via LiteLLM"""
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """Estimate cost using LiteLLM's pricing database"""
    
    async def validate_credentials(self) -> bool:
        """Validate provider API keys"""
    
    def get_models(self) -> list[ModelInfo]:
        """Get available models from config"""
    
    # Private helper methods
    def _map_model_name(self, model: str) -> str:
        """Map Polly model name to LiteLLM format"""
    
    def _map_error(self, error: Exception) -> ProviderError:
        """Map LiteLLM exception to Polly error type"""
    
    def _prepare_kwargs(self, kwargs: dict) -> dict:
        """Prepare kwargs for LiteLLM (API key injection, etc.)"""
    
    def _load_config(self, config_path: str) -> dict:
        """Load litellm_config.yaml"""
```

## Data Flow

### 1. Normal Completion Request
```
Router.complete_with_fallback()
    ↓
LiteLLMAdapter.complete(messages, model="claude-sonnet-4-20250514")
    ↓
_map_model_name() → "anthropic/claude-sonnet-4-20250514"
    ↓
litellm.acompletion(model="anthropic/...", api_key=...)
    ↓
Map response → CompletionResponse
    ↓
Return to router
    ↓
BudgetManager.record_usage()
```

### 2. Streaming Request
```
Router → LiteLLMAdapter.stream()
    ↓
litellm.acompletion(stream=True)
    ↓
async for chunk → yield chunk.delta.content
    ↓
Stream to caller
```

### 3. Error Handling
```
litellm.RateLimitError raised
    ↓
_map_error() → ProviderRateLimitError
    ↓
Router catches ProviderRateLimitError
    ↓
Router tries fallback chain (existing logic)
```

## Files to Create/Modify

### New Files
1. `core/providers/litellm_adapter.py` (~350 lines)
2. `config/litellm_config.yaml` (~100 lines)

### Modified Files
1. `requirements.txt` (add litellm>=1.30.0)
2. `config/approved_packages.yaml` (add litellm entry)
3. `core/router_v2.py` (add use_litellm parameter, ~20 line change)
4. `config/config.yaml` (add routing.use_litellm: false)

### Unchanged Files (Important!)
- `core/providers/base.py` - NO changes
- All existing provider files - kept for backward compatibility
- `core/budget_manager.py` - NO changes
- Router routing logic - NO changes to tier configs, complexity classification, fallback chains

## Testing Strategy

### Unit Tests
1. Model name mapping (Polly format → LiteLLM format)
2. Error mapping (LiteLLM exceptions → Polly errors)
3. Cost estimation via LiteLLM's pricing DB
4. Config loading and validation

### Integration Tests
1. Complete request through each of 7 providers
2. Streaming response from each provider
3. Cost tracking to BudgetManager
4. Fallback chain with intentional failures
5. API key loading from environment variables

### Validation Tests
1. Compare responses: LiteLLM vs. existing providers
2. Verify identical token counts
3. Verify identical costs
4. Verify identical error behavior

## Rollout Plan

### Phase 1: Implementation (This Agent)
- Create LiteLLMAdapter
- Create config files
- Update dependencies
- Add router flag (default: OFF)

### Phase 2: Testing (This Agent)
- Test all 7 providers
- Verify cost tracking
- Test fallback chains
- Validate against existing providers

### Phase 3: Migration (Future)
- Set use_litellm: true in production
- Monitor for 1 week
- Deprecate old providers if successful
- Remove old provider files (optional)

## Risk Mitigation

### Risk: LiteLLM version changes break compatibility
**Mitigation:** Pin to specific version range (>=1.30.0,<2.0.0)

### Risk: Cost calculations differ from existing providers
**Mitigation:** 
- Extensive testing with known requests
- Validate against existing provider costs
- Log cost discrepancies for review

### Risk: Provider-specific features lost
**Mitigation:**
- LiteLLM supports provider-specific kwargs
- Pass through unsupported kwargs with warning
- Document any feature gaps in config

### Risk: Performance degradation
**Mitigation:**
- Benchmark response times vs existing providers
- LiteLLM adds minimal overhead (<10ms)
- Can revert to existing providers via flag

## Success Metrics

1. ✅ All 7 providers work through LiteLLM
2. ✅ Cost tracking accurate within 1%
3. ✅ Fallback chains functional
4. ✅ No breaking changes to existing code
5. ✅ Response times within 10% of direct provider calls
6. ✅ Zero router logic changes required
