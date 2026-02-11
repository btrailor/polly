# Learning Profile & Administrator Profile — Proposal

**Created:** February 2026  
**Scope:** Frontend (Learning page redesign), Backend (prompt injectors, competency tracking, email/calendar integration), both personas  
**Tier/Phase:** Tier 4 — Phase 22 (Teaching, frontend), Phase 18 (Onboarding), Phase 20 (Communication)

---

## What

Two persona profiles that define how Polly teaches the user and how Polly manages communication:

### 1. Learning Profile

**UI Redesign:** The analytics section currently dominates the Learning page center area. This is a "banking model" problem (Freire): measuring deposits instead of supporting transformation. Analytics move to a collapsible Review tab; the active learning surface becomes center stage.

**Meta-Pedagogy System:** Polly teaches users how to use Polly more effectively over time. Persona-specific prompt injectors detect when a user's prompt could be improved and offer brief, contextual coaching. Coaching fades as competency grows — a concrete implementation of progressive independence.

**Competency Tracking:** Per-persona, per-skill tracking of user prompting competency. Five levels (0–4): not encountered → introduced → reminded → competent → expert. Stored in user profile. Drives the scaffolding-fade system.

### 2. Administrator Profile

**Superhuman-Informed Design:** The Administrator persona gains four concrete modes (Schedule, Compose, Triage, Remind) informed by Superhuman's core insight: speed is a feature. Polly doesn't replace the email client — it provides an intelligence layer on top, making email processing take 15 minutes instead of 90.

**Triage Workflow:** Sequential, flow-based email processing (Superhuman-style). For each email: Reply, Delegate, Defer, Archive, or Flag. Split processing by email type. AI prioritization that learns from response patterns.

**Compose with Voice Matching:** Draft generation that sounds like the user, with context injection from the knowledge base.

**Calendar Intelligence:** Find availability, detect conflicts, energy-aware scheduling from user profile.

## Why

### Learning Profile

- The current Learning page centers analytics over learning. This communicates the wrong priorities. The fix is small (move analytics to a tab) but the philosophy matters: the active learning surface — the conversation with Professor — should be center stage.
- The meta-pedagogy system makes Polly's progressive independence concrete. Instead of abstract "over time Polly gets better," specific prompt coaching teaches transferable thinking skills: articulating goals, specifying constraints, recognizing what kind of help you need.
- This connects to the onboarding spec's "tutorials fade as user demonstrates competence" principle. Competency tracking provides the mechanism.

### Administrator Profile

- The communication spec already defines Phase 20a–20c (email intelligence, calendar, progressive autonomy). The Administrator Profile adds concrete UX design informed by what Superhuman gets right: keyboard-driven flow, sequential processing, temporal controls, voice-matched drafts.
- The Administrator has four defined modes (Configure, Monitor, Maintain, Automate) in the personas spec but they're generic. This spec replaces them with communication-specific modes (Schedule, Compose, Triage, Remind) when the Administrator is operating in communication context.
- Cross-persona integration: Scribe captures action items from emails, Architect gets informed of technical emails, Publisher uses Compose for newsletters, Librarian indexes reference-worthy threads.

## Why Now

- Phase 22 (Teaching Mode) frontend is ~40% complete. This spec defines what the center area should be before the frontend work continues.
- The onboarding spec (Phase 18) already calls for "tutorials that fade as competency grows." The competency tracking system is the missing mechanism.
- The communication spec exists but lacks UX design. Defining the Administrator modes now means implementation has a clear target.

## Scope

### In Scope

- Learning page center area redesign (4 states: active session, curriculum view, practice space, review)
- Prompt injector system (pattern detection, coaching, competency tracking)
- Per-persona competency profile (`prompting-competency.yml`)
- Onboarding persona introductions (one-time first-interaction messages)
- Progressive scaffolding fade (levels 0–4)
- Administrator modes: Schedule, Compose, Triage, Remind
- Slash commands for email/calendar triage
- Voice-matched draft generation
- Superhuman-style flow-based processing

### Out of Scope (for now)

- Full email client replacement
- IMAP/Gmail API implementation (that's Phase 20a)
- EventKit calendar access (that's Phase 20b, requires Phase 9)
- Communication autonomy levels 3–4 (Phase 20c)
- Practice space embedding (p5.js, SuperCollider) — design defined, implementation depends on Phase 17/27

## Impact on Existing Systems

| System                       | Impact                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Teaching**                 | Learning page redesigned. Meta-pedagogy layer added.                                                                                        |
| **Onboarding**               | Competency tracking mechanism added. Persona introductions defined. Progressive fade formalized.                                            |
| **Personas (Professor)**     | Professor context-aware: provides coaching moments. Learning center area states defined.                                                    |
| **Personas (Administrator)** | Modes expanded from generic (Configure/Monitor/Maintain/Automate) to include communication-specific modes (Schedule/Compose/Triage/Remind). |
| **Communication**            | UX design added for Phase 20a–20b. Superhuman-informed triage and composition workflows.                                                    |
| **UI**                       | Learning page redesigned. Analytics repositioned. Communication triage view defined.                                                        |
| **Analytics**                | Analytics page relationship clarified: analytics serve reflection, not center-stage display. Learning analytics move to Review tab.         |
| **Patterns**                 | Prompting competency tracked as a new pattern type.                                                                                         |
| **Design**                   | "Banking vs. problem-posing" principle articulated for learning UI decisions.                                                               |

## Reference

- Freire: Banking education (measure deposits) vs. problem-posing education (support transformation)
- Superhuman: Speed is a feature. Keyboard-first, flow-based, AI triage, voice matching.
- Existing teaching spec: [teaching spec](../../specs/teaching/spec.md)
- Existing onboarding spec: [onboarding spec](../../specs/onboarding/spec.md)
- Existing communication spec: [communication spec](../../specs/communication/spec.md)
- Existing analytics spec: [analytics spec](../../specs/analytics/spec.md)
