# Design: Open-Source Tool Integration Research

**Change:** `oss-tool-integration-research`  
**Last Updated:** February 2026

---

## 1. Tool Evaluation Matrix

### Category 1: Memory/Knowledge

#### Mem0 — Universal Memory Layer
- **GitHub:** mem0ai/mem0 | **Stars:** ~47k | **License:** Apache-2.0 | **Language:** Python 66%, TypeScript 21%
- **Architecture:** Hybrid multi-store parallel — vector store (ChromaDB default) + graph DB (Neo4j/Memgraph/Neptune/Kuzu) + KV store
- **Key Features:**
  - Multi-level memory: User, Session, Agent state
  - Graph memory with entity/relationship nodes
  - Reranker-enhanced search with metadata filtering
  - Custom fact extraction and memory update prompts
  - Async operations, multimodal support
  - Factory architecture with pluggable providers
- **Performance:** +26% accuracy vs OpenAI Memory, 91% faster, 90% token reduction
- **Polly Subsystem Alignment:**
  - **KnowledgeWriter** ⭐⭐⭐⭐⭐ — Direct fit. Mem0's `add()` / `search()` / `update()` map to Polly's knowledge writing pipeline. Graph memory enables relationship tracking between knowledge items.
  - **Patterns** ⭐⭐⭐⭐ — Graph-based entity relationships can store and query pattern associations. Memory evolution supports pattern decay/reinforcement.
  - **Personas** ⭐⭐⭐⭐ — Multi-level memory (user/session/agent) enables per-persona context. Session state maps to persona mode state.
  - **RAG** ⭐⭐⭐⭐ — Reranker-enhanced search improves retrieval quality. Complements existing ChromaDB setup.
  - **Routing** ⭐⭐⭐ — Graph relationships can inform routing decisions, but Mem0 doesn't provide routing logic itself.
  - **PIL** ⭐⭐⭐ — Memory evolution + custom prompts support progressive learning, but requires adapter layer.
  - **Compression** ⭐⭐⭐ — Token reduction via selective memory retrieval (implicit, not explicit compression).
- **Integration Approach:** **Module (pip install)** — Use Mem0's Python SDK as internal module. Wrap with `core/memory/mem0_adapter.py` to interface with existing `KnowledgeWriter` and `PatternLearner`.
- **Effort:** Medium (2–3 weeks) — Requires configuring vector store, graph DB, and LLM providers; writing adapter layer; migrating existing patterns.json to graph format.
- **License:** ✅ Apache-2.0 — Permissive. Requires attribution but allows modification and commercial use. Compatible with Polly.

#### A-MEM — Agentic Memory (Zettelkasten-inspired)
- **GitHub:** agentic-memory | **License:** Research/MIT | **Language:** Python
- **Architecture:** ChromaDB + all-MiniLM-L6-v2 embeddings, dynamic knowledge network
- **Key Features:**
  - Zettelkasten-inspired linking (notes connect semantically)
  - Active memory evolution — new info triggers retroactive updates
  - Semantic similarity + temporal + categorical associations
  - 10X token efficiency improvement
- **Polly Subsystem Alignment:**
  - **KnowledgeWriter** ⭐⭐⭐⭐ — Zettelkasten model aligns with Polly's note/knowledge architecture
  - **Patterns** ⭐⭐⭐⭐⭐ — Memory evolution is essentially pattern learning
  - **Mental Models** ⭐⭐⭐⭐ — Semantic linking maps directly to mental model connections
- **Integration Approach:** **Code incorporation** — Extract core algorithms (memory evolution, semantic linking) into Polly's pattern learner.
- **Effort:** Medium (2 weeks) — Less mature than Mem0; requires more adaptation work.
- **License:** ⚠️ Verify — Research project; confirm production-use licensing.

---

### Category 2: Document Infrastructure

#### AFFiNE — Local-First Knowledge Workspace
- **GitHub:** toeverything/AFFiNE | **Stars:** ~43k | **License:** MIT (core) | **Language:** TypeScript
- **Architecture:** Block-based editor, local-first with optional cloud sync, whiteboard + docs unified
- **Key Features:**
  - Block editor (Notion-like) with whiteboard canvas
  - Local-first, privacy-focused
  - Markdown import/export
  - Real-time collaboration
  - CRDT-based data model (yjs)
