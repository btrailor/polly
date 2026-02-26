"""
Tests for NexusCoordinator (Phase 24a).

Tests: task classification, agent selection, route() execution and storage
recording, failure handling, and list_executables.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.nexus.coordinator import NexusCoordinator, TaskComplexity, _COMPLEX_KEYWORDS, _SIMPLE_KEYWORDS
from core.nexus.interface import (
    AgentCapability,
    AgentContract,
    AgentInput,
    AgentResult,
    AgentStatus,
    ExecutionMode,
)
from core.nexus.registry import AgentRegistry
from core.nexus.storage import SwarmStorage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_contract(name: str, capabilities: list = None, domains: list = None) -> AgentContract:
    caps = [AgentCapability(name=c, description=f"{c}") for c in (capabilities or [])]
    return AgentContract(
        id=f"agent_{name.lower()}",
        name=name,
        agent_type="persona",
        capabilities=caps,
        domain_affinity=domains or [],
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


def _coordinator() -> tuple:
    """Create an in-memory coordinator (temp SQLite DBs)."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    registry = AgentRegistry(db_path)
    storage = SwarmStorage(db_path)
    coord = NexusCoordinator(registry, storage)
    return coord, registry, storage


# ---------------------------------------------------------------------------
# Tests: __init__ + repr
# ---------------------------------------------------------------------------

class TestInit:
    def test_no_executables_at_start(self):
        coord, *_ = _coordinator()
        assert len(coord._executables) == 0

    def test_repr(self):
        coord, *_ = _coordinator()
        r = repr(coord)
        assert "NexusCoordinator" in r


# ---------------------------------------------------------------------------
# Tests: register_executable
# ---------------------------------------------------------------------------

class TestRegisterExecutable:
    def test_registers_executable(self):
        coord, registry, _ = _coordinator()
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        exe = _mock_executable(contract)
        coord.register_executable(contract.id, exe)
        assert contract.id in coord._executables

    def test_registers_contract_in_registry(self):
        coord, registry, _ = _coordinator()
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        exe = _mock_executable(contract)
        coord.register_executable(contract.id, exe)
        retrieved = registry.get(contract.id)
        assert retrieved is not None
        assert retrieved.has_capability("capture_note")

    def test_register_multiple(self):
        coord, *_ = _coordinator()
        for name in ["Scribe", "Architect", "Professor"]:
            contract = _make_contract(name)
            exe = _mock_executable(contract)
            coord.register_executable(contract.id, exe)
        assert len(coord._executables) == 3


# ---------------------------------------------------------------------------
# Tests: classify_task
# ---------------------------------------------------------------------------

class TestClassifyTask:
    def test_simple_query(self):
        coord, *_ = _coordinator()
        result = coord.classify_task("save this note", {})
        assert result == TaskComplexity.SIMPLE

    def test_complex_query(self):
        coord, *_ = _coordinator()
        result = coord.classify_task("design a microservices architecture", {})
        assert result == TaskComplexity.COMPLEX

    def test_long_query_is_complex(self):
        coord, *_ = _coordinator()
        long_query = "word " * 60
        result = coord.classify_task(long_query, {})
        assert result == TaskComplexity.COMPLEX

    def test_moderate_default(self):
        coord, *_ = _coordinator()
        result = coord.classify_task("tell me about Python", {})
        assert result == TaskComplexity.MODERATE

    def test_complex_keywords_trigger_complex(self):
        coord, *_ = _coordinator()
        for kw in list(_COMPLEX_KEYWORDS)[:3]:
            result = coord.classify_task(f"please {kw} the system", {})
            assert result == TaskComplexity.COMPLEX, f"keyword {kw!r} should trigger COMPLEX"

    def test_simple_keywords_trigger_simple(self):
        coord, *_ = _coordinator()
        for kw in list(_SIMPLE_KEYWORDS)[:3]:
            result = coord.classify_task(f"{kw} this content", {})
            assert result == TaskComplexity.SIMPLE, f"keyword {kw!r} should trigger SIMPLE"


# ---------------------------------------------------------------------------
# Tests: select_agent
# ---------------------------------------------------------------------------

