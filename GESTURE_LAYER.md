# GESTURE_LAYER.md
*Vocal Gesture System — Phase 2–3*
*Status: Planned*
*Owners: @code_architect (architecture), @backend (recognizer, library), @frontend (gesture screen, AppIntents), @design_eng (SOUL sections, register profiles)*
*Last updated: 2026-03-30*

---

## 1. Overview

Polly's voice input is not just transcription → agent response. Short utterances (≤ 8 words) pass through a **gesture recognizer** before reaching the agent routing layer. Gestures are personal, fuzzy-matched vocal shortcuts — "push back," "thinking out loud," "save that" — that trigger pre-configured behaviors without requiring exact phrasing.

Gestures are complementary to shortcuts (§10.1). Shortcuts are text prompts that route to agents. Gestures are vocal patterns that change behavior. They operate at different layers of the system.

---

## 2. Gesture Types

Three gesture types:

- **Mode gestures** — configure session state before a conversation begins (agent selection, domain context, response register). Example: "thinking out loud" → activates low-commitment ideation mode.
- **Invocation gestures** — summon a specific behavior mid-conversation. Example: "push back on that" → The Contrarian receives the last agent response for critique.
- **Transition gestures** — shift register without stopping the session. Example: "go sparse" → agent switches to compressed output mode.

---

## 3. Gesture Data Model

### 3.1 Gesture Tuple Definition

Each gesture in the library is defined as:

```json
{
  "id": "string — kebab-case gesture ID",
  "trigger_phrases": ["string — canonical phrase", "...variants"],
  "trigger_embeddings": ["float[] — stored vector for each trigger phrase"],
  "type": "mode | invocation | transition",
  "behavior": "string — plain-language description of what happens",
  "default_owner": "string — agent ID",
  "ownership_map": {
    "domain_overrides": {
      "<domain_name>": "<agent_id>"
    },
    "group_overrides": [
      {
        "group_id": "string",
        "owner": "string — agent ID"
      }
    ]
  },
  "usage_stats": {
    "invocation_count": "integer",
    "last_used": "ISO 8601 timestamp | null",
    "last_resolved_agent": "string — agent ID | null"
  },
  "source": "system | user",
  "created_at": "ISO 8601 timestamp"
}
```

### 3.2 Execution Mode — Not a Field

`execution_mode` (ambient vs. conversational) is **not a field on gestures**. The Ward determines execution mode at runtime based on:
- Whether Brett is in an active conversation
- Whether the gesture type semantically requires a thread (invocation) vs. operates independently (mode, transition)

Pre-classification was explicitly rejected because the same gesture phrase ("save that") may need to be ambient (save a thought with no active thread) or conversational (save to the active thread) depending on context. The Ward resolves this at invocation time. See `WARD.md` §3.

---

## 4. Recognition Pipeline

### 4.1 Flow

```
Incoming voice utterance
    ↓
Transcription (Whisper)
    ↓
Word count check: ≤ 8 words?
    ├── No → skip gesture recognizer → agent routing
    └── Yes → gesture recognizer pass
                    ↓
            Embed utterance (nomic-embed-text or confirmed alternative — see §12 Q2)
                    ↓
            Cosine similarity against gesture library embeddings
                    ↓
            Similarity score
            ├── ≥ 0.82 → gesture match → resolve ownership → execute
            ├── 0.65–0.81 → candidate band → disambiguation card surfaced to user
            └── < 0.65 → no match → routes normally (logged to gesture_candidate_log)
```

### 4.2 Ownership Resolution

When a gesture matches (≥ 0.82 similarity):
1. Check `ownership_map.domain_overrides` for current domain context → if match, that agent owns it
2. Check `ownership_map.group_overrides` for current group composition → if match, that agent owns it
3. Fall back to `default_owner`

### 4.3 Disambiguation Card

When similarity falls in the 0.65–0.81 band, the UI surfaces a disambiguation card:
- Phrase as transcribed
- Top candidate gesture + agent owner + behavior summary
- Actions: **Execute** / **Dismiss** / **That's not a gesture**
- "That's not a gesture" routes the phrase normally and optionally logs it as a negative sample

---

## 5. Gesture Screen UI

### 5.1 Entry Point

Gesture screen is accessible from the main navigation. Mic button present throughout (see `WARD.md` §2 and @frontend Task 1).

### 5.2 Layout

```
[Gesture Screen]
─────────────────────────────
  Type filter tabs: All | Mode | Invocation | Transition | System
─────────────────────────────
  [gesture entry]
  "push back"                         ← trigger phrase (primary)
  Sends last response to Contrarian   ← behavior summary
  @contrarian · default               ← agent owner · scope
  ─────────────────────
  [gesture entry]
  "thinking out loud"
  Low-commitment ideation mode — no citations, no structure
  @mentor · Writing domain: @writer
  ─────────────────────
  ...

  [+] button (nav bar right) → opens Gesture Builder conversation
─────────────────────────────
```

