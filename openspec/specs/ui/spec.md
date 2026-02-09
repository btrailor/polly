# UI (OpenSpec)

Source of truth for Polly's user interface: design system, layout, and pages. Detailed specs: [docs/planning/phases/phase-0.5/](../../../docs/planning/phases/phase-0.5/).

## Design System

- **Aesthetic:** Obsidian-inspired clean layout with subtle retro-brutalist accents. Professional first, dark-mode native.
- **Layout:** Three-column (ribbon, sidebar, main content, optional right panel). Page-based navigation; dedicated chat per page.
- **Ribbon:** Home, Chat, Notes, Patterns, Mental Models, Learning, Settings. Context-sensitive left sidebar per page.

## Pages

- **Home** — Dashboard / entry.
- **Chat** — Per-page conversations; floating chat bar; context-aware persona switching.
- **Notes** — Native notes browser, file tree, editor, TOC, templates (see [notes](notes/spec.md)).
- **Patterns** — Pattern learning UI, compression stats.
- **Mental Models** — Settings and override UI for mental models.
- **Learning** — Curriculum browser, progress, teaching mode (see [curriculum](../curriculum/spec.md), [teaching](../teaching/spec.md)).
- **Settings** — API keys, domains, routing, mental models, integrations, security.

## Implementation

- `electron-app/src/renderer/`: `app.js`, `index.html`, component modules, `styles/`. Lucide icons; marked for markdown.

## Reference

- [PHASE0.5_OBSIDIAN_INSPIRED_UI.md](../../../docs/planning/phases/phase-0.5/PHASE0.5_OBSIDIAN_INSPIRED_UI.md) — Vision and design system
- [PHASE0.5_UI_DESIGN_SYSTEM.md](../../../docs/planning/phases/phase-0.5/PHASE0.5_UI_DESIGN_SYSTEM.md) — Component and layout detail
