# Development Philosophy Configuration (OpenSpec)

Source of truth for Polly's development philosophy configuration system. This is the technical counterpart to the aesthetic philosophy (themes): themes position aesthetics, the development philosophy positions technical decisions.

## Overview

Every coding project involves implicit decisions about where to sit on several spectrums. Most AI coding tools either ignore these decisions or impose their own defaults. Polly makes these explicit, configurable, and part of the development context.

The guided process is itself a thinking exercise — the conversation clarifies the user's priorities, and the resulting document informs all persona behavior throughout the project.

**Connection to design principles:** The philosophy system embodies "instruments over tracks" — a philosophy is a tuned instrument for a specific project, not a template to fill in. It also connects to "continuation over completion" — the philosophy is a living document that evolves with the project (finite vs. infinite games).

---

## The Spectrums

Core tensions in app development. Each exists on a continuum (0–100), not a binary.

### 1. Open Tool ↔ Constraint-Based

| Left (0) | Right (100) |
|-----------|-------------|
| Maximum flexibility, user configures everything | Opinionated defaults, fewer choices, clearer path |

**Connection:** Bogost — constraints create meaning. But which constraints, and for whom?

### 2. User-Friendly ↔ Powerful

| Left (0) | Right (100) |
|-----------|-------------|
| Low learning curve, progressive disclosure | Full capability surface, assumes competent user |

Not always opposed — the best tools are both. But early in development, you often must choose where to invest.

### 3. Convention ↔ Configuration

| Left (0) | Right (100) |
|-----------|-------------|
| "Do it this way" (Rails, Next.js) | "Set it up however you want" (Express, Vite) |

### 4. Local-First ↔ Cloud-Native

| Left (0) | Right (100) |
|-----------|-------------|
| Data sovereignty, offline capability, privacy | Collaboration, sync, scale |

### 5. Build ↔ Buy (Integrate)

| Left (0) | Right (100) |
|-----------|-------------|
| Custom implementation, full control | Use existing tools/services, faster to market |

**Connection:** Graeber — what is meaningful work vs. what is just reinventing?

### 6. MVP ↔ Architecture-First

| Left (0) | Right (100) |
|-----------|-------------|
| Ship something, learn from real usage | Design the system properly, avoid rework |

**Connection:** Reverse engineering tension — start from the outcome (architecture-first thinking) but need working systems fast (MVP).

### Extensibility

Spectrums are defined in `config/philosophy_spectrums.yaml`. Users (or Polly herself) can add new dimensions:

```yaml
spectrums:
  - id: accessibility-aesthetic
    name: "Accessibility ↔ Aesthetic"
    left:
      label: "Accessibility-first"
      description: "WCAG compliance, screen reader support, universal design"
    right:
      label: "Aesthetic-first"
      description: "Visual distinction, brand identity, experience quality"
    context_questions:
      - "Who are your users? Do any have accessibility needs?"
      - "Is this a tool (optimize for access) or an experience (optimize for feel)?"
```

Custom phases can also be added: a game developer might add a "Player Experience" phase, a team project might add a "Collaboration Model" phase.

---

## Guided Configuration Process

### Phase 1: Project Framing (Architect persona leads)

Polly asks structured questions:
- What is this project? (description, scope)
- Who is it for? (audience, their technical level)
- What's the deployment target? (local, web, mobile, embedded)
- What's the time horizon? (weekend hack, long-term instrument, production app)

### Phase 2: Spectrum Positioning (Conversational)

For each spectrum, Polly presents the tradeoffs in context of the specific project:

> "For a personal norns script, constraint-based makes sense — you know the hardware, the audience is you. But for Polly itself, you need to balance open extensibility (other users will customize) with opinionated defaults (so it works out of the box). Where do you want to start?"

This is a thinking exercise, not a quiz. The user's answers produce a philosophy document, but the conversation itself clarifies thinking.

Output per spectrum: numeric position (0–100) + rationale text.

### Phase 3: Philosophy Document Generation

Produces `development-philosophy.md` in the project root (or wherever the user specifies).

---

## Philosophy Document Format

### Frontmatter

```yaml
---
project: polly
created: 2026-02-09
author: brett
last_reviewed: 2026-02-09
review_cadence: monthly
---
```

### Body

```markdown
# Development Philosophy: Polly

## Positioning

| Spectrum | Position | Rationale |
|----------|----------|-----------|
| Open ↔ Constrained | 70% Open | Users need extensibility, but sensible defaults matter |
| Friendly ↔ Powerful | Start friendly, reveal power | Progressive disclosure pattern |
| Convention ↔ Config | Convention with escape hatches | Opinionated defaults, configurable for power users |
| Local ↔ Cloud | Local-first, cloud-optional | Core value: data sovereignty |
| Build ↔ Buy | Build core, integrate periphery | Own the RAG engine, use existing UI frameworks |
| MVP ↔ Architecture | Architecture-informed MVP | Design first, but ship early iterations |

## Non-Negotiables
- Edge-native: computation happens locally by default
- Privacy-respecting: user data never leaves device without consent
- Extensible: persona system must be open to user-created personas

## Technical Commitments
- TypeScript for core application
- SQLite + vector extensions for local storage
- Agent Skills format for extensibility
- Progressive web app for cross-platform

## Design Principles
- Instruments over tracks (ongoing capability, not finished products)
- Constraint as generative (each persona's limitations create focus)
- Documentation as thinking (not just record-keeping)
```

