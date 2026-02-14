# Security (OpenSpec)

Source of truth for security behavior. Current + planned (Phase 23.5): [docs/SECURITY.md](../../../docs/SECURITY.md). Phase 23.5 spec: [docs/planning/phases/phase-23.5/](../../../docs/planning/phases/phase-23.5/).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Secrets (Keychain, env), API keys | ✅ Implemented | Phase 5 |
| Code execution (Pyodide sandbox) | ✅ Implemented | Phase 23.5; client-side Pyodide, server validates |
| Capability Broker | ✅ Implemented | core/capability_broker.py; api_gateway, shell_executor |
| Pyodide sandbox | ✅ Implemented | core/sandbox.py; electron pyodide-loader/worker |
| Package allowlist + approval workflow | ✅ Implemented | core/package_detector.py, approved_packages.yaml, package-approval-dialog.js |
| CORS from security policy | ✅ Implemented | server.py loads security_policy.get_cors_config() |
| Audit logging | ✅ Implemented | core/audit_logger.py, ~/.polly/audit.db |
| Hardened failure logging | ✅ Implemented | core/hardened/failure.py → ~/.polly/hardened.db |
| Retry manager + circuit breaker | ✅ Implemented | core/hardened/retry_manager.py; config/retry.yaml |
| PII detection in RAG content | ✅ Implemented | core/hardened/validator.py ContentValidator |
| Prompt injection detection in RAG content | ✅ Implemented | core/hardened/validator.py ContentValidator |
| Performance observability | ✅ Implemented | core/hardened/performance.py, dashboard.py |
| Content sanitization (prompt injection, PII) | ✅ Partial | Hardened validator checks RAG content; server-level sanitizer not yet implemented |
| API key context managers / cleanup | 📐 Config only | security_policy api_keys section; not verified in providers |
| Agent Swarms execution context brokering | 💭 Vision | Phase 24c |
| DRM Ed25519 PKI | 💭 Vision | Phase 36d |

## Current

- **Secrets:** API keys in Keychain (Phase 5); env fallback. Multiple providers.
- **Code execution (Phase 23.5):** Curriculum exercises run in Pyodide sandbox (Electron renderer). Server validates; no subprocess for untrusted code.

## Phase 23.5 (Substantially Complete)

- **Capability Broker:** ✅ Implemented. All high-risk operations route through broker; audit logging to ~/.polly/audit.db.
- **Pyodide sandbox:** ✅ Implemented. Code runs in Electron renderer (Pyodide); server validates; no subprocess for untrusted code.
- **Package allowlist:** ✅ Implemented. `config/approved_packages.yaml`; package_detector; approval dialog; Context7 trust scores in UI.
- **Content sanitization:** 📐 Config only (scan_for_prompt_injection, pii_detection in security_policy). Optional for personal mode; content_sanitizer.py / pii_filter.py not implemented.
- **API key hardening:** 📐 Config (use_secure_context_manager, auto_cleanup_memory). Provider-level implementation not verified.
- **CORS:** ✅ Loaded from `config/security_policy.yaml`.
- **Analysis:** See [PHASE23.5_ANALYSIS.md](../../../docs/planning/phases/phase-23.5/PHASE23.5_ANALYSIS.md).

## Hardened Knowledge Infrastructure (Current)

Defense-in-depth for the query pipeline with fail-closed design and observable failure modes.

### Observable Failure Modes
- Explicit `FailureCategory` taxonomy mapping every failure type to actionable context
- `FailureFactory` generates standardized `FailureReport` objects with user messages, technical details, and suggestions
- `FailureLogger` persists failures to `~/.polly/hardened.db` for pattern analysis
- `ErrorHandler` bridges existing `ProviderError` hierarchy into failure reports

### Retry Manager + Circuit Breaker
- Unified retry strategy across RAG retrieval, LLM generation, context assembly, external APIs
- Exponential backoff with jitter (configurable per operation in `config/retry.yaml`)
- Operation-specific parameter adjustments per attempt (e.g. relax similarity threshold, reduce max_tokens)
- Circuit breaker prevents cascading failures: CLOSED → OPEN (after threshold failures) → HALF_OPEN (probe) → CLOSED
- All retry events logged to `hardened.db`

### Dual-Phenomenology Validation
- Independent provenance (source trust) and content (quality/safety) checks on every RAG result
- Source trust levels per Polly source type: HIGH_TRUST (vault, codebase), MEDIUM_TRUST (patterns, entities), VERIFY_REQUIRED (web), UNTRUSTED (unknown)
- Content validator: PII hard block, prompt injection hard block, epistemological alignment checks (enrichment, not blocking)
- Constitutional check reconciliation: scapegoat/essentialist detection triggers deeper analysis per [ethics spec](../ethics/spec.md), never content filtering

