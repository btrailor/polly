# Ambient Agent Behavioral Specification
*Frontend spec. Owner: @frontend. Part of the Polly framework. Created: 2026-03-25.*
*Cross-reference: POLLY.md (philosophy), SCRIBE_AGENT_DESIGN.md (Scribe agent), POLLY_AGENT_TEMPLATES.md (SOUL baseline), AIGHT_POLLY_CARD.md (iOS surface)*

---

## What Is the Ambient Agent?

The Ambient Agent is Polly's proactive mode. It doesn't wait to be asked. It watches — conversations, vault activity, time, domain patterns — and surfaces connections, observations, and nudges when they're useful. It's the "round-machine" philosophy made operational: a system that generates surprising output, rewards depth over time, and invites play without demanding attention.

This is *not* a notification spam engine. The Ambient Agent operates under strict economy: it speaks rarely, specifically, and when it's genuinely earned. The signal-to-noise ratio is non-negotiable.

---

## Core Principle: Earned Interruption

The Ambient Agent earns the right to surface something by meeting one or more of these criteria:

1. **A connection was found that the user couldn't have found without the system** — cross-domain, cross-time, or cross-conversation links that require synthesizing material the user hasn't held in mind simultaneously
2. **A pattern surfaced that has behavioral implications** — not just "interesting" but "this might change what you do next"
3. **A temporal trigger with genuine relevance** — a note from six months ago is suddenly relevant to today's conversation
4. **An epistemic flag** — something in the conversation pattern triggers a constitutional reasoning habit (cui bono, scapegoat suspicion, etc.) at a level of salience that warrants surfacing
5. **A vault health signal** — an orphaned cluster, a domain that's going quiet, a concept that keeps appearing but was never captured

The test: *Would Brett be glad to have been interrupted by this?* If uncertain, don't surface it.

**Permanent dismiss, no re‑queue rule:** When a Polly card is dismissed by the user (via the × button), the observation is considered **completed** and **must not be re‑queued**. The UI does not retain a hidden queue indicator; the card simply disappears from Today view. This rule is enforced in the state machine for the Ambient Agent and mirrors the design decision #4 from the card spec.
---

## Trigger Taxonomy

### T1: Cross-Domain Connection
**What it is:** Two or more active concepts touch different domains in the Five-Sigils taxonomy, and a meaningful bridge exists between them.

**Activation condition:** Polly detects that the current conversation is engaging at least one domain (via classifier or explicit signal), and the vault or conversation history contains content in a second domain with ≥ 0.80 semantic similarity to the bridge concept defined in the cross-domain connection map.

**Example:** Brett is working on a synthesis patch (Signals). The ambient agent surfaces a note from three months ago about constraint-based composition (Signals/Grids bridge) that contains a workflow pattern directly applicable to what he's building now.

**Card trigger:** `cross_domain_connection`
**Frequency cap:** Max 1 per conversation session unless second connection meets a higher threshold (≥ 0.90).

---

### T2: Temporal Resurfacing
**What it is:** A vault note or captured idea has reached a relevant maturity threshold or is suddenly contextually applicable.

**Activation conditions:**
- A `30-Ideas` note has been in the vault for ≥ 30 days with no update → may be ready for `20-Active` staging
- A `20-Active` note hasn't been touched in ≥ 60 days → may need archiving or renewed attention
- Semantic similarity between a current conversation chunk and a vault note exceeds 0.85 → temporal resurface ("you explored this in [timeframe]")

**Example:** Brett is in a conversation about documentation systems. A Scrolls note from two months ago on "designing explanations as tools, not answers" scores 0.88 similarity. Ambient agent surfaces it.

**Card trigger:** `temporal_resurface`
**Frequency cap:** Max 1 per day.

---

### T3: Vault Health
**What it is:** The vault has a structural condition worth flagging.

