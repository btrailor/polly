# UI (OpenSpec)

Source of truth for Polly's user interface: design system, layout, and pages. Detailed specs: [docs/planning/phases/phase-0.5/](../../../docs/planning/phases/phase-0.5/).

## Design System

- **Aesthetic:** Obsidian-inspired clean layout with subtle retro-brutalist accents. Professional first, dark-mode native. Switchable via artist-derived Aesthetic Theme Engine — see [themes spec](../themes/spec.md).
- **Layout:** Three-column (ribbon, sidebar, main content, optional right panel). Page-based navigation; dedicated chat per page.
- **Ribbon:** Home, Chat, Notes, Patterns, Mental Models, Learning, Settings. Context-sensitive left sidebar per page.
- **Theme system:** All visual properties (palette, typography, texture, spacing, motion, chrome) driven by CSS custom properties (`--polly-*`). Theme switching regenerates custom properties at `:root` for real-time UI transformation. Default theme (Reas) produces visual output identical to current UI. See [themes spec](../themes/spec.md).

## Pages

### Current

- **Home** — Dashboard / entry.
- **Chat** — Per-page conversations; floating chat bar; context-aware persona switching.
- **Notes** — Native notes browser, file tree, editor, TOC, templates (see [notes](../notes/spec.md)).
- **Patterns** — Pattern learning UI, compression stats.
- **Mental Models** — Settings and override UI for mental models.
- **Learning** — Four center-area states: Active Session (full-width Professor conversation), Curriculum View (navigable learning map), Practice Space (embedded workspace), Review (analytics). Analytics in collapsible Review tab, not center stage. See [curriculum](../curriculum/spec.md), [teaching](../teaching/spec.md).
- **Settings** — API keys, domains, routing, mental models, integrations, security.

### Planned

- **Canvas** — BAD Canvas project planning with zone editor, focus mode, gap view. See [canvas spec](../canvas/spec.md).
- **Analytics** — Knowledge patterns, quality metrics, domain distribution, capture frequency, reflective features. See [analytics spec](../analytics/spec.md).
- **Swarms** — Workflow template browser, swarm execution view, agent configuration. See [agent-swarms spec](../agent-swarms/spec.md).
- **Knowledge Graph** — Interactive Cytoscape.js visualization, reasoning transparency, "Explore From Here" mode. See [knowledge-graph spec](../knowledge-graph/spec.md).
- **Code Architecture** (Phase 25) — Visual dependency tree, impact analysis, auto-generated architecture docs. See [docs/planning/phases/other/PHASE25_CODE_ARCHITECTURE_SYSTEM.md](../../../docs/planning/phases/other/PHASE25_CODE_ARCHITECTURE_SYSTEM.md).
- **Project Management** (Phase 26) — Visual roadmaps, OmniFocus-style tasks, dynamic todos, dependency visualization. See [docs/planning/phases/other/PHASE26_PROJECT_MANAGEMENT.md](../../../docs/planning/phases/other/PHASE26_PROJECT_MANAGEMENT.md).
- **Browser** (Phase 29) — Embedded browser + DevTools, AI-powered web analysis, live preview. See [docs/planning/phases/other/PHASE29_BUILT_IN_BROWSER.md](../../../docs/planning/phases/other/PHASE29_BUILT_IN_BROWSER.md).
- **Communication** (Phase 20) — Superhuman-informed triage view (sequential flow-based email processing), distraction-free compose, calendar intelligence with available slots, remind panel with follow-ups, autonomy dashboard. Slash commands (`/mail triage`, `/mail compose`, etc.). See [communication spec](../communication/spec.md).

### Aesthetic Theme Engine (Planned)

The theme system adds the following UI components:

- **Theme browser** (Settings page): Card grid showing available themes — name, artist, core principle, palette preview. Click to preview, confirm to switch. Active theme highlighted.
- **Theme composition matrix** (Settings page): Matrix of themes × property categories. Drag property groups between themes to compose hybrids. Live preview panel. Save composed themes with provenance.
- **Quick switcher**: Command palette integration and/or ribbon indicator for fast theme switching.
- **CSS custom property layer**: All UI components reference `--polly-*` custom properties instead of hardcoded values. Theme switch regenerates properties at `:root`.
- **Texture overlays**: Per-theme background textures (grain, paper, woven patterns) via CSS background-image or SVG overlays.
- **Motion system**: Per-theme CSS transitions and animations (generative for Reas, flowing for Fidenza, flicker for Ghost Box, weaving for Albers, optical for Riley, none for Jetset).
- **Persona indicators**: Theme-aware persona badges (e.g., Ghost Box stamps, Martens overprint marks).

See [themes spec](../themes/spec.md) for full seven-theme definitions and composability system.

### Planned UI Enhancements

#### Augmented Writing Panel

Right panel in Notes view showing related notes during composition. Entity-based matching in real-time. See [knowledge-graph spec](../knowledge-graph/spec.md).

#### Maturity Indicators

Visual maturity stage (30-Ideas / 20-Active / 10-Archive) on notes, captures, and canvases. Stage transition via drag-and-drop or context menu. See [capture spec](../capture/spec.md).

#### Review Workflow Views

Triage, daily, weekly, domain-specific, and cross-domain review modes as filtered views in the UI. See [capture spec](../capture/spec.md).

#### Visualization Features

- Domain distribution chart (pie/bar)
- Maturity stage flow diagram (Sankey)
- Capture frequency heatmap (calendar)
- Cross-domain connection graph
- Project progress indicators

#### Connection Metrics in Notes

Display inbound/outbound connection counts on notes. Hub/isolated/bridge indicators. See [knowledge-graph spec](../knowledge-graph/spec.md).

#### Agent Swarms UI

- **Swarm Execution View:** Live streaming of agent outputs, progress indicators per agent in workflow, intervention points (pause, redirect, take over), cost/time tracking.
- **Template Browser:** Domain-suggested templates, usage stats, ratings. Fork and modify templates.
- **Agent Configuration (Level 3):** Structured form for defining custom agents — capabilities, schemas, execution contexts, constraints, domain affinity.
- **Progressive disclosure:** Level 1 (one-click templates) through Level 4 (code-level Nexus API). Most users stay at Level 1–2.
- See [agent-swarms spec](../agent-swarms/spec.md).

## Implementation

- `electron-app/src/renderer/`: `app.js`, `index.html`, component modules, `styles/`. Lucide icons; marked for markdown.

## Reference

- [PHASE0.5_OBSIDIAN_INSPIRED_UI.md](../../../docs/planning/phases/phase-0.5/PHASE0.5_OBSIDIAN_INSPIRED_UI.md) — Vision and design system
- [PHASE0.5_UI_DESIGN_SYSTEM.md](../../../docs/planning/phases/phase-0.5/PHASE0.5_UI_DESIGN_SYSTEM.md) — Component and layout detail
