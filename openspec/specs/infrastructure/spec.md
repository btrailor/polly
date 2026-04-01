# Infrastructure — Current State

*Skill manifest format is defined. Marketplace and MCP adapter ship in Phase 2.*

## Skill Manifest Format (§8.8)

```json
{
  "id": "string",
  "type": "native | mcp",
  "permissions": ["read:filesystem:{path}", "network:{domain}"],
  "network": [],
  "data_destination": "local | cloud",
  "cloud_domains": []
}
```

`network: []` is strictly enforced for all local-only skills. Conversation history data must never have network permissions.

## Security Model

- **Verified tier:** cryptographic signature, trust anchor baked into gateway at install
- **Community tier:** explicit two-step user confirmation for cloud skills
- **Blocked tier:** gateway-level rejection, signed blocklist, 7-day staleness window, fail-closed offline
- Permission-adding updates trigger full re-consent flow

## Open Pre-Production Gate

Push registration security fix (C1: unauthenticated push registration, C2: cleartext `sendKey` in `devices.json`) — @backend owns, @security_audit sign-off required before Phase 2 ships to production. See `PUSH_SECURITY_FIX.md`.

---

## Household Compute Mesh Architecture (Phase 4)

*Source: `POLLY_WEB_ANALYSIS.md`. Change set: `phase-4-federation`.*

The household compute mesh is **Reading A of the Polly Web**: all home devices contributing compute and memory within a LAN-perimeter, orchestrated by the gateway (Mac Mini). Brett's gateway remains the center. No new trust model needed — LAN trust perimeter applies throughout.

### Node Class Taxonomy

| Node class | Target hardware | Contribution | Phase |
|-----------|----------------|-------------|-------|
| `gateway` | Mac Mini (M-series, 16–32GB) | Primary inference (any model up to 70B 4-bit), indexing | Exists |
| `picoclaw` | Sipeed hardware | Lightweight inference, TTS, embedding | Phase 3 (existing spec) |
| `nas-docker` | UGREEN NASync DXP4800 (ARM64, 16GB, Docker) | Inference (7B range), embedding, vector store persistence candidate | Phase 4 |
| `android-always-on` | Apolosign (RK3576, always-on, LAN) | BGE-small embedding, Kokoro TTS, Phi-3-mini inference | Phase 4 |
| `mobile-relay` | iPhone / Android phones | On-device STT, capture embedding, TTS — own sessions only, not general dispatch | Phase 4 |

### Design Principles

- **Honest capability matching.** Each device class contributes what it's actually good at. Mobile devices cannot reliably run inference as background services (iOS kills processes; battery drain). Mobile contribution = relay (own sessions only) + charging-aware embedding queue.
- **Gateway as orchestrator.** The capability registry routes by capability match, availability, trust, and latency. Latency-sensitive tasks stay on the Mac Mini. Batch embedding and long-running indexing can route to NAS or Apolosign.
- **LAN trust perimeter.** No new trust model for Phase 4 household mesh. All nodes are within the existing LAN trust boundary.

### The Polly Web — Reading Taxonomy (locked positions)

| Reading | Description | Status |
|---------|-------------|--------|
| A — Household mesh | Home devices in a compute mesh, gateway-orchestrated | **Spec in Phase 4** |
| B — Voluntary peer network | Two sovereign Polly stacks sharing compute voluntarily; requires trust + accounting model | **Future horizon — named in `POLLY_WEB.md`, not specced** |
| C — Public compute mesh | Global BOINC-style inference network | **Explicitly out of scope, foreseeable future** |

### Shared Household Knowledge Section

- `/Household/` vault section indexed by Knowledge Skill, tagged `source: "household"`
- Readable by household nodes within `vault_sections` scope
- Writable by nodes with `vault_write: true` (Phase 3+ only)
- No new vector infrastructure — same FAISS index, additional source section
- See `phase-3a-obsidian-write-back` tasks for implementation detail
