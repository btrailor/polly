# TEMPORAL_INTELLIGENCE.md
*Phase 3 — Intellectual Drift Detection*
*Status: Planned*
*Owners: @backend (drift pipeline, position index), @code_architect (topic ontology, drift view)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Drift detection — a system that tracks how Brett's intellectual positions change over time and surfaces that movement as a navigable view.

Most knowledge management systems treat knowledge as static: a note says what it says. Temporal Intelligence treats knowledge as *historical*: a position held at a point in time, potentially contradicted or evolved by later positions. The question is not "what does Brett think about X?" but "how has Brett's thinking about X moved, and when did it move?"

The Drift View is the instrument panel for intellectual evolution. It makes visible what is otherwise invisible: the slow accretion of position changes that, taken individually, seem minor but, seen across time, reveal genuine intellectual development (or genuine inconsistency).

---

## 2. Two-Pipeline Architecture

The Knowledge Skill handles all content ingestion. Temporal Intelligence is a second-pass layer on top of it.

```
Knowledge Skill pipeline (existing):
  vault content → chunking → embedding → HNSW index

Temporal Intelligence pipeline (new):
  Knowledge Skill corpus → classifier filter → LLM position extraction → position index
```

**The classifier filter** runs first: not every note contains a position. Notes that are pure process (meeting notes, task lists, code snippets) are filtered out. Only notes that express a stance, claim, or belief pass to the extraction stage.

**LLM position extraction** extracts structured position objects from passing notes:

```json
{
  "note_id": "abc123",
  "note_date": "2025-11-14",
  "topic": "open_source_sustainability",
  "position": "Open source projects that refuse commercial licensing eventually die from maintainer burnout",
  "confidence": 0.84,
  "qualifiers": ["eventually", "maintainer burnout"],
  "sentiment_valence": -0.3
}
```

**The position index** is separate from the HNSW semantic index — it stores position objects, not embeddings, and is queried by topic.

---

## 3. Topic Ontology

**The topic ontology is emergent, not fixed.**

Topics are derived by clustering position embeddings — Brett's own positions define the topic space. There is no predetermined taxonomy imposed from outside. This is the Freirean principle: categories emerge from the user's own knowledge, not from an external authority's classification system.

Initial topics emerge from the first batch of position extractions. As more positions are extracted, topics split (when a cluster becomes too large and heterogeneous) or merge (when two clusters converge). The ontology evolves as Brett's intellectual life evolves.

**Prior art:** Hamilton et al. (2016) diachronic word embeddings detect how word meanings shift over time in large corpora. Polly's contribution is applying this method to personal intellectual history — detecting how *positions* shift over time in a single person's knowledge graph.

---

## 4. Drift View

The Drift View is a topic map with a time axis.

**Layout:**
- X-axis: time
- Y-axis: topics (ordered by recency of last position)
- Each point: a position, colored by topic, sized by confidence
- Connecting lines: position changes within a topic over time

**Interactions:**
- Tap a point: see the full position and source note
- Tap a connection line: see the diff between two positions ("moved from X to Y")
- Filter by topic, time range, confidence threshold
- "Surprise me" — surfaces the largest position change in a given period

**Drift summary card:** Archivist-generated summary of significant drift over the selected period. "In the last 6 months, your thinking on open source sustainability shifted significantly — you moved from [position A] to [position B], apparently triggered by [note cluster from October]."

---

## 5. Dialogic Interaction

When the system detects a new position that contradicts an earlier position, it can surface the contradiction dialogically — not as an accusation, but as a question:

> "In November you wrote that open source projects that refuse commercial licensing eventually die from burnout. Today you're arguing the opposite. What changed?"

**Agent assignment:** This is natural territory for the Interlocutor (examination without agenda) or the Philosopher (socratic development of the evolved position). The Contrarian is the wrong choice — drift is not an error to be corrected, it's a data point to be examined.

**Timing:** Dialogic interactions are surfaced in the Today View, not injected mid-session. Brett decides when to engage with them.

---

## 6. COGNITIVE_ARTIFACT.md Integration

The `drift/` layer in the export package is populated by this system:

```
drift/
  positions/        ← all extracted position objects (JSON)
  topic_ontology/   ← emergent topic taxonomy (JSON)
  drift_maps/       ← per-topic position timelines (JSON)
  summary.md        ← Archivist-generated drift narrative
```

This layer is what makes the cognitive artifact a *historical* document rather than a snapshot.

---

## 7. Open Questions

None blocking.

**Deferred:**
- **Q1:** Position extraction latency — the LLM extraction pass is computationally expensive for large vaults. Batch size and scheduling strategy TBD at implementation.
- **Q2:** Position confidence threshold for drift surfacing — only surface drift when both positions have confidence > X. Starting default: 0.7.

---

## 8. Dependencies

- Knowledge Skill live with corpus
- LLM available for extraction pass (same gateway LLM, async)
- Separate position index (@backend — new data structure)
- COGNITIVE_ARTIFACT.md: `drift/` layer ✅
- Archivist agent: drift narrative generation

**Academic reference:**
- Hamilton, W. L., Leskovec, J., & Jurafsky, D. (2016). Diachronic word embeddings reveal statistical laws of semantic change. *ACL 2016*.

---

*Cross-references: KNOWLEDGE_SKILL.md, COGNITIVE_ARTIFACT.md, ORAL_HISTORY.md, POLLY_AGENT_TEMPLATES.md (Interlocutor, Archivist)*
