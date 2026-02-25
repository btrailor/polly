# Tasks: CSS Architecture Cleanup

Ordered so each phase is independently shippable — later phases don't break things if paused.

---

## Phase 1: z-index Token System

### 1.1 Define z-index tokens

- [ ] Add z-index CSS custom properties to `:root` in `main.css`: `--z-base`, `--z-dropdown`, `--z-sticky`, `--z-overlay`, `--z-modal`, `--z-toast`, `--z-tooltip`, `--z-titlebar`
- [ ] Document the layer ordering in a CSS comment block

### 1.2 Migrate z-index values

- [ ] Run `grep -rn "z-index" styles/` to get all 30+ instances
- [ ] Replace each raw number with the appropriate `var(--z-*)` token
- [ ] Replace z-index values in JS-created inline styles (search `app.js` for `zIndex` or `z-index`)
- [ ] Test: verify modals appear above content, toasts above modals, titlebar above everything

---

## Phase 2: Border Radius Variables

### 2.1 Update variable definitions

- [ ] Change `--radius-sm/md/lg/xl` from `0px` to actual values used in the codebase (`4px`, `6px`, `8px`, `12px`)
- [ ] Add `--radius-xs: 2px` and `--radius-full: 9999px`

### 2.2 Replace hardcoded border-radius values

- [ ] Run `grep -rn "border-radius" styles/` to find all declarations
- [ ] Map each hardcoded value to the closest token
- [ ] Replace with `var(--radius-*)` references
- [ ] Test: spot-check that buttons, cards, modals, inputs still look correct

---

## Phase 3: Color Variable Consolidation

### 3.1 Inventory hardcoded colors

- [ ] Extract all unique hex/rgb color values used across all CSS files
- [ ] Group by similarity (same color used with different hex casing, etc.)
- [ ] Map each to an existing or new CSS custom property

### 3.2 Define missing color variables

- [ ] Add `--accent-red` if not defined (for destructive actions, errors)
- [ ] Add `--accent-green` if not defined (for success states)
- [ ] Add `--accent-yellow` if not defined (for warnings)
- [ ] Add `--bg-hover` for hover state backgrounds if commonly hardcoded

### 3.3 Replace hardcoded colors

- [ ] Systematically replace all hardcoded hex values with `var()` references across all 7+ CSS files
- [ ] Prioritize `main.css` first (largest file, most hardcoded values)
- [ ] Then `notes.css`, `persona-ui.css`, `curriculum.css`, etc.
- [ ] Verify no visual changes after each file's migration

---

## Phase 4: Naming and Deduplication

### 4.1 Fix misleading variable names

- [ ] Rename `--accent-purple` to `--accent-primary` or remove it (it's `#f0903b`, same as the main accent)
- [ ] Standardize `--signal` vs `--signals` — pick one, alias the other, add deprecation comment
- [ ] Search for any other misleading variable names

### 4.2 Deduplicate .loading-spinner

- [ ] Identify all 4 locations of `.loading-spinner` in `main.css`
- [ ] Keep the first occurrence (or move to a dedicated "Components" section)
- [ ] Remove the other 3 duplicates
- [ ] Verify spinner still works in all contexts (dashboard, patterns, settings, chat)

### 4.3 Audit for other duplicates

- [ ] Search for class names defined more than once across CSS files
- [ ] Consolidate any identical duplicates
- [ ] For intentional overrides, add comments explaining why

---

## Phase 5: !important Reduction

### 5.1 Audit !important usage

- [ ] Run `grep -c "!important" styles/*.css` to count per file
- [ ] Categorize each usage: necessary (override inline style from JS) vs unnecessary (specificity war)

### 5.2 Fix specificity conflicts

- [ ] For unnecessary `!important`: restructure selectors to win naturally
- [ ] Common fix: increase specificity of the intended rule (e.g., `.ribbon .btn` instead of `.btn!important`)
- [ ] Remove `!important` after fixing the cascade
- [ ] Target: reduce `!important` count by 50%+

---

## Completion Criteria

- [ ] z-index uses named tokens exclusively (no raw numbers in CSS)
- [ ] Border-radius uses `var(--radius-*)` tokens exclusively
- [ ] Zero hardcoded hex color values in CSS (all use `var()` references)
- [ ] `--accent-purple` renamed or removed
- [ ] `.loading-spinner` defined exactly once
- [ ] `!important` count reduced by 50%+ from current baseline
- [ ] No visual regressions — app looks identical before and after
- [ ] All z-index tokens documented in a comment block
