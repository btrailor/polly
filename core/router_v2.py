"""
Core adapter for polly-routing library.
Builds IntelligentRouterV2 from Polly config and re-exports public API.
"""

from typing import Optional, Dict, Any

try:
    from polly_routing import (
    IntelligentRouterV2,
    ConfidenceLevel,
    TaskType,
    RoutingDecision,
    TierConfig,
    BudgetManager,
    UsageRecord,
    SpendingSummary,
    ProviderAdapter,
    CompletionResponse,
    AllProvidersFailed,
)
except ModuleNotFoundError as e:
    if "polly_routing" in str(e):
        raise ModuleNotFoundError(
            "polly_routing is not installed. From the project root run: pip install -r requirements.txt"
            " or: pip install -e libs/polly-routing"
        ) from e
    raise

__all__ = [
    "IntelligentRouterV2",
    "ConfidenceLevel",
    "TaskType",
    "RoutingDecision",
    "TierConfig",
    "BudgetManager",
    "UsageRecord",
    "SpendingSummary",
    "ProviderAdapter",
    "CompletionResponse",
    "AllProvidersFailed",
    "create_router_v2",
]


def create_router_v2(
    *,
    budget_manager: BudgetManager,
    anthropic_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    github_token: Optional[str] = None,
    grok_api_key: Optional[str] = None,
    perplexity_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    mistral_api_key: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
    use_litellm: bool = False,
    litellm_config_path: str = "config/litellm_config.yaml",
    tier_configs: Optional[Dict[ConfidenceLevel, TierConfig]] = None,
) -> IntelligentRouterV2:
    """
    Build IntelligentRouterV2 from Polly-style config and secrets.
    When use_litellm=False, builds provider adapters from core.providers (archive).
    When use_litellm=True, passes api_keys to the library's LiteLLM adapter.
    """
    if use_litellm:
        api_keys = {}
        if anthropic_api_key:
            api_keys["anthropic"] = anthropic_api_key
        if openai_api_key:
            api_keys["openai"] = openai_api_key
        if github_token:
            api_keys["github"] = github_token
        if grok_api_key:
            api_keys["grok"] = grok_api_key
        if perplexity_api_key:
            api_keys["perplexity"] = perplexity_api_key
        if gemini_api_key:
            api_keys["gemini"] = gemini_api_key
        if mistral_api_key:
            api_keys["mistral"] = mistral_api_key
        if openrouter_api_key:
            api_keys["openrouter"] = openrouter_api_key
        return IntelligentRouterV2(
            providers=None,
            tier_configs=tier_configs,
            budget_manager=budget_manager,
            use_litellm=True,
            litellm_config_path=litellm_config_path,
            api_keys=api_keys if api_keys else None,
        )
    # Build providers from core.providers (archive adapters)
    from core.providers import (
        AnthropicAdapter,
        OpenAIAdapter,
        GitHubModelsAdapter,
        GrokAdapter,
        PerplexityAdapter,
        GeminiAdapter,
        MistralAdapter,
    )
    providers: Dict[str, ProviderAdapter] = {}
    if anthropic_api_key:
        providers["anthropic"] = AnthropicAdapter(anthropic_api_key)
    if openai_api_key:
        providers["openai"] = OpenAIAdapter(openai_api_key)
    if github_token:
        providers["github"] = GitHubModelsAdapter(github_token)
    if grok_api_key:
        providers["grok"] = GrokAdapter(grok_api_key)
    if perplexity_api_key:
        providers["perplexity"] = PerplexityAdapter(perplexity_api_key)
    if gemini_api_key:
        providers["gemini"] = GeminiAdapter(gemini_api_key)
    if mistral_api_key:
        providers["mistral"] = MistralAdapter(mistral_api_key)
    return IntelligentRouterV2(
        providers=providers,
        tier_configs=tier_configs,
        budget_manager=budget_manager,
        use_litellm=False,
    )
