"""
Tests for PersonaAgent (Phase 24a).

Wraps a mock AgentPersona and verifies contract building, capability
declarations, and execute() behaviour including failure handling.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.nexus.interface import AgentStatus, ExecutionMode
from core.nexus.persona_adapter import (
    PERSONA_CAPABILITY_MAP,
    PERSONA_DOMAIN_MAP,
    PersonaAgent,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _mock_persona(content: str = "response content") -> MagicMock:
    """Build a mock AgentPersona whose process() returns a PersonaResponse-like object."""
    persona = MagicMock()
    persona_response = MagicMock()
    persona_response.content = content
    persona_response.mode = "capture"
    persona_response.actions = []
    persona_response.metadata = {}
    persona.process = AsyncMock(return_value=persona_response)
    return persona


# ---------------------------------------------------------------------------
# Tests: PERSONA_CAPABILITY_MAP
# ---------------------------------------------------------------------------

class TestCapabilityMap:
    def test_all_three_personas_declared(self):
        for name in ["scribe", "architect", "professor"]:
            assert name in PERSONA_CAPABILITY_MAP

    def test_each_persona_has_at_least_one_capability(self):
        for name, caps in PERSONA_CAPABILITY_MAP.items():
            assert len(caps) >= 1, f"{name} has no capabilities"

    def test_each_capability_has_name_and_description(self):
        for name, caps in PERSONA_CAPABILITY_MAP.items():
            for cap in caps:
                assert "name" in cap and cap["name"], f"{name} cap missing name"
                assert "description" in cap and cap["description"], f"{name} cap missing description"


class TestDomainMap:
    def test_all_three_personas_have_domains(self):
        for name in ["scribe", "architect", "professor"]:
            assert name in PERSONA_DOMAIN_MAP
            assert len(PERSONA_DOMAIN_MAP[name]) >= 1


# ---------------------------------------------------------------------------
# Tests: PersonaAgent._build_contract
# ---------------------------------------------------------------------------

class TestBuildContract:
    @pytest.mark.parametrize("persona_name", ["scribe", "architect", "professor"])
    def test_contract_id_format(self, persona_name):
        agent = PersonaAgent(_mock_persona(), persona_name)
        assert agent.contract.id == f"persona_{persona_name}"

    @pytest.mark.parametrize("persona_name", ["scribe", "architect", "professor"])
    def test_contract_name_is_title_case(self, persona_name):
        agent = PersonaAgent(_mock_persona(), persona_name)
        assert agent.contract.name == persona_name.title()

    @pytest.mark.parametrize("persona_name", ["scribe", "architect", "professor"])
    def test_contract_agent_type_is_persona(self, persona_name):
        agent = PersonaAgent(_mock_persona(), persona_name)
        assert agent.contract.agent_type == "persona"

    @pytest.mark.parametrize("persona_name", ["scribe", "architect", "professor"])
    def test_contract_has_capabilities(self, persona_name):
        agent = PersonaAgent(_mock_persona(), persona_name)
        assert len(agent.contract.capabilities) >= 1

    @pytest.mark.parametrize("persona_name", ["scribe", "architect", "professor"])
    def test_contract_has_domain_affinity(self, persona_name):
        agent = PersonaAgent(_mock_persona(), persona_name)
        assert len(agent.contract.domain_affinity) >= 1

    def test_contract_execution_mode_interactive(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        assert agent.contract.execution_mode == ExecutionMode.INTERACTIVE

    def test_contract_prefer_local(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        assert agent.contract.resource_constraints.prefer_local is True

    def test_unknown_persona_has_empty_capabilities(self):
        agent = PersonaAgent(_mock_persona(), "unknown_persona")
        assert len(agent.contract.capabilities) == 0


# ---------------------------------------------------------------------------
# Tests: PersonaAgent.can_handle
# ---------------------------------------------------------------------------

class TestCanHandle:
    def test_can_handle_declared_capability(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        assert agent.can_handle("capture_note") is True

    def test_cannot_handle_undeclared_capability(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        assert agent.can_handle("nonexistent_cap") is False

    def test_architect_can_plan_task(self):
        agent = PersonaAgent(_mock_persona(), "architect")
        assert agent.can_handle("plan_task") is True

    def test_professor_can_explain_concept(self):
        agent = PersonaAgent(_mock_persona(), "professor")
        assert agent.can_handle("explain_concept") is True


# ---------------------------------------------------------------------------
# Tests: PersonaAgent.execute
# ---------------------------------------------------------------------------

class TestExecute:
    def test_execute_returns_completed_result(self):
        persona = _mock_persona("Here is my response")
        agent = PersonaAgent(persona, "scribe")

        from core.nexus.interface import AgentInput
        inp = AgentInput(query="Save this note")
        result = _run(agent.execute(inp))

        assert result.status == AgentStatus.COMPLETED
        assert result.content == "Here is my response"
        assert result.agent_id == "persona_scribe"

    def test_execute_sets_agent_id(self):
        agent = PersonaAgent(_mock_persona(), "architect")
        from core.nexus.interface import AgentInput
        result = _run(agent.execute(AgentInput(query="Design a system")))
        assert result.agent_id == "persona_architect"

    def test_execute_preserves_execution_id(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        from core.nexus.interface import AgentInput
        inp = AgentInput(query="q", execution_id="my-exec-id")
        result = _run(agent.execute(inp))
        assert result.execution_id == "my-exec-id"

    def test_execute_records_duration(self):
        agent = PersonaAgent(_mock_persona(), "professor")
        from core.nexus.interface import AgentInput
        result = _run(agent.execute(AgentInput(query="explain X")))
        assert result.duration_ms >= 0

    def test_execute_on_persona_failure_returns_failed_result(self):
        persona = MagicMock()
        persona.process = AsyncMock(side_effect=Exception("persona exploded"))
        agent = PersonaAgent(persona, "scribe")

        from core.nexus.interface import AgentInput
        result = _run(agent.execute(AgentInput(query="fail")))

        assert result.status == AgentStatus.FAILED
        assert result.error == "persona exploded"
        assert result.agent_id == "persona_scribe"

    def test_execute_output_contains_mode(self):
        agent = PersonaAgent(_mock_persona("content"), "scribe")
        from core.nexus.interface import AgentInput
        result = _run(agent.execute(AgentInput(query="note")))
        assert "mode" in result.output

    def test_execute_passes_conversation_history(self):
        persona = _mock_persona()
        agent = PersonaAgent(persona, "scribe")

        from core.nexus.interface import AgentInput
        history = [{"role": "user", "content": "prev message"}]
        inp = AgentInput(query="current", context={"conversation_history": history})
        _run(agent.execute(inp))

        persona.process.assert_called_once()
        call_args = persona.process.call_args[0][0]
        assert call_args.conversation_history == history


# ---------------------------------------------------------------------------
# Tests: repr
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr_contains_persona_name(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        r = repr(agent)
        assert "scribe" in r

    def test_repr_contains_capabilities(self):
        agent = PersonaAgent(_mock_persona(), "scribe")
        r = repr(agent)
        assert "capture_note" in r or "capabilities" in r
