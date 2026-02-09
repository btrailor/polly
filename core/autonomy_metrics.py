"""
Autonomy Metrics Tracker — Progressive autonomy tracking for knowledge writes.

Stores metrics about knowledge writes in SQLite (same DB as BudgetManager)
to power the autonomy dashboard: local routing %, cloud tokens saved, KB growth.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AutonomySnapshot:
    """Summary of autonomy metrics over a time period."""
    knowledge_writes_count: int = 0
    knowledge_writes_by_source: Dict[str, int] = None  # {ai_suggestion: N, context_menu: M, ...}
    estimated_tokens_saved: int = 0
    local_routing_pct: float = 0.0
    cloud_routing_pct: float = 0.0
    total_queries: int = 0
    period_days: int = 30

    def __post_init__(self):
        if self.knowledge_writes_by_source is None:
            self.knowledge_writes_by_source = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomyMetrics:
    """
    Tracks knowledge writes and routing decisions for progressive autonomy.

    Uses the same SQLite database as BudgetManager (~/.polly/usage.db).
    Creates additional tables:
    - knowledge_writes: log of every note saved from chat
    - routing_decisions: log of local vs cloud routing for each query
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / '.polly' / 'usage.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
        logger.info("AutonomyMetrics initialized")

    def _init_tables(self):
        """Create autonomy-specific tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_writes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    title TEXT NOT NULL,
                    domain TEXT,
                    source_type TEXT NOT NULL,
                    cloud_provider TEXT,
                    estimated_future_savings INTEGER DEFAULT 0,
                    note_path TEXT,
                    gap_score REAL
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_kw_timestamp
                ON knowledge_writes(timestamp)
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routing_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    query_hash TEXT,
                    route_type TEXT NOT NULL,
                    provider TEXT,
                    rag_coverage REAL,
                    tokens_used INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    local_pct REAL DEFAULT 0.0
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rd_timestamp
                ON routing_decisions(timestamp)
            """)

            conn.commit()

    # ------------------------------------------------------------------
    # Knowledge Write Tracking
    # ------------------------------------------------------------------

    def record_knowledge_write(
        self,
        title: str,
        domain: str = "",
        source_type: str = "unknown",
        cloud_provider: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        note_path: Optional[str] = None,
        gap_score: Optional[float] = None,
        estimated_future_savings: int = 0,
    ):
        """Record a knowledge write event."""
        ts = timestamp or datetime.now()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO knowledge_writes
                    (timestamp, title, domain, source_type, cloud_provider,
                     estimated_future_savings, note_path, gap_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ts.isoformat(),
                        title,
                        domain,
                        source_type,
                        cloud_provider,
                        estimated_future_savings,
                        note_path,
                        gap_score,
                    ),
                )
                conn.commit()
            logger.info(f"Recorded knowledge write: '{title}' ({source_type})")
        except Exception as e:
            logger.error(f"Failed to record knowledge write: {e}")

    # ------------------------------------------------------------------
    # Routing Decision Tracking
    # ------------------------------------------------------------------

    def record_routing_decision(
        self,
        route_type: str,  # "local", "cloud", "split"
        provider: Optional[str] = None,
        rag_coverage: float = 0.0,
        tokens_used: int = 0,
        cost: float = 0.0,
        local_pct: float = 0.0,
        query_hash: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        """Record a routing decision (local, cloud, or split)."""
        ts = timestamp or datetime.now()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO routing_decisions
                    (timestamp, query_hash, route_type, provider, rag_coverage,
                     tokens_used, cost, local_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ts.isoformat(),
                        query_hash,
                        route_type,
                        provider,
                        rag_coverage,
                        tokens_used,
                        cost,
                        local_pct,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record routing decision: {e}")

    # ------------------------------------------------------------------
    # Metrics Queries
    # ------------------------------------------------------------------

    def get_snapshot(self, days: int = 30) -> AutonomySnapshot:
        """
        Get an autonomy snapshot for the last N days.
        Returns knowledge write counts, routing percentages, and savings.
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Knowledge writes count
                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM knowledge_writes WHERE timestamp >= ?",
                    (cutoff,),
                ).fetchone()
                writes_count = row['cnt'] if row else 0

                # Writes by source_type
                rows = conn.execute(
                    "SELECT source_type, COUNT(*) as cnt FROM knowledge_writes "
                    "WHERE timestamp >= ? GROUP BY source_type",
                    (cutoff,),
                ).fetchall()
                writes_by_source = {r['source_type']: r['cnt'] for r in rows}

                # Estimated tokens saved
                row = conn.execute(
                    "SELECT COALESCE(SUM(estimated_future_savings), 0) as total "
                    "FROM knowledge_writes WHERE timestamp >= ?",
                    (cutoff,),
                ).fetchone()
                tokens_saved = row['total'] if row else 0

                # Routing decisions
                row = conn.execute(
                    "SELECT COUNT(*) as total FROM routing_decisions WHERE timestamp >= ?",
                    (cutoff,),
                ).fetchone()
                total_queries = row['total'] if row else 0

                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM routing_decisions "
                    "WHERE timestamp >= ? AND route_type = 'local'",
                    (cutoff,),
                ).fetchone()
                local_count = row['cnt'] if row else 0

                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM routing_decisions "
                    "WHERE timestamp >= ? AND route_type IN ('cloud', 'split')",
                    (cutoff,),
                ).fetchone()
                cloud_count = row['cnt'] if row else 0

                local_pct = (local_count / total_queries * 100) if total_queries > 0 else 0
                cloud_pct = (cloud_count / total_queries * 100) if total_queries > 0 else 0

                return AutonomySnapshot(
                    knowledge_writes_count=writes_count,
                    knowledge_writes_by_source=writes_by_source,
                    estimated_tokens_saved=tokens_saved,
                    local_routing_pct=round(local_pct, 1),
                    cloud_routing_pct=round(cloud_pct, 1),
                    total_queries=total_queries,
                    period_days=days,
                )

        except Exception as e:
            logger.error(f"Failed to get autonomy snapshot: {e}")
            return AutonomySnapshot(period_days=days)

    def get_recent_writes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent knowledge writes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM knowledge_writes ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to get recent writes: {e}")
            return []

    def get_routing_trend(self, days: int = 30, bucket_days: int = 7) -> List[Dict[str, Any]]:
        """
        Get routing trend over time, bucketed by week.
        Returns list of {period_start, local_pct, cloud_pct, total_queries}.
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """SELECT 
                        date(timestamp, 'start of day', 
                             '-' || (CAST(strftime('%w', timestamp) AS INTEGER)) || ' days') as week_start,
                        COUNT(*) as total,
                        SUM(CASE WHEN route_type = 'local' THEN 1 ELSE 0 END) as local_count,
                        SUM(CASE WHEN route_type IN ('cloud', 'split') THEN 1 ELSE 0 END) as cloud_count
                    FROM routing_decisions
                    WHERE timestamp >= ?
                    GROUP BY week_start
                    ORDER BY week_start""",
                    (cutoff,),
                ).fetchall()

                trend = []
                for r in rows:
                    total = r['total'] or 1
                    trend.append({
                        'period_start': r['week_start'],
                        'local_pct': round((r['local_count'] / total) * 100, 1),
                        'cloud_pct': round((r['cloud_count'] / total) * 100, 1),
                        'total_queries': total,
                    })
                return trend
        except Exception as e:
            logger.error(f"Failed to get routing trend: {e}")
            return []


# ========== Module-Level Singleton ==========

_metrics: Optional[AutonomyMetrics] = None


def get_autonomy_metrics() -> Optional[AutonomyMetrics]:
    """Get the global AutonomyMetrics instance."""
    return _metrics


def init_autonomy_metrics(db_path: Optional[Path] = None) -> AutonomyMetrics:
    """Initialize the global AutonomyMetrics instance."""
    global _metrics
    _metrics = AutonomyMetrics(db_path=db_path)
    return _metrics
