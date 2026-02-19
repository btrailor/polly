"""ContextContributor protocol — systems that contribute context to the system prompt."""

from __future__ import annotations

from typing import Any, Optional, Protocol


class ContextContributor(Protocol):
    """Systems that contribute context to the system prompt.

    Implemented by: MentalModelManager, EntityContextBuilder, PatternEngine,
                    CompressionManager, MemoryRetriever
    Each returns a formatted string block for prompt injection.
    """

    def build_context(
        self,
        query: str,
        domains: list[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: Any,
    ) -> str:
        """Build context contribution for system prompt.

        Args:
            query: The user's query
            domains: Active domains for this query
            persona: Active persona name
            mode: Persona mode
            token_budget: Maximum tokens for this contribution (0 = no limit).
                When specified, the contributor should truncate its output
                to fit within this budget.
            **kwargs: Additional keyword arguments

        Returns formatted markdown string (may be empty if nothing relevant).
        """
        ...

    @property
    def context_priority(self) -> int:
        """Priority for ordering in prompt (higher = closer to user message).

        Suggested ordering:
        - 100: Constitutional/ethics (always first)
        - 80: Persona mode prompt
        - 60: Mental models
        - 50: Memory retrieval
        - 40: Knowledge graph entities
        - 20: Learned patterns
        - 10: Compressed conversation summary
        """
        ...
