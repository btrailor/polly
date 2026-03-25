# DREAM_LOGIC.md
*Phase 3 — Structured Misretrieval*
*Status: Planned*
*Owners: @backend (FAISS distance-band query, knowledge_dream tool)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Structured misretrieval — a retrieval mode that deliberately targets the uncanny valley of Brett's knowledge graph.

Standard semantic retrieval (`knowledge_search`) targets distance 0.0–0.3: close matches, high relevance, good recall. Dream Logic targets distance 0.5–0.7: notes that are non-arbitrarily related (not random noise) but whose connection has not yet been named. The relationship exists — it's just not conscious yet.

The biological grounding is REM sleep (Stickgold & Walker, 2013): during REM, the hippocampus activates distant associative connections that waking cognition suppresses. Dreams are not random — they are thematically coherent in ways that resist literal interpretation. Dream Logic is the same principle applied to knowledge retrieval.

Eno's ambient music methodology is the creative practice analog: create conditions for unexpected emergence rather than directing outcomes. `knowledge_dream` creates conditions for unexpected connection rather than retrieving expected matches.

---

## 2. The Distance Band

```
0.0 – 0.3: high semantic similarity → knowledge_search territory
0.3 – 0.5: moderate similarity → related notes, usually findable by browsing
0.5 – 0.7: low similarity, non-arbitrary → the uncanny valley (Dream Logic zone)
0.7 – 1.0: noise → random, no meaningful connection
```

The 0.5–0.7 band is the generative zone: connections that exist but haven't been made consciously. Too close (< 0.5) and the connection is already obvious. Too far (> 0.7) and it's just noise. The band is tunable per-query but 0.5–0.7 is the default.

---

## 3. Tool Specification

```
knowledge_dream(
  context: string,           // What Brett is currently thinking about
  distance_min?: float,      // Default: 0.5
  distance_max?: float,      // Default: 0.7
  exclude_domain?: string,   // Exclude Brett's current domain (force cross-domain collisions)
  limit?: number             // Default: 3 (collision generator, not result list)
) → DreamResult[]
```

**DreamResult:**
```json
{
  "note_id": "xyz789",
  "note_title": "On the grain of a surface",
  "domain": "typography",
  "distance": 0.63,
  "collision_context": null
}
```

**limit=3 is the spec.** Dream Logic is not a retrieval tool that happens to return distant results — it's a collision generator. Three collisions is enough to be generative; more is noise.

**exclude_domain** forces cross-domain collisions. If Brett is working in SuperCollider, `exclude_domain: "synthesis"` ensures the dream results come from outside that cluster — typography, systems thinking, pedagogy. The value of Dream Logic is precisely the cross-domain collision; same-domain distant results are less interesting.

---

## 4. Agent Behavior — Inverted

This is the most important design constraint: **the agent's behavior is inverted**.

In standard retrieval, the agent presents a result with an explanation of why it's relevant. In Dream Logic mode, the agent presents the collision *without* explanation and asks Brett to find the meaning:

> "I don't know why this is relevant. Do you?"
> *[note title and brief excerpt]*

The agent is not withholding an explanation it has — it genuinely doesn't explain. The interpretation belongs to Brett. The agent's job is to surface the collision and get out of the way.

This is the Oblique Strategies principle applied to retrieval: the constraint (present without explaining) forces Brett into a different cognitive mode. If the agent explains, Brett evaluates the explanation. If the agent doesn't explain, Brett has to *find* the connection — which is the creative act.

An agent that explains the dream result has defeated the purpose of Dream Logic.

---

## 5. Agent Selectivity

Dream Logic is not available to all agents. The `allowed_modes` field in the agent manifest governs access.

**Agents with Dream mode enabled (default):**
- Writer
- Audio Producer
- Music Producer
- Cartographer
- Philosopher
- Generalist
- Ambient Agent

**Agents without Dream mode (analytical agents — default off):**
- Code Architect
- Backend Architect
- Security Auditor
- Analyst
- Data Scientist
- Strategist

**Rationale:** Dream Logic is generative and interpretive. Analytical agents working on implementation problems need accurate retrieval, not productive confusion. Adding Dream mode to an agent is a deliberate choice, not a default.

Brett can override per-agent in agent settings.

---

## 6. Session Context

`knowledge_dream` is called with `context` — what Brett is currently thinking about. This context is used to query the FAISS index: find notes that are in the 0.5–0.7 distance band *relative to this context*, not relative to the full corpus. The context anchors the dream; without it, results would be random relative to Brett's current thinking.

The context is typically the last user message or a brief summary of the current session topic, injected by the gateway automatically when Dream mode is active.

---

## 7. Implementation Notes

### 7.1 FAISS Distance-Band Query

The existing `IndexHNSWFlat` supports distance-filtered queries. The implementation:

```python
# Standard retrieval
results = index.search(query_vector, k=10)  # top-k closest

# Dream Logic retrieval
distances, indices = index.search(query_vector, k=200)  # cast wide
dream_results = [
    (d, i) for d, i in zip(distances, indices)
    if distance_min <= d <= distance_max
][:limit]  # filter to band, take limit
```

The wider initial search (k=200) ensures we have candidates in the target band before filtering. The band is applied post-search.

### 7.2 Domain Exclusion

If `exclude_domain` is specified, filter out results whose domain label matches before applying the distance band filter.

---

## 8. Open Questions

None blocking.

**Deferred:**
- **Q1:** Band calibration per-user — 0.5–0.7 is a starting default based on theoretical reasoning, not empirical tuning. User feedback loop (was this result generative? yes/no) could tune the band over time. Phase 3+ feature.

---

## 9. Dependencies

- Knowledge Skill live with FAISS HNSW index
- Domain labels on index entries (Practice Layer taxonomy)
- `allowed_modes` field in agent manifest schema (@backend — new field)
- SOMATIC_INTERFACE.md: prosodic context could inform whether Dream mode is appropriate (slow/uncertain state → more receptive to dream collisions)

**Academic references:**
- Stickgold, R., & Walker, M. P. (2013). Sleep-dependent memory triage: evolving generalization through selective processing. *Nature Neuroscience*, 16(2), 139–145.

---

*Cross-references: KNOWLEDGE_SKILL.md, PRACTICE_LAYER.md, POLLY_AGENT_TEMPLATES.md (agent manifest schema)*
