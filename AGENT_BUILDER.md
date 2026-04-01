# AGENT_BUILDER.md
*Custom Agent Creation System — Phase 2–3*
*Status: Planned*
*Owners: @code_architect (architecture), @backend (manifest registration), @design_eng (Builder SOUL), @security_audit (constraint enforcement)*
*Last updated: 2026-03-30*

---

## 1. Overview

The Agent Builder is a system agent — not in the general roster — that guides Brett through creating custom agents conversationally. Custom agents are structurally identical to built-in agents: same manifest schema, same SOUL baseline injection, same routing behavior. They get a `source: "user"` field and a subtle indicator in the UI.

---

## 2. Three Creation Scenarios

The Builder handles three distinct scenarios. Identifying which scenario applies is the first step:

### 2.1 Specificity Gap

Brett wants an existing agent, but more narrowly scoped to a domain, workflow, or register that the base agent doesn't capture. 

**Builder action:** Creates a custom variant of the base agent — inherits the base agent's SOUL, adds specificity layers for domain, register, and workflow context. The result is a new agent with a relationship to the parent.

**Example:** "I want a version of The Researcher that only works with academic papers and always checks citation quality."

### 2.2 Composition Gap

Brett wants capabilities that are best served by a standing team, not a single agent.

**Builder action:** Recommends a team configuration instead of creating a new agent. Explains the reasoning. Offers to help configure the team.

**Example:** "I want an agent that writes and edits for me simultaneously." → "That's a Writer + Editor team — one agent can't sustain both perspectives in the same session."

### 2.3 Missing Archetype

Brett wants something genuinely new — a cognitive role that doesn't exist in the roster.

**Builder action:** Builds a new agent from scratch. Guides Brett through: name, role, SOUL content, register, one-question frame, gesture vocabulary.

---

## 3. Agent Manifest Schema

Custom agents use the same manifest schema as built-in agents. The `source` field distinguishes them.

```json
{
  "agent": {
    "id": "string — kebab-case, user-defined",
    "name": "string",
    "emoji": "string",
    "category": "string — builders | thinkers | creators | operators | specialists | wildcards",
    "source": "system | user",
    "allowed_modes": ["search", "graph"],
    "autonomy_level": "reactive",
    "ward_mode": false,
    "domain_affinity": ["string[]"],
    "sensibility": {
      "aesthetic": {
        "register": "sparse | dense | balanced",
        "vocabulary": "technical | plain | mixed",
        "compression": 0.5
      }
    }
  }
}
```

**`source` values:**
- `"system"` — built-in agent from `POLLY_AGENT_TEMPLATES.md`
- `"user"` — custom agent created via Agent Builder

Custom agents are displayed with a subtle indicator in the agent list and drawer. They are otherwise indistinguishable in routing behavior.

**`domain_affinity`:** String array of domain names this agent is preferred in. Empty for all built-in agents. User sets this during Builder conversation for custom agents. The routing layer uses this for tie-breaking when multiple agents could handle a request.

---

## 4. Builder Conversation Flow

### 4.1 Entry Points

- From the agent list: "Create a custom agent" button
- From the Ward: "I want a new agent for..." → Ward detects creation intent, routes to Builder
- Direct invocation: tap Builder in system agents section

### 4.2 Conversation Structure

The Builder uses a **one-question-at-a-time discipline**. It never presents a form. It asks one question, gets an answer, and uses that answer to inform the next question.

```
Builder: "Tell me what you need — what would this agent do that your current agents don't?"

Brett: "I need something that reviews my writing specifically for argument structure, not prose style."

Builder: "So it's less about how the writing sounds and more about whether the logic holds up — does that sound right?"

Brett: "Yes, exactly."

Builder: "Is this closer to an editor (finds problems) or a sparring partner (argues with you about your claims)?"

...
```

### 4.3 SOUL Construction

The Builder constructs the SOUL collaboratively. It:
1. Drafts a SOUL based on what Brett has described
2. Reads it back conversationally ("Here's what I'd write — let me read it to you")
3. Invites refinement: "Does this feel right, or is there something off?"
4. One refinement pass at a time

The Builder never presents the raw SOUL text unless Brett asks. The conversation is about behavior, not prompt engineering.

