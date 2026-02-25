# Design: Consistent User Feedback System

## Architecture Impact

No new subsystems. Enhancement of the existing `showToast()` function and standardization of its usage.

### showToast() Enhancements

**Current signature** (`app.js:240`):
```js
function showToast(message, type = 'info', duration = 4000)
```

**Enhanced signature:**
```js
function showToast(message, type = 'info', options = {})
// options: { duration, persistent, action, actionLabel, icon }
```

New capabilities:

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `duration` | `number` | `4000` | Auto-dismiss time in ms. `0` for persistent |
| `persistent` | `boolean` | `false` | Stay until manually dismissed |
| `action` | `function` | `null` | Callback for action button (e.g., "Undo") |
| `actionLabel` | `string` | `null` | Label for the action button |
| `icon` | `string` | auto | Lucide icon name. Auto-selects based on type if not provided |

This allows the toast system to handle the "Undo" pattern (needed by `ux-undo-destructive-actions`) and richer feedback without adding a new mechanism.

### Toast Stacking and Queue

- Maximum 3 toasts visible simultaneously
- New toasts push older ones up (stack from bottom)
- If more than 3, oldest auto-dismiss early
- Each toast has a unique ID for programmatic dismissal

### Save Button Loading Pattern

Standardize how save buttons behave during async operations:

```js
async function withButtonLoading(button, asyncFn) {
  const originalText = button.textContent;
  const originalDisabled = button.disabled;

  button.disabled = true;
  button.classList.add('btn-loading');
  button.innerHTML = '<div class="btn-spinner"></div> Saving...';

  try {
    const result = await asyncFn();
    showToast(/* success message */, 'success');
    return result;
  } catch (error) {
    showToast(error.message, 'error');
    throw error;
  } finally {
    button.disabled = originalDisabled;
    button.classList.remove('btn-loading');
    button.textContent = originalText;
  }
}
```

### Feedback Consolidation Map

| Current Mechanism | Location | Replacement |
|-------------------|----------|-------------|
| `alert("Settings saved!")` | `app.js:10358` | `showToast("Settings saved", "success")` |
| `alert("Routing settings saved successfully!")` | `app.js:10752` | `showToast("Routing settings saved", "success")` |
| Button text "Saved!" for 2s | `api-keys-manager.js:515-523` | `showToast("Budget saved", "success")` + use `withButtonLoading` |
| Green checkmark inline | `api-keys-manager.js:401` | `showToast("API key saved", "success")` + close modal |
| Status element mutation for test | `api-keys-manager.js:425-453` | Keep inline for test results (contextual), but also `showToast` for the final status |
| `showNotification(...)` | `app.js:10254, 10257, 10291, 10295` | Replace with `showToast()` or verify they're the same function and remove duplication |
| Sequential `alert()` for validation | `app.js:13165-13190` | Inline field validation with red borders + single summary toast |

### Inline Validation (for form-heavy sections)

For settings panels and forms with multiple fields, complement toasts with inline validation:

```css
.field-error {
  border-color: var(--accent-red, #e53935) !important;
}
.field-error-message {
  color: var(--accent-red, #e53935);
  font-size: 11px;
  margin-top: 4px;
}
```

This provides contextual feedback (which field is wrong) while the toast provides the summary.

## Files Affected

| File | Changes |
|------|---------|
| `app.js` | Enhance `showToast()`, add `withButtonLoading()`, migrate all `alert()` feedback, consolidate `showNotification()`, add loading states to save buttons |
| `api-keys-manager.js` | Replace inline status mutations with toasts, use `withButtonLoading` for budget save |
| `styles/main.css` | Add `.btn-loading`, `.btn-spinner` styles. Enhance toast stacking CSS. Add `.field-error` styles |
