# Tasks: Undo for Destructive Actions

Depends on `ux-consistent-feedback` (showToast action button support). Implement UndoManager first, then migrate each entity type.

---

## Phase 1: UndoManager Utility

### 1.1 Create UndoManager class

- [ ] Create `electron-app/src/renderer/utils/undo-manager.js`
- [ ] Implement `schedule(id, options)` — registers pending deletion with timer
- [ ] Implement `cancel(id)` — cancels timer, calls `onRestore`, shows "restored" toast
- [ ] Implement `executePending()` — forces all pending deletes (for app quit)
- [ ] Implement `cancelAll()` — cancels all pending (restores everything)
- [ ] Expose as `window.undoManager`
- [ ] Register script in `index.html`

### 1.2 Wire app quit handler

- [ ] In `app.js` or via IPC, listen for `beforeunload` event
- [ ] Call `window.undoManager.executePending()` to flush all pending deletes
- [ ] Ensure this runs synchronously or uses `navigator.sendBeacon` for reliability

---

## Phase 2: Conversation Delete Undo

### 2.1 Implement conversation hide/restore

- [ ] Modify `deleteConversation()` (`app.js:2183`) to:
  - Remove `confirm()` call
  - Hide conversation from UI immediately (filter from render list or add `.hidden` class)
  - If deleted conversation was active, switch to next conversation
  - Call `undoManager.schedule()` with restore/delete callbacks
- [ ] `onRestore`: re-add conversation to local state, re-render list, optionally switch back to it
- [ ] `onDelete`: call `window.polly.conversationDelete(id)` (actual permanent delete)
- [ ] Test: delete conversation → see undo toast → click undo → conversation reappears

---

## Phase 3: Agent Delete Undo

### 3.1 Implement agent hide/restore

- [ ] Modify agent delete handler (`app.js:1586`) to use `undoManager.schedule()`
- [ ] Hide agent from sidebar immediately
- [ ] `onRestore`: re-add agent to sidebar, re-render
- [ ] `onDelete`: call `window.polly.agentDelete(id)`

---

## Phase 4: Mental Model Delete Undo

### 4.1 Implement mental model hide/restore

- [ ] Modify mental model delete handler (`app.js:13300`) to use `undoManager.schedule()`
- [ ] Remove model from displayed list, keep data in memory
- [ ] `onRestore`: re-add to list, re-render
- [ ] `onDelete`: call `DELETE /polly/mental-models/{id}`

---

## Phase 5: Curriculum Delete Undo

### 5.1 Implement curriculum hide/restore

- [ ] Modify curriculum delete handler (`app.js:7217`) to use `undoManager.schedule()`
- [ ] Hide curriculum from list
- [ ] `onRestore`: re-add, re-render
- [ ] `onDelete`: call delete endpoint

---

## Phase 6: Domain Delete Undo

### 6.1 Implement domain hide/restore

- [ ] Modify domain delete handler (`app.js:13903`) to use `undoManager.schedule()`
- [ ] Hide domain from list
- [ ] `onRestore`: re-add, re-render
- [ ] `onDelete`: call delete endpoint

---

## Phase 7: API Key Delete Undo

### 7.1 Implement API key hide/restore

- [ ] Modify API key delete handler (`api-keys-manager.js:461`) to use `undoManager.schedule()`
- [ ] Hide key from displayed list
- [ ] `onRestore`: re-add to list, re-render
- [ ] `onDelete`: call actual delete via keytar/keychain

---

## Phase 8: Pattern Reset Undo (Special Case)

### 8.1 Snapshot and restore patterns

- [ ] Before reset (`app.js:10265`), fetch current patterns from `GET /polly/patterns` and store in memory
- [ ] Execute reset immediately
- [ ] `undoManager.schedule()` with longer timeout (10 seconds — this is a bigger operation)
- [ ] `onRestore`: POST snapshot back to restore patterns (may need a bulk import endpoint)
- [ ] `onDelete`: discard snapshot (no further action needed — reset already executed)

### 8.2 Backend support for pattern restore (if needed)

- [ ] Check if a `POST /polly/patterns/import` or similar endpoint exists
- [ ] If not, add one that accepts a patterns array and writes them back to storage
- [ ] This is the only backend change in this entire spec

---

## Completion Criteria

- [ ] UndoManager utility exists and is globally accessible
- [ ] Conversation delete shows undo toast and restores on click
- [ ] Agent delete shows undo toast and restores on click
- [ ] Mental model delete shows undo toast and restores on click
- [ ] Curriculum delete shows undo toast and restores on click
- [ ] Domain delete shows undo toast and restores on click
- [ ] API key delete shows undo toast and restores on click
- [ ] Pattern reset shows undo toast and restores on click
- [ ] Undo window is 5 seconds for single items, 10 seconds for bulk operations
- [ ] App quit flushes all pending deletes (no items left in hidden-but-not-deleted state)
- [ ] Multiple concurrent undo operations work correctly (e.g., delete 3 conversations rapidly)
