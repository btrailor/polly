# Proposal: Open-Source Tool Integration Research

**Change:** `oss-tool-integration-research`  
**Phase/Tier:** Cross-cutting — informs Core Framework Refinement, Phase 12a (Knowledge Graph), Phase 24 (Orchestrator), and future RAG/routing work  
**Scope:** Backend (primary), Frontend (secondary — where tools affect UI patterns)  
**Date:** February 2026

---

## What

Evaluate open-source tools across 7 categories against Polly's subsystems, determine integration approach (code incorporation vs module vs API), rate effort and license compatibility, and produce actionable integration recommendations.

## Why

Polly's roadmap includes several planned-but-not-started components:
- **Provider Registry** — could leverage LiteLLM's unified 100+ provider interface
- **Knowledge Graph (Phase 12a/12b)** — could use Mem0's graph memory or LlamaIndex's KG capabilities
- **Query Decomposition + Split Routing + Synthesis** — could adopt existing orchestration patterns
- **Pattern → Routing** — could use Mem0's adaptive memory for routing decisions
- **PIL Expansion** — compression tools could reduce token costs
- **Orchestrator (Phase 24)** — multi-agent frameworks exist (CrewAI)
- **RAG Optimization** — rerankers and advanced retrieval pipelines are available off-the-shelf

Rather than building everything from scratch, incorporating mature open-source tools can accelerate delivery by 40–60% on some components while maintaining Polly's edge-native, privacy-first architecture.

## Scope

| Category | Polly Subsystems Affected | Backend/Frontend |
|----------|--------------------------|-----------------|
| Memory/Knowledge | KnowledgeWriter, patterns, mental models | Backend |
| Document Infrastructure | Notes, templates, Obsidian integration | Both |
| AI Routing/Orchestration | Router v2, provider registry, personas | Backend |
| RAG/Search | Hybrid search, ChromaDB, BM25, domain routing | Backend |
| Compression | Compressor, pattern compression | Backend |
| Local AI | Ollama integration, local model routing | Backend |
| Workflow/Automation | Orchestrator mode, persona collaboration | Both |

## Tools Evaluated

1. **Mem0** — Universal memory layer (Apache-2.0, ~47k stars)
2. **LiteLLM** — Unified LLM API proxy (MIT, ~18k stars)
3. **AFFiNE** — Local-first knowledge workspace (MIT, ~43k stars)
4. **Haystack** — RAG pipeline framework (Apache-2.0, ~18k stars)
5. **LlamaIndex** — RAG + knowledge graph framework (MIT, ~38k stars)
6. **LLMLingua** — Prompt compression (MIT, Microsoft Research)
7. **CrewAI** — Multi-agent orchestration (MIT, ~25k stars)
8. **n8n** — Workflow automation (Sustainable Use License, ~52k stars)
9. **Open WebUI** — Self-hosted LLM interface (MIT, ~60k stars)
10. **Langfuse** — LLM observability (MIT, ~8k stars)
11. **A-MEM** — Zettelkasten-inspired agentic memory (Research, ~3k stars)
12. **CopilotKit** — AI copilot framework (MIT, ~28k stars)
13. **Ollama** — Local LLM inference (MIT, ~120k stars)

## Status

✅ **Research complete.** All 13 tools evaluated. Findings integrated into Core Framework Refinement:
- **design.md** → Full evaluation matrix, compatibility scores, architecture impact
- **tasks.md** → Original OSS task breakdown (reference)
- **Unified plan** → [core-framework-refinement/tasks.md](../core-framework-refinement/tasks.md) merges OSS tasks with existing core refinement tasks into a 6-wave execution plan

## Success Criteria

- [x] Each tool rated against all 7 categories with clear scores
- [x] Integration approach determined (code incorporation / module / API)
- [x] Effort estimates provided (Low / Medium / High + time)
- [x] License compatibility verified for each tool
- [x] Top recommendations mapped to Polly roadmap items
- [x] Design document with architecture impact analysis
- [x] Tasks document with ordered implementation steps
- [x] Unified with Core Framework Refinement — no conflicts
