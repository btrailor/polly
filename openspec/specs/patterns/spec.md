# Patterns & Pattern Learning (OpenSpec)

Source of truth for the pattern learning system (Phase 13a) and pattern-based compression (Phase 2b). Detail: [docs/planning/phases/other/PHASE13A_PATTERN_LEARNING_CORE.md](../../../docs/planning/phases/other/PHASE13A_PATTERN_LEARNING_CORE.md), [docs/planning/tiers/TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md).

## Overview

Polly learns from every interaction. The pattern learning system extracts recurring structures from user queries, code, concepts, routing decisions, and workflows — then uses those patterns to optimize RAG retrieval, inform routing decisions, and personalize responses. Knowledge compounds over time: the more you use Polly, the better it gets.

---

## Pattern Types

### Query Patterns
- **What:** Templates extracted from user queries (e.g., "How do I {action} {thing}?").
- **Learned from:** Conversation history — repeated query structures detected and generalized.
- **Used by:** RAG query expansion, domain detection.

### Query→Chunk Patterns (Phase 13a)
- **What:** Maps specific query types to the document chunks that successfully answered them.
- **Learned from:** RAG search results where the user accepted/used the response.
- **Used by:** RAG chunk boosting — previously successful chunks get priority for similar queries.
- **Impact:** 30–50% faster RAG retrieval via pattern-based chunk boosting.

### Domain→Collection Priority Patterns (Phase 13a)
- **What:** Maps domains to which RAG collections are most relevant.
- **Learned from:** Which collections produce useful results per domain over time.
- **Used by:** RAG collection weighting — skip low-priority collections for faster search.
- **Impact:** 20–40% faster retrieval by pruning irrelevant collections early.

### Code Patterns
- **What:** Structural patterns extracted from code via AST analysis.
- **Python patterns:** Common imports, class inheritance, decorators, error handling (try/except), async/await, context managers, comprehensions.
- **JavaScript patterns:** Framework detection (React, Vue), hooks, JSX, async/await, arrow functions, promises, TypeScript, class vs. functional components.
- **Learned from:** Code files indexed by RAG. Extracted during indexing by `CodePatternExtractor`.
- **Used by:** Code-aware RAG context, persona behavior (Architect Build mode).

### Conceptual Patterns
- **What:** Relationships between concepts — how ideas connect across the user's knowledge base.
- **Learned from:** Entity co-occurrence in notes, conversations, captures.
- **Used by:** Query expansion (mention X, also search for related concept Y), knowledge graph enrichment.
- **Status:** Foundation exists (spaCy concept extraction with 500+ technical terms); refinement planned.

### Workflow Patterns
- **What:** Project-specific sequences of actions and decisions.
- **Learned from:** Repeated workflows across conversations (Research → Plan → Write, Teach → Assess → Refine).
- **Used by:** Proactive suggestions ("You usually do X next after Y"), Agent Swarms Nexus (template suggestion, workflow composition).
- **Status:** Data model exists; learning and application planned.

### Library Usage Patterns (Planned)
- **What:** Tracks which code library modules are applied where and how successfully.
- **Learned from:** `CodeLibraryManager.record_usage()` calls when modules are applied to projects.
- **Used by:** Library module confidence scoring, cross-project pattern recognition, Librarian persona recommendations.
- **Data:** Module name, projects applied in, times applied, edge cases encountered.
- **Promotion pipeline:** High-confidence code patterns (>0.8) are candidates for promotion to full library modules. See [code-library spec](../code-library/spec.md).

### Routing Patterns (Planned)
- **What:** Which models work best for which task types.
- **Learned from:** Routing decisions + user satisfaction signals.
- **Used by:** Router v2 for adaptive model selection.
- **Impact:** 10–20% better routing accuracy.

### Persona Patterns (Planned)
- **What:** Persona-specific behavior preferences (Scribe writing style, Architect decision patterns).
- **Learned from:** Persona mode interactions and user feedback.
- **Used by:** Persona behavior customization.

## Architecture (Unified Pattern Engine — Feb 2026)

The pattern system was consolidated from two independent implementations into a single **Unified Pattern Engine** (`core/patterns/`). This eliminated fragile duck-typed bridging code and provides a single API for all consumers.

