"""
GitHub Models Provider Adapter
Provides access to GitHub Models API (GPT-4, Claude, Llama, and more)

API Documentation: https://docs.github.com/en/rest/models/inference
Models Catalog: https://github.com/marketplace/models
"""

import httpx
import json
import logging
from typing import AsyncIterator, Optional, Dict, Any
from datetime import datetime

from ..base import (
    ProviderAdapter,
    CompletionResponse,
    ModelInfo,
    ProviderAPIError,
    ProviderRateLimitError,
    ProviderAuthError,
    ProviderConnectionError,
    ProviderTimeoutError
)

logger = logging.getLogger(__name__)


class GitHubModelsAdapter(ProviderAdapter):
    """
    Adapter for GitHub Models API
    
    Provides access to multiple model providers through GitHub's unified API:
    - OpenAI (GPT-4o, GPT-4.1, GPT-3.5)
    - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
    - Meta (Llama 3.1, Llama 3.2)
    - Microsoft (Phi-4)
    - Mistral AI
    - And more...
    
    Requires: GitHub Personal Access Token with `models:read` permission
    """
    
    BASE_URL = "https://models.github.ai"
    API_VERSION = "2022-11-28"
    
    # Pricing estimates (free tier has rate limits, paid via Azure/GitHub)
    # Note: Free tier available, production pricing varies by model
    PRICING = {
        # OpenAI models (via GitHub)
        "openai/gpt-4o": {"in": 2.50, "out": 10.00},  # $2.50/$10 per 1M tokens
        "openai/gpt-4.1": {"in": 2.50, "out": 10.00},
        "openai/gpt-4o-mini": {"in": 0.15, "out": 0.60},
        "openai/gpt-3.5-turbo": {"in": 0.50, "out": 1.50},
        
        # Anthropic models (via GitHub)
        "anthropic/claude-3.5-sonnet": {"in": 3.00, "out": 15.00},
        "anthropic/claude-3-opus": {"in": 15.00, "out": 75.00},
        "anthropic/claude-3-sonnet": {"in": 3.00, "out": 15.00},
        "anthropic/claude-3-haiku": {"in": 0.25, "out": 1.25},
        
        # Meta Llama (free via GitHub)
        "meta-llama/llama-3.1-405b": {"in": 0.00, "out": 0.00},
        "meta-llama/llama-3.1-70b": {"in": 0.00, "out": 0.00},
        "meta-llama/llama-3.2-90b": {"in": 0.00, "out": 0.00},
        
        # Microsoft models (free via GitHub)
        "microsoft/phi-4": {"in": 0.00, "out": 0.00},
        
        # Fallback for unknown models
        "default": {"in": 1.00, "out": 3.00}
    }
    
    # Model capabilities
    MODELS = {
        "openai/gpt-4o": ModelInfo(
            id="openai/gpt-4o",
            name="GPT-4o (GitHub)",
            context_length=128000,
            pricing={"input": 2.50, "output": 10.00},
            capabilities=["chat", "reasoning", "code"],
            provider="github"
        ),
        "openai/gpt-4o-mini": ModelInfo(
            id="openai/gpt-4o-mini",
            name="GPT-4o Mini (GitHub)",
            context_length=128000,
            pricing={"input": 0.15, "output": 0.60},
            capabilities=["chat", "reasoning", "code"],
            provider="github"
        ),
        "anthropic/claude-3.5-sonnet": ModelInfo(
            id="anthropic/claude-3.5-sonnet",
            name="Claude 3.5 Sonnet (GitHub)",
            context_length=200000,
            pricing={"input": 3.00, "output": 15.00},
            capabilities=["chat", "reasoning", "code", "long-context"],
            provider="github"
        ),
        "meta-llama/llama-3.1-405b": ModelInfo(
            id="meta-llama/llama-3.1-405b",
            name="Llama 3.1 405B (GitHub)",
            context_length=128000,
            pricing={"input": 0.00, "output": 0.00},
            capabilities=["chat", "reasoning", "code"],
            provider="github"
        ),
        "microsoft/phi-4": ModelInfo(
            id="microsoft/phi-4",
            name="Phi-4 (GitHub)",
            context_length=16000,
            pricing={"input": 0.00, "output": 0.00},
            capabilities=["chat", "reasoning", "code"],
            provider="github"
        ),
    }
    
    def __init__(self, token: str = None):
        """
        Initialize GitHub Models adapter
        
        Args:
            token: GitHub Personal Access Token with 'models:read' permission
        """
        super().__init__("github", api_key=token)
        self.token = token
        self.default_model = "openai/gpt-4o-mini"  # Fast, cheap, reliable
        self.current_model = self.default_model
        
        if not self.token:
            raise ProviderAuthError("GitHub token is required")
    
    async def complete(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a chat conversation using GitHub Models
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model ID (format: 'publisher/model-name')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional parameters
        
        Returns:
            CompletionResponse with content, tokens, cost
        """
        model = model or self.current_model or self.default_model
        
        # Extract system prompt from kwargs if provided
        system_prompt = kwargs.get('system', None)
        
        # Build messages list with system prompt if provided
        if system_prompt:
            # Prepend system message to messages array
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        
        # Build request payload (OpenAI-compatible)
        payload = {
            "model": model,
            "messages": full_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.API_VERSION
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/inference/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                # Handle errors
                if response.status_code == 401:
                    raise ProviderAuthError("Invalid GitHub token or missing 'models:read' permission")
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise ProviderRateLimitError("GitHub Models rate limit exceeded", retry_after=retry_after)
                elif response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("message", response.text)
                    raise ProviderAPIError(f"GitHub API error: {error_msg}", status_code=response.status_code)
                
                data = response.json()
                
                # Extract response content
                choice = data["choices"][0]
                content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason", "stop")
                
                # Extract token usage (if available)
                usage = data.get("usage", {})
                tokens_in = usage.get("prompt_tokens", 0)
                tokens_out = usage.get("completion_tokens", 0)
                
                # Calculate cost
                cost = self._calculate_cost_for_model(model, tokens_in, tokens_out)
                
                return CompletionResponse(
                    content=content,
                    model=model,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost=cost,
                    provider="github",
                    finish_reason=finish_reason,
                    metadata={
                        "id": data.get("id"),
                        "created": data.get("created")
                    }
                )
        
        except httpx.TimeoutException:
            raise ProviderTimeoutError("GitHub Models request timed out")
        except httpx.ConnectError:
            raise ProviderConnectionError("Failed to connect to GitHub Models API")
        except (ProviderAPIError, ProviderAuthError, ProviderRateLimitError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in GitHub Models completion: {e}", exc_info=True)
            raise ProviderAPIError(f"Unexpected error: {str(e)}")
    
    async def stream(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from GitHub Models
        
        Args:
            messages: List of message dicts
            model: Model ID
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
        
        Yields:
            Content tokens as strings
        """
        model = model or self.current_model or self.default_model
        
        # Extract system prompt from kwargs if provided
        system_prompt = kwargs.get('system', None)
        
        # Build messages list with system prompt if provided
        if system_prompt:
            # Prepend system message to messages array
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        
        payload = {
            "model": model,
            "messages": full_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "X-GitHub-Api-Version": self.API_VERSION
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.BASE_URL}/inference/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status_code == 401:
                        raise ProviderAuthError("Invalid GitHub token")
                    elif response.status_code == 429:
                        raise ProviderRateLimitError("Rate limit exceeded")
                    elif response.status_code >= 400:
                        error_text = await response.aread()
                        logger.error(f"GitHub API error (status {response.status_code}): {error_text.decode()}")
                        raise ProviderAPIError(f"API error: {error_text.decode()}", status_code=response.status_code)
                    
                    logger.debug(f"GitHub Models streaming response status: {response.status_code}")
                    
                    # Parse SSE stream
                    chunk_count = 0
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str == "[DONE]":
                                logger.debug(f"GitHub Models stream completed, received {chunk_count} chunks")
                                break
                            
                            try:
                                data = json.loads(data_str)
                                
                                # Log first chunk for debugging
                                if chunk_count == 0:
                                    logger.debug(f"First SSE chunk structure: {json.dumps(data, indent=2)[:500]}")
                                
                                # Check if choices array exists and is not empty
                                if "choices" not in data or len(data["choices"]) == 0:
                                    logger.warning(f"Empty choices in SSE response: {data_str[:200]}")
                                    continue
                                
                                delta = data["choices"][0].get("delta", {})
                                
                                if "content" in delta:
                                    chunk_count += 1
                                    yield delta["content"]
                            
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE chunk: {data_str[:200]}")
                                continue
        
        except httpx.TimeoutException:
            raise ProviderTimeoutError("Stream timeout")
        except httpx.ConnectError:
            raise ProviderConnectionError("Connection failed")
        except (ProviderAPIError, ProviderAuthError, ProviderRateLimitError):
            raise
        except Exception as e:
            logger.error(f"Unexpected streaming error: {e}", exc_info=True)
            raise ProviderAPIError(f"Stream error: {str(e)}")
    
    def estimate_cost(self, tokens: int, model: str = None) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (assumes 50/50 input/output split)
            model: Model ID
        
        Returns:
            Estimated cost in USD
        """
        model = model or self.current_model or self.default_model
        tokens_in = tokens // 2
        tokens_out = tokens - tokens_in
        return self._calculate_cost_for_model(model, tokens_in, tokens_out)
    
    def _calculate_cost_for_model(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost for specific model and token counts"""
        pricing = self.PRICING.get(model, self.PRICING["default"])
        return self._calculate_cost(model, tokens_in, tokens_out, self.PRICING)
    
    async def validate_credentials(self) -> bool:
        """
        Validate GitHub token by making a test request
        
        Returns:
            True if token is valid and has 'models:read' permission
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.API_VERSION
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test with minimal completion request
                response = await client.post(
                    f"{self.BASE_URL}/inference/chat/completions",
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 5
                    },
                    headers=headers
                )
                
                return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def get_models(self) -> list[ModelInfo]:
        """Get list of available models"""
        return list(self.MODELS.values())
    
    def supports_streaming(self) -> bool:
        """GitHub Models supports streaming"""
        return True
    
    def get_default_model(self) -> str:
        """Get default model (GPT-4o Mini - fast and cheap)"""
        return self.default_model
    
    def __repr__(self) -> str:
        return f"<GitHubModelsAdapter token={'set' if self.token else 'not set'}>"
