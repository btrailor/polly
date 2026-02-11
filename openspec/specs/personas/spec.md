# Personas (OpenSpec)

Source of truth for the agent persona system. Full architecture: [docs/PERSONA_SYSTEM_ARCHITECTURE.md](../../../docs/PERSONA_SYSTEM_ARCHITECTURE.md). API: [docs/PERSONA_API.md](../../../docs/PERSONA_API.md).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Architect, Scribe, Professor | ✅ Implemented | `core/personas/implementations/` |
| PersonaManager, mode switching | ✅ Implemented | `core/personas/manager.py` |
| PersonaAware (pattern, entity, mental model) | ✅ Implemented | integration-contracts |
| Theme behavior injection | 💭 Vision | aesthetic-theme-engine change |
| Programmer, Librarian, Designer, Administrator | 💭 Vision | Spec-only; Phase 25, 27, 20a–20b |

## Integration Contracts (Feb 2026)

Personas compose with other systems via shared protocols:

- **Persona↔Pattern** — On activation (`activate_persona`, `switch_mode`), Polly notifies the pattern engine via `set_active_persona(name, mode)`. Learned patterns are attributed to the active persona; `get_patterns_for_prompt()` boosts persona-specific patterns.
- **Persona↔Entity** — EntityContextBuilder is notified of the active persona; entity context can boost entities that appear in that persona's patterns (persona affinity terms).
- **Persona↔Mental model** — MentalModelManager receives `set_active_persona`; activation scoring uses the current persona so persona-relevant models are preferred.

When `query()` is called without explicit persona/mode, Polly resolves them from the currently active persona so context and learning stay consistent.

See [integration-contracts design](../../changes/integration-contracts/design.md).

## Current Personas (Implemented)

- **Architect** — Plan and Build modes; structured planning and execution. Used for note creation and complex tasks.
- **Scribe** — Research, Write, Refine modes; writing and organization. Skills: template-guide, wiki-linking, domain-structure.
- **Professor** — Teaching, curriculum generation, section enrichment, exercise validation. Used in curriculum (Phase 23) and teaching mode (Phase 22).

## Planned Personas

### Programmer

**Phase:** Tier 4 (Phase 25 Code Architecture depends on this)
**Modes:** Code, Review, Debug, Refactor

| Mode | Description |
|---|---|
| **Code** | Hands-on code generation, implementation, and modification. Works within the code workspace (Phase 17 Monaco). Understands project architecture via Code Architecture System (Phase 25). |
| **Review** | Code review with security, performance, and style analysis. Generates structured review feedback. |
| **Debug** | Systematic debugging with hypothesis formation, test suggestions, and root cause analysis. |
| **Refactor** | Architectural refactoring with impact analysis. Uses dependency tree to identify ripple effects of changes. |

Distinct from Architect: Architect plans at the strategic level (what to build, how to structure). Programmer executes at the code level (writing, reviewing, debugging). In Agent Swarms, these compose naturally: Architect(Plan) → Programmer(Code) → Programmer(Review).

### Librarian

**Phase:** Tier 3 (Knowledge Platform — aligns with knowledge graph, BookLore)
**Modes:** Organize, Recommend, Archive, Connect

| Mode | Description |
|---|---|
| **Organize** | Knowledge curation: categorize, tag, and structure content. Works with PARA organization and maturity lifecycle. Maintains knowledge quality (anti-slop). |
| **Recommend** | Proactive knowledge surfacing: "Based on what you're working on, you might want to revisit..." Uses entity graph and connection metrics. |
| **Archive** | Knowledge lifecycle management: identify stale content, suggest merges, flag orphans for review. Drives garden maintenance workflows. |
| **Connect** | Discovery of hidden connections between knowledge items. Cross-domain bridge detection. "These 3 notes all discuss the same concept — link them?" |

Deeply integrated with: [knowledge-graph spec](../knowledge-graph/spec.md), [library spec](../library/spec.md), [capture spec](../capture/spec.md). The Librarian operationalizes the knowledge quality pipeline through a user-facing persona rather than purely automated background processes.

### Designer

**Phase:** Phase 27 (Tier 4)
**Modes:** Vision, Mockup, Critic, System, Generate
**Depends on:** Phase 17 (Code Workspace) for full UX; p5.js pipeline works independently

