"""
Mistral AI provider adapter for Phase 11

Mistral AI uses an OpenAI-compatible API, so we can use the OpenAI SDK
with a custom base_url pointing to Mistral's API.
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


class MistralAdapter(ProviderAdapter):
    """
    Mistral AI provider adapter
    
    Supports:
    - mistral-small-latest (fast, cost-effective)
    - mistral-medium-latest (balanced)
    - mistral-large-latest (highest quality)
    - codestral-latest (specialized for code)
    
    Uses OpenAI-compatible API via Mistral's endpoint
    """
    
    # Mistral AI API endpoint
    API_BASE_URL = "https://api.mistral.ai/v1"
    
    # Model pricing (per 1M tokens) - based on Mistral's pricing (Feb 2026)
    PRICING = {
        "mistral-small-latest": {"in": 0.20, "out": 0.60},
        "mistral-medium-latest": {"in": 2.70, "out": 8.10},
        "mistral-large-latest": {"in": 4.00, "out": 12.00},
        "codestral-latest": {"in": 0.30, "out": 0.90},
        "open-mistral-7b": {"in": 0.25, "out": 0.25},
        "open-mixtral-8x7b": {"in": 0.70, "out": 0.70},
        "open-mixtral-8x22b": {"in": 2.00, "out": 6.00},
    }
    
    # Model context windows
    CONTEXT_WINDOWS = {
        "mistral-small-latest": 32_768,
        "mistral-medium-latest": 32_768,
        "mistral-large-latest": 128_000,
        "codestral-latest": 32_768,
        "open-mistral-7b": 32_768,
        "open-mixtral-8x7b": 32_768,
        "open-mixtral-8x22b": 65_536,
    }
    
    def __init__(self, api_key: str):
        super().__init__(name="mistral", api_key=api_key)
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not installed (required for Mistral). "
                "Install with: pip install openai>=1.0.0"
            )
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.API_BASE_URL
        )
        self.default_model = "mistral-small-latest"
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using Mistral
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Mistral model identifier (default: mistral-small-latest)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional OpenAI-compatible options
        
        Returns:
            CompletionResponse with content, tokens, cost
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Make API call using OpenAI SDK
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
                    "system_fingerprint": getattr(response, 'system_fingerprint', None),
                    "created": response.created
                }
            )
        
        except RateLimitError as e:
            logger.warning(f"Mistral rate limit: {e}")
            raise ProviderRateLimitError(
                f"Mistral rate limit exceeded: {e}",
                retry_after=60
            )
        
        except AuthenticationError as e:
            logger.error(f"Mistral auth error: {e}")
            raise ProviderAuthError(f"Invalid Mistral API key: {e}")
        
        except APIConnectionError as e:
            logger.error(f"Mistral connection error: {e}")
            raise ProviderConnectionError(f"Failed to connect to Mistral: {e}")
        
        except APITimeoutError as e:
            logger.error(f"Mistral timeout: {e}")
            raise ProviderTimeoutError(f"Mistral request timed out: {e}")
        
        except APIError as e:
            logger.error(f"Mistral API error: {e}")
            raise ProviderAPIError(
                f"Mistral API error: {e}",
                status_code=getattr(e, 'status_code', None)
            )
        
        except OpenAIError as e:
            logger.error(f"Mistral OpenAI SDK error: {e}")
            raise ProviderAPIError(f"Mistral error: {e}")
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from Mistral
        
        Args:
            messages: List of message dicts
            model: Mistral model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional options
        
        Yields:
            Content tokens as strings
        """
        model = model or self.default_model
        self.current_model = model
        
        try:
            # Stream response using OpenAI SDK
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            
            # Yield tokens as they arrive
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except RateLimitError as e:
            raise ProviderRateLimitError(f"Mistral rate limit: {e}")
        
        except AuthenticationError as e:
            raise ProviderAuthError(f"Invalid Mistral API key: {e}")
        
        except APIConnectionError as e:
            raise ProviderConnectionError(f"Connection failed: {e}")
        
        except APITimeoutError as e:
            raise ProviderTimeoutError(f"Request timed out: {e}")
        
        except (APIError, OpenAIError) as e:
            raise ProviderAPIError(f"Mistral API error: {e}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (input + output)
            model: Mistral model identifier
        
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
            logger.info("Mistral credentials validated successfully")
            return True
        
        except AuthenticationError as e:
            logger.error(f"Mistral credential validation failed: {e}")
            raise ProviderAuthError(f"Invalid Mistral API key: {e}")
        
        except (APIError, OpenAIError) as e:
            logger.warning(f"Mistral validation error (may still be valid): {e}")
            # Non-auth errors don't necessarily mean invalid credentials
            return True
    
    def get_models(self) -> list[ModelInfo]:
        """
        Get available Mistral models
        
        Returns:
            List of ModelInfo objects
        """
        return [
            ModelInfo(
                id="mistral-small-latest",
                name="Mistral Small",
                context_length=self.CONTEXT_WINDOWS["mistral-small-latest"],
                pricing=self.PRICING["mistral-small-latest"],
                capabilities=["chat", "code", "fast"],
                provider=self.name
            ),
            ModelInfo(
                id="mistral-medium-latest",
                name="Mistral Medium",
                context_length=self.CONTEXT_WINDOWS["mistral-medium-latest"],
                pricing=self.PRICING["mistral-medium-latest"],
                capabilities=["chat", "code", "analysis"],
                provider=self.name
            ),
            ModelInfo(
                id="mistral-large-latest",
                name="Mistral Large",
                context_length=self.CONTEXT_WINDOWS["mistral-large-latest"],
                pricing=self.PRICING["mistral-large-latest"],
                capabilities=["chat", "code", "analysis", "reasoning"],
                provider=self.name
            ),
            ModelInfo(
                id="codestral-latest",
                name="Codestral",
                context_length=self.CONTEXT_WINDOWS["codestral-latest"],
                pricing=self.PRICING["codestral-latest"],
                capabilities=["code", "completion", "fill-in-middle"],
                provider=self.name
            ),
            ModelInfo(
                id="open-mistral-7b",
                name="Open Mistral 7B",
                context_length=self.CONTEXT_WINDOWS["open-mistral-7b"],
                pricing=self.PRICING["open-mistral-7b"],
                capabilities=["chat", "open-source"],
                provider=self.name
            ),
            ModelInfo(
                id="open-mixtral-8x7b",
                name="Open Mixtral 8x7B",
                context_length=self.CONTEXT_WINDOWS["open-mixtral-8x7b"],
                pricing=self.PRICING["open-mixtral-8x7b"],
                capabilities=["chat", "code", "open-source"],
                provider=self.name
            ),
            ModelInfo(
                id="open-mixtral-8x22b",
                name="Open Mixtral 8x22B",
                context_length=self.CONTEXT_WINDOWS["open-mixtral-8x22b"],
                pricing=self.PRICING["open-mixtral-8x22b"],
                capabilities=["chat", "code", "analysis", "open-source"],
                provider=self.name
            ),
        ]
    
    def supports_streaming(self) -> bool:
        """Mistral supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default Mistral model"""
        return self.default_model
