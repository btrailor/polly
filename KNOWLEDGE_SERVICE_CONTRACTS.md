# KNOWLEDGE_SERVICE_CONTRACTS.md
*Cross-feature data sharing contracts for the Knowledge Service and its consumers*
*Status: Planned*
*Owners: @code_architect (contract definitions), @backend (gateway config read path, layers 3-5 injection)*
*Last updated: 2026-03-25*

---

## 1. Architecture Decision: Single Service Model

**Decided: 2026-03-25 (@backend sign-off)**

The Knowledge Skill is a **single service with multiple tool interfaces**, not a collection of independent skills. All Phase 3 features that need retrieval (Practice Layer, Structural Analogy, Epistemic Immune System, Metacognitive Dashboard, Temporal Intelligence, Oral History) are **consumers** of this service — they do not run their own indexes.

The shared FAISS index is the crux. Independent skills that each duplicate the index create:
- Index consistency problems (different features see different versions of the corpus)
- Disk and memory waste (multiple copies of large embedding indexes)
- Ingest coordination problems (who watches which files?)
- Cross-feature data dependencies that can't be satisfied without shared state

Single service with declared consumer contracts solves all of these.

**What this means concretely:**
- The Knowledge Skill owns the FAISS index, the SQLite graph store, and the conversation history corpus. Full stop.
- Other features register as consumers via the index hook system (write-side) and tool interfaces (read-side).
- No feature outside the Knowledge Skill writes to the index or graph store directly.
- No feature duplicates index infrastructure.

---

## 2. Tool Interface Contracts

These are the tool interfaces the Knowledge Service exposes. Other features call these tools; they do not read the underlying data structures directly.

### 2.1 `knowledge_search`

Already specified in `KNOWLEDGE_SKILL.md`. Consumer contract:

```
Consumers: all agents, all Phase 3 features
Access: read-only
Returns: SearchResult[] with retrieval_tier (DIRECT | ADJACENT | ABSENT)
SLA: p95 < 300ms for dense+sparse+rerank pipeline
Degradation: ABSENT tier returned if index unhealthy — never throws
```

**Consumer obligation:** Agents must communicate retrieval tier to the user. DIRECT = assertable. ADJACENT = qualify. ABSENT = "this is my general knowledge, not from your notes." Non-compliance with this contract produces epistemic dishonesty in agent responses.

---

### 2.2 `knowledge_graph`

Already specified in `KNOWLEDGE_SKILL.md`. Consumer contract:

```
Consumers: Practice Layer, Structural Analogy, agents with graph access
Access: read-only, vault source only
Returns: { nodes: NoteNode[], edges: WikilinkEdge[], root: string }
Requires: wikilink graph layer opt-in (user setting)
SLA: p95 < 500ms for depth ≤ 2; depth 3 may take up to 2s
Degradation: empty graph returned if graph store unavailable — never throws
```

---

### 2.3 `knowledge_domains`

Returns the current domain taxonomy — the merged result of user-declared domains (iOS MMKV seed) and any graph-derived enrichments (Phase 3).

```json
{
  "name": "knowledge_domains",
  "description": "Returns the current domain taxonomy used for tagging and filtering knowledge base content.",
  "parameters": {},
  "returns": {
    "domains": "Domain[]",
    "source": "string — 'seeded' | 'graph-enriched' (Phase 3)",
    "last_enriched": "ISO 8601 timestamp | null"
  }
}
```

**`Domain` schema:**
```json
{
  "id": "string — e.g. 'code', 'systems', 'audio'",
  "name": "string — display label",
  "color": "string — hex #RRGGBB (from iOS domain config)",
  "keywords": "string[] — user-declared keywords (from iOS domain config)",
  "note_count": "integer — number of vault notes tagged to this domain",
  "cluster_confirmed": "boolean — Phase 3: whether graph analysis confirms this domain exists in vault structure"
}
```

```
Consumers: Practice Layer, Structural Analogy, Conversation Architecture, agents using domain filters
Access: read-only
SLA: p95 < 50ms (cached in memory, refreshed on domain config change)
Degradation: returns seeded domains from config if graph enrichment unavailable
```

---

### 2.4 `knowledge_register_hook`

Registers an index hook for the next indexing cycle. Phase 3 features use this at startup to register their hooks. Does not trigger immediate re-indexing — hooks run on the next dirty-flag cycle.

