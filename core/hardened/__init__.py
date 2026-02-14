"""
Hardened Knowledge Infrastructure
Defense-in-depth architecture for Polly's query pipeline.

Subsystems:
- failure: Observable failure modes with actionable context
- retry_manager: Unified retry strategy with circuit breaker
- validator: Dual-phenomenology validation (provenance + content)
- classifier: Three-tier retrieval classification (DIRECT/ADJACENT/ABSENT)
- performance: Percentile-based performance metrics
- dashboard: Performance reporting and degradation detection
- db: Database initialization and connection management
- migration: Schema migration system
"""

from core.hardened.failure import (
    FailureCategory,
    FailureSeverity,
    FailureReport,
    FailureFactory,
    FailureLogger,
    ErrorHandler,
)
from core.hardened.retry_manager import (
    RetryOutcome,
    RetryResult,
    RetryManager,
    CircuitBreaker,
    CircuitBreakerState,
    get_retry_manager,
    init_retry_manager,
)
from core.hardened.validator import (
    TrustLevel,
    ValidationStatus,
    ProvenanceResult,
    ContentResult,
    ValidationResult,
    ProvenanceValidator,
    ContentValidator,
    DualValidator,
)
from core.hardened.classifier import (
    RetrievalTier,
    TierResult,
    RetrievalClassifier,
)
from core.hardened.performance import (
    PercentileStats,
    PerformanceTracker,
    track_performance,
    track_performance_async,
    get_performance_tracker,
    init_performance_tracker,
)
from core.hardened.dashboard import PerformanceDashboard
from core.hardened.db import initialize_database, get_connection, get_db_path
from core.hardened.migration import MigrationManager

__all__ = [
    # Failure
    "FailureCategory",
    "FailureSeverity",
    "FailureReport",
    "FailureFactory",
    "FailureLogger",
    "ErrorHandler",
    # Retry
    "RetryOutcome",
    "RetryResult",
    "RetryManager",
    "CircuitBreaker",
    "CircuitBreakerState",
    "get_retry_manager",
    "init_retry_manager",
    # Validation
    "TrustLevel",
    "ValidationStatus",
    "ProvenanceResult",
    "ContentResult",
    "ValidationResult",
    "ProvenanceValidator",
    "ContentValidator",
    "DualValidator",
    # Classification
    "RetrievalTier",
    "TierResult",
    "RetrievalClassifier",
    # Performance
    "PercentileStats",
    "PerformanceTracker",
    "track_performance",
    "track_performance_async",
    "get_performance_tracker",
    "init_performance_tracker",
    # Dashboard
    "PerformanceDashboard",
    # Database
    "initialize_database",
    "get_connection",
    "get_db_path",
    "MigrationManager",
]
