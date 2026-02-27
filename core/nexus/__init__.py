"""
Polly Nexus — Phase 24a + Phase 24b

Provides:
  Phase 24a:
  - AgentContract, AgentCapability, AgentInput, AgentResult, Executable: core interface
  - ExecutionMode, AgentStatus, ResourceConstraints: enums + guardrails
  - PersonaAgent: wraps existing AgentPersona as Executable
  - AgentRegistry: SQLite-backed agent discovery
  - SwarmStorage: SQLite execution history
  - NexusCoordinator: single-agent routing

  Phase 24b:
  - WorkflowStep, WorkflowTemplate, MergeStrategy: DAG workflow types
  - StepResult, WorkflowResult: execution output types
  - WorkflowPlanner: topological sort + input resolution
  - WorkflowExecutor: parallel/sequential multi-agent execution
  - TemplateRegistry, BUILTIN_TEMPLATES: template management
  - NexusCoordinator.execute_workflow(): multi-agent entry point
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
from core.nexus.workflow import (
    MergeStrategy,
    StepResult,
    WorkflowResult,
    WorkflowStep,
    WorkflowTemplate,
)
from core.nexus.planner import ExecutionGroup, WorkflowPlanner
from core.nexus.executor import WorkflowExecutor
from core.nexus.templates import BUILTIN_TEMPLATES, TemplateRegistry

__all__ = [
    # interface (Phase 24a)
    "AgentCapability",
    "AgentContract",
    "AgentInput",
    "AgentResult",
    "AgentStatus",
    "Executable",
    "ExecutionMode",
    "ResourceConstraints",
    # adapter (Phase 24a)
    "PersonaAgent",
    "PERSONA_CAPABILITY_MAP",
    # storage (Phase 24a)
    "AgentRegistry",
    "SwarmStorage",
    # coordinator (Phase 24a/24b)
    "NexusCoordinator",
    "TaskComplexity",
    # workflow types (Phase 24b)
    "MergeStrategy",
    "StepResult",
    "WorkflowResult",
    "WorkflowStep",
    "WorkflowTemplate",
    # planner (Phase 24b)
    "ExecutionGroup",
    "WorkflowPlanner",
    # executor (Phase 24b)
    "WorkflowExecutor",
    # templates (Phase 24b)
    "BUILTIN_TEMPLATES",
    "TemplateRegistry",
]
