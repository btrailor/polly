"""
Apollo Intelligent Router
Seamlessly pivots between local (Ollama) and cloud (Anthropic/OpenAI) models

The router decides which model to use based on:
- Query complexity
- Required context length
- User preference
- Model availability
- Response quality needs
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any, AsyncIterator
import asyncio
import httpx
import json
import logging
import re
import os

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model capability tiers."""
    FAST = "fast"         # Quick responses, simple queries
    BALANCED = "balanced" # Good quality, reasonable speed
    QUALITY = "quality"   # Best quality, may be slower


class RoutingMode(Enum):
    """Routing preferences."""
    LOCAL = "local"       # Always use local models
    CLOUD = "cloud"       # Always use cloud models
    AUTO = "auto"         # Intelligent routing


@dataclass
class ModelConfig:
    """Configuration for a model."""
    name: str
    provider: str  # "ollama", "anthropic", "openai", "openrouter"
    tier: ModelTier
    context_window: int
    supports_streaming: bool = True
    cost_per_1k_tokens: float = 0.0  # $0 for local


@dataclass
class RoutingDecision:
    """The result of a routing decision."""
    model: ModelConfig
    reason: str
    fallback: Optional[ModelConfig] = None


class IntelligentRouter:
    """
    Routes queries to the most appropriate model.

    Decision factors:
    - Query complexity (simple lookup vs complex reasoning)
    - Context length needed
    - User preference (local, cloud, auto)
    - Model availability
    - Domain requirements
    """

    # Default model configurations (overridden by config local_models)
    DEFAULT_MODELS = {
        'ollama': {
            'fast': ModelConfig(
                name='llama3.2:3b',
                provider='ollama',
                tier=ModelTier.FAST,
                context_window=8192
            ),
            'balanced': ModelConfig(
                name='llama3.1:7b',
                provider='ollama',
                tier=ModelTier.BALANCED,
                context_window=8192
            ),
            'quality': ModelConfig(
                name='llama3.1:70b',
                provider='ollama',
                tier=ModelTier.QUALITY,
                context_window=8192
            )
        },
        'anthropic': {
            'fast': ModelConfig(
                name='claude-haiku-4-5-20251001',
                provider='anthropic',
                tier=ModelTier.FAST,
                context_window=200000,
                cost_per_1k_tokens=0.00025
            ),
            'balanced': ModelConfig(
                name='claude-sonnet-4-20250514',
                provider='anthropic',
                tier=ModelTier.BALANCED,
                context_window=200000,
                cost_per_1k_tokens=0.003
            ),
            'quality': ModelConfig(
                name='claude-opus-4-20250514',
                provider='anthropic',
                tier=ModelTier.QUALITY,
                context_window=200000,
                cost_per_1k_tokens=0.015
            )
        }
    }

    # Pre-compiled patterns for cloud/local scoring (avoids per-call regex compilation)
    _CLOUD_PATTERNS = [re.compile(p) for p in [
        r'complex|complicated|multi-step',
        r'review|analyze|critique',
        r'synthesize|combine|integrate',
        r'compare|contrast|evaluate',
        r'explain in depth|thoroughly',
        r'all files|entire codebase|whole project',
        r'creative|innovative|novel',
    ]]

    _LOCAL_PATTERNS = [re.compile(p) for p in [
        r'simple|quick|basic',
        r'what is|define|explain',
        r'list|enumerate|show',
        r'complete this|finish|autocomplete',
        r'fix this|correct|typo',
        r'format|prettify|clean up',
    ]]

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        default_mode: RoutingMode = RoutingMode.AUTO,
        local_models: Optional[Dict[str, str]] = None,
    ):
        self.ollama_host = ollama_host
        self.anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.default_mode = default_mode

        self.models = self.DEFAULT_MODELS.copy()
        
        # Override Ollama model names from config if provided
        if local_models:
            for tier_key in ('fast', 'balanced', 'quality'):
                model_name = local_models.get(tier_key)
                if model_name and tier_key in self.models.get('ollama', {}):
                    self.models['ollama'][tier_key] = ModelConfig(
                        name=model_name,
                        provider='ollama',
                        tier=self.models['ollama'][tier_key].tier,
                        context_window=self.models['ollama'][tier_key].context_window,
                    )
            # Expose the configured local model name for metadata (prefer balanced tier)
            self.local_model = local_models.get(
                'balanced',
                local_models.get('fast', self.DEFAULT_MODELS['ollama']['balanced'].name)
            )
        else:
            self.local_model = self.DEFAULT_MODELS['ollama']['balanced'].name
        
        self._ollama_available: Optional[bool] = None
        self._cloud_available: Optional[bool] = None
        # Persistent client for lightweight availability checks (reuses connection)
        self._availability_client = httpx.AsyncClient(timeout=5.0)

    async def check_availability(self):
        """Check which providers are available."""
        # Check Ollama using persistent client
        try:
            response = await self._availability_client.get(f"{self.ollama_host}/api/tags")
            self._ollama_available = response.status_code == 200
        except Exception:
            self._ollama_available = False

        # Check cloud (just verify API key exists for now)
        self._cloud_available = bool(self.anthropic_api_key or self.openai_api_key)

        logger.info(f"Availability: Ollama={self._ollama_available}, Cloud={self._cloud_available}")

    def route(
        self,
        query: str,
        context_length: int = 0,
        mode: Optional[RoutingMode] = None,
        preferred_tier: Optional[ModelTier] = None
    ) -> RoutingDecision:
        """
        Decide which model to use for a query.

        Args:
            query: The user's query
            context_length: Approximate length of context to include
            mode: Override routing mode
            preferred_tier: Preferred model tier

        Returns:
            RoutingDecision with selected model and reason
        """
        mode = mode or self.default_mode
        tier = preferred_tier or self._estimate_tier(query)

        # Handle explicit mode preferences
        if mode == RoutingMode.LOCAL:
            return self._select_local(tier, context_length)
        elif mode == RoutingMode.CLOUD:
            return self._select_cloud(tier, context_length)

        # Auto mode: intelligent routing
        cloud_score = self._score_cloud_need(query, context_length)

        if cloud_score > 0.7 and self._cloud_available:
            decision = self._select_cloud(tier, context_length)
            decision.reason = f"Cloud selected (score: {cloud_score:.2f}): {decision.reason}"
            # Add local fallback
            decision.fallback = self._select_local(tier, context_length).model
            return decision
        else:
            decision = self._select_local(tier, context_length)
            decision.reason = f"Local selected (cloud score: {cloud_score:.2f}): {decision.reason}"
            # Add cloud fallback if available
            if self._cloud_available:
                decision.fallback = self._select_cloud(tier, context_length).model
            return decision

    def _estimate_tier(self, query: str) -> ModelTier:
        """Estimate the appropriate model tier for a query."""
        query_lower = query.lower()

        # Check for quality indicators
        quality_words = ['thorough', 'comprehensive', 'detailed', 'in-depth', 'complete']
        if any(word in query_lower for word in quality_words):
            return ModelTier.QUALITY

        # Check for simplicity indicators
        simple_words = ['quick', 'simple', 'basic', 'just', 'only']
        if any(word in query_lower for word in simple_words):
            return ModelTier.FAST

        # Default to balanced
        return ModelTier.BALANCED

    def _score_cloud_need(self, query: str, context_length: int) -> float:
        """Score how much this query would benefit from cloud models."""
        score = 0.0
        query_lower = query.lower()

        # Check cloud indicators (pre-compiled at class level)
        for pattern in self._CLOUD_PATTERNS:
            if pattern.search(query_lower):
                score += 0.15

        # Check local indicators (reduce score)
        for pattern in self._LOCAL_PATTERNS:
            if pattern.search(query_lower):
                score -= 0.15

        # Context length factor
        if context_length > 4000:
            score += 0.2
        if context_length > 8000:
            score += 0.2

        # Query length factor (longer queries often need more reasoning)
        if len(query) > 200:
            score += 0.1
        if len(query) > 500:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _select_local(self, tier: ModelTier, context_length: int) -> RoutingDecision:
        """Select a local model."""
        # If availability not checked yet, assume Ollama is available (we'll fail later if not)
        if self._ollama_available is None:
            self._ollama_available = True  # Optimistic default

        if not self._ollama_available:
            # Fallback to cloud if local unavailable
            if self._cloud_available:
                return RoutingDecision(
                    model=self.models['anthropic'][tier.value],
                    reason="Local unavailable, using cloud"
                )
            raise RuntimeError("No models available")

        model = self.models['ollama'][tier.value]

        # Check context fits
        if context_length > model.context_window:
            # Try to find a model with larger context
            for check_tier in [ModelTier.QUALITY, ModelTier.BALANCED, ModelTier.FAST]:
                check_model = self.models['ollama'][check_tier.value]
                if context_length <= check_model.context_window:
                    return RoutingDecision(
                        model=check_model,
                        reason=f"Upgraded to {check_model.name} for context length"
                    )

        return RoutingDecision(
            model=model,
            reason=f"Local {tier.value} model for efficiency"
        )

    def _select_cloud(self, tier: ModelTier, context_length: int) -> RoutingDecision:
        """Select a cloud model."""
        if not self._cloud_available:
            if self._ollama_available:
                return RoutingDecision(
                    model=self.models['ollama'][tier.value],
                    reason="Cloud unavailable, using local"
                )
            raise RuntimeError("No models available")

        provider = 'anthropic' if self.anthropic_api_key else 'openai'
        model = self.models[provider][tier.value]

        return RoutingDecision(
            model=model,
            reason=f"Cloud {tier.value} model for quality/capability"
        )


