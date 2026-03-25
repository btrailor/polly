# CONVERSATION_ARCHITECTURE.md
*Phase 3 — Conversation Topology Design*
*Status: Planned*
*Owners: @code_architect (topology library, Liaison SOUL), @backend (group chat coordination protocol)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Conversation topology design — the Liaison agent acting as a meta-instrument that designs cognitive structures before conversations begin.

Most multi-agent conversations in Polly are unstructured: Brett asks, agents respond, the conversation finds its shape emergently. That works for most things. But for high-stakes thinking — decisions, difficult problems, learning new domains — the *structure* of the conversation is itself a design choice. A well-structured conversation is different from an unstructured one, and the difference matters.

The Monome step sequencer metaphor is architecturally precise: a step sequencer doesn't play notes — it designs the temporal structure that notes move through. Conversation Architecture is the same: the Liaison doesn't answer questions — it designs the cognitive structure that thinking moves through.

**Distinction from Plans (§23):** Plans are task-oriented — who does what by when. Conversation architectures are epistemically-oriented — what cognitive modes thinking passes through. Different layer, different purpose.

---

## 2. The Topology Library

Each topology is a named conversation structure with defined phases, agent assignments, time constraints, and a synthesis protocol.

### 2.1 Diverge-Converge

**Purpose:** Generate a wide option space before evaluating.
**Phases:**
1. Diverge (no critique) — all agents generate options, no evaluation
2. Cluster — group related options, identify the option space
3. Converge — evaluate clusters, identify leading options
4. Synthesize — Strategist produces recommendation

**Agent assignments:** Writer/Researcher/Generalist in diverge; Analyst in cluster; Contrarian/Strategist in converge; Strategist in synthesize.
**Time constraint:** Diverge phase is time-boxed — ends when the timer fires, not when ideas run out.
**When to use:** Early-stage problem framing, creative briefs, option generation before a decision.

### 2.2 Steelman-Then-Decide

**Purpose:** Ensure the strongest version of every position is understood before choosing.
**Phases:**
1. Steelman — each significant position is articulated at its strongest (Philosopher leads)
2. Test — Contrarian tests each steelmanned position
3. Weigh — Strategist weighs tested positions against each other
4. Decide — Brett decides with full understanding of option space

**When to use:** Any decision where Brett has a prior lean and wants to ensure he's not just confirming it.

### 2.3 Pre-Mortem

**Purpose:** Surface failure modes before committing to a plan.
**Phases:**
1. Assume failure — "It is 6 months from now. The plan failed. What happened?"
2. Generate failure narratives — all agents contribute; no critique during generation
3. Cluster failure modes — group by type (execution, assumption, external)
4. Mitigate — for each high-probability failure mode, design a mitigation

**Agent assignments:** Systems Thinker + Contrarian + Infra Engineer in generation; Analyst in clustering; Strategist in mitigation.
**When to use:** Before committing significant resources to a plan.

### 2.4 Socratic

**Purpose:** Develop a position through questioning rather than assertion.
**Structure:** Single agent (Philosopher or Mentor) asks questions only — never asserts, never answers. Brett develops the position by answering. Agent's questions deepen based on answers.
**When to use:** When Brett has an intuition but can't articulate it yet; when he needs to develop a position from scratch.

### 2.5 Layered Inquiry

**Purpose:** Move from surface question to root question systematically.
**Structure:** Each exchange goes one level deeper. "Why does this matter?" → "Why does *that* matter?" → until the root concern is reached.
**Agent assignment:** Mentor or Philosopher.
**When to use:** When the stated problem is probably not the real problem.

### 2.6 Devil's Advocate Sprint

**Purpose:** Concentrated adversarial pressure on a leading position, time-boxed.
**Structure:** Devil's Advocate and Contrarian both attack the position for a defined period (15 minutes, 10 exchanges). Brett defends. Strategist observes and identifies which attacks landed.
**When to use:** Before finalizing a plan; when Brett has been living with an idea long enough that he can't see its weaknesses clearly.

---

## 3. Liaison as Conversation Architect

The Liaison agent (already in POLLY_AGENT_TEMPLATES.md) acquires a new mode: **conversation architect**.

In this mode, the Liaison:
1. Diagnoses the type of thinking Brett needs (decision? exploration? development? stress-test?)
2. Recommends a topology from the library
3. Configures the group chat: assigns agents to phases, sets time constraints, defines synthesis protocol
4. Gates phase transitions: signals when a phase is complete and the next begins
5. Produces a synthesis at the end if the topology requires one

**Liaison SOUL addition (to be written into existing Liaison template):**

```markdown
## Conversation Architect Mode

When Brett asks "how should we think about this?" or explicitly requests a structured conversation, you switch into Conversation Architect mode.

You diagnose first: What kind of thinking is needed here? Is this an exploration (needs divergence), a decision (needs evaluation), a development (needs Socratic questioning), a stress-test (needs adversarial pressure)?

You then propose a topology from the library, explain why it fits, and offer to configure the group chat. You don't start the topology without Brett's agreement — the structure is a proposal, not a directive.

When running a topology, you are the timekeeper and gatekeeper. You signal phase transitions. You don't let the conversation collapse into unstructured discussion once a structure has been agreed. You synthesize at the end.
```

---

## 4. Metacognitive Dashboard Integration

The Metacognitive Dashboard (Phase 3) tracks which topologies Brett finds most useful in which contexts. Over time, it can:

- Surface that Brett systematically skips the diverge phase and goes straight to evaluation
- Note that Pre-Mortem sessions have a higher correlation with plan revisions than Devil's Advocate Sprints
- Suggest topology variants based on Brett's cognitive patterns

This is personalization of conversation structure — the topology library is calibrated against Brett's actual thinking patterns, not generic best practices.

---

## 5. Infrastructure Requirements

### 5.1 Phase-Aware Group Chat

Group chats need a concept of phases: a set of agents is active in phase 1, a different set in phase 2, etc. The Liaison gates transitions.

**@backend:** This requires a lightweight phase state on the group chat session object:
```json
{
  "topology": "diverge-converge",
  "current_phase": 1,
  "phases": [
    {"phase": 1, "name": "Diverge", "active_agents": ["writer", "researcher", "generalist"], "time_limit_minutes": 15},
    {"phase": 2, "name": "Cluster", "active_agents": ["analyst", "liaison"], "time_limit_minutes": 10},
    ...
  ]
}
```

The Liaison sends a `phase.transition` message to advance. Agents outside the active phase are silenced (receive messages but don't respond).

### 5.2 Topology Library as Structured Prompt Library

The topology library itself is a structured prompt library — each topology is a set of agent instructions injected at the start of each phase. Mostly SOUL + group chat coordination. Light infrastructure lift.

---

## 6. Open Questions

None blocking.

**Deferred:**
- **Q1:** User-defined topologies — can Brett create custom topologies and save them to the library? Phase 3+ feature.
- **Q2:** Topology recommendation model — at what point does the system recommend a topology unprompted? (e.g., "This looks like a decision with a prior lean — want to run a Steelman-Then-Decide?") Requires Metacognitive Dashboard data.

---

## 7. Dependencies

- Group chats live (Phase 2)
- Liaison agent (existing, SOUL addition needed)
- Phase-aware group chat session state (@backend — new)
- Metacognitive Dashboard (for personalization — Phase 3)

---

*Cross-references: POLLY_AGENT_TEMPLATES.md (Liaison), METACOGNITIVE_DASHBOARD.md, POLLY_IOS_SPEC.md §22/§23*
