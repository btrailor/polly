"""
Tests for Nexus interface types (Phase 24a).

Tests AgentCapability, AgentContract, AgentInput, AgentResult, ResourceConstraints
serialization, has_capability, and the Executable Protocol check.
"""

from __future__ import annotations

import pytest

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


# ---------------------------------------------------------------------------
# ResourceConstraints
# ---------------------------------------------------------------------------

class TestResourceConstraints:
    def test_default_values(self):
        rc = ResourceConstraints()
        assert rc.max_tokens == 4096
        assert rc.timeout_seconds == 120
        assert rc.cost_cap_usd == 0.10
        assert rc.prefer_local is True

    def test_to_dict_roundtrip(self):
        rc = ResourceConstraints(max_tokens=2048, timeout_seconds=60, cost_cap_usd=0.05, prefer_local=False)
        d = rc.to_dict()
        rc2 = ResourceConstraints.from_dict(d)
        assert rc2.max_tokens == 2048
        assert rc2.timeout_seconds == 60
        assert rc2.cost_cap_usd == 0.05
        assert rc2.prefer_local is False

    def test_from_dict_uses_defaults_for_missing_keys(self):
        rc = ResourceConstraints.from_dict({})
        assert rc.max_tokens == 4096


# ---------------------------------------------------------------------------
# AgentCapability
# ---------------------------------------------------------------------------

class TestAgentCapability:
    def test_basic_creation(self):
        cap = AgentCapability(name="capture_note", description="Capture a note")
        assert cap.name == "capture_note"
        assert cap.description == "Capture a note"
        assert cap.input_schema == {}
        assert cap.output_schema == {}

    def test_to_dict_roundtrip(self):
        cap = AgentCapability(
            name="plan_task",
            description="Plan a task",
            input_schema={"query": "string"},
            output_schema={"plan": "string"},
        )
        d = cap.to_dict()
        cap2 = AgentCapability.from_dict(d)
        assert cap2.name == "plan_task"
        assert cap2.description == "Plan a task"
        assert cap2.input_schema == {"query": "string"}
        assert cap2.output_schema == {"plan": "string"}

    def test_from_dict_minimal(self):
        cap = AgentCapability.from_dict({"name": "foo"})
        assert cap.name == "foo"
        assert cap.description == ""


# ---------------------------------------------------------------------------
# AgentContract
# ---------------------------------------------------------------------------

def _make_contract(name="TestAgent") -> AgentContract:
    return AgentContract(
        id=f"agent_{name.lower()}",
        name=name,
        agent_type="persona",
        capabilities=[
            AgentCapability(name="capture_note", description="Capture notes"),
            AgentCapability(name="summarize", description="Summarize content"),
        ],
        execution_contexts=["chat"],
        domain_affinity=["writing", "notes"],
        execution_mode=ExecutionMode.INTERACTIVE,
    )


class TestAgentContract:
    def test_has_capability_true(self):
        contract = _make_contract()
        assert contract.has_capability("capture_note") is True

    def test_has_capability_false(self):
        contract = _make_contract()
        assert contract.has_capability("nonexistent") is False

    def test_has_capability_case_sensitive(self):
        contract = _make_contract()
        assert contract.has_capability("Capture_Note") is False

    def test_to_dict_roundtrip(self):
        contract = _make_contract("Scribe")
        d = contract.to_dict()
        contract2 = AgentContract.from_dict(d)
        assert contract2.id == contract.id
        assert contract2.name == "Scribe"
        assert contract2.agent_type == "persona"
        assert len(contract2.capabilities) == 2
        assert contract2.has_capability("capture_note")
        assert contract2.execution_mode == ExecutionMode.INTERACTIVE

    def test_to_dict_contains_required_keys(self):
        d = _make_contract().to_dict()
        for key in ("id", "name", "agent_type", "capabilities", "execution_contexts",
                    "resource_constraints", "domain_affinity", "execution_mode"):
            assert key in d

    def test_from_dict_preserves_capabilities(self):
        contract = _make_contract()
        d = contract.to_dict()
        contract2 = AgentContract.from_dict(d)
        cap_names = {c.name for c in contract2.capabilities}
        assert "capture_note" in cap_names
        assert "summarize" in cap_names

    def test_from_dict_default_execution_mode(self):
        contract = AgentContract.from_dict({"id": "x", "name": "X", "agent_type": "generic"})
        assert contract.execution_mode == ExecutionMode.INTERACTIVE

    def test_resource_constraints_preserved(self):
        contract = _make_contract()
        contract.resource_constraints.max_tokens = 8192
        d = contract.to_dict()
        contract2 = AgentContract.from_dict(d)
        assert contract2.resource_constraints.max_tokens == 8192


