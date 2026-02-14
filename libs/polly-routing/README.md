# polly-routing

Intelligent multi-provider routing for LLM requests: Router v2, provider adapters (base + LiteLLM), and budget tracking.

## What it does

- **IntelligentRouterV2** — Routes queries by complexity, confidence tier (fast/balanced/thorough), and budget. Supports pattern-informed routing (PatternConsumer protocol).
- **ProviderAdapter** — Base interface; **LiteLLMAdapter** — unified adapter over LiteLLM (100+ providers).
- **BudgetManager** — SQLite-backed usage tracking, daily/monthly limits, spending summaries.

Individual provider adapters (Anthropic, OpenAI, GitHub, etc.) remain in the main app (`core/providers/archive/`) and are passed into the router via the core adapter.

## Installation

From the Polly repo root (with venv active):

```bash
pip install -e libs/polly-routing
```

Optional LiteLLM support:

```bash
pip install -e "libs/polly-routing[litellm]"
```

## Usage

```python
from polly_routing import IntelligentRouterV2, ConfidenceLevel, BudgetManager

# With pre-built providers (e.g. from core.providers)
providers = {"anthropic": AnthropicAdapter(api_key), "openai": OpenAIAdapter(api_key)}
budget = BudgetManager()
router = IntelligentRouterV2(providers=providers, budget_manager=budget)

# Or use LiteLLM only
router = IntelligentRouterV2(
    use_litellm=True,
    litellm_config_path="config/litellm_config.yaml",
    api_keys={"anthropic": "...", "openai": "..."},
    budget_manager=budget,
)

decision = await router.route(messages, confidence=ConfidenceLevel.BALANCED)
response = await router.complete_with_fallback(messages, confidence=ConfidenceLevel.BALANCED)
```

In Polly, use `core.router_v2.create_router_v2(...)` to build the router from config and secrets; it injects providers from `core.providers` when not using LiteLLM.

## Public API

- **IntelligentRouterV2**, **ConfidenceLevel**, **TaskType**, **RoutingDecision**, **TierConfig**
- **BudgetManager**, **UsageRecord**, **SpendingSummary**
- **ProviderAdapter**, **CompletionResponse**, **ModelInfo**, **LiteLLMAdapter**
- **ProviderError**, **ProviderAPIError**, **ProviderRateLimitError**, **AllProvidersFailed**, etc.

## Dependency

- **polly-routing** has no dependency on other Polly libs. The main app depends on it via `-e libs/polly-routing` in `requirements.txt`.
