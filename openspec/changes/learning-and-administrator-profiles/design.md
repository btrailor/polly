# Learning Profile & Administrator Profile — Design

**Created:** February 2026  
**Impact:** Python backend (`core/pedagogy/`, `core/commands/`), Electron frontend (Learning page, Communication views), user profile

---

## Part 1: Learning Profile

### Learning Page Center Area Redesign

The current Learning page puts analytics front-and-center. This is a banking model problem: measuring deposits, not supporting transformation. The center area should be the **active learning surface**.

#### Four Center-Area States

| State               | What                                                                                                                                                                    | When Active                                                   |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Active Session**  | Full-width conversation with Professor in current mode (Explain, Socratic, Curriculum, Quiz). Minimal chrome. The learning interaction IS the UI.                       | Default when a learning session is in progress.               |
| **Curriculum View** | Current learning path as a navigable map. Not a flat list — shows position, upcoming topics, and how they connect. Knowledge graph filtered through a pedagogical lens. | Default when no session active but curriculum exists.         |
| **Practice Space**  | Embedded workspace for domains that involve doing. Professor observes and coaches. Code editor, markdown drafting, or (future) p5.js/SuperCollider scratch pad.         | When user is in a practice-oriented domain and learning mode. |
| **Review Mode**     | Where analytics live. Pulled intentionally, not imposed. Shows: study history, competency progression, spaced repetition schedule, knowledge gaps.                      | When user navigates to Review tab.                            |

**Default:** Active Session (if session in progress) → Curriculum View (if curriculum exists) → empty state with "Start learning" prompt.

**Analytics location:** Collapsible right panel or dedicated "Review" tab in the Learning page. The user pulls analytics when they want them.

### Meta-Pedagogy: Prompt Injector System

Polly teaches users how to use Polly effectively. Each persona has "teaching moments" — brief, contextual coaching that fires when a prompt could be improved. Not error messages; thinking-skill development.

#### Architecture

Three components:

```
User message → Pattern Detection → Coaching Decision → Response
                    │                       │
                    │                       ├── Coaching needed → inject coaching + process normally
                    │                       └── No coaching needed → process normally
                    │
                    └── Competency Check (has user learned this?)
                              │
                              ├── Level 0-1 → Coach
                              ├── Level 2 → Brief reminder
                              └── Level 3+ → Skip coaching
```

#### 1. Pattern Detection

Runs on incoming user message before routing. Detects:

| Pattern                   | Description                                              | Example                                            |
| ------------------------- | -------------------------------------------------------- | -------------------------------------------------- |
| **Vague request**         | No specificity, missing context                          | "explain Docker"                                   |
| **Missing error context** | Code question without error message or expected behavior | "fix this code"                                    |
| **Missing constraints**   | Design request without style/size/context                | "make a nice icon"                                 |
| **Wrong persona**         | Request better suited for a different persona            | Asking Programmer for what Architect should handle |
| **Outcome-missing**       | No goal stated                                           | "tell me about databases"                          |
| **Depth-unspecified**     | No indication of expertise level                         | "how does React work"                              |

Implementation: Lightweight classifier (rule-based initially, LLM-augmented later). Runs in <50ms.

#### 2. Coaching Responses (Per-Persona)

One or two sentences max. Framed as "better results" not "you did it wrong."

**Professor:**

> "I notice you asked me to 'explain Docker.' I can do that, but you'll get more useful results if you tell me what you're trying to accomplish with Docker. Are you setting up a new container, debugging a networking issue, or understanding the concept from scratch?"

**Programmer:**

> "You asked me to 'fix this code.' I'll take a look, but for faster debugging, try including: what you expected to happen, what actually happened, and any error messages."

**Architect:**

> "You asked for 'a database schema.' Before I design one, it helps to know: what are the main entities? What queries will be most common? What's the scale — dozens of records or millions?"

**Designer:**

> "You asked for 'a nice icon.' Design works best with constraints. What style — outlined or filled? What size — 16px, 24px, 48px? What's the context — navigation, feature illustration, decorative?"

**Scribe:**

> "You asked me to 'write something about X.' I'll get started, but the draft will be sharper if you tell me: who's the audience? What's the format — blog post, documentation, social thread? What's the key point you want to make?"

#### 3. Competency Tracking

Per-persona, per-skill tracking. Stored in user profile.

