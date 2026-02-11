# Themes — Aesthetic Theme Engine (OpenSpec)

Source of truth for Polly's artist-derived aesthetic theme system. Themes operate on two levels: surface-level UI presentation (colors, typography, textures, spacing, motion) and deep-level behavioral configuration for AI personas. Switching themes changes not just how Polly looks, but how it thinks and makes decisions.

**Catalogue Reference:** Affinity Suite Techniques Catalogue (38 techniques, 12 artists)
**Domains touched:** Sights × Sigils × Signals × Scrolls × Glyphs (all five)

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Theme schema, registry, loader | 💭 Vision | aesthetic-theme-engine change |
| Theme API (list, active, switch, compose) | 💭 Vision | aesthetic-theme-engine change |
| Persona theme behavior injection | 💭 Vision | aesthetic-theme-engine change |
| CSS variable system, settings UI | 💭 Vision | aesthetic-theme-engine change |
| Theme sequences, conditional activation | 💭 Vision | aesthetic-theme-engine change |

---

## Core Concept

Each theme is derived from the practice and philosophy of a specific artist or design collective documented in the Affinity Suite Techniques Catalogue. A theme is not a skin — it is an epistemological stance. It encodes compositional logic, color philosophy, relationship to material, tolerance for ambiguity, and orientation toward emergence versus control. When a user selects a theme, Polly's personas inherit that stance as their default aesthetic constitution.

### Design Principles

- **Operational aesthetics:** Themes are not decorative. They alter decision-making in measurable ways.
- **Artist fidelity:** Each theme should be recognizable to someone familiar with the source artist's work.
- **Composability:** Users can mix elements from multiple themes to create hybrid configurations.
- **Infinite game orientation:** Themes support continuation and exploration, not completion and optimization.
- **Domain permeability:** Theme choices in the Sights domain ripple into Sigils, Signals, Scrolls, and Glyphs.

---

## Architecture

### Theme Object Structure

Each theme is a configuration object with three layers: a **presentation layer** (UI rendering), a **behavior layer** (persona defaults), and a **metadata layer** (provenance, catalogue references, user modifications). Any property can be overridden individually when composing hybrid themes.

#### Presentation Layer

| Property | Description |
|---|---|
| `palette` | Primary, secondary, accent, background, surface, and text colors with hex values and semantic names |
| `typography` | Font stack, heading treatment, body treatment, monospace choice, tracking, weight hierarchy |
| `texture` | Background grain, surface treatment, noise level, aging effects, overlay behavior |
| `spacing` | Grid module size, gutter width, density preference (sparse→dense), alignment strictness |
| `motion` | Transition style, loading behavior, interaction feedback, animation philosophy (present/absent, subtle/dramatic) |
| `chrome` | Border treatment, shadow behavior, corner radius, divider style, element edges |

#### Behavior Layer

| Property | Type | Description |
|---|---|---|
| `designer.default_composition` | string | Compositional logic default (instruction-based, flow-field, grid-emergent, found-ephemera, overprint-layered, material-aware, systematic-variation) |
| `designer.color_logic` | string | Color decision method (structural, probabilistic-weighted, hauntological, overprint-mixing, restrained, perceptual-juxtaposition, material-derived) |
| `designer.turbulence` | float 0.0–1.0 | Tolerance for chaos versus order in generative outputs |
| `designer.material_awareness` | string | Whether outputs acknowledge constructed/digital nature or pursue seamlessness |
| `programmer.output_style` | string | Code aesthetic (systems-emergent, probabilistic, archival, layered-process, minimal-functional, parametric, constraint-driven) |
| `programmer.documentation` | string | Documentation style (rules-as-content, parameter-driven, institutional, process-log, brechtian-transparent, study-notes, material-first) |
| `programmer.abstraction_level` | string | Preference for abstraction versus concreteness |
| `writer.voice` | string | Prose character (procedural, warm-technical, hauntological-vague, process-aware, neutral-helvetica, observational, material-aware) |
| `writer.structure` | string | Written output organization (constellation, grid, flow, systematic-variation) |
| `systems.emergence_tolerance` | string | How much the system allows unexpected outcomes (high, medium-high, low-medium, medium, low) |
| `systems.constraint_philosophy` | string | Constraints as generative (Albers) or reductive (Jetset) |

#### Metadata Layer

