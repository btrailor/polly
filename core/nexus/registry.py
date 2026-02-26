"""
AgentRegistry — SQLite-backed agent contract store (Phase 24a)

Stores AgentContract objects so Polly can discover, look up, and filter
agents by capability or domain without holding them in memory indefinitely.

Schema:
    agents (id, name, type, capabilities JSON, execution_contexts JSON,
            resource_constraints JSON, domain_affinity JSON, execution_mode,
            is_active, created_at)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.nexus.interface import AgentContract

logger = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    agent_type          TEXT NOT NULL DEFAULT 'generic',
    capabilities        TEXT NOT NULL DEFAULT '[]',
    execution_contexts  TEXT NOT NULL DEFAULT '[]',
    resource_constraints TEXT NOT NULL DEFAULT '{}',
    domain_affinity     TEXT NOT NULL DEFAULT '[]',
    execution_mode      TEXT NOT NULL DEFAULT 'interactive',
    is_active           INTEGER NOT NULL DEFAULT 1,
    created_at          TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active);
CREATE INDEX IF NOT EXISTS idx_agents_type   ON agents(agent_type);
"""


class AgentRegistry:
    """
    SQLite-backed registry for AgentContract objects.

    All operations are synchronous (SQLite is fast enough for
    the number of agents expected in Phase 24a).

    Args:
        db_path: Path to the SQLite database file.
                 Created if it does not exist.
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

    def _row_to_contract(self, row: sqlite3.Row) -> AgentContract:
        return AgentContract.from_dict({
            "id": row["id"],
            "name": row["name"],
            "agent_type": row["agent_type"],
            "capabilities": json.loads(row["capabilities"]),
            "execution_contexts": json.loads(row["execution_contexts"]),
            "resource_constraints": json.loads(row["resource_constraints"]),
            "domain_affinity": json.loads(row["domain_affinity"]),
            "execution_mode": row["execution_mode"],
        })

    # ---- public API ----

    def register(self, contract: AgentContract) -> AgentContract:
        """
        Upsert an AgentContract into the registry.

        If an agent with the same id already exists it is replaced.
        Returns the contract unchanged.
        """
        d = contract.to_dict()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agents
                    (id, name, agent_type, capabilities, execution_contexts,
                     resource_constraints, domain_affinity, execution_mode,
                     is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    d["id"],
                    d["name"],
                    d["agent_type"],
                    json.dumps(d["capabilities"]),
                    json.dumps(d["execution_contexts"]),
                    json.dumps(d["resource_constraints"]),
                    json.dumps(d["domain_affinity"]),
                    d["execution_mode"],
                    datetime.now().isoformat(),
                ),
            )
        logger.debug(f"AgentRegistry: registered agent '{contract.id}' ({contract.name})")
        return contract

    def get(self, agent_id: str) -> Optional[AgentContract]:
        """Return the AgentContract for `agent_id`, or None if not found."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM agents WHERE id = ?", (agent_id,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_contract(row)

    def find_by_capability(self, capability: str) -> List[AgentContract]:
        """
        Return all active agents that declare `capability`.

        Performs a case-insensitive substring search on the JSON-serialised
        capabilities column (fast enough for the expected number of agents).
        """
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agents WHERE is_active = 1 AND capabilities LIKE ?",
                (f'%"{capability}"%',),
            ).fetchall()
        results = []
        for row in rows:
            contract = self._row_to_contract(row)
            if contract.has_capability(capability):
                results.append(contract)
        return results

    def find_by_domain(self, domain: str) -> List[AgentContract]:
        """Return all active agents with `domain` in their domain_affinity list."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agents WHERE is_active = 1 AND domain_affinity LIKE ?",
                (f'%"{domain}"%',),
            ).fetchall()
        results = []
        for row in rows:
            contract = self._row_to_contract(row)
            if domain in contract.domain_affinity:
                results.append(contract)
        return results

    def list_active(self) -> List[AgentContract]:
        """Return all currently active AgentContracts."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agents WHERE is_active = 1 ORDER BY name"
            ).fetchall()
        return [self._row_to_contract(row) for row in rows]

    def deactivate(self, agent_id: str) -> bool:
        """
        Mark an agent as inactive (soft delete).

        Returns True if the agent was found and deactivated, False otherwise.
        """
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE agents SET is_active = 0 WHERE id = ?", (agent_id,)
            )
            changed = cur.rowcount > 0
        if changed:
            logger.debug(f"AgentRegistry: deactivated agent '{agent_id}'")
        return changed

    def __repr__(self) -> str:
        try:
            n = len(self.list_active())
        except Exception:
            n = "?"
        return f"<AgentRegistry {n} active agents @ {self.db_path}>"
