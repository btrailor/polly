"""PatternConsumer protocol — systems that consume patterns to adapt behavior."""

from __future__ import annotations

from typing import Any, Dict, List, Protocol

# Pattern type from core.patterns (avoid circular import by using string annotation)
# Implementors use: from core.patterns import Pattern


class PatternConsumer(Protocol):
    """Systems that consume patterns to adapt behavior.

    Implemented by: Router, RAG, DomainEngine, PersonaManager
    """

    def apply_patterns(self, patterns: List[Any], context: Dict[str, Any]) -> None:
        """Apply relevant patterns to current operation.

        Args:
            patterns: Relevant patterns from PatternEngine
            context: Current operation context (query, domain, persona, etc.)
        """
        ...

    def report_outcome(self, pattern_id: str, was_helpful: bool, metadata: Dict[str, Any]) -> None:
        """Report whether a pattern-informed decision was helpful.

        Enables pattern reinforcement/decay based on actual outcomes.
        """
        ...
