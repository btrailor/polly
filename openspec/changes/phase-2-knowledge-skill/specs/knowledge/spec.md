# Delta: Knowledge — Phase 2

## ADDED Requirements

### Requirement: Unified Knowledge Index
The system MUST maintain a single shared FAISS HNSW index serving all knowledge sources (vault, booklore, conversation history). No feature outside the Knowledge Skill SHALL write to this index directly.

### Requirement: Hybrid Retrieval
The system MUST use hybrid dense+sparse retrieval with RRF fusion for all knowledge_search queries. Pure dense or pure sparse retrieval alone is insufficient.

### Requirement: Retrieval Classification
Every search result MUST carry a retrieval tier: DIRECT (score ≥ 0.75), ADJACENT (0.45–0.75), or ABSENT (< 0.45). The ABSENT tier MUST be returned as an empty results array with a top-level `retrieval_tier: "ABSENT"` field — the skill SHALL NOT return low-confidence chunks as results.

#### Scenario: Agent communicates retrieval tier
- GIVEN a knowledge_search result with `retrieval_tier: "ADJACENT"`
- WHEN an agent incorporates this result into a response
- THEN the agent MUST qualify the claim ("Your notes don't address this directly, but…")
- AND the agent MUST NOT assert the content as if it were a DIRECT match

### Requirement: Wikilink Graph
The system MUST extract wikilinks from vault notes at ingest time and store them in a SQLite graph store. Dangling links (pointing to notes that don't exist) MUST be stored with `to_id: null` and resolved on the next ingest cycle when the target note is created.

### Requirement: Index Hooks Extension Point
The Knowledge Skill MUST support a registered hook interface for additional metadata enrichment passes at index time. The hook registry MUST hot-reload from `hooks.json` without requiring service restart. Phase 2 ships with zero registered hooks.

### Requirement: Degradation Resilience
The system MUST handle all failure modes without throwing to the caller:
- Stale index: continue serving from stale index; surface amber indicator in skill settings
- Corrupt index: return ABSENT for all queries; surface red indicator + rebuild action
- Embedding failure: fall back to sparse-only (BM25); circuit breaker with 60s reset
- Watcher failure: restart with exponential backoff; surface error after 3 failures

### Requirement: Domain Taxonomy Bootstrap
The system MUST read user-declared domains from gateway config key `polly.knowledge.domain_seeds` and apply keyword-based domain labeling to vault notes at ingest time. User-declared domains MUST NOT be silently overridden.

## MODIFIED Requirements

### Requirement: knowledge_search Return Type
(Previously: unspecified)
The `knowledge_search` tool SHALL return `SearchResult[]` where each result includes: chunk_id, source, title, path, section (vault), chapter (booklore), tags (vault), author (booklore), text, score (RRF fusion), retrieval_tier.

## ADDED Requirements (Service Contracts)

### Requirement: Single Service Model
All Phase 3 features that require knowledge retrieval MUST consume the Knowledge Skill's tool interfaces. No feature SHALL maintain its own vector index or duplicate the FAISS infrastructure.

### Requirement: Read-Only Consumer Contract
All consumers of the Knowledge Skill are read-only. The Knowledge Skill is the sole writer to the FAISS index, SQLite graph store, dirty-flag registry, and hook registry.
