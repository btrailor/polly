"""
Tests for AgentRegistry (Phase 24a).

Uses a temporary SQLite DB so tests are isolated and do not touch ~/.polly.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.nexus.interface import AgentCapability, AgentContract, ExecutionMode
from core.nexus.registry import AgentRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_contract(
    name: str = "TestAgent",
    capabilities: list = None,
    domains: list = None,
    agent_type: str = "persona",
) -> AgentContract:
    caps = [AgentCapability(name=c, description=f"cap {c}") for c in (capabilities or [])]
    return AgentContract(
        id=f"agent_{name.lower()}",
        name=name,
        agent_type=agent_type,
        capabilities=caps,
        domain_affinity=domains or [],
        execution_mode=ExecutionMode.INTERACTIVE,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def registry(temp_db):
    return AgentRegistry(temp_db)


# ---------------------------------------------------------------------------
# Tests: __init__ + repr
# ---------------------------------------------------------------------------

class TestInit:
    def test_creates_db_file(self, temp_db):
        r = AgentRegistry(temp_db)
        assert temp_db.exists()

    def test_repr_shows_active_count(self, registry):
        r = repr(registry)
        assert "AgentRegistry" in r
        assert "0" in r  # empty

    def test_creates_parent_dirs(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c" / "test.db"
        r = AgentRegistry(nested)
        assert nested.exists()


# ---------------------------------------------------------------------------
# Tests: register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_returns_contract(self, registry):
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        result = registry.register(contract)
        assert result is contract

    def test_register_persists_to_db(self, registry):
        contract = _make_contract("Scribe")
        registry.register(contract)
        retrieved = registry.get(contract.id)
        assert retrieved is not None
        assert retrieved.id == contract.id
        assert retrieved.name == "Scribe"

    def test_register_upserts_existing(self, registry):
        contract = _make_contract("Scribe", capabilities=["cap1"])
        registry.register(contract)
        # Update with new capabilities
        contract2 = AgentContract(
            id=contract.id,
            name="ScribeV2",
            agent_type="persona",
            capabilities=[AgentCapability(name="cap1", description=""), AgentCapability(name="cap2", description="")],
        )
        registry.register(contract2)
        retrieved = registry.get(contract.id)
        assert retrieved.name == "ScribeV2"
        assert retrieved.has_capability("cap2")

    def test_register_multiple_agents(self, registry):
        for name in ["Scribe", "Architect", "Professor"]:
            registry.register(_make_contract(name))
        active = registry.list_active()
        assert len(active) == 3


# ---------------------------------------------------------------------------
# Tests: get
# ---------------------------------------------------------------------------

class TestGet:
    def test_get_existing_returns_contract(self, registry):
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        registry.register(contract)
        retrieved = registry.get(contract.id)
        assert retrieved is not None
        assert retrieved.has_capability("capture_note")

    def test_get_nonexistent_returns_none(self, registry):
        result = registry.get("agent_does_not_exist")
        assert result is None


# ---------------------------------------------------------------------------
# Tests: find_by_capability
# ---------------------------------------------------------------------------

class TestFindByCapability:
    def test_finds_agent_with_capability(self, registry):
        scribe = _make_contract("Scribe", capabilities=["capture_note", "summarize"])
        architect = _make_contract("Architect", capabilities=["plan_task"])
        registry.register(scribe)
        registry.register(architect)

        results = registry.find_by_capability("capture_note")
        assert len(results) == 1
        assert results[0].name == "Scribe"

    def test_returns_empty_when_no_match(self, registry):
        registry.register(_make_contract("Scribe", capabilities=["capture_note"]))
        results = registry.find_by_capability("nonexistent_cap")
        assert results == []

    def test_finds_multiple_agents_with_same_capability(self, registry):
        for name in ["Agent1", "Agent2"]:
            registry.register(_make_contract(name, capabilities=["shared_cap"]))
        results = registry.find_by_capability("shared_cap")
        assert len(results) == 2

    def test_excludes_inactive_agents(self, registry):
        contract = _make_contract("Scribe", capabilities=["capture_note"])
        registry.register(contract)
        registry.deactivate(contract.id)
        results = registry.find_by_capability("capture_note")
        assert results == []


# ---------------------------------------------------------------------------
# Tests: find_by_domain
# ---------------------------------------------------------------------------

class TestFindByDomain:
    def test_finds_agent_with_domain(self, registry):
        scribe = _make_contract("Scribe", domains=["writing", "notes"])
        registry.register(scribe)
        results = registry.find_by_domain("writing")
        assert len(results) == 1
        assert results[0].name == "Scribe"

    def test_returns_empty_for_unknown_domain(self, registry):
        registry.register(_make_contract("Scribe", domains=["notes"]))
        results = registry.find_by_domain("rocket_science")
        assert results == []

    def test_excludes_inactive_agents(self, registry):
        contract = _make_contract("Scribe", domains=["writing"])
        registry.register(contract)
        registry.deactivate(contract.id)
        results = registry.find_by_domain("writing")
        assert results == []


# ---------------------------------------------------------------------------
# Tests: list_active
# ---------------------------------------------------------------------------

class TestListActive:
    def test_empty_when_no_agents(self, registry):
        assert registry.list_active() == []

    def test_lists_registered_agents(self, registry):
        for name in ["A", "B", "C"]:
            registry.register(_make_contract(name))
        active = registry.list_active()
        assert len(active) == 3

    def test_excludes_deactivated_agents(self, registry):
        a = _make_contract("A")
        b = _make_contract("B")
        registry.register(a)
        registry.register(b)
        registry.deactivate(a.id)
        active = registry.list_active()
        assert len(active) == 1
        assert active[0].name == "B"


# ---------------------------------------------------------------------------
# Tests: deactivate
# ---------------------------------------------------------------------------

class TestDeactivate:
    def test_deactivate_existing_returns_true(self, registry):
        contract = _make_contract("Scribe")
        registry.register(contract)
        result = registry.deactivate(contract.id)
        assert result is True

    def test_deactivate_nonexistent_returns_false(self, registry):
        result = registry.deactivate("nonexistent_id")
        assert result is False

    def test_deactivated_agent_not_in_list_active(self, registry):
        contract = _make_contract("Scribe")
        registry.register(contract)
        registry.deactivate(contract.id)
        assert registry.get(contract.id) is not None  # still accessible via get
        assert registry.list_active() == []


# ---------------------------------------------------------------------------
# Tests: contract serialization round-trip
# ---------------------------------------------------------------------------

class TestContractRoundtrip:
    def test_capabilities_preserved_through_db(self, registry):
        contract = _make_contract("Scribe", capabilities=["capture_note", "summarize"])
        registry.register(contract)
        retrieved = registry.get(contract.id)
        cap_names = {c.name for c in retrieved.capabilities}
        assert "capture_note" in cap_names
        assert "summarize" in cap_names

    def test_domain_affinity_preserved_through_db(self, registry):
        contract = _make_contract("Scribe", domains=["writing", "notes"])
        registry.register(contract)
        retrieved = registry.get(contract.id)
        assert "writing" in retrieved.domain_affinity
        assert "notes" in retrieved.domain_affinity

    def test_execution_mode_preserved_through_db(self, registry):
        contract = _make_contract("Scribe")
        registry.register(contract)
        retrieved = registry.get(contract.id)
        assert retrieved.execution_mode == ExecutionMode.INTERACTIVE
