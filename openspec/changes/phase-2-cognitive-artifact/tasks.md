# Phase 2/3: Cognitive Artifact

**Status:** 📋 Planned  
**Gate:** Phase 1 agent system complete; Phase 3 for full export  
**Spec source:** `COGNITIVE_ARTIFACT.md`

## Goal

A portable, versioned export of everything Polly knows about how Brett thinks — mental models, reasoning patterns, intellectual positions, conversation history summaries. The "Polly README" that travels with the user.

## Phase Breakdown

**Phase 1 hook (tracked in phase-2-knowledge-skill):** `manifest.json` export — @backend owns, one task  
**Phase 2:** Export package structure, Archivist README generation  
**Phase 3:** Full export layers (requires Knowledge Skill + Oral History)

## Tasks

### Phase 2 — Export Architecture
- [ ] Export package directory structure: define layer layout (`manifest.json`, `soul/`, `models/`, `positions/`, `conversations/`)
- [ ] `present: false` for non-existent layer directories (non-destructive export)
- [ ] Archivist README: first-person narrative summary auto-generated from conversation history
- [ ] Export trigger: manual via Settings → Export Cognitive Artifact

### Phase 3 — Full Export Layers (requires Knowledge Skill + Oral History)
- [ ] Mental model layer: usage history, effectiveness per model per agent
- [ ] Position layer: extracted intellectual positions with timestamps (from Temporal Intelligence)
- [ ] Conversation history layer: session summaries (from Knowledge Skill conversation adapter)
- [ ] Oral history layer: voice transcript synthesis (from Oral History)
- [ ] Import UX: onboarding flow accepts `.cognitive-artifact` package to bootstrap new gateway

## Done when
Export package generates correctly. Archivist README is readable and accurate. Import flow works on fresh onboarding.
