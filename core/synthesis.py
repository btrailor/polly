"""
Synthesis Layer

Combines responses from multiple sub-queries into a single coherent answer.
Handles attribution, conflict resolution, and context compression.

Architecture:
    Sub-Responses → Synthesis → Unified Response (with source attribution)
    
Features:
    - Merge multiple responses coherently
    - Attribute sources (local RAG vs cloud)
    - Resolve conflicts between responses
    - Compress combined context if needed (LLMLingua)
    - Preserve citations and references

Integration points:
    - SplitRouter: Receives sub-query responses
    - LLMLingua: Optional compression of combined context
    - IntelligentRouterV2: Local model for synthesis when possible
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import logging

from core.split_router import SplitRoutingResult, SubQueryResponse

logger = logging.getLogger(__name__)


@dataclass
class SynthesisResult:
    """
    Result of synthesizing multiple sub-query responses.
    
    Attributes:
        synthesized_response: Combined response text
        original_query: Original user query
        source_attribution: List of sources used
        compression_applied: Whether compression was used
        tokens_saved: Tokens saved by compression
        success: Whether synthesis succeeded
    """
    synthesized_response: str
    original_query: str
    source_attribution: List[Dict[str, Any]]
    compression_applied: bool = False
    tokens_saved: int = 0
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return asdict(self)


class Synthesizer:
    """
    Synthesizes multiple sub-query responses into a coherent whole.
    
    Strategy:
    1. If single response, return as-is (no synthesis needed)
    2. If multiple responses without conflicts, concatenate with attribution
    3. If conflicts or complex, use LLM to synthesize
    4. Apply compression if combined context is large
    
    Example:
        >>> routing_result = await split_router.route(decomposition, context)
        >>> synthesis = await synthesizer.synthesize(routing_result)
        >>> # Returns unified response with source attribution
    """
    
    SYNTHESIS_PROMPT = """You are synthesizing multiple responses into a single coherent answer.

Original question: {original_query}

Sub-responses:
{sub_responses}

Instructions:
1. Combine the sub-responses into a single, coherent answer
2. Preserve important details from each response
3. Resolve any conflicts or contradictions logically
4. Maintain natural flow and readability
5. Include citations when referencing specific sources

