# Design Review Results: Polly Electron App (All Views)

**Review Date**: 2026-02-25  
**Route**: All views (Dashboard, Chat, Notes, Settings, Knowledge, Patterns, Setup, Modals)  
**Focus Areas**: Visual Design, UX/Usability, Responsive/Mobile, Accessibility, Micro-interactions/Motion, Consistency, Performance  

> **Note**: This review was conducted through static code analysis only. Visual inspection via browser would provide additional insights into layout rendering, interactive behaviors, and actual appearance.

---

## Summary

Polly has a strong, intentional retro/terminal aesthetic with a well-structured CSS token system and good foundational accessibility features (skip links, ARIA labels, focus-visible states). However, the codebase has grown organically and shows signs of technical debt: a 9,000-line CSS monolith, conflicting CSS variable names across files, duplicated HTML element IDs, and a settings page with both new and legacy markup coexisting. The biggest opportunities are in navigation discoverability, design system consistency, and eliminating dead/duplicate code.

---

## Issues

| # | Issue | Criticality | Category | Location |
|---|-------|-------------|----------|----------|
| 1 | `marked.js` included twice — once in `<head>` and again at bottom of `<body>`, causing a duplicate script load | 🔴 Critical | Performance | `electron-app/src/renderer/index.html:22` and `index.html:3571` |
| 2 | Duplicate element IDs: `id="settings-code-paths"` appears in both the new section layout and the legacy `tab-general` block | 🔴 Critical | Consistency | `index.html:583` and `index.html:1075` |
| 3 | Duplicate element IDs: `id="settings-routing-mode"` appears in the new section and the legacy `tab-general` block | 🔴 Critical | Consistency | `index.html:600` and `index.html:1091` |
| 4 | `--accent-color` (used in `persona-ui.css`) is never defined in `:root`, so it silently falls back to hardcoded `#4a9eff` (blue), creating a completely different accent colour from the app's orange `--accent-primary` | 🔴 Critical | Consistency | `electron-app/src/renderer/styles/persona-ui.css:153` |
| 5 | `notes.css` references undefined CSS variables: `--accent`, `--hover-bg`, `--border-primary`, `--text-normal`, `--text-tertiary`, `--accent-subtle` — none are defined in `:root` | 🔴 Critical | Consistency | `electron-app/src/renderer/styles/notes.css:35,87,191,207,277,505` |
| 6 | Domain cards (`.domain-card`) are plain `<div>` elements with `cursor: pointer` but no `role="button"`, `tabindex="0"`, or keyboard event handlers — not keyboard-accessible | 🟠 High | Accessibility | `index.html:408-429` |
| 7 | Toggle switch inputs (`.toggle-switch`) hide the underlying `<input type="checkbox">` visually but provide no visible focus indicator for keyboard users on the label/toggle track | 🟠 High | Accessibility | `main.css` (toggle-switch section); `index.html:611-615` |
| 8 | `--text-muted` (`#8a8a8a`) on `--bg-secondary` (`#252525`) yields ~3.8:1 contrast ratio — fails WCAG AA (4.5:1) for normal-weight body text | 🟠 High | Accessibility | `main.css:17` (`:root` block) |
| 9 | Settings page contains BOTH a modern section-based layout AND 6+ legacy `settings-tab-content` blocks (marked "will be migrated") — dead HTML is served on every load | 🟠 High | Performance | `index.html:1069-1284` |
| 10 | Ribbon navigation has 13 icon-only items with no text labels — discoverability is extremely low; users must hover each to find what they do | 🟠 High | UX/Usability | `index.html:104-158` |
| 11 | Left sidebar duplicates the same navigation as the ribbon (dashboard, knowledge, patterns, settings) — redundant UI element that wastes horizontal space | 🟠 High | UX/Usability | `index.html:164-196` |
| 12 | Save buttons in Settings use entirely inline styles (`style="background: #2d5a27; color: #c8e6c9; ..."`), bypassing the design system and creating a visually inconsistent green button | 🟠 High | Consistency | `index.html:930-933`, `index.html:1061-1064` |
| 13 | `Courier New` monospace is the body font for ALL text including settings descriptions, long prose, and labels — significantly reduces readability for non-code content | 🟡 Medium | Visual Design | `main.css:183-184` |
| 14 | `main.css` is 8,992 lines and mixes dashboard, chat, notes, settings, graph, and modal styles in a single file — makes specificity conflicts and maintenance very difficult | 🟡 Medium | Performance | `electron-app/src/renderer/styles/main.css` |
| 15 | Overuse of `!important` — the ribbon and layout sections use `!important` on nearly every property, suggesting layout issues were patched rather than fixed at the root | 🟡 Medium | Consistency | `main.css:334-465` (ribbon), `main.css:540-558` (left sidebar) |
| 16 | Dashboard stat cards show `"-"` while loading instead of using the existing `skeleton-loader.js` component that's already included | 🟡 Medium | Micro-interactions | `index.html:328-344`; `electron-app/src/renderer/components/skeleton-loader.js` |
| 17 | View switching (ribbon click) hides/shows views using `display: none` with no transition — jarring UX when navigating between views | 🟡 Medium | Micro-interactions | `main.css:1721-1723` (`.view.hidden { display: none }`) |
| 18 | Border radius values are hardcoded (`8px`, `6px`, `12px`, `50%`) throughout, bypassing the defined `--radius-*` token scale | 🟡 Medium | Consistency | `main.css:2556`, `2560`, `2686`, many others |
| 19 | Font size values are hardcoded throughout with no typography scale tokens — sizes range from `9px` to `36px` with no consistent type scale | 🟡 Medium | Visual Design | `main.css` throughout |
| 20 | Dashboard heading uses terminal prefix: `<h2>> dashboard</h2>` — inconsistent heading style; the `>` prefix is pure decoration that screen readers will announce | 🟡 Medium | Accessibility | `index.html:322` |
| 21 | `main-content-area` has `min-width: 400px` — prevents the app from working in narrow panel/split-screen scenarios | 🟡 Medium | Responsive | `main.css:594` |
| 22 | Only one responsive breakpoint exists in `notes.css` (`900px`) and none in `main.css` for the core three-column layout | 🟡 Medium | Responsive | `main.css` (entire file); `notes.css:1277-1297` |
| 23 | Glitch animation on `.ribbon-logo.glitch:hover` and `.ribbon-item.active.glitch` runs continuously — can be visually fatiguing during long sessions | ⚪ Low | Micro-interactions | `glitch-effects.css:139-150`, `216-221` |
| 24 | `aria-current="page"` is hardcoded to the dashboard ribbon button in HTML and is never dynamically updated when switching views | ⚪ Low | Accessibility | `index.html:111` |
| 25 | `context-picker-menu` uses raw `z-index: 400` instead of `var(--z-modal)` token | ⚪ Low | Consistency | `main.css:936` |
| 26 | The ASCII art in the setup view (`":>  polly  -&"`) uses a raw `&` character instead of `&amp;` — invalid HTML that may render incorrectly | ⚪ Low | Consistency | `index.html:208-210` |
| 27 | No `contain: layout` or CSS containment on large scrollable panels — missed rendering optimization opportunity | ⚪ Low | Performance | `main.css` (`.left-sidebar`, `.chat-messages-panel`, `.agents-list`) |
| 28 | `skeleton.css` is imported but skeleton loading is not wired up to the dashboard stats grid, autonomy ring, or patterns list | ⚪ Low | Micro-interactions | `index.html:20`; view-dashboard stats grid |