| Property | Description |
|---|---|
| `source_artist` | Name and domain of originating artist |
| `catalogue_refs` | Array of technique numbers from the Affinity Techniques Catalogue |
| `core_principle` | Single-sentence summary of the aesthetic stance |
| `user_overrides` | Object tracking any user modifications from base theme |

### Theme Registry

Themes are stored as JSON configuration files in Polly's configuration directory (`~/.polly/themes/`). The registry maintains a manifest of available themes, the currently active theme, and any user-composed hybrid themes. Themes can be loaded, switched, composed, and exported.

### Persona Integration

When a theme is activated, each persona reads the behavior layer properties relevant to its domain. The persona does not override explicit user instructions — the theme provides defaults and tendencies, not mandates. The theme is the background hum, not the foreground command.

**Priority Hierarchy:**
1. Explicit user instruction (highest)
2. Task-specific requirements (e.g., accessibility standards override Riley's perceptual extremes)
3. Active theme behavior defaults
4. Persona base behavior (lowest)

See [personas spec](../personas/spec.md) for full integration protocol.

---

## Theme Definitions

Seven initial themes derived from the Affinity Techniques Catalogue.

### 1. Reas (Casey Reas)

**Core Principle:** Systems create emergence. Simple rules generate complex outcomes.
**Catalogue References:** #001 Flow Field Composition, #002 Emergence Grid System, #003 Instruction-Based Composition

**Presentation:**
- **Palette:** Monochromatic with structural accent. Off-white background (`#F8F6F3`), charcoal primary (`#2D2D2D`), system blue accent (`#3A6B9F`). Color is secondary to structure.
- **Typography:** Monospaced for all text (instruction-set aesthetic). Fira Code or JetBrains Mono. Code and content share the same voice.
- **Texture:** Clean, minimal grain. Subtle pixel grid visible at certain zoom levels. No aging effects.
- **Spacing:** Strict grid with visible construction lines as decorative elements. 8px base module.
- **Motion:** Elements emerge from simple starting positions. Loading states show rule application in sequence. Transitions are generative, not decorative.
- **Chrome:** Minimal borders. UI elements defined by position in grid, not by outlines. Negative space is structural.

**Behavior:**
- `designer.default_composition`: `instruction-based` — outputs include the rule set that generated them
- `designer.color_logic`: `structural` — color serves system legibility, not expression
- `designer.turbulence`: `0.3` — low chaos, high emergence through iteration
- `programmer.output_style`: `systems-emergent` — favor small composable functions that create complex behavior
- `programmer.documentation`: `rules-as-content` — documentation is executable instruction set
- `writer.voice`: `procedural` — clear, unambiguous, instruction-like
- `systems.emergence_tolerance`: `high` — let systems run and observe results

---

### 2. Fidenza (Tyler Hobbs)

**Core Principle:** Probabilistic systems with controlled chaos. Algorithmic aesthetics refined by hand.
**Catalogue References:** #006 Probabilistic Color Palette, #007 Non-Overlapping Ribbon Composition, #008 Turbulence Variation

**Presentation:**
- **Palette:** Weighted probabilistic selection from curated set. Cream (`#F2E8D5`, 40%), terracotta (`#C4653A`, 25%), deep blue (`#1B3A5C`, 20%), gold accent (`#D4A84B`, 10%), charcoal (`#2A2A2A`, 5%). Weights shift per-session.
- **Typography:** Humanist sans-serif. Source Sans Pro or similar. Warm, readable, not mechanical.
- **Texture:** Canvas grain at low opacity. Slight paper feel. No digital sharpness.
- **Spacing:** Organic. Elements maintain minimum spacing (collision avoidance) but positions are not grid-locked. Fluid density.
- **Motion:** Flowing curves and ribbons for transitions. Loading states show probabilistic settling. Turbulence parameter controls overall animation energy.
- **Chrome:** Thick, rounded elements. Ribbon-like containers. No sharp corners.

**Behavior:**
- `designer.default_composition`: `flow-field` — organic arrangement with collision detection
- `designer.color_logic`: `probabilistic-weighted` — every color choice uses weighted random selection
- `designer.turbulence`: `0.6` — user-adjustable; calm mode (0.2) to energetic mode (0.9)
- `programmer.output_style`: `probabilistic` — favor weighted randomization and configurable parameters
- `programmer.documentation`: `parameter-driven` — document ranges and weights, not just values
- `writer.voice`: `warm-technical` — precise but accessible; explain the math, but gently
- `systems.emergence_tolerance`: `medium-high` — control through probability, not determinism

---

### 3. Ghost Box (Julian House)

**Core Principle:** Memory over reference. The aesthetic of things remembered wrong.
**Catalogue References:** #015 Hauntological Color Palette, #016 Found Ephemera Collage, #017 Memory-Based Composition, #018 Institutional Typography

**Presentation:**
- **Palette:** Faded institutional. Worn orange (`#D4763A`), teal (`#2A7B8C`), paper brown (`#C4A77D`), muted red (`#8B3A3A`), worn cream (`#E8DCC4`), public information blue (`#4A6B82`). Everything feels yellowed and remembered.
- **Typography:** Institutional grotesque. Akzidenz Grotesk, Knockout, or Grotesque variants for headers. Clarendon or Rockwell for body. Tabular figures. Tight tracking on caps.
- **Texture:** Heavy. Foxing, paper grain, yellowed overlay, faded edges. UI surfaces feel like scanned index cards and bureaucratic forms.
- **Spacing:** Grid-based but imperfect. Slight misalignment as design feature. Form-like structure with boxes, rules, and reference numbers.
- **Motion:** Minimal. Slight flicker. VHS tracking artifacts on transitions. Things appear already present, not animated into existence.
- **Chrome:** Visible edges, torn borders, stamped marks. UI elements have the quality of found documents.

**Behavior:**
- `designer.default_composition`: `found-ephemera` — collage from accumulated reference, never direct
- `designer.color_logic`: `hauntological` — colors applied as if remembered, slightly off from source
- `designer.turbulence`: `0.2` — quiet, still, archival; motion is suspicious
- `designer.material_awareness`: `high` — everything looks printed, scanned, photocopied
- `programmer.output_style`: `archival` — code structured like filing systems and index cards
- `programmer.documentation`: `institutional` — documentation reads like government technical manuals
- `writer.voice`: `hauntological-vague` — allusive, indirect, working from impression
- `systems.emergence_tolerance`: `low-medium` — things are ordered but the order feels slightly wrong

---

### 4. Martens (Karel Martens)

**Core Principle:** Process is content. Each output is a unique artifact of layered making.
**Catalogue References:** #019 Digital Monoprint Process, #020 Found Metal Object Shape Library, #021 Overprint Color Mixing

**Presentation:**
- **Palette:** Overprint primaries. Red (`#E03030`), blue (`#2040A0`), yellow (`#E8C820`), with emergent greens, oranges, and browns from multiply-blended overlaps. Black only where all layers converge.
- **Typography:** Functional Dutch modernist. Univers or Frutiger. Weight used structurally. Clean but not sterile.
- **Texture:** Letterpress impression. Slight ink spread on type. Uncoated paper feel. Visible printing artifacts.
- **Spacing:** Modular grid. Systematic but flexible. Found-object shapes break grid where they land.
- **Motion:** Layered. Transitions show elements building up like successive print passes. Each color appears separately, then overlaps emerge.
- **Chrome:** Overlapping panels create emergent colors at intersections. Every UI element is a print pass.

**Behavior:**
- `designer.default_composition`: `overprint-layered` — build through transparent overlay, not direct placement
- `designer.color_logic`: `overprint-mixing` — never pre-mix colors; only base hues, let Multiply blending create the rest
- `designer.turbulence`: `0.4` — controlled process with room for material accident
- `programmer.output_style`: `layered-process` — each function is a print pass; composition through combination
- `programmer.documentation`: `process-log` — documentation tracks the sequence of making, not just the result
- `writer.voice`: `process-aware` — describe the making, not just the outcome
- `systems.emergence_tolerance`: `medium` — controlled emergence through material process

---

### 5. Jetset (Experimental Jetset)

**Core Principle:** Material awareness. The medium refuses to disappear.
**Catalogue References:** #022 Material Awareness Typography, #023 Helvetica as Neutral Voice, #024 Restrained Palette, #025 Brechtian Gesture Design

**Presentation:**
- **Palette:** Strictly limited. Black (`#000000`), white (`#FFFFFF`), red (`#FF0000`), blue (`#0000FF`). No gradients. No intermediate values. Full saturation only.
- **Typography:** Helvetica. Only Helvetica. Neue Haas Grotesk if necessary. Variation through weight and size only. Never a second typeface.
- **Texture:** None — but production artifacts visible. Crop marks, registration marks, fold lines as decorative elements. The medium shows itself.
- **Spacing:** Strict grid. Generous margins. Visible construction. Grid lines shown, not hidden.
- **Motion:** Minimal to none. If present, motion reveals structure (unfolding, printing, registering). Never decorative motion.
- **Chrome:** Crop marks at corners. Fold lines. Registration targets. The UI is a printed sheet that knows it's a printed sheet.

**Behavior:**
- `designer.default_composition`: `material-aware` — every output includes gestures that reveal its construction
- `designer.color_logic`: `restrained` — four colors maximum; deviation is a conscious, documented choice
- `designer.turbulence`: `0.1` — maximum restraint; every element is deliberate
- `designer.material_awareness`: `maximum` — the design always acknowledges that it is design
- `programmer.output_style`: `minimal-functional` — fewest possible abstractions; code is transparent about what it does
- `programmer.documentation`: `brechtian-transparent` — documentation breaks the fourth wall; comments explain why, not what
- `writer.voice`: `neutral-helvetica` — ego-less; content speaks, voice does not perform
- `systems.constraint_philosophy`: `reductive` — constraints remove options to clarify what remains

---

### 6. Riley (Bridget Riley)

**Core Principle:** Perception is the content. Systematic variation reveals how seeing works.
**Catalogue References:** #031 Perceptual Color Mixing, #032 Stripe as Neutral Form, #033 Systematic Variation Study, #034 Movement Through Modulation

**Presentation:**
- **Palette:** Perceptual interaction sets. Colors chosen for what happens between them, not individual quality. High saturation, similar value. Complementary and triadic pairings that vibrate optically.
- **Typography:** Minimal, recessive. Small, light-weight sans-serif that never competes with color. Text is functional, never decorative.
- **Texture:** None. Pure color and form. Any texture would interfere with perceptual effects.
- **Spacing:** Stripe-based. Navigation and panels defined by systematic stripe variation. Width modulates to create movement and hierarchy.
- **Motion:** Optical. Static elements that appear to move through modulation. Compression, expansion, and curvature in patterns. No literal animation needed.
- **Chrome:** Stripe boundaries define all elements. No borders — edges are where one color field meets another.

**Behavior:**
- `designer.default_composition`: `systematic-variation` — explore one parameter across a series, not many parameters at once
- `designer.color_logic`: `perceptual-juxtaposition` — colors chosen for interaction effects, not individual appeal
- `designer.turbulence`: `0.0–0.3` — systematic, not chaotic; variation is controlled and documented
- `programmer.output_style`: `parametric` — code structured around variable isolation and systematic testing
- `programmer.documentation`: `study-notes` — documentation records what was varied, what was observed
- `writer.voice`: `observational` — precise description of perception and effect
- `systems.emergence_tolerance`: `low` — emergence through careful study, not through chaos

---

### 7. Albers (Anni Albers)

**Core Principle:** The grid is generative, not restrictive. Material leads, concept follows.
**Catalogue References:** #035 Grid as Generative Constraint, #036 Woven Pattern Construction, #037 Material-First Design Thinking, #038 Floating Weft Line Drawing

**Presentation:**
- **Palette:** Material-derived. Warm earth tones, fiber colors, natural dye spectrum. Unbleached (`#E8DBC4`), indigo (`#2B3A67`), madder red (`#A0423A`), ochre (`#C4923A`), charcoal (`#3A3A3A`). Colors reference physical materials.
- **Typography:** Woven quality. Monospaced or pixel fonts that feel like they belong on a grid. Each character occupies equal space, like threads on a loom.
- **Texture:** Woven. Canvas, linen, thread-crossing patterns as background texture. Tactile, material presence.
- **Spacing:** Absolute grid adherence. Every element snaps strictly. Grid visible as warp/weft structure. Complexity emerges from grid-allowed combinations, not from breaking the grid.
- **Motion:** Weaving. Elements interlace, pass over and under each other. Loading states show thread-by-thread construction.
- **Chrome:** Woven intersections. Panels overlap with over-under logic. Borders are threads.

**Behavior:**
- `designer.default_composition`: `grid-emergent` — strict grid adherence creates complexity through combination
- `designer.color_logic`: `material-derived` — colors reference physical materials and processes
- `designer.turbulence`: `0.0` — zero deviation from grid; complexity comes from within the constraint
- `designer.material_awareness`: `maximum` — material leads to discovery, not self-reference (contrast with Jetset)
- `programmer.output_style`: `constraint-driven` — define the grid first, then find what the grid allows
- `programmer.documentation`: `material-first` — documentation starts with what the tool does, not what you want
- `writer.voice`: `material-aware` — begin from material observation, let ideas emerge from handling
- `systems.constraint_philosophy`: `generative` — constraints create possibilities, not limitations

---

## Theme Comparison Matrix

| Dimension | Reas | Fidenza | Ghost Box | Martens | Jetset | Riley | Albers |
|---|---|---|---|---|---|---|---|
| **Turbulence** | 0.3 | 0.6 | 0.2 | 0.4 | 0.1 | 0.0–0.3 | 0.0 |
| **Color approach** | Structural | Probabilistic | Hauntological | Overprint | Restrained | Perceptual | Material |
| **Grid strictness** | Strict | Organic | Imperfect | Modular | Strict | Stripe-based | Absolute |
| **Texture** | Minimal | Canvas grain | Heavy/aged | Letterpress | None (artifacts) | None | Woven |
| **Motion** | Generative | Flowing | Minimal/flicker | Layered | None/structural | Optical illusion | Weaving |
| **Typography** | Monospaced | Humanist sans | Institutional | Dutch modern | Helvetica only | Recessive sans | Grid/pixel |
| **Emergence** | High | Medium-high | Low-medium | Medium | Low | Low | Low (within grid) |
| **Material awareness** | Low | Low | High | Medium | Maximum | None | Maximum |

---

## Theme Composability

### Hybrid Theme Construction

Users can compose hybrid themes by selecting presentation properties from one theme and behavior properties from another. The composability system operates at the property level.

**Composition Rules:**
- **Layer independence:** Presentation, behavior, and metadata layers can be sourced from different themes.
- **Property-level override:** Individual properties within a layer can come from different themes.
- **Conflict resolution:** When composed properties conflict (e.g., Jetset's no-texture with Ghost Box's heavy-texture), last-specified value wins. The system logs conflicts for user review.
- **Inheritance:** Unspecified properties inherit from a base theme (default: Reas as most structurally neutral).

### Example Compositions

| Composition | Effect |
|---|---|
| **Martens color + Albers grid + House typography** | Overprint color mixing on strict woven grid with institutional grotesque type. Process-driven making within absolute structural constraint, documented in bureaucratic voice. |
| **Fidenza behavior + Jetset presentation** | Probabilistic decision-making expressed through black/white/red/blue restraint. Tension between organic logic and strict visual vocabulary. |
| **Riley color + Reas structure + Albers constraint** | Perceptual color interaction organized by instruction-based systems on strict grid. Scientific rigor across all three domains. |

### Composition Interface

In Settings, users see a matrix of themes versus property categories. They can drag individual properties or entire layers from source themes into their active configuration. A live preview shows the result. Composed themes are saved to `~/.polly/themes/` with full provenance tracking.

---

## Cross-Domain Ripple

Theme effects are not siloed by persona. When the Ghost Box theme is active, the writer persona's hauntological voice influences how the programmer persona comments code. The Albers theme's material-first approach affects how the systems-thinker persona frames problem analysis. This cross-domain permeability is intentional and mirrors the five-domain interconnection principle.

**Ripple Examples:**
- **Ghost Box active, programmer persona:** Code comments read like declassified technical documents. Variable names reference institutional systems. File organization mimics archival filing.
- **Fidenza active, writer persona:** Prose uses weighted emphasis — some ideas recur with probability-weighted frequency. Structure is organic, not grid-locked. Metaphors drawn from flow and turbulence.
- **Jetset active, systems persona:** Analysis is restrained to essential variables. Frameworks use minimum necessary components. Diagrams are black/white/red/blue only.

---

## Implementation

### Theme File Format

Themes are stored as JSON files conforming to a `polly-theme` schema. Each file is self-contained with all presentation, behavior, and metadata properties. Schema version is tracked for forward migration.

**Storage:** `~/.polly/themes/` — one `.json` per theme
**Active theme:** Runtime property of the Polly session, persisted in user config
**Switching:** Non-destructive and immediate; mid-conversation switch does not alter previous outputs

### Data Model

```
~/.polly/themes/
  reas.json
  fidenza.json
  ghost-box.json
  martens.json
  jetset.json
  riley.json
  albers.json
  custom/
    user-hybrid-1.json
    ...
```

### API (Planned)

| Endpoint | Method | Description |
|---|---|---|
| `/themes/list` | GET | Available themes and active theme |
| `/themes/active` | GET | Current theme configuration (resolved, including overrides) |
| `/themes/switch` | POST | Switch active theme |
| `/themes/compose` | POST | Create hybrid from source themes + overrides |
| `/themes/export` | GET | Export theme as standalone JSON |
| `/themes/import` | POST | Import theme from JSON |

### Frontend

- **Settings page:** Theme browser with live preview. Composition matrix for hybrid themes.
- **Quick switcher:** Command palette or ribbon shortcut for theme switching.
- **CSS variable mapping:** Presentation layer properties map to CSS custom properties for real-time switching.
- **Persona UI hints:** Theme-aware persona indicators (e.g., Ghost Box stamps on persona badge).

### Backend

- **Theme loader:** `core/themes/loader.py` — reads theme JSON, resolves inheritance and overrides
- **Persona adapter:** `core/themes/persona_adapter.py` — feeds behavior layer to persona system prompt construction
- **Composition engine:** `core/themes/composer.py` — handles hybrid creation, conflict detection, provenance tracking

---

## Theme Development

New themes can be created through three paths:

1. **Catalogue derivation:** Analyze a new artist from the Affinity Techniques Catalogue and populate the theme schema from their practice.
2. **User composition:** Compose a hybrid from existing themes using the composability system.
3. **Manual creation:** Define all properties from scratch, useful for themes not derived from specific artists.

### Extension Points

- **Custom properties:** The behavior layer accepts arbitrary key-value pairs for domain-specific needs.
- **Conditional activation:** Themes can include conditions (time of day, domain context, project type) that modulate property values.
- **Theme sequences:** Users can define sequences of themes that rotate on a schedule, supporting the daily practice orientation.

---

## Future Themes

| Theme | Source | Key Character |
|---|---|---|
| **Schaff** | William Schaff | Dense layered collage. Heavy ink/gouache texture, music iconography, found text integration. High density, dark palette, scratchboard UI elements. Catalogue: #009–012 |
| **Weaver** | Mark Weaver | Retro-geometric daily practice. Vintage color treatment, bold geometric overlays, daily rotation of theme parameters. Catalogue: #013–014 |
| **Metahaven** | Metahaven | Research-accumulative, critical design stance. Opacity as conceptual tool. Visual research constellation layout. Catalogue: #026–027 |
| **Frank** | Tina Frank / Mego | Synesthetic. High saturation, pulsating patterns, sound-to-visual translation in UI feedback. Aggressive and sensory. Catalogue: #028–030 |
| **Lieberman** | Zach Lieberman | Daily sketch practice as operational principle. Theme changes daily. Constraint rotation built into the system. Export-at-timer-end philosophy. Catalogue: #004–005 |
| **User-submitted** | Community | Community-contributed themes following the schema, reviewed for coherence and artist fidelity. |
| **Domain-triggered** | System | Automatic theme switching based on active domain (e.g., Sigils activates Reas, Signals activates Frank). |

---

## Theme → Generative Design Engine

The `designer.*` behavior layer properties gain concrete operational meaning through the Designer persona's p5.js generative pipeline. These properties don't just influence prompts — they constrain the generative engine that produces icons, patterns, feature images, and other design assets.

### Constraint Mapping

| Theme Property | Generator Effect |
|----------------|-----------------|
| `designer.default_composition` | Composition algorithm selection: `instruction-based` → rule-set generation, `flow-field` → organic curves, `found-ephemera` → collage/stamp, `overprint-layered` → transparency layers, `material-aware` → production artifacts, `systematic-variation` → parameter study, `grid-emergent` → strict grid |
| `designer.color_logic` | Color selection strategy: `structural` → monochrome, `probabilistic-weighted` → weighted random from palette, `hauntological` → desaturated/shifted, `overprint-mixing` → multiply blend, `restrained` → max 4 colors, `perceptual-juxtaposition` → optical interaction, `material-derived` → earth tones |
| `designer.turbulence` | Maps directly to p5.js `noise()` and random seed parameters. 0.0 → zero deviation, 1.0 → maximum chaos. |
| `designer.material_awareness` | Post-processing: `none` → clean digital, `high` → aging/scan effects, `maximum` → crop marks/registration/fold lines |

### Example: Same Icon, Different Themes

Requesting "generate a home icon" produces different results under each theme:

- **Reas** (turbulence: 0.3, instruction-based): Clean geometric construction. Visible grid alignment. Icon feels like a diagram with clear instruction-set logic.
- **Fidenza** (turbulence: 0.6, flow-field): Organic curves with weighted randomness. Slight irregularity gives hand-drawn quality. Color weighted from curated palette.
- **Ghost Box** (turbulence: 0.2, found-ephemera): Stamp-like quality. Slight misregistration. Feels like a symbol from a government technical manual.
- **Martens** (turbulence: 0.4, overprint-layered): Layers build up like print passes. Color from overprint mixing. Process visible in output.
- **Jetset** (turbulence: 0.1, material-aware): Maximum restraint. Black stroke only. Crop marks visible. The icon knows it's a design artifact.
- **Riley** (turbulence: 0.0–0.3, systematic-variation): Minimal form. Stripe-like elements. Systematic variation across stroke weight.
- **Albers** (turbulence: 0.0, grid-emergent): Absolute grid adherence. Woven quality. Complexity from grid-allowed combinations only.

### Integration with Per-Project Design Systems

When a theme is active and a project has a `_design/system.yml`, the constraint resolution priority is:

1. Explicit user request (highest)
2. Active theme `designer.*` properties
3. Project `system.yml` defaults (lowest)

The theme mediates between the user's aesthetic intent and the design system's concrete tokens. Switching themes can regenerate assets within the same design system, exploring different aesthetic interpretations of the same structural constraints.

See [personas spec](../personas/spec.md) for full Designer persona details and [design spec](../design/spec.md) for the per-project design system format.

---

## Relationship to Other Systems

| System | Theme Integration |
|---|---|
| **Personas** | Behavior layer feeds persona system prompt defaults. See [personas spec](../personas/spec.md) |
| **Designer (Generate mode)** | `designer.*` properties constrain p5.js generative pipeline. Theme changes alter generated assets. See [personas spec](../personas/spec.md) |
| **Design Systems** | Theme presentation layer can seed project `system.yml`. Theme → design token derivation. See [design spec](../design/spec.md) |
| **Domains** | Domain-triggered theme switching; theme palette integrates with domain color config. See [domains spec](../domains/spec.md) |
| **UI** | Presentation layer maps to CSS custom properties and design system tokens. See [ui spec](../ui/spec.md) |
| **Design** | Themes implement the operational aesthetics principle. See [design spec](../design/spec.md) |
| **Code Library** | Generator scripts are reusable library modules. Theme presets parameterize them. See [code-library spec](../code-library/spec.md) |
| **Agent Swarms** | Theme behavior layer propagates through Nexus to all agents in a workflow |
| **Publishing** | Theme presentation influences published output styling (POSE pipeline). Feature images generated via Designer(Generate) inherit theme constraints. See [publishing spec](../publishing/spec.md) |
| **Settings** | Theme browser, composition matrix, and quick switcher in Settings page |

---

## Reference

- Affinity Suite Techniques Catalogue — 38 techniques across 12 artists (generative, collage, designer-artist, sound-visual, abstract/pattern)
- [personas spec](../personas/spec.md) — Persona integration protocol
- [ui spec](../ui/spec.md) — UI design system
- [design spec](../design/spec.md) — Design philosophy
- [domains spec](../domains/spec.md) — Domain configuration
- Designer persona (Phase 27): [docs/planning/phases/other/PHASE27_DESIGNER_PERSONA.md](../../../docs/planning/phases/other/PHASE27_DESIGNER_PERSONA.md)
- Designer profile change: [openspec/changes/designer-profile/](../../changes/designer-profile/)
- Code library: [code-library spec](../code-library/spec.md)
- Per-project design systems: [design spec](../design/spec.md)
