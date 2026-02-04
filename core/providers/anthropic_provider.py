"""
Anthropic (Claude) provider adapter for Phase 11
"""

from typing import AsyncIterator, Optional
import logging

try:
    import anthropic
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None
    AsyncAnthropic = None

from .base import (
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


class AnthropicAdapter(ProviderAdapter):
    """
    Anthropic Claude provider adapter
    
    Supports:
    - Claude 3 Haiku (fast, cost-effective)
    - Claude Sonnet 4 (balanced, recommended)
    - Claude Opus 4 (highest quality)
    """
    
    # Model pricing (per 1M tokens)
    PRICING = {
        "claude-3-haiku-20240307": {"in": 0.25, "out": 1.25},
        "claude-sonnet-4-20250514": {"in": 3.00, "out": 15.00},
        "claude-opus-4-20250514": {"in": 15.00, "out": 75.00},
    }
    
    # Model context windows
    CONTEXT_WINDOWS = {
        "claude-3-haiku-20240307": 200_000,
        "claude-sonnet-4-20250514": 200_000,
        "claude-opus-4-20250514": 200_000,
    }
    
    def __init__(self, api_key: str):
        super().__init__(name="anthropic", api_key=api_key)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic library not installed. "
                "Install with: pip install anthropic>=0.20.0"
            )
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = "claude-sonnet-4-20250514"
        self.api_version = "2023-06-01"
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using Claude
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Claude model identifier (default: claude-sonnet-4)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0 for Claude)
            **kwargs: Additional Anthropic-specific options
        
        Returns:
            CompletionResponse with content, tokens, cost
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Extract system message (Anthropic handles it separately)
            system_message = self._extract_system_message(messages)
            
            # Format messages (exclude system messages)
            formatted_messages = [
                m for m in messages if m.get("role") != "system"
            ]
            
            # Make API call
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=formatted_messages,
                system=system_message,
                **kwargs
            )
            
            # Extract content
            content = response.content[0].text
            
            # Calculate cost
            cost = self._calculate_cost(
                model,
                response.usage.input_tokens,
                response.usage.output_tokens,
                self.PRICING
            )
            
            return CompletionResponse(
                content=content,
                model=response.model,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                cost=cost,
                provider=self.name,
                finish_reason=response.stop_reason,
                metadata={
                    "stop_sequence": response.stop_sequence,
                    "api_version": self.api_version
                }
            )
        
        except anthropic.RateLimitError as e:
            logger.warning(f"Anthropic rate limit: {e}")
            raise ProviderRateLimitError(
                f"Anthropic rate limit exceeded: {e}",
                retry_after=60
            )
        
        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic auth error: {e}")
            raise ProviderAuthError(f"Invalid Anthropic API key: {e}")
        
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            raise ProviderConnectionError(f"Failed to connect to Anthropic: {e}")
        
        except anthropic.APITimeoutError as e:
            logger.error(f"Anthropic timeout: {e}")
            raise ProviderTimeoutError(f"Anthropic request timed out: {e}")
        
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise ProviderAPIError(
                f"Anthropic API error: {e}",
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
        Stream completion tokens from Claude
        
        Args:
            messages: List of message dicts
            model: Claude model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional options
        
        Yields:
            Content tokens as strings
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Extract system message
            system_message = self._extract_system_message(messages)
            
            # Format messages
            formatted_messages = [
                m for m in messages if m.get("role") != "system"
            ]
            
            # Stream response
            async with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=formatted_messages,
                system=system_message,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        
        except anthropic.RateLimitError as e:
            raise ProviderRateLimitError(f"Anthropic rate limit: {e}")
        
        except anthropic.AuthenticationError as e:
            raise ProviderAuthError(f"Invalid Anthropic API key: {e}")
        
        except anthropic.APIConnectionError as e:
            raise ProviderConnectionError(f"Connection failed: {e}")
        
        except anthropic.APIError as e:
            raise ProviderAPIError(f"Anthropic API error: {e}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Claude model identifier
        
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
            response = await self.client.messages.create(
                model=self.default_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("Anthropic credentials validated successfully")
            return True
        
        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic credential validation failed: {e}")
            raise ProviderAuthError(f"Invalid Anthropic API key: {e}")
        
        except anthropic.APIError as e:
            logger.warning(f"Anthropic validation error (may still be valid): {e}")
            # Non-auth errors don't necessarily mean invalid credentials
            return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available Claude models
        
        Returns:
            List of ModelInfo objects
        """
        return [
            ModelInfo(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                context_length=self.CONTEXT_WINDOWS["claude-3-haiku-20240307"],
                pricing=self.PRICING["claude-3-haiku-20240307"],
                capabilities=["chat", "code", "analysis"],
                provider=self.name
            ),
            ModelInfo(
                id="claude-sonnet-4-20250514",
                name="Claude Sonnet 4",
                context_length=self.CONTEXT_WINDOWS["claude-sonnet-4-20250514"],
                pricing=self.PRICING["claude-sonnet-4-20250514"],
                capabilities=["chat", "code", "analysis", "planning"],
                provider=self.name
            ),
            ModelInfo(
                id="claude-opus-4-20250514",
                name="Claude Opus 4",
                context_length=self.CONTEXT_WINDOWS["claude-opus-4-20250514"],
                pricing=self.PRICING["claude-opus-4-20250514"],
                capabilities=["chat", "code", "analysis", "planning", "reasoning"],
                provider=self.name
            ),
        ]
    
    def supports_streaming(self) -> bool:
        """Anthropic supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default Claude model"""
        return self.default_model
