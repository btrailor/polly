# METACOGNITIVE_DASHBOARD.md
*Phase 3 — Reasoning Pattern Effectiveness Tracking*
*Status: Planned*
*Owners: @backend (pattern extraction, dashboard data model), @frontend (dashboard UI)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A dashboard that tracks the effectiveness of Brett's reasoning patterns over time — not *what* he thinks, but *how* he thinks, and how well that's working.

Practice Layer tracks creative practices (what Brett does over and over). Metacognitive Dashboard tracks cognitive practices (how Brett reasons, which mental models he uses, which he avoids, and which produce good outcomes vs. poor ones).

The Metacognitive Dashboard is the instrument panel for Brett's reasoning life. It doesn't tell him how to think — it shows him how he's been thinking and what the patterns suggest.

---

## 2. What It Tracks

### 2.1 Mental Model Usage

Which mental models from POLLY_IOS_SPEC.md §15 (the suggested_models library) appear in Brett's conversation history and reasoning output:

| Model | 90-day usage count | Recent trend |
|-------|-------------------|-------------|
| `second_order_effects` | 47 | ↑ |
| `inversion` | 23 | → |
| `first_principles` | 31 | ↓ |
| `chestertons_fence` | 4 | → |

Models that appear frequently in sessions where Brett reports satisfaction or reaches a clear decision are flagged as "high-efficacy for Brett." Models he almost never uses are surfaced as potential blind spots.

### 2.2 Reasoning Pattern Signatures

Beyond individual models, the dashboard tracks recurring *patterns* in how Brett reasons:

- **Premature convergence:** Moving to a conclusion before adequately exploring the option space
- **Authority anchoring:** Adopting a position because of who holds it rather than examining the reasoning
- **Legibility bias:** Systematically choosing the most articulable option over the most interesting one (links to ANTI_PRODUCTIVITY.md)
- **Sunk cost reasoning:** Defending past decisions rather than evaluating current options
- **Scope creep reasoning:** Expanding a question's scope before resolving the original question

These are extracted from conversation history by a lightweight pattern classification pass — the same general approach as the Epistemic Immune System, but applied to Brett's *own* reasoning rather than the arguments presented to him.

### 2.3 Outcome Correlation

Where outcome data exists (Archivist post-mortems, Plans layer completion records), the dashboard attempts to correlate reasoning patterns with outcomes:

> "Sessions where you used `inversion` before committing to a plan were 2.3x more likely to produce plans that were executed without significant revision."

> "Projects scoped in sessions showing premature convergence were 1.8x more likely to require mid-project replanning."

This is probabilistic, not causal. The dashboard presents correlations, not prescriptions.

---

## 3. Dashboard Views

### 3.1 Reasoning Health View

Summary card showing:
- Most used models (last 90 days)
- Least used models (potential blind spots)
- Dominant reasoning pattern signatures (positive and negative)
- Trend indicators

### 3.2 Pattern Detail View

Drill into any pattern:
- Definition and examples
- Brett's historical instances (with session links)
- Outcome correlation if available
- Related mental models that address this pattern

### 3.3 Session Retrospective

After a significant session (decision made, plan committed to), the Metacognitive Dashboard runs a lightweight retrospective:
- Which models appeared in this session?
- Were there pattern signatures present?
- Compared to sessions of this type historically, how does this one look?

This is a quiet background process — it surfaces in the Today View as a brief card if it finds something interesting. It doesn't interrupt the session.

---

## 4. Integration Points

| System | Integration |
|--------|-------------|
| CONVERSATION_ARCHITECTURE.md | Personalizes topology recommendations against Brett's cognitive tendencies |
| EPISTEMIC_IMMUNE_SYSTEM.md | Shares pattern extraction infrastructure; different focus (external arguments vs. Brett's own reasoning) |
| PRACTICE_LAYER.md | Cross-references: which practices correlate with which reasoning patterns? |
| ORAL_HISTORY.md | Annual synthesis includes reasoning pattern trends from dashboard |
| COGNITIVE_ARTIFACT.md | `reasoning/` layer in export package populated by dashboard data |
| ANTI_PRODUCTIVITY.md | Avoidance pattern data (legibility bias detection) |
| Archivist | Post-mortem data as outcome signal |

---

## 5. Privacy Notes

The Metacognitive Dashboard holds a detailed model of how Brett reasons — his cognitive strengths, weaknesses, and patterns. This is among the most sensitive data in the system alongside the Epistemic Immune System pattern library.

- Never leaves the gateway
- Encrypted at rest (same tier as Epistemic Immune System pattern library)
- LOCKDOWN_MODE.md: key management applies

---

## 6. Open Questions

None blocking.

**Deferred:**
- **Q1:** Session annotation — does Brett explicitly annotate session outcomes ("this decision worked out"), or does the system infer from Archivist data? Starting assumption: infer from Archivist, no explicit annotation required. Revisit at Phase 3 implementation.
- **Q2:** Dashboard surface — dedicated view, Today View cards, or in-chat access? All three probably; priority order TBD by @frontend + @design_eng.

---

## 7. Dependencies

- Conversation history searchable (Knowledge Skill corpus)
- Archivist post-mortem data (outcome signals)
- Plans layer (§23, outcome signals)
- Mental model library defined (POLLY_IOS_SPEC.md §15)
- COGNITIVE_ARTIFACT.md: `reasoning/` layer

---

*Cross-references: EPISTEMIC_IMMUNE_SYSTEM.md, CONVERSATION_ARCHITECTURE.md, PRACTICE_LAYER.md, COGNITIVE_ARTIFACT.md, ANTI_PRODUCTIVITY.md, ORAL_HISTORY.md, POLLY_IOS_SPEC.md §15*