### Module Structure
```
core/patterns/
├── __init__.py          # Public API: PatternEngine, Pattern, PatternType, PatternQuery
├── models.py            # Unified Pattern dataclass, PatternType enum, specialized pattern types
├── engine.py            # PatternEngine — main class for learn/search/lifecycle
├── scorer.py            # Multi-factor relevance scoring (migrated from polly.py)
├── migration.py         # One-time migration from old v2.0 JSON format
└── storage/
    ├── base.py          # StorageBackend protocol
    ├── json_backend.py  # Primary: JSON file with in-memory cache, atomic writes
    └── mem0_backend.py  # Optional: Mem0 semantic search backend
```

### Key Classes
- **`PatternEngine`**: Single entry point. Initializes backends, exposes learn/search/lifecycle API.
- **`Pattern`**: Unified dataclass merging fields from both old learners. Includes `PatternType` enum, usefulness tracking, entity references.
- **`PatternScorer`**: Ranks patterns by multi-factor score (confidence, recency, domain match, keyword overlap, type-specific boosts).
- **`JSONBackend`**: Always-on file storage with in-memory cache and atomic writes (temp + rename).
- **`Mem0Backend`**: Optional semantic search. Lazy-initializes. Returns proper `Pattern` objects (no more anonymous duck-typed wrappers).

### Previous Architecture (deprecated)
Before Feb 2026, patterns were split across two incompatible systems:
- `learners/patterns.py` — Rich Pattern model with spaCy NLP, in-memory dicts, 1000+ lines
- `core/pattern_learning.py` — Simple Pattern model with Mem0 integration, 400 lines
- Bridge: `polly.py._get_patterns_for_prompt()` used anonymous `type()` wrappers to merge results

The old files are preserved for reference but no longer used by the main application.

## Storage

### Primary: JSON File
- **Location:** `~/.polly/patterns.json`
- **Format:** Version 3.0 (unified engine format). Auto-migrates from v2.0 on first load.
- **Atomic writes:** Uses temp-file-then-rename to prevent corruption.
- **Structure:** Unified Pattern objects with type enum, domains, keywords, usefulness tracking, entity refs.

### Secondary: Mem0 (Optional)
- **When enabled:** Patterns also stored in Mem0 for semantic search.
- **Benefit:** Fuzzy pattern matching — "code review preferences" finds patterns even if stored as "prefers Sonnet 4 for reviewing code."
- **Fallback:** If Mem0 unavailable, keyword search over JSON.
- **No more wrappers:** Mem0 results are proper `Pattern` objects, not anonymous duck-typed classes.

### Planned: Knowledge Graph Integration
- Pattern entities (high-confidence patterns) become nodes in the knowledge graph.
- Cross-project pattern recognition: patterns from one project inform another.
- See [knowledge-graph spec](../knowledge-graph/spec.md).

## Pattern Lifecycle

### Learning
```
User interaction
  │
  ├── Query → extract query template → QueryPattern
  ├── Successful RAG result → record query→chunk mapping → QueryChunkPattern
  ├── Code indexed → AST analysis → CodePattern
  ├── Concepts mentioned → spaCy extraction → ConceptualPattern
  └── Domain query → collection results → DomainPriorityPattern
```

### Reinforcement
- Repeated patterns increase `occurrences` count and `confidence` score.
- Confidence increases by 0.1 per occurrence (capped at 1.0).
- Timestamp updated on each reinforcement.

### Decay & Pruning
- **Decay:** 2% confidence decay per day after 60 days of inactivity.
- **Pruning:** Patterns with confidence below threshold are removed.
- **Usefulness tracking:** `times_used` and `times_helpful` fields track whether patterns actually improve results.
- Prevents pattern accumulation from becoming its own form of slop.

## Concept Extraction (spaCy)

### Technical Terms Whitelist
- 500+ curated technical terms preserved during extraction (e.g., "machine learning," "finite state machine," "dependency injection").
- Prevents spaCy from filtering domain-specific terminology as stopwords.

### Stopwords
- 700+ stopwords for filtering noise from concept extraction.
- Augmented beyond spaCy defaults with conversation-specific terms.

### Extraction Pipeline
```
Text → spaCy NLP → Named entities + noun chunks
  → Filter by whitelist/stopwords
  → Deduplicate and normalize
  → Return concept list with frequency
```

## RAG Integration (Active)

