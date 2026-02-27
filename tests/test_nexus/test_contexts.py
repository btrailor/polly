"""
Tests for Phase 24c: execution context types and NexusContextBroker.

Covers:
  - ExecutionContextType enum values and string serialization
  - ContextToken: is_expired(), allows(), to_dict(), from_dict() round-trip
  - ContextDenial: to_dict()
  - NexusContextBroker: is_context_enabled(), request_contexts() grant/deny,
    list_available(), TTL expiry, multi-context batch, get_active_tokens(),
    revoke_token(), unknown context type
  - WorkflowStep: required_contexts / optional_contexts in to_dict/from_dict,
    backward compatibility (missing fields default to [])
  - Executor integration: required context granted → runs; required context
    denied → FAILED step; optional context denied → step runs; no broker →
    backward compatible
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.nexus.contexts import (
    ContextDenial,
    ContextRequest,
    ContextToken,
    ExecutionContextType,
    NexusContextBroker,
)
from core.nexus.workflow import WorkflowStep, WorkflowTemplate
from core.nexus.interface import AgentResult, AgentStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _broker(config: dict | None = None) -> NexusContextBroker:
    cfg = config if config is not None else {
        "rag": {"enabled": True, "allowed_operations": ["query"]},
        "filesystem": {"enabled": True, "read_only": True, "allowed_operations": ["read"]},
        "obsidian": {"enabled": True, "allowed_operations": ["read", "write"]},
        "knowledge_graph": {"enabled": True, "allowed_operations": ["query"]},
        "github": {"enabled": False},
        "email": {"enabled": False},
        "ghost_cms": {"enabled": False},
        "calendar": {"enabled": False},
    }
    return NexusContextBroker(cfg)


def _future_token(ctx_type: str = "rag", ops: list | None = None) -> ContextToken:
    """Return a non-expired token."""
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    now = datetime.now(timezone.utc).isoformat()
    return ContextToken(
        token_id="tok-1",
        context_type=ExecutionContextType(ctx_type),
        agent_id="agent_scribe",
        workflow_exec_id="exec-1",
        granted_operations=ops or ["query"],
        issued_at=now,
        expires_at=future,
    )


def _expired_token() -> ContextToken:
    """Return an already-expired token."""
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    now = datetime.now(timezone.utc).isoformat()
    return ContextToken(
        token_id="tok-exp",
        context_type=ExecutionContextType.RAG,
        agent_id="agent_scribe",
        workflow_exec_id="exec-2",
        granted_operations=["query"],
        issued_at=past,
        expires_at=past,
    )


# ---------------------------------------------------------------------------
# TestExecutionContextType
# ---------------------------------------------------------------------------

class TestExecutionContextType:
    def test_filesystem_value(self):
        assert ExecutionContextType.FILESYSTEM == "filesystem"

    def test_github_value(self):
        assert ExecutionContextType.GITHUB == "github"

    def test_obsidian_value(self):
        assert ExecutionContextType.OBSIDIAN == "obsidian"

    def test_ghost_cms_value(self):
        assert ExecutionContextType.GHOST_CMS == "ghost_cms"

    def test_rag_value(self):
        assert ExecutionContextType.RAG == "rag"

    def test_knowledge_graph_value(self):
        assert ExecutionContextType.KNOWLEDGE_GRAPH == "knowledge_graph"

    def test_email_value(self):
        assert ExecutionContextType.EMAIL == "email"

    def test_calendar_value(self):
        assert ExecutionContextType.CALENDAR == "calendar"

    def test_eight_types(self):
        assert len(ExecutionContextType) == 8

    def test_from_string_rag(self):
        assert ExecutionContextType("rag") == ExecutionContextType.RAG

    def test_from_string_knowledge_graph(self):
        assert ExecutionContextType("knowledge_graph") == ExecutionContextType.KNOWLEDGE_GRAPH

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            ExecutionContextType("unknown_type")

    def test_is_str_subclass(self):
        assert isinstance(ExecutionContextType.RAG, str)


# ---------------------------------------------------------------------------
# TestContextToken
# ---------------------------------------------------------------------------

class TestContextToken:
    def test_basic_creation(self):
        t = _future_token()
        assert t.token_id == "tok-1"
        assert t.context_type == ExecutionContextType.RAG
        assert t.granted_operations == ["query"]

    def test_not_expired_for_future_token(self):
        t = _future_token()
        assert t.is_expired() is False

    def test_expired_for_past_token(self):
        t = _expired_token()
        assert t.is_expired() is True

    def test_allows_granted_operation(self):
        t = _future_token(ops=["read", "write"])
        assert t.allows("read") is True
        assert t.allows("write") is True

    def test_denies_non_granted_operation(self):
        t = _future_token(ops=["read"])
        assert t.allows("write") is False

    def test_to_dict_contains_all_fields(self):
        t = _future_token()
        d = t.to_dict()
        for key in ("token_id", "context_type", "agent_id", "workflow_exec_id",
                    "granted_operations", "issued_at", "expires_at", "metadata"):
            assert key in d

    def test_to_dict_context_type_is_string(self):
        t = _future_token()
        d = t.to_dict()
        assert isinstance(d["context_type"], str)
        assert d["context_type"] == "rag"

    def test_from_dict_roundtrip(self):
        t = _future_token(ctx_type="filesystem", ops=["read"])
        d = t.to_dict()
        t2 = ContextToken.from_dict(d)
        assert t2.token_id == t.token_id
        assert t2.context_type == ExecutionContextType.FILESYSTEM
        assert t2.granted_operations == ["read"]
        assert t2.agent_id == t.agent_id

    def test_from_dict_preserves_metadata(self):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        now = datetime.now(timezone.utc).isoformat()
        t = ContextToken(
            token_id="x",
            context_type=ExecutionContextType.FILESYSTEM,
            agent_id="a",
            workflow_exec_id="e",
            granted_operations=["read"],
            issued_at=now,
            expires_at=future,
            metadata={"read_only": True},
        )
        d = t.to_dict()
        t2 = ContextToken.from_dict(d)
        assert t2.metadata.get("read_only") is True

    def test_repr_contains_type(self):
        t = _future_token()
        assert "rag" in repr(t)

    def test_empty_metadata_default(self):
        t = _future_token()
        assert t.metadata == {}


# ---------------------------------------------------------------------------
# TestContextDenial
# ---------------------------------------------------------------------------

class TestContextDenial:
    def test_basic_creation(self):
        d = ContextDenial(
            context_type=ExecutionContextType.GITHUB,
            agent_id="agent_scribe",
            reason="disabled_in_config",
        )
        assert d.reason == "disabled_in_config"
        assert d.context_type == ExecutionContextType.GITHUB

    def test_to_dict_contains_required_keys(self):
        d = ContextDenial(
            context_type=ExecutionContextType.EMAIL,
            agent_id="a",
            reason="disabled_in_config",
        )
        result = d.to_dict()
        assert result["granted"] is False
        assert result["reason"] == "disabled_in_config"
        assert result["context_type"] == "email"

    def test_repr_contains_type_and_reason(self):
        d = ContextDenial(
            context_type=ExecutionContextType.CALENDAR,
            agent_id="a",
            reason="disabled_in_config",
        )
        r = repr(d)
        assert "calendar" in r
        assert "disabled_in_config" in r


# ---------------------------------------------------------------------------
# TestNexusContextBroker — is_context_enabled
# ---------------------------------------------------------------------------

class TestIsContextEnabled:
    def test_rag_enabled(self):
        b = _broker()
        assert b.is_context_enabled(ExecutionContextType.RAG) is True

    def test_github_disabled(self):
        b = _broker()
        assert b.is_context_enabled(ExecutionContextType.GITHUB) is False

    def test_email_disabled(self):
        b = _broker()
        assert b.is_context_enabled(ExecutionContextType.EMAIL) is False

    def test_filesystem_enabled(self):
        b = _broker()
        assert b.is_context_enabled(ExecutionContextType.FILESYSTEM) is True

    def test_unknown_type_returns_false(self):
        b = _broker({})
        assert b.is_context_enabled(ExecutionContextType.CALENDAR) is False

    def test_custom_config(self):
        b = _broker({"calendar": {"enabled": True, "allowed_operations": ["read"]}})
        assert b.is_context_enabled(ExecutionContextType.CALENDAR) is True


# ---------------------------------------------------------------------------
# TestNexusContextBroker — list_available
# ---------------------------------------------------------------------------

class TestListAvailable:
    def test_returns_eight_entries(self):
        b = _broker()
        result = b.list_available()
        assert len(result) == 8

    def test_each_entry_has_required_keys(self):
        b = _broker()
        for entry in b.list_available():
            assert "type" in entry
            assert "enabled" in entry
            assert "allowed_operations" in entry

    def test_rag_enabled_in_list(self):
        b = _broker()
        entries = {e["type"]: e for e in b.list_available()}
        assert entries["rag"]["enabled"] is True
        assert "query" in entries["rag"]["allowed_operations"]

    def test_github_disabled_in_list(self):
        b = _broker()
        entries = {e["type"]: e for e in b.list_available()}
        assert entries["github"]["enabled"] is False

    def test_all_eight_types_present(self):
        b = _broker()
        types = {e["type"] for e in b.list_available()}
        for ctx in ExecutionContextType:
            assert ctx.value in types


# ---------------------------------------------------------------------------
# TestNexusContextBroker — request_contexts
# ---------------------------------------------------------------------------

class TestRequestContexts:
    def test_enabled_context_grants_token(self):
        b = _broker()
        result = b.request_contexts("agent_a", ["rag"], "exec-1", operations=["query"])
        assert isinstance(result["rag"], ContextToken)

    def test_disabled_context_returns_denial(self):
        b = _broker()
        result = b.request_contexts("agent_a", ["github"], "exec-1", operations=["read"])
        assert isinstance(result["github"], ContextDenial)
        assert result["github"].reason == "disabled_in_config"

    def test_unknown_context_type_returns_denial(self):
        b = _broker()
        result = b.request_contexts("agent_a", ["unknown_xyz"], "exec-1", operations=["read"])
        denial = result["unknown_xyz"]
        assert "unknown_context_type" in denial.reason

    def test_token_has_correct_agent_id(self):
        b = _broker()
        result = b.request_contexts("my_agent", ["rag"], "exec-1", operations=["query"])
        assert result["rag"].agent_id == "my_agent"

    def test_token_has_correct_workflow_exec_id(self):
        b = _broker()
        result = b.request_contexts("a", ["rag"], "exec-42", operations=["query"])
        assert result["rag"].workflow_exec_id == "exec-42"

    def test_token_not_expired(self):
        b = _broker()
        result = b.request_contexts("a", ["rag"], "e", operations=["query"])
        assert result["rag"].is_expired() is False

    def test_token_has_unique_token_id(self):
        b = _broker()
        r1 = b.request_contexts("a", ["rag"], "e1", operations=["query"])
        r2 = b.request_contexts("a", ["rag"], "e2", operations=["query"])
        assert r1["rag"].token_id != r2["rag"].token_id

    def test_multi_context_batch(self):
        b = _broker()
        result = b.request_contexts("a", ["rag", "github", "filesystem"], "e",
                                    operations=["read"])
        assert isinstance(result["rag"], ContextDenial)  # "query" needed, not "read"
        assert isinstance(result["github"], ContextDenial)  # disabled
        assert isinstance(result["filesystem"], ContextToken)  # "read" is allowed

    def test_operation_intersection_rag_query(self):
        b = _broker()
        result = b.request_contexts("a", ["rag"], "e", operations=["query"])
        assert "query" in result["rag"].granted_operations

    def test_operation_not_permitted_returns_denial(self):
        b = _broker()
        # rag only allows "query", requesting "write" should be denied
        result = b.request_contexts("a", ["rag"], "e", operations=["write"])
        assert isinstance(result["rag"], ContextDenial)
        assert result["rag"].reason == "operations_not_permitted"

    def test_filesystem_metadata_passed_through(self):
        b = _broker()
        result = b.request_contexts("a", ["filesystem"], "e", operations=["read"])
        token = result["filesystem"]
        assert isinstance(token, ContextToken)
        assert token.metadata.get("read_only") is True

    def test_default_operations_read(self):
        b = _broker()
        result = b.request_contexts("a", ["filesystem"], "e")
        assert isinstance(result["filesystem"], ContextToken)

    def test_empty_context_types_returns_empty_dict(self):
        b = _broker()
        result = b.request_contexts("a", [], "e")
        assert result == {}

    def test_obsidian_write_allowed(self):
        b = _broker()
        result = b.request_contexts("a", ["obsidian"], "e", operations=["write"])
        assert isinstance(result["obsidian"], ContextToken)
        assert "write" in result["obsidian"].granted_operations


# ---------------------------------------------------------------------------
# TestNexusContextBroker — TTL and token management
# ---------------------------------------------------------------------------

class TestTokenManagement:
    def test_granted_token_tracked_in_active(self):
        b = _broker()
        b.request_contexts("a", ["rag"], "exec-1", operations=["query"])
        active = b.get_active_tokens("exec-1")
        assert len(active) == 1
        assert active[0].context_type == ExecutionContextType.RAG

    def test_get_active_tokens_filters_by_exec_id(self):
        b = _broker()
        b.request_contexts("a", ["rag"], "exec-1", operations=["query"])
        b.request_contexts("a", ["filesystem"], "exec-2", operations=["read"])
        assert len(b.get_active_tokens("exec-1")) == 1
        assert len(b.get_active_tokens("exec-2")) == 1

    def test_revoke_token_returns_true(self):
        b = _broker()
        result = b.request_contexts("a", ["rag"], "e", operations=["query"])
        tid = result["rag"].token_id
        assert b.revoke_token(tid) is True

    def test_revoke_token_removes_from_active(self):
        b = _broker()
        result = b.request_contexts("a", ["rag"], "e", operations=["query"])
        tid = result["rag"].token_id
        b.revoke_token(tid)
        assert b.get_active_tokens("e") == []

    def test_revoke_nonexistent_returns_false(self):
        b = _broker()
        assert b.revoke_token("nonexistent-token-id") is False

    def test_ttl_seconds_respected(self):
        b = _broker()
        result = b.request_contexts("a", ["rag"], "e", operations=["query"],
                                    ttl_seconds=7200)
        token = result["rag"]
        issued = datetime.fromisoformat(token.issued_at)
        expires = datetime.fromisoformat(token.expires_at)
        delta = expires - issued
        # Should be approximately 7200 seconds
        assert 7100 <= delta.total_seconds() <= 7300

    def test_expired_tokens_not_in_active(self):
        b = _broker()
        # Inject an expired token manually
        expired = _expired_token()
        b._active_tokens[expired.token_id] = expired
        active = b.get_active_tokens(expired.workflow_exec_id)
        assert expired not in active

    def test_repr_contains_enabled_types(self):
        b = _broker()
        r = repr(b)
        assert "NexusContextBroker" in r
        assert "rag" in r


# ---------------------------------------------------------------------------
# TestWorkflowStepContexts
# ---------------------------------------------------------------------------

class TestWorkflowStepContexts:
    def test_default_required_contexts_empty(self):
        step = WorkflowStep(id="s", agent_capability="c")
        assert step.required_contexts == []

    def test_default_optional_contexts_empty(self):
        step = WorkflowStep(id="s", agent_capability="c")
        assert step.optional_contexts == []

    def test_required_contexts_set(self):
        step = WorkflowStep(id="s", agent_capability="c", required_contexts=["rag"])
        assert "rag" in step.required_contexts

    def test_optional_contexts_set(self):
        step = WorkflowStep(id="s", agent_capability="c", optional_contexts=["github"])
        assert "github" in step.optional_contexts

    def test_to_dict_includes_required_contexts(self):
        step = WorkflowStep(id="s", agent_capability="c", required_contexts=["rag"])
        d = step.to_dict()
        assert "required_contexts" in d
        assert "rag" in d["required_contexts"]

    def test_to_dict_includes_optional_contexts(self):
        step = WorkflowStep(id="s", agent_capability="c", optional_contexts=["obsidian"])
        d = step.to_dict()
        assert "optional_contexts" in d
        assert "obsidian" in d["optional_contexts"]

    def test_from_dict_required_contexts(self):
        step = WorkflowStep.from_dict({
            "id": "s", "agent_capability": "c",
            "required_contexts": ["knowledge_graph"],
        })
        assert "knowledge_graph" in step.required_contexts

    def test_from_dict_optional_contexts(self):
        step = WorkflowStep.from_dict({
            "id": "s", "agent_capability": "c",
            "optional_contexts": ["rag"],
        })
        assert "rag" in step.optional_contexts

    def test_from_dict_backward_compat_missing_required(self):
        """Older dicts without required_contexts default to []."""
        step = WorkflowStep.from_dict({"id": "s", "agent_capability": "c"})
        assert step.required_contexts == []

    def test_from_dict_backward_compat_missing_optional(self):
        """Older dicts without optional_contexts default to []."""
        step = WorkflowStep.from_dict({"id": "s", "agent_capability": "c"})
        assert step.optional_contexts == []

    def test_to_dict_from_dict_roundtrip(self):
        step = WorkflowStep(
            id="x",
            agent_capability="cap",
            required_contexts=["rag"],
            optional_contexts=["filesystem", "obsidian"],
        )
        d = step.to_dict()
        step2 = WorkflowStep.from_dict(d)
        assert step2.required_contexts == ["rag"]
        assert set(step2.optional_contexts) == {"filesystem", "obsidian"}


# ---------------------------------------------------------------------------
# TestExecutorWithContexts
# ---------------------------------------------------------------------------

def _make_mock_coordinator(broker=None):
    """Build a minimal coordinator mock for executor tests."""
    from core.nexus.interface import AgentContract, AgentCapability, AgentStatus
    coordinator = MagicMock()
    coordinator.context_broker = broker

    # Mock agent contract
    contract = MagicMock()
    contract.id = "mock_agent"
    coordinator.select_agent.return_value = contract

    # Mock executable that returns a successful AgentResult
    executable = MagicMock()
    agent_result = AgentResult(
        agent_id="mock_agent",
        execution_id="exec-1",
        status=AgentStatus.COMPLETED,
        content="mock output",
    )
    executable.execute = AsyncMock(return_value=agent_result)
    coordinator._executables = {"mock_agent": executable}

    return coordinator, executable


def _make_storage():
    from core.nexus.storage import SwarmStorage
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    return SwarmStorage(path), path


class TestExecutorWithContexts:
    """Integration tests for executor context handling."""

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_no_broker_step_runs(self):
        """Backward compatible: no broker → step executes normally."""
        from core.nexus.executor import WorkflowExecutor
        from core.nexus.planner import WorkflowPlanner
        from core.nexus.workflow import WorkflowStep, WorkflowTemplate

        storage, path = _make_storage()
        try:
            coordinator, executable = _make_mock_coordinator(broker=None)
            storage.create_agent_run = MagicMock(return_value="run-1")
            storage.update_agent_run = MagicMock()
            storage.create_execution = MagicMock(return_value="exec-1")
            storage.update_execution = MagicMock()
            storage.increment_template_usage = MagicMock()

            template = WorkflowTemplate(
                id="t",
                name="T",
                description="",
                steps=[WorkflowStep(id="s", agent_capability="cap",
                                    required_contexts=["rag"])],
                output_step="s",
            )
            executor = WorkflowExecutor(coordinator, storage, WorkflowPlanner())
            result = self._run(executor.execute(template, "query", {}))
            assert result.status == "completed"
            executable.execute.assert_called_once()
        finally:
            path.unlink(missing_ok=True)

    def test_required_context_granted_step_runs(self):
        """Required context granted → step executes."""
        from core.nexus.executor import WorkflowExecutor
        from core.nexus.planner import WorkflowPlanner

        storage, path = _make_storage()
        try:
            broker = _broker()
            coordinator, executable = _make_mock_coordinator(broker=broker)
            storage.create_agent_run = MagicMock(return_value="run-1")
            storage.update_agent_run = MagicMock()
            storage.create_execution = MagicMock(return_value="exec-1")
            storage.update_execution = MagicMock()
            storage.increment_template_usage = MagicMock()

            template = WorkflowTemplate(
                id="t",
                name="T",
                description="",
                steps=[WorkflowStep(id="s", agent_capability="cap",
                                    required_contexts=["rag"])],
                output_step="s",
            )
            executor = WorkflowExecutor(coordinator, storage, WorkflowPlanner())
            result = self._run(executor.execute(template, "query", {}))
            assert result.status == "completed"
            executable.execute.assert_called_once()
        finally:
            path.unlink(missing_ok=True)

    def test_required_context_denied_fails_step(self):
        """Required context denied (disabled) → step is FAILED without calling agent."""
        from core.nexus.executor import WorkflowExecutor
        from core.nexus.planner import WorkflowPlanner

        storage, path = _make_storage()
        try:
            # broker with github disabled
            broker = _broker()
            coordinator, executable = _make_mock_coordinator(broker=broker)
            storage.create_agent_run = MagicMock(return_value="run-1")
            storage.update_agent_run = MagicMock()
            storage.create_execution = MagicMock(return_value="exec-1")
            storage.update_execution = MagicMock()
            storage.increment_template_usage = MagicMock()

            template = WorkflowTemplate(
                id="t",
                name="T",
                description="",
                steps=[WorkflowStep(id="s", agent_capability="cap",
                                    required_contexts=["github"])],
                output_step="s",
            )
            executor = WorkflowExecutor(coordinator, storage, WorkflowPlanner())
            result = self._run(executor.execute(template, "query", {}))
            # Workflow itself "completes" but the single step should be FAILED
            step_result = result.step_results.get("s")
            assert step_result is not None
            assert step_result.result.status == AgentStatus.FAILED
            assert "github" in (step_result.result.error or "")
            executable.execute.assert_not_called()
        finally:
            path.unlink(missing_ok=True)

    def test_optional_context_denied_step_still_runs(self):
        """Optional context denied → step runs without that token."""
        from core.nexus.executor import WorkflowExecutor
        from core.nexus.planner import WorkflowPlanner

        storage, path = _make_storage()
        try:
            broker = _broker()
            coordinator, executable = _make_mock_coordinator(broker=broker)
            storage.create_agent_run = MagicMock(return_value="run-1")
            storage.update_agent_run = MagicMock()
            storage.create_execution = MagicMock(return_value="exec-1")
            storage.update_execution = MagicMock()
            storage.increment_template_usage = MagicMock()

            template = WorkflowTemplate(
                id="t",
                name="T",
                description="",
                steps=[WorkflowStep(id="s", agent_capability="cap",
                                    optional_contexts=["github"])],
                output_step="s",
            )
            executor = WorkflowExecutor(coordinator, storage, WorkflowPlanner())
            result = self._run(executor.execute(template, "query", {}))
            assert result.status == "completed"
            executable.execute.assert_called_once()
        finally:
            path.unlink(missing_ok=True)

    def test_context_tokens_in_agent_input(self):
        """Granted context tokens are passed in agent_input.context['context_tokens']."""
        from core.nexus.executor import WorkflowExecutor
        from core.nexus.planner import WorkflowPlanner
        from core.nexus.interface import AgentInput

        storage, path = _make_storage()
        captured_inputs = []

        try:
            broker = _broker()
            coordinator, executable = _make_mock_coordinator(broker=broker)

            # Capture the AgentInput passed to execute
            async def capture_execute(agent_input):
                captured_inputs.append(agent_input)
                return AgentResult(
                    agent_id="mock_agent",
                    execution_id="exec-1",
                    status=AgentStatus.COMPLETED,
                    content="ok",
                )
            executable.execute = capture_execute

            storage.create_agent_run = MagicMock(return_value="run-1")
            storage.update_agent_run = MagicMock()
            storage.create_execution = MagicMock(return_value="exec-1")
            storage.update_execution = MagicMock()
            storage.increment_template_usage = MagicMock()

            template = WorkflowTemplate(
                id="t",
                name="T",
                description="",
                steps=[WorkflowStep(id="s", agent_capability="cap",
                                    optional_contexts=["rag"])],
                output_step="s",
            )
            executor = WorkflowExecutor(coordinator, storage, WorkflowPlanner())
            self._run(executor.execute(template, "query", {}))

            assert len(captured_inputs) == 1
            ctx = captured_inputs[0].context
            assert "context_tokens" in ctx
            assert "rag" in ctx["context_tokens"]
        finally:
            path.unlink(missing_ok=True)
