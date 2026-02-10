# Designer Profile — Tasks

**Created:** February 2026  
**Order:** Backend before frontend. Design system format before generation. Generation before publishing integration.

---

## Priority Summary

| Priority | What | Rationale |
|----------|------|-----------|
| **Phase 1: Foundation** | Design system format, Lucide rules, p5.js-svg proof of concept | Establishes the artifact format and proves the generation pipeline |
| **Phase 2: Integration** | Designer↔Programmer handoff, feature images, Affinity export | Connects generation to real workflows |
| **Phase 3: Intelligence** | Consistency checking, generative variation, cross-project coherence | Adds design-aware behavior |

---

## Phase 1: Foundation (2–3 weeks)

### Task 1: Design System Models & Format

**Files:** `core/design/__init__.py`, `core/design/models.py`, `core/design/system_manager.py`

**Steps:**
1. [ ] Create `core/design/` package
2. [ ] Define dataclasses: `DesignSystem`, `DesignConstraints`, `GeneratedAsset`, `AssetType`
3. [ ] Implement `DesignSystemManager`:
   - `init_design_dir()` — create `_design/` directory structure
   - `load_system()` / `save_system()` — YAML I/O for `system.yml`
   - `add_icon()` — add to `icons/` + update `registry.json`
   - `add_pattern()` — add to `patterns/`
   - `save_generator()` — save p5.js script to `generators/`
   - `get_icon_registry()` — load and return `icons/registry.json`
   - `update_system()` — modify `system.yml` values
