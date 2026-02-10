# Learning Profile & Administrator Profile — Tasks

**Created:** February 2026  
**Order:** Learning profile before administrator (Learning is closer to shippable — Phase 22 frontend is in progress). Backend before frontend.

---

## Wave 1 — Learning UI Redesign (1 week)

### Task 1: Learning Page Center Area Refactor

**Files:** `electron-app/src/renderer/` (Learning page components)

**Steps:**
1. [ ] Define four center-area states: Active Session, Curriculum View, Practice Space, Review
2. [ ] Move analytics from center to collapsible Review tab/panel
3. [ ] Implement state switching logic:
   - Active session in progress → show Active Session
   - No session but curriculum exists → show Curriculum View
   - User clicks Review tab → show analytics
   - Practice space → future (placeholder for Phase 17/27)
4. [ ] Active Session state: full-width chat with Professor, minimal chrome
5. [ ] Curriculum View state: navigable map of current learning path (topics, connections, position)
6. [ ] Review state: existing analytics content (progress, mastery, spaced repetition, gaps)
7. [ ] Empty state: "Start learning" prompt when no session or curriculum

**Acceptance:** Default center area shows active learning surface, not analytics. Analytics accessible via Review tab.

---

### Task 2: Persona Introduction Messages

**Files:** `core/pedagogy/coaching_templates.py`, `core/personas/manager.py` (modify)

**Steps:**
1. [ ] Create one-time introduction messages for each persona (Professor, Programmer, Architect, Designer, Scribe, Librarian, Administrator)
2. [ ] Track delivery in `user_journey.features_revealed` (e.g., `persona_intro_professor`)
3. [ ] Deliver on first interaction with each persona — single natural message, not tutorial wall
4. [ ] Wire into persona activation flow: check if introduction delivered, inject if not
5. [ ] Write tests

**Acceptance:** First time user activates Professor, they receive a brief orientation. Second time, nothing.

---

## Wave 2 — Prompt Injector System (1–2 weeks)

### Task 3: Pattern Detection Engine

**Files:** `core/pedagogy/__init__.py`, `core/pedagogy/models.py`, `core/pedagogy/prompt_coach.py`

**Steps:**
1. [ ] Create `core/pedagogy/` package
2. [ ] Define models: `CompetencyLevel`, `PromptingSkill`, `PersonaCompetency`, `CoachingDecision`
3. [ ] Implement pattern detection:
   - Vague request detection (missing specifics, no goal)
   - Missing context detection (code without error, design without constraints)
   - Depth-unspecified detection (no indication of expertise level)
   - Wrong-persona detection (intent misalignment)
4. [ ] Rule-based classifier (fast, <50ms)
5. [ ] Integration point: runs on user message before persona routing
6. [ ] Write tests: `tests/test_prompt_coach.py`

**Acceptance:** Given "explain Docker", pattern detection returns `vague_request` with coaching suggestion.

---

### Task 4: Competency Tracking

**Files:** `core/pedagogy/competency_tracker.py`

**Steps:**
1. [ ] Implement competency profile I/O:
   - Load/save `_polly/user/prompting-competency.yml`
   - Initialize with empty profile on first run
2. [ ] Implement level progression:
   - Level 0 → 1: First coaching delivered
   - Level 1 → 2: Second coaching delivered
   - Level 2 → 3: User demonstrates skill unprompted (detected by reverse pattern)
   - Level 3 → 4: User's corrections improve Polly's defaults
3. [ ] Implement reverse pattern detection:
   - After coaching "include error messages," detect when user provides error messages unprompted
   - After coaching "provide constraints," detect when user specifies constraints without prompting
4. [ ] Coaching gating: check competency level before deciding to coach
   - Level 0–1: Full coaching
   - Level 2: Brief reminder
   - Level 3+: Skip
5. [ ] Minimum interval: don't coach same skill more than once per `min_coaching_interval_hours`
6. [ ] Write tests: `tests/test_competency_tracker.py`

**Acceptance:** Competency levels progress correctly. Coaching silences after Level 3. Reverse detection works.

---

### Task 5: Coaching Templates & Persona Integration

**Files:** `core/pedagogy/coaching_templates.py`, `core/personas/manager.py` (modify), `interfaces/server.py` (modify)

