# Architecture Integration Audit — Design

**Last Updated:** February 2026

---

## Findings Summary

### Critical Issues (Must Fix)

| # | Issue | Systems Affected | Sibling Change |
|---|-------|-----------------|----------------|
| 1 | Two incompatible `PatternLearner` classes with duck-typed bridge | `learners/patterns.py`, `core/pattern_learning.py`, `core/polly.py` | [unified-pattern-engine](../unified-pattern-engine/) |
| 2 | Three independent entity extraction systems, no shared model | `learners/graph.py`, `learners/patterns.py`, `core/memory/mem0_adapter.py` | [entity-model-unification](../entity-model-unification/) |
| 3 | Knowledge graph is architecturally disconnected from RAG and personas | `learners/graph.py`, `core/rag.py`, `core/personas/` | [entity-model-unification](../entity-model-unification/) |
| 4 | Specs reference unbuilt systems as current architecture | All specs | This document (reconciliation plan below) |
| 5 | Conversation storage split: Python `conversation_history` vs Electron SQLite | `core/polly.py`, `electron-app/src/main/conversation-manager.js` | [integration-contracts](../integration-contracts/) |

### High Issues (Should Fix)

| # | Issue | Systems Affected | Sibling Change |
|---|-------|-----------------|----------------|
| 6 | Personas don't compose with mental models, patterns, or graph | `core/personas/`, `core/mental_models.py`, pattern learners | [integration-contracts](../integration-contracts/) |
| 7 | Routing doesn't learn from pattern outcomes | `core/router_v2.py`, pattern learners | [integration-contracts](../integration-contracts/) |
| 8 | PIL is misnamed/misscoped — format string, not language | `core/compression/compressor.py`, `core/mental_models.py` | [unified-pattern-engine](../unified-pattern-engine/) |
| 9 | Mental models are prompt fragments with no effectiveness feedback | `core/mental_models.py` | [integration-contracts](../integration-contracts/) |
| 10 | Domain engine is static where spec promises dynamic | `core/domains.py` | [integration-contracts](../integration-contracts/) |

---

## Finding #1: Two Incompatible Pattern Learners

### Current State

**`learners/patterns.py`** (3000+ lines):
- `PatternLearner` class with rich concept extraction (spaCy, 500+ term whitelist)
- Stores `Pattern` dataclass (pattern_type, name, description, confidence, examples, occurrences, last_seen, domains)
- JSON file storage (`~/.polly/patterns.json`)
- Domain priority learning, code pattern extraction, query pattern tracking
- Conceptual patterns with cross-domain connections
- Used throughout `core/polly.py` for domain detection, RAG boosting, query expansion

**`core/pattern_learning.py`** (~400 lines):
- Separate `PatternLearner` class, different `Pattern` dataclass
- `Pattern(type, description, confidence, timestamp, metadata, occurrences)`
- Mem0-backed semantic search storage
- Used as `self.pattern_learner_mem0` in `core/polly.py`

**Bridge in `core/polly.py`** (`_get_patterns_for_prompt()`):
```python
# Anonymous class to bridge incompatible interfaces
wrap = type("_Mem0Pattern", (), {
    "name": p.description[:60] + "...",
    "pattern_type": p.type,
    "description": p.description,
    ...
})()
all_patterns.append(wrap)
```

### Problems
1. Two different `Pattern` data models — different field names, different semantics
2. Duck-typed bridge via anonymous class — no type safety, untestable
3. No bidirectional sync — patterns learned in one never reach the other
4. Rich features (concept extraction, domain priorities) only in `learners/` version
5. Semantic search only in `core/` version
6. Pattern decay/pruning exists in both but with different algorithms

### Resolution → [unified-pattern-engine/](../unified-pattern-engine/)

---

## Finding #2: Three Independent Entity Extraction Systems

### Current State

**System A: `KnowledgeGraph.extract_entities_from_text()`** (`learners/graph.py`):
- Regex-based keyword matching against hardcoded entity lists
- Entity types: concept, tool, project, pattern, person, file
- ~20 hardcoded concepts, ~10 tools — very limited coverage
- No NLP, no context-awareness

**System B: `PatternLearner` concept extraction** (`learners/patterns.py`):
- spaCy-based NLP extraction
- 500+ technical term whitelist
- Noun phrase extraction with frequency analysis
- Contextual — considers surrounding text

**System C: `Mem0Adapter.add_memory()`** (`core/memory/mem0_adapter.py`):
- LLM-based entity extraction (via Mem0 internal pipeline)
- Relationship mapping
- Semantic memory with entity metadata

### Problems
1. No shared `Entity` model — each system defines its own
2. No deduplication — "Python" extracted by all three systems stored independently
3. No relationship bridging — graph relationships don't know about Mem0 relationships
4. The knowledge graph's regex extraction is the weakest link — it's the only one that feeds into prompt context, but it has the worst extraction quality

### Resolution → [entity-model-unification/](../entity-model-unification/)

---

## Finding #3: Knowledge Graph is Architecturally Disconnected

### Current State

The knowledge graph is used in exactly two places during query processing:

```python
# In Polly.query() — prompt injection
graph_context = self.knowledge_graph.get_context_for_query(query, detected_domains)

# In Polly.query() — post-response extraction
self.knowledge_graph.extract_entities_from_text(query, detected_domains)
self.knowledge_graph.extract_entities_from_text(full_response, detected_domains)
```

### What the Spec Describes (But Doesn't Exist)
- Authority scoring algorithm for entities
- Anti-slop quality pipeline
- RAG integration with entity-graph traversal
- Visualization via Cytoscape.js
- Cross-domain connection bridging via graph algorithms
- Integration with Library (book entities), Capture, Notes

