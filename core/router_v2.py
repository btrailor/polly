"""
IntelligentRouterV2 - Multi-Provider Intelligent Routing

Routes queries across multiple cloud providers (Anthropic, OpenAI, GitHub Copilot,
Grok, Perplexity, Gemini, Mistral) using a three-tier system: Fast, Balanced, and Thorough.

Features:
- Task complexity classification
- Budget-aware provider selection
- Automatic fallback chains
- Cost estimation and tracking
- Provider health monitoring
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any
import asyncio
import logging
import re
from datetime import datetime

from core.providers.base import (
    ProviderAdapter,
    CompletionResponse,
    ProviderError,
    ProviderRateLimitError,
    AllProvidersFailed
)
from core.providers.anthropic_provider import AnthropicAdapter
from core.providers.openai_provider import OpenAIAdapter
from core.providers.github_provider import GitHubModelsAdapter
from core.providers.grok_provider import GrokAdapter
from core.providers.perplexity_provider import PerplexityAdapter
from core.providers.gemini_provider import GeminiAdapter
from core.providers.mistral_provider import MistralAdapter

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """User confidence/quality preference."""
    FAST = "fast"           # Speed over quality, low cost
    BALANCED = "balanced"   # Balance speed, quality, cost
    THOROUGH = "thorough"   # Quality over speed, higher cost


class TaskType(Enum):
    """Types of tasks for complexity classification."""
    SIMPLE_QUERY = "simple_query"           # Basic questions, lookups
    CODE_COMPLETION = "code_completion"     # Autocomplete, simple edits
    CODE_GENERATION = "code_generation"     # Write new functions
    CODE_REVIEW = "code_review"             # Review existing code
    MULTI_FILE = "multi_file"               # Cross-file analysis
    REFACTORING = "refactoring"             # Complex code changes
    ARCHITECTURAL = "architectural"         # Design decisions
    CREATIVE = "creative"                   # Novel solutions
    DEBUGGING = "debugging"                 # Find and fix bugs
    DOCUMENTATION = "documentation"         # Write docs, comments


@dataclass
class RoutingDecision:
    """Result of routing logic."""
    provider: ProviderAdapter
    model: str
    confidence: ConfidenceLevel
    complexity_score: int  # 1-10
    estimated_cost: float
    reason: str
    fallback_chain: List[tuple[ProviderAdapter, str]]  # List of (provider, model)


@dataclass
class TierConfig:
    """Configuration for a routing tier."""
    name: str
    max_cost_per_request: float
    providers: List[tuple[str, str, int]]  # (provider_name, model, priority)


class IntelligentRouterV2:
    """
    Intelligent multi-provider routing system.
    
    Routes queries to the most appropriate model based on:
    - Task complexity (classified 1-10)
    - User confidence preference (fast/balanced/thorough)
    - Budget constraints
    - Provider availability
    - Context size requirements
    """

    # Default tier configurations
    DEFAULT_TIERS = {
        ConfidenceLevel.FAST: TierConfig(
            name="fast",
            max_cost_per_request=0.01,
            providers=[
                ("github", "openai/gpt-4o-mini", 1),  # Fastest, cheapest
                ("gemini", "gemini-1.5-flash-8b", 2),  # Google's fastest model
                ("mistral", "mistral-small-latest", 3),  # Mistral small
                ("perplexity", "llama-3.1-sonar-small-128k-online", 4),  # Perplexity small
                ("anthropic", "claude-3-haiku-20240307", 5),
                ("openai", "gpt-3.5-turbo", 6),
            ]
        ),
        ConfidenceLevel.BALANCED: TierConfig(
            name="balanced",
            max_cost_per_request=0.10,
            providers=[
                ("github", "openai/gpt-4o", 1),  # Good balance
                ("gemini", "gemini-1.5-flash", 2),  # Google balanced
                ("anthropic", "claude-sonnet-4-20250514", 3),
                ("mistral", "mistral-medium-latest", 4),  # Mistral medium
                ("perplexity", "llama-3.1-sonar-large-128k-online", 5),  # Perplexity large
                ("openai", "gpt-4-turbo", 6),
            ]
        ),
        ConfidenceLevel.THOROUGH: TierConfig(
            name="thorough",
            max_cost_per_request=1.00,
            providers=[
                ("github", "openai/gpt-4o", 1),  # GPT-4o via GitHub (free, reliable)
                ("anthropic", "claude-opus-4-20250514", 2),  # Claude Opus (highest quality)
                ("openai", "gpt-4o", 3),  # GPT-4o direct (if GitHub fails)
                ("gemini", "gemini-1.5-pro", 4),  # Google Pro model
                ("mistral", "mistral-large-latest", 5),  # Mistral large
                ("grok", "grok-2-1212", 6),  # Grok latest
                ("perplexity", "llama-3.1-sonar-huge-128k-online", 7),  # Perplexity huge
            ]
        )
    }

    # Patterns for task complexity classification
    COMPLEXITY_INDICATORS = {
        # High complexity (7-10)
        'high': [
            r'architect|design system|refactor entire',
            r'multi-file|across files|whole codebase',
            r'complex|sophisticated|advanced',
            r'optimize|performance|scalability',
            r'review all|analyze entire|comprehensive',
        ],
        # Medium complexity (4-6)
        'medium': [
            r'implement|create|build',
            r'review|analyze|explain',
            r'debug|fix bug|troubleshoot',
            r'refactor|improve|enhance',
            r'integrate|connect|combine',
        ],
        # Low complexity (1-3)
        'low': [
            r'what is|define|explain simple',
            r'quick|simple|basic',
            r'complete this|finish|autocomplete',
            r'fix typo|format|prettify',
            r'list|show|display',
        ]
    }

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        github_token: Optional[str] = None,
        grok_api_key: Optional[str] = None,
        perplexity_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        mistral_api_key: Optional[str] = None,
        tier_configs: Optional[Dict[ConfidenceLevel, TierConfig]] = None,
        budget_manager: Optional[Any] = None,  # BudgetManager instance
        use_litellm: bool = False,  # Use unified LiteLLM adapter
        litellm_config_path: str = "config/litellm_config.yaml"
    ):
        """
        Initialize the router.
        
        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: OpenAI API key
            github_token: GitHub Copilot token (future)
            grok_api_key: xAI Grok API key
            perplexity_api_key: Perplexity AI API key
            gemini_api_key: Google Gemini API key
            mistral_api_key: Mistral AI API key
            tier_configs: Custom tier configurations
            budget_manager: BudgetManager instance for cost tracking
            use_litellm: Use unified LiteLLM adapter instead of individual providers
            litellm_config_path: Path to litellm_config.yaml
        """
        self.tier_configs = tier_configs or self.DEFAULT_TIERS
        self.budget_manager = budget_manager
        self.use_litellm = use_litellm

        # Initialize providers
        self.providers: Dict[str, ProviderAdapter] = {}
        
        if use_litellm:
            # Use unified LiteLLM adapter
            try:
                from core.providers.litellm_adapter import LiteLLMAdapter
                
                # Collect all API keys for LiteLLM
                api_keys = {}
                if anthropic_api_key:
                    api_keys['anthropic'] = anthropic_api_key
                if openai_api_key:
                    api_keys['openai'] = openai_api_key
                if github_token:
                    api_keys['github'] = github_token
                if grok_api_key:
                    api_keys['grok'] = grok_api_key
                if perplexity_api_key:
                    api_keys['perplexity'] = perplexity_api_key
                if gemini_api_key:
                    api_keys['gemini'] = gemini_api_key
                if mistral_api_key:
                    api_keys['mistral'] = mistral_api_key
                
                # Initialize unified adapter
                self.providers['litellm'] = LiteLLMAdapter(
                    config_path=litellm_config_path,
                    api_keys=api_keys if api_keys else None
                )
                logger.info("Initialized unified LiteLLM adapter")
                
            except Exception as e:
                logger.error(f"Failed to initialize LiteLLM adapter: {e}")
                logger.warning("Falling back to individual providers")
                use_litellm = False
                self.use_litellm = False
        
        if not use_litellm:
            # Use individual provider adapters (original behavior)
            if anthropic_api_key:
                self.providers['anthropic'] = AnthropicAdapter(anthropic_api_key)
                logger.info("Initialized Anthropic provider")
            
            if openai_api_key:
                self.providers['openai'] = OpenAIAdapter(openai_api_key)
                logger.info("Initialized OpenAI provider")
            
            if github_token:
                self.providers['github'] = GitHubModelsAdapter(github_token)
                logger.info("Initialized GitHub Models provider")
            
            if grok_api_key:
                self.providers['grok'] = GrokAdapter(grok_api_key)
                logger.info("Initialized Grok (xAI) provider")
            
            if perplexity_api_key:
                self.providers['perplexity'] = PerplexityAdapter(perplexity_api_key)
                logger.info("Initialized Perplexity provider")
            
            if gemini_api_key:
                self.providers['gemini'] = GeminiAdapter(gemini_api_key)
                logger.info("Initialized Gemini provider")
            
            if mistral_api_key:
                self.providers['mistral'] = MistralAdapter(mistral_api_key)
                logger.info("Initialized Mistral provider")

        # Provider health tracking
        self._provider_failures: Dict[str, int] = {name: 0 for name in self.providers}
        self._provider_last_success: Dict[str, datetime] = {}

    async def validate_providers(self) -> Dict[str, bool]:
        """
        Validate all configured providers.
        
        Returns:
            Dict mapping provider name to availability status
        """
        status = {}
        
        for name, provider in self.providers.items():
            try:
                is_valid = await provider.validate_credentials()
                status[name] = is_valid
                if is_valid:
                    logger.info(f"Provider {name} validated successfully")
                    self._provider_last_success[name] = datetime.now()
                else:
                    logger.warning(f"Provider {name} credentials invalid")
            except Exception as e:
                logger.error(f"Provider {name} validation failed: {e}")
                status[name] = False
        
        return status

    async def route(
        self,
        messages: List[Dict[str, str]],
        task_type: Optional[TaskType] = None,
        confidence: ConfidenceLevel = ConfidenceLevel.BALANCED,
        max_tokens: int = 2000
    ) -> RoutingDecision:
        """
        Route a request to the most appropriate provider and model.
        
        Args:
            messages: Chat messages (OpenAI format)
            task_type: Type of task (for complexity hints)
            confidence: User's confidence/quality preference
            max_tokens: Maximum tokens to generate
        
        Returns:
            RoutingDecision with selected provider, model, and reasoning
        
        Raises:
            AllProvidersFailed: If all providers are unavailable
        """
        # Classify complexity
        user_query = self._extract_user_query(messages)
        complexity = self._classify_complexity(user_query, task_type)
        
        # Get tier configuration
        tier_config = self.tier_configs[confidence]
        
        # Get candidates from tier
        candidates = self._get_tier_candidates(tier_config)
        
        if not candidates:
            raise AllProvidersFailed("No providers available")
        
        # Filter by budget if budget manager available
        if self.budget_manager:
            candidates = await self._filter_by_budget(candidates, max_tokens)
        
        if not candidates:
            # Budget exceeded - try fast tier as fallback
            logger.warning("Budget constraints - falling back to fast tier")
            fast_config = self.tier_configs[ConfidenceLevel.FAST]
            candidates = self._get_tier_candidates(fast_config)
            if not candidates:
                raise AllProvidersFailed("No providers available within budget")
        
        # Select primary provider (first available candidate)
        provider, model, priority = candidates[0]
        
        # Estimate cost
        estimated_cost = provider.estimate_cost(
            tokens=max_tokens,
            model=model
        )
        
        # Build fallback chain (remaining candidates)
        fallback_chain = [(p, m) for p, m, _ in candidates[1:]]
        
        # Create routing decision
        reason = self._explain_routing(
            confidence, complexity, provider, model, estimated_cost
        )
        
        decision = RoutingDecision(
            provider=provider,
            model=model,
            confidence=confidence,
            complexity_score=complexity,
            estimated_cost=estimated_cost,
            reason=reason,
            fallback_chain=fallback_chain
        )
        
        logger.info(f"Routing: {reason}")
        return decision

    async def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        task_type: Optional[TaskType] = None,
        confidence: ConfidenceLevel = ConfidenceLevel.BALANCED,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """
        Complete a request with automatic fallback on failure.
        
        Args:
            messages: Chat messages
            task_type: Task type hint
            confidence: Quality preference
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
        
        Returns:
            CompletionResponse from successful provider
        
        Raises:
            AllProvidersFailed: If all providers fail
        """
        # Get routing decision
        decision = await self.route(messages, task_type, confidence, max_tokens)
        
        # Try primary provider
        try:
            response = await decision.provider.complete(
                messages=messages,
                model=decision.model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Record success
            provider_name = self._get_provider_name(decision.provider)
            self._provider_failures[provider_name] = 0
            self._provider_last_success[provider_name] = datetime.now()
            
            # Track usage if budget manager available
            if self.budget_manager:
                await self.budget_manager.record_usage(
                    provider=provider_name,
                    model=response.model,
                    tokens_in=response.tokens_in,
                    tokens_out=response.tokens_out,
                    cost=response.cost
                )
            
            logger.info(
                f"Completion successful: {provider_name}/{response.model} "
                f"(in={response.tokens_in}, out={response.tokens_out}, cost=${response.cost:.4f})"
            )
            
            return response
        
        except ProviderRateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            # Try fallback chain
            return await self._try_fallback_chain(
                decision.fallback_chain,
                messages,
                max_tokens,
                temperature,
                **kwargs
            )
        
        except ProviderError as e:
            logger.error(f"Provider error: {e}")
            provider_name = self._get_provider_name(decision.provider)
            self._provider_failures[provider_name] += 1
            
            # Try fallback chain
            return await self._try_fallback_chain(
                decision.fallback_chain,
                messages,
                max_tokens,
                temperature,
                **kwargs
            )

    async def _try_fallback_chain(
        self,
        fallback_chain: List[tuple[ProviderAdapter, str]],
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> CompletionResponse:
        """Try providers in fallback chain."""
        for provider, model in fallback_chain:
            try:
                logger.info(f"Trying fallback: {self._get_provider_name(provider)}/{model}")
                
                response = await provider.complete(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                # Record success
                provider_name = self._get_provider_name(provider)
                self._provider_failures[provider_name] = 0
                self._provider_last_success[provider_name] = datetime.now()
                
                # Track usage
                if self.budget_manager:
                    await self.budget_manager.record_usage(
                        provider=provider_name,
                        model=response.model,
                        tokens_in=response.tokens_in,
                        tokens_out=response.tokens_out,
                        cost=response.cost
                    )
                
                logger.info(f"Fallback successful: {provider_name}/{model}")
                return response
            
            except ProviderError as e:
                logger.warning(f"Fallback failed: {e}")
                provider_name = self._get_provider_name(provider)
                self._provider_failures[provider_name] += 1
                continue
        
        # All providers failed
        raise AllProvidersFailed("All providers in fallback chain failed")

    def _extract_user_query(self, messages: List[Dict[str, str]]) -> str:
        """Extract the latest user query from messages."""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                return msg.get('content', '')
        return ''

    def _classify_complexity(
        self,
        query: str,
        task_type: Optional[TaskType] = None
    ) -> int:
        """
        Classify query complexity on scale of 1-10.
        
        Args:
            query: User query text
            task_type: Optional task type hint
        
        Returns:
            Complexity score (1=trivial, 10=highly complex)
        """
        score = 5  # Start at medium
        query_lower = query.lower()
        
        # Check high complexity indicators
        for pattern in self.COMPLEXITY_INDICATORS['high']:
            if re.search(pattern, query_lower):
                score += 1
        
        # Check medium complexity indicators
        for pattern in self.COMPLEXITY_INDICATORS['medium']:
            if re.search(pattern, query_lower):
                score += 0.5
        
        # Check low complexity indicators
        for pattern in self.COMPLEXITY_INDICATORS['low']:
            if re.search(pattern, query_lower):
                score -= 1
        
        # Task type hints
        if task_type:
            task_complexity = {
                TaskType.SIMPLE_QUERY: 2,
                TaskType.CODE_COMPLETION: 3,
                TaskType.CODE_GENERATION: 5,
                TaskType.CODE_REVIEW: 6,
                TaskType.MULTI_FILE: 7,
                TaskType.REFACTORING: 7,
                TaskType.ARCHITECTURAL: 9,
                TaskType.CREATIVE: 8,
                TaskType.DEBUGGING: 6,
                TaskType.DOCUMENTATION: 4,
            }
            # Weight task type hint heavily
            score = (score + task_complexity.get(task_type, 5) * 2) / 3
        
        # Query length factor
        if len(query) > 500:
            score += 1
        if len(query) > 1000:
            score += 1
        
        # Clamp to 1-10
        return max(1, min(10, int(score)))

    def _get_tier_candidates(
        self,
        tier_config: TierConfig
    ) -> List[tuple[ProviderAdapter, str, int]]:
        """
        Get available providers for a tier, sorted by priority.
        
        Returns:
            List of (provider, model, priority) tuples
        """
        candidates = []
        
        for provider_name, model, priority in tier_config.providers:
            # Check if provider is available
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            
            # Check if provider has too many recent failures
            if self._provider_failures.get(provider_name, 0) > 3:
                logger.warning(f"Skipping {provider_name} due to recent failures")
                continue
            
            # Check if model is supported
            available_models = [m.id for m in provider.get_models()]
            if model not in available_models:
                logger.warning(f"Model {model} not available in {provider_name}")
                continue
            
            candidates.append((provider, model, priority))
        
        # Sort by priority (lower number = higher priority)
        candidates.sort(key=lambda x: x[2])
        
        return candidates

    async def _filter_by_budget(
        self,
        candidates: List[tuple[ProviderAdapter, str, int]],
        max_tokens: int
    ) -> List[tuple[ProviderAdapter, str, int]]:
        """Filter candidates by budget constraints."""
        if not self.budget_manager:
            return candidates
        
        filtered = []
        
        for provider, model, priority in candidates:
            # Estimate cost for this request
            estimated_cost = provider.estimate_cost(max_tokens, model)
            
            # Check if within budget
            can_afford = await self.budget_manager.check_budget(estimated_cost)
            
            if can_afford:
                filtered.append((provider, model, priority))
            else:
                provider_name = self._get_provider_name(provider)
                logger.warning(
                    f"Filtering out {provider_name}/{model} "
                    f"(estimated cost: ${estimated_cost:.4f})"
                )
        
        return filtered

    def _explain_routing(
        self,
        confidence: ConfidenceLevel,
        complexity: int,
        provider: ProviderAdapter,
        model: str,
        cost: float
    ) -> str:
        """Generate human-readable routing explanation."""
        provider_name = self._get_provider_name(provider)
        
        reason_parts = [
            f"{confidence.value} tier",
            f"complexity={complexity}/10",
            f"{provider_name}/{model}",
            f"~${cost:.4f}"
        ]
        
        return " | ".join(reason_parts)

    def _get_provider_name(self, provider: ProviderAdapter) -> str:
        """Get provider name from adapter instance."""
        for name, p in self.providers.items():
            if p is provider:
                return name
        return "unknown"

    def get_provider_stats(self) -> Dict[str, Any]:
        """
        Get statistics about provider usage and health.
        
        Returns:
            Dict with provider statistics
        """
        stats = {}
        
        for name, provider in self.providers.items():
            stats[name] = {
                'available': name in self._provider_last_success,
                'failures': self._provider_failures.get(name, 0),
                'last_success': self._provider_last_success.get(name),
                'models': [m.id for m in provider.get_models()]
            }
        
        return stats
