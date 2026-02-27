"""
Tests for WorkflowPlanner (Phase 24b).

Covers: topological sort, parallel grouping, input variable resolution,
validation delegation, and edge cases.
"""

from __future__ import annotations

import pytest

from core.nexus.interface import AgentResult, AgentStatus
from core.nexus.planner import ExecutionGroup, WorkflowPlanner
from core.nexus.workflow import StepResult, WorkflowStep, WorkflowTemplate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _planner() -> WorkflowPlanner:
    return WorkflowPlanner()


def _make_result(step_id: str, content: str = "output") -> StepResult:
    return StepResult(
        step_id=step_id,
        agent_id="agent_scribe",
        result=AgentResult(
            agent_id="agent_scribe",
            execution_id="exec-1",
            status=AgentStatus.COMPLETED,
            content=content,
        ),
        started_at="2026-01-01T10:00:00",
        completed_at="2026-01-01T10:00:01",
    )


def _linear_template(n: int = 3) -> WorkflowTemplate:
    """Create a strictly sequential n-step template."""
    steps = []
    for i in range(n):
        steps.append(WorkflowStep(
            id=f"step{i}",
            agent_capability="capture_note",
            input_mapping={"query": "$user_input" if i == 0 else f"$step{i-1}.output"},
            depends_on=[] if i == 0 else [f"step{i-1}"],
        ))
    return WorkflowTemplate(
        id="linear",
        name="Linear",
        description="",
        steps=steps,
        output_step=f"step{n-1}",
    )


def _parallel_template() -> WorkflowTemplate:
    """Two parallel steps then a merge step."""
    return WorkflowTemplate(
        id="parallel",
        name="Parallel",
        description="",
        steps=[
            WorkflowStep(id="a", agent_capability="capture_note", input_mapping={"query": "$user_input"}),
            WorkflowStep(id="b", agent_capability="explain_concept", input_mapping={"query": "$user_input"}),
            WorkflowStep(id="merge", agent_capability="summarize",
                         input_mapping={"query": "$user_input"},
                         depends_on=["a", "b"]),
        ],
        output_step="merge",
    )


# ---------------------------------------------------------------------------
# Tests: plan() / topological grouping
# ---------------------------------------------------------------------------

class TestPlan:
    def test_single_step_produces_one_group(self):
        p = _planner()
        t = WorkflowTemplate(
            id="one",
            name="One",
            description="",
            steps=[WorkflowStep(id="only", agent_capability="cap")],
            output_step="only",
        )
        groups = p.plan(t)
        assert len(groups) == 1
        assert len(groups[0].steps) == 1
        assert groups[0].steps[0].id == "only"

    def test_linear_template_produces_sequential_groups(self):
        p = _planner()
        t = _linear_template(3)
        groups = p.plan(t)
        assert len(groups) == 3
        for i, group in enumerate(groups):
            assert len(group.steps) == 1
            assert group.steps[0].id == f"step{i}"

    def test_parallel_steps_in_same_group(self):
        p = _planner()
        t = _parallel_template()
        groups = p.plan(t)
        # Group 0: a + b (parallel), Group 1: merge
        assert len(groups) == 2
        group0_ids = {s.id for s in groups[0].steps}
        assert "a" in group0_ids
        assert "b" in group0_ids
        assert groups[1].steps[0].id == "merge"

    def test_fork_join_dag(self):
        """A → B and A → C, then D depends on B + C."""
        p = _planner()
        t = WorkflowTemplate(
            id="fork-join",
            name="Fork-Join",
            description="",
            steps=[
                WorkflowStep(id="A", agent_capability="c"),
                WorkflowStep(id="B", agent_capability="c", depends_on=["A"]),
                WorkflowStep(id="C", agent_capability="c", depends_on=["A"]),
                WorkflowStep(id="D", agent_capability="c", depends_on=["B", "C"]),
            ],
            output_step="D",
        )
        groups = p.plan(t)
        assert len(groups) == 3
        assert groups[0].steps[0].id == "A"
        group1_ids = {s.id for s in groups[1].steps}
        assert "B" in group1_ids
        assert "C" in group1_ids
        assert groups[2].steps[0].id == "D"

    def test_plan_validates_before_sorting(self):
        p = _planner()
        t = WorkflowTemplate(
            id="cyclic",
            name="Cyclic",
            description="",
            steps=[
                WorkflowStep(id="a", agent_capability="c", depends_on=["b"]),
                WorkflowStep(id="b", agent_capability="c", depends_on=["a"]),
            ],
            output_step="a",
        )
        with pytest.raises(ValueError, match="cycle"):
            p.plan(t)

    def test_independent_steps_grouped_together(self):
        """All steps independent → single group."""
        p = _planner()
        t = WorkflowTemplate(
            id="all-parallel",
            name="All Parallel",
            description="",
            steps=[
                WorkflowStep(id="x", agent_capability="c"),
                WorkflowStep(id="y", agent_capability="c"),
                WorkflowStep(id="z", agent_capability="c"),
            ],
            output_step="x",
        )
        groups = p.plan(t)
        assert len(groups) == 1
        assert len(groups[0].steps) == 3