- **Polly Subsystem Alignment:**
  - **Notes/Knowledge Writing** ⭐⭐ — AFFiNE is a full workspace app; overkill for Polly's note system. Polly already has CodeMirror 6 + markdown notes.
  - **Document Infrastructure** ⭐⭐⭐ — Block model concepts (CRDT, structured blocks) could enhance Polly's note system long-term.
  - **Templates** ⭐⭐ — AFFiNE's template system is UI-focused, not AI-focused.
- **Integration Approach:** **Reference only** — AFFiNE is a standalone app, not a library. Study block model architecture for inspiration, but don't embed.
- **Effort:** N/A (reference study)
- **License:** ✅ MIT — Permissive. But full app integration not practical.
- **Verdict:** 🟡 **Low priority.** Polly's existing CodeMirror 6 + markdown pipeline is sufficient. AFFiNE's block model is interesting for Phase 17 (Monaco) but not actionable now.

---

### Category 3: AI Routing/Orchestration

#### LiteLLM — Unified LLM API Proxy
- **GitHub:** BerriAI/litellm | **Stars:** ~18k | **License:** MIT | **Language:** Python
- **Architecture:** Drop-in OpenAI SDK replacement; proxy server with routing, fallback, budget
- **Key Features:**
  - Unified API for 100+ LLM providers (OpenAI, Anthropic, Gemini, Mistral, Ollama, etc.)
  - Proxy server with load balancing, fallback chains, rate limiting
  - Budget management (daily/monthly spend limits, cost tracking per model)
  - Caching, logging, and streaming support
  - Model-specific parameter mapping
- **Polly Subsystem Alignment:**
  - **Router v2** ⭐⭐⭐⭐⭐ — Direct replacement for planned Provider Registry. Fallback chains = Polly's routing tiers. Budget management = Polly's BudgetManager.
  - **Provider Registry** ⭐⭐⭐⭐⭐ — LiteLLM IS a provider registry. Per-provider enable/disable, health tracking, model listing — all built-in.
  - **OpenRouter Gateway** ⭐⭐⭐⭐⭐ — LiteLLM supports OpenRouter as a provider. Replaces need for custom `openrouter_provider.py`.
  - **Budget Manager** ⭐⭐⭐⭐ — LiteLLM has spend tracking, but Polly's `BudgetManager` also tracks conversation-level costs. Need adapter.
  - **Personas** ⭐⭐⭐ — Model selection per persona mode can use LiteLLM routing. Config-driven.
  - **RAG** ⭐⭐ — LiteLLM doesn't do retrieval, but its unified API simplifies embedding calls across providers.
  - **Compression** ⭐⭐ — No direct compression, but cost tracking helps measure compression savings.
- **Integration Approach:** **Module (pip install) + adapter** — Replace Polly's multi-provider LLM calling code with `litellm.completion()`. Wrap with `core/providers/litellm_adapter.py` that integrates with existing routing logic and BudgetManager.
- **Effort:** Low-Medium (1–2 weeks) — LiteLLM is a drop-in; main work is migrating provider configs and integrating with existing Router v2 logic.
- **License:** ✅ MIT — Maximally permissive. No restrictions.
- **Verdict:** 🟢 **HIGH PRIORITY.** Single biggest acceleration for Polly's planned Provider Registry, OpenRouter, and routing pipeline. Replaces 3 planned custom components.

#### CrewAI — Multi-Agent Orchestration
- **GitHub:** crewAIInc/crewAI | **Stars:** ~25k | **License:** MIT | **Language:** Python
- **Architecture:** Role-based agent framework with task delegation, tool use, memory
- **Key Features:**
  - Define agents with roles, goals, backstories
  - Sequential and parallel task execution
  - Built-in memory (short-term, long-term, entity)
  - Tool integration, delegation between agents
  - Process types: sequential, hierarchical
