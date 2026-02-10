"""
Build prompt context from the knowledge graph.

Replaces KnowledgeGraph.get_context_for_query() with graph-aware context.
"""

from __future__ import annotations

import logging
import re
from typing import Any, List, Optional, Set

from .models import Entity, EntityQuery, EntityType
from .store import EntityStore

logger = logging.getLogger(__name__)


class EntityContextBuilder:
    """Build knowledge graph context for system prompt. PersonaAware + ContextContributor."""

    context_priority = 40

    def __init__(self, store: EntityStore, pattern_engine: Any = None):
        self.store = store
        self.pattern_engine = pattern_engine  # Optional: for persona-affinity entity boost
        self._active_persona: Optional[str] = None
        self._active_mode: Optional[str] = None

    def _get_persona_affinity_terms(self, persona_name: str, max_terms: int = 30) -> Set[str]:
        """Extract entity-like terms from this persona's patterns (names/descriptions)."""
        if not self.pattern_engine or not hasattr(self.pattern_engine, "get_persona_patterns"):
            return set()
        try:
            patterns = self.pattern_engine.get_persona_patterns(persona_name, limit=20)
            terms: Set[str] = set()
            for p in patterns:
                for text in (p.name, p.description or ""):
                    # Simple tokenization: words of 2+ chars
                    for word in re.findall(r"[a-zA-Z0-9_][a-zA-Z0-9_-]{1,}", text):
                        if len(word) >= 2:
                            terms.add(word.lower())
                if p.examples:
                    for ex in p.examples[:2]:
                        for word in re.findall(r"[a-zA-Z0-9_][a-zA-Z0-9_-]{1,}", str(ex)[:200]):
                            if len(word) >= 2:
                                terms.add(word.lower())
            return set(list(terms)[:max_terms])
        except Exception as e:
            logger.debug(f"Persona affinity terms failed: {e}")
            return set()

    def set_active_persona(self, persona_name: str, mode: str) -> None:
        """Notify of active persona (PersonaAware protocol)."""
        self._active_persona = persona_name
        self._active_mode = mode

    def get_persona_context(self, persona_name: str, mode: str) -> dict:
        """Return persona-specific context (e.g. entity affinities). Empty for now."""
        return {}

    def build_context(
        self,
        query: str,
        domains: List[str],
        max_entities: int = 10,
        include_relationships: bool = True,
        include_cross_domain: bool = True,
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        **kwargs: object,
    ) -> str:
        """Build formatted context block for prompt injection."""
        persona_name = persona or self._active_persona
        affinity_terms = self._get_persona_affinity_terms(persona_name) if persona_name else set()

        # 1) Lightweight entity extraction from query (keyword match in store)
        query_lower = query.lower()
        query_words = set(query_lower.split())
        # Find entities whose name or alias appears in query
        all_entities = self.store.get_top_entities(limit=max_entities * 3)
        matching: List[Entity] = []
        for e in all_entities:
            name_lower = e.name.lower()
            if name_lower in query_lower or any(w in name_lower for w in query_words if len(w) > 2):
                matching.append(e)
            elif e.aliases and any(a.lower() in query_lower for a in e.aliases):
                matching.append(e)
        # 2) Add top by authority if we have domains
        if domains:
            for d in domains:
                eq = EntityQuery(domains=[d], min_authority=0.1, limit=5)
                for e in self.store.search(eq):
                    if e not in matching and len(matching) < max_entities:
                        matching.append(e)
        # Dedupe by id
        seen = set()
        unique: List[Entity] = []
        for e in matching:
            if e.id not in seen:
                seen.add(e.id)
                unique.append(e)
        # 3) Boost persona-affinity entities to the top when active
        if affinity_terms and unique:
            def _affinity_score(entity: Entity) -> int:
                name_lower = entity.name.lower()
                if name_lower in affinity_terms:
                    return 1
                if entity.aliases and any(a.lower() in affinity_terms for a in entity.aliases):
                    return 1
                return 0
            unique.sort(key=lambda e: _affinity_score(e), reverse=True)
        matching = unique[:max_entities]
        if not matching:
            return ""

        parts = ["## Relevant Knowledge Graph Context\n"]
        for entity in matching:
            et = entity.entity_type.value if isinstance(entity.entity_type, EntityType) else entity.entity_type
            parts.append(f"\n### {entity.name} ({et})")
            if entity.description:
                parts.append(f"{entity.description}")
            if include_relationships:
                related = self.store.get_related(entity.id, max_hops=1, min_strength=0.2)
                if related:
                    parts.append("\nRelated:")
                    for rel_entity, rel in related[:5]:
                        rt = rel.relationship_type.value if hasattr(rel.relationship_type, "value") else rel.relationship_type
                        parts.append(f"- {rel_entity.name} ({rt})")
        # Cross-domain bridges
        if include_cross_domain and len(domains) >= 2:
            bridges = self.store.get_cross_domain_bridges(domains[0], domains[1], limit=5)
            if bridges:
                parts.append("\n**Cross-Domain Connections:**")
                for b in bridges:
                    parts.append(f"- {b.name} (spans {domains[0]} and {domains[1]})")
        # Connection path if two entities
        if include_relationships and len(matching) >= 2:
            path = self.store.find_path(matching[0].id, matching[1].id, max_hops=4)
            if path and len(path) > 1:
                path_names = [p[0].name for p in path]
                parts.append(f"\nConnection path: {' → '.join(path_names)}")
        return "\n".join(parts)
