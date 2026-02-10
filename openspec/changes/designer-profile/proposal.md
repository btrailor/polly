# Designer Profile — Proposal

**Created:** February 2026  
**Scope:** Backend + Frontend + Design system infrastructure  
**Tier/Phase:** Tier 4 — Phase 27 (Designer Persona), with cross-cutting connections to themes, code library, publishing

---

## What

A comprehensive expansion of the Designer persona from abstract modes (Vision/Mockup/Critic/System) into a working generative design engine with three concrete capabilities:

1. **p5.js Generative Design Pipeline** — Polly generates custom design assets (icons, patterns, textures, feature images, data visualizations, UI micro-elements) programmatically using p5.js with SVG output. Constraint-driven rather than template-driven: define rules (palette, grid, stroke weight), generate within them.

2. **Per-Project Design System** — Each project maintains a `_design/` directory with `system.yml` (design tokens), custom icons, patterns, components, and the p5.js generator scripts that produced them. The design system is an artifact Polly maintains, not just a concept.

3. **Theme → Generator Integration** — The existing Aesthetic Theme Engine's behavior layer properties (`designer.default_composition`, `designer.color_logic`, `designer.turbulence`, `designer.material_awareness`) directly constrain the p5.js generation pipeline. Switching themes changes not just how Polly talks about design, but how it generates design assets.

## Why

### The Relume Lesson

Relume (the most relevant model for AI-assisted design) demonstrates the right abstraction level:
- **Component library as design substrate** — 1000+ components organized by section type within a design system. AI composes by selecting and arranging internally-consistent components.
- **Sitemap → wireframe → design pipeline** — Each stage is editable before proceeding. Genuine workflow acceleration, not "generate a website."
- **Style Guide Builder** — System first, components second. The right order of operations.
- **Client-First (Finsweet) naming** — Adopted existing convention rather than inventing one. Output is immediately legible.

### Where Polly Diverges

Relume optimizes for speed-to-client-site (agencies, freelancers). Polly's Designer serves a different purpose:

| Relume | Polly |
|--------|-------|
| Template-driven (pick from 1000 components) | **Constraint-driven** (define rules, generate within them) |
| Layout composition only | **Generative assets** — icons, patterns, textures, feature images |
| No knowledge of user's other work | **Cross-domain awareness** — Signals (audio viz), Scrolls (blog images), Sigils (UI) |
| Cloud export (Webflow, Figma) | **Local-first** SVG generation, any-tool compatible |
| No aesthetic philosophy | **Theme-constrained** — Fidenza theme produces different icons than Jetset theme |

### Why Now

- The themes spec already defines `designer.*` behavior properties. They currently only influence prompts — this spec makes them control a **generative engine**.
- The code library spec just defined a module format. Design components, generator scripts, and design system templates are natural library modules.
- The publishing pipeline (POSE) needs feature images for Ghost CMS posts. This spec provides the pipeline.
- Phase 27 exists on the roadmap but was abstract. This spec makes it concrete and buildable.

## Scope

### In Scope
- p5.js SVG generation pipeline (need → constraints → sketch → SVG → optimize)
- Lucide-compatible icon generation (24x24, stroke-based, grid-aligned)
- Per-project design system directory structure and `system.yml` schema
- Theme behavior layer → p5.js constraint mapping
- Design system management by Designer persona (System mode expansion)
- Feature image generation for publishing pipeline
- Generator scripts as reusable code library modules
- Design asset types: icons, pattern tiles, feature images, data viz, UI micro-elements
- SVGO post-processing for SVG cleanup
- Affinity Designer export compatibility

### Out of Scope (for now)
- Full Figma API integration (mentioned in existing spec as future)
- Raster output (PNG, JPEG) — SVG only for now
- Interactive design assets (p5.js runtime in app)
- Full Relume-style sitemap → wireframe pipeline (Polly is constraint-driven, not template-driven)
- Design collaboration features (Phase 27c)

## Impact on Existing Systems

| System | Impact |
|--------|--------|
| **Themes** | Behavior layer properties gain concrete meaning: they constrain the p5.js generator. `designer.turbulence: 0.6` now means something measurable in generated output. |
| **Personas (Designer)** | Modes expanded with generative capabilities. System mode gains design system management. New Generate mode for p5.js pipeline. |
| **Code Library** | Three new module types: design components, generator scripts, design system templates. Designer becomes a library producer alongside Programmer. |
| **Publishing** | Feature image generation via p5.js for Ghost CMS posts. POSE pipeline gains a visual asset step. |
| **Design spec** | Per-project design systems formalized. Design tokens as first-class artifacts. |
| **Architecture** | New subsystem: Design Engine (`core/design/`). p5.js-svg as build dependency. |
| **Patterns** | Design patterns recognized and tracked alongside code patterns. |

## Relationship to Existing Specs

- **themes/spec.md** — The behavior layer's `designer.*` properties become constraints for the generative engine. This is the tightest integration: theme ↔ generator is a direct mapping.
- **personas/spec.md** — Designer section expanded significantly. Current modes (Vision/Mockup/Critic/System) remain; System mode enhanced with design system management; new Generate mode added.
- **code-library/spec.md** — Design components, generators, and system templates are library modules.
- **publishing/spec.md** — Feature images generated for POSE pipeline.
- **design/spec.md** — Per-project design system as formal artifact.

## Open Questions

1. **How much design capability in Polly vs. Affinity/Figma?** Explore vs. Exploit — Polly generates quickly (explore), refinement may belong in purpose-built tools (exploit). Icons and patterns stay in Polly; complex illustrations go to Affinity.
2. **Design trend awareness?** Librarian persona could index design references (ebook library, bookmarked sites), giving Designer a knowledge base beyond rules.
3. **p5.js version pinning:** p5.js-svg (zenozeng) requires p5.js 1.6.0, not latest. Acceptable since generation is a build step, not runtime.

## Reference

- Relume: AI-assisted web design (sitemap → wireframe → design)
- Lucide: Open-source icon set with precise design guidelines
- p5.js-svg (zenozeng): SVG renderer for p5.js
- SVGO: SVG optimizer
- Affinity Designer: Professional vector editor with Lucide template
- Existing themes spec: [themes spec](../../specs/themes/spec.md)
- Existing code library spec: [code-library spec](../../specs/code-library/spec.md)