### Performance Observability
- Percentile tracking (p50/p90/p95/p99) for all pipeline operations
- In-memory buffer flushed to `hardened.db` periodically
- Degradation detection: compare recent p95 to baseline p95
- Dashboard: human-readable reports, JSON export, layer status indicators

### Schema Migration
- `MigrationManager` handles forward-only SQL migrations in `migrations/`
- `schema_version` table tracks applied migrations
- Atomic transactions per migration

Implementation: `core/hardened/`. Config: `config/validation.yaml`, `config/retry.yaml`. Change folder: [changes/hardened-knowledge-infrastructure/](../../changes/hardened-knowledge-infrastructure/).

---

## Agent Swarms Security (Planned)

The Capability Broker from Phase 23.5 extends to serve as the execution context broker for Agent Swarms (Phase 24c):

- **Execution context brokering:** Agents declare required execution contexts (github, filesystem, obsidian, ghost_cms, email, calendar, etc.). The Capability Broker validates and grants scoped access.
- **Scoped access tokens:** Time-limited, operation-restricted (read-only vs read-write), resource-scoped (specific repos, directories).
- **Agent trust model:** New agents start with minimal permissions. User explicitly grants context access. Permissions remembered per agent.
- **Workflow-level permissions:** Users approve execution contexts per workflow, not per individual agent invocation. Template permissions saved.
- **Audit trail:** All agent context access logged. Users can review what agents accessed.
- See [agent-swarms spec](../agent-swarms/spec.md).

## DRM Security (Planned)

### Phase 36 (Local Network): Trusted, No Auth

- Nodes assumed non-malicious on LAN. Firewall recommended.
- No authentication overhead. Suitable for home network only.

### Phase 36d (Remote Mesh): Ed25519 PKI Token System

Two-layer cryptographic authentication for internet-facing mesh:

**Layer 1 — Mesh Membership (long-lived):**

- Each node has Ed25519 keypair. Node ID derived from public key.
- `trusted-peers.yaml` is the mesh "constitution" — explicit, auditable allowlist signed by admin key.
- Admin key held offline (cold storage). Consider multisig for critical meshes.
- Monthly keypair rotation with 7-day grace period. Emergency revocation via `revoked` list.

**Layer 2 — Task Authorization (short-lived):**

- JWT (EdDSA algorithm) generated per task request. 5-minute expiry.
- Claims: issuer (sender), audience (recipient), task ID, mesh ID, task type, priority.
- Recipient verifies: signature against sender's public key from trusted-peers, audience matches self, not expired, task ID not replayed, sender has required role.

**Replay protection:** Task ID bound to token. Recipient tracks processed IDs in memory with TTL. Timestamp validation (±5min clock skew).

**Performance:** ~1.5ms total per-task overhead (signing + verification + replay check). Negligible vs LLM inference.

**Simplified alternative:** HMAC shared secret for small, fully-trusted meshes (2–5 nodes). Tradeoff: can't revoke individual nodes.

### Data Privacy

- Sensitive queries should process locally (configurable per-domain).
- End-to-end encryption for task payloads: encrypt with recipient's public key before transmission.
- Cloudflare Tunnels provide TLS in transit. E2E adds defense-in-depth.
- Geographic tagging enables data sovereignty routing (tasks stay in same country if required).

### Resource Limits

- Max concurrent tasks per node (configurable, default 10).
- CPU/memory caps to prevent resource exhaustion.
- Rate limiting: 100 heartbeats/hour, 1000 task submissions/hour per peer, 50 concurrent tasks per peer.
- Cloudflare Worker enforces per-peer registration limits.

### Key Storage

- Private keys: `~/.polly/keys/` (chmod 600).
- Trusted peers: `~/.polly/drm/trusted-peers.yaml`.
- Backup via GPG encryption. If key lost, node must be re-added to mesh.

See [drm spec](../drm/spec.md) for full security architecture details.

## Reference

- [docs/SECURITY.md](../../../docs/SECURITY.md) — User-facing security guide
- [PHASE23.5_SECURITY_HARDENING.md](../../../docs/planning/phases/phase-23.5/PHASE23.5_SECURITY_HARDENING.md) — Spec
- [PHASE23.5_IMPLEMENTATION_PLAN.md](../../../docs/planning/phases/phase-23.5/PHASE23.5_IMPLEMENTATION_PLAN.md)
- DRM: [drm spec](../drm/spec.md)