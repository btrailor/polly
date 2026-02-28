"""
SwarmStorage — SQLite execution history for Nexus (Phase 24a)

Persists swarm execution records and per-agent run records so
GET /swarms/{exec_id} and GET /swarms/history have data to serve.

Tables:
    swarm_executions    — one row per NexusCoordinator.route() call
    swarm_agent_runs    — one row per individual agent execution within a swarm
    swarm_templates     — reusable workflow templates (Phase 24b; schema only)
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS swarm_executions (
    id              TEXT PRIMARY KEY,
    status          TEXT NOT NULL DEFAULT 'pending',
    input_data      TEXT NOT NULL DEFAULT '{}',
    output_data     TEXT NOT NULL DEFAULT '{}',
    template_id     TEXT,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    error           TEXT
);
CREATE INDEX IF NOT EXISTS idx_swarm_exec_status ON swarm_executions(status);
CREATE INDEX IF NOT EXISTS idx_swarm_exec_started ON swarm_executions(started_at DESC);

CREATE TABLE IF NOT EXISTS swarm_agent_runs (
    id              TEXT PRIMARY KEY,
    execution_id    TEXT NOT NULL,
    agent_id        TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    input_data      TEXT NOT NULL DEFAULT '{}',
    output_data     TEXT NOT NULL DEFAULT '{}',
    tokens_used     INTEGER DEFAULT 0,
    cost_usd        REAL DEFAULT 0.0,
    duration_ms     INTEGER DEFAULT 0,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    error           TEXT,
    FOREIGN KEY (execution_id) REFERENCES swarm_executions(id)
);
CREATE INDEX IF NOT EXISTS idx_agent_run_exec ON swarm_agent_runs(execution_id);
CREATE INDEX IF NOT EXISTS idx_agent_run_agent ON swarm_agent_runs(agent_id);

CREATE TABLE IF NOT EXISTS swarm_templates (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    definition  TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT,
    usage_count INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_template_active ON swarm_templates(is_active);
"""

