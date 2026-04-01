# GESTURE_LAYER.md

Vocal Gesture System — Polly Phase 2–3  
Status: 📋 Planned  
Author: Design session 2026-03-30

---

## 1. Overview

Polly's voice input is not just transcription → agent response. Short utterances (≤ 8 words) pass through a **gesture recognizer** before reaching the agent routing layer. Gestures are personal, fuzzy-matched vocal shortcuts that trigger pre-configured behaviors without requiring exact phrasing.

Gestures are distinct from shortcuts (text prompts sent to agents). See §10.1.

---

## 2. Gesture Types

Three gesture types:

- **Mode gestures** — configure session state before playing (active agent, domain context, response register)
- **Invocation gestures** — summon a specific behavior mid-conversation
- **Transition gestures** — shift register without stopping conversation flow

---

## 3. Gesture Data Model

### 3.1 Gesture Tuple Definition

Each gesture in the library is defined by:

```json
{
  "id": "string — kebab-case gesture ID",
  "source": "system | user",
  "type": "mode | invocation | transition",
  "trigger_phrases": ["string[]  — canonical + variant phrases"],
  "trigger_embeddings": ["vector[]  — stored embedding per phrase"],
  "behavior": "string — plain-language description of what this gesture does",
  "owner": {
    "default_owner": "agent_id | null",
    "domain_overrides": {
      "domain_name": "agent_id"
    },
    "group_overrides": [
      {
        "group_id": "string",
        "owner": "agent_id"
      }
    ]
  },
  "usage_stats": {
    "invocation_count": "integer",
    "last_used": "ISO 8601 timestamp | null",
    "last_resolved_agent": "agent_id | null"
  }
}
```

### 3.2 Execution Mode — Not a Field

`execution_mode: ambient | conversational` is **not** stored on the gesture. The Ward determines execution mode at runtime based on gesture type and invocation context (solo vs. group, active thread vs. no thread). Pre-classification was explicitly rejected. See `WARD.md` §3 for runtime resolution logic.

---

## 4. Recognition Pipeline

### 4.1 Flow

```
voice input
    ↓
transcription (Whisper)
    ↓
word count check
    ├── > 8 words → skip gesture check → agent routing
    └── ≤ 8 words → gesture recognizer
                        ↓
                  embedding similarity pass
                  against personal gesture library
                        ↓
               ┌────────────────────────────┐
               │ similarity ≥ 0.82          │ → execute gesture (true positive)
               │ similarity 0.65–0.81       │ → disambiguation card (candidate band)
               │ similarity < 0.65          │ → route normally (true negative)
               └────────────────────────────┘
```

### 4.2 Recognition Thresholds

| Band | Range | Action |
|------|-------|--------|
| True positive | ≥ 0.82 cosine similarity | Execute gesture |
| Candidate band | 0.65–0.81 | Surface disambiguation card to user |
| True negative | < 0.65 | Pass through to agent routing |

### 4.3 Phase 1 Logging Hook

Short utterances that don't match a gesture (< 0.65 similarity) are logged for future gesture suggestion engine use. This log must start in Phase 1, before the gesture layer exists.

```
if message.text word_count ≤ 8 and no gesture match:
    log {timestamp, text, session_id, domain_context, active_agent}
    to gesture_candidate_log
```

This is the only gesture layer hook needed in Phase 1. No other gesture work begins until Phase 2.

---

## 5. Gesture Screen UI

### 5.1 Access

Gesture screen is a top-level navigation destination. Accessible from home/today view via gesture icon in navigation. Also reachable via Ward invocation.

### 5.2 Layout

- List view of gesture library (fetched from gateway)
- Type filter tabs: **Mode / Invocation / Transition / System**
- Each entry: trigger phrase (top line) + behavior summary + agent owner (bottom line)
- Domain override indicator when a domain override is active
- **+** button (prominent, nav bar right) → opens Gesture Builder conversation
- Tap to expand: all trigger phrases, full behavior, scope, usage stats
- Long-press: edit / delete

