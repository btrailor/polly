# polly-routing

Intelligent multi-provider routing library for AI applications.

## Installation

```bash
# Basic installation
pip install -e libs/polly-routing

# With LiteLLM support (100+ providers)
pip install -e "libs/polly-routing[litellm]"
```

## Quick Start

```python
from polly_routing import IntelligentRouterV2, ConfidenceLevel, BudgetManager

# Create budget manager
budget = BudgetManager()

# Option 1: Use LiteLLM adapter (recommended)
router = IntelligentRouterV2(
    budget_manager=budget,
    use_litellm=True,
    litellm_config_path="config/litellm_config.yaml",
    api_keys={
        "anthropic": "sk-ant-...",
        "openai": "sk-...",
    }
)

# Option 2: Provide your own provider adapters
router = IntelligentRouterV2(
    providers={"anthropic": my_anthropic_adapter},
    budget_manager=budget,
)

# Route and complete
messages = [{"role": "user", "content": "Hello!"}]
response = await router.complete_with_fallback(
    messages,
    confidence=ConfidenceLevel.BALANCED
)
```

## Features

- Three-tier routing: Fast, Balanced, Thorough
- Task complexity classification
- Budget-aware provider selection
- Automatic fallback chains
- Cost estimation and tracking
- Provider health monitoring
- LiteLLM integration for 100+ providers
