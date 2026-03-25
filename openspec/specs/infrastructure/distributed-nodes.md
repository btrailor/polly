# DISTRIBUTED_NODES.md
*Phase 3 — PicoClaw Node Federation*
*Status: Planned*
*Owners: @backend (node registration, capability registry, routing), @infra (node discovery, trust)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Federation of PicoClaw compute nodes with the OpenClaw gateway — lightweight edge devices that extend the gateway's local compute without exposing them as distinct infrastructure to the iOS client.

**Reference:** https://github.com/sipeed/picoclaw

**Design principle:** The iOS client is unaware of node boundaries. From the client's perspective, there is one gateway. PicoClaw nodes are invisible infrastructure — they appear to OpenClaw as registered compute extensions, not as separate services that the client needs to know about.

---

## 2. Node Architecture

```
iOS client
    ↕
OpenClaw gateway (orchestrates everything)
    ↕
PicoClaw nodes (local compute, discovered via mDNS)
```

The gateway is the single point of contact for the client. Nodes register with the gateway, not with the client. The gateway routes work to nodes based on capability.

---

## 3. Node Registration

### 3.1 Discovery

Nodes advertise via mDNS on the local network:

```
_picoclaw._tcp.local
  name: "brett-picoclaw-01"
  capabilities: ["inference:phi-3-mini", "embedding:bge-small", "tts:kokoro"]
  version: "0.3.1"
```

The gateway discovers nodes automatically on the local network. No manual configuration required for LAN nodes.

### 3.2 Capability Registry

The gateway maintains a capability registry — a map of what each node can do:

```json
{
  "nodes": [
    {
      "node_id": "brett-picoclaw-01",
      "address": "192.168.1.42:8080",
      "trust_level": "local",
      "capabilities": {
        "inference": ["phi-3-mini", "llama-3.2-1b"],
        "embedding": ["bge-small-en"],
        "tts": ["kokoro-v1"]
      },
      "status": "online",
      "last_seen": "2026-03-25T14:00:00Z"
    }
  ]
}
```

### 3.3 Trust Levels

| Level | Condition | Access |
|-------|-----------|--------|
| `local` | Same subnet, mDNS discovered | Full capability access, no auth |
| `remote-vpn` | Reachable via Tailscale, verified | Full capability access, Tailscale auth |
| `untrusted` | Unverified node | Rejected at registration |

No remote nodes without VPN. mDNS is LAN-only; Tailscale is the remote extension. No open internet node registration.

---

## 4. Routing

The gateway routes tasks to nodes based on:

1. **Capability match** — does the node have what's needed?
2. **Availability** — is the node online and not overloaded?
3. **Trust level** — is the node trusted for this task type?
4. **Latency** — prefer lower latency when multiple capable nodes exist

Routing is automatic and transparent. Brett does not choose which node handles a given task. The gateway selects the best available node.

### 4.1 `sessions.create` Node Routing Parameter

Advanced users can hint at node preference via `sessions.create`:

```json
{
  "node_preference": "brett-picoclaw-01",
  "node_fallback": "gateway"
}
```

`node_fallback: "gateway"` means: if the preferred node is unavailable, fall back to gateway inference. This prevents sessions from failing when a specific node is offline.

---

## 5. Use Cases

**Lightweight always-on inference:** A PicoClaw node running a small model (Phi-3-mini, Llama-3.2-1b) handles ambient agent background processing — routine tasks that don't need the full gateway LLM. Frees gateway compute for demanding sessions.

**Dedicated embedding node:** A PicoClaw node running BGE-small handles real-time embedding for new vault content. Index updates don't compete with inference workloads.

**Local TTS:** A PicoClaw node running Kokoro handles voice synthesis for Polly responses. Lower latency than gateway TTS for voice-heavy sessions.

---

## 6. Open Questions

None blocking.

**Deferred:**
- **Q1:** Node authentication for remote-vpn tier — Tailscale auth is the mechanism, but the specific handshake with OpenClaw's session model needs specification at implementation time.
- **Q2:** Node failure handling — if a node drops mid-session, does the gateway transparently fall back to local inference, or does the session error? Default: transparent fallback. No user-visible failure for node dropout.

---

## 7. Dependencies

- OpenClaw gateway routing layer (@backend)
- mDNS discovery library (@infra)
- Capability registry data model (@backend)
- Tailscale for remote-vpn trust tier (@infra)
- LOCKDOWN_MODE.md: node discovery behavior in lockdown (mDNS = LAN only, already consistent; remote-vpn = Tailscale, already allowed)

---

*Cross-references: LOCKDOWN_MODE.md, POLLY_IOS_SPEC.md §8.8*
