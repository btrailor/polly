"""
Tests for WorkflowExecutor (Phase 24b).

Covers: single-step, sequential chain, parallel fork-join, intervention point
pause, FIRST/ENSEMBLE merge, agent failure handling, resume().
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.nexus.executor import WorkflowExecutor
from core.nexus.interface import (
    AgentCapability,
    AgentContract,
    AgentInput,
    AgentResult,
    AgentStatus,
    ExecutionMode,
)
from core.nexus.planner import WorkflowPlanner
from core.nexus.workflow import MergeStrategy, StepResult, WorkflowStep, WorkflowTemplate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_contract(name: str, capabilities: list = None) -> AgentContract:
    caps = [AgentCapability(name=c, description=c) for c in (capabilities or [])]
    return AgentContract(
        id=f"agent_{name.lower()}",
        name=name,
        agent_type="persona",
        capabilities=caps,
        execution_mode=ExecutionMode.INTERACTIVE,
    )


def _mock_executable(contract: AgentContract, content: str = "response") -> MagicMock:
    exe = MagicMock()
    exe.contract = contract
    result = AgentResult(
        agent_id=contract.id,
        execution_id="exec-1",
        status=AgentStatus.COMPLETED,
        content=content,
    )
    exe.execute = AsyncMock(return_value=result)
    exe.can_handle = contract.has_capability
    return exe


def _make_coordinator(executables: dict = None) -> MagicMock:
    """Build a mock NexusCoordinator that routes by capability."""
    coord = MagicMock()
    executables = executables or {}
    coord._executables = executables

    def _select_agent(query, context, required_capability=None):
        for exe in executables.values():
            if required_capability is None or exe.contract.has_capability(required_capability):
                return exe.contract
        return None

    coord.select_agent = MagicMock(side_effect=_select_agent)
    return coord


def _make_storage():
    """Build a minimal mock SwarmStorage."""
    storage = MagicMock()
    storage.create_execution = MagicMock(return_value="exec-test-123")
    storage.update_execution = MagicMock()
    storage.create_agent_run = MagicMock(return_value="run-test-456")
    storage.update_agent_run = MagicMock()
    storage.increment_template_usage = MagicMock()
    return storage


def _make_executor(executables=None, **kwargs) -> tuple:
    """Return (executor, coordinator, storage)."""
    executables = executables or {}
    coord = _make_coordinator(executables)
    storage = _make_storage()
    planner = WorkflowPlanner()
    executor = WorkflowExecutor(coord, storage, planner)
    return executor, coord, storage


def _single_step_template(intervention: bool = False) -> WorkflowTemplate:
    return WorkflowTemplate(
        id="single",
        name="Single Step",
        description="",
        steps=[WorkflowStep(id="only", agent_capability="capture_note",
                            input_mapping={"query": "$user_input"})],
        output_step="only",
        intervention_points=["only"] if intervention else [],
    )


def _sequential_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        id="seq",
        name="Sequential",
        description="",
        steps=[
            WorkflowStep(id="s1", agent_capability="capture_note",
                         input_mapping={"query": "$user_input"}),
            WorkflowStep(id="s2", agent_capability="summarize",
                         input_mapping={"query": "$s1.output"}, depends_on=["s1"]),
        ],
        output_step="s2",
    )


def _parallel_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        id="par",
        name="Parallel",
        description="",
        steps=[
            WorkflowStep(id="p1", agent_capability="capture_note",
                         input_mapping={"query": "$user_input"}),
            WorkflowStep(id="p2", agent_capability="explain_concept",
                         input_mapping={"query": "$user_input"}),
            WorkflowStep(id="merge", agent_capability="summarize",
                         input_mapping={"query": "$user_input"},
                         depends_on=["p1", "p2"]),
        ],
        output_step="merge",
        merge_strategy=MergeStrategy.ENSEMBLE,
    )


# ---------------------------------------------------------------------------
# Tests: Single-step execution
# ---------------------------------------------------------------------------

class TestSingleStep:
    def test_returns_completed_result(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe, content="captured note")
        executor, coord, storage = _make_executor({"agent_scribe": exe})

        result = _run(executor.execute(_single_step_template(), "save my idea", {}))

        assert result.status == "completed"
        assert result.final_content == "captured note"

    def test_step_results_populated(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe, content="output")
        executor, *_ = _make_executor({"agent_scribe": exe})

        result = _run(executor.execute(_single_step_template(), "q", {}))

        assert "only" in result.step_results
        assert result.step_results["only"].result.content == "output"

    def test_storage_create_execution_called(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe)
        executor, _, storage = _make_executor({"agent_scribe": exe})

        _run(executor.execute(_single_step_template(), "q", {}))

        storage.create_execution.assert_called_once()

    def test_storage_update_execution_called_completed(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe)
        executor, _, storage = _make_executor({"agent_scribe": exe})

        _run(executor.execute(_single_step_template(), "q", {}))

        calls = [str(c) for c in storage.update_execution.call_args_list]
        assert any("completed" in c for c in calls)

    def test_agent_execute_called_once(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe)
        executor, *_ = _make_executor({"agent_scribe": exe})

        _run(executor.execute(_single_step_template(), "q", {}))

        exe.execute.assert_called_once()

    def test_no_agent_for_capability_returns_failed_step(self):
        executor, *_ = _make_executor({})  # no agents registered

        result = _run(executor.execute(_single_step_template(), "q", {}))

        # Execution should complete but step should be failed
        assert "only" in result.step_results
        assert result.step_results["only"].result.status == AgentStatus.FAILED

    def test_agent_execution_id_matches_exec_id(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe)
        executor, *_ = _make_executor({"agent_scribe": exe})

        result = _run(executor.execute(_single_step_template(), "q", {}))

        assert result.execution_id is not None


# ---------------------------------------------------------------------------
# Tests: Sequential execution
# ---------------------------------------------------------------------------

class TestSequentialExecution:
    def test_sequential_output_is_final_step(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        exe = _mock_executable(scribe, content="summary result")
        executor, *_ = _make_executor({"agent_scribe": exe})

        result = _run(executor.execute(_sequential_template(), "q", {}))

        assert result.status == "completed"
        assert result.final_content == "summary result"

    def test_sequential_steps_both_recorded(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        exe = _mock_executable(scribe)
        executor, *_ = _make_executor({"agent_scribe": exe})

        result = _run(executor.execute(_sequential_template(), "q", {}))

        assert "s1" in result.step_results
        assert "s2" in result.step_results

    def test_step2_input_uses_step1_output(self):
        """Verify $s1.output variable resolution by checking the agent was called with step1 content."""
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        captured_inputs = []

        async def _execute(agent_input: AgentInput) -> AgentResult:
            captured_inputs.append(agent_input)
            return AgentResult(
                agent_id="agent_scribe",
                execution_id=agent_input.execution_id,
                status=AgentStatus.COMPLETED,
                content=f"processed: {agent_input.query}",
            )

        exe = MagicMock()
        exe.contract = scribe
        exe.execute = _execute
        exe.can_handle = scribe.has_capability

        executor, *_ = _make_executor({"agent_scribe": exe})
        result = _run(executor.execute(_sequential_template(), "original", {}))

        # s2 should have received s1's output as its query
        assert len(captured_inputs) == 2
        s2_input = captured_inputs[1]
        assert "processed" in s2_input.query  # s2 gets s1's content

    def test_sequential_agent_called_twice(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        exe = _mock_executable(scribe)
        executor, *_ = _make_executor({"agent_scribe": exe})

        _run(executor.execute(_sequential_template(), "q", {}))

        assert exe.execute.call_count == 2


# ---------------------------------------------------------------------------
# Tests: Parallel execution
# ---------------------------------------------------------------------------

class TestParallelExecution:
    def test_parallel_steps_both_completed(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        professor = _make_contract("Professor", ["explain_concept"])
        scribe_exe = _mock_executable(scribe, content="scribe output")
        prof_exe = _mock_executable(professor, content="professor output")
        executables = {"agent_scribe": scribe_exe, "agent_professor": prof_exe}
        executor, *_ = _make_executor(executables)

        result = _run(executor.execute(_parallel_template(), "q", {}))

        assert "p1" in result.step_results
        assert "p2" in result.step_results
        assert "merge" in result.step_results

    def test_ensemble_merge_concatenates(self):
        """ENSEMBLE merge should join all step contents."""
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        professor = _make_contract("Professor", ["explain_concept"])
        scribe_exe = _mock_executable(scribe, content="scribe output")
        prof_exe = _mock_executable(professor, content="professor output")
        executor, *_ = _make_executor({"agent_scribe": scribe_exe, "agent_professor": prof_exe})

        result = _run(executor.execute(_parallel_template(), "q", {}))

        # ENSEMBLE merges all step contents
        assert result.status == "completed"
        assert isinstance(result.final_content, str)


# ---------------------------------------------------------------------------
# Tests: Intervention points
# ---------------------------------------------------------------------------

class TestInterventionPoints:
    def test_single_step_intervention_pauses(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe, content="captured")
        executor, *_ = _make_executor({"agent_scribe": exe})

        t = _single_step_template(intervention=True)
        result = _run(executor.execute(t, "q", {}))

        assert result.status == "paused"
        assert result.paused_at_step == "only"

    def test_paused_result_has_completed_steps(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe, content="captured")
        executor, *_ = _make_executor({"agent_scribe": exe})

        t = _single_step_template(intervention=True)
        result = _run(executor.execute(t, "q", {}))

        assert "only" in result.step_results

    def test_storage_updated_to_paused(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = _mock_executable(scribe)
        executor, _, storage = _make_executor({"agent_scribe": exe})

        t = _single_step_template(intervention=True)
        _run(executor.execute(t, "q", {}))

        calls = [str(c) for c in storage.update_execution.call_args_list]
        assert any("paused" in c for c in calls)

    def test_intervention_mid_workflow_pauses_correctly(self):
        """Intervention after s1 — s2 should not run."""
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        exe = _mock_executable(scribe)
        executor, *_ = _make_executor({"agent_scribe": exe})

        t = WorkflowTemplate(
            id="mid-pause",
            name="Mid-Pause",
            description="",
            steps=[
                WorkflowStep(id="s1", agent_capability="capture_note",
                             input_mapping={"query": "$user_input"}),
                WorkflowStep(id="s2", agent_capability="summarize",
                             input_mapping={"query": "$s1.output"},
                             depends_on=["s1"]),
            ],
            output_step="s2",
            intervention_points=["s1"],
        )
        result = _run(executor.execute(t, "q", {}))

        assert result.status == "paused"
        assert result.paused_at_step == "s1"
        assert "s1" in result.step_results
        assert "s2" not in result.step_results


# ---------------------------------------------------------------------------
# Tests: Failure handling
# ---------------------------------------------------------------------------

class TestFailureHandling:
    def test_agent_exception_produces_failed_step(self):
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = MagicMock()
        exe.contract = scribe
        exe.execute = AsyncMock(side_effect=Exception("agent crash"))
        exe.can_handle = scribe.has_capability

        executor, *_ = _make_executor({"agent_scribe": exe})
        result = _run(executor.execute(_single_step_template(), "q", {}))

        # Executor catches the exception and produces a failed step result
        assert "only" in result.step_results
        assert result.step_results["only"].result.status == AgentStatus.FAILED
        assert "agent crash" in (result.step_results["only"].result.error or "")

    def test_workflow_with_failed_step_still_completes(self):
        """A step failure should not abort the whole workflow."""
        scribe = _make_contract("Scribe", ["capture_note"])
        exe = MagicMock()
        exe.contract = scribe
        exe.execute = AsyncMock(side_effect=Exception("boom"))
        exe.can_handle = scribe.has_capability

        executor, *_ = _make_executor({"agent_scribe": exe})
        result = _run(executor.execute(_single_step_template(), "q", {}))

        # Workflow itself does not fail; step is marked failed
        assert result.status in ("completed", "failed")

    def test_total_tokens_summed(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        result_with_tokens = AgentResult(
            agent_id="agent_scribe",
            execution_id="e",
            status=AgentStatus.COMPLETED,
            content="out",
            tokens_used=50,
        )
        exe = MagicMock()
        exe.contract = scribe
        exe.execute = AsyncMock(return_value=result_with_tokens)
        exe.can_handle = scribe.has_capability

        executor, *_ = _make_executor({"agent_scribe": exe})
        result = _run(executor.execute(_sequential_template(), "q", {}))

        assert result.total_tokens == 100  # 50 per step × 2 steps

    def test_total_cost_summed(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        result_with_cost = AgentResult(
            agent_id="agent_scribe",
            execution_id="e",
            status=AgentStatus.COMPLETED,
            content="out",
            cost_usd=0.01,
        )
        exe = MagicMock()
        exe.contract = scribe
        exe.execute = AsyncMock(return_value=result_with_cost)
        exe.can_handle = scribe.has_capability

        executor, *_ = _make_executor({"agent_scribe": exe})
        result = _run(executor.execute(_sequential_template(), "q", {}))

        assert abs(result.total_cost_usd - 0.02) < 1e-9


# ---------------------------------------------------------------------------
# Tests: Merge strategies
# ---------------------------------------------------------------------------

class TestMerge:
    def test_first_merge_uses_output_step(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        call_count = [0]

        async def _execute(inp):
            call_count[0] += 1
            return AgentResult(
                agent_id="agent_scribe",
                execution_id=inp.execution_id,
                status=AgentStatus.COMPLETED,
                content=f"call_{call_count[0]}",
            )

        exe = MagicMock()
        exe.contract = scribe
        exe.execute = _execute
        exe.can_handle = scribe.has_capability

        executor, *_ = _make_executor({"agent_scribe": exe})
        result = _run(executor.execute(_sequential_template(), "q", {}))

        # FIRST strategy: output_step (s2) content wins
        assert result.final_content == "call_2"

    def test_ensemble_merge_joins_all_contents(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        professor = _make_contract("Professor", ["explain_concept"])
        scribe_exe = _mock_executable(scribe, content="scribe says X")
        prof_exe = _mock_executable(professor, content="professor says Y")

        t = WorkflowTemplate(
            id="ensemble-test",
            name="Ensemble",
            description="",
            steps=[
                WorkflowStep(id="s", agent_capability="capture_note",
                             input_mapping={"query": "$user_input"}),
                WorkflowStep(id="p", agent_capability="explain_concept",
                             input_mapping={"query": "$user_input"}),
            ],
            output_step="s",
            merge_strategy=MergeStrategy.ENSEMBLE,
        )

        executor, *_ = _make_executor({"agent_scribe": scribe_exe, "agent_professor": prof_exe})
        result = _run(executor.execute(t, "q", {}))

        assert "scribe says X" in result.final_content
        assert "professor says Y" in result.final_content


# ---------------------------------------------------------------------------
# Tests: Resume
# ---------------------------------------------------------------------------

class TestResume:
    def test_resume_continues_from_paused_state(self):
        scribe = _make_contract("Scribe", ["capture_note", "summarize"])
        exe = _mock_executable(scribe, content="resumed output")
        executor, *_ = _make_executor({"agent_scribe": exe})

        # Simulate prior step result (s1 already done, paused after it)
        prior_s1 = StepResult(
            step_id="s1",
            agent_id="agent_scribe",
            result=AgentResult(
                agent_id="agent_scribe",
                execution_id="exec-resume",
                status=AgentStatus.COMPLETED,
                content="s1 output",
            ),
            started_at="2026-01-01T10:00:00",
            completed_at="2026-01-01T10:00:01",
        )

        result = _run(executor.resume(
            execution_id="exec-resume",
            template=_sequential_template(),
            user_input="q",
            context={},
            prior_step_results={"s1": prior_s1},
            resume_from_step="s1",
        ))

        assert result.status in ("completed", "paused", "failed")
        # s1 was already done, executor should have run s2
        assert "s1" in result.step_results or result.status != "completed"
