"""
Persona system for Polly (Phase 11c + 16c)

Agent personas are specialized AI workflows with distinct modes of operation.
Users can manually switch between modes to control the reasoning approach.

Available Personas:
- Architect: Planning and building complex tasks (note creation, project planning)
- Scribe: Transform conversations into structured notes with auto-linking (Phase 16c)

Future Personas (not yet implemented):
- Librarian: Knowledge organization and discovery
- Programmer: Code generation and debugging
- Professor: Teaching and learning
- Administrator: Scheduling and communication
"""

from .base import (
    AgentPersona,
    PersonaContext,
    PersonaResponse,
    PersonaAction,
    PersonaState
)

from .models import (
    # Architect models
    Plan,
    GeneratedContent,
    OutlineNode,
    Template,
    # Lazy-loading models (Phase 16c)
    PersonaMetadata,
    ModeMetadata,
    PersonaPromptCache
)

from .architect import ArchitectPersona
from .implementations.scribe import ScribePersona
from .manager import PersonaManager

__all__ = [
    # Base classes
    'AgentPersona',
    'PersonaContext',
    'PersonaResponse',
    'PersonaAction',
    'PersonaState',
    
    # Architect models
    'Plan',
    'GeneratedContent',
    'OutlineNode',
    'Template',
    
    # Lazy-loading models (Phase 16c)
    'PersonaMetadata',
    'ModeMetadata',
    'PersonaPromptCache',
    
    # Personas
    'ArchitectPersona',
    'ScribePersona',  # Phase 16c
    
    # Manager
    'PersonaManager',
]
