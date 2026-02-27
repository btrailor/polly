"""
Execution context types and brokering for Nexus agents (Phase 24c).

Agents declare what external systems they need (filesystem, RAG, github, etc.)
via WorkflowStep.required_contexts / optional_contexts.  The NexusContextBroker
mediates access by issuing scoped, time-limited ContextTokens.

The actual *use* of granted contexts (e.g. hitting a GitHub API) is out of
scope here — the broker mediates *access*, ContextToken carries the grant
metadata, and agents can inspect their token to know what they are allowed to do.

Usage:
    config = {
        "rag": {"enabled": True, "allowed_operations": ["query"]},
        "github": {"enabled": False},
    }
    broker = NexusContextBroker(config)
    grants = broker.request_contexts(
        agent_id="agent_scribe",
        context_types=["rag", "filesystem"],
        workflow_exec_id="exec-123",
        operations=["read"],
    )
    token = grants["rag"]          # ContextToken
    denial = grants["filesystem"]  # ContextDenial (not in config / disabled)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# ExecutionContextType
# ---------------------------------------------------------------------------

class ExecutionContextType(str, Enum):
    """External systems an agent can be granted access to."""

    FILESYSTEM = "filesystem"              # Read/write local files
    GITHUB = "github"                      # Repo access, PRs
    OBSIDIAN = "obsidian"                  # Vault read/write, wikilink resolution
    GHOST_CMS = "ghost_cms"               # Post creation, scheduling
    RAG = "rag"                            # Semantic search, knowledge retrieval
    KNOWLEDGE_GRAPH = "knowledge_graph"    # Entity queries, graph traversal
    EMAIL = "email"                        # Inbox access, SMTP
    CALENDAR = "calendar"                  # Event read/write


# ---------------------------------------------------------------------------
# ContextRequest
# ---------------------------------------------------------------------------

@dataclass
class ContextRequest:
    """
    A request for access to an execution context, submitted by an agent.

    Args:
        context_type:          The type of context being requested.
        agent_id:              The requesting agent's identifier.
        workflow_exec_id:      The workflow execution this request belongs to.
        requested_operations:  Operations the agent needs (e.g. ["read", "write"]).
        requested_at:          ISO timestamp when the request was made.
    """
    context_type: ExecutionContextType
    agent_id: str
    workflow_exec_id: str
    requested_operations: List[str]
    requested_at: str


# ---------------------------------------------------------------------------
# ContextToken
# ---------------------------------------------------------------------------

@dataclass
class ContextToken:
    """
    A scoped, time-limited grant of access to an execution context.

    Args:
        token_id:            UUID for this token.
        context_type:        The type of context granted.
        agent_id:            The agent this token was issued to.
        workflow_exec_id:    The workflow execution this token is scoped to.
        granted_operations:  Which operations are permitted (subset of what was requested).
        issued_at:           ISO timestamp when the token was issued.
        expires_at:          ISO timestamp when the token expires.
        metadata:            Additional broker-provided metadata (e.g. read_only, scope).
    """
    token_id: str
    context_type: ExecutionContextType
    agent_id: str
    workflow_exec_id: str
    granted_operations: List[str]
    issued_at: str
    expires_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ---- Inspection ----

    def is_expired(self) -> bool:
        """Return True if this token has passed its expiry time."""
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            # Make timezone-aware comparison if needed
            now = datetime.now(timezone.utc)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            return now > expiry
        except (ValueError, TypeError):
            return True

    def allows(self, operation: str) -> bool:
        """Return True if this token grants the named operation."""
        return operation in self.granted_operations

    # ---- Serialization ----

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "context_type": self.context_type.value,
            "agent_id": self.agent_id,
            "workflow_exec_id": self.workflow_exec_id,
            "granted_operations": list(self.granted_operations),
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ContextToken":
        return cls(
            token_id=d["token_id"],
            context_type=ExecutionContextType(d["context_type"]),
            agent_id=d["agent_id"],
            workflow_exec_id=d["workflow_exec_id"],
            granted_operations=list(d.get("granted_operations", [])),
            issued_at=d["issued_at"],
            expires_at=d["expires_at"],
            metadata=dict(d.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"<ContextToken type={self.context_type.value!r} "
            f"agent={self.agent_id!r} ops={self.granted_operations}>"
        )


# ---------------------------------------------------------------------------
# ContextDenial
# ---------------------------------------------------------------------------

@dataclass
class ContextDenial:
    """
    Represents a rejected context access request.

    Args:
        context_type: The type of context that was denied.
        agent_id:     The agent that requested access.
        reason:       Human-readable denial reason (e.g. "disabled_in_config").
    """
    context_type: ExecutionContextType
    agent_id: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_type": self.context_type.value,
            "agent_id": self.agent_id,
            "reason": self.reason,
            "granted": False,
        }

    def __repr__(self) -> str:
        return (
            f"<ContextDenial type={self.context_type.value!r} "
            f"reason={self.reason!r}>"
        )


# ---------------------------------------------------------------------------
# NexusContextBroker
# ---------------------------------------------------------------------------

class NexusContextBroker:
    """
    Mediates agent access to external execution contexts.

    Reads per-context policy from a config dict (the `nexus.contexts` section
    of config.yaml) and issues ContextToken grants or ContextDenial objects.

    This is a peer system to the existing CapabilityBroker (Phase 23.5, which
    handles PACKAGE_INSTALL / SHELL_EXEC).  NexusContextBroker is focused on
    agent context mediation for workflow execution.

    Args:
        config:        Dict mapping context type name → policy dict.
                       Each policy may contain:
                           enabled (bool)          — defaults to False
                           allowed_operations (list) — defaults to ["read"]
                           Any additional metadata passed through to the token.
        audit_logger:  Optional logger for audit trail (uses standard logging
                       if None).

    Example config::

        {
            "rag":        {"enabled": True, "allowed_operations": ["query"]},
            "filesystem": {"enabled": True, "read_only": True, "allowed_operations": ["read"]},
            "github":     {"enabled": False},
        }
    """

    def __init__(
        self,
        config: Dict[str, Any],
        audit_logger: Any = None,
    ) -> None:
        self._config = config or {}
        self._audit_logger = audit_logger
        # token_id → ContextToken (for active token tracking)
        self._active_tokens: Dict[str, ContextToken] = {}

    # ---- Policy ----

    def is_context_enabled(self, context_type: ExecutionContextType) -> bool:
        """Return True if the given context type is enabled in config."""
        policy = self._config.get(context_type.value, {})
        return bool(policy.get("enabled", False))

    def list_available(self) -> List[Dict[str, Any]]:
        """
        Return all context types with their enabled/disabled status and
        allowed operations from config.

        Returns a list ordered by ExecutionContextType definition order.
        """
        result = []
        for ctx_type in ExecutionContextType:
            policy = self._config.get(ctx_type.value, {})
            result.append({
                "type": ctx_type.value,
                "enabled": bool(policy.get("enabled", False)),
                "allowed_operations": list(policy.get("allowed_operations", [])),
            })
        return result

    # ---- Token issuance ----

    def request_contexts(
        self,
        agent_id: str,
        context_types: List[str],
        workflow_exec_id: str,
        operations: Optional[List[str]] = None,
        ttl_seconds: int = 3600,
    ) -> Dict[str, Union[ContextToken, ContextDenial]]:
        """
        Request access to one or more context types for an agent.

        For each requested type:
        - If the type is unknown (not a valid ExecutionContextType) → ContextDenial
        - If disabled in config → ContextDenial("disabled_in_config")
        - Otherwise → ContextToken with intersected operations

        Args:
            agent_id:          The agent requesting access.
            context_types:     List of context type string values to request.
            workflow_exec_id:  The workflow execution ID for scoping.
            operations:        Requested operations (default ["read"]).
            ttl_seconds:       Token lifetime in seconds (default 3600).

        Returns:
            Dict mapping each context_type string to a ContextToken or ContextDenial.
        """
        if operations is None:
            operations = ["read"]

        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=ttl_seconds)
        issued_at = now.isoformat()
        expires_at = expires.isoformat()

        results: Dict[str, Union[ContextToken, ContextDenial]] = {}

        for ctx_str in context_types:
            # Validate the context type
            try:
                ctx_type = ExecutionContextType(ctx_str)
            except ValueError:
                denial = ContextDenial(
                    context_type=ExecutionContextType.RAG,  # placeholder
                    agent_id=agent_id,
                    reason=f"unknown_context_type:{ctx_str}",
                )
                # Use a synthetic denial with the raw string type — override to_dict
                results[ctx_str] = _UnknownContextDenial(
                    raw_type=ctx_str,
                    agent_id=agent_id,
                    reason=f"unknown_context_type:{ctx_str}",
                )
                self._audit("denied", agent_id, ctx_str, workflow_exec_id,
                            results[ctx_str].reason)
                continue

            # Check enabled
            if not self.is_context_enabled(ctx_type):
                denial = ContextDenial(
                    context_type=ctx_type,
                    agent_id=agent_id,
                    reason="disabled_in_config",
                )
                results[ctx_str] = denial
                self._audit("denied", agent_id, ctx_str, workflow_exec_id,
                            denial.reason)
                continue

            # Grant — intersect requested operations with allowed operations
            policy = self._config.get(ctx_type.value, {})
            allowed_ops = set(policy.get("allowed_operations", ["read"]))
            granted_ops = [op for op in operations if op in allowed_ops]
            if not granted_ops:
                # Requested operations not available → deny
                denial = ContextDenial(
                    context_type=ctx_type,
                    agent_id=agent_id,
                    reason="operations_not_permitted",
                )
                results[ctx_str] = denial
                self._audit("denied", agent_id, ctx_str, workflow_exec_id,
                            denial.reason)
                continue

            # Build metadata from policy (drop known keys)
            metadata = {
                k: v for k, v in policy.items()
                if k not in ("enabled", "allowed_operations")
            }

            token = ContextToken(
                token_id=str(uuid.uuid4()),
                context_type=ctx_type,
                agent_id=agent_id,
                workflow_exec_id=workflow_exec_id,
                granted_operations=granted_ops,
                issued_at=issued_at,
                expires_at=expires_at,
                metadata=metadata,
            )
            self._active_tokens[token.token_id] = token
            results[ctx_str] = token
            self._audit("granted", agent_id, ctx_str, workflow_exec_id, "ok")

        return results

    # ---- Token management ----

    def revoke_token(self, token_id: str) -> bool:
        """
        Revoke an active token by ID.

        Returns True if the token was found and revoked, False otherwise.
        """
        if token_id in self._active_tokens:
            del self._active_tokens[token_id]
            return True
        return False

    def get_active_tokens(self, workflow_exec_id: str) -> List[ContextToken]:
        """
        Return all non-expired active tokens for a workflow execution.
        """
        return [
            t for t in self._active_tokens.values()
            if t.workflow_exec_id == workflow_exec_id and not t.is_expired()
        ]

    # ---- Internal ----

    def _audit(
        self,
        action: str,
        agent_id: str,
        context_type: str,
        workflow_exec_id: str,
        detail: str,
    ) -> None:
        """Emit an audit log entry."""
        if self._audit_logger is not None:
            self._audit_logger.info(
                f"NexusContextBroker: {action} context={context_type!r} "
                f"agent={agent_id!r} exec={workflow_exec_id!r} detail={detail!r}"
            )

    def __repr__(self) -> str:
        enabled = [
            ctx.value for ctx in ExecutionContextType
            if self.is_context_enabled(ctx)
        ]
        return f"<NexusContextBroker enabled={enabled} active_tokens={len(self._active_tokens)}>"


# ---------------------------------------------------------------------------
# Internal helper for unknown context type denials
# ---------------------------------------------------------------------------

class _UnknownContextDenial:
    """Denial for a context type string that is not a valid ExecutionContextType."""

    def __init__(self, raw_type: str, agent_id: str, reason: str) -> None:
        self.raw_type = raw_type
        self.agent_id = agent_id
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_type": self.raw_type,
            "agent_id": self.agent_id,
            "reason": self.reason,
            "granted": False,
        }

    def __repr__(self) -> str:
        return f"<ContextDenial type={self.raw_type!r} reason={self.reason!r}>"
