"""
polly_routing.providers - Provider adapters and base classes

This package contains the ProviderAdapter protocol and concrete implementations
for routing requests to various AI providers.
"""

from .base import (
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

# LiteLLMAdapter is optional - requires litellm and pyyaml
try:
    from .litellm import LiteLLMAdapter
    _LITELLM_AVAILABLE = True
except ImportError:
    LiteLLMAdapter = None  # type: ignore
    _LITELLM_AVAILABLE = False

__all__ = [
    # Base classes and protocols
    "ProviderAdapter",
    "CompletionResponse",
    "ModelInfo",
    # Error hierarchy
    "ProviderError",
    "ProviderAPIError",
    "ProviderRateLimitError",
    "ProviderAuthError",
    "ProviderConnectionError",
    "ProviderTimeoutError",
    "AllProvidersFailed",
    # Concrete adapters (optional)
    "LiteLLMAdapter",
]
