# WARD.md
*Universal Entry Point + Liaison Extension — Phase 2–4*
*Status: Planned*
*Owners: @code_architect (architecture), @backend (context assembly, routing protocol), @frontend (mic button), @design_eng (Ward SOUL integration into Liaison)*
*Last updated: 2026-03-30*

---

## 1. Overview

The Ward is the universal entry point — what Brett reaches when he activates the mic outside of an active conversation. It is also the Liaison: the same agent operating in two modes determined by invocation context.

- **Solo mode (Ward):** orient, route, execute ambient gestures, hand off to conversations. Highest-value behavior is silence and invisibility — get Brett to the right place without friction.
- **Group mode (Liaison):** existing cross-team coordination behavior (see `POLLY_IOS_SPEC.md` §22.9), unchanged.

The Ward is not a new agent. It is the Liaison agent with a second operating mode activated by invocation context.

---

## 2. Mic Button

The mic button is **universal and persistent** throughout the app. Same visual appearance in all contexts. Behavioral difference is handled by context, not UI.

| Context | Mic button routes to |
|---------|---------------------|
| Inside an active solo conversation | Voice to current agent |
| Inside a group chat | Voice to Liaison (group mode) |
| Anywhere outside an active conversation | Voice to Ward (solo mode) |

**Implementation:** The mic button must be present on:
- Home / today view
- Gesture screen
- Settings (outer level)
- Inside solo conversations (routes to current agent, not Ward)
- Inside group chats (routes to Liaison)
- Any other top-level navigation destination

See @frontend Task 1 for the implementation audit and approach recommendation.

---

## 3. Ward Solo Mode Behavior

The Ward's highest-value behavior is **getting out of the way**. It does not initiate conversations. It does not ask how it can help. It listens, routes, and becomes invisible.

Three response categories:

### 3.1 Ambient Gesture

Input is a recognized gesture. Ward executes it without opening a conversation thread.

- No new conversation thread created
- Confirmation feedback is minimal: brief haptic or ephemeral status text
- If gesture requires a response (e.g., "summarize my last session"), Ward speaks the response and dismisses

### 3.2 Conversational Routing

Input has conversational intent — Brett wants to talk about something.

- Ward identifies relevant active thread (if any) from state summary
- If relevant thread exists: routes to that thread, opens it, delivers input to the active agent
- If no relevant thread: opens a new conversation with the most appropriate agent

### 3.3 Ambiguity

Input could route to multiple destinations.

- Ward asks **one question only**: "Were you thinking about [topic A] or [topic B]?"
- Never asks more than one question. If further disambiguation is needed, routes to the most likely destination and the agent handles it.

---

## 4. Ward vs. Liaison — Same Agent, Two Modes

| | Ward (Solo Mode) | Liaison (Group Mode) |
|---|-----------------|---------------------|
| **Invocation** | Mic outside active conversation | Mic inside group chat; cross-team routing |
| **Goal** | Route and disappear | Coordinate and synthesize |
| **Conversation threads** | Avoids creating threads for ambient gestures | Operates within group chat thread |
| **Context received** | Compressed state summary (§6) | Group chat context |
| **SOUL** | Solo-mode section active | Group-mode section active |

Mode detection happens at session start. The Ward/Liaison reads its invocation context:
- Called from group chat → Group Mode (Liaison)
- Called from outside any active conversation → Solo Mode (Ward)

Mode does not switch mid-session.

---

## 5. Ward SOUL

The Ward/Liaison SOUL is the Liaison's SOUL extended with the Ward solo-mode section. See `POLLY_AGENT_TEMPLATES.md` for the full combined SOUL.

**Mode-detection preamble (prepended to Liaison SOUL):**

```
On session start, read your invocation context. If you are in a group
chat: operate in Group Mode (Liaison). If Brett has arrived alone:
operate in Solo Mode (Ward). Do not switch modes mid-session.
```

**Ward solo-mode behavioral principles:**
- No "how can I help?" Never. The Ward acts on what it receives.
- No preamble. Execute or ask one question.
- Silence after an ambient gesture is correct behavior.
- One question maximum to resolve ambiguity. If still ambiguous: route to the most likely destination.
- Never open a conversation thread for an ambient gesture.
- The goal is friction zero. Every word the Ward says is friction.

---

## 6. Context Injection

### 6.1 Ward Context Block

At every Ward invocation in solo mode, the gateway assembles a compressed state summary and injects it into the Ward's session context:

```markdown
## Ward Context

**Active threads** (last 7 days, recency-sorted):
- [thread title / agent / topic summary — 1 line each, max 10 threads]

**Recent gestures** (last 14 days):
- [gesture ID / trigger phrase / last invocation timestamp — max 5]

**Domain context:**
- [current active domain, if detected from recent thread topics]

**Active teams:**
- [team names currently configured, comma-separated]
```

### 6.2 Assembly Rules

- **Thread recency filter:** Only threads with activity in the last 7 days
- **Thread count cap:** Maximum 10 threads in the context block
- **Topic summary:** Generated by a lightweight 5-message pass per thread, cached at message 5 and invalidated when 3+ new messages arrive
- **Team recency filter:** Only teams with activity (any agent interaction) in the last 14 days
- **Domain detection:** Inferred from the last 3 active thread topics; omitted if confidence < 0.7

