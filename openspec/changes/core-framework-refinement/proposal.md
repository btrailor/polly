# Core Framework Refinement — Proposal

**Tier:** 1 (Core Intelligence) + 3 (Polish & Autonomy)  
**Scope:** Backend + Frontend  
**Status:** In progress — Knowledge Writing complete; Intelligent Routing pipeline pending  
**Created:** February 2026

---

## What We're Doing

Refining and integrating the core components that make Polly unique as a progressively autonomous personal AI system. This is not a single phase but a cross-cutting refinement effort that touches:

1. **Provider Management** — Per-provider enable/disable toggles, health tracking, OpenRouter gateway
2. **Intelligent Routing ("Polly" mode)** — Query decomposition → split routing → synthesis pipeline
3. **Knowledge Writing** — Chat-to-KB note creation (AI-suggested + user-triggered), filling RAG gaps
4. **Progressive Autonomy** — Feedback loop: KB growth → more local routing → fewer cloud tokens
5. **Pattern Learning → Routing Integration** — Use learned patterns to inform decomposition
6. **PIL Compression Expansion** — Extend PIL to cover patterns, knowledge summaries, routing decisions
7. **SKILL ↔ Mental Model Bridge** — Skills activate mental models, PIL-compressed in context
8. **Orchestrator Persona** — Multi-persona coordination for complex tasks
9. **BookLore Library Integration** — Ebook catalogue integrated into RAG
10. **RAG Optimization** — Context window tuning for local models, incremental indexing

## Why

Polly's unique value proposition is **progressive autonomy**: the more you use it, the less you need cloud providers. This requires the above components to work together as a coherent system, not as disconnected features.

## What's Done So Far

- ✅ Knowledge Writing system (full stack: `core/knowledge_writer.py`, settings API, frontend)
- ✅ Autonomy Metrics tracking (`core/autonomy_metrics.py`, SQLite, dashboard API)
- ✅ AI Features settings (config, UI toggles, backend)
- ✅ Incremental RAG indexing (`rag.py` → `index_single_document()`)
- ✅ Scribe standalone enrich for KnowledgeWriter
- ✅ Detailed designs for Provider Registry, "Polly" mode, OpenRouter gateway

## What's Next

### Wave 1 — In Progress
- **LLMLingua Compression Integration** (Task 13) — Adding algorithmic compression for RAG context
- LiteLLM Provider Adapter (Task 12)

### Wave 2+
- Provider Registry (`core/provider_registry.py`)
- "Polly" mode in model selector UI
- OpenRouter provider adapter
- Query Decomposition Engine
- Split Routing + Synthesis Layer
- Pattern → Routing integration
- PIL expansion
- SKILL ↔ Mental Model bridge
- Orchestrator coordination
- BookLore integration
- RAG optimization for local models

## Reference

- Plan file: `.cursor/plans/polly_core_framework_refinement_*.plan.md`
- Existing phases: 2a (RAG), 2b (Compression), 11 (Routing), 13a (Patterns), 14 (Mental Models), 16c (AI Notes)
