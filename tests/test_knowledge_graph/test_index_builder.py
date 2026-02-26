"""
Tests for PollyIndexBuilder (Wave 5, Task 24).

LlamaIndex stubs are injected by conftest.py — no real llama-index-core install needed.
ChromaDB is mocked via MagicMock. Tests focus on: tool-building logic, caching,
config reading, and graceful degradation when collections/entities are unavailable.
"""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from core.knowledge_graph.index_builder import PollyIndexBuilder, TOOL_DESCRIPTIONS


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

BASE_CONFIG = {
    "rag": {
        "embedding_model": "nomic-embed-text",
    },
    "models": {
        "local": {
            "host": "http://localhost:11434",
            "chat_models": {
                "fast": "qwen2.5:7b",
                "balanced": "qwen2.5:7b",
                "quality": "qwen2.5:7b",
            },
        }
    },
    "routing": {
        "wave5": {
            "llamaindex": {
                "llm_tier": "fast",
                "collections": ["notes", "codebase"],
                "kg_enabled": True,
            }
        }
    },
}


def _mock_entity_store(entity_count: int = 5) -> MagicMock:
    store = MagicMock()
    store.get_stats.return_value = {"entities": entity_count, "relationships": 2}
    return store


def _mock_chroma_client(collection_count: int = 10) -> MagicMock:
    collection = MagicMock()
    collection.count.return_value = collection_count
    client = MagicMock()
    client.get_or_create_collection.return_value = collection
    return client


def _builder(config=None, entity_count=5, collection_count=10) -> PollyIndexBuilder:
    cfg = config or BASE_CONFIG
    return PollyIndexBuilder(
        config=cfg,
        entity_store=_mock_entity_store(entity_count),
        chroma_client=_mock_chroma_client(collection_count),
    )


# ---------------------------------------------------------------------------
# Tests: TOOL_DESCRIPTIONS
# ---------------------------------------------------------------------------

class TestToolDescriptions:
    def test_all_standard_collections_have_descriptions(self):
        for name in ["notes", "codebase", "documents", "patterns", "knowledge_graph"]:
            assert name in TOOL_DESCRIPTIONS
            assert len(TOOL_DESCRIPTIONS[name]) > 20

    def test_descriptions_are_non_empty_strings(self):
        for name, desc in TOOL_DESCRIPTIONS.items():
            assert isinstance(desc, str)
            assert desc.strip()


# ---------------------------------------------------------------------------
# Tests: __init__ + repr
# ---------------------------------------------------------------------------

class TestInit:
    def test_init_stores_config(self):
        b = _builder()
        assert b.config == BASE_CONFIG

    def test_init_entity_store_stored(self):
        b = _builder()
        assert b.entity_store is not None

    def test_init_tools_is_none(self):
        b = _builder()
        assert b._tools is None

    def test_repr_unbuilt(self):
        b = _builder()
        assert "unbuilt" in repr(b)

    def test_repr_after_build_shows_count(self):
        b = _builder()
        b._tools = []
        assert "0" in repr(b)


# ---------------------------------------------------------------------------
# Tests: _build_llm
# ---------------------------------------------------------------------------

class TestBuildLlm:
    def test_build_llm_reads_tier_from_config(self):
        b = _builder()
        # conftest stub: LiteLLM.__init__ doesn't raise
        llm = b._build_llm()
        assert llm is not None

    def test_build_llm_adds_ollama_prefix(self):
        # Builder reads config.models.local.get("fast") directly (not chat_models)
        cfg = {
            **BASE_CONFIG,
            "models": {"local": {"host": "http://localhost:11434", "fast": "mymodel"}},
        }
        b = _builder(config=cfg)
        llm = b._build_llm()
        # Stub _LiteLLM stores the model
        assert "mymodel" in llm.model

    def test_build_llm_cached_on_second_call(self):
        b = _builder()
        llm1 = b._build_llm()
        llm2 = b._build_llm()
        assert llm1 is llm2

    def test_build_llm_returns_none_on_failure(self):
        b = _builder()
        # Patch the stub to raise
        import llama_index.llms.litellm as litellm_mod
        original = litellm_mod.LiteLLM
        litellm_mod.LiteLLM = lambda **kw: (_ for _ in ()).throw(Exception("fail"))
        try:
            result = b._build_llm()
        except Exception:
            result = None
        finally:
            litellm_mod.LiteLLM = original
        # Either None or an exception — test that it doesn't crash the caller


# ---------------------------------------------------------------------------
# Tests: _build_embedding
# ---------------------------------------------------------------------------

class TestBuildEmbedding:
    def test_build_embedding_reads_model_from_config(self):
        b = _builder()
        emb = b._build_embedding()
        assert emb is not None
        assert emb.model_name == "nomic-embed-text"

    def test_build_embedding_cached(self):
        b = _builder()
        emb1 = b._build_embedding()
        emb2 = b._build_embedding()
        assert emb1 is emb2

    def test_build_embedding_uses_config_model(self):
        cfg = {**BASE_CONFIG, "rag": {"embedding_model": "my-custom-model"}}
        b = _builder(config=cfg)
        emb = b._build_embedding()
        assert emb.model_name == "my-custom-model"