---

## Persona Integration

The philosophy document is injected into persona system prompts:

```
System prompt = [
  base_persona_prompt,
  active_mode_instructions,
  theme_behavior_context,
  philosophy_context,           ← from development-philosophy.md
  active_skills,
  user_instructions
]
```

**Priority hierarchy** (lowest to highest):
1. Persona base behavior
2. Active theme behavior
3. Project philosophy context
4. Active skills
5. Explicit user instruction

The philosophy is context, not command — it influences default behavior but never overrides explicit instructions.

---

## Philosophy Evolution

The philosophy is a living document, not a contract:

### Review Cadence

Configurable: monthly, milestone-based, or manual. At review time, Polly prompts:

> "You're six weeks into Polly development. Your philosophy said 'architecture-informed MVP' but you've been deep in architecture without shipping. Want to revisit that positioning?"

### Drift Detection (Future)

Continuous comparison of code patterns (from pattern learning) against philosophy positions:
- Code structure analysis shows increasing abstraction → compare against "convention ↔ configuration" position
- Dependency graph analysis shows many external packages → compare against "build ↔ buy" position
- "Your code diverged from your philosophy" notifications

---

## Slash Commands

| Command | Description | Persona |
|---------|-------------|---------|
| `/philosophy init` | Start guided configuration for new project | Architect |
| `/philosophy review` | Revisit current project philosophy | Architect |
| `/philosophy check` | Compare current code against stated philosophy | Architect |
| `/philosophy spectrum <name>` | Deep-dive into a specific spectrum | Architect |

---

## API

### Core (`core/philosophy/manager.py`)

```python
manager = PhilosophyManager(config, spectrums_path)

# Spectrums
spectrums = manager.get_spectrums()
manager.add_spectrum(new_spectrum_dict)

# Philosophy lifecycle
philosophy = manager.init_philosophy(project="polly", responses=guided_responses)
philosophy = manager.load_philosophy("development-philosophy.md")
manager.save_philosophy(philosophy, "development-philosophy.md")

# Persona integration
context = manager.get_philosophy_context(philosophy)

# Alignment
alignment = manager.check_alignment(philosophy, code_analysis)
review_prompt = manager.suggest_review(philosophy, project_metrics)
```

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/philosophy/spectrums` | List spectrum definitions |
| `POST` | `/api/philosophy/spectrums` | Add custom spectrum |
| `POST` | `/api/philosophy/init` | Start guided process |
| `GET` | `/api/philosophy/current` | Get current philosophy |
| `PUT` | `/api/philosophy/current` | Update philosophy |
| `POST` | `/api/philosophy/check` | Alignment check |

---

## UI

### Settings / Standalone Page

- **Guided flow:** Phase 1 framing form → Phase 2 spectrum sliders with contextual prompts → Phase 3 document preview
- **Spectrum visualization:** Bar chart or radar chart showing all positions
- **Philosophy viewer:** Rendered markdown with edit capability
- **Review banner:** Notification when review is due

---

## Config

```yaml
# In config/config.yaml
philosophy:
  enabled: true
  spectrums_path: "config/philosophy_spectrums.yaml"
  review_cadence: "monthly"
  inject_into_prompts: true
```

---

## Implementation Files

| File | Purpose |
|------|---------|
| `core/philosophy/__init__.py` | Package |
| `core/philosophy/models.py` | DevelopmentPhilosophy, SpectrumPosition |
| `core/philosophy/manager.py` | PhilosophyManager |
| `core/philosophy/guided_process.py` | Three-phase guided conversation |
| `interfaces/philosophy_api.py` | REST endpoints |
| `config/philosophy_spectrums.yaml` | Default spectrum definitions |

---

## Relationship to Other Systems

| System | Integration |
|--------|-------------|
| **Design spec** | Philosophy is the technical counterpart to aesthetic philosophy. Design principles inform default spectrum positions. |
| **Themes** | Theme = aesthetic positioning. Philosophy = technical positioning. Both inject context into persona prompts. |
| **Personas** | Philosophy context injected into all persona system prompts. Architect leads guided process. |
| **Patterns** | Code patterns analyzed for alignment checks. Drift detection uses pattern data. |
| **Code Library** | Library conventions influenced by philosophy (e.g., "convention-heavy" philosophy → stricter library module standards). |
| **Onboarding** | Philosophy init could be part of project onboarding flow. |

---

## Reference

- Change folder: [openspec/changes/code-library-and-dev-philosophy/](../../changes/code-library-and-dev-philosophy/)
- Design philosophy: [design spec](../design/spec.md)
- Themes (aesthetic philosophy): [themes spec](../themes/spec.md)
- Personas: [personas spec](../personas/spec.md)
- Patterns: [patterns spec](../patterns/spec.md)
- Code Library: [code-library spec](../code-library/spec.md)
