"""EntityProvider protocol — systems that produce entities for the knowledge graph."""

from __future__ import annotations

from typing import Any, List, Protocol

# Entity type from core.entities (avoid circular import)
# Implementors use: from core.entities import Entity


class EntityProvider(Protocol):
    """Systems that produce entities for the knowledge graph.

    Implemented by: EntityExtractor, PatternEngine, KnowledgeWriter, (future) BookLore
    """

    def extract_entities(
        self, content: str, source_type: str, source_id: str
    ) -> List[Any]:
        """Extract entities from content and return them.

        The caller (usually the query pipeline) is responsible for storing.
        """
        ...
