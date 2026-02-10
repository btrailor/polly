# Unified Pattern Engine — Design

**Last Updated:** February 2026

---

## Architecture Overview

```
core/patterns/
├── __init__.py          # Public API exports
├── models.py            # Pattern, PatternType, PatternQuery data models
├── engine.py            # PatternEngine — main class
├── extractor.py         # Concept extraction (migrated from learners/patterns.py)
├── scorer.py            # Pattern relevance scoring (migrated from polly.py)
├── storage/
│   ├── __init__.py
│   ├── base.py          # StorageBackend protocol
│   ├── json_backend.py  # JSON file storage (fast read/write)
│   └── mem0_backend.py  # Mem0 semantic storage (search)
└── migration.py         # One-time migration from old format
```

Replaces:
- `learners/patterns.py` (archived to `learners/archive/patterns_v1.py`)
- `core/pattern_learning.py` (archived to `core/archive/pattern_learning_v1.py`)

---

## Data Model

### `Pattern` (unified)

```python
@dataclass
class Pattern:
    """A learned interaction pattern — unified model.
    
    Merges fields from both learners/patterns.Pattern and core/pattern_learning.Pattern.
    """
    id: str                          # Unique identifier (UUID or deterministic hash)
    pattern_type: PatternType        # Enum: see below
    name: str                        # Human-readable short name
    description: str                 # Detailed description
    
    # Confidence & frequency
    confidence: float                # 0.0–1.0, learned over time
    occurrences: int                 # Times observed
    last_seen: datetime              # Last observation timestamp
    created: datetime                # First observation timestamp
    
    # Activation context
    domains: list[str]               # Relevant domains (Sigils, Signals, etc.)
    keywords: list[str]              # Trigger keywords
    
    # Rich data
    examples: list[str]              # Concrete examples (from learners/patterns)
    metadata: dict[str, Any]         # Extensible metadata
    
    # Relationships (new — foundation for entity-model-unification)
    related_patterns: list[str]      # IDs of related patterns
    entity_refs: list[str]           # IDs of related entities (for future graph integration)
    
    # Source tracking
    source: str                      # "observation", "extraction", "compression", "user"
```

### `PatternType` (enum)

```python
class PatternType(str, Enum):
    # Existing types (from both systems)
    ROUTING = "routing"              # Model preferences for task types
    USER_PREFERENCE = "user_preference"  # Explicit/implicit user preferences  
    TASK_TYPE = "task_type"          # Task classification patterns
    DOMAIN = "domain"                # Domain/tag associations
    PERSONA = "persona"              # Persona behavior patterns
    
    # From learners/patterns.py
    CONCEPTUAL = "conceptual"        # Cross-concept connections
    QUERY = "query"                  # Query phrasing patterns
    CODE = "code"                    # Code pattern extraction
    DOMAIN_PRIORITY = "domain_priority"  # Domain→collection weight learning
    
    # Planned (for integration-contracts)
    WORKFLOW = "workflow"             # Multi-step workflow patterns
    AESTHETIC = "aesthetic"           # Design/theme preferences
    ROUTING_OUTCOME = "routing_outcome"  # Post-hoc routing effectiveness
```

### `PatternQuery`

```python
@dataclass
class PatternQuery:
    """Query object for searching patterns."""
    text: Optional[str] = None       # Semantic search text
    pattern_types: Optional[list[PatternType]] = None  # Filter by type
    domains: Optional[list[str]] = None  # Filter by domain
    min_confidence: float = 0.0      # Minimum confidence threshold
    limit: int = 10                  # Max results
    include_decayed: bool = False    # Include low-confidence patterns
```

---

## Storage Backend Protocol

```python
class StorageBackend(Protocol):
    """Protocol for pattern storage backends.
    
    Implementations must support basic CRUD and search.
    The engine can use multiple backends simultaneously.
    """
    
    def save(self, pattern: Pattern) -> None:
        """Save or update a pattern."""
        ...
    
    def save_batch(self, patterns: list[Pattern]) -> None:
        """Save multiple patterns efficiently."""
        ...
    
    def load_all(self) -> dict[str, Pattern]:
        """Load all patterns into memory."""
        ...
    
    def delete(self, pattern_id: str) -> None:
        """Delete a pattern by ID."""
        ...
    
    def search(self, query: PatternQuery) -> list[Pattern]:
        """Search patterns by query criteria."""
        ...
    
    def search_semantic(self, text: str, limit: int = 10) -> list[Pattern]:
        """Semantic similarity search. Backends without semantic support return []."""
        ...
```

