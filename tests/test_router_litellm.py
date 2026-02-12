"""
Tests for Router v2 LiteLLM integration (Task 12).

When use_litellm=True, the router uses the single LiteLLM adapter for all
tier (provider, model) entries; _get_tier_candidates returns one candidate
per tier row with the LiteLLM adapter and the tier's model string.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_litellm_adapter():
    """Provider adapter that implements the interface used by router."""
    adapter = MagicMock()
    adapter.name = "litellm"
    adapter.get_models = Mock(return_value=[
        MagicMock(id="anthropic/claude-3-haiku-20240307"),
        MagicMock(id="openai/gpt-4o-mini"),
    ])
    adapter.estimate_cost = Mock(return_value=0.001)
    return adapter


@pytest.mark.asyncio
async def test_get_tier_candidates_uses_litellm_when_enabled(mock_litellm_adapter):
    """When use_litellm=True, _get_tier_candidates returns (litellm_adapter, model, priority) per tier row."""
    from core.router_v2 import IntelligentRouterV2, ConfidenceLevel
    
    with patch("polly_routing.providers.litellm.LiteLLMAdapter", MagicMock(return_value=mock_litellm_adapter)):
        router = IntelligentRouterV2(
            use_litellm=True,
            litellm_config_path="config/litellm_config.yaml",
            api_keys={"anthropic": "test"}
        )
    
    assert router.use_litellm is True
    assert "litellm" in router.providers
    tier_config = router.tier_configs[ConfidenceLevel.FAST]
    candidates = router._get_tier_candidates(tier_config)
    
    assert len(candidates) > 0
    for provider, model, priority in candidates:
        assert provider is mock_litellm_adapter
        assert isinstance(model, str)
        # Model should be one of the tier's configured models
        assert any(m in model for m in ["gpt", "claude", "gemini", "mistral", "sonar", "haiku"])


@pytest.mark.asyncio
async def test_route_returns_decision_when_litellm_enabled(mock_litellm_adapter):
    """When use_litellm=True, route() returns a RoutingDecision with the LiteLLM provider."""
    from core.router_v2 import IntelligentRouterV2, ConfidenceLevel
    
    with patch("polly_routing.providers.litellm.LiteLLMAdapter", MagicMock(return_value=mock_litellm_adapter)):
        router = IntelligentRouterV2(
            use_litellm=True,
            litellm_config_path="config/litellm_config.yaml",
            api_keys={"anthropic": "test"}
        )
    
    decision = await router.route(
        messages=[{"role": "user", "content": "What is 2+2?"}],
        confidence=ConfidenceLevel.FAST,
        max_tokens=100
    )
    
    assert decision is not None
    assert decision.provider is mock_litellm_adapter
    assert decision.model
    assert decision.confidence == ConfidenceLevel.FAST
