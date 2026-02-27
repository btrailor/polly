"""
Tests for Phase 24b workflow types.

Covers: WorkflowStep, WorkflowTemplate, MergeStrategy, StepResult, WorkflowResult
"""

from __future__ import annotations

import pytest

from core.nexus.interface import AgentResult, AgentStatus
from core.nexus.workflow import (
    MergeStrategy,
    StepResult,
    WorkflowResult,
    WorkflowStep,
    WorkflowTemplate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent_result(agent_id="agent_scribe", content="result") -> AgentResult:
    return AgentResult(
        agent_id=agent_id,
        execution_id="exec-1",
        status=AgentStatus.COMPLETED,
        content=content,
    )


def _simple_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        id="test-template",
        name="Test",
        description="A test template",
        steps=[
            WorkflowStep(id="step1", agent_capability="capture_note", input_mapping={"query": "$user_input"}),
            WorkflowStep(id="step2", agent_capability="summarize", input_mapping={"query": "$step1.output"}, depends_on=["step1"]),
        ],
        output_step="step2",
    )


# ---------------------------------------------------------------------------
# Tests: WorkflowStep
# ---------------------------------------------------------------------------

class TestWorkflowStep:
    def test_basic_creation(self):
        step = WorkflowStep(id="capture", agent_capability="capture_note")
        assert step.id == "capture"
        assert step.agent_capability == "capture_note"
        assert step.input_mapping == {}
        assert step.depends_on == []

    def test_with_input_mapping(self):
        step = WorkflowStep(
            id="write",
            agent_capability="summarize",
            input_mapping={"query": "$capture.output"},
            depends_on=["capture"],
        )
        assert step.input_mapping["query"] == "$capture.output"
        assert "capture" in step.depends_on

    def test_to_dict_roundtrip(self):
        step = WorkflowStep(
            id="step1",
            agent_capability="plan_task",
            input_mapping={"query": "$user_input"},
            depends_on=["prev"],
        )
        d = step.to_dict()
        step2 = WorkflowStep.from_dict(d)
        assert step2.id == "step1"
        assert step2.agent_capability == "plan_task"
        assert step2.input_mapping == {"query": "$user_input"}
        assert "prev" in step2.depends_on

    def test_from_dict_minimal(self):
        step = WorkflowStep.from_dict({"id": "x", "agent_capability": "foo"})
        assert step.id == "x"
        assert step.depends_on == []
        assert step.input_mapping == {}

    def test_to_dict_contains_required_keys(self):
        step = WorkflowStep(id="s", agent_capability="c")
        d = step.to_dict()
        for key in ("id", "agent_capability", "input_mapping", "depends_on"):
            assert key in d


# ---------------------------------------------------------------------------
# Tests: MergeStrategy
# ---------------------------------------------------------------------------

class TestMergeStrategy:
    def test_values(self):
        assert MergeStrategy.FIRST == "first"
        assert MergeStrategy.ENSEMBLE == "ensemble"

    def test_from_string(self):
        assert MergeStrategy("first") == MergeStrategy.FIRST
        assert MergeStrategy("ensemble") == MergeStrategy.ENSEMBLE


# ---------------------------------------------------------------------------
# Tests: WorkflowTemplate
# ---------------------------------------------------------------------------