# ---------------------------------------------------------------------------
# Tests: resolve_inputs()
# ---------------------------------------------------------------------------

class TestResolveInputs:
    def test_user_input_resolved(self):
        p = _planner()
        step = WorkflowStep(
            id="s",
            agent_capability="c",
            input_mapping={"query": "$user_input"},
        )
        result = p.resolve_inputs(step, "hello world", {})
        assert result["query"] == "hello world"

    def test_step_output_resolved(self):
        p = _planner()
        step_results = {"capture": _make_result("capture", content="my note")}
        step = WorkflowStep(
            id="write",
            agent_capability="c",
            input_mapping={"query": "$capture.output"},
        )
        result = p.resolve_inputs(step, "original", step_results)
        assert result["query"] == "my note"

    def test_literal_string_passed_through(self):
        p = _planner()
        step = WorkflowStep(
            id="s",
            agent_capability="c",
            input_mapping={"mode": "capture"},
        )
        result = p.resolve_inputs(step, "q", {})
        assert result["mode"] == "capture"

    def test_missing_step_output_raises(self):
        p = _planner()
        step = WorkflowStep(
            id="write",
            agent_capability="c",
            input_mapping={"query": "$nonexistent.output"},
        )
        with pytest.raises(ValueError, match="nonexistent"):
            p.resolve_inputs(step, "q", {})

    def test_unknown_var_syntax_raises(self):
        p = _planner()
        step = WorkflowStep(
            id="s",
            agent_capability="c",
            input_mapping={"query": "$weirdvar"},
        )
        with pytest.raises(ValueError):
            p.resolve_inputs(step, "q", {})

    def test_unknown_attribute_raises(self):
        p = _planner()
        step_results = {"s1": _make_result("s1", "content")}
        step = WorkflowStep(
            id="s2",
            agent_capability="c",
            input_mapping={"query": "$s1.metadata"},
        )
        with pytest.raises(ValueError, match="metadata"):
            p.resolve_inputs(step, "q", step_results)

    def test_fallback_query_added_when_missing(self):
        p = _planner()
        step = WorkflowStep(id="s", agent_capability="c", input_mapping={})
        result = p.resolve_inputs(step, "original query", {})
        assert result["query"] == "original query"

    def test_multiple_mappings_resolved(self):
        p = _planner()
        step_results = {
            "s1": _make_result("s1", "first output"),
            "s2": _make_result("s2", "second output"),
        }
        step = WorkflowStep(
            id="s3",
            agent_capability="c",
            input_mapping={
                "query": "$user_input",
                "part1": "$s1.output",
                "part2": "$s2.output",
            },
        )
        result = p.resolve_inputs(step, "user q", step_results)
        assert result["query"] == "user q"
        assert result["part1"] == "first output"
        assert result["part2"] == "second output"

    def test_empty_input_mapping_returns_query(self):
        p = _planner()
        step = WorkflowStep(id="s", agent_capability="c")
        result = p.resolve_inputs(step, "my query", {})
        assert result["query"] == "my query"


# ---------------------------------------------------------------------------
# Tests: validate()
# ---------------------------------------------------------------------------

class TestValidate:
    def test_validate_passes_linear(self):
        p = _planner()
        p.validate(_linear_template(3))  # no raise

    def test_validate_passes_parallel(self):
        p = _planner()
        p.validate(_parallel_template())  # no raise

    def test_validate_raises_on_bad_output_step(self):
        p = _planner()
        t = _linear_template(2)
        t.output_step = "ghost"
        with pytest.raises(ValueError):
            p.validate(t)

    def test_validate_raises_on_unknown_dep(self):
        p = _planner()
        t = WorkflowTemplate(
            id="x",
            name="X",
            description="",
            steps=[WorkflowStep(id="a", agent_capability="c", depends_on=["nope"])],
            output_step="a",
        )
        with pytest.raises(ValueError):
            p.validate(t)


# ---------------------------------------------------------------------------
# Tests: ExecutionGroup
# ---------------------------------------------------------------------------

class TestExecutionGroup:
    def test_repr(self):
        steps = [WorkflowStep(id="a", agent_capability="c"),
                 WorkflowStep(id="b", agent_capability="c")]
        g = ExecutionGroup(steps=steps)
        r = repr(g)
        assert "a" in r
        assert "b" in r

    def test_empty_group(self):
        g = ExecutionGroup()
        assert g.steps == []
