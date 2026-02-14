-- Migration: 001
-- Description: Initial hardened knowledge infrastructure schema
-- Version: 1
--
-- Tables:
--   schema_version         — Migration version tracking
--   source_provenance      — Source trust levels and verification history
--   content_validations    — Content quality check results
--   retrieval_events       — Three-tier classification logs
--   retry_events           — Retry attempt tracking
--   circuit_breaker_state  — Circuit breaker status per operation
--   failure_log            — Observable failure reports
--   performance_metrics    — Operation timing with percentile support

-- =====================================================================
-- Schema Version Tracking
-- =====================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- =====================================================================
-- Source Provenance — Source trust levels and verification history
-- =====================================================================

CREATE TABLE IF NOT EXISTS source_provenance (
    source_id TEXT PRIMARY KEY,
    source_uri TEXT NOT NULL,
    source_type TEXT NOT NULL,
    trust_level TEXT CHECK(trust_level IN (
        'HIGH_TRUST', 'MEDIUM_TRUST', 'LOW_TRUST',
        'VERIFY_REQUIRED', 'UNTRUSTED'
    )),
    last_verified TEXT,
    verification_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    average_usefulness REAL,
    domain TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prov_trust_level ON source_provenance(trust_level);
CREATE INDEX IF NOT EXISTS idx_prov_last_verified ON source_provenance(last_verified);
CREATE INDEX IF NOT EXISTS idx_prov_source_type ON source_provenance(source_type);
CREATE INDEX IF NOT EXISTS idx_prov_domain ON source_provenance(domain);

-- =====================================================================
-- Content Validations — Content quality check results
-- =====================================================================

CREATE TABLE IF NOT EXISTS content_validations (
    validation_id TEXT PRIMARY KEY,
    document_id TEXT,
    chunk_id TEXT,
    query_hash TEXT NOT NULL,
    constitutional_pass INTEGER NOT NULL DEFAULT 1,
    content_score REAL,
    relevance_score REAL,
    blocking_reason TEXT,
    warnings TEXT,
    quality_metrics TEXT,
    domain TEXT,
    persona TEXT,
    validated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cv_constitutional ON content_validations(constitutional_pass);
CREATE INDEX IF NOT EXISTS idx_cv_query_hash ON content_validations(query_hash);
CREATE INDEX IF NOT EXISTS idx_cv_validated_at ON content_validations(validated_at);
CREATE INDEX IF NOT EXISTS idx_cv_domain ON content_validations(domain);

-- =====================================================================
-- Retrieval Events — Three-tier classification logs
-- =====================================================================

CREATE TABLE IF NOT EXISTS retrieval_events (
    event_id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    query_hash TEXT NOT NULL,
    tier TEXT CHECK(tier IN ('DIRECT', 'ADJACENT', 'ABSENT')),
    confidence REAL,
    persona TEXT,
    domain TEXT,

    -- Retrieval metrics
    docs_searched INTEGER,
    docs_retrieved INTEGER,
    best_match_score REAL,
    retrieval_time_ms INTEGER,

    -- Validation results
    provenance_pass_count INTEGER,
    content_pass_count INTEGER,
    constitutional_blocks INTEGER,

    -- User action taken
    user_action TEXT,

    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_re_tier ON retrieval_events(tier);
CREATE INDEX IF NOT EXISTS idx_re_query_hash ON retrieval_events(query_hash);
CREATE INDEX IF NOT EXISTS idx_re_confidence ON retrieval_events(confidence);
CREATE INDEX IF NOT EXISTS idx_re_created_at ON retrieval_events(created_at);
CREATE INDEX IF NOT EXISTS idx_re_persona_domain ON retrieval_events(persona, domain);

-- =====================================================================
-- Retry Events — Retry attempt tracking
-- =====================================================================

CREATE TABLE IF NOT EXISTS retry_events (
    event_id TEXT PRIMARY KEY,
    operation TEXT NOT NULL,
    outcome TEXT CHECK(outcome IN ('success', 'failed_all_attempts', 'circuit_breaker_open')),
    attempts_made INTEGER,
    total_time_ms REAL,
    errors TEXT,
    final_parameters TEXT,
    reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_retry_operation ON retry_events(operation);
CREATE INDEX IF NOT EXISTS idx_retry_outcome ON retry_events(outcome);
CREATE INDEX IF NOT EXISTS idx_retry_created_at ON retry_events(created_at);

-- =====================================================================
-- Circuit Breaker State — Per-operation circuit breaker status
-- =====================================================================

CREATE TABLE IF NOT EXISTS circuit_breaker_state (
    operation TEXT PRIMARY KEY,
    state TEXT CHECK(state IN ('closed', 'open', 'half_open')),
    failure_count INTEGER DEFAULT 0,
    last_failure TEXT,
    opened_at TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- Failure Log — Observable failure reports
-- =====================================================================

CREATE TABLE IF NOT EXISTS failure_log (
    failure_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('error', 'warning', 'info')),
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
);

CREATE INDEX IF NOT EXISTS idx_fl_category ON failure_log(category);
CREATE INDEX IF NOT EXISTS idx_fl_severity ON failure_log(severity);
CREATE INDEX IF NOT EXISTS idx_fl_occurred_at ON failure_log(occurred_at);
CREATE INDEX IF NOT EXISTS idx_fl_domain ON failure_log(domain);

-- =====================================================================
-- Performance Metrics — Operation timing for percentile analysis
-- =====================================================================

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
);

CREATE INDEX IF NOT EXISTS idx_pm_operation ON performance_metrics(operation);
CREATE INDEX IF NOT EXISTS idx_pm_recorded_at ON performance_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_pm_success ON performance_metrics(success);

-- =====================================================================
-- Record this migration
-- =====================================================================

INSERT INTO schema_version (version, description) VALUES
(1, 'Initial hardened knowledge infrastructure schema');
