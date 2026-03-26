# Polly — OpenSpec Entry Point

This is the authoritative build documentation for Polly. Read this first.

## What Polly Is

A native iOS app (React Native + Expo) connecting to a self-hosted OpenClaw gateway. A team of intelligent agents that know your work, your Obsidian vault, and your mental models. Local-first. Privacy by architecture.

## How to Use This Documentation

**If you're starting implementation:** Go to `changes/` and find the current active phase. Read `tasks.md` top to bottom. Work through checkboxes in order. Check items off as work is done.

**If you want to understand what's currently built:** Read `specs/`. These describe only what exists and is running.

**If you're proposing new work:** Use `/opsx:propose "your idea"` to create a new change.

**If a phase is complete:** Use `/opsx:archive <change-name>` — tasks.md is archived, specs/ is updated.

## Build Order

| # | Change | Status | Gate |
|---|--------|--------|------|
| 1 | `phase-1-ios-foundation` | 🔨 In progress | — |
| 2 | `phase-1-agent-system` | 🔨 In progress | — |
| 3 | `phase-1-testing-infrastructure` | 📋 Planned | Must ship alongside Phase 1 features |
| 4 | `phase-2-knowledge-skill` | 📋 Planned | Phase 1 complete |
| 5 | `phase-2-skills-marketplace` | 📋 Planned | Phase 1 complete |
| 6 | `phase-2-push-security` | ⚠️ Required pre-production | Phase 1 complete |
| 7 | `phase-2-gateway-changes` | ⚠️ @backend — all 14 tasks | Staged by wave; wave 0 = pre-prod gate |
| 8 | `phase-2-push-notifications` | 📋 Planned | push-security + gateway #1 #2 |
| 9 | `phase-2-voice-upgrade` | 📋 Planned | Phase 1 voice working |
| 10 | `phase-2-vault-browser` | 📋 Planned | Phase 1 bookmark + knowledge-skill |
| 11 | `phase-2-integrations` | 📋 Planned | Phase 1 settings |
| 12 | `phase-2-gateway-discovery` | 📋 Planned | Phase 1 LAN WebSocket |
| 13 | `phase-2-today-crud` | 📋 Planned | Phase 1 Today display |
| 14 | `phase-2-image-attachments` | 📋 Planned | Phase 1 chat |
| 15 | `phase-2-message-search` | 📋 Planned | Phase 1 message cache |
| 16 | `phase-2-lockdown-mode` | 📋 Planned | Phase 1 + architectural hooks set in Phase 1 |
| 17 | `phase-2-cognitive-artifact` | 📋 Planned | Phase 1 agent system complete |
| 18 | `phase-2-model-routing` | 📋 Planned | Phase 1 complete (gateway-changes #7 #8 #9 required) |
| 19 | `phase-2-swarm-coordination` | 📋 Planned | Phase 1 group chat foundation (gateway-changes #5 #6 required) |
| 20 | `phase-2-sensibility-behavior` | 📋 Planned | Phase 1 sensibility foundation complete (gateway-changes #12) |
| 21 | `phase-2-figma-integration` | 📋 Planned | Phase 1 complete (low priority) |
| 22 | `phase-2-ipad-layout` | 📋 Planned | Phase 1 complete (low priority) |
| 23 | `phase-3-cognitive-features` | 💡 Specced | Phase 2 Knowledge Skill |
| 24 | `phase-3-creative-systems` | 💡 Specced | Phase 2 Knowledge Skill |
| 25 | `phase-3-rag-routing` | 💡 Specced | Phase 2 Knowledge Skill + Phase 2 model-routing |
| 26 | `phase-3-swarm-structured` | 💡 Specced | Phase 2 swarm-coordination + Phase 1 agent system (Liaison SOUL) |
| 27 | `phase-3-sensibility-picker` | 💡 Specced | Phase 2 sensibility-behavior complete |
| 28 | `phase-4-federation` | 💡 Future | Phase 3 complete |

## Domains (specs/)

| Domain | What it covers |
|--------|---------------|
| `agent-system/` | What's shipped: SOUL baseline, 33 agent templates, team rosters (10 stubs pending) |
| `ios-app/` | Actual codebase state: what's built, what's a stub, missing dependencies |
| `knowledge/` | Locked contracts + prompt injection layer hierarchy (implementation in Phase 2) |
| `infrastructure/` | Skill manifest format, security model, push security gate |

## Reference Docs (not build-facing)

These root-level `.md` files are source material, not build tasks. They inform the changes above.

| File | Role |
|------|------|
| `INFLUENCE_GUIDE.md` | Development methodology (Liz SDLC + Monome synthesis) |
| `MONOME_LAYER.md` | Aesthetic + philosophical foundation |
| `CL4R1T4S_RESEARCH.md` | EIS pattern vocabulary (input to phase-3-cognitive-features) |
| `ANTI_PRODUCTIVITY.md` | Practice Layer dormancy data source (input to phase-3-cognitive-features) |
| `MASTER_ROADMAP.md` | Superseded by this file |
| `SPEC_INDEX.md` | Superseded by this structure |
| `PROJECT_STATUS.md` | To be rewritten — was aspirational, not accurate |
| `README.md` | Project overview |

## Source Specs (narrative reference)

The full narrative specs live at `~/polly/*.md`. The OpenSpec `specs/` and `changes/` are the build-facing extracted form. When there's a conflict, the change's tasks.md wins for in-flight work; the root `.md` file is the narrative source of record.
