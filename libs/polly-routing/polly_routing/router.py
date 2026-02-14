"""
IntelligentRouterV2 - Multi-Provider Intelligent Routing.
"""

from typing import List, Dict, Optional, Any
import asyncio
import logging
import re
from datetime import datetime

from .models import ConfidenceLevel, TaskType, RoutingDecision, TierConfig
from .providers.base import (
    ProviderAdapter,
    CompletionResponse,
    ProviderError,
    ProviderRateLimitError,
    AllProvidersFailed,
)
from .providers.litellm import LiteLLMAdapter

logger = logging.getLogger(__name__)


class IntelligentRouterV2:
    """Intelligent multi-provider routing. Routes to provider/model by complexity, confidence, and budget."""

    DEFAULT_TIERS = {
        ConfidenceLevel.FAST: TierConfig(
            name="fast",
            max_cost_per_request=0.01,
            providers=[
                ("github", "openai/gpt-4o-mini", 1),
                ("gemini", "gemini-1.5-flash-8b", 2),
                ("mistral", "mistral-small-latest", 3),
                ("perplexity", "llama-3.1-sonar-small-128k-online", 4),
                ("anthropic", "claude-3-haiku-20240307", 5),
                ("openai", "gpt-3.5-turbo", 6),
            ]
        ),
        ConfidenceLevel.BALANCED: TierConfig(
            name="balanced",
            max_cost_per_request=0.10,
            providers=[
                ("github", "openai/gpt-4o", 1),
                ("gemini", "gemini-1.5-flash", 2),
                ("anthropic", "claude-sonnet-4-20250514", 3),
                ("mistral", "mistral-medium-latest", 4),
                ("perplexity", "llama-3.1-sonar-large-128k-online", 5),
                ("openai", "gpt-4-turbo", 6),
            ]
        ),
        ConfidenceLevel.THOROUGH: TierConfig(
            name="thorough",
            max_cost_per_request=1.00,
            providers=[
                ("github", "openai/gpt-4o", 1),
                ("anthropic", "claude-opus-4-20250514", 2),
                ("openai", "gpt-4o", 3),
                ("gemini", "gemini-1.5-pro", 4),
                ("mistral", "mistral-large-latest", 5),
                ("grok", "grok-2-1212", 6),
                ("perplexity", "llama-3.1-sonar-huge-128k-online", 7),
            ]
        )
    }

    COMPLEXITY_INDICATORS = {
        'high': [
            r'architect|design system|refactor entire',
            r'multi-file|across files|whole codebase',
            r'complex|sophisticated|advanced',
            r'optimize|performance|scalability',
            r'review all|analyze entire|comprehensive',
        ],
        'medium': [
            r'implement|create|build',
            r'review|analyze|explain',
            r'debug|fix bug|troubleshoot',
            r'refactor|improve|enhance',
            r'integrate|connect|combine',
        ],
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
        providers: Optional[Dict[str, ProviderAdapter]] = None,
        tier_configs: Optional[Dict[ConfidenceLevel, TierConfig]] = None,
        budget_manager: Optional[Any] = None,
        use_litellm: bool = False,
        litellm_config_path: str = "config/litellm_config.yaml",
        api_keys: Optional[Dict[str, str]] = None,
    ):
        self.tier_configs = tier_configs or self.DEFAULT_TIERS
        self.budget_manager = budget_manager
        self.use_litellm = use_litellm
        self.providers: Dict[str, ProviderAdapter] = {}

        if providers is not None:
            self.providers = dict(providers)
        elif use_litellm:
            try:
                self.providers['litellm'] = LiteLLMAdapter(
                    config_path=litellm_config_path,
                    api_keys=api_keys or None
                )
                logger.info("Initialized unified LiteLLM adapter")
            except Exception as e:
                logger.error(f"Failed to initialize LiteLLM adapter: {e}")
                self.use_litellm = False

        self._provider_failures: Dict[str, int] = {name: 0 for name in self.providers}
        self._provider_last_success: Dict[str, datetime] = {}
        self._routing_patterns: Optional[List[Any]] = None
        self.config: Dict[str, Any] = {}

    def apply_patterns(self, patterns: List[Any], context: Dict[str, Any]) -> None:
        """Apply ROUTING_OUTCOME patterns for next route() (PatternConsumer protocol)."""
        self._routing_patterns = list(patterns) if patterns else None

    async def validate_providers(self) -> Dict[str, bool]:
        status = {}
        for name, provider in self.providers.items():
            try:
                is_valid = await provider.validate_credentials()
                status[name] = is_valid
                if is_valid:
                    self._provider_last_success[name] = datetime.now()
            except Exception as e:
                logger.error(f"Provider {name} validation failed: {e}")
                status[name] = False
        return status

    async def route(
        self,
        messages: List[Dict[str, str]],
        task_type: Optional[TaskType] = None,
        confidence: ConfidenceLevel = ConfidenceLevel.BALANCED,
        max_tokens: int = 2000,
        patterns: Optional[List[Any]] = None,
    ) -> RoutingDecision:
        patterns = patterns if patterns is not None else self._routing_patterns
        user_query = self._extract_user_query(messages)
        complexity = self._classify_complexity(user_query, task_type)
        tier_config = self.tier_configs[confidence]
        candidates = self._get_tier_candidates(tier_config)
        if not candidates:
            raise AllProvidersFailed("No providers available")
        if self.budget_manager:
            candidates = await self._filter_by_budget(candidates, max_tokens)
        if not candidates:
            logger.warning("Budget constraints - falling back to fast tier")
            fast_config = self.tier_configs[ConfidenceLevel.FAST]
            candidates = self._get_tier_candidates(fast_config)
            if not candidates:
                raise AllProvidersFailed("No providers available within budget")
        if patterns:
            for p in patterns:
                pt = getattr(p, "pattern_type", None)
                pt_val = getattr(pt, "value", pt) if pt else None
                if pt_val != "routing_outcome":
                    continue
                if getattr(p, "confidence", 0) < 0.6:
                    continue
                meta = getattr(p, "metadata", None) or {}
                preferred = meta.get("model") or meta.get("preferred_model")
                if not preferred:
                    continue
                for i, (prov, model, _) in enumerate(candidates):
                    if model == preferred:
                        candidates.insert(0, candidates.pop(i))
                        logger.info(f"Pattern-informed routing: boosted {preferred}")
                        break
                break
        provider, model, priority = candidates[0]
        estimated_cost = provider.estimate_cost(tokens=max_tokens, model=model)
        fallback_chain = [(p, m) for p, m, _ in candidates[1:]]
        reason = self._explain_routing(confidence, complexity, provider, model, estimated_cost)
        return RoutingDecision(
            provider=provider,
            model=model,
            confidence=confidence,
            complexity_score=complexity,
            estimated_cost=estimated_cost,
            reason=reason,
            fallback_chain=fallback_chain
        )

    async def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        task_type: Optional[TaskType] = None,
        confidence: ConfidenceLevel = ConfidenceLevel.BALANCED,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        decision = await self.route(messages, task_type, confidence, max_tokens)
        try:
            response = await decision.provider.complete(
                messages=messages,
                model=decision.model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            provider_name = self._get_provider_name(decision.provider)
            self._provider_failures[provider_name] = 0
            self._provider_last_success[provider_name] = datetime.now()
            if self.budget_manager:
                await self.budget_manager.record_usage(
                    provider=provider_name,
                    model=response.model,
                    tokens_in=response.tokens_in,
                    tokens_out=response.tokens_out,
                    cost=response.cost
                )
            return response
        except ProviderRateLimitError:
            return await self._try_fallback_chain(decision.fallback_chain, messages, max_tokens, temperature, **kwargs)
        except ProviderError as e:
            provider_name = self._get_provider_name(decision.provider)
            self._provider_failures[provider_name] += 1
            return await self._try_fallback_chain(decision.fallback_chain, messages, max_tokens, temperature, **kwargs)

    async def _try_fallback_chain(
        self,
        fallback_chain: List[tuple],
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> CompletionResponse:
        failures = []
        for provider, model in fallback_chain:
            try:
                response = await provider.complete(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                provider_name = self._get_provider_name(provider)
                self._provider_failures[provider_name] = 0
                self._provider_last_success[provider_name] = datetime.now()
                if self.budget_manager:
                    await self.budget_manager.record_usage(
                        provider=provider_name,
                        model=response.model,
                        tokens_in=response.tokens_in,
                        tokens_out=response.tokens_out,
                        cost=response.cost
                    )
                return response
            except ProviderError as e:
                provider_name = self._get_provider_name(provider)
                self._provider_failures[provider_name] += 1
                reason = str(e).strip() or type(e).__name__
                failures.append((provider_name, model, reason))
                logger.warning("Provider %s (%s) failed: %s", provider_name, model, reason)
                continue
        msg = "All providers in fallback chain failed"
        if failures:
            details = "; ".join(f"{p} ({m}): {r}" for p, m, r in failures)
            msg = f"{msg}: {details}"
            logger.error("All providers failed. Details: %s", details)
        raise AllProvidersFailed(msg, failures=failures)

    def _extract_user_query(self, messages: List[Dict[str, str]]) -> str:
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                return msg.get('content', '')
        return ''

    def _classify_complexity(self, query: str, task_type: Optional[TaskType] = None) -> int:
        score = 5
        query_lower = query.lower()
        for pattern in self.COMPLEXITY_INDICATORS['high']:
            if re.search(pattern, query_lower):
                score += 1
        for pattern in self.COMPLEXITY_INDICATORS['medium']:
            if re.search(pattern, query_lower):
                score += 0.5
        for pattern in self.COMPLEXITY_INDICATORS['low']:
            if re.search(pattern, query_lower):
                score -= 1
        if task_type:
            task_complexity = {
                TaskType.SIMPLE_QUERY: 2, TaskType.CODE_COMPLETION: 3, TaskType.CODE_GENERATION: 5,
                TaskType.CODE_REVIEW: 6, TaskType.MULTI_FILE: 7, TaskType.REFACTORING: 7,
                TaskType.ARCHITECTURAL: 9, TaskType.CREATIVE: 8, TaskType.DEBUGGING: 6, TaskType.DOCUMENTATION: 4,
            }
            score = (score + task_complexity.get(task_type, 5) * 2) / 3
        if len(query) > 500:
            score += 1
        if len(query) > 1000:
            score += 1
        return max(1, min(10, int(score)))

    def _get_tier_candidates(self, tier_config: TierConfig) -> List[tuple]:
        candidates = []
        if self.use_litellm and "litellm" in self.providers:
            litellm_provider = self.providers["litellm"]
            if self._provider_failures.get("litellm", 0) > 3:
                return []
            for _provider_name, model, priority in tier_config.providers:
                candidates.append((litellm_provider, model, priority))
            candidates.sort(key=lambda x: x[2])
            return candidates
        for provider_name, model, priority in tier_config.providers:
            if provider_name not in self.providers:
                continue
            provider = self.providers[provider_name]
            if self._provider_failures.get(provider_name, 0) > 3:
                continue
            available_models = [m.id for m in provider.get_models()]
            if model not in available_models:
                logger.warning(f"Model {model} not available in {provider_name}")
                continue
            candidates.append((provider, model, priority))
        candidates.sort(key=lambda x: x[2])
        return candidates

    async def _filter_by_budget(
        self,
        candidates: List[tuple],
        max_tokens: int
    ) -> List[tuple]:
        if not self.budget_manager:
            return candidates
        filtered = []
        for provider, model, priority in candidates:
            estimated_cost = provider.estimate_cost(max_tokens, model)
            can_afford = await self.budget_manager.check_budget(estimated_cost)
            if can_afford:
                filtered.append((provider, model, priority))
        return filtered

    def _explain_routing(
        self,
        confidence: ConfidenceLevel,
        complexity: int,
        provider: ProviderAdapter,
        model: str,
        cost: float
    ) -> str:
        provider_name = self._get_provider_name(provider)
        return f"{confidence.value} tier | complexity={complexity}/10 | {provider_name}/{model} | ~${cost:.4f}"

    def _get_provider_name(self, provider: ProviderAdapter) -> str:
        for name, p in self.providers.items():
            if p is provider:
                return name
        return "unknown"

    def get_provider_stats(self) -> Dict[str, Any]:
        return {
            name: {
                'available': name in self._provider_last_success,
                'failures': self._provider_failures.get(name, 0),
                'last_success': self._provider_last_success.get(name),
                'models': [m.id for m in provider.get_models()]
            }
            for name, provider in self.providers.items()
        }
