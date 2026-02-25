# Design: CSS Architecture Cleanup

## Architecture Impact

No new subsystems. Refactoring of existing CSS with new conventions.

### 1. z-index Token System

Define a clear z-index scale in `main.css` `:root`:

```css
:root {
  /* z-index layers — use these tokens, never raw numbers */
  --z-base: 0;
  --z-dropdown: 100;        /* autocomplete, context menus, select dropdowns */
  --z-sticky: 200;          /* sticky headers, pinned elements */
  --z-overlay: 300;         /* modal backdrops, drawer overlays */
  --z-modal: 400;           /* modal dialogs, confirm dialogs */
  --z-toast: 500;           /* toast notifications (above modals) */
  --z-tooltip: 600;         /* tooltips (above everything) */
  --z-titlebar: 700;        /* Electron titlebar (always on top) */
}
```

**Migration map:**

| Current | Element | New Token |
|---------|---------|-----------|
| `100` | Status bar, slash-command autocomplete | `var(--z-dropdown)` |
| `300` | Persona-switch dialog | `var(--z-modal)` |
| `999` | Various overlays | `var(--z-overlay)` |
| `1000-1003` | Titlebar | `var(--z-titlebar)` |
| `9999` | Some dialogs | `var(--z-modal)` |
| `10000` | Modals | `var(--z-modal)` |
| `10001` | Toast over modal | `var(--z-toast)` |

### 2. Border Radius Variables

Update the CSS variables to reflect actual usage (abandon the `0px` brutalist values that are universally ignored):

```css
:root {
  --radius-xs: 2px;     /* subtle rounding on small elements */
  --radius-sm: 4px;     /* buttons, inputs, tags */
  --radius-md: 6px;     /* cards, panels, modals */
  --radius-lg: 8px;     /* larger cards, dialog panels */
  --radius-xl: 12px;    /* feature cards, overlays */
  --radius-full: 9999px; /* pills, avatars, toggles */
}
```

Then replace all hardcoded `border-radius` values with the appropriate variable. Use `grep` to find all `border-radius:` declarations and map each to a token.

### 3. Color Variable Audit

**Step 1: Inventory all hardcoded hex/rgb values in CSS.**

Run `grep -oP '#[0-9a-fA-F]{3,8}' styles/*.css | sort | uniq -c | sort -rn` to find the most-used hardcoded colors.

**Step 2: Map to existing or new CSS variables.**

Expected mappings:
- `#e0e0e0` → `var(--text-primary)`
- `#808080` → `var(--text-secondary)`
- `#606060` → `var(--text-muted)` (after contrast fix)
- `#1e1e1e` → `var(--bg-primary)`
- `#252525` or `#2a2a2a` → `var(--bg-secondary)`
- `#333333` or `#363636` → `var(--bg-tertiary)`
- `#f0903b` → `var(--accent-primary)`
- `#e53935` or similar red → `var(--accent-red)` (define if missing)
- `#4caf50` or similar green → `var(--accent-green)` (define if missing)

**Step 3: Replace all hardcoded values with variables.**

### 4. Variable Naming Fixes

| Current | Issue | Fix |
|---------|-------|-----|
| `--accent-purple: #f0903b` | Orange, not purple | Rename to `--accent-primary` or remove (it's a duplicate) |
| `--signal` / `--signals` | Inconsistent pluralization | Standardize on one form, alias the other for backward compatibility, then deprecate |

### 5. Duplicate Definition Deduplication

The `.loading-spinner` is defined identically at 4 locations in `main.css`. Consolidate into a single definition in the "Components" section of the stylesheet.

Audit process:
1. Search for class names defined more than once
2. Verify they're identical (not intentional overrides)
3. Consolidate to first/most logical occurrence
4. Remove duplicates

### 6. !important Reduction Strategy

For each `!important` usage:
1. Determine why it was added (likely specificity conflict)
2. Fix the specificity conflict by restructuring selectors (increase specificity of the winning rule, or reduce specificity of the competing rule)
3. Remove `!important`

Common causes in this codebase:
- Ribbon styles fighting with view-level styles
- Sidebar styles fighting with general button/link styles
- Dynamic class toggles needing to override base styles

## Files Affected

| File | Changes |
|------|---------|
| `styles/main.css` | z-index tokens, border-radius variables, color variable audit, dedup `.loading-spinner`, reduce `!important`, fix variable names |
| `styles/notes.css` | Replace hardcoded colors/radius with variables |
| `styles/persona-ui.css` | Replace hardcoded colors/radius with variables |
| `styles/curriculum.css` | Replace hardcoded colors/radius with variables |
| `styles/persona-switch-dialog.css` | Replace z-index with tokens, hardcoded values with variables |
| `styles/template-gallery.css` | Replace hardcoded values with variables |
| `styles/glitch-effects.css` | Replace any hardcoded colors |
| `components/mental-models-editor.css` | Replace hardcoded values with variables |
| JS files that use inline styles | Replace inline `style=` color/size values with CSS class references where possible |
