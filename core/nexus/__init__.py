"""
Polly Nexus Foundation — Phase 24a

Provides:
  - AgentContract, AgentCapability, AgentInput, AgentResult, Executable: core interface
  - ExecutionMode, AgentStatus, ResourceConstraints: enums + guardrails
  - PersonaAgent: wraps existing AgentPersona as Executable
  - AgentRegistry: SQLite-backed agent discovery
  - SwarmStorage: SQLite execution history
  - NexusCoordinator: single-agent routing (Phase 24a)

Phase 24b additions (deferred):
  - Multi-agent DAG execution
  - Workflow templates
  - CrewAI execution backend
"""

from core.nexus.interface import (
    AgentCapability,
    AgentContract,
    AgentInput,
    AgentResult,
    AgentStatus,
    Executable,
    ExecutionMode,
    ResourceConstraints,
)
from core.nexus.persona_adapter import PersonaAgent, PERSONA_CAPABILITY_MAP
from core.nexus.registry import AgentRegistry
from core.nexus.storage import SwarmStorage
from core.nexus.coordinator import NexusCoordinator, TaskComplexity

__all__ = [
    # interface
    "AgentCapability",
    "AgentContract",
    "AgentInput",
    "AgentResult",
    "AgentStatus",
    "Executable",
    "ExecutionMode",
    "ResourceConstraints",
    # adapter
    "PersonaAgent",
    "PERSONA_CAPABILITY_MAP",
    # storage
    "AgentRegistry",
    "SwarmStorage",
    # coordinator
    "NexusCoordinator",
    "TaskComplexity",
]
