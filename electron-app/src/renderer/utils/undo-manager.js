/**
 * UndoManager — lightweight pending-deletion tracker with timer-based commit.
 *
 * Usage:
 *   window.undoManager.schedule("conv-abc", {
 *     label:     "My Chat",
 *     onDelete:  () => window.polly.conversationDelete("abc"),
 *     onRestore: () => { /* re-add to local state; re-render *\/ },
 *     timeout:   5000,   // ms (default 5000)
 *   });
 *
 * The manager shows a toast with an "Undo" action button. If the user clicks
 * Undo the deletion is cancelled and the item is restored. If the timeout
 * expires the permanent delete fires automatically.
 *
 * Call window.undoManager.executePending() before the app quits so nothing
 * is left in the hidden-but-not-deleted limbo state.
 */
class UndoManager {
  constructor() {
    /** @type {Map<string, {label:string, timer:number, onRestore:Function, onDelete:Function, toastId:string}>} */
    this.pending = new Map();
  }

  /**
   * Schedule a destructive action with undo capability.
   *
   * @param {string} id - stable unique identifier (e.g. "conv-abc123")
   * @param {object} options
   * @param {string}   options.label     - human-readable name shown in toast
   * @param {function} options.onDelete  - called when undo window expires
   * @param {function} options.onRestore - called when user clicks Undo
   * @param {number}  [options.timeout=5000] - undo window in ms
   * @returns {string} toastId
   */
  schedule(id, options) {
    const { label, onDelete, onRestore, timeout = 5000 } = options;

    // Cancel any existing pending delete for this id
    if (this.pending.has(id)) {
      this._clearEntry(id, false /* don't restore */);
    }

    const timer = setTimeout(() => {
      try { onDelete(); } catch (e) { console.error('[UndoManager] onDelete threw:', e); }
      this.pending.delete(id);
    }, timeout);

    const toastId = showToast(`${label} deleted`, 'info', {
      duration: timeout,
      action: () => this.cancel(id),
      actionLabel: 'Undo',
    });

    this.pending.set(id, { label, timer, onRestore, onDelete, toastId });
    return toastId;
  }

  /**
   * Cancel a pending deletion — restores the item and shows a "restored" toast.
   * @param {string} id
   */
  cancel(id) {
    const entry = this.pending.get(id);
    if (!entry) return;

    this._clearEntry(id, true /* restore */);
    showToast(`${entry.label} restored`, 'success', { duration: 2000 });
  }

  /**
   * Cancel all pending deletions and restore all items.
   * Useful if the user performs a "cancel all" action.
   */
  cancelAll() {
    for (const id of [...this.pending.keys()]) {
      this.cancel(id);
    }
  }

  /**
   * Flush all pending deletes immediately (e.g. on app quit).
   * Fires onDelete for every pending entry without waiting for timers.
   */
  executePending() {
    for (const [id, entry] of this.pending) {
      clearTimeout(entry.timer);
      try { entry.onDelete(); } catch (e) { console.error('[UndoManager] executePending onDelete threw:', e); }
    }
    this.pending.clear();
  }

  /** @private */
  _clearEntry(id, restore) {
    const entry = this.pending.get(id);
    if (!entry) return;
    clearTimeout(entry.timer);
    if (restore) {
      try { entry.onRestore(); } catch (e) { console.error('[UndoManager] onRestore threw:', e); }
    }
    if (entry.toastId) {
      try { dismissToast(entry.toastId); } catch (_) {}
    }
    this.pending.delete(id);
  }
}

window.undoManager = new UndoManager();
