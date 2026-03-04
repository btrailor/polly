"""
Split Router

Routes decomposed sub-queries in parallel to local (RAG + Ollama) and cloud providers.
This is where Polly's intelligent routing strategy executes.

Architecture:
    DecompositionResult → Split Router → [Local RAG, Cloud Models] → Sub-Responses

Routing Strategy (tier-aware):
    The main query pipeline classifies retrieval quality into three tiers
    (DIRECT / ADJACENT / ABSENT) via RetrievalClassifier.  The split router
    receives this tier through context and uses it to make per-sub-query
    local vs cloud decisions:

    DIRECT tier (strong RAG grounding):
      - RAG_ANSWERABLE / FACTUAL → Local Ollama (if coverage ≥ threshold)
      - REASONING / ANALYSIS / CODE_GEN / CREATIVE → Cloud

    ADJACENT tier (tangential RAG matches):
      - All sub-queries → Cloud (RAG passed as background context only)

    ABSENT tier (no relevant KB content):
      - All sub-queries → Cloud (no RAG search performed)

    This ensures the same retrieval-tier intelligence that drives the
    standard routing path (polly.py _should_use_local_model) is respected
    when queries are decomposed through Wave 3.

Integration points:
    - QueryDecomposer: Receives decomposition results
    - RetrievalClassifier: Three-tier classification informs routing
    - IntelligentRouterV2: Routes cloud sub-queries
    - RAG: Local knowledge retrieval (DIRECT tier only)
    - AutonomyMetrics: Track local vs cloud routing
    - Synthesis: Combines results
"""

import asyncio
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib
import logging

from core.query_decomposition import DecompositionResult, SubQuery, SubQueryType
from core.hardened.classifier import RetrievalTier

logger = logging.getLogger(__name__)


@dataclass
class SubQueryResponse:
    """
    Response to a sub-query.
    
    Attributes:
        sub_query: Original sub-query
        response: LLM response content
        route_info: Information about how this was routed
        success: Whether the query succeeded
        error: Error message if failed
    """
    sub_query: SubQuery
    response: str
    route_info: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = asdict(self)
        result['sub_query'] = self.sub_query.to_dict()
        return result


@dataclass
class SplitRoutingResult:
    """
    Result of split routing across multiple sub-queries.
    
    Attributes:
        sub_responses: List of responses for each sub-query
        original_query: Original user query
        total_tokens: Total tokens used across all sub-queries
        total_cost: Total cost across all sub-queries
        local_count: Number of sub-queries routed locally
        cloud_count: Number of sub-queries routed to cloud
        success: Whether all sub-queries succeeded
    """
    sub_responses: List[SubQueryResponse]
    original_query: str
    total_tokens: int = 0
    total_cost: float = 0.0
    local_count: int = 0
    cloud_count: int = 0
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = asdict(self)
        result['sub_responses'] = [sr.to_dict() for sr in self.sub_responses]
        return result


