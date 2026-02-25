# Tasks: Replace setTimeout Race Conditions

---

## Phase 1: DOM Helper Utilities

### 1.1 Create DOM helper utilities

- [ ] Create `electron-app/src/renderer/utils/dom-helpers.js`
- [ ] Implement `waitForElement(selector, container, timeout)` using MutationObserver
- [ ] Implement `refreshIcons(container)` with requestAnimationFrame batching
- [ ] Expose as `window.waitForElement` and `window.refreshIcons`
- [ ] Register in `index.html`

---

## Phase 2: Replace Lucide Icon Delays

### 2.1 Centralize icon refresh

- [ ] Search for all `lucide.createIcons()` calls in `app.js` (5+ locations)
- [ ] Replace each `setTimeout(() => lucide.createIcons(), 50)` with `refreshIcons()`
- [ ] Replace direct `lucide.createIcons()` calls after DOM mutations with `refreshIcons()` as well
- [ ] Verify: icons render correctly in all contexts (sidebar toggle, view switch, dynamic list render)

---

## Phase 3: Replace DOM Readiness Delays

### 3.1 Fix notes initialization

- [ ] Replace `setTimeout(() => notesManager.initialize(), 100)` at `app.js:~3095` with double `requestAnimationFrame` or `waitForElement` for the notes container
- [ ] Test: switch to Notes view rapidly → initialization completes correctly
- [ ] Test: switch to Notes view on slow DOM → no race condition

### 3.2 Audit other view initialization delays

- [ ] Search `app.js` for `setTimeout` calls within `showView()` and view initialization code
- [ ] Replace any arbitrary delays with `requestAnimationFrame` or `waitForElement`
- [ ] Document any delays that are intentional and cannot be replaced (with a comment explaining why)

---

## Phase 4: Fix Persona Auto-Advance

### 4.1 Add cancellation and state validation

- [ ] Replace `setTimeout(async () => { /* persona step */ }, 500)` at `app.js:~5371`
- [ ] Add `cancelPersonaAutoAdvance()` function
- [ ] Add state validation (current step, current conversation) before execution
- [ ] Cancel on: new message send, view switch, conversation switch
- [ ] Test: send message → start auto-advance → quickly send another message → auto-advance for first message should not fire

---

## Phase 5: Replace Miscellaneous Delays

### 5.1 Auto-categorize with requestIdleCallback

- [ ] Replace `setTimeout(() => autoCategorizeConversation(), 200)` at `app.js:~8745` with `requestIdleCallback`
- [ ] Add polyfill for `requestIdleCallback` (simple `setTimeout` fallback for older Electron versions)
- [ ] Add 1-second timeout to ensure it eventually runs

### 5.2 Audit remaining setTimeouts

- [ ] Search for all `setTimeout` calls in `app.js`, `notes-manager.js`, `api-keys-manager.js`
- [ ] Categorize each as: (a) intentional delay (debounce, animation, user-facing), (b) race condition workaround
- [ ] Replace (b) category with robust alternatives
- [ ] Add comments to (a) category explaining the intentional delay

---

## Completion Criteria

- [ ] `refreshIcons()` utility replaces all scattered `setTimeout(() => lucide.createIcons(), 50)` calls
- [ ] `waitForElement()` utility available for DOM-readiness checks
- [ ] Notes view initialization works without arbitrary 100ms delay
- [ ] Persona auto-advance has cancellation and state validation
- [ ] Auto-categorize uses `requestIdleCallback` instead of arbitrary `setTimeout`
- [ ] All remaining `setTimeout` calls in renderer code are either: (a) intentional with comments, or (b) replaced with robust alternatives
- [ ] No race conditions observed during rapid view switching
