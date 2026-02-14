"""
polly-routing: Intelligent multi-provider routing (Router v2, providers, budget).

Use:
  from polly_routing import IntelligentRouterV2, ConfidenceLevel, TaskType
  from polly_routing import BudgetManager, ProviderAdapter
  from polly_routing.providers import LiteLLMAdapter
"""

from .models import ConfidenceLevel, TaskType, RoutingDecision, TierConfig
from .router import IntelligentRouterV2
from .budget import BudgetManager, UsageRecord, SpendingSummary
from .providers.base import (
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
from .providers.litellm import LiteLLMAdapter

__all__ = [
    "IntelligentRouterV2",
    "ConfidenceLevel",
    "TaskType",
    "RoutingDecision",
    "TierConfig",
    "BudgetManager",
    "UsageRecord",
    "SpendingSummary",
    "ProviderAdapter",
    "CompletionResponse",
    "ModelInfo",
    "ProviderError",
    "ProviderAPIError",
    "ProviderRateLimitError",
    "ProviderAuthError",
    "ProviderConnectionError",
    "ProviderTimeoutError",
    "AllProvidersFailed",
    "LiteLLMAdapter",
]