| Mode | Description |
|---|---|
| **Vision** | High-level design direction: mood boards, design briefs, aesthetic guidance. Translates user intent into design language. Theme-informed: active theme constrains aesthetic direction. Cross-domain aware: knows about Signals (audio viz needs), Scrolls (blog feature images), Sigils (UI for tools). |
| **Mockup** | Generate UI mockup descriptions, wireframe specs, component layouts. Relume-inspired sitemap → wireframe thinking. Component selection from project design system (`_design/system.yml`). Future: Figma API integration. |
| **Critic** | Design review and critique: accessibility audit, consistency check, UX heuristic evaluation. **Design system conformance checking** — "This component doesn't match your `system.yml`." Lucide rule validation for icons. |
| **System** | **Full design system management.** Create, update, and maintain `_design/` directory with `system.yml` (design tokens), icon registry, patterns, and generators. Generate `system.yml` from active theme's presentation layer. Export tokens as CSS custom properties, Tailwind config, or JSON. Style guide builder: system first, components second. |
| **Generate** | *(NEW)* **p5.js generative asset creation.** Produces custom icons (Lucide-compatible), pattern tiles, feature images (for POSE/Ghost CMS), data visualizations, and UI micro-elements. Constraint-driven: define rules (palette, grid, stroke weight), generate within them. Theme behavior layer (`designer.default_composition`, `designer.color_logic`, `designer.turbulence`, `designer.material_awareness`) directly constrains the p5.js generator. |

Sub-phases: 27a (Visual Designer + Generate mode), 27b (Artist Mode — theme-aware generation), 27c (Design Collaboration).

**Key divergence from Relume:** Polly's Designer is constraint-driven rather than template-driven. Relume gives 1000 components to pick from. Polly defines constraints (palette, grid, stroke weight, content type) then generates within them. Fewer options, more coherence. Connects to Bogost's conception of play — constraints as generative.

**p5.js as generative design engine:**
- Uses p5.js-svg (zenozeng) for vector SVG output — build-step, not runtime
- Post-processed by SVGO for clean, optimized SVGs
- Lucide design rules enforced programmatically for icon generation
- Generator scripts saved to `_design/generators/` and optionally to code library as reusable instruments

**Asset types:** Custom icon sets, pattern tiles (backgrounds, textures, dividers), feature images (blog posts via POSE), data visualizations (charts matching design system), UI micro-elements (spinners, dividers, decorative elements).

**Per-project design system** (`_design/` directory): `system.yml` defines tokens (colors, typography, spacing, icons, breakpoints, chrome). Icons tracked via `registry.json`. Generator scripts preserved for reproducibility. See [design spec](../design/spec.md) for full format.

**Theme-as-Meta-Persona concept:** The Designer can generate Polly theme configurations — a meta-persona that customizes the tool's own appearance based on user aesthetic preferences. Theme configurations are defined in [themes spec](../themes/spec.md). The Designer's System mode is the natural interface for creating and modifying themes.

**Theme → Generator integration:** The active theme's `designer.*` behavior properties directly constrain the p5.js generation pipeline. Same icon request under different themes produces meaningfully different output:
- **Reas** (turbulence: 0.3, instruction-based): Clean, geometric, rule-derived.
- **Fidenza** (turbulence: 0.6, flow-field): Organic curves, slight irregularity.
- **Ghost Box** (turbulence: 0.2, found-ephemera): Stamp-like, institutional quality.
- **Albers** (turbulence: 0.0, grid-emergent): Absolute grid, woven complexity.

See [themes spec](../themes/spec.md) for behavior layer property definitions and the full theme → generator mapping.

**Change folder:** [openspec/changes/designer-profile/](../../changes/designer-profile/)

### Administrator

**Phase:** Tier 4 (Polish & Autonomy), with communication modes tied to Phase 20
**Modes:** Configure, Monitor, Maintain, Automate + Triage, Compose, Schedule, Remind

#### System Modes

| Mode | Description |
|---|---|
| **Configure** | System configuration assistant: help users set up domains, API keys, integrations, routing preferences. Explains tradeoffs. |
| **Monitor** | System health monitoring: performance metrics, cost tracking, storage usage, integration status. Surfaces issues proactively. |
| **Maintain** | Maintenance tasks: database optimization, cache clearing, index rebuilding, log rotation. Handles housekeeping. |
| **Automate** | Workflow automation: help users create automation rules, scheduled tasks, export jobs. Progressive autonomy configuration. |

