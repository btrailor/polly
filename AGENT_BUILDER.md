# AGENT_BUILDER.md

Custom Agent Creation System — Polly Phase 2–3  
Status: 📋 Planned  
Author: Design session 2026-03-30

---

## 1. Overview

The Agent Builder is a system agent (not in the general roster) that guides Brett through creating custom agents conversationally. Custom agents are structurally identical to built-in agents — same manifest schema, same SOUL baseline injection, same routing behavior — with two additions: `source: "user"` field and a subtle indicator in the UI.

---

## 2. Three Creation Scenarios

The Agent Builder handles three distinct scenarios and responds differently to each:

### 2.1 Specificity Gap → Build a Custom Variant

Brett wants an agent that does what an existing agent does, but tuned to a specific domain, register, or working style.

**Example:** "I want a Code Architect who thinks in systems first, not tasks."

**Builder response:** Build a custom agent that shares the base archetype but has a differentiated SOUL. The built-in agent is not replaced.

### 2.2 Composition Gap → Recommend a Standing Team

Brett wants coverage for a use case that would be better served by a coordinated group of existing agents than by a single new agent.

**Example:** "I need something that handles my quarterly planning."

**Builder response:** Recommend a standing team (named team + agent lineup + activation protocol). Do not build a new agent. Explain why a team serves this better.

### 2.3 Missing Archetype → Build a New Agent

Brett wants something genuinely new — a perspective, domain, or character not covered by existing agents.

**Example:** "I want an agent that only knows about Ottoman history."

**Builder response:** Build a new agent with a full SOUL, manifest, and gesture vocabulary.

---

## 3. Manifest Schema for Custom Agents

Custom agents use the same manifest schema as built-in agents with the following additional fields:

```json
{
  "id": "string — kebab-case, user-chosen",
  "name": "string — display name",
  "emoji": "string — single emoji",
  "source": "user",
  "category": "string — same categories as built-in agents",
  "autonomy_level": "reactive",
  "allowed_modes": ["search", "graph"],
  "domain_affinity": ["string[] — domain names this agent is preferred in"],
  "ward_mode": false,
  "created_at": "ISO 8601 timestamp",
  "created_via": "agent-builder"
}
```

**Constraints enforced at registration (architectural, not behavioral):**
- `autonomy_level` is always `"reactive"` for custom agents — cannot be overridden
- `config_write` is never in `allowed_modes` for custom agents — cannot be granted
- `ward_mode` is always `false` for custom agents — cannot be set to true
- These constraints are enforced by the gateway at registration time, not by the Builder's SOUL

---

## 4. Builder Conversation Flow

### 4.1 Opening

The Builder opens by asking one diagnostic question to identify which of the three scenarios applies. It does not present a menu.

### 4.2 One Question Per Turn

The Builder never asks two questions in the same turn. It advances one step at a time. When it has enough information to propose, it proposes — it doesn't continue gathering.

### 4.3 SOUL Construction

The Builder guides Brett through three SOUL anchors:

1. **Character** — who is this agent? (a person, a perspective, a domain expert)
2. **Frame** — what's the one-sentence operating principle?
3. **Register** — how does it speak? (not just tone — what does it notice, what does it ignore)

After three anchors: draft the SOUL. One section at a time. Brett refines.

### 4.4 Gesture Vocabulary Integration

During the Builder conversation, gesture vocabulary is populated for the new agent. The Builder asks: "Are there phrases you'd naturally say to invoke this agent or shift into its mode?" Each phrase becomes a gesture entry in the personal library.

Custom agents arrive with gesture vocabulary populated. They integrate into team membership, domain affinity, and all routing behavior without special handling.

### 4.5 Final Confirmation

Before registering, the Builder presents:
- Agent name + emoji + tagline
- SOUL preview (first 150 words)
- Gesture vocabulary (if any)
- Domain affinity (if set)

One question: "Ready to add this agent?"

---

## 5. Agent Builder SOUL Design Principles

See `POLLY_AGENT_TEMPLATES.md` → System Agents section for the final registered Builder SOUL. The design spec is here.

**Design principles for the SOUL:**

- **Composition gap detection must feel natural, not like a redirect.** When the Builder identifies that Brett needs a team rather than a new agent, it should present the recommendation as a positive insight ("What you're describing sounds like a team configuration — here's why that's stronger") not a refusal.
- **One-question-frame design guidance:** The Builder teaches SOUL design by example, not by lecturing. It demonstrates what makes a SOUL work by drafting one in the conversation.
- **Clarity about what makes a SOUL work vs. not work:** The Builder distinguishes between a SOUL that configures behavior (effective) and one that adds disclaimers and caveats (ineffective). It can name this distinction when Brett drifts toward the latter.

---

## 6. Custom Agent Integration

## 6. Custom Agent Integration

### 6.1 UI Indicator

Custom agents display a subtle indicator (small dot or "custom" badge) in the agent selector. The indicator is subtle — custom agents are first-class, not second-class.

### 6.2 Routing Behavior

Custom agents participate in all routing behaviors identically to built-in agents:
- Team membership
- Domain affinity routing
- Gesture ownership
- Group chat participation
- Mental model application

### 6.3 Domain Affinity

The `domain_affinity` field gates routing preference. When a domain context is active and a custom agent has that domain in its `domain_affinity`, it receives a routing preference weight. This is a soft preference — not an exclusive lock.

### 6.4 Editing

Custom agents can be edited after creation. Editing reopens a Builder conversation scoped to modification ("What would you like to change?").

### 6.5 Deletion

Custom agents can be deleted. Deletion is permanent. Gateway purges the manifest, SOUL, and gesture vocabulary. Conversation history is retained.

### 6.6 Phase 3 Allowed Modes

In Phase 3, custom agents may receive additional `allowed_modes` values (e.g., `"analogy"`, `"dream"`) following the same selectivity rules as built-in agents. Brett can configure this via the Builder or settings.

**Security constraint (Phase 3):** `config_write` remains unavailable to all custom agents regardless of phase.

---

## 7. Security Constraints

Custom agents must never:
- Receive `config_write` in `allowed_modes`
- Have `autonomy_level` set to anything other than `"reactive"`
- Have `ward_mode: true`

These constraints are **architectural** — enforced by the gateway at registration time, not by the Builder's SOUL. The Builder's SOUL cannot be bypassed to grant these capabilities.

**Gateway enforcement:** At `agent.register` RPC call, gateway validates:
```
if agent.source == "user":
    assert agent.autonomy_level == "reactive"
    assert "config_write" not in agent.allowed_modes
    assert agent.ward_mode == false
    reject registration if any constraint violated
```

---

## 8. System Agent Registration

The Agent Builder is a system agent — same section as Liaison, Ambient Agent, and Janitor in `POLLY_AGENT_TEMPLATES.md`. It does not appear in the general agent roster or team membership.

See `POLLY_AGENT_TEMPLATES.md` → System Agents section for the full registered SOUL.

---

## 9. Dependencies

- Phase 1 voice pipeline must be live before Agent Builder ships (Phase 2)
- Gesture Layer must be live before gesture vocabulary integration works
- Custom agent registration requires gateway `agent.register` RPC extension

---

## 10. Open Questions

**Q1 — Agent and gesture sharing:** Does Brett want the data model to support sharing custom agents and gestures between Polly users in the future? This affects the manifest schema (shared ID namespace, author field). **Do not implement. Flag for Brett's decision.**

---

*Spec authored: 2026-03-30. Integrate with `GESTURE_LAYER.md` and `WARD.md`.*
