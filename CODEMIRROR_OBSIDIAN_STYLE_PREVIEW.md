# CodeMirror 6 - Obsidian-Style Live Preview Enhancement

**Date:** 2026-02-01  
**Status:** In Progress - Phase 1  
**Goal:** Make Polly's markdown editor experience match Obsidian's polish

---

## Overview

Enhance Polly's CodeMirror 6 live preview to match Obsidian's editing experience:
- When cursor is on formatted text, show markers in gray but keep formatting applied
- Seamless transition between editing and reading modes
- No jarring size/style changes when clicking into headings

---

## Implementation Phases

### ✅ Phase 0: Markdown Formatting Shortcuts (COMPLETED)
**What we built:**
- Cmd+B: Toggle bold (`**text**`)
- Cmd+I: Toggle italic (`*text*`)
- Cmd+E: Toggle inline code (`` `text` ``)
- Cmd+K: Insert wiki link (`[[text]]`)

**Key learnings:**
- Removed complex syntax tree detection - kept it simple
- Selection-based: wrap/unwrap based on what's selected
- No cursor-only auto-detection (too complex, fragile with nested formats)
- Works reliably across all contexts

**Files modified:**
- `/Users/brettgershon/polly/electron-app/src/renderer/markdown-editor-cm6.js`
  - Simplified `toggleMarkdownFormat()` method (lines 378-438)
  - Custom keybindings placed BEFORE defaults to override (lines 92-136)

---

### 🔄 Phase 1: Obsidian-Style Headings (IN PROGRESS)

#### Current Behavior (Before)
```
Cursor on heading line:
"## My Heading"          (plain text, normal size)

Cursor on different line:
"My Heading"             (large text, ## hidden)
```

#### Target Behavior (Obsidian-like)
```
Cursor on heading line:
"##" (gray) + "My Heading"   (large, bold)

Cursor on different line:  
"My Heading"                 (large, bold, ## hidden)
```

#### Changes Required

**File:** `/Users/brettgershon/polly/electron-app/src/renderer/live-preview-extension.js`

**Change 1: Remove blanket cursor line skip**
- **Lines 215-218:** Delete the early return that skips all decorations on cursor line
- Currently: `if (nodeLine === cursorLine) { return }`
- New: Remove this block entirely

**Change 2: Conditional heading marker styling**
- **Lines 353-395:** Heading decoration logic
- Add check: `const isCursorOnHeading = (nodeLine === cursorLine)`
- If cursor on heading: Style markers gray instead of hiding
- If cursor elsewhere: Hide markers (current behavior)
- Always apply large text styling regardless

**New Logic:**
```javascript
const isCursorOnHeading = (nodeLine === cursorLine)

if (isCursorOnHeading) {
  // Style markers as muted/gray
  builder.add(nodeFrom, hashEnd, Decoration.mark({
    attributes: {
      style: "color: var(--text-secondary, #808080); opacity: 0.6; font-weight: normal;"
    }
  }))
} else {
  // Hide markers (original behavior)
  builder.add(nodeFrom, hashEnd, Decoration.replace({ widget: new HiddenWidget() }))
}

// Always style heading text large (unchanged)
builder.add(hashEnd, nodeTo, Decoration.mark({
  attributes: {
    style: `font-size: ${fontSizes[hashCount]}; font-weight: bold;`
  }
}))
```

#### Testing Checklist
- [ ] Click into `## Heading` - markers visible in gray, text large
- [ ] Test all heading levels `#` through `######`
- [ ] Move cursor off heading - markers disappear
- [ ] Multiple headings - only active one shows markers
- [ ] Cursor at line start (before `#`)
- [ ] Cursor right after `##` (on space)
- [ ] Cursor at end of heading text
- [ ] Selection spanning multiple words

---

### 📋 Phase 2: Extend to All Formats (PLANNED)

