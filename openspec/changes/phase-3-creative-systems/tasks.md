# Phase 3: Creative Systems

**Status:** 💡 Specced  
**Gate:** Phase 2 Knowledge Skill complete  
**Spec sources:** `CREATIVE_CONSTRAINT_ENGINE.md`, `CONVERSATION_ARCHITECTURE.md`, `CHORUS_MODE.md`, `SOMATIC_INTERFACE.md` (Phase 1 foundation, Phase 3 full feature), `DREAM_LOGIC.md`, `CREATIVE_CODE_SKILL.md`

## Goal

The structural engagement layer — how Polly shapes the form of thinking, not just the content. Constraint, architecture, and simultaneity.

## Features + Tasks

### Creative Constraint Engine
Structural rules as SOUL-level engagement mode. Oblique Strategies as system layer.

- [ ] `structural_rules` field activation in Sensibility schema (was empty Phase 1)
- [ ] Fragment mode (Ghost Box pattern)
- [ ] Systematic variation mode (Riley pattern)
- [ ] `activation: "explicit" | "suggested" | "automatic"` per agent
- [ ] Metacognitive Dashboard integration: automatic mode uses engagement data

### Conversation Architecture (Liaison agent)
Liaison designs cognitive structures before conversations begin.

- [ ] Topology library: diverge-converge, steelman-then-decide, pre-mortem, Socratic, layered inquiry, devil's advocate sprint
- [ ] Liaison SOUL: conversation architect mode (pre-conversation brief)
- [ ] Personalization via Metacognitive Dashboard
- [ ] Depends on: group chats (Phase 1 — not yet built) + Liaison agent SOUL (Phase 1 — stub only) + Metacognitive Dashboard

### Chorus Mode
Parallel agent dispatch, no shared context, grid UI.

- [ ] **⚠️ Phase 1 dependency check (before starting):** Verify `topology` field on message objects and `MultiPanelChatLayout` were shipped in Phase 1 — if not, Chorus requires Phase 1 refactor first; check with @frontend before beginning
- [ ] `MultiPanelChatLayout` — topology-agnostic renderer (Phase 1 foundation needed from @frontend)
- [ ] Message model `topology` field + `chorus_position: {row, col}` (Phase 1 architecture needed)
- [ ] Parallel dispatch pipeline using existing fan-out with `activationMode: "always"` — **no gateway changes needed**
- [ ] Grid UI: agents as rows, response units as columns (2-panel phone / full grid iPad)
- [ ] Divergence detection: semantic similarity pass per column
- [ ] Divergence token UI (cool neutral color — "pay attention", not error)
- [ ] Chorus response chunking enforced (2-4 sentence units)

### Somatic Interface — Full Feature
Phase 1 specced locks. Phase 3 full feature with Practice Layer + EIS integration.

- [ ] Phase 1 gateway field shipped (prosodics nullable on all messages — @backend)
- [ ] Phase 1 iOS: client-side signal extraction from audio buffer (speech_rate, pause_p95_ms, volume_variance, turn_length_words — @frontend)
- [ ] Phase 3: engagement state influences Creative Constraint Engine mode suggestions
- [ ] Phase 3: engagement state informs Conversation Architecture topology selection
- [ ] Lockdown mode: prosodics disabled + non-toggleable (behavioral metadata = potential evidence)

## Done when
All features shipped. Chorus grid rendering on iPad. Creative Constraint Engine modes activatable by user. Conversation Architecture topology library in Liaison. Creative Code Skill sandboxed execution working.

### Creative Code Skill (`CREATIVE_CODE_SKILL.md`)
Sandboxed generative code execution — agents can write and run code as part of a creative workflow.

**Hard-blocker dependency chain — sequential gates, not advisory ordering. A task cannot enter "in progress" until all tasks it is blocked by are in done/approved state. No exceptions under schedule pressure.**

```
security-design-doc (@security_audit)
  → security-review-signoff (@security_audit)
  → infra-observability-spec (@infra)        ← parallel with security review; unblocks QA plan
  → qa-containment-validation-plan (@qa_guy) ← blocked on BOTH security-review-signoff AND infra-observability-spec
  → implementation (@backend)
  → qa-containment-validation-execution (@qa_guy)
  → ship gate
```

**Task 1: `security-design-doc` — @security_audit**
- [ ] Sandbox boundary model: what the sandbox can and cannot access
- [ ] Capability scope: filesystem (workspace-only), network (none), runtime (explicit memory + CPU ceilings)
- [ ] I/O handling spec: input sanitization, output escaping, stdio-only IPC
- [ ] **Audit logging spec** (required for sign-off — design doc without this will not be approved):
  - Audit log is write-only from sandbox's perspective — sandbox process cannot suppress or modify its own entries
  - Separate write path from application logging; separate retention policy; not rotated on standard log schedule
  - Audit entry fields per signal type: timestamp, input hash, agent ID, execution context
  - `SANDBOX_ESCAPE` entries: logged before error is returned to caller; caller signal may be generic; audit entry must not be; **hard-abort if audit write fails**
  - `RESOURCE_EXHAUSTED` entries: log agent ID + input; repeated exhaustion from same agent = detectable pattern; fail-open if audit write fails (alert via stderr + gateway status flag)
  - `INPUT_REJECTED` entries: log rejection reason + input fingerprint; flood of rejections = buggy client or boundary probing; **hard-abort if audit write fails**
  - `EXECUTION_TIMEOUT` entries: log with agent context for abuse pattern detection; fail-open if audit write fails (alert via stderr + gateway status flag)
  - Alert path (stderr `[OPENCLAW-AUDIT-FAIL]` + gateway status flag) must be established before audit write is attempted — not after-the-fact
