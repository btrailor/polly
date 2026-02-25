# Tasks: Custom Styled Dialogs

Ordered by dependency. Component first, then systematic migration.

---

## Phase 1: Build the ConfirmDialog Component

### 1.1 Create ConfirmDialog component

- [ ] Create `electron-app/src/renderer/components/confirm-dialog.js`
- [ ] Implement `ConfirmDialog.show(options)` returning `Promise<boolean>`
- [ ] Options: `title`, `message`, `confirmLabel`, `cancelLabel`, `destructive`, `icon`
- [ ] Render: overlay, dialog panel, title, message, Cancel + Confirm buttons
- [ ] Singleton pattern — one DOM element reused across calls
- [ ] Expose as `window.ConfirmDialog`

### 1.2 Create ConfirmDialog styles

- [ ] Create `electron-app/src/renderer/components/confirm-dialog.css`
- [ ] Dark theme matching `var(--bg-secondary)`, `var(--text-primary)`, `var(--accent-primary)`
- [ ] Destructive variant: red confirm button
- [ ] Entry/exit animations (fade + scale)
- [ ] Max-width 420px, responsive padding
- [ ] Link stylesheet in `index.html`

### 1.3 Implement keyboard and accessibility

- [ ] `Escape` → cancel, `Enter` → confirm
- [ ] Focus trap: Tab cycles within dialog
- [ ] Initial focus on Cancel button (safe default)
- [ ] `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `aria-describedby`
- [ ] Body scroll lock while open

### 1.4 Register in index.html

- [ ] Add `<script>` tag for `confirm-dialog.js` in `index.html`
- [ ] Add `<link>` tag for `confirm-dialog.css` in `index.html`

---

## Phase 2: Fix showToast() Fallback

### 2.1 Remove alert() from showToast

- [ ] In `app.js:254`, remove the `if (type === "error") alert(...)` fallback
- [ ] Replace with lazy container creation: if `#polly-toast-container` doesn't exist, create and append it to `document.body`
- [ ] Test: call `showToast()` before DOM is fully loaded — should work without native alert

---

## Phase 3: Migrate alert() to showToast()

Migrate systematically by file. Each migration is a direct replacement.

### 3.1 Migrate app.js alert() calls (~80 instances)

- [ ] Settings saves (`10358, 10752`) → `showToast("Settings saved", "success")`
- [ ] Note save to Obsidian (`5867-5871`) → `showToast(\`Note saved: ${title}\`, "success")`
- [ ] Mental model validation (`13165-13190`) → collect errors into array, show single toast or inline validation
- [ ] Sync errors (`11145-11318`, 8 instances) → `showToast(errorMsg, "error")`
- [ ] Graph garden operations (`20579-20782`, 7+ instances) → appropriate toast types
- [ ] Setup errors (`4572, 4576`) → `showToast(errorMsg, "error")`
- [ ] Pattern export (`10235`) → `showToast("Could not export patterns", "error")`
- [ ] Domain operations (`13899-13924`) → toast
- [ ] Keyword suggestions (`14157-14215`) → toast
- [ ] All remaining `alert()` calls in `app.js`
- [ ] Verify: `grep -c "alert(" app.js` returns 0

### 3.2 Migrate api-keys-manager.js alert() calls (~5 instances)

- [ ] Key deletion error (`480`) → `showToast(error.message, "error")`
- [ ] Budget validation (`492`) → `showToast("Please enter valid budget limits", "warning")`
- [ ] Budget save error (`527`) → `showToast(error.message, "error")`
- [ ] All remaining `alert()` calls
- [ ] Verify: `grep -c "alert(" api-keys-manager.js` returns 0

### 3.3 Migrate notes-manager.js alert() calls (~3 instances)

- [ ] Note append validation (`2619`) → `showToast("Please select a note to append to", "warning")`
- [ ] All remaining `alert()` calls
- [ ] Verify: `grep -c "alert(" notes-manager.js` returns 0

### 3.4 Migrate component file alert() calls

- [ ] Scan all files in `components/` for `alert(` and replace
- [ ] Verify: `grep -r "alert(" components/` returns 0

---

## Phase 4: Migrate confirm() to ConfirmDialog

Each function using `confirm()` must become `async` (if not already) and use `await ConfirmDialog.show()`.

### 4.1 Migrate app.js confirm() calls (~8 instances)

- [ ] Delete conversation (`2187`) → `await ConfirmDialog.show({ title: "Delete conversation", ... , destructive: true })`
- [ ] Reset all settings (`2776`) → destructive confirmation
- [ ] Delete agent (`1586`) → destructive confirmation
- [ ] Delete curriculum (`7217`) → destructive confirmation
- [ ] Reset all patterns (`10265`) → destructive confirmation with detailed message
- [ ] Delete mental model (`13300`) → destructive confirmation
- [ ] Delete domain (`13903`) → destructive confirmation
- [ ] Prune graph connections (`20695`) → destructive confirmation
- [ ] Convert containing functions to `async` where needed
- [ ] Verify: `grep -c "confirm(" app.js` returns 0 (excluding ConfirmDialog references)

### 4.2 Migrate api-keys-manager.js confirm() calls

- [ ] Delete API key (`461`) → destructive confirmation
- [ ] Verify: `grep -c "confirm(" api-keys-manager.js` returns 0

---

## Phase 5: Validation and Cleanup

### 5.1 Full audit

- [ ] Run `grep -rn "alert(" electron-app/src/renderer/` — should return 0 results
- [ ] Run `grep -rn "[^.]confirm(" electron-app/src/renderer/` — should return 0 results (excluding `ConfirmDialog` references)
- [ ] Manual test: trigger every migrated path (save settings, delete conversation, delete agent, etc.)
- [ ] Verify toast positioning doesn't overlap with chat panel or modals

### 5.2 Documentation

- [ ] Add JSDoc comments to `ConfirmDialog.show()` documenting all options
- [ ] Add usage example in a comment block at the top of `confirm-dialog.js`

---

## Completion Criteria

- [ ] Zero native `alert()` calls remain in renderer codebase
- [ ] Zero native `confirm()` calls remain in renderer codebase
- [ ] `ConfirmDialog` component is accessible (keyboard nav, ARIA, focus trap)
- [ ] `showToast()` works without fallback to native `alert()`
- [ ] All destructive actions show themed confirmation dialogs
- [ ] All success/error messages show themed toast notifications
- [ ] Mental model validation shows a single consolidated error (not 6 sequential dialogs)
