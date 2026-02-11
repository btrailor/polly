# Intelligent Communication (OpenSpec)

Source of truth for Polly's email intelligence, calendar features, and progressive communication autonomy. Detail: [docs/planning/phases/other/PHASE20_INTELLIGENT_COMMUNICATION.md](../../../docs/planning/phases/other/PHASE20_INTELLIGENT_COMMUNICATION.md), [docs/planning/phases/other/PHASE7_CALENDAR_FEATURES.md](../../../docs/planning/phases/other/PHASE7_CALENDAR_FEATURES.md).

> **Implementation Status:** 💭 Vision — no code exists for this system.
> This spec describes the target design. Implementation is planned for Tier 5 / Phases 20a–20c.
> Other specs should not design integration points against this system until implementation begins.

## Overview

Intelligent Communication transforms Polly from a knowledge tool into a communication partner. Rather than simply forwarding emails or showing calendars, Polly understands communication patterns, extracts actionable information, and progressively takes on communication tasks as user trust builds.

Three sub-phases, each building on the last:

| Phase | Name | Focus |
|---|---|---|
| **20a** | Email Intelligence | Parsing, categorization, thread summarization, noise filtering |
| **20b** | Calendar & Action Items | Meeting analysis, action extraction, deadline tracking, calendar optimization |
| **20c** | Progressive Communication Autonomy | Pattern-to-rule conversion, communication autonomy dashboard, offline intelligence |

**Depends on:** Phase 9 (macOS Permissions — unlocks Calendar/Reminders), Phase 11 (Personas), Phase 13a (Pattern Learning).

---

## Phase 20a: Email Intelligence

### Core Features

- **Email parsing & categorization:** IMAP/Gmail API integration. Classify incoming email by priority (urgent, important, informational, noise), domain relevance, and action-required status.
- **Thread summarization:** Condense long email threads into structured summaries. Extract key decisions, open questions, and action items.
- **Noise filtering:** Identify newsletters, marketing, automated notifications. Separate signal from noise without unsubscribing.
- **Smart triage:** Domain-aware email routing. Technical emails surface context from Sigils domain; writing-related emails pull from Scrolls.
- **Draft assistance:** Generate reply drafts with appropriate tone, referencing relevant knowledge from RAG. User always reviews before sending.

### Data Model

```sql
-- Email metadata (not full content — privacy-first)
CREATE TABLE email_threads (
    id TEXT PRIMARY KEY,
    subject TEXT,
    participants TEXT,       -- JSON array
    category TEXT,           -- urgent, important, informational, noise
    domain_tags TEXT,         -- JSON array of relevant domains
    action_required BOOLEAN,
    summary TEXT,
    last_activity TIMESTAMP,
    thread_length INTEGER
);

CREATE TABLE email_actions (
    id TEXT PRIMARY KEY,
    thread_id TEXT REFERENCES email_threads(id),
    action_type TEXT,        -- reply, forward, schedule, delegate, archive
    description TEXT,
    deadline TIMESTAMP,
    status TEXT,             -- pending, done, dismissed
    created_at TIMESTAMP
);
```

### Privacy

- Email content processed locally (on-device LLM or local inference).
- Only metadata and summaries stored — full email bodies not persisted by Polly.
- Cloud LLM opt-in only for summarization (with user consent per thread).
- Credentials stored in Keychain (existing secrets infrastructure).

## Phase 20b: Calendar & Action Items

### Core Features

- **Calendar intelligence:** Multi-account support. Natural language queries ("What's my Tuesday look like?"). Smart event creation from chat.
- **Meeting analysis:** Pre-meeting briefs (attendee context, related notes, previous meeting outcomes). Post-meeting action extraction.
- **Action item tracking:** Extract action items from emails, meetings, and conversations. Deadline detection. Status tracking.
- **Calendar optimization:** Identify scheduling conflicts, suggest optimal meeting times, protect focus blocks.
- **Obsidian integration:** Meeting notes auto-linked to calendar events. Action items sync with notes system.

### Calendar API

```
GET  /calendar/events           # List events (with filters)
POST /calendar/events           # Create event (natural language or structured)
GET  /calendar/events/{id}      # Event detail with AI context
POST /calendar/events/{id}/brief # Generate pre-meeting brief
GET  /calendar/actions          # List pending action items
POST /calendar/actions          # Extract actions from content
```

**Depends on:** Phase 9 (macOS Permissions — EventKit access for Calendar and Reminders).

## Phase 20c: Progressive Communication Autonomy

### Core Features

- **Pattern-to-rule conversion:** Polly learns communication patterns (e.g., "you always archive newsletters from X") and suggests automation rules. User approves rules explicitly before Polly acts autonomously.
- **Communication autonomy dashboard:** Visual display of what Polly handles autonomously vs. what requires user input. Trust sliders per communication type.
- **Offline intelligence:** When user is unavailable, Polly can triage, categorize, and prepare responses — but never sends without approval (unless user has explicitly granted that level of autonomy).
- **Escalation logic:** Urgent items surface immediately. Non-urgent items batched into daily/weekly digests.

### Autonomy Levels

| Level | Name | Polly Does | User Does |
|---|---|---|---|
| 0 | Passive | Categorize, summarize | Everything else |
| 1 | Triage | Sort by priority, flag actions | Decide and act |
| 2 | Draft | Generate reply drafts, schedule suggestions | Review and send |
| 3 | Assisted | Send routine replies (with rules), manage calendar | Handle exceptions |
| 4 | Autonomous | Full communication management for approved categories | Override when needed |

