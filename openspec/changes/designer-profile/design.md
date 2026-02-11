# Designer Profile — Design

**Created:** February 2026  
**Impact:** Python backend (`core/design/`), Electron frontend, project file system (`_design/`), themes integration, code library integration, publishing pipeline

---

## Part 1: p5.js Generative Design Pipeline

### Pipeline Overview

```
User need ("I need icons for my navigation")
        ↓
Designer persona defines constraints
  - Canvas: 24x24 viewBox (Lucide-compatible)
  - Style: stroke-based, 2px stroke, round caps/joins
  - Palette: currentColor (inherits from parent)
  - Grid: snap to 24x24 grid where possible
  - Theme influence: active theme's designer.* properties
        ↓
AI generates p5.js sketch
  - Uses p5.js-svg library (zenozeng) for SVG output
  - Produces vector output, not raster
  - Parametric — stroke weight, size, palette are variables
        ↓
SVG output
  - Clean, optimized SVG (SVGO post-processing)
  - Format-compatible (Lucide, Affinity Designer, web)
  - Added to project's _design/ asset library
        ↓
Optionally: refine in external tool
  - Affinity Designer (Lucide template available)
  - Figma, Inkscape, or any SVG editor
```

### Asset Types

| Type                    | Description                     | Constraints                                  | Use Case                              |
| ----------------------- | ------------------------------- | -------------------------------------------- | ------------------------------------- |
| **Custom icons**        | Lucide-compatible vector icons  | 24x24 viewBox, stroke-based, 2px, round caps | Navigation, UI, branded icons         |
| **Pattern tiles**       | Repeating SVG patterns          | Tileable, configurable density               | Backgrounds, textures, dividers       |
| **Feature images**      | Generative compositions         | Configurable dimensions, palette, mood       | Blog posts (POSE → Ghost CMS), social |
| **Data visualizations** | Charts, diagrams                | Match project design system tokens           | Reports, dashboards, explanations     |
| **UI micro-elements**   | Spinners, dividers, decorations | Match project chrome and spacing             | Interface polish                      |

### Lucide Icon Generation Rules

Lucide's guidelines are precise and enforceable programmatically:

```yaml
# Encoded as constraint set for p5.js generator
icon_constraints:
  viewBox: "0 0 24 24"
  transforms: none # No SVG transforms
  filters: none # No SVG filters
  fills: none # No explicit fills
  explicit_strokes: none # Stroke attributes on root <svg> only
  stroke_linecap: round
  stroke_linejoin: round
  stroke_width: 2 # Default, configurable
  grid_alignment: preferred # Snap to 24x24 grid where possible
  naming: lower-kebab-case # Describe depiction, not use case
  visual_weight: balanced # Blur test: should match reference icons
```

### p5.js-svg Technical Details

- **Library:** zenozeng/p5.js-svg — renders p5.js canvas to SVG DOM
- **p5.js version:** Pinned to 1.6.0 (compatibility requirement)
- **Runtime model:** Build-step, not runtime. Generate SVG, discard sketch.
- **Post-processing:** SVGO for cleanup — strip unnecessary attributes, minify paths, remove metadata

### Theme → Generator Constraint Mapping

The Aesthetic Theme Engine's `designer.*` behavior properties directly constrain the p5.js generation pipeline. This is the key integration: the theme doesn't just set prompt defaults — it controls the generative engine.

| Theme Property                 | Generator Effect                                                                                                                                                                                                                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `designer.default_composition` | Composition algorithm: `instruction-based` → rule-set, `flow-field` → organic curves, `found-ephemera` → collage, `overprint-layered` → transparency layers, `material-aware` → production artifacts, `systematic-variation` → parameter study, `grid-emergent` → strict grid                                             |
| `designer.color_logic`         | Color selection: `structural` → monochrome for legibility, `probabilistic-weighted` → weighted random from palette, `hauntological` → desaturated/shifted, `overprint-mixing` → multiply blend primaries, `restrained` → max 4 colors, `perceptual-juxtaposition` → optical interaction, `material-derived` → earth tones |
| `designer.turbulence`          | Noise/randomness: 0.0 → zero deviation, 1.0 → maximum chaos. Maps directly to p5.js `noise()` and random seed parameters.                                                                                                                                                                                                 |
| `designer.material_awareness`  | Production artifact inclusion: `none` → clean digital, `high` → print/scan effects, `maximum` → crop marks/registration/fold lines                                                                                                                                                                                        |

