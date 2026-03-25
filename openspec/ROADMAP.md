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
| 3 | `phase-2-knowledge-skill` | 📋 Planned | Phase 1 complete |
| 4 | `phase-2-skills-marketplace` | 📋 Planned | Phase 1 complete |
| 5 | `phase-2-push-security` | ⚠️ Required pre-production | Phase 1 complete |
| 6 | `phase-2-lockdown-mode` | 📋 Planned | Phase 1 + architectural hooks set in Phase 1 |
| 7 | `phase-2-cognitive-artifact` | 📋 Planned | Phase 1 agent system complete |
| 8 | `phase-2-model-routing` | 📋 Planned | Phase 1 complete (@backend questions answered) |
| 9 | `phase-2-figma-integration` | 📋 Planned | Phase 1 complete (low priority) |
| 10 | `phase-3-cognitive-features` | 💡 Specced | Phase 2 Knowledge Skill |
| 11 | `phase-3-creative-systems` | 💡 Specced | Phase 2 Knowledge Skill |
| 12 | `phase-3-rag-routing` | 💡 Specced | Phase 2 Knowledge Skill + Phase 2 model-routing |
| 13 | `phase-4-federation` | 💡 Future | Phase 3 complete |

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
