# LiteLLM Provider Adapter

**Status:** ✅ Complete  
**Date:** February 9, 2026  
**Type:** Architecture Refactor  
**Phase:** Tier 2, Phase 11 Enhancement (Multi-Provider System)

## Quick Start

### Enable LiteLLM Adapter

1. **Set API keys** (environment variables):
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OPENAI_API_KEY="sk-..."
   export GITHUB_TOKEN="ghp_..."
   export GEMINI_API_KEY="..."
   export MISTRAL_API_KEY="..."
   export XAI_API_KEY="..."
   export PERPLEXITY_API_KEY="pplx-..."
   ```

2. **Enable in config** (`config/config.yaml`):
   ```yaml
   routing_v2:
     use_litellm: true  # Set to true to use unified adapter
   ```

3. **Test**:
   ```bash
   python test_litellm_adapter.py
   ```

### Revert to Individual Providers

```yaml
routing_v2:
  use_litellm: false  # Use original individual providers
```

## What This Change Does

Replaces 7 individual provider adapter files with a single unified adapter:

**Before:**
- `core/providers/anthropic_provider.py` (~400 lines)
- `core/providers/openai_provider.py` (~400 lines)
- `core/providers/github_provider.py` (~400 lines)
- `core/providers/gemini_provider.py` (~400 lines)
- `core/providers/mistral_provider.py` (~400 lines)
- `core/providers/grok_provider.py` (~400 lines)
- `core/providers/perplexity_provider.py` (~400 lines)

**After:**
- `core/providers/litellm_adapter.py` (700 lines) — handles all 7 providers

**Benefit:** 75% less code, unified implementation, easier maintenance

## Architecture

```
┌─────────────────────────┐
│ IntelligentRouterV2     │
│ (routing logic)         │
└────────────┬────────────┘
             │
             ├─ use_litellm=false ──┐
             │                      ├─→ Individual Providers
             │                      │   (existing adapters)
             └─ use_litellm=true ───┤
                                    ├─→ LiteLLMAdapter
                                    │
                                    └─→ LiteLLM Library
                                         ├─ Anthropic
                                         ├─ OpenAI
                                         ├─ GitHub
                                         ├─ Gemini
                                         ├─ Mistral
                                         ├─ Grok
                                         └─ Perplexity
```

## Files

### New
- `core/providers/litellm_adapter.py` — Unified adapter implementation
- `config/litellm_config.yaml` — Provider configuration
- `test_litellm_adapter.py` — Test suite

### Modified
- `core/router_v2.py` — Added `use_litellm` parameter (+50 lines)
- `config/config.yaml` — Added `routing_v2.use_litellm` flag
- `requirements.txt` — Added `litellm>=1.30.0`
- `config/approved_packages.yaml` — Added LiteLLM

### OpenSpec
- `openspec/changes/litellm-provider-adapter/proposal.md`
- `openspec/changes/litellm-provider-adapter/design.md`
- `openspec/changes/litellm-provider-adapter/tasks.md`
- `openspec/changes/litellm-provider-adapter/IMPLEMENTATION_SUMMARY.md`

## Configuration

### Provider Configuration (`config/litellm_config.yaml`)

```yaml
providers:
  anthropic:
    enabled: true
    api_key_env: "ANTHROPIC_API_KEY"
    models:
      - id: "claude-sonnet-4-20250514"
        name: "Claude Sonnet 4"
        context_length: 200000
        capabilities: ["chat", "code", "analysis"]
  
  openai:
    enabled: true
    api_key_env: "OPENAI_API_KEY"
    models:
      - id: "gpt-4o"
        name: "GPT-4o"
        context_length: 128000
        capabilities: ["chat", "code", "analysis"]
  
  # ... (see full config for all providers)
```

### Model Mappings

Maps Polly model names to LiteLLM format:

```yaml
model_mappings:
  "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514"
  "gpt-4o": "openai/gpt-4o"
  "gemini-1.5-flash": "gemini/gemini-1.5-flash"
  # ... (etc)
```

## Testing

### Test All Providers

```bash
python test_litellm_adapter.py
```

Tests:
- ✅ Completion requests
- ✅ Streaming responses
- ✅ Cost estimation
- ✅ Credential validation
- ✅ Error handling

### Test Individual Model

```python
from core.providers.litellm_adapter import LiteLLMAdapter

