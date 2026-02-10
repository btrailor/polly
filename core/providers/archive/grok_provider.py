"""
Grok (xAI) provider adapter for Phase 11

Grok uses an OpenAI-compatible API, so we can use the OpenAI SDK
with a custom base_url pointing to xAI's API.
"""

from typing import AsyncIterator, Optional
import logging

try:
    from openai import AsyncOpenAI, OpenAIError, APIError, RateLimitError, AuthenticationError, APIConnectionError, APITimeoutError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    OpenAIError = None
    APIError = None
    RateLimitError = None
    AuthenticationError = None
    APIConnectionError = None
    APITimeoutError = None

from ..base import (
    ProviderAdapter,
    CompletionResponse,
    ModelInfo,
    ProviderAPIError,
    ProviderRateLimitError,
    ProviderAuthError,
    ProviderConnectionError,
    ProviderTimeoutError,
)

logger = logging.getLogger(__name__)


class GrokAdapter(ProviderAdapter):
    """
    Grok (xAI) provider adapter
    
    Supports:
    - grok-2-1212 (latest model)
    - grok-2-vision-1212 (with vision capabilities)
    - grok-beta (beta model)
    
    Uses OpenAI-compatible API via xAI's endpoint
    """
    
    # xAI API endpoint
    API_BASE_URL = "https://api.x.ai/v1"
    
    # Model pricing (per 1M tokens) - based on xAI's pricing
    PRICING = {
        "grok-2-1212": {"in": 2.00, "out": 10.00},
        "grok-2-vision-1212": {"in": 2.00, "out": 10.00},
        "grok-beta": {"in": 5.00, "out": 15.00},
    }
    
    # Model context windows
    CONTEXT_WINDOWS = {
        "grok-2-1212": 131_072,
        "grok-2-vision-1212": 131_072,
        "grok-beta": 131_072,
    }
    
    def __init__(self, api_key: str):
        super().__init__(name="grok", api_key=api_key)
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not installed (required for Grok). "
                "Install with: pip install openai>=1.0.0"
            )
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.API_BASE_URL
        )
        self.default_model = "grok-2-1212"
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using Grok
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Grok model identifier (default: grok-2-1212)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional OpenAI-compatible options
        
        Returns:
            CompletionResponse with content, tokens, cost
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Make API call using OpenAI-compatible endpoint
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Get token usage
            tokens_in = response.usage.prompt_tokens
            tokens_out = response.usage.completion_tokens
            
            # Calculate cost
            cost = self._calculate_cost(
                model,
                tokens_in,
                tokens_out,
                self.PRICING
            )
            
            return CompletionResponse(
                content=content,
                model=response.model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                provider=self.name,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "system_fingerprint": response.system_fingerprint,
                }
            )
        
        except RateLimitError as e:
            logger.warning(f"Grok rate limit: {e}")
            raise ProviderRateLimitError(
                f"Grok rate limit exceeded: {e}",
                retry_after=60
            )
        
        except AuthenticationError as e:
            logger.error(f"Grok auth error: {e}")
            raise ProviderAuthError(f"Invalid Grok API key: {e}")
        
        except APIConnectionError as e:
            logger.error(f"Grok connection error: {e}")
            raise ProviderConnectionError(f"Failed to connect to Grok: {e}")
        
        except APITimeoutError as e:
            logger.error(f"Grok timeout: {e}")
            raise ProviderTimeoutError(f"Grok request timed out: {e}")
        
        except APIError as e:
            logger.error(f"Grok API error: {e}")
            raise ProviderAPIError(
                f"Grok API error: {e}",
                status_code=getattr(e, 'status_code', None)
            )
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from Grok
        
        Args:
            messages: List of message dicts
            model: Grok model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional options
        
        Yields:
            Content tokens as strings
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Stream response
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except RateLimitError as e:
            raise ProviderRateLimitError(f"Grok rate limit: {e}")
        
        except AuthenticationError as e:
            raise ProviderAuthError(f"Invalid Grok API key: {e}")
        
        except APIConnectionError as e:
            raise ProviderConnectionError(f"Connection failed: {e}")
        
        except APIError as e:
            raise ProviderAPIError(f"Grok API error: {e}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Grok model identifier
        
        Returns:
            Estimated cost in USD
        """
        model = model or self.default_model
        
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = self.default_model
        
        pricing = self.PRICING[model]
        
        # Assume 50/50 split for estimation
        avg_cost_per_1m = (pricing["in"] + pricing["out"]) / 2
        return (tokens / 1_000_000) * avg_cost_per_1m
    
    async def validate_credentials(self) -> bool:
        """
        Validate API credentials by making a minimal API call
        
        Returns:
            True if credentials are valid
        
        Raises:
            ProviderAuthError: Invalid credentials
        """
        try:
            # Make minimal API call to test credentials
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            logger.info("Grok credentials validated successfully")
            return True
        
        except AuthenticationError as e:
            logger.error(f"Grok credential validation failed: {e}")
            raise ProviderAuthError(f"Invalid Grok API key: {e}")
        
        except APIError as e:
            logger.warning(f"Grok validation error (may still be valid): {e}")
            # Non-auth errors don't necessarily mean invalid credentials
            return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available Grok models
        
        Returns:
            List of ModelInfo objects
        """
        return [
            ModelInfo(
                id="grok-2-1212",
                name="Grok 2 (Latest)",
                context_length=self.CONTEXT_WINDOWS["grok-2-1212"],
                pricing=self.PRICING["grok-2-1212"],
                capabilities=["chat", "code", "analysis", "reasoning"],
                provider=self.name
            ),
            ModelInfo(
                id="grok-2-vision-1212",
                name="Grok 2 Vision",
                context_length=self.CONTEXT_WINDOWS["grok-2-vision-1212"],
                pricing=self.PRICING["grok-2-vision-1212"],
                capabilities=["chat", "code", "analysis", "reasoning", "vision"],
                provider=self.name
            ),
            ModelInfo(
                id="grok-beta",
                name="Grok Beta",
                context_length=self.CONTEXT_WINDOWS["grok-beta"],
                pricing=self.PRICING["grok-beta"],
                capabilities=["chat", "code", "analysis", "reasoning", "experimental"],
                provider=self.name
            ),
        ]
    
    def supports_streaming(self) -> bool:
        """Grok supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default Grok model"""
        return self.default_model
