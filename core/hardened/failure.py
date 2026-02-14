"""
Observable Failure Modes
Hardened Knowledge Infrastructure — Wave 1

Explicit categorization of every failure type with actionable context.
Extends the existing ProviderError hierarchy from polly-routing rather
than replacing it.

Design principles:
- Every failure has a user-facing message and technical details
- Every failure suggests next actions
- Failures are logged to hardened.db for pattern analysis
- Constitutional checks (scapegoat/essentialist detection) trigger deeper
  analysis, not blocking — per ethics spec
- Hard blocks reserved for PII and prompt injection only
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path
import sqlite3
import json
import uuid
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Failure Taxonomy
# ---------------------------------------------------------------------------

class FailureCategory(Enum):
    """
    Explicit failure categories with actionable semantics.

    Organized by subsystem so each category maps to specific remediation.
    """

    # RAG Retrieval Failures
    NO_DOCUMENTS_FOUND = "no_documents_found"
    LOW_RELEVANCE = "low_relevance"
    EMBEDDING_SERVICE_DOWN = "embedding_service_down"

    # Epistemological Alignment (NOT content filtering — see ethics spec)
    # These trigger deeper analysis, not blocking.
    SCAPEGOAT_NARRATIVE_DETECTED = "scapegoat_narrative_detected"
    ESSENTIALIST_CLAIM_DETECTED = "essentialist_claim_detected"

    # Security (hard blocks — infrastructure, not epistemological)
    PII_DETECTED = "pii_detected"
    PROMPT_INJECTION_DETECTED = "prompt_injection_detected"

    # Provenance Failures
    UNTRUSTED_SOURCE = "untrusted_source"
    SOURCE_UNAVAILABLE = "source_unavailable"
    STALE_DATA = "stale_data"

    # Content Quality Failures
    FACT_CONTRADICTION = "fact_contradiction"
    OUTDATED_INFORMATION = "outdated_information"

    # Generation Failures
    CONTEXT_TOO_LARGE = "context_too_large"
    LLM_SERVICE_DOWN = "llm_service_down"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    GENERATION_TIMEOUT = "generation_timeout"

    # System Failures
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class FailureSeverity(Enum):
    """How serious the failure is."""
    ERROR = "error"       # Operation cannot continue
    WARNING = "warning"   # Operation degraded but usable
    INFO = "info"         # Informational — no actual problem


# ---------------------------------------------------------------------------
# Failure Report
# ---------------------------------------------------------------------------

@dataclass
class FailureReport:
    """
    Structured failure information with actionable context.

    Every failure produces one of these. The user_message is shown to the
    user; technical_details go to logs and the dashboard.
    """

    category: FailureCategory
    severity: FailureSeverity
    user_message: str
    technical_details: str

    # Actionable suggestions for the user
    suggestions: List[str] = field(default_factory=list)

    # Can this be retried?
    retryable: bool = False

    # Metadata for debugging and pattern analysis
    metadata: Optional[Dict[str, Any]] = None

    # Unique identifier
    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # When it happened
    occurred_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "user_message": self.user_message,
            "technical_details": self.technical_details,
            "suggestions": self.suggestions,
            "retryable": self.retryable,
            "metadata": self.metadata,
            "occurred_at": self.occurred_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Failure Factory — standardized failure construction
# ---------------------------------------------------------------------------

class FailureFactory:
    """Generate standardized FailureReports for common failure scenarios."""

    # --- RAG Retrieval ---

    @staticmethod
    def no_documents_found(query: str, docs_searched: int) -> FailureReport:
        return FailureReport(
            category=FailureCategory.NO_DOCUMENTS_FOUND,
            severity=FailureSeverity.INFO,
            user_message=f"I don't have information about this in my knowledge base.",
            technical_details=f"RAG search returned 0 results from {docs_searched} documents",
            suggestions=[
                "Search external sources for this information",
                "Add relevant documents to your knowledge base",
                "Rephrase your query to match existing content",
            ],
            retryable=False,
            metadata={"query": query[:500], "docs_searched": docs_searched},
        )

    @staticmethod
    def low_relevance(
        query: str, best_score: float, threshold: float
    ) -> FailureReport:
        return FailureReport(
            category=FailureCategory.LOW_RELEVANCE,
            severity=FailureSeverity.WARNING,
            user_message=(
                "I found some related information, but nothing that directly "
                "answers your question."
            ),
            technical_details=(
                f"Best relevance score {best_score:.2f} below threshold {threshold:.2f}"
            ),
            suggestions=[
                "Try rephrasing your question",
                "Be more specific about what you're looking for",
                "Break complex questions into simpler parts",
            ],
            retryable=True,
            metadata={
                "query": query[:500],
                "best_score": best_score,
                "threshold": threshold,
            },
        )

    @staticmethod
    def embedding_service_down(service: str, error: str) -> FailureReport:
        return FailureReport(
            category=FailureCategory.EMBEDDING_SERVICE_DOWN,
            severity=FailureSeverity.ERROR,
            user_message="The embedding service is unavailable. Retrying...",
            technical_details=f"Embedding service '{service}' failed: {error}",
            suggestions=[
                "Check that Ollama is running",
                "Verify the embedding model is pulled",
                "Check system resources",
            ],
            retryable=True,
            metadata={"service": service, "error": error},
        )

    # --- Epistemological (deeper analysis, NOT blocking) ---

    @staticmethod
    def scapegoat_narrative_detected(
        content_sample: str, analysis_context: Dict[str, Any]
    ) -> FailureReport:
        """
        Scapegoat narrative detected in retrieved content.

        Per ethics spec: this triggers deeper structural analysis, not blocking.
        The 'failure' is informational — it tells the system to enrich the
        response with cui bono and material analysis context.
        """
        return FailureReport(
            category=FailureCategory.SCAPEGOAT_NARRATIVE_DETECTED,
            severity=FailureSeverity.INFO,
            user_message="",  # Not shown to user — triggers deeper analysis internally
            technical_details=(
                f"Scapegoat narrative pattern detected: {analysis_context.get('reason', '')}"
            ),
            suggestions=[],  # Not a user-facing failure
            retryable=False,
            metadata={
                "content_sample": content_sample[:200],
                "analysis_context": analysis_context,
                "action": "enrich_with_structural_analysis",
            },
        )

    @staticmethod
    def essentialist_claim_detected(
        content_sample: str, analysis_context: Dict[str, Any]
    ) -> FailureReport:
        """
        Essentialist claim detected in retrieved content.

        Per ethics spec: triggers material/historical analysis enrichment,
        not blocking.
        """
        return FailureReport(
            category=FailureCategory.ESSENTIALIST_CLAIM_DETECTED,
            severity=FailureSeverity.INFO,
            user_message="",
            technical_details=(
                f"Essentialist claim pattern detected: {analysis_context.get('reason', '')}"
            ),
            suggestions=[],
            retryable=False,
            metadata={
                "content_sample": content_sample[:200],
                "analysis_context": analysis_context,
                "action": "enrich_with_material_analysis",
            },
        )

    # --- Security (hard blocks) ---

    @staticmethod
    def pii_detected(pii_type: str, context: str = "") -> FailureReport:
        return FailureReport(
            category=FailureCategory.PII_DETECTED,
            severity=FailureSeverity.ERROR,
            user_message="Personal information was detected and blocked for privacy.",
            technical_details=f"PII type '{pii_type}' detected in content",
            suggestions=[
                "Remove personal information from the query",
                "This content was blocked before reaching any external service",
            ],
            retryable=False,
            metadata={"pii_type": pii_type, "context": context[:100]},
        )

    @staticmethod
    def prompt_injection_detected(pattern: str) -> FailureReport:
        return FailureReport(
            category=FailureCategory.PROMPT_INJECTION_DETECTED,
            severity=FailureSeverity.ERROR,
            user_message="A prompt injection attempt was detected and blocked.",
            technical_details=f"Prompt injection pattern: {pattern}",
            suggestions=[],
            retryable=False,
            metadata={"pattern": pattern[:200]},
        )

    # --- Provenance ---

    @staticmethod
    def untrusted_source(
        source_uri: str, trust_level: str, required_level: str
    ) -> FailureReport:
        return FailureReport(
            category=FailureCategory.UNTRUSTED_SOURCE,
            severity=FailureSeverity.WARNING,
            user_message=(
                "Some retrieved content comes from an unverified source and "
                "has been excluded."
            ),
            technical_details=(
                f"Source '{source_uri}' trust level '{trust_level}' "
                f"below required '{required_level}'"
            ),
            suggestions=[
                "Add this source to your trusted sources",
                "Verify the content independently",
            ],
            retryable=False,
            metadata={
                "source_uri": source_uri,
                "trust_level": trust_level,
                "required_level": required_level,
            },
        )

    @staticmethod
    def stale_data(
        source_uri: str, last_verified: Optional[str], max_age_seconds: int
    ) -> FailureReport:
        return FailureReport(
            category=FailureCategory.STALE_DATA,
            severity=FailureSeverity.WARNING,
            user_message="Some retrieved content may be outdated.",
            technical_details=(
                f"Source '{source_uri}' last verified: {last_verified}, "
                f"max age: {max_age_seconds}s"
            ),
            suggestions=[
                "Re-index this document to refresh it",
                "Verify the information is still current",
            ],
            retryable=False,
            metadata={
                "source_uri": source_uri,
                "last_verified": last_verified,
                "max_age_seconds": max_age_seconds,
            },
        )

    # --- Generation ---

    @staticmethod
    def context_too_large(
        token_count: int, max_tokens: int, documents_count: int
    ) -> FailureReport:
        return FailureReport(
            category=FailureCategory.CONTEXT_TOO_LARGE,
            severity=FailureSeverity.WARNING,
            user_message=(
                "Your query retrieved too much information to process at once. "
                "Retrying with more aggressive summarization."
            ),
            technical_details=(
                f"Context {token_count} tokens exceeds limit of {max_tokens}"
            ),
            suggestions=[
                "Narrow your query to a more specific topic",
                "Ask about one aspect at a time",
            ],
            retryable=True,
            metadata={
                "token_count": token_count,
                "max_tokens": max_tokens,
                "documents_count": documents_count,
            },
        )

    @staticmethod
    def rate_limit_exceeded(
        service: str, retry_after: Optional[int] = None
    ) -> FailureReport:
        retry_msg = f" Retry in {retry_after} seconds." if retry_after else ""
        return FailureReport(
            category=FailureCategory.RATE_LIMIT_EXCEEDED,
            severity=FailureSeverity.WARNING,
            user_message=f"Rate limit reached for {service}.{retry_msg}",
            technical_details=f"{service} API rate limit exceeded",
            suggestions=[
                "Wait a moment and try again",
                "Switch to local model if available",
            ],
            retryable=True,
            metadata={"service": service, "retry_after": retry_after},
        )

    @staticmethod
    def llm_service_down(service: str, error: str) -> FailureReport:
        return FailureReport(
            category=FailureCategory.LLM_SERVICE_DOWN,
            severity=FailureSeverity.ERROR,
            user_message=f"The LLM service ({service}) is currently unavailable.",
            technical_details=f"LLM service '{service}' failed: {error}",
            suggestions=[
                "Try a different provider",
                "Switch to local model if available",
                "Check your API keys and network connection",
            ],
            retryable=True,
            metadata={"service": service, "error": error},
        )

    @staticmethod
    def generation_timeout(service: str, timeout_ms: int) -> FailureReport:
        return FailureReport(
            category=FailureCategory.GENERATION_TIMEOUT,
            severity=FailureSeverity.WARNING,
            user_message="The response took too long to generate. Retrying...",
            technical_details=f"Generation timed out after {timeout_ms}ms on {service}",
            suggestions=[
                "Try a simpler query",
                "Use a faster model",
            ],
            retryable=True,
            metadata={"service": service, "timeout_ms": timeout_ms},
        )

    # --- System ---

    @staticmethod
    def database_error(error: Exception) -> FailureReport:
        return FailureReport(
            category=FailureCategory.DATABASE_ERROR,
            severity=FailureSeverity.ERROR,
            user_message="A database error occurred. This has been logged.",
            technical_details=f"Database error: {type(error).__name__}: {str(error)}",
            suggestions=[
                "Check database file permissions",
                "Verify database is not corrupted",
                "Check available disk space",
            ],
            retryable=False,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

    @staticmethod
    def network_error(error: Exception, operation: str = "") -> FailureReport:
        return FailureReport(
            category=FailureCategory.NETWORK_ERROR,
            severity=FailureSeverity.ERROR,
            user_message="A network error occurred. Falling back to local-only mode.",
            technical_details=f"Network error during {operation}: {type(error).__name__}: {str(error)}",
            suggestions=[
                "Check your internet connection",
                "Local-only mode is available",
            ],
            retryable=True,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "operation": operation,
            },
        )

    @staticmethod
    def unknown_error(error: Exception, context: str = "") -> FailureReport:
        return FailureReport(
            category=FailureCategory.UNKNOWN_ERROR,
            severity=FailureSeverity.ERROR,
            user_message="An unexpected error occurred.",
            technical_details=f"{type(error).__name__}: {str(error)} (context: {context})",
            suggestions=[
                "Check logs for details",
                "Report this issue if it persists",
            ],
            retryable=False,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
            },
        )

    # --- Provider Error Mapping ---

    @staticmethod
    def from_provider_error(error: Exception) -> FailureReport:
        """
        Map existing ProviderError hierarchy to FailureReport.

        This bridges the existing error types from polly-routing into the
        hardened failure taxonomy without replacing them.
        """
        from core.providers.base import (
            ProviderRateLimitError,
            ProviderAuthError,
            ProviderConnectionError,
            ProviderTimeoutError,
            ProviderAPIError,
            AllProvidersFailed,
        )

        if isinstance(error, ProviderRateLimitError):
            return FailureFactory.rate_limit_exceeded(
                service="LLM provider",
                retry_after=getattr(error, "retry_after", None),
            )
        elif isinstance(error, ProviderAuthError):
            return FailureReport(
                category=FailureCategory.CONFIGURATION_ERROR,
                severity=FailureSeverity.ERROR,
                user_message="Authentication failed. Check your API keys.",
                technical_details=str(error),
                suggestions=[
                    "Verify your API key in settings",
                    "Check that the API key hasn't expired",
                ],
                retryable=False,
                metadata={"error_type": "ProviderAuthError"},
            )
        elif isinstance(error, ProviderConnectionError):
            return FailureFactory.network_error(error, operation="LLM provider call")
        elif isinstance(error, ProviderTimeoutError):
            return FailureFactory.generation_timeout(
                service="LLM provider", timeout_ms=0
            )
        elif isinstance(error, AllProvidersFailed):
            return FailureReport(
                category=FailureCategory.LLM_SERVICE_DOWN,
                severity=FailureSeverity.ERROR,
                user_message="All LLM providers failed. Try again or switch to local model.",
                technical_details=str(error),
                suggestions=[
                    "Check your internet connection",
                    "Try a different provider",
                    "Use local Ollama model",
                ],
                retryable=True,
                metadata={
                    "failures": getattr(error, "failures", []),
                },
            )
        elif isinstance(error, ProviderAPIError):
            return FailureReport(
                category=FailureCategory.LLM_SERVICE_DOWN,
                severity=FailureSeverity.ERROR,
                user_message="The LLM provider returned an error.",
                technical_details=str(error),
                suggestions=["Try again", "Switch provider"],
                retryable=True,
                metadata={
                    "status_code": getattr(error, "status_code", None),
                },
            )
        else:
            return FailureFactory.unknown_error(error, context="provider_call")


# ---------------------------------------------------------------------------
# Failure Logger — persistent failure tracking
# ---------------------------------------------------------------------------

class FailureLogger:
    """
    Log failures to hardened.db for pattern analysis and observability.

    Uses the same database as other hardened infrastructure tables.
    Falls back gracefully if the database is unavailable.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".polly" / "hardened.db"
        self._initialized = False

    def _ensure_table(self) -> None:
        """Create failure_log table if it doesn't exist (lazy init)."""
        if self._initialized:
            return
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS failure_log (
                        failure_id TEXT PRIMARY KEY,
                        category TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        user_message TEXT,
                        technical_details TEXT,
                        suggestions TEXT,
                        retryable INTEGER NOT NULL DEFAULT 0,
                        retry_attempted INTEGER DEFAULT 0,
                        retry_succeeded INTEGER,
                        query_id TEXT,
                        operation TEXT,
                        domain TEXT,
                        persona TEXT,
                        metadata TEXT,
                        occurred_at TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_failure_category
                    ON failure_log(category)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_failure_severity
                    ON failure_log(severity)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_failure_occurred
                    ON failure_log(occurred_at)
                """)
                conn.commit()
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize failure_log table: {e}")

    def log_failure(
        self,
        failure: FailureReport,
        query_id: Optional[str] = None,
        operation: Optional[str] = None,
        domain: Optional[str] = None,
        persona: Optional[str] = None,
    ) -> str:
        """
        Log a failure to the database.

        Returns the failure_id for correlation.
        """
        self._ensure_table()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO failure_log
                    (failure_id, category, severity, user_message, technical_details,
                     suggestions, retryable, query_id, operation, domain, persona,
                     metadata, occurred_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        failure.failure_id,
                        failure.category.value,
                        failure.severity.value,
                        failure.user_message,
                        failure.technical_details,
                        json.dumps(failure.suggestions),
                        1 if failure.retryable else 0,
                        query_id,
                        operation,
                        domain,
                        persona,
                        json.dumps(failure.metadata) if failure.metadata else None,
                        failure.occurred_at.isoformat(),
                    ),
                )
                conn.commit()
            return failure.failure_id
        except Exception as e:
            logger.error(f"Failed to log failure: {e}")
            return failure.failure_id

    def mark_retry_outcome(
        self, failure_id: str, succeeded: bool
    ) -> None:
        """Update a failure record with retry outcome."""
        self._ensure_table()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE failure_log
                    SET retry_attempted = 1, retry_succeeded = ?
                    WHERE failure_id = ?
                    """,
                    (1 if succeeded else 0, failure_id),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update retry outcome: {e}")

    def get_failure_patterns(
        self,
        timeframe_hours: int = 24,
        min_occurrences: int = 3,
    ) -> Dict[str, Dict[str, Any]]:
        """Identify recurring failure patterns within the timeframe."""
        self._ensure_table()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT category, COUNT(*) as count,
                           SUM(CASE WHEN retry_attempted = 1 THEN 1 ELSE 0 END) as retries,
                           SUM(CASE WHEN retry_succeeded = 1 THEN 1 ELSE 0 END) as successes
                    FROM failure_log
                    WHERE occurred_at >= datetime('now', '-' || ? || ' hours')
                    GROUP BY category
                    HAVING count >= ?
                    ORDER BY count DESC
                    """,
                    (timeframe_hours, min_occurrences),
                )

                patterns: Dict[str, Dict[str, Any]] = {}
                for row in cursor.fetchall():
                    category, count, retries, successes = row
                    patterns[category] = {
                        "occurrences": count,
                        "retry_attempts": retries or 0,
                        "retry_successes": successes or 0,
                        "retry_success_rate": (
                            (successes / retries * 100) if retries else 0
                        ),
                    }
                return patterns
        except Exception as e:
            logger.error(f"Failed to get failure patterns: {e}")
            return {}

    def get_recent_failures(
        self,
        limit: int = 20,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent failures, optionally filtered by category."""
        self._ensure_table()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                query = "SELECT * FROM failure_log"
                params: list = []
                if category:
                    query += " WHERE category = ?"
                    params.append(category)
                query += " ORDER BY occurred_at DESC LIMIT ?"
                params.append(limit)

                rows = conn.execute(query, params).fetchall()
                results = []
                for row in rows:
                    d = dict(row)
                    if d.get("suggestions"):
                        try:
                            d["suggestions"] = json.loads(d["suggestions"])
                        except json.JSONDecodeError:
                            pass
                    if d.get("metadata"):
                        try:
                            d["metadata"] = json.loads(d["metadata"])
                        except json.JSONDecodeError:
                            pass
                    results.append(d)
                return results
        except Exception as e:
            logger.error(f"Failed to get recent failures: {e}")
            return []


# ---------------------------------------------------------------------------
# Error Handler — bridge between exceptions and failure reports
# ---------------------------------------------------------------------------

class ErrorHandler:
    """
    Convert exceptions to FailureReports and log them.

    Usage:
        handler = ErrorHandler(FailureLogger())
        try:
            result = await do_something()
        except Exception as e:
            failure = handler.handle(e, context={"query": query})
    """

    def __init__(self, failure_logger: Optional[FailureLogger] = None):
        self.logger = failure_logger or FailureLogger()
        self.factory = FailureFactory()

    def handle(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        query_id: Optional[str] = None,
        operation: Optional[str] = None,
        domain: Optional[str] = None,
        persona: Optional[str] = None,
    ) -> FailureReport:
        """
        Convert an exception to a FailureReport and log it.

        Tries to map the exception to a specific failure category first.
        Falls back to unknown_error.
        """
        ctx = context or {}
        failure: Optional[FailureReport] = None

        # Try provider error mapping first
        try:
            from core.providers.base import ProviderError
            if isinstance(error, ProviderError):
                failure = self.factory.from_provider_error(error)
        except ImportError:
            pass

        # Map other known exception types
        if failure is None:
            if isinstance(error, ConnectionError):
                failure = self.factory.network_error(
                    error, operation=ctx.get("operation", "")
                )
            elif isinstance(error, TimeoutError):
                failure = self.factory.generation_timeout(
                    service=ctx.get("service", "unknown"),
                    timeout_ms=ctx.get("timeout_ms", 0),
                )
            elif isinstance(error, sqlite3.Error):
                failure = self.factory.database_error(error)
            else:
                failure = self.factory.unknown_error(
                    error, context=ctx.get("operation", "")
                )

        # Log to database
        self.logger.log_failure(
            failure,
            query_id=query_id,
            operation=operation or ctx.get("operation"),
            domain=domain or ctx.get("domain"),
            persona=persona or ctx.get("persona"),
        )

        return failure