#### Communication Modes (Superhuman-Informed)

| Mode | Description | Superhuman Parallel |
|---|---|---|
| **Triage** | Sequential, flow-based email processing. Priority-sorted queue. For each email: Reply, Delegate, Defer, Archive, Flag. Split processing by email type (team, newsletters, notifications). AI prioritization learns from response patterns. | Split Inbox + Flow processing |
| **Compose** | Voice-matched draft generation. Analyzes user's sent email to build style profile. Context injection from knowledge base (RAG). Template system for recurring patterns. Distraction-free writing interface. | AI Compose + Instant Reply |
| **Schedule** | Calendar intelligence. Find open slots, propose meeting times, detect conflicts. Buffer-aware. Energy-aware scheduling from user profile (morning productivity → suggest afternoon meetings). | Calendar integration |
| **Remind** | Follow-up tracking ("You emailed Dean's office 5 days ago with no reply"). Deadline extraction from emails + calendar. Snooze with context — stores reason, resurfaces with it. | Snooze + Remind Me |

**Mode selection:** Automatic based on context. Email/calendar intent → communication mode. System/config intent → system mode.

**Core design insight from Superhuman:** Speed is a feature. Polly doesn't replace the email client — it provides a fast intelligence layer on top. Making email processing take 15 minutes instead of 90.

**Slash commands:**
- `/mail triage` → start triage session
- `/mail next` → next in queue
- `/mail reply` / `/mail archive` / `/mail snooze 2d` → quick actions
- `/mail summary` → AI thread summary
- `/mail compose` → new draft
- `/mail schedule` → find meeting times
- `/mail follow-up` → check pending follow-ups

**Cross-persona integration:** Scribe captures action items from emails. Architect gets informed of technical emails. Publisher uses Compose for newsletters. Librarian indexes reference-worthy threads.

The Administrator is Polly's self-awareness persona — it understands the system's own state and helps users manage it. Integrates with autonomy metrics, budget manager, DRM node health, and communication intelligence.

**Change folder:** [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/)

## Complete Persona-as-Agent Architecture

With the Agent Swarms system, all personas (current and planned) gain formal capability declarations:

| Persona | Agent Capabilities | Modes as Sub-Agents |
|---|---|---|
| **Architect** | planning, decomposition, canvas_analysis | Plan Agent, Build Agent, Canvas Agent |
| **Scribe** | writing, enrichment, publishing, organization | Capture Agent, Organize Agent, Enrich Agent, Edit Agent, Publish Agent |
| **Professor** | teaching, assessment, curriculum, explanation | Explain Agent, Socratic Agent, Quiz Agent |
| **Programmer** | coding, review, debugging, refactoring | Code Agent, Review Agent, Debug Agent, Refactor Agent |
| **Librarian** | knowledge_curation, recommendation, archival, connection_discovery | Organize Agent, Recommend Agent, Archive Agent, Connect Agent |
| **Designer** | design_vision, mockup, critique, design_system, generative_design | Vision Agent, Mockup Agent, Critic Agent, System Agent, Generate Agent |
| **Administrator** | configuration, monitoring, maintenance, automation, triage, compose, schedule, remind | Configure Agent, Monitor Agent, Maintain Agent, Automate Agent, Triage Agent, Compose Agent, Schedule Agent, Remind Agent |

Each persona is an **agent group** — a pre-composed swarm. The Nexus can invoke individual modes as standalone agents or compose cross-persona workflows (e.g., Architect(Plan) → Programmer(Code) → Programmer(Review) → Scribe(Write)).

This replaces the original "Orchestrator mode" toggle (Phase 24) with a composable agent architecture. See [agent-swarms spec](../agent-swarms/spec.md).

## Behavior

- **Lazy-loading:** Persona prompts/skills loaded when activated. User can switch manually; context-aware switching detects intent.
- **Modes:** Each persona has modes. Activate via API or UI; state persisted.
- **Agent interface:** Each persona implements the Agent Swarms capability declaration — modes become distinct agent capabilities the Nexus can invoke independently. See [agent-swarms spec](../agent-swarms/spec.md).

### Constitutional Epistemology

