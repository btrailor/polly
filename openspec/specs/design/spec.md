# Design (OpenSpec)

Source of truth for Polly's design philosophy and principles. Full text: [docs/planning/DESIGN_PHILOSOPHY.md](../../../docs/planning/DESIGN_PHILOSOPHY.md).

## Vision

Polly is a personal AI that grows with you—starting simple, becoming powerful, always yours. It enhances and extends your thinking; it does not replace it. Polly is infrastructure for polymathic practice as continuation, not a productivity app for task completion.

## Core Principle: Progressive Capability

- **Progressive revelation:** Start simple (notes + chat); reveal domains, personas, tools as the user is ready.
- **Context reveals complexity:** Don't show every option upfront; suggest features when contextually relevant.
- **Intelligent defaults:** Work well with no config; allow deep customization.
- **Default-driven configuration:** Opinionated but sensible defaults; power users can override.

## Design Principles

1. **Context reveals complexity** — Suggest features at teachable moments.
2. **Intelligent defaults** — 80% never change defaults; defaults should be opinionated and sensible.
3. **Capture over perfection** — Get it in fast, refine later. Frictionless input matters more than perfect structure at capture time.
4. **Signal over noise** — Every feature should increase knowledge quality, not just quantity. Anti-slop by design.
5. **Domain fluidity** — Work crosses boundaries; the system supports that. Features work regardless of how users customize domains.
6. **Continuation over completion** — Support ongoing work, not just finished products. The system treats development as infinite game.
7. **Emergence over prescription** — Let patterns surface from connections rather than forcing structure. Organization emerges from connection patterns, not folder hierarchies.
8. **Local control** — Your data, your infrastructure, your rules. Local-first; opt-in to sharing and cloud.
9. **Privacy by default** — Opt-in to external services. No content sent to cloud unless user chooses.
10. **Reverse engineering** — Start with desired outcome (published work), build backward through the pipeline.
11. **Progressive autonomy** — Agent swarms start with tight user oversight. As trust builds, users loosen control. Intervention points at every agent boundary; transparency in execution.
12. **Operational aesthetics** — Aesthetic choices are not decorative. They alter decision-making in measurable ways. The Aesthetic Theme Engine embodies this: themes derived from artist practices change how personas think, not just how the UI looks. See [themes spec](../themes/spec.md).
13. **Domain permeability** — Theme choices in one domain ripple into all others. A visual aesthetic decision affects writing voice, code style, and systems thinking. The five domains (Sights, Sigils, Signals, Scrolls, Glyphs) are interconnected through shared aesthetic constitution.
14. **Constitutional epistemology** — Foundation, not filter. Polly's analytical commitments (material analysis over essentialism, cui bono, scapegoat suspicion) are hardcoded and non-negotiable. They shape _how_ Polly thinks, not what topics are available. The user never gets lectured; they get deeper analysis. Antifascism as consistently better thinking, not as content moderation. See [ethics spec](../ethics/spec.md).

(See DESIGN_PHILOSOPHY for historical context: growth-oriented design, open plugin future, etc.)

## Aesthetic Theme System

Polly's design philosophy is operationalized through an artist-derived Aesthetic Theme Engine. Each theme is derived from a specific artist's practice and philosophy (Casey Reas, Tyler Hobbs, Julian House, Karel Martens, Experimental Jetset, Bridget Riley, Anni Albers). Themes are not skins — they are epistemological stances encoding compositional logic, color philosophy, relationship to material, tolerance for ambiguity, and orientation toward emergence versus control.

Key properties:

- **Artist fidelity:** Each theme recognizable to someone familiar with the source artist's work.
- **Composability:** Users mix elements from multiple themes for hybrid configurations.
- **Infinite game orientation:** Themes support continuation and exploration, not completion.
- **Two-level operation:** Surface (UI presentation) and deep (persona behavior defaults) change together.

See [themes spec](../themes/spec.md) for full theme definitions and composability system.

## Development Philosophy Configuration

The technical counterpart to the aesthetic theme system. Where themes position aesthetics, the development philosophy positions **technical decisions** along configurable spectrums:

| Spectrum                   | What It Asks                                        |
| -------------------------- | --------------------------------------------------- |
| Open ↔ Constrained         | How much flexibility vs. how many opinions?         |
| Friendly ↔ Powerful        | Progressive disclosure vs. full capability surface? |
| Convention ↔ Configuration | Rails-like vs. Express-like?                        |
| Local ↔ Cloud              | Data sovereignty vs. collaboration?                 |
| Build ↔ Buy                | Custom vs. integrate existing?                      |
| MVP ↔ Architecture         | Ship fast vs. design properly?                      |

Key properties:

- **Guided process:** Polly walks the user through a three-phase conversation (Frame, Position, Generate) rather than presenting checkboxes.
- **Thinking exercise:** The conversation clarifies priorities; the document is a byproduct.
- **Living document:** Not write-once. Polly prompts for review at configurable intervals.
- **Persona integration:** Philosophy context injected into all persona system prompts, influencing default behavior.
- **Extensible:** Users can add custom spectrums and phases.
- **Spectrums as continua:** 0–100 positioning, not binary choices.

See [dev-philosophy spec](../dev-philosophy/spec.md) for the full philosophy configuration system.

## Per-Project Design System

Each project Polly works on can maintain a design system as a first-class artifact in a `_design/` directory. This is Relume's insight applied locally: system first, components second. The design system is created and maintained by the Designer persona's System mode.

```
project/
├── _design/
│   ├── system.yml           # Design tokens (colors, typography, spacing, icons, chrome)
│   ├── palette.svg          # Visual palette reference
│   ├── icons/               # Custom icon set + registry.json
│   ├── patterns/            # Repeating patterns and textures
│   ├── components/          # Component specs
│   └── generators/          # p5.js sketches that produced assets
```

**`system.yml`** defines design tokens: colors, typography (heading/body/mono), spacing scale, icon conventions (Lucide base set + custom), breakpoints, and chrome (border radius, shadow style, divider style). Tokens can be exported as CSS custom properties, Tailwind config, or JSON.

**Theme derivation:** A design system can be seeded from the active theme's presentation layer — Reas theme produces a monochromatic, grid-strict system; Fidenza produces an organic, warm-toned system. Switching themes doesn't destroy the design system but can regenerate assets within it.

**Persona usage:** Designer creates/maintains, Programmer references tokens in code, Architect considers system implications in technical decisions, Scribe uses palette/typography for published content.

See [personas spec — Designer](../personas/spec.md) for the full Designer profile and [themes spec](../themes/spec.md) for theme → design system derivation.

## Reusable Code Library

Polly builds a living library of reusable code as a byproduct of working. This embodies the "instruments over tracks" principle: the library is an instrument played across projects, not a collection of finished tracks. Uses the Agent Skills format (SKILL.md) for cross-platform portability. Design components, generator scripts, and design system templates are library modules alongside code patterns.

See [code-library spec](../code-library/spec.md) for the full code library system.

## Learning UI: Problem-Posing over Banking

The Learning page center area embodies problem-posing education (Freire): the active learning surface (conversation, curriculum map, practice space) is center stage. Analytics — progress metrics, time spent, competency levels — are useful metadata about learning, but they're secondary. They live in a collapsible Review tab, summoned intentionally rather than imposed by default.

**Design principle:** When analytics dominate the center of the screen, the tool communicates "tracking your learning is more important than doing your learning." That's a banking model. The active session is the UI.

See [teaching spec](../teaching/spec.md) for center-area states and meta-pedagogy.

## Reference

- [docs/planning/DESIGN_PHILOSOPHY.md](../../../docs/planning/DESIGN_PHILOSOPHY.md) — Full design philosophy and principles
- [themes spec](../themes/spec.md) — Aesthetic Theme Engine
- [dev-philosophy spec](../dev-philosophy/spec.md) — Development Philosophy Configuration
- [code-library spec](../code-library/spec.md) — Reusable Code Library
- [personas spec — Designer](../personas/spec.md) — Designer persona and generative design
- [teaching spec](../teaching/spec.md) — Meta-pedagogy and Learning page redesign
- [ethics spec](../ethics/spec.md) — Constitutional epistemology
- [openspec/changes/designer-profile/](../../changes/designer-profile/) — Designer Profile change
- [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/) — Learning & Administrator Profiles change
- [openspec/changes/constitutional-epistemology/](../../changes/constitutional-epistemology/) — Constitutional Epistemology change