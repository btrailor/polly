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

- [ ] `MultiPanelChatLayout` — topology-agnostic renderer (Phase 1 foundation needed from @frontend)
- [ ] Message model `topology` field + `chorus_position: {row, col}` (Phase 1 architecture needed)
- [ ] Parallel dispatch pipeline (no shared context between agents)
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

- [ ] Depends on: skill runner (phase-2-skills-marketplace) + token schema
- [ ] Sandboxed execution environment (sandbox-exec, stdio-only IPC)
- [ ] Token schema for structured code output
- [ ] Agent manifest `allowed_modes` entry for code execution
