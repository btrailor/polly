"""
Tests for QueryDecomposerV2 (Wave 5, Task 24).

LlamaIndex stubs are injected by conftest.py — no real llama-index-core install needed.
Tests cover: V1 fallback, sub-query extraction, tool mapping, DecompositionResult structure.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.query_decomposition import SubQueryType, DecompositionResult, SubQuery
from core.knowledge_graph.query_decomposition_v2 import QueryDecomposerV2


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BASE_CONFIG = {
    "routing": {
        "decomposition": {
            "enabled": True,
            "min_complexity_score": 0.35,
            "model": "fast",
        },
        "wave5": {
            "llamaindex": {"llm_tier": "fast"},
        },
    },
    "models": {
        "local": {
            "host": "http://localhost:11434",
            "chat_models": {"fast": "qwen2.5:7b"},
        }
    },
}


def _mock_index_builder(num_tools: int = 2) -> MagicMock:
    builder = MagicMock()
    builder.build_tools.return_value = [MagicMock() for _ in range(num_tools)]
    builder._build_llm.return_value = MagicMock()
    return builder


def _decomposer(llama_available: bool = True, num_tools: int = 2) -> QueryDecomposerV2:
    index_builder = _mock_index_builder(num_tools) if llama_available else None
    d = QueryDecomposerV2(
        config=BASE_CONFIG,
        router=None,
        pattern_learner=None,
        index_builder=index_builder,
    )
    d._llama_available = llama_available and index_builder is not None
    return d


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Tests: __init__
# ---------------------------------------------------------------------------

class TestInit:
    def test_inherits_query_decomposer(self):
        from core.query_decomposition import QueryDecomposer
        d = _decomposer(llama_available=False)
        assert isinstance(d, QueryDecomposer)

    def test_index_builder_stored(self):
        builder = _mock_index_builder()
        d = QueryDecomposerV2(BASE_CONFIG, index_builder=builder)
        assert d.index_builder is builder

    def test_engine_not_initialized_at_creation(self):
        d = _decomposer()
        assert d._sub_question_engine is None

    def test_llama_unavailable_when_no_index_builder(self):
        d = QueryDecomposerV2(BASE_CONFIG, index_builder=None)
        assert d._llama_available is False

    def test_llama_unavailable_when_import_fails(self):
        import sys
        # Temporarily remove llama_index from sys.modules to simulate ImportError
        llama_mods = {k: v for k, v in sys.modules.items() if k.startswith("llama_index")}
        for k in llama_mods:
            del sys.modules[k]
        try:
            d = QueryDecomposerV2(BASE_CONFIG, index_builder=_mock_index_builder())
            assert d._llama_available is False
        finally:
            sys.modules.update(llama_mods)

    def test_repr_contains_class_name(self):
        d = _decomposer()
        r = repr(d)
        assert "QueryDecomposerV2" in r


# ---------------------------------------------------------------------------
# Tests: _ensure_engine
# ---------------------------------------------------------------------------

class TestEnsureEngine:
    def test_returns_false_when_not_available(self):
        d = _decomposer(llama_available=False)
        result = d._ensure_engine()
        assert result is False

    def test_returns_false_when_no_tools(self):
        d = _decomposer(num_tools=0)
        result = d._ensure_engine()
        assert result is False
        # Should have disabled llama
        assert d._llama_available is False

    def test_returns_true_and_sets_engine(self):
        d = _decomposer(num_tools=2)
        result = d._ensure_engine()
        assert result is True
        assert d._sub_question_engine is not None

    def test_returns_true_when_engine_already_set(self):
        d = _decomposer()
        d._sub_question_engine = MagicMock()
        result = d._ensure_engine()
        assert result is True
        # Should not have rebuilt (index_builder not called again)

    def test_disables_llama_when_tools_empty(self):
        d = _decomposer(num_tools=0)
        d._ensure_engine()
        assert d._llama_available is False


# ---------------------------------------------------------------------------
# Tests: _tool_to_subquery_type (static method)
# ---------------------------------------------------------------------------

class TestToolToSubqueryType:
    @pytest.mark.parametrize("tool_name,expected", [
        ("notes", SubQueryType.RAG_ANSWERABLE),
        ("codebase", SubQueryType.CODE_GEN),
        ("documents", SubQueryType.FACTUAL),
        ("patterns", SubQueryType.ANALYSIS),
        ("knowledge_graph", SubQueryType.REASONING),
        ("unknown_tool", SubQueryType.REASONING),
        ("", SubQueryType.REASONING),
    ])
    def test_mapping(self, tool_name, expected):
        result = QueryDecomposerV2._tool_to_subquery_type(tool_name)
        assert result == expected


# ---------------------------------------------------------------------------
# Tests: _extract_sub_queries
# ---------------------------------------------------------------------------

class TestExtractSubQueries:
    def _make_response(self, sub_question_responses=None, full_text="full answer"):
        response = MagicMock()
        response.__str__ = lambda self: full_text
        if sub_question_responses is not None:
            response.metadata = {"sub_question_responses": sub_question_responses}
        else:
            response.metadata = {}
        return response

    def test_empty_metadata_returns_single_reasoning_subquery(self):
        d = _decomposer()
        response = self._make_response()
        sub_queries = d._extract_sub_queries(response, "test query")
        assert len(sub_queries) == 1
        assert sub_queries[0].type == SubQueryType.REASONING
        assert "llamaindex_answer" in sub_queries[0].metadata

    def test_sub_question_responses_parsed_correctly(self):
        d = _decomposer()
        sqrs = [
            {"sub_q": {"sub_question": "What is Python?", "tool_name": "notes"}, "answer": "Python is a language."},
            {"sub_q": {"sub_question": "Show code", "tool_name": "codebase"}, "answer": "def f(): pass"},
        ]
        response = self._make_response(sub_question_responses=sqrs)
        sub_queries = d._extract_sub_queries(response, "original query")
        assert len(sub_queries) == 2
        assert sub_queries[0].query == "What is Python?"
        assert sub_queries[0].type == SubQueryType.RAG_ANSWERABLE
        assert sub_queries[0].metadata["llamaindex_answer"] == "Python is a language."
        assert sub_queries[0].metadata["source"] == "llamaindex_sub_question_engine"
        assert sub_queries[1].type == SubQueryType.CODE_GEN

    def test_empty_sub_question_responses_returns_fallback(self):
        d = _decomposer()
        response = self._make_response(sub_question_responses=[])
        sub_queries = d._extract_sub_queries(response, "query")
        assert len(sub_queries) == 1
        assert sub_queries[0].type == SubQueryType.REASONING

    def test_sub_query_has_required_fields(self):
        d = _decomposer()
        response = self._make_response(
            sub_question_responses=[
                {"sub_q": {"sub_question": "Q1", "tool_name": "notes"}, "answer": "A1"}
            ]
        )
        sub_queries = d._extract_sub_queries(response, "query")
        sq = sub_queries[0]
        assert isinstance(sq, SubQuery)
        assert sq.query == "Q1"
        assert sq.confidence == 0.9
        assert sq.metadata["tool_name"] == "notes"

    def test_fallback_sets_llamaindex_answer_in_metadata(self):
        d = _decomposer()
        response = self._make_response(full_text="synthesized answer")
        sub_queries = d._extract_sub_queries(response, "q")
        assert sub_queries[0].metadata["llamaindex_answer"] is not None


# ---------------------------------------------------------------------------
# Tests: _llm_decompose (the main override)
# ---------------------------------------------------------------------------

class TestLlmDecompose:
    def test_falls_back_to_v1_when_unavailable(self):
        d = _decomposer(llama_available=False)
        v1_result = DecompositionResult(
            sub_queries=[SubQuery(query="q", type=SubQueryType.REASONING, confidence=0.8)],
            original_query="q",
            is_complex=False,
            reasoning="v1",
        )
        with patch("core.query_decomposition.QueryDecomposer._llm_decompose", new_callable=AsyncMock) as mock_v1:
            mock_v1.return_value = v1_result
            result = _run(d._llm_decompose("q", {}))
        assert result is v1_result

    def test_falls_back_to_v1_when_engine_not_ready(self):
        d = _decomposer(num_tools=0)  # no tools → engine won't init
        v1_result = DecompositionResult(
            sub_queries=[SubQuery(query="q", type=SubQueryType.REASONING, confidence=0.8)],
            original_query="q",
            is_complex=False,
            reasoning="v1",
        )
        with patch("core.query_decomposition.QueryDecomposer._llm_decompose", new_callable=AsyncMock) as mock_v1:
            mock_v1.return_value = v1_result
            result = _run(d._llm_decompose("q", {}))
        assert result is v1_result

    def test_falls_back_to_v1_when_llamaindex_raises(self):
        d = _decomposer(num_tools=2)
        v1_result = DecompositionResult(
            sub_queries=[SubQuery(query="q", type=SubQueryType.REASONING, confidence=0.8)],
            original_query="q",
            is_complex=False,
            reasoning="v1",
        )
        with patch.object(d, "_llamaindex_decompose", new_callable=AsyncMock) as mock_li:
            mock_li.side_effect = Exception("engine crash")
            with patch("core.query_decomposition.QueryDecomposer._llm_decompose", new_callable=AsyncMock) as mock_v1:
                mock_v1.return_value = v1_result
                result = _run(d._llm_decompose("q", {}))
        assert result is v1_result

    def test_uses_llamaindex_when_available(self):
        d = _decomposer(num_tools=2)
        li_result = DecompositionResult(
            sub_queries=[
                SubQuery(
                    query="sub1",
                    type=SubQueryType.RAG_ANSWERABLE,
                    confidence=0.9,
                    metadata={"llamaindex_answer": "ans", "source": "llamaindex_sub_question_engine"},
                )
            ],
            original_query="complex query",
            is_complex=True,
            reasoning="LlamaIndex decomposed",
        )
        with patch.object(d, "_llamaindex_decompose", new_callable=AsyncMock) as mock_li:
            mock_li.return_value = li_result
            result = _run(d._llm_decompose("complex query", {}))
        assert result is li_result


# ---------------------------------------------------------------------------
# Tests: _llamaindex_decompose
# ---------------------------------------------------------------------------

class TestLlamaindexDecompose:
    """Tests for _llamaindex_decompose. Uses a MagicMock engine to control query() output."""

    def _decomposer_with_mock_engine(self) -> QueryDecomposerV2:
        d = _decomposer(num_tools=2)
        # Replace the conftest stub with a MagicMock so we can set return_value
        d._sub_question_engine = MagicMock()
        return d

    def test_runs_engine_and_returns_decomposition_result(self):
        d = self._decomposer_with_mock_engine()
        mock_response = MagicMock()
        mock_response.metadata = {
            "sub_question_responses": [
                {"sub_q": {"sub_question": "Q1", "tool_name": "notes"}, "answer": "A1"}
            ]
        }
        d._sub_question_engine.query.return_value = mock_response

        result = _run(d._llamaindex_decompose("test query", {}))

        assert isinstance(result, DecompositionResult)
        assert result.original_query == "test query"
        assert len(result.sub_queries) == 1
        assert result.is_complex is False

    def test_multiple_sub_queries_marks_as_complex(self):
        d = self._decomposer_with_mock_engine()
        mock_response = MagicMock()
        mock_response.metadata = {
            "sub_question_responses": [
                {"sub_q": {"sub_question": "Q1", "tool_name": "notes"}, "answer": "A1"},
                {"sub_q": {"sub_question": "Q2", "tool_name": "codebase"}, "answer": "A2"},
            ]
        }
        d._sub_question_engine.query.return_value = mock_response

        result = _run(d._llamaindex_decompose("complex query", {}))
        assert result.is_complex is True
        assert len(result.sub_queries) == 2

    def test_reasoning_field_mentions_llamaindex(self):
        d = self._decomposer_with_mock_engine()
        mock_response = MagicMock()
        mock_response.metadata = {
            "sub_question_responses": [
                {"sub_q": {"sub_question": "Q1", "tool_name": "notes"}, "answer": "A1"},
            ]
        }
        d._sub_question_engine.query.return_value = mock_response

        result = _run(d._llamaindex_decompose("q", {}))
        assert "LlamaIndex" in result.reasoning or "sub-question" in result.reasoning.lower()

    def test_result_has_original_query(self):
        d = self._decomposer_with_mock_engine()
        mock_response = MagicMock()
        mock_response.metadata = {"sub_question_responses": []}
        d._sub_question_engine.query.return_value = mock_response

        result = _run(d._llamaindex_decompose("my original query", {}))
        assert result.original_query == "my original query"
