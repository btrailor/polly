# Library Extraction — Design

**Last Updated:** February 2026

---

## Extraction Strategy

### Principle: Extract, Don't Rewrite

Each library is extracted from existing code, not rewritten. The steps for each:

1. Create `libs/<library>/` directory with `pyproject.toml`
2. Move existing files into the library package
3. Update imports in `core/polly.py` and other consumers
4. Add library-specific README and minimal docs
5. Verify all tests pass with new import paths

### Principle: Polly-Agnostic APIs

Each library's public API should make no assumptions about Polly. No references to "Sigils/Signals/Scrolls/Glyphs/Grids", no Polly-specific config parsing, no assumptions about the Electron frontend.

Polly-specific behavior is injected at composition time (in `core/polly.py`), not baked into the library.

---

## Library 1: `polly-routing`

**Source:** `core/router_v2.py`, `core/providers/`, `core/budget_manager.py`

### Public API

```python
# polly_routing/__init__.py
from .router import IntelligentRouter, RouteDecision, ConfidenceLevel
from .providers import ProviderAdapter, LiteLLMAdapter
from .budget import BudgetManager
from .models import ModelConfig, TaskAnalysis

# Usage (outside Polly):
router = IntelligentRouter(
    providers={"anthropic": LiteLLMAdapter("anthropic")},
    budget=BudgetManager(daily_limit=10.0)
)
decision = router.route(
    query="Explain quantum computing",
    context={"task_type": "explanation", "complexity": "high"}
)
response = await router.execute(decision, messages=[...])
```

### Package Structure

```
libs/polly-routing/
├── polly_routing/
│   ├── __init__.py
│   ├── router.py          # IntelligentRouter (from router_v2.py, generalized)
│   ├── models.py          # ModelConfig, TaskAnalysis, RouteDecision, ConfidenceLevel
│   ├── budget.py          # BudgetManager (from budget_manager.py)
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py        # ProviderAdapter protocol
│   │   └── litellm.py     # LiteLLMAdapter (from litellm_adapter.py)
│   └── analysis.py        # Task complexity analysis
├── pyproject.toml
├── README.md
└── tests/
```

### Dependencies
- `litellm` (optional — only if LiteLLM provider used)
- `aiosqlite` or `sqlite3` (budget tracking)

### What Gets Removed from Polly
- `core/router_v2.py` → import from `polly_routing`
- `core/providers/` → import from `polly_routing.providers`
- `core/budget_manager.py` → import from `polly_routing`
- `core/router.py` (v1) → archived, v1 functionality absorbed into library

### Polly-Specific Wrapper
```python
# core/polly.py
from polly_routing import IntelligentRouter, LiteLLMAdapter, BudgetManager

# Polly configures the router with its specific providers, budget, and pattern integration
self.router = IntelligentRouter(
    providers=self._build_providers(),
    budget=BudgetManager(**self._budget_config()),
    pattern_consumer=self.pattern_engine  # Integration contract
)
```

---

## Library 2: `polly-patterns`

**Source:** `core/patterns/` (after unified-pattern-engine change)

### Public API

```python
# polly_patterns/__init__.py
from .engine import PatternEngine
from .models import Pattern, PatternType, PatternQuery
from .storage import JSONBackend, Mem0Backend, StorageBackend
from .extractor import ConceptExtractor

# Usage (outside Polly):
engine = PatternEngine(
    json_path=Path("~/.myapp/patterns.json"),
    extractor=ConceptExtractor()
)
engine.learn(Pattern(
    pattern_type=PatternType.USER_PREFERENCE,
    name="prefers dark themes",
    description="User consistently chooses dark color schemes",
    confidence=0.8
))
results = engine.search(PatternQuery(text="theme preferences", limit=5))
```

### Package Structure

```
libs/polly-patterns/
├── polly_patterns/
│   ├── __init__.py
│   ├── engine.py
│   ├── models.py
│   ├── extractor.py
│   ├── scorer.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── json_backend.py
│   │   └── mem0_backend.py
│   └── migration.py
├── pyproject.toml
├── README.md
└── tests/
```

### Dependencies
- `spacy` (optional — concept extraction)
- `mem0ai` (optional — semantic storage)

---

## Library 3: `polly-compression`

**Source:** `core/compression/` (existing)

### Public API

```python
# polly_compression/__init__.py
from .manager import CompressionManager
from .compressor import ConversationCompressor, CompressedConversation
from .strategies import LLMLinguaStrategy, LLMSummaryStrategy

# Usage (outside Polly):
compressor = ConversationCompressor()
compressed = compressor.compress(conversation_messages)
summary = compressor.decompress(compressed)

# Or strategy-based:
result = compressor.compress_with_strategy(
    text=long_context,
    strategy="llmlingua",
    ratio=0.5
)
```

### Package Structure

```
libs/polly-compression/
├── polly_compression/
│   ├── __init__.py
│   ├── manager.py         # CompressionManager
│   ├── compressor.py      # ConversationCompressor
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── llmlingua.py
│   │   └── llm_summary.py
│   └── compact_format.py  # Mental model compact encoding (renamed from PIL)
├── pyproject.toml
├── README.md
└── tests/
```