```yaml
# _polly/user/prompting-competency.yml
professor:
  outcome-oriented-prompts:
    level: 2
    last_coached: 2026-02-01
    times_coached: 2
  specifying-depth-level:
    level: 1
    last_coached: 2026-02-08
    times_coached: 1
programmer:
  including-error-messages:
    level: 3 # Competent — no longer coached
    last_coached: null
    times_coached: 3
  specifying-language-version:
    level: 1
    last_coached: 2026-02-09
    times_coached: 1
designer:
  providing-constraints:
    level: 0 # Not yet encountered
    last_coached: null
    times_coached: 0
architect:
  defining-requirements:
    level: 2
    last_coached: 2026-01-28
    times_coached: 2
```

**Levels:**

| Level | Name            | Behavior                                    |
| ----- | --------------- | ------------------------------------------- |
| 0     | Not encountered | No coaching yet — waiting for first trigger |
| 1     | Introduced      | First coaching delivered                    |
| 2     | Reminded        | Second coaching — briefer this time         |
| 3     | Competent       | No longer coached on this skill             |
| 4     | Expert          | User's corrections improve Polly's defaults |

**Progression:** Competency increases when user demonstrates the skill in subsequent interactions (e.g., next time they include error messages without prompting → level up). Detected by the same pattern system running in reverse: "user provided constraints unprompted" → increment level.

### Progressive Scaffolding Fade

This is the resolution of the "teach prompting vs. make prompting unnecessary" tension: **both, sequenced**.

```
New user → Full explanation (show routing, explain persona selection)
         → Brief reminder (second time)
         → Assume competence (minimal explanation)
         → Invisible operation (surface only when unexpected)
```

Concretely:

1. **First interaction with a persona:** One-message orientation. Natural, not tutorial-wall.
2. **First few interactions:** Coaching injectors active. Brief contextual suggestions.
3. **After competency established:** Injectors silent. Polly infers intent.
4. **Expert users:** Polly's routing and persona selection invisible. Only surfaces when something unexpected happens.

### Onboarding: Persona Introductions

First-time interaction with each persona includes a natural orientation:

**Professor:** "I'm Polly's learning persona. I work in four modes: I can explain concepts, guide you through Socratic questioning, design learning curricula, or quiz you on material. The more you tell me about what you're trying to learn and why, the better I can tailor my approach. What are you working on?"

**Programmer:** "I'm Polly's coding persona. I can write code, review it, debug issues, or plan refactors. I work best when you tell me what you're building and what's going wrong — I'll ask if I need more context."

**Architect:** "I'm Polly's planning persona. I help you design systems, break down complex problems, and think through tradeoffs. Start by telling me what you're trying to build and I'll help you figure out how."

**Designer:** "I'm Polly's design persona. I can generate icons, patterns, and design assets, maintain design systems, review consistency, or help with visual direction. Constraints make better design — tell me what it's for and I'll work within those bounds."

**Scribe:** "I'm Polly's writing persona. I help with research, drafting, and refinement. Whether it's a blog post, documentation, or notes organization — tell me what you're writing and who it's for."

Delivered once, stored in `user_journey` table (`features_revealed` includes `persona_intro_<name>`).

### Key Types (Python Backend)

```python
# core/pedagogy/models.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class CompetencyLevel(int, Enum):
    NOT_ENCOUNTERED = 0
    INTRODUCED = 1
    REMINDED = 2
    COMPETENT = 3
    EXPERT = 4

@dataclass
class PromptingSkill:
    """A specific prompting skill tracked per persona."""
    name: str                           # e.g., "outcome-oriented-prompts"
    level: CompetencyLevel = CompetencyLevel.NOT_ENCOUNTERED
    last_coached: Optional[datetime] = None
    times_coached: int = 0

@dataclass
class PersonaCompetency:
    """User's prompting competency for a specific persona."""
    persona: str
    skills: dict[str, PromptingSkill] = field(default_factory=dict)

@dataclass
class CoachingDecision:
    """Result of pattern detection on a user message."""
    should_coach: bool
    pattern_detected: Optional[str] = None  # e.g., "vague_request"
    persona: Optional[str] = None
    skill_name: Optional[str] = None
    coaching_message: Optional[str] = None
    current_level: CompetencyLevel = CompetencyLevel.NOT_ENCOUNTERED

@dataclass
class LearningCenterState(str, Enum):
    ACTIVE_SESSION = "active_session"
    CURRICULUM_VIEW = "curriculum_view"
    PRACTICE_SPACE = "practice_space"
    REVIEW = "review"
```

### Core API

```python
# core/pedagogy/prompt_coach.py

class PromptCoach:
    """Detects improvable prompts and provides coaching."""

    def __init__(self, config, competency_path: str):
        """Load competency profile and coaching templates."""

    def analyze(self, message: str, active_persona: str) -> CoachingDecision:
        """Detect patterns in user message. Check competency. Return coaching decision."""

    def record_competency_gain(self, persona: str, skill: str) -> None:
        """User demonstrated skill unprompted. Increment level."""

    def record_coaching_delivered(self, persona: str, skill: str) -> None:
        """Coaching was shown. Update last_coached and times_coached."""

    def get_competency_profile(self) -> dict[str, PersonaCompetency]:
        """Return full competency profile."""

    def get_coaching_stats(self) -> dict:
        """Stats: skills at each level, coaching frequency, progression rate."""
```

---

## Part 2: Administrator Profile (Mail & Calendar)

### Core Insight from Superhuman

Speed is a feature. Every design decision prioritizes reducing the time between "I need to do something with this email" and "it's done." Polly doesn't build a full email client — it provides a fast triage and composition layer on top of existing email.

### Administrator Communication Modes

The Administrator persona gains four communication-specific modes alongside its existing system modes:

| Mode         | Description                                                                                                                                                                         | Superhuman Parallel           |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **Triage**   | Sequential, flow-based email processing. Priority-sorted queue. For each: Reply, Delegate, Defer, Archive, Flag. Split processing by email type (team, newsletters, notifications). | Split Inbox + Flow processing |
| **Compose**  | Voice-matched draft generation. Context injection from knowledge base. Template system for recurring patterns. Distraction-free writing.                                            | AI Compose + Instant Reply    |
| **Schedule** | Calendar awareness. Find open slots, propose meeting times, detect conflicts. Energy-aware scheduling from user profile.                                                            | Calendar integration          |
| **Remind**   | Follow-up tracking. Deadline awareness from emails + calendar. Snooze with context. Proactive surfacing.                                                                            | Snooze + Remind Me            |

**Relationship to existing modes:** Configure/Monitor/Maintain/Automate remain as system administration modes. The four communication modes activate when the Administrator is operating on email/calendar context. Mode selection is automatic based on user intent.

### Triage Mode

#### Workflow

```
/mail triage
        ↓
Split emails by type (Team, Newsletters, Notifications, etc.)
        ↓
Present first batch (e.g., Team emails, priority-sorted)
        ↓
For each email:
  ├── Show: subject, sender, AI summary, priority badge
  ├── Quick actions:
  │     Reply (→ Compose mode)
  │     Delegate (forward with context)
  │     Defer (snooze to specific time)
  │     Archive (done, move to next)
  │     Flag (needs attention later)
  └── /mail next → advance to next message
        ↓
Batch complete → next batch or done
```

#### AI Prioritization

Learns from user's response patterns:

- Which senders always get immediate replies?
- Which email types always get archived without reading?
- Which subjects correlate with urgency?
- Which times of day produce faster responses?

Builds user profile over time. After ~2 weeks, reaches ~94% prioritization accuracy (Superhuman benchmark).

### Compose Mode

- **Voice matching:** Learn user's writing style from sent emails. Generate drafts that sound like the user. Polly's advantage: also knows Scrolls domain preferences, communication patterns, and relationship context.
- **Template system:** Recurring patterns become templates. "Meeting follow-up", "Scheduling request", "Status update" — customizable fields, user's voice.
- **Context injection:** When composing, Polly pulls relevant context from knowledge base. Replying to project question → surface relevant notes. Scheduling request → check calendar.
- **Distraction-free:** Minimal chrome during composition. Just the message.

### Schedule Mode

Conversational calendar interface:

> **User:** "Find time for a 30-min meeting with the housing team next week"
> **Administrator:** "You have openings Tuesday 2-3pm, Wednesday 10-11am, and Thursday 3-4pm. Tuesday and Thursday have buffer time before and after. Want me to send availability for those slots?"

- **Conflict detection:** "You have a 1pm and 1:30pm meeting Thursday — the first often runs long."
- **Energy-aware:** If user profile indicates morning productivity preference, suggest afternoon slots for meetings.
- **Buffer management:** Respect focus blocks, suggest breaks between back-to-back meetings.