All personas inherit a non-negotiable epistemological foundation — the constitutional layer. It shapes *how* every persona thinks, not what topics are available. Three core commitments: material analysis over essentialism, cui bono as default heuristic, suspicion of scapegoat narratives. Five conduct rules: never label users, lead with curiosity, acknowledge legitimate grievances, reserve naming for analysis, defamiliarize don't denounce.

The constitutional layer is the deepest system prompt layer. It cannot be overridden by themes, philosophy, personas, or user instructions. It is Polly's nervous system, not her wardrobe.

See [ethics spec](../ethics/spec.md) for the full constitutional epistemology system.

### Aesthetic Theme Integration

When an aesthetic theme is active, all personas receive theme behavior layer properties as weighted defaults in their system prompt. The theme is the background hum, not the foreground command — explicit user instructions always take priority.

### Development Philosophy Integration

When a project has an active `development-philosophy.md`, all personas receive philosophy context in their system prompt. Philosophy positions (e.g., "local-first", "convention with escape hatches") inform default behavior.

**Combined prompt injection:**
Each persona's system prompt gains constitutional, theme, and philosophy context sections:

```
System prompt = [
  constitutional_epistemology,  ← deepest layer, non-negotiable (core/constitutional/layer.py)
  base_persona_prompt,
  active_mode_instructions,
  theme_behavior_context,      ← injected by ThemePersonaAdapter
  philosophy_context,           ← injected from development-philosophy.md
  active_skills,
  user_instructions
]
```

**Priority hierarchy:**
1. Explicit user instruction (highest) — what to do
2. Task-specific requirements (e.g., accessibility standards override perceptual extremes)
3. Active skills
4. Project philosophy context
5. Active theme behavior defaults
6. Persona base behavior
7. Constitutional epistemology (deepest) — how to think about everything

See [dev-philosophy spec](../dev-philosophy/spec.md) for the full philosophy system.

### Code Library Relationships

Each persona has a defined relationship to the reusable code library:

| Persona | Library Role |
|---------|-------------|
| **Programmer** | Primary producer + consumer. Extracts patterns during coding, applies modules in new projects. Runs scripts directly. |
| **Architect** | Reviewer + strategist. Reviews for architectural patterns. Suggests composing existing modules over writing from scratch. |
| **Designer** | Producer + consumer. Generates design components, icons, patterns → `components/`. Generator scripts → `workflows/`. Design system templates → `workflows/`. Accesses `components/` for UI patterns. |
| **Librarian** | Indexer + retriever. Handles RAG layer connecting queries to library entries. |
| **Scribe** | Documenter. Documents library additions. Creates changelogs. |
| **Professor** | Teacher. Uses library modules as teaching examples. |
| **Administrator** | Maintainer. Library health: stale modules, unused modules, dependency audit. |

See [code-library spec](../code-library/spec.md) for the full library system.

**Cross-domain ripple:** Theme effects are not siloed by persona. When a theme is active, all personas receive relevant behavior properties — the writer persona's voice influences how the programmer comments code, the designer's material awareness affects how the systems-thinker frames problems. This cross-domain permeability mirrors the five-domain interconnection principle.

**Examples:**
- Ghost Box theme + Scribe: Voice becomes allusive and indirect. Written structure follows found-document logic. Organization favors archival filing patterns.
- Fidenza theme + Architect: Plans use probabilistic weighting. Structure is organic, not rigid. Multiple viable paths explored in parallel.
- Jetset theme + Programmer: Code uses minimal abstractions. Comments explain why, not what. Documentation breaks the fourth wall.

See [themes spec](../themes/spec.md) for full theme definitions and composability system.

### Context-Aware Persona Switching

Polly detects when a user's query would work better with a different persona and suggests switching:

- **Hybrid detection:** Frontend regex pattern matching (fast, current) + future LLM-based intent classification (more accurate).
- **Intent patterns:** Each persona defines trigger patterns (e.g., "make a note" / "create a guide" → Scribe, "plan this" / "architect" → Architect, "teach me" / "explain" → Professor, "review this code" → Programmer).
- **UI:** Non-intrusive suggestion dialog. User can accept, dismiss, or configure auto-switching per persona.
- **Performance:** <1ms per message (regex); future AI classification adds latency only when confidence is ambiguous.
- **Learning:** User switching patterns are tracked via PatternLearner. Over time, Polly learns which persona the user prefers for which contexts.

### Skill System

