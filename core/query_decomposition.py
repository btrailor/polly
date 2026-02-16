"""
Query Decomposition Engine

Analyzes complex user queries and breaks them into sub-queries with routing hints.
This is Polly's core differentiator for intelligent routing.

Architecture:
    User Query → Decomposition → Sub-queries (with routing hints) → Split Router
    
Each sub-query is tagged with:
    - rag_answerable: Can be answered from local knowledge base
    - reasoning_required: Requires complex reasoning
    - code_generation: Involves code generation
    - factual_lookup: Simple fact retrieval
    - creative_writing: Creative content generation

Integration points:
    - PatternLearner: Check for known query patterns
    - IntelligentRouterV2: Each sub-query routed independently
    - SplitRouter: Parallel execution of sub-queries
    - Synthesis: Combine results into coherent response
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class SubQueryType(Enum):
    """Classification of sub-query types for routing hints."""
    RAG_ANSWERABLE = "rag_answerable"  # Can be answered from local KB
    REASONING = "reasoning_required"  # Requires complex reasoning
    CODE_GEN = "code_generation"  # Code generation task
    FACTUAL = "factual_lookup"  # Simple fact retrieval
    CREATIVE = "creative_writing"  # Creative content
    ANALYSIS = "analysis"  # Data analysis, interpretation


@dataclass
class SubQuery:
    """
    A decomposed sub-query with routing hints.
    
    Attributes:
        query: The sub-query text
        type: Classification of the sub-query
        confidence: Confidence in the decomposition (0.0-1.0)
        dependencies: Indices of sub-queries this depends on
        metadata: Additional context for routing
    """
    query: str
    type: SubQueryType
    confidence: float = 0.8
    dependencies: List[int] = None  # Indices of dependent sub-queries
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = asdict(self)
        result['type'] = self.type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubQuery':
        """Create SubQuery from dict."""
        data_copy = data.copy()
        if 'type' in data_copy:
            data_copy['type'] = SubQueryType(data_copy['type'])
        return cls(**data_copy)


@dataclass
class DecompositionResult:
    """
    Result of query decomposition.
    
    Attributes:
        sub_queries: List of decomposed sub-queries
        original_query: Original user query
        is_complex: Whether decomposition was needed
        reasoning: Explanation of decomposition strategy
    """
    sub_queries: List[SubQuery]
    original_query: str
    is_complex: bool
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            'sub_queries': [sq.to_dict() for sq in self.sub_queries],
            'original_query': self.original_query,
            'is_complex': self.is_complex,
            'reasoning': self.reasoning
        }


class QueryDecomposer:
    """
    Decomposes complex queries into sub-queries with routing hints.
    
    Simple first version: Uses LLM to identify sub-queries.
    Future: Upgrade to LlamaIndex SubQuestionQueryEngine when KG is available.
    
    Example:
        >>> decomposer = QueryDecomposer(config, router)
        >>> result = await decomposer.decompose(
        ...     query="What are the main themes in my notes about AI, and can you write a blog post about them?",
        ...     context={"persona": "Scribe"}
        ... )
        >>> # Returns 2 sub-queries:
        >>> # 1. RAG_ANSWERABLE: "What are the main themes in notes about AI?"
        >>> # 2. CREATIVE: "Write a blog post about [themes from query 1]"
    """
    
    DECOMPOSITION_PROMPT = """You are a query decomposition specialist. Analyze the user's query and break it into independent sub-queries if needed.

For each sub-query, classify it as one of:
- rag_answerable: Can be answered from a local knowledge base
- reasoning_required: Requires complex reasoning or analysis
- code_generation: Involves generating code
- factual_lookup: Simple fact retrieval
- creative_writing: Creative content generation
- analysis: Data analysis or interpretation

Rules:
1. Simple queries don't need decomposition - return the original query
2. Complex queries should be broken into logical steps
3. Identify dependencies between sub-queries
4. Be concise - don't over-decompose

User Query: {query}

Context: {context}

