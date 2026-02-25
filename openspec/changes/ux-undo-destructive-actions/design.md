# Design: Undo for Destructive Actions

## Architecture Impact

### Undo Manager

A lightweight undo manager that tracks pending deletions and handles timer-based permanent execution.

```js
// electron-app/src/renderer/utils/undo-manager.js

class UndoManager {
  constructor() {
    this.pending = new Map(); // id -> { type, data, timer, restoreFn, deleteFn }
  }

  /**
   * Schedule a destructive action with undo capability.
   * @param {string} id - unique identifier (e.g., "conversation-abc123")
   * @param {object} options
   * @param {string} options.type - entity type ("conversation", "mental-model", etc.)
   * @param {string} options.label - human-readable label for the toast ("My Chat")
   * @param {function} options.onDelete - called when undo window expires (permanent delete)
   * @param {function} options.onRestore - called when user clicks Undo (restore item)
   * @param {number} options.timeout - undo window in ms (default: 5000)
   * @returns {string} toastId - the toast ID for programmatic dismissal
   */
  schedule(id, options) {
    const { type, label, onDelete, onRestore, timeout = 5000 } = options;

    // If there's already a pending delete for this item, cancel it
    if (this.pending.has(id)) {
      this.cancel(id);
    }

    const timer = setTimeout(() => {
      onDelete();
      this.pending.delete(id);
    }, timeout);

    this.pending.set(id, { type, label, timer, onRestore, onDelete });

    // Show toast with undo action
    const toastId = showToast(
      `${label} deleted`,
      'info',
      {
        duration: timeout,
        action: () => this.cancel(id),
        actionLabel: 'Undo',
      }
    );

    return toastId;
  }

  cancel(id) {
    const entry = this.pending.get(id);
    if (!entry) return;

    clearTimeout(entry.timer);
    entry.onRestore();
    this.pending.delete(id);
    showToast(`${entry.label} restored`, 'success', { duration: 2000 });
  }

  // Cancel all pending deletes (e.g., on app quit)
  cancelAll() {
    for (const [id] of this.pending) {
      this.cancel(id);
    }
  }
}

window.undoManager = new UndoManager();
```

### Per-Entity Undo Flow

#### Conversations

```
Current:
  confirm() → conversationDelete() → remove from local state → re-render

New:
  1. Hide conversation from UI immediately (add .conversation-hidden class or filter from render)
  2. undoManager.schedule("conv-{id}", {
       label: conversation.title,
       onDelete: () => window.polly.conversationDelete(id),  // permanent delete
       onRestore: () => { unhide conversation; re-render list; },
     })
  3. If undo clicked: conversation reappears in list
  4. If timeout expires: actual delete call fires
```

The conversation manager's existing `deleted_at` soft-delete column can optionally be used: set `deleted_at` immediately, clear it on undo, and have a cleanup job for expired soft-deletes. But the simpler approach (delay the API call, hide in UI) is sufficient and avoids backend changes.

#### Mental Models

```
Current:
  confirm() → DELETE /polly/mental-models/{id} → remove from list → re-render

New:
  1. Remove from displayed list immediately (but keep data in memory)
  2. undoManager.schedule("model-{id}", {
       label: model.name,
       onDelete: () => safeFetch(`/polly/mental-models/${id}`, { method: 'DELETE' }),
       onRestore: () => { re-add to list; re-render; },
     })
```

#### Agents

```
Current:
  confirm() → window.polly.agentDelete(id) → remove from sidebar → re-render

New:
  1. Hide agent from sidebar
  2. undoManager.schedule("agent-{id}", {
       label: agent.name,
       onDelete: () => window.polly.agentDelete(id),
       onRestore: () => { unhide agent; re-render; },
     })
```

The same pattern applies to curricula, domains, API keys, and pattern resets.

### Pattern Reset (Special Case)

"Reset all patterns" is different from single-item deletion — it's a bulk operation that clears the entire pattern store. For this:

1. Before reset, snapshot the current patterns state (fetch from API and hold in memory).
2. Execute the reset immediately.
3. Show undo toast.
4. If undo clicked: POST the snapshot back to restore patterns.
5. If timeout expires: discard the snapshot.

This requires the patterns API to support a bulk import/restore endpoint (or we hold the data client-side and re-POST individual patterns).

### App Quit Safety

When the app is about to quit (Electron `before-quit` event), all pending undo timers should be cancelled and permanent deletions executed immediately, so the user doesn't lose their undo window and have items in a "hidden but not deleted" limbo state.

```js
// main.js or via IPC
window.addEventListener('beforeunload', () => {
  window.undoManager.executePending(); // force all pending deletes
});
```

Alternatively, cancel all pending and restore items (safer — the user didn't explicitly confirm they wanted the delete to go through, since they might have quit to undo via "I'll just restart the app"). Either behavior is defensible; defaulting to **execute pending deletes** matches the mental model of "the undo window has closed."

## Files Affected

| File | Changes |
|------|---------|
| New: `utils/undo-manager.js` | UndoManager class |
| `app.js` | Replace `confirm()` + immediate delete with `undoManager.schedule()` for conversations, agents, mental models, curricula, domains |
| `api-keys-manager.js` | Replace `confirm()` + delete for API keys with `undoManager.schedule()` |
| `index.html` | Register `undo-manager.js` script |
| `main.js` or `app.js` | Handle `beforeunload` to flush pending deletes |

## Dependencies on Other Changes

- **`ux-consistent-feedback`:** The `showToast()` enhancement with `action` button support is required for the undo toast. Implement that first.
