# Layout Cleanup Plan

## Current Issues

1. **Multiple Right Sidebars Competing**
   - `agents-sidebar` (new, correct)
   - `legacy-right-sidebar` (old conversations sidebar, should be hidden)
   - `notes-right-sidebar` (inside notes view, conflicts with new layout)

2. **Notes View Has Its Own Right Sidebar**
   - Backlinks, Tags, TOC are in a separate right sidebar within the notes view
   - This conflicts with the new layout where chat panel is always on the right
   - These should be moved to the LEFT sidebar when on notes page

3. **Left Sidebar Content Not Updating Properly**
   - Should show page-specific content (ribbon buttons for Notes, VSCode views for Code)
   - Currently showing navigation by default

4. **Layout Structure Issues**
   - Need to verify the three-column layout is correct
   - Main center column should always be split
   - Chat panel should always be visible

## Cleanup Steps

### Step 1: Hide Legacy Right Sidebar ✅
- [x] Hide `legacy-right-sidebar` (conversations sidebar)
- [ ] Remove or comment out its content (keep for reference)

### Step 2: Fix Notes View Layout
- [ ] Remove `notes-right-sidebar` from notes view HTML
- [ ] Move backlinks/tags/TOC content to left sidebar when on notes page
- [ ] Update `renderNotesSidebar()` to include backlinks/tags/TOC panels
- [ ] Update CSS to remove notes-right-sidebar styles

### Step 3: Ensure Left Sidebar Updates
- [ ] Verify `updateLeftSidebar()` is called on all view changes
- [ ] Ensure setup view has proper sidebar content
- [ ] Test all views show correct sidebar content

### Step 4: Verify Main Center Split
- [ ] Ensure chat panel is always visible
- [ ] Verify resize handle works
- [ ] Check that all views render in main-content-area

### Step 5: CSS Cleanup
- [ ] Remove conflicting CSS for old layouts
- [ ] Ensure proper flex layout hierarchy
- [ ] Fix any z-index or positioning issues

## Expected Final Structure

```
┌─────────────────────────────────────────────────────────┐
│ Titlebar                                                 │
├─────────┬───────────────────────────────────────────────┤
│ Ribbon  │                                               │
├─────────┼───────────────────────────────────────────────┤
│ Left    │ ┌──────────────────┬─────────────┬─────────┐ │
│ Sidebar │ │ Main Content      │ Chat Panel  │ Agents  │ │
│         │ │ (varies by page)  │ (always)    │ Sidebar │ │
│         │ │                   │             │         │ │
│         │ │ [Page Content]    │ [Messages] │ [List]  │ │
│         │ └──────────────────┴─────────────┴─────────┘ │
├─────────┴───────────────────────────────────────────────┤
│ Status Bar                                                │
└─────────────────────────────────────────────────────────┘
```

## Notes Page Specific

When on Notes page:
- **Left Sidebar**: Ribbon buttons (New, Templates, Folders, Tags, Search) + Backlinks/Tags/TOC panels
- **Main Content**: Note editor
- **Right Sub-column**: Chat panel (always visible)
- **Right Sidebar**: Agents sidebar