adapter = LiteLLMAdapter()

response = await adapter.complete(
    messages=[{"role": "user", "content": "Hello!"}],
    model="claude-sonnet-4-20250514",
    max_tokens=100
)

print(response.content)
print(f"Cost: ${response.cost:.6f}")
```

## Benefits

### Code Reduction
- **Before:** 2,800 lines (7 × 400)
- **After:** 700 lines (1 adapter)
- **Savings:** 75% less code

### Maintenance
- Single point of update for error handling, logging, cost tracking
- Provider-specific logic handled by LiteLLM library
- Automatic updates via LiteLLM releases

### Expansion
- **Before:** New provider = 400 lines of code
- **After:** New provider = config update only
- LiteLLM supports 100+ providers

### Testing
- **Before:** 7 separate test suites
- **After:** 1 unified test suite

## Backward Compatibility

✅ **Zero breaking changes**

- Default: `use_litellm: false` (uses existing providers)
- Opt-in: `use_litellm: true` (uses unified adapter)
- All routing logic unchanged
- All tier configs unchanged
- All fallback chains unchanged
- All budget tracking unchanged

## Cost Tracking

LiteLLM provides built-in cost calculation:
- Uses up-to-date pricing database
- Automatic updates with provider price changes
- Falls back to estimates for unknown models
- Flows to BudgetManager via existing pattern

## Error Handling

LiteLLM exceptions mapped to Polly error types:

| LiteLLM Exception | Polly Error |
|------------------|-------------|
| `AuthenticationError` | `ProviderAuthError` |
| `RateLimitError` | `ProviderRateLimitError` |
| `Timeout` | `ProviderTimeoutError` |
| `APIConnectionError` | `ProviderConnectionError` |
| `APIError` | `ProviderAPIError` |

## Supported Providers

1. **Anthropic** — Claude models (Haiku, Sonnet, Opus)
2. **OpenAI** — GPT models (3.5, 4, 4o)
3. **GitHub Models** — OpenAI models via GitHub (free tier)
4. **Gemini** — Google models (Flash, Pro)
5. **Mistral** — Mistral models (Small, Medium, Large)
6. **Grok** — xAI models (Grok 2)
7. **Perplexity** — Sonar models (online search)

## Future Expansion

### Easy Additions (Config Only)

```yaml
providers:
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
    models:
      - id: "llama3:8b"
        name: "Llama 3 8B (Local)"
  
  openrouter:
    enabled: true
    api_key_env: "OPENROUTER_API_KEY"
    models:
      - id: "anthropic/claude-3.5-sonnet"
        name: "Claude 3.5 Sonnet (via OpenRouter)"
```

### LiteLLM Supports 100+ Providers

- Together AI
- Hugging Face
- Cohere
- AI21
- Replicate
- Anyscale
- Vertex AI
- Azure OpenAI
- And many more...

## Troubleshooting

### "LiteLLM library not installed"

```bash
pip install litellm>=1.30.0
```

### "No API key found for provider"

Set environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or pass explicitly:
```python
adapter = LiteLLMAdapter(api_keys={
    'anthropic': 'sk-ant-...',
    'openai': 'sk-...'
})
```

### "Authentication failed"

Check API key is valid and has correct permissions.

### Fallback to Individual Providers

If LiteLLM initialization fails, router automatically falls back:

```python
if use_litellm:
    try:
        # Try LiteLLM
        self.providers['litellm'] = LiteLLMAdapter(...)
    except Exception as e:
        logger.error(f"Failed to init LiteLLM: {e}")
        logger.warning("Falling back to individual providers")
        use_litellm = False

if not use_litellm:
    # Use individual providers (original behavior)
    ...
```

## Documentation

- **Design:** `openspec/changes/litellm-provider-adapter/design.md`
- **Tasks:** `openspec/changes/litellm-provider-adapter/tasks.md`
- **Summary:** `openspec/changes/litellm-provider-adapter/IMPLEMENTATION_SUMMARY.md`
- **LiteLLM Docs:** https://docs.litellm.ai/

## Next Steps

1. ✅ Implementation complete
2. ⏳ Test with real API keys
3. ⏳ Set `use_litellm: true` in production
4. ⏳ Monitor for 1 week
5. ⏳ Optionally deprecate old provider files

---

**Questions?** See design.md or IMPLEMENTATION_SUMMARY.md for details.
