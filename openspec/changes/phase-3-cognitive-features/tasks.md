# Phase 3: Cognitive Features

**Status:** 💡 Specced  
**Gate:** Phase 2 Knowledge Skill complete (shared FAISS index + conversation history adapter required)  
**Spec sources:** `EPISTEMIC_IMMUNE_SYSTEM.md`, `METACOGNITIVE_DASHBOARD.md`, `TEMPORAL_INTELLIGENCE.md`, `STRUCTURAL_ANALOGY.md`, `DREAM_LOGIC.md`, `TREE_OF_THOUGHTS.md`, `PRACTICE_LAYER.md`, `ORAL_HISTORY.md`, `CL4R1T4S_RESEARCH.md` (EIS pattern vocabulary), `ANTI_PRODUCTIVITY.md` (Practice Layer dormancy data)

## Goal

The reflexive layer — Polly as an extension of the self. Seven capabilities that turn the knowledge base into a thinking partner that knows how you think, not just what you know.

## Dependency Map

All features below require Phase 2 Knowledge Skill. Additional dependencies noted per feature.

## Features + Tasks

### Epistemic Immune System
Detects when rhetorical patterns that have bypassed Brett's critical faculties in the past recur in new contexts. Layer 6 prompt injection.

- [ ] `rhetorical-structure-extractor` index hook registered at startup
- [ ] Pattern library built from Contrarian session outcomes (starting vocabulary: `CL4R1T4S_RESEARCH.md`)
- [ ] `polly.epistemic.flags` gateway config key (runtime-updated)
- [ ] Layer 6 injection into prompt assembly (request-scoped — confirm with @backend)
- [ ] Flag presentation: legible (show pattern + why), never blocks

### Metacognitive Dashboard
Tracks mental model usage across conversations. Surfaces which reasoning patterns are most effective for this user.

- [ ] `knowledge_conversation_history` consumer: extract mental model usage per session
- [ ] Implicit outcome signals: task creation, vault writes, conversation resolution
- [ ] Explicit outcome signal: user rating
- [ ] `suggested_models` re-ranking per agent based on personal effectiveness history
- [ ] Dashboard UI (Today view integration)

### Temporal Intelligence
Tracks how intellectual positions change over time. Drift detection + Drift view.

- [ ] Classifier filter pass (flags ~20-30% of chunks as position-relevant)
- [ ] LLM position extraction from flagged chunks
- [ ] Separate position index (distinct from main FAISS — temporal queries differ)
- [ ] Topic ontology: emergent from cluster analysis, not fixed taxonomy
- [ ] Drift view: topic map with time axis
- [ ] Dialogic agent prompt on detected drift

### Tree of Thoughts (`TREE_OF_THOUGHTS.md`)
Explicit multi-path reasoning mode. Agent generates a tree of candidate reasoning paths, evaluates them, and selects the best — surfacing the reasoning tree to the user rather than hiding the deliberation.

- [ ] Tree of Thoughts reasoning mode implementation in agent SOUL baseline (Phase 3 activation)
- [ ] `allowed_modes: ["tree_of_thoughts"]` gating — analytical agents (Code Architect, Strategist, Analyst, Data Scientist) + any agent where user explicitly enables
- [ ] Routing integration: routing engine can request tree-of-thoughts mode for high-complexity queries (Tier 3+)
- [ ] UI: collapsible reasoning tree display in chat bubble (shows candidate paths + evaluation) — @frontend
- [ ] Coordination with Metacognitive Dashboard: tree depth + branching factor logged as complexity signal

### Structural Analogy (`knowledge_analogy` tool)
Cross-domain structural transfer — finds notes with matching relational structure, not vocabulary.

- [ ] Structural pattern taxonomy (~15 core patterns)
- [ ] `structural-pattern-tagger` index hook registered at startup
- [ ] `domain-label-enricher` index hook registered at startup
- [ ] `knowledge_analogy` tool implementation
- [ ] Confidence scoring + pattern tag transparency
- [ ] `allowed_modes: ["analogy"]` gating per agent manifest

### Dream Logic (`knowledge_dream` tool)
Structured misretrieval — FAISS distance band 0.5–0.7.

- [ ] Distance-band FAISS query (k=200 initial, filter to band)
- [ ] `knowledge_dream` tool implementation
- [ ] Agent behavior contract enforced: surface collision, no explanation
- [ ] `allowed_modes: ["dream"]` gating — creative agents only
- [ ] Domain exclusion (`exclude_domain` filter)

### Practice Layer
Derives a map of the user's creative practices from vault structure and timestamps. No new user input required.

- [ ] Data model: last_engaged, engagement_frequency (90-day histogram), depth_signal, cross_domain_links, dormancy_threshold_days
- [ ] Derived from Knowledge Skill wikilink graph + file timestamps
- [ ] Dormancy alert
- [ ] Cross-pollination view
- [ ] Feeds: Anti-Productivity (`ANTI_PRODUCTIVITY.md`), Conversation Architecture

### Oral History
Voice transcripts → longitudinal intellectual autobiography.

- [ ] Voice transcript corpus ingestion (requires Phase 1 real audio recording)
- [ ] Archivist agent annual synthesis pass
- [ ] Output: readable intellectual autobiography sections
- [ ] Integration with Cognitive Artifact export

## Done when
All 7 features shipped and integrated. Knowledge Skill consumer dependency table fully resolved. Cognitive Artifact export includes all layers.
