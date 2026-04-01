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

## Memory Architecture Notes

**Two-tier pattern (validated):** USER.md (always-loaded) + Knowledge Skill (per-query) is the correct architecture. This matches production patterns in comparable systems.

**USER.md cap guidance:** Current soft cap is 500 words (~50 lines). Production data suggests a hard cap of ~150 lines / 25KB is appropriate headroom before token budget pressure. Consider raising the soft cap or converting to a hard cap at ~150 lines. Do not change without @backend review of context window budget model.

**LLM-selection fallback:** For low-confidence FAISS results (all results below ABSENT threshold), an LLM-based selection fallback (send note frontmatter/titles to Sonnet, select top 5) may outperform vector search for small vaults. FAISS remains primary. See `phase-2-knowledge-skill` tasks for implementation details.

**Session-end extraction pattern:** Memory extraction at session end MUST use a forked agent (copy of session sharing prompt cache), not a separate LLM call with conversation pasted as input. The fork preserves SOUL, mental models, and domain context — all relevant to what facts are worth extracting. See `phase-2-knowledge-skill` tasks and `KNOWLEDGE_WRITE_PATH.md §7`.
