# Phase 1: Agent System

**Status:** 🔨 In progress  
**Gate:** None — runs parallel to iOS Foundation  
**Spec source:** `POLLY_AGENT_TEMPLATES.md`, `SOMATIC_INTERFACE.md`, `AGENT_BOOTSTRAP_DEV.md`

## Goal

Complete agent template system ready for implementation: all 43 SOULs, team rosters, schema definitions, and the Standard SOUL Baseline that every agent inherits.

## Tasks

### Standard SOUL Baseline
- [x] Context Management block
- [x] Work Character block
- [x] Tool Use block
- [x] Memory Writes block (6 sections including `## Reasoning`)
- [x] Epistemological Commitments block (Layer 7 — cui bono, material-first, scapegoat suspicion, defamiliarization, second-order honesty)

### Agent Schema
- [x] Agent manifest schema (`id`, `category`, `allowed_modes`)
- [x] Sensibility schema (`aesthetic` layer + `structural_rules` stub for Phase 3)

### Agent SOULs — All 43
- [x] All 6 Builder agents
- [x] All 9 Thinker agents
- [x] All 6 Creator agents
- [x] All 3 Operator agents
- [x] All 4 Specialist agents
- [x] All 10 Wildcard agents
- [x] All 3 System agents (Janitor, Ambient, Liaison)
- [x] `## Prosodic Sensitivity` section on all 43 SOULs

### Team Rosters
- [x] 16 team templates defined
- [x] Agent → Team Membership table (authoritative, all 16 teams × all 43 agents)

### Somatic Interface
- [x] Prosodic engagement state spec locked (`SOMATIC_INTERFACE.md`)
- [ ] Gateway: `prosodics` nullable field on ALL message objects (not voice-gated) — @backend
- [ ] iOS: client-side prosodic signal extraction from audio buffer — @frontend Phase 1 deliverable
- [ ] iOS: `MultiPanelChatLayout` with topology-aware message data model — @frontend

### Bootstrap + Ops
- [x] `AGENT_BOOTSTRAP_DEV.md` — 5-step bootstrap sequence, hard rules
- [x] `PROJECT_STATUS.md` — living cross-session state doc

## Done when
All agent SOULs finalized. Somatic interface gateway field shipped. @backend confirms message schema. Ready to hand off to implementation.
