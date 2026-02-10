# Code Library — Reusable Code Modules (OpenSpec)

Source of truth for Polly's reusable code library system. The Code Library is distinct from BookLore (the [ebook library](../library/spec.md)): BookLore manages reading material; the Code Library manages reusable code patterns, components, prompts, and workflows that Polly builds as a byproduct of working.

## Overview

As Polly writes code across projects, she recognizes abstract patterns and packages them into reusable modules. The library isn't static — it's a living instrument that grows through use. Polly doesn't just use code libraries; she builds them as a byproduct of working.

This connects to the "instruments over tracks" practice: the library is an instrument Polly plays across projects, not a collection of finished tracks.

**Format:** Agent Skills compatible (SKILL.md + scripts/references/assets). Portable across agent platforms (Claude Code, Codex, Kilo Code, VS Code Copilot).

---

## Architecture

### Storage

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

### Module Categories

| Category | What | Examples |
|----------|------|---------|
| **patterns** | Abstract code patterns, language-agnostic | State machine, pub-sub, retry-with-backoff, form validation |
| **components** | Concrete reusable components | Plugin scaffolds, API clients, UI grids, auth middleware |
| **prompts** | Reusable prompt templates | Code review, architecture decision, refactor plan |
| **workflows** | Multi-step processes | Project setup, deployment, migration pipelines |

---

## Module Format (Agent Skills Compatible)

Each module is a directory with a required `SKILL.md` file and optional subdirectories:

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
metadata:
  author: polly                   # "polly" for auto-extracted, user name for manual
  version: "1.2"
  language: [typescript, python]
  domain: sigils                  # Polly domain
  category: patterns              # patterns | components | prompts | workflows
  tags: [networking, resilience, async]
  created_from: ghost-api-client  # Provenance tracking
  confidence: 0.85                # 0.0–1.0, increases with use
  times_used: 7
  last_used: 2026-02-08
  dependencies: []
---

# Retry with Exponential Backoff

## When to Use
- API client implementations
- Webhook delivery systems
- Any operation that can fail transiently

## When NOT to Use
- Operations that should fail fast
- Non-idempotent operations without careful consideration

## Implementation Notes
- Always include jitter to prevent thundering herd
- Circuit breaker threshold should be configurable
- Log retry attempts at debug level, final failure at error level

## Usage
See `scripts/retry.ts` for TypeScript implementation.
See `references/patterns.md` for pattern variations.
```

### Progressive Disclosure

Following the Agent Skills spec, module loading is progressive:
1. **Metadata** (~100 bytes): Name, description from frontmatter — loaded for registry browsing
2. **Instructions** (~2–5K tokens): Full SKILL.md content — loaded when module is activated
3. **Scripts/References** (on demand): Executable code and detailed docs — loaded when applied

---

## Registry (`registry.yml`)

The registry is the index of all modules. It enables fast listing, filtering, and usage tracking without reading every SKILL.md.

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
```

---

## How Polly Builds the Library

The library grows through four mechanisms:

### 1. Pattern Recognition During Coding

As Polly writes code, she maintains awareness of abstraction opportunities. When she implements something with reuse potential, she flags it:

> "I just built retry logic for the Ghost API client. This pattern generalizes well. Want me to extract it into the library?"

Or, more autonomously (when `auto_extract` is enabled): Polly extracts silently and mentions it in a session summary.

### 2. Abstraction Extraction

Polly doesn't copy-paste. She:
- Strips project-specific details (hardcoded paths, API keys, project names)
- Parameterizes configuration (constants become config parameters)
- Writes the SKILL.md with usage context (when to use, when not to)
- Creates reference implementations in relevant languages
- Tags with domain for cross-domain retrieval

### 3. Registry Maintenance

`registry.yml` tracks:
- All modules with metadata
- Usage frequency (explore vs. exploit signal)
- Provenance (which project spawned this module)
- Dependencies between modules
- Confidence level (battle-tested vs. first extraction)

### 4. Progressive Refinement

Each time a module is used, Polly can:
- Improve the implementation based on new edge cases
- Expand language support
- Update the SKILL.md with better documentation
- Increment usage counter

### Confidence Lifecycle

- New modules start at confidence `0.5`
- Confidence increases `+0.05` per use (capped at `1.0`)
- Confidence decays `2%` per month after 90 days of inactivity
- Modules with confidence below `0.2` flagged for review or pruning

---

## Pattern → Library Promotion Pipeline

The Code Library is where high-confidence patterns graduate to:

```
Observation (PatternLearner)
  │
  ├── Low-confidence pattern (stored in patterns.json)
  │     └── Reinforced over time → confidence increases
  │
  ├── High-confidence code pattern (confidence > 0.8)
  │     └── Candidate for library extraction
  │           └── Polly suggests: "Extract to library?"
  │
  └── Library module (SKILL.md + scripts)
        ├── Used in new projects → record_usage()
        ├── Edge cases found → refinement
        └── Pattern learning tracks library_usage patterns
```

