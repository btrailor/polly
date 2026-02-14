"""
Base provider adapter and error classes for Phase 11 multi-provider system
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
    def __init__(self, message: str, failures: list[dict] = None):
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
        """Total tokens used in this completion"""
        return self.tokens_in + self.tokens_out
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
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
    pricing: dict  # {"input": cost_per_1m, "output": cost_per_1m}
    capabilities: list[str] = field(default_factory=list)
    provider: str = ""
    
    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Estimate cost for given token counts"""
        input_cost = (tokens_in / 1_000_000) * self.pricing.get("input", 0)
        output_cost = (tokens_out / 1_000_000) * self.pricing.get("output", 0)
        return input_cost + output_cost


# ========== Base Provider Adapter ==========

class ProviderAdapter(ABC):
    """
    Base class for all AI provider adapters
    
    Each provider (Anthropic, OpenAI, etc.) implements this interface
    to provide a unified API for the router.
    """
    
    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.api_key = api_key
        self.current_model = None
        self._models_cache = None
        self._cache_timestamp = None
    
    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Provider-specific options
        
        Returns:
            CompletionResponse with content, tokens, cost
        
        Raises:
            ProviderAPIError: API error
            ProviderRateLimitError: Rate limit exceeded
            ProviderAuthError: Authentication failed
            ProviderConnectionError: Network error
            ProviderTimeoutError: Request timeout
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens as they arrive
        
        Args:
            messages: List of message dicts
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific options
        
        Yields:
            Content tokens as strings
        
        Raises:
            Same exceptions as complete()
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Model identifier (uses default if None)
        
        Returns:
            Estimated cost in USD
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate API credentials
        
        Returns:
            True if credentials are valid
        
        Raises:
            ProviderAuthError: Invalid credentials
        """
        pass
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available models for this provider
        
        Returns:
            List of ModelInfo objects
        
        Note: Override this method in provider implementations
        """
        return []
    
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default model identifier for this provider"""
        return getattr(self, 'default_model', None)
    
    def _calculate_cost(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        pricing: dict[str, dict]
    ) -> float:
        """
        Helper method to calculate cost from pricing table
        
        Args:
            model: Model identifier
            tokens_in: Input tokens
            tokens_out: Output tokens
            pricing: Pricing dict {model: {"in": price, "out": price}}
        
        Returns:
            Total cost in USD
        """
        if model not in pricing:
            logger.warning(f"No pricing info for model {model}, using fallback")
            model = list(pricing.keys())[0] if pricing else "default"
        
        model_pricing = pricing.get(model, {"in": 0, "out": 0})
        input_cost = (tokens_in / 1_000_000) * model_pricing.get("in", 0)
        output_cost = (tokens_out / 1_000_000) * model_pricing.get("out", 0)
        
        return input_cost + output_cost
    
    def _format_messages(self, messages: list[dict]) -> list[dict]:
        """
        Format messages for this provider
        
        Override in subclass if provider has specific format requirements
        """
        return messages
    
    def _extract_system_message(self, messages: list[dict]) -> Optional[str]:
        """
        Extract system message from messages list
        
        Some providers (like Anthropic) handle system messages separately
        """
        system_msgs = [m["content"] for m in messages if m.get("role") == "system"]
        return system_msgs[0] if system_msgs else None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
