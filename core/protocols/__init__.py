"""
Integration contracts for Polly's core systems.

Protocols are descriptive — they formalize how systems interact.
Implementors: see design in openspec/changes/integration-contracts/design.md
"""

from .pattern_consumer import PatternConsumer
from .entity_provider import EntityProvider
from .persona_aware import PersonaAware
from .context_contributor import ContextContributor

__all__ = [
    "PatternConsumer",
    "EntityProvider",
    "PersonaAware",
    "ContextContributor",
]
