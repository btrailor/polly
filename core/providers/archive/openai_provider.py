"""
OpenAI (GPT) provider adapter for Phase 11
"""

from typing import AsyncIterator, Optional
import logging

try:
    from openai import AsyncOpenAI
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    openai = None

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


class OpenAIAdapter(ProviderAdapter):
    """
    OpenAI GPT provider adapter
    
    Supports:
    - GPT-3.5 Turbo (fast, cost-effective)
    - GPT-4 Turbo (balanced)
    - GPT-4o (balanced, multimodal)
    - o1-preview (reasoning, highest quality)
    """
    
    # Model pricing (per 1M tokens)
    PRICING = {
        "gpt-3.5-turbo": {"in": 0.50, "out": 1.50},
        "gpt-4-turbo": {"in": 10.00, "out": 30.00},
        "gpt-4o": {"in": 5.00, "out": 15.00},
        "o1-preview": {"in": 15.00, "out": 60.00},
    }
    
    # Model context windows
    CONTEXT_WINDOWS = {
        "gpt-3.5-turbo": 16_385,
        "gpt-4-turbo": 128_000,
        "gpt-4o": 128_000,
        "o1-preview": 128_000,
    }
    
    def __init__(self, api_key: str):
        super().__init__(name="openai", api_key=api_key)
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not installed. "
                "Install with: pip install openai>=1.10.0"
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = "gpt-4-turbo"
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using GPT
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: GPT model identifier (default: gpt-4-turbo)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional OpenAI-specific options
        
        Returns:
            CompletionResponse with content, tokens, cost
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Make API call
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                **kwargs
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Calculate cost
            cost = self._calculate_cost(
                model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                self.PRICING
            )
            
            return CompletionResponse(
                content=content,
                model=response.model,
                tokens_in=response.usage.prompt_tokens,
                tokens_out=response.usage.completion_tokens,
                cost=cost,
                provider=self.name,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "system_fingerprint": response.system_fingerprint,
                    "created": response.created
                }
            )
        
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit: {e}")
            # Try to extract retry-after from headers
            retry_after = 60
            if hasattr(e, 'response') and e.response:
                retry_after = int(e.response.headers.get("retry-after", 60))
            
            raise ProviderRateLimitError(
                f"OpenAI rate limit exceeded: {e}",
                retry_after=retry_after
            )
        
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI auth error: {e}")
            raise ProviderAuthError(f"Invalid OpenAI API key: {e}")
        
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}")
            raise ProviderConnectionError(f"Failed to connect to OpenAI: {e}")
        
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI timeout: {e}")
            raise ProviderTimeoutError(f"OpenAI request timed out: {e}")
        
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ProviderAPIError(
                f"OpenAI API error: {e}",
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
        Stream completion tokens from GPT
        
        Args:
            messages: List of message dicts
            model: GPT model identifier
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
        
        except openai.RateLimitError as e:
            raise ProviderRateLimitError(f"OpenAI rate limit: {e}")
        
        except openai.AuthenticationError as e:
            raise ProviderAuthError(f"Invalid OpenAI API key: {e}")
        
        except openai.APIConnectionError as e:
            raise ProviderConnectionError(f"Connection failed: {e}")
        
        except openai.APIError as e:
            raise ProviderAPIError(f"OpenAI API error: {e}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: GPT model identifier
        
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
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("OpenAI credentials validated successfully")
            return True
        
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI credential validation failed: {e}")
            raise ProviderAuthError(f"Invalid OpenAI API key: {e}")
        
        except openai.APIError as e:
            logger.warning(f"OpenAI validation error (may still be valid): {e}")
            # Non-auth errors don't necessarily mean invalid credentials
            return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available GPT models
        
        Returns:
            List of ModelInfo objects
        """
        return [
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                context_length=self.CONTEXT_WINDOWS["gpt-3.5-turbo"],
                pricing=self.PRICING["gpt-3.5-turbo"],
                capabilities=["chat", "code"],
                provider=self.name
            ),
            ModelInfo(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                context_length=self.CONTEXT_WINDOWS["gpt-4-turbo"],
                pricing=self.PRICING["gpt-4-turbo"],
                capabilities=["chat", "code", "analysis", "planning"],
                provider=self.name
            ),
            ModelInfo(
                id="gpt-4o",
                name="GPT-4o",
                context_length=self.CONTEXT_WINDOWS["gpt-4o"],
                pricing=self.PRICING["gpt-4o"],
                capabilities=["chat", "code", "analysis", "vision", "multimodal"],
                provider=self.name
            ),
            ModelInfo(
                id="o1-preview",
                name="o1-preview",
                context_length=self.CONTEXT_WINDOWS["o1-preview"],
                pricing=self.PRICING["o1-preview"],
                capabilities=["reasoning", "math", "coding", "analysis"],
                provider=self.name
            ),
        ]
    
    def supports_streaming(self) -> bool:
        """OpenAI supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default GPT model"""
        return self.default_model