New pattern type: `library_usage` — tracks which library modules are applied where, how often, and with what results.

---

## AI Slop Review

Before code reaches the library or the user's project, a review pass checks for:

1. **Unnecessary abstraction** — Does this layer actually serve a purpose?
2. **Boilerplate bloat** — Can this be simplified?
3. **Inconsistent patterns** — Does this match existing library conventions?
4. **Missing error handling** — Production-readiness check
5. **Over-commenting** — AI tends to over-explain in comments
6. **Dependency creep** — Is this npm package actually necessary?

Implemented as a library module itself (`_polly/library/prompts/code-review/`). Any persona can invoke it. The review skill improves over time as it learns the user's style preferences.

---

## Multi-Model Cost Optimization

Library operations are routed to cost-appropriate models:

| Operation | Model Tier | Rationale |
|-----------|-----------|-----------|
| Pattern extraction from code | Free/Budget | Mostly mechanical |
| Code formatting and linting | Free/Budget | Rule-based |
| Template instantiation | Free/Budget | Parameter substitution |
| Registry indexing | Free/Budget | Metadata operations |
| AI Slop review (rule checks) | Free/Budget | Against known rules |
| Documentation generation | Free/Budget | Structured output |
| Novel abstraction design | Frontier | Creative decisions |
| Cross-domain pattern recognition | Frontier | Broad understanding |
| Complex code review | Frontier | Nuanced understanding |
| User-facing explanations | Frontier | Quality matters |

**Key insight from Kilo Code:** Free models handle 50%+ of coding tasks competently. Reserve expensive models for genuinely hard problems.

---

## Design Assets as Library Modules

The Designer persona produces three types of library-compatible output:

### Design Components

UI components built and styled within a design system become library modules:

```
_polly/library/components/tailwind-card-grid/
├── SKILL.md              # Description, design system requirements
├── scripts/
│   └── card-grid.tsx     # Implementation
├── references/
│   └── design-notes.md   # Design decisions, accessibility notes
└── assets/
    └── preview.svg       # Visual preview
```

### Generator Scripts as Instruments

p5.js sketches that produce design assets are reusable instruments — parameterized for any project:

```
_polly/library/workflows/lucide-icon-generator/
├── SKILL.md              # How to use, Lucide rules, customization points
├── scripts/
│   └── generator.js      # Parametric p5.js sketch
├── references/
│   └── lucide-rules.md   # Full Lucide design guidelines
└── assets/
    └── template.svg      # Base SVG template
```

The generator with Lucide constraints can be reused across projects — change the glyphs, keep the visual grammar. This is the "instruments over tracks" principle applied to design.

### Design System Templates

A well-developed `system.yml` becomes a starting point for new projects:

```
_polly/library/workflows/design-system-starter/
├── SKILL.md              # How to customize, which tokens to change
├── assets/
│   ├── system.yml        # Template system with placeholder values
│   └── directory.md      # _design/ structure documentation
```

See [personas spec — Designer](../personas/spec.md) and the [designer-profile change](../../changes/designer-profile/) for full details.

---

## Persona Integration

| Persona | Library Role |
|---------|-------------|
| **Programmer** | Primary code producer + consumer. Extracts patterns during coding, applies modules in new projects. Runs scripts directly. |
| **Designer** | Design producer + consumer. Generates design components, icon generator scripts, and design system templates as library modules. Accesses `components/` for UI patterns. |
| **Architect** | Reviews library for architectural patterns. Uses `prompts/architecture-decision/`. Suggests composing existing modules. |
| **Librarian** | Indexes and retrieves modules. Handles RAG layer. "I need retry logic" → `patterns/retry-with-backoff/`. |
| **Scribe** | Documents library additions. Creates changelogs. |
| **Professor** | Uses modules as teaching examples. |
| **Administrator** | Library health: stale modules, unused modules, dependency audit. |

---

## RAG Integration

Library modules indexed in a `code-library` ChromaDB collection (separate from `notes`, `code`, `library`/BookLore):

```
ChromaDB Collections:
  ├── notes          (personal notes, captures)
  ├── code           (code files, GitHub repos)
  ├── library        (ebook content — BookLore)
  └── code-library   (reusable code modules)
```

Metadata per chunk: module name, category, languages, domain, tags, confidence.

---

## Slash Commands

| Command | Description | Persona |
|---------|-------------|---------|
| `/library search <query>` | RAG search across all modules | Librarian |
| `/library extract` | Extract current code into a new module | Programmer |
| `/library apply <module>` | Instantiate a module in current project | Programmer |
| `/library review` | Run AI Slop review on current file/selection | Programmer |
| `/library stats` | Usage statistics, most/least used modules | Administrator |

---

## API

### Core (`core/code_library/manager.py`)