# ---------------------------------------------------------------------------
# AgentInput
# ---------------------------------------------------------------------------

class TestAgentInput:
    def test_default_execution_id_generated(self):
        inp = AgentInput(query="test")
        assert inp.execution_id is not None
        assert len(inp.execution_id) > 0

    def test_custom_execution_id(self):
        inp = AgentInput(query="test", execution_id="custom-id")
        assert inp.execution_id == "custom-id"

    def test_defaults(self):
        inp = AgentInput(query="hello")
        assert inp.data == {}
        assert inp.context == {}


# ---------------------------------------------------------------------------
# AgentResult
# ---------------------------------------------------------------------------

class TestAgentResult:
    def test_to_dict_contains_all_fields(self):
        result = AgentResult(
            agent_id="agent_scribe",
            execution_id="exec-123",
            status=AgentStatus.COMPLETED,
            content="Done",
            tokens_used=50,
            cost_usd=0.001,
            duration_ms=200,
        )
        d = result.to_dict()
        assert d["agent_id"] == "agent_scribe"
        assert d["execution_id"] == "exec-123"
        assert d["status"] == "completed"
        assert d["content"] == "Done"
        assert d["tokens_used"] == 50
        assert d["cost_usd"] == 0.001
        assert d["duration_ms"] == 200
        assert d["error"] is None

    def test_failed_result_has_error(self):
        result = AgentResult(
            agent_id="a",
            execution_id="e",
            status=AgentStatus.FAILED,
            error="something went wrong",
        )
        d = result.to_dict()
        assert d["status"] == "failed"
        assert d["error"] == "something went wrong"


# ---------------------------------------------------------------------------
# ExecutionMode enum
# ---------------------------------------------------------------------------

class TestExecutionMode:
    def test_values(self):
        assert ExecutionMode.AUTONOMOUS == "autonomous"
        assert ExecutionMode.INTERACTIVE == "interactive"
        assert ExecutionMode.HYBRID == "hybrid"

    def test_from_string(self):
        mode = ExecutionMode("interactive")
        assert mode == ExecutionMode.INTERACTIVE


# ---------------------------------------------------------------------------
# AgentStatus enum
# ---------------------------------------------------------------------------

class TestAgentStatus:
    def test_all_values_present(self):
        for v in ("idle", "running", "paused", "completed", "failed"):
            s = AgentStatus(v)
            assert s.value == v


# ---------------------------------------------------------------------------
# Executable Protocol
# ---------------------------------------------------------------------------

class TestExecutableProtocol:
    def test_mock_executable_satisfies_protocol(self):
        """A class with contract + execute + can_handle satisfies Executable."""
        from unittest.mock import AsyncMock

        class MockAgent:
            contract = _make_contract("Mock")

            async def execute(self, agent_input):
                return AgentResult(
                    agent_id="mock", execution_id="e", status=AgentStatus.COMPLETED
                )

            def can_handle(self, capability: str) -> bool:
                return self.contract.has_capability(capability)

        agent = MockAgent()
        assert isinstance(agent, Executable)

    def test_object_without_contract_does_not_satisfy_protocol(self):
        class BadAgent:
            async def execute(self, inp):
                pass

        bad = BadAgent()
        assert not isinstance(bad, Executable)
