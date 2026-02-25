# Tasks: Debounce Search and Input Operations

---

## Phase 1: Debounce Utility

### 1.1 Create debounce utility

- [ ] Create `electron-app/src/renderer/utils/debounce.js`
- [ ] Implement `debounce(fn, delay, options)` with leading/trailing edge support
- [ ] Add `.cancel()` method on returned function
- [ ] Expose as `window.debounce`
- [ ] Register script in `index.html`

---

## Phase 2: Conversation Search

### 2.1 Debounce conversation search

- [ ] Wrap `searchConversations()` call at `app.js:2611` with `debounce(searchConversations, 200)`
- [ ] Remove duplicate listener at `app.js:4116`
- [ ] Test: type rapidly in search → should only re-render once after 200ms pause

### 2.2 Add searching indicator

- [ ] On raw `input` event (not debounced), add `.input-searching` class to input
- [ ] In debounced callback, remove `.input-searching` class
- [ ] Add `.input-searching` CSS with subtle spinner or opacity change

---

## Phase 3: Other Search/Filter Inputs

### 3.1 Notes search debounce

- [ ] Audit `notes-manager.js` for input-driven search/filter operations
- [ ] Wrap in `debounce()` with 250ms delay
- [ ] Test: filter notes by typing → should debounce

### 3.2 Garden entity search migration

- [ ] Replace manual `clearTimeout`/`setTimeout` pattern (`app.js:20821-20826`) with `debounce()` utility
- [ ] Keep 300ms delay (already correct)
- [ ] Verify identical behavior after migration

### 3.3 Pattern/model filter debounce

- [ ] Audit patterns and mental models views for any input-driven filtering
- [ ] Apply debounce where found

---

## Phase 4: Auto-Save Standardization

### 4.1 Notes auto-save migration (optional)

- [ ] Evaluate whether `notes-manager.js` auto-save delay (`this.autoSaveDelay = 2000`) should use the debounce utility
- [ ] If beneficial: migrate to `debounce(this.saveCurrentNote.bind(this), 2000)`
- [ ] Ensure `.cancel()` is called when switching notes to prevent saving to the wrong note

---

## Completion Criteria

- [ ] Reusable `debounce()` utility exists and is globally accessible
- [ ] Conversation search is debounced (200ms) — no full re-render on every keystroke
- [ ] Duplicate search listener removed
- [ ] Garden entity search uses the shared utility (not manual setTimeout)
- [ ] All input-driven filtering across the app is debounced
- [ ] Visual feedback (searching indicator) shown during debounce delay
- [ ] Performance improvement measurable: rapid typing in search causes 1 re-render instead of N
