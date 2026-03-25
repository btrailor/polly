# Polly Spec Index

Single source of truth for all spec documents. A spec doesn't officially exist until it's listed here.

---

## How This Works

- **All specs live at `~/polly/` root** — flat, no subdirectories
- **Naming convention:** `SCREAMING_SNAKE_CASE.md` (e.g. `VOICE_INTERACTION.md`)
- **A spec is "active" when:** it's listed here with a phase and status
- **A spec is "reference" when:** it informs decisions but isn't directly implemented (e.g. philosophy docs)
- **Before writing a new spec:** add it here first with status `planned`, then write it

---

## Active Specs

| Spec | Phase | Status | What it covers |
|------|-------|--------|----------------|
| `POLLY_IOS_SPEC.md` | 1–4 | ✅ Authoritative | Full iOS feature spec — canonical source of truth |
| `POLLY_AGENT_TEMPLATES.md` | 1–4 | ✅ Authoritative | 31 agent templates, team rosters, SOUL content |
| `VOICE_INTERACTION.md` | 1 | 🔨 In progress | Voice requirements: idle timer, mic button prominence, interruption recovery |
| `COPY_VOICE.md` | 1 | 🔨 In progress | Voice design tokens, state machine, copy patterns, accessibility |
| `VOICE_BEHAVIOR_TESTS.md` | 1 | 🔨 In progress | QA test suite for voice interaction |
| `FIGMA_INTEGRATION.md` | 2 | 📋 Planned | Figma link-surfacing in chat; deep-link to boards from spec context |

---

## Reference Docs

Not directly implemented — inform design and agent behavior decisions.

| Doc | What it is |
|-----|-----------|
| `MASTER_ROADMAP.md` | Phase sequencing and feature pipeline |
| `MONOME_LAYER.md` | Aesthetic-philosophical foundation (the *why* behind design decisions) |
| `INFLUENCE_GUIDE.md` | Liz's Agentic SDLC + Monome synthesis — operational methodology |
| `README.md` | Project overview |

---

## Status Key

| Status | Meaning |
|--------|---------|
| ✅ Authoritative | Complete, stable, source of truth — changes require deliberate decision |
| 🔨 In progress | Being actively implemented |
| 📋 Planned | Spec written, not yet in implementation |
| 💡 Idea | Not yet specced — placeholder for incoming work |
| ✅ Done | Shipped and verified |

---

## Escalation Trigger — When to Move to OpenSpec

Adopt the full OpenSpec system (`openspec/` directory, `changes/` proposals, `INDEX.md`) when **any one** of these is true:

1. **3+ specs in "In progress" simultaneously** — coordination overhead exceeds this index's capacity
2. **Dependency chain exists** — a spec can't be implemented until another spec is done
3. **Ownership ambiguity** — two agents conflict about what's in scope for a feature
4. **Idea dump produces 8+ new specs** — volume requires proposal → review → prioritize workflow

Until then: add to this index, keep specs at root, update status as work moves.

---

*Last updated: 2026-03-25*
