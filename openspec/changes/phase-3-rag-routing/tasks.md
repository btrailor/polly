# Phase 3: RAG-Integrated Routing

**Status:** 💡 Specced  
**Gate:** Phase 2 Knowledge Skill complete + Phase 2 model routing complete  
**Spec source:** `MODEL_ROUTING_SPEC.md` §6, §7, §8 Phase 3

## Goal

Routing becomes knowledge-aware. A DIRECT vault hit means a cheap local model is adequate. A missing knowledge match means escalate to frontier. Cost drops significantly for vault-populated use.

## Tasks

### RAGEvaluator
- [ ] `RAGEvaluator`: call `knowledge_search` on every message, read `retrieval_tier` + `top_score` + `domain`
- [ ] DIRECT (≥0.75) → recommend Tier 0, augment with top 2–3 chunks
- [ ] ADJACENT (0.45–0.75) → recommend Tier 1, augment with top chunk + "related" note
- [ ] ABSENT (<0.45) → no augmentation, fallthrough to ComplexityEvaluator
- [ ] Add RAGEvaluator to Resolver priority (between ConstraintEvaluator and ComplexityEvaluator)

### Augmentation Decision
- [ ] Tier 0 model selected → send 300-word summary (fits local context window)
- [ ] Tier 1+ model selected → send summary + full source
- [ ] Routing engine + augmentation layer coordinate: model tier determines augmentation depth
- [ ] RAG results injected at Layer 2 in 7-layer hierarchy (see `KNOWLEDGE_SERVICE_CONTRACTS.md §3`)

### Domain Routing
- [ ] Domain detection from RAG `domain` field
- [ ] `domainModels` map in RoutingProfile: detected domain → preferred model (e.g., `code → codestral:latest`)
- [ ] Domain routing applied after RAGEvaluator, before ComplexityEvaluator

### Budget Tracking (SQLite)
- [ ] **Migration:** one-time automatic migration of MMKV budget data to SQLite on first Phase 3 launch; MMKV budget keys deprecated after migration; migration script idempotent (safe to run twice)
- [ ] Migrate MMKV budget tracking to SQLite `~/.polly/routing_decisions.db`
- [ ] Daily reset via cron job
- [ ] Budget warning events → iOS toast notification
- [ ] Usage view: RAG hit rate card ("X% of queries answered locally")

### Feedback Loop
- [ ] Log `userSatisfactionSignal` per routing decision:
  - `regenerated` — user hit regenerate
  - `continued` — user continued conversation
  - `switched_model` — user manually changed model after response
- [ ] Frequency table: `query_type × model_tier → regeneration_rate`
- [ ] **Cold-start strategy:** hold default tier config until ≥50 data points accumulated per query type; show "learning your usage" indicator in routing debug view; prevent single-session data from triggering tier bumps
- [ ] If regeneration_rate > 30% for a type AND ≥50 data points → bump default tier for that type

## Done when
RAG hit → local model used. Augmentation depth tied to selected model. Domain routing active. Budget tracking in SQLite. Feedback loop logging.

---

## Additions from DYNAMIC_PROVIDER_POOL_ROUTING.md

### RAGEvaluator × Provider Pool Integration

The RAGEvaluator constrains the pool based on retrieval confidence. This is where the largest cost savings come — a DIRECT hit means the answer is already retrieved; model's job is synthesis, not knowledge.

| Retrieval Tier | Pool Filter | Augmentation |
|---------------|------------|-------------|
| DIRECT (≥0.75) | Prefer Tier 0–1. Allow Tier 2 only if Tier 0–1 pool empty. Block Tier 3 unless pinned. | Top 2–3 chunks; 300-word summary for local, full source for cloud |
| ADJACENT (0.45–0.75) | Prefer Tier 1–2. Allow Tier 0 if maxComplexity ≥ medium. Allow Tier 3 if complexity heavy. | Top chunk + "related" note reference |
| ABSENT (<0.45) | All tiers allowed. Free cloud first; paid only if complexity heavy. | None — no vault knowledge |

**LLM-selection fallback** (from CLAUDE_CODE_ARCHITECTURE_INSIGHTS.md §3.2): when FAISS returns all results below ABSENT threshold (<0.45), fall back to LLM-based note selection (send note frontmatter/titles to Sonnet, select top 5 by semantic understanding). FAISS is primary; this is a complement for small vaults.

### Privacy-Sensitive Routing (RAGEvaluator → PoolEvaluator signal)

- [ ] `RAGEvaluatorOutput` extended with `privacySensitive: boolean` — true if retrieved chunks contain personal/sensitive vault content
- [ ] When `privacySensitive: true`, PoolEvaluator filters to `dataPolicy: 'local' | 'no-training'` only — personal vault content never routes to training-enabled providers (Gemini free, Mistral Experiment, DeepSeek, xAI)
- [ ] This runs automatically — no user action needed

### DomainEvaluator (new evaluator, extracted here from §14 of pool routing doc)

- [ ] Detects domain from RAG `domain` field (authoritative) or keyword heuristics fallback
- [ ] Promotes domain-specialist models to top of pool within their tier, per user-configured `DomainRoutingPreferences`
- [ ] Default domain routing profiles (all configurable by user in Settings → Models → Domain Routing):

| Domain | Local | Free Cloud | Paid Cloud |
|--------|-------|-----------|-----------|
| Sigils (code) | codestral:latest | Kimi K2.5, Qwen3 Coder 480B | Claude Sonnet 4.6 |
| Signals (audio) | llama3.1:8b | MiniMax M2.5, GLM 4.7 | Claude Opus 4.6 |
| Scrolls (writing) | llama3.1:8b | MiniMax M2.5, Trinity Large | Claude Opus 4.6 |
| Glyphs (visual) | llama3.2:3b | MiniMax M2.5 | Claude Sonnet 4.6 |
| Grids (systems) | llama3.1:8b | DeepSeek R1, Kimi K2.5 | Claude Opus 4.6 |

- [ ] DomainEvaluator position in chain: after ComplexityEvaluator, before Resolver
- [ ] Agent declared domain specialty (Layer 2 per-agent override) bypasses domain detection — forces DomainEvaluator to treat query as belonging to that domain

### Phase 3 Provider Pool Tasks

- [ ] RAGEvaluator `privacySensitive` flag wired to PoolEvaluator privacy filter
- [ ] RAG tier → pool filter logic implemented (DIRECT/ADJACENT/ABSENT → candidate promotion/demotion)
- [ ] DomainEvaluator implemented and inserted in chain
- [ ] Default domain routing profiles seeded in gateway config on first Phase 3 launch
- [ ] Usage analytics: "X% of queries answered free" card in Usage view
- [ ] Feedback loop extended: track `retrieval_tier × model_tier → regeneration_rate` (join with existing `query_type × model_tier` tracking)
