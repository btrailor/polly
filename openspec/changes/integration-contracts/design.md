# Integration Contracts — Design

**Last Updated:** February 2026

---

## Architecture Overview

```
core/protocols/
├── __init__.py              # All protocol exports
├── pattern_consumer.py      # PatternConsumer protocol
├── entity_provider.py       # EntityProvider protocol
├── persona_aware.py         # PersonaAware protocol
└── context_contributor.py   # ContextContributor protocol
```

These protocols are *descriptive* — they formalize integration points that exist (or should exist) between systems. They don't add new infrastructure; they add contracts.

---

## Protocol Definitions

### PatternConsumer

Systems that use learned patterns to adapt their behavior.

```python
class PatternConsumer(Protocol):
    """Systems that consume patterns to adapt behavior.
    
    Implemented by: Router, RAG, DomainEngine, PersonaManager
    """
    
    def apply_patterns(self, patterns: list[Pattern], context: dict) -> None:
        """Apply relevant patterns to current operation.
        
        Args:
            patterns: Relevant patterns from PatternEngine
            context: Current operation context (query, domain, persona, etc.)
        """
        ...
    
    def report_outcome(self, pattern_id: str, was_helpful: bool, metadata: dict) -> None:
        """Report whether a pattern-informed decision was helpful.
        
        Enables pattern reinforcement/decay based on actual outcomes.
        """
        ...
```

**Implementors:**

| System | How It Consumes Patterns |
|--------|------------------------|
| `IntelligentRouterV2` | Uses ROUTING and ROUTING_OUTCOME patterns to prefer models that worked well for similar tasks |
| `UnifiedRAG` | Uses DOMAIN_PRIORITY patterns to weight collection scores |
| `DomainEngine` | Uses DOMAIN patterns to boost domain detection confidence |
| `PersonaManager` | Uses PERSONA patterns to recall per-persona preferences and behaviors |

### EntityProvider

Systems that produce entities for the knowledge graph.

```python
class EntityProvider(Protocol):
    """Systems that produce entities for the knowledge graph.
    
    Implemented by: EntityExtractor, PatternEngine, KnowledgeWriter, (future) BookLore
    """
    
    def extract_entities(self, content: str, source_type: str, source_id: str) -> list[Entity]:
        """Extract entities from content and return them.
        
        The caller (usually the query pipeline) is responsible for storing.
        """
        ...
```

### PersonaAware

Systems that change behavior based on the active persona.

```python
class PersonaAware(Protocol):
    """Systems that adapt behavior per-persona.
    
    Implemented by: PatternEngine, MentalModelManager, EntityContextBuilder, Router
    """
    
    def set_active_persona(self, persona_name: str, mode: str) -> None:
        """Notify this system that the active persona/mode has changed."""
        ...
    
    def get_persona_context(self, persona_name: str, mode: str) -> dict:
        """Get persona-specific context from this system."""
        ...
```

### ContextContributor

Systems that contribute context to the prompt.

```python
class ContextContributor(Protocol):
    """Systems that contribute context to the system prompt.
    
    Implemented by: MentalModelManager, EntityContextBuilder, PatternEngine, CompressionManager
    Each returns a formatted string block for prompt injection.
    """
    
    def build_context(self, query: str, domains: list[str], persona: Optional[str] = None, mode: Optional[str] = None) -> str:
        """Build context contribution for system prompt.
        
        Returns formatted markdown string (may be empty if nothing relevant).
        """
        ...
    
    @property
    def context_priority(self) -> int:
        """Priority for ordering in prompt (higher = closer to user message).
        
        Suggested ordering:
        - 100: Constitutional/ethics (always first)
        - 80: Persona mode prompt
        - 60: Mental models
        - 40: Knowledge graph entities
        - 20: Learned patterns
        - 10: Compressed conversation summary
        """
        ...
```

---

## Integration: Persona Composition

### Current State (Islands)

