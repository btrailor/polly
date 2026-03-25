# PROJECT_STATUS.md

**Owner:** @code_architect (writes) — all agents read-only  
**Updated:** 2026-03-25  
**Branch:** development  
**HEAD:** 200f308

---

## Current Phase

**Phase 1 — Foundation** (in progress)

---

## What's Shipped

| Item | Commit | Notes |
|------|--------|-------|
| Voice button components | 7c0d110 | VoiceButton, VoiceButtonActive, VoiceButtonIdle |
| FIGMA_INTEGRATION.md | 7c0d110 | Phase 2 spec, root level |
| MONOME_LAYER.md | 7c0d110 | Aesthetic/philosophical foundation |
| INFLUENCE_GUIDE.md | 7c0d110 | Liz SDLC + Monome synthesis |
| SPEC_INDEX.md | aa16bdf | Flat spec index, escalation triggers |
| MASTER_ROADMAP.md (updated) | aa16bdf | Voice→Phase 1, Figma→Phase 2, index linked |
| KNOWLEDGE_SKILL.md | 01133b7→955c414→d56d698 | Phase 2, Planned, @security_audit ✅ |
| SKILLS_MARKETPLACE.md | 85922e3 | Phase 2, Draft, @security_audit review pending |
| MCP_ADAPTER.md | 200f308 | Phase 2, Draft, @security_audit review required |
| ASSET_STATE_MACHINE.md | 860801e | Phase 2 support, Draft (@backend) |

---

## Active Work (in flight right now)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Token schema JSON | @design_eng | 4pm today | In progress |
| QA workflow doc | @design_eng | 4pm today | In progress |
| Structured output format (POLLY_AGENT_TEMPLATES.md) | @design_eng | 4pm today | In progress |
| Staging view wireframe | @frontend | After @design_eng branch | Waiting on branch |
| CL4R1T4S structured pass | @researcher | Async | In progress |
| Push registration security fix | @backend | Pre-production gate | Queued |
| SKILLS_MARKETPLACE.md security review | @security_audit | TBD | Queued |
| MCP_ADAPTER.md security review | @security_audit | TBD | Queued |

---

## Specs Status

| Spec | Phase | Status | Blocking |
|------|-------|--------|---------|
| `KNOWLEDGE_SKILL.md` | 2 | 📋 Planned | Nothing — @security_audit ✅ |
| `SKILLS_MARKETPLACE.md` | 2 | 📋 Draft | @security_audit review |
| `MCP_ADAPTER.md` | 2 | 📋 Draft | @security_audit review, depends SKILLS_MARKETPLACE |
| `ASSET_STATE_MACHINE.md` | 2 | 📋 Draft | @backend Q1/Q3 open |
| `PROJECT_STATUS.md` | 1 | 📋 Draft | — |
| `AGENT_BOOTSTRAP_DEV.md` | 1 | 📋 Draft | — |
| `SKILLS_MARKETPLACE.md` | 2 | 📋 Planned | — |
| `DISTRIBUTED_NODES.md` | 3 | 💡 Idea | Phase 3, not started |
| `CREATIVE_CODE_SKILL.md` | 3 | 💡 Idea | Needs token schema + skill runner |
| `TREE_OF_THOUGHTS.md` | 3 | 💡 Idea | Phase 3, not started |
| `MCP_ADAPTER.md` | 2 | 📋 Planned | SKILLS_MARKETPLACE ✅ unblocked |

---

## Open Blockers

| Blocker | Owner | Impact |
|---------|-------|--------|
| SKILLS_MARKETPLACE.md open questions §9 (Q1: key rotation) | @security_audit | Blocking Verified tier implementation |
| MCP_ADAPTER.md §12 Q1: Linux sandbox equivalent to sandbox-exec | @infra | Blocking non-macOS gateway support |
| MCP_ADAPTER.md §12 Q2: static manifest inspection vs dry-run | @backend | Affects install-time linting path |
| ASSET_STATE_MACHINE.md Q3: cross-skill asset sharing default | @backend | Minor, default=no agreed verbally |
| **`useVoiceRecording` hook is scaffolded only** — no real audio recording | @frontend | VOICE_BEHAVIOR_TESTS.md (543 lines) can't run. Voice QA is blocked until real impl. |
| **VOICE_INTERACTION.md REQ-VOICE-01 uses Swift APIs** (`UIApplication.shared.isIdleTimerDisabled`) | @frontend | Must be replaced with `expo-keep-awake`. Spec needs correction too. |
| **`VoiceMicButton.tsx` line 269 uses emoji 🎤** instead of Lucide `Mic` icon | @frontend | Violates §18.3 Design Constitution. Will ship as emoji if not fixed. |
| **`polly-ios/src/colors.ts` is a duplicate** of `src/theme/colors.ts` | @frontend | Maintenance hazard — wrong file will be edited. Delete `src/colors.ts`. |
| **`PROFESSOR_STUDIES_MODE.md`** referenced in `chat.tsx` header but doesn't exist | Brett to confirm | Is this a planned spec or stale reference? |
| **Vault access duality unspecced** — Phase 1 uses iOS expo-document-picker bookmarks; Phase 2 Knowledge Skill uses gateway filesystem reads. Separate vault paths, not acknowledged in spec. | @backend + @code_architect | Knowledge Skill spec needs a section on gateway vault path config. |

---

## Git State

- Branch: `development`
- HEAD: `200f308`
- Remote: `git@github.com:btrailor/polly.git`
- Author: Brett Gershon <Brett.gershon@gmail.com> ✅
- Clean: yes

---

## Phase 1 Remaining (before Phase 2 begins)

- [ ] `AGENT_BOOTSTRAP_DEV.md` — write spec and implement bootstrap sequence
- [ ] Phase 1 features from `MASTER_ROADMAP.md` — verify all items checked
- [ ] Push registration security fix (@backend) — roadmap-required pre-production gate

---

## Notes

- `specs/` folder at repo root = archived legacy content. Never reference, never edit.
- Live specs = root-level `.md` files only.
- Code Architect owns writes to this file. All other agents read-only.
- OpenSpec escalation trigger #2 hit (dependency chain: MCP_ADAPTER depends on SKILLS_MARKETPLACE). Trigger #4 hit (>8 specs from idea dump). Not blocking — both documented in SPEC_INDEX.md.
