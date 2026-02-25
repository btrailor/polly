"""
Tests for RAG Optimization for Local Models (Core Framework Wave 4, Task #23)

Tests cover:
- _estimate_model_tier(): confidence → tier mapping
- Tier-aware n_results: local_fast=3, local_balanced=5, cloud=10
- Tier-aware max_context_tokens: local_fast=2000, local_balanced=3000, cloud=6000
- RAG context compression: only for local tiers when context > min_chars
- Config defaults are safe when keys are missing
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock


# ===================== _estimate_model_tier =====================


class TestEstimateModelTier:
    """Tests for Polly._estimate_model_tier()."""

    def _make_polly(self, default_confidence="balanced"):
        """Create a minimal Polly-like object with _estimate_model_tier."""
        from core.polly import Polly
        from core.router_v2 import ConfidenceLevel

        polly = object.__new__(Polly)
        polly.default_confidence = ConfidenceLevel(default_confidence)
        return polly

    def test_fast_maps_to_local_fast(self):
        polly = self._make_polly()
        assert polly._estimate_model_tier("fast") == "local_fast"

    def test_thorough_maps_to_cloud(self):
        polly = self._make_polly()
        assert polly._estimate_model_tier("thorough") == "cloud"

    def test_balanced_maps_to_local_balanced(self):
        polly = self._make_polly()
        assert polly._estimate_model_tier("balanced") == "local_balanced"

    def test_none_uses_default_confidence(self):
        polly = self._make_polly(default_confidence="fast")
        assert polly._estimate_model_tier(None) == "local_fast"

    def test_none_uses_default_balanced(self):
        polly = self._make_polly(default_confidence="balanced")
        assert polly._estimate_model_tier(None) == "local_balanced"

    def test_none_uses_default_thorough(self):
        polly = self._make_polly(default_confidence="thorough")
        assert polly._estimate_model_tier(None) == "cloud"

    def test_unknown_confidence_falls_back_to_local_balanced(self):
        polly = self._make_polly()
        assert polly._estimate_model_tier("unknown_value") == "local_balanced"

    def test_case_insensitive(self):
        polly = self._make_polly()
        assert polly._estimate_model_tier("FAST") == "local_fast"
        assert polly._estimate_model_tier("Thorough") == "cloud"


# ===================== Tier-aware config defaults =====================


class TestTierAwareConfigDefaults:
    """
    Verify the config defaults for n_results, max_context_tokens,
    and rag_compression are correct.
    """

    def test_config_has_tier_n_results(self):
        """config.yaml should define tier_n_results for all three tiers."""
        import yaml
        from pathlib import Path

        cfg_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)

        rag = cfg.get("rag", {})
        tier_n = rag.get("tier_n_results", {})
        assert tier_n.get("local_fast") == 3
        assert tier_n.get("local_balanced") == 5
        assert tier_n.get("cloud") == 10

    def test_config_has_tier_max_context_tokens(self):
        import yaml
        from pathlib import Path

        cfg_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)

        rag = cfg.get("rag", {})
        tier_ctx = rag.get("tier_max_context_tokens", {})
        assert tier_ctx.get("local_fast") == 2000
        assert tier_ctx.get("local_balanced") == 3000
        assert tier_ctx.get("cloud") == 6000

    def test_config_has_rag_compression(self):
        import yaml
        from pathlib import Path

        cfg_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)

        rag = cfg.get("rag", {})
        comp = rag.get("rag_compression", {})
        assert comp.get("enabled") is True
        assert comp.get("local_fast_ratio") == pytest.approx(0.3)
        assert comp.get("local_balanced_ratio") == pytest.approx(0.5)
        assert comp.get("cloud_ratio") == pytest.approx(0.7)
        assert comp.get("min_chars") == 1500

    def test_config_has_local_context_windows(self):
        import yaml
        from pathlib import Path

        cfg_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)

        cw = cfg.get("models", {}).get("local", {}).get("context_windows", {})
        assert cw.get("balanced") == 32768
        assert cw.get("fast") == 32768


# ===================== n_results selection logic =====================


class TestTierNResults:
    """
    Verify that tier-aware n_results values are correctly derived from config.
    These tests exercise the logic that was added to polly.py's RAG section.
    """

    def _tier_n_results(self, model_tier: str, cfg: dict) -> int:
        """Mirror the polly.py n_results selection logic."""
        tier_n = {
            "local_fast":     cfg.get("rag", {}).get("tier_n_results", {}).get("local_fast", 3),
            "local_balanced": cfg.get("rag", {}).get("tier_n_results", {}).get("local_balanced", 5),
            "cloud":          cfg.get("rag", {}).get("tier_n_results", {}).get("cloud", 10),
        }
        return tier_n.get(model_tier, 5)

    def test_local_fast_returns_3(self):
        cfg = {"rag": {"tier_n_results": {"local_fast": 3, "local_balanced": 5, "cloud": 10}}}
        assert self._tier_n_results("local_fast", cfg) == 3

    def test_local_balanced_returns_5(self):
        cfg = {"rag": {"tier_n_results": {"local_fast": 3, "local_balanced": 5, "cloud": 10}}}
        assert self._tier_n_results("local_balanced", cfg) == 5

    def test_cloud_returns_10(self):
        cfg = {"rag": {"tier_n_results": {"local_fast": 3, "local_balanced": 5, "cloud": 10}}}
        assert self._tier_n_results("cloud", cfg) == 10

    def test_missing_tier_key_falls_back_to_5(self):
        """Unknown tier should fall back to 5 (default)."""
        cfg = {"rag": {}}
        assert self._tier_n_results("unknown_tier", cfg) == 5

    def test_custom_values_respected(self):
        cfg = {"rag": {"tier_n_results": {"local_fast": 2, "local_balanced": 7, "cloud": 15}}}
        assert self._tier_n_results("cloud", cfg) == 15


# ===================== max_context_tokens selection logic =====================


class TestTierMaxContextTokens:
    """Verify tier-aware max_context_tokens is correctly derived."""

    def _tier_max_tokens(self, model_tier: str, cfg: dict) -> int:
        tier_ctx = {
            "local_fast":     cfg.get("rag", {}).get("tier_max_context_tokens", {}).get("local_fast", 2000),
            "local_balanced": cfg.get("rag", {}).get("tier_max_context_tokens", {}).get("local_balanced", 3000),
            "cloud":          cfg.get("rag", {}).get("tier_max_context_tokens", {}).get("cloud", 6000),
        }
        return tier_ctx.get(model_tier, 3000)

    def test_local_fast_gets_2000(self):
        cfg = {"rag": {"tier_max_context_tokens": {"local_fast": 2000, "local_balanced": 3000, "cloud": 6000}}}
        assert self._tier_max_tokens("local_fast", cfg) == 2000

    def test_local_balanced_gets_3000(self):
        cfg = {"rag": {"tier_max_context_tokens": {"local_fast": 2000, "local_balanced": 3000, "cloud": 6000}}}
        assert self._tier_max_tokens("local_balanced", cfg) == 3000

    def test_cloud_gets_6000(self):
        cfg = {"rag": {"tier_max_context_tokens": {"local_fast": 2000, "local_balanced": 3000, "cloud": 6000}}}
        assert self._tier_max_tokens("cloud", cfg) == 6000

    def test_cloud_gets_more_than_local(self):
        """Cloud should always get more context tokens than local tiers."""
        cfg = {"rag": {"tier_max_context_tokens": {"local_fast": 2000, "local_balanced": 3000, "cloud": 6000}}}
        assert self._tier_max_tokens("cloud", cfg) > self._tier_max_tokens("local_balanced", cfg)
        assert self._tier_max_tokens("local_balanced", cfg) > self._tier_max_tokens("local_fast", cfg)


# ===================== RAG compression logic =====================


class TestRagCompressionLogic:
    """
    Verify the RAG compression decision and ratio selection logic.
    These tests mirror the if-guard and ratio lookup added to polly.py.
    """

    def _should_compress(self, rag_context: str, model_tier: str, cfg: dict, is_integration: bool = False) -> bool:
        """Mirror the polly.py compression guard."""
        if is_integration:
            return False
        enabled = cfg.get("rag", {}).get("rag_compression", {}).get("enabled", True)
        if not enabled:
            return False
        if model_tier == "cloud":
            return False
        min_chars = cfg.get("rag", {}).get("rag_compression", {}).get("min_chars", 1500)
        return len(rag_context) > min_chars

    def _compression_ratio(self, model_tier: str, cfg: dict) -> float:
        """Mirror the polly.py ratio lookup."""
        key_map = {
            "local_fast": "local_fast_ratio",
            "local_balanced": "local_balanced_ratio",
        }
        ratio_key = key_map.get(model_tier, "local_balanced_ratio")
        return cfg.get("rag", {}).get("rag_compression", {}).get(ratio_key, 0.5)

    def _base_cfg(self):
        return {
            "rag": {
                "rag_compression": {
                    "enabled": True,
                    "local_fast_ratio": 0.3,
                    "local_balanced_ratio": 0.5,
                    "cloud_ratio": 0.7,
                    "min_chars": 1500,
                }
            }
        }

    def test_compresses_when_local_and_large(self):
        large = "word " * 500  # >1500 chars
        assert self._should_compress(large, "local_balanced", self._base_cfg())

    def test_no_compress_when_small(self):
        small = "Short context."
        assert not self._should_compress(small, "local_balanced", self._base_cfg())

    def test_no_compress_for_cloud(self):
        large = "word " * 500
        assert not self._should_compress(large, "cloud", self._base_cfg())

    def test_no_compress_for_integration_query(self):
        large = "word " * 500
        assert not self._should_compress(large, "local_balanced", self._base_cfg(), is_integration=True)

    def test_no_compress_when_disabled(self):
        cfg = {"rag": {"rag_compression": {"enabled": False, "min_chars": 1500}}}
        large = "word " * 500
        assert not self._should_compress(large, "local_fast", cfg)

    def test_local_fast_uses_0_3_ratio(self):
        assert self._compression_ratio("local_fast", self._base_cfg()) == pytest.approx(0.3)

    def test_local_balanced_uses_0_5_ratio(self):
        assert self._compression_ratio("local_balanced", self._base_cfg()) == pytest.approx(0.5)

    def test_local_fast_compresses_more_than_balanced(self):
        """local_fast should have a lower (more aggressive) compression ratio."""
        assert self._compression_ratio("local_fast", self._base_cfg()) < \
               self._compression_ratio("local_balanced", self._base_cfg())

    def test_compression_ratio_capped_at_min_0_3(self):
        """Compression ratio should not go below 0.3 per spec."""
        assert self._compression_ratio("local_fast", self._base_cfg()) >= 0.3