The pattern system is deeply integrated with RAG. Three active integration points:

### 1. Chunk Boosting
```python
# In core/rag.py — during search
boosted_chunks = pattern_learner.get_boosted_chunks_for_query(query)
# Boosted chunks get priority in result ranking
```
When a query matches a known QueryChunkPattern, the chunks that previously answered similar queries get boosted in the search results.

### 2. Collection Weighting
```python
# In core/rag.py — before collection search
weights = pattern_learner.get_collection_weights_for_domain(domain)
# High-weight collections searched first; low-weight skipped
```
Domains accumulate patterns about which collections are relevant. A code-heavy domain learns to prioritize the `code` collection.

### 3. Code Pattern Extraction
```python
# In core/rag.py — during code indexing
code_extractor = CodePatternExtractor()
patterns = code_extractor.extract(source_code, language)
pattern_learner.record_code_pattern(patterns)
```
Code files are analyzed for structural patterns during RAG indexing. These patterns inform code-aware responses.

## UI

### Patterns Page
- **Navigation:** Accessible via ribbon icon.
- **Pattern cards:** Grouped by type (conceptual, query, code). Show confidence score, occurrence count, domains.
- **Filters:** Time range (last 7 days, 30 days, all time).
- **Actions:** Refresh, export to JSON, reset all patterns.
- **Statistics sidebar:** Total patterns, breakdown by type, confidence distribution (high/medium/low).
- **Empty state:** Guidance when no patterns learned yet.

### Implementation
- `electron-app/src/renderer/app.js` — `loadPatterns()`, `filterPatterns()`, `exportPatterns()`, `resetPatterns()`
- `electron-app/src/renderer/index.html` — Patterns view section with controls and statistics.

## API

### Pattern Learner (`core/pattern_learning.py`)

```python
from core.pattern_learning import get_pattern_learner, Pattern

learner = get_pattern_learner(config)

# Learn a pattern
learner.learn_pattern(Pattern(
    type="routing",
    description="User prefers Sonnet 4 for code review tasks",
    confidence=0.9,
    timestamp=datetime.now().isoformat(),
    metadata={"model": "claude-sonnet-4", "task": "code_review"}
))

# Search patterns (semantic via Mem0, fallback to keyword)
results = learner.search_patterns("code review preferences", pattern_type="routing")

# Get patterns by type
routing_patterns = learner.get_patterns_by_type("routing")

# Statistics
stats = learner.get_pattern_stats()
# → {'total': 42, 'by_type': {'routing': 12, 'query': 18, ...}, 'avg_confidence': 0.72, ...}
```

### Advanced Pattern Learner (`learners/patterns.py`)

```python
from learners.patterns import PatternLearner

learner = PatternLearner(config)

# Query→Chunk patterns
learner.create_or_update_query_chunk_pattern(query, successful_chunks, domain)
boosted = learner.get_boosted_chunks_for_query(query)

# Domain→Collection weights
learner.create_or_update_domain_priority_pattern(domain, collection_weights)
weights = learner.get_collection_weights_for_domain(domain)

# Concept patterns
concepts = learner.get_conceptual_patterns_for_concept("finite games")
```

### REST API
- `GET /api/patterns` — List patterns (filterable by type, time range)
- `GET /api/patterns/stats` — Pattern statistics
- `POST /api/patterns/export` — Export patterns to JSON
- `POST /api/patterns/reset` — Reset all patterns (with confirmation)

## Planned Enhancements

### Router Integration (Use Case 4)
- Use query→chunk patterns to determine if a query is well-answered locally.
- Route to local model if patterns show high confidence for similar queries.
- Route to cloud if patterns show low confidence.

### Domain Auto-Detection (Use Case 2)
- Use domain patterns to auto-detect domain from query content.
- Improves domain classification for captures and notes.

### Proactive Context Loading (Use Case 1)
- Pre-load RAG context based on predicted patterns.
- "You usually ask about X after discussing Y" → prefetch X context.

### Workflow Learning (Use Case 3)
- Learn multi-step workflows from conversations.
- Suggest next steps based on workflow patterns.
- Feed into Agent Swarms Nexus (Phase 24a–24e): successful workflow patterns inform template suggestions and automatic workflow composition.
- See [agent-swarms spec](../agent-swarms/spec.md).

