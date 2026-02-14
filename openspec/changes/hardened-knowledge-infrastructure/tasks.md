# Hardened Knowledge Infrastructure — Tasks

## Wave 1: Observable Failure Modes + Retry Manager

- [x] Task 1: Create `core/hardened/__init__.py`
- [x] Task 2: Create `core/hardened/failure.py` — FailureCategory enum, FailureReport dataclass, FailureFactory
- [x] Task 3: Create `core/hardened/retry_manager.py` — RetryManager with CircuitBreaker, exponential backoff, jitter, operation-specific parameter adjustments
- [x] Task 4: Create `config/retry.yaml` — Retry policies for rag_retrieval, llm_generation, context_assembly, external_api

## Wave 2: Dual-Phenomenology Validation + Three-Tier Classification

- [x] Task 5: Create `core/hardened/validator.py` — ProvenanceValidator, ContentValidator, DualValidator
- [x] Task 6: Create `core/hardened/classifier.py` — RetrievalClassifier (DIRECT/ADJACENT/ABSENT), domain-aware tier assignment
- [x] Task 7: Create `config/validation.yaml` — Trust levels, score thresholds, constitutional check config

## Wave 3: Performance Metrics + Observability

- [x] Task 8: Create `core/hardened/performance.py` — PerformanceTracker, percentile calculation (stdlib statistics), track_performance context manager, PerformanceDashboard
- [x] Task 9: Create `core/hardened/dashboard.py` — Report generation, degradation detection, JSON export

## Wave 4: Persistent State + Schema Migration

- [x] Task 10: Create `core/hardened/db.py` — Database initialization, WAL mode, foreign keys
- [x] Task 11: Create `core/hardened/migration.py` — MigrationManager (apply, current_version, available_migrations)
- [x] Task 12: Create `migrations/001_initial_hardened.sql` — Complete schema with all tables

## Spec Updates

- [x] Task 13: Update `openspec/specs/architecture/spec.md` — Add hardened infrastructure layer
- [x] Task 14: Update `openspec/specs/rag/spec.md` — Add dual validation and three-tier classification
- [x] Task 15: Update `openspec/specs/security/spec.md` — Add hardened failure logging and retry
- [x] Task 16: Update `openspec/specs/project/roadmap.md` — Add cross-cutting entry
