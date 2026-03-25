# Polly — OpenSpec Entry Point

This is the authoritative build documentation for Polly. Read this first.

## What Polly Is

A native iOS app (React Native + Expo) connecting to a self-hosted OpenClaw gateway. A team of intelligent agents that know your work, your Obsidian vault, and your mental models. Local-first. Privacy by architecture.

## How to Use This Documentation

**If you're starting implementation:** Go to `changes/` and find the current active phase. Read `proposal.md`, then `design.md`, then start working through `tasks.md`.

**If you want to understand what's currently built:** Read `specs/`. These describe only what exists and is running.

**If you're proposing new work:** Use `/opsx:propose "your idea"` to create a new change.

## Build Order

| # | Change | Status | Gate |
|---|--------|--------|------|
| 1 | `phase-1-ios-foundation` | 🔨 In progress | — |
| 2 | `phase-1-agent-system` | 🔨 In progress | — |
| 3 | `phase-2-knowledge-skill` | 📋 Planned | Phase 1 complete |
| 4 | `phase-2-skills-marketplace` | 📋 Planned | Phase 1 complete |
| 5 | `phase-2-push-security` | ⚠️ Required pre-production | Phase 1 complete |
| 6 | `phase-3-cognitive-features` | 💡 Specced | Phase 2 Knowledge Skill |
| 7 | `phase-3-creative-systems` | 💡 Specced | Phase 2 Knowledge Skill |
| 8 | `phase-4-federation` | 💡 Specced | Phase 3 complete |

## Domains (specs/)

| Domain | What it covers |
|--------|---------------|
| `agent-system/` | What's shipped: SOUL baseline, agent templates, team rosters |
| `ios-app/` | What's shipped: iOS client screens, voice, design system |
| `knowledge/` | What's shipped: Knowledge Skill contracts (Phase 2 adds implementation) |
| `infrastructure/` | What's shipped: skill manifest format, security model |

## Source Specs (reference material)

The full narrative specs live at `~/polly/*.md`. The OpenSpec `specs/` and `changes/` are the build-facing extracted form. When there's a conflict, the change's delta spec wins for in-flight work; the root `.md` file is the narrative source.
