# Integration Contracts — Tasks

**Last Updated:** February 2026  
**Priority:** P1 — Depends on unified-pattern-engine and entity-model-unification  
**Estimated Effort:** 2–3 weeks

---

## Task Overview

| # | Task | Est. | Depends | Status |
|---|------|------|---------|--------|
| 1 | Create `core/protocols/` package with protocol definitions | 0.5d | — | ✅ Done |
| 2 | Implement ContextContributor across existing systems | 1d | P0 changes | ✅ Done |
| 3 | Implement `_gather_context()` in `core/polly.py` | 0.5d | Task 2 | ✅ Done |
| 4 | Implement persona↔pattern integration | 1.5d | unified-pattern-engine | ✅ Done |
| 5 | Implement persona↔entity integration | 1d | entity-model-unification | ✅ Done |
| 6 | Implement persona↔mental model integration | 0.5d | — | ✅ Done |
| 7 | Implement pattern→router integration | 1.5d | unified-pattern-engine | ✅ Done |
| 8 | Implement router→pattern feedback loop | 1d | Task 7 | ✅ Done |
| 9 | Implement conversation synchronization | 1d | — | ✅ Done |
| 10 | Implement compression→entity integration | 0.5d | entity-model-unification | ✅ Done |
| 11 | Implement mental model effectiveness tracking | 0.5d | — | ✅ Done |
| 12 | Implement dynamic domain configuration | 1.5d | — | ✅ Done |
| 13 | Write integration tests | 1.5d | All above | ✅ Done |
| 14 | Update affected specs | 1d | All above | ✅ Done |

---

## Detailed Task Descriptions

### 1. Create `core/protocols/` package

Create `core/protocols/` with:
- `__init__.py` — exports all protocols
- `pattern_consumer.py` — `PatternConsumer` Protocol
- `entity_provider.py` — `EntityProvider` Protocol
- `persona_aware.py` — `PersonaAware` Protocol
- `context_contributor.py` — `ContextContributor` Protocol

These are Python `typing.Protocol` classes — no implementation, just contracts.

**Files:** New package  
**Tests:** N/A (protocols are structural types)

### 2. Implement ContextContributor across existing systems

Add `build_context(query, domains, persona, mode) -> str` and `context_priority` property to:

**`MentalModelManager` (priority 60):**
- Wraps existing `_build_mental_models_context()` logic
- Returns PIL/compact-formatted mental models string

**`EntityContextBuilder` (priority 40):**
- Already has `build_context()` from entity-model-unification
- Add `context_priority = 40`

**`PatternEngine` (priority 20):**
- Wraps existing `get_patterns_for_prompt()` into formatted string
- Returns "Learned Patterns:" block

**`CompressionManager` (priority 10):**
- Returns most recent compressed conversation summary if available
- Wraps existing decompression logic

**Files:** `core/mental_models.py`, `core/entities/context.py`, `core/patterns/engine.py`, `core/compression/manager.py`  
**Tests:** `tests/root/test_context_contributors.py`

### 3. Implement `_gather_context()` in `core/polly.py`

Replace the manual context assembly in `Polly.query()`:

**Before:**
```python
mental_models_context = self._build_mental_models_context(query, domain, page, persona, mode)
graph_context = self.entity_context.build_context(query, domains)
pattern_context = "..." # manual formatting
# Assembled into augmented prompt manually
```

**After:**
```python
full_context = self._gather_context(query, domain_names, persona, mode)
# Single method collects from all ContextContributors, ordered by priority
```

The method iterates over registered contributors, calls `build_context()` on each, sorts by `context_priority`, and concatenates.

**Files:** `core/polly.py`  
**Tests:** `tests/root/test_polly_context_gathering.py`

### 4. Implement persona↔pattern integration

**In PatternEngine:**
- Add `set_active_persona(name, mode)` method
- Modify `learn_from_query()` to attribute patterns to active persona
- Modify `get_patterns_for_prompt()` to boost persona-specific patterns
- Add `get_persona_patterns(persona_name)` for per-persona pattern retrieval