### `JSONBackend`

- Migrated from `learners/patterns.py` JSON storage logic
- Fast in-memory dictionary with periodic file flush
- Search: keyword matching, type filtering, domain filtering
- Semantic search: returns [] (not supported)
- File: `~/.polly/patterns.json` (same location, new format with migration)

### `Mem0Backend`

- Migrated from `core/pattern_learning.py` Mem0 integration
- Stores pattern descriptions as Mem0 memories with metadata
- Search: delegates to Mem0's semantic search with reranking
- Lazy initialization (only when Mem0 is configured)
- Bidirectional sync: patterns saved to both JSON and Mem0

---

## PatternEngine Class

```python
class PatternEngine:
    """Unified pattern learning and retrieval engine.
    
    Replaces both learners/patterns.PatternLearner and core/pattern_learning.PatternLearner.
    Uses multiple storage backends simultaneously.
    """
    
    def __init__(
        self,
        json_path: Path,
        mem0_config: Optional[dict] = None,
        extractor: Optional[ConceptExtractor] = None
    ):
        # Primary storage (always active)
        self.json_backend = JSONBackend(json_path)
        
        # Semantic storage (optional, when Mem0 configured)
        self.mem0_backend = Mem0Backend(mem0_config) if mem0_config else None
        
        # Concept extraction (spaCy-based, migrated from learners/patterns.py)
        self.extractor = extractor or ConceptExtractor()
        
        # In-memory cache (loaded from JSON backend at init)
        self._patterns: dict[str, Pattern] = self.json_backend.load_all()
    
    # === Learning API ===
    
    def learn(self, pattern: Pattern) -> Pattern:
        """Learn a new pattern or reinforce an existing one.
        
        If a matching pattern exists (same type + similar description),
        reinforces it (increment occurrences, boost confidence).
        Otherwise creates a new pattern.
        
        Saves to all active backends.
        """
        ...
    
    def learn_from_query(self, query: str, domains: list[str], response: str) -> list[Pattern]:
        """Extract and learn patterns from a query-response pair.
        
        Migrated from learners/patterns.PatternLearner.record_query().
        """
        ...
    
    def learn_from_compressed(self, compressed_data: dict, conversation_id: str, rag_metadata: Optional[dict] = None) -> list[Pattern]:
        """Extract patterns from compressed conversation data.
        
        Migrated from learners/patterns.PatternLearner.learn_from_compressed().
        """
        ...
    
    def learn_domain_priorities(self, query: str, domain: str, collection_scores: dict) -> None:
        """Learn domain→collection priority weights from search results.
        
        Migrated from learners/patterns.PatternLearner.learn_domain_priorities().
        """
        ...
    
    def learn_code_patterns(self, code: str, language: str, file_path: str) -> list[Pattern]:
        """Extract code patterns from source code.
        
        Migrated from learners/patterns.PatternLearner code pattern extraction.
        """
        ...
    
    # === Search API ===
    
    def search(self, query: PatternQuery) -> list[Pattern]:
        """Search patterns across all backends, merge and rank results."""
        ...
    
    def search_semantic(self, text: str, limit: int = 10) -> list[Pattern]:
        """Semantic search — delegates to Mem0 backend when available, falls back to keyword."""
        ...
    
    def get_patterns_for_prompt(self, query: str, domains: list[str], limit: int = 5) -> list[Pattern]:
        """Get most relevant patterns for system prompt injection.
        
        Migrated from Polly._get_patterns_for_prompt() — scoring logic moves here.
        """
        ...
    
    def get_conceptual_patterns(self, concept: str) -> list[Pattern]:
        """Get cross-concept connection patterns for a concept.
        
        Migrated from learners/patterns.PatternLearner.get_conceptual_patterns_for_concept().
        """
        ...
    
    def get_domain_priorities(self, domain: str) -> dict[str, float]:
        """Get learned collection weights for a domain.
        
        Migrated from learners/patterns.PatternLearner.get_domain_priorities().
        """
        ...
    
    # === Lifecycle API ===
    
    def decay(self, half_life_days: int = 30) -> int:
        """Apply time-based confidence decay. Returns number of patterns decayed."""
        ...
    
    def prune(self, min_confidence: float = 0.1, min_occurrences: int = 1) -> int:
        """Remove low-value patterns. Returns number pruned."""
        ...
    
    def save(self) -> None:
        """Flush all changes to all backends."""
        ...
    
    def export(self) -> dict:
        """Export all patterns for analysis."""
        ...
    
    # === Stats API ===
    
    def get_stats(self) -> dict:
        """Get pattern statistics."""
        ...
```

