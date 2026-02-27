"""
Workflow types for multi-agent DAG execution (Phase 24b).

Defines:
    MergeStrategy   — how to combine results from parallel agents
    WorkflowStep    — a single step in a workflow (capability + deps + input mapping)
    WorkflowTemplate — a directed acyclic graph of steps with metadata
    StepResult      — the output of one completed step
    WorkflowResult  — the full output of a completed/paused/failed workflow
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from core.nexus.interface import AgentResult


# ---------------------------------------------------------------------------
# Merge strategy
# ---------------------------------------------------------------------------

class MergeStrategy(str, Enum):
    FIRST = "first"        # output_step's result is the final answer
    ENSEMBLE = "ensemble"  # concatenate all step results (for parallel workflows)


# ---------------------------------------------------------------------------
# WorkflowStep
# ---------------------------------------------------------------------------

@dataclass
class WorkflowStep:
    """
    A single node in the workflow DAG.

    Args:
        id:               Unique step identifier within the template (e.g. "researcher").
        agent_capability: The capability name to route this step to.
        input_mapping:    Maps step input keys to resolved variable references.
                          Use "$user_input" for the original query.
                          Use "$<step_id>.output" for a prior step's content.
        depends_on:       IDs of steps that must complete before this step runs.
    """
    id: str
    agent_capability: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_capability": self.agent_capability,
            "input_mapping": self.input_mapping,
            "depends_on": list(self.depends_on),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkflowStep":
        return cls(
            id=d["id"],
            agent_capability=d["agent_capability"],
            input_mapping=d.get("input_mapping", {}),
            depends_on=d.get("depends_on", []),
        )


# ---------------------------------------------------------------------------
# WorkflowTemplate
# ---------------------------------------------------------------------------

@dataclass
class WorkflowTemplate:
    """
    A reusable multi-agent workflow definition.

    The steps form a DAG. The planner performs a topological sort and groups
    independent steps for parallel execution.

    Args:
        id:                  Unique template identifier.
        name:                Human-readable name.
        description:         What this workflow does.
        steps:               List of WorkflowStep nodes.
        output_step:         ID of the step whose output is the final result.
        intervention_points: Step IDs after which to pause and await user confirmation.
        domain_affinity:     Suggested domains for this template.
        merge_strategy:      How to combine results (FIRST or ENSEMBLE).
        is_builtin:          True for Polly-provided templates.
    """
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    output_step: str
    intervention_points: List[str] = field(default_factory=list)
    domain_affinity: List[str] = field(default_factory=list)
    merge_strategy: MergeStrategy = MergeStrategy.FIRST
    is_builtin: bool = False

    # ---- Validation ----

    def validate(self) -> None:
        """
        Validate the template for structural correctness.

        Raises:
            ValueError: On cycle, missing output_step, or unknown depends_on ref.
        """
        step_ids = {s.id for s in self.steps}

        # output_step must exist
        if self.output_step not in step_ids:
            raise ValueError(
                f"WorkflowTemplate '{self.id}': output_step '{self.output_step}' "
                f"not in steps {sorted(step_ids)}"
            )

        # all depends_on refs must exist
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(
                        f"WorkflowTemplate '{self.id}': step '{step.id}' depends_on "
                        f"'{dep}' which does not exist"
                    )

        # no self-dependency
        for step in self.steps:
            if step.id in step.depends_on:
                raise ValueError(
                    f"WorkflowTemplate '{self.id}': step '{step.id}' depends on itself"
                )

        # cycle detection via Kahn's algorithm
        in_degree = {s.id: 0 for s in self.steps}
        adjacency: Dict[str, List[str]] = {s.id: [] for s in self.steps}
        for step in self.steps:
            for dep in step.depends_on:
                adjacency[dep].append(step.id)
                in_degree[step.id] += 1

        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        visited = 0
        while queue:
            node = queue.pop(0)
            visited += 1
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited != len(self.steps):
            raise ValueError(
                f"WorkflowTemplate '{self.id}': dependency cycle detected"
            )

    # ---- Serialization ----

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "output_step": self.output_step,
            "intervention_points": list(self.intervention_points),
            "domain_affinity": list(self.domain_affinity),
            "merge_strategy": self.merge_strategy.value,
            "is_builtin": self.is_builtin,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkflowTemplate":
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            steps=[WorkflowStep.from_dict(s) for s in d.get("steps", [])],
            output_step=d["output_step"],
            intervention_points=d.get("intervention_points", []),
            domain_affinity=d.get("domain_affinity", []),
            merge_strategy=MergeStrategy(d.get("merge_strategy", "first")),
            is_builtin=d.get("is_builtin", False),
        )

    def __repr__(self) -> str:
        return (
            f"<WorkflowTemplate id={self.id!r} steps={len(self.steps)} "
            f"output={self.output_step!r}>"
        )


# ---------------------------------------------------------------------------
# StepResult
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    """
    The output of a single completed workflow step.

    Args:
        step_id:      The WorkflowStep.id this result belongs to.
        agent_id:     The agent that executed this step.
        result:       The full AgentResult from the agent.
        started_at:   ISO timestamp when the step began.
        completed_at: ISO timestamp when the step finished.
    """
    step_id: str
    agent_id: str
    result: AgentResult
    started_at: str
    completed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "result": self.result.to_dict(),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StepResult":
        from core.nexus.interface import AgentResult, AgentStatus
        r = d["result"]
        result = AgentResult(
            agent_id=r["agent_id"],
            execution_id=r["execution_id"],
            status=AgentStatus(r["status"]),
            content=r.get("content", ""),
            output=r.get("output", {}),
            tokens_used=r.get("tokens_used", 0),
            cost_usd=r.get("cost_usd", 0.0),
            duration_ms=r.get("duration_ms", 0),
            error=r.get("error"),
        )
        return cls(
            step_id=d["step_id"],
            agent_id=d["agent_id"],
            result=result,
            started_at=d["started_at"],
            completed_at=d["completed_at"],
        )


# ---------------------------------------------------------------------------
# WorkflowResult
# ---------------------------------------------------------------------------

@dataclass
class WorkflowResult:
    """
    The output of a completed, paused, or failed workflow execution.

    Args:
        execution_id:    The storage execution ID.
        template_id:     The WorkflowTemplate used.
        status:          "completed", "paused", or "failed".
        step_results:    Map of step_id → StepResult for all completed steps.
        final_content:   The content of the output_step (or empty string).
        final_output:    The output dict of the output_step.
        total_tokens:    Sum of tokens across all agent runs.
        total_cost_usd:  Sum of cost across all agent runs.
        total_duration_ms: Wall-clock time from start to finish.
        paused_at_step:  Step ID where execution paused (if status=="paused").
        error:           Error message (if status=="failed").
    """
    execution_id: str
    template_id: str
    status: str
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    final_content: str = ""
    final_output: Dict[str, Any] = field(default_factory=dict)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: int = 0
    paused_at_step: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "template_id": self.template_id,
            "status": self.status,
            "step_results": {k: v.to_dict() for k, v in self.step_results.items()},
            "final_content": self.final_content,
            "final_output": self.final_output,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "total_duration_ms": self.total_duration_ms,
            "paused_at_step": self.paused_at_step,
            "error": self.error,
        }

    def __repr__(self) -> str:
        return (
            f"<WorkflowResult execution_id={self.execution_id!r} "
            f"status={self.status!r} steps={len(self.step_results)}>"
        )