### 4.4 Gesture Vocabulary

During the Builder conversation, Brett can name gestures that should route to this agent. The Builder:
1. Asks: "Is there a quick phrase you'd use to summon this agent?"
2. Checks for conflicts with existing gestures (similarity ≥ 0.75)
3. Suggests variations if conflict detected
4. Registers approved gestures in the gesture library with `source: "user"`

### 4.5 SOUL Quality Criteria

A SOUL that works:
- Has a clear cognitive role that is not already served by an existing agent
- States what the agent will and won't do
- Has a distinct register (how it sounds)
- Has a one-question frame (the question it asks that others don't)
- Doesn't try to do everything

A SOUL that doesn't work:
- Tries to be multiple agents at once
- Has no distinctive angle ("be helpful and accurate")
- Clones an existing agent with minor wording changes

The Builder names these problems directly and proposes alternatives.

---

## 5. Custom Agent Constraints

### 5.1 Security Constraints

Custom agents are **always** subject to the following constraints, enforced by the gateway at registration time — not by the Builder's SOUL:

- `allowed_modes` never includes `config_write` — custom agents cannot write to gateway config
- `autonomy_level` is always `reactive` — custom agents cannot be `proactive` or `autonomous`
- `ward_mode` is always `false` — custom agents cannot operate as Ward/Liaison

These constraints are **architectural**, not behavioral. The Builder's SOUL cannot override them. Even if the Builder conversation produces instructions that would set these fields, the gateway registration handler rejects the values and substitutes the enforced defaults.

See `SECURITY_IMPLEMENTATION_SPEC.md` and @security_audit Task 3 for verification requirements.

### 5.2 Team Membership

Custom agents integrate into team membership, domain affinity, and all routing behavior without special handling. They can be added to any team via the normal team configuration flow.

### 5.3 UI Indicator

Custom agents display a subtle indicator (small tag or badge) in:
- Agent list
- Drawer navigation
- Team roster views

The indicator is informational — it does not affect functionality.

---

## 6. Phase Sequence

| Phase | What ships |
|-------|-----------|
| **Phase 2** | Full Agent Builder system agent; custom agent creation flow; manifest registration with `source: "user"`; gesture vocabulary registration during Builder conversation; team membership integration; security constraint enforcement at registration |
| **Phase 3** | Custom agent learning from usage patterns; community agent sharing (pending Brett's decision on §9 Q1); `domain_affinity` auto-suggestion from usage data |

---

## 7. Relationship to Existing Systems

- **Agent manifest:** Same schema as built-in agents, plus `source`, `ward_mode`, `domain_affinity` fields (see `POLLY_AGENT_TEMPLATES.md` §Agent Manifest Schema)
- **Gesture Layer:** Custom agents register gestures during Builder conversation; same library as built-in gestures (see `GESTURE_LAYER.md`)
- **SOUL Baseline:** Same injection as built-in agents — Session Startup, Context Management, etc.
- **Ward:** Custom agents are addressable by the Ward in routing; no special handling required

---

## 8. What the Builder Is Not

- Not a jailbreak surface. Custom agents cannot circumvent security constraints.
- Not a way to create autonomous agents. All custom agents are `reactive`.
- Not a Shortcuts replacement. Creating a custom agent is not the same as creating a shortcut. Shortcuts are text prompts; agents are persistent cognitive roles.
- Not a way to clone built-in agents. Clones (specificity gap agents) inherit from the base agent but are distinct registered entries.

---

## 9. Open Questions

**Q1 — Agent and gesture sharing between Polly users:** Does Brett want the data model to support sharing custom agents between Polly instances now? This is a data model decision (adding a `shareable: boolean` field and export format) that is easier to add early than retrofit. Pending Brett's decision — do not implement assumptions.

---

## 10. Lockdown Mode

Custom agents are not affected by Lockdown Mode beyond the standard constraints:
- Agent data encrypted at rest under the Lockdown Mode key hierarchy
- No network access for `config_write` (already blocked by §5.1)

---

*Cross-references: `GESTURE_LAYER.md`, `WARD.md`, `POLLY_AGENT_TEMPLATES.md`, `SECURITY_IMPLEMENTATION_SPEC.md`, `LOCKDOWN_MODE.md`*
