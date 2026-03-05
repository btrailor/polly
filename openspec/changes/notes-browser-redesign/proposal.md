# Notes Browser Redesign — Proposal

**Date**: 2026-03-04  
**Status**: ✅ Complete  
**Priority**: P1 — Core navigation and organization broken  
**Scope**: Frontend (primary) + Backend (minor API changes)  
**Depends On**: None  
**Related Specs**: [notes spec](../../specs/notes/spec.md), [domains spec](../../specs/domains/spec.md)

---

## Problem Statement

The Notes browser page has five categories of issues that collectively make it a poor experience for finding, organizing, and managing notes:

### Issue 1: Domain Grouping Uses Folder Structure Instead of Domain Model

When grouping by domain in the notes page, domains are derived from the directory structure where notes are stored (e.g., `00-system`, `01-Sigils`, etc.) rather than the domain model as defined by the user in Polly's domain configuration. This creates several problems:

- **Non-domain folders appear as domains** — `00-system` (used for templates and config) shows up as a "domain" alongside real domains like Sigils, Signals, etc.
- **Project maturity folders appear as domains** — If the user organizes by maturity (Ideas, Active, Archive), these appear as domain groups, creating a confusing mix of organizational axes
- **Domain order is interrupted** — Actual domains are interspersed with system folders, breaking the conceptual flow
- **Uncategorized notes** get grouped under their literal folder name rather than a meaningful "Uncategorized" bucket

The root cause is in `updateBrowseList()` (`notes-manager.js:1062`) which fetches from `/polly/graph/list` — the backend returns `primary_domain` based on the note's file path rather than its frontmatter `domain` field or the domain configuration.

### Issue 2: List View vs Card View Offer Minimal Differentiation

The two view modes (list and card) are nearly identical in practice:

- **List view**: Shows note title, date, type icon, authority badge
- **Card view**: Shows the same plus the associated domain name

Neither view offers compelling advantages:

- Card view doesn't show a content preview, tags, connections, or other metadata that would justify the extra space
- List view doesn't offer density advantages — items are the same height
- Neither view shows backlinks, entity count, or maturity stage
- The toggle between views feels pointless since so little changes

### Issue 3: Filter System Contains Irrelevant Options

The filter panel allows selecting content types like "conversations" which will never appear in the Notes page (conversations live in the Conversations panel). Other filters are either non-functional or poorly scoped:

- **Type filter** includes "conversation," "book," "capture," "code" — none of which appear in the notes browse
- **Maturity filter** (Ideas/Active/Archive) concept exists but doesn't map to actual data
- **Connection status filter** (hub/bridge/isolated) depends on entity graph data that may not be populated
- **Sort options** include "authority" which is an internal metric meaningless to most users
- No ability to filter by **tag**, **date range**, or **creation source** (manual vs AI-created)

### Issue 4: No Note Deletion Capability

Users cannot delete notes from within the Notes browser. To delete a note, a user must:

1. Find the note file in their filesystem (vault folder)
2. Manually delete it
3. Restart Polly or trigger a re-index for the deletion to be reflected

There is no delete button, no right-click context menu with delete, no keyboard shortcut (Delete/Backspace), and no confirmation dialog for deletion.

### Issue 5: Overall Navigation is Weak

- No breadcrumb path showing current location/filters
- No "recent notes" quick access
- No pinned/favorited notes
- Search within notes is basic text matching with no highlighting of results
- No keyboard navigation through the note list (arrow keys, Enter to open)

---

## Goals

1. **Domain grouping uses the user's domain model** — groups come from domain configuration, not filesystem
2. **Meaningful view differentiation** — list view optimized for density/scanning, card view optimized for rich preview
3. **Relevant, useful filters** — remove impossible options, add practical ones (tags, date range, creation source)
4. **In-browser note deletion** — with confirmation dialog and undo capability
5. **Improved navigation** — keyboard shortcuts, recent notes, better search, breadcrumbs

---

## Non-Goals

- Redesigning the note editor itself (separate concern)
- Adding folder/directory management to the notes browser
- Real-time collaboration features
- Mobile version of the notes browser