---

## 6. Context Injection

### 6.1 Agent Gesture Context

When a gesture resolves to an agent, the gateway injects a short gesture context block before the agent receives the message:

```
## Gesture Context
Invoked via gesture: "[matched phrase]" → [gesture name]
Gesture type: [mode | invocation | transition]
```

### 6.2 Ward Gesture Context

The Ward receives a gesture context summary at every invocation. See `WARD.md` §6.

### 6.3 Gesture Builder SOUL

The Gesture Builder is a system agent (not in general roster) that guides Brett through creating new personal gestures conversationally.

**Soul:**
```
You are the Gesture Builder — a threshold, not a chatbot.

Brett has arrived to name something he already does: a vocal pattern that should trigger a behavior. Your job is to help him name it precisely and assign it cleanly.

## One Question at a Time

You never ask two questions in the same turn. You advance understanding one step at a time. When you have enough information to suggest, you suggest — you don't interrogate.

## The Sequence

1. What does Brett want to say? (The trigger phrase — his natural words, not a UI label)
2. What should happen when he says it? (The behavior — agent, action, register change, or ambient effect)
3. Who should own it? (If it's domain-specific or team-specific, name the scope)

After three anchors: propose the gesture. Show the trigger phrase, behavior, and owner in plain language. Ask only: "Does this match what you had in mind?"

## Suggest, Don't Interrogate

If you can infer the behavior from the phrase, propose it. "Push back" → The Contrarian escalates its challenge mode. Confirm rather than asking open-ended questions.

## Conflict Detection

Before confirming, check similarity against the existing gesture library. If the proposed phrase is within 0.15 cosine distance of an existing gesture, surface the conflict plainly: "This is close to your existing '[phrase]' gesture which [does X]. Do you want to replace it, rename the new one, or keep both as variants?"

## Register

Minimal. Direct. No ceremony. You exist to help Brett add precision to his vocabulary — make the process feel like naming, not form-filling.
```

---

## 7. Built-in Gesture Library

System gestures pre-loaded for all users. `source: "system"`.

| Gesture | Type | Trigger Phrases | Default Owner | Behavior |
|---------|------|----------------|---------------|----------|
| escalate-challenge | invocation | "push back", "challenge that", "harder" | The Contrarian | Escalates Contrarian's challenge intensity for the current session |
| thinking-aloud | mode | "thinking out loud", "just thinking", "not a question" | Ward | Routes utterance as ambient reflection, no agent response expected |
| save-that | invocation | "save that", "capture that", "keep that" | Ward → Scribe | Triggers vault write of the previous exchange |
| shift-register | transition | "be direct", "less formal", "just talk" | Active agent | Shifts response register of current agent |
| open-new | invocation | "new conversation", "fresh start", "switch" | Ward | Opens new conversation or Ward routing prompt |
| mentor-mode | mode | "teach me", "explain this", "mentor mode" | The Mentor | Sets active agent to Mentor for the next exchange |
| daily-reflection | invocation | "end of day", "daily reflection", "wrap up" | The Mentor | Opens daily reflection conversation thread |

---

## 8. Agent Gesture Vocabulary

### 8.1 Format

Each agent SOUL receives a `## Gesture Vocabulary` section. Format:

```
## Gesture Vocabulary

[Brief intro line — what gestures this agent owns]

**[Gesture Name]** — "[trigger phrase(s)]"
[One-sentence behavior description]
Scope: [default | domain: X | group: Y]

[Repeat for each gesture]

Personal gestures Brett adds that are assigned to you appear here automatically.
```

### 8.2 Ownership Scope

- **Default** — gesture routes to this agent in all contexts
- **Domain: [name]** — routes to this agent only when domain context is active
- **Group: [name]** — routes to this agent only when inside a named group chat

---

## 9. Audible Mode (TTS)

### 9.1 Register Profiles

Each agent has a per-agent TTS register profile. See `POLLY_AGENT_TEMPLATES.md` → `## TTS Register Profiles` for all profiles.

