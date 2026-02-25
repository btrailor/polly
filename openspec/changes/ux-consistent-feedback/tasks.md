# Tasks: Consistent User Feedback System

---

## Phase 1: Enhance showToast()

### 1.1 Add options parameter

- [ ] Refactor `showToast(message, type, duration)` to `showToast(message, type, options)` with backward compatibility (if third arg is a number, treat as duration)
- [ ] Support `options.duration`, `options.persistent`, `options.action`, `options.actionLabel`, `options.icon`
- [ ] Add action button rendering inside toast when `options.action` is provided
- [ ] Add persistent mode: no auto-dismiss timer, requires click to close

### 1.2 Toast stacking

- [ ] Limit visible toasts to 3 maximum
- [ ] New toasts stack from bottom, push older ones up
- [ ] Excess toasts auto-dismiss the oldest
- [ ] Each toast gets a unique ID, returned by `showToast()` for programmatic dismissal via `dismissToast(id)`

### 1.3 Toast CSS improvements

- [ ] Add stacking layout (flexbox column-reverse or similar)
- [ ] Ensure toasts don't overlap with chat panel or modals (z-index: above modals)
- [ ] Add action button styling within toast
- [ ] Verify `prefers-reduced-motion` removes slide animation (from accessibility change)

---

## Phase 2: Button Loading Pattern

### 2.1 Create withButtonLoading utility

- [ ] Implement `withButtonLoading(button, asyncFn, successMessage)` in `app.js` (or `utils/`)
- [ ] Disables button, shows spinner + "Saving..." text
- [ ] On success: shows toast, restores button
- [ ] On error: shows error toast, restores button
- [ ] Returns the result of `asyncFn` for chaining

### 2.2 Add button loading CSS

- [ ] Create `.btn-loading` class: reduces opacity, changes cursor
- [ ] Create `.btn-spinner` inline spinner (small, 14px, matches button text color)
- [ ] Ensure spinner respects `prefers-reduced-motion`

---

## Phase 3: Consolidate showNotification

### 3.1 Audit showNotification usage

- [ ] Find definition of `showNotification()` — determine if it's a separate function or alias for `showToast()`
- [ ] If separate: replace all calls with `showToast()` equivalents and remove the function
- [ ] If alias: keep as alias or inline, ensuring consistent behavior
- [ ] Verify pattern export (`10254, 10257`) and pattern import (`10291, 10295`) use toasts after migration

---

## Phase 4: Migrate Inline Feedback

### 4.1 Budget save button

- [ ] Replace button text "Saved!" pattern (`api-keys-manager.js:515-523`) with `withButtonLoading` + toast
- [ ] Remove manual `setTimeout` for text revert

### 4.2 API key save modal

- [ ] Replace inline green checkmark + auto-close (`api-keys-manager.js:401-404`) with toast + explicit close
- [ ] Show `showToast("API key for {provider} saved", "success")` on save
- [ ] Close modal after toast is shown (not after arbitrary delay)

### 4.3 API key test results

- [ ] Keep inline test results for contextual display (user needs to see result near the test button)
- [ ] Additionally show a toast for the overall result ("API key valid" / "API key invalid")
- [ ] Remove the `setTimeout` revert pattern (`api-keys-manager.js:440-453`) — let result persist until modal closes or key is retested

### 4.4 API key delete

- [ ] Add success toast on key deletion (`api-keys-manager.js:476`): `showToast("API key deleted", "info")`
- [ ] Currently no feedback at all on successful delete — list just refreshes silently

---

## Phase 5: Add Inline Validation

### 5.1 Field validation styles

- [ ] Add `.field-error` CSS class (red border) and `.field-error-message` (red helper text)
- [ ] Add `.field-success` CSS class (green/accent border) for successful validation

### 5.2 Mental model validation consolidation

- [ ] Replace 6 sequential `alert()` calls (`app.js:13165-13190`) with:
  - Collect all validation errors into an array
  - Highlight each invalid field with `.field-error` class
  - Show a single summary toast: `showToast("Please fix {n} validation errors", "warning")`
  - Clear error highlights when user starts editing the field

### 5.3 Settings validation

- [ ] Add basic validation to port field (numeric, range 1024-65535)
- [ ] Add validation to API key field (non-empty when save is clicked)
- [ ] Show inline error messages below invalid fields
- [ ] Block save and show warning toast if validation fails

---

## Completion Criteria

- [ ] Every user action that saves data shows feedback via `showToast()` (not `alert()`, not inline text mutation)
- [ ] Every save button shows a loading spinner during the async operation
- [ ] `showNotification()` is removed or aliased to `showToast()`
- [ ] Toast stacking works correctly with max 3 visible
- [ ] API key delete shows success feedback
- [ ] Mental model validation shows consolidated errors (not 6 sequential dialogs)
- [ ] No `setTimeout`-based button text revert patterns remain
- [ ] Inline validation with red borders exists for form fields with validation requirements