```json
{
  "name": "knowledge_register_hook",
  "description": "Register an index hook to run additional processing passes during chunk ingestion. Phase 3 features use this to add metadata without requiring full re-index.",
  "parameters": {
    "hook_id": "string — unique identifier, e.g. 'structural-pattern-tagger'",
    "sources": "string[] — which sources this hook applies to: ['vault', 'booklore', 'conversation']",
    "run_async": "boolean — true: runs in background after chunk ingest; false: blocks ingest (use sparingly)",
    "hook_endpoint": "string — tool name or service endpoint the Knowledge Skill calls to process each chunk"
  },
  "returns": {
    "registered": "boolean",
    "existing_hook_overwritten": "boolean — true if a hook with this ID was already registered"
  }
}
```

```
Consumers: Structural Analogy (structural-pattern-tagger), Practice Layer (domain-label-enricher),
           Epistemic Immune System (rhetorical-structure-extractor)
Access: write (hook registry only — does not write to index directly)
Timing: register at feature startup; hook runs on next dirty-flag cycle
```

**Registered Phase 3 hooks:**

| Hook ID | Registered by | Sources | Async | Adds to metadata |
|---------|--------------|---------|-------|-----------------|
| `structural-pattern-tagger` | Structural Analogy | `['vault']` | true | `structural_patterns: string[]` |
| `domain-label-enricher` | Practice Layer | `['vault', 'conversation']` | true | `domain: string` (graph-derived) |
| `rhetorical-structure-extractor` | Epistemic Immune System | `['conversation']` | true | `rhetorical_type: string`, `argument_structure: object` |

---

### 2.5 `knowledge_conversation_history`

Searches the conversation history corpus specifically. This is the same FAISS index queried via `knowledge_search` with `sources: ["conversation"]` — but with additional date-range and agent filtering that conversation-specific consumers need.

```json
{
  "name": "knowledge_conversation_history",
  "description": "Search the conversation history corpus for past arguments, decisions, and reasoning patterns.",
  "parameters": {
    "query": "string — what to search for",
    "date_from": "string (optional) — ISO 8601 date, e.g. '2026-01-01'",
    "date_to": "string (optional) — ISO 8601 date",
    "agent_id": "string (optional) — filter to a specific agent's memory files",
    "sections": "string[] (optional) — filter to specific memory sections: ['Reasoning', 'Decisions made', 'Goal', 'Key facts']",
    "limit": "integer (optional) — max results (default: 5)"
  },
  "returns": {
    "results": "ConversationResult[]"
  }
}
```

**`ConversationResult` schema:**
```json
{
  "chunk_id": "string",
  "agent_id": "string — which agent wrote this memory",
  "date": "string — YYYY-MM-DD",
  "section": "string — which ## section of the memory file",
  "text": "string — chunk content",
  "score": "float — RRF fusion score",
  "retrieval_tier": "DIRECT | ADJACENT | ABSENT"
}
```

```
Consumers: Epistemic Immune System (pattern matching against past arguments),
           Metacognitive Dashboard (mental model usage history),
           Temporal Intelligence (position extraction from past conversations),
           Oral History (longitudinal synthesis corpus)
Access: read-only
SLA: p95 < 400ms
Degradation: ABSENT tier if conversation corpus not yet indexed (Phase 2 foundation not built)
```

---

## 3. Read-Only Contract

All contracts above are **read-only** for consumers. The Knowledge Service is the sole writer to:
- FAISS HNSW index
- SQLite graph store (`graph.db`)
- Dirty-flag registry (`dirty.json`)
- Hook registry (`hooks.json`)

No consumer feature reads these files directly. All access is through the tool interfaces above.

**Why this matters:** Direct file reads would bypass the retrieval classification layer (DIRECT/ADJACENT/ABSENT), the staleness detection, and the circuit breaker logic. Consumers that read raw index files also become tightly coupled to the Knowledge Skill's internal storage format — making it impossible to change the storage layer without breaking every downstream feature.

---

## 4. Prompt Injection Layer Hierarchy

**Locked: 2026-03-25 (@backend sign-off)**

Multiple specs inject content into the agent's effective system prompt. This is the formal precedence order. No lower layer can override a higher one. Absent layers are omitted entirely — not null-padded.

| Layer | Content | Owner | Mechanism | Phase |
|-------|---------|-------|-----------|-------|
| **7** (deepest) | Constitutional epistemology | Gateway | Static SOUL baseline (Phase 1) → `polly.constitutional.layer` config key (Phase 2+) | 1 |
| **6** | Epistemic Immune System flags | Gateway | `polly.epistemic.flags` config key, runtime-updated by EIS service | 3 |
| **5** | Theme behavior | Gateway | `polly.ios.aestheticStance` config key | 1 |
| **4** | Plan context (swarm) | Gateway | §23.7 auto-injection | 2 |
| **3** | Group chat context header | Gateway | §22.5 auto-injection | 2 |
| **2** | Domain context hint | iOS client | Message augmentation (Phase 5) | 5 |
| **1** (closest to message) | Mental model framing + vault note | iOS client | `<framing>` block in message | 1 |

