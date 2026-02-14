"""
Retry Manager with Circuit Breaker
Hardened Knowledge Infrastructure — Wave 1

Unified retry strategy across RAG retrieval, LLM generation, and external
API calls.  Consolidates fragments from core/rag.py (embedding retries) and
provider-level retry_after handling.

Design:
- Max 3 attempts per operation (configurable)
- Exponential backoff with jitter
- Operation-specific parameter adjustments per attempt
  (e.g. relax similarity threshold, reduce max_tokens)
- Circuit breaker prevents cascading failures
- All retry events logged to hardened.db
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Dict, List, Tuple
from pathlib import Path
import asyncio
import random
import time
import threading
import sqlite3
import json
import uuid
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retry Outcome
# ---------------------------------------------------------------------------

class RetryOutcome(Enum):
    SUCCESS = "success"
    FAILED_ALL_ATTEMPTS = "failed_all_attempts"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"


@dataclass
class RetryResult:
    """Result of a retry-managed operation."""
    outcome: RetryOutcome
    result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.outcome == RetryOutcome.SUCCESS


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------

class CircuitBreakerState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing — reject immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker prevents cascading failures by short-circuiting
    requests to a failing service.

    States:
      CLOSED  — normal; failures counted
      OPEN    — all requests rejected immediately; waits for timeout
      HALF_OPEN — allows one probe request; success → CLOSED, fail → OPEN
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_duration_s: int = 60,
        half_open_requests: int = 1,
    ):
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration_s
        self.half_open_requests = half_open_requests

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()

    def is_open(self) -> bool:
        """Check if circuit breaker is blocking requests."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if (
                    self.last_failure_time
                    and time.time() - self.last_failure_time >= self.timeout_duration
                ):
                    # Timeout elapsed — transition to half-open
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    return False
                return True
            return False

    def record_success(self) -> None:
        """Record successful request."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_requests:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker closed — service recovered")
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed request and potentially open circuit."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker opened — half-open probe failed")
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(
                    f"Circuit breaker opened after {self.failure_count} failures"
                )

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state for observability."""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time,
            }


# ---------------------------------------------------------------------------
# Default Retry Policies
# ---------------------------------------------------------------------------

DEFAULT_RETRY_POLICIES: Dict[str, Dict[str, Any]] = {
    "rag_retrieval": {
        "max_attempts": 3,
        "initial_delay_ms": 100,
        "backoff_multiplier": 2.0,
        "max_delay_ms": 2000,
        "jitter": True,
        "retry_on": [
            "timeout",
            "connection_error",
            "embedding_service_unavailable",
        ],
        "parameter_adjustments": {
            "attempt_1": {"similarity_threshold": 0.8, "top_k": 5},
            "attempt_2": {"similarity_threshold": 0.6, "top_k": 10},
            "attempt_3": {
                "similarity_threshold": 0.4,
                "top_k": 20,
                "enable_fuzzy_match": True,
            },
        },
    },
    "llm_generation": {
        "max_attempts": 3,
        "initial_delay_ms": 500,
        "backoff_multiplier": 1.5,
        "max_delay_ms": 5000,
        "jitter": True,
        "retry_on": [
            "rate_limit",
            "service_unavailable",
            "timeout",
        ],
        "parameter_adjustments": {
            "attempt_1": {"temperature": 0.7, "max_tokens": 2048},
            "attempt_2": {"temperature": 0.5, "max_tokens": 1024},
            "attempt_3": {
                "temperature": 0.3,
                "max_tokens": 512,
                "fallback_to_local_model": True,
            },
        },
    },
    "context_assembly": {
        "max_attempts": 2,
        "initial_delay_ms": 0,
        "backoff_multiplier": 1.0,
        "max_delay_ms": 0,
        "jitter": False,
        "retry_on": ["context_too_large"],
        "parameter_adjustments": {
            "attempt_1": {"max_context_tokens": 16000, "summarization": "none"},
            "attempt_2": {
                "max_context_tokens": 8000,
                "summarization": "aggressive",
                "chunk_strategy": "most_relevant_only",
            },
        },
    },
    "external_api": {
        "max_attempts": 3,
        "initial_delay_ms": 1000,
        "backoff_multiplier": 2.0,
        "max_delay_ms": 10000,
        "jitter": True,
        "retry_on": [
            "rate_limit",
            "service_unavailable",
            "timeout",
            "connection_error",
        ],
        "circuit_breaker": {
            "failure_threshold": 5,
            "timeout_duration_s": 60,
            "half_open_requests": 1,
        },
    },
}