- **Polly Subsystem Alignment:**
  - **Orchestrator Mode (Phase 24)** ⭐⭐⭐⭐ — CrewAI's agent model maps to Polly's personas (Architect=agent, Scribe=agent, Professor=agent).
  - **Personas** ⭐⭐⭐⭐ — Role/goal/backstory maps directly to persona definitions. Mode switching ≈ task reassignment.
  - **Routing** ⭐⭐⭐ — Task delegation can inform routing decisions, but CrewAI is higher-level than Polly's confidence-based routing.
  - **Knowledge Writing** ⭐⭐⭐ — Multi-agent collaboration could enable Scribe+Architect workflows for knowledge creation.
- **Integration Approach:** **Module (pip install) + custom agents** — Define Polly personas as CrewAI agents for Phase 24 orchestrator mode. Keep existing persona system for non-orchestrated use.
- **Effort:** Medium (3–4 weeks) — Need to map persona skills to CrewAI tools, define task workflows, integrate with existing persona lifecycle.
- **License:** ✅ MIT — Fully permissive.
- **Verdict:** 🟡 **Medium priority.** Valuable for Phase 24 (Orchestrator) but that phase is blocked by Phase 23.5 (Security). Park for now, revisit when Phase 24 starts.

#### CopilotKit — AI Copilot Framework
- **GitHub:** CopilotKit/CopilotKit | **Stars:** ~28k | **License:** MIT | **Language:** TypeScript/JavaScript
- **Architecture:** React-based copilot components with agent support
- **Key Features:** Chat components, agent platform, CoAgents for LangGraph integration
- **Polly Alignment:** ⭐⭐ — React-based; Polly doesn't use React. The agent orchestration patterns are interesting but CopilotKit is more of a frontend framework.
- **Integration Approach:** **Reference only** — Study patterns; don't embed (React dependency).
- **License:** ✅ MIT
- **Verdict:** 🔴 **Skip.** React dependency conflicts with Polly's vanilla JS Electron app.

---

### Category 4: RAG/Search

#### Haystack — RAG Pipeline Framework
- **GitHub:** deepset-ai/haystack | **Stars:** ~18k | **License:** Apache-2.0 | **Language:** Python
- **Architecture:** Component-based pipeline builder (generators, retrievers, readers, preprocessors)
- **Key Features:**
  - Modular pipeline construction (YAML or Python)
  - Document stores: Chroma, Elasticsearch, Pinecone, Weaviate, etc.
  - Retrievers: BM25, embedding, hybrid
  - Pre-built RAG, QA, and summarization pipelines
  - Evaluation framework
- **Polly Subsystem Alignment:**
  - **RAG** ⭐⭐⭐⭐ — Haystack's hybrid retrieval (BM25 + embedding) mirrors Polly's existing approach. Pipeline abstraction could clean up Polly's RAG code.
  - **Domain Routing** ⭐⭐⭐ — Metadata filtering and routing by document store
  - **Knowledge Writing** ⭐⭐⭐ — Document preprocessing/chunking pipelines
  - **Query Decomposition** ⭐⭐⭐⭐ — Haystack has query expansion and decomposition components
- **Integration Approach:** **Module (selective components)** — Don't adopt full Haystack; cherry-pick retriever components and pipeline patterns.
- **Effort:** Medium (2–3 weeks) — Polly already has working RAG; migration is optional. Value is in query decomposition and evaluation.
- **License:** ✅ Apache-2.0
- **Verdict:** 🟡 **Medium priority.** Useful for Query Decomposition component (planned but not started). Don't replace working RAG.

#### LlamaIndex — RAG + Knowledge Graph Framework
- **GitHub:** run-llama/llama_index | **Stars:** ~38k | **License:** MIT | **Language:** Python
- **Architecture:** Data framework for LLM applications with index types, query engines, agents
- **Key Features:**
  - Multiple index types: vector, keyword, tree, knowledge graph
  - Knowledge graph index with entity extraction
  - Query engines with response synthesis
  - Data connectors (100+ sources)
  - Agent framework with tool use
