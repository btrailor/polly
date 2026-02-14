"""
polly_routing - Intelligent multi-provider routing library

This library provides intelligent routing across multiple AI providers
(Anthropic, OpenAI, GitHub Copilot, Grok, Perplexity, Gemini, Mistral)
using a three-tier system: Fast, Balanced, and Thorough.

Features:
- Task complexity classification
- Budget-aware provider selection
- Automatic fallback chains
- Cost estimation and tracking
- Provider health monitoring
- LiteLLM integration for 100+ providers

Basic usage:
    from polly_routing import IntelligentRouterV2, ConfidenceLevel, BudgetManager
    
    budget = BudgetManager()
    router = IntelligentRouterV2(
        providers=my_providers,
        budget_manager=budget,
    )
    
    decision = await router.route(messages, confidence=ConfidenceLevel.BALANCED)
    response = await router.complete_with_fallback(messages)
"""

__version__ = "0.1.0"

# Router classes and types
from .router import (
    IntelligentRouterV2,
    ConfidenceLevel,
    TaskType,
    RoutingDecision,
    TierConfig,
)

# Budget management
from .budget import (
    BudgetManager,
    UsageRecord,
    SpendingSummary,
)

# Provider base classes and errors
from .providers import (
    ProviderAdapter,
    CompletionResponse,
    ModelInfo,
    ProviderError,
    ProviderAPIError,
    ProviderRateLimitError,
    ProviderAuthError,
    ProviderConnectionError,
    ProviderTimeoutError,
    AllProvidersFailed,
)

# LiteLLMAdapter is optional (requires litellm, pyyaml)
from .providers import LiteLLMAdapter  # May be None if deps not installed

__all__ = [
    # Version
    "__version__",
    # Router
    "IntelligentRouterV2",
    "ConfidenceLevel",
    "TaskType",
    "RoutingDecision",
    "TierConfig",
    # Budget
    "BudgetManager",
    "UsageRecord",
    "SpendingSummary",
    # Providers
    "ProviderAdapter",
    "CompletionResponse",
    "ModelInfo",
    "LiteLLMAdapter",
    # Errors
    "ProviderError",
    "ProviderAPIError",
    "ProviderRateLimitError",
    "ProviderAuthError",
    "ProviderConnectionError",
    "ProviderTimeoutError",
    "AllProvidersFailed",
]
