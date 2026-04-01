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
All 14 Phase 2 tasks complete and verified. @backend confirms each wave. @security_audit signs off on wave 0.

---

## Wave 2.5 — Context Management (from CLAUDE_CODE_ARCHITECTURE_INSIGHTS.md §4)

- [ ] **Post-compact restoration:** After conversation compaction/summarization, gateway MUST re-inject: (a) active agent SOUL (always), (b) active mental models, (c) most recently referenced vault notes (up to 5, from Knowledge Skill access log), (d) active WorkflowSession state if one is in progress. Without this, agents forget context after compaction. @backend owns.
- [ ] **Proactive compaction:** Gateway tracks context window budget and compacts *before* hitting the limit. Do NOT implement reactive compaction (prompt-too-long error → retroactive compact) — that's a symptom of insufficient budget tracking.
- [ ] **Token budget reference points** (empirical from production deployments — starting point, not gospel; adjust per model tier and context window):

  | Budget | Reference value |
  |--------|----------------|
  | Compaction summary max | 20,000 tokens |
  | Post-compact vault note restoration | 50,000 tokens total, 5,000 per note |
  | Post-compact SOUL + mental model re-injection | 25,000 tokens |
  | USER.md hard cap | ~150 lines / 25,000 bytes |

  Note: local models have smaller context windows than frontier models — tune budgets per routing tier.

---

## Wave 4 — Phase 3 Unlocks
*Listed here for @backend visibility. Owned separately; do not start until Phase 2 complete.*

- [ ] #15 `knowledge_analogy` tool registration — blocks: Structural Analogy (`phase-3-cognitive-features`)
- [ ] #16 `knowledge_dream` tool registration — blocks: Dream Logic (`phase-3-cognitive-features`)
- [ ] #17 `knowledge_conversation_history` tool registration — blocks: Metacognitive Dashboard, EIS, Temporal Intelligence, Oral History; **@qa_guy** needs JSONL schema spec when this work begins (fixture generator is schema-driven)
- [ ] #18 Index hook hot-reload support — blocks: all Phase 3 cognitive features that register hooks
- [ ] #19 `vault_write` tool implementation — blocks: Obsidian write-back (`phase-3a-obsidian-write-back`)
- [ ] #20 Notion Knowledge Skill adapter — blocks: Notion integration (`phase-3d-notion`)
- [ ] #21 Creative Code Skill sandbox execution — blocks: Creative Code Skill (`phase-3-creative-systems`); **@security_audit** hard gate before design begins
- **No gateway changes needed** for Chorus Mode (existing fan-out + `activationMode: "always"`) or phase transitions (client-side only)

---

## Done When

All Wave 1–3 items complete. Specifically:
- WebSocket authenticated (Wave 1 #1) — @frontend can connect
- Agent list, session create/send/receive, event stream working (Wave 1 #2–5)
- vault_read + knowledge_search tools registered (Wave 2 #6–7) — Knowledge Skill unblocked
- Prosodics field on all message objects (Wave 2 #8) — Gesture Layer Phase 1 unblocked
- Model routing fields + provider pool scaffolding (Wave 2 #9–10) — Model Routing Phase 2 unblocked
- Compaction infrastructure (Wave 3 #11–14) — context management unblocked
- Wave 4 items (#15–21) tracked here but gated on Phase 2 complete; do not start Wave 4 until all Wave 1–3 shipped and confirmed by @qa_guy

@backend declares gateway-changes complete when @qa_guy has run the gateway integration test suite (phase-1-testing-infrastructure) against all Wave 1–3 tools and sign-off is recorded in this file.
