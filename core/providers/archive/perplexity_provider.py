"""
Perplexity AI provider adapter for Phase 11

Perplexity uses an OpenAI-compatible API
"""

from typing import AsyncIterator, Optional
import logging

try:
    from openai import AsyncOpenAI, OpenAIError, APIError, RateLimitError, AuthenticationError, APIConnectionError, APITimeoutError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

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


class PerplexityAdapter(ProviderAdapter):
    """
    Perplexity AI provider adapter
    
    Supports:
    - llama-3.1-sonar-small-128k-online (fast, online search)
    - llama-3.1-sonar-large-128k-online (balanced, online search)
    - llama-3.1-sonar-huge-128k-online (highest quality, online search)
    
    Uses OpenAI-compatible API via Perplexity's endpoint
    """
    
    # Perplexity API endpoint
    API_BASE_URL = "https://api.perplexity.ai"
    
    # Model pricing (per 1M tokens) - based on Perplexity's pricing
    PRICING = {
        "llama-3.1-sonar-small-128k-online": {"in": 0.20, "out": 0.20},
        "llama-3.1-sonar-large-128k-online": {"in": 1.00, "out": 1.00},
        "llama-3.1-sonar-huge-128k-online": {"in": 5.00, "out": 5.00},
    }
    
    # Model context windows
    CONTEXT_WINDOWS = {
        "llama-3.1-sonar-small-128k-online": 127_072,
        "llama-3.1-sonar-large-128k-online": 127_072,
        "llama-3.1-sonar-huge-128k-online": 127_072,
    }
    
    def __init__(self, api_key: str):
        super().__init__(name="perplexity", api_key=api_key)
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not installed (required for Perplexity). "
                "Install with: pip install openai>=1.0.0"
            )
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.API_BASE_URL
        )
        self.default_model = "llama-3.1-sonar-large-128k-online"
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,  # Perplexity recommends lower temperature
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using Perplexity
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Perplexity model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0, recommend 0.2 for search)
            **kwargs: Additional options
        
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
            
            # Extract citations if available (Perplexity-specific)
            citations = []
            if hasattr(response, 'citations'):
                citations = response.citations
            
            return CompletionResponse(
                content=content,
                model=response.model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                provider=self.name,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "citations": citations,  # Perplexity provides sources
                    "system_fingerprint": getattr(response, 'system_fingerprint', None),
                }
            )
        
        except RateLimitError as e:
            logger.warning(f"Perplexity rate limit: {e}")
            raise ProviderRateLimitError(
                f"Perplexity rate limit exceeded: {e}",
                retry_after=60
            )
        
        except AuthenticationError as e:
            logger.error(f"Perplexity auth error: {e}")
            raise ProviderAuthError(f"Invalid Perplexity API key: {e}")
        
        except APIConnectionError as e:
            logger.error(f"Perplexity connection error: {e}")
            raise ProviderConnectionError(f"Failed to connect to Perplexity: {e}")
        
        except APITimeoutError as e:
            logger.error(f"Perplexity timeout: {e}")
            raise ProviderTimeoutError(f"Perplexity request timed out: {e}")
        
        except APIError as e:
            logger.error(f"Perplexity API error: {e}")
            raise ProviderAPIError(
                f"Perplexity API error: {e}",
                status_code=getattr(e, 'status_code', None)
            )
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from Perplexity
        
        Args:
            messages: List of message dicts
            model: Perplexity model identifier
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
            raise ProviderRateLimitError(f"Perplexity rate limit: {e}")
        
        except AuthenticationError as e:
            raise ProviderAuthError(f"Invalid Perplexity API key: {e}")
        
        except APIConnectionError as e:
            raise ProviderConnectionError(f"Connection failed: {e}")
        
        except APIError as e:
            raise ProviderAPIError(f"Perplexity API error: {e}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Perplexity model identifier
        
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
            logger.info("Perplexity credentials validated successfully")
            return True
        
        except AuthenticationError as e:
            logger.error(f"Perplexity credential validation failed: {e}")
            raise ProviderAuthError(f"Invalid Perplexity API key: {e}")
        
        except APIError as e:
            logger.warning(f"Perplexity validation error (may still be valid): {e}")
            return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available Perplexity models
        
        Returns:
            List of ModelInfo objects
        """
        return [
            ModelInfo(
                id="llama-3.1-sonar-small-128k-online",
                name="Sonar Small (Online)",
                context_length=self.CONTEXT_WINDOWS["llama-3.1-sonar-small-128k-online"],
                pricing=self.PRICING["llama-3.1-sonar-small-128k-online"],
                capabilities=["chat", "search", "citations"],
                provider=self.name
            ),
            ModelInfo(
                id="llama-3.1-sonar-large-128k-online",
                name="Sonar Large (Online)",
                context_length=self.CONTEXT_WINDOWS["llama-3.1-sonar-large-128k-online"],
                pricing=self.PRICING["llama-3.1-sonar-large-128k-online"],
                capabilities=["chat", "search", "citations", "analysis"],
                provider=self.name
            ),
            ModelInfo(
                id="llama-3.1-sonar-huge-128k-online",
                name="Sonar Huge (Online)",
                context_length=self.CONTEXT_WINDOWS["llama-3.1-sonar-huge-128k-online"],
                pricing=self.PRICING["llama-3.1-sonar-huge-128k-online"],
                capabilities=["chat", "search", "citations", "analysis", "reasoning"],
                provider=self.name
            ),
        ]
    
    def supports_streaming(self) -> bool:
        """Perplexity supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default Perplexity model"""
        return self.default_model
