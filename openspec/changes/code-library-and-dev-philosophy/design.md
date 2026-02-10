# Code Library & Development Philosophy — Design

**Created:** February 2026  
**Impact:** Python backend (core/, interfaces/), Electron frontend, knowledge base file system (`_polly/library/`), config

---

## Part 1: Reusable Code Library

### Architecture

The Code Library lives at `_polly/library/` within the user's knowledge base. Each module is an Agent Skills-compatible directory. The registry (`registry.yml`) is the index.

```
_polly/
├── library/
│   ├── registry.yml              # Index of all modules with metadata
│   ├── patterns/                 # Abstract code patterns
│   │   ├── state-machine/
│   │   │   ├── SKILL.md
│   │   │   ├── scripts/
│   │   │   └── references/
│   │   ├── pub-sub/
│   │   ├── retry-with-backoff/
│   │   └── form-validation/
│   ├── components/               # Concrete reusable components
│   │   ├── obsidian-plugin-scaffold/
│   │   ├── ghost-api-client/
│   │   ├── tailwind-card-grid/
│   │   └── express-auth-middleware/
│   ├── prompts/                  # Reusable prompt templates
│   │   ├── code-review/
│   │   ├── architecture-decision/
│   │   └── refactor-plan/
│   └── workflows/                # Multi-step processes
│       ├── new-project-setup/
│       ├── deploy-to-docker/
│       └── obsidian-to-ghost/
```

### Module Format (Agent Skills Compatible)

Each module directory contains:

```
retry-with-backoff/
├── SKILL.md          # Required: YAML frontmatter + markdown instructions
├── scripts/          # Optional: executable implementations
│   └── retry.ts
├── references/       # Optional: detailed docs, pattern variations
│   └── patterns.md
└── assets/           # Optional: templates, config files
    └── template.ts
```

### SKILL.md Schema

```yaml
---
name: retry-with-backoff
description: >
  Implements retry logic with exponential backoff and jitter. Use when
  building API clients, webhook handlers, or any network-dependent code.
  Supports configurable max retries, base delay, and circuit breaker patterns.
metadata:
  author: polly                   # "polly" for auto-extracted, user name for manual
  version: "1.2"
  language: [typescript, python]  # Supported languages
  domain: sigils                  # Polly domain (Sights, Sigils, Signals, Scrolls, Glyphs)
  category: patterns              # patterns | components | prompts | workflows
  tags: [networking, resilience, async]
  created_from: ghost-api-client  # Provenance: which project spawned this
  confidence: 0.85                # 0.0–1.0, increases with use
  times_used: 7
  last_used: 2026-02-08
  dependencies: []                # Other library modules this depends on
---

# Retry with Exponential Backoff

## When to Use
- API client implementations
- Webhook delivery systems
- Any operation that can fail transiently

## When NOT to Use
- Operations that should fail fast (user-initiated cancellations)
- Non-idempotent operations without careful consideration

## Implementation Notes
- Always include jitter to prevent thundering herd
- Circuit breaker threshold should be configurable
- Log retry attempts at debug level, final failure at error level

## Usage
See `scripts/retry.ts` for TypeScript implementation.
See `references/patterns.md` for pattern variations.
```

### Registry Schema (`registry.yml`)

```yaml
version: 1
updated: 2026-02-09T12:00:00Z
modules:
  - name: retry-with-backoff
    path: patterns/retry-with-backoff
    category: patterns
    confidence: 0.85
    times_used: 7
    last_used: 2026-02-08
    languages: [typescript, python]
    domain: sigils
    tags: [networking, resilience, async]
    created_from: ghost-api-client
    depends_on: []
  - name: ghost-api-client
    path: components/ghost-api-client
    category: components
    confidence: 0.9
    times_used: 3
    last_used: 2026-02-05
    languages: [typescript]
    domain: scrolls
    tags: [api, cms, publishing]
    created_from: blog-publisher
    depends_on: [retry-with-backoff]
```

### Key Types (Python Backend)

