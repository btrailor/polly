"""
Nexus Agent Interface — Phase 24a Foundation

Pure Python dataclasses + Protocol. No CrewAI or external agent framework
dependency at this stage. CrewAI can be a Phase 24b execution backend.

Defines:
    ExecutionMode     — autonomous / interactive / hybrid
    AgentStatus       — idle / running / paused / completed / failed
    ResourceConstraints — cost + latency guardrails
    AgentCapability   — a single named capability with I/O schema
    AgentContract     — full agent descriptor (capabilities, domains, etc.)
    AgentInput        — input envelope for agent execution
    AgentResult       — output envelope from agent execution
    Executable        — runtime Protocol; anything with contract + execute()
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ExecutionMode(str, Enum):
    AUTONOMOUS = "autonomous"
    INTERACTIVE = "interactive"
    HYBRID = "hybrid"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Resource constraints
# ---------------------------------------------------------------------------

@dataclass
class ResourceConstraints:
    """Guardrails for a single agent execution."""
    max_tokens: int = 4096
    timeout_seconds: int = 120
    cost_cap_usd: float = 0.10
    prefer_local: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
            "cost_cap_usd": self.cost_cap_usd,
            "prefer_local": self.prefer_local,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ResourceConstraints":
        return cls(
            max_tokens=d.get("max_tokens", 4096),
            timeout_seconds=d.get("timeout_seconds", 120),
            cost_cap_usd=d.get("cost_cap_usd", 0.10),
            prefer_local=d.get("prefer_local", True),
        )


# ---------------------------------------------------------------------------
# Agent capability
# ---------------------------------------------------------------------------

@dataclass
class AgentCapability:
    """A named, schema-bearing capability that an agent can perform."""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AgentCapability":
        return cls(
            name=d["name"],
            description=d.get("description", ""),
            input_schema=d.get("input_schema", {}),
            output_schema=d.get("output_schema", {}),
        )


# ---------------------------------------------------------------------------
# Agent contract
# ---------------------------------------------------------------------------

@dataclass
class AgentContract:
    """
    Full descriptor for a registered agent.

    The contract is immutable after registration (id, name, agent_type).
    Capability declarations and domain affinity inform routing.
    """
    id: str
    name: str
    agent_type: str

    capabilities: List[AgentCapability] = field(default_factory=list)
    execution_contexts: List[str] = field(default_factory=list)  # e.g. ["chat", "batch"]
    resource_constraints: ResourceConstraints = field(default_factory=ResourceConstraints)
    domain_affinity: List[str] = field(default_factory=list)  # e.g. ["writing", "code"]
    execution_mode: ExecutionMode = ExecutionMode.INTERACTIVE

    def has_capability(self, name: str) -> bool:
        """Return True if this agent declares the named capability."""
        return any(c.name == name for c in self.capabilities)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "execution_contexts": self.execution_contexts,
            "resource_constraints": self.resource_constraints.to_dict(),
            "domain_affinity": self.domain_affinity,
            "execution_mode": self.execution_mode.value,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AgentContract":
        return cls(
            id=d["id"],
            name=d["name"],
            agent_type=d.get("agent_type", "generic"),
            capabilities=[AgentCapability.from_dict(c) for c in d.get("capabilities", [])],
            execution_contexts=d.get("execution_contexts", []),
            resource_constraints=ResourceConstraints.from_dict(
                d.get("resource_constraints", {})
            ),
            domain_affinity=d.get("domain_affinity", []),
            execution_mode=ExecutionMode(d.get("execution_mode", "interactive")),
        )


# ---------------------------------------------------------------------------
# Agent input / result
# ---------------------------------------------------------------------------

@dataclass
class AgentInput:
    """Input envelope for a single agent execution."""
    query: str
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    execution_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AgentResult:
    """Output envelope from a single agent execution."""
    agent_id: str
    execution_id: str
    status: AgentStatus

    content: str = ""
    output: Dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "content": self.content,
            "output": self.output,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Executable Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class Executable(Protocol):
    """
    Runtime Protocol: anything that can be registered in NexusCoordinator.

    Implementors:
        - PersonaAgent (Phase 24a) — wraps existing AgentPersona
        - CrewAIAgent (Phase 24b) — wraps CrewAI agent/crew
        - Future: ExternalAPIAgent, LangGraphAgent, etc.
    """
    contract: AgentContract

    async def execute(self, agent_input: AgentInput) -> AgentResult:
        """Execute the agent and return a result."""
        ...

    def can_handle(self, capability: str) -> bool:
        """Return True if this agent can handle the given capability."""
        ...
