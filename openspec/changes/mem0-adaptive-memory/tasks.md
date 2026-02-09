# Tasks: Mem0 Adaptive Memory Layer

## Phase 1: Core Infrastructure

### Task 1: Create Memory Module Structure ✅
- [x] Create `core/memory/` directory
- [x] Create `core/memory/__init__.py`
- [x] Update `requirements.txt` with `mem0ai>=1.0.0`
- [x] Update `config/approved_packages.yaml`

### Task 2: Implement Mem0Adapter
**File:** `core/memory/mem0_adapter.py`

**Implementation:**
```python
from mem0 import Memory
from typing import Dict, List, Optional, Any
import logging

class Mem0Adapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        mem_config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "polly_mem0_memories",
                    "path": "~/.polly/chroma_mem0"
                }
            }
        }
        
        # Optional graph store
        if config.get('memory', {}).get('mem0', {}).get('graph_store'):
            mem_config["graph_store"] = config['memory']['mem0']['graph_store']
        
        self.memory = Memory.from_config(mem_config)
    
    def add_memory(self, content: str, user_id: str = "default",
                   metadata: dict = None) -> Dict:
        """Add memory with entity extraction"""
        return self.memory.add(content, user_id=user_id, metadata=metadata)
    
    def search_memory(self, query: str, user_id: str = "default",
                      limit: int = 5) -> List[Dict]:
        """Search memories with reranking"""
        return self.memory.search(query, user_id=user_id, limit=limit)
    
    def get_relevant_context(self, query: str, user_id: str = "default") -> str:
        """Get memory-enhanced context for LLM calls"""
        memories = self.search_memory(query, user_id, limit=3)
        return "\n\n".join([m['memory'] for m in memories])
```

**Success Criteria:**
- [ ] Adapter initializes with config
- [ ] Add/search/update/delete operations work
- [ ] Error handling for Mem0 unavailable
- [ ] Logging for debugging

---

## Phase 2: System Integrations

### Task 3: Integrate with Knowledge Writer
**File:** `core/knowledge_writer.py`
**Location:** After `_save_note()` succeeds (around line 200-250)

**Changes:**
1. Add Mem0 import at top
2. In `_save_note()`, after successful file write and RAG indexing:
```python
# Persist to Mem0 if enabled
if self.config.get('memory', {}).get('provider') == 'mem0':
    try:
        from core.memory.mem0_adapter import Mem0Adapter
        mem0 = Mem0Adapter(self.config)
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
        logger.info(f"Added note to Mem0: {title}")
    except Exception as e:
        logger.warning(f"Failed to add to Mem0 (non-critical): {e}")
```

**Success Criteria:**
- [ ] Saved notes added to Mem0
- [ ] Metadata preserved
- [ ] Failures logged but don't break save
- [ ] Works when `provider: "local"`

### Task 4: Create Pattern Learning Module
**File:** `core/pattern_learning.py` (new file)

**Purpose:** Extract and store interaction patterns

**Implementation:**
```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

@dataclass
class Pattern:
    type: str  # "routing", "user_preference", "task_type"
    description: str
    confidence: float  # 0.0-1.0
    timestamp: str
    metadata: Dict

class PatternLearner:
    def __init__(self, config: Dict):
        self.config = config
        self.patterns_file = Path.home() / ".polly" / "patterns.json"
        
        # Initialize Mem0 if enabled
        if config.get('memory', {}).get('provider') == 'mem0':
            from core.memory.mem0_adapter import Mem0Adapter
            self.mem0 = Mem0Adapter(config)
        else:
            self.mem0 = None
    
    def learn_pattern(self, pattern: Pattern):
        """Store pattern in both JSON and Mem0"""
        # Save to patterns.json (existing behavior)
        patterns = self._load_patterns()
        patterns.append(pattern.__dict__)
        self._save_patterns(patterns)
        
        # Save to Mem0 (new behavior)
        if self.mem0:
            self.mem0.add_memory(
                content=f"Pattern: {pattern.type} - {pattern.description}",
                user_id="patterns",
                metadata={
                    'type': 'pattern',
                    'pattern_type': pattern.type,
                    'confidence': pattern.confidence,
                    'timestamp': pattern.timestamp
                }
            )
    
    def search_patterns(self, query: str) -> List[Pattern]:
        """Search patterns using Mem0 or fallback to JSON"""
        if self.mem0:
            results = self.mem0.search_memory(query, user_id="patterns", limit=5)
            # Convert to Pattern objects
            return [Pattern(**r['metadata']) for r in results]
        else:
            # Fallback: simple keyword search in patterns.json
            patterns = self._load_patterns()
            return [Pattern(**p) for p in patterns if query.lower() in p['description'].lower()]
```

**Success Criteria:**
- [ ] Patterns stored in both JSON and Mem0
- [ ] Search works with Mem0 enabled
- [ ] Fallback works with local provider
- [ ] Backwards compatible with existing patterns

### Task 5: Integrate with Personas
**Files:** 
- `core/personas/implementations/scribe.py`
- `core/personas/implementations/professor.py`
- `core/personas/base.py` (add helper method)

**Changes to `base.py`:**
```python
def _get_memory_context(self, query: str) -> str:
    """Get persona-specific memory context"""
    if not hasattr(self, 'mem0') or not self.mem0:
        return ""
    
    user_id = f"persona:{self.name}"
    return self.mem0.get_relevant_context(query, user_id)
```

**Changes to `scribe.py` (in `__init__`):**
```python
# Initialize Mem0 if enabled
if hasattr(router, 'config') and router.config.get('memory', {}).get('provider') == 'mem0':
    from core.memory.mem0_adapter import Mem0Adapter
    self.mem0 = Mem0Adapter(router.config)
else:
    self.mem0 = None
```

