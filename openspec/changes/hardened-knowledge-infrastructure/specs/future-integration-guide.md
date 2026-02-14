# Hardened Knowledge Infrastructure — Future Integration Guide

**Purpose:** When building future Polly subsystems, use this guide to integrate with the hardened layer rather than building ad-hoc error handling, retry logic, or validation. The hardened infrastructure is architectural — it should be used by default, not opted into.

---

## Principle: Hardening Happens at Initialization, Not Runtime

Every future subsystem should assume the hardened layer is active. Don't build separate retry logic, error handling, or validation — use the existing infrastructure. If a new operation type is needed, add a policy to `config/retry.yaml` rather than writing custom retry code.

---

## Quick Reference

| Need | Use | Location |
|------|-----|----------|
| Retry with backoff | `RetryManager.execute_with_retry()` | `core/hardened/retry_manager.py` |
| Circuit breaker for flaky service | Add `circuit_breaker` config to retry policy | `config/retry.yaml` |
| Log a failure | `FailureLogger.log_failure()` | `core/hardened/failure.py` |
| Map exception to user message | `ErrorHandler.handle()` or `FailureFactory` methods | `core/hardened/failure.py` |
| Bridge ProviderError | `FailureFactory.from_provider_error()` | `core/hardened/failure.py` |
| Validate retrieved content | `DualValidator.validate()` or `.filter_verified()` | `core/hardened/validator.py` |
| Classify retrieval quality | `RetrievalClassifier.classify()` | `core/hardened/classifier.py` |
| Track operation performance | `track_performance()` / `track_performance_async()` | `core/hardened/performance.py` |
| Check for degradation | `PerformanceDashboard.check_degradation()` | `core/hardened/dashboard.py` |
| Add a new DB table | Create `migrations/NNN_description.sql` | `migrations/` |

---

## Immediate Next Step: Wire Into Polly.query()

The hardened modules are implemented but not yet wired into `core/polly.py`. The integration points are:

```python
# In Polly.query(), after RAG search:
from core.hardened import DualValidator, RetrievalClassifier
from core.hardened import track_performance_async, get_performance_tracker

# After rag_results = await asyncio.to_thread(self.rag.search, ...)
validator = DualValidator()
classifier = RetrievalClassifier()

# Convert rag_results to dicts for validation
result_dicts = [{"content": r.chunk.text, "source_type": r.chunk.source_type,
                 "source_uri": r.chunk.source, "score": r.score} for r in rag_results]

# Validate and classify
filtered, validations = validator.filter_verified(result_dicts, query, domain=domain_names[0] if domain_names else None)
tier_result = classifier.classify(query, filtered, validations, query_domains=domain_names)

# Use tier_result.tier to guide response behavior
# DIRECT → proceed normally
# ADJACENT → add refinement suggestions to response
# ABSENT → acknowledge gap, offer external search
```

This should happen when the existing query path is next modified (e.g., during Query Decomposition or Provider Registry work).

---

## Per-Subsystem Integration Notes

### Agent Swarms (Phase 24a–24e)

**Must use:**
- **RetryManager** for all agent LLM and RAG calls. Add `agent_execution` policy to `config/retry.yaml` with agent-specific parameter adjustments (e.g., retry with different agent, reduce complexity).
- **FailureLogger** for agent failures, timeouts, schema mismatches. Use `FailureCategory.LLM_SERVICE_DOWN` or add agent-specific categories.
- **ContentValidator** on agent outputs before handoff to next agent in workflow. Prevents one agent's bad output from cascading.
- **PerformanceTracker** per-agent and per-workflow. Track `agent_execution`, `agent_handoff`, `workflow_completion`.

**Circuit breaker consideration:** If a specific agent type repeatedly fails, the circuit breaker should prevent Nexus from routing to it. Add per-agent circuit breakers.

**New failure categories to consider:** `AGENT_TIMEOUT`, `AGENT_SCHEMA_MISMATCH`, `WORKFLOW_ESCALATION`.

### DRM — Distributed Reasoning Mesh (Phase 36–36e)

**Must use:**
- **CircuitBreaker** per remote node. When a node is unresponsive, the circuit opens and tasks route to other nodes automatically. Add `drm_task_submission` policy to `config/retry.yaml`.
- **ProvenanceValidator** for content from remote peers. Add `drm_remote_trusted` (MEDIUM_TRUST) and `drm_remote_unknown` (VERIFY_REQUIRED) source types to `config/validation.yaml`.
- **FailureLogger** for node failures, timeout, authentication failures. Maps to `NETWORK_ERROR`, `SOURCE_UNAVAILABLE`, or new DRM-specific categories.
- **PerformanceTracker** per node and per task type. Critical for DRM's intelligent routing — nodes with degraded p95 should receive fewer tasks.

**Key principle:** DRM content from remote nodes enters the same validation pipeline as any other source. Trust comes from PKI (Ed25519 identity verification) but content still passes through DualValidator. A trusted peer can send stale or low-quality content.

### Knowledge Graph + Quality Pipeline (Phase 12a-ext)

**Must use:**
- **ContentValidator** before saving entities/relationships to graph. PII and prompt injection checks prevent contamination of the knowledge base.
- **ProvenanceValidator** scores should be enriched by authority scoring from the knowledge graph. High-authority entities (many inbound connections) should boost provenance scores. This is a bidirectional integration:
  - Knowledge graph → ProvenanceValidator: authority signals improve trust scores
  - ProvenanceValidator → Knowledge graph: trust levels inform entity confidence