- **Polly Subsystem Alignment:**
  - **Knowledge Graph (Phase 12a)** ⭐⭐⭐⭐⭐ — LlamaIndex's KG index is exactly what Phase 12a needs. Entity extraction, triple storage, graph querying.
  - **RAG** ⭐⭐⭐⭐ — Multiple index types provide flexibility Polly doesn't have today.
  - **Query Decomposition** ⭐⭐⭐⭐⭐ — Sub-question query engine decomposes complex queries into sub-queries routed to different indices.
  - **Routing** ⭐⭐⭐⭐ — Router query engine selects best index/retriever per query.
  - **Knowledge Writing** ⭐⭐⭐ — Data connectors can ingest from many sources.
  - **Synthesis** ⭐⭐⭐⭐ — Response synthesis across multiple retrievals (tree summarize, refine, etc.).
- **Integration Approach:** **Module (selective)** — Use LlamaIndex's KG index for Phase 12a and sub-question engine for Query Decomposition. Don't replace existing ChromaDB/BM25 RAG.
- **Effort:** Medium-High (3–4 weeks) — Significant API surface; need to integrate with existing domain routing.
- **License:** ✅ MIT — Fully permissive.
- **Verdict:** 🟢 **HIGH PRIORITY for Phase 12a.** Best available tool for Knowledge Graph implementation. Sub-question engine directly addresses planned Query Decomposition.

---

### Category 5: Compression

#### LLMLingua / LLMLingua-2 — Prompt Compression
- **GitHub:** microsoft/LLMLingua | **Stars:** ~5k | **License:** MIT | **Language:** Python
- **Architecture:** Token-level and sentence-level prompt compression using small language models
- **Key Features:**
  - 2x–10x compression with minimal quality loss
  - LLMLingua-2: data-distillation-based compression (faster, better)
  - Works with any LLM (compress before sending)
  - Preserves key information via perplexity-based selection
  - Compatible with RAG pipelines (compress retrieved context)
- **Polly Subsystem Alignment:**
  - **Compression** ⭐⭐⭐⭐⭐ — Direct replacement/enhancement for `core/compression/compressor.py`. LLMLingua provides algorithmic compression Polly currently does via LLM summarization.
  - **RAG** ⭐⭐⭐⭐ — Compress retrieved context before sending to LLM, reducing token cost while maintaining quality.
  - **Routing** ⭐⭐⭐ — Compressed prompts reduce cost, enabling more aggressive cloud routing at lower cost.
  - **Budget** ⭐⭐⭐⭐ — Direct token savings = budget savings.
- **Integration Approach:** **Module (pip install)** — Drop-in compression step in Polly's RAG pipeline, between retrieval and LLM call.
- **Effort:** Low (1 week) — Well-documented, single-purpose library. Add as preprocessing step in `core/rag.py` and `core/compression/compressor.py`.
- **License:** ✅ MIT — Fully permissive.
- **Verdict:** 🟢 **HIGH PRIORITY.** Low effort, high impact. 2x–10x compression directly reduces API costs. Enhances existing compression system without replacing it.

---

### Category 6: Local AI

#### Ollama — Local LLM Inference (Already Integrated)
- **GitHub:** ollama/ollama | **Stars:** ~120k | **License:** MIT | **Language:** Go
- **Status:** Already integrated in Polly for local model routing.
- **Enhancement opportunity:** LiteLLM provides unified API that includes Ollama, simplifying Polly's provider code.
- **Verdict:** ✅ **Already in use.** LiteLLM integration would improve the Ollama connection.

#### Open WebUI — Self-Hosted LLM Interface
- **GitHub:** open-webui/open-webui | **Stars:** ~60k | **License:** MIT | **Language:** JavaScript/Python
- **Architecture:** Full-featured chat UI supporting Ollama and OpenAI-compatible APIs, RAG, web search
- **Polly Subsystem Alignment:**
  - **Local AI** ⭐⭐⭐ — Good reference for Ollama integration patterns, but Polly has its own UI.
  - **RAG** ⭐⭐ — Has RAG but Polly's is more sophisticated.
  - **Document Infrastructure** ⭐⭐ — File upload/management, but Polly has its own system.
