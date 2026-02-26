"""
Tests for SwarmStorage (Phase 24a).

Uses a temporary SQLite DB. Tests create/update round-trips for
swarm_executions and swarm_agent_runs.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.nexus.storage import SwarmStorage


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
def storage(temp_db):
    return SwarmStorage(temp_db)


# ---------------------------------------------------------------------------
# Tests: __init__ + repr
# ---------------------------------------------------------------------------

class TestInit:
    def test_creates_db_file(self, temp_db):
        s = SwarmStorage(temp_db)
        assert temp_db.exists()

    def test_repr(self, storage):
        r = repr(storage)
        assert "SwarmStorage" in r

    def test_creates_parent_dirs(self, tmp_path):
        nested = tmp_path / "x" / "y" / "z.db"
        s = SwarmStorage(nested)
        assert nested.exists()


# ---------------------------------------------------------------------------
# Tests: create_execution
# ---------------------------------------------------------------------------

class TestCreateExecution:
    def test_returns_string_id(self, storage):
        exec_id = storage.create_execution({"query": "test"})
        assert isinstance(exec_id, str)
        assert len(exec_id) > 0

    def test_creates_unique_ids(self, storage):
        id1 = storage.create_execution({"query": "a"})
        id2 = storage.create_execution({"query": "b"})
        assert id1 != id2

    def test_new_execution_has_pending_status(self, storage):
        exec_id = storage.create_execution({"query": "test"})
        record = storage.get_execution(exec_id)
        assert record["status"] == "pending"

    def test_input_data_stored(self, storage):
        exec_id = storage.create_execution({"query": "hello", "context": {"x": 1}})
        record = storage.get_execution(exec_id)
        assert record["input_data"]["query"] == "hello"
        assert record["input_data"]["context"] == {"x": 1}

    def test_with_template_id(self, storage):
        exec_id = storage.create_execution({}, template_id="tmpl-1")
        record = storage.get_execution(exec_id)
        assert record["template_id"] == "tmpl-1"

    def test_without_template_id(self, storage):
        exec_id = storage.create_execution({})
        record = storage.get_execution(exec_id)
        assert record["template_id"] is None


# ---------------------------------------------------------------------------
# Tests: update_execution
# ---------------------------------------------------------------------------

class TestUpdateExecution:
    def test_update_to_completed(self, storage):
        exec_id = storage.create_execution({"query": "q"})
        storage.update_execution(exec_id, "completed", output_data={"content": "done"})
        record = storage.get_execution(exec_id)
        assert record["status"] == "completed"
        assert record["output_data"]["content"] == "done"
        assert record["completed_at"] is not None

    def test_update_to_failed_stores_error(self, storage):
        exec_id = storage.create_execution({"query": "q"})
        storage.update_execution(exec_id, "failed", error="something broke")
        record = storage.get_execution(exec_id)
        assert record["status"] == "failed"
        assert record["error"] == "something broke"

    def test_running_status_does_not_set_completed_at(self, storage):
        exec_id = storage.create_execution({"query": "q"})
        storage.update_execution(exec_id, "running")
        record = storage.get_execution(exec_id)
        assert record["completed_at"] is None


# ---------------------------------------------------------------------------
# Tests: get_execution
# ---------------------------------------------------------------------------

class TestGetExecution:
    def test_returns_none_for_unknown_id(self, storage):
        result = storage.get_execution("nonexistent-id")
        assert result is None

    def test_returns_dict_with_required_keys(self, storage):
        exec_id = storage.create_execution({"query": "q"})
        record = storage.get_execution(exec_id)
        for key in ("id", "status", "input_data", "output_data", "started_at"):
            assert key in record

    def test_id_matches(self, storage):
        exec_id = storage.create_execution({})
        record = storage.get_execution(exec_id)
        assert record["id"] == exec_id


# ---------------------------------------------------------------------------
# Tests: get_history
# ---------------------------------------------------------------------------

class TestGetHistory:
    def test_empty_history(self, storage):
        history = storage.get_history()
        assert history == []

    def test_history_ordered_newest_first(self, storage):
        ids = [storage.create_execution({"n": i}) for i in range(3)]
        history = storage.get_history()
        # Newest should be last created
        assert len(history) == 3
        # IDs in reverse order of creation
        history_ids = [h["id"] for h in history]
        assert history_ids[0] == ids[-1]

    def test_history_respects_limit(self, storage):
        for i in range(10):
            storage.create_execution({"n": i})
        history = storage.get_history(limit=5)
        assert len(history) == 5

    def test_history_entries_have_required_keys(self, storage):
        storage.create_execution({"query": "test"})
        history = storage.get_history()
        for key in ("id", "status", "input_data", "started_at"):
            assert key in history[0]


# ---------------------------------------------------------------------------
# Tests: create_agent_run
# ---------------------------------------------------------------------------

class TestCreateAgentRun:
    def test_returns_string_id(self, storage):
        exec_id = storage.create_execution({})
        run_id = storage.create_agent_run(exec_id, "agent_scribe", {"query": "q"})
        assert isinstance(run_id, str)

    def test_creates_unique_run_ids(self, storage):
        exec_id = storage.create_execution({})
        id1 = storage.create_agent_run(exec_id, "agent_scribe", {})
        id2 = storage.create_agent_run(exec_id, "agent_scribe", {})
        assert id1 != id2

    def test_run_has_running_status(self, storage):
        exec_id = storage.create_execution({})
        run_id = storage.create_agent_run(exec_id, "agent_scribe", {})
        runs = storage.get_agent_runs(exec_id)
        assert len(runs) == 1
        assert runs[0]["status"] == "running"


# ---------------------------------------------------------------------------
# Tests: update_agent_run
# ---------------------------------------------------------------------------

class TestUpdateAgentRun:
    def test_update_to_completed(self, storage):
        exec_id = storage.create_execution({})
        run_id = storage.create_agent_run(exec_id, "agent_scribe", {})
        storage.update_agent_run(
            run_id,
            status="completed",
            output_data={"content": "done"},
            tokens_used=100,
            cost_usd=0.002,
            duration_ms=500,
        )
        runs = storage.get_agent_runs(exec_id)
        run = runs[0]
        assert run["status"] == "completed"
        assert run["output_data"]["content"] == "done"
        assert run["tokens_used"] == 100
        assert run["cost_usd"] == 0.002
        assert run["duration_ms"] == 500
        assert run["completed_at"] is not None

    def test_update_to_failed_stores_error(self, storage):
        exec_id = storage.create_execution({})
        run_id = storage.create_agent_run(exec_id, "agent_scribe", {})
        storage.update_agent_run(run_id, status="failed", error="agent error")
        runs = storage.get_agent_runs(exec_id)
        assert runs[0]["status"] == "failed"
        assert runs[0]["error"] == "agent error"


# ---------------------------------------------------------------------------
# Tests: get_agent_runs
# ---------------------------------------------------------------------------

class TestGetAgentRuns:
    def test_returns_empty_for_unknown_execution(self, storage):
        runs = storage.get_agent_runs("nonexistent")
        assert runs == []

    def test_returns_multiple_runs(self, storage):
        exec_id = storage.create_execution({})
        storage.create_agent_run(exec_id, "agent_scribe", {})
        storage.create_agent_run(exec_id, "agent_architect", {})
        runs = storage.get_agent_runs(exec_id)
        assert len(runs) == 2

    def test_run_has_required_keys(self, storage):
        exec_id = storage.create_execution({})
        storage.create_agent_run(exec_id, "agent_scribe", {"query": "q"})
        runs = storage.get_agent_runs(exec_id)
        for key in ("id", "execution_id", "agent_id", "status", "started_at"):
            assert key in runs[0]

    def test_run_input_data_stored(self, storage):
        exec_id = storage.create_execution({})
        storage.create_agent_run(exec_id, "agent_scribe", {"query": "hello world"})
        runs = storage.get_agent_runs(exec_id)
        assert runs[0]["input_data"]["query"] == "hello world"