**Schema consideration:** The `source_provenance` table in `hardened.db` can track per-source authority scores from the knowledge graph. Add a `migrations/NNN_authority_scoring.sql` migration when implementing.

### Capture System (Phase 30)

**Must use:**
- **ContentValidator** on all captured content before indexing. Especially critical for:
  - URL archival (web content = VERIFY_REQUIRED trust level)
  - OCR from images (error-prone, may contain PII)
  - Voice transcripts (transcription errors could look like injection)
- **ProvenanceValidator** with capture-specific trust levels. Add to `config/validation.yaml`:
  - `capture_voice`: MEDIUM_TRUST
  - `capture_url`: VERIFY_REQUIRED
  - `capture_paste`: MEDIUM_TRUST
  - `capture_code`: HIGH_TRUST (user-written)

**Principle:** Validation happens on capture, not on retrieval. Content entering the knowledge base should already be validated, so RAG retrieval later doesn't need to re-validate it.

### Data Autonomy & Export (Phase 19)

**Must include:**
- `~/.polly/hardened.db` in all backup and export operations. Failure history, performance metrics, and provenance data are part of the user's data.
- **MigrationManager** in import/restore flow. When restoring from backup, migrations should be re-applied to handle schema differences.

**Database consolidation opportunity:** Phase 19 is the right time to consider merging `hardened.db`, `entities.db`, `usage.db`, and `audit.db` into a single `polly.db` with the MigrationManager handling the unified schema. This is noted in the plan but deferred to Phase 19 when export/migration tooling exists.

### Analytics & Insights (Phase 35)

**Must consume:**
- **PerformanceTracker** data from `hardened.db` → `performance_metrics` table. Analytics should query percentiles for:
  - RAG retrieval latency trends
  - LLM generation latency by provider
  - Success rates by operation, domain, persona
  - Token usage distribution
- **FailureLogger** patterns from `failure_log` table. Analytics should surface:
  - Recurring failure categories
  - Retry success rates
  - Circuit breaker open/close history
  - Correlation between failures and performance degradation

**Visualization opportunities:** p95 latency over time, failure category distribution, circuit breaker state timeline, retrieval tier distribution (DIRECT/ADJACENT/ABSENT over time).

### Constitutional Epistemology (Foundation Layer)

**Connects to:**
- **ContentValidator.epistemological_enrichment** field. When the constitutional layer is implemented (`core/constitutional/layer.py`), the `enrich_with_structural_analysis` and `enrich_with_material_analysis` signals from ContentValidator should trigger injection of constitutional analysis context into the prompt.
- The flow: ContentValidator detects scapegoat/essentialist pattern → sets `epistemological_enrichment` → prompt builder checks this field → injects constitutional mental models (Cui Bono, Historical Construction, Structural Analysis) with higher priority.

**Principle:** The constitutional layer operates at the prompt level. The hardened validator operates at the retrieval level. They are complementary — the validator flags content that needs deeper analysis, the constitutional layer provides the analytical framework.

### Query Decomposition + Split Routing (Core Framework Refinement)

**Must use:**
- Each sub-query from decomposition should go through the full hardened pipeline independently: RAG → DualValidator → RetrievalClassifier → RetryManager → generation.
- Sub-queries may have different domains (a complex question about "Docker networking for my Signals project" decomposes into Sigils + Signals sub-queries). Each gets domain-aware classification.
- The synthesis step that merges sub-query results should also pass through ContentValidator to check the merged output.

### Provider Registry (Core Framework Refinement)

**Must integrate:**
- **CircuitBreaker** state should inform provider health. A provider whose circuit breaker is OPEN should show as "unhealthy" in the registry UI.
- **PerformanceTracker** data feeds provider health metrics. p95 latency and success rate per provider.
- Provider enable/disable toggles should respect circuit breaker state — don't let users enable a provider whose circuit is open.

---

## Adding New Failure Categories

When a new subsystem needs failure types not in the current taxonomy:

1. Add to `FailureCategory` enum in `core/hardened/failure.py`
2. Add factory method to `FailureFactory`
3. Update `migrations/` with any new DB columns needed
4. Consider: is this a hard block (security) or enrichment (epistemological)? Default to enrichment unless it's infrastructure security.

## Adding New Retry Policies

When a new operation type needs retry:

1. Add policy to `config/retry.yaml`
2. Add `parameter_adjustments` per attempt if the operation has tunable parameters
3. Add error condition mappings to `_ERROR_CONDITION_MAP` in `retry_manager.py` if new exception types exist
4. Consider whether a circuit breaker is needed (yes for external services, no for local operations)

## Adding New Source Types

When content comes from a new source (e.g., DRM remote, capture voice):

1. Add to `DEFAULT_SOURCE_TRUST` in `core/hardened/validator.py`
2. Add to `config/validation.yaml` → `provenance.trust_levels`
3. Add staleness threshold if applicable

---

## Anti-Patterns to Avoid

1. **Don't write ad-hoc try/except retry loops.** Use `RetryManager.execute_with_retry()`.
2. **Don't swallow errors silently.** Use `ErrorHandler.handle()` to log and categorize.
3. **Don't build content filters.** Use epistemological enrichment per the ethics spec.
4. **Don't duplicate validation.** If content enters the knowledge base validated, don't re-validate on retrieval. Validate at ingestion.
5. **Don't create new SQLite databases.** Add tables to `hardened.db` via `migrations/`.
6. **Don't track performance with ad-hoc timing code.** Use `track_performance()` context manager.
