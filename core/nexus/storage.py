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
    is_active   INTEGER NOT NULL DEFAULT 1
);
"""


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

    def __repr__(self) -> str:
        return f"<SwarmStorage @ {self.db_path}>"
