"""
WorkflowPlanner — DAG planning for multi-agent workflows (Phase 24b).

Responsibilities:
  - Validate a WorkflowTemplate (structural checks, cycle detection)
  - Topological sort → group independent steps for parallel execution
  - Resolve $-prefixed input variable references at execution time

Usage:
    planner = WorkflowPlanner()
    groups = planner.plan(template)          # List[ExecutionGroup]
    inputs = planner.resolve_inputs(step, user_input, step_results)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from core.nexus.workflow import StepResult, WorkflowStep, WorkflowTemplate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ExecutionGroup
# ---------------------------------------------------------------------------

@dataclass
class ExecutionGroup:
    """
    A set of WorkflowSteps that can execute in parallel.

    The planner groups steps such that all steps in a group have had their
    dependencies satisfied by previous groups.
    """
    steps: List[WorkflowStep] = field(default_factory=list)

    def __repr__(self) -> str:
        ids = [s.id for s in self.steps]
        return f"<ExecutionGroup steps={ids}>"


# ---------------------------------------------------------------------------
# WorkflowPlanner
# ---------------------------------------------------------------------------

class WorkflowPlanner:
    """
    Converts a WorkflowTemplate into an ordered list of ExecutionGroups.

    Parallel steps (steps whose all dependencies are in earlier groups) are
    grouped together. The executor runs each group concurrently via asyncio.gather.
    """

    # ---- Public API ----

    def plan(self, template: WorkflowTemplate) -> List[ExecutionGroup]:
        """
        Validate the template and produce an ordered list of ExecutionGroups.

        Args:
            template: A WorkflowTemplate (must be valid).

        Returns:
            Ordered list of ExecutionGroups. Steps within a group are independent
            and may run in parallel. Groups must run sequentially.

        Raises:
            ValueError: If the template has structural problems (delegated to validate()).
        """
        self.validate(template)
        return self._topological_groups(template.steps)

    def validate(self, template: WorkflowTemplate) -> None:
        """
        Validate a WorkflowTemplate.

        Delegates to WorkflowTemplate.validate() which checks:
        - output_step exists
        - all depends_on refs exist
        - no self-dependencies
        - no cycles

        Raises:
            ValueError: On any structural problem.
        """
        template.validate()

    def resolve_inputs(
        self,
        step: WorkflowStep,
        user_input: str,
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """
        Resolve $-prefixed variable references in a step's input_mapping.

        Variable syntax:
          $user_input           → the original user_input string
          $<step_id>.output     → step_results[step_id].result.content

        Args:
            step:         The step whose input_mapping to resolve.
            user_input:   The original query string from the user.
            step_results: Accumulated results from all completed steps.

        Returns:
            Dict with resolved values ready to pass as agent input data.

        Raises:
            ValueError: If a $-reference cannot be resolved.
        """
        resolved: Dict[str, Any] = {}
        for key, ref in step.input_mapping.items():
            resolved[key] = self._resolve_ref(ref, user_input, step_results)
        # Always include the original query as a fallback
        if "query" not in resolved:
            resolved["query"] = user_input
        return resolved

    # ---- Internal ----

    def _resolve_ref(
        self,
        ref: str,
        user_input: str,
        step_results: Dict[str, StepResult],
    ) -> Any:
        """Resolve a single variable reference."""
        if not ref.startswith("$"):
            # Literal value — pass through
            return ref

        var = ref[1:]  # strip leading $

        if var == "user_input":
            return user_input

        # $<step_id>.output
        if "." in var:
            step_id, attr = var.split(".", 1)
            if step_id not in step_results:
                raise ValueError(
                    f"Cannot resolve '{ref}': step '{step_id}' has no result yet. "
                    f"Available: {sorted(step_results.keys())}"
                )
            sr = step_results[step_id]
            if attr == "output":
                return sr.result.content
            raise ValueError(
                f"Cannot resolve '{ref}': unknown attribute '{attr}' "
                f"(only '.output' is supported)"
            )

        raise ValueError(
            f"Cannot resolve '{ref}': unrecognised variable syntax. "
            f"Use '$user_input' or '$<step_id>.output'."
        )

    def _topological_groups(
        self, steps: List[WorkflowStep]
    ) -> List[ExecutionGroup]:
        """
        Kahn's algorithm adapted to produce parallel execution groups.

        Steps with in-degree 0 (no pending deps) go into the current group.
        After processing a group, reduce in-degrees of successors; repeat.

        Returns:
            List of ExecutionGroups in execution order.
        """
        # Build adjacency and in-degree maps
        step_map: Dict[str, WorkflowStep] = {s.id: s for s in steps}
        in_degree: Dict[str, int] = {s.id: 0 for s in steps}
        adjacency: Dict[str, List[str]] = {s.id: [] for s in steps}

        for step in steps:
            for dep in step.depends_on:
                adjacency[dep].append(step.id)
                in_degree[step.id] += 1

        groups: List[ExecutionGroup] = []
        ready: Set[str] = {sid for sid, deg in in_degree.items() if deg == 0}

        while ready:
            group_steps = [step_map[sid] for sid in sorted(ready)]
            groups.append(ExecutionGroup(steps=group_steps))

            next_ready: Set[str] = set()
            for step in group_steps:
                for successor in adjacency[step.id]:
                    in_degree[successor] -= 1
                    if in_degree[successor] == 0:
                        next_ready.add(successor)
            ready = next_ready

        logger.debug(
            f"WorkflowPlanner: {len(steps)} steps → {len(groups)} execution groups"
        )
        return groups

    def __repr__(self) -> str:
        return "<WorkflowPlanner>"
