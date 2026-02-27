"""
WorkflowExecutor — multi-agent DAG execution engine (Phase 24b).

Orchestrates the execution of a WorkflowTemplate by:
  - Running the planner to get ordered ExecutionGroups
  - Executing independent steps in parallel (asyncio.gather)
  - Executing dependent steps sequentially between groups
  - Pausing at intervention points and allowing resume
  - Merging results according to the template's MergeStrategy
  - Persisting execution state to SwarmStorage throughout

Usage:
    planner = WorkflowPlanner()
    executor = WorkflowExecutor(coordinator, storage, planner)
    result = await executor.execute(template, user_input="...", context={})
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.nexus.interface import AgentInput, AgentResult, AgentStatus
from core.nexus.planner import ExecutionGroup, WorkflowPlanner
from core.nexus.storage import SwarmStorage
from core.nexus.workflow import MergeStrategy, StepResult, WorkflowResult, WorkflowStep, WorkflowTemplate

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Executes a WorkflowTemplate against the registered agents in NexusCoordinator.

    The executor delegates step execution to the coordinator's agent selection
    and execute() path, ensuring storage records are created for every step.

    Args:
        coordinator: NexusCoordinator instance (for agent selection + execution)
        storage:     SwarmStorage (for execution + run record persistence)
        planner:     WorkflowPlanner (for topological sort + input resolution)
    """

    def __init__(
        self,
        coordinator: Any,     # NexusCoordinator (avoid circular import)
        storage: SwarmStorage,
        planner: WorkflowPlanner,
    ) -> None:
        self.coordinator = coordinator
        self.storage = storage
        self.planner = planner

    # ---- Public: Execute ----

    async def execute(
        self,
        template: WorkflowTemplate,
        user_input: str,
        context: Dict[str, Any],
        execution_id: Optional[str] = None,
    ) -> WorkflowResult:
        """
        Execute a workflow template from the beginning.

        Args:
            template:     The WorkflowTemplate to execute.
            user_input:   The user's original query string.
            context:      Arbitrary context dict passed to each agent.
            execution_id: Optional pre-assigned ID (for testing / idempotency).

        Returns:
            WorkflowResult with status "completed", "paused", or "failed".
        """
        self.planner.validate(template)
        groups = self.planner.plan(template)

        exec_id = self.storage.create_execution(
            input_data={"query": user_input, "context": context},
            template_id=template.id,
        )
        self.storage.update_execution(exec_id, "running")

        wall_start = time.monotonic()
        step_results: Dict[str, StepResult] = {}

        try:
            result = await self._run_groups(
                groups=groups,
                template=template,
                user_input=user_input,
                context=context,
                exec_id=exec_id,
                step_results=step_results,
            )
        except _PausedException as pause_exc:
            # Intervention point reached — save state and return paused
            return self._build_paused_result(
                exec_id=exec_id,
                template=template,
                step_results=pause_exc.step_results,
                paused_at_step=pause_exc.step_id,
                wall_start=wall_start,
            )
        except Exception as e:
            logger.error(f"WorkflowExecutor: workflow '{template.id}' failed: {e}")
            self.storage.update_execution(exec_id, "failed", error=str(e))
            return WorkflowResult(
                execution_id=exec_id,
                template_id=template.id,
                status="failed",
                step_results=step_results,
                error=str(e),
                total_duration_ms=int((time.monotonic() - wall_start) * 1000),
            )

        return result

    # ---- Public: Resume ----

    async def resume(
        self,
        execution_id: str,
        template: WorkflowTemplate,
        user_input: str,
        context: Dict[str, Any],
        prior_step_results: Dict[str, StepResult],
        resume_from_step: str,
    ) -> WorkflowResult:
        """
        Resume a paused workflow from after a given step.

        Args:
            execution_id:      The original execution ID (already in storage).
            template:          The same WorkflowTemplate that was paused.
            user_input:        The original query string.
            context:           The original context dict.
            prior_step_results: Step results accumulated before the pause.
            resume_from_step:  The step ID where pausing occurred (completed steps
                               up to and including this one are already in prior_step_results).

        Returns:
            WorkflowResult with status "completed", "paused", or "failed".
        """
        self.planner.validate(template)
        groups = self.planner.plan(template)

        # Find which groups have already completed (all steps in group are in prior_step_results)
        completed_step_ids = set(prior_step_results.keys())
        pending_groups = [
            g for g in groups
            if not all(s.id in completed_step_ids for s in g.steps)
        ]

        self.storage.update_execution(execution_id, "running")
        wall_start = time.monotonic()
        step_results = dict(prior_step_results)

        try:
            result = await self._run_groups(
                groups=pending_groups,
                template=template,
                user_input=user_input,
                context=context,
                exec_id=execution_id,
                step_results=step_results,
            )
        except _PausedException as pause_exc:
            return self._build_paused_result(
                exec_id=execution_id,
                template=template,
                step_results=pause_exc.step_results,
                paused_at_step=pause_exc.step_id,
                wall_start=wall_start,
            )
        except Exception as e:
            logger.error(
                f"WorkflowExecutor: resume of '{template.id}' failed: {e}"
            )
            self.storage.update_execution(execution_id, "failed", error=str(e))
            return WorkflowResult(
                execution_id=execution_id,
                template_id=template.id,
                status="failed",
                step_results=step_results,
                error=str(e),
                total_duration_ms=int((time.monotonic() - wall_start) * 1000),
            )

        return result

    # ---- Internal: Group / Step execution ----

    async def _run_groups(
        self,
        groups: List[ExecutionGroup],
        template: WorkflowTemplate,
        user_input: str,
        context: Dict[str, Any],
        exec_id: str,
        step_results: Dict[str, StepResult],
    ) -> WorkflowResult:
        """Run all execution groups sequentially, parallel steps within each group."""
        wall_start = time.monotonic()

        for group in groups:
            new_results = await self._run_group(
                group=group,
                user_input=user_input,
                context=context,
                step_results=step_results,
                exec_id=exec_id,
            )
            step_results.update(new_results)

            # Check intervention points after each step in the group
            for step in group.steps:
                if step.id in template.intervention_points:
                    # Save partial state and raise pause signal
                    self._save_partial_state(exec_id, template.id, step_results)
                    raise _PausedException(
                        step_id=step.id,
                        step_results=step_results,
                    )

        # All groups completed — build final result
        final_content, final_output = self._merge(step_results, template)
        total_tokens = sum(sr.result.tokens_used for sr in step_results.values())
        total_cost = sum(sr.result.cost_usd for sr in step_results.values())
        total_ms = int((time.monotonic() - wall_start) * 1000)
        agents_used = list({sr.agent_id for sr in step_results.values()})

        self.storage.update_execution(
            exec_id=exec_id,
            status="completed",
            output_data={
                "final_content": final_content,
                "step_results": {k: v.to_dict() for k, v in step_results.items()},
                "agents_used": agents_used,
            },
        )
        if template.id:
            self.storage.increment_template_usage(template.id)

        return WorkflowResult(
            execution_id=exec_id,
            template_id=template.id,
            status="completed",
            step_results=step_results,
            final_content=final_content,
            final_output=final_output,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            total_duration_ms=total_ms,
        )

    async def _run_group(
        self,
        group: ExecutionGroup,
        user_input: str,
        context: Dict[str, Any],
        step_results: Dict[str, StepResult],
        exec_id: str,
    ) -> Dict[str, StepResult]:
        """Execute all steps in a group concurrently using asyncio.gather."""
        tasks = [
            self._run_step(
                step=step,
                user_input=user_input,
                context=context,
                step_results=step_results,
                exec_id=exec_id,
            )
            for step in group.steps
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return {sr.step_id: sr for sr in results}

    async def _run_step(
        self,
        step: WorkflowStep,
        user_input: str,
        context: Dict[str, Any],
        step_results: Dict[str, StepResult],
        exec_id: str,
    ) -> StepResult:
        """
        Execute a single workflow step.

        1. Request execution contexts (if broker configured and step declares contexts)
        2. Fail fast if any required context is denied
        3. Resolve $-prefixed input variables
        4. Select an agent with the required capability
        5. Execute the agent (with context_tokens injected into AgentInput.context)
        6. Store the agent run record
        7. Return a StepResult

        If no agent has the required capability, returns a FAILED StepResult.
        """
        started_at = datetime.now().isoformat()
        step_start = time.monotonic()

        # ---- Context broker ----
        agent_context = dict(context)
        broker = getattr(self.coordinator, "context_broker", None)
        all_declared = list(step.required_contexts) + list(step.optional_contexts)

        if broker is not None and all_declared:
            grants = broker.request_contexts(
                agent_id="workflow_step",
                context_types=all_declared,
                workflow_exec_id=exec_id,
                operations=["read", "write", "query"],
            )

            from core.nexus.contexts import ContextToken

            # Check required contexts — any denial → FAILED step
            for ctx_type in step.required_contexts:
                grant = grants.get(ctx_type)
                if not isinstance(grant, ContextToken):
                    reason = getattr(grant, "reason", "not_granted")
                    logger.warning(
                        f"WorkflowExecutor: step '{step.id}' required context "
                        f"'{ctx_type}' denied: {reason}"
                    )
                    agent_result = AgentResult(
                        agent_id="none",
                        execution_id=exec_id,
                        status=AgentStatus.FAILED,
                        error=f"Required context '{ctx_type}' denied: {reason}",
                    )
                    return StepResult(
                        step_id=step.id,
                        agent_id="none",
                        result=agent_result,
                        started_at=started_at,
                        completed_at=datetime.now().isoformat(),
                    )

            # Collect granted tokens (required + optional that were granted)
            context_tokens = {
                ct: grant.to_dict()
                for ct, grant in grants.items()
                if isinstance(grant, ContextToken)
            }
            if context_tokens:
                agent_context["context_tokens"] = context_tokens

        # Resolve inputs
        try:
            resolved = self.planner.resolve_inputs(step, user_input, step_results)
        except ValueError as e:
            logger.error(
                f"WorkflowExecutor: step '{step.id}' input resolution failed: {e}"
            )
            agent_result = AgentResult(
                agent_id="none",
                execution_id=exec_id,
                status=AgentStatus.FAILED,
                error=str(e),
            )
            return StepResult(
                step_id=step.id,
                agent_id="none",
                result=agent_result,
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )

        # Select agent
        contract = self.coordinator.select_agent(
            query=resolved.get("query", user_input),
            context=context,
            required_capability=step.agent_capability,
        )
        if contract is None:
            logger.warning(
                f"WorkflowExecutor: no agent for capability '{step.agent_capability}'"
            )
            agent_result = AgentResult(
                agent_id="none",
                execution_id=exec_id,
                status=AgentStatus.FAILED,
                error=f"No agent registered for capability '{step.agent_capability}'",
            )
            return StepResult(
                step_id=step.id,
                agent_id="none",
                result=agent_result,
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )

        executable = self.coordinator._executables.get(contract.id)
        agent_input = AgentInput(
            query=resolved.get("query", user_input),
            data=resolved,
            context=agent_context,
            execution_id=exec_id,
        )

        # Create agent run record
        run_id = self.storage.create_agent_run(
            execution_id=exec_id,
            agent_id=contract.id,
            input_data=resolved,
        )

        try:
            agent_result = await executable.execute(agent_input)
            duration_ms = int((time.monotonic() - step_start) * 1000)

            self.storage.update_agent_run(
                run_id=run_id,
                status=agent_result.status.value,
                output_data={"content": agent_result.content, **agent_result.output},
                tokens_used=agent_result.tokens_used,
                cost_usd=agent_result.cost_usd,
                duration_ms=duration_ms,
                error=agent_result.error,
            )

            completed_at = datetime.now().isoformat()
            logger.debug(
                f"WorkflowExecutor: step '{step.id}' → '{contract.id}' "
                f"({agent_result.status.value}, {duration_ms}ms)"
            )
            return StepResult(
                step_id=step.id,
                agent_id=contract.id,
                result=agent_result,
                started_at=started_at,
                completed_at=completed_at,
            )

        except Exception as e:
            logger.error(
                f"WorkflowExecutor: step '{step.id}' agent '{contract.id}' raised: {e}"
            )
            self.storage.update_agent_run(
                run_id=run_id,
                status="failed",
                error=str(e),
            )
            agent_result = AgentResult(
                agent_id=contract.id,
                execution_id=exec_id,
                status=AgentStatus.FAILED,
                error=str(e),
            )
            return StepResult(
                step_id=step.id,
                agent_id=contract.id,
                result=agent_result,
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )

    # ---- Internal: Merge ----

    def _merge(
        self,
        step_results: Dict[str, StepResult],
        template: WorkflowTemplate,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Produce the final (content, output) from accumulated step results.

        FIRST:    Use the output_step's content.
        ENSEMBLE: Concatenate all step contents separated by "---".
        """
        if template.merge_strategy == MergeStrategy.ENSEMBLE:
            parts = []
            for step_id, sr in step_results.items():
                if sr.result.content:
                    parts.append(sr.result.content)
            final_content = "\n\n---\n\n".join(parts) if parts else ""
            return final_content, {"step_contents": {k: v.result.content for k, v in step_results.items()}}

        # Default: FIRST — use output_step
        output_sr = step_results.get(template.output_step)
        if output_sr is not None:
            return output_sr.result.content, output_sr.result.output
        return "", {}

    # ---- Internal: Pause / State ----

    def _save_partial_state(
        self,
        exec_id: str,
        template_id: str,
        step_results: Dict[str, StepResult],
    ) -> None:
        """Persist partial execution state so resume() can reconstruct it."""
        self.storage.update_execution(
            exec_id=exec_id,
            status="paused",
            output_data={
                "step_results": {k: v.to_dict() for k, v in step_results.items()},
                "template_id": template_id,
            },
        )

    def _build_paused_result(
        self,
        exec_id: str,
        template: WorkflowTemplate,
        step_results: Dict[str, StepResult],
        paused_at_step: str,
        wall_start: float,
    ) -> WorkflowResult:
        """Build a WorkflowResult reflecting a paused state."""
        total_tokens = sum(sr.result.tokens_used for sr in step_results.values())
        total_cost = sum(sr.result.cost_usd for sr in step_results.values())
        return WorkflowResult(
            execution_id=exec_id,
            template_id=template.id,
            status="paused",
            step_results=step_results,
            final_content="",
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            total_duration_ms=int((time.monotonic() - wall_start) * 1000),
            paused_at_step=paused_at_step,
        )

    def __repr__(self) -> str:
        return f"<WorkflowExecutor coordinator={self.coordinator}>"


# ---------------------------------------------------------------------------
# Internal pause signal
# ---------------------------------------------------------------------------

class _PausedException(Exception):
    """Internal signal raised when an intervention point is reached."""

    def __init__(self, step_id: str, step_results: Dict[str, StepResult]) -> None:
        super().__init__(f"Paused at step '{step_id}'")
        self.step_id = step_id
        self.step_results = step_results