---

## Concept Extraction (Migrated)

```python
class ConceptExtractor:
    """Extract concepts from text using NLP.
    
    Migrated from learners/patterns.py spaCy-based extraction.
    Includes 500+ technical term whitelist.
    """
    
    def __init__(self, use_spacy: bool = True):
        self._nlp = None  # Lazy-loaded spaCy model
        self.technical_terms = TECHNICAL_TERMS  # From learners/patterns.py
        self.stop_words = DOMAIN_STOP_WORDS
    
    def extract_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text."""
        ...
    
    def extract_noun_phrases(self, text: str) -> list[str]:
        """Extract noun phrases for entity candidates."""
        ...
    
    def extract_keywords(self, text: str) -> list[str]:
        """Extract keywords (lighter weight than full concept extraction)."""
        ...
```

---

## Integration Points (Updated)

### In `core/polly.py`

**Before (current):**
```python
from learners.patterns import PatternLearner
from core.pattern_learning import PatternLearner as Mem0PatternLearner

self.pattern_learner = PatternLearner(patterns_path)
self.pattern_learner_mem0 = Mem0PatternLearner(config_dict)
```

**After:**
```python
from core.patterns import PatternEngine

self.pattern_engine = PatternEngine(
    json_path=patterns_path,
    mem0_config=mem0_config if mem0_enabled else None
)
```

All call sites in `polly.py` update from `self.pattern_learner.*` / `self.pattern_learner_mem0.*` to `self.pattern_engine.*`.

### In `core/rag.py`

Currently receives `pattern_learner` for code pattern extraction:
```python
self.pattern_learner = pattern_learner  # learners/patterns.PatternLearner
```

After: receives `PatternEngine`:
```python
self.pattern_engine = pattern_engine  # core/patterns.PatternEngine
```

### In `core/domains.py`

Currently:
```python
self.pattern_learner = pattern_learner  # set via set_pattern_learner()
```

After:
```python
self.pattern_engine = pattern_engine  # set via set_pattern_engine()
```

### In `interfaces/server.py`

Pattern endpoints update to use `polly.pattern_engine.*` methods.

---

## Migration Strategy

### Data Migration

Create `core/patterns/migration.py`:

1. Read `~/.polly/patterns.json` (old format from `learners/patterns.py`)
2. Convert each pattern to new `Pattern` model
3. Preserve all fields, map old field names to new
4. Write new format to same file (with backup)
5. If Mem0 is configured, sync all patterns to Mem0 backend

### Code Migration

1. Create new `core/patterns/` package
2. Implement `PatternEngine` with all methods
3. Run old and new in parallel (dual-write) for validation
4. Switch `core/polly.py` to use new engine
5. Update all consumers
6. Archive old files

### Naming Migration (PIL → Compact Format)

In `core/compression/compressor.py` and `core/mental_models.py`:
- Rename `_compress_mental_model()` → `_compact_mental_model()` (or keep method name, update comments)
- Rename "PIL format" references to "Compact Format" in comments and docs
- Update `openspec/specs/compression/spec.md` and `openspec/specs/mental-models/spec.md`
- The abbreviation scheme stays — just the branding changes to be honest about what it is

---

## What This Enables

After this change, other systems get a clean API to build on:

| Consumer | Current (messy) | After (clean) |
|----------|----------------|---------------|
| RAG boosting | `self.pattern_learner.patterns.values()` iteration | `self.pattern_engine.search(PatternQuery(domains=..., min_confidence=0.6))` |
| Domain detection | `self.domains.pattern_learner.get_domain_priorities()` | `self.domains.pattern_engine.get_domain_priorities()` |
| Query expansion | Manual iteration + confidence check | `self.pattern_engine.get_conceptual_patterns(concept)` |
| Prompt injection | `Polly._get_patterns_for_prompt()` with merge hack | `self.pattern_engine.get_patterns_for_prompt(query, domains)` |
| Routing integration | Not connected | `self.pattern_engine.search(PatternQuery(pattern_types=[ROUTING_OUTCOME]))` |
| Persona patterns | Not connected | `self.pattern_engine.search(PatternQuery(pattern_types=[PERSONA], metadata_filter={"persona": "architect"}))` |