4. [ ] Create default `system.yml` template (Polly's own design tokens)
5. [ ] Write tests: `tests/test_design_system.py`

**Acceptance:** Can create `_design/` directory, write/read `system.yml`, add icons with registry tracking.

---

### Task 2: Lucide Constraint Rules

**Files:** `core/design/lucide_rules.py`

**Steps:**
1. [ ] Encode Lucide design guidelines as enforceable constraint set:
   - 24x24 viewBox validation
   - No transforms, filters, fills rule
   - Stroke attribute placement (root `<svg>` only)
   - Round linecap/linejoin
   - 2px default stroke width
   - Grid alignment scoring
   - Visual weight heuristic (bounding box area, stroke density)
   - Naming convention (lower-kebab-case, describe depiction not use case)
2. [ ] Implement `validate_icon_svg(svg_content) -> list[LintIssue]`
3. [ ] Implement `apply_lucide_constraints(constraints) -> DesignConstraints` — merge Lucide rules into any constraint set
4. [ ] Write tests with known-good and known-bad SVGs

**Acceptance:** Validator catches non-Lucide-compliant SVGs. Constraints produce Lucide-compatible output.

---

### Task 3: p5.js-svg Generation Pipeline

**Files:** `core/design/engine.py`, `core/design/svg_optimizer.py`

**Steps:**
1. [ ] Set up p5.js-svg execution environment:
   - p5.js 1.6.0 + zenozeng/p5.js-svg as build-step dependencies
   - Node.js headless execution (p5.js sketch → SVG DOM → string output)
   - Clean separation: Python orchestrates, Node executes sketch
2. [ ] Implement `DesignEngine`:
   - `generate_icon(name, description, constraints)` — generate Lucide-compatible icon
   - `generate_pattern(name, type, constraints)` — generate repeating tile
   - `generate_feature_image(topic, dimensions, constraints)` — generate composition
3. [ ] Implement `SvgOptimizer` (SVGO wrapper):
   - `optimize(svg_content) -> str` — strip unnecessary attributes, minify paths
   - Configure SVGO plugins: removeViewBox=false, removeDimensions=true, sortAttrs, mergePaths
4. [ ] Implement AI sketch generation:
   - Given description + constraints, generate p5.js sketch code via LLM
   - Execute sketch in headless Node
   - Capture SVG output
   - Post-process with SVGO
5. [ ] Proof of concept: generate a set of 5 Lucide-compatible icons from descriptions
6. [ ] Write tests: `tests/test_design_engine.py`

**Acceptance:** Given "home icon, minimalist" + Lucide constraints, produces a valid Lucide-compatible SVG. SVGO cleanup runs automatically.

---

### Task 4: Theme → Constraint Resolution

**Files:** `core/design/constraint_resolver.py`

**Steps:**
1. [ ] Implement `ConstraintResolver`:
   - Read active theme's `designer.*` behavior properties from theme manager
   - Read project's `system.yml` design tokens
   - Merge: explicit request overrides theme, theme overrides design system defaults
2. [ ] Map theme properties to generator parameters:
   - `designer.default_composition` → composition algorithm selection
   - `designer.color_logic` → color selection strategy
   - `designer.turbulence` → noise/random seed parameters
   - `designer.material_awareness` → post-processing effects (aging, artifacts)
3. [ ] Implement theme-derived generation presets:
   - Each theme definition produces a named preset for the generator
   - User can request: "generate icon using Fidenza style" without configuring every parameter
4. [ ] Write tests: generate same icon with 3 different theme presets, verify visual differences

**Acceptance:** Same icon request under Reas vs. Fidenza vs. Albers themes produces meaningfully different SVG output.

---

### Task 5: Design REST API

**Files:** `interfaces/design_api.py`, `interfaces/server.py` (register routes)

**Steps:**
1. [ ] Create `interfaces/design_api.py` with endpoints:
   - `POST /api/design/generate/icon` — generate icon
   - `POST /api/design/generate/pattern` — generate pattern
   - `POST /api/design/generate/feature-image` — generate feature image
   - `GET /api/design/system` — get current design system
   - `POST /api/design/system` — create design system
   - `PUT /api/design/system` — update design system
   - `GET /api/design/icons` — list icon registry
   - `POST /api/design/check` — consistency check
2. [ ] Register routes in `interfaces/server.py`
3. [ ] Add design config section to `config.yaml`
4. [ ] Write API tests

**Acceptance:** All generation and design system operations accessible via REST.

---

## Phase 2: Integration (2–3 weeks)

### Task 6: Designer Persona Enhancement

**Files:** `core/personas/implementations/designer.py` (extend), persona skills

**Steps:**
1. [ ] Expand Designer persona with Generate mode:
   - Register `generate` capabilities: icon, pattern, feature_image, data_viz, micro_element
   - Generate mode uses `DesignEngine` for asset creation
   - Results returned as GeneratedAsset with SVG preview
2. [ ] Enhance System mode with design system management:
   - Create/load/update `_design/system.yml` via `DesignSystemManager`
   - Generate `system.yml` from active theme's presentation layer
   - Manage icon registry
3. [ ] Enhance Critic mode with consistency checking:
   - Compare generated assets against `system.yml` tokens
   - Report: "This icon uses colors not in your palette"
   - Lucide rule validation
4. [ ] Add Designer skills:
   - `skills/designer/lucide-guidelines.md` — Lucide design rules
   - `skills/designer/design-system-management.md` — How to maintain a design system
   - `skills/designer/generative-constraints.md` — Constraint-driven design philosophy
5. [ ] Wire into Agent Swarms capability declaration
6. [ ] Write tests

**Acceptance:** Designer(Generate) produces SVG assets. Designer(System) manages `_design/`. Designer(Critic) validates consistency.

---

### Task 7: Designer ↔ Programmer Handoff

**Files:** `core/design/system_manager.py` (extend)

**Steps:**
1. [ ] Design token export formats:
   - CSS custom properties from `system.yml`
   - Tailwind config from `system.yml`
   - JSON tokens (universal)
2. [ ] Icon usage in code:
   - Programmer references icons by name from `_design/icons/`
   - `system.yml` icons section specifies base set (Lucide) + custom icons
3. [ ] Spacing and color validation:
   - When Programmer generates UI code, validate against design system tokens
   - "You used `#e94560` directly — this is `accent` in your design system. Use the token instead."
4. [ ] Write tests

**Acceptance:** Design tokens can be exported as CSS vars and Tailwind config. Token usage violations detected.

---

### Task 8: Feature Image Pipeline (Publishing)

**Files:** `core/design/engine.py` (extend), publishing integration

**Steps:**
1. [ ] Implement `generate_feature_image()` for Ghost CMS dimensions:
   - Default: 1200x630 (OpenGraph standard)
   - Accept topic, mood, palette constraints
   - Generate abstract/semi-abstract composition via p5.js
2. [ ] Agent Swarms composition: `Scribe(Publish) → Designer(Generate) → Scribe(Publish)`
   - Scribe passes topic + domain to Designer
   - Designer generates feature image
   - Scribe attaches to publication draft
3. [ ] Feature image saved to `_design/feature-images/` with metadata
4. [ ] Optional PNG export for platforms that don't support SVG
5. [ ] Write tests

**Acceptance:** Publishing a draft to Ghost triggers feature image generation. Image uses project's design system palette.

---

### Task 9: Affinity Designer Export

**Files:** `core/design/system_manager.py` (extend)

**Steps:**
1. [ ] SVG export with Affinity Designer compatibility:
   - Clean SVG that Affinity can import without artifacts
   - Lucide Affinity template format when generating icons
   - Layers preserved for multi-element compositions
2. [ ] Export command: `manager.export_for_affinity(icon_name)` → Affinity-ready SVG
3. [ ] Documentation: which generation fidelity levels work best with Affinity import
4. [ ] Write tests

**Acceptance:** Generated icons import cleanly into Affinity Designer.

---

## Phase 3: Intelligence (1–2 weeks)

### Task 10: Design Consistency Checking

**Files:** `core/design/engine.py` (extend)

**Steps:**
1. [ ] Implement `check_consistency(asset, system)`:
   - Color validation: all colors in SVG exist in `system.yml` palette (or `currentColor`)
   - Stroke validation: stroke width, linecap, linejoin match system defaults
   - Size validation: viewBox matches system icon spec
   - Typography: font families in SVG match system typography
2. [ ] Batch check: validate all assets in `_design/` against `system.yml`
3. [ ] Suggested fixes: "Replace `#ff0000` with `accent` token (`#e94560`)"
4. [ ] Write tests

**Acceptance:** Batch check on `_design/` directory catches non-conformant assets with fix suggestions.

---

### Task 11: Generative Variation

**Files:** `core/design/engine.py` (extend)

**Steps:**
1. [ ] `generate_variations(asset, count=5)` — produce N variations of an asset within constraints
   - Same constraints, different seeds
   - User picks favorite or requests more
2. [ ] Theme-based variations: "Show me this icon in each theme style"
   - Iterate through theme presets, generate one per theme
3. [ ] Write tests

**Acceptance:** "Give me 5 pattern variations" returns 5 visually distinct but constraint-consistent SVGs.

---

### Task 12: Code Library Integration (Design Modules)

**Files:** `core/code_library/manager.py` (extend), `core/design/engine.py` (extend)

**Steps:**
1. [ ] Auto-register generated assets as library modules when pattern/component is reusable:
   - Design components → `_polly/library/components/`
   - Generator scripts → `_polly/library/workflows/`
   - Design system templates → `_polly/library/workflows/`
2. [ ] Generator script parameterization:
   - Extract p5.js sketches into reusable, parameterized scripts
   - "Use the Polly icon generator but change the glyph" = one parameter change
3. [ ] Design system as library template:
   - Save current `system.yml` as a library workflow module
   - New projects can instantiate from it
4. [ ] Write tests

**Acceptance:** A p5.js icon generator script is saved to the code library and can be applied in a new project.

---

### Task 13: Frontend — Design Studio

**Files:** `electron-app/src/renderer/` (new design components)

**Steps:**
1. [ ] Design panel accessible when Designer persona is active:
   - Asset gallery (grid of SVG thumbnails)
   - Generate panel (description input, constraint controls, theme preset selector)
   - Preview with iteration (generate → preview → regenerate/accept)
2. [ ] Design system viewer:
   - Color swatches from `system.yml`
   - Type specimens
   - Spacing scale visualization
   - Icon grid
3. [ ] Consistency dashboard:
   - List of design system conformance issues
   - Fix suggestions
4. [ ] Slash commands in chat: `/design icon`, `/design pattern`, `/design system`
5. [ ] Write frontend tests

**Acceptance:** Designer persona shows asset gallery. Generate an icon from chat, see SVG preview, save to `_design/`.

---

## Dependencies Summary

```
Phase 1 (Foundation)
  Task 1: Models & Format ──→ Task 3: p5.js Pipeline ──→ Task 5: REST API
  Task 2: Lucide Rules ────→ Task 3: p5.js Pipeline
  Task 4: Theme→Constraint ──→ Task 3 (enriches, doesn't block)

Phase 2 (Integration) — depends on Phase 1
  Task 6: Persona Enhancement (depends on Tasks 3, 5)
  Task 7: Programmer Handoff (depends on Task 1)
  Task 8: Feature Image Pipeline (depends on Tasks 3, 6)
  Task 9: Affinity Export (depends on Task 3)

Phase 3 (Intelligence) — depends on Phase 2
  Task 10: Consistency Checking (depends on Tasks 1, 6)
  Task 11: Generative Variation (depends on Task 3)
  Task 12: Code Library Integration (depends on Tasks 3, 6)
  Task 13: Frontend (depends on Tasks 5, 6)

External Dependencies:
  - Node.js (already in Electron app)
  - p5.js 1.6.0 + p5.js-svg (build dependency)
  - SVGO (build dependency)
  - Phase 17 (Monaco) — for full Designer persona UX, but p5.js pipeline works without it
  - Themes spec — active theme's designer.* properties
  - Code Library — for design module registration
  - Publishing pipeline (POSE) — for feature image integration
```

---

## Effort Estimate

| Phase | Effort | Can Parallel With |
|-------|--------|-------------------|
| Phase 1 | 2–3 weeks | Code Library Wave 1 |
| Phase 2 | 2–3 weeks | — |
| Phase 3 | 1–2 weeks | — |
| **Total** | **5–8 weeks** | |

Phase 1 can run in parallel with Code Library development since they share no file dependencies.