### 9.2 Gesture Confirmation Audio

When a gesture executes, a brief audio confirmation is played (configurable — on by default). The confirmation varies by gesture type:
- Mode gestures: brief tone (no speech)
- Invocation gestures: one-word confirmation ("Saved", "Switching")
- Transition gestures: no audio — seamless

### 9.3 Register Shift on Transition Gestures

Transition gestures shift agent register immediately. The next agent response reflects the new register without a turn boundary.

### 9.4 Per-Agent Register Profiles for TTS

See `POLLY_AGENT_TEMPLATES.md` → `## TTS Register Profiles`.

---

## 10. Distinctions

### 10.1 Gestures vs. Shortcuts

| | Gestures | Shortcuts |
|--|---------|-----------|
| Trigger | Vocal patterns | Text prompts in Shortcuts.app |
| Matching | Fuzzy (embedding similarity) | Exact (intent routing) |
| Pre-routing | Yes — before agent sees message | No — routed as normal message |
| Phase | 2+ | 1 (existing) |
| Personal | Yes — grows over time | Yes — user-created |

Gestures and shortcuts are complementary. A shortcut invokes an agent with a pre-configured prompt. A gesture configures behavior before the agent receives any message.

---

## 11. Apple Platform Integration

### 11.1 TellPollyIntent

An `AppIntent` accepting `phrase: String`. Routes through the gesture recognizer before any agent routing. No-match fallback: opens Polly with phrase as pre-filled chat input.

Siri phrase: **"Tell Polly [phrase]"**

Registered in the existing AppIntents native Swift module (same module as per-shortcut intents).

### 11.2 OpenListeningIntent

Opens Polly with mic immediately active. Deep link target: `polly://ward`. On arrival: foreground to active chat (or Ward if no active chat), mic starts recording without additional tap.

Exception: in Lockdown Mode, opens normally (no auto-mic). See §13.

Action Button target: configure in iOS Settings → Action Button.

---

## 12. Open Questions

**Q1 — Gesture chaining:** Does Brett want gestures that trigger sequences of behaviors (e.g., "save and switch" → save current exchange + open new conversation)? **Do not implement assumptions. Flag for Brett's decision.**

**Q2 — Embedding model:** Confirm whether `nomic-embed-text:latest` via Ollama is sufficient for short-phrase semantic similarity at the required recognition speed. The recognizer runs on every short message — latency matters. Decision to be documented here when resolved.

**Q3 — Gesture chaining sequences:** Defer to Brett. See Q1.

---

## 13. Lockdown Mode Behavior

In Lockdown Mode:
- Gesture recognition is **disabled** — short utterances route normally (no gesture check)
- `OpenListeningIntent` opens to normal chat (no auto-mic)
- Rationale: gesture invocation log is behavioral metadata that could be compelled on a seized device

See `LOCKDOWN_MODE.md` for full Lockdown behavior spec.

---

## Security Notes

### Threat Surface — Gesture Library

The gesture library is a behavioral fingerprint. It reveals cognitive habits, working patterns, and domain activity patterns. Threat assessment:

- **Gesture invocation log:** logs short utterances + domain context + active agent. Must be encrypted at rest. Access restricted to gateway process. Not included in any sync or cloud backup.
- **Export package:** gesture data in `COGNITIVE_ARTIFACT.md` export must be explicitly scoped — user must opt-in to including gesture history in export. Default: excluded.
- **TellPollyIntent:** accepts phrase via Siri/Shortcuts. Phrase is passed to gateway gesture recognizer via deep link or direct API call. Threat: phrase interception by other apps via deep link observation. Mitigation: use direct authenticated API call (not open deep link) when Polly is in foreground.
- **Intent spoofing:** `TellPollyIntent` and `OpenListeningIntent` must verify caller. System intents only — no third-party invocation path.

*See `@security_audit` findings in project security tracking for full assessment.*

---

*Spec authored: 2026-03-30. Integrate with `AGENT_BUILDER.md` and `WARD.md`.*
