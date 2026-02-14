"""
Performance Metrics with Percentiles
Hardened Knowledge Infrastructure — Wave 3

Track response time distributions using percentiles (p50, p90, p95, p99)
to identify outliers and degradation patterns.

Design:
- Uses Python stdlib `statistics` module (no numpy dependency)
- In-memory buffer flushed to hardened.db periodically
- Context manager for automatic tracking
- Percentile thinking over averages: edge cases matter
"""

from collections import defaultdict
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime
import statistics
import sqlite3
import json
import time
import uuid
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Performance Metrics
# ---------------------------------------------------------------------------

@dataclass
class PercentileStats:
    """Percentile statistics for an operation."""
    count: int = 0
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    median_ms: float = 0.0
    p50_ms: float = 0.0
    p75_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    stdev_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "min": round(self.min_ms, 1),
            "max": round(self.max_ms, 1),
            "mean": round(self.mean_ms, 1),
            "median": round(self.median_ms, 1),
            "p50": round(self.p50_ms, 1),
            "p75": round(self.p75_ms, 1),
            "p90": round(self.p90_ms, 1),
            "p95": round(self.p95_ms, 1),
            "p99": round(self.p99_ms, 1),
            "stdev": round(self.stdev_ms, 1),
        }


# ---------------------------------------------------------------------------
# Performance Tracker
# ---------------------------------------------------------------------------

