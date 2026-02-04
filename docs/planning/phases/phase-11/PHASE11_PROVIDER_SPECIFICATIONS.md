# Phase 11: Provider Specifications

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Related:** [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md)

---

## Overview

This document provides detailed specifications for integrating 8 cloud AI providers into Polly's multi-model routing system. Each provider section includes authentication methods, API endpoints, model specifications, pricing, rate limits, and error handling patterns.

---

## Provider Priority

**Essential (Phase 11a - Week 1-2):**
1. Anthropic (Claude)
2. OpenAI (GPT)
3. GitHub Copilot

**Extended (Phase 11b - Week 3-4):**
4. OpenRouter
5. Google AI (Gemini)
6. Mistral AI
7. Grok (xAI)
8. Perplexity

---

## 1. Anthropic (Claude)

### Overview
- **Provider:** Anthropic
- **Models:** Claude 3 Haiku, Claude Sonnet 4, Claude Opus 4
- **API Docs:** https://docs.anthropic.com/
- **Priority:** 1 (Highest)

### Authentication
```python
# Using API key
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

### Available Models

| Model | ID | Context | Input (per 1M tokens) | Output (per 1M tokens) | Tier |
|-------|----|---------|-----------------------|------------------------|------|
| Claude 3 Haiku | `claude-3-haiku-20240307` | 200K | $0.25 | $1.25 | Fast |
| Claude Sonnet 4 | `claude-sonnet-4-20250514` | 200K | $3.00 | $15.00 | Balanced |
| Claude Opus 4 | `claude-opus-4-20250514` | 200K | $15.00 | $75.00 | Thorough |

### API Interface

```python
# core/providers/anthropic.py
class AnthropicAdapter(ProviderAdapter):
    """Anthropic Claude adapter"""
    
    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = "claude-sonnet-4-20250514"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """
        Complete a chat conversation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: model, max_tokens, temperature, etc.
        """
        try:
            response = await self.client.messages.create(
                model=kwargs.get("model", self.default_model),
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 1.0),
                messages=self._format_messages(messages),
                system=self._extract_system_message(messages)
            )
            
            return CompletionResponse(
                content=response.content[0].text,
                model=response.model,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                cost=self._calculate_cost(
                    response.model,
                    response.usage.input_tokens,
                    response.usage.output_tokens
                ),
                provider="anthropic"
            )
        
        except anthropic.RateLimitError as e:
            raise ProviderRateLimitError("Anthropic rate limit exceeded", retry_after=60)
        except anthropic.APIError as e:
            raise ProviderAPIError(f"Anthropic API error: {e}")
    
    async def stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """Stream completion tokens"""
        async with self.client.messages.stream(
            model=kwargs.get("model", self.default_model),
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=self._format_messages(messages)
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost for token count"""
        pricing = {
            "claude-3-haiku-20240307": {"in": 0.25, "out": 1.25},
            "claude-sonnet-4-20250514": {"in": 3.00, "out": 15.00},
            "claude-opus-4-20250514": {"in": 15.00, "out": 75.00}
        }
        
        model_pricing = pricing.get(model, pricing["claude-sonnet-4-20250514"])
        # Assume 50/50 split for estimation
        avg_cost = (model_pricing["in"] + model_pricing["out"]) / 2
        return (tokens / 1_000_000) * avg_cost
    
    def _format_messages(self, messages: list[dict]) -> list[dict]:
        """Format messages for Anthropic API (excludes system messages)"""
        return [m for m in messages if m["role"] != "system"]
    
    def _extract_system_message(self, messages: list[dict]) -> str | None:
        """Extract system message if present"""
        system_msgs = [m["content"] for m in messages if m["role"] == "system"]
        return system_msgs[0] if system_msgs else None
```

### Rate Limits
- **Free Tier:** N/A (API key required)
- **Paid Tier:** 
  - 5 requests per second
  - 100,000 tokens per minute
  - No hard daily limit

### Error Handling

```python
# Anthropic-specific errors
try:
    response = await client.messages.create(...)
except anthropic.RateLimitError as e:
    # Retry after 60 seconds
    await asyncio.sleep(60)
    response = await client.messages.create(...)
except anthropic.APIConnectionError:
    # Network error, try different provider
    pass
except anthropic.AuthenticationError:
    # Invalid API key
    raise ProviderAuthError("Invalid Anthropic API key")
```

---

## 2. OpenAI (GPT)

### Overview
- **Provider:** OpenAI
- **Models:** GPT-3.5 Turbo, GPT-4 Turbo, GPT-4o, o1-preview
- **API Docs:** https://platform.openai.com/docs/
- **Priority:** 2

### Authentication
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

### Available Models

| Model | ID | Context | Input (per 1M tokens) | Output (per 1M tokens) | Tier |
|-------|----|---------|-----------------------|------------------------|------|
| GPT-3.5 Turbo | `gpt-3.5-turbo` | 16K | $0.50 | $1.50 | Fast |
| GPT-4 Turbo | `gpt-4-turbo` | 128K | $10.00 | $30.00 | Balanced |
| GPT-4o | `gpt-4o` | 128K | $5.00 | $15.00 | Balanced |
| o1-preview | `o1-preview` | 128K | $15.00 | $60.00 | Thorough |

### API Interface

```python
# core/providers/openai_provider.py
class OpenAIAdapter(ProviderAdapter):
    """OpenAI GPT adapter"""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = "gpt-4-turbo"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """Complete a chat conversation"""
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.default_model),
                messages=messages,
                max_tokens=kwargs.get("max_tokens"),
                temperature=kwargs.get("temperature", 1.0),
                stream=False
            )
            
            return CompletionResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_in=response.usage.prompt_tokens,
                tokens_out=response.usage.completion_tokens,
                cost=self._calculate_cost(
                    response.model,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                ),
                provider="openai"
            )
        
        except openai.RateLimitError as e:
            raise ProviderRateLimitError("OpenAI rate limit exceeded")
        except openai.APIError as e:
            raise ProviderAPIError(f"OpenAI API error: {e}")
    
    async def stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """Stream completion tokens"""
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.default_model),
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost for token count"""
        pricing = {
            "gpt-3.5-turbo": {"in": 0.50, "out": 1.50},
            "gpt-4-turbo": {"in": 10.00, "out": 30.00},
            "gpt-4o": {"in": 5.00, "out": 15.00},
            "o1-preview": {"in": 15.00, "out": 60.00}
        }
        
        model_pricing = pricing.get(model, pricing["gpt-4-turbo"])
        avg_cost = (model_pricing["in"] + model_pricing["out"]) / 2
        return (tokens / 1_000_000) * avg_cost
```

### Rate Limits
- **Free Tier:** 3 requests per minute (limited models)
- **Tier 1:** 3,500 requests per minute
- **Tier 5:** 10,000 requests per minute
- Token limits vary by tier and model

### Error Handling

```python
try:
    response = await client.chat.completions.create(...)
except openai.RateLimitError as e:
    # Check headers for retry-after
    retry_after = int(e.response.headers.get("retry-after", 60))
    await asyncio.sleep(retry_after)
except openai.APIConnectionError:
    # Network error
    pass
except openai.AuthenticationError:
    # Invalid API key
    raise ProviderAuthError("Invalid OpenAI API key")
```

---

## 3. GitHub Copilot

### Overview
- **Provider:** GitHub (Microsoft)
- **Models:** GitHub Copilot (GPT-4 based)
- **API Docs:** https://docs.github.com/en/copilot
- **Priority:** 3
- **Note:** Already integrated via OAuth

### Authentication
```python
# Reuse existing OAuth integration
# core/providers/github.py
class GitHubCopilotAdapter(ProviderAdapter):
    """GitHub Copilot adapter (reuses existing OAuth)"""
    
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        self.client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "Accept": "application/vnd.github+json"
            }
        )