### Cross-Project Pattern Recognition
- Detect transferable patterns across projects/domains.
- "You solved a similar problem in project X using approach Y."
- Enabled by knowledge graph integration.
- See [canvas spec](../canvas/spec.md) for cross-canvas pattern recognition.

### Pattern → Code Library Promotion
- High-confidence code patterns (confidence > 0.8) are candidates for promotion to reusable library modules.
- Patterns seen in 3+ different files/projects automatically flagged as extraction candidates.
- Promotion workflow: PatternLearner flags candidate → user confirmation (or auto-extract) → extraction → module created → pattern linked to module via provenance.
- The Code Library is where patterns graduate from observations to instruments.
- See [code-library spec](../code-library/spec.md).

### Knowledge Graph Integration
- High-confidence patterns become entities in the knowledge graph.
- Pattern relationships tracked as graph edges.
- Pattern authority scoring: frequently-used, high-confidence patterns rank higher.
- See [knowledge-graph spec](../knowledge-graph/spec.md).

### Library Pattern Learning
- Learn which book passages are relevant for which query types.
- "When user asks about pedagogy, chapters from Freire's work are usually helpful."
- Integrates with library source-type weighting.
- See [library spec](../library/spec.md).

## Ancillary Use Cases (9 planned, documented in Phase 13a)

| # | Use Case | Target Phase | Status |
|---|----------|-------------|--------|
| 1 | Proactive Context Loading | Phase 20 | 📋 |
| 2 | Domain Auto-Detection Enhancement | Phase 1.5 | 📋 Critical |
| 3 | Autonomous Workflow Learning | Phase 3 | 📋 |
| 4 | Multi-Model Router Optimization | Phase 11 | 📋 |
| 5 | Session Context Persistence | Phase 20 | 📋 |
| 6 | Smart Notification Filtering | Phase 6 | 📋 |
| 7 | Intelligent Command Suggestions | Phase 10 | 📋 |
| 8 | Knowledge Gap Detection | Phase 18 | 📋 |
| 9 | Concept-Based Note Linking | Phase 12 | 📋 |

Detail: [PHASE13A_ANCILLARY_USE_CASES.md](../../../docs/planning/phases/other/PHASE13A_ANCILLARY_USE_CASES.md)

## Implementation Files

| File | Purpose | Lines |
|---|---|---|
| `core/pattern_learning.py` | Pattern dataclass + PatternLearner (JSON + Mem0) | ~395 |
| `learners/patterns.py` | Advanced pattern learner (query→chunk, domain priority, concepts, spaCy) | ~3,024 |
| `learners/code_patterns.py` | AST-based code pattern extraction (Python, JavaScript) | ~200 |
| `core/rag.py` | Pattern integration: chunk boosting, collection weighting, code extraction | (integrated) |
| `electron-app/src/renderer/app.js` | Pattern UI: load, filter, export, reset | (integrated) |

## Compression (Phase 2b)

Pattern-based compression reduces token usage for pattern and mental model context:

- **Types:** conversation, pattern, mental_model.
- **Token savings:** 40–60% for pattern-based context management.
- **Triggers:** Token threshold, message count.
- **Settings UI:** Compression panel, stats (tokens saved, ratio), user thresholds.
- **Implementation:** `core/compression/compressor.py`.
- **Detailed compression spec:** [compression spec](../compression/spec.md).

## Reference

- [PHASE13A_PATTERN_LEARNING_CORE.md](../../../docs/planning/phases/other/PHASE13A_PATTERN_LEARNING_CORE.md) — Full Phase 13a spec (3,200 lines)
- [PHASE13A_ANCILLARY_USE_CASES.md](../../../docs/planning/phases/other/PHASE13A_ANCILLARY_USE_CASES.md) — 9 ancillary use cases
- [PHASE11_COMPRESSION_SYSTEM.md](../../../docs/planning/phases/phase-11/PHASE11_COMPRESSION_SYSTEM.md) — Compression UI
- [TIER_1_INTELLIGENCE.md](../../../docs/planning/tiers/TIER_1_INTELLIGENCE.md) — Tier 1 pattern summary
- Compression: [compression spec](../compression/spec.md)
- Knowledge graph: [knowledge-graph spec](../knowledge-graph/spec.md)
- Library: [library spec](../library/spec.md)
