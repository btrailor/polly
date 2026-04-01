# POLLY_WEB_ANALYSIS.md

Design Analysis — Household Nodes as Compute and Memory Contributors  
Source: Design session 2026-03-30  
Status: Pre-spec analysis — decisions captured, incorporated into openspec  
Approved by Brett for incorporation into active specs

## What This Document Is

Analysis of what it would mean for each household node to contribute processing power and accessible memory to a "Polly Web." Three subquestions: compute contribution, memory contribution, and what "the Polly Web" actually means architecturally.

**All spec actions from this document have been incorporated into the relevant openspec change sets and specs. This file is the source reference.**

---

## Key Findings Summary

### Compute Contribution — by Device Class

| Device class | What it contributes | How |
|-------------|--------------------|----|
| Mac Mini (gateway) | Primary inference, indexing | Always |
| NAS (UGREEN DXP4800) | Inference (7B range), embedding, vector store persistence | Docker + mDNS registration |
| Apolosign (RK3576) | Embedding (always-on), TTS | Android compute node registration |
| iPhone (Brett) | On-device STT, local capture embedding, TTS for own responses | Relay: own sessions only |
| Child's Android | On-device STT, capture embedding; embedding queue when charging | Relay pattern |
| PicoClaw | Lightweight inference, TTS, dedicated embedding | Existing mDNS registration |

**Mobile devices cannot reliably run inference as a background service.** iOS kills background processes; battery drain is prohibitive. Mobile contribution = relay (own sessions only) + charging-aware embedding queue.

### Memory Contribution — Three Types

- **Type A: Household operational memory** — chore history, calendar, meal plans. Already shared by design in household.chores skill. Nothing new needed.
- **Type B: Shared household knowledge section** — `/Household/` vault section, indexed by Knowledge Skill, readable by all household nodes within scope. Tractable and valuable. → Specced in `phase-3a-obsidian-write-back`.
- **Type C: Personal knowledge** — Brett's research vault, agent memories. Explicitly not for sharing. Capability scoping already enforces this.

### The Polly Web — Three Readings

- **Reading A (household mesh):** All home devices in a compute mesh orchestrated by the gateway. Brett's Mac Mini is still center. → **Spec this now.** Incorporated into `phase-4-federation`.
- **Reading B (voluntary peer network):** Multiple independent Polly instances sharing compute voluntarily. Requires trust + accounting model. → **Future horizon**, named in `POLLY_WEB.md` forward spec.
- **Reading C (public compute mesh):** Global BOINC-style network. → **Explicitly out of scope** for the foreseeable future.

---

## Open Questions (for resolution during implementation)

**Q1:** Should the FAISS index live on the NAS (storage advantage) rather than the Mac Mini (latency advantage)? Decision depends on update vs. query frequency. Large vaults (10k+ notes) may favor NAS. → `KNOWLEDGE_SKILL.md` question, not `DISTRIBUTED_NODES.md`.

**Q2:** Mobile contribution consent — onboarding vs. settings? **Recommendation: Settings, default off.** Charging-aware contribution is a power-user feature; onboarding is already complex.

**Q3:** What does a household node "see" of the shared knowledge section — full conversational search or only through explicit household skills? Likely age/context dependent. → Capability scoping question for `HOUSEHOLD_NODES.md`.

**Q4:** Could `FEDERATED_COLLABORATION.md` git mailbox transport carry compute tasks for Reading B peer networks? Technically yes, trust model underdeveloped. → Future spec, not now.

---

## Cross-Reference Map

| This document section | Incorporated into |
|----------------------|------------------|
| §2 Compute contribution, device classes | `phase-4-federation/tasks.md` — new node classes |
| §3.2 Shared vault section | `phase-3a-obsidian-write-back/tasks.md` — `/Household/` section |
| §4 Polly Web readings | `openspec/specs/infrastructure/spec.md` — compute mesh architecture |
| §5.3 POLLY_WEB.md | `phase-4-federation/tasks.md` — forward spec task |
| NAS compute node | `phase-4-federation/tasks.md` + `infrastructure/spec.md` |
| Mobile charging queue | `phase-4-federation/tasks.md` |
| Q1 NAS as vector store | `phase-2-knowledge-skill/tasks.md` — open question |
