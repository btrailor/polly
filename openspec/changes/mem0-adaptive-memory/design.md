# Design: Mem0 Adaptive Memory Layer

## Architecture Overview

Mem0 serves as an **additive memory layer** that enhances existing systems without replacing them:

```
┌─────────────────────────────────────────────────────────────┐
│                        Polly Core                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐     ┌──────────┐   │
│  │ Knowledge    │      │   Personas   │     │   RAG    │   │
│  │  Writer      │      │ (Scribe/etc) │     │ (Chroma) │   │
│  └──────┬───────┘      └──────┬───────┘     └────┬─────┘   │
│         │                     │                   │          │
│         └─────────────────────┼───────────────────┘          │
│                               │                              │
│                    ┌──────────▼──────────┐                  │
│                    │   Mem0 Adapter      │                  │
│                    │  (Unified Memory)   │                  │
│                    └──────────┬──────────┘                  │
│                               │                              │
│              ┌────────────────┼────────────────┐            │
│              │                │                │             │
│         ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐      │
│         │ Entity   │    │ Session  │    │  User    │       │
│         │ Memory   │    │ Context  │    │ Memories │       │
│         └──────────┘    └──────────┘    └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Mem0Adapter (`core/memory/mem0_adapter.py`)

**Purpose:** Unified interface for Mem0 operations

**Key Methods:**
- `add_memory(content, user_id, metadata)` - Store memory with entity extraction
- `search_memory(query, user_id, limit)` - Search with semantic reranking
- `get_relevant_context(query, user_id)` - Get formatted context for LLM calls
- `update_memory(memory_id, content)` - Update existing memory
- `delete_memory(memory_id)` - Remove memory

**Configuration:**
- Vector store: ChromaDB (separate collection from main RAG)
- Graph store: Optional Neo4j (disabled by default)
- LLM: Uses LiteLLM adapter if available (Agent 1 integration)
- Collections: Per-use-case namespacing (knowledge, patterns, personas)

### 2. Integration Points

#### Knowledge Writer Integration
**File:** `core/knowledge_writer.py`
**Location:** After `_save_note()` succeeds
**Logic:**
```python
if self.config.get('memory.provider') == 'mem0':
    mem0.add_memory(
        content=note_content,
        user_id="default",
        metadata={
            'title': title,
            'domain': domain,
            'source': 'knowledge_writer',
            'timestamp': datetime.now().isoformat()
        }
    )
```
**Why:** Enables entity extraction from saved notes, builds knowledge graph

#### Pattern Learning Integration
**File:** `core/pattern_learning.py` (to be created)
**Logic:**
- Store patterns in both `patterns.json` (existing) and Mem0 (new)
- Use Mem0 search for pattern-informed routing decisions
- Metadata: `type: 'pattern'`, `pattern_type`, `confidence`

**Why:** Enables semantic pattern search, relationship discovery

#### Persona Integration
**Files:** `core/personas/implementations/*.py`
**Logic:** Per-persona memory via `agent_id`
- Scribe: `user_id=f"persona:scribe"` - enrichment context, style preferences
- Architect: `user_id=f"persona:architect"` - planning decisions, system context
- Professor: `user_id=f"persona:professor"` - learning progress, teaching history

**Example (Scribe):**
```python
async def _handle_enrich(self, context: PersonaContext) -> PersonaResponse:
    # Get Scribe-specific memories
    if self.config.get('memory.provider') == 'mem0':
        memory_context = self.mem0.get_relevant_context(
            query=content,
            user_id="persona:scribe"
        )
        # Inject into LLM prompt
```

**Why:** Personas learn from interactions, maintain consistent style/behavior

### 3. Configuration Schema

**File:** `config/config.yaml`

```yaml
memory:
  provider: "local"  # "local" | "mem0"
  
  mem0:
    enabled: false  # Opt-in
    vector_store: "chroma"
    graph_store: null  # Optional: Neo4j config
    llm: "litellm"  # Use Agent 1's adapter
    
    collections:
      knowledge: "polly_knowledge"
      patterns: "polly_patterns"
      personas: "polly_personas"
```

### 4. Data Flow

**Memory Creation Flow:**
1. User saves note via Knowledge Writer
2. Knowledge Writer writes markdown to vault
3. Knowledge Writer indexes to RAG (ChromaDB)
4. **NEW:** Knowledge Writer adds to Mem0 with metadata
5. Mem0 extracts entities and relationships
6. Future queries can leverage entity graph

**Memory Retrieval Flow:**
1. Persona receives user query
2. **NEW:** Persona searches Mem0 for relevant context
3. Mem0 returns ranked memories + entity relationships
4. Persona constructs enhanced prompt with memory context
5. Persona calls LLM via router
6. LLM generates context-aware response

## API Endpoints

**New routes in router:**
- `POST /api/memory/add` - Add memory
- `GET /api/memory/search?query=...&user_id=...` - Search memories
- `GET /api/memory/context?query=...` - Get formatted context
- `PUT /api/memory/{memory_id}` - Update memory
- `DELETE /api/memory/{memory_id}` - Delete memory
- `GET /api/memory/entities` - List entities (future: graph visualization)

## Migration Strategy

**Script:** `scripts/migrate_patterns_to_mem0.py`

**Steps:**
1. Check if `~/.polly/patterns.json` exists
2. Load existing patterns
3. Initialize Mem0Adapter
4. For each pattern:
   - Convert to memory format
   - Preserve pattern type, timestamp, confidence
   - Add to Mem0 with `source: 'migration'`
5. Create backup: `patterns.json.backup`
6. Log migration summary

**Rollback:** Keep `patterns.json` intact (additive layer)

## Performance Targets

- Memory add: < 50ms (async, non-blocking)
- Memory search: < 100ms (critical path)
- Context retrieval: < 100ms (included in LLM call)
- RAG integration: No regression in existing search performance

## Testing Strategy

1. **Unit Tests:**
   - Mem0Adapter operations (add, search, update, delete)
   - Configuration parsing
   - Error handling (Mem0 unavailable)

2. **Integration Tests:**
   - Knowledge Writer → Mem0 flow
   - Pattern Learning → Mem0 flow
   - Persona context retrieval
   - API endpoints

3. **Regression Tests:**
   - Existing systems work with `provider: "local"`
   - No performance degradation when Mem0 disabled

4. **Success Criteria:**
   - [ ] Knowledge saves persist to both file + Mem0
   - [ ] Pattern searches use Mem0 when enabled
   - [ ] Per-persona context recall works
   - [ ] Existing systems work with `provider: "local"`
   - [ ] Optional graph store config tested (even if null)
   - [ ] Memory search performance < 100ms
   - [ ] Migration script preserves all pattern data

## Future Enhancements (Out of Scope)

- Graph visualization UI (entity browser, relationship explorer)
- Neo4j graph store for advanced relationship queries
- Cross-persona memory sharing
- Memory decay/aging strategies
- Memory consolidation (summarize old memories)