**Example — Same icon request, different themes:**

- **Reas theme** (`turbulence: 0.3`, `composition: instruction-based`): Clean, geometric, rule-derived. Minimal noise. Icon feels like a diagram.
- **Fidenza theme** (`turbulence: 0.6`, `composition: flow-field`): Organic curves, weighted randomness. Icon has slight irregularity, hand-drawn quality.
- **Ghost Box theme** (`turbulence: 0.2`, `composition: found-ephemera`): Feels like a stamp or found symbol. Slight misregistration. Institutional quality.
- **Albers theme** (`turbulence: 0.0`, `composition: grid-emergent`): Absolute grid. Woven quality. Complexity from grid combinations, zero randomness.

---

## Part 2: Per-Project Design System

### Directory Structure

```
project/
├── _design/
│   ├── system.yml           # Design tokens (colors, typography, spacing, icons)
│   ├── palette.svg          # Visual reference for color palette
│   ├── icons/               # Custom icon set
│   │   ├── registry.json    # Icon metadata, tags, categories
│   │   ├── home.svg
│   │   ├── rune-fehu.svg
│   │   └── ...
│   ├── patterns/            # Repeating patterns and textures
│   │   ├── noise-bg.svg
│   │   └── wave-divider.svg
│   ├── components/          # Component specs (structure, not full implementations)
│   │   ├── card-grid.md
│   │   └── nav-header.md
│   └── generators/          # p5.js sketches that produced assets
│       ├── icon-generator.js
│       └── pattern-tile.js
```

### `system.yml` Schema

```yaml
name: polly-ui
version: 1.0
updated: 2026-02-09
theme_source: reas # Active Polly theme that influenced this system

colors:
  primary: "#1a1a2e"
  secondary: "#16213e"
  accent: "#e94560"
  surface: "#f5f5f5"
  text: "#1a1a2e"
  muted: "#6b7280"

typography:
  heading:
    family: "Inter"
    weights: [600, 700]
  body:
    family: "Inter"
    weights: [400, 500]
  mono:
    family: "JetBrains Mono"
    weights: [400, 500]

spacing:
  unit: 4px
  scale: [4, 8, 12, 16, 24, 32, 48, 64, 96]

icons:
  viewBox: "0 0 24 24"
  strokeWidth: 2
  strokeLinecap: round
  strokeLinejoin: round
  source: lucide # Base set, extended with custom icons

breakpoints:
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1280px

chrome:
  borderRadius: 8px
  shadowStyle: subtle # none, subtle, dramatic
  dividerStyle: line # line, pattern, stripe
```

### Icon Registry Schema (`icons/registry.json`)

```json
{
  "version": 1,
  "icons": [
    {
      "name": "rune-fehu",
      "file": "rune-fehu.svg",
      "tags": ["rune", "elder-futhark", "wealth"],
      "category": "custom",
      "generator": "../generators/icon-generator.js",
      "params": { "glyph": "fehu", "style": "lucide" },
      "created": "2026-02-09",
      "theme_at_creation": "reas"
    }
  ]
}
```

---

## Part 3: Designer Persona Expansion

### Expanded Mode Table

