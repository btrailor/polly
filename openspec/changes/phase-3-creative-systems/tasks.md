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

**Hard-blocker dependency chain — these are sequential gates, not advisory ordering. A step cannot start until the prior step is in done/approved state. No exceptions under schedule pressure:**

1. **[HARD GATE] `security-design-doc`** — @security_audit writes sandbox security design doc: boundary model, capability scope (filesystem, network, runtime), I/O handling spec. No implementation begins until this exists.
2. **[HARD GATE] `security-review-signoff`** — @security_audit reviews sandbox implementation design and signs off in writing. Blocks step 3.
3. **[HARD GATE] `qa-containment-validation`** — @qa_guy validates observable failure modes (see below). **Cannot enter "in progress" until `security-review-signoff` is approved.** Blocks step 4. @infra must be looped in for signal/observability section.
4. **[SHIP GATE]** Implementation eligible only after steps 1–3 complete.

**Containment Validation Requirements (@qa_guy scope — gateway-changes #21 prerequisite):**
- Sandbox escape attempt → must produce distinct, named error signal (not a generic 500)
- Resource exhaustion (CPU/memory ceiling hit) → must produce graceful degradation signal, not a hung request
- Timeout breach → must produce explicit timeout signal with context, not a swallowed exception
- Input rejection at sandbox boundary → must produce rejection signal distinguishable from execution failure
- **Silent failures are a defect:** if two different failure modes produce the same observable output, that's an observability defect, not a logging gap — must be fixed before QA sign-off
- @infra loop-in required for signal/observability spec section — "is this detectable" is only answerable knowing what instrumentation the gateway surfaces

**Implementation tasks (start only after all 3 gates pass):**
- [ ] Sandboxed execution environment (sandbox-exec, stdio-only IPC)
- [ ] Capability scope: no network, no filesystem outside workspace, explicit memory ceiling
- [ ] Four distinct named error signals: `SANDBOX_ESCAPE`, `RESOURCE_EXHAUSTED`, `EXECUTION_TIMEOUT`, `INPUT_REJECTED`
- [ ] Token schema for structured code output
- [ ] Agent manifest `allowed_modes` entry for code execution
- [ ] Depends on: skill runner (phase-2-skills-marketplace) + token schema + gateway-changes #21
