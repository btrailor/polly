# Onboarding & Progressive Teaching (OpenSpec)

Source of truth for Polly's onboarding, progressive feature revelation, and adaptive tutorial system. Detail: [docs/planning/phases/other/PHASE18_ONBOARDING.md](../../../docs/planning/phases/other/PHASE18_ONBOARDING.md).

> **Implementation Status:** 💭 Vision — no code exists for this system.
> This spec describes the target design. Implementation is planned for Tier 4 / Phase 18.
> Other specs should not design integration points against this system until implementation begins.

## Overview

Onboarding is how Polly teaches users to use Polly — without forced tutorials, through contextual education that reveals features when they're relevant. The system learns each user's pace and adapts.

**Core insight:** "Polly teaches you as you teach Polly." The onboarding experience mirrors the product's own learning philosophy.

## Key Principles

- **No forced tutorials** — Value before complexity.
- **Contextual education** — Suggest features at teachable moments.
- **Adaptive pacing** — Learn the user's pace; don't overwhelm or underwhelm.
- **Autonomy awareness** — Show users how Polly is learning and growing.

## Core Components

### 1. First-Run Wizard

Minimal, fast setup (<60s to first value):

1. **Welcome** — Name, brief intro.
2. **Domain setup** — Quick-start template selection (6 templates: Software Dev, Research, Creative Writing, Personal Knowledge, Academic, Polly Creator) or custom.
3. **API key** — At least one provider. Explain local vs cloud tradeoffs.
4. **Knowledge source** — Connect Obsidian vault or start fresh.
5. **First conversation** — Guided first query that demonstrates RAG + persona capabilities.

### 2. Progressive Feature Revelation

Features surface when contextually relevant, not all at once:

| Trigger | Feature Revealed | Condition |
|---|---|---|
| 5th conversation | Pattern Learning | System has enough data to show patterns |
| First note saved | Note Templates | User has engaged with notes |
| Domain tag used 3x | Domain-specific features | User is using domains |
| First Scribe activation | Publishing pipeline | User is writing |
| 10th conversation | Mental Models | Enough context for model suggestions |
| First code discussion | Code Workspace | User discusses code |
| 20+ notes | Knowledge Graph | Enough content for graph value |
| Multiple domains active | Cross-domain features | User is working polymathically |

Revelation UI: subtle, non-intrusive indicators (badge on ribbon, contextual tooltip, "Did you know?" in chat).

### 3. Adaptive Tutorial System

- Tutorials fade as user demonstrates competence.
- Re-surface if user appears confused (long pauses, repeated failed queries).
- Professor persona can be invoked for deeper teaching on any feature.
- Tutorial content itself lives in the curriculum system (Phase 23).

### 3a. Persona Introductions

First interaction with each persona includes a natural one-message orientation — not a tutorial wall:

- **Professor:** "I'm Polly's learning persona. I work in four modes: I can explain concepts, guide you through Socratic questioning, design learning curricula, or quiz you on material. The more you tell me about what you're trying to learn and why, the better I can tailor my approach. What are you working on?"
- **Programmer:** "I'm Polly's coding persona. I can write code, review it, debug issues, or plan refactors. I work best when you tell me what you're building and what's going wrong."
- **Architect:** "I'm Polly's planning persona. I help you design systems, break down complex problems, and think through tradeoffs."
- **Designer:** "I'm Polly's design persona. I can generate icons, patterns, and design assets, maintain design systems, review consistency, or help with visual direction. Constraints make better design."
- **Scribe:** "I'm Polly's writing persona. I help with research, drafting, and refinement. Tell me what you're writing and who it's for."

Delivered once per persona. Tracked in `user_journey.features_revealed` (e.g., `persona_intro_professor`).

### 3b. Prompt Coaching & Competency Tracking

After persona introductions, ongoing meta-pedagogy through prompt coaching:

- **Prompt injectors:** Detect improvable prompts and offer brief, contextual coaching per persona.
- **Competency tracking:** Per-persona, per-skill tracking (5 levels: 0–4). Coaching silences as user demonstrates mastery.
- **Progressive scaffolding fade:** Full explanation → brief reminder → assume competence → invisible operation.
- **Resolution of teach-vs-automate tension:** New users get scaffolding (teach). As competency grows, scaffolding fades (automate). Both approaches, sequenced.

Full details: [teaching spec](../teaching/spec.md) (Meta-Pedagogy section).

### 4. Autonomy Dashboard

Visual display of Polly's learning progress:

- **Token usage** — Local vs cloud ratio, cost tracking.
- **RAG hit rate** — How often local knowledge satisfies queries.
- **Pattern learning** — Number and types of patterns learned.
- **Topics going local** — Which topics Polly handles locally now that started as cloud.
- **Knowledge compound score** — Overall knowledge base growth and quality.

This dashboard is both an onboarding tool (shows Polly is learning) and an ongoing feature (tracks progressive autonomy).

### 5. Usage Pattern Detection

Learn user workflows to customize the experience:

- Preferred personas and modes.
- Common task sequences (inform Agent Swarm template suggestions).
- Peak usage times.
- Domain balance (which domains get most attention).
- Feature adoption rate (which features are used, which are ignored).

## Target Audiences

- **ADHD/Neurodivergent** — Minimal cognitive load, clear next-steps, no overwhelming options.
- **Polymaths** — Quick setup for multi-domain work, cross-domain features highlighted early.
- **Privacy-Conscious** — Clear data handling explanation, local-first emphasis, opt-in cloud.

## Success Criteria

- Time-to-first-value: <60 seconds.
- 70% feature discovery within first month.
- 80% of users view autonomy dashboard within first week.
- <5% tutorial dismissal rate (tutorials feel helpful, not annoying).

## Storage

```sql
CREATE TABLE user_journey (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    onboarding_complete BOOLEAN DEFAULT FALSE,
    current_stage TEXT,           -- 'first_run', 'exploring', 'proficient', 'power_user'
    features_revealed TEXT,       -- JSON array of feature IDs
    features_used TEXT,           -- JSON array of feature IDs + usage counts
    tutorials_completed TEXT,     -- JSON array
    preferences TEXT,             -- JSON (pacing, notification style)
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Implementation

**Phase 18 (Tier 4)** — 1–2 weeks. Depends on: Tier 3 features exist (so there's something to onboard users to).

## Reference

- [docs/planning/phases/other/PHASE18_ONBOARDING.md](../../../docs/planning/phases/other/PHASE18_ONBOARDING.md) — Full 1275-line spec
- [docs/planning/DESIGN_PHILOSOPHY.md](../../../docs/planning/DESIGN_PHILOSOPHY.md) — Progressive capability principle
- Curriculum: [curriculum spec](../curriculum/spec.md)
- Domains: [domains spec](../domains/spec.md)
- Teaching (meta-pedagogy): [teaching spec](../teaching/spec.md)
- Change folder: [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/)
