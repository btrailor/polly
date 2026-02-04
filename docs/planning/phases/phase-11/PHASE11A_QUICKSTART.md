# Phase 11a Quick Start Guide

**Status:** ✅ Complete and ready to test  
**Date:** January 28, 2026

## What's New

Phase 11a adds multi-provider intelligent routing with:

- **Three-tier routing**: Fast, Balanced, Thorough
- **Two providers**: Anthropic Claude and OpenAI GPT
- **Secure key management**: System keyring + encrypted fallback
- **Budget tracking**: Daily/monthly limits with automatic enforcement
- **Fallback chains**: Automatic failover on errors
- **Web UI**: Beautiful settings interface at `/settings`

## Quick Start (5 minutes)

### 1. Activate Virtual Environment

```bash
cd /Users/brettgershon/polly
source venv/bin/activate
```

### 2. Verify Dependencies

All dependencies are already installed:
- ✅ keyring (secure storage)
- ✅ cryptography (encryption)
- ✅ anthropic (Claude API)
- ✅ openai (GPT API)

### 3. Add Your API Keys

**Option A: Web UI (Recommended)**
```bash
python3 -m interfaces.cli serve
# Open http://localhost:11436/settings
# Click "Add API Key" and enter your keys
```

**Option B: CLI**
```bash
python3 -m interfaces.cli keys set anthropic
# Enter your sk-ant-api03-... key

python3 -m interfaces.cli keys set openai
# Enter your sk-... key
```

**Option C: Setup Script**
```bash
python3 setup_keys.py
# Follow the interactive wizard
```

### 4. Run Tests

```bash
python3 test_phase11a.py
```

This will test:
1. ✅ Secrets Manager (API key storage)
2. ✅ Budget Manager (spending tracking)
3. ✅ Router V2 (intelligent routing)
4. ✅ Routing decisions
5. ✅ Real API call (with your permission)
6. ✅ Provider statistics

### 5. Try the Example

```bash
python3 examples/test_routing_v2.py
```

This demonstrates:
- All three confidence levels (fast, balanced, thorough)
- Budget tracking
- Fallback chains
- Provider statistics

## Web UI Features

Access the settings UI at `http://localhost:11436/settings`:

### API Keys Tab
- ✅ View all providers and their status
- ✅ Add/update API keys with validation
- ✅ Test connections with one click
- ✅ Delete keys
- ✅ See storage type (Keyring/File/Environment)

### Budget & Usage Tab
- ✅ Daily/monthly budget progress bars
- ✅ Total cost, requests, tokens
- ✅ Breakdown by provider and model
- ✅ Update budget limits
- ✅ Color-coded warnings

### Provider Info Tab
- ℹ️ Provider descriptions
- ℹ️ Key format examples
- ℹ️ Links to get API keys

## CLI Commands

```bash
# List API keys
python3 -m interfaces.cli keys list

# Set API key (secure prompt)
python3 -m interfaces.cli keys set <provider>

# Test API key
python3 -m interfaces.cli keys test [provider]

# Delete API key
python3 -m interfaces.cli keys delete <provider>

# Start server
python3 -m interfaces.cli serve
```

## Configuration

Edit `config.yaml` to customize:

```yaml
routing_v2:
  enabled: true
  default_confidence: balanced
  
  budget:
    daily_limit: 10.00      # Change this
    monthly_limit: 200.00   # Change this
    warn_at_percent: 80
  
  tiers:
    fast:
      max_cost_per_request: 0.01
    balanced:
      max_cost_per_request: 0.10
    thorough:
      max_cost_per_request: 1.00
```

## Usage Examples

### Example 1: Simple Query

```python
from core.router_v2 import IntelligentRouterV2, ConfidenceLevel
from core.secrets_manager import get_secrets_manager

# Get API keys
secrets = get_secrets_manager()
keys = secrets.get_all_provider_keys()

# Initialize router
router = IntelligentRouterV2(
    anthropic_api_key=keys['anthropic'],
    openai_api_key=keys['openai']
)

# Make request
messages = [{"role": "user", "content": "Explain Python decorators"}]
response = await router.complete_with_fallback(
    messages=messages,
    confidence=ConfidenceLevel.BALANCED
)

print(response.content)
print(f"Cost: ${response.cost:.4f}")
```

### Example 2: With Budget Tracking

```python
from core.budget_manager import BudgetManager

budget = BudgetManager(daily_limit=5.0, monthly_limit=100.0)

# Check before making request
if await budget.check_budget(estimated_cost=0.05):
    response = await router.complete_with_fallback(...)
    # Budget is automatically recorded
else:
    print("Budget exceeded!")
```

### Example 3: Different Confidence Levels