**Tap to expand:**
- All trigger phrase variants
- Full behavior description
- Scope: default owner + all domain/group overrides
- Usage stats: invocation count, last used, last resolved agent

**Long-press:** Edit / Delete context menu

### 5.3 Domain Override Indicator

When a gesture has domain overrides, a subtle indicator (e.g., a dot or tag) appears on the entry. Expanded view shows the full override map.

---

## 6. Context Injection

### 6.1 Gesture Context Block

When a gesture resolves to an agent, a context block is injected into the agent's session:

```
## Gesture Invocation

Brett invoked: "[trigger phrase as spoken]"
Gesture: [gesture behavior description]
Invoked at: [ISO timestamp]
Mode: [ambient | conversational]
```

For invocation gestures in group context, the resolved agent receives this block. Other agents in the group receive a brief notice: `[Brett gestured: @[agent] was invoked directly]`.

### 6.2 Ward Handoff

After gesture execution, if the gesture was conversational (mode determined by Ward at runtime), the Ward hands off to the conversation. The gesture context block remains in the session. See `WARD.md` §7.

### 6.3 Gesture Builder Session

The Gesture Builder is a system agent (see §6.3 in `POLLY_AGENT_TEMPLATES.md` — Gesture Builder entry). It is invoked from the gesture screen [+] button or via a gesture (`"create a gesture"` — built-in system gesture).

During a Builder conversation, Brett names the gesture, describes the behavior, and the Builder:
1. Suggests trigger phrases (3–5 variations)
2. Checks for conflict with existing gestures (similarity threshold 0.75)
3. Confirms the owning agent
4. Saves to gesture library

---

## 7. Built-In Gesture Library

The built-in gesture library ships with Polly. All entries have `source: "system"`. Brett's personal gestures have `source: "user"`.

### 7.1 Mode Gestures

| Gesture ID | Trigger Phrases | Behavior | Default Owner |
|-----------|----------------|---------|---------------|
| `thinking-out-loud` | "thinking out loud", "just thinking", "brainstorming" | Low-commitment mode — no citations, no structure, rough engagement | `the-mentor` |
| `go-deep` | "go deep", "deep dive", "let's go deep" | Extended analytical mode — long-form reasoning, full citations | `the-researcher` |
| `be-brief` | "be brief", "go sparse", "short answers" | Sparse register, compressed output, minimum sentence count | current agent |
| `be-contrarian` | "devil's advocate", "push back", "challenge everything" | Activates Contrarian register for session duration | `the-contrarian` |
| `creative-mode` | "creative mode", "let's be creative", "generative" | Associative register, low constraints, exploratory | `the-writer` |

### 7.2 Invocation Gestures

| Gesture ID | Trigger Phrases | Behavior | Default Owner |
|-----------|----------------|---------|---------------|
| `push-back` | "push back on that", "challenge that", "play devil's advocate" | Contrarian receives last response for critique | `the-contrarian` |
| `save-that` | "save that", "bookmark that", "keep that" | Saves last exchange or named content to vault `_inbox/` | `the-mentor` |
| `summarize-now` | "summarize this", "wrap this up", "summarize" | Produces concise summary of current thread | current agent |
| `what-am-i-missing` | "what am I missing", "blind spots", "what else" | Surfaces missing considerations | `the-contrarian` |
| `research-this` | "research this", "look this up", "find sources" | Invokes Knowledge Skill search on current topic | `the-researcher` |
| `second-opinion` | "second opinion", "get another take", "another perspective" | Routes current question to a second agent | `the-liaison` |

### 7.3 Transition Gestures

| Gesture ID | Trigger Phrases | Behavior | Default Owner |
|-----------|----------------|---------|---------------|
| `shift-register` | "go sparse", "go dense", "be more concise", "expand that" | Adjusts agent register for subsequent responses | current agent |
| `switch-agent` | "switch to [agent name]", "talk to [agent name]" | Routes session to named agent | `the-liaison` |
| `end-session` | "we're done", "close this", "end session" | Closes current conversation, returns to Ward | Ward |

---

## 8. Agent SOUL Integration

### 8.1 Gesture Vocabulary Section Format

Every agent SOUL gets a `## Gesture Vocabulary` section. Format:

```
## Gesture Vocabulary

[Agent name] owns the following gestures by default:

**[Gesture name]** — "[canonical trigger phrase]" (and variants). [Plain-language description of what happens when this gesture is invoked for this agent]. Scope: default. [Note any domain overrides if applicable.]

**[Gesture name]** — "[canonical trigger phrase]". [Description]. Scope: [domain name] only.

Personal gestures Brett creates that reference this agent appear here automatically.
```

Maximum 100–200 words per section. See `POLLY_AGENT_TEMPLATES.md` for the full template and five example agents.

### 8.2 Ownership at SOUL Level

