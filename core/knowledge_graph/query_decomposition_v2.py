"""
Query Decomposition V2 — LlamaIndex SubQuestionQueryEngine (Wave 5, Task 24)

Drop-in replacement for QueryDecomposer. Same public interface, same config keys.

Upgrade strategy:
  - Inherits QueryDecomposer and overrides _llm_decompose() only
  - If LlamaIndex is unavailable or fails, falls back to V1 LLM decomposition
  - The SubQuestionQueryEngine handles both decomposition AND retrieval for each
    sub-question. When it pre-answers a sub-query, SplitRouter short-circuits
    the LLM call and uses the cached answer from metadata["llamaindex_answer"].

Fallback chain:
  LlamaIndex SubQuestionQueryEngine → V1 LLM decompose → simple query result
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from core.query_decomposition import (
    DecompositionResult,
    QueryDecomposer,
    SubQuery,
    SubQueryType,
)

logger = logging.getLogger(__name__)


class QueryDecomposerV2(QueryDecomposer):
    """
    Upgraded query decomposer using LlamaIndex SubQuestionQueryEngine.

    Drop-in replacement for QueryDecomposer with the same public interface.

    The SubQuestionQueryEngine:
    1. Generates sub-questions for the user query
    2. Routes each sub-question to the best tool (notes, codebase, KG, etc.)
    3. Retrieves answers per sub-question
    4. Synthesizes a final answer

    We intercept the sub-questions AND their tool-specific answers to return
    a DecompositionResult that SplitRouter can process. The pre-answered
    sub-queries have metadata["llamaindex_answer"] set so SplitRouter skips
    the redundant LLM call.

    Usage:
        builder = PollyIndexBuilder(config, entity_store, chroma_client)
        decomposer = QueryDecomposerV2(config, router, index_builder=builder)
        result = await decomposer.decompose(query, context)
        # Returns DecompositionResult — identical structure to V1
    """

    def __init__(
        self,
        config: Dict[str, Any],
        router: Any = None,
        pattern_learner: Any = None,
        index_builder: Optional[Any] = None,  # PollyIndexBuilder
    ) -> None:
        super().__init__(config, router, pattern_learner)
        self.index_builder = index_builder
        self._sub_question_engine: Optional[Any] = None
        self._llama_available: bool = False

        # Check if LlamaIndex is importable (don't init yet — lazy)
        try:
            import llama_index.core  # noqa: F401
            self._llama_available = index_builder is not None
        except ImportError:
            logger.info(
                "QueryDecomposerV2: llama-index-core not installed, "
                "falling back to V1 decomposition"
            )

    # ---- Engine initialization (lazy) ----

    def _ensure_engine(self) -> bool:
        """
        Initialize SubQuestionQueryEngine on first use.

        Returns True if engine is ready, False if initialization failed.
        LlamaIndex import happens here (not at module load) to avoid startup cost.
        """
        if self._sub_question_engine is not None:
            return True
        if not self._llama_available or self.index_builder is None:
            return False

        try:
            from llama_index.core.query_engine import SubQuestionQueryEngine
            from llama_index.core.question_gen import LLMQuestionGenerator

            tools = self.index_builder.build_tools()
            if not tools:
                logger.warning(
                    "QueryDecomposerV2: no tools built (empty collections?), "
                    "falling back to V1"
                )
                self._llama_available = False
                return False

            llm = self.index_builder._build_llm()
            question_gen_kwargs: Dict[str, Any] = {}
            if llm is not None:
                question_gen_kwargs["llm"] = llm

            question_gen = LLMQuestionGenerator.from_defaults(**question_gen_kwargs)
            self._sub_question_engine = SubQuestionQueryEngine.from_defaults(
                query_engine_tools=tools,
                question_gen=question_gen,
                use_async=False,  # We run in thread pool anyway
                verbose=False,
            )
            logger.info(
                f"QueryDecomposerV2: SubQuestionQueryEngine ready "
                f"with {len(tools)} tools"
            )
            return True
        except Exception as e:
            logger.warning(
                f"QueryDecomposerV2: SubQuestionQueryEngine init failed ({e}), "
                "falling back to V1"
            )
            self._llama_available = False
            return False

    # ---- Override: _llm_decompose ----

    async def _llm_decompose(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> DecompositionResult:
        """
        Override V1 LLM decompose with LlamaIndex SubQuestionQueryEngine.

        Falls back to super()._llm_decompose() if LlamaIndex is unavailable
        or the engine fails.
        """
        if not self._llama_available:
            return await super()._llm_decompose(query, context)

        if not self._ensure_engine():
            return await super()._llm_decompose(query, context)

        try:
            return await self._llamaindex_decompose(query, context)
        except Exception as e:
            logger.warning(
                f"QueryDecomposerV2: LlamaIndex decomposition failed ({e}), "
                "falling back to V1"
            )
            return await super()._llm_decompose(query, context)

    async def _llamaindex_decompose(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> DecompositionResult:
        """
        Run SubQuestionQueryEngine and capture sub-questions + answers.

        The engine generates sub-questions, routes them to tools, retrieves
        answers, and synthesizes a final response. We capture the sub-questions
        and per-tool answers so SplitRouter can short-circuit redundant LLM calls.
        """
        loop = asyncio.get_event_loop()

        # Run in thread pool to avoid blocking the event loop
        response = await loop.run_in_executor(
            None,
            lambda: self._sub_question_engine.query(query),
        )

        sub_queries = self._extract_sub_queries(response, query)

        return DecompositionResult(
            sub_queries=sub_queries,
            original_query=query,
            is_complex=len(sub_queries) > 1,
            reasoning=(
                f"LlamaIndex SubQuestionQueryEngine decomposed into "
                f"{len(sub_queries)} sub-question(s) across "
                f"{len(set(sq.metadata.get('tool_name', '') for sq in sub_queries))} tool(s)"
            ),
        )

    def _extract_sub_queries(
        self,
        response: Any,
        original_query: str,
    ) -> List[SubQuery]:
        """
        Extract sub-questions and answers from LlamaIndex response.

        LlamaIndex SubQuestionQueryEngine stores generated sub-questions in
        response.metadata["sub_question_responses"] as a list of dicts:
            [{"sub_q": {"sub_question": "...", "tool_name": "..."}, "answer": "..."}]

        If metadata key is missing (LlamaIndex version change), falls back to
        a single REASONING sub-query carrying the full synthesized answer.
        """
        metadata = getattr(response, "metadata", {}) or {}
        sub_question_responses = metadata.get("sub_question_responses", [])

        if not sub_question_responses:
            # Fallback: return the full synthesized answer as a single REASONING sub-query
            logger.debug(
                "QueryDecomposerV2: sub_question_responses not found in metadata, "
                "using full response as single sub-query"
            )
            return [
                SubQuery(
                    query=original_query,
                    type=SubQueryType.REASONING,
                    confidence=0.8,
                    metadata={
                        "llamaindex_answer": str(response),
                        "source": "llamaindex_synthesized",
                    },
                )
            ]

        sub_queries: List[SubQuery] = []
        for item in sub_question_responses:
            sub_q_info = item.get("sub_q", {})
            sub_question_text = sub_q_info.get("sub_question", original_query)
            tool_name = sub_q_info.get("tool_name", "")
            answer = item.get("answer", "")

            sub_type = self._tool_to_subquery_type(tool_name)

            sub_queries.append(
                SubQuery(
                    query=sub_question_text,
                    type=sub_type,
                    confidence=0.9,
                    dependencies=[],
                    metadata={
                        "tool_name": tool_name,
                        "llamaindex_answer": answer,  # SplitRouter short-circuit
                        "source": "llamaindex_sub_question_engine",
                    },
                )
            )

        return sub_queries if sub_queries else [
            SubQuery(
                query=original_query,
                type=SubQueryType.REASONING,
                confidence=0.8,
                metadata={
                    "llamaindex_answer": str(response),
                    "source": "llamaindex_fallback",
                },
            )
        ]

    @staticmethod
    def _tool_to_subquery_type(tool_name: str) -> SubQueryType:
        """Map LlamaIndex tool name to SubQueryType for SplitRouter compatibility."""
        mapping = {
            "notes": SubQueryType.RAG_ANSWERABLE,
            "codebase": SubQueryType.CODE_GEN,
            "documents": SubQueryType.FACTUAL,
            "patterns": SubQueryType.ANALYSIS,
            "knowledge_graph": SubQueryType.REASONING,
        }
        return mapping.get(tool_name, SubQueryType.REASONING)

    def __repr__(self) -> str:
        status = "ready" if self._sub_question_engine else ("unavailable" if not self._llama_available else "uninitialized")
        return f"<QueryDecomposerV2 llamaindex={status}>"