```
Polly.query()
├── Detect domain
├── RAG search
├── Build mental models context (persona considered for activation, not by persona)
├── Build pattern context (no persona awareness)
├── Build graph context (no persona awareness)  
├── Route to LLM
└── Learn patterns (no persona attribution)
```

### Target State (Composed)

```
Polly.query()
├── Detect domain
├── Notify systems of active persona: pattern_engine, mental_models, entity_context
├── RAG search (persona-aware collection weighting)
├── Gather context from all ContextContributors (ordered by priority)
│   ├── Constitutional layer (priority 100)
│   ├── Persona mode prompt (priority 80)
│   ├── Mental models (priority 60, persona-filtered)
│   ├── Entity graph context (priority 40, persona-relevant entities boosted)
│   ├── Learned patterns (priority 20, persona-specific patterns included)
│   └── Compressed history (priority 10)
├── Route to LLM (persona-specific model preference from patterns)
├── Learn patterns (attributed to active persona)
└── Report routing outcome (pattern feedback)
```

### Implementation in `core/polly.py`

**New method: `_notify_persona_context(persona_name, mode)`**
```python
def _notify_persona_context(self, persona_name: str, mode: str):
    """Notify all persona-aware systems of the active persona."""
    for system in [self.pattern_engine, self.mental_model_manager, self.entity_context]:
        if hasattr(system, 'set_active_persona'):
            system.set_active_persona(persona_name, mode)
```

**New method: `_gather_context(query, domains, persona, mode)`**
```python
def _gather_context(self, query: str, domains: list[str], persona: str = None, mode: str = None) -> str:
    """Gather context from all ContextContributors, ordered by priority."""
    contributors = []
    
    for system in [self.mental_model_manager, self.entity_context, self.pattern_engine, self.compression_manager]:
        if system and hasattr(system, 'build_context'):
            context = system.build_context(query, domains, persona, mode)
            if context:
                contributors.append((system.context_priority, context))
    
    # Sort by priority (highest first)
    contributors.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join(ctx for _, ctx in contributors)
```

### Per-System Persona Integration

**PatternEngine (persona-aware patterns):**
```python
def set_active_persona(self, persona_name: str, mode: str):
    self._active_persona = persona_name
    self._active_mode = mode

def get_patterns_for_prompt(self, query, domains, limit=5):
    patterns = self.search(PatternQuery(domains=domains, limit=limit * 2))
    
    # Boost persona-specific patterns
    if self._active_persona:
        for p in patterns:
            if p.metadata.get("persona") == self._active_persona:
                p._score_boost = 0.3  # 30% relevance boost
    
    return sorted(patterns, key=lambda p: p._relevance + getattr(p, '_score_boost', 0), reverse=True)[:limit]

def learn_from_query(self, query, domains, response):
    patterns = super().learn_from_query(query, domains, response)
    # Attribute patterns to active persona
    if self._active_persona:
        for p in patterns:
            p.metadata["persona"] = self._active_persona
            p.metadata["mode"] = self._active_mode
    return patterns
```

**MentalModelManager (persona-prioritized):**
```python
def set_active_persona(self, persona_name: str, mode: str):
    self._active_persona = persona_name
    self._active_mode = mode

def get_active_models(self, domain, page, keywords, limit=5):
    models = self._score_models(domain, page, self._active_persona, self._active_mode, keywords)
    # Existing three-tier scoring already considers persona — 
    # this ensures it's always set correctly, not just when passed as param
    return models[:limit]
```

**EntityContextBuilder (persona-relevant entities):**
```python
def set_active_persona(self, persona_name: str, mode: str):
    self._active_persona = persona_name

def build_context(self, query, domains, persona=None, mode=None):
    # Base entity context
    context = self._base_context(query, domains)
    
    # Boost entities that this persona frequently interacts with
    persona_name = persona or self._active_persona
    if persona_name:
        # Get entities that appear in this persona's pattern metadata
        persona_entities = self._get_persona_entity_affinity(persona_name)
        # Boost these in the context ranking
        ...
    
    return context
```