- **Integration Approach:** **Reference only** — Study patterns for multi-model management UI.
- **Effort:** N/A
- **License:** ✅ MIT
- **Verdict:** 🔴 **Skip integration.** Polly has its own complete UI. Reference only for Ollama management patterns.

---

### Category 7: Workflow/Automation

#### n8n — Workflow Automation
- **GitHub:** n8n-io/n8n | **Stars:** ~52k | **License:** Sustainable Use License (fair-code, not OSI-approved) | **Language:** TypeScript
- **Architecture:** Node-based workflow builder, 400+ integrations, self-hosted
- **Key Features:** Visual workflow builder, 400+ app integrations, AI agent nodes, webhook triggers
- **Polly Subsystem Alignment:**
  - **Workflow/Automation** ⭐⭐⭐ — Could automate knowledge ingestion, scheduled tasks, external service integration.
  - **Integrations** ⭐⭐⭐ — n8n's connectors could extend Polly's GitHub/Calendar/etc. integrations.
- **Integration Approach:** **API** — Connect Polly as n8n node via REST API. Don't embed n8n.
- **Effort:** Medium (2 weeks) — Build n8n-compatible API endpoints + custom n8n node.
- **License:** ⚠️ **Sustainable Use License** — NOT OSI-approved. Restricts competing products. Polly is not a competing product, but license is unusual. Proceed with caution.
- **Verdict:** 🟡 **Low priority.** Interesting for power users but adds complexity. License concern. Consider for Tier 3+.

#### Langfuse — LLM Observability
- **GitHub:** langfuse/langfuse | **Stars:** ~8k | **License:** MIT (client SDK) | **Language:** Python/TypeScript
- **Architecture:** Tracing, evaluation, and monitoring for LLM applications
- **Key Features:**
  - Trace LLM calls (latency, tokens, cost)
  - Evaluation framework (LLM-as-judge, human eval)
  - Prompt management and versioning
  - Dashboard and analytics
- **Polly Subsystem Alignment:**
  - **Routing** ⭐⭐⭐⭐ — Tracing helps understand routing decisions and model performance.
  - **Budget** ⭐⭐⭐⭐ — Cost tracking per trace complements BudgetManager.
  - **Autonomy Metrics** ⭐⭐⭐⭐ — Evaluation framework can measure Polly's progressive autonomy.
- **Integration Approach:** **Module (pip install SDK)** — Add tracing decorators to LLM calls. Lightweight.
- **Effort:** Low (1 week) — SDK is decorator-based, minimal code change.
- **License:** ✅ MIT (client SDK). Server is AGPL but self-hosted server is optional (can use cloud or skip server).
- **Verdict:** 🟡 **Medium priority.** Valuable for development and debugging. Low effort. Consider after core integrations.

---

## 2. Master Compatibility Matrix

| Tool | Memory | Docs | Routing | RAG | Compress | Local AI | Workflow | License | Approach | Effort | Priority |
|------|--------|------|---------|-----|----------|----------|----------|---------|----------|--------|----------|
| **Mem0** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Apache-2.0 ✅ | Module | Med | 🟢 High |
| **LiteLLM** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | MIT ✅ | Module | Low-Med | 🟢 High |
| **LlamaIndex** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | MIT ✅ | Module | Med-High | 🟢 High |
| **LLMLingua** | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | MIT ✅ | Module | Low | 🟢 High |
| **Haystack** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | Apache-2.0 ✅ | Selective | Med | 🟡 Medium |
| **CrewAI** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | MIT ✅ | Module | Med | 🟡 Medium |
| **A-MEM** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⚠️ Verify | Code | Med | 🟡 Medium |
| **Langfuse** | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | MIT ✅ | Module | Low | 🟡 Medium |
| **AFFiNE** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | MIT ✅ | Reference | N/A | 🔴 Skip |
| **CopilotKit** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | MIT ✅ | Reference | N/A | 🔴 Skip |
| **Open WebUI** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | MIT ✅ | Reference | N/A | 🔴 Skip |
| **n8n** | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⚠️ SUL | API | Med | 🟡 Low |

