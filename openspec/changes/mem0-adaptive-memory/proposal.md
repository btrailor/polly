# Proposal: Mem0 Adaptive Memory Layer

**Change:** Add Mem0 as an adaptive memory layer for knowledge persistence, pattern storage, and persona context.

**Why:** Polly currently has multiple memory/knowledge systems that operate independently:
- Knowledge Writer: Saves markdown notes to vault
- RAG (ChromaDB): Vector search across knowledge base
- Personas: Architect, Scribe, Professor with modes and behaviors

These systems lack:
- **Entity relationships**: No graph-based connections between concepts
- **Multi-level context**: No distinction between user-specific, session, and long-term memory
- **Adaptive learning**: No automatic pattern extraction from interactions
- **Cross-system coherence**: Knowledge in RAG doesn't inform persona behavior

Mem0 provides:
- Graph-based memory with entity relationships
- Multi-level memory (user, session, agent)
- Automatic fact extraction and relationship mapping
- Memory decay and relevance scoring
- Unified query interface across memory types

**Scope:** 
- **Backend:** Core integration (`core/memory/`), API endpoints, integration with existing systems
- **Frontend:** Memory visualization, entity browser, relationship graph (future phase)
- **Impact:** Additive layer — enhances but doesn't replace existing systems

**Tier/Phase:** Phase 1.5 / Core Intelligence (Memory & Learning)

**Success Criteria:**
1. Mem0 installed and configured
2. Memory operations (add, search, update) functional
3. Integration with personas for context-aware responses
4. Integration with knowledge writer for entity extraction
5. API endpoints for memory management

**Non-Goals (Future Work):**
- Replace existing RAG system
- Replace existing knowledge writer
- Complex graph visualization UI (defer to later phase)
