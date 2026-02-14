"""
Base provider adapter and error classes for multi-provider routing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ========== Error Hierarchy ==========

class ProviderError(Exception):
    """Base class for all provider errors"""
    pass


class ProviderAPIError(ProviderError):
    """API returned an error response"""
    def __init__(self, message: str, status_code: int = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class ProviderAuthError(ProviderError):
    """Authentication failed (invalid API key, expired token, etc.)"""
    pass


class ProviderConnectionError(ProviderError):
    """Network connection failed"""
    pass


class ProviderTimeoutError(ProviderError):
    """Request timed out"""
    pass


class AllProvidersFailed(ProviderError):
    """All providers in fallback chain failed"""
    def __init__(self, message: str, failures: list = None):
        super().__init__(message)
        self.failures = failures or []


# ========== Data Classes ==========

@dataclass
class CompletionResponse:
    """Unified response format from any provider"""
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    provider: str
    finish_reason: str = "stop"
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "model": self.model,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost": self.cost,
            "provider": self.provider,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ModelInfo:
    """Information about an available model"""
    id: str
    name: str
    context_length: int
    pricing: dict
    capabilities: list = field(default_factory=list)
    provider: str = ""

    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * self.pricing.get("input", 0)
        output_cost = (tokens_out / 1_000_000) * self.pricing.get("output", 0)
        return input_cost + output_cost


# ========== Base Provider Adapter ==========

class ProviderAdapter(ABC):
    """Base class for all AI provider adapters."""

    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.api_key = api_key
        self.current_model = None
        self._models_cache = None
        self._cache_timestamp = None

    @abstractmethod
    async def complete(
        self,
        messages: list,
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list,
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        pass

    def get_models(self) -> list:
        return []

    def supports_streaming(self) -> bool:
        return True

    def get_default_model(self) -> str:
        return getattr(self, 'default_model', None)

    def _calculate_cost(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        pricing: dict
    ) -> float:
        if model not in pricing:
            logger.warning(f"No pricing info for model {model}, using fallback")
            model = list(pricing.keys())[0] if pricing else "default"
        model_pricing = pricing.get(model, {"in": 0, "out": 0})
        input_cost = (tokens_in / 1_000_000) * model_pricing.get("in", 0)
        output_cost = (tokens_out / 1_000_000) * model_pricing.get("out", 0)
        return input_cost + output_cost

    def _format_messages(self, messages: list) -> list:
        return messages

    def _extract_system_message(self, messages: list) -> Optional[str]:
        system_msgs = [m["content"] for m in messages if m.get("role") == "system"]
        return system_msgs[0] if system_msgs else None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