# Map exception class names to retry condition strings
_ERROR_CONDITION_MAP: Dict[str, str] = {
    "TimeoutError": "timeout",
    "asyncio.TimeoutError": "timeout",
    "ConnectionError": "connection_error",
    "ConnectionRefusedError": "connection_error",
    "ProviderRateLimitError": "rate_limit",
    "ProviderConnectionError": "connection_error",
    "ProviderTimeoutError": "timeout",
    "ProviderAPIError": "service_unavailable",
    "AllProvidersFailed": "service_unavailable",
    "EmbeddingServiceError": "embedding_service_unavailable",
    "ContextTooLargeError": "context_too_large",
    "OSError": "connection_error",
}


# ---------------------------------------------------------------------------
# Retry Manager
# ---------------------------------------------------------------------------

class RetryManager:
    """
    Execute operations with configurable retry logic.

    Usage:
        manager = RetryManager()
        result = await manager.execute_with_retry(
            "rag_retrieval",
            retrieve_documents,
            query=query,
            domain=domain,
        )
        if result.success:
            documents = result.result
    """

    def __init__(
        self,
        policies: Optional[Dict[str, Dict[str, Any]]] = None,
        db_path: Optional[Path] = None,
    ):
        self.policies = policies or DEFAULT_RETRY_POLICIES
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.db_path = db_path or Path.home() / ".polly" / "hardened.db"
        self._db_initialized = False

    def _get_policy(self, operation: str) -> Dict[str, Any]:
        """Get retry policy for an operation, falling back to defaults."""
        return self.policies.get(operation, {
            "max_attempts": 1,
            "initial_delay_ms": 0,
            "backoff_multiplier": 1.0,
            "max_delay_ms": 0,
            "jitter": False,
            "retry_on": [],
        })

    def _get_circuit_breaker(self, operation: str) -> Optional[CircuitBreaker]:
        """Get or create circuit breaker for an operation, if configured."""
        policy = self._get_policy(operation)
        cb_config = policy.get("circuit_breaker")
        if not cb_config:
            return None
        if operation not in self.circuit_breakers:
            self.circuit_breakers[operation] = CircuitBreaker(
                failure_threshold=cb_config.get("failure_threshold", 5),
                timeout_duration_s=cb_config.get("timeout_duration_s", 60),
                half_open_requests=cb_config.get("half_open_requests", 1),
            )
        return self.circuit_breakers[operation]

    async def execute_with_retry(
        self,
        operation: str,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> RetryResult:
        """
        Execute a function with retry logic.

        Args:
            operation: Policy name (e.g. 'rag_retrieval', 'llm_generation')
            func: Async or sync function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func (may be adjusted per attempt)

        Returns:
            RetryResult with outcome, result, and metadata
        """
        policy = self._get_policy(operation)
        max_attempts = policy.get("max_attempts", 1)

        # Check circuit breaker
        cb = self._get_circuit_breaker(operation)
        if cb and cb.is_open():
            logger.warning(f"Circuit breaker open for '{operation}' — rejecting")
            return RetryResult(
                outcome=RetryOutcome.CIRCUIT_BREAKER_OPEN,
                metadata={
                    "operation": operation,
                    "reason": "Circuit breaker is open",
                    "circuit_breaker": cb.get_state(),
                },
            )

        errors: List[Dict[str, Any]] = []
        attempts_made = 0

        for attempt in range(1, max_attempts + 1):
            attempts_made = attempt

            # Apply parameter adjustments for this attempt
            adjusted_kwargs = self._apply_adjustments(policy, attempt, kwargs)

            try:
                start_time = time.time()

                # Support both sync and async functions
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **adjusted_kwargs)
                else:
                    result = func(*args, **adjusted_kwargs)

                execution_time_ms = (time.time() - start_time) * 1000

                # Success
                if cb:
                    cb.record_success()

                self._log_retry_event(
                    operation=operation,
                    outcome="success",
                    attempts=attempts_made,
                    total_time_ms=execution_time_ms,
                    errors=errors,
                    final_params=adjusted_kwargs,
                )

                return RetryResult(
                    outcome=RetryOutcome.SUCCESS,
                    result=result,
                    metadata={
                        "attempts": attempts_made,
                        "execution_time_ms": round(execution_time_ms, 1),
                        "final_parameters": {
                            k: v for k, v in adjusted_kwargs.items()
                            if k in (policy.get("parameter_adjustments", {})
                                     .get(f"attempt_{attempt}", {}))
                        },
                    },
                )

            except Exception as e:
                error_type = type(e).__name__
                error_info = {
                    "attempt": attempt,
                    "error_type": error_type,
                    "error_message": str(e)[:500],
                }
                errors.append(error_info)
                logger.warning(
                    f"Retry {attempt}/{max_attempts} for '{operation}' failed: "
                    f"{error_type}: {str(e)[:200]}"
                )

                # Check if retryable
                if not self._is_retryable(policy, error_type):
                    if cb:
                        cb.record_failure()
                    self._log_retry_event(
                        operation=operation,
                        outcome="failed_all_attempts",
                        attempts=attempts_made,
                        total_time_ms=0,
                        errors=errors,
                        reason=f"Non-retryable error: {error_type}",
                    )
                    return RetryResult(
                        outcome=RetryOutcome.FAILED_ALL_ATTEMPTS,
                        metadata={
                            "attempts": attempts_made,
                            "errors": errors,
                            "reason": f"Non-retryable error: {error_type}",
                        },
                    )

                # Last attempt failed
                if attempt == max_attempts:
                    if cb:
                        cb.record_failure()
                    self._log_retry_event(
                        operation=operation,
                        outcome="failed_all_attempts",
                        attempts=attempts_made,
                        total_time_ms=0,
                        errors=errors,
                        reason="Exhausted all retry attempts",
                    )
                    return RetryResult(
                        outcome=RetryOutcome.FAILED_ALL_ATTEMPTS,
                        metadata={
                            "attempts": attempts_made,
                            "errors": errors,
                            "reason": "Exhausted all retry attempts",
                        },
                    )

                # Wait before next attempt
                delay_ms = self._calculate_delay(policy, attempt)
                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)

        # Should not reach here, but safety fallback
        return RetryResult(
            outcome=RetryOutcome.FAILED_ALL_ATTEMPTS,
            metadata={"attempts": attempts_made, "errors": errors},
        )

    def _apply_adjustments(
        self,
        policy: Dict[str, Any],
        attempt: int,
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply parameter adjustments for the given attempt number."""
        adjustments = (
            policy
            .get("parameter_adjustments", {})
            .get(f"attempt_{attempt}", {})
        )
        if not adjustments:
            return kwargs
        # Merge: adjustments override kwargs
        return {**kwargs, **adjustments}

    def _calculate_delay(self, policy: Dict[str, Any], attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        initial = policy.get("initial_delay_ms", 100)
        multiplier = policy.get("backoff_multiplier", 2.0)
        max_delay = policy.get("max_delay_ms", 5000)

        delay = initial * (multiplier ** (attempt - 1))
        delay = min(delay, max_delay)

        if policy.get("jitter", False):
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(delay, 0)

    def _is_retryable(self, policy: Dict[str, Any], error_type: str) -> bool:
        """Check if this error type should trigger a retry."""
        retry_on = policy.get("retry_on", [])
        if not retry_on:
            return False

        # Direct match from error condition map
        condition = _ERROR_CONDITION_MAP.get(error_type)
        if condition and condition in retry_on:
            return True

        # Fallback: lowercase error type name
        return error_type.lower() in retry_on

    def _log_retry_event(
        self,
        operation: str,
        outcome: str,
        attempts: int,
        total_time_ms: float = 0,
        errors: Optional[List[Dict]] = None,
        final_params: Optional[Dict] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Log retry event to hardened.db (best-effort)."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS retry_events (
                        event_id TEXT PRIMARY KEY,
                        operation TEXT NOT NULL,
                        outcome TEXT NOT NULL,
                        attempts_made INTEGER,
                        total_time_ms REAL,
                        errors TEXT,
                        final_parameters TEXT,
                        reason TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute(
                    """
                    INSERT INTO retry_events
                    (event_id, operation, outcome, attempts_made, total_time_ms,
                     errors, final_parameters, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        operation,
                        outcome,
                        attempts,
                        round(total_time_ms, 1),
                        json.dumps(errors) if errors else None,
                        json.dumps(final_params) if final_params else None,
                        reason,
                    ),
                )
                conn.commit()
        except Exception as e:
            # Best effort — don't let logging failures break the pipeline
            logger.debug(f"Failed to log retry event: {e}")

    def get_circuit_breaker_states(self) -> Dict[str, Dict[str, Any]]:
        """Get state of all circuit breakers for observability."""
        return {
            op: cb.get_state()
            for op, cb in self.circuit_breakers.items()
        }


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_retry_manager: Optional[RetryManager] = None


def get_retry_manager() -> RetryManager:
    """Get global RetryManager instance."""
    global _retry_manager
    if _retry_manager is None:
        _retry_manager = RetryManager()
    return _retry_manager


def init_retry_manager(
    policies: Optional[Dict[str, Dict[str, Any]]] = None,
    db_path: Optional[Path] = None,
) -> RetryManager:
    """Initialize global RetryManager with optional custom policies."""
    global _retry_manager
    _retry_manager = RetryManager(policies=policies, db_path=db_path)
    return _retry_manager
