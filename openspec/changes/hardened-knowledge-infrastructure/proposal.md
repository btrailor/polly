# Hardened Knowledge Infrastructure — Proposal

**Tier:** Cross-cutting (benefits Tiers 1–5)  
**Scope:** Backend  
**Status:** In progress  
**Created:** February 2026

---

## What We're Doing

Building a hardened infrastructure layer beneath Polly's query pipeline. Inspired by OPSEC defense-in-depth principles and dual-phenomenology site checking, this change formalizes, unifies, and extends the existing fragments of retry logic, error handling, validation, and observability into a coherent system.

Six interlocking subsystems:

1. **Observable Failure Modes** — Explicit failure taxonomy with actionable context, replacing ad-hoc exception handling
2. **Retry Manager + Circuit Breaker** — Unified retry strategy across RAG retrieval, LLM generation, and external APIs, consolidating fragments in `core/rag.py` and `core/providers/`
3. **Dual-Phenomenology Validation** — Independent provenance (source trust) and content (quality/safety) checks on every RAG retrieval result
4. **Three-Tier Retrieval Classification** — Replace binary found/not-found with DIRECT/ADJACENT/ABSENT tiers that guide user experience and next actions
5. **Performance Metrics with Percentiles** — p50/p90/p95/p99 tracking for all pipeline operations, enabling degradation detection
6. **Persistent State with Schema Migration** — SQLite database (`hardened.db`) with automatic schema evolution for all hardened infrastructure tables

## Why

Polly's current architecture has the right shape but lacks hardened infrastructure:

- Retry logic exists in fragments (`core/rag.py` embedding retries, provider `retry_after`) but isn't unified
- Error handling uses try/except blocks that log and continue, with no structured failure taxonomy
- RAG results are binary (found or not), losing the rich middle ground of "related but not direct" answers
- No systematic observability for pipeline performance — can't detect degradation
- No schema migration system — database changes require manual intervention

The OPSEC principle applies: security (and reliability) that requires manual steps isn't security — it's a suggestion. These protections must be architectural, active by default, and observable.

## What's Done So Far

Existing fragments this change unifies:

- ✅ Provider error hierarchy (`libs/polly-routing/polly_routing/providers/base.py`)
- ✅ Embedding retry with backoff (`core/rag.py`)
- ✅ Audit logging (`core/audit_logger.py`)
- ✅ Autonomy metrics (`core/autonomy_metrics.py`)
- ✅ Security policy with PII/prompt injection config (`config/security_policy.yaml`)
- ✅ Input validation middleware (`interfaces/server.py`)

## Implementation Waves

### Wave 1 — Observable Failure Modes + Retry Manager
- `core/hardened/failure.py` — FailureCategory enum, FailureReport, FailureFactory
- `core/hardened/retry_manager.py` — RetryManager with circuit breaker, operation-specific policies
- `config/retry.yaml` — Retry policies per operation

### Wave 2 — Dual-Phenomenology Validation + Three-Tier Classification
- `core/hardened/validator.py` — DualValidator (provenance + content checks)
- `core/hardened/classifier.py` — RetrievalClassifier (DIRECT/ADJACENT/ABSENT)
- `config/validation.yaml` — Trust levels and thresholds
- Integration into `Polly.query()` between RAG search and `_gather_context()`

### Wave 3 — Performance Metrics + Observability
- `core/hardened/performance.py` — PerformanceTracker, percentile stats, context manager
- `core/hardened/dashboard.py` — PerformanceDashboard, report generation, degradation detection

### Wave 4 — Persistent State + Schema Migration
- `core/hardened/db.py` — Database initialization (WAL mode, foreign keys)
- `core/hardened/migration.py` — MigrationManager
- `migrations/001_initial_hardened.sql` — Initial schema

## Reference

- Ethics spec: `openspec/specs/ethics/spec.md` (constitutional epistemology — NOT content filtering)
- Architecture spec: `openspec/specs/architecture/spec.md` (query hot path)
- Security spec: `openspec/specs/security/spec.md` (Phase 23.5)
- Provider error hierarchy: `libs/polly-routing/polly_routing/providers/base.py`
