# Notes Auto-Save Safety

**Date:** February 2026
**Scope:** Frontend (primary) + Backend (version history storage)
**Priority:** P2 — data safety; prevents silent data loss in the notes editor

---

## What We're Doing

Adding three safety mechanisms to the notes editor to protect against data loss from auto-save:

1. **Conflict detection** — when an external change to a note is detected while the user is editing (e.g., Obsidian syncs a change), show a dialog offering choices: keep local version, load external version, or view a diff.
2. **Local version history** — store the last 10 versions of each note on save, allowing users to revert to a previous version.
3. **Persistent save status indicator** — replace the auto-hiding "saved" indicator with one that remains visible, so users always know the save state.

## Why

- The notes editor auto-saves after a 2-second delay (`notes-manager.js:39`) with **no undo, no version history, and no conflict detection**.
- The sync polling (`notes-manager.js:432`) checks for external changes every 5 seconds. If the user is editing and an external change arrives, the reload is silently skipped (`notes-manager.js:474-478`). When the user exits edit mode, the reload may **overwrite their external changes** without warning — or conversely, their edits may overwrite the external change.
- The save status indicator at `notes-manager.js:2122` auto-hides after 1.5 seconds: `setTimeout(() => { if (this.saveStatus === 'saved') this.updateSaveStatus(null); }, 1500)`. Users have no persistent indicator of save state.
- There is no mechanism to recover from an accidental edit or bad auto-save — the previous content is gone.

## Scope

- **In scope:** (1) External change detection during editing. (2) Conflict resolution dialog (keep mine / take theirs / view diff). (3) Local version history (last 10 saves per note, stored in SQLite or localStorage). (4) "Revert to version" UI. (5) Persistent save status.
- **Out of scope:** Real-time collaborative editing. Full operational transform (OT/CRDT). Merge conflict resolution (auto-merge). Three-way merge. Cloud sync.

## Backend vs Frontend

- **Frontend:** Conflict detection logic, dialog UI, version history UI, save status.
- **Backend:** Version history storage (either a new SQLite table or filesystem-based). Optional: diff generation endpoint.

## Dependencies

- **`ux-custom-dialogs`:** The conflict resolution dialog uses the same modal pattern as ConfirmDialog (but with 3 options instead of 2).
