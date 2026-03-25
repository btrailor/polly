# CHORUS_MODE.md
*Phase 4+ — Polyphonic Multi-Agent Response*
*Status: Planned (Phase 4+, primarily iPad/desktop canvas feature)*
*Owners: @frontend (grid UI, divergence visualization), @backend (parallel dispatch, chorus payload assembly)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Polyphonic multi-agent response — agents fire simultaneously with no shared context, no coordination, no @mention routing. Meaning emerges from the field between the responses, not from any single response.

Every multi-agent system built before this — including Polly's current group chat — is serial coordination with the appearance of multiplicity. Each agent reads what came before and responds to the conversation-so-far. Chorus is genuinely parallel: agents receive the same prompt simultaneously, produce responses independently, and the result is a set of non-coordinated perspectives on the same question.

The chat metaphor forces turn-taking. Chorus abandons the chat metaphor entirely.

**Contrast with Conversation Architecture:** Conversation Architecture designs sequential cognitive structures for questions that have a path. Chorus is for questions with no right answer, where the full perspectival landscape matters — where you want to see the whole field, not arrive at a conclusion.

---

## 2. The Grid

The Chorus UI is a grid:
- **Rows:** agents
- **Columns:** response units (2–4 sentence chunks)
- **Cells:** individual response units, interactive

### 2.1 Cell Interactions

| Interaction | Effect |
|-------------|--------|
| Tap cell | Expand to full response |
| Mute row | Hide agent's responses |
| Solo row | Show only this agent's responses |
| Highlight cell | Mark for reference |
| Divergence flag | Auto-highlighted when semantic distance from other agents' same-column responses exceeds threshold |

### 2.2 Divergence Detection

A semantic similarity pass runs across same-column positions across agents. When the distance between what two agents said at the same point in their response exceeds a threshold:

- The cells are visually distinguished — a subtle indicator, not an error state
- A "divergence summary" is available: tap to see what the divergence is about

Divergence is not bad. It's information — it means two agents with different perspectives landed differently on the same point. That's worth examining.

**Divergence token:** A new semantic category in the design system. Not an error (red). Not a warning (yellow). A "pay attention" signal — cool neutral. @design_eng to specify.

### 2.3 Response Chunking

Agents in Chorus mode receive a system instruction via mode modifier:

> "Respond in 2–4 sentence units, separated by paragraph breaks. Do not write long paragraphs. Each unit should be a complete, position-forward thought."

This constraint serves the grid: long paragraphs don't chunk well. It also improves output — compressed, position-forward, no hedging. The constraint produces better Chorus responses than free-form would.

---

## 3. Dispatch Architecture

Chorus dispatch is simpler than group chat:

1. Brett sends a prompt
2. Gateway fans out to all active Chorus agents simultaneously (no coordination protocol)
3. Each agent responds independently
4. Gateway assembles the chorus payload — all responses, chunked, with agent metadata
5. Client renders as grid

No agent reads another's response. No Liaison routing. No phase gating. Pure parallel.

**@backend:** Chorus payload format:

```json
{
  "type": "chorus_response",
  "prompt": "What is the most significant design constraint in Polly?",
  "agents": [
    {
      "agent_id": "code_architect",
      "chunks": [
        {"position": 1, "text": "Privacy architecture is load-bearing..."},
        {"position": 2, "text": "The gateway cannot call home..."},
        {"position": 3, "text": "This shapes every other decision..."}
      ]
    },
    {
      "agent_id": "the_philosopher",
      "chunks": [
        {"position": 1, "text": "The constraint that Polly must not optimize for engagement..."},
        {"position": 2, "text": "Most AI systems are designed to maximize session time..."},
        {"position": 3, "text": "Polly is designed to maximize thinking quality..."}
      ]
    }
  ],
  "divergence": [
    {"position": 1, "agents": ["code_architect", "the_philosopher"], "distance": 0.71}
  ]
}
```

---

## 4. Device Considerations

### Phone (degraded but useful)
2-panel horizontal split. Two agents visible at once. Swipe to switch visible pair. Divergence summary available as a separate view. This is enough to be useful; it's not the full experience.

### iPad / Desktop (full grid)
Full NxM grid. All agents and all response units visible simultaneously. The Monome grid metaphor is architecturally precise at this scale — agents as rows, time as columns, interact with intersections.

**The full Chorus experience requires a larger screen.** This is a Phase 4+ feature *primarily* because the UI hasn't been designed yet — but the concept is noted now because it informs iOS architecture decisions earlier. The chat metaphor should not be baked in so deeply that breaking it later requires a rewrite.

---

## 5. Phase 1 Architecture Decisions (Locked)

These decisions must be made in Phase 1 even though the feature ships in Phase 4+:

1. **`MultiPanelChatLayout`** — the layout component must be panel-agnostic, not chat-specific
2. **Topology-agnostic renderer** — the message renderer must not assume sequential single-agent messages
3. **Message model `topology` field** — all message objects should include `topology: "chat" | "chorus" | "architecture"` so the renderer can branch
4. **Optional `chorus_position: {row, col}`** — message objects support Chorus grid coordinates when topology is "chorus"

These are additions to the Phase 1 data model that cost little now and prevent painful refactoring later. @frontend and @backend to implement.

---

## 6. Open Questions

None blocking Phase 4+.

**Deferred:**
- **Q1:** Agent selection for Chorus — does Brett select which agents fire, or does the system suggest a Chorus configuration for a given question type?
- **Q2:** Chorus history — how does a Chorus session appear in conversation history? As a single item? As a grid snapshot? As individual agent threads?

---

## 7. Dependencies

- Group chats live (Phase 2 foundation)
- Phase 1 architecture: `topology` field on message model, `MultiPanelChatLayout` (non-chat-specific)
- `chorus_position` field on message objects (@backend + @frontend, Phase 1 data model)
- Divergence detection: semantic similarity pass at payload assembly time (@backend)

---

*Cross-references: CONVERSATION_ARCHITECTURE.md, POLLY_IOS_SPEC.md §22/§23, POLLY_AGENT_TEMPLATES.md*
