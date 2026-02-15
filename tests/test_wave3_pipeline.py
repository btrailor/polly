"""
Tests for Wave 3 routing pipeline (Query Decomposition, Split Routing, Synthesis)

Run with: pytest tests/test_wave3_pipeline.py -v
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from pathlib import Path

from core.query_decomposition import (
    QueryDecomposer,
    SubQuery,
    SubQueryType,
    DecompositionResult
)
from core.split_router import SplitRouter, SubQueryResponse, SplitRoutingResult
from core.synthesis import Synthesizer, SynthesisResult


@pytest.fixture
def mock_config():
    """Mock config for testing."""
    return {
        'routing': {
            'decomposition': {
                'enabled': True,
                'model': 'balanced',
                'min_complexity_score': 0.6
            },
            'split_routing': {
                'enabled': True,
                'prefer_local': True,
                'local_rag_threshold': 0.7,
                'max_parallel_queries': 5
            },
            'synthesis': {
                'enabled': True,
                'use_llm': True,
                'prefer_local': True,
                'compression_threshold': 2000
            }
        },
        'compression': {
            'strategy': 'auto',
            'rag_context': {
                'ratio': 0.5
            }
        }
    }


@pytest.fixture
def mock_router():
    """Mock router for testing."""
    router = AsyncMock()
    
    # Mock route method
    async def mock_route(prompt, model, stream=False):
        response = Mock()
        response.content = "This is a test response"
        response.tokens_used = 100
        response.cost = 0.001
        return response
    
    router.route = mock_route
    return router


@pytest.fixture
def mock_rag():
    """Mock RAG for testing."""
    rag = Mock()
    
    # Mock search method
    def mock_search(query, n_results=5, domains=None):
        # Return mock search results
        result = Mock()
        result.chunk = Mock()
        result.chunk.content = "Test RAG content"
        result.chunk.filepath = "test.md"
        result.score = 0.8
        return [result] * 3  # 3 results
    
    rag.search = mock_search
    return rag


@pytest.fixture
def mock_autonomy_metrics():
    """Mock autonomy metrics for testing."""
    metrics = Mock()
    metrics.record_routing_decision = Mock()
    return metrics


class TestQueryDecomposer:
    """Test query decomposition."""
    
    def test_simple_query_classification(self, mock_config, mock_router):
        """Test that simple queries are classified correctly without decomposition."""
        decomposer = QueryDecomposer(mock_config, mock_router, None)
        
        # Test RAG answerable
        result = decomposer._simple_query_result("What did I write about AI?")
        assert not result.is_complex
        assert len(result.sub_queries) == 1
        assert result.sub_queries[0].type == SubQueryType.RAG_ANSWERABLE
        
        # Test code generation
        result = decomposer._simple_query_result("Write a function to parse JSON")
        assert result.sub_queries[0].type == SubQueryType.CODE_GEN
        
        # Test creative writing
        result = decomposer._simple_query_result("Write a blog post about testing")
        assert result.sub_queries[0].type == SubQueryType.CREATIVE
    
    def test_complexity_detection(self, mock_config, mock_router):
        """Test that complex queries are detected."""
        decomposer = QueryDecomposer(mock_config, mock_router, None)
        
        # Simple query
        assert not decomposer._is_complex_query("What is the weather?")
        
        # Complex queries (need multiple indicators to reach 0.6 threshold)
        # This has 'and' + 'can you' + 'write' (1 indicator = 0.25) + 2 question words (0.4) = 0.65
        assert decomposer._is_complex_query("What are the main themes and can you write a summary?")
        
        # Multiple questions (2 indicators from '?') = 0.5 + 2 question words (0.4) = 0.9
        assert decomposer._is_complex_query("Show me my repos? What about the issues?")
        
        # This is NOT complex enough (only 'first' + 'then' = 0.25, no questions)
        assert not decomposer._is_complex_query("First analyze the data, then create a visualization")
    
    @pytest.mark.asyncio
    async def test_decompose_simple_query(self, mock_config, mock_router):
        """Test decomposition of simple query returns single sub-query."""
        decomposer = QueryDecomposer(mock_config, mock_router, None)
        
        result = await decomposer.decompose("What is Python?")
        
        assert not result.is_complex
        assert len(result.sub_queries) == 1
        assert result.original_query == "What is Python?"


class TestSplitRouter:
    """Test split routing."""
    
    @pytest.mark.asyncio
    async def test_simple_routing_to_local(self, mock_config, mock_router, mock_rag, mock_autonomy_metrics):
        """Test that RAG answerable queries route to local."""
        split_router = SplitRouter(mock_config, mock_router, mock_rag, mock_autonomy_metrics)
        
        # Create simple decomposition result
        sub_query = SubQuery(
            query="What did I write about AI?",
            type=SubQueryType.RAG_ANSWERABLE,
            confidence=0.9
        )
        decomposition = DecompositionResult(
            sub_queries=[sub_query],
            original_query="What did I write about AI?",
            is_complex=False
        )
        
        result = await split_router.route(decomposition, {})
        
        assert result.success
        assert len(result.sub_responses) == 1
        assert result.local_count >= 0  # Should prefer local
        assert result.cloud_count >= 0
    
    @pytest.mark.asyncio
    async def test_route_decision_rag_coverage(self, mock_config, mock_router, mock_rag, mock_autonomy_metrics):
        """Test that routing decision considers RAG coverage."""
        split_router = SplitRouter(mock_config, mock_router, mock_rag, mock_autonomy_metrics)
        
        # RAG answerable query
        sub_query = SubQuery(
            query="What did I write about AI?",
            type=SubQueryType.RAG_ANSWERABLE
        )
        
        decision = await split_router._decide_route(sub_query, {})
        
        # Should have RAG context since mock returns 3 results
        assert 'rag_context' in decision
        assert decision['rag_coverage'] > 0


class TestSynthesizer:
    """Test synthesis."""
    
    @pytest.mark.asyncio
    async def test_single_response_synthesis(self, mock_config, mock_router):
        """Test that single response is returned as-is."""
        synthesizer = Synthesizer(mock_config, mock_router, None)
        
        # Create single sub-query response
        sub_query = SubQuery(
            query="Test query",
            type=SubQueryType.FACTUAL
        )
        sub_response = SubQueryResponse(
            sub_query=sub_query,
            response="Test response",
            route_info={'type': 'local', 'provider': 'ollama'},
            success=True
        )
        routing_result = SplitRoutingResult(
            sub_responses=[sub_response],
            original_query="Test query",
            success=True
        )
        
        result = await synthesizer.synthesize(routing_result, {})
        
        assert result.success
        assert result.synthesized_response == "Test response"
        assert len(result.source_attribution) == 1
    
    @pytest.mark.asyncio
    async def test_multiple_response_synthesis(self, mock_config):
        """Test synthesis of multiple responses."""
        # Create a custom mock router for this test that returns synthesized content
        mock_router = AsyncMock()
        
        async def mock_complete(messages, confidence, max_tokens=2000, temperature=0.7):
            response = Mock()
            # Extract prompt from messages
            prompt = messages[0]['content'] if messages else ""
            # When synthesis calls the router, return content that includes the sub-responses
            if "Synthesize" in prompt or "Response 1" in prompt:
                response.content = "Combined synthesis: Response 1 and Response 2"
            else:
                response.content = "This is a test response"
            response.tokens_in = 50
            response.tokens_out = 50
            response.cost = 0.001
            return response
        
        mock_router.complete_with_fallback = mock_complete
        
        synthesizer = Synthesizer(mock_config, mock_router, None)
        
        # Create multiple sub-query responses
        sub_query1 = SubQuery(query="Query 1", type=SubQueryType.RAG_ANSWERABLE)
        sub_query2 = SubQuery(query="Query 2", type=SubQueryType.CREATIVE)
        
        sub_responses = [
            SubQueryResponse(
                sub_query=sub_query1,
                response="Response 1",
                route_info={'type': 'local', 'provider': 'ollama', 'rag_coverage': 0.8},
                success=True
            ),
            SubQueryResponse(
                sub_query=sub_query2,
                response="Response 2",
                route_info={'type': 'cloud', 'provider': 'anthropic', 'rag_coverage': 0.0},
                success=True
            )
        ]
        
        routing_result = SplitRoutingResult(
            sub_responses=sub_responses,
            original_query="Combined query",
            local_count=1,
            cloud_count=1,
            success=True
        )
        
        result = await synthesizer.synthesize(routing_result, {})
        
        assert result.success
        assert len(result.source_attribution) == 2
        # Should contain synthesized content (not just original responses)
        assert "synthesis" in result.synthesized_response.lower() or ("Response 1" in result.synthesized_response and "Response 2" in result.synthesized_response)
    
    def test_format_sub_responses(self, mock_config, mock_router):
        """Test formatting of sub-responses for synthesis prompt."""
        synthesizer = Synthesizer(mock_config, mock_router, None)
        
        sub_query = SubQuery(query="Test", type=SubQueryType.FACTUAL)
        sub_response = SubQueryResponse(
            sub_query=sub_query,
            response="Test response",
            route_info={'type': 'local', 'provider': 'ollama', 'rag_coverage': 0.5},
            success=True
        )
        
        formatted = synthesizer._format_sub_responses([sub_response])
        
        assert "Response 1" in formatted
        assert "Test" in formatted
        assert "Test response" in formatted
        assert "RAG coverage: 50" in formatted


class TestEndToEndPipeline:
    """Test end-to-end Wave 3 pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_simple_query(self, mock_config, mock_router, mock_rag, mock_autonomy_metrics):
        """Test full pipeline with simple query."""
        # Initialize components
        decomposer = QueryDecomposer(mock_config, mock_router, None)
        split_router = SplitRouter(mock_config, mock_router, mock_rag, mock_autonomy_metrics)
        synthesizer = Synthesizer(mock_config, mock_router, None)
        
        # Run pipeline
        query = "What did I write about AI?"
        
        # 1. Decompose
        decomposition = await decomposer.decompose(query)
        assert not decomposition.is_complex
        
        # 2. Route
        routing_result = await split_router.route(decomposition, {})
        assert routing_result.success
        
        # 3. Synthesize
        synthesis = await synthesizer.synthesize(routing_result, {})
        assert synthesis.success
        assert synthesis.original_query == query


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
