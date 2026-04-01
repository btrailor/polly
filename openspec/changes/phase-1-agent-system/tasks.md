# Phase 1: Agent System

**Status:** 🔨 In progress  
**Gate:** None — runs parallel to iOS Foundation  
**Spec source:** `POLLY_AGENT_TEMPLATES.md`, `SOMATIC_INTERFACE.md`, `AGENT_BOOTSTRAP_DEV.md`

## What Actually Exists Right Now

- `POLLY_AGENT_TEMPLATES.md` — 43 complete SOUL templates *(updated 2026-04-01)*:
  - Standard SOUL Baseline: written and complete (5 blocks)
  - Agent manifest + Sensibility schemas: defined in prose/JSON snippets, not per-agent fields
  - All 43 agents: have full SOUL templates with Prosodic Sensitivity sections — including all 10 previously stubbed agents (Estimator, Librarian, Mirror, Janitor, Interlocutor, Scaffolder, Archivist, Ambient, Experimentalist, Translator)
  - `allowed_modes`: documented in schema section with Phase 1–2 defaults and Phase 3 additions per agent
  - Team Membership table: 16 teams × all 43 agents — complete
  - ⚠️ `suggested_prompts` field: NOT YET WRITTEN on any of the 43 agents — this is the remaining content task
- `SOMATIC_INTERFACE.md` — prosodic engagement state spec: written
- `AGENT_BOOTSTRAP_DEV.md` — bootstrap sequence and hard rules: written
- `PROJECT_STATUS.md` — exists but was aspirational, not accurate

## Tasks

### Standard SOUL Baseline
- [x] Context Management block
- [x] Work Character block
- [x] Tool Use block
- [x] Memory Writes block (6 sections including `## Reasoning`)
- [x] Epistemological Commitments block (Layer 7 — cui bono, material-first, scapegoat suspicion, defamiliarization, second-order honesty)

### Agent Schema
- [x] Agent manifest schema defined (`id`, `category`, `allowed_modes`)
- [x] Sensibility schema defined (`aesthetic` layer + `structural_rules` stub)
- [ ] `allowed_modes` field written per-agent for all 43 agents (currently only documented in schema section, not on individual agents)
- [ ] `suggested_prompts: string[]` field added to all 43 agent templates (3–4 items each) — feeds cold start empty state UI

### Agent SOULs — 33 Established Agents
- [x] All 6 Builder agents (full SOUL + Prosodic Sensitivity)
- [x] All 9 Thinker agents (full SOUL + Prosodic Sensitivity)
- [x] All 6 Creator agents (full SOUL + Prosodic Sensitivity)
- [x] All 3 Operator agents (full SOUL + Prosodic Sensitivity)
- [x] All 4 Specialist agents (full SOUL + Prosodic Sensitivity)
- [x] 5 of 10 Wildcard agents (Devil's Advocate, Mentor, Mirror-stub — partial)

### Agent SOULs — 10 New Agent Stubs (need full templates)

**Downstream blockers — do not skip these:**
- **The Librarian** → blocks `web_import` shipping (`phase-2-web-fetch` / Phase 3A). `web_import` is Librarian-scoped; no SOUL = no implementation gate.
- **All 10** → block `phase-2-gesture-layer`. All 43 agents need `## Gesture Vocabulary` sections injected by Phase 2; stubs must have full SOULs first so @design_eng can write their vocabulary sections.
- **The Janitor + Ambient Agent** → block Phase 3 maintenance features (gesture retirement suggestions, Today View card suggestions from Builder).

Owner: @design_eng (SOUL voice + register profile). @code_architect reviews manifest fields (`allowed_modes`, `autonomy_level`) for each.

- [x] The Estimator — write full SOUL template + Prosodic Sensitivity section + `autonomy_level` + `allowed_modes`
- [x] The Librarian — write full SOUL template + Prosodic Sensitivity section + `autonomy_level: "reactive"` + `allowed_modes: ["web_import", "vault_write"]` — **PRIORITY: blocks web_import (Phase 3A)**
- [x] The Mirror — write full SOUL template + Prosodic Sensitivity section + `autonomy_level` + `allowed_modes`
- [x] The Janitor — write full SOUL template + `autonomy_level: "proactive"` + `allowed_modes` — system agent, proactive maintenance behaviors
- [x] The Interlocutor — write full SOUL template + Prosodic Sensitivity section + `autonomy_level` + `allowed_modes`
- [x] The Scaffolder — write full SOUL template + Prosodic Sensitivity section + `autonomy_level` + `allowed_modes`
- [x] The Archivist — write full SOUL template + Prosodic Sensitivity section + `autonomy_level: "proactive"` + `allowed_modes`
- [x] The Ambient Agent — write full SOUL template; document explicitly as non-conversational (no Prosodic profile); `autonomy_level: "proactive"`; no `## Prosodic Calibration` section
- [x] The Experimentalist — write full SOUL template + Prosodic Sensitivity section + `autonomy_level` + `allowed_modes`
- [x] The Translator — write full SOUL template + Prosodic Sensitivity section + `autonomy_level` + `allowed_modes`

### Team Rosters
- [x] 16 team templates defined
- [x] Agent → Team Membership table (16 teams × all 43 agents)

### Somatic Interface
- [x] Prosodic engagement state spec locked (`SOMATIC_INTERFACE.md`)
- [ ] Gateway: `prosodics` nullable field on ALL message objects (not voice-gated) — @backend (see `phase-1-gesture-layer`)
- [ ] iOS: Phase 1 prosodic signal extraction — `speechRate` + `turnLengthWords` from transcript metadata — @frontend (see `phase-1-gesture-layer`)
- [ ] iOS: Waveform orb ambient feedback states — @frontend (see `phase-1-gesture-layer`)
- [ ] SOUL Baseline: add Prosodic Calibration block (6th block) — documents flowing/processing/struggling calibration; "never label the state to Brett" rule
- [ ] iOS: `MultiPanelChatLayout` with topology-aware message data model — @frontend

### Bootstrap + Ops
- [x] `AGENT_BOOTSTRAP_DEV.md` — 5-step bootstrap sequence, hard rules
- [ ] `PROJECT_STATUS.md` — needs to be rewritten to reflect actual state (currently aspirational)

### Agent Behavior Contract (AGENT_BEHAVIOR_CONTRACT.md §8–9 Phase 1 tasks)
- [ ] Add domain boundary protocol (§5.1) to SOUL Baseline footer or per-agent SOULs in `POLLY_AGENT_TEMPLATES.md`
- [ ] Write `autonomy_level` value for all 43 agents in agent manifest — default `reactive`; exceptions: Ops Coordinator + Scheduler = `proactive`; Ambient Agent + Janitor = `autonomous`
- [ ] Write `allowed_modes` for all 43 agents (schema exists; values not written yet — see Phase 3 selectivity rules in `POLLY_AGENT_TEMPLATES.md`)
- [ ] Document iOS client boundaries in agent development guide (what agents describe vs. what iOS client does — §5.2)

## Done when
All 43 agent SOUL templates complete. `allowed_modes` written per-agent. `autonomy_level` written per-agent. Somatic interface gateway field shipped. @backend confirms message schema.