**Activation conditions:**
- An entire domain (Sigils/Signals/Scrolls/Glyphs/Grids) has had zero new notes for ≥ 14 days
- An orphaned cluster of ≥ 3 notes exists with no wikilinks to other notes and no recent access
- A concept appears in conversation ≥ 3 times across ≥ 2 sessions but no vault note exists for it (ABSENT signal that hasn't been captured)

**Example:** The Grids domain has been quiet for three weeks, but Brett has been referencing systems thinking concepts in Signals conversations. Ambient agent flags the gap and suggests Scribe capture.

**Card trigger:** `vault_health`
**Frequency cap:** Max 1 per week per domain.

---

### T4: Constitutional Flag
**What it is:** A conversation pattern activates a constitutional reasoning habit at high salience — not a normal analysis trigger, but something that warrants proactive notice.

**Activation conditions (any):**
- **Cui bono:** A framing in the conversation assigns cause or benefit without identifying who is structurally advantaged. Salience threshold: framing recurs ≥ 2 times or is the premise of a decision.
- **Scapegoat suspicion:** An individual or group is assigned blame for what appears to be a systemic condition. Threshold: blame is used as an explanation terminus (nothing structural is named).
- **Defamiliarization opportunity:** A highly familiar concept is being treated as fixed/settled in a context where treating it as strange would produce useful insight. Threshold: the familiar concept is being used as justification, not examined.

**Note:** This trigger is the rarest and the highest-stakes. False positives erode trust immediately. Only surface when the pattern is clear and the observation is specific, not generic. "I notice a cui bono pattern here" is useless. "I notice this framing assumes the platform captures value — worth asking who else might" is earned.

**Card trigger:** `constitutional_flag`
**Frequency cap:** Max 1 per conversation session. Never in task execution contexts (Sigils/code tasks). Active in Scrolls, Grids, and analysis contexts only.

---

### T5: Continuation Probe
**What it is:** Something 80% done that could be finished before starting something new.

**Activation condition:** A vault note is in `process: organize` or `process: enrich` with no update in ≥ 7 days, while a new note on a related topic is being created.

**Example:** Brett starts capturing a new idea about feedback loops in generative systems. Ambient agent surfaces a Grids note from 10 days ago on the same topic that was organized but never enriched — "this looks like an extension of [note title]. Finish that one first?"

**Card trigger:** `continuation_probe`
**Frequency cap:** Max 1 per session.

---

## What the Ambient Agent Is NOT

- **Not a search interface.** If Brett wants to search the vault, he asks Scribe directly. The Ambient Agent is not triggered by queries.
- **Not a reminder system.** Reminders are handled by the standard `aight_item` trigger workflow. Ambient Agent is about synthesis and connection, not task management.
- **Not a coaching persona.** It doesn't encourage, validate, or motivate. It observes and surfaces.
- **Not always on.** During Sigils/execution tasks, the ambient triggers T1, T2, T5 only. T3 (vault health) and T4 (constitutional flag) are suppressed — don't interrupt coding flow with philosophical observations.

---

## Response Format

When the Ambient Agent fires, it surfaces as a **"Polly noticed…" card** in the iOS Today view (see `AIGHT_POLLY_CARD.md`). 

The message body follows a strict format:

```
[One sentence stating what was noticed — specific, not vague]
[Optional: One sentence of why it's relevant to now]
[One concrete next move, if applicable]
```

**Good:** "Your Signals/Grids bridge concept from January maps directly onto what you're designing now — the feedback loop architecture you documented there handles this same constraint differently. Worth a look before continuing?"

**Bad:** "I noticed you've been working across multiple domains lately. There might be some interesting connections to explore!"

Economy. Specificity. One move.

---

## Session Modes and Ambient Behavior

| Context | T1 Cross-Domain | T2 Temporal | T3 Vault Health | T4 Constitutional | T5 Continuation |
|---------|----------------|------------|-----------------|-------------------|-----------------|
| Sigils (code/infra) | ✅ | ✅ | ❌ | ❌ | ✅ |
| Signals (audio/synthesis) | ✅ | ✅ | ✅ | ❌ | ✅ |
| Scrolls (writing/pedagogy) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Glyphs (visual/design) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Grids (systems/meta) | ✅ | ✅ | ✅ | ✅ | ✅ |
| General/unclassified | ✅ | ✅ | ❌ | ❌ | ✅ |

---

## Relationship to Other Agents

**Scribe:** The Ambient Agent surfaces the observation; Scribe does the capture. When T3 (vault health) or T5 (continuation probe) fires, the card should offer a "Capture with Scribe" action that hands off to Scribe with context pre-populated.

**Epistemic Immune System (Phase 3):** T4 (constitutional flag) is the Phase 1 seed for what becomes the full Epistemic Immune System in Phase 3. Phase 1 version: static pattern detection based on constitutional habits. Phase 3 version: historical instance retrieval, rhetorical structure comparison across sessions. The interface (the card) stays the same; the intelligence underneath deepens.

**Main agent (SOUL.md):** The Ambient Agent runs as a background process, not inline with conversation. It does not interrupt conversations in-channel. It writes to the Today view and can surface at session start or session end as appropriate.

---

## Phase 1 Implementation Scope

Phase 1 implements the behavioral spec and card format. The actual trigger logic depends on:

- Knowledge Skill's graph layer (T1 — cross-domain connection) — *blocked on KNOWLEDGE_SKILL.md update*
- Knowledge Skill's conversation adapter (T2, T4 — needs searchable session history) — *blocked*
- Vault activity timestamps (T3) — available from Obsidian skill
- Vault maturity fields (T2, T5) — available from Obsidian skill

**What can ship in Phase 1:** T3 (vault health, domain quiet) and T5 (continuation probe) using data already available from the Obsidian skill. T1, T2, T4 are Phase 2 items dependent on the Knowledge Skill's expanded architecture.

Phase 1 Ambient Agent fires on:
- Domain quiet (≥ 14 days, any domain)
- Orphaned notes (≥ 3 unlinked, no recent access)
- Continuation probe (related note in organize/enrich state, new note being created on same topic)

---

*Document lives at `~/.openclaw/workspace/AMBIENT_AGENT_SPEC.md`*
*iOS surface spec: `~/.openclaw/workspace/AIGHT_POLLY_CARD.md`*