Respond with ONLY a JSON object (no markdown code blocks):
{{
    "is_complex": true/false,
    "reasoning": "why this decomposition makes sense",
    "sub_queries": [
        {{
            "query": "the sub-query text",
            "type": "rag_answerable|reasoning_required|code_generation|factual_lookup|creative_writing|analysis",
            "confidence": 0.0-1.0,
            "dependencies": [0, 1],  // indices of sub-queries this depends on
            "metadata": {{"key": "value"}}  // any additional context
        }}
    ]
}}"""
    
    def __init__(self, config: Dict[str, Any], router=None, pattern_learner=None):
        """
        Initialize Query Decomposer.
        
        Args:
            config: Configuration dict with routing.decomposition settings
            router: IntelligentRouterV2 instance for LLM calls
            pattern_learner: PatternLearner instance for pattern matching
        """
        self.config = config
        self.router = router
        self.pattern_learner = pattern_learner
        
        # Get decomposition config
        decomp_config = config.get('routing', {}).get('decomposition', {})
        self.enabled = decomp_config.get('enabled', True)
        self.model = decomp_config.get('model', 'fast')  # fast/balanced/thorough
        self.min_complexity_score = decomp_config.get('min_complexity_score', 0.6)
        
        logger.info(f"QueryDecomposer initialized (enabled={self.enabled}, model={self.model})")
    
    async def decompose(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DecompositionResult:
        """
        Decompose a query into sub-queries with routing hints.
        
        Args:
            query: User query to decompose
            context: Additional context (persona, conversation history, etc.)
            
        Returns:
            DecompositionResult with sub-queries or original query if simple
        """
        if not self.enabled:
            # Decomposition disabled - return original query as single sub-query
            return self._simple_query_result(query)
        
        # Check for known patterns first (if pattern learner available)
        if self.pattern_learner:
            pattern_result = await self._check_patterns(query, context)
            if pattern_result:
                return pattern_result
        
        # Quick complexity check
        if not self._is_complex_query(query):
            return self._simple_query_result(query)
        
        # Use LLM to decompose
        try:
            return await self._llm_decompose(query, context or {})
        except Exception as e:
            logger.warning(f"Decomposition failed, falling back to simple query: {e}")
            return self._simple_query_result(query)
    
    def _is_complex_query(self, query: str) -> bool:
        """
        Quick heuristic check if query is complex enough to warrant decomposition.
        
        Complex queries typically have:
        - Multiple sentences or clauses (and, then, also)
        - Multiple question words (what, how, why)
        - Both retrieval and generation aspects
        - Semantically complex topics (requires structural/historical analysis)
        """
        query_lower = query.lower()
        
        # Simple heuristics
        complexity_indicators = [
            ' and ' in query_lower and any(word in query_lower for word in ['then', 'can you', 'write', 'create', 'also']),
            ' then ' in query_lower,
            ' also ' in query_lower,
            query.count('?') > 1,
            'after that' in query_lower,
            'first' in query_lower and ('second' in query_lower or 'then' in query_lower),
            'can you' in query_lower and ' and ' in query_lower,
        ]
        
        # Count question words (including duplicates for multi-part questions)
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        question_count = sum(query_lower.count(qw) for qw in question_words)
        
        # Check for multiple distinct questions (e.g., "what X and what Y")
        has_multiple_questions = (
            (' and what' in query_lower or ' and how' in query_lower or ' and why' in query_lower) or
            question_count >= 2
        )
        
        # Semantic complexity: topics that require structural/historical analysis
        # regardless of syntactic simplicity. A simple declarative sentence about
        # a complex topic still needs analytical depth.
        semantic_score = self._semantic_complexity_score(query_lower)
        
        complexity_score = (
            sum(complexity_indicators) * 0.25 +
            min(question_count * 0.15, 0.4) +
            (0.3 if has_multiple_questions else 0.0) +  # Bonus for multiple questions
            semantic_score  # Semantic/topic complexity boost
        )
        
        is_complex = complexity_score >= self.min_complexity_score
        print(f"[Complexity] Query: '{query[:60]}...' score={complexity_score:.2f} (semantic={semantic_score:.2f}), threshold={self.min_complexity_score}, complex={is_complex}, qcount={question_count}, multi_q={has_multiple_questions}", flush=True)
        logger.debug(f"Complexity check: score={complexity_score:.2f}, semantic={semantic_score:.2f}, threshold={self.min_complexity_score}, complex={is_complex}, question_count={question_count}, has_multiple_questions={has_multiple_questions}")
        
        return is_complex
    
    def _semantic_complexity_score(self, query_lower: str) -> float:
        """
        Score semantic/topic complexity independent of syntactic structure.
        
        A query like "Tell me about the Somali problem in Minneapolis" is
        syntactically simple but semantically complex — it touches on
        immigration, demographics, political framing, and structural causes.
        
        This doesn't block or filter anything. It just tells the decomposer
        "this topic needs analytical depth, not a simple factual lookup."
        
        Returns a score between 0.0 and 0.65.
        """
        score = 0.0
        
        # --- Scapegoat narrative patterns ---
        # Structural pattern: "things are bad because of [outgroup]"
        # Reuses patterns from core/hardened/validator.py:407-436
        scapegoat_indicators = [
            "because of immigrants",
            "because of foreigners",
            "they're taking our",
            "they're ruining",
            "they're destroying",
            "invasion of",
            "replace us",
            "great replacement",
        ]
        if any(indicator in query_lower for indicator in scapegoat_indicators):
            score += 0.5
        
        # --- Essentialist claim patterns ---
        # Attributes problems to inherent group qualities
        # Reuses patterns from core/hardened/validator.py:438-465
        essentialist_indicators = [
            "inherently violent",
            "naturally inferior",
            "biologically determined",
            "genetically predisposed to crime",
            "racial iq",
            "born criminals",
        ]
        if any(indicator in query_lower for indicator in essentialist_indicators):
            score += 0.5
        
        # --- "Problem" + group/place framing ---
        # "the [group] problem" or "[group] problem in [place]" is a historically
        # loaded framing that benefits from structural analysis. This catches
        # patterns like "the Somali problem" or "the immigrant problem".
        problem_framing_groups = [
            "immigrant", "refugee", "migrant", "muslim", "somali", "mexican",
            "hispanic", "latino", "arab", "jewish", "black", "african",
            "chinese", "asian", "roma", "gypsy", "indigenous", "native",
            "homeless", "welfare",
        ]
        if "problem" in query_lower or "issue" in query_lower or "crisis" in query_lower:
            if any(group in query_lower for group in problem_framing_groups):
                score += 0.45
        
        # --- Cui bono signals ---
        # Questions about who benefits, power dynamics, systemic causes
        # These are analytically complex even when simply stated
        cui_bono_patterns = [
            "who benefits",
            "who profits",
            "follow the money",
            "real reason",
            "actually behind",
            "power structure",
            "systemic",
            "structural cause",
            "root cause",
        ]
        if any(pattern in query_lower for pattern in cui_bono_patterns):
            score += 0.35
        
        # --- Topic sensitivity signals ---
        # Topics that are inherently multi-causal and need analytical depth
        # Not because they're taboo, but because simple answers are wrong answers
        sensitive_topic_pairs = [
            # (topic_keyword, context_keyword) — both must be present
            ("crime", "race"),
            ("crime", "ethnic"),
            ("crime", "immigrant"),
            ("poverty", "race"),
            ("poverty", "culture"),
            ("intelligence", "race"),
            ("welfare", "race"),
            ("terrorism", "muslim"),
            ("terrorism", "islam"),
            ("crime", "neighborhood"),
            ("gentrification", "displacement"),
        ]
        for topic, context in sensitive_topic_pairs:
            if topic in query_lower and context in query_lower:
                score += 0.4
                break  # Only count once
        
        # Cap at 0.65 — semantic complexity alone can push past threshold (0.6)
        # but shouldn't dominate when combined with syntactic complexity
        return min(score, 0.65)
    
    def _simple_query_result(self, query: str) -> DecompositionResult:
        """Create a DecompositionResult for a simple (non-decomposed) query."""
        # Classify the single query
        query_type = self._classify_simple_query(query)
        
        sub_query = SubQuery(
            query=query,
            type=query_type,
            confidence=1.0,
            dependencies=[],
            metadata={}
        )
        
        return DecompositionResult(
            sub_queries=[sub_query],
            original_query=query,
            is_complex=False,
            reasoning="Query is simple and doesn't require decomposition"
        )
    
    def _classify_simple_query(self, query: str) -> SubQueryType:
        """Classify a simple query using heuristics."""
        query_lower = query.lower()
        
        # RAG answerable indicators (check first - most specific)
        if any(keyword in query_lower for keyword in ['my notes', 'my knowledge', 'what did i write', 'what have i written', 'show me', 'find in my']):
            return SubQueryType.RAG_ANSWERABLE
        
        # Code generation indicators
        if any(keyword in query_lower for keyword in ['write code', 'implement', 'function', 'class', 'script', 'program']):
            return SubQueryType.CODE_GEN
        
        # Creative writing indicators (be specific to avoid false positives)
        if any(keyword in query_lower for keyword in ['write a blog', 'write an article', 'create a story', 'draft a', 'blog post', 'article']):
            return SubQueryType.CREATIVE
        
        # Analysis indicators (explicit keywords)
        if any(keyword in query_lower for keyword in ['analyze', 'compare', 'evaluate', 'assess']):
            return SubQueryType.ANALYSIS
        
        # Semantic complexity check: topics requiring analytical depth should
        # be classified as ANALYSIS, not FACTUAL, even when stated simply.
        # "I want to talk about the Somali problem in Minneapolis" needs
        # analysis, not a factual lookup.
        if self._semantic_complexity_score(query_lower) > 0.0:
            return SubQueryType.ANALYSIS
        
        # Reasoning indicators
        if any(keyword in query_lower for keyword in ['why', 'how', 'explain', 'understand']):
            return SubQueryType.REASONING
        
        # Default to factual lookup
        return SubQueryType.FACTUAL
    
    async def _check_patterns(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[DecompositionResult]:
        """
        Check if query matches known patterns for decomposition.
        
        Returns:
            DecompositionResult if pattern found, None otherwise
        """
        try:
            # Search for routing patterns
            patterns = self.pattern_learner.search_patterns(
                query=query,
                pattern_type="routing",
                limit=3
            )
            
            if patterns:
                # Use highest confidence pattern
                best_pattern = max(patterns, key=lambda p: p.confidence)
                
                if best_pattern.confidence > 0.7:
                    logger.debug(f"Using known pattern: {best_pattern.description}")
                    # Pattern found but we still decompose normally
                    # This is just for logging/metrics
                    # Actual pattern-informed routing happens in split_router
                    return None
            
        except Exception as e:
            logger.debug(f"Pattern check failed: {e}")
        
        return None
    
    async def _llm_decompose(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> DecompositionResult:
        """
        Use LLM to decompose query into sub-queries.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            DecompositionResult with decomposed sub-queries
        """
        if not self.router:
            raise ValueError("Router required for LLM decomposition")
        
        # Format prompt
        context_str = json.dumps(context, indent=2) if context else "{}"
        prompt = self.DECOMPOSITION_PROMPT.format(
            query=query,
            context=context_str
        )
        
        # Call LLM via router (using model tier from config)
        try:
            # Convert model tier to ConfidenceLevel
            from core.router_v2 import ConfidenceLevel
            if self.model == 'fast':
                confidence = ConfidenceLevel.FAST
            elif self.model == 'thorough':
                confidence = ConfidenceLevel.THOROUGH
            else:
                confidence = ConfidenceLevel.BALANCED
            
            # Format prompt as messages (OpenAI format)
            messages = [{"role": "user", "content": prompt}]
            
            # Use complete_with_fallback for automatic fallback chain
            response = await self.router.complete_with_fallback(
                messages=messages,
                confidence=confidence,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse response
            response_text = response.content
            result_data = self._parse_llm_response(response_text)
            
            # Build DecompositionResult
            sub_queries = [
                SubQuery(
                    query=sq['query'],
                    type=SubQueryType(sq['type']),
                    confidence=sq.get('confidence', 0.8),
                    dependencies=sq.get('dependencies', []),
                    metadata=sq.get('metadata', {})
                )
                for sq in result_data.get('sub_queries', [])
            ]
            
            return DecompositionResult(
                sub_queries=sub_queries if sub_queries else [SubQuery(query=query, type=SubQueryType.REASONING)],
                original_query=query,
                is_complex=result_data.get('is_complex', True),
                reasoning=result_data.get('reasoning', '')
            )
            
        except Exception as e:
            logger.error(f"LLM decomposition failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response JSON.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed dict
        """
        # Clean response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith('```'):
            # Remove code block markers
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1] if len(lines) > 2 else lines)
        
        response = response.strip()
        if response.startswith('json'):
            response = response[4:].strip()
        
        try:
            # Try parsing with strict=False to allow control characters (newlines in strings)
            return json.loads(response, strict=False)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response}")
            
            # Try to fix common issues: escape newlines in string values
            try:
                # Replace literal newlines in JSON strings (but not in JSON structure)
                # This is a heuristic fix - replace \n that appear between quotes
                import re
                # Find all string values and escape their newlines
                fixed_response = re.sub(r':\s*"([^"]*)"', lambda m: f': "{m.group(1).replace(chr(10), "\\n").replace(chr(13), "\\r")}"', response)
                return json.loads(fixed_response, strict=False)
            except:
                raise ValueError(f"Invalid JSON response from LLM: {e}")
