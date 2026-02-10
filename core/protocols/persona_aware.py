"""PersonaAware protocol — systems that adapt behavior per active persona."""

from __future__ import annotations

from typing import Any, Dict, Protocol


class PersonaAware(Protocol):
    """Systems that adapt behavior per-persona.

    Implemented by: PatternEngine, MentalModelManager, EntityContextBuilder, Router
    """

    def set_active_persona(self, persona_name: str, mode: str) -> None:
        """Notify this system that the active persona/mode has changed."""
        ...

    def get_persona_context(self, persona_name: str, mode: str) -> Dict[str, Any]:
        """Get persona-specific context from this system."""
        ...