---

## Integration: Routing Feedback Loop

### Current State
- Patterns of type ROUTING exist but are never used by the router
- Routing decisions are not recorded as patterns
- No outcome tracking

### Target State

**Step 1: Pattern-Informed Routing**

In `IntelligentRouterV2.route()`:
```python
def route(self, query, context, patterns=None):
    # Existing complexity analysis + budget check
    base_decision = self._analyze_and_route(query, context)
    
    # Pattern-informed adjustment
    if patterns:
        routing_patterns = [p for p in patterns if p.pattern_type == PatternType.ROUTING_OUTCOME]
        for pattern in routing_patterns:
            if self._matches_current_task(pattern, query, context):
                # E.g., "claude-sonnet-4 performs well for code review tasks"
                preferred_model = pattern.metadata.get("preferred_model")
                if preferred_model and preferred_model in self.available_models:
                    base_decision.model_hint = preferred_model
                    base_decision.hint_confidence = pattern.confidence
    
    return base_decision
```

**Step 2: Outcome Recording**

After response generation in `Polly.query()`:
```python
# Record routing outcome for future learning
if self.pattern_engine:
    self.pattern_engine.learn(Pattern(
        pattern_type=PatternType.ROUTING_OUTCOME,
        name=f"routing_{task_type}_{model_used}",
        description=f"{model_used} used for {task_type} task",
        confidence=0.5,  # Starts neutral, adjusted by feedback
        metadata={
            "model": model_used,
            "task_type": detected_task_type,
            "rag_coverage": rag_confidence,
            "response_quality": None,  # Set by user feedback or heuristic
            "persona": active_persona,
            "tokens_used": token_count,
            "cost": cost
        }
    ))
```

**Step 3: Outcome Feedback**

When user provides implicit feedback (continues conversation, saves note, etc.):
```python
if last_routing_pattern_id:
    self.pattern_engine.learn(existing_pattern)  # Reinforces — increments occurrences, boosts confidence
```

---

## Integration: Conversation Synchronization

### Current Split
- Electron `conversation-manager.js`: SQLite, persistent, manages CRUD
- Python `Polly.conversation_history`: list[dict], ephemeral, used for compression/learning

### Resolution: Electron Remains Source of Truth

The Electron SQLite database is already the persistent conversation store. Python's role is a runtime buffer. The fix is:

1. **On conversation load** (when user switches to existing conversation): Electron sends last N messages to Python via API
2. **On query**: Python uses its buffer for immediate context, but references Electron's store for historical compression
3. **On compression trigger**: Python requests full conversation from Electron API

**New endpoint in `interfaces/server.py`:**
```python
@router.post("/polly/conversation/sync")
async def sync_conversation(request: ConversationSyncRequest):
    """Receive conversation messages from Electron to populate Python buffer.
    
    Called when:
    - User opens an existing conversation
    - App starts and restores last conversation
    """
    polly = get_polly()
    polly.conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]
    return {"status": "synced", "message_count": len(request.messages)}
```

**In Electron `app.js`:**
```javascript
async function loadConversation(conversationId) {
    const messages = await window.polly.getConversationMessages(conversationId);
    
    // Sync to Python backend
    await safeFetch('/polly/conversation/sync', {
        method: 'POST',
        body: JSON.stringify({ messages: messages.slice(-50) })  // Last 50 messages
    });
}
```

**This avoids:**
- Duplicating the persistence layer
- Complex two-way sync
- Changing either system's primary responsibility

---

## Integration: Mental Model Effectiveness

### Approach: Lightweight Heuristic Tracking

Rather than asking users to rate mental models (high friction), track effectiveness heuristically:

