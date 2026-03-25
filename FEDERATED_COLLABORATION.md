# FEDERATED_COLLABORATION.md
*Phase 3 — Cross-Instance Sovereign Collaboration*
*Status: Planned*
*Owners: @backend (Liaison protocol, mailbox transport), @infra (peer discovery, git transport)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A protocol for two sovereign Polly stacks to collaborate without a central server — Liaison agents communicating across gateways using a shared git repository as transport.

Each participant owns their Polly instance. Neither is primary. The collaboration infrastructure is a shared git repo — append-only, forkable at any time, no platform dependency. If either participant wants to stop collaborating, they stop pushing to the shared repo. No account deletion required, no platform permission needed. Revocation is immediate and unilateral.

**Architectural principle (Graeber):** Horizontal structure enforced by architecture, not policy. There is no central authority because the architecture makes central authority impossible. No server can be seized. No platform can revoke access. The collaboration is between the two participants and the shared repo — nothing else.

---

## 2. The Liaison Protocol

The Liaison agent (already in POLLY_AGENT_TEMPLATES.md) acquires a federated mode: cross-instance collaboration peer.

In federated mode, Liaison agents communicate via **async mailbox** — messages written to the shared git repo, read on the other side's polling interval. This is not real-time chat. It is async correspondence — the right model for sovereign collaboration between two thinking people who have other things to do.

### 2.1 Message Format

```json
{
  "from": "brett-polly/liaison",
  "to": "collaborator-polly/liaison",
  "thread_id": "collab-2026-q1-synthesis",
  "message_id": "msg-20260325-001",
  "timestamp": "2026-03-25T14:00:00Z",
  "content": "...",
  "context_projection": {
    "shared_topics": ["open_source_sustainability", "knowledge_management"],
    "position_summary": "..."
  },
  "signature": "<ed25519-sig>"
}
```

All messages are signed. A message without a valid signature from the expected sender is rejected.

### 2.2 Context Projection

Liaison agents do not share full vault access. They share a *projection* — a filtered summary of the owner's context, scoped to the collaboration's shared topics.

The projection contains:
- Position summaries on shared topics (from Temporal Intelligence, if available)
- Relevant notes (selected by the local Liaison, not the full vault)
- No raw session history
- No Epistemic Immune System data
- No Metacognitive Dashboard data

What to share is the local Liaison's judgment call, informed by the collaboration's stated scope. The remote Liaison never pulls from the local vault directly — it only receives what the local Liaison sends.

---

## 3. Shared Git Repository as Transport

The shared repo serves as the async mailbox:

```
collab-repo/
  mailbox/
    brett-to-collaborator/
      msg-20260325-001.json
      msg-20260325-002.json
    collaborator-to-brett/
      msg-20260325-001.json
  threads/
    collab-2026-q1-synthesis/
      context.json
      summary.md
  signatures/
    brett.pub
    collaborator.pub
```

**Append-only:** Messages are never deleted or modified after writing. The history is the record.

**Forkable:** Either participant can fork the repo and continue the collaboration unilaterally. The fork carries the full history. No permission needed.

**Transport agnostic:** The shared repo can be hosted anywhere — GitHub, a self-hosted Gitea, a local NAS both participants access via Tailscale. The Liaison doesn't care where the repo lives as long as it can push and pull.

---

## 4. Peer Discovery

Two discovery paths:

**Manual (Phase 3):** Brett shares a collaboration invite — a JSON object containing his Liaison's public key, the shared repo URL, and the collaboration scope. The collaborator imports it into their Polly instance. One-time setup.

**mDNS (LAN-only, Phase 3+):** Two Polly instances on the same network can discover each other automatically. Still requires manual pairing confirmation — discovery doesn't auto-pair.

---

## 5. Symmetric TOFU Pairing

Neither participant is primary. The pairing ceremony is symmetric:

1. Brett generates a collaboration invite
2. Collaborator accepts and generates a counter-invite
3. Both instances exchange public keys
4. Both instances verify the key exchange (emoji code confirmation, same mechanism as PUSH_SECURITY_FIX.md TOFU pairing)
5. Collaboration scope is agreed (which topics are shared)
6. First Liaison message is sent by both simultaneously

After pairing: neither instance has elevated access to the other. The collaboration scope defines what each Liaison shares. Changing the scope requires mutual agreement (both Liaison agents propose, both owners confirm).

---

## 6. Lockdown Mode Behavior

In Lockdown Mode:
- Federated collaboration is suspended (no outbound messages to shared repo)
- Inbound messages continue to accumulate in the shared repo (other participant can still write)
- On Lockdown Mode exit: Brett's Liaison reviews accumulated messages and decides whether to respond

Lockdown Mode does not revoke the collaboration. It pauses it. The collaborator is not notified that Brett is in Lockdown Mode — the silence is the signal, consistent with the stealth design principle.

---

## 7. Open Questions

None blocking.

**Deferred:**
- **Q1:** Collaboration scope evolution — what happens when the scope needs to change? Requires mutual Liaison agreement and both owner confirmations. Protocol TBD at implementation.
- **Q2:** Multi-participant collaboration — can more than two Polly instances share a mailbox? Phase 3+ feature; two-participant model is the starting point.

---

## 8. Dependencies

- Liaison agent (existing, federated mode addition needed)
- Temporal Intelligence: position summaries for context projection
- PUSH_SECURITY_FIX.md: TOFU pairing mechanism (reused)
- LOCKDOWN_MODE.md: suspension behavior
- Git library for mailbox transport (@infra)

---

*Cross-references: POLLY_AGENT_TEMPLATES.md (Liaison), TEMPORAL_INTELLIGENCE.md, PUSH_SECURITY_FIX.md, LOCKDOWN_MODE.md*
