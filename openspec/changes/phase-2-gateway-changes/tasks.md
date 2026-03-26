# Phase 2: Gateway Changes

**Status:** 📋 Planned  
**Owner:** @backend  
**Purpose:** Consolidates all 14 gateway-side tasks previously scattered across 6 task files. @frontend changes block on these; sequence confirmed by @backend 2026-03-25.

---

## Wave 0 — Pre-Production Gate (must ship before production)

These four are the push-security prerequisite. Nothing goes to production without them.

- [ ] **#1** Auth-gate `aight.push.register` — require authenticated session before push token registration (C1 fix). Blocks: push-notifications.
- [ ] **#2** Encrypt `sendKey` in macOS Keychain, not `devices.json` cleartext (C2 fix). Blocks: push-notifications.
- [ ] **#3** `polly.security.protectionLevel: "standard"` emitted at gateway startup (config key initialized). Blocks: lockdown-mode iOS enforcement.
- [ ] **#4** Scrub API keys from config change logs — prevents key leak to gateway log files. Blocks: all `config.patch` callers.

@security_audit sign-off required before any of these close.

---

## Wave 1 — Phase 1 Ship Unlocks (my queue once Phase 1 ships)

- [ ] **#7** `sessions.patch` model field — allow per-session model override mid-session. Unblocks: model-routing Option B (race condition fix). Target: Phase 2 routing sprint start.
- [ ] **#8** `models.list` extension — add `contextWindow: number` and `strengths: string[]` per model. Unblocks: complexity evaluator in auto-routing.
- [ ] **#9** Confirm completion event token count field names — document exact field names for `inputTokens` + `outputTokens` in completion event payload. Unblocks: usage tracking + budget guard.
- [ ] **#10** `vault.write_complete` event — gateway emits after every vault write regardless of backend (Obsidian or Notion); includes `path`, `frontmatter`, `origin`, `session_key`. Unblocks: Knowledge Skill incremental FAISS index update.

---

## Wave 2 — Mid-Cycle (after swarm coordination spec stabilizes)

- [ ] **#5** `targetAgentIds` on `agent` RPC — allow fan-out to a subset of group agents. Currently all-or-nothing per group. Unblocks: phase-managed dispatch, cost-aware partial fan-out. (@backend Phase 2 enhancement — requires group membership record changes)
- [ ] **#6** Per-agent-per-group `activationMode` override — `activationMode` field on group membership record (separate from global per-agent setting). Unblocks: group-specific mention vs. always activation. (@backend Phase 2 enhancement)

---

## Wave 3 — Late Phase 2 (complex, needs design time)

- [ ] **#11** `skills.install` RPC — gateway endpoint for skill installation from ClawHub. Unblocks: skills-marketplace install flow.
- [ ] **#12** Per-device config scoping — `polly.ios.aestheticStance.{deviceId}` support in gateway config. Unblocks: multi-client sensibility conflict detection. Needs design: config namespace schema for per-device overrides. Unblocks: sensibility-behavior conflict banner.
- [ ] **#13** Network enforcement (Lockdown Mode) — IP-range blocking, APNs outbound block, skill network restriction enforcement at gateway level. Complex — requires gateway network layer changes. Unblocks: lockdown-mode full implementation.
- [ ] **#14** Gateway encryption at rest — passphrase-derived key, Secure Enclave path, session file encryption. Complex — requires significant gateway storage layer changes. Unblocks: lockdown-mode Phase 3 data protection.

---

## Blocking Relationships Summary

```
#1, #2, #3, #4  →  production gate (wave 0, @security_audit sign-off)
     #1, #2     →  phase-2-push-notifications
        #3      →  phase-2-lockdown-mode (iOS enforcement)
        #4      →  all config.patch callers safe
        #7      →  phase-2-model-routing (Option B routing, race condition fix)
        #8      →  phase-2-model-routing (complexity evaluator)
        #9      →  phase-2-model-routing (budget guard + usage tracking)
       #10      →  phase-2-knowledge-skill (incremental FAISS index)
        #5      →  phase-2-swarm-coordination (phase-managed dispatch)
        #6      →  phase-2-swarm-coordination (per-group activation mode)
       #11      →  phase-2-skills-marketplace (install flow)
       #12      →  phase-2-sensibility-behavior (multi-client conflict banner)
    #13, #14    →  phase-2-lockdown-mode (full enforcement)
```

## Done When
All 14 tasks complete and verified. @backend confirms each wave. @security_audit signs off on wave 0.