---

## 3. Recommended Integration Architecture

### Tier 1 — Immediate (next 4–6 weeks)

```
┌─────────────────────────────────────────────────┐
│ Polly Backend (Python)                          │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ LiteLLM  │  │ LLMLingua│  │ Mem0 Memory  │  │
│  │ Adapter  │  │ Compress │  │ Adapter      │  │
│  │          │  │          │  │              │  │
│  │ Replaces:│  │ Enhances:│  │ Enhances:    │  │
│  │ Provider │  │ compressor│  │ KnowledgeWr  │  │
│  │ Registry │  │ .py      │  │ PatternLearn │  │
│  │ OpenRouter│  │          │  │              │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│       │              │              │            │
│  ┌────┴──────────────┴──────────────┴─────────┐ │
│  │        Existing Polly Infrastructure       │ │
│  │  Router v2 │ RAG │ Personas │ BudgetMgr   │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Tier 2 — Phase 12a+ (after security hardening)

```
┌─────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────┐  ┌───────────┐ │
│  │ LlamaIndex   │  │ CrewAI   │  │ Langfuse  │ │
│  │ KG Index     │  │ Agents   │  │ Tracing   │ │
│  │              │  │          │  │           │ │
│  │ Phase 12a:   │  │ Phase 24:│  │ Dev/Debug:│ │
│  │ Knowledge    │  │ Orchest- │  │ LLM call  │ │
│  │ Graph        │  │ rator    │  │ observ.   │ │
│  └──────────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 4. Impact on Existing Code

### Backend Impact

| Component | Change | Risk |
|-----------|--------|------|
| `core/rag.py` | Add LLMLingua compression step before LLM call; optional Mem0 search alongside existing | Low — additive |
| `core/compression/compressor.py` | Add LLMLingua as alternative compression strategy | Low — strategy pattern |
| `interfaces/server.py` | LLM calls route through LiteLLM adapter | Medium — central change |
| `core/pattern_learning.py` | Optional Mem0 graph backend for pattern storage | Low — adapter pattern |
| `core/knowledge_writer.py` | Mem0 `add()` for knowledge persistence | Low — additive |
| `core/providers/` (planned) | Replace with LiteLLM adapter | Low — planned component |
| `config/config.yaml` | Add `integrations:` section for tool configs | Low — additive |
| `config/approved_packages.yaml` | Add mem0ai, litellm, llmlingua | Low — config |
| `requirements.txt` | Add new dependencies | Low — versioned |

### Frontend Impact

| Component | Change | Risk |
|-----------|--------|------|
| Settings UI | Add integration toggle panels | Low — additive |
| Budget display | Update to show LiteLLM cost data | Low — display only |

---

## 5. Dependency Analysis

```
Tier 1 integrations (independent, can be done in parallel):
  ├── LiteLLM (no dependencies on other new tools)
  ├── LLMLingua (no dependencies)
  └── Mem0 (no dependencies; optional graph DB adds Neo4j dep)

Tier 2 integrations (sequential):
  ├── LlamaIndex KG → depends on Phase 23.5 completion
  ├── CrewAI → depends on Phase 24 start
  └── Langfuse → independent, but lower priority
```

---

## 6. License Summary

| Tool | License | OSI Approved | Commercial Use | Attribution | Copyleft |
|------|---------|-------------|----------------|-------------|----------|
| LiteLLM | MIT | ✅ | ✅ | Optional | No |
| LLMLingua | MIT | ✅ | ✅ | Optional | No |
| Mem0 | Apache-2.0 | ✅ | ✅ | Required | No |
| LlamaIndex | MIT | ✅ | ✅ | Optional | No |
| CrewAI | MIT | ✅ | ✅ | Optional | No |
| Langfuse SDK | MIT | ✅ | ✅ | Optional | No |
| Haystack | Apache-2.0 | ✅ | ✅ | Required | No |
| n8n | SUL | ❌ | ⚠️ Restricted | Required | No |

**All Tier 1 recommended tools have permissive, OSI-approved licenses.** No copyleft concerns.