**Changes to `scribe.py` (in `_handle_enrich`):**
```python
# Get Scribe-specific memory context
memory_context = self._get_memory_context(content) if self.mem0 else ""

# Inject into prompt
system_prompt = f"""You are the Scribe...

{memory_context}

Transform the following..."""
```

**Success Criteria:**
- [ ] Scribe recalls previous enrichment patterns
- [ ] Professor recalls learning progress
- [ ] Architect recalls planning decisions
- [ ] Memory context improves response quality

---

## Phase 3: Configuration & API

### Task 6: Update Configuration
**File:** `config/config.yaml`

**Add section:**
```yaml
# Memory Layer Configuration
memory:
  provider: "local"  # "local" | "mem0"
  
  mem0:
    enabled: false  # Opt-in for safety
    vector_store: "chroma"
    graph_store: null  # Optional: Neo4j config for future
    llm: "litellm"  # Use unified adapter if available
    
    collections:
      knowledge: "polly_knowledge"
      patterns: "polly_patterns"
      personas: "polly_personas"
```

**Success Criteria:**
- [ ] Config loads without errors
- [ ] Provider defaults to "local"
- [ ] Mem0 disabled by default
- [ ] Documentation in comments

### Task 7: Add API Endpoints
**File:** `interfaces/polly_server.py` or new `interfaces/memory_api.py`

**Endpoints:**
```python
@app.post("/api/memory/add")
async def add_memory(request: MemoryAddRequest):
    """Add a memory"""
    mem0 = get_mem0_adapter()
    result = mem0.add_memory(
        content=request.content,
        user_id=request.user_id,
        metadata=request.metadata
    )
    return {"success": True, "memory_id": result['id']}

@app.get("/api/memory/search")
async def search_memory(query: str, user_id: str = "default", limit: int = 5):
    """Search memories"""
    mem0 = get_mem0_adapter()
    results = mem0.search_memory(query, user_id, limit)
    return {"results": results}

@app.get("/api/memory/context")
async def get_memory_context(query: str, user_id: str = "default"):
    """Get formatted context for LLM"""
    mem0 = get_mem0_adapter()
    context = mem0.get_relevant_context(query, user_id)
    return {"context": context}
```

**Success Criteria:**
- [ ] Endpoints respond correctly
- [ ] Error handling for Mem0 disabled
- [ ] Authentication/authorization (if needed)
- [ ] API documentation

---

## Phase 4: Migration & Testing

### Task 8: Create Migration Script
**File:** `scripts/migrate_patterns_to_mem0.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""Migrate existing patterns.json to Mem0"""

import json
from pathlib import Path
import sys

def main():
    patterns_file = Path.home() / ".polly" / "patterns.json"
    
    if not patterns_file.exists():
        print("No patterns.json found, skipping migration")
        return
    
    # Load patterns
    with open(patterns_file) as f:
        patterns = json.load(f)
    
    print(f"Found {len(patterns)} patterns to migrate")
    
    # Initialize Mem0
    from core.memory.mem0_adapter import Mem0Adapter
    # Load config...
    mem0 = Mem0Adapter(config)
    
    # Migrate each pattern
    for i, pattern in enumerate(patterns):
        mem0.add_memory(
            content=f"Pattern: {pattern['type']} - {pattern['description']}",
            user_id="patterns",
            metadata={
                'type': 'pattern',
                'pattern_type': pattern['type'],
                'confidence': pattern.get('confidence', 0.8),
                'timestamp': pattern.get('timestamp', ''),
                'source': 'migration'
            }
        )
        print(f"Migrated pattern {i+1}/{len(patterns)}")
    
    # Create backup
    backup_file = patterns_file.with_suffix('.json.backup')
    patterns_file.rename(backup_file)
    print(f"Created backup: {backup_file}")
    
    print("Migration complete!")

if __name__ == "__main__":
    main()
```

**Success Criteria:**
- [ ] All patterns migrated
- [ ] Backup created
- [ ] Metadata preserved
- [ ] Idempotent (can run multiple times)

### Task 9: Testing & Validation
**Create tests in `tests/test_mem0_integration.py`**

**Test Cases:**
1. Mem0Adapter initialization
2. Add/search/update/delete operations
3. Knowledge Writer integration
4. Pattern Learning integration
5. Persona memory recall
6. API endpoints
7. Configuration variations
8. Error handling

**Performance Tests:**
- Memory add: < 50ms
- Memory search: < 100ms
- No regression in existing systems

**Success Criteria:**
- [ ] All tests pass
- [ ] Performance targets met
- [ ] No regressions
- [ ] Integration tests pass

---

## Phase 5: Documentation & Completion

### Task 10: Update OpenSpec
**Files:**
- `openspec/specs/memory/spec.md` (create)
- `openspec/specs/project/status.md` (update)
- `openspec/specs/project/roadmap.md` (update)
- `docs/status/CHANGELOG.md` (add entry)

**Success Criteria:**
- [ ] Spec documents current behavior
- [ ] Status reflects completion
- [ ] Changelog entry added
- [ ] Change folder archived

---

## Implementation Order

1. ✅ Task 1: Module structure
2. Task 2: Mem0Adapter (core)
3. Task 6: Configuration
4. Task 3: Knowledge Writer integration
5. Task 4: Pattern Learning module
6. Task 5: Persona integration
7. Task 7: API endpoints
8. Task 8: Migration script
9. Task 9: Testing
10. Task 10: Documentation

**Backend first, then frontend visualization in future phase.**
