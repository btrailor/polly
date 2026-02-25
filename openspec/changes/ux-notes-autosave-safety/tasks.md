# Tasks: Notes Auto-Save Safety

Backend (version storage) first, then frontend.

---

## Phase 1: Version History Storage (Backend)

### 1.1 Create note versions SQLite table

- [ ] In `main/conversation-manager.js` (or new `main/note-versions-manager.js`), add `note_versions` table schema
- [ ] Columns: `id`, `note_path`, `content`, `saved_at`, `source`, `content_hash`
- [ ] Index on `(note_path, saved_at DESC)`
- [ ] Run migration on app startup

### 1.2 Implement CRUD operations

- [ ] `saveVersion(notePath, content, source)` — compute hash, skip if matches latest, insert, prune to 10 versions
- [ ] `listVersions(notePath)` — return last 10 versions with metadata (no content, for list display)
- [ ] `getVersion(versionId)` — return full content for a specific version
- [ ] `revertToVersion(notePath, versionId)` — save current as new version (source: 'revert'), return reverted content
- [ ] `cleanup()` — delete versions older than 30 days (run on startup)

### 1.3 IPC bridge

- [ ] Add `note-versions:save`, `note-versions:list`, `note-versions:get`, `note-versions:revert` handlers in `main.js`
- [ ] Expose via `preload.js` as `window.polly.noteVersions.*`

---

## Phase 2: Persistent Save Status

### 2.1 Update save status display

- [ ] In `notes-manager.js`, remove the `setTimeout` auto-hide in `updateSaveStatus()` (`line 2122`)
- [ ] Always display current state: "Saved", "Unsaved", "Saving...", "Save failed", "External change"
- [ ] Add color coding based on state
- [ ] Status element always visible in the editor toolbar/status bar area

### 2.2 Update save status styles

- [ ] In `styles/notes.css`, add persistent status bar styles
- [ ] Muted for "Saved" (not distracting), yellow for "Unsaved" and "External change", red for "Save failed"
- [ ] Include a small dot or icon indicator alongside text

---

## Phase 3: Version History on Save

### 3.1 Wire version saving to auto-save

- [ ] In `saveCurrentNote()` (`notes-manager.js:2103`), after successful save, call `window.polly.noteVersions.save(path, content, 'auto-save')`
- [ ] For manual saves (Cmd+S), use source `'manual-save'`
- [ ] Ensure version save is non-blocking (fire-and-forget, don't await in the critical path)
- [ ] Handle version save failure gracefully (log, don't block the actual save)

---

## Phase 4: Version History UI

### 4.1 Create version history component

- [ ] Create `components/version-history.js`
- [ ] "History" button in note editor toolbar opens history panel
- [ ] List versions: date/time, source badge (auto/manual/revert), first 100 chars preview
- [ ] Click version to preview in read-only mode
- [ ] "Restore this version" button to revert

### 4.2 Create version history styles

- [ ] Create `components/version-history.css`
- [ ] Sidebar panel or modal layout
- [ ] Version list with clear visual hierarchy
- [ ] Source badges with distinct colors
- [ ] Register in `index.html`

### 4.3 Wire revert flow

- [ ] On "Restore": call `window.polly.noteVersions.revert(path, versionId)`
- [ ] Update editor content with reverted content
- [ ] Save the revert as a new version (handled by backend)
- [ ] Show toast: "Reverted to version from {date}"

---

## Phase 5: Conflict Detection

### 5.1 Track external content state

- [ ] In `notes-manager.js`, add `lastKnownExternalContent` property
- [ ] Set on note load and after each successful save
- [ ] In `reloadAfterSync()`, compare fetched content with `lastKnownExternalContent`

### 5.2 Detect conflicts during editing

- [ ] When external content differs and user is editing:
  - Store the external content in `pendingExternalChange`
  - Update save status to "External change"
  - Show a subtle banner in the editor: "This note was changed externally"
- [ ] Do NOT auto-reload or overwrite the user's edits

### 5.3 Create conflict resolution dialog

- [ ] Create `components/conflict-dialog.js`
- [ ] Three-option dialog: "Keep my changes" / "Load external version" / "View diff"
- [ ] On "Keep mine": discard `pendingExternalChange`, save user's version
- [ ] On "Load theirs": replace editor content with external version, save as new version
- [ ] On "View diff": show inline diff, then offer the two choices again

### 5.4 Implement simple diff renderer

- [ ] Implement a minimal line-by-line diff function (no external library)
- [ ] Display additions (green background), deletions (red background), unchanged (grey)
- [ ] Show in a modal overlay on the editor
- [ ] User can choose "Keep mine" or "Take theirs" from the diff view

### 5.5 Trigger conflict resolution

- [ ] When user exits edit mode (or tries to save) with a pending external change:
  - Show the conflict resolution dialog
  - Block the save until resolved
- [ ] After resolution, clear `pendingExternalChange` and resume normal operation

---

## Phase 6: Navigation Guard

### 6.1 Auto-save on navigation

- [ ] When user switches notes or views with unsaved changes, auto-save first
- [ ] If auto-save succeeds: navigate silently
- [ ] If auto-save fails: show ConfirmDialog ("Save failed. Leave anyway and lose changes?")

### 6.2 Auto-save on app quit

- [ ] In `beforeunload` or Electron `before-quit`, trigger note save if unsaved changes exist
- [ ] Ensure save completes before quit (use synchronous IPC if needed)

---

## Completion Criteria

- [ ] Save status is always visible in the editor (never auto-hides)
- [ ] Version history stores last 10 versions per note
- [ ] User can view and revert to any previous version
- [ ] External changes during editing are detected and flagged
- [ ] Conflict resolution dialog offers clear choices (keep mine / take theirs / view diff)
- [ ] Diff view shows additions and deletions clearly
- [ ] Navigation away from unsaved changes triggers auto-save
- [ ] App quit does not lose unsaved changes
- [ ] Version storage is pruned (max 10 per note, 30-day retention)