### Dependencies
- `llmlingua` (optional — algorithmic compression)

---

## Library 4: `polly-entities`

**Source:** `core/entities/` (after entity-model-unification change)

### Public API

```python
# polly_entities/__init__.py
from .store import EntityStore
from .models import Entity, EntityType, Relationship, RelationshipType, EntityQuery
from .extractor import EntityExtractor
from .context import EntityContextBuilder

# Usage (outside Polly):
store = EntityStore(db_path=Path("~/.myapp/entities.db"))
extractor = EntityExtractor(store)

entities = extractor.extract_and_store(
    "FastAPI is a Python web framework used in this project",
    source_type="document",
    source_id="doc1"
)

context = EntityContextBuilder(store).build_context(
    query="How does the API work?",
    domains=["backend"]
)
```

### Package Structure

```
libs/polly-entities/
├── polly_entities/
│   ├── __init__.py
│   ├── store.py
│   ├── models.py
│   ├── extractor.py
│   ├── context.py
│   └── migration.py
├── pyproject.toml
├── README.md
└── tests/
```

### Dependencies
- `spacy` (optional — NER extraction)
- Standard library `sqlite3`

---

## Library 5: `polly-personas`

**Source:** `core/personas/` (existing)

### Public API

```python
# polly_personas/__init__.py
from .base import AgentPersona, PersonaContext, PersonaResponse, PersonaAction
from .manager import PersonaManager
from .models import PersonaMetadata, PersonaState

# Usage:
manager = PersonaManager(
    router=my_router,
    skill_manager=my_skills
)
manager.activate("architect", mode="plan")
response = await manager.process(PersonaContext(
    user_message="Help me plan this project",
    conversation_history=[...]
))
```

### Package Structure

```
libs/polly-personas/
├── polly_personas/
│   ├── __init__.py
│   ├── base.py            # AgentPersona ABC
│   ├── manager.py         # PersonaManager
│   ├── models.py          # PersonaMetadata, PersonaState
│   ├── implementations/
│   │   ├── __init__.py
│   │   ├── architect.py
│   │   ├── scribe.py
│   │   └── professor.py
│   └── definitions/       # YAML persona definitions
│       ├── architect.yaml
│       ├── scribe.yaml
│       └── professor.yaml
├── pyproject.toml
├── README.md
└── tests/
```

### Dependencies
- Requires a `Router` (uses protocol, not concrete class)
- Requires a `SkillManager` (optional)

### Note
This is the hardest to extract because personas reference Polly-specific concepts (RAG, domains, knowledge writing). The extraction requires:
- Personas declare their needs via protocols (need router, need RAG, need skill system)
- Polly injects concrete implementations at composition time
- Persona implementations remain Polly-specific but the framework is generic

---

## Monorepo Setup

### `pyproject.toml` (root)

```toml
[project]
name = "polly"
dependencies = [
    "polly-routing",
    "polly-patterns",
    "polly-compression",
    "polly-entities",
    "polly-personas",
]

[tool.setuptools.packages.find]
where = ["libs/polly-routing", "libs/polly-patterns", ...]

# Or use workspace feature if using poetry/pdm
```

### Import Updates in `core/polly.py`

```python
# Before
from .router_v2 import IntelligentRouterV2
from .compression import CompressionManager
from .patterns import PatternEngine
from .entities import EntityStore, EntityExtractor
from .personas import PersonaManager

# After
from polly_routing import IntelligentRouter
from polly_compression import CompressionManager
from polly_patterns import PatternEngine
from polly_entities import EntityStore, EntityExtractor
from polly_personas import PersonaManager
```

---

## Extraction Timeline

| Order | Library | Complexity | Can Start After |
|-------|---------|-----------|-----------------|
| 1 | `polly-routing` | Low | integration-contracts (clean interface already exists) |
| 2 | `polly-patterns` | Low | unified-pattern-engine (clean interface by design) |
| 3 | `polly-compression` | Low | Anytime (already self-contained) |
| 4 | `polly-entities` | Medium | entity-model-unification |
| 5 | `polly-personas` | High | All above (most coupled to Polly) |

**Suggested approach:** Extract one library at a time, verify all tests pass, then proceed to next. Don't attempt parallel extraction.

---

## Success Criteria

1. Each library installable independently with `pip install -e libs/polly-<name>`
2. Each library has its own test suite that passes without Polly running
3. `core/polly.py` imports from library packages, not internal paths
4. No circular dependencies between libraries
5. Each library README documents public API and usage examples
6. Library dependency graph is acyclic:
   ```
   polly-routing ← (no dependencies on other polly libs)
   polly-patterns ← (no dependencies on other polly libs)
   polly-compression ← (no dependencies on other polly libs)
   polly-entities ← (no dependencies on other polly libs)
   polly-personas ← depends on polly-routing (via protocol, not import)
   ```
