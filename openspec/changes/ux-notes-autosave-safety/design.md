# Design: Notes Auto-Save Safety

## Architecture Impact

### 1. Conflict Detection

**Current behavior (`notes-manager.js:467-517`):**
```
reloadAfterSync() called every 5s:
  → if user is editing: skip reload (return early)
  → if content changed externally: reload from disk
```

**New behavior:**
```
reloadAfterSync() called every 5s:
  → fetch latest content from disk
  → if user is NOT editing:
      → if content changed: reload (existing behavior)
  → if user IS editing:
      → if external content ≠ last known external content:
          → store external change in pendingExternalChange
          → show "External change detected" banner in editor
      → on exit edit mode:
          → if pendingExternalChange exists:
              → show conflict resolution dialog
```

**Conflict resolution dialog:**

A custom modal (similar to ConfirmDialog but with 3 actions):

```js
const result = await ConflictDialog.show({
  title: 'Note changed externally',
  message: `"${note.title}" was modified outside Polly while you were editing.`,
  options: [
    { label: 'Keep my changes', value: 'mine', description: 'Discard the external changes' },
    { label: 'Load external version', value: 'theirs', description: 'Discard your edits and load the new version' },
    { label: 'View diff', value: 'diff', description: 'See what changed before deciding' },
  ]
});
```

If "View diff" is selected, show a side-by-side or inline diff of the two versions. The user can then choose "mine" or "theirs."

**Diff rendering:**
- Use a simple line-by-line diff algorithm (e.g., a minimal JS diff library or hand-rolled longest-common-subsequence)
- Display in a modal with additions in green, deletions in red
- No external dependency required — a 50-line diff function is sufficient for markdown notes

### 2. Version History

**Storage: SQLite table** (preferred over localStorage for size and query capability)

```sql
-- In conversation-manager.js or a new note-versions table
CREATE TABLE IF NOT EXISTS note_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  note_path TEXT NOT NULL,
  content TEXT NOT NULL,
  saved_at TEXT NOT NULL DEFAULT (datetime('now')),
  source TEXT NOT NULL DEFAULT 'auto-save',  -- 'auto-save', 'manual-save', 'revert'
  content_hash TEXT NOT NULL  -- SHA-256 of content, for dedup
);

CREATE INDEX idx_note_versions_path ON note_versions(note_path, saved_at DESC);
```

**Version management:**
- On each save, compute content hash. If hash matches the most recent version, skip (no duplicate saves).
- Keep the last 10 versions per note. On 11th save, delete the oldest.
- Cleanup: on app startup, delete versions older than 30 days.

**IPC bridge:**
```js
// preload.js additions
noteVersions: {
  save: (notePath, content, source) => ipcRenderer.invoke('note-versions:save', notePath, content, source),
  list: (notePath) => ipcRenderer.invoke('note-versions:list', notePath),
  get: (versionId) => ipcRenderer.invoke('note-versions:get', versionId),
  revert: (notePath, versionId) => ipcRenderer.invoke('note-versions:revert', notePath, versionId),
}
```

**Version history UI:**
- Accessible from a "History" button in the note editor toolbar
- Opens a sidebar panel or modal listing versions: date, time, source (auto-save/manual), content preview (first 100 chars)
- Click a version to preview it (read-only)
- "Restore this version" button to revert — creates a new version entry (source: 'revert') so the revert itself can be undone

### 3. Persistent Save Status

**Current:** `updateSaveStatus()` at `notes-manager.js:2122` shows "Saved" then hides after 1.5s.

**New:** Always show the current save state in the editor status bar:

| State | Display | Color |
|-------|---------|-------|
| Saved | "Saved" | `var(--text-muted)` (subtle, non-distracting) |
| Unsaved changes | "Unsaved" | `var(--accent-yellow)` |
| Saving... | "Saving..." | `var(--text-secondary)` |
| Save error | "Save failed" | `var(--accent-red)` |
| External change pending | "External change" | `var(--accent-yellow)` with icon |

Remove the `setTimeout` auto-hide. The status should always reflect the current state.

### 4. Dirty-State Navigation Guard

When the user has unsaved changes and tries to navigate away (switch views, switch notes, close app):

```js
// In notes-manager.js
canNavigateAway() {
  if (!this.hasUnsavedChanges) return true;

  // Option 1: Auto-save before navigating (least disruptive)
  await this.saveCurrentNote();
  return true;

  // Option 2: Confirm dialog (if save failed or user wants to discard)
  return await ConfirmDialog.show({
    title: 'Unsaved changes',
    message: 'You have unsaved changes. Save before leaving?',
    confirmLabel: 'Save and leave',
    cancelLabel: 'Discard changes',
  });
}
```

Preferred approach: auto-save before navigation (option 1). Only show the dialog if the auto-save fails.

## Files Affected

| File | Changes |
|------|---------|
| `notes-manager.js` | Conflict detection in `reloadAfterSync()`, version save on each `saveCurrentNote()`, persistent save status, navigation guard |
| New: `components/conflict-dialog.js` | Conflict resolution dialog (3-option modal) |
| New: `components/conflict-dialog.css` | Conflict dialog styles |
| New: `components/version-history.js` | Version history sidebar/modal component |
| New: `components/version-history.css` | Version history styles |
| `main/conversation-manager.js` or new `main/note-versions-manager.js` | SQLite table for version history, CRUD operations |
| `main/preload.js` | IPC bridge for note version operations |
| `main/main.js` | IPC handlers for note version operations |
| `styles/notes.css` | Persistent save status styles, conflict banner styles |
