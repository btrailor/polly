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
- [ ] If regeneration_rate > 30% for a type → bump default tier for that type

## Done when
RAG hit → local model used. Augmentation depth tied to selected model. Domain routing active. Budget tracking in SQLite. Feedback loop logging.