```python
# core/code_library/models.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class ModuleCategory(str, Enum):
    PATTERNS = "patterns"
    COMPONENTS = "components"
    PROMPTS = "prompts"
    WORKFLOWS = "workflows"

@dataclass
class LibraryModule:
    """A reusable code module in Polly's library."""
    name: str
    path: str                               # Relative path within _polly/library/
    category: ModuleCategory
    description: str
    author: str = "polly"
    version: str = "1.0"
    languages: list[str] = field(default_factory=list)
    domain: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.5                 # 0.0–1.0
    times_used: int = 0
    last_used: Optional[datetime] = None
    created_from: Optional[str] = None      # Project provenance
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExtractionCandidate:
    """A code pattern Polly recognizes as having reuse potential."""
    source_code: str
    source_file: str
    source_project: Optional[str] = None
    pattern_type: ModuleCategory = ModuleCategory.PATTERNS
    suggested_name: str = ""
    abstraction_notes: str = ""             # What to parameterize
    confidence: float = 0.5                 # How reusable this looks
    languages: list[str] = field(default_factory=list)

@dataclass
class LibrarySearchResult:
    """Result from searching the library."""
    module: LibraryModule
    relevance_score: float
    match_reason: str                       # "tag_match", "semantic", "name"
```

### Core API (Python Backend)

```python
# core/code_library/manager.py

class CodeLibraryManager:
    """Manages Polly's reusable code library."""
    
    def __init__(self, config, library_path: str, rag=None):
        """
        Args:
            config: Polly config object
            library_path: Path to _polly/library/
            rag: Optional RAG instance for semantic search
        """
    
    # --- Registry ---
    def load_registry(self) -> dict:
        """Load registry.yml into memory."""
    
    def save_registry(self) -> None:
        """Persist registry.yml to disk."""
    
    # --- Module CRUD ---
    def list_modules(self, category: str = None, domain: str = None,
                     language: str = None, tags: list[str] = None) -> list[LibraryModule]:
        """List modules with optional filters."""
    
    def get_module(self, name: str) -> LibraryModule:
        """Get a single module by name."""
    
    def create_module(self, module: LibraryModule, skill_md: str,
                      scripts: dict[str, str] = None,
                      references: dict[str, str] = None) -> LibraryModule:
        """Create a new module directory with SKILL.md and optional files."""
    
    def update_module(self, name: str, updates: dict) -> LibraryModule:
        """Update module metadata and/or content."""
    
    def delete_module(self, name: str) -> bool:
        """Remove a module from the library."""
    
    # --- Search ---
    def search(self, query: str, limit: int = 10) -> list[LibrarySearchResult]:
        """Search library modules. Uses RAG semantic search + tag/name matching."""
    
    # --- Usage Tracking ---
    def record_usage(self, name: str, project: str = None) -> None:
        """Record that a module was used. Increments times_used, updates last_used."""
    
    def get_stats(self) -> dict:
        """Library statistics: total modules, by category, most/least used, etc."""
    
    # --- Extraction ---
    def extract_module(self, candidate: ExtractionCandidate) -> LibraryModule:
        """Extract a reusable module from code. Strips project-specific details,
        parameterizes configuration, writes SKILL.md."""
    
    def suggest_extractions(self, code: str, file_path: str) -> list[ExtractionCandidate]:
        """Analyze code for abstraction opportunities. Returns candidates."""
    
    # --- Application ---
    def apply_module(self, name: str, target_path: str,
                     config: dict = None) -> str:
        """Instantiate a module in the current project.
        Adapts template to project conventions, records usage."""
    
    # --- Review ---
    def review_code(self, code: str, context: str = "") -> dict:
        """AI Slop review pass. Checks for unnecessary abstraction, boilerplate,
        inconsistent patterns, missing error handling, over-commenting, dependency creep."""
```

### AI Slop Review Skill

The review pass is itself a library module at `_polly/library/prompts/code-review/SKILL.md`. Any persona can invoke it. Checks for:

1. **Unnecessary abstraction** — Does this layer actually serve a purpose?
2. **Boilerplate bloat** — Can this be simplified?
3. **Inconsistent patterns** — Does this match existing library conventions?
4. **Missing error handling** — Production-readiness check
5. **Over-commenting** — AI tends to over-explain in comments
6. **Dependency creep** — Is this npm package actually necessary?

