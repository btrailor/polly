# Tasks: Aesthetic Theme Engine

Ordered implementation steps. Backend contract stable before frontend.

---

## Phase 1: Schema and Data (Backend)

### 1.1 Define theme JSON schema
- [ ] Create `core/themes/schema.py` with Pydantic models for PresentationLayer, BehaviorLayer, MetadataLayer, and Theme
- [ ] All properties optional at the individual level (supports partial themes for composition)
- [ ] Schema version field for migration support
- [ ] Validation: hex colors, float ranges (0.0–1.0), enum values for known properties

### 1.2 Create built-in theme JSON files
- [ ] Write seven theme JSON files matching spec definitions: `reas.json`, `fidenza.json`, `ghost-box.json`, `martens.json`, `jetset.json`, `riley.json`, `albers.json`
- [ ] Bundle in `core/themes/builtins/` for distribution
- [ ] First-run: copy builtins to `~/.polly/themes/` if not already present
- [ ] Each file is self-contained with full presentation, behavior, and metadata

### 1.3 Theme registry and loader
- [ ] Create `core/themes/registry.py` — scans `~/.polly/themes/`, maintains manifest
- [ ] Create `core/themes/loader.py` — loads theme JSON, resolves inheritance chain (hybrid base → overrides)
- [ ] Active theme tracked in registry; persisted to config
- [ ] Error handling: graceful fallback to Reas (default) if active theme file missing or invalid

---

## Phase 2: Persona Integration (Backend)

### 2.1 Persona behavior adapter
- [ ] Create `core/themes/persona_adapter.py`
- [ ] Extract behavior layer properties relevant to each persona type (designer, programmer, writer, systems)
- [ ] Generate structured theme context block for system prompt injection
- [ ] Context block format: natural language description of aesthetic orientation, not raw config

### 2.2 Integrate with persona system prompt
- [ ] Modify `core/personas/base.py` — add `apply_theme_behavior()` method
- [ ] Theme context injected after base prompt, before skills and user instructions
- [ ] Theme context is advisory ("your aesthetic orientation tends toward..."), not mandatory
- [ ] Test: verify theme context appears in system prompt when theme active, absent when no theme

### 2.3 Cross-domain ripple
- [ ] When theme is active, all personas receive relevant behavior properties (not just the matching persona)
- [ ] Ghost Box active → programmer gets `documentation: institutional`, writer gets `voice: hauntological-vague`
- [ ] Ripple is additive context, not overriding: persona-specific properties take priority, theme fills gaps

---

## Phase 3: API (Backend)

### 3.1 Theme API endpoints
- [ ] `GET /themes/list` — returns all themes with metadata (name, artist, core_principle, palette preview)
- [ ] `GET /themes/active` — returns fully resolved active theme
- [ ] `POST /themes/switch` — switch by theme name; validates exists; updates registry + config
- [ ] Add to `interfaces/server.py` following existing endpoint patterns
- [ ] WebSocket broadcast on theme switch (extend existing notification pattern)

### 3.2 Theme composition API
- [ ] `POST /themes/compose` — accepts source themes + property-level overrides, returns composed theme
- [ ] `POST /themes/save` — save composed theme to `~/.polly/themes/custom/` with provenance metadata
- [ ] Conflict detection: log when composed properties contradict (e.g., no-texture + heavy-texture)
- [ ] Inheritance: unspecified properties fall through to base theme (default: Reas)

### 3.3 Import/export
- [ ] `GET /themes/export/:name` — returns theme JSON for download
- [ ] `POST /themes/import` — accepts theme JSON, validates schema, saves to custom themes directory
- [ ] Schema version check on import; migration support for older schema versions

---

## Phase 4: Frontend — CSS Variable System

### 4.1 CSS custom property generation
- [ ] Create `electron-app/src/renderer/themes/theme-engine.js`
- [ ] Maps presentation layer properties to CSS custom properties (`--polly-bg`, `--polly-primary`, etc.)
- [ ] Applies properties to `:root` on theme switch
- [ ] Handles typography (font-family, tracking, weight), spacing (grid module, density), chrome (borders, radius)

### 4.2 Refactor existing CSS to use custom properties
- [ ] Audit current `styles/` for hardcoded color values, font stacks, spacing
- [ ] Replace with `var(--polly-*)` references
- [ ] Ensure default theme (Reas) produces visual output identical to current UI
- [ ] Test each theme applies correctly without breaking layout

### 4.3 Texture and motion system
- [ ] Texture overlays: CSS background-image or SVG overlays for grain, paper, woven patterns
- [ ] Motion system: CSS transitions and animations configurable per-theme
- [ ] Ghost Box: VHS flicker, aged paper overlay
- [ ] Martens: layered print-pass transitions
- [ ] Albers: weaving interlace motion
- [ ] Riley: modulation patterns via CSS animations

---

## Phase 5: Frontend — Settings UI

### 5.1 Theme browser
- [ ] Theme cards grid in Settings page (new section)
- [ ] Each card: theme name, artist name, core principle, palette color dots, thumbnail/preview
- [ ] Click card to preview (temporary apply), confirm button to switch
- [ ] Active theme highlighted

### 5.2 Theme composition interface
- [ ] Tab or section for composing hybrid themes
- [ ] Matrix view: themes × property categories (palette, typography, texture, spacing, motion, chrome, behavior)
- [ ] Drag property groups between themes
- [ ] Live preview panel showing composed result
- [ ] Save composed theme with name and description

### 5.3 Quick switcher
- [ ] Command palette integration (if command palette exists) for fast theme switching
- [ ] Keyboard shortcut for theme cycle
- [ ] Ribbon indicator showing active theme (subtle, not intrusive)

---

## Phase 6: Advanced Features

### 6.1 Conditional activation
- [ ] Time-of-day theme modulation (e.g., Riley during day, Ghost Box at night)
- [ ] Domain-triggered themes (active domain maps to theme)
- [ ] Project-type conditions (writing project → Ghost Box, code project → Reas)
- [ ] Condition evaluation in theme loader; user-configurable rules

### 6.2 Theme sequences
- [ ] Define ordered sequences of themes that rotate on schedule
- [ ] Daily rotation supports Lieberman-style daily practice orientation
- [ ] Sequence stored in user config; cron-like schedule

### 6.3 Agent swarm propagation
- [ ] Theme behavior layer included in Nexus execution context
- [ ] All agents in a workflow inherit theme defaults
- [ ] Agent-level theme override possible (e.g., specific agent uses different aesthetic)

---

## Completion Criteria

- [ ] Seven themes load and render correctly
- [ ] Theme switch changes both UI and persona behavior
- [ ] Hybrid themes compose and persist
- [ ] Cross-domain ripple verified (theme affects all active personas)
- [ ] Settings UI allows browsing, previewing, switching, and composing
- [ ] Default (Reas) theme is visually identical to current UI on first install
- [ ] Theme switch is non-destructive (previous conversation outputs unchanged)
