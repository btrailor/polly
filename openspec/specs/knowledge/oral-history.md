# ORAL_HISTORY.md
*Phase 3 — Voice-First Longitudinal Self-Documentation*
*Status: Planned*
*Owners: @backend (corpus indexing, synthesis pipeline), @frontend (voice transcription hooks)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A voice-first longitudinal self-documentation layer. Daily reflections with any agent accumulate as a transcribed oral history corpus. The Archivist agent runs periodic synthesis passes over that corpus, producing structured documents that together form an intellectual autobiography — not of Brett's thoughts in isolation, but of his work, his positions, and how both have changed over time.

The key insight: the data already exists. Every voice conversation with Polly is transcribed. The Oral History layer is a new *pointing direction* for that existing data — not new infrastructure.

---

## 2. The Two Components

### 2.1 The Corpus

Every voice session produces a transcript. The Oral History layer indexes these transcripts as a dedicated subcorpus within the Knowledge Skill — separate from vault notes but queryable alongside them.

Corpus entries are tagged with:
- Date and agent
- Session type (freeform reflection, project debrief, structured interview, etc.)
- Extracted topics (Knowledge Skill classification pass)
- Flagged positions (explicit claims Brett made — "I think X," "I've decided Y")

The corpus grows passively. Brett doesn't do anything differently. He speaks to Polly as he normally would. The Oral History layer captures the longitudinal record.

### 2.2 The Archivist Synthesis Pass

The Archivist agent (see POLLY_AGENT_TEMPLATES.md) runs periodic synthesis passes over the corpus. Two pass types:

**Post-mortem synthesis** (triggered by project completion signal or manually):
- Reads: conversation history for the project, relevant vault notes, Plans layer (§23), memory files
- Produces: a narrative post-mortem document (10-minute read, full context reconstruction)
- Format: structured markdown, stored in `oral_history/post-mortems/`

**Annual synthesis** (triggered by year boundary or manually):
- Reads: full year of corpus entries, post-mortems, Practice Layer data, Temporal Intelligence drift maps
- Produces: an "intellectual autobiography" document for the year
- Format: structured markdown, stored in `oral_history/annual/`
- Content: recurring themes, significant decision points, unresolved questions, position shifts (with Temporal Intelligence citations), practice rhythms (with Practice Layer citations), the year's actual shape vs. its stated intentions

---

## 3. Post-Mortem Format

The Archivist's post-mortem format is the canonical output format for completed work. It is also the data source for the Estimator's reference class forecasting.

```markdown
# [Project Name] — Post-Mortem
*Completed: YYYY-MM-DD | Duration: X weeks (estimated: Y weeks)*
*Written by: The Archivist | [Date]*

## What Was Set Out to Do
[1-2 paragraphs: the original intent, as stated in early conversation history and Plans]

## What Actually Happened
[2-3 paragraphs: the actual trajectory — pivots, blockers, discoveries, what changed from the original plan]

## The Distance Between Them
[1-2 paragraphs: what the gap between intention and execution reveals. Not judgment — observation.]

## What This Connects To
[1-2 paragraphs: patterns linking this project to prior ones. References other post-mortems by name.]

## What a Future Self Needs to Know
[Bullet list: the context a future Brett needs to understand this chapter in 10 minutes. Technical decisions, relationship context, unresolved threads.]

## Effort Actuals
*For Estimator calibration:*
- Estimated duration: X weeks
- Actual duration: Y weeks
- Primary sources of slippage: [list]
- Planning optimism factor: Y/X
```

---

## 4. Annual Synthesis Format

```markdown
# [Year] — Annual Synthesis
*Written by: The Archivist | [Date]*
*Source corpus: [N] sessions, [M] post-mortems, [P] vault modifications*

## What This Year Was Actually About
[2-3 paragraphs: the year's actual shape — what dominated attention, what receded, what surprised]

## The Work
[Summary of completed projects, with post-mortem links. Patterns across projects.]

## The Positions
[Positions that shifted this year, with Temporal Intelligence citations: "In March, Brett held X. By October, he held Y. The shift appears to have been driven by..."]

## The Practices
[Practice Layer data: which domains were active, which went dormant, cross-pollination patterns]

## The Unresolved
[Questions that surfaced this year and remain open. Not a to-do list — an honest accounting of what wasn't figured out.]

## What the Year Intended vs. What It Was
[Comparison: stated intentions (from early-year conversation history) vs. actual trajectory. The gap, stated plainly.]
```

---

## 5. Storage Structure

Oral history output lives in the export package structure (see COGNITIVE_ARTIFACT.md):

```
oral_history/
  post-mortems/
    2026-03-polly-ios-phase1.md
    2025-11-glyphs-variable-fonts.md
    ...
  annual/
    2025.md
    2026.md
    ...
  corpus/
    [indexed transcript entries — managed by Knowledge Skill]
```

---

## 6. Integration Points

| System | Integration |
|--------|-------------|
| Knowledge Skill | Corpus indexing (transcript subcorpus); topic extraction; flagged position tagging |
| Practice Layer | Annual synthesis reads practice rhythm data |
| Temporal Intelligence | Annual synthesis reads position drift maps |
| COGNITIVE_ARTIFACT.md | `oral_history/` directory is one layer in the export package |
| Estimator | Post-mortem effort actuals feed reference class calibration |
| Voice transcription (Phase 1) | Corpus grows from existing transcripts — no new infrastructure |

---

## 7. Privacy Notes

The oral history corpus is among the most sensitive data in the system — it contains spoken reflections, not just written notes. Standard Knowledge Skill privacy protections apply plus:

- Corpus never leaves the gateway
- Synthesis output (post-mortems, annual documents) is user-owned and exportable
- No synthesis pass runs without user initiation or explicit cron configuration
- The corpus is explicitly deletable, per-session and in bulk

---

## 8. Open Questions

None blocking.

**Deferred:** Structured interview mode — a dedicated session type where Brett sits with the Archivist for a deliberate reflection conversation (end of year, end of project). Format: Archivist asks structured questions, Brett responds in voice, Archivist synthesizes in real time. This is a Phase 3+ feature beyond the MVP oral history corpus.

---

## 9. Dependencies

- Knowledge Skill live (corpus indexing)
- Voice transcription live (Phase 1 — transcripts exist before this layer activates)
- Archivist agent template: complete ✅ (POLLY_AGENT_TEMPLATES.md)
- COGNITIVE_ARTIFACT.md: export package structure includes `oral_history/`
- Practice Layer: practice rhythm data for annual synthesis
- Temporal Intelligence: position drift maps for annual synthesis (Phase 3)

---

*Cross-references: KNOWLEDGE_SKILL.md, PRACTICE_LAYER.md, COGNITIVE_ARTIFACT.md, TEMPORAL_INTELLIGENCE.md, POLLY_AGENT_TEMPLATES.md (Archivist), POLLY_IOS_SPEC.md §4.8*