**Performance target:** Ward context assembly must add < 50ms to Ward invocation latency. Summaries are cached; assembly is a cache read + format pass.

### 6.3 What the Ward Does Not Receive

The Ward does not receive full conversation transcripts. Only:
- Topic summaries (1-line per thread)
- Thread titles and agent names
- Gesture invocation history (IDs and timestamps, not content)

This is a deliberate constraint: the Ward is a routing layer, not a knowledge layer. If Brett wants the content of a thread, he opens it.

---

## 7. Routing Protocol

### 7.1 Ward Routing Decision Tree

```
Ward receives input
    ↓
Gesture recognizer pass (word count ≤ 8)
    ├── Gesture match (≥ 0.82) → execute gesture
    │       ├── Ambient execution → no thread, confirm + dismiss
    │       └── Conversational execution → route to relevant thread or new conversation
    └── No gesture match
            ↓
        Scan active threads for relevance (embedding match against thread topic summaries)
            ├── High relevance (≥ 0.75) → route to that thread, open it
            ├── Multiple high-relevance threads → ask one disambiguation question
            ├── No relevant thread → open new conversation, route to best-matching agent
            └── No input content (silence / ambient presence) → Ward waits, no prompt
```

### 7.2 Disambiguation Question Format

When two threads both match with high relevance:

```
Ward: "Were you thinking about [thread A topic] or [thread B topic]?"
```

No other options surfaced. One question, two choices. If Brett says something else, Ward routes to most likely match and the agent handles it.

### 7.3 No Generic Prompt

The Ward never says:
- "What would you like to talk about?"
- "How can I help?"
- "What's on your mind?"

These are friction. If the Ward has no routing signal, it waits silently.

---

## 8. Conversation Persistence

Ambient gesture interactions (Solo mode, no thread) **do not create conversation threads**. The Ward is not a journaling agent. Its interactions are routing events, not conversations.

Conversational routing (when Brett has something to say) creates or resumes a conversation thread with the destination agent — the Ward is not the conversation partner, it is the router.

**This is a deliberate design decision.** The Ward should be nearly invisible in the conversation history. Brett's history is with his agents, not with the routing layer.

---

## 9. Scaling Model

### 9.1 Phase 2 — Single Ward

The single Ward is correct for Phase 2. All routing flows through one Ward/Liaison instance. This covers all expected usage up to approximately 20 active threads across 3 or fewer domains.

### 9.2 Phase 3 — Hierarchical Domain Wards

When active threads exceed ~20 across 3+ domains, hierarchical Domain Wards activate. Each domain gets a Domain Ward that handles routing within its domain; the primary Ward routes between domain Wards.

**Do not implement the hierarchical model in Phase 2.** The trigger is clear: 20+ threads, 3+ domains. Design the single Ward to be replaceable by a hierarchical model without fundamental refactoring.

---

## 10. Ward Manifest Entry

The Ward/Liaison manifest is the Liaison manifest with `ward_mode: true` and `solo_context_injection: ward_context_v1`. See `POLLY_AGENT_TEMPLATES.md` for the full entry.

```yaml
id: the-liaison
ward_mode: true
solo_context_injection: ward_context_v1
```

`solo_context_injection: ward_context_v1` tells the gateway to assemble and inject the Ward context block (§6.1) when this agent is invoked in solo mode. The version suffix allows the context format to evolve without a flag day.

---

## 11. Open Questions

**Q1 — Ward conversation persistence:** Do Ward ambient interactions create conversation threads? The spec recommends no — Ward ambient interactions are routing events, not conversations. Validate this against the gateway's session model before implementing. @backend recommendation required before implementation. **Pending Brett's decision — do not resolve unilaterally.**

**Q2 — Lockdown Mode and Ward context:** In Lockdown Mode, Ward context injection is stripped entirely. No thread summaries, no gesture history, no domain context. The Ward receives no state. Behavioral implication: the Ward cannot route intelligently and falls back to asking one question ("What do you want to work on?"). This is acceptable in Lockdown Mode — behavioral metadata is the threat surface.

---

## 12. Lockdown Mode

In Lockdown Mode:
- Ward context injection is **disabled**. No thread summaries, no gesture history, no domain context are injected.
- The Ward falls back to a single clarifying question if routing is ambiguous.
- `OpenListeningIntent` opens Polly normally (no auto-mic activation).
- Rationale: the Ward context block contains behavioral metadata (active thread topics, domain patterns, gesture history) that constitutes a fingerprint of Brett's cognitive activity and could be compelled on a seized device.

See `LOCKDOWN_MODE.md` for the full Lockdown Mode spec and Ward-specific additions.

---

## 13. Dependencies

- Phase 1 voice pipeline must be live before Ward routing activates
- Gesture Layer must be live before Ward gesture pre-computation
- Gateway session model must support `ward_mode` flag on Liaison invocations
- Topic summary generation and caching infrastructure (Phase 2 @backend)

---

*Cross-references: `GESTURE_LAYER.md`, `AGENT_BUILDER.md`, `POLLY_AGENT_TEMPLATES.md`, `POLLY_IOS_SPEC.md` §22.9, `LOCKDOWN_MODE.md`*