```

### Available Models

| Model | ID | Context | Pricing | Tier |
|-------|----|---------|---------| -----|
| Copilot | `copilot` | 8K | $10/month subscription | Balanced |

**Note:** GitHub Copilot is subscription-based, not pay-per-use. If user has active subscription, no additional API costs.

### API Interface

```python
async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
    """
    Complete using GitHub Copilot
    
    Note: GitHub Copilot primarily for code completion,
    may not support full chat API
    """
    # Implementation depends on GitHub's API
    # May need to use completions endpoint instead of chat
    pass

def estimate_cost(self, tokens: int, model: str) -> float:
    """GitHub Copilot is subscription-based, return 0"""
    return 0.0  # No per-request cost
```

### Rate Limits
- Tied to GitHub Copilot subscription
- Typically generous for individual users
- No hard rate limits published

---

## 4. OpenRouter

### Overview
- **Provider:** OpenRouter
- **Models:** 100+ models from multiple providers
- **API Docs:** https://openrouter.ai/docs
- **Priority:** 4

### Authentication
```python
import httpx

client = httpx.AsyncClient(
    base_url="https://openrouter.ai/api/v1",
    headers={
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://polly.app",
        "X-Title": "Polly"
    }
)
```

### Available Models (Selected)

| Provider | Model | ID | Input Cost | Output Cost | Tier |
|----------|-------|----|------------|-------------|------|
| Anthropic | Claude Haiku | `anthropic/claude-3-haiku` | $0.25 | $1.25 | Fast |
| Anthropic | Claude Sonnet 4 | `anthropic/claude-sonnet-4` | $3.00 | $15.00 | Balanced |
| OpenAI | GPT-4 Turbo | `openai/gpt-4-turbo` | $10.00 | $30.00 | Balanced |
| Meta | Llama 3.1 70B | `meta-llama/llama-3.1-70b` | $0.70 | $0.80 | Balanced |
| Mistral | Mistral Large | `mistralai/mistral-large` | $4.00 | $12.00 | Thorough |

**Full list:** https://openrouter.ai/models

### API Interface

```python
# core/providers/openrouter.py
class OpenRouterAdapter(ProviderAdapter):
    """OpenRouter unified API adapter"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://polly.app",
                "X-Title": "Polly"
            }
        )
        self.default_model = "anthropic/claude-sonnet-4"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """Complete using OpenRouter (OpenAI-compatible API)"""
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": kwargs.get("model", self.default_model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 1.0)
            }
        )
        
        if response.status_code == 429:
            raise ProviderRateLimitError("OpenRouter rate limit exceeded")
        
        response.raise_for_status()
        data = response.json()
        
        return CompletionResponse(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            tokens_in=data["usage"]["prompt_tokens"],
            tokens_out=data["usage"]["completion_tokens"],
            cost=self._parse_cost_from_headers(response.headers),
            provider="openrouter"
        )
    
    def _parse_cost_from_headers(self, headers: dict) -> float:
        """OpenRouter includes cost in response headers"""
        return float(headers.get("x-openrouter-cost", 0))
    
    async def list_models(self) -> list[ModelInfo]:
        """Fetch available models from OpenRouter"""
        response = await self.client.get("/models")
        data = response.json()
        
        return [
            ModelInfo(
                id=model["id"],
                name=model["name"],
                context_length=model["context_length"],
                pricing=model["pricing"]
            )
            for model in data["data"]
        ]
```

### Rate Limits
- **Free Tier:** Limited to free models, 10 requests/minute
- **Paid:** Based on credits purchased
- No hard rate limits, throttled by credit balance

### Benefits
- Single API key for 100+ models
- Automatic fallback between models
- Cost optimization features
- Real-time model availability

---

## 5. Google AI (Gemini)

### Overview
- **Provider:** Google
- **Models:** Gemini 2.0 Flash, Gemini 1.5 Pro
- **API Docs:** https://ai.google.dev/docs
- **Priority:** 5

### Authentication
```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_AI_API_KEY"))
```

### Available Models

| Model | ID | Context | Input (per 1M tokens) | Output (per 1M tokens) | Tier |
|-------|----|---------|-----------------------|------------------------|------|
| Gemini 2.0 Flash | `gemini-2.0-flash` | 1M | $0.075 | $0.30 | Fast |
| Gemini 1.5 Pro | `gemini-1.5-pro` | 2M | $1.25 | $5.00 | Balanced |

### API Interface

```python
# core/providers/google_ai.py
class GoogleAIAdapter(ProviderAdapter):
    """Google Gemini adapter"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.default_model = "gemini-1.5-pro"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """Complete using Gemini"""
        model = genai.GenerativeModel(
            kwargs.get("model", self.default_model)
        )
        
        # Convert messages to Gemini format
        gemini_messages = self._format_messages(messages)
        
        response = await model.generate_content_async(
            gemini_messages,
            generation_config={
                "max_output_tokens": kwargs.get("max_tokens", 8192),
                "temperature": kwargs.get("temperature", 1.0)
            }
        )
        
        return CompletionResponse(
            content=response.text,
            model=kwargs.get("model", self.default_model),
            tokens_in=response.usage_metadata.prompt_token_count,
            tokens_out=response.usage_metadata.candidates_token_count,
            cost=self._calculate_cost(
                kwargs.get("model", self.default_model),
                response.usage_metadata.prompt_token_count,
                response.usage_metadata.candidates_token_count
            ),
            provider="google"
        )
    
    def _format_messages(self, messages: list[dict]) -> list:
        """Convert OpenAI-style messages to Gemini format"""
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        return gemini_messages
```

### Rate Limits
- **Free Tier:** 15 requests per minute
- **Paid Tier:** 1,000 requests per minute
- **Context:** Up to 2M tokens (Gemini 1.5 Pro)

---

## 6. Mistral AI

### Overview
- **Provider:** Mistral AI
- **Models:** Mistral Small, Medium, Large
- **API Docs:** https://docs.mistral.ai/
- **Priority:** 6

### Authentication
```python
from mistralai.client import MistralClient

client = MistralClient(api_key=os.environ.get("MISTRAL_API_KEY"))
```

### Available Models

| Model | ID | Context | Input (per 1M tokens) | Output (per 1M tokens) | Tier |
|-------|----|---------|-----------------------|------------------------|------|
| Mistral Small | `mistral-small-latest` | 32K | $0.20 | $0.60 | Fast |
| Mistral Medium | `mistral-medium-latest` | 32K | $2.70 | $8.10 | Balanced |
| Mistral Large | `mistral-large-latest` | 32K | $4.00 | $12.00 | Thorough |

### API Interface

```python
# core/providers/mistral.py
class MistralAdapter(ProviderAdapter):
    """Mistral AI adapter"""
    
    def __init__(self, api_key: str):
        self.client = MistralClient(api_key=api_key)
        self.default_model = "mistral-medium-latest"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """Complete using Mistral"""
        response = await self.client.chat_async(
            model=kwargs.get("model", self.default_model),
            messages=messages,
            max_tokens=kwargs.get("max_tokens"),
            temperature=kwargs.get("temperature", 1.0)
        )
        
        return CompletionResponse(
            content=response.choices[0].message.content,
            model=response.model,
            tokens_in=response.usage.prompt_tokens,
            tokens_out=response.usage.completion_tokens,
            cost=self._calculate_cost(
                response.model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            ),
            provider="mistral"
        )
```

### Rate Limits
- **Free Tier:** N/A
- **Paid Tier:** No hard limits, usage-based pricing

---

## 7. Grok (xAI)

### Overview
- **Provider:** xAI (X Corp)
- **Models:** Grok-2
- **API Docs:** https://docs.x.ai/
- **Priority:** 7
- **⚠️ Requires mandatory content safety filters**

### Authentication
```python
import httpx

client = httpx.AsyncClient(
    base_url="https://api.x.ai/v1",
    headers={"Authorization": f"Bearer {api_key}"}
)
```

### Available Models

| Model | ID | Context | Pricing | Tier | Safety |
|-------|----|---------|---------| -----|--------|
| Grok-2 | `grok-2` | 128K | TBD | Balanced | ⚠️ Required |

### API Interface

```python
# core/providers/grok.py
from core.safety.grok_filter import GrokSafetyFilter

class GrokAdapter(ProviderAdapter):
    """
    Grok (xAI) adapter with MANDATORY safety filters
    
    WARNING: Do not disable safety filters.
    See PHASE11_GROK_SAFETY.md for details.
    """
    
    BASE_URL = "https://api.x.ai/v1"
    
    def __init__(self, api_key: str, safety_filter: GrokSafetyFilter):
        self.api_key = api_key
        self.safety = safety_filter
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.default_model = "grok-2"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """
        Complete using Grok with safety filtering
        
        Process:
        1. Pre-request validation (task type)
        2. API call
        3. Post-response content filtering
        4. Return or raise GrokContentFilteredError
        """
        task_type = kwargs.get("task_type", "general")
        
        # PRE-REQUEST VALIDATION
        if not self.safety.is_task_allowed(task_type):
            raise GrokTaskForbiddenError(
                f"Grok is not allowed for task type: {task_type}. "
                f"Allowed tasks: {self.safety.WHITELIST_TASKS}"
            )
        
        # API CALL (OpenAI-compatible)
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.default_model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 1.0)
            }
        )
        
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # POST-RESPONSE FILTERING
        is_safe, flags = self.safety.validate_content(content)
        if not is_safe:
            logger.warning(f"Grok response filtered: {flags}")
            await self._log_filter_hit(task_type, flags)
            raise GrokContentFilteredError(
                "Response contained unsafe content and was filtered",
                flags=flags
            )
        
        return CompletionResponse(
            content=content,
            model=self.default_model,
            tokens_in=data["usage"]["prompt_tokens"],
            tokens_out=data["usage"]["completion_tokens"],
            cost=self._calculate_cost(
                data["usage"]["prompt_tokens"],
                data["usage"]["completion_tokens"]
            ),
            provider="grok"
        )
```

### Rate Limits
- TBD (API in beta as of Jan 2026)
- Expect similar limits to other major providers

### Safety Requirements
- **See:** [PHASE11_GROK_SAFETY.md](./PHASE11_GROK_SAFETY.md) for complete specification
- Pre-request task validation
- Post-response content filtering
- User consent required before enabling

---

## 8. Perplexity

### Overview
- **Provider:** Perplexity AI
- **Models:** Sonar Pro, Sonar
- **API Docs:** https://docs.perplexity.ai/
- **Priority:** 8 (Optional)
- **Note:** Requires Pro subscription

### Authentication
```python
import httpx

client = httpx.AsyncClient(
    base_url="https://api.perplexity.ai",
    headers={"Authorization": f"Bearer {api_key}"}
)
```

### Available Models

| Model | ID | Context | Features | Pricing |
|-------|----|---------| ---------|---------|
| Sonar Pro | `sonar-pro` | 128K | Online search | Pro subscription |
| Sonar | `sonar` | 128K | Online search | Pro subscription |

### API Interface

```python
# core/providers/perplexity.py
class PerplexityAdapter(ProviderAdapter):
    """Perplexity AI adapter (optional, requires Pro)"""
    
    BASE_URL = "https://api.perplexity.ai"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.default_model = "sonar-pro"
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """
        Complete using Perplexity with online search
        
        Unique feature: Includes web search results in context
        """
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.default_model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 1.0),
                "search": kwargs.get("search", True)  # Enable online search
            }
        )
        
        response.raise_for_status()
        data = response.json()
        
        return CompletionResponse(
            content=data["choices"][0]["message"]["content"],
            model=self.default_model,
            tokens_in=data["usage"]["prompt_tokens"],
            tokens_out=data["usage"]["completion_tokens"],
            cost=0.0,  # Subscription-based
            provider="perplexity",
            metadata={
                "search_results": data.get("citations", [])
            }
        )
```

### Rate Limits
- Tied to Pro subscription
- Typically: 50 requests per minute
- No hard token limits

### Use Cases
- Web-connected queries
- Current events
- Research tasks
- Fact-checking

**Note:** Optional integration since not all users have Perplexity Pro

---

## Unified Provider Interface

All providers implement this base interface:

```python
# core/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CompletionResponse:
    """Unified response format"""
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    provider: str
    metadata: dict = None

@dataclass
class ModelInfo:
    """Model information"""
    id: str
    name: str
    context_length: int
    pricing: dict
    capabilities: list[str] = None

class ProviderAdapter(ABC):
    """Base class for all AI provider adapters"""
    
    @abstractmethod
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """
        Complete a chat conversation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Provider-specific options
        
        Returns:
            CompletionResponse with content, tokens, cost
        
        Raises:
            ProviderAPIError: API error
            ProviderRateLimitError: Rate limit exceeded
            ProviderAuthError: Authentication failed
        """
        pass
    
    @abstractmethod
    async def stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """
        Stream completion tokens
        
        Args:
            messages: List of message dicts
            **kwargs: Provider-specific options
        
        Yields:
            Content tokens as they arrive
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, tokens: int, model: str) -> float:
        """
        Estimate cost for given token count
        
        Args:
            tokens: Estimated total tokens (in + out)
            model: Model identifier
        
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
        """
        pass
