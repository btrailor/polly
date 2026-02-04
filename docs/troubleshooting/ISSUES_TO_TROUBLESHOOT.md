# Issues to Troubleshoot

**Project:** Polly - Edge-Native Personal AI System  
**Purpose:** Track known issues that have been documented but not yet resolved  
**Last Updated:** January 31, 2026 (Added Issue #4: Conversation context reload)

---

## Active Issues

### 1. Titlebar Button Sliding Animation
**Status:** 🟡 Documented - Not Resolved  
**Priority:** Medium (UX Enhancement)  
**Detailed Documentation:** [TITLEBAR_ANIMATION_ISSUE.md](./TITLEBAR_ANIMATION_ISSUE.md)

**Quick Summary:**
- **Problem**: Titlebar toggle buttons become unclickable when animated to slide with sidebar edges
- **Current Workaround**: Buttons remain stationary in titlebar, only icon direction changes
- **Root Cause**: Location-specific mouse hit-testing blocked in coordinates `left: 80-328px, top: 0-40px`
- **Suspected Culprits**: 
  - macOS traffic lights protected zone extending horizontally
  - Electron webkit-app-region compositor behavior
  - Grid layout interference with titlebar
  
**Impact:**
- ✅ Functionality: Buttons work perfectly in current implementation
- ❌ UX: No visual connection between button position and sidebar edge
- ✅ Workaround: Keyboard shortcuts (Cmd+B, Cmd+/) work flawlessly

**Next Steps When Resuming:**
1. Try moving buttons to ribbon (Option 1 - highest feasibility)
2. Try animating container instead of buttons (Option 4 - novel approach)
3. Research Electron window configuration options
4. Test on Windows/Linux to determine if issue is macOS-specific

**Files Involved:**
- `/Users/brettgershon/polly/electron-app/src/renderer/index.html` (lines 16-41)
- `/Users/brettgershon/polly/electron-app/src/renderer/styles/main.css` (lines 96-203)
- `/Users/brettgershon/polly/electron-app/src/renderer/app.js` (lines 937-1050)
- `/Users/brettgershon/polly/electron-app/src/main/main.js` (trafficLightPosition config)

---

### 2. Unused "Conversations" UI Element in Right Sidebar
**Status:** 🟡 Documented - Needs Cleanup  
**Priority:** Low (UI Cleanup)  
**Detailed Documentation:** This document (inline)

**Quick Summary:**
- **Problem**: Right sidebar has unused "conversations" element with clickable dropdown arrow that does nothing
- **Current Workaround**: Element exists but has no functionality
- **Root Cause**: Old UI element from previous design, replaced by lower sidebar conversation list
- **Suspected Culprits**: Leftover HTML/CSS from earlier iteration

**Impact:**
- ✅ Functionality: No impact (element does nothing)
- ❌ UX: Confusing non-functional UI element
- ❌ Polish: Looks unfinished

**Next Steps When Resuming:**
1. Locate element in index.html (search for "conversations" in right sidebar section)
2. Remove HTML element
3. Remove associated CSS
4. Remove any JavaScript event listeners
5. Test that removal doesn't break anything

**Files Involved:**
- `/Users/brettgershon/polly/electron-app/src/renderer/index.html` (right sidebar section)
- `/Users/brettgershon/polly/electron-app/src/renderer/styles/three-column.css` (right sidebar styles)
- `/Users/brettgershon/polly/electron-app/src/renderer/app.js` (event listeners, if any)

---

### 3. Settings UI Update Incomplete
**Status:** 🟡 Documented - Needs Completion  
**Priority:** Low (Polish)  
**Detailed Documentation:** This document (inline)

**Quick Summary:**
- **Problem**: Settings page UI update mentioned in brain dump but incomplete
- **Current Workaround**: Settings page functional but may need visual updates
- **Root Cause**: Settings page built before Phase 0.5 Obsidian-inspired redesign
- **Suspected Culprits**: Inconsistent styling between old (Phases 1-5) and new (Phase 0.5) UI

**Impact:**
- ✅ Functionality: Settings work correctly
- ⚠️ UX: Visual inconsistency with newer pages
- ❌ Polish: Doesn't match Obsidian-inspired aesthetic

**Next Steps When Resuming:**
1. Audit settings page styling against Phase 0.5 design system
2. Update settings tabs to match navigation ribbon style
3. Standardize form controls (inputs, buttons, dropdowns)
4. Ensure dark theme consistency
5. Test all settings interactions

**Files Involved:**
- `/Users/brettgershon/polly/electron-app/src/renderer/index.html` (settings section)
- `/Users/brettgershon/polly/electron-app/src/renderer/styles/main.css` (settings styles)
- `/Users/brettgershon/polly/electron-app/src/renderer/app.js` (settings logic)

**Related Documents:**
- `PHASE0.5_COMPLETE.md` - Design system to follow
- `PHASE_0.5_TO_0.7_ROADMAP.md` - UI polish sprint planning

---

### 4. Conversation Context Reload After Startup
**Status:** ✅ Fixed (January 31, 2026)  
**Priority:** High (User Experience - Critical)  
**Detailed Documentation:** [CONVERSATION_RELOAD_FIX.md](./CONVERSATION_RELOAD_FIX.md)

**Quick Summary:**
- **Problem**: Conversation reloads 2-5 seconds after Polly starts, causing jarring UI flash
- **Root Cause**: `updateRightSidebar()` replacing entire sidebar HTML when data loads complete
- **Solution**: Prevent HTML replacement when active conversation exists

**Implementation:**
- Modified `updateRightSidebar()` to check for active conversations before replacing HTML
- Added guards in `loadDashboardData()` and `loadKnowledgeData()`
- Simple 20-line fix, no complex state management needed

**User Experience:**
- Before: Messages flash (disappear/reappear) 2-5 seconds after startup
- After: Conversation remains stable, no visual disruption

**Testing Status:**
- ✅ Verified working - No more reload after 5-second delay
- ✅ Messages stay visible and stable
- ✅ Works on all views (dashboard, knowledge, chat)

**Files Modified:**
- `electron-app/src/renderer/app.js` (lines 2229-2248, 3560-3565, 3653-3662)

**Related Documents:**
- `CONVERSATION_RELOAD_FIX.md` - Debugging process and detailed explanation

---

## Resolved Issues

### Issue #4: Conversation Context Reload After Startup
**Resolved:** January 31, 2026  
**Original Priority:** High (User Experience - Critical)  

**Problem:** Conversation reloaded 2-5 seconds after Polly started, causing all messages to flash (disappear and reappear).

**Solution:** Modified `updateRightSidebar()` to prevent HTML replacement when an active conversation exists. Simple 20-line fix that checks for `currentConversationId` before replacing sidebar content.

**Documentation:** [CONVERSATION_RELOAD_FIX.md](./CONVERSATION_RELOAD_FIX.md)

---

## Issue Template

When adding new issues to this document, use this template:

```markdown
### [Issue Number]. [Brief Title]
**Status:** 🔴 Critical / 🟡 Documented / 🟢 Resolved  
**Priority:** High / Medium / Low  
**Detailed Documentation:** [ISSUE_NAME.md](./ISSUE_NAME.md) *(if separate doc exists)*

**Quick Summary:**
- **Problem**: [One sentence description]
- **Current Workaround**: [How we're handling it now]
- **Root Cause**: [What we think is causing it]
- **Suspected Culprits**: [Bullet list of possibilities]

**Impact:**
- [How it affects users/functionality]
- [What works vs what doesn't]

**Next Steps When Resuming:**
1. [First thing to try]
2. [Second approach]
3. [Research needed]

**Files Involved:**
- `path/to/file.ext` (line numbers if applicable)
```

---

## Issue Categories

### UI/UX Issues
- [#1 Titlebar Button Sliding Animation](#1-titlebar-button-sliding-animation)

### Backend/Server Issues
*None currently*

### Performance Issues
*None currently*

### Build/Configuration Issues
*None currently*

### Third-Party Integration Issues
*None currently*

---

## Investigation Guidelines

When investigating issues from this list:

1. **Read the detailed documentation first** - Don't start from scratch
2. **Test on multiple platforms** - Some issues may be OS-specific
3. **Document new findings** - Update both this file and detailed docs
4. **Try suggested approaches in order** - They're ranked by feasibility
5. **Create test cases** - Build minimal reproducible examples
6. **Check Electron/framework updates** - Issues may be fixed upstream
7. **Ask the community** - Search GitHub issues for similar problems

---

## Notes

- This document tracks **documented issues that we've moved on from**, not active bugs being worked on
- Each issue should have a clear workaround or acceptable current state
- Issues are moved to "Resolved" when permanently fixed
- Keep this index concise - detailed analysis goes in separate docs
- Update "Last Updated" date when modifying this file

---

**Document Created:** January 26, 2026  
**Status:** Living Document - Update as issues are discovered/resolved