Provide the synthesized response:"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        router=None,  # IntelligentRouterV2
        compression_manager=None  # Optional LLMLingua compression
    ):
        """
        Initialize Synthesizer.
        
        Args:
            config: Configuration dict
            router: IntelligentRouterV2 instance for synthesis LLM calls
            compression_manager: Optional CompressionManager for LLMLingua
        """
        self.config = config
        self.router = router
        self.compression_manager = compression_manager
        
        # Get synthesis config
        synthesis_config = config.get('routing', {}).get('synthesis', {})
        self.enabled = synthesis_config.get('enabled', True)
        self.use_llm = synthesis_config.get('use_llm', True)
        self.compression_threshold = synthesis_config.get('compression_threshold', 2000)
        self.prefer_local = synthesis_config.get('prefer_local', True)
        
        logger.info(f"Synthesizer initialized (enabled={self.enabled}, use_llm={self.use_llm})")
    
    async def synthesize(
        self,
        routing_result: SplitRoutingResult,
        context: Optional[Dict[str, Any]] = None
    ) -> SynthesisResult:
        """
        Synthesize sub-query responses into a unified response.
        
        Args:
            routing_result: SplitRoutingResult from SplitRouter
            context: Additional context
            
        Returns:
            SynthesisResult with synthesized response
        """
        if not self.enabled:
            # Synthesis disabled - just concatenate
            return self._simple_concatenate(routing_result)
        
        # Handle single response (no synthesis needed)
        if len(routing_result.sub_responses) == 1:
            return self._single_response(routing_result)
        
        # Handle multiple responses
        if self.use_llm and self.router:
            return await self._llm_synthesize(routing_result, context or {})
        else:
            return self._simple_concatenate(routing_result)
    
    def _single_response(
        self,
        routing_result: SplitRoutingResult
    ) -> SynthesisResult:
        """Handle single response - no synthesis needed."""
        response = routing_result.sub_responses[0]
        
        # Build source attribution
        source_attr = [{
            'type': response.route_info.get('type', 'unknown'),
            'provider': response.route_info.get('provider', 'unknown'),
            'query': response.sub_query.query,
            'rag_coverage': response.route_info.get('rag_coverage', 0.0)
        }]
        
        return SynthesisResult(
            synthesized_response=response.response,
            original_query=routing_result.original_query,
            source_attribution=source_attr,
            compression_applied=False,
            tokens_saved=0,
            success=response.success
        )
    
    def _simple_concatenate(
        self,
        routing_result: SplitRoutingResult
    ) -> SynthesisResult:
        """Simple concatenation with source attribution."""
        parts = []
        source_attr = []
        
        for i, response in enumerate(routing_result.sub_responses, 1):
            if not response.success:
                continue
            
            # Add response with attribution
            route_type = response.route_info.get('type', 'unknown')
            source_label = f"[{route_type}]"
            
            parts.append(f"{source_label} {response.response}")
            
            # Track source
            source_attr.append({
                'index': i,
                'type': route_type,
                'provider': response.route_info.get('provider', 'unknown'),
                'query': response.sub_query.query,
                'rag_coverage': response.route_info.get('rag_coverage', 0.0)
            })
        
        synthesized = "\n\n".join(parts)
        
        return SynthesisResult(
            synthesized_response=synthesized,
            original_query=routing_result.original_query,
            source_attribution=source_attr,
            compression_applied=False,
            tokens_saved=0,
            success=bool(parts)
        )
    
    async def _llm_synthesize(
        self,
        routing_result: SplitRoutingResult,
        context: Dict[str, Any]
    ) -> SynthesisResult:
        """
        Use LLM to synthesize responses intelligently.
        
        Args:
            routing_result: Routing result with sub-responses
            context: Additional context
            
        Returns:
            SynthesisResult with LLM-synthesized response
        """
        try:
            # Format sub-responses for LLM
            sub_response_text = self._format_sub_responses(routing_result.sub_responses)
            
            # Check if we should compress the context
            combined_length = len(sub_response_text)
            compression_applied = False
            tokens_saved = 0
            
            if combined_length > self.compression_threshold and self.compression_manager:
                # Apply LLMLingua compression
                try:
                    compressed = await self._compress_context(sub_response_text)
                    tokens_saved = self._estimate_tokens_saved(sub_response_text, compressed)
                    sub_response_text = compressed
                    compression_applied = True
                    logger.info(f"Applied compression, saved ~{tokens_saved} tokens")
                except Exception as e:
                    logger.warning(f"Compression failed, using original: {e}")
            
            # Build synthesis prompt
            prompt = self.SYNTHESIS_PROMPT.format(
                original_query=routing_result.original_query,
                sub_responses=sub_response_text
            )
            
            # Choose confidence level - prefer fast for synthesis
            from core.router_v2 import ConfidenceLevel
            confidence = ConfidenceLevel.FAST if self.prefer_local else ConfidenceLevel.BALANCED
            
            # Format as messages (OpenAI format)
            messages = [{"role": "user", "content": prompt}]
            
            # Call LLM with complete_with_fallback
            response = await self.router.complete_with_fallback(
                messages=messages,
                confidence=confidence,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extract response
            synthesized = response.content
            
            # Build source attribution
            source_attr = [
                {
                    'index': i + 1,
                    'type': resp.route_info.get('type', 'unknown'),
                    'provider': resp.route_info.get('provider', 'unknown'),
                    'query': resp.sub_query.query,
                    'rag_coverage': resp.route_info.get('rag_coverage', 0.0)
                }
                for i, resp in enumerate(routing_result.sub_responses)
                if resp.success
            ]
            
            return SynthesisResult(
                synthesized_response=synthesized,
                original_query=routing_result.original_query,
                source_attribution=source_attr,
                compression_applied=compression_applied,
                tokens_saved=tokens_saved,
                success=True
            )
            
        except Exception as e:
            logger.error(f"LLM synthesis failed: {e}")
            # Fallback to simple concatenation
            return self._simple_concatenate(routing_result)
    
    def _format_sub_responses(self, sub_responses: List[SubQueryResponse]) -> str:
        """Format sub-responses for LLM synthesis prompt."""
        parts = []
        
        for i, response in enumerate(sub_responses, 1):
            if not response.success:
                continue
            
            route_type = response.route_info.get('type', 'unknown')
            provider = response.route_info.get('provider', 'unknown')
            rag_coverage = response.route_info.get('rag_coverage', 0.0)
            
            # Build response header with metadata
            header = f"Response {i} [{route_type}/{provider}]"
            if rag_coverage > 0:
                header += f" (RAG coverage: {rag_coverage:.1%})"
            header += f"\nQuery: {response.sub_query.query}"
            
            parts.append(f"{header}\n\n{response.response}")
        
        return "\n\n---\n\n".join(parts)
    
    async def _compress_context(self, text: str) -> str:
        """
        Compress context using LLMLingua.
        
        Args:
            text: Text to compress
            
        Returns:
            Compressed text
        """
        if not self.compression_manager:
            return text
        
        try:
            # Get compression strategy
            strategy = self.config.get('compression', {}).get('strategy', 'auto')
            ratio = self.config.get('compression', {}).get('rag_context', {}).get('ratio', 0.5)
            
            # Compress with specified strategy (run in thread pool since it's blocking)
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.compression_manager.compress_text,
                text,
                strategy,
                ratio,
                'synthesis'
            )
            
            return result.get('compressed_text', text)
            
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return text
    
    def _estimate_tokens_saved(self, original: str, compressed: str) -> int:
        """
        Estimate tokens saved by compression.
        Simple heuristic: ~4 chars per token.
        """
        original_chars = len(original)
        compressed_chars = len(compressed)
        chars_saved = max(0, original_chars - compressed_chars)
        return chars_saved // 4
    
    def add_citations(
        self,
        response: str,
        source_attribution: List[Dict[str, Any]]
    ) -> str:
        """
        Add source citations to synthesized response.
        
        Args:
            response: Synthesized response text
            source_attribution: List of sources
            
        Returns:
            Response with citations appended
        """
        if not source_attribution:
            return response
        
        # Build citation section
        citations = ["\n\n---\n\nSources:"]
        
        for source in source_attribution:
            route_type = source.get('type', 'unknown')
            provider = source.get('provider', 'unknown')
            query = source.get('query', '')
            rag_coverage = source.get('rag_coverage', 0.0)
            
            citation = f"- [{route_type}/{provider}]"
            if rag_coverage > 0:
                citation += f" (RAG: {rag_coverage:.1%})"
            if query:
                citation += f": {query}"
            
            citations.append(citation)
        
        return response + "\n".join(citations)
