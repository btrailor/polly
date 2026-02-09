# Phase 17: Pre-Migration Cleanup Audit

**Date:** February 4, 2026  
**Purpose:** Clean up codebase before migration to VSCode fork  
**Status:** In Progress

---

## 1. Backup Files to Remove

### Identified Backup Files:
- `electron-app/src/renderer/app.js.backup` - Old backup, not needed
- `electron-app/src/renderer/app.js.backup-phase0.5` - Phase 0.5 backup, not needed
- `electron-app/src/renderer/index.html.backup` - Old backup, not needed
- `electron-app/src/renderer/index.html.backup-phase0.5` - Phase 0.5 backup, not needed
- `electron-app/src/renderer/styles/main.css.backup` - CSS backup, not needed

**Action:** Delete all backup files

---

## 2. Code Cleanup - app.js (14,417 lines)

### Issues Identified:
- **Very large file** - Should be broken into modules
- **Debug code** - Multiple `console.log('[Init DEBUG]...')` statements
- **TODO comments** - Multiple TODOs that need review
- **Legacy code** - Old migration code, deprecated functions
- **Duplicate functions** - Need to identify duplicates

### Functions to Audit:
- `showToast()` - Simple utility, keep
- `PollyBridge` - IPC bridge, keep but clean up
- `safeFetch()` - HTTP wrapper, keep
- `withErrorBoundary()` - Error handling, keep
- `checkPollyInitStatus()` - Initialization, review
- `startPollyStatusPolling()` - Status polling, review
- `initialize()` - Main init, very large, needs refactoring
- `showView()` - View switching, keep but clean
- `updateLeftSidebar()` - Sidebar management, review
- `updateRightSidebar()` - Sidebar management, review
- `loadVSCodeWorkbench()` - VSCode integration, REMOVE (not needed in migration)
- `hideVSCodeWorkbench()` - VSCode integration, REMOVE (not needed in migration)

### Debug Code to Remove:
- Line 328-329: Chat input debug logs
- Line 363-370: DOM element debug logs
- Multiple `console.log('[Init DEBUG]...')` statements

### Legacy Code to Remove:
- `needsMigration` flag and related migration code (if migration complete)
- Old conversation history migration code
- Deprecated UI state management

---

## 3. CSS Files Audit

### CSS Files to Review:
1. `chat-sidebar.css` - Chat sidebar styles - **REMOVE** (will rebuild in VSCode)
2. `chat.css` - Chat styles - **REMOVE** (will rebuild in VSCode)
3. `floating-chat.css` - Floating chat - **REMOVE** (will rebuild in VSCode)
4. `curriculum.css` - Learning/curriculum styles - **REVIEW** (may need some patterns)
5. `glitch-effects.css` - Glitch animation effects - **REVIEW** (may want to preserve)
6. `layout.css` - Main layout - **REMOVE** (VSCode has its own layout)
7. `main.css` - Main styles - **REVIEW** (extract only essential patterns)
8. `main.css.backup` - **REMOVE** (backup file)
9. `notes.css` - Notes styles - **REVIEW** (may need some patterns)
10. `obsidian-theme.css` - Obsidian theme - **REVIEW** (may want to preserve)
11. `persona-switch-dialog.css` - Persona dialog - **REVIEW** (may need patterns)
12. `persona-ui.css` - Persona UI - **REVIEW** (may need patterns)
13. `ribbon.css` - Ribbon navigation - **REMOVE** (using activity bar instead)
14. `template-gallery.css` - Template gallery - **REVIEW** (may need patterns)
15. `three-column.css` - Three column layout - **REMOVE** (VSCode has its own layout)

### CSS Patterns to Preserve (if any):
- Color scheme (Polly orange: #f0903b)
- Glitch effects (if desired)
- Obsidian theme colors (if desired)

---

## 4. Component Files Audit

### Components:
1. `mental-models-editor.js` - Mental models editor - **KEEP** (will port to VSCode)
2. `package-approval-dialog.js` - Package approval - **REVIEW** (may not be needed)
3. `preview-modal.js` - Preview modal - **REVIEW** (may use VSCode native)
4. `question-form.js` - Question form - **REVIEW** (may use VSCode native)
5. `template-gallery.js` - Template gallery - **KEEP** (will port to VSCode)

---

## 5. Feature Audit

### Features to Review:

#### GitHub Integration
- **Current:** OAuth flow, token storage, backend connection
- **Decision:** ENHANCE - Integrate with VSCode native Git/GitHub, add Polly RAG features
- **Action:** Remove old GitHub OAuth UI, keep RAG indexing logic

#### Codebase Indexing
- **Current:** Manual codebase path selection, indexing
- **Decision:** ENHANCE - Use VSCode workspace awareness
- **Action:** Remove manual path selection UI, use VSCode workspace

#### Calendar/Mail/Projects
- **Current:** Placeholder views
- **Decision:** REMOVE - Not implemented, remove placeholders

#### Search
- **Current:** Polly search functionality
- **Decision:** REVIEW - VSCode has search, but Polly search may add RAG value
- **Action:** Keep RAG search, remove if redundant with VSCode search

---

## 6. Orphaned Code to Remove

### Identified Orphaned Code:
1. VSCode BrowserView integration code (loadVSCodeWorkbench, hideVSCodeWorkbench) - **REMOVE**
2. Old panel system files (already deleted, but check for references)
3. Backup file references
4. Deprecated migration code (if migration complete)
5. Debug console.log statements
6. Unused utility functions

---

## 7. Cleanup Actions

### Immediate Actions:
1. ✅ Delete backup files
2. ⏳ Remove debug code
3. ⏳ Remove VSCode BrowserView integration code
4. ⏳ Remove placeholder views (Calendar, Mail, Projects)
5. ⏳ Clean up TODO comments
6. ⏳ Remove unused CSS files
7. ⏳ Document what each remaining file does

### Before Migration:
1. Create feature inventory
2. Create UI component inventory
3. Document API dependencies
4. Create migration checklist

---

## Next Steps

1. Execute cleanup actions
2. Create feature audit document
3. Create UI placement specification
4. Begin migration
