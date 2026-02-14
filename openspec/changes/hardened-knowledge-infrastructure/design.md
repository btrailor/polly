# Hardened Knowledge Infrastructure — Design

## Architecture

The hardened infrastructure layer inserts into the existing query hot path at specific points:

```
User → Polly.query()
  ├─ DomainEngine.detect_domains()
  ├─ PersonaManager (resolve persona)
  ├─ UnifiedRAG.search()
  │     ↓
  ├─ [NEW] RetrievalClassifier (DIRECT/ADJACENT/ABSENT)
  ├─ [NEW] DualValidator (provenance + content)
  │     ├─ VERIFIED → continue
  │     ├─ REJECTED → FailureFactory → FailureLogger
  │     └─ TRUSTED_SOURCE_POOR_CONTENT → log, skip
  ├─ _gather_context() (ContextContributor protocol — unchanged)
  ├─ Build augmented prompt
  ├─ [NEW] RetryManager wraps router_v2.route()
  │     ├─ Success → continue
  │     └─ All retries failed → FailureFactory → FailureLogger
  ├─ LLM Response (streaming)
  ├─ _record_routing_outcome()
  └─ [NEW] PerformanceTracker.record()
```

### Design Principles

1. **Pre-filter, not ContextContributor**: DualValidator runs between RAG search and `_gather_context()`, not as a ContextContributor. Only validated results enter the context pipeline.
2. **Extend, don't replace**: FailureCategory wraps existing `ProviderError` hierarchy. RetryManager consolidates existing retry fragments. New database alongside existing ones.
3. **Epistemological alignment, not content filtering**: Per ethics spec, constitutional checks trigger deeper analysis, not blocking. Hard blocks reserved for PII and prompt injection only.
4. **Domain-aware classification**: Three-tier retrieval respects Polly's domain system. Cross-domain matches are ADJACENT, not DIRECT.

## Database: `~/.polly/hardened.db`

New SQLite database with WAL mode. Separate from existing databases to avoid migration risk. Schema managed by MigrationManager.

Tables:
- `schema_version` — Migration tracking
- `source_provenance` — Source trust levels and verification history
- `content_validations` — Content quality check results
- `retrieval_events` — Three-tier classification logs with domain/persona
- `retry_events` — Retry attempt tracking
- `circuit_breaker_state` — Circuit breaker status per operation
- `failure_log` — Observable failure reports
- `performance_metrics` — Operation timing with percentile support

## Key Types

### FailureCategory (extends ProviderError hierarchy)

```python
class FailureCategory(Enum):
    # RAG Retrieval
    NO_DOCUMENTS_FOUND = "no_documents_found"
    LOW_RELEVANCE = "low_relevance"
    EMBEDDING_SERVICE_DOWN = "embedding_service_down"
    # Constitutional (epistemological)
    SCAPEGOAT_NARRATIVE_DETECTED = "scapegoat_narrative_detected"
    ESSENTIALIST_CLAIM_DETECTED = "essentialist_claim_detected"
    # Security (hard blocks)
    PII_DETECTED = "pii_detected"
    PROMPT_INJECTION_DETECTED = "prompt_injection_detected"
    # Generation
    CONTEXT_TOO_LARGE = "context_too_large"
    LLM_SERVICE_DOWN = "llm_service_down"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    GENERATION_TIMEOUT = "generation_timeout"
    # System
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    status: str       # VERIFIED, TRUSTED_SOURCE_POOR_CONTENT, UNTRUSTED_SOURCE_GOOD_CONTENT, REJECTED
    confidence: float # 0.0-1.0
    provenance_score: float
    content_score: float
    reason: str       # Empty if VERIFIED
    metadata: dict
```

### RetrievalTier

```python
class RetrievalTier(Enum):
    DIRECT = "direct"       # High-confidence, verified answer
    ADJACENT = "adjacent"   # Related but not direct
    ABSENT = "absent"       # No relevant information
```

## Constitutional Check Reconciliation

The ethics spec (openspec/specs/ethics/spec.md) explicitly rejects content filtering. Constitutional checks in the Content Validator are reframed:

| Original Spec | Polly Adaptation | Behavior |
|---|---|---|
| harmful_ideology_detection | scapegoat_narrative_detection | Triggers deeper retrieval + structural analysis context, NOT blocking |
| personal_info_detection | pii_detection | Hard block (infrastructure security) |
| fact_contradiction_check | fact_contradiction_check | Soft warning, allows override |
| temporal_relevance_check | staleness_detection | Soft warning, marks as potentially outdated |

Scapegoat detection adds structural analysis context (cui bono, material analysis) rather than blocking. This aligns with the ethics spec principle: "build analytical capacity, don't filter content."

## Source Trust Levels (Polly-specific)

```yaml
trust_levels:
  obsidian_vault: HIGH_TRUST
  curriculum_exercises: HIGH_TRUST
  github_personal: HIGH_TRUST
  pattern_derived: MEDIUM_TRUST
  entity_graph: MEDIUM_TRUST
  mem0_memories: MEDIUM_TRUST
  github_starred: MEDIUM_TRUST
  web_search: VERIFY_REQUIRED
  external_api: LOW_TRUST
  unknown: UNTRUSTED
```

## Impact on Existing Code

The hardened modules are implemented as a standalone package (`core/hardened/`). Wiring into the query hot path is a **separate integration step** — the modules are ready but `core/polly.py` has not been modified yet.

### Integration pending (next change):

- `core/polly.py` — `query()` method gains DualValidator + RetrievalClassifier between RAG search and `_gather_context()`; RetryManager wraps router call; PerformanceTracker records at method end. See [future-integration-guide.md](specs/future-integration-guide.md) for sample code.
- `core/rag.py` — Existing embedding retry logic delegates to RetryManager
- `config/config.yaml` — Existing `fallback.retry_on_error` becomes alias into retry.yaml

### Already integrated:

- `core/providers/base.py` — FailureCategory maps from existing ProviderError types via `FailureFactory.from_provider_error()`
- No frontend changes required

### Future subsystem integration:

All planned subsystems (Agent Swarms, DRM, Knowledge Graph, Capture, Analytics, Data Autonomy) must use the hardened layer. See [future-integration-guide.md](specs/future-integration-guide.md) for per-subsystem requirements.