```

---

## Error Handling

### Common Error Types

```python
# core/providers/errors.py

class ProviderError(Exception):
    """Base class for provider errors"""
    pass

class ProviderAPIError(ProviderError):
    """API returned an error"""
    pass

class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after

class ProviderAuthError(ProviderError):
    """Authentication failed"""
    pass

class ProviderConnectionError(ProviderError):
    """Network connection failed"""
    pass

class GrokTaskForbiddenError(ProviderError):
    """Grok task type not allowed"""
    pass

class GrokContentFilteredError(ProviderError):
    """Grok response filtered by safety system"""
    def __init__(self, message: str, flags: list[str]):
        super().__init__(message)
        self.flags = flags
```

### Retry Logic

```python
# core/providers/retry.py
import asyncio
from functools import wraps

def with_retry(max_attempts=3, backoff_factor=2):
    """Decorator for retrying failed requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                
                except ProviderRateLimitError as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(e.retry_after)
                
                except ProviderConnectionError as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(backoff_factor ** attempt)
                    last_exception = e
                
                except ProviderAuthError:
                    # Don't retry auth errors
                    raise
            
            raise last_exception
        
        return wrapper
    return decorator
```

---

## Testing

### Provider Testing Checklist

For each provider:
- [ ] Authentication works
- [ ] Completion endpoint works
- [ ] Streaming works
- [ ] Cost estimation accurate
- [ ] Rate limit handling works
- [ ] Error handling works
- [ ] Model listing works

### Integration Tests

```python
# tests/test_providers.py
import pytest

@pytest.mark.asyncio
async def test_anthropic_completion():
    adapter = AnthropicAdapter(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = await adapter.complete([
        {"role": "user", "content": "Hello, Claude!"}
    ])
    
    assert response.content
    assert response.tokens_in > 0
    assert response.tokens_out > 0
    assert response.cost > 0
    assert response.provider == "anthropic"

@pytest.mark.asyncio
async def test_grok_safety_filter():
    safety = GrokSafetyFilter()
    adapter = GrokAdapter(
        api_key=os.getenv("GROK_API_KEY"),
        safety_filter=safety
    )
    
    # Should fail pre-request validation
    with pytest.raises(GrokTaskForbiddenError):
        await adapter.complete(
            [{"role": "user", "content": "Tell me about politics"}],
            task_type="political_analysis"
        )
    
    # Should pass for code
    response = await adapter.complete(
        [{"role": "user", "content": "Write a Python function"}],
        task_type="code_completion"
    )
    assert response.content
```

---

## Cost Comparison

### Pricing Snapshot (per 1M tokens)

**Fast Tier (< $0.01 per request):**
- Gemini 2.0 Flash: $0.075 / $0.30
- Claude 3 Haiku: $0.25 / $1.25
- GPT-3.5 Turbo: $0.50 / $1.50
- Mistral Small: $0.20 / $0.60

**Balanced Tier ($0.01 - $0.10 per request):**
- Gemini 1.5 Pro: $1.25 / $5.00
- Claude Sonnet 4: $3.00 / $15.00
- GPT-4o: $5.00 / $15.00
- GPT-4 Turbo: $10.00 / $30.00

**Thorough Tier ($0.10+ per request):**
- Mistral Large: $4.00 / $12.00
- Claude Opus 4: $15.00 / $75.00
- o1-preview: $15.00 / $60.00

**Subscription-Based (no per-request cost):**
- GitHub Copilot: $10/month
- Perplexity Pro: $20/month

---

## Provider Selection Strategy

### Default Provider Order (by Tier)

**Fast Tier:**
1. Claude 3 Haiku (best quality/cost ratio)
2. GPT-3.5 Turbo (fast, reliable)
3. Gemini 2.0 Flash (ultra-cheap)

**Balanced Tier:**
1. Claude Sonnet 4 (best overall)
2. GPT-4o (strong alternative)
3. Gemini 1.5 Pro (large context)

**Thorough Tier:**
1. Claude Opus 4 (highest quality)
2. GPT-4o (good balance)
3. o1-preview (reasoning tasks)

### Task-Specific Routing

```python
TASK_PREFERRED_PROVIDERS = {
    "code_completion": ["github", "anthropic", "openai"],
    "code_review": ["anthropic", "openai", "github"],
    "note_creation": ["anthropic", "openai"],
    "planning": ["anthropic", "openai"],
    "research": ["perplexity", "openai", "anthropic"],
    "math": ["openai", "anthropic"],
    "creative_writing": ["anthropic", "openai"],
    "translation": ["anthropic", "google", "openai"]
}
```

---

## Implementation Timeline

**Phase 11a (Weeks 1-2):**
- ✅ Anthropic
- ✅ OpenAI
- ✅ GitHub Copilot

**Phase 11b (Weeks 3-4):**
- ✅ OpenRouter
- ✅ Google AI
- ✅ Mistral AI
- ✅ Grok (with safety)
- ✅ Perplexity

---

## Related Documents

- [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md) - Overall Phase 11 spec
- [PHASE11_GROK_SAFETY.md](./PHASE11_GROK_SAFETY.md) - Grok safety filters
- [PHASE11_SECRETS_MANAGEMENT.md](./PHASE11_SECRETS_MANAGEMENT.md) - API key storage
- [master_roadmap.md](./master_roadmap.md) - Project roadmap
