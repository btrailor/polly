"""
Tests for dynamic domain configuration (integration-contracts Task 12).
Verifies YAML config load, custom domains, and fallback order.
"""

import pytest
from core.domains import (
    DomainEngine,
    DomainType,
    DomainConfig,
    load_domains_from_yaml,
)


def test_load_domains_from_yaml_dict():
    """load_domains_from_yaml with config_dict returns list of DomainConfig."""
    cfg = {
        "domains": {
            "sigils": {
                "name": "Sigils",
                "description": "Code & Infrastructure",
                "color": "#4A90D9",
                "keywords": ["docker", "python", "rust"],
                "rag_collections": ["codebase", "github"],
            },
        }
    }
    result = load_domains_from_yaml(config_dict=cfg)
    assert result is not None
    assert len(result) == 1
    assert result[0].id == "sigils"
    assert result[0].name == "Sigils"
    assert result[0].keywords == ["docker", "python", "rust"]
    assert result[0].rag_collections == ["codebase", "github"]


def test_domain_engine_with_yaml_config():
    """DomainEngine with config_dict uses YAML domains and keeps five + custom."""
    cfg = {
        "domains": {
            "sigils": {"name": "Sigils", "description": "Code", "keywords": ["python"]},
            "custom_domain": {"name": "Custom", "description": "Extra", "keywords": ["x"]},
        }
    }
    engine = DomainEngine(config_dict=cfg)
    assert DomainType.SIGILS in engine.domains
    assert engine.domains[DomainType.SIGILS].keywords == ["python"]
    assert len(engine._custom_domains) == 1
    assert engine._custom_domains[0].custom_id == "custom_domain"
    assert engine._custom_domains[0].name == "Custom"


def test_domain_engine_fallback_without_config():
    """DomainEngine with no config_dict uses domain_config or hardcoded."""
    engine = DomainEngine(config_domains=None, config_dict=None)
    assert len(engine.domains) >= 5
    for dt in [DomainType.SIGILS, DomainType.SIGNALS, DomainType.SCROLLS, DomainType.GLYPHS, DomainType.GRIDS]:
        assert dt in engine.domains


def test_yaml_empty_domains_returns_none():
    """Empty or missing domains key returns None."""
    assert load_domains_from_yaml(config_dict={}) is None
    assert load_domains_from_yaml(config_dict={"domains": {}}) is None