**In PersonaManager:**
- On persona activation, call `pattern_engine.set_active_persona()`
- In persona `process()` methods, optionally query persona-specific patterns

**In Polly:**
- After persona activation, notify pattern engine
- When learning patterns post-query, include persona context

**Files:** `core/patterns/engine.py`, `core/personas/manager.py`, `core/polly.py`  
**Tests:** `tests/root/test_persona_pattern_integration.py`

### 5. Implement persona↔entity integration

**In EntityContextBuilder:**
- Add `set_active_persona(name, mode)` method
- Track which entities each persona interacts with (from pattern metadata)
- Boost persona-affiliated entities in context ranking

**In PersonaManager:**
- On persona activation, call `entity_context.set_active_persona()`

**Files:** `core/entities/context.py`, `core/personas/manager.py`, `core/polly.py`  
**Tests:** `tests/root/test_persona_entity_integration.py`

### 6. Implement persona↔mental model integration

**Current state:** Mental model activation already considers `active_for_personas` and `active_for_modes`. But the persona doesn't actively participate in selection.

**Changes:**
- Add `set_active_persona(name, mode)` to `MentalModelManager`
- Ensure activation scoring always uses the current persona (not just when passed as parameter)
- Allow personas to declare preferred mental models in their YAML definitions:
  ```yaml
  # definitions/architect.yaml
  preferred_mental_models:
    - systems_thinking
    - first_principles
    - constraint_as_meaning
  ```
- Preferred models get a scoring boost

**Files:** `core/mental_models.py`, persona YAML definitions  
**Tests:** `tests/root/test_persona_mental_model_integration.py`

### 7. Implement pattern→router integration

**In IntelligentRouterV2:**
- Add `apply_patterns(patterns, context)` method
- During routing, check for ROUTING_OUTCOME patterns matching current task type
- If high-confidence pattern exists for a model, use as hint (not override — budget and availability still apply)
- Log when pattern influences routing decision

**In Polly.query():**
- Before routing, get relevant routing patterns:
  ```python
  routing_patterns = self.pattern_engine.search(PatternQuery(
      pattern_types=[PatternType.ROUTING_OUTCOME],
      min_confidence=0.6,
      limit=3
  ))
  route_decision = self.router_v2.route(query, context, patterns=routing_patterns)
  ```

**Files:** `core/router_v2.py`, `core/polly.py`  
**Tests:** `tests/root/test_pattern_router_integration.py`

### 8. Implement router→pattern feedback loop

**In Polly.query() post-response:**
```python
# Record routing decision as pattern
self.pattern_engine.learn(Pattern(
    pattern_type=PatternType.ROUTING_OUTCOME,
    name=f"route_{task_type}_{model}",
    description=f"{model} for {task_type}",
    confidence=0.5,  # Neutral start
    metadata={
        "model": model_used,
        "task_type": task_type,
        "rag_coverage": rag_confidence,
        "persona": active_persona,
        "tokens": token_count,
        "cost": cost
    }
))
```

**Outcome signals (reinforce/decay):**
- Conversation continues → neutral (no change)
- User saves response to KB → positive (reinforce: +0.05 confidence)
- User re-asks immediately → negative (decay: -0.1 confidence)
- Explicit thumbs up/down (future UI) → strong signal (±0.15)

Implement as `Polly._record_routing_outcome()` called at end of query.

**Files:** `core/polly.py`  
**Tests:** `tests/root/test_routing_feedback.py`

### 9. Implement conversation synchronization

**Backend (`interfaces/server.py`):**
- New endpoint: `POST /polly/conversation/sync`
- Accepts: `{ messages: [{role, content, timestamp}], conversation_id: str }`
- Sets `polly.conversation_history` from received messages
- Clears old history, sets new

**Frontend (`electron-app/src/renderer/app.js`):**
- On conversation load: send last 50 messages to `/polly/conversation/sync`
- On app start with restored conversation: same
- On new conversation: send empty sync to clear Python buffer