| Mode         | Original Scope                                        | Expanded With                                                                                                                                                      |
| ------------ | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Vision**   | Mood boards, design briefs, aesthetic guidance        | Theme-informed design direction. Cross-domain awareness (Signals needs, Scrolls feature images, Sigils UI).                                                        |
| **Mockup**   | UI mockup descriptions, wireframe specs               | Sitemap → wireframe thinking (Relume-inspired). Component selection from design system.                                                                            |
| **Critic**   | Accessibility audit, consistency check, UX heuristics | **Design system consistency checking.** "This component doesn't match your `system.yml`." Compare generated assets against active design tokens.                   |
| **System**   | Design tokens, component library docs, style guide    | **Full design system management.** Create, update, and maintain `_design/` directory. Generate `system.yml` from theme. Manage icon registry.                      |
| **Generate** | _(NEW)_                                               | **p5.js generative asset creation.** Icon sets, pattern tiles, feature images, data viz, UI micro-elements. Constraint-driven: define rules, generate within them. |

### Generate Mode Details

```python
# Designer persona in Generate mode
class DesignerGenerateMode:
    """
    Constraint-driven generative design using p5.js-svg.
    Theme behavior layer properties constrain the generator.
    """

    capabilities = [
        "icon_generation",        # Lucide-compatible custom icons
        "pattern_generation",     # Repeating SVG tiles
        "feature_image",          # Compositions for blog/social
        "data_visualization",     # Charts matching design system
        "micro_element",          # Spinners, dividers, decorations
    ]

    def generate(self, request, constraints, theme_behavior, design_system):
        """
        1. Parse request (what asset, what for)
        2. Merge constraints: explicit + theme.designer.* + design_system tokens
        3. Generate p5.js sketch
        4. Execute sketch → SVG
        5. Post-process (SVGO)
        6. Add to _design/ directory
        7. Update registry
        """
```

### Persona ↔ Design System Relationships

| Persona        | Design System Role                                                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Designer**   | Creates and maintains the system. Generates assets that conform to it. Flags inconsistencies via Critic mode.                            |
| **Programmer** | References `system.yml` when implementing UI. Uses design tokens rather than hardcoded values. Pulls from `icons/` directory.            |
| **Architect**  | Considers design system implications in technical decisions. "If we use Tailwind, the spacing scale maps directly to our design tokens." |
| **Scribe**     | Publishes content that respects the design system. Feature images follow palette. Typography matches blog theme.                         |

---

## Part 4: Code Library Integration

Design outputs feed directly into the code library system:

### Design Components as Library Modules

A Tailwind card grid component, built and styled within a design system, becomes a library module (Agent Skills format):

```
_polly/library/components/tailwind-card-grid/
├── SKILL.md              # Description, when to use, design system requirements
├── scripts/
│   └── card-grid.tsx     # Implementation
├── references/
│   └── design-notes.md   # Design decisions, accessibility notes
└── assets/
    └── preview.svg       # Visual preview
```

### Generator Scripts as Instruments

p5.js sketches are themselves reusable. The icon generator with Lucide constraints can be parameterized for any project:

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

### Design Systems as Templates

A well-developed `system.yml` becomes a starting point for new projects:

```
_polly/library/workflows/design-system-starter/
├── SKILL.md              # How to customize, which tokens to change
├── assets/
│   ├── system.yml        # Template system with placeholder values
│   └── directory.md      # _design/ structure documentation
```

---

## Part 5: Publishing Pipeline Integration

### Feature Image Generation for POSE

Every Ghost CMS post needs a feature image. The Designer's Generate mode provides this:

```
Draft ready for publish
        ↓
Scribe passes topic + constraints to Designer(Generate)
  - Dimensions: 1200x630 (OpenGraph standard)
  - Palette: from active design system
  - Mood: inferred from post content and domain
  - Theme: active theme's designer.* properties
        ↓
p5.js generates composition → SVG → optional PNG export
        ↓
Feature image attached to publication draft
        ↓
Published to Ghost CMS with post
```

This is an Agent Swarms composition: `Scribe(Publish) → Designer(Generate) → Scribe(Publish)`.

---

## Part 6: Key Types (Python Backend)