### Remind Mode

- **Follow-up tracking:** "You emailed the Dean's office 5 days ago with no reply. Draft a follow-up?"
- **Deadline extraction:** Pull deadlines from emails and calendar, surface proactively.
- **Snooze with context:** When email is snoozed, store the reason. On resurface: "This came back because you wanted to reply after the Friday meeting. Meeting notes are [here]."

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

| Persona       | Mail Integration                                                                      |
| ------------- | ------------------------------------------------------------------------------------- |
| **Scribe**    | Captures action items from emails, creates notes from email threads                   |
| **Architect** | Gets informed of technical emails that might inform system design                     |
| **Publisher** | Uses Compose mode for newsletter drafts destined for Ghost CMS                        |
| **Librarian** | Indexes email threads that contain reference-worthy information                       |
| **Professor** | Surfaces learning-relevant emails (conference announcements, reading recommendations) |

---

## Part 3: REST API

### Pedagogy

| Method | Endpoint                             | Description                                |
| ------ | ------------------------------------ | ------------------------------------------ |
| `GET`  | `/api/pedagogy/competency`           | Get full competency profile                |
| `GET`  | `/api/pedagogy/competency/<persona>` | Get persona-specific competency            |
| `POST` | `/api/pedagogy/coaching/analyze`     | Analyze a message for coaching opportunity |
| `POST` | `/api/pedagogy/coaching/delivered`   | Record coaching was shown                  |
| `POST` | `/api/pedagogy/coaching/gained`      | Record competency gain                     |
| `GET`  | `/api/pedagogy/stats`                | Coaching statistics                        |

### Learning Center

| Method | Endpoint                | Description                     |
| ------ | ----------------------- | ------------------------------- |
| `GET`  | `/api/learning/state`   | Current center area state       |
| `POST` | `/api/learning/state`   | Switch center area state        |
| `GET`  | `/api/learning/session` | Active learning session details |

### Administrator Communication

| Method | Endpoint                       | Description                             |
| ------ | ------------------------------ | --------------------------------------- |
| `GET`  | `/api/mail/triage`             | Get prioritized email queue             |
| `POST` | `/api/mail/triage/<id>/action` | Act on email (reply/defer/archive/flag) |
| `POST` | `/api/mail/compose`            | Generate draft                          |
| `POST` | `/api/mail/schedule`           | Find available meeting times            |
| `GET`  | `/api/mail/reminders`          | Pending follow-ups and deadlines        |
| `POST` | `/api/mail/snooze`             | Snooze email with context               |

---

## File Organization

```
core/
├── pedagogy/
│   ├── __init__.py
│   ├── models.py              # CompetencyLevel, PromptingSkill, CoachingDecision
│   ├── prompt_coach.py        # PromptCoach — detection + coaching
│   ├── competency_tracker.py  # Competency profile I/O
│   └── coaching_templates.py  # Per-persona coaching messages
├── communication/
│   ├── __init__.py
│   ├── triage.py              # Email triage workflow
│   ├── composer.py            # Voice-matched draft generation
│   ├── scheduler.py           # Calendar intelligence
│   └── reminders.py           # Follow-up and deadline tracking
interfaces/
├── pedagogy_api.py            # Competency and coaching endpoints
├── communication_api.py       # Mail and calendar endpoints (extends existing)
```

---

## Config Additions

```yaml
# In config/config.yaml
pedagogy:
  enabled: true
  coaching_enabled: true
  min_coaching_interval_hours: 24 # Don't coach same skill more than once per day
  auto_level_up: true # Automatically detect competency gains
  competency_path: "_polly/user/prompting-competency.yml"

communication:
  email_provider: null # "gmail", "outlook", "imap" — set during onboarding
  triage_batch_size: 10
  voice_matching_enabled: true
  energy_aware_scheduling: true
  snooze_default_hours: 48
```

---

## Reference

- Freire: Banking education vs. problem-posing education
- Superhuman: Speed as feature, keyboard-first, flow processing, AI triage, voice matching
- Teaching spec: [teaching spec](../../specs/teaching/spec.md)
- Onboarding spec: [onboarding spec](../../specs/onboarding/spec.md)
- Communication spec: [communication spec](../../specs/communication/spec.md)
- Analytics spec: [analytics spec](../../specs/analytics/spec.md)