Users start at Level 0. Each escalation requires explicit opt-in. Polly suggests level increases based on demonstrated patterns, but never auto-escalates.

## Integration with Existing Systems

| System | Integration |
|---|---|
| **Personas** | Administrator(Monitor) surfaces communication health. Scribe(Capture) ingests email content as knowledge. |
| **Agent Swarms** | Email triage as a workflow template. Meeting brief generation as a multi-agent pipeline. |
| **RAG** | Email/calendar context available for retrieval. Domain-filtered: technical emails indexed under relevant domain. |
| **Knowledge Graph** | People entities from email/calendar linked to knowledge graph. Meeting topics create entity connections. |
| **Patterns** | Communication patterns learned alongside other patterns. Inform routing and autonomy suggestions. |
| **Domains** | Domain-aware email routing. Domain-specific calendar views. |
| **Capture** | Emails and meeting notes as capture sources. Flow through standard entity extraction pipeline. |

## Administrator Communication Modes (Superhuman-Informed UX)

The Administrator persona gains four communication-specific modes informed by Superhuman's core insight: **speed is a feature**. Polly doesn't replace the email client — it provides a fast triage and composition layer on top.

### Triage Mode

Sequential flow-based processing (Superhuman-style):
1. Split emails by type (Team, Newsletters, Notifications)
2. Present each batch in priority order
3. Per email: subject, sender, AI summary, priority badge
4. Quick actions: Reply (→ Compose), Delegate, Defer, Archive, Flag
5. `/mail next` advances. Batch complete → next batch or done.

AI prioritization learns from user patterns: which senders always get immediate replies, which types get archived, which subjects correlate with urgency. Reaches ~94% accuracy after ~2 weeks (Superhuman benchmark).

### Compose Mode

- **Voice matching:** Learn writing style from sent emails. Drafts sound like the user.
- **Context injection:** Pull relevant notes from RAG when composing replies.
- **Template system:** Recurring patterns become templates (meeting follow-up, scheduling request, status update).
- **Distraction-free:** Minimal chrome during composition.

### Schedule Mode

Conversational calendar interface:
- Find open slots given constraints (duration, participants, date range)
- Conflict detection ("1pm and 1:30pm Thursday — first one often runs long")
- Energy-aware scheduling from user profile (morning focus time protected)
- Buffer management between meetings

### Remind Mode

- Follow-up tracking ("Emailed Dean's office 5 days ago, no reply — draft follow-up?")
- Deadline extraction from emails + calendar
- Snooze with context: store reason, resurface with it ("Came back because you wanted to reply after Friday meeting")

### Slash Commands

```
/mail triage          → Start triage session
/mail next            → Next message in queue
/mail reply           → Compose reply to current
/mail snooze 2d       → Snooze current for 2 days
/mail archive         → Archive current, move to next
/mail summary         → AI summary of current thread
/mail compose         → New composition
/mail schedule        → Find meeting times
/mail follow-up       → Check for pending follow-ups
```

### Cross-Persona Integration

| Persona | Integration |
|---------|------------|
| **Scribe** | Captures action items from emails, creates notes |
| **Architect** | Informed of technical emails relevant to system design |
| **Publisher** | Uses Compose for newsletter drafts (Ghost CMS) |
| **Librarian** | Indexes reference-worthy email threads |
| **Professor** | Surfaces learning-relevant emails (conferences, reading) |

See [personas spec — Administrator](../personas/spec.md) for full mode definitions.

---

## Competitive Positioning

- **vs Superhuman:** Polly's intelligence layer is local-first and integrated with your full knowledge base. Not a standalone email tool, but adds the speed insights Superhuman demonstrates.
- **vs SaneBox:** Polly's triage learns from patterns across your entire interaction history, not just email.
- **vs Jace.ai:** Polly's progressive autonomy is explicit and user-controlled. No opaque AI decisions.
- **vs Apple Mail/Calendar:** Polly adds AI intelligence layer on top of native platform access (EventKit).

## Implementation Phases

### Phase 20a: Email Intelligence (2–3 weeks)
- IMAP/Gmail API integration
- Email parsing, categorization, and summarization
- Noise filtering and smart triage
- Draft assistance with RAG context
- UI: Email triage view, thread summaries

### Phase 20b: Calendar & Action Items (2–3 weeks)
- EventKit integration (requires Phase 9)
- Calendar intelligence and natural language queries
- Meeting briefs and post-meeting action extraction
- Action item tracking across sources
- UI: Calendar view, action items panel

### Phase 20c: Progressive Communication Autonomy (2–3 weeks)
- Pattern-to-rule engine
- Autonomy dashboard with trust sliders
- Offline triage and batch processing
- Escalation logic and digest generation
- UI: Autonomy dashboard, rule management

## Reference

- [docs/planning/phases/other/PHASE20_INTELLIGENT_COMMUNICATION.md](../../../docs/planning/phases/other/PHASE20_INTELLIGENT_COMMUNICATION.md) — Full 1826-line spec
- [docs/planning/phases/other/PHASE7_CALENDAR_FEATURES.md](../../../docs/planning/phases/other/PHASE7_CALENDAR_FEATURES.md) — Calendar features detail
- [docs/planning/phases/other/PHASE8_NEW_INTEGRATIONS.md](../../../docs/planning/phases/other/PHASE8_NEW_INTEGRATIONS.md) — Integration candidates
- Integrations: [integrations spec](../integrations/spec.md)
- Personas: [personas spec](../personas/spec.md)
- Permissions: Phase 9 (macOS Permissions)
- Change folder: [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/)
