# CSS Architecture Cleanup

**Date:** February 2026
**Scope:** Frontend
**Priority:** P2 — maintainability; eliminates visual inconsistencies and reduces technical debt

---

## What We're Doing

Auditing and restructuring the CSS architecture across all 7+ stylesheets to establish consistency in z-index layering, CSS variable usage, border-radius, color references, and duplicate definitions. The CSS has grown organically across 23+ development phases and accumulated significant inconsistencies.

## Why

### z-index Chaos
Values range from 0 to 10001 with no token system:
- Modals: `10000`
- Persona-switch dialog: `300`
- Titlebar: `1000-1003`
- Status bar: `100`
- Slash-command autocomplete: `100`
- Various overlays: `999`, `9999`, `10001`

Without a defined layering system, any new component requires guessing a z-index value and hoping it doesn't conflict with existing layers.

### Border Radius Ignored
CSS variables `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl` are all defined as `0px` (brutalist aesthetic), but actual code hardcodes `border-radius: 4px`, `6px`, `8px`, `12px` throughout — completely ignoring the variables.

### Color Hardcoding
Some selectors use `var(--text-primary)` while others hardcode the same value as `#e0e0e0` or `#808080`. This makes theme switching impossible and creates a maintenance burden.

### Duplicate Definitions
`.loading-spinner` is defined 4 times in `main.css` at lines 3703, 4601, 5390, and 6892 — identical definitions repeated in different sections.

### Naming Confusion
- `--accent-purple` is set to `#f0903b` (orange, not purple)
- `--signal` aliases `--signals` (inconsistent pluralization)

### !important Overuse
Ribbon and sidebar styles use dozens of `!important` declarations, indicating specificity wars rather than clean cascade.

## Scope

- **In scope:** (1) Define z-index token system. (2) Fix border-radius variables and usage. (3) Replace hardcoded colors with variables. (4) Deduplicate repeated definitions. (5) Fix misleading variable names. (6) Audit and reduce `!important` usage.
- **Out of scope:** Full CSS rewrite. Migration to CSS modules or CSS-in-JS. Responsive design overhaul (separate concern). Theme engine (separate change: `aesthetic-theme-engine`).

## Backend vs Frontend

Frontend-only. All changes in `electron-app/src/renderer/styles/`.
