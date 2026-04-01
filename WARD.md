# WARD.md

Universal Entry Point + Liaison Extension — Polly Phase 2–4  
Status: 📋 Planned  
Author: Design session 2026-03-30

---

## 1. Overview

The Ward is the universal entry point — what Brett reaches when he presses the mic button outside of an active conversation. It is also the Liaison: the same agent operating in two modes determined by invocation context.

- **Solo mode (Ward):** orient, route, execute ambient gestures, hand off to conversations. Highest-value behavior is silence and invisibility.
- **Group mode (Liaison):** existing cross-team coordination behavior, unchanged (see `POLLY_IOS_SPEC.md` §22.9).

The Ward is not a separate agent from the Liaison. It is the Liaison in solo mode. One agent manifest, one SOUL with a mode-detection preamble.

---

## 2. Mic Button Behavior

The mic button is universal and persistent throughout the app:

| Location | Mic Routes To |
|----------|---------------|
| Inside an active solo conversation | Current agent (not Ward) |
| Inside a group chat | Liaison in group mode |
| Home / today view | Ward (solo mode) |
| Gesture screen | Ward (solo mode) |
| Settings (outer level) | Ward (solo mode) |
| Any other top-level navigation destination | Ward (solo mode) |
| No active conversation | Ward (solo mode) |

The button must look identical in all contexts. Behavioral difference is handled by invocation context, not UI.

---

## 3. Solo Mode Routing Protocol

When invoked in solo mode, the Ward executes the following decision tree:

```
Ward receives invocation (solo mode)
    ↓
gesture recognizer runs first (pre-routing)
    ├── gesture match (≥ 0.82) → execute gesture
    │       ├── ambient gesture → execute, no thread opened
    │       └── conversational gesture → route to thread
    └── no gesture match
            ↓
        read compressed state summary
            ↓
        ┌─────────────────────────────────────────┐
        │ active threads relevant to utterance?   │
        │   yes → route to most relevant thread   │
        │   no + utterance is question/task        │
        │     → open new conversation             │
        │   no + utterance is ambient/reflective   │
        │     → Ward waits (no generic prompt)    │
        └─────────────────────────────────────────┘
```

### 3.1 Ambient vs. Conversational Execution

The Ward determines at runtime whether a gesture or utterance is ambient (executes without opening a thread) or conversational (routes to or opens a thread). This is based on:

- Gesture type (mode/transition gestures → often ambient; invocation gestures → often conversational)
- Whether relevant active threads exist
- Whether the utterance is a question, task, or reflection

This classification is **not pre-stored** on gestures. See `GESTURE_LAYER.md` §3.2.

### 3.2 Disambiguation

When the Ward identifies two equally plausible destination threads, it surfaces a single disambiguation question: "Did you mean [thread A] or [thread B]?" No multi-question disambiguation flows.

### 3.3 No Generic Prompt

The Ward never responds with a generic prompt ("How can I help?"). If it cannot route, it waits. Silence is the correct behavior when there is nothing useful to surface.

---

## 4. Group Mode

Group mode is the existing Liaison behavior, unchanged. When invoked from inside a group chat, the Liaison operates in group mode. See `POLLY_IOS_SPEC.md` §22.9 for the full group mode spec.

The Ward solo-mode additions do not modify group mode behavior.

---

## 5. Ward SOUL

The Liaison's SOUL receives a mode-detection preamble and a solo-mode section. The group-mode section is preserved exactly.

**Mode-detection preamble (inserted before both sections):**

```
On session start, read your invocation context. If you are in a group chat: operate in Group Mode (Liaison). If Brett has arrived alone: operate in Solo Mode (Ward). Do not switch modes mid-session.
```

**Solo-mode section:**

```
## Solo Mode (Ward)

You are the threshold Brett crosses on the way to a conversation. Your job is to dissolve, not to be noticed.

When Brett arrives with a gesture — route it and disappear. When he arrives with a question — route him to the right conversation and disappear. When he arrives with nothing — wait. Silence is the highest-value output.

**How you read arrival:**

The compressed state summary tells you what's active: threads, recent gestures, domain context, teams. You scan it fast. You are looking for the most plausible destination for whatever Brett just said or did.

**Routing hierarchy:**
1. If a gesture fired — execute it. Don't narrate the execution.
2. If there's an active thread that clearly owns this — route there. One sentence max: "Continuing [thread name]" and done.
3. If you need to open a new conversation — name the agent and why, in one sentence. Start the conversation.
4. If nothing is clearly right — wait. Do not fill the silence.

**What you never do:**
- You never greet Brett when he arrives
- You never ask "How can I help?"
- You never summarize your routing decision at length
- You never open a meta-conversation about routing

**Your register:** Minimal, precise, invisible. You are infrastructure. The conversation is the thing.
```