Personas gain capabilities through a modular skill system:

**Skill format:** Each skill is a `SKILL.md` file containing structured instructions, examples, and constraints.

```
skills/
  scribe/
    template-guide.md
    wiki-linking.md
    domain-structure.md
  architect/
    plan-format.md
    impact-analysis.md
  professor/
    socratic-method.md
    exercise-design.md
  programmer/
    code-review-checklist.md
    debug-methodology.md
  librarian/
    organization-rules.md
    connection-heuristics.md
  designer/
    lucide-guidelines.md
    design-system-management.md
    generative-constraints.md
```

- **SkillManager:** Lazy-loads skills for active persona. Skills are additive — they extend the persona's system prompt with domain-specific expertise.
- **ThemePersonaAdapter:** Translates active theme behavior layer into natural-language context for system prompt injection. Advisory, not mandatory. See [themes spec](../themes/spec.md).
- **User-extensible (future):** Custom skill files that extend persona capabilities. Custom persona definitions via YAML format.
- **Marketplace concept (future, Phase 28):** Community-contributed skills distributed via Open Polly Tools ecosystem. See [plugins spec](../plugins/spec.md).

## API (Summary)

- `GET /persona/list` — Available personas and modes.
- `POST /persona/activate` — Activate persona (default mode).
- `POST /persona/switch-mode` — Change mode (e.g. teaching mode).
- Persona-specific endpoints for plan/build, note creation, curriculum, etc.
- Action types in responses: `show_questions`, `show_preview`, `suggest_mode_switch`.

## Scribe Standalone Enrich (Core Framework Refinement)

- **`enrich_standalone(content, title, domain, conversation_history)`** — Direct enrichment method added to `ScribePersona`. Skips Capture/Organize pipeline; used by `KnowledgeWriter` for Scribe-assisted saves. Returns enriched content + metadata.
- **Change folder:** [openspec/changes/core-framework-refinement/](../../changes/core-framework-refinement/)

## Planned Persona Extensions

### Architect: Canvas-Aware Plan Mode
When Architect is active and user is in a BAD Canvas, behavior shifts to design strategist:
- Challenge assumptions tactfully.
- Surface cross-domain gaps and dependencies.
- Connect design decisions to business outcomes.
- Reference past successful patterns from other canvases.
Not a new persona — a context-aware mode of existing Architect. See [canvas spec](../canvas/spec.md).

### Scribe: Publishing Mode
Scribe gains a publishing-specific mode for POSE pipeline:
- Transform notes into publication-ready drafts.
- Apply domain-specific style and formatting.
- Generate summaries, excerpts, social threads.
- See [publishing spec](../publishing/spec.md).

### Professor: Domain Onboarding
Built-in curriculum template teaching new users how to effectively configure and use domains for polymathic practice. See [domains spec](../domains/spec.md), [curriculum spec](../curriculum/spec.md).

## Implementation

- **Current files:** `core/personas/base.py`, `core/personas/manager.py`, `core/personas/architect.py`, `core/personas/implementations/scribe.py`, `core/personas/implementations/professor.py`
- **Planned:** `core/personas/implementations/programmer.py`, `core/personas/implementations/librarian.py`, `core/personas/implementations/designer.py`, `core/personas/implementations/administrator.py`
- **Skills:** `core/personas/skills/` directory with per-persona skill files
- **Theme integration:** `core/themes/persona_adapter.py` — translates theme behavior layer to persona system prompt context. See [themes spec](../themes/spec.md)

## Reference

- [docs/PERSONA_SYSTEM_ARCHITECTURE.md](../../../docs/PERSONA_SYSTEM_ARCHITECTURE.md) — Full roster, skills, orchestrator design
- [docs/PERSONA_API.md](../../../docs/PERSONA_API.md) — REST API
- [docs/planning/phases/phase-11/](../../../docs/planning/phases/phase-11/) — Phase 11/11c implementation
- [docs/planning/phases/other/PHASE27_DESIGNER_PERSONA.md](../../../docs/planning/phases/other/PHASE27_DESIGNER_PERSONA.md) — Designer persona detail
- Agent Swarms: [agent-swarms spec](../agent-swarms/spec.md)
- Canvas: [canvas spec](../canvas/spec.md)
- Publishing: [publishing spec](../publishing/spec.md)
- Plugins: Phase 28 (Open Polly Tools)