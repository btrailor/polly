# Phase 4 — Household Nodes: Multi-User Gateway Architecture

**Status:** 📋 Planned  
**Gate:** Phase 3 complete, DISTRIBUTED_NODES.md, phase-3a-obsidian-write-back, KNOWLEDGE_SKILL.md  
**Spec source:** HOUSEHOLD_NODES.md (2026-04-06)  
**Owners:** @backend (principal registry, capability token, gateway enforcement), @security_audit (token model, isolation guarantees), @frontend (onboarding extension, settings), @infra (node registration)  
**Last updated:** 2026-04-06

---

## What This Delivers

Multiple people (partner, children, guests) connect iOS clients to the same gateway with distinct identities, vault access, and capability profiles. One gateway process. Clients are oblivious to the household model — they just receive a scoped session token and a filtered agent list.

---

## Phase 1 Hooks ⚠️ Ship NOW (non-deferrable)

These two items must ship in Phase 1 to avoid a protocol version bump when Phase 4 lands. Zero behaviour change — purely additive.

### Hook 1 — `sessions.create` response: add `principal_id` field (Backend)

From HOUSEHOLD_NODES.md §9.2:

> `sessions.create` response MUST include `principal_id: "owner"` from Phase 1 onwards. This is a non-breaking addition. iOS client ignores it until this spec ships; it ensures the protocol never needs a version bump to add the field.

**What to add to the gateway `sessions.create` response:**
```json
{
  "session_id": "...",
  "principal": {
    "id": "owner",
    "display_name": "Owner",
    "role": "owner"
  }
}
```

Owner: @backend  
Gate: Phase 1A — must be in gateway before Phase 4 gateway work begins

---

### Hook 2 — iOS client: store `principal_id` from session init

The iOS client must read and persist `principal.id` from the `sessions.create` response so the field is available when Phase 4 UI ships. Just store it — no UI change, no routing logic.

**Where to store:** MMKV key `polly.session.principalId` (string, default `"owner"`)  
**When to write:** After every successful `sessions.create` / session init  
**What to use it for:** Nothing yet — Phase 4 reads it for the Household settings section and agent drawer scoping

Owner: @frontend  
Gate: Phase 1A — add when `sessions.create` response is wired up

---

## Architecture Summary (Phase 4 scope, not Phase 1)

### Principal Model
```
Principal
├── id: string              // "brett", "sarah", "kid-1"
├── display_name: string
├── role: "owner" | "partner" | "child" | "guest"
├── devices: DeviceId[]     // Ed25519 public key fingerprints
├── vault_config: VaultConfig
└── capability_profile: CapabilityProfile
```

### Capability Token (gateway-side, not sent to iOS client)
- `VaultScope` — which vault paths accessible, which shared sections
- `AgentScope` — all / allowlist / blocklist of agent_ids
- `ToolScope` — agentic_tools, vault_write, knowledge_search, mcp_skills booleans
- `ContentPolicy` — safe_mode, max_model_tier

### Vault Isolation
- Per-principal FAISS index — Brett's semantic search never touches Sarah's
- `/Household/` shared section inside owner's vault — readable by all principals per their VaultScope
- Agent memories namespaced by `{agent_id}:{principal_id}` — agents shared, memories isolated

### Device Approval Flow
- New device → gateway returns `auth.pending`
- Owner receives push notification → approves in Settings → Household → assigns principal
- Device receives `auth.ok` on next connection attempt

### iOS Changes (Phase 4)
- `Settings → Household` section (owner-only): principal list, device approval queue, guest QR generator
- Agent drawer filtered by session's `AgentScope` (gateway filters `agents.list` response — no iOS changes needed)
- "Waiting for approval" state in onboarding for unregistered devices on household gateways

---

## Storage (Phase 4)

Principals stored in gateway config via `config.patch polly.household.principals`:
```json
{
  "polly": {
    "household": {
      "principals": {
        "brett": { "role": "owner", "devices": [...], "vault_config": {...} },
        "sarah": { "role": "partner", "devices": [...], "vault_config": {...} }
      }
    }
  }
}
```

---

## Dependencies

| Dependency | Why |
|------------|-----|
| Phase 3 complete | vault_write tool, Knowledge Skill with source tagging, agent memory layer |
| phase-3a-obsidian-write-back | /Household/ vault section, source: "household" tagging |
| KNOWLEDGE_SKILL.md Phase 2 | FAISS index operational — needed before per-vault index routing |
| SECURITY_IMPLEMENTATION_SPEC.md | Ed25519 device identity — principal↔device mapping builds on this |

@security_audit review required before implementation:
- Capability token format and signing
- Device approval flow — pending state cannot be bypassed
- Principal deletion — memory namespace purge must be complete and verifiable
- Guest token expiry enforcement

---

## Cross-References

| Spec | Relationship |
|------|-------------|
| DISTRIBUTED_NODES.md | Separate concern — compute nodes, not user principals |
| phase-3a-obsidian-write-back | /Household/ vault section implemented there; this spec defines access control |
| KNOWLEDGE_SKILL.md | Knowledge Skill enforces vault isolation at query time |
| SECURITY_IMPLEMENTATION_SPEC.md | Ed25519 device identity, TOFU — principal↔device mapping extends this |
| LOCKDOWN_MODE.md | In lockdown: household remote connections disabled, guest tokens disabled, owner + pre-approved LAN devices only |
| FEDERATED_COLLABORATION.md | Cross-instance Liaison (two sovereign Polly stacks) is architecturally separate — different trust model |

---

## Phase 4 Tasks (placeholder — full breakdown at Phase 3 completion)

### Backend
- [ ] Principal registry in gateway config (`polly.household.principals`)
- [ ] `CapabilityToken` minting at session init — resolve device → principal → role → profile
- [ ] `sessions.create` response: add `principal` field (see Phase 1 Hook 1 above)
- [ ] `agents.list` filtered by session's `AgentScope`
- [ ] Knowledge Skill: `VaultScope` enforcement in FAISS query path
- [ ] Agent memory namespace: `{agent_id}:{principal_id}` key scheme
- [ ] Device approval flow: `auth.pending` state, `approveDevice(principalId)` endpoint
- [ ] Guest token generation + TTL enforcement

### Frontend  
- [ ] Store `principal_id` from `sessions.create` response in MMKV (see Phase 1 Hook 2 above)
- [ ] `Settings → Household` section (owner-only)
- [ ] Principal management UI (create, edit, delete)
- [ ] Device approval queue UI
- [ ] Guest access QR generator
- [ ] "Waiting for approval" onboarding state
- [ ] Per-principal capability override UI (power user)

### Security Audit
- [ ] Capability token signing scheme review
- [ ] Device approval flow audit
- [ ] Principal deletion + memory purge verification
- [ ] Guest token expiry enforcement audit