class TestSelectAgent:
    def test_returns_none_when_no_agents(self):
        coord, *_ = _coordinator()
        result = coord.select_agent("query", {})
        assert result is None

    def test_returns_none_when_no_live_executables(self):
        coord, registry, _ = _coordinator()
        # Register in registry but no executable
        registry.register(_make_contract("Scribe", capabilities=["capture_note"]))
        result = coord.select_agent("query", {}, required_capability="capture_note")
        assert result is None

    def test_returns_contract_when_agent_available(self):
        coord, *_ = _coordinator()
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        exe = _mock_executable(contract)
        coord.register_executable(contract.id, exe)

        result = coord.select_agent("query", {})
        assert result is not None
        assert result.id == contract.id

    def test_selects_by_required_capability(self):
        coord, *_ = _coordinator()
        scribe = _make_contract("Scribe", capabilities=["capture_note"])
        architect = _make_contract("Architect", capabilities=["plan_task"])
        coord.register_executable(scribe.id, _mock_executable(scribe))
        coord.register_executable(architect.id, _mock_executable(architect))

        result = coord.select_agent("query", {}, required_capability="plan_task")
        assert result is not None
        assert result.id == architect.id

    def test_returns_none_for_unmatched_capability(self):
        coord, *_ = _coordinator()
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        coord.register_executable(contract.id, _mock_executable(contract))
        result = coord.select_agent("query", {}, required_capability="nonexistent")
        assert result is None


# ---------------------------------------------------------------------------
# Tests: route
# ---------------------------------------------------------------------------

class TestRoute:
    def test_returns_none_when_no_agent(self):
        coord, *_ = _coordinator()
        result = _run(coord.route("query", {}))
        assert result is None

    def test_routes_to_registered_agent(self):
        coord, *_ = _coordinator()
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        exe = _mock_executable(contract, content="note saved")
        coord.register_executable(contract.id, exe)

        result = _run(coord.route("save this note", {}))
        assert result is not None
        assert result.status == AgentStatus.COMPLETED
        assert result.content == "note saved"

    def test_records_execution_in_storage(self):
        coord, _, storage = _coordinator()
        contract = _make_contract("Scribe")
        exe = _mock_executable(contract)
        coord.register_executable(contract.id, exe)

        _run(coord.route("test query", {}))
        history = storage.get_history()
        assert len(history) == 1
        assert history[0]["input_data"]["query"] == "test query"

    def test_execution_status_completed_in_storage(self):
        coord, _, storage = _coordinator()
        contract = _make_contract("Scribe")
        exe = _mock_executable(contract)
        coord.register_executable(contract.id, exe)

        _run(coord.route("query", {}))
        history = storage.get_history()
        assert history[0]["status"] == "completed"

    def test_handles_agent_execution_failure(self):
        coord, _, storage = _coordinator()
        contract = _make_contract("Scribe")
        exe = MagicMock()
        exe.contract = contract
        exe.execute = AsyncMock(side_effect=Exception("agent crash"))
        coord.register_executable(contract.id, exe)

        result = _run(coord.route("query", {}))
        assert result is not None
        assert result.status == AgentStatus.FAILED
        assert "agent crash" in result.error

        history = storage.get_history()
        assert history[0]["status"] == "failed"

    def test_routes_with_required_capability(self):
        coord, *_ = _coordinator()
        scribe = _make_contract("Scribe", capabilities=["capture_note"])
        architect = _make_contract("Architect", capabilities=["plan_task"])
        scribe_exe = _mock_executable(scribe, content="scribe response")
        arch_exe = _mock_executable(architect, content="architect response")
        coord.register_executable(scribe.id, scribe_exe)
        coord.register_executable(architect.id, arch_exe)

        result = _run(coord.route("plan my system", {}, required_capability="plan_task"))
        assert result.content == "architect response"

    def test_route_calls_executable_execute(self):
        coord, *_ = _coordinator()
        contract = _make_contract("Scribe")
        exe = _mock_executable(contract)
        coord.register_executable(contract.id, exe)

        _run(coord.route("test", {}))
        exe.execute.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: list_executables
# ---------------------------------------------------------------------------

class TestListExecutables:
    def test_empty_initially(self):
        coord, *_ = _coordinator()
        assert coord.list_executables() == []

    def test_returns_all_registered(self):
        coord, *_ = _coordinator()
        for name in ["Scribe", "Architect"]:
            contract = _make_contract(name)
            coord.register_executable(contract.id, _mock_executable(contract))
        contracts = coord.list_executables()
        assert len(contracts) == 2
        names = {c.name for c in contracts}
        assert "Scribe" in names
        assert "Architect" in names