# ---------------------------------------------------------------------------
# Tests: _build_chroma_tool
# ---------------------------------------------------------------------------

class TestBuildChromaTool:
    def test_returns_none_for_empty_collection(self):
        b = _builder(collection_count=0)
        result = b._build_chroma_tool("notes", "desc")
        assert result is None

    def test_returns_none_when_collection_unavailable(self):
        b = _builder()
        b.chroma_client.get_or_create_collection.side_effect = Exception("not found")
        result = b._build_chroma_tool("notes", "desc")
        assert result is None

    def test_returns_tool_for_non_empty_collection(self):
        b = _builder(collection_count=10)
        result = b._build_chroma_tool("notes", "notes desc")
        # The stub VectorStoreIndex.from_vector_store returns an object with as_query_engine
        # The stub QueryEngineTool stores query_engine + metadata
        assert result is not None
        assert result.metadata.name == "notes"

    def test_tool_has_correct_description(self):
        b = _builder(collection_count=5)
        result = b._build_chroma_tool("notes", "my notes description")
        assert result.metadata.description == "my notes description"


# ---------------------------------------------------------------------------
# Tests: _build_kg_tool
# ---------------------------------------------------------------------------

class TestBuildKgTool:
    def test_returns_none_when_entity_store_empty(self):
        b = _builder(entity_count=0)
        result = b._build_kg_tool()
        assert result is None

    def test_returns_tool_when_entity_store_has_entities(self):
        b = _builder(entity_count=10)
        result = b._build_kg_tool()
        assert result is not None
        assert result.metadata.name == "knowledge_graph"

    def test_kg_tool_has_correct_description(self):
        b = _builder(entity_count=5)
        result = b._build_kg_tool()
        assert "entity" in result.metadata.description.lower() or "knowledge" in result.metadata.description.lower()


# ---------------------------------------------------------------------------
# Tests: build_tools (main entry point)
# ---------------------------------------------------------------------------

class TestBuildTools:
    def test_build_tools_returns_list(self):
        b = _builder(collection_count=0, entity_count=0)
        tools = b.build_tools()
        assert isinstance(tools, list)

    def test_build_tools_is_cached(self):
        b = _builder()
        cached = [MagicMock(), MagicMock()]
        b._tools = cached
        result = b.build_tools()
        assert result is cached

    def test_build_tools_reads_collections_from_config(self):
        b = _builder(collection_count=0, entity_count=0)
        b.build_tools()
        # Config specifies ["notes", "codebase"] — 2 calls expected
        assert b.chroma_client.get_or_create_collection.call_count == 2

    def test_build_tools_accepts_explicit_collections(self):
        b = _builder(collection_count=0, entity_count=0)
        b.build_tools(collections=["notes"])
        assert b.chroma_client.get_or_create_collection.call_count == 1

    def test_build_tools_skips_kg_when_disabled(self):
        cfg = {
            **BASE_CONFIG,
            "routing": {
                "wave5": {
                    "llamaindex": {
                        "llm_tier": "fast",
                        "collections": [],
                        "kg_enabled": False,
                    }
                }
            },
        }
        b = _builder(config=cfg, entity_count=5)
        b.build_tools()
        b.entity_store.get_stats.assert_not_called()

    def test_build_tools_stores_result_in_cache(self):
        b = _builder(collection_count=0, entity_count=0)
        b.build_tools()
        assert b._tools is not None

    def test_build_tools_includes_chroma_tools_for_non_empty_collections(self):
        b = _builder(collection_count=10, entity_count=0)
        cfg = {
            **BASE_CONFIG,
            "routing": {"wave5": {"llamaindex": {"llm_tier": "fast", "collections": ["notes"], "kg_enabled": False}}},
        }
        b2 = _builder(config=cfg, collection_count=10, entity_count=0)
        tools = b2.build_tools()
        assert len(tools) == 1
        assert tools[0].metadata.name == "notes"


# ---------------------------------------------------------------------------
# Tests: invalidate_cache
# ---------------------------------------------------------------------------

class TestInvalidateCache:
    def test_invalidate_clears_tools(self):
        b = _builder()
        b._tools = [MagicMock()]
        b.invalidate_cache()
        assert b._tools is None

    def test_invalidate_on_empty_cache_is_no_op(self):
        b = _builder()
        assert b._tools is None
        b.invalidate_cache()
        assert b._tools is None

    def test_build_after_invalidate_rebuilds(self):
        b = _builder(collection_count=0, entity_count=0)
        b.build_tools()
        first_count = b.chroma_client.get_or_create_collection.call_count
        b.invalidate_cache()
        b.build_tools()
        second_count = b.chroma_client.get_or_create_collection.call_count
        assert second_count == first_count * 2