# Phase 24e: prompt_agents table (created via migration for existing DBs)
_PROMPT_AGENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_agents (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    capability_name TEXT NOT NULL,
    system_prompt   TEXT NOT NULL,
    domain_affinity TEXT NOT NULL DEFAULT '[]',
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL
);
"""

# Columns added in Phase 24b; use ALTER TABLE with error handling for
# upgrading DBs created under Phase 24a schema.
_MIGRATIONS = [
    "ALTER TABLE swarm_templates ADD COLUMN updated_at TEXT",
    "ALTER TABLE swarm_templates ADD COLUMN usage_count INTEGER NOT NULL DEFAULT 0",
]


class SwarmStorage:
    """
    Execution history store for the Nexus coordinator.

    All operations are synchronous (SQLite is fast enough for this use case).

    DB file: ~/.polly/swarms.db (configurable via db_path).
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ---- internal ----

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(_SCHEMA)
            conn.executescript(_PROMPT_AGENTS_SCHEMA)
        self._run_migrations()

    def _run_migrations(self) -> None:
        """Apply Phase 24b schema additions to existing DBs (idempotent)."""
        with self._conn() as conn:
            for stmt in _MIGRATIONS:
                try:
                    conn.execute(stmt)
                except Exception:
                    pass  # Column already exists — safe to ignore

    # ---- Swarm execution CRUD ----

    def create_execution(
        self,
        input_data: Dict[str, Any],
        template_id: Optional[str] = None,
    ) -> str:
        """
        Create a new swarm execution record.

        Returns the new execution ID.
        """
        exec_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO swarm_executions
                    (id, status, input_data, output_data, template_id, started_at)
                VALUES (?, 'pending', ?, '{}', ?, ?)
                """,
                (exec_id, json.dumps(input_data), template_id, now),
            )
        return exec_id

    def update_execution(
        self,
        exec_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update the status and optional output/error of a swarm execution."""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE swarm_executions
                SET status = ?, output_data = ?, completed_at = ?, error = ?
                WHERE id = ?
                """,
                (
                    status,
                    json.dumps(output_data or {}),
                    now if status in ("completed", "failed") else None,
                    error,
                    exec_id,
                ),
            )

    def get_execution(self, exec_id: str) -> Optional[Dict[str, Any]]:
        """Return execution record as a dict, or None if not found."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM swarm_executions WHERE id = ?", (exec_id,)
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "status": row["status"],
            "input_data": json.loads(row["input_data"]),
            "output_data": json.loads(row["output_data"]),
            "template_id": row["template_id"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "error": row["error"],
        }

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent `limit` executions ordered by start time (newest first)."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM swarm_executions ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "status": r["status"],
                "input_data": json.loads(r["input_data"]),
                "output_data": json.loads(r["output_data"]),
                "template_id": r["template_id"],
                "started_at": r["started_at"],
                "completed_at": r["completed_at"],
                "error": r["error"],
            }
            for r in rows
        ]

    # ---- Agent run CRUD ----

    def create_agent_run(
        self,
        execution_id: str,
        agent_id: str,
        input_data: Dict[str, Any],
    ) -> str:
        """Create a new agent run record within an execution. Returns the run ID."""
        run_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO swarm_agent_runs
                    (id, execution_id, agent_id, status, input_data, started_at)
                VALUES (?, ?, ?, 'running', ?, ?)
                """,
                (run_id, execution_id, agent_id, json.dumps(input_data), now),
            )
        return run_id

    def update_agent_run(
        self,
        run_id: str,
        status: Optional[str] = None,
        output_data: Optional[Dict[str, Any]] = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        duration_ms: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Update an agent run record."""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE swarm_agent_runs
                SET status = COALESCE(?, status),
                    output_data = ?,
                    tokens_used = ?,
                    cost_usd = ?,
                    duration_ms = ?,
                    completed_at = ?,
                    error = ?
                WHERE id = ?
                """,
                (
                    status,
                    json.dumps(output_data or {}),
                    tokens_used,
                    cost_usd,
                    duration_ms,
                    now if status in ("completed", "failed") else None,
                    error,
                    run_id,
                ),
            )

    def get_agent_runs(self, execution_id: str) -> List[Dict[str, Any]]:
        """Return all agent runs for a given execution."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM swarm_agent_runs WHERE execution_id = ? ORDER BY started_at",
                (execution_id,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "execution_id": r["execution_id"],
                "agent_id": r["agent_id"],
                "status": r["status"],
                "input_data": json.loads(r["input_data"]),
                "output_data": json.loads(r["output_data"]),
                "tokens_used": r["tokens_used"],
                "cost_usd": r["cost_usd"],
                "duration_ms": r["duration_ms"],
                "started_at": r["started_at"],
                "completed_at": r["completed_at"],
                "error": r["error"],
            }
            for r in rows
        ]

    # ---- Template CRUD ----

    def create_template(self, template_id: str, name: str, definition: Dict[str, Any]) -> str:
        """
        Upsert a workflow template.

        Stores the full template as JSON in the `definition` column.
        `name` is duplicated at the top level for fast listing queries.

        Returns template_id.
        """
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO swarm_templates (id, name, definition, created_at, updated_at, usage_count, is_active)
                VALUES (?, ?, ?, ?, ?, 0, 1)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    definition = excluded.definition,
                    updated_at = excluded.updated_at
                """,
                (template_id, name, json.dumps(definition), now, now),
            )
        return template_id

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Return template definition dict, or None if not found or inactive."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM swarm_templates WHERE id = ? AND is_active = 1",
                (template_id,),
            ).fetchone()
        if row is None:
            return None
        d = json.loads(row["definition"])
        d["_usage_count"] = row["usage_count"]
        return d

    def list_templates(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Return all active templates as definition dicts.

        If `domain` is provided, filters by domain_affinity (JSON LIKE match).
        """
        with self._conn() as conn:
            if domain:
                rows = conn.execute(
                    """
                    SELECT * FROM swarm_templates
                    WHERE is_active = 1 AND definition LIKE ?
                    ORDER BY usage_count DESC, name
                    """,
                    (f'%"{domain}"%',),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM swarm_templates WHERE is_active = 1 ORDER BY usage_count DESC, name"
                ).fetchall()
        result = []
        for row in rows:
            d = json.loads(row["definition"])
            d["_usage_count"] = row["usage_count"]
            result.append(d)
        return result

    def update_template(self, template_id: str, definition: Dict[str, Any]) -> None:
        """Update the definition JSON of an existing template."""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE swarm_templates
                SET definition = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(definition), now, template_id),
            )

    def delete_template(self, template_id: str) -> bool:
        """Soft-delete a template (sets is_active=0). Returns True if found."""
        with self._conn() as conn:
            cursor = conn.execute(
                "UPDATE swarm_templates SET is_active = 0 WHERE id = ? AND is_active = 1",
                (template_id,),
            )
        return cursor.rowcount > 0

    def increment_template_usage(self, template_id: str) -> None:
        """Increment the usage_count for a template (called after each workflow execution)."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE swarm_templates SET usage_count = usage_count + 1 WHERE id = ?",
                (template_id,),
            )

    # ---- Prompt agent CRUD (Phase 24e) ----

    def create_prompt_agent(
        self,
        agent_id: str,
        name: str,
        capability_name: str,
        system_prompt: str,
        domain_affinity: Optional[List[str]] = None,
    ) -> str:
        """Persist a user-defined PromptAgent. Returns agent_id."""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO prompt_agents
                    (id, name, capability_name, system_prompt, domain_affinity, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    capability_name = excluded.capability_name,
                    system_prompt = excluded.system_prompt,
                    domain_affinity = excluded.domain_affinity
                """,
                (
                    agent_id, name, capability_name, system_prompt,
                    json.dumps(domain_affinity or []), now,
                ),
            )
        return agent_id

    def list_prompt_agents(self) -> List[Dict[str, Any]]:
        """Return all active prompt agents as dicts."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM prompt_agents WHERE is_active = 1 ORDER BY created_at"
            ).fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "capability_name": row["capability_name"],
                "system_prompt": row["system_prompt"],
                "domain_affinity": json.loads(row["domain_affinity"] or "[]"),
            }
            for row in rows
        ]

    def delete_prompt_agent(self, agent_id: str) -> bool:
        """Soft-delete a prompt agent. Returns True if found."""
        with self._conn() as conn:
            cursor = conn.execute(
                "UPDATE prompt_agents SET is_active = 0 WHERE id = ? AND is_active = 1",
                (agent_id,),
            )
        return cursor.rowcount > 0

    def get_metrics(self) -> Dict[str, Any]:
        """Return aggregate execution metrics."""
        with self._conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) as n FROM swarm_executions"
            ).fetchone()["n"]
            by_status = conn.execute(
                "SELECT status, COUNT(*) as n FROM swarm_executions GROUP BY status"
            ).fetchall()
            agent_totals = conn.execute(
                """SELECT SUM(tokens_used) as tokens, SUM(cost_usd) as cost,
                   SUM(duration_ms) as duration FROM swarm_agent_runs"""
            ).fetchone()
        return {
            "total_executions": total,
            "by_status": {r["status"]: r["n"] for r in by_status},
            "total_tokens": agent_totals["tokens"] or 0,
            "total_cost_usd": agent_totals["cost"] or 0.0,
            "total_duration_ms": agent_totals["duration"] or 0,
        }

    def __repr__(self) -> str:
        return f"<SwarmStorage @ {self.db_path}>"
