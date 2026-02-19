"""
Tests for Session Extractor.
Tests extraction prompting, JSON parsing, tier classification, and dedup.
Uses mocks for Ollama and cloud model calls.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.memory.extractor import SessionExtractor, ExtractedFact, ExtractionResult


def _make_config():
    """Config for SessionExtractor tests — matches the __init__ kwargs."""
    return {
        "enabled": True,
        "cloud_threshold": "balanced",
        "cloud_model": "claude-haiku",
        "local_model": "llama3.2:latest",
        "max_cloud_cost": 0.02,
    }


def _make_conversation(n=5):
    """Create a simple conversation history."""
    messages = []
    for i in range(n):
        if i % 2 == 0:
            messages.append({"role": "user", "content": f"User message {i}"})
        else:
            messages.append({"role": "assistant", "content": f"Assistant response {i}"})
    return messages


class TestExtractedFact:
    """Test ExtractedFact dataclass."""

    def test_create_fact(self):
        fact = ExtractedFact(
            content="User prefers TypeScript",
            tier="stable",
            source_type="user_stated",
            domain="sigils",
            salience=0.9,
            tags=["preference", "language"],
        )
        assert fact.content == "User prefers TypeScript"
        assert fact.tier == "stable"
        assert fact.salience == 0.9


class TestExtractionResult:
    """Test ExtractionResult dataclass."""

    def test_default_values(self):
        result = ExtractionResult()
        assert result.stable_count == 0
        assert result.episodic_count == 0
        assert result.model_used == ""


class TestSessionExtractorInit:
    """Test SessionExtractor initialization."""

    def test_init_with_config(self):
        config = _make_config()
        mock_store = MagicMock()
        extractor = SessionExtractor(
            tiered_store=mock_store,
            config=config,
        )
        assert extractor.enabled is True
        assert extractor.cloud_model == "claude-haiku"
        assert extractor.local_model == "llama3.2:latest"

    def test_init_with_defaults(self):
        mock_store = MagicMock()
        extractor = SessionExtractor(
            tiered_store=mock_store,
            config={},
        )
        # Should use defaults
        assert extractor.enabled is True
        assert extractor.cloud_threshold == "balanced"


class TestSessionExtractorModelSelection:
    """Test model selection logic via _assess_session_value."""

    def test_simple_session_uses_local_model(self):
        config = _make_config()
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=config)
        # Short conversation with no decision signals → local
        conversation = _make_conversation(4)
        tier = extractor._assess_session_value(conversation, {})
        assert tier == "local"

    def test_complex_session_uses_cloud_model(self):
        config = _make_config()
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=config)
        # Long conversation (>20 exchanges) → cloud
        conversation = _make_conversation(50)
        tier = extractor._assess_session_value(
            conversation, {"exchange_count": 25}
        )
        assert tier == "cloud"


class TestSessionExtractorParsing:
    """Test JSON response parsing."""

    def test_parse_valid_json(self):
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=_make_config())

        # The extraction prompt asks for a JSON array of facts
        response_text = json.dumps([
            {
                "content": "User prefers Python",
                "tier": "stable",
                "source_type": "user_stated",
                "domain": "sigils",
                "salience": 0.9,
                "tags": ["language", "preference"],
            },
            {
                "content": "Decided to use FastAPI for the server",
                "tier": "episodic",
                "source_type": "decision",
                "domain": "sigils",
                "salience": 0.7,
                "tags": ["architecture"],
            },
        ])

        facts = extractor._parse_extraction_response(response_text)
        assert len(facts) == 2
        stable_facts = [f for f in facts if f.tier == "stable"]
        episodic_facts = [f for f in facts if f.tier == "episodic"]
        assert len(stable_facts) == 1
        assert len(episodic_facts) == 1
        assert stable_facts[0].content == "User prefers Python"

    def test_parse_json_in_markdown_block(self):
        """JSON wrapped in markdown code fence should still parse."""
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=_make_config())

        response_text = """Here are the extracted facts:
```json
[{"content": "Test fact", "tier": "stable", "source_type": "inferred", "domain": "general", "salience": 0.5, "tags": []}]
```"""

        facts = extractor._parse_extraction_response(response_text)
        assert len(facts) == 1
        assert facts[0].content == "Test fact"

    def test_parse_invalid_json_returns_empty(self):
        """Invalid JSON should return empty list, not crash."""
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=_make_config())

        facts = extractor._parse_extraction_response("This is not JSON at all")
        assert facts == []

    def test_parse_empty_response(self):
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=_make_config())
        facts = extractor._parse_extraction_response("")
        assert facts == []


class TestSessionExtractorMinMessages:
    """Test minimum message threshold."""

    @pytest.mark.asyncio
    async def test_too_few_messages_skips_extraction(self):
        """Sessions with fewer than 2 messages should be skipped."""
        config = _make_config()
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=config)
        # Only 1 message — should be skipped
        conversation = _make_conversation(1)
        result = await extractor.extract_and_store(conversation)
        assert result.model_used == "skipped_too_short"

    @pytest.mark.asyncio
    async def test_empty_conversation_skips_extraction(self):
        config = _make_config()
        mock_store = MagicMock()
        extractor = SessionExtractor(tiered_store=mock_store, config=config)
        result = await extractor.extract_and_store([])
        assert result.model_used == "skipped_too_short"