The review skill itself improves over time as it learns the user's style preferences (via pattern learning integration).

### Multi-Model Routing for Library Operations

Library operations are routed to cost-appropriate models:

| Operation | Model Tier | Rationale |
|-----------|-----------|-----------|
| Pattern extraction from code | Free/Budget | Mostly mechanical analysis |
| Code formatting and linting | Free/Budget | Rule-based, low complexity |
| Template instantiation | Free/Budget | Parameter substitution |
| Registry indexing | Free/Budget | Metadata operations |
| AI Slop review (rule checks) | Free/Budget | Checking against known rules |
| Documentation generation | Free/Budget | Structured output from code |
| Novel abstraction design | Frontier | Creative architectural decisions |
| Cross-domain pattern recognition | Frontier | Requires broad understanding |
| Complex code review | Frontier | Nuanced understanding needed |
| User-facing explanations | Frontier | Quality matters for teaching |

Integration with existing LiteLLM adapter: Library operations pass a `task_type` to the router, which uses the routing table to select the appropriate model tier.

### Library → Pattern Learning Integration

The library and pattern learning system form a promotion pipeline:

```
Observation (PatternLearner)
  │
  ├── Low-confidence pattern (stored in patterns.json)
  │     └── Reinforced over time → confidence increases
  │
  ├── High-confidence code pattern (confidence > 0.8)
  │     └── Candidate for library extraction
  │           └── Polly suggests: "This pattern generalizes well. Extract to library?"
  │
  └── Library module (SKILL.md + scripts)
        ├── Used in new projects → record_usage()
        ├── Edge cases found → refinement
        └── Pattern learning tracks library_usage patterns
```

New pattern type added to `patterns/spec.md`:

```python
# Library usage pattern
Pattern(
    type="library_usage",
    description="Module retry-with-backoff applied in ghost-api-client, webhook-handler",
    confidence=0.9,
    metadata={
        "module": "retry-with-backoff",
        "projects": ["ghost-api-client", "webhook-handler"],
        "times_applied": 7
    }
)
```

### RAG Integration

Library modules are indexed in a `code-library` ChromaDB collection (separate from `notes`, `code`, `library`/BookLore):

```python
# Indexing
rag.index_document(
    content=skill_md_content,
    collection="code-library",
    metadata={
        "source_type": "code-library",
        "module_name": "retry-with-backoff",
        "category": "patterns",
        "languages": ["typescript", "python"],
        "domain": "sigils",
        "tags": ["networking", "resilience"]
    }
)

# Search
results = rag.search(
    query="How do I handle API failures with retries?",
    collections=["code-library"],
    limit=5
)
```

### Persona ↔ Library Relationships

| Persona | Library Role | Details |
|---------|-------------|---------|
| **Programmer** | Primary producer + consumer | Extracts patterns during coding, applies modules in new projects. Runs scripts directly. |
| **Architect** | Reviewer + strategist | Reviews library for architectural patterns. Uses `prompts/architecture-decision/`. Suggests composing existing modules over writing from scratch. |
| **Designer** | Component consumer | Accesses `components/` for UI patterns (Tailwind grids, card layouts). Could contribute generative assets. |
| **Librarian** | Indexer + retriever | Handles RAG layer connecting natural language queries to library entries. Organizes, tags, suggests connections. |
| **Scribe** | Documenter | Documents library additions in session notes. Creates changelogs for the library itself. |
| **Professor** | Teacher | Uses library modules as teaching examples. "Here's how retry-with-backoff works..." |
| **Administrator** | Maintainer | Library health: stale modules, unused modules, dependency audit. |

---

## Part 2: Development Philosophy Configuration

### Spectrum Definitions

Spectrums are defined in a config file, extensible by users:

