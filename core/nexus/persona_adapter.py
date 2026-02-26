"""
PersonaAgent — wraps AgentPersona as Nexus Executable (Phase 24a)

Adapts Polly's existing persona system (ScribePersona, ArchitectPersona,
ProfessorPersona) to the Executable Protocol so they can be routed by
NexusCoordinator without duplication or reimplementation.

Usage:
    from core.personas.manager import PersonaManager
    from core.nexus.persona_adapter import PersonaAgent

    persona = persona_manager.get_persona("scribe")
    agent = PersonaAgent(persona, "scribe")
    result = await agent.execute(AgentInput(query="Save this note"))
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from core.nexus.interface import (
    AgentCapability,
    AgentContract,
    AgentInput,
    AgentResult,
    AgentStatus,
    ExecutionMode,
    ResourceConstraints,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Capability declarations per persona
# ---------------------------------------------------------------------------

# Maps persona_name → list of capability dicts
# These are hardcoded to match the Phase 24 spec persona ↔ capability mapping.
PERSONA_CAPABILITY_MAP: Dict[str, List[Dict[str, Any]]] = {
    "scribe": [
        {
            "name": "capture_note",
            "description": "Capture and structure user input as a note in the knowledge base.",
            "input_schema": {"query": "string", "format": "string?"},
            "output_schema": {"note_id": "string", "content": "string"},
        },
        {
            "name": "organize_notes",
            "description": "Organize, tag, and link existing notes.",
            "input_schema": {"query": "string"},
            "output_schema": {"content": "string"},
        },
        {
            "name": "summarize",
            "description": "Summarize content or a collection of notes.",
            "input_schema": {"query": "string"},
            "output_schema": {"summary": "string"},
        },
    ],
    "architect": [
        {
            "name": "plan_task",
            "description": "Break down a complex goal into structured steps and deliverables.",
            "input_schema": {"query": "string", "context": "dict?"},
            "output_schema": {"plan": "string", "steps": "list"},
        },
        {
            "name": "design_system",
            "description": "Design software system architecture and component structure.",
            "input_schema": {"query": "string"},
            "output_schema": {"design": "string"},
        },
        {
            "name": "review_code",
            "description": "Review code for correctness, style, and architectural fit.",
            "input_schema": {"query": "string", "code": "string?"},
            "output_schema": {"feedback": "string"},
        },
    ],
    "professor": [
        {
            "name": "explain_concept",
            "description": "Explain a technical or academic concept clearly and pedagogically.",
            "input_schema": {"query": "string", "level": "string?"},
            "output_schema": {"explanation": "string"},
        },
        {
            "name": "teach_topic",
            "description": "Provide a structured lesson or tutorial on a topic.",
            "input_schema": {"query": "string"},
            "output_schema": {"lesson": "string"},
        },
        {
            "name": "answer_question",
            "description": "Answer a factual or conceptual question with depth and accuracy.",
            "input_schema": {"query": "string"},
            "output_schema": {"answer": "string"},
        },
    ],
}

# Domain affinity per persona
PERSONA_DOMAIN_MAP: Dict[str, List[str]] = {
    "scribe": ["writing", "notes", "knowledge", "capture", "organization"],
    "architect": ["code", "software", "architecture", "planning", "engineering"],
    "professor": ["education", "learning", "explanation", "teaching", "research"],
}


class PersonaAgent:
    """
    Adapts an AgentPersona instance to the Nexus Executable Protocol.

    Does NOT create a new persona instance — wraps the existing one from
    PersonaManager to avoid duplication.

    Args:
        persona:      The AgentPersona instance (ScribePersona, etc.)
        persona_name: The persona slug ("scribe", "architect", "professor")
    """

    def __init__(self, persona: Any, persona_name: str) -> None:
        self.persona = persona
        self.persona_name = persona_name.lower()
        self.contract = self._build_contract(self.persona_name)

    def _build_contract(self, persona_name: str) -> AgentContract:
        """Build AgentContract from PERSONA_CAPABILITY_MAP + PERSONA_DOMAIN_MAP."""
        cap_dicts = PERSONA_CAPABILITY_MAP.get(persona_name, [])
        capabilities = [AgentCapability.from_dict(c) for c in cap_dicts]
        domains = PERSONA_DOMAIN_MAP.get(persona_name, [])

        return AgentContract(
            id=f"persona_{persona_name}",
            name=persona_name.title(),
            agent_type="persona",
            capabilities=capabilities,
            execution_contexts=["chat", "interactive"],
            resource_constraints=ResourceConstraints(prefer_local=True),
            domain_affinity=domains,
            execution_mode=ExecutionMode.INTERACTIVE,
        )

    def can_handle(self, capability: str) -> bool:
        """Return True if this persona declares the given capability."""
        return self.contract.has_capability(capability)

    async def execute(self, agent_input: AgentInput) -> AgentResult:
        """
        Delegate to persona.process() and wrap the PersonaResponse as AgentResult.

        Imports PersonaContext lazily to avoid circular imports at module load.
        """
        from core.personas.base import PersonaContext

        start_ms = time.monotonic() * 1000
        execution_id = agent_input.execution_id or str(uuid.uuid4())

        try:
            ctx = PersonaContext(
                user_message=agent_input.query,
                conversation_history=agent_input.context.get("conversation_history", []),
                current_mode=agent_input.data.get("mode"),
                metadata=agent_input.data,
            )

            persona_response = await self.persona.process(ctx)

            duration_ms = int(time.monotonic() * 1000 - start_ms)

            return AgentResult(
                agent_id=self.contract.id,
                execution_id=execution_id,
                status=AgentStatus.COMPLETED,
                content=getattr(persona_response, "content", str(persona_response)),
                output={
                    "mode": getattr(persona_response, "mode", ""),
                    "actions": [
                        a.to_dict() if hasattr(a, "to_dict") else a
                        for a in getattr(persona_response, "actions", [])
                    ],
                    "metadata": getattr(persona_response, "metadata", {}),
                },
                tokens_used=0,  # Tracked by router layer
                cost_usd=0.0,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int(time.monotonic() * 1000 - start_ms)
            logger.warning(
                f"PersonaAgent.execute failed for '{self.persona_name}': {e}"
            )
            return AgentResult(
                agent_id=self.contract.id,
                execution_id=execution_id,
                status=AgentStatus.FAILED,
                content="",
                error=str(e),
                duration_ms=duration_ms,
            )

    def __repr__(self) -> str:
        cap_names = [c.name for c in self.contract.capabilities]
        return f"<PersonaAgent name={self.persona_name!r} capabilities={cap_names}>"
