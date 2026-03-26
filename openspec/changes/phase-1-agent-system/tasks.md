# Phase 1: Agent System

**Status:** 🔨 In progress  
**Gate:** None — runs parallel to iOS Foundation  
**Spec source:** `POLLY_AGENT_TEMPLATES.md`, `SOMATIC_INTERFACE.md`, `AGENT_BOOTSTRAP_DEV.md`

## What Actually Exists Right Now

- `POLLY_AGENT_TEMPLATES.md` — large file with substantial spec content, but mixed state:
  - Standard SOUL Baseline: written and complete (5 blocks)
  - Agent manifest + Sensibility schemas: defined in prose/JSON snippets, not per-agent fields
  - 33 "established" agents: have full SOUL templates with Prosodic Sensitivity sections
  - 10 new agents (Estimator, Librarian, Mirror, Janitor, Interlocutor, Scaffolder, Archivist, Ambient, Experimentalist, Translator): exist only as stubs in `## Agent Stubs — Templates Pending` section — no SOUL templates written
  - `allowed_modes`: documented in schema section only — not written per-agent in any manifest block
  - Team Membership table: 16 teams × all 43 agents — complete
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
- [ ] The Estimator — write full SOUL template + Prosodic Sensitivity
- [ ] The Librarian — write full SOUL template + Prosodic Sensitivity
- [ ] The Mirror — write full SOUL template + Prosodic Sensitivity
- [ ] The Janitor — write full SOUL template + Prosodic Sensitivity
- [ ] The Interlocutor — write full SOUL template + Prosodic Sensitivity
- [ ] The Scaffolder — write full SOUL template + Prosodic Sensitivity
- [ ] The Archivist — write full SOUL template + Prosodic Sensitivity
- [ ] The Ambient Agent — write full SOUL template + Prosodic Sensitivity (or document explicitly as non-conversational/no-Prosodic-profile)
- [ ] The Experimentalist — write full SOUL template + Prosodic Sensitivity
- [ ] The Translator — write full SOUL template + Prosodic Sensitivity

### Team Rosters
- [x] 16 team templates defined
- [x] Agent → Team Membership table (16 teams × all 43 agents)

### Somatic Interface
- [x] Prosodic engagement state spec locked (`SOMATIC_INTERFACE.md`)
- [ ] Gateway: `prosodics` nullable field on ALL message objects (not voice-gated) — @backend
- [ ] iOS: client-side prosodic signal extraction from audio buffer — @frontend (Phase 1 deliverable, blocked on real audio recording)
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