```yaml
# config/philosophy_spectrums.yaml

spectrums:
  - id: open-constrained
    name: "Open Tool ↔ Constraint-Based"
    left:
      label: "Open"
      description: "Maximum flexibility, user configures everything"
    right:
      label: "Constrained"
      description: "Opinionated defaults, fewer choices, clearer path"
    context_questions:
      - "Who will use this? How technical are they?"
      - "Is this a tool for you or for others?"
    connection: "Bogost: Constraints create meaning. But which constraints, and for whom?"

  - id: friendly-powerful
    name: "User-Friendly ↔ Powerful"
    left:
      label: "Friendly"
      description: "Low learning curve, progressive disclosure"
    right:
      label: "Powerful"
      description: "Full capability surface, assumes competent user"
    context_questions:
      - "Will new users need to be productive immediately?"
      - "What's the cost of a wrong action?"

  - id: convention-configuration
    name: "Convention ↔ Configuration"
    left:
      label: "Convention"
      description: "Do it this way (Rails, Next.js)"
    right:
      label: "Configuration"
      description: "Set it up however you want (Express, Vite)"
    context_questions:
      - "Do you want speed-to-start or flexibility-to-change?"
      - "How many developers will work on this?"

  - id: local-cloud
    name: "Local-First ↔ Cloud-Native"
    left:
      label: "Local"
      description: "Data sovereignty, offline capability, privacy"
    right:
      label: "Cloud"
      description: "Collaboration, sync, scale"
    context_questions:
      - "Does the data need to stay on-device?"
      - "Will multiple people collaborate on this?"

  - id: build-buy
    name: "Build ↔ Buy (Integrate)"
    left:
      label: "Build"
      description: "Custom implementation, full control"
    right:
      label: "Buy"
      description: "Use existing tools/services, faster to market"
    context_questions:
      - "Is this core to your value proposition?"
      - "What's the cost of depending on a third party?"
    connection: "Graeber: What is meaningful work vs. just reinventing?"

  - id: mvp-architecture
    name: "MVP ↔ Architecture-First"
    left:
      label: "MVP"
      description: "Ship something, learn from real usage"
    right:
      label: "Architecture"
      description: "Design properly, avoid rework"
    context_questions:
      - "How much will the requirements change?"
      - "What's the cost of rework vs. the cost of delay?"
    connection: "Reverse engineering tension: start from outcome but need working systems fast."
```

### Guided Process (Three Phases)

#### Phase 1: Project Framing (Architect persona leads)

Polly asks structured questions:
- What is this project? (description, scope)
- Who is it for? (audience, technical level)
- What's the deployment target? (local, web, mobile, embedded)
- What's the time horizon? (weekend hack, long-term instrument, production app)

#### Phase 2: Spectrum Positioning (Conversational)

For each spectrum, Polly presents tradeoffs in the context of the specific project. This is a thinking exercise, not a quiz:

> "For a personal norns script, constraint-based makes sense — you know the hardware, the audience is you. But for Polly itself, you need to balance open extensibility with opinionated defaults. Where do you want to start?"

Output: numeric position (0–100) per spectrum, plus user's rationale.

#### Phase 3: Philosophy Document Generation

Output: `development-philosophy.md` in the project root.

### Philosophy Document Schema

```yaml
---
project: polly
created: 2026-02-09
author: brett
last_reviewed: 2026-02-09
review_cadence: monthly  # or milestone-based
---
```

