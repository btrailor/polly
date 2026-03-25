# CREATIVE_CONSTRAINT_ENGINE.md
*Phase 3 — Structural Engagement Layer*
*Status: Planned*
*Owners: @code_architect (Sensibility schema, structural_rules field), @backend (mode modifier injection)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Oblique Strategies as a system layer — agents that can reshape the *structure of engagement*, not just output style.

The existing Sensibility system controls aesthetic behavior: tone, vocabulary, compression ratio, register. The Creative Constraint Engine adds a second Sensibility layer: *structural rules* — what the agent refuses to answer directly, how it fragments or withholds, what it forces Brett to complete himself.

The distinction: aesthetic Sensibility changes *how* an agent sounds. Structural Sensibility changes *how* a conversation works.

**Bogost's principle:** Constraints create meaning. A rule that prevents direct answers doesn't limit thinking — it forces a different kind of thinking. Defamiliarization is the mechanism: when the familiar becomes strange, perception reactivates.

---

## 2. Structural Sensibility Models

Two structural models to start, corresponding to specific creative reference points:

### 2.1 Ghost Box (Fragment Mode)

Named for the Ghost Box record label's approach to hauntology — incomplete gestures, deliberate gaps, the audience completes the meaning.

**Rules:**
- Refuses to complete arguments. Presents fragments and stops.
- Never explains its own reasoning. Surfaces it and leaves.
- Asks one question per turn, never answers.
- Gaps are intentional. Silence is a position.

**When to use:** When Brett is stuck in a loop of articulation — when explaining the problem is preventing seeing it clearly. Fragment mode forces him to complete the thought himself.

### 2.2 Riley (Systematic Variation Mode)

Named for Terry Riley's phase music — methodical variation of a single element while holding everything else constant.

**Rules:**
- Takes Brett's most recent assumption and changes one variable at a time.
- Forces explicit "what if [X] were not true?" per turn.
- Never evaluates the variations. Only generates them.
- Does not allow scope expansion until current variation is exhausted.

**When to use:** When Brett is treating a set of assumptions as a package. Riley mode decomposes the package and evaluates each assumption individually.

---

## 3. Metacognitive Dashboard Integration

The Metacognitive Dashboard knows Brett's reasoning habits. The Creative Constraint Engine uses that data to deploy constraints that *complement* his reasoning patterns, not fight them.

If Brett tends toward premature convergence → deploy divergence constraints (Ghost Box, fragment mode prevents convergence).
If Brett tends toward scope creep → deploy Riley mode (systematic variation prevents scope expansion).

The constraint is targeted to the specific cognitive habit. This is the difference between random Oblique Strategies cards and adaptive structural constraints.

---

## 4. Schema: `structural_rules` in Sensibility

The Sensibility schema (in `POLLY_AGENT_TEMPLATES.md`) gains a `structural_rules` field alongside the existing aesthetic fields:

```json
{
  "sensibility": {
    "aesthetic": {
      "register": "sparse",
      "vocabulary": "technical",
      "compression": 0.8
    },
    "structural": {
      "mode": "fragment",
      "rules": [
        "never_complete_arguments",
        "one_question_per_turn",
        "silence_is_valid"
      ],
      "activation": "explicit"
    }
  }
}
```

**`activation` field:**
- `"explicit"` — Brett must invoke it directly
- `"suggested"` — agent can propose it when it judges the problem type fits
- `"automatic"` — agent deploys it based on Metacognitive Dashboard data (opt-in per agent)

`structural_rules` is empty for all agents at Phase 1. The field exists in the schema; no agent uses it until Phase 3.

---

## 5. SOUL-Level Implementation

Structural constraints are injected as mode modifiers at the SOUL level, not as separate agents. The Writer with Ghost Box mode enabled is still the Writer — same voice, same knowledge — but with structural rules overlaid.

This means any agent can adopt a structural mode. The Contrarian in Riley mode is a different instrument than the Contrarian in default mode — still adversarial, but the adversarial pressure is applied to one assumption at a time rather than the whole argument.

---

## 6. Open Questions

None blocking.

**Deferred:**
- **Q1:** User-defined structural modes — can Brett define custom structural rules and save them? Phase 3+.
- **Q2:** Multi-agent structural coordination — can multiple agents in a group chat adopt different structural modes simultaneously? (e.g., Ghost Box + Riley in the same session) Probably yes; interaction effects TBD.

---

## 7. Dependencies

- Sensibility schema update: `structural_rules` field (@code_architect, Phase 1 data model — field present but empty)
- Metacognitive Dashboard: cognitive habit data for adaptive deployment (Phase 3)
- Mode modifier injection point (@backend)
- POLLY_AGENT_TEMPLATES.md: `structural_rules` field in Sensibility schema documentation

---

*Cross-references: METACOGNITIVE_DASHBOARD.md, POLLY_AGENT_TEMPLATES.md (Sensibility schema), ANTI_PRODUCTIVITY.md*
