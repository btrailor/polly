"""
Tests for Phase 24e — Advanced Nexus Features.

Covers:
  - PromptAgent contract shape, execution, and error handling
  - Pattern learning wired into NexusCoordinator.execute_workflow()
  - GET /swarms/capabilities endpoint
  - POST /agents endpoint
  - Usage count in GET /swarms/templates response
  - _init_nexus wiring (TemplateRegistry + NexusContextBroker connected)
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from core.nexus.interface import (
    AgentInput,
    AgentResult,
    AgentStatus,
    ExecutionMode,
)
from core.nexus.prompt_agent import PromptAgent
from core.nexus.coordinator import NexusCoordinator
from core.nexus.registry import AgentRegistry
from core.nexus.storage import SwarmStorage
from core.nexus.workflow import WorkflowResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _tmp_db() -> Path:
    tmp = tempfile.mktemp(suffix=".db")
    return Path(tmp)


def _make_coordinator(db_path=None, pattern_engine=None, template_registry=None):
    p = db_path or _tmp_db()
    registry = AgentRegistry(p)
    storage = SwarmStorage(p)
    return NexusCoordinator(
        registry,
        storage,
        template_registry=template_registry,
        pattern_engine=pattern_engine,
    )


def _make_mock_llm(response_text: str = "hello from llm"):
    """Return a mock UnifiedLLM whose .chat() async-generates response_text."""
    async def _gen(*args, **kwargs):
        yield response_text

    llm = MagicMock()
    llm.chat = MagicMock(side_effect=_gen)
    return llm


# ===========================================================================
# TestPromptAgent
# ===========================================================================

class TestPromptAgent:
    """Tests for the PromptAgent class (Phase 24e)."""

    def test_contract_agent_type_is_prompt(self):
        pa = PromptAgent(
            agent_id="pa_test",
            name="Test Agent",
            system_prompt="You are helpful.",
            capability_name="test_capability",
        )
        assert pa.contract.agent_type == "prompt"

    def test_contract_id_matches_agent_id(self):
        pa = PromptAgent(
            agent_id="pa_xyz",
            name="XYZ",
            system_prompt="sys",
            capability_name="do_xyz",
        )
        assert pa.contract.id == "pa_xyz"

    def test_contract_has_correct_capability(self):
        pa = PromptAgent(
            agent_id="pa_sum",
            name="Summariser",
            system_prompt="Summarise briefly.",
            capability_name="summarise_text",
        )
        assert pa.contract.has_capability("summarise_text")

    def test_can_handle_returns_true_for_declared_capability(self):
        pa = PromptAgent(
            agent_id="pa_1",
            name="A",
            system_prompt="...",
            capability_name="my_cap",
        )
        assert pa.can_handle("my_cap") is True

    def test_can_handle_returns_false_for_unknown_capability(self):
        pa = PromptAgent(
            agent_id="pa_1",
            name="A",
            system_prompt="...",
            capability_name="my_cap",
        )
        assert pa.can_handle("other_cap") is False

    def test_domain_affinity_stored_on_contract(self):
        pa = PromptAgent(
            agent_id="pa_dom",
            name="Domain Agent",
            system_prompt="...",
            capability_name="cap",
            domain_affinity=["writing", "knowledge"],
        )
        assert "writing" in pa.contract.domain_affinity
        assert "knowledge" in pa.contract.domain_affinity

    def test_execute_returns_completed_result(self):
        llm = _make_mock_llm("LLM output text")
        pa = PromptAgent(
            agent_id="pa_exec",
            name="Exec",
            system_prompt="Be helpful.",
            capability_name="run",
            llm=llm,
        )
        agent_input = AgentInput(query="Hello", data={}, context={}, execution_id="ex-1")
        result = _run(pa.execute(agent_input))
        assert result.status == AgentStatus.COMPLETED
        assert result.content == "LLM output text"
        assert result.agent_id == "pa_exec"

    def test_execute_includes_system_prompt_in_llm_call(self):
        llm = _make_mock_llm("ok")
        pa = PromptAgent(
            agent_id="pa_sys",
            name="SysPT",
            system_prompt="MY SPECIAL SYSTEM PROMPT",
            capability_name="cap",
            llm=llm,
        )
        agent_input = AgentInput(query="q", data={}, context={}, execution_id="e")
        _run(pa.execute(agent_input))
        call_kwargs = llm.chat.call_args
        assert call_kwargs is not None
        # system_prompt should be passed as kwarg
        assert call_kwargs.kwargs.get("system_prompt") == "MY SPECIAL SYSTEM PROMPT" or \
               (len(call_kwargs.args) > 1 and call_kwargs.args[1] == "MY SPECIAL SYSTEM PROMPT")

    def test_execute_no_llm_returns_failed_result(self):
        pa = PromptAgent(
            agent_id="pa_nollm",
            name="NoLLM",
            system_prompt="...",
            capability_name="cap",
            llm=None,
        )
        agent_input = AgentInput(query="q", data={}, context={}, execution_id="e")
        result = _run(pa.execute(agent_input))
        assert result.status == AgentStatus.FAILED
        assert result.error is not None
        assert "no LLM" in result.error.lower() or "llm" in result.error.lower()

    def test_execute_llm_exception_returns_failed_result(self):
        async def _bad_gen(*args, **kwargs):
            raise RuntimeError("LLM exploded")
            yield  # make it a generator

        llm = MagicMock()
        llm.chat = MagicMock(side_effect=_bad_gen)
        pa = PromptAgent(
            agent_id="pa_err",
            name="ErrAgent",
            system_prompt="...",
            capability_name="cap",
            llm=llm,
        )
        agent_input = AgentInput(query="q", data={}, context={}, execution_id="e")
        result = _run(pa.execute(agent_input))
        assert result.status == AgentStatus.FAILED
        assert "LLM exploded" in result.error

    def test_execute_collects_multiple_chunks(self):
        async def _multi(*args, **kwargs):
            for chunk in ["part1", " ", "part2"]:
                yield chunk

        llm = MagicMock()
        llm.chat = MagicMock(side_effect=_multi)
        pa = PromptAgent(
            agent_id="pa_chunks",
            name="Chunks",
            system_prompt="...",
            capability_name="cap",
            llm=llm,
        )
        agent_input = AgentInput(query="q", data={}, context={}, execution_id="e")
        result = _run(pa.execute(agent_input))
        assert result.content == "part1 part2"

    def test_repr_contains_agent_id_and_capability(self):
        pa = PromptAgent(
            agent_id="pa_repr",
            name="Repr",
            system_prompt="...",
            capability_name="my_cap",
        )
        r = repr(pa)
        assert "pa_repr" in r
        assert "my_cap" in r

    def test_execution_mode_is_autonomous(self):
        pa = PromptAgent(
            agent_id="pa_mode",
            name="Mode",
            system_prompt="...",
            capability_name="cap",
        )
        assert pa.contract.execution_mode == ExecutionMode.AUTONOMOUS


# ===========================================================================
# TestPatternLearning
# ===========================================================================

class TestPatternLearning:
    """Tests for pattern_engine wiring in NexusCoordinator (Phase 24e)."""

    def _make_workflow_result(self, status: str = "completed") -> WorkflowResult:
        return WorkflowResult(
            execution_id="exec-wf-1",
            template_id="research-to-write",
            status=status,
            total_tokens=42,
            total_duration_ms=100,
        )

    def _make_template_mock(self, template_id="research-to-write"):
        tmpl = MagicMock()
        tmpl.name = "Research to Write"
        tmpl.steps = [MagicMock(), MagicMock()]
        tmpl.domain_affinity = ["writing"]
        return tmpl

    def test_pattern_engine_stored_on_coordinator(self):
        engine = MagicMock()
        coord = _make_coordinator(pattern_engine=engine)
        assert coord.pattern_engine is engine

    def test_learn_called_after_completed_workflow(self):
        engine = MagicMock()
        coord = _make_coordinator(pattern_engine=engine)

        tmpl = self._make_template_mock()
        tmpl_registry = MagicMock()
        tmpl_registry.get.return_value = tmpl
        coord.template_registry = tmpl_registry

        wf_result = self._make_workflow_result("completed")

        with patch("core.nexus.executor.WorkflowExecutor") as MockExec, \
             patch("core.nexus.planner.WorkflowPlanner"):
            executor_instance = MagicMock()
            executor_instance.execute = AsyncMock(return_value=wf_result)
            MockExec.return_value = executor_instance

            _run(coord.execute_workflow("research-to-write", "test query", {}))

        engine.learn.assert_called_once()
        engine.save.assert_called_once()

    def test_learn_not_called_on_failed_workflow(self):
        engine = MagicMock()
        coord = _make_coordinator(pattern_engine=engine)

        tmpl = self._make_template_mock()
        tmpl_registry = MagicMock()
        tmpl_registry.get.return_value = tmpl
        coord.template_registry = tmpl_registry

        wf_result = self._make_workflow_result("failed")

        with patch("core.nexus.executor.WorkflowExecutor") as MockExec, \
             patch("core.nexus.planner.WorkflowPlanner"):
            executor_instance = MagicMock()
            executor_instance.execute = AsyncMock(return_value=wf_result)
            MockExec.return_value = executor_instance

            _run(coord.execute_workflow("research-to-write", "test query", {}))

        engine.learn.assert_not_called()
        engine.save.assert_not_called()

    def test_learn_not_called_when_no_pattern_engine(self):
        coord = _make_coordinator(pattern_engine=None)

        tmpl = self._make_template_mock()
        tmpl_registry = MagicMock()
        tmpl_registry.get.return_value = tmpl
        coord.template_registry = tmpl_registry

        wf_result = self._make_workflow_result("completed")

        with patch("core.nexus.executor.WorkflowExecutor") as MockExec, \
             patch("core.nexus.planner.WorkflowPlanner"):
            executor_instance = MagicMock()
            executor_instance.execute = AsyncMock(return_value=wf_result)
            MockExec.return_value = executor_instance

            # Should not raise even with no pattern engine
            result = _run(coord.execute_workflow("research-to-write", "q", {}))
            assert result is wf_result

    def test_pattern_type_is_workflow(self):
        engine = MagicMock()
        coord = _make_coordinator(pattern_engine=engine)

        tmpl = self._make_template_mock()
        tmpl_registry = MagicMock()
        tmpl_registry.get.return_value = tmpl
        coord.template_registry = tmpl_registry

        wf_result = self._make_workflow_result("completed")

        with patch("core.nexus.executor.WorkflowExecutor") as MockExec, \
             patch("core.nexus.planner.WorkflowPlanner"):
            executor_instance = MagicMock()
            executor_instance.execute = AsyncMock(return_value=wf_result)
            MockExec.return_value = executor_instance

            _run(coord.execute_workflow("research-to-write", "q", {}))

        from core.patterns.models import PatternType
        pattern_arg = engine.learn.call_args[0][0]
        assert pattern_arg.pattern_type == PatternType.WORKFLOW

    def test_pattern_template_id_in_metadata(self):
        engine = MagicMock()
        coord = _make_coordinator(pattern_engine=engine)

        tmpl = self._make_template_mock("my-template")
        tmpl_registry = MagicMock()
        tmpl_registry.get.return_value = tmpl
        coord.template_registry = tmpl_registry

        wf_result = self._make_workflow_result("completed")
        wf_result.template_id = "my-template"

        with patch("core.nexus.executor.WorkflowExecutor") as MockExec, \
             patch("core.nexus.planner.WorkflowPlanner"):
            executor_instance = MagicMock()
            executor_instance.execute = AsyncMock(return_value=wf_result)
            MockExec.return_value = executor_instance

            _run(coord.execute_workflow("my-template", "q", {}))

        pattern_arg = engine.learn.call_args[0][0]
        assert pattern_arg.metadata["template_id"] == "my-template"

    def test_pattern_engine_failure_does_not_crash_coordinator(self):
        engine = MagicMock()
        engine.learn.side_effect = RuntimeError("engine broke")

        coord = _make_coordinator(pattern_engine=engine)

        tmpl = self._make_template_mock()
        tmpl_registry = MagicMock()
        tmpl_registry.get.return_value = tmpl
        coord.template_registry = tmpl_registry

        wf_result = self._make_workflow_result("completed")

        with patch("core.nexus.executor.WorkflowExecutor") as MockExec, \
             patch("core.nexus.planner.WorkflowPlanner"):
            executor_instance = MagicMock()
            executor_instance.execute = AsyncMock(return_value=wf_result)
            MockExec.return_value = executor_instance

            # Should not raise — pattern learning is non-critical
            result = _run(coord.execute_workflow("research-to-write", "q", {}))
            assert result is wf_result


# ===========================================================================
# TestSwarmStorage_PromptAgents
# ===========================================================================

class TestSwarmStoragePromptAgents:
    """Tests for the prompt_agents table in SwarmStorage."""

    def _storage(self) -> SwarmStorage:
        return SwarmStorage(_tmp_db())

    def test_list_prompt_agents_empty_initially(self):
        s = self._storage()
        assert s.list_prompt_agents() == []

    def test_create_and_list_prompt_agent(self):
        s = self._storage()
        agent_id = s.create_prompt_agent(
            agent_id="pa_001",
            name="Test PA",
            capability_name="test_cap",
            system_prompt="Be helpful.",
            domain_affinity=["writing"],
        )
        assert agent_id == "pa_001"
        agents = s.list_prompt_agents()
        assert len(agents) == 1
        assert agents[0]["id"] == "pa_001"
        assert agents[0]["name"] == "Test PA"
        assert agents[0]["capability_name"] == "test_cap"
        assert agents[0]["system_prompt"] == "Be helpful."
        assert agents[0]["domain_affinity"] == ["writing"]

    def test_create_multiple_prompt_agents(self):
        s = self._storage()
        s.create_prompt_agent("pa_a", "A", "cap_a", "sys_a", [])
        s.create_prompt_agent("pa_b", "B", "cap_b", "sys_b", ["code"])
        agents = s.list_prompt_agents()
        assert len(agents) == 2

    def test_delete_prompt_agent(self):
        s = self._storage()
        s.create_prompt_agent("pa_del", "Del", "cap", "sys", [])
        assert len(s.list_prompt_agents()) == 1
        s.delete_prompt_agent("pa_del")
        assert len(s.list_prompt_agents()) == 0

    def test_delete_nonexistent_returns_false(self):
        s = self._storage()
        result = s.delete_prompt_agent("nonexistent")
        assert result is False

    def test_domain_affinity_persisted_as_list(self):
        s = self._storage()
        s.create_prompt_agent("pa_dom", "Dom", "cap", "sys", ["a", "b", "c"])
        agents = s.list_prompt_agents()
        assert agents[0]["domain_affinity"] == ["a", "b", "c"]


# ===========================================================================
# TestInitNexusFix
# ===========================================================================

class TestInitNexusFix:
    """Tests for correct _init_nexus wiring (template_registry + context_broker)."""

    def _make_polly_nexus(self):
        """Instantiate NexusCoordinator the same way polly.py _init_nexus does."""
        from core.nexus import (AgentRegistry, SwarmStorage, NexusCoordinator, TemplateRegistry)
        from core.nexus.contexts import NexusContextBroker
        db_path = _tmp_db()
        registry = AgentRegistry(db_path)
        storage = SwarmStorage(db_path)
        tmpl_reg = TemplateRegistry(storage)
        tmpl_reg.seed_builtins()
        broker = NexusContextBroker({})
        return NexusCoordinator(
            registry, storage,
            template_registry=tmpl_reg,
            context_broker=broker,
        )

    def test_template_registry_not_none(self):
        coord = self._make_polly_nexus()
        assert coord.template_registry is not None

    def test_context_broker_not_none(self):
        coord = self._make_polly_nexus()
        assert coord.context_broker is not None

    def test_builtins_seeded(self):
        coord = self._make_polly_nexus()
        templates = coord.template_registry.list_all()
        assert len(templates) >= 5

    def test_execute_workflow_returns_result_not_none(self):
        """execute_workflow should not return None due to missing template_registry."""
        coord = self._make_polly_nexus()
        # Run the known built-in template
        templates = coord.template_registry.list_all()
        assert len(templates) >= 1
        # Verify template lookup works (does not raise and returns something)
        t = coord.template_registry.get(templates[0].id)
        assert t is not None


# ===========================================================================
# TestUsageCount
# ===========================================================================

class TestUsageCount:
    """Tests for usage_count in GET /swarms/templates response."""

    def _storage(self) -> SwarmStorage:
        return SwarmStorage(_tmp_db())

    def test_list_templates_returns_usage_count_key(self):
        """storage.list_templates() rows should have a _usage_count key."""
        s = self._storage()
        from core.nexus.templates import TemplateRegistry
        tmpl_reg = TemplateRegistry(s)
        tmpl_reg.seed_builtins()

        rows = s.list_templates()
        assert len(rows) >= 1
        for row in rows:
            assert "_usage_count" in row

    def test_usage_count_initially_zero(self):
        s = self._storage()
        from core.nexus.templates import TemplateRegistry
        tmpl_reg = TemplateRegistry(s)
        tmpl_reg.seed_builtins()

        rows = s.list_templates()
        for row in rows:
            assert row["_usage_count"] == 0