**Gateway owns Layers 3-7. iOS client owns Layers 1-2.**

**Invariants:**
- Layer 7 is always present. It cannot be absent.
- Layers 6, 4, 3 are absent until their respective phases ship.
- Layer 5 is present from Phase 1 (theme behavior), but omitted if the agent has no active theme.
- Layers 1-2 are client-side; the gateway never injects into these positions.

---

### ⚠️ @backend — Config Read Path (Layers 3-5)

*This section is the abstraction boundary @backend needs to review before this spec ships final.*

**How the gateway reads `polly.*` config keys at request time and injects them into Layers 3-7:**

Proposed mechanism:

```
Request arrives at gateway
    ↓
Gateway assembles system prompt in layer order (7 → 1)
    ↓
For each gateway-owned layer (3-7):
    if config key exists AND is non-empty:
        append layer content to system prompt
    else:
        skip layer entirely (no null padding)
    ↓
Pass assembled system prompt to agent
```

**Config key → layer mapping:**

| Layer | Config key | Format | Notes |
|-------|-----------|--------|-------|
| 7 | `polly.constitutional.layer` | Raw text block | Phase 2+; Phase 1 baked into SOUL |
| 6 | `polly.epistemic.flags` | JSON array of flag objects | Phase 3; EIS service writes, gateway reads |
| 5 | `polly.ios.aestheticStance` | Raw text block | Phase 1; written by iOS theme selection |
| 4 | `polly.swarm.plan_context` | Raw text block | Phase 2; written by swarm coordinator |
| 3 | `polly.group_chat.context_header` | Raw text block | Phase 2; written per-session by group chat feature |

**The question for @backend:** Is `config.patch` the right read mechanism here, or does the gateway need a dedicated prompt-assembly step that reads these keys fresh on each request? The concern is caching — if Layer 6 (Epistemic Immune System flags) is updated mid-session, the gateway needs to read the new value on the next request, not serve a cached version from session start.

Recommendation: treat Layers 5, 4, 3 as session-scoped (read once at session start, stable for the session). Treat Layers 7 and 6 as request-scoped (read on every request — constitutional layer must be immutable, EIS flags must be fresh). @backend to confirm this split is implementable in the current gateway config read path.

---

## 5. Shared Data Structures

Data structures used across multiple features. Defined here as the canonical source; individual feature specs reference this file.

### `NoteNode`
```json
{
  "note_id": "string — stable ID derived from vault path",
  "note_title": "string",
  "path": "string — filesystem path",
  "tags": "string[]",
  "domain": "string | null — Practice Layer domain label"
}
```

### `WikilinkEdge`
```json
{
  "from_id": "string — note_id of the linking note",
  "to_id": "string | null — note_id of the linked note; null if dangling",
  "to_title": "string — the [[link text]] as written",
  "link_text": "string — same as to_title (reserved for display alias support)"
}
```

### `Domain`
```json
{
  "id": "string",
  "name": "string",
  "color": "string — hex #RRGGBB",
  "keywords": "string[]",
  "note_count": "integer",
  "cluster_confirmed": "boolean"
}
```

### `StructuralPattern` (Phase 3)
```json
{
  "pattern_id": "string — e.g. 'feedback-loop', 'threshold-behavior', 'layered-dependency'",
  "label": "string — human-readable label",
  "description": "string — what this pattern looks like in a note/argument",
  "confidence": "float — LLM classification confidence (0.0–1.0)"
}
```

### `EpistemicFlag` (Phase 3)
```json
{
  "flag_id": "string — unique ID for this pattern instance",
  "pattern_type": "string — e.g. 'authority-adjacent-acceptance', 'urgency-bypass'",
  "trigger_text": "string — the argument structure that triggered this flag",
  "historical_instance": "string | null — chunk_id of a past conversation where this pattern appeared",
  "confidence": "float",
  "active_since": "ISO 8601 timestamp"
}
```

---

## 6. Consumer Dependency Declaration

Each Phase 3 feature that consumes Knowledge Service data must declare its dependencies. This table is the canonical record — prevents features from silently depending on data that isn't available.