---

## 6. Context Injection — Ward Compressed State Summary

The Ward receives a compressed state summary at every invocation (solo mode). This is not a full transcript — it is enough to route.

### 6.1 Context Block Format

```markdown
## Ward Context

**Active Threads** (last 7 days, by recency):
- [thread title] — [topic summary, ≤15 words] — last active [relative time]
- [thread title] — [topic summary, ≤15 words] — last active [relative time]
[max 8 threads shown]

**Recent Gestures** (last 72 hours):
- [gesture name] — [time] — [resolved agent]
[max 5 gestures shown]

**Domain Context:** [active domain name | none]

**Active Teams:** [team names, comma-separated | none]
```

### 6.2 Assembly Rules

- **Thread recency filter:** threads active in the last 7 days only. Threads older than 7 days not surfaced.
- **Thread topic summaries:** generated via lightweight 5-message pass, cached per thread, invalidated when new messages arrive.
- **Team recency filter:** teams with activity in the last 14 days.
- **Maximum context size:** the Ward context block must not exceed 400 tokens.
- **Performance target:** Ward context assembly adds < 50ms to Ward invocation latency.
- **Absent context is omitted:** if no active threads → omit threads block entirely. Do not show empty sections.

---

## 7. Routing Protocol

### 7.1 Gesture Pre-Computation

Gesture recognition runs **before** the Ward receives the invocation. The gesture recognizer at the gateway runs on every short utterance (≤ 8 words), resolves the gesture (if match ≥ 0.82), and passes the result to the Ward along with the compressed state summary.

The Ward does not re-run gesture matching. It receives a resolved gesture (or no-match) as input.

**Dependency:** Gesture pre-computation must run before Ward receives invocation. See `GESTURE_LAYER.md` §4.

### 7.2 Thread Routing

When routing to an active thread, the Ward passes a brief routing note to the receiving agent:

```
Ward routing note: Brett arrived via [gesture name | direct] — forwarding to this thread.
```

The receiving agent acknowledges the routing by continuing the conversation naturally — no meta-commentary about the routing.

### 7.3 New Conversation Opening

When opening a new conversation, the Ward selects the agent based on:
1. Domain affinity (if domain context is active)
2. Utterance semantic match to agent SOULs
3. Default routing (Generalist if no match)

---

## 8. Scaling Model

**Phase 2:** Single Ward. One Liaison instance handles all Ward (solo) and Liaison (group) invocations.

**Phase 3 trigger:** Activate hierarchical Domain Wards when active threads exceed ~20 across 3+ distinct domains. A Domain Ward is a domain-scoped routing layer that handles threads within its domain and surfaces only cross-domain requests to the global Ward.

**Do not implement Domain Wards in Phase 2.** The single Ward model is correct for Phase 2 scale.

---

## 9. Manifest Fields

The Liaison's manifest receives two new fields (see `POLLY_AGENT_TEMPLATES.md` for full schema):

```yaml
ward_mode: true
solo_context_injection: ward_context_v1
```

`ward_mode: true` is set only on the Liaison. No other agent has this field set true. It signals to the gateway that this agent can receive Ward context injection (the compressed state summary).

`solo_context_injection: ward_context_v1` names the context assembly pipeline the gateway uses when invoking this agent in solo mode.

---

## 10. Onboarding

The Ward is introduced in onboarding as "your mic button." Onboarding language:

> "Wherever you are in Polly, the mic button takes you where you need to go. Outside a conversation, it opens Polly's routing layer — say what you're working on, and Polly finds the right conversation."

No technical language about "Ward" or "Liaison" in onboarding. Those are internal names.

---

## 11. Open Questions

**Q1 — Ward conversation persistence:** Do Ward ambient interactions (gestures that execute without opening a thread) create conversation threads? The spec recommends **no** — ambient gesture executions are ephemeral, not threaded. Validate this against the gateway's session model before implementing. **Flag for Brett's decision if gateway session model conflicts.**

**Q2 — Lockdown Mode:** In Lockdown Mode, Ward context injection is stripped:
- No thread summaries
- No gesture history
- No domain context
- Ward receives invocation with no compressed state summary

Behavioral implication: Ward in Lockdown Mode cannot route based on thread history. It routes based on utterance content only. This is the correct behavior — thread summaries and gesture history are behavioral metadata that could be compelled on a seized device.

See `LOCKDOWN_MODE.md` for full Lockdown behavior spec.

---

*Spec authored: 2026-03-30. Integrate with `GESTURE_LAYER.md` and `AGENT_BUILDER.md`.*