---

## Success Criteria

1. Domain groups match exactly the user's configured domains (Sigils, Signals, Scrolls, Glyphs, Grids) plus an "Uncategorized" bucket — no system folders
2. Card view shows: title, domain badge, content preview (first 2-3 lines), tags, connection count, created date, creation source icon
3. List view shows: title, domain dot, date, tags (compact) — optimized for maximum notes visible on screen
4. Filter panel contains only: Domain (from config), Tags (populated from actual tags), Sort (Recent, Alphabetical, Most Connected), Date range, Creation source (Manual, AI, Import)
5. Users can delete notes via right-click menu or toolbar button, with undo toast (10 second window)
6. Arrow keys navigate the note list; Enter opens; Delete key triggers delete with confirmation

---

## User Stories

**As a user browsing by domain**, I want to see only my defined domains as groups, not filesystem folders, so the organization matches my mental model.

**As a user scanning many notes**, I want a dense list view that shows titles and key metadata so I can find what I'm looking for quickly.

**As a user exploring notes**, I want a card view with content previews so I can browse and discover without opening each note.

**As a user who created a note by mistake**, I want to delete it from the Notes page directly instead of digging through my filesystem.

**As a user looking for a specific note**, I want to filter by tag, date range, or how the note was created so I can narrow down results efficiently.

---

## Technical Approach

### Phase 1: Fix Domain Grouping

**Backend (`server.py` — `/polly/graph/list` or notes browse endpoint):**

- When returning notes for the browse list, resolve `primary_domain` from:
  1. Note frontmatter `domain` field (highest priority)
  2. Domain configuration mapping (folder → domain)
  3. Fallback: "Uncategorized" (not the raw folder name)
- Add `GET /polly/domains/configured` endpoint that returns the user's domain definitions with display order
- Exclude system folders (`00-system`, `.polly`, etc.) from domain grouping

**Frontend (`notes-manager.js`):**

- When rendering domain groups, use the configured domains list as the group structure
- Sort groups by domain configuration order, not alphabetically
- Add "Uncategorized" group at the end for notes without a domain match
- Domain group headers show: domain name, icon/color, note count

### Phase 2: Redesign View Modes

**List View (density-optimized):**

```
┌──────────────────────────────────────────────────────┐
│ ● Title of Note                    #tag1 #tag2  Mar 4│
│ ● Another Note Title               #research    Mar 3│
│ ● Third Note                       #project     Mar 2│
└──────────────────────────────────────────────────────┘
```

- Single-line per note
- Domain shown as colored dot (left edge)
- Tags shown as compact pills (right-aligned before date)
- No authority badge, no type icon (reduce noise)
- Target: 15-20 visible notes without scrolling

**Card View (preview-optimized):**

```
┌──────────────────────────────────────────────────────┐
│ Title of Note                                        │
│ Domain: Sigils  ·  3 connections  ·  Created via AI  │
│                                                      │
│ First 2-3 lines of note content preview appear here  │
│ giving the user context about what's inside...       │
│                                                      │
│ #tag1  #tag2  #research                     Mar 4    │
└──────────────────────────────────────────────────────┘
```

- Multi-line cards with content preview (first 100-150 chars)
- Domain badge, connection count, creation source indicator
- Tags row at bottom
- Target: 4-6 visible notes without scrolling

### Phase 3: Redesign Filter System

**Remove:**

- Type filter with "conversation," "book," "capture," "code" options
- "Authority" sort option (internal metric, not user-facing)
- Connection status filter (hub/bridge/isolated) — move to Knowledge Graph page

**Keep/Improve:**

- Domain filter → populate from configured domains, not filesystem
- Sort: Recent (default), Alphabetical, Most Connected, Oldest First
- Search: full-text with result highlighting

**Add:**

- **Tag filter**: Multi-select from tags actually present in notes. Show tag count.
- **Date range filter**: "Last 7 days," "Last 30 days," "Last 90 days," "All time," "Custom range"
- **Creation source filter**: "All," "Manual," "AI-created," "Imported"
- **Quick filters bar**: Horizontal pill buttons above the list for most common filters (All, Recent, AI-Created, Untagged)