- [ ] Violation event routing: who receives each signal type — skill caller, operator, or both? (determines @qa_guy test architecture — if operator-only, QA needs gateway-level test hooks, not skill API assertions)

**Task 2: `security-review-signoff` — @security_audit**
- [ ] Review implementation design against security-design-doc
- [ ] Written sign-off confirming sandbox is architecturally sound, capabilities correctly scoped, I/O handling safe
- [ ] Blocks: infra-observability-spec start (parallel), qa-containment-validation-plan start

**Task 3: `infra-observability-spec` — @infra**
- [ ] Runs parallel to or immediately after security-review-signoff; can be drafted while security design doc is in review
- [ ] Four typed error responses (not generic 500s): `SANDBOX_ESCAPE`, `RESOURCE_EXHAUSTED`, `EXECUTION_TIMEOUT`, `INPUT_REJECTED`
- [ ] Structured log entry schema for each signal: exact field names, types, required vs. optional
- [ ] Metric counter definitions: increment on each failure mode
- [ ] Health surface: sandbox process health check endpoint + format
- [ ] **Audit write failure behavior (locked — do not relitigate in code review):**

| Event | Audit write failure behavior | Alert path |
|-------|------------------------------|------------|
| `SANDBOX_ESCAPE` | Hard-abort — sandbox does not proceed; signal not returned to caller | N/A (never reaches caller) |
| `INPUT_REJECTED` | Hard-abort — input not processed; signal not returned to caller | N/A (never reaches caller) |
| `RESOURCE_EXHAUSTED` | Fail-open — signal returned to caller; failure logged on best-effort | `stderr` `[OPENCLAW-AUDIT-FAIL]` + gateway status flag |
| `EXECUTION_TIMEOUT` | Fail-open — signal returned to caller; failure logged on best-effort | `stderr` `[OPENCLAW-AUDIT-FAIL]` + gateway status flag |

- [ ] **Alert path implementation (v0.1):**
  - Primary: `stderr` write with prefix `[OPENCLAW-AUDIT-FAIL]` — survives application log failure, zero dependencies, shows up in any process supervisor
  - Secondary: in-memory gateway status flag (optionally persisted to `~/.openclaw/gateway.status`) — surfaced by health check endpoint; operator/monitoring polls this
  - Alert path must be established **before** audit write is attempted (fd + stderr handle ready at sandbox spawn time — not after-the-fact)
  - Alert path must be pluggable for future surfaces (system tray, Aight alert, etc.) — design for extensibility at v0.1
- [ ] **Audit log is a security artifact:** separate write path from application logging; separate retention policy; not rotated on standard log schedule; write-only from sandbox's perspective
- [ ] Named deliverable — @qa_guy cannot write executable test cases until signal names, log field schemas, and metric counters are confirmed here; implicit assumptions = useless test suites

**Task 4: `qa-containment-validation-plan` — @qa_guy**
- [ ] **BLOCKED on: security-review-signoff (Task 2) AND infra-observability-spec (Task 3) — both required**
- [ ] Test cases against the four named signals; assertions bound to actual field names from observability spec
- [ ] Silent failure test: two different failure modes must produce different observable outputs — any overlap = observability defect, must be fixed before plan advances
- [ ] Test architecture decision (depends on Task 1 violation routing answer): skill API assertions vs. gateway-level test hooks vs. log assertions
- [ ] Abuse pattern detection tests: repeated `RESOURCE_EXHAUSTED` from same agent ID; flood of `INPUT_REJECTED`

**Task 5: Implementation — @backend**
- [ ] **BLOCKED on: qa-containment-validation-plan (Task 4)**
- [ ] Sandboxed execution environment (sandbox-exec, stdio-only IPC)
- [ ] Capability scope: no network, no filesystem outside workspace, explicit memory ceiling
- [ ] Four distinct named error signals per spec: `SANDBOX_ESCAPE`, `RESOURCE_EXHAUSTED`, `EXECUTION_TIMEOUT`, `INPUT_REJECTED`
- [ ] Audit log write path (separate from application logs, write-only from sandbox, correct retention policy)
- [ ] Token schema for structured code output
- [ ] Agent manifest `allowed_modes` entry for code execution
- [ ] Depends on: skill runner (phase-2-skills-marketplace) + gateway-changes #21

**Task 6: `qa-containment-validation-execution` — @qa_guy**
- [ ] **BLOCKED on: implementation (Task 5)**
- [ ] Execute containment validation plan against live implementation
- [ ] Verify all four failure modes produce distinct, named signals
- [ ] Verify audit log is write-only from sandbox perspective
- [ ] Verify abuse pattern detection signals fire correctly
- [ ] @infra sign-off on observability surface before this closes
- [ ] **Ship gate: implementation cannot ship until this task closes with explicit QA sign-off**