Followed by markdown sections:
- **Positioning** — Table of spectrum positions with rationale
- **Non-Negotiables** — Hard constraints that don't bend
- **Technical Commitments** — Stack, formats, storage
- **Design Principles** — Project-specific principles (connects to Polly's design spec)

### Philosophy → Persona Integration

The philosophy document is injected into persona system prompts as context, similar to how themes are injected:

```
System prompt = [
  base_persona_prompt,
  active_mode_instructions,
  theme_behavior_context,
  philosophy_context,           ← NEW: from development-philosophy.md
  active_skills,
  user_instructions
]
```

Priority hierarchy (lowest to highest):
1. Persona base behavior
2. Active theme behavior
3. Project philosophy context
4. Active skills
5. Explicit user instruction

### Philosophy Review / Drift Detection (Future)

At configured intervals or milestones, Polly prompts review:

> "You're six weeks into Polly development. Your philosophy said 'architecture-informed MVP' but you've been deep in architecture without shipping. Want to revisit that positioning?"

### Key Types (Python Backend)

```python
# core/philosophy/models.py

@dataclass
class SpectrumPosition:
    """A project's position on one development spectrum."""
    spectrum_id: str
    position: int               # 0–100 (0 = full left, 100 = full right)
    rationale: str
    
@dataclass  
class DevelopmentPhilosophy:
    """A project's development philosophy configuration."""
    project: str
    author: str
    created: datetime
    last_reviewed: datetime
    review_cadence: str         # "monthly", "milestone", "weekly"
    positions: list[SpectrumPosition]
    non_negotiables: list[str]
    technical_commitments: list[str]
    design_principles: list[str]
```

### Core API (Python Backend)

```python
# core/philosophy/manager.py

class PhilosophyManager:
    """Manages development philosophy configuration."""
    
    def __init__(self, config, spectrums_path: str = None):
        """Load spectrum definitions from config."""
    
    def get_spectrums(self) -> list[dict]:
        """Return all available spectrum definitions."""
    
    def add_spectrum(self, spectrum: dict) -> None:
        """Add a custom spectrum definition."""
    
    def init_philosophy(self, project: str, responses: dict) -> DevelopmentPhilosophy:
        """Create a new philosophy from guided process responses."""
    
    def load_philosophy(self, path: str) -> DevelopmentPhilosophy:
        """Load an existing development-philosophy.md."""
    
    def save_philosophy(self, philosophy: DevelopmentPhilosophy, path: str) -> None:
        """Save philosophy to markdown file."""
    
    def get_philosophy_context(self, philosophy: DevelopmentPhilosophy) -> str:
        """Generate persona system prompt context from philosophy."""
    
    def check_alignment(self, philosophy: DevelopmentPhilosophy, 
                         code_analysis: dict) -> dict:
        """Compare current code patterns against stated philosophy.
        Returns alignment report with suggestions."""
    
    def suggest_review(self, philosophy: DevelopmentPhilosophy,
                        project_metrics: dict) -> Optional[str]:
        """Check if it's time for a philosophy review. Returns prompt or None."""
```

---

## Part 3: Slash Commands

### Library Commands

| Command | Description | Persona |
|---------|-------------|---------|
| `/library search <query>` | RAG search across all modules | Librarian |
| `/library extract` | Extract current code into a new module | Programmer |
| `/library apply <module>` | Instantiate a module in current project | Programmer |
| `/library review` | Run AI Slop review on current file/selection | Programmer |
| `/library stats` | Usage statistics, most/least used modules | Administrator |

### Philosophy Commands

| Command | Description | Persona |
|---------|-------------|---------|
| `/philosophy init` | Start guided configuration for new project | Architect |
| `/philosophy review` | Revisit current project philosophy | Architect |
| `/philosophy check` | Compare current code against stated philosophy | Architect |
| `/philosophy spectrum <name>` | Deep-dive into a specific spectrum | Architect |

### Meta Commands

| Command | Description | Persona |
|---------|-------------|---------|
| `/model status` | Show current model routing table | Administrator |
| `/model route <task> <model>` | Override routing for a specific task | Administrator |
| `/cost report` | Token usage and cost breakdown by model tier | Administrator |

### Slash Command Backend

```python
# core/commands/registry.py

class SlashCommandRegistry:
    """Registry for all slash commands across library, philosophy, and meta."""
    
    def register(self, command: str, handler: callable, persona: str = None,
                 description: str = "", args: list[str] = None) -> None:
        """Register a slash command."""
    
    def execute(self, command_str: str, context: dict) -> dict:
        """Parse and execute a slash command. Returns result dict."""
    
    def list_commands(self, category: str = None) -> list[dict]:
        """List available commands, optionally filtered by category."""
```

---

## REST API Endpoints

### Library

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/library/modules` | List modules (filterable) |
| `GET` | `/api/library/modules/<name>` | Get module detail |
| `POST` | `/api/library/modules` | Create a module |
| `PUT` | `/api/library/modules/<name>` | Update a module |
| `DELETE` | `/api/library/modules/<name>` | Delete a module |
| `POST` | `/api/library/search` | Search library (RAG) |
| `POST` | `/api/library/extract` | Extract module from code |
| `POST` | `/api/library/apply/<name>` | Apply module to project |
| `POST` | `/api/library/review` | AI Slop review |
| `GET` | `/api/library/stats` | Library statistics |

### Philosophy

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/philosophy/spectrums` | List spectrum definitions |
| `POST` | `/api/philosophy/spectrums` | Add custom spectrum |
| `POST` | `/api/philosophy/init` | Start guided process |
| `GET` | `/api/philosophy/current` | Get current project philosophy |
| `PUT` | `/api/philosophy/current` | Update philosophy |
| `POST` | `/api/philosophy/check` | Run alignment check |

### Commands

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/commands/execute` | Execute a slash command |
| `GET` | `/api/commands/list` | List available commands |

---

## Frontend Impact

### Electron App Changes

1. **Library Page** — New ribbon page for browsing/searching the code library
   - Module browser (grid/list view by category)
   - Module detail view (SKILL.md rendered, scripts, usage stats)
   - Search bar (connected to RAG)
   - Extract button (when code workspace is available, Phase 17)

2. **Philosophy Panel** — Accessible from Settings or as standalone guided flow
   - Spectrum positioning sliders (visual)
   - Guided conversation flow
   - Philosophy document preview/edit

3. **Slash Command Bar** — Chat input recognizes `/` prefix
   - Autocomplete for available commands
   - Results displayed inline in chat or as panels

4. **AI Slop Review** — Results displayed as inline annotations or panel

### Config Additions

```yaml
# In config/config.yaml

library:
  enabled: true
  path: "_polly/library"           # Relative to knowledge base
  auto_extract: false              # Auto-suggest extractions during coding
  auto_extract_confidence: 0.8    # Minimum pattern confidence for suggestion
  review_on_extract: true          # Run AI Slop review on new modules
  rag_collection: "code-library"   # ChromaDB collection name

philosophy:
  enabled: true
  spectrums_path: "config/philosophy_spectrums.yaml"
  review_cadence: "monthly"
  inject_into_prompts: true        # Add philosophy context to persona prompts

model_routing:
  library_operations:
    extraction: "free"             # Model tier for pattern extraction
    formatting: "free"
    indexing: "free"
    review_basic: "free"
    review_complex: "frontier"
    abstraction_design: "frontier"
    documentation: "free"
```

---

## Performance Considerations

- **Module indexing:** Background task, ~1 second per module (SKILL.md + scripts embedding)
- **Library search:** Same latency as RAG (~100–500ms)
- **Pattern extraction:** LLM call, 2–10 seconds depending on code size and model tier
- **Philosophy generation:** Multi-turn conversation, user-paced
- **Slash command parsing:** <10ms (regex + registry lookup)
- **Registry load:** <50ms for 100+ modules (YAML parse)

## File Organization (New Backend Files)

```
core/
├── code_library/
│   ├── __init__.py
│   ├── models.py              # LibraryModule, ExtractionCandidate, etc.
│   ├── manager.py             # CodeLibraryManager
│   ├── extractor.py           # Pattern recognition and extraction
│   ├── reviewer.py            # AI Slop review implementation
│   └── registry.py            # Registry I/O (YAML)
├── philosophy/
│   ├── __init__.py
│   ├── models.py              # DevelopmentPhilosophy, SpectrumPosition
│   ├── manager.py             # PhilosophyManager
│   └── guided_process.py      # Three-phase guided conversation
├── commands/
│   ├── __init__.py
│   ├── registry.py            # SlashCommandRegistry
│   ├── library_commands.py    # /library subcommands
│   ├── philosophy_commands.py # /philosophy subcommands
│   └── meta_commands.py       # /model, /cost subcommands
```

## Reference

- Agent Skills spec: https://agentskills.io
- Existing pattern system: [patterns spec](../../specs/patterns/spec.md)
- Existing personas: [personas spec](../../specs/personas/spec.md)
- Design philosophy: [design spec](../../specs/design/spec.md)
- LiteLLM routing: [core-framework-refinement](../core-framework-refinement/)
