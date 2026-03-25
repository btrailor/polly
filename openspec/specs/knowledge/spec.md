# Knowledge — Current State

*Contracts are locked. Implementation ships in `phase-2-knowledge-skill` change.*

## Service Contracts (locked)

Full contracts in `KNOWLEDGE_SERVICE_CONTRACTS.md`. Summary:

**Single service model.** One FAISS index. All Phase 3 features consume via tool interfaces — none maintain their own index.

**5 tool interfaces:**
- `knowledge_search` — hybrid retrieval (dense + sparse + RRF)
- `knowledge_graph` — wikilink traversal
- `knowledge_domains` — domain taxonomy
- `knowledge_register_hook` — Phase 3 hook registration
- `knowledge_conversation_history` — conversation corpus search

**Retrieval classification:** Every result carries DIRECT (≥0.75) / ADJACENT (0.45–0.75) / ABSENT (<0.45). Agents must communicate tier to user.

## Prompt Injection Layer Hierarchy (locked 2026-03-25)

| Layer | Content | Owner |
|-------|---------|-------|
| 7 (deepest) | Constitutional epistemology | Gateway |
| 6 | EIS flags (Phase 3) | Gateway — `polly.epistemic.flags` |
| 5 | Theme behavior | Gateway — `polly.ios.aestheticStance` |
| 4 | Plan context (Phase 2+) | Gateway |
| 3 | Group chat header (Phase 2+) | Gateway |
| 2 | Domain context hint | iOS client |
| 1 (closest) | Mental model framing + vault note | iOS client |

No lower layer overrides a higher one. Absent layers are omitted entirely.

## Open Item

@backend: `KNOWLEDGE_SERVICE_CONTRACTS.md §4` — confirm session-scoped vs. request-scoped read for Layer 6 (EIS flags) before Phase 3.