```python
# core/design/models.py

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class AssetType(str, Enum):
    ICON = "icon"
    PATTERN = "pattern"
    FEATURE_IMAGE = "feature_image"
    DATA_VIZ = "data_viz"
    MICRO_ELEMENT = "micro_element"

@dataclass
class DesignConstraints:
    """Constraints for generative design. Merged from explicit request + theme + design system."""
    canvas_width: int = 24
    canvas_height: int = 24
    palette: list[str] = field(default_factory=list)
    stroke_width: float = 2.0
    stroke_linecap: str = "round"
    stroke_linejoin: str = "round"
    composition: str = "instruction-based"  # From theme
    color_logic: str = "structural"          # From theme
    turbulence: float = 0.3                  # From theme
    material_awareness: str = "none"         # From theme
    grid_alignment: bool = True
    fill: bool = False

@dataclass
class DesignSystem:
    """A project's design system (loaded from system.yml)."""
    name: str
    version: str
    colors: dict                    # Token name → hex value
    typography: dict                # heading/body/mono families + weights
    spacing: dict                   # unit + scale
    icons: dict                     # viewBox, strokeWidth, source
    breakpoints: dict               # sm/md/lg/xl
    chrome: dict                    # borderRadius, shadowStyle, dividerStyle
    theme_source: Optional[str] = None

@dataclass
class GeneratedAsset:
    """An asset produced by the p5.js pipeline."""
    name: str
    asset_type: AssetType
    svg_content: str                # Clean SVG string
    generator_script: str           # p5.js source that produced it
    constraints: DesignConstraints
    theme_at_creation: Optional[str] = None
    file_path: Optional[str] = None  # Path in _design/
```

## Part 7: Core API

```python
# core/design/engine.py

class DesignEngine:
    """Generative design engine. Produces SVG assets via p5.js pipeline."""

    def __init__(self, config, theme_manager=None, design_system=None):
        """
        Args:
            config: Polly config
            theme_manager: For reading active theme behavior layer
            design_system: Active project's DesignSystem
        """

    # --- Constraint Resolution ---
    def resolve_constraints(self, explicit: dict, asset_type: AssetType) -> DesignConstraints:
        """Merge: explicit request + active theme designer.* + design system tokens.
        Explicit overrides theme, theme overrides design system defaults."""

    # --- Generation ---
    def generate_icon(self, name: str, description: str,
                      constraints: DesignConstraints = None) -> GeneratedAsset:
        """Generate a Lucide-compatible icon via p5.js-svg."""

    def generate_pattern(self, name: str, pattern_type: str,
                         constraints: DesignConstraints = None) -> GeneratedAsset:
        """Generate a repeating SVG pattern tile."""

    def generate_feature_image(self, topic: str, dimensions: tuple = (1200, 630),
                                constraints: DesignConstraints = None) -> GeneratedAsset:
        """Generate a feature image composition for publishing."""

    def generate_data_viz(self, data: dict, viz_type: str,
                          constraints: DesignConstraints = None) -> GeneratedAsset:
        """Generate a data visualization matching design system."""

    # --- Post-Processing ---
    def optimize_svg(self, svg_content: str) -> str:
        """Run SVGO optimization. Strip unnecessary attributes, minify paths."""

    # --- Design System ---
    def load_design_system(self, path: str) -> DesignSystem:
        """Load _design/system.yml."""

    def create_design_system(self, project_name: str,
                              theme: str = None) -> DesignSystem:
        """Create a new design system, optionally derived from a theme's palette."""

    def check_consistency(self, asset_path: str,
                          system: DesignSystem) -> list[dict]:
        """Check if an asset conforms to the design system. Returns issues."""

# core/design/system_manager.py

class DesignSystemManager:
    """Manages per-project _design/ directory and system.yml."""

    def __init__(self, project_path: str):
        """Initialize with path to project root."""

    def init_design_dir(self, system: DesignSystem) -> None:
        """Create _design/ directory structure and initial system.yml."""

    def add_icon(self, asset: GeneratedAsset) -> None:
        """Add icon to _design/icons/ and update registry.json."""

    def add_pattern(self, asset: GeneratedAsset) -> None:
        """Add pattern to _design/patterns/."""

    def save_generator(self, name: str, script: str) -> None:
        """Save p5.js generator script to _design/generators/."""

    def get_icon_registry(self) -> dict:
        """Load icons/registry.json."""

    def update_system(self, updates: dict) -> DesignSystem:
        """Update system.yml with new values."""

    def export_for_affinity(self, icon_name: str) -> str:
        """Export icon SVG in Affinity Designer-compatible format."""
```