**Steps:**
1. [ ] Create coaching message templates for each persona (5 personas × 3-5 skills each)
2. [ ] Wire PromptCoach into the request processing pipeline:
   - Before routing to persona: `coach.analyze(message, active_persona)`
   - If coaching needed: prepend coaching to response (or show as inline suggestion)
   - After response: check if user demonstrated improvement → `record_competency_gain()`
3. [ ] Add coaching display format: brief, contextual, "better results" framing
4. [ ] Config: `pedagogy.coaching_enabled`, `pedagogy.min_coaching_interval_hours`
5. [ ] Write tests

**Acceptance:** Vague prompt to Programmer triggers coaching. Same user includes error messages next time → competency increments.

---

### Task 6: Pedagogy REST API

**Files:** `interfaces/pedagogy_api.py`, `interfaces/server.py` (register)

**Steps:**
1. [ ] Create endpoints:
   - `GET /api/pedagogy/competency` — full profile
   - `GET /api/pedagogy/competency/<persona>` — per-persona
   - `POST /api/pedagogy/coaching/analyze` — analyze message
   - `GET /api/pedagogy/stats` — coaching statistics
2. [ ] Register routes
3. [ ] Write API tests

**Acceptance:** Competency profile and coaching stats accessible via REST.

---

## Wave 3 — Administrator Communication Modes (2–3 weeks)

### Task 7: Administrator Mode Expansion

**Files:** `core/personas/implementations/administrator.py` (extend), persona definitions

**Steps:**
1. [ ] Add communication-specific modes to Administrator:
   - Triage: sequential email processing
   - Compose: voice-matched draft generation
   - Schedule: calendar intelligence
   - Remind: follow-up tracking
2. [ ] Mode context detection: if user message is about email/calendar, activate communication mode; if about system config/health, use existing system modes
3. [ ] Agent Swarms capability declaration update: add `triage`, `compose`, `schedule`, `remind`
4. [ ] Write tests

**Acceptance:** Administrator switches to Triage mode for `/mail triage` and to Configure mode for system questions.

---

### Task 8: Triage Workflow Engine

**Files:** `core/communication/triage.py`

**Steps:**
1. [ ] Implement email triage workflow:
   - Priority sorting (urgent → important → informational → noise)
   - Split processing: group by type (team, newsletters, notifications)
   - Sequential presentation with quick actions (reply, delegate, defer, archive, flag)
2. [ ] AI prioritization model:
   - Learn from user response patterns (which senders → immediate reply, which → archive)
   - Store learning in user profile
   - Confidence scoring per email
3. [ ] Triage session state:
   - Track current position in queue
   - `/mail next` advances
   - Session summary on completion
4. [ ] Integration with email data model (from communication spec)
5. [ ] Write tests: `tests/test_triage.py`

**Acceptance:** `/mail triage` starts a session. Emails presented in priority order. Actions advance to next.

---

### Task 9: Compose with Voice Matching

**Files:** `core/communication/composer.py`

**Steps:**
1. [ ] Implement voice-matched draft generation:
   - Analyze user's sent emails to build style profile (tone, length, greeting patterns, signature)
   - Generate drafts that match style
   - Template system for recurring patterns
2. [ ] Context injection:
   - Pull relevant notes from RAG when composing replies
   - Check calendar when responding to scheduling requests
3. [ ] Distraction-free composition flag: UI strips chrome during compose
4. [ ] Write tests

**Acceptance:** Draft for a meeting follow-up matches user's writing style. Relevant notes surfaced in context.

---

### Task 10: Schedule & Remind

**Files:** `core/communication/scheduler.py`, `core/communication/reminders.py`

**Steps:**
1. [ ] Implement calendar intelligence:
   - Find open slots given constraints (duration, participants, date range)
   - Conflict detection
   - Buffer awareness (before/after meetings)
   - Energy-aware scheduling (from user profile preferences)
2. [ ] Implement reminder system:
   - Follow-up tracking: detect unanswered outbound emails, suggest follow-ups
   - Deadline extraction from email content
   - Snooze with context: store reason, resurface with context
3. [ ] Write tests

**Acceptance:** "Find 30 min next week" returns available slots with buffer. Snoozed email returns with stored context.

---