Gesture ownership is not enforced in the SOUL — it is enforced by the gateway recognizer and ownership resolution layer. The SOUL section is informational: it tells the agent what to expect, and helps it respond appropriately when a gesture invokes it without preamble.

---

## 9. Audible Mode

### 9.1 Overview

When Brett invokes Polly by voice (via `OpenListeningIntent`, Action Button, or Siri), responses may be read aloud. Each agent has a TTS register profile controlling how its output is formatted for speech.

### 9.2 TTS Formatting Rules

- Markdown stripped before TTS: headers, bullets, bold/italic, code blocks → plain prose
- Long enumerations split at sentence boundaries, not rendered as lists
- Code snippets: announced as "code block" and skipped, or summarized: "I've included code below"
- URLs: announced as "link included" or read as domain only

### 9.3 Interruption Handling

User can interrupt TTS at any point. On interruption:
- Current sentence completes (< 0.5s)
- Recording begins immediately
- No UI acknowledgment required — gesture input may resume

### 9.4 Per-Agent Register Profiles

Each agent has a TTS register profile defining sentence length, pacing, list handling, and voice character notes. Full profiles in `POLLY_AGENT_TEMPLATES.md` → `## TTS Register Profiles` section.

---

## 10. Relationship to Shortcuts

### 10.1 Gestures vs. Shortcuts — The Distinction

| | Shortcuts | Gestures |
|---|-----------|---------|
| **Invocation** | Text prompts sent to agents | Vocal patterns → behavior changes |
| **Layer** | Agent routing layer | Gateway, pre-routing |
| **Persistence** | Permanent prompt templates | Dynamic behavioral library |
| **Exactness** | Exact match | Fuzzy (embedding similarity) |
| **Scope** | Single agent at a time | Can affect session state, agent switch |

Shortcuts and gestures are complementary. A shortcut might say "run the weekly review format." A gesture might say "be brief" — changing how the shortcut's output is delivered.

---

## 11. Apple Platform Integration

### 11.1 TellPollyIntent

```swift
struct TellPollyIntent: AppIntent {
    static var title: LocalizedStringResource = "Tell Polly"
    static var description = IntentDescription("Send a phrase to Polly — routes through gesture recognizer.")
    
    @Parameter(title: "Phrase")
    var phrase: String
    
    // Siri phrase: "Tell Polly [phrase]"
    // On match: routes phrase to gateway gesture recognizer
    // On no-match: opens Polly with phrase as pre-filled chat input
}
```

### 11.2 OpenListeningIntent

```swift
struct OpenListeningIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Polly Listening"
    static var description = IntentDescription("Opens Polly with mic immediately active.")
    
    // Deep link target: polly://ward
    // On arrival: foreground to active chat (or Ward if no active chat)
    // Mic starts recording without additional tap
    // Exception: Lockdown Mode → open normally (no auto-mic)
}
```

Both intents extend the existing shortcuts AppIntents native Swift module. See @frontend Task 3.

### 11.3 Action Button

`OpenListeningIntent` is the recommended Action Button target. Onboarding surfaces a suggestion during setup (see `ONBOARDING_SPEC.md` and @frontend Task 4).

---

## 12. Open Questions

**Q1 — Gesture chaining:** Does Brett want gestures that trigger sequences of behaviors? Example: "research and summarize" → invokes research gesture, then summarize gesture on the result. Not implemented; pending Brett's decision.

**Q2 — Embedding model:** Is `nomic-embed-text:latest` via Ollama sufficient for short-phrase semantic similarity at required speed? The recognizer runs on every short utterance — latency matters. @backend must confirm and document decision here before recognizer work begins.

**Q3 — Gesture chaining (Phase 3):** Confirmed pending Brett's decision. Do not implement assumptions.

---

## 13. Lockdown Mode

In Lockdown Mode:
- Gesture recognition is **disabled**. Short utterances route normally through the agent routing layer.
- The gesture invocation log is **not written**.
- Rationale: gesture patterns are behavioral metadata that could be compelled on a seized device.

See `LOCKDOWN_MODE.md` for the full Lockdown Mode spec and gesture-specific additions.

---

## 14. Phase Sequence

| Phase | What ships |
|-------|-----------|
| **Phase 1** | Gesture candidate log only — short utterances (≤ 8 words) with no gesture match are logged to `gesture_candidate_log` for future training. No recognizer. No library. This is the only Phase 1 hook. |
| **Phase 2** | Full gesture recognizer, built-in gesture library (§7), Gesture screen UI (§5), AppIntents (§11), Gesture Builder system agent, `## Gesture Vocabulary` sections in agent SOULs |
| **Phase 3** | Personal gesture learning (candidate log → suggestion engine), domain ward routing, gesture chaining (if Brett approves) |

---

*Cross-references: `WARD.md`, `AGENT_BUILDER.md`, `POLLY_AGENT_TEMPLATES.md`, `LOCKDOWN_MODE.md`, `ONBOARDING_SPEC.md`, `POLLY_IOS_SPEC.md` §4.3*