```python
manager = CodeLibraryManager(config, library_path, rag)

# CRUD
modules = manager.list_modules(category="patterns", language="typescript")
module = manager.get_module("retry-with-backoff")
module = manager.create_module(module, skill_md, scripts, references)
module = manager.update_module("retry-with-backoff", updates)
manager.delete_module("retry-with-backoff")

# Search
results = manager.search("API failure handling", limit=10)

# Usage
manager.record_usage("retry-with-backoff", project="ghost-api-client")
stats = manager.get_stats()

# Extraction
candidates = manager.suggest_extractions(code, file_path)
module = manager.extract_module(candidate)

# Application
output = manager.apply_module("retry-with-backoff", target_path, config)

# Review
review = manager.review_code(code, context)
```

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/library/modules` | List modules (filterable) |
| `GET` | `/api/library/modules/<name>` | Module detail |
| `POST` | `/api/library/modules` | Create module |
| `PUT` | `/api/library/modules/<name>` | Update module |
| `DELETE` | `/api/library/modules/<name>` | Delete module |
| `POST` | `/api/library/search` | Search library (RAG) |
| `POST` | `/api/library/extract` | Extract module from code |
| `POST` | `/api/library/apply/<name>` | Apply module to project |
| `POST` | `/api/library/review` | AI Slop review |
| `GET` | `/api/library/stats` | Statistics |

---

## UI

### Library Page

New page in ribbon navigation:
- **Module browser:** Grid/list view by category. Search bar. Module cards with name, description, languages, usage count, confidence badge.
- **Module detail:** Rendered SKILL.md, scripts listing, usage history, "Apply to project" button.
- **Stats sidebar:** Total modules by category, most/least used, recently added.
- **Empty state:** "Polly will build your library as you work."

---

## Config

```yaml
# In config/config.yaml
library:
  enabled: true
  path: "_polly/library"
  auto_extract: false
  auto_extract_confidence: 0.8
  review_on_extract: true
  rag_collection: "code-library"
```

---

## Ecosystem Context

The Code Library design draws from and is compatible with:

- **Agent Skills (agentskills.io)** — Primary format. SKILL.md + scripts/references/assets. Portable across agent platforms.
- **awesome-cursorrules** — Demonstrates appetite for shareable AI coding context. Code Library modules are more structured (progressive disclosure, modular).
- **ample-education/cursor-resources** — Global vs. project-specific rules. Library is the global layer; project philosophy is the project-specific layer.
- **promptz.dev** — Taxonomy inspiration: Libraries, Prompts, Agents, Powers, Steering, Hooks. Code Library categories (patterns, components, prompts, workflows) map to this.
- **Kilo Code** — Multi-model cost optimization. Free models for 50%+ of library operations.

---

## Relationship to Other Systems

| System | Integration |
|--------|-------------|
| **Patterns** (Phase 13a) | High-confidence code patterns promoted to library modules. New `library_usage` pattern type. |
| **Personas** | Each persona has defined library role (producer, consumer, reviewer, indexer, documenter). |
| **RAG** | `code-library` ChromaDB collection. Semantic search for `/library search`. |
| **Agent Swarms** | Nexus can invoke library modules. Library extraction as swarm workflow. |
| **BookLore** | Separate system. BookLore = reading material. Code Library = reusable code. Both under `_polly/` but distinct. |
| **LiteLLM routing** | Library operations pass `task_type` for cost-appropriate model selection. |
| **Phase 17 (Monaco)** | Full extract/apply UX requires code workspace. Library is useful before Phase 17 via chat. |
| **Phase 25 (Programmer)** | Primary library persona. Library format designed for Programmer workflows. |
| **Phase 28 (Open Polly Tools)** | Library modules are the unit of sharing in the plugin ecosystem. |

---

## Implementation Files

| File | Purpose |
|------|---------|
| `core/code_library/__init__.py` | Package |
| `core/code_library/models.py` | LibraryModule, ExtractionCandidate, etc. |
| `core/code_library/manager.py` | CodeLibraryManager |
| `core/code_library/extractor.py` | Pattern recognition and extraction |
| `core/code_library/reviewer.py` | AI Slop review |
| `core/code_library/registry.py` | Registry I/O (YAML) |
| `interfaces/library_api.py` | REST endpoints |
| `_polly/library/registry.yml` | Module registry |
| `_polly/library/prompts/code-review/SKILL.md` | Bootstrap review skill |

---

## Reference

- Change folder: [openspec/changes/code-library-and-dev-philosophy/](../../changes/code-library-and-dev-philosophy/)
- Agent Skills spec: https://agentskills.io
- Pattern learning: [patterns spec](../patterns/spec.md)
- Personas: [personas spec](../personas/spec.md)
- BookLore (ebook library): [library spec](../library/spec.md)
- Design philosophy: [design spec](../design/spec.md)
- Development philosophy: [dev-philosophy spec](../dev-philosophy/spec.md)