class UnifiedLLM:
    """
    Unified interface for calling LLMs across providers.

    Handles:
    - Ollama (local)
    - Anthropic (Claude)
    - OpenAI (GPT)
    - OpenRouter (any model)
    """

    def __init__(
        self,
        router: IntelligentRouter,
        default_system_prompt: str = ""
    ):
        self.router = router
        self.default_system_prompt = default_system_prompt
        # Single persistent client reused across all provider calls.
        # Avoids TCP connection pool setup/teardown on every LLM request.
        self._client = httpx.AsyncClient(timeout=120.0)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[ModelConfig] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """
        Send a chat request to the appropriate model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Specific model to use (or let router decide)
            system_prompt: Override system prompt
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Whether to stream responses

        Yields:
            Response text (or chunks if streaming)
        """
        if not model:
            # Get last user message for routing
            user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
            context_length = sum(len(m['content']) for m in messages)
            decision = self.router.route(user_msg, context_length)
            model = decision.model
            logger.info(f"Routing decision: {decision.reason}")

        # Prepare messages with system prompt
        system = system_prompt or self.default_system_prompt
        full_messages = messages.copy()
        if system and (not full_messages or full_messages[0]['role'] != 'system'):
            full_messages.insert(0, {'role': 'system', 'content': system})

        # Route to appropriate provider
        if model.provider == 'ollama':
            async for chunk in self._call_ollama(full_messages, model, temperature, max_tokens, stream):
                yield chunk
        elif model.provider == 'anthropic':
            async for chunk in self._call_anthropic(full_messages, model, temperature, max_tokens, stream):
                yield chunk
        elif model.provider == 'openai':
            async for chunk in self._call_openai(full_messages, model, temperature, max_tokens, stream):
                yield chunk
        else:
            raise ValueError(f"Unknown provider: {model.provider}")

    async def _call_ollama(
        self,
        messages: List[Dict],
        model: ModelConfig,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> AsyncIterator[str]:
        """Call Ollama API."""
        response = await self._client.post(
            f"{self.router.ollama_host}/api/chat",
            json={
                'model': model.name,
                'messages': messages,
                'stream': stream,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens
                }
            }
        )

        if stream:
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if 'error' in data:
                        raise RuntimeError(f"Ollama error: {data['error']}")
                    if 'message' in data and 'content' in data['message']:
                        yield data['message']['content']
        else:
            data = response.json()
            if 'error' in data:
                raise RuntimeError(f"Ollama error: {data['error']}")
            yield data['message']['content']

    async def _call_anthropic(
        self,
        messages: List[Dict],
        model: ModelConfig,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> AsyncIterator[str]:
        """Call Anthropic API."""
        # Extract system message
        system = ""
        chat_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                system = msg['content']
            else:
                chat_messages.append(msg)

        response = await self._client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                'x-api-key': self.router.anthropic_api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': model.name,
                'max_tokens': max_tokens,
                'system': system,
                'messages': chat_messages,
                'temperature': temperature,
                'stream': stream
            }
        )

        if stream:
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if data['type'] == 'content_block_delta':
                        yield data['delta'].get('text', '')
        else:
            data = response.json()
            yield data['content'][0]['text']

    async def _call_openai(
        self,
        messages: List[Dict],
        model: ModelConfig,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> AsyncIterator[str]:
        """Call OpenAI API."""
        response = await self._client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                'Authorization': f'Bearer {self.router.openai_api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model.name,
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'stream': stream
            }
        )

        if stream:
            async for line in response.aiter_lines():
                if line.startswith('data: ') and line != 'data: [DONE]':
                    data = json.loads(line[6:])
                    if data['choices'][0]['delta'].get('content'):
                        yield data['choices'][0]['delta']['content']
        else:
            data = response.json()
            yield data['choices'][0]['message']['content']
