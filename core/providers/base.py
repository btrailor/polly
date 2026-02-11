"""
Re-export provider base from polly_routing. Archive adapters inherit from ProviderAdapter.
"""

from polly_routing.providers.base import (
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

__all__ = [
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
]
