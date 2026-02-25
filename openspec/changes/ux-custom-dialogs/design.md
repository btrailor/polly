# Design: Custom Styled Dialogs

## Architecture Impact

### New Component

**`ConfirmDialog`** (`electron-app/src/renderer/components/confirm-dialog.js` + `confirm-dialog.css`)

A promise-based confirmation dialog that replaces native `confirm()`. Returns a `Promise<boolean>` so callers can `await` the result.

```js
// Usage
const confirmed = await ConfirmDialog.show({
  title: 'Delete conversation',
  message: 'Are you sure you want to delete "My Chat"? This cannot be undone.',
  confirmLabel: 'Delete',        // default: 'Confirm'
  cancelLabel: 'Cancel',         // default: 'Cancel'
  destructive: true,             // red confirm button styling
  icon: 'trash-2',              // optional Lucide icon name
});
if (confirmed) { /* proceed */ }
```

### Component Specification

**Visual design:**
- Dark modal overlay (`rgba(0, 0, 0, 0.6)`) matching existing modal patterns
- Centered dialog panel with `var(--bg-secondary)` background, consistent border radius
- Title in `var(--text-primary)`, message in `var(--text-secondary)`
- Two action buttons: Cancel (ghost/outlined) and Confirm (filled, accent or destructive-red)
- Optional Lucide icon in the header area
- Max-width `420px`, responsive padding

**Behavior:**
- `Escape` key → cancel
- `Enter` key → confirm
- Click overlay → cancel
- Focus trapped within the dialog (Tab cycles between Cancel and Confirm)
- Focus set to Cancel button on open (safe default — user must explicitly reach for Confirm)
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby` and `aria-describedby` for accessibility
- Body scroll locked while dialog is open
- Animate in: fade + slight scale (150ms ease-out). Animate out: fade (100ms ease-in)
- Only one dialog visible at a time (queue or replace)

**Destructive variant:**
- Confirm button uses `var(--accent-red, #e53935)` background
- Icon defaults to `alert-triangle` if not specified

### Existing System Modifications

**`showToast()` fix (`app.js:240-260`):**
- Remove the `alert()` fallback at line 254
- Instead, create the toast container lazily if it doesn't exist in the DOM
- Ensure the container is appended to `document.body` on first call

**Migration pattern:**
Each `alert()` call maps to a `showToast()` call with the appropriate type:

| Current Pattern | Replacement |
|----------------|-------------|
| `alert("Settings saved!")` | `showToast("Settings saved", "success")` |
| `alert(\`Error: ${msg}\`)` | `showToast(msg, "error")` |
| `alert("Please enter valid...")` | `showToast("Please enter valid...", "warning")` |
| `alert(\`Note saved: ${title}\`)` | `showToast(\`Note saved: ${title}\`, "success")` |

Each `confirm()` call maps to a `ConfirmDialog.show()` call:

| Current Pattern | Replacement |
|----------------|-------------|
| `if (!confirm(\`Delete "${name}"?\`)) return;` | `if (!(await ConfirmDialog.show({ title: "Delete conversation", message: \`Delete "${name}"?\`, destructive: true, confirmLabel: "Delete" }))) return;` |

**Note:** Functions containing `confirm()` that are not already `async` must be converted to `async` when migrating. Callers should already handle promises or use `await`.

### Mental Model Validation Special Case

`app.js:13165-13190` uses 6 sequential `alert()` calls for field validation, each blocking the user. Replace with:
- Collect all validation errors into an array
- Show a single `showToast()` with a combined message listing all issues
- Or highlight invalid fields inline with red borders and helper text (preferred, but more effort)

## Implementation Notes

- The `ConfirmDialog` component should be a singleton — one instance created at app startup, reused for all confirmations
- Export as `window.ConfirmDialog` for global access (matching existing component patterns like `window.QuestionForm`, `window.PreviewModal`)
- CSS should use existing CSS variables from `main.css` for consistency
- No external dependencies — pure vanilla JS and CSS
