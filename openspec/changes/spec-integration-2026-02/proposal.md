# Spec Integration: Knowledge Management, DRM, BAD Canvas, Knowledge Quality

**Date:** February 2026
**Scope:** Backend + Frontend + New subsystems
**Tier/Phase:** Cross-cutting — touches Tiers 1–4+

---

## What We're Doing

Integrating five interconnected specification sets into Polly's OpenSpec:

1. **Knowledge Management & Capture** — PARA-inspired organization with maturity lifecycle (30-Ideas/20-Active/10-Archive), multi-modal capture system (voice, image, URL, code), POSE publishing pipeline (Ghost CMS, social, newsletter, RSS), structured review workflows, analytics and insights.

2. **Distributed Reasoning Mesh (DRM)** — Peer-to-peer protocol for distributing LLM reasoning tasks across local network nodes. mDNS discovery, capability-aware task routing, domain-specialized model distribution, result aggregation. Enables desktop + NAS collaboration, model specialization across machines, and mobile companion as thin DRM node.

3. **BAD Canvas** — Business Aware Design canvas system for structured project planning. Multi-zone triadic structure (Design Process, User Analysis, Competition, Business Model, Iteration Planning) with RAG-powered gap detection, cross-canvas pattern recognition, and persona integration. Built on existing RAG, domains, and personas.

4. **Knowledge Quality & Entity Graph (Anti-Slop)** — Entity extraction pipeline, graph-based knowledge organization with authority scoring, anti-slop mechanisms (connection thresholds, garden maintenance, augmented writing), smart summarization layers. Overhauls existing dedup engine (Phase 21) into a broader knowledge quality system. Directly extends Phase 12a (Knowledge Graph).

5. **Agent Swarms** — Configurable multi-agent workflow architecture. Formal agent interface specification (capability declarations, input/output schemas, execution contexts). Nexus coordination layer for composing agents into workflows. Progressive disclosure configuration (Level 1: templates, Level 2: modify, Level 3: custom agents, Level 4: code). Subsumes and expands Phase 24 (Orchestrator Mode). Integrates with DRM for distributed agent execution and Capability Broker for secure execution context access.

## Why

Polly's core intelligence (RAG, routing, personas, domains) is ~82% complete. These specs define the next layer: how knowledge flows in (capture), how it's organized (PARA + maturity + entity graph), how it maintains quality (anti-slop), how it's used for planning (canvas), how it's published (POSE), and how compute scales (DRM). Together they transform Polly from a powerful single-node AI assistant into a distributed knowledge platform.

## Shared Systems Across All Five Specs

Several concepts appear in multiple specs and should be implemented as shared infrastructure:

| Shared System | Used By |
|---|---|
| **Maturity tracking** (30-Ideas/20-Active/10-Archive) | Captures, Notes, Canvases |
| **Entity extraction + graph** | Notes, Canvases, Captures, RAG, Search, Agent context |
| **Review workflows** | Garden maintenance, Canvas gaps, Capture triage |
| **Connection metrics / authority** | RAG ranking, Note quality, Canvas validation |
| **Version control / provenance** | Notes, AI content, Canvas iterations |
| **Smart summarization layers** | Conversations, Weekly/monthly digests, Canvas auto-fill |
| **Agent capability declarations** | Personas, Custom agents, Nexus routing, DRM task assignment |
| **Execution context brokering** | Agent Swarms, Capability Broker, Integrations |
| **Workflow templates** | Agent Swarms, Publishing pipeline, Capture processing |

## Approach

1. Create new domain specs for net-new subsystems (knowledge-graph, capture, drm, canvas, publishing, mobile, analytics, agent-swarms, communication, onboarding, data-autonomy)
2. Update existing domain specs to reference new capabilities and integration points
3. Audit all docs/planning/ files to ensure no planned features were missed — resulted in adding 4 missing personas (Programmer, Librarian, Designer, Administrator), skill system, knowledge graph visualization, and detailed Phase 18–29 entries
4. Update roadmap with new phases organized by dependency and tier (Phase 24 reconceived as Agent Swarms 24a–24e; DRM expanded to 6 phases; Phases 25–29 expanded from one-liner to proper entries)
5. Keep existing completed work unchanged — this is additive, not revisionary
