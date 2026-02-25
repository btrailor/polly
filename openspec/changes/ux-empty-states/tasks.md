# Tasks: Empty States with Calls-to-Action

---

## Phase 1: EmptyState Component

### 1.1 Create EmptyState component

- [ ] Create `electron-app/src/renderer/components/empty-state.js`
- [ ] Implement `EmptyState.render(options)` returning a DOM element
- [ ] Support: `icon`, `title`, `description`, `actionLabel`, `onAction`, `secondaryLabel`, `onSecondary`, `size`
- [ ] Trigger Lucide icon rendering within the component
- [ ] Expose as `window.EmptyState`

### 1.2 Create EmptyState styles

- [ ] Create `electron-app/src/renderer/components/empty-state.css`
- [ ] Three size variants: `small` (sidebar contexts), `medium` (default), `large` (full-page views)
- [ ] Use CSS variables for theming consistency
- [ ] Centered flex layout, muted icon, clear hierarchy
- [ ] Register in `index.html`

---

## Phase 2: Core Views (High-Traffic)

### 2.1 Conversation list empty states

- [ ] No conversations: replace existing text with `EmptyState.render()` including "New Chat" button
- [ ] Search no results: add NEW empty state for when search query matches nothing — currently renders blank
- [ ] Page filter empty: replace "No conversations on this page yet" with EmptyState

### 2.2 Dashboard empty state

- [ ] When no data is indexed, show EmptyState with guidance to visit Knowledge Base
- [ ] Check: does dashboard currently handle zero-data gracefully? If it just shows "0" values, overlay or replace the stats section

### 2.3 Notes empty states

- [ ] No notes: show EmptyState with "New Note" action
- [ ] Search/filter no results: show EmptyState with "Clear Filters" action
- [ ] Replace all text-only "No notes found" in `notes-manager.js`

---

## Phase 3: Secondary Views

### 3.1 Patterns empty state

- [ ] Replace "No patterns learned yet" with EmptyState (no action — passive learning)
- [ ] Include description explaining how patterns are learned

### 3.2 Curricula empty state

- [ ] Replace text with EmptyState including action to start a curriculum via `/curriculum`
- [ ] Action focuses chat input and pre-fills `/curriculum`

### 3.3 Knowledge base empty state

- [ ] Show EmptyState with "Add Source" action when no sources are indexed
- [ ] Include description of what can be indexed (Obsidian vault, code directories)

### 3.4 Graph empty state

- [ ] Show EmptyState when no entities exist in the graph
- [ ] Action: navigate to chat view

### 3.5 Learning tracker empty state

- [ ] Show EmptyState when no topics are tracked
- [ ] Include guidance about Professor persona

---

## Phase 4: Settings and Configuration

### 4.1 API keys empty state

- [ ] Replace "No API keys configured" in `api-keys-manager.js` with EmptyState
- [ ] Action: "Add API Key" opens the add key modal

### 4.2 Mental models empty state

- [ ] Show EmptyState when no custom models exist (distinct from the default models list)
- [ ] Action: "Create Model" opens the mental model editor

### 4.3 Domains empty state

- [ ] Show EmptyState when no custom domains exist
- [ ] Action: "Create Domain" opens the domain form

### 4.4 Replace "Coming soon" placeholders

- [ ] Replace all inline-styled "Coming soon" text in settings sidebar (`app.js:3506-3517`)
- [ ] Use `EmptyState.render({ icon: 'clock', title: 'Coming soon', description: '{Feature} is planned for a future release.', size: 'small' })`
- [ ] Remove inline `style=` attributes

---

## Completion Criteria

- [ ] EmptyState component exists and is reusable across the app
- [ ] Every view that can be empty shows a themed EmptyState with icon, title, and description
- [ ] Search/filter no-results shows appropriate feedback (not a blank void)
- [ ] Primary action buttons in empty states work correctly (navigate to relevant view, open creation modal, etc.)
- [ ] "Coming soon" placeholders use the EmptyState component with CSS classes (no inline styles)
- [ ] All empty states use CSS variables for theming
- [ ] Small variant works well in sidebar contexts (conversation search, settings nav)