### Task 11: Communication Slash Commands

**Files:** `core/commands/communication_commands.py`, `core/commands/registry.py` (extend)

**Steps:**
1. [ ] Register communication slash commands:
   - `/mail triage`, `/mail next`, `/mail reply`, `/mail snooze`, `/mail archive`
   - `/mail summary`, `/mail compose`, `/mail schedule`, `/mail follow-up`
2. [ ] Wire to Administrator persona modes
3. [ ] Results display: triage shows email cards, schedule shows time slots, compose opens draft
4. [ ] Write tests

**Acceptance:** All mail slash commands functional. Results displayed appropriately.

---

### Task 12: Communication REST API

**Files:** `interfaces/communication_api.py`, `interfaces/server.py` (register)

**Steps:**
1. [ ] Create endpoints:
   - `GET /api/mail/triage` — prioritized queue
   - `POST /api/mail/triage/<id>/action` — act on email
   - `POST /api/mail/compose` — generate draft
   - `POST /api/mail/schedule` — find meeting times
   - `GET /api/mail/reminders` — pending follow-ups
   - `POST /api/mail/snooze` — snooze with context
2. [ ] Register routes
3. [ ] Write API tests

**Acceptance:** All communication operations accessible via REST.

---

## Wave 4 — Frontend Polish (1 week)

### Task 13: Learning Page Frontend

**Files:** `electron-app/src/renderer/` (Learning page)

**Steps:**
1. [ ] Implement center area state switching (Active Session / Curriculum View / Review)
2. [ ] Review tab: relocate analytics widgets
3. [ ] Curriculum View: navigable topic map (future: integrates with knowledge graph viz)
4. [ ] Coaching display: inline coaching messages with dismiss/acknowledge
5. [ ] Competency dashboard: accessible from Learning page or Settings

**Acceptance:** Learning page defaults to active learning surface. Analytics in Review tab.

---

### Task 14: Communication Frontend

**Files:** `electron-app/src/renderer/` (Communication view)

**Steps:**
1. [ ] Triage view: email cards with quick-action buttons, priority badges
2. [ ] Compose view: distraction-free draft editor
3. [ ] Schedule view: calendar visualization with available slots highlighted
4. [ ] Remind panel: pending follow-ups list with snooze/action options
5. [ ] Slash command integration in chat

**Acceptance:** Triage flow works end-to-end in UI. Compose view is distraction-free.

---

## Dependencies Summary

```
Wave 1 (Learning UI) — can start immediately
  Task 1: Center area refactor
  Task 2: Persona introductions

Wave 2 (Prompt Injectors) — depends on Wave 1 for persona intro mechanism
  Task 3: Pattern detection ──→ Task 5: Persona integration
  Task 4: Competency tracking ──→ Task 5: Persona integration
  Task 5 ──→ Task 6: REST API

Wave 3 (Administrator) — can parallel Waves 1–2
  Task 7: Mode expansion ──→ Tasks 8, 9, 10
  Task 8: Triage ──→ Task 11: Slash commands
  Task 9: Compose (parallel with 8)
  Task 10: Schedule & Remind (parallel with 8, 9)
  Task 11 ──→ Task 12: REST API

Wave 4 (Frontend) — depends on Waves 1–3
  Task 13: Learning frontend (depends on Tasks 1, 5)
  Task 14: Communication frontend (depends on Tasks 7–12)

External Dependencies:
  - Phase 22 (Teaching Mode) frontend — Wave 1 is a refinement of this work
  - Phase 20a (Email Intelligence) — Wave 3 needs email API integration
  - Phase 9 (macOS Permissions) — Schedule mode needs EventKit
  - Phase 18 (Onboarding) — Task 2 implements onboarding spec's persona introductions
```

---

## Effort Estimate

| Wave | Effort | Can Parallel With |
|------|--------|-------------------|
| Wave 1 | 1 week | Wave 3 |
| Wave 2 | 1–2 weeks | Wave 3 |
| Wave 3 | 2–3 weeks | Waves 1–2 |
| Wave 4 | 1 week | — |
| **Total** | **4–6 weeks** | |

Waves 1–2 (Learning) and Wave 3 (Administrator) can run in parallel, bringing effective timeline to **3–5 weeks**.