---

## Criticality Legend
- 🔴 **Critical**: Breaks functionality or violates accessibility standards
- 🟠 **High**: Significantly impacts user experience or design quality
- 🟡 **Medium**: Noticeable issue that should be addressed
- ⚪ **Low**: Nice-to-have improvement

---

## Next Steps

**Immediate (Critical fixes — low effort, high impact):**
1. Remove the duplicate `marked.js` script tag from the bottom of `<body>` (`index.html:3571`)
2. Deduplicate IDs `settings-code-paths` and `settings-routing-mode` — remove or rename the legacy tab versions
3. Add `--accent-color: var(--accent-primary)` alias to `:root` in `main.css` to fix the blue accent bleed in persona-ui
4. Define the missing `notes.css` variables (`--accent`, `--hover-bg`, `--border-primary`, etc.) in `:root` or update notes.css to use the correct tokens

**Short-term (High priority):**
5. Add `role="button" tabindex="0"` and `keydown` handlers (Enter/Space) to all clickable `<div>` elements (domain cards, etc.)
6. Add a visible focus indicator to toggle switches (box-shadow on the track element when associated input is `:focus-visible`)
7. Lighten `--text-muted` from `#8a8a8a` to at least `#9e9e9e` on `#252525` background to achieve 4.5:1 contrast
8. Remove the legacy settings tab blocks (`tab-general`, `tab-routing`, `tab-api-keys`, etc.) once the new section layout is complete
9. Consider adding a minimum of 2-3 text labels to the most-used ribbon icons (or show labels on hover via tooltip)

**Medium-term (Design system health):**
10. Introduce a sans-serif font (e.g., `Inter`, `system-ui`) for prose/description text; keep monospace only for code and terminal-aesthetic headers
11. Split `main.css` into logical modules: `layout.css`, `chat.css`, `dashboard.css`, `settings.css`, `components.css`
12. Audit and remove `!important` from layout rules — fix the root cause of layout conflicts instead
13. Wire `skeleton-loader.js` to dashboard stats, autonomy ring, and patterns list for a polished loading experience
14. Add a CSS `transition: opacity 0.15s ease` (with `pointer-events: none` on hidden) to view switching to replace the jarring `display: none`