After Phase 1 success, apply same pattern to:
- **Bold** `**text**` - show `**` gray when cursor inside
- **Italic** `*text*` - show `*` gray when cursor inside
- **Code** `` `code` `` - show `` ` `` gray when cursor inside
- **Strikethrough** `~~text~~` - show `~~` gray when cursor inside
- **Wiki links** `[[note]]` - show `[[]]` gray when cursor inside

Each follows the same pattern:
1. Check if cursor is on the element's line
2. If yes: style markers gray/muted
3. If no: hide markers
4. Always apply content styling

---

## Design Decisions

### Granularity: Line-based vs Node-based
**Decision:** Line-based (show markers for all formats on cursor's line)

**Rationale:**
- Simpler to implement and maintain
- Consistent with heading behavior
- Can refine to node-based later if needed

**Alternative considered:** Only show markers for the specific format cursor is inside
- More precise but significantly more complex
- Requires cursor position checking within node bounds
- Can add in future if users request it

### Marker Color/Opacity
**Decision:** `var(--text-secondary, #808080)` with `opacity: 0.6`

**Rationale:**
- Matches Polly's existing secondary text color (defined in `styles/main.css`)
- 60% opacity = subtle but visible
- Consistent with app's design language

**Colors available:**
- `--text-primary: #e0e0e0` (main text)
- `--text-secondary: #808080` (muted text) ← using this
- `--text-muted: #606060` (darker muted)

### Debug Logging
**Decision:** Keep console.log statements during development, remove when stable

**Current logging:**
- `[LivePreview]` prefix for all live preview logs
- `[Format]` prefix for formatting shortcuts (removed in Phase 0)
- Helps debug cursor position and decoration application

---

## Technical Notes

### CodeMirror 6 Decoration System

**Two decoration types used:**

1. **`Decoration.replace()`** - Replaces content with widget
   - Used to hide markers on non-cursor lines
   - `new HiddenWidget()` - renders as empty text node

2. **`Decoration.mark()`** - Applies styling to content
   - Used to style visible markers on cursor line
   - Used to style heading/bold/italic text

**Key insight:** Can't hide and style the same range simultaneously
- Must choose: hide OR style, not both
- Our approach: conditionally apply one or the other based on cursor position

### Cursor Position Detection

**Current approach:**
```javascript
const cursorLine = view.state.doc.lineAt(view.state.selection.main.head).number
const nodeLine = view.state.doc.lineAt(nodeFrom).number
const isCursorOnLine = (nodeLine === cursorLine)
```

**Why line-based:**
- Simple, reliable
- Matches Obsidian's behavior for headings (entire line treated as unit)
- Avoids edge cases with cursor at exact marker boundaries

**Alternative (node-based):**
```javascript
const cursorPos = view.state.selection.main.head
const isCursorInside = (cursorPos >= nodeFrom && cursorPos <= nodeTo)
```
- More granular but more complex
- Could add later for inline formats if needed

---

## Files Involved

### Primary Files
1. **`/Users/brettgershon/polly/electron-app/src/renderer/live-preview-extension.js`** (441 lines)
   - Live preview ViewPlugin
   - Handles decoration building
   - Changes: Lines 215-218 (remove skip), Lines 353-395 (heading logic)

2. **`/Users/brettgershon/polly/electron-app/src/renderer/markdown-editor-cm6.js`** (550+ lines)
   - Main CodeMirror 6 editor wrapper
   - Keyboard shortcuts
   - Phase 0 changes completed here

### Supporting Files
3. **`/Users/brettgershon/polly/electron-app/build-cm6.js`**
   - Bundles CM6 modules using esbuild
   - Run after changes: `node build-cm6.js`

4. **`/Users/brettgershon/polly/electron-app/src/renderer/styles/main.css`**
   - CSS variables (colors, spacing)
   - `--text-secondary` used for marker colors

### Generated File
5. **`/Users/brettgershon/polly/electron-app/src/renderer/markdown-editor-cm6.bundle.js`** (~1.1MB)
   - Auto-generated by build-cm6.js
   - Don't edit directly

---

## Build Process

```bash
# After making changes to source files:
cd /Users/brettgershon/polly/electron-app
node build-cm6.js

# Start app
npm start

# Or rebuild and start in one command:
npm start  # (package.json has prebuild script)
```

---

## Known Issues

### IndexSizeError on Hidden Markers (Non-critical)
**Error:** `Failed to execute 'setEnd' on 'Range': The offset 2 is larger than the node's length (0)`

**Cause:** HiddenWidget has 0 length, clicking where marker used to be confuses DOM range

**Impact:** Console error only, doesn't break functionality

**Future fix:** Use CSS `display: none` instead of HiddenWidget, or handle clicks specially

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Headings show gray `##` markers when cursor on line
- [ ] Heading text stays large/bold when cursor on line
- [ ] Markers disappear when cursor moves to different line
- [ ] All heading levels (1-6) work correctly
- [ ] No visual glitches or jarring transitions
- [ ] Code is clean and maintainable

### Phase 2 Complete When:
- [ ] All inline formats show gray markers on cursor line
- [ ] Bold, italic, code, strikethrough work consistently
- [ ] Wiki links show gray `[[]]` on cursor line
- [ ] Experience matches Obsidian's polish
- [ ] Debug logging removed
- [ ] Documentation updated

---

## Future Enhancements (Post-Phase 2)

### Potential Improvements
1. **Granular cursor detection** - Only show markers for exact format cursor is inside
2. **Selection-aware markers** - Hide markers even on cursor line if text is selected
3. **Nested format support** - Handle `**bold with *italic* inside**`
4. **Custom marker styling** - User preferences for marker color/opacity
5. **Animation transitions** - Smooth fade in/out of markers
6. **Mobile/touch support** - Adapt behavior for touch devices

### Integration Opportunities
1. **Command palette** - Add "Toggle live preview" command
2. **Settings panel** - User preferences for live preview behavior
3. **Keyboard shortcuts** - Toggle live preview on/off
4. **Status bar** - Indicator showing live preview state

---

## References

### Obsidian's Approach
- Markers visible but muted when editing
- Content maintains formatting even when showing markers
- Seamless transition feels like "editing the rendered view"
- No sudden size changes when clicking into text

### CodeMirror 6 Documentation
- [Decorations](https://codemirror.net/docs/ref/#view.Decoration)
- [View Plugins](https://codemirror.net/docs/ref/#view.ViewPlugin)
- [Syntax Tree](https://codemirror.net/docs/ref/#language.syntaxTree)

---

## Session Notes

### 2026-02-01: Phase 0 & Phase 1 Planning
- Completed markdown formatting shortcuts (Cmd+B/I/E/K)
- Learned: Keep implementations simple, avoid over-engineering
- Fixed keybinding conflict: Custom bindings must come before defaults
- Planned Obsidian-style heading enhancement
- Decided on line-based granularity for Phase 1
- Ready to implement heading marker styling

---

## Next Steps

1. ✅ Document the plan (this file)
2. ⏳ Implement Phase 1: Heading marker styling
3. ⏳ Test Phase 1 thoroughly
4. ⏳ Get user feedback
5. ⏳ Implement Phase 2: All other formats
6. ⏳ Clean up debug logging
7. ⏳ Update user-facing documentation

---

*This document tracks the evolution of Polly's markdown editing experience toward Obsidian-level polish.*