**Files:** `interfaces/server.py`, `electron-app/src/renderer/app.js`  
**Tests:** `tests/root/test_conversation_sync.py`

### 10. Implement compression→entity integration

**In `Polly._try_compress_conversation()`:**
- After compression, extract entities from key concepts and focus topics
- Call `self.entity_extractor.extract_and_store()` with compressed data
- Source type: "compression"

This is a small wiring task — both systems exist after P0 changes.

**Files:** `core/polly.py`  
**Tests:** `tests/root/test_compression_entity_integration.py`

### 11. Implement mental model effectiveness tracking

**In MentalModelManager:**
- Add `_effectiveness_log: list[dict]` (in-memory, periodically flushed to YAML)
- Add `record_activation(model_ids, signals)` method
- Add `get_effectiveness_summary()` method

**In Polly.query():**
- Track which models were activated
- After response, check for positive/negative signals:
  - Did user save to KB? (check next action)
  - Did user rephrase? (check next query similarity)
- Call `record_activation()` with signals

**Files:** `core/mental_models.py`, `core/polly.py`  
**Tests:** `tests/root/test_mental_model_effectiveness.py`

### 12. Implement dynamic domain configuration

**In `core/domains.py`:**
- Keep `DomainType` enum for backward compatibility with existing string-based comparison
- Add `DomainConfig` dataclass:
  ```python
  @dataclass
  class DomainConfig:
      id: str
      name: str
      description: str
      color: str
      icon: str
      keywords: list[str]
      rag_collections: list[str]
      folder_path: Optional[str] = None
  ```
- Modify `DomainEngine.__init__()` to:
  1. Load from config YAML first
  2. Fall back to hardcoded defaults if no config
  3. Support custom domains beyond the original five
- Domain detection algorithm stays the same — just reads keywords from config instead of hardcoded

**Config format:**
```yaml
domains:
  sigils:
    name: "Sigils"
    description: "Code & Infrastructure"
    color: "#4A90D9"
    keywords: ["docker", "python", "rust", ...]
    rag_collections: ["codebase", "github"]
```

**Files:** `core/domains.py`, `config/config.yaml` (add domain config section)  
**Tests:** `tests/root/test_dynamic_domains.py`

### 13. Write integration tests

End-to-end tests that verify cross-system behavior:

- `test_persona_activates_patterns.py` — Persona change triggers pattern engine update
- `test_routing_uses_patterns.py` — Router consults patterns, outcomes recorded
- `test_context_gathering.py` — All contributors produce context in correct order
- `test_conversation_roundtrip.py` — Electron syncs messages, Python uses them for compression
- `test_compression_feeds_entities.py` — Compressed conversation produces entities

**Files:** `tests/root/test_integration_*.py`

### 14. Update affected specs

After implementation, update:

| Spec | Updates |
|------|---------|
| `patterns/spec.md` | Add integration contracts section, update integration points |
| `personas/spec.md` | Document persona↔pattern, persona↔entity, persona↔mental model composition |
| `mental-models/spec.md` | Document effectiveness tracking, persona integration |
| `architecture/spec.md` | Update data flow to show integration contracts |
| `rag/spec.md` | Document pattern-aware retrieval |
| `compression/spec.md` | Document entity extraction from compression |

---

## Verification Criteria

1. **Persona activation** propagates to pattern engine, entity context, and mental model manager
2. **Pattern-informed routing** demonstrably selects different models based on learned patterns
3. **Routing outcomes** recorded as ROUTING_OUTCOME patterns with confidence evolution
4. **Conversation sync** — Python buffer populated when Electron loads a conversation
5. **Context gathering** produces ordered context from all contributors
6. **Entity extraction** triggered from compressed conversation data
7. **Mental model effectiveness** signals recorded after each query
8. **Custom domains** loadable from config.yaml

---

## Follow-up (non-blocking)

- **Linter cleanup:** Known basedpyright messages in `interfaces/server.py` (ObsidianIntegration, `polly` scope) are documented in **docs/status/LINTER_TODO.md** for later cleanup.
