# Security (OpenSpec)

Source of truth for security behavior. Current + planned (Phase 23.5): [docs/SECURITY.md](../../../docs/SECURITY.md). Phase 23.5 spec: [docs/planning/phases/phase-23.5/](../../../docs/planning/phases/phase-23.5/).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Secrets (Keychain, env), API keys | ✅ Implemented | Phase 5 |
| Code execution (subprocess, timeout) | ✅ Implemented | Phase 23; not sandboxed |
| Capability Broker, Pyodide sandbox | 💭 Vision | Phase 23.5 not started |
| Package allowlist, content sanitization | 💭 Vision | Phase 23.5 |
| Agent Swarms execution context brokering | 💭 Vision | Phase 24c |
| DRM Ed25519 PKI | 💭 Vision | Phase 36d |

## Current

- **Secrets:** API keys in Keychain (Phase 5); env fallback. Multiple providers.
- **Code execution (Phase 23):** Curriculum exercises run via subprocess (Python). Timeout; stdout/stderr capture. **Not yet sandboxed** — Phase 23.5 will replace with Pyodide.

## Planned (Phase 23.5)

- **Capability Broker:** LLM requests capabilities; no direct access. Extended by Agent Swarms to broker execution contexts (see below).
- **Pyodide sandbox:** Replace subprocess; WebAssembly Python; no network/filesystem; timeout and memory limits.
- **Package allowlist:** Pre-approved packages in `config/approved_packages.yaml`; approval workflow for unknown; Context7 trust scores.
- **Content sanitization:** Prompt-injection detection; PII detection (warn-only).
- **API key hardening:** Context managers; clear after use. Config: `config/security_policy.yaml`.

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