| Consumer | Tools Used | Hooks Registered | Phase 2 dependency? |
|----------|-----------|-----------------|---------------------|
| Practice Layer | `knowledge_graph`, `knowledge_domains` | `domain-label-enricher` | Yes — graph layer |
| Structural Analogy | `knowledge_search`, `knowledge_graph`, `knowledge_domains` | `structural-pattern-tagger` | Yes — graph layer |
| Epistemic Immune System | `knowledge_conversation_history`, `knowledge_search` | `rhetorical-structure-extractor` | Yes — conversation adapter |
| Metacognitive Dashboard | `knowledge_conversation_history` | — | Yes — conversation adapter |
| Temporal Intelligence | `knowledge_conversation_history`, `knowledge_search` | — | Yes — conversation adapter |
| Oral History | `knowledge_conversation_history`, `knowledge_search` | — | Yes — conversation adapter |
| Conversation Architecture | `knowledge_domains` | — | No |
| Creative Constraint Engine | `knowledge_conversation_history` | — | Yes — conversation adapter |

**Phase 2 gate:** Features marked "Yes — graph layer" or "Yes — conversation adapter" cannot ship their Knowledge-dependent functionality until the Phase 2 graph layer and conversation adapter foundation are in place. This is expected and by design. These features are spec'd now; they build when the infrastructure is ready.

---

## 6.1 `knowledge_dedup` (Phase 2)

Checks for semantically similar content before a vault write. Called by the write pipeline before committing any note. Never blocks silently — always surfaces warnings for user resolution.

```json
{
  "name": "knowledge_dedup",
  "description": "Check if similar content already exists in the knowledge base. Returns similar notes and a recommendation. Called before every vault write.",
  "parameters": {
    "content": "string — note body (or first 500 chars for performance)",
    "threshold": "float — similarity threshold 0.0–1.0 (see recommended defaults below)"
  },
  "returns": {
    "similar_notes": "[{ title: string, path: string, similarity_score: float, preview: string }]",
    "recommendation": "\"create\" | \"merge\" | \"skip\""
  }
}
```

**Recommended thresholds by write origin (locked 2026-03-25, @backend):**

| Origin | Default Threshold |
|--------|-----------------|
| `quick-capture` | 0.85 |
| `share-extension` | 0.85 |
| `promotion` | 0.80 |
| `conversation-save` | 0.75 |
| `write-back` | 0.70 (matches `core/notes_dedup.py` default) |

```
Consumers: write pipeline (all Phase 2+ write paths)
Access: read-only (does not write anything)
Phase: 2+
SLA: p95 < 200ms (500-char truncated input)
Degradation: if index unavailable → return recommendation: "create", similar_notes: [] — never block a write
```

---

## 6.2 `vault.write_complete` Event (Phase 1)

The gateway write path emits this event after every successful vault write, regardless of backend (Obsidian or Notion). The Knowledge Skill subscribes and triggers an incremental index update. This decouples indexing from the file watcher (which misses Notion writes and can lag on Obsidian).

```json
{
  "event": "vault.write_complete",
  "payload": {
    "path": "string — vault-relative path (Obsidian) or Notion page ID",
    "backend": "\"obsidian\" | \"notion\"",
    "operation": "\"create\" | \"update\" | \"delete\"",
    "metadata": {
      "source": "\"capture\" | \"agent\" | \"promotion\" | \"conversation\" | \"import\"",
      "domain": "string | null",
      "maturity": "string"
    }
  }
}
```

**Subscribers:**
- Knowledge Skill — incremental index update on every `create` or `update`
- Practice Layer (Phase 3) — engagement tracking on `create`

**Owner:** @backend — gateway write path emits this event. Knowledge Skill subscribes via internal event bus.

---

## 7. Open Questions

**Resolved:**
- Sidecar vs. multi-skill: single service model. (@backend 2026-03-25)
- Layer hierarchy precedence: locked. (@backend 2026-03-25)

**Pending @backend review:**
- **Config read path caching model** (§4 above): session-scoped vs. request-scoped per layer. Specifically: can the gateway gateway read `polly.epistemic.flags` (Layer 6) fresh on each request without performance impact? Or does this require a push model (EIS pushes to an in-memory cache the gateway reads)?

**Deferred:**
- Cross-feature write contracts — currently all consumers are read-only against the Knowledge Service. If Phase 4+ features need to write back to the corpus (e.g., user annotations, agent-generated notes), write contracts will be needed. Out of scope for now.
- Multi-user/federated scenarios — see `FEDERATED_COLLABORATION.md`. All contracts above assume single-user, single-gateway deployment.