class SplitRouter:
    """
    Routes decomposed sub-queries in parallel to appropriate providers.
    
    Routing logic:
    1. Analyze each sub-query type
    2. For RAG_ANSWERABLE: Check local RAG coverage
    3. Route to local or cloud based on type + RAG availability
    4. Execute in parallel (respecting dependencies)
    5. Track metrics
    
    Example:
        >>> decomp_result = await decomposer.decompose("What are AI themes in my notes? Write a blog post.")
        >>> routing_result = await split_router.route(decomp_result, context)
        >>> # Returns 2 responses: 1 local RAG, 1 cloud creative
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        router,  # IntelligentRouterV2
        rag,  # RAG instance
        local_llm=None,  # Local LLM instance (for Ollama)
        autonomy_metrics=None  # AutonomyMetrics instance
    ):
        """
        Initialize Split Router.
        
        Args:
            config: Configuration dict
            router: IntelligentRouterV2 instance
            rag: RAG instance for local retrieval
            local_llm: Local LLM instance (for Ollama routing)
            autonomy_metrics: AutonomyMetrics instance for tracking
        """
        self.config = config
        self.router = router
        self.rag = rag
        self.local_llm = local_llm
        self.autonomy_metrics = autonomy_metrics
        
        # Get config
        routing_config = config.get('routing', {})
        self.prefer_local = routing_config.get('prefer_local', True)
        self.local_threshold = routing_config.get('local_rag_threshold', 0.7)
        self.max_parallel = routing_config.get('max_parallel_queries', 5)

        # Session-scoped RAG result cache: avoids re-running the same embedding+vector
        # search for identical sub-queries within a session (common in multi-turn).
        # Keyed by query string; evicts oldest when full (insertion-order dict).
        self._rag_cache: dict = {}
        self._rag_cache_max: int = routing_config.get('rag_cache_size', 128)

        logger.info(f"SplitRouter initialized (prefer_local={self.prefer_local})")

    @staticmethod
    def _cloud_model_for_type(sq_type: SubQueryType) -> str:
        """Choose cloud model tier based on sub-query type."""
        if sq_type in (SubQueryType.REASONING, SubQueryType.ANALYSIS):
            return 'auto:thorough'
        elif sq_type == SubQueryType.CODE_GEN:
            return 'auto:balanced'
        else:
            return 'auto:balanced'

    async def route(
        self,
        decomposition: DecompositionResult,
        context: Optional[Dict[str, Any]] = None
    ) -> SplitRoutingResult:
        """
        Route decomposed sub-queries to appropriate providers.
        
        Args:
            decomposition: DecompositionResult from QueryDecomposer
            context: Additional context (persona, conversation history, etc.)
            
        Returns:
            SplitRoutingResult with responses for each sub-query
        """
        context = context or {}
        
        # Handle simple (non-decomposed) queries
        if not decomposition.is_complex:
            return await self._route_simple(decomposition, context)
        
        # Route complex queries with dependencies
        return await self._route_complex(decomposition, context)
    
    async def _route_simple(
        self,
        decomposition: DecompositionResult,
        context: Dict[str, Any]
    ) -> SplitRoutingResult:
        """Route a simple (single sub-query) through standard routing."""
        sub_query = decomposition.sub_queries[0]
        
        # Determine routing strategy
        route_decision = await self._decide_route(sub_query, context)
        
        # Execute query
        response = await self._execute_sub_query(sub_query, route_decision, context)
        
        # Track metrics
        if self.autonomy_metrics:
            self._record_routing_metrics(
                route_type=route_decision['type'],
                provider=route_decision.get('provider'),
                tokens=response.route_info.get('tokens_used', 0),
                cost=response.route_info.get('cost', 0.0),
                local_pct=1.0 if route_decision['type'] == 'local' else 0.0,
                query=decomposition.original_query,
                rag_coverage=route_decision.get('rag_coverage', 0.0),
            )

        return SplitRoutingResult(
            sub_responses=[response],
            original_query=decomposition.original_query,
            total_tokens=response.route_info.get('tokens_used', 0),
            total_cost=response.route_info.get('cost', 0.0),
            local_count=1 if route_decision['type'] == 'local' else 0,
            cloud_count=1 if route_decision['type'] == 'cloud' else 0,
            success=response.success
        )
    
    async def _route_complex(
        self,
        decomposition: DecompositionResult,
        context: Dict[str, Any]
    ) -> SplitRoutingResult:
        """Route complex queries with multiple sub-queries and dependencies."""
        sub_queries = decomposition.sub_queries
        responses: List[SubQueryResponse] = []
        
        # Build dependency graph
        dep_graph = self._build_dependency_graph(sub_queries)
        
        # Execute in dependency order
        executed = set()
        while len(executed) < len(sub_queries):
            # Find sub-queries ready to execute (dependencies satisfied)
            ready = [
                i for i in range(len(sub_queries))
                if i not in executed and all(dep in executed for dep in dep_graph[i])
            ]
            
            if not ready:
                # Circular dependency or error - execute remaining serially
                logger.warning("Circular dependency detected, executing remaining serially")
                ready = [i for i in range(len(sub_queries)) if i not in executed]
            
            # Execute ready sub-queries in parallel (up to max_parallel)
            batch_responses = await self._execute_batch(
                [sub_queries[i] for i in ready[:self.max_parallel]],
                context,
                [responses[dep] for dep in range(len(responses))]  # Previous responses
            )
            
            responses.extend(batch_responses)
            executed.update(ready[:self.max_parallel])
        
        # Calculate totals
        total_tokens = sum(r.route_info.get('tokens_used', 0) for r in responses)
        total_cost = sum(r.route_info.get('cost', 0.0) for r in responses)
        local_count = sum(1 for r in responses if r.route_info.get('type') == 'local')
        cloud_count = len(responses) - local_count
        
        # Track metrics
        if self.autonomy_metrics:
            local_pct = local_count / len(responses) if responses else 0.0
            avg_rag_coverage = (
                sum(r.route_info.get('rag_coverage', 0.0) for r in responses) / len(responses)
                if responses else 0.0
            )
            self._record_routing_metrics(
                route_type='split',
                provider='mixed',
                tokens=total_tokens,
                cost=total_cost,
                local_pct=local_pct,
                query=decomposition.original_query,
                rag_coverage=avg_rag_coverage,
            )
        
        return SplitRoutingResult(
            sub_responses=responses,
            original_query=decomposition.original_query,
            total_tokens=total_tokens,
            total_cost=total_cost,
            local_count=local_count,
            cloud_count=cloud_count,
            success=all(r.success for r in responses)
        )
    
    def _build_dependency_graph(self, sub_queries: List[SubQuery]) -> Dict[int, List[int]]:
        """Build dependency graph from sub-queries."""
        return {i: sq.dependencies for i, sq in enumerate(sub_queries)}
    
    async def _execute_batch(
        self,
        sub_queries: List[SubQuery],
        context: Dict[str, Any],
        previous_responses: List[SubQueryResponse]
    ) -> List[SubQueryResponse]:
        """Execute a batch of sub-queries in parallel.

        Route decisions (which include RAG searches) are resolved concurrently
        first, then execution tasks are gathered in parallel as well.
        """
        # Step 1: Resolve all routing decisions concurrently (RAG searches run in parallel)
        route_decisions = await asyncio.gather(
            *[self._decide_route(sq, context) for sq in sub_queries]
        )

        # Step 2: Build and gather execution tasks in parallel
        tasks = []
        for sub_query, route_decision in zip(sub_queries, route_decisions):
            sub_context = context.copy()
            if sub_query.dependencies:
                sub_context['previous_responses'] = [
                    previous_responses[dep] for dep in sub_query.dependencies
                    if dep < len(previous_responses)
                ]
            tasks.append(self._execute_sub_query(sub_query, route_decision, sub_context))

        return await asyncio.gather(*tasks)
    
    async def _decide_route(
        self,
        sub_query: SubQuery,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Decide how to route a sub-query.

        This respects the three-tier retrieval classification from the main
        query pipeline.  The retrieval tier (DIRECT / ADJACENT / ABSENT) tells
        us how strongly the knowledge base can ground an answer:

        - DIRECT  → strong RAG grounding — local is ideal for RAG-answerable subs.
        - ADJACENT → tangential matches — prefer cloud; RAG provides background only.
        - ABSENT   → no relevant KB content — cloud for all sub-queries.

        When retrieval_tier is not passed in context, falls back to the
        coverage-based heuristic (legacy behaviour).

        Returns:
            Dict with 'type' (local/cloud), 'provider', 'model', 'rag_context'
        """
        # Extract retrieval tier from context (set by polly.py query pipeline)
        retrieval_tier: Optional[RetrievalTier] = context.get('retrieval_tier')

        # ----- Sub-query types that ALWAYS go to cloud regardless of tier -----
        CLOUD_ONLY_TYPES = {
            SubQueryType.CODE_GEN,
            SubQueryType.CREATIVE,
            SubQueryType.REASONING,
            SubQueryType.ANALYSIS,
        }
        if sub_query.type in CLOUD_ONLY_TYPES:
            model = self._cloud_model_for_type(sub_query.type)
            logger.info(
                f"[Wave3 Route] sub='{sub_query.query[:50]}' → CLOUD "
                f"(type={sub_query.type.value} always routes to cloud)"
            )
            print(
                f"[Wave3 Route] CLOUD: type={sub_query.type.value} "
                f"(always cloud), model={model}",
                flush=True,
            )
            return {
                'type': 'cloud',
                'provider': 'cloud',
                'model': model,
                'rag_context': None,
                'rag_coverage': 0.0,
            }

        # ----- Tier-based early decisions (before RAG search) -----
        # ABSENT: no KB content at all — send to cloud, skip RAG search cost
        if retrieval_tier == RetrievalTier.ABSENT:
            model = self._cloud_model_for_type(sub_query.type)
            logger.info(
                f"[Wave3 Route] sub='{sub_query.query[:50]}' → CLOUD "
                f"(retrieval_tier=ABSENT, no KB grounding)"
            )
            print(
                f"[Wave3 Route] CLOUD: tier=ABSENT, no KB content, "
                f"type={sub_query.type.value}",
                flush=True,
            )
            return {
                'type': 'cloud',
                'provider': 'cloud',
                'model': model,
                'rag_context': None,
                'rag_coverage': 0.0,
            }

        # ----- RAG search (only for local-candidate types) -----
        LOCAL_CANDIDATE_TYPES = {SubQueryType.RAG_ANSWERABLE, SubQueryType.FACTUAL}
        should_search_rag = sub_query.type in LOCAL_CANDIDATE_TYPES

        rag_coverage = 0.0
        rag_context = None

        if should_search_rag:
            # Search RAG, using session cache to avoid redundant embedding+vector queries
            cache_key = sub_query.query
            if cache_key in self._rag_cache:
                rag_results = self._rag_cache[cache_key]
                logger.debug(f"RAG cache hit: '{cache_key[:50]}'")
            else:
                try:
                    rag_results = await asyncio.to_thread(
                        self.rag.search,
                        sub_query.query,
                        n_results=5
                    )
                    # Evict oldest entry when at capacity (insertion-order dict)
                    if len(self._rag_cache) >= self._rag_cache_max:
                        self._rag_cache.pop(next(iter(self._rag_cache)))
                    self._rag_cache[cache_key] = rag_results
                except Exception as e:
                    logger.warning(f"RAG search failed: {e}")
                    rag_results = []

            if rag_results:
                rag_coverage = min(len(rag_results) / 5.0, 1.0)
                rag_context = self._format_rag_context(rag_results)

        # ----- Tier-informed routing decision -----

        if retrieval_tier == RetrievalTier.ADJACENT:
            # ADJACENT: RAG found tangential content.  The main pipeline already
            # determined these results are *related but not directly on-topic*.
            # Cloud models handle this better — they can use the tangential context
            # as background while drawing on broader training knowledge.
            model = self._cloud_model_for_type(sub_query.type)
            logger.info(
                f"[Wave3 Route] sub='{sub_query.query[:50]}' → CLOUD "
                f"(retrieval_tier=ADJACENT, tangential RAG — cloud handles better)"
            )
            print(
                f"[Wave3 Route] CLOUD: tier=ADJACENT, "
                f"type={sub_query.type.value}, rag_coverage={rag_coverage:.2f}",
                flush=True,
            )
            return {
                'type': 'cloud',
                'provider': 'cloud',
                'model': model,
                'rag_context': rag_context if rag_coverage > 0.3 else None,
                'rag_coverage': rag_coverage,
            }

        # ----- DIRECT tier (or no tier provided — legacy fallback) -----
        # For DIRECT tier: strong RAG grounding exists.  Route locally if coverage
        # meets the threshold; otherwise fall through to cloud.

        if sub_query.type in LOCAL_CANDIDATE_TYPES and rag_coverage >= self.local_threshold:
            logger.info(
                f"[Wave3 Route] sub='{sub_query.query[:50]}' → LOCAL "
                f"(tier={retrieval_tier.value if retrieval_tier else 'none'}, "
                f"type={sub_query.type.value}, rag_coverage={rag_coverage:.2f})"
            )
            print(
                f"[Wave3 Route] LOCAL: tier={retrieval_tier.value if retrieval_tier else 'none'}, "
                f"type={sub_query.type.value}, rag_coverage={rag_coverage:.2f}",
                flush=True,
            )
            return {
                'type': 'local',
                'provider': 'ollama',
                'model': 'auto:fast',
                'rag_context': rag_context,
                'rag_coverage': rag_coverage,
            }

        # Default: insufficient local coverage — route to cloud
        model = self._cloud_model_for_type(sub_query.type)
        logger.info(
            f"[Wave3 Route] sub='{sub_query.query[:50]}' → CLOUD "
            f"(tier={retrieval_tier.value if retrieval_tier else 'none'}, "
            f"low rag_coverage={rag_coverage:.2f})"
        )
        print(
            f"[Wave3 Route] CLOUD: tier={retrieval_tier.value if retrieval_tier else 'none'}, "
            f"type={sub_query.type.value}, rag_coverage={rag_coverage:.2f} < threshold={self.local_threshold}",
            flush=True,
        )
        return {
            'type': 'cloud',
            'provider': 'cloud',
            'model': model,
            'rag_context': rag_context if rag_coverage > 0.3 else None,
            'rag_coverage': rag_coverage,
        }
    
    def _format_rag_context(self, rag_results: List) -> str:
        """Format RAG results into context string."""
        if not rag_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(rag_results[:5], 1):
            # Handle different result formats (SearchResult or dict)
            if hasattr(result, 'chunk'):
                content = result.chunk.content
                filepath = result.chunk.filepath
            else:
                content = result.get('content', '')
                filepath = result.get('filepath', 'unknown')
            
            context_parts.append(f"[{i}] {filepath}\n{content}")
        
        return "\n\n".join(context_parts)
    
    async def _execute_sub_query(
        self,
        sub_query: SubQuery,
        route_decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> SubQueryResponse:
        """
        Execute a single sub-query with the routing decision.
        
        Args:
            sub_query: SubQuery to execute
            route_decision: Routing decision dict
            context: Execution context
            
        Returns:
            SubQueryResponse with result
        """
        try:
            # Wave 5 short-circuit: if LlamaIndex has pre-answered this sub-query,
            # skip the LLM call and return the cached answer directly.
            llamaindex_answer = (sub_query.metadata or {}).get("llamaindex_answer")
            if llamaindex_answer and str(
                (sub_query.metadata or {}).get("source", "")
            ).startswith("llamaindex"):
                logger.debug(
                    f"SplitRouter: using LlamaIndex pre-answered response for "
                    f"'{sub_query.query[:60]}'"
                )
                return SubQueryResponse(
                    sub_query=sub_query,
                    response=str(llamaindex_answer),
                    route_info={
                        "type": "llamaindex",
                        "provider": "llamaindex_sub_question_engine",
                        "model": (sub_query.metadata or {}).get("tool_name", "unknown"),
                        "tokens_used": 0,
                        "cost": 0.0,
                    },
                    success=True,
                )

            # Build prompt with RAG context if available
            prompt = sub_query.query
            if route_decision.get('rag_context'):
                prompt = f"""Context from knowledge base:
{route_decision['rag_context']}

Based on the above context, answer this question:
{sub_query.query}"""
            
            # Add previous responses if available
            if context.get('previous_responses'):
                prev_context = "\n\n".join([
                    f"Previous answer: {resp.response}"
                    for resp in context['previous_responses']
                ])
                prompt = f"{prev_context}\n\n{prompt}"
            
            # Get system prompt from context (persona, augmented context, etc.)
            system_prompt = context.get('system_prompt', '')
            
            # Check routing decision type
            route_type = route_decision.get('type', 'cloud')
            
            if route_type == 'local' and self.local_llm:
                # Use local Ollama for this sub-query
                logger.info(f"Routing sub-query to LOCAL (Ollama): {sub_query.query[:50]}...")
                
                # Build messages for local LLM
                messages = [{"role": "user", "content": prompt}]
                
                # Stream from local LLM and collect response
                response_text = ""
                async for chunk in self.local_llm.chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    stream=True
                ):
                    response_text += chunk
                
                # Estimate tokens (rough approximation)
                tokens_in = len(system_prompt.split()) + len(prompt.split())
                tokens_out = len(response_text.split())
                tokens_used = tokens_in + tokens_out
                cost = 0.0  # Local is free
                
                return SubQueryResponse(
                    sub_query=sub_query,
                    response=response_text,
                    route_info={
                        'type': 'local',
                        'provider': 'ollama',
                        'model': getattr(self.local_llm, 'model', 'qwen2.5-coder:7b'),
                        'rag_coverage': route_decision.get('rag_coverage', 0.0),
                        'tokens_used': tokens_used,
                        'cost': cost
                    },
                    success=True,
                    error=None
                )
            
            else:
                # Route through IntelligentRouterV2 (cloud providers)
                logger.info(f"Routing sub-query to CLOUD: {sub_query.query[:50]}...")
                
                # Map route_decision['model'] to confidence level
                from core.router_v2 import ConfidenceLevel
                model_str = route_decision.get('model', 'auto:balanced')
                if 'fast' in model_str.lower():
                    confidence = ConfidenceLevel.FAST
                elif 'thorough' in model_str.lower():
                    confidence = ConfidenceLevel.THOROUGH
                else:
                    confidence = ConfidenceLevel.BALANCED
                
                # Format as messages (OpenAI format) - include system prompt
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await self.router.complete_with_fallback(
                    messages=messages,
                    confidence=confidence,
                    max_tokens=2000,
                    temperature=0.7
                )
                
                # Extract response content and metadata
                response_text = response.content
                tokens_used = response.tokens_in + response.tokens_out
                cost = response.cost
                
                return SubQueryResponse(
                    sub_query=sub_query,
                    response=response_text,
                    route_info={
                        'type': route_decision['type'],
                        'provider': response.provider,
                        'model': response.model,
                        'rag_coverage': route_decision.get('rag_coverage', 0.0),
                        'tokens_used': tokens_used,
                        'cost': cost
                    },
                    success=True,
                    error=None
                )
            
        except Exception as e:
            logger.error(f"Sub-query execution failed: {e}")
            return SubQueryResponse(
                sub_query=sub_query,
                response="",
                route_info=route_decision,
                success=False,
                error=str(e)
            )
    
    def _record_routing_metrics(
        self,
        route_type: str,
        provider: Optional[str],
        tokens: int,
        cost: float,
        local_pct: float,
        query: str,
        rag_coverage: float = 0.0,
    ):
        """Record routing metrics to AutonomyMetrics."""
        try:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:16]

            self.autonomy_metrics.record_routing_decision(
                route_type=route_type,
                provider=provider,
                rag_coverage=rag_coverage,
                tokens_used=tokens,
                cost=cost,
                local_pct=local_pct,
                query_hash=query_hash
            )
        except Exception as e:
            logger.warning(f"Failed to record routing metrics: {e}")