class PerformanceTracker:
    """
    Track operation performance with percentile statistics.

    Records execution times, token usage, and success/failure rates.
    Uses an in-memory buffer that flushes to hardened.db periodically.

    Usage:
        tracker = PerformanceTracker()

        # Manual recording
        tracker.record("rag_retrieval", execution_time_ms=42.5, success=True)

        # Context manager (sync)
        with track_performance(tracker, "rag_retrieval"):
            results = rag.search(query)

        # Context manager (async)
        async with track_performance_async(tracker, "generation"):
            response = await llm.generate(prompt)

        # Get stats
        stats = tracker.get_percentiles("rag_retrieval")
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        buffer_size: int = 100,
    ):
        self.db_path = db_path or Path.home() / ".polly" / "hardened.db"
        self.buffer_size = buffer_size
        self._buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._db_initialized = False

    def _ensure_table(self) -> None:
        """Create performance_metrics table if needed (lazy init)."""
        if self._db_initialized:
            return
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        metric_id TEXT PRIMARY KEY,
                        operation TEXT NOT NULL,
                        execution_time_ms REAL,
                        tokens_used INTEGER,
                        memory_mb REAL,
                        success INTEGER NOT NULL DEFAULT 1,
                        error_type TEXT,
                        domain TEXT,
                        persona TEXT,
                        recorded_at TEXT NOT NULL,
                        metadata TEXT
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_perf_operation
                    ON performance_metrics(operation)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_perf_recorded
                    ON performance_metrics(recorded_at)
                """)
                conn.commit()
            self._db_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize performance_metrics table: {e}")

    def record(
        self,
        operation: str,
        execution_time_ms: float,
        tokens_used: Optional[int] = None,
        memory_mb: Optional[float] = None,
        success: bool = True,
        error_type: Optional[str] = None,
        domain: Optional[str] = None,
        persona: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a single performance metric."""
        metric = {
            "metric_id": str(uuid.uuid4()),
            "operation": operation,
            "execution_time_ms": execution_time_ms,
            "tokens_used": tokens_used,
            "memory_mb": memory_mb,
            "success": success,
            "error_type": error_type,
            "domain": domain,
            "persona": persona,
            "recorded_at": datetime.now().isoformat(),
            "metadata": metadata,
        }

        self._buffer[operation].append(metric)

        # Auto-flush when buffer is full
        if len(self._buffer[operation]) >= self.buffer_size:
            self._flush_operation(operation)

    def _flush_operation(self, operation: str) -> None:
        """Write buffered metrics for an operation to database."""
        metrics = self._buffer.get(operation, [])
        if not metrics:
            return

        self._ensure_table()

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany(
                    """
                    INSERT OR IGNORE INTO performance_metrics
                    (metric_id, operation, execution_time_ms, tokens_used,
                     memory_mb, success, error_type, domain, persona,
                     recorded_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            m["metric_id"],
                            m["operation"],
                            m["execution_time_ms"],
                            m["tokens_used"],
                            m["memory_mb"],
                            1 if m["success"] else 0,
                            m["error_type"],
                            m["domain"],
                            m["persona"],
                            m["recorded_at"],
                            json.dumps(m["metadata"]) if m["metadata"] else None,
                        )
                        for m in metrics
                    ],
                )
                conn.commit()
            self._buffer[operation] = []
        except Exception as e:
            logger.error(f"Failed to flush performance metrics for '{operation}': {e}")

    def flush_all(self) -> None:
        """Flush all buffered metrics to database."""
        for operation in list(self._buffer.keys()):
            self._flush_operation(operation)

    def get_percentiles(
        self,
        operation: str,
        timeframe_hours: int = 24,
    ) -> PercentileStats:
        """
        Calculate percentile statistics for an operation.

        Uses Python stdlib statistics module (no numpy dependency).
        """
        self._ensure_table()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT execution_time_ms
                    FROM performance_metrics
                    WHERE operation = ?
                      AND recorded_at >= datetime('now', '-' || ? || ' hours')
                      AND success = 1
                    ORDER BY execution_time_ms
                    """,
                    (operation, timeframe_hours),
                )
                times = [row[0] for row in cursor.fetchall()]

            # Also include buffered (not yet flushed) metrics
            for m in self._buffer.get(operation, []):
                if m["success"]:
                    times.append(m["execution_time_ms"])

            if not times:
                return PercentileStats()

            times.sort()

            return PercentileStats(
                count=len(times),
                min_ms=min(times),
                max_ms=max(times),
                mean_ms=statistics.mean(times),
                median_ms=statistics.median(times),
                p50_ms=_percentile(times, 50),
                p75_ms=_percentile(times, 75),
                p90_ms=_percentile(times, 90),
                p95_ms=_percentile(times, 95),
                p99_ms=_percentile(times, 99),
                stdev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            )
        except Exception as e:
            logger.error(f"Failed to get percentiles for '{operation}': {e}")
            return PercentileStats()

    def get_operation_summary(
        self,
        timeframe_hours: int = 24,
    ) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics for all operations."""
        self._ensure_table()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT operation,
                           COUNT(*) as total,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                           SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
                    FROM performance_metrics
                    WHERE recorded_at >= datetime('now', '-' || ? || ' hours')
                    GROUP BY operation
                    """,
                    (timeframe_hours,),
                )

                summary: Dict[str, Dict[str, Any]] = {}
                for row in cursor.fetchall():
                    op, total, successes, failures = row
                    summary[op] = {
                        "total": total,
                        "successes": successes or 0,
                        "failures": failures or 0,
                        "success_rate": round(
                            ((successes or 0) / total * 100), 1
                        ) if total > 0 else 0,
                        "percentiles": self.get_percentiles(
                            op, timeframe_hours
                        ).to_dict(),
                    }

                return summary
        except Exception as e:
            logger.error(f"Failed to get operation summary: {e}")
            return {}


# ---------------------------------------------------------------------------
# Context managers for automatic tracking
# ---------------------------------------------------------------------------

@contextmanager
def track_performance(
    tracker: PerformanceTracker,
    operation: str,
    domain: Optional[str] = None,
    persona: Optional[str] = None,
    **extra_metadata: Any,
):
    """
    Context manager for automatic performance tracking (sync).

    Usage:
        with track_performance(tracker, 'rag_retrieval', domain='Sigils'):
            results = rag.search(query)
    """
    start_time = time.time()
    error_type = None
    success = True

    try:
        yield
    except Exception as e:
        error_type = type(e).__name__
        success = False
        raise
    finally:
        execution_time = (time.time() - start_time) * 1000
        tracker.record(
            operation=operation,
            execution_time_ms=execution_time,
            success=success,
            error_type=error_type,
            domain=domain,
            persona=persona,
            metadata=extra_metadata if extra_metadata else None,
        )


@asynccontextmanager
async def track_performance_async(
    tracker: PerformanceTracker,
    operation: str,
    domain: Optional[str] = None,
    persona: Optional[str] = None,
    **extra_metadata: Any,
):
    """
    Async context manager for automatic performance tracking.

    Usage:
        async with track_performance_async(tracker, 'generation'):
            response = await llm.generate(prompt)
    """
    start_time = time.time()
    error_type = None
    success = True

    try:
        yield
    except Exception as e:
        error_type = type(e).__name__
        success = False
        raise
    finally:
        execution_time = (time.time() - start_time) * 1000
        tracker.record(
            operation=operation,
            execution_time_ms=execution_time,
            success=success,
            error_type=error_type,
            domain=domain,
            persona=persona,
            metadata=extra_metadata if extra_metadata else None,
        )


# ---------------------------------------------------------------------------
# Percentile helper (stdlib, no numpy)
# ---------------------------------------------------------------------------

def _percentile(sorted_data: List[float], p: float) -> float:
    """
    Calculate the p-th percentile from sorted data using linear interpolation.

    Equivalent to numpy.percentile(data, p) for sorted input.
    """
    if not sorted_data:
        return 0.0
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]

    # Linear interpolation between closest ranks
    k = (p / 100.0) * (n - 1)
    f = int(k)
    c = f + 1

    if c >= n:
        return sorted_data[-1]

    d0 = sorted_data[f]
    d1 = sorted_data[c]
    return d0 + (d1 - d0) * (k - f)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get global PerformanceTracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = PerformanceTracker()
    return _tracker


def init_performance_tracker(
    db_path: Optional[Path] = None,
    buffer_size: int = 100,
) -> PerformanceTracker:
    """Initialize global PerformanceTracker."""
    global _tracker
    _tracker = PerformanceTracker(db_path=db_path, buffer_size=buffer_size)
    return _tracker