## Part 8: REST API

| Method | Endpoint                             | Description                       |
| ------ | ------------------------------------ | --------------------------------- |
| `POST` | `/api/design/generate/icon`          | Generate icon with constraints    |
| `POST` | `/api/design/generate/pattern`       | Generate pattern tile             |
| `POST` | `/api/design/generate/feature-image` | Generate feature image            |
| `POST` | `/api/design/generate/data-viz`      | Generate data visualization       |
| `GET`  | `/api/design/system`                 | Get current project design system |
| `POST` | `/api/design/system`                 | Create new design system          |
| `PUT`  | `/api/design/system`                 | Update design system              |
| `GET`  | `/api/design/icons`                  | List icons in registry            |
| `POST` | `/api/design/check`                  | Run consistency check             |
| `POST` | `/api/design/optimize`               | SVGO optimize an SVG              |

## Part 9: Frontend Impact

### Design Studio Page (within Designer persona context)

When Designer persona is active, the main workspace includes:

- **Asset gallery:** Grid of generated icons, patterns, images with thumbnails
- **Generator panel:** Define constraints, preview, generate, iterate
- **Design system viewer:** Visual rendering of `system.yml` tokens (color swatches, type specimens, spacing scale)
- **Consistency dashboard:** Design system conformance report

### Slash Commands

| Command                      | Description                              |
| ---------------------------- | ---------------------------------------- |
| `/design icon <description>` | Generate a Lucide-compatible icon        |
| `/design pattern <type>`     | Generate a pattern tile                  |
| `/design image <topic>`      | Generate a feature image                 |
| `/design system init`        | Create design system for current project |
| `/design system check`       | Run consistency check                    |
| `/design system show`        | Display current design tokens            |

---

## File Organization (New Backend Files)

```
core/
├── design/
│   ├── __init__.py
│   ├── models.py              # DesignConstraints, DesignSystem, GeneratedAsset, AssetType
│   ├── engine.py              # DesignEngine — p5.js generation pipeline
│   ├── system_manager.py      # DesignSystemManager — _design/ directory management
│   ├── constraint_resolver.py # Theme + system + explicit constraint merging
│   ├── svg_optimizer.py       # SVGO wrapper
│   └── lucide_rules.py        # Lucide design rules as enforceable constraints
interfaces/
├── design_api.py              # REST endpoints
```

---

## Performance Considerations

- **p5.js generation:** 1–5 seconds per asset (depends on complexity, runs as build step)
- **SVGO optimization:** <500ms per SVG
- **Design system load:** <50ms (YAML parse)
- **Consistency check:** <1 second per asset (rule evaluation)
- **Feature image generation:** 3–10 seconds (larger canvas, more complex composition)

---

## Reference

- Relume: AI-assisted web design (component library, sitemap → wireframe → design)
- Lucide icons: https://lucide.dev/guide/design/icon-design-guide
- p5.js-svg: https://github.com/zenozeng/p5.js-svg
- SVGO: https://github.com/svg/svgo
- Affinity Designer Lucide template: Available from Lucide project
- Themes spec: [themes spec](../../specs/themes/spec.md)
- Code Library spec: [code-library spec](../../specs/code-library/spec.md)
- Publishing spec: [publishing spec](../../specs/publishing/spec.md)
