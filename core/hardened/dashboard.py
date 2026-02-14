"""
Performance Dashboard
Hardened Knowledge Infrastructure — Wave 3

Report generation, degradation detection, and JSON export for the
hardened infrastructure layer.

Design:
- Human-readable performance reports
- Degradation detection (p95 vs baseline comparison)
- Failure pattern analysis
- JSON export for external tooling
"""

from typing import Optional, Dict, List, Any
from pathlib import Path
import json
import logging

from core.hardened.performance import PerformanceTracker, PercentileStats
from core.hardened.failure import FailureLogger

logger = logging.getLogger(__name__)


class PerformanceDashboard:
    """
    Performance dashboard combining metrics and failure analysis.

    Usage:
        dashboard = PerformanceDashboard(tracker, failure_logger)
        print(dashboard.generate_report(timeframe_hours=24))
        print(dashboard.check_degradation("rag_retrieval"))
    """

    def __init__(
        self,
        tracker: Optional[PerformanceTracker] = None,
        failure_logger: Optional[FailureLogger] = None,
    ):
        self.tracker = tracker or PerformanceTracker()
        self.failure_logger = failure_logger or FailureLogger()

    def generate_report(self, timeframe_hours: int = 24) -> str:
        """
        Generate human-readable performance report.

        Includes operation summaries, percentile breakdowns, and warnings
        for operations with high variance.
        """
        summary = self.tracker.get_operation_summary(timeframe_hours)

        lines = []
        lines.append(f"Performance Report (Last {timeframe_hours} hours)")
        lines.append("=" * 60)

        if not summary:
            lines.append("\nNo performance data recorded in this timeframe.")
            return "\n".join(lines)

        for operation, stats in sorted(summary.items()):
            lines.append(f"\n{operation}:")
            lines.append(f"  Total: {stats['total']} requests")
            lines.append(f"  Success Rate: {stats['success_rate']}%")

            if stats["failures"] > 0:
                lines.append(f"  Failures: {stats['failures']}")

            p = stats.get("percentiles", {})
            if p and p.get("count", 0) > 0:
                lines.append("  Response Times:")
                lines.append(f"    Min:    {p.get('min', 0):.0f}ms")
                lines.append(f"    p50:    {p.get('p50', 0):.0f}ms")
                lines.append(f"    p90:    {p.get('p90', 0):.0f}ms")
                lines.append(f"    p95:    {p.get('p95', 0):.0f}ms")
                lines.append(f"    p99:    {p.get('p99', 0):.0f}ms")
                lines.append(f"    Max:    {p.get('max', 0):.0f}ms")

                # Warn if p95 is significantly higher than median
                p50 = p.get("p50", 0)
                p95 = p.get("p95", 0)
                if p50 > 0 and p95 > p50 * 3:
                    lines.append(
                        f"    WARNING: p95 is {p95/p50:.1f}x median — "
                        f"significant tail latency"
                    )

        # Add failure patterns if any
        patterns = self.failure_logger.get_failure_patterns(
            timeframe_hours=timeframe_hours,
            min_occurrences=2,
        )
        if patterns:
            lines.append("\n" + "-" * 60)
            lines.append("Recurring Failure Patterns:")
            for category, info in patterns.items():
                lines.append(
                    f"  {category}: {info['occurrences']}x "
                    f"(retried: {info['retry_attempts']}, "
                    f"recovered: {info['retry_successes']})"
                )

        return "\n".join(lines)

    def check_degradation(
        self,
        operation: str,
        threshold_multiplier: float = 2.0,
        recent_hours: int = 1,
        baseline_hours: int = 168,  # 1 week
    ) -> Dict[str, Any]:
        """
        Check if recent performance has degraded compared to baseline.

        Compares p95 of recent period to p95 of baseline period.
        Returns degradation info if recent p95 exceeds threshold.

        Args:
            operation: Operation name to check
            threshold_multiplier: How many times worse p95 must be to flag
            recent_hours: Recent period to compare
            baseline_hours: Baseline period (default 1 week)

        Returns:
            Dict with 'degraded' boolean and details
        """
        recent = self.tracker.get_percentiles(operation, timeframe_hours=recent_hours)
        baseline = self.tracker.get_percentiles(operation, timeframe_hours=baseline_hours)

        if recent.count == 0 or baseline.count == 0:
            return {
                "degraded": False,
                "operation": operation,
                "reason": "Insufficient data for comparison",
                "recent_count": recent.count,
                "baseline_count": baseline.count,
            }

        if baseline.p95_ms == 0:
            return {
                "degraded": False,
                "operation": operation,
                "reason": "Baseline p95 is zero",
            }

        degradation_factor = recent.p95_ms / baseline.p95_ms

        if degradation_factor > threshold_multiplier:
            return {
                "degraded": True,
                "operation": operation,
                "recent_p95_ms": round(recent.p95_ms, 1),
                "baseline_p95_ms": round(baseline.p95_ms, 1),
                "degradation_factor": round(degradation_factor, 2),
                "threshold": threshold_multiplier,
                "recommendation": (
                    f"'{operation}' p95 has degraded {degradation_factor:.1f}x "
                    f"compared to baseline. Investigate recent changes."
                ),
            }

        return {
            "degraded": False,
            "operation": operation,
            "recent_p95_ms": round(recent.p95_ms, 1),
            "baseline_p95_ms": round(baseline.p95_ms, 1),
            "degradation_factor": round(degradation_factor, 2),
        }

    def check_all_degradation(
        self,
        threshold_multiplier: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """Check degradation for all tracked operations."""
        summary = self.tracker.get_operation_summary(timeframe_hours=1)
        results = []
        for operation in summary:
            result = self.check_degradation(
                operation, threshold_multiplier=threshold_multiplier
            )
            results.append(result)
        return results

    def get_layer_status(self) -> Dict[str, Any]:
        """
        Get status of all hardened infrastructure layers.

        Returns observable state for each protection layer:
        validation, retry, circuit breakers, performance.
        """
        status: Dict[str, Any] = {
            "layers": {},
            "healthy": True,
        }

        # Performance layer
        try:
            summary = self.tracker.get_operation_summary(timeframe_hours=1)
            status["layers"]["performance"] = {
                "active": True,
                "operations_tracked": len(summary),
                "operations": {
                    op: {
                        "success_rate": stats["success_rate"],
                        "total": stats["total"],
                    }
                    for op, stats in summary.items()
                },
            }
        except Exception as e:
            status["layers"]["performance"] = {
                "active": False,
                "error": str(e),
            }
            status["healthy"] = False

        # Failure logging layer
        try:
            patterns = self.failure_logger.get_failure_patterns(
                timeframe_hours=1, min_occurrences=1
            )
            recent = self.failure_logger.get_recent_failures(limit=5)
            status["layers"]["failure_logging"] = {
                "active": True,
                "patterns_detected": len(patterns),
                "recent_failures": len(recent),
            }
        except Exception as e:
            status["layers"]["failure_logging"] = {
                "active": False,
                "error": str(e),
            }

        return status

    def export_json(self, timeframe_hours: int = 24) -> str:
        """Export all metrics as JSON for external tooling."""
        data = {
            "timeframe_hours": timeframe_hours,
            "operations": self.tracker.get_operation_summary(timeframe_hours),
            "failure_patterns": self.failure_logger.get_failure_patterns(
                timeframe_hours=timeframe_hours
            ),
            "layer_status": self.get_layer_status(),
            "degradation": self.check_all_degradation(),
        }
        return json.dumps(data, indent=2, default=str)
