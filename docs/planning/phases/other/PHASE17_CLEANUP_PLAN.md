# Phase 17: Cleanup Plan

**Date:** February 4, 2026  
**Purpose:** Remove old UI code as we implement the new ribbon system

---

## Code to Remove

### 1. Premature Panel System (Already Disabled)

**Files to Remove:**
- `electron-app/src/renderer/panel-manager.js`
- `electron-app/src/renderer/components/icon-nav.js`
- `electron-app/src/renderer/components/panel-container.js`
- `electron-app/src/renderer/components/panel-resizer.js`
- `electron-app/src/renderer/panel-configs.js`
- `electron-app/src/renderer/panel-swapper.js`
- `electron-app/src/renderer/panel-renderers.js`
- `electron-app/src/renderer/panel-integration.js`
- `electron-app/src/renderer/styles/panel-system.css`

**Reason:** This was premature - we're building the correct system in VSCode fork first

**When:** After ribbon is working in VSCode fork

---

### 2. Old Sidebar Update Functions

**Files to Check:**
- `electron-app/src/renderer/app.js`
  - `updateLeftSidebar()` - May be replaced by VSCode system
  - `updateRightSidebar()` - May be replaced by VSCode system

**Action:** Review after ribbon integration, remove if replaced

---

### 3. Legacy Sidebar HTML

**File:** `electron-app/src/renderer/index.html`

**Current:**
- Has disabled panel system elements
- Has legacy sidebar content
- May have duplicate structures

**Action:** Clean up after ribbon works

---

## Cleanup Strategy

### Phase 1: During Implementation
- Remove old panel system files immediately
- Clean up disabled code in index.html
- Remove unused imports in app.js

### Phase 2: After Ribbon Works
- Review sidebar update functions
- Remove if replaced by VSCode system
- Clean up any duplicate code

### Phase 3: Final Cleanup
- Remove all commented-out code
- Remove unused CSS
- Remove unused JavaScript files
- Verify no duplicate functionality

---

## Files to Clean Up

### Immediate (Before Implementation)

1. **Remove panel system files:**
   ```bash
   rm electron-app/src/renderer/panel-manager.js
   rm electron-app/src/renderer/components/icon-nav.js
   rm electron-app/src/renderer/components/panel-container.js
   rm electron-app/src/renderer/components/panel-resizer.js
   rm electron-app/src/renderer/panel-configs.js
   rm electron-app/src/renderer/panel-swapper.js
   rm electron-app/src/renderer/panel-renderers.js
   rm electron-app/src/renderer/panel-integration.js
   rm electron-app/src/renderer/styles/panel-system.css
   ```

2. **Clean up index.html:**
   - Remove disabled panel system elements
   - Remove unused script tags
   - Clean up structure

3. **Clean up app.js:**
   - Remove panel system imports
   - Remove disabled initialization code
   - Clean up comments

### After Ribbon Integration

4. **Review and remove:**
   - Old sidebar update functions (if replaced)
   - Duplicate navigation code
   - Unused CSS classes

---

## Verification

After cleanup, verify:
- ✅ No duplicate functionality
- ✅ No unused files
- ✅ No commented-out code
- ✅ Clean imports
- ✅ All functionality works

---

**Status:** Ready to execute cleanup as we implement