```python
# Fast: Quick responses, simple queries ($0.0002/request)
response = await router.complete_with_fallback(
    messages=[{"role": "user", "content": "What is 2+2?"}],
    confidence=ConfidenceLevel.FAST
)

# Balanced: Good quality, complex queries ($0.03/request)
response = await router.complete_with_fallback(
    messages=[{"role": "user", "content": "Design a RESTful API"}],
    confidence=ConfidenceLevel.BALANCED
)

# Thorough: Best quality, critical work ($0.15/request)
response = await router.complete_with_fallback(
    messages=[{"role": "user", "content": "Review this production code"}],
    confidence=ConfidenceLevel.THOROUGH
)
```

## Costs

### Anthropic (Claude)
- **Fast** (Haiku): $0.25 / $1.25 per 1M tokens (in/out)
- **Balanced** (Sonnet 4): $3 / $15 per 1M tokens
- **Thorough** (Opus 4): $15 / $75 per 1M tokens

### OpenAI (GPT)
- **Fast** (GPT-3.5 Turbo): $0.50 / $1.50 per 1M tokens
- **Balanced** (GPT-4 Turbo): $10 / $30 per 1M tokens
- **Thorough** (GPT-4o): $2.50 / $10 per 1M tokens

**Typical Request Costs:**
- Fast tier: $0.0002 - $0.005 per request
- Balanced tier: $0.01 - $0.05 per request
- Thorough tier: $0.05 - $0.20 per request

## Troubleshooting

### "No module named 'keyring'"
```bash
source venv/bin/activate
pip install keyring cryptography anthropic openai
```

### "Settings page not found"
```bash
ls -la web/templates/settings.html
# If missing, the file should be at /Users/brettgershon/polly/web/templates/settings.html
```

### "Connection test failed"
- Verify API key format (Anthropic: `sk-ant-api03-...`, OpenAI: `sk-...`)
- Check internet connectivity
- Verify provider API is online
- Check for rate limiting

### "Budget exceeded"
Edit limits in `config.yaml` or via Web UI:
```yaml
routing_v2:
  budget:
    daily_limit: 50.00     # Increase this
    monthly_limit: 1000.00 # Increase this
```

Or reset budget database:
```bash
rm ~/.polly/usage.db
```

## File Structure

```
/Users/brettgershon/polly/
├── core/
│   ├── providers/           # Provider adapters
│   │   ├── base.py
│   │   ├── anthropic_provider.py
│   │   └── openai_provider.py
│   ├── router_v2.py         # Intelligent router
│   ├── budget_manager.py    # Budget tracking
│   └── secrets_manager.py   # API key storage
├── web/
│   ├── templates/
│   │   └── settings.html    # Settings UI
│   └── static/
│       ├── css/settings.css
│       └── js/settings.js
├── interfaces/
│   ├── settings_api.py      # REST API
│   └── cli.py              # CLI commands
├── examples/
│   └── test_routing_v2.py  # Usage example
├── test_phase11a.py        # Test suite
├── setup_keys.py           # Setup wizard
└── config.yaml             # Configuration

~/.polly/                   # User data
├── usage.db               # Budget database
└── secrets/               # Encrypted keys
    ├── .key
    ├── secrets.enc
    └── metadata.json
```

## Next Steps

After testing Phase 11a:

1. **Integration**: Update `core/polly.py` to optionally use `router_v2`
2. **Unit Tests**: Create `tests/test_router_v2.py` and `tests/test_budget_manager.py`
3. **Phase 11b**: Add GitHub Copilot provider
4. **Phase 11c**: Complete settings UI with charts/graphs
5. **Production**: Add authentication, HTTPS, monitoring

## Documentation

- `PHASE11A_IMPLEMENTATION.md` - Technical implementation details
- `docs/API_KEYS.md` - Complete API key management guide
- `docs/WEB_UI.md` - Web UI user guide
- `QUICKSTART_API_KEYS.md` - Quick start for first-time users

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review documentation in `docs/`
3. Run tests with `python3 test_phase11a.py`
4. Check server logs when running `python3 -m interfaces.cli serve`

## Summary

Phase 11a is **complete and ready to use**. All core components are implemented:

- ✅ Multi-provider routing (Anthropic + OpenAI)
- ✅ Three-tier system (Fast, Balanced, Thorough)
- ✅ Secure key management (Keyring + Encryption)
- ✅ Budget tracking (Daily/monthly limits)
- ✅ Web UI (Settings page)
- ✅ CLI commands (Key management)
- ✅ Fallback chains (Automatic failover)
- ✅ Cost estimation (Before API calls)

**Start testing now:**
```bash
source venv/bin/activate
python3 test_phase11a.py
```
