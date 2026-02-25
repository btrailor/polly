# Tasks: Skeleton Loading States

---

## Phase 1: Skeleton CSS Primitives

### 1.1 Create skeleton stylesheet

- [ ] Create `electron-app/src/renderer/styles/skeleton.css`
- [ ] Implement `.skeleton` base class with shimmer animation
- [ ] Implement primitives: `.skeleton-text` (with width variants), `.skeleton-heading`, `.skeleton-avatar`, `.skeleton-card`, `.skeleton-stat`, `.skeleton-list-item`
- [ ] Add `prefers-reduced-motion` support (disable shimmer, use static opacity)
- [ ] Add fade-in animation for skeleton views
- [ ] Register in `index.html`

---

## Phase 2: SkeletonLoader Component

### 2.1 Create SkeletonLoader with view templates

- [ ] Create `electron-app/src/renderer/components/skeleton-loader.js`
- [ ] Implement templates for: `dashboard`, `conversations`, `notes`, `patterns`, `settings`, `knowledge`, `graph`
- [ ] Each template matches the approximate layout of its real view (same number of cards, list items, stat blocks)
- [ ] Include `role="status"` and `aria-label` for accessibility
- [ ] Expose as `window.SkeletonLoader`
- [ ] Register in `index.html`

---

## Phase 3: View Transition Integration

### 3.1 Replace loading text in showView()

- [ ] In `app.js:showView()` (`~line 3037`), find all "Loading..." string assignments to sidebar/content areas
- [ ] Replace with `SkeletonLoader.forView(viewName)` calls
- [ ] Views to update: dashboard, notes, patterns, curricula, settings, knowledge, domains, learning, graph

### 3.2 Replace loading text in conversation list

- [ ] When conversation list is loading/re-rendering, show conversation skeleton (6 list items)
- [ ] Replace when data arrives

### 3.3 Replace loading text in notes manager

- [ ] In `notes-manager.js`, replace "Loading notes..." with skeleton
- [ ] Show note list skeleton while fetching, replace with actual list

---

## Phase 4: Polish

### 4.1 Skeleton-to-content transition

- [ ] Add subtle fade transition when real content replaces skeleton
- [ ] Content should fade in over 150-200ms
- [ ] Skeleton should not "flash" if content loads very fast (<100ms) — add minimum display time or use requestAnimationFrame to batch the swap

### 4.2 Loading spinner coexistence

- [ ] Audit remaining uses of `.loading-spinner` — skeleton is for view/list loading, spinner is for individual operations (save, submit, etc.)
- [ ] Ensure both coexist: skeletons for page-level loading, spinners for action-level loading
- [ ] Deduplicate the 4 `.loading-spinner` definitions in `main.css` into one (CSS architecture overlap)

---

## Completion Criteria

- [ ] Skeleton CSS primitives exist and animate smoothly
- [ ] Every view transition shows a skeleton matching the view's layout structure
- [ ] No "Loading..." text strings remain for view transitions
- [ ] Skeletons respect `prefers-reduced-motion` (static opacity, no shimmer)
- [ ] Skeletons have `role="status"` and `aria-label` for screen readers
- [ ] Content replacement is smooth (no jarring flash or layout shift)
- [ ] Skeleton loads instantly (no dependencies on data or API calls)
