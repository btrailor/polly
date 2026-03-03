"""
Graph-based retriever — ContextContributor that discovers content via entity graph traversal.

Phase 12b: Retrieves context by extracting entities from the user's query, matching
them against the knowledge graph, and traversing relationships to find connected
content that semantic search alone would miss.

Usage:
    from core.entities.retriever import GraphRetriever

    retriever = GraphRetriever(entity_store, entity_extractor, config)
    context_str = retriever.build_context(query, domains)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .extractor import EntityExtractor
from .models import Entity, EntityQuery, EntityType
from .store import EntityStore

logger = logging.getLogger(__name__)


@dataclass
class GraphTraversalResult:
    """A single result from graph traversal retrieval."""
    entity: Entity
    source_path: str
    source_type: str
    context_snippet: str
    hop_distance: int
    traversal_score: float  # Combined score: 1/(hop+1) * authority * strength
    relationship_chain: List[str] = field(default_factory=list)  # e.g. ["RELATED_TO", "INSPIRES"]


class GraphRetriever:
    """ContextContributor that retrieves content via entity graph traversal.

    Priority 45: between memory retrieval (50) and entity context (40).
    Provides a different signal than EntityContextBuilder — instead of formatting
    entity relationships as context, this retriever finds *source documents*
    connected through the entity graph that should be included in RAG results.
    """

    def __init__(
        self,
        entity_store: EntityStore,
        entity_extractor: EntityExtractor,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.entity_store = entity_store
        self.extractor = entity_extractor
        cfg = (config or {}).get("knowledge_graph", {}).get("graph_traversal", {})
        self.max_hops: int = cfg.get("max_hops", 2)
        self.min_strength: float = cfg.get("min_strength", 0.3)
        self.enabled: bool = cfg.get("enabled", True)
        self._priority: int = cfg.get("contributor_priority", 45)

    @property
    def context_priority(self) -> int:
        return self._priority

    # ------------------------------------------------------------------
    # Core traversal
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        domains: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> List[GraphTraversalResult]:
        """Retrieve source documents connected through entity graph traversal.

        1. Extract entities from query text (no storage).
        2. Fuzzy-match each against the EntityStore.
        3. Traverse relationships up to max_hops.
        4. Collect source mentions for traversed entities.
        5. Score by hop distance, authority, and relationship strength.
        6. Deduplicate by source path and return top results.
        """
        if not self.enabled:
            return []

        # 1. Extract entities from query
        query_entities = self.extractor.extract_entities_only(query)
        if not query_entities:
            # Try simple word-level matching as fallback
            query_entities = self._fuzzy_match_query_words(query)
        if not query_entities:
            return []

        logger.debug(f"GraphRetriever: extracted {len(query_entities)} entities from query")

        # 2. Match against store
        matched_entities: List[Entity] = []
        for qe in query_entities:
            # Try exact match first
            stored = self.entity_store.get_entity(qe.id)
            if stored:
                matched_entities.append(stored)
                continue
            # Try name-based lookup
            stored = self.entity_store.get_entity_by_name(qe.name)
            if stored:
                matched_entities.append(stored)

        if not matched_entities:
            logger.debug("GraphRetriever: no entities matched in store")
            return []

        logger.debug(f"GraphRetriever: {len(matched_entities)} entities matched in store")

        # 3. Traverse and collect
        results: List[GraphTraversalResult] = []
        visited_sources: Set[str] = set()

        for root_entity in matched_entities:
            # Add root entity's own mentions first (hop 0)
            self._collect_mentions(
                root_entity,
                hop_distance=0,
                rel_chain=[],
                rel_strength=1.0,
                results=results,
                visited_sources=visited_sources,
                domains=domains,
            )

            # Traverse neighbors
            related = self.entity_store.get_related(
                root_entity.id,
                max_hops=self.max_hops,
                min_strength=self.min_strength,
            )
            for related_entity, relationship in related:
                # Estimate hop distance from relationship strength decay
                # (get_related returns BFS results, hop encoded by order)
                hop = 1  # Default; get_related doesn't expose hop, but
                # we can infer: lower strength suggests further hop
                self._collect_mentions(
                    related_entity,
                    hop_distance=hop,
                    rel_chain=[relationship.relationship_type.value],
                    rel_strength=relationship.strength,
                    results=results,
                    visited_sources=visited_sources,
                    domains=domains,
                )

        # 4. Sort by traversal score and return top N
        results.sort(key=lambda r: r.traversal_score, reverse=True)
        return results[:max_results]

    def _collect_mentions(
        self,
        entity: Entity,
        hop_distance: int,
        rel_chain: List[str],
        rel_strength: float,
        results: List[GraphTraversalResult],
        visited_sources: Set[str],
        domains: Optional[List[str]] = None,
    ) -> None:
        """Collect source mentions for an entity and add to results."""
        try:
            conn = self.entity_store._conn()
            cur = conn.execute(
                """
                SELECT source_type, source_id, context
                FROM entity_mentions
                WHERE entity_id = ?
                ORDER BY created DESC
                LIMIT 20
                """,
                (entity.id,),
            )
            for row in cur.fetchall():
                source_type, source_id, context = row
                if source_id in visited_sources:
                    continue
                visited_sources.add(source_id)

                # Domain filtering: if domains specified, prefer matching domains
                # but still include cross-domain results (core value of graph traversal)
                domain_boost = 1.0
                if domains and entity.domains:
                    if any(d in entity.domains for d in domains):
                        domain_boost = 1.2  # Slight boost for same domain

                # Compute traversal score
                hop_factor = 1.0 / (hop_distance + 1)
                score = hop_factor * entity.authority_score * rel_strength * domain_boost

                results.append(GraphTraversalResult(
                    entity=entity,
                    source_path=source_id,
                    source_type=source_type,
                    context_snippet=context or "",
                    hop_distance=hop_distance,
                    traversal_score=score,
                    relationship_chain=list(rel_chain),
                ))
        except Exception as e:
            logger.debug(f"GraphRetriever: mention lookup for {entity.name} failed: {e}")

    def _fuzzy_match_query_words(self, query: str) -> List[Entity]:
        """Fall back to matching individual words against entity names."""
        import re
        words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        # Remove common stopwords
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
            'have', 'been', 'this', 'that', 'with', 'what', 'how',
            'when', 'where', 'why', 'who', 'about', 'which', 'from',
        }
        words -= stopwords

        matched: List[Entity] = []
        for word in words:
            result = self.entity_store.search(EntityQuery(text=word, limit=2))
            for entity in result:
                if entity.name.lower() == word or word in entity.name.lower():
                    if not any(m.id == entity.id for m in matched):
                        matched.append(entity)
        return matched[:5]  # Limit fuzzy matches

    # ------------------------------------------------------------------
    # ContextContributor interface
    # ------------------------------------------------------------------

    def build_context(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: Any,
    ) -> str:
        """Build context contribution from graph traversal results.

        Returns a formatted markdown string of graph-discovered content.
        """
        if not self.enabled:
            return ""

        results = self.retrieve(query, domains=domains)
        if not results:
            return ""

        # Format results into context string
        lines: List[str] = ["## Graph-Connected Context"]
        tokens_used = 0

        for r in results:
            entry = (
                f"- **{r.entity.name}** ({r.entity.entity_type.value})"
                f" [authority: {r.entity.authority_score:.2f}]"
            )
            if r.relationship_chain:
                entry += f" via {' → '.join(r.relationship_chain)}"
            if r.source_path:
                entry += f"\n  Source: {r.source_path}"
            if r.context_snippet:
                snippet = r.context_snippet[:200]
                entry += f"\n  Context: {snippet}"

            # Rough token estimate
            entry_tokens = len(entry) // 4
            if token_budget > 0 and tokens_used + entry_tokens > token_budget:
                break
            lines.append(entry)
            tokens_used += entry_tokens

        if len(lines) <= 1:
            return ""

        return "\n".join(lines)