class TestWorkflowTemplate:
    def test_basic_creation(self):
        t = _simple_template()
        assert t.id == "test-template"
        assert len(t.steps) == 2
        assert t.output_step == "step2"
        assert t.is_builtin is False
        assert t.merge_strategy == MergeStrategy.FIRST

    def test_validate_passes_for_valid_template(self):
        t = _simple_template()
        t.validate()  # Should not raise

    def test_validate_raises_on_missing_output_step(self):
        t = _simple_template()
        t.output_step = "nonexistent"
        with pytest.raises(ValueError, match="output_step"):
            t.validate()

    def test_validate_raises_on_unknown_depends_on(self):
        t = WorkflowTemplate(
            id="bad",
            name="Bad",
            description="",
            steps=[
                WorkflowStep(id="step1", agent_capability="cap", depends_on=["ghost"]),
            ],
            output_step="step1",
        )
        with pytest.raises(ValueError, match="ghost"):
            t.validate()

    def test_validate_raises_on_self_dependency(self):
        t = WorkflowTemplate(
            id="self-dep",
            name="X",
            description="",
            steps=[
                WorkflowStep(id="step1", agent_capability="cap", depends_on=["step1"]),
            ],
            output_step="step1",
        )
        with pytest.raises(ValueError):
            t.validate()

    def test_validate_raises_on_cycle(self):
        t = WorkflowTemplate(
            id="cyclic",
            name="Cyclic",
            description="",
            steps=[
                WorkflowStep(id="a", agent_capability="cap", depends_on=["b"]),
                WorkflowStep(id="b", agent_capability="cap", depends_on=["a"]),
            ],
            output_step="a",
        )
        with pytest.raises(ValueError, match="cycle"):
            t.validate()

    def test_validate_three_step_cycle(self):
        t = WorkflowTemplate(
            id="cycle3",
            name="X",
            description="",
            steps=[
                WorkflowStep(id="a", agent_capability="cap", depends_on=["c"]),
                WorkflowStep(id="b", agent_capability="cap", depends_on=["a"]),
                WorkflowStep(id="c", agent_capability="cap", depends_on=["b"]),
            ],
            output_step="a",
        )
        with pytest.raises(ValueError, match="cycle"):
            t.validate()

    def test_to_dict_roundtrip(self):
        t = _simple_template()
        d = t.to_dict()
        t2 = WorkflowTemplate.from_dict(d)
        assert t2.id == t.id
        assert t2.name == t.name
        assert len(t2.steps) == 2
        assert t2.output_step == t.output_step
        assert t2.merge_strategy == MergeStrategy.FIRST

    def test_to_dict_contains_all_fields(self):
        t = _simple_template()
        d = t.to_dict()
        for key in ("id", "name", "description", "steps", "output_step",
                    "intervention_points", "domain_affinity", "merge_strategy", "is_builtin"):
            assert key in d

    def test_from_dict_defaults_merge_strategy(self):
        t = WorkflowTemplate.from_dict({
            "id": "x",
            "name": "X",
            "description": "",
            "steps": [{"id": "s", "agent_capability": "c"}],
            "output_step": "s",
        })
        assert t.merge_strategy == MergeStrategy.FIRST

    def test_ensemble_merge_preserved(self):
        t = _simple_template()
        t.merge_strategy = MergeStrategy.ENSEMBLE
        d = t.to_dict()
        t2 = WorkflowTemplate.from_dict(d)
        assert t2.merge_strategy == MergeStrategy.ENSEMBLE

    def test_repr_contains_id(self):
        t = _simple_template()
        r = repr(t)
        assert "test-template" in r

    def test_single_step_template_valid(self):
        t = WorkflowTemplate(
            id="one-step",
            name="One Step",
            description="",
            steps=[WorkflowStep(id="only", agent_capability="cap")],
            output_step="only",
        )
        t.validate()  # Should not raise

    def test_intervention_points_preserved(self):
        t = _simple_template()
        t.intervention_points = ["step1"]
        d = t.to_dict()
        t2 = WorkflowTemplate.from_dict(d)
        assert "step1" in t2.intervention_points

    def test_domain_affinity_preserved(self):
        t = _simple_template()
        t.domain_affinity = ["writing", "notes"]
        d = t.to_dict()
        t2 = WorkflowTemplate.from_dict(d)
        assert "writing" in t2.domain_affinity
        assert "notes" in t2.domain_affinity


# ---------------------------------------------------------------------------
# Tests: StepResult
# ---------------------------------------------------------------------------

class TestStepResult:
    def test_basic_creation(self):
        sr = StepResult(
            step_id="step1",
            agent_id="agent_scribe",
            result=_make_agent_result(),
            started_at="2026-01-01T10:00:00",
            completed_at="2026-01-01T10:00:01",
        )
        assert sr.step_id == "step1"
        assert sr.agent_id == "agent_scribe"
        assert sr.result.content == "result"

    def test_to_dict_roundtrip(self):
        sr = StepResult(
            step_id="s1",
            agent_id="a1",
            result=_make_agent_result(content="hello"),
            started_at="2026-01-01T10:00:00",
            completed_at="2026-01-01T10:00:01",
        )
        d = sr.to_dict()
        sr2 = StepResult.from_dict(d)
        assert sr2.step_id == "s1"
        assert sr2.agent_id == "a1"
        assert sr2.result.content == "hello"
        assert sr2.result.status == AgentStatus.COMPLETED

    def test_to_dict_contains_required_keys(self):
        sr = StepResult(
            step_id="s", agent_id="a",
            result=_make_agent_result(),
            started_at="t1", completed_at="t2",
        )
        d = sr.to_dict()
        for key in ("step_id", "agent_id", "result", "started_at", "completed_at"):
            assert key in d


# ---------------------------------------------------------------------------
# Tests: WorkflowResult
# ---------------------------------------------------------------------------

class TestWorkflowResult:
    def test_basic_creation(self):
        wr = WorkflowResult(
            execution_id="exec-1",
            template_id="test-template",
            status="completed",
        )
        assert wr.status == "completed"
        assert wr.final_content == ""
        assert wr.step_results == {}
        assert wr.paused_at_step is None

    def test_to_dict_contains_required_keys(self):
        wr = WorkflowResult(
            execution_id="exec-1",
            template_id="tmpl-1",
            status="completed",
            final_content="done",
        )
        d = wr.to_dict()
        for key in ("execution_id", "template_id", "status", "final_content",
                    "total_tokens", "total_cost_usd", "total_duration_ms",
                    "paused_at_step", "error"):
            assert key in d

    def test_paused_result_has_paused_at_step(self):
        wr = WorkflowResult(
            execution_id="e",
            template_id="t",
            status="paused",
            paused_at_step="capture",
        )
        d = wr.to_dict()
        assert d["paused_at_step"] == "capture"
        assert d["status"] == "paused"

    def test_failed_result_has_error(self):
        wr = WorkflowResult(
            execution_id="e",
            template_id="t",
            status="failed",
            error="something broke",
        )
        d = wr.to_dict()
        assert d["error"] == "something broke"

    def test_repr_contains_execution_id(self):
        wr = WorkflowResult(execution_id="exec-42", template_id="t", status="completed")
        assert "exec-42" in repr(wr)
