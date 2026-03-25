# Knowledge — Spec Domain

The Knowledge domain covers everything related to the user's personal knowledge base — indexing, retrieval, graph traversal, and the service contracts that allow Phase 3 cognitive features to consume knowledge data without duplicating infrastructure.

## Specs in this domain

| File | What it covers | Status |
|------|---------------|--------|
| `knowledge-skill.md` | Full Knowledge Skill spec: Obsidian + BookLore + conversation history adapters, FAISS/HNSW index, hybrid retrieval (dense+sparse+RRF), graph layer (SQLite), index hooks extension point, DIRECT/ADJACENT/ABSENT classification, degradation paths, domain taxonomy reconciliation | Active — Phase 2 ready |
| `service-contracts.md` | Cross-feature data sharing contracts: 5 tool interfaces, prompt injection layer hierarchy (7 layers, locked), shared data structures, consumer dependency table | Active — @backend §4 review pending |
| `structural-analogy.md` | Structural pattern retrieval — finds notes with matching relational structure across domains. LLM classification at index time. Phase 3. | Planned |
| `dream-logic.md` | Structured misretrieval — FAISS distance band 0.5–0.7. Agent behavior contract: surface collision, do not explain. Phase 3. | Planned |
| `practice-layer.md` | Domain taxonomy discovery from vault wikilink graph. Phase 3. | Planned |
| `temporal-intelligence.md` | Time-aware retrieval — extracts positions from conversation history, surfaces relevant past reasoning at decision points. Phase 3. | Planned |
| `oral-history.md` | Longitudinal synthesis from conversation history corpus. Phase 3. | Planned |
| `cognitive-artifact.md` | Export format for cognitive artifacts (vault, agents, memory). Versioned manifest.json schema. | Active — @backend manifest.json Phase 1 |

## Key decisions locked

- **Single service model** — Knowledge Skill owns the FAISS index. All Phase 3 features are consumers, not independent skills. (2026-03-25, @backend)
- **Prompt injection layer hierarchy** — 7 layers, gateway owns 3-7, iOS client owns 1-2. No lower layer overrides a higher one. (2026-03-25, @backend)
- **DIRECT/ADJACENT/ABSENT** — Retrieval tier must be communicated to the user. Agents asserting from ADJACENT without qualification is epistemic dishonesty.
- **Index hooks extension point** — Phase 2 ships zero hooks. Phase 3 features register hooks rather than requiring full re-index.
- **Conversation history adapter** — Memory files indexed from Phase 2. `## Reasoning` section in agent memory writes provides inferential content.

## Cross-domain dependencies

- Conversation history adapter → Agent SOUL Baseline `## Reasoning` section (`agent-system/agent-templates.md`)
- `allowed_modes` tool gating → Agent manifest schema (`agent-system/agent-templates.md`)
- Domain taxonomy seeds → iOS MMKV `polly.domains` (`ios-app/ios-spec.md`)
- Layer 5 theme injection → iOS theme selection (`ios-app/ios-spec.md`)
- Layer 6 EIS flags → Epistemic Immune System (`cognitive-features/epistemic-immune-system.md`)
- Phase 3 hooks → Structural Analogy, Practice Layer, EIS (`cognitive-features/`)

## Open items

- @backend: §4 of `service-contracts.md` — config read path caching model for Layer 6 (EIS flags). Session-scoped vs. request-scoped. Recommendation in file; needs confirmation.