### Problems
1. Graph context in prompt is cosmetic — basic entity mention, no traversal
2. No authority scoring — all entities weighted equally
3. No RAG integration — graph doesn't influence retrieval ranking
4. No connection to personas — Architect doesn't use graph for planning, Scribe doesn't use it for organization
5. JSON storage limits graph operations — no adjacency queries, no path finding

### Resolution → [entity-model-unification/](../entity-model-unification/)

---

## Finding #4: Specs Reference Unbuilt Systems

### Systems Referenced as Architecture but Not Implemented

| System | Spec Status | Code Status | Referenced By |
|--------|-------------|-------------|---------------|
| Agent Swarms | Detailed spec with capability declarations, execution graphs, Nexus coordinator | **Zero code** | Personas, Security, DRM, Architecture |
| Aesthetic Themes | Detailed spec with 7 artist-derived themes, behavior injection | **Zero code** (no theme system at all) | Personas, Design, Domains, UI, Designer |
| DRM (Distributed Reasoning Mesh) | Detailed spec with discovery layers, PKI, task distribution | **Zero code** | Agent Swarms, Mobile, Router, Architecture |
| Mobile Companion | Spec with capture, chat, DRM node | **Zero code** | Capture, DRM, Communication |
| Communication/Email | Spec with Administrator modes, email intelligence | **Zero code** | Personas, Administrator profile |
| Publishing Pipeline | Spec with POSE stages, Ghost CMS | **Zero code** | Scribe, Designer, Maturity lifecycle |
| Canvas (BAD Canvas) | Spec with zone customization, RAG integration | **Zero code** | Architect, Knowledge graph |

### Problems
1. Other specs design their integration points against interfaces that don't exist
2. Architecture spec describes three-tier routing (Nexus → DRM Router → Router v2) but only Router v2 exists
3. Persona spec references "Agent Swarms capability declarations" for persona-agent mapping
4. Security spec plans "Capability Broker extends to Agent Swarms" — Capability Broker itself doesn't exist

### Reconciliation Plan

**Approach:** Every spec gets a clear status marker on every feature:

- **✅ Implemented** — Code exists and works
- **🔧 Partially Implemented** — Code exists but incomplete
- **📐 Designed** — Design exists in change folder, no code
- **💭 Vision** — Concept described, no detailed design

Specs that are 100% vision (Agent Swarms, DRM, Mobile, Communication, Publishing, Canvas) should have an explicit "Implementation Status: Vision — no code exists" header.

Specs that mix implemented and vision features (Personas, Patterns, Knowledge Graph, Themes) should annotate each section.

---

## Finding #5: Conversation Storage Split

### Current State

Conversations are stored in two independent systems:

1. **Electron Main Process** (`conversation-manager.js`): SQLite database, manages conversation CRUD, persists across sessions
2. **Python Backend** (`core/polly.py`): `self.conversation_history = []`, ephemeral list, reset on each Polly instance

### Problems
1. Two sources of truth — Electron has the persistent record, Python has the runtime buffer
2. Compression acts on Python's `conversation_history` but doesn't know about Electron's stored conversations
3. Pattern learning happens in Python against the ephemeral buffer — historical conversations in SQLite are never mined
4. No mechanism for Electron to tell Python "here are the last N messages from this conversation" at startup

### Resolution → [integration-contracts/](../integration-contracts/) (conversation synchronization protocol)

---

## Finding #6–10: Additional Issues

Detailed in their respective sibling change design documents:

- **#6 Persona isolation** → [integration-contracts/](../integration-contracts/) (PersonaAware protocol)
- **#7 Routing doesn't learn** → [integration-contracts/](../integration-contracts/) (PatternConsumer protocol)
- **#8 PIL misscoping** → [unified-pattern-engine/](../unified-pattern-engine/) (rename to "compact format")
- **#9 Mental model feedback** → [integration-contracts/](../integration-contracts/) (effectiveness tracking)
- **#10 Static domains** → [integration-contracts/](../integration-contracts/) (dynamic domain configuration)

---

## Execution Order

The four sibling changes have dependencies:

```
1. unified-pattern-engine (no dependencies — can start immediately)
   ├── Merge Pattern data model
   ├── Merge PatternLearner classes
   └── Unified storage backend

2. entity-model-unification (no dependencies — can parallel with #1)
   ├── Shared Entity model
   ├── Knowledge graph restructure
   └── Entity extraction pipeline consolidation

3. integration-contracts (depends on #1 and #2)
   ├── Cross-system protocols (PersonaAware, PatternConsumer, EntityProvider)
   ├── Persona composition with patterns, graph, mental models
   ├── Routing feedback loop
   ├── Conversation synchronization
   └── Mental model effectiveness tracking

4. library-extraction (depends on #3 for clean interfaces)
   ├── polly-routing library
   ├── polly-patterns library
   ├── polly-compression library
   ├── polly-knowledge-graph library
   └── polly-personas library

Concurrent: Spec reconciliation (this document) — can happen anytime
```

---

## Spec Reconciliation Schedule

After each sibling change completes, update the affected specs:

| Sibling Change | Specs to Update |
|---------------|-----------------|
| unified-pattern-engine | `patterns/spec.md`, `compression/spec.md` |
| entity-model-unification | `knowledge-graph/spec.md`, `rag/spec.md` |
| integration-contracts | `personas/spec.md`, `mental-models/spec.md`, `patterns/spec.md`, `architecture/spec.md` |
| library-extraction | `architecture/spec.md`, all affected domain specs |

**Immediately (before implementation):**
- Add implementation status markers to all specs
- Update `architecture/spec.md` to reflect actual (not aspirational) data flow
- Add "Vision — no code exists" header to: `agent-swarms`, `drm`, `mobile`, `communication`, `publishing`, `canvas`