**Signals of helpfulness:**
- User continues the conversation (neutral — expected)
- User saves response as note (positive signal)
- User immediately re-asks with different phrasing (negative signal — response wasn't helpful)
- User rates response (if rating exists in UI)
- Response length vs query complexity alignment

**Implementation:**

Add to `MentalModelManager`:
```python
def record_activation(self, model_ids: list[str], query: str, response_signals: dict):
    """Record which models were active and the outcome signals.
    
    response_signals: {
        "saved_to_kb": bool,
        "rephrased": bool,
        "conversation_continued": bool,
        "user_rating": Optional[int]  # 1-5
    }
    """
    for model_id in model_ids:
        self._effectiveness_log.append({
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            "signals": response_signals
        })
    
    # Periodically analyze: which models correlate with positive signals?
    # This can influence activation scoring over time
```

This is intentionally lightweight. We're not building a full A/B testing framework — just collecting signals that can inform activation scoring if we want to tune it later.

---

## Integration: Dynamic Domain Configuration

### Current State

Domains are a Python enum in `core/domains.py`:
```python
class DomainType(Enum):
    SIGILS = "sigils"
    SIGNALS = "signals"
    SCROLLS = "scrolls"
    GLYPHS = "glyphs"
    GRIDS = "grids"
```

With hardcoded keywords, colors, and RAG collection mappings.

### Target State

Domains loaded from user configuration:

```yaml
# ~/.polly/config.yaml or config/config.yaml
domains:
  sigils:
    name: "Sigils"
    description: "Code & Infrastructure"
    color: "#4A90D9"
    icon: "code"
    keywords: ["docker", "python", "rust", "javascript", "api", "server"]
    rag_collections: ["codebase", "github"]
    folder_path: "~/notes/sigils"
  signals:
    name: "Signals"
    description: "Audio Programming"
    # ... etc
  # Users can add custom domains:
  custom_domain:
    name: "My Domain"
    description: "Custom domain for X"
    color: "#FF6B6B"
    keywords: ["keyword1", "keyword2"]
    rag_collections: ["notes"]
    folder_path: "~/notes/custom"
```

**Implementation:**
- `DomainEngine.__init__()` reads from config instead of using enum
- `DomainType` enum kept for backward compatibility but new domains are string-based
- Domain detection uses configurable keyword lists
- RAG collection mapping uses configurable associations
- UI domain selector reads from config (already somewhat does this)

This is a moderate refactor of `core/domains.py` — the detection algorithm stays the same, only the data source changes from hardcoded to configured.

---

## Compression→Entity Integration

When conversations are compressed, the compressed output contains extracted concepts and topics. These should flow into the entity system:

```python
# In Polly._try_compress_conversation()
if result.get('compressed'):
    compressed = result['compressed']
    
    # Existing: feed to pattern learner
    self.pattern_engine.learn_from_compressed(compressed, conversation_id)
    
    # NEW: extract entities from compressed summary
    if self.entity_extractor:
        # Key concepts from compression are high-signal entity candidates
        key_concepts = compressed.get('key_concepts', [])
        focus_topics = compressed.get('focus_topics', [])
        
        for concept in key_concepts:
            self.entity_extractor.extract_and_store(
                concept.get('concept', ''),
                source_type="compression",
                source_id=conversation_id,
                domains=list(compressed.get('domains', []))
            )
```

---

## Summary of All Integration Points

| From | To | Integration | Priority |
|------|-----|-------------|----------|
| PatternEngine | Router | Pattern-informed model selection | High |
| Router | PatternEngine | Routing outcome recording | High |
| Persona | PatternEngine | Persona-attributed pattern learning | High |
| PatternEngine | Persona | Persona-specific pattern retrieval | High |
| Persona | EntityStore | Persona-relevant entity boosting | Medium |
| Persona | MentalModels | Persona-prioritized model selection | Medium (already partial) |
| Compression | EntityExtractor | Entity extraction from summaries | Medium |
| Compression | PatternEngine | Pattern extraction from summaries | Medium (already exists) |
| Electron | Python | Conversation sync on load | Medium |
| MentalModels | Effectiveness log | Activation outcome tracking | Low |
| Config | DomainEngine | Dynamic domain configuration | Low |