**Layout:**

- Filters in a collapsible panel above the note list (not a sidebar — maximize horizontal space for notes)
- Active filters shown as dismissible chips below the filter bar
- "Clear all filters" link when any filter is active

### Phase 4: Note Deletion

**Frontend (`notes-manager.js`):**

- Add delete action to:
  1. Right-click context menu on note item
  2. Toolbar button (trash icon) when a note is selected/open
  3. Keyboard shortcut: `Delete` or `Backspace` key with note selected in list
- Show confirmation via existing ConfirmDialog pattern: "Delete '{note title}'? This action can be undone for 10 seconds."
- On confirm: call `DELETE /polly/notes/{path}` → show undo toast
- Undo toast (10 seconds): "Note deleted. [Undo]" — clicking Undo restores the note

**Backend (`server.py` or `settings_api.py`):**

- Add `DELETE /polly/notes/{path}` endpoint:
  1. Move file to a `.polly/trash/` directory (soft delete, not permanent)
  2. Remove from RAG index
  3. Remove from notes browse index
  4. Return `{ success: true, undo_token: "..." }`
- Add `POST /polly/notes/restore` endpoint:
  1. Move file back from `.polly/trash/` to original location
  2. Re-index into RAG and browse index
- Trash cleanup: permanently delete files in `.polly/trash/` older than 30 days (run on app startup)

### Phase 5: Navigation Improvements

- **Keyboard navigation**: Arrow Up/Down to move selection in note list, Enter to open, Escape to deselect
- **Breadcrumbs**: Show current path: "Notes > Sigils > [tag: research]" based on active filters
- **Recent notes**: Show last 5 opened notes at the top of the unfiltered list (or as a quick-access section)
- **Search highlighting**: When filtering by search query, highlight matching text in titles and previews

---

## Risks & Mitigations

**Risk**: Domain resolution from frontmatter may be inconsistent across notes  
**Mitigation**: Fall back gracefully to "Uncategorized." Add a one-time migration to ensure all notes have domain frontmatter.

**Risk**: Note deletion is dangerous — users may accidentally delete important notes  
**Mitigation**: Soft delete to trash with 30-day retention. 10-second undo toast. Confirmation dialog.

**Risk**: Filter redesign may remove options power users depend on  
**Mitigation**: Authority sort and connection status filters move to Knowledge Graph page where they're more relevant, not removed entirely.

**Risk**: Content preview in card view requires reading file content for every note  
**Mitigation**: Preview snippets are truncated server-side and cached. Only fetch for visible cards (virtual scrolling for large collections).

---

## Timeline Estimate

- Phase 1 (Domain grouping fix): 4 hours
- Phase 2 (View mode redesign): 6 hours
- Phase 3 (Filter redesign): 5 hours
- Phase 4 (Note deletion): 4 hours
- Phase 5 (Navigation): 4 hours
- CSS + Polish: 3 hours

**Total: ~26 hours** (3-4 working days)

---

## Related Work

- Notes Manager: `electron-app/src/renderer/notes-manager.js`
- Browse list rendering: `updateBrowseList()`, `renderBrowseItems()` in notes-manager.js
- Domain config: `core/domain_config.py`, `core/domains.py`
- Notes spec: [openspec/specs/notes/spec.md](../../specs/notes/spec.md)
- Graph list endpoint: `interfaces/server.py` — `/polly/graph/list`
- UX empty states: [openspec/changes/ux-empty-states/](../ux-empty-states/) (related component patterns)

---

## Open Questions

1. Should we support multi-domain notes (a note belonging to both "Sigils" and "Signals")? → **Yes, show in both groups. Primary domain determines sort position.**
2. Should deleted notes also be removed from the entity graph? → **Yes, remove entity mentions sourced from the deleted note. Entities themselves persist if mentioned elsewhere.**
3. Should the notes browser support infinite scroll or pagination? → **Infinite scroll with virtual DOM for performance. Load 50 notes initially, fetch more on scroll.**
4. Should we add a "favorites/pinned" feature? → **Defer to future enhancement — focus on filters and search first.**
