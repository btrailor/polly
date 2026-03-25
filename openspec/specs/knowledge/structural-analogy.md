# STRUCTURAL_ANALOGY.md
*Phase 3 — Cross-Domain Structural Transfer*
*Status: Planned*
*Owners: @backend (indexing pipeline extension, knowledge_analogy tool), @code_architect (pattern taxonomy)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Cross-domain structural transfer from Brett's personal corpus — "find the version of me that already solved this problem in a different domain."

Semantic RAG finds surface similarity: notes that use similar words and concepts. Structural analogy finds *shape* similarity: notes that describe the same relational structure in different domains. These are different things. A feedback loop in a synthesizer and a feedback loop in organizational dynamics share almost no vocabulary — but they share structure.

The `knowledge_analogy` tool queries the structural layer of the Knowledge Skill index, not the semantic layer.

---

## 2. Theoretical Foundation

Grounded in Gentner's Structure Mapping Theory (1983): analogical reasoning aligns *relational structure*, not surface features. The analogy "an atom is like a solar system" works because the relational structure (central body, orbiting bodies, gravitational/electrostatic force) maps — not because atoms and solar systems share vocabulary.

Google Analogical Prompting research (2022–2024) demonstrates that LLMs can reliably identify structural analogies when prompted explicitly to look for relational structure rather than surface similarity. This is the implementation approach: LLM classification at retrieval time, not symbolic pattern matching.

**Why LLM classification is correct:** Symbolic Structure Mapping Theory implementations (SMT software) have failed at naturalistic text for 40 years — the formalization required strips away the contextual richness that makes analogies recognizable. LLM classification preserves that richness. @ai_expert confirmed this decision is correct. It is locked.

---

## 3. Implementation Architecture

### 3.1 Three Indexing Layers

The Knowledge Skill index is extended with two new layers alongside the existing semantic embedding layer:

| Layer | What it stores | How it's built |
|-------|---------------|----------------|
| Semantic embedding | Dense vector (existing) | `BAAI/bge-large-en` at index time |
| Structural pattern tags | Controlled vocabulary tags | LLM classification pass at index time |
| Domain label | Practice Layer taxonomy | Derived from wikilink cluster |

### 3.2 Structural Pattern Taxonomy

Starting taxonomy (~15 core patterns, growing from classification uncertainty):

| Pattern | Description |
|---------|-------------|
| `feedback-loop` | Output feeds back as input, amplifying or dampening |
| `layered-dependency` | Lower layers must be stable before upper layers can function |
| `constraint-produces-emergence` | Adding constraints creates new possibilities rather than limiting them |
| `threshold-behavior` | System behaves differently above and below a threshold value |
| `resource-contention` | Multiple processes compete for a shared limited resource |
| `graceful-degradation` | System loses capability incrementally rather than failing catastrophically |
| `tension-generative` | Two opposing forces in balance produce the system's characteristic output |
| `scaffolded-learning` | Temporary structure enables capability that persists after structure is removed |
| `asymmetric-information` | Parties in a system have access to different information |
| `phase-transition` | Quantitative change produces qualitative state change |
| `emergence-from-iteration` | Pattern only visible after many cycles; not present in any single cycle |
| `signal-noise-tradeoff` | Increasing sensitivity increases both signal detection and false positives |
| `attractor-state` | System tends toward certain configurations regardless of starting position |
| `delegation-loss` | Capability transferred to subsystem creates dependency and loss of direct access |
| `dead-reckoning` | Position estimated from known starting point + accumulated changes, without direct measurement |

The taxonomy is emergent — patterns are added when the LLM classifier's uncertainty is high (no existing pattern fits well). Brett reviews and names candidate additions.

### 3.3 LLM Classification Pass

At index time, each note receives a classification pass:

```
Given this note, identify which of the following structural patterns it describes or instantiates.
A note may match multiple patterns. Return pattern IDs with confidence scores.
If no pattern fits well (confidence < 0.4 for all), flag as "candidate new pattern."

Patterns: [taxonomy list]

Note content: [note text]
```

This pass is asynchronous and runs on the same dirty-flag schedule as the main index — it does not block retrieval.

### 3.4 Mapping Generation

Mapping generation happens at **retrieval time**, not indexing time. When `knowledge_analogy` returns a candidate:

```
Given that Brett is thinking about [context], and this note from his vault describes [note summary]:

Generate an explicit structural vocabulary mapping between the two domains.
Format: "Your [source concept] = their [target concept]"
Example: "Your 'guided practice layer' = 'orchestration layer'"

Focus on the relational structure, not the surface vocabulary.
```

This is an LLM pass at query time. It's computationally heavier than semantic retrieval but runs on a single result, not the full corpus.

---

## 4. Tool Specification

```
knowledge_analogy(
  context: string,           // The problem or situation Brett is thinking about
  source_domain?: string,    // Optional: constrain source to this domain (Practice Layer taxonomy)
  target_domain?: string,    // Optional: constrain target to this domain
  patterns?: string[],       // Optional: filter to specific structural patterns
  limit?: number             // Default: 3
) → AnalogyResult[]
```

**AnalogyResult:**
```json
{
  "note_id": "abc123",
  "note_title": "Feedback loops in organizational design",
  "domain": "systems_thinking",
  "matched_patterns": ["feedback-loop", "attractor-state"],
  "pattern_confidence": 0.87,
  "vocabulary_mapping": [
    "Your 'synthesis patch' = their 'organizational process'",
    "Your 'parameter modulation' = their 'policy adjustment'",
    "Your 'signal feedback' = their 'performance review cycle'"
  ],
  "mapping_confidence": 0.74
}
```

**Transparency requirement:** Both `pattern_confidence` (which patterns drove the match) and `mapping_confidence` (how well the vocabulary mapping holds) are surfaced. Brett sees which structural patterns were recognized and how confident the mapping is.

---

## 5. Agent Integration

The `knowledge_analogy` tool is available to agents that benefit from cross-domain reasoning. It is the technical grounding for the Generalist agent's SOUL statement about cross-domain synthesis — that claim is no longer purely rhetorical.

Agents most likely to use it: Generalist, Strategist, Systems Thinker, Philosopher, Scaffolder (for finding analogies to existing knowledge when building bridges to new domains).

---

## 6. Open Questions

None blocking.

**Deferred:**
- **Q1:** Taxonomy size ceiling — at what point does the taxonomy become too large to be useful? Current hypothesis: ~50 patterns is the ceiling before it needs hierarchical organization. Revisit at Phase 3 implementation.
- **Q2:** Mapping quality evaluation — how do we know if a generated vocabulary mapping is accurate? User feedback loop (thumbs up/down on returned analogies) feeds back to mapping confidence model.

---

## 7. Dependencies

- Knowledge Skill live (structural pattern indexing is an extension of existing index)
- Practice Layer domain taxonomy (for domain-constrained queries)
- LLM available at index time for classification pass
- `knowledge_analogy` as fourth Knowledge Skill tool (alongside `knowledge_search`, `knowledge_graph`, `knowledge_dream`)

**Academic references:**
- Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. *Cognitive Science*, 7(2), 155–170.
- Google Analogical Prompting: Yasunaga et al. (2023). Large Language Models as Analogical Reasoners. *arXiv:2310.01714*.

---

*Cross-references: KNOWLEDGE_SKILL.md, PRACTICE_LAYER.md, COGNITIVE_ARTIFACT.md (patterns/ layer), POLLY_AGENT_TEMPLATES.md (Generalist, Scaffolder)*
