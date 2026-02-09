# Phase 17: VSCode Fork Integration Plan

**Status:** 🚧 In Progress  
**Purpose:** Integrate VSCode fork into Polly Electron app and apply UI patterns across all pages  
**Timeline:** 2-3 weeks for POC

---

## Overview

This plan covers:
1. **Integration:** Embed VSCode fork workbench into Polly's Code workspace
2. **Pattern Extraction:** Extract Cursor-like UI patterns from Code workspace
3. **Pattern Application:** Apply patterns to all Polly pages (Dashboard, Knowledge, Notes, etc.)

---

## Phase 1: VSCode Fork Integration

### Step 1: Build VSCode Fork for Integration

**Location:** `~/projects/polly-code`

**Tasks:**
1. Ensure VSCode fork is built and working
2. Verify ribbon is visible and functional
3. Build workbench HTML/JS for embedding
4. Document workbench entry point

**Deliverables:**
- Working VSCode fork build
- Workbench HTML path: `~/projects/polly-code/out/vs/code/electron-browser/workbench/workbench.html`
- Ribbon visible and functional

---

### Step 2: BrowserView Integration

**Files to Modify:**
- `electron-app/src/main/main.js` - Add BrowserView management
- `electron-app/src/renderer/app.js` - Handle Code view loading
- `electron-app/src/renderer/index.html` - Update Code view container

**Implementation:**

1. **Create BrowserView Manager in Main Process:**
   ```javascript
   // electron-app/src/main/main.js
   let vscodeView = null;
   
   function createVSCodeView() {
     vscodeView = new BrowserView({
       webPreferences: {
         nodeIntegration: false,
         contextIsolation: true,
         // VSCode-specific preload if needed
       }
     });
     
     const workbenchPath = path.join(
       process.env.HOME,
       'projects',
       'polly-code',
       'out',
       'vs',
       'code',
       'electron-browser',
       'workbench',
       'workbench.html'
     );
     
     vscodeView.webContents.loadFile(workbenchPath);
     
     return vscodeView;
   }
   ```

2. **Add IPC Handlers:**
   ```javascript
   // Show/hide VSCode view
   ipcMain.handle('show-vscode', () => {
     if (!vscodeView) {
       vscodeView = createVSCodeView();
     }
     mainWindow.setBrowserView(vscodeView);
     // Position and size BrowserView
     const bounds = mainWindow.getBounds();
     vscodeView.setBounds({
       x: 48, // After ribbon
       y: 35, // After titlebar
       width: bounds.width - 48,
       height: bounds.height - 35
     });
   });
   
   ipcMain.handle('hide-vscode', () => {
     if (vscodeView) {
       mainWindow.removeBrowserView(vscodeView);
     }
   });
   ```

3. **Update Renderer to Load VSCode:**
   ```javascript
   // electron-app/src/renderer/app.js
   async function showView(view) {
     // ... existing code ...
     
     if (view === 'code') {
       // Hide placeholder, show VSCode
       const placeholder = document.querySelector('#view-code .empty-state');
       const container = document.querySelector('#vscode-container');
       
       if (placeholder) placeholder.style.display = 'none';
       if (container) container.style.display = 'block';
       
       // Request main process to show VSCode BrowserView
       await PollyBridge.safeCall('showVSCode');
     } else {
       // Hide VSCode when switching away
       await PollyBridge.safeCall('hideVSCode');
     }
   }
   ```

4. **Update Preload:**
   ```javascript
   // electron-app/src/main/preload.js
   showVSCode: () => ipcRenderer.invoke('show-vscode'),
   hideVSCode: () => ipcRenderer.invoke('hide-vscode'),
   ```

**Deliverables:**
- VSCode workbench loads in Code view
- Ribbon visible in VSCode
- Can switch between Polly pages and Code workspace

---

### Step 3: IPC Communication Setup

**Purpose:** Enable communication between Polly and VSCode fork

**IPC Channels:**

1. **Polly → VSCode:**
   - Navigation (switch to different VSCode views)
   - RAG results (send to VSCode)
   - Persona changes
   - Domain context

2. **VSCode → Polly:**
   - File operations
   - Code analysis requests
   - Navigation requests (switch Polly pages)

**Implementation:**

```javascript
// electron-app/src/main/main.js
// Forward messages between Polly and VSCode
ipcMain.handle('vscode-message', (event, message) => {
  if (vscodeView && vscodeView.webContents) {
    vscodeView.webContents.send('polly-message', message);
  }
});

// Listen for messages from VSCode
if (vscodeView) {
  vscodeView.webContents.on('ipc-message', (event, channel, message) => {
    if (channel === 'vscode-to-polly') {
      mainWindow.webContents.send('vscode-message', message);
    }
  });
}
```

**Deliverables:**
- IPC bridge between Polly and VSCode
- Can send messages both ways
- Navigation works between contexts

---

## Phase 2: UI Pattern Extraction

### Step 4: Analyze Code Workspace UI Patterns

**Patterns to Extract:**

1. **Panel System:**
   - Collapsible sidebars
   - Resizable panels
   - Persistent panel states
   - Smooth transitions

2. **Icon Navigation:**
   - Horizontal icon bar (activity bar replacement)
   - Small, sleek icons
   - Active state indicators
   - Hover effects

3. **Layout System:**
   - Three-column layout (left sidebar, main, right sidebar)
   - Responsive to window size
   - Panel collapsing/expanding
   - State persistence

4. **Visual Design:**
   - Dark theme consistency
   - Smooth animations
   - Clean borders and dividers
   - Professional polish

**Documentation:**
- Create `docs/planning/phases/other/PHASE17_UI_PATTERNS.md`
- Document each pattern with examples
- Note CSS classes and structure

**Deliverables:**
- Pattern documentation
- Code examples
- CSS/structure reference

---

### Step 5: Create Reusable UI Component Library

**Components to Create:**

1. **PanelManager:**
   - Manages collapsible panels
   - Handles resizing
   - Persists state

2. **IconNav:**
   - Horizontal icon navigation
   - Active state management
   - Click handlers

3. **LayoutSystem:**
   - Three-column layout
   - Responsive behavior
   - Panel integration

**Location:** `electron-app/src/renderer/components/`

**Files:**
- `panel-manager.js` - Panel management
- `icon-nav.js` - Icon navigation component
- `layout-system.js` - Layout system
- `styles/ui-patterns.css` - Shared styles

**Deliverables:**
- Reusable component library
- Documentation
- Examples

---

## Phase 3: Apply Patterns to All Polly Pages

### Step 6: Update Dashboard

**Changes:**
- Replace current sidebar with panel system
- Add horizontal icon navigation (if needed)
- Apply Cursor-like polish
- Smooth transitions

**Files:**
- `electron-app/src/renderer/app.js` - Dashboard rendering
- `electron-app/src/renderer/index.html` - Dashboard HTML
- `electron-app/src/renderer/styles/dashboard.css` - Dashboard styles

---

### Step 7: Update Knowledge Page

**Changes:**
- Panel system for knowledge graph
- Icon navigation for different views
- Cursor-like polish
- Smooth animations

---

### Step 8: Update Notes Page

**Changes:**
- Panel system for note list and editor
- Icon navigation for note views
- Cursor-like polish
- Better file tree

---

### Step 9: Update Other Pages

**Pages to Update:**
- Patterns
- Learning
- Domains
- Settings

**Approach:**
- Apply panel system
- Add icon navigation where appropriate
- Polish UI to match Code workspace

---

## Phase 4: Ribbon Integration

### Step 10: Connect Polly Ribbon to VSCode Ribbon

**Goal:** When in Code workspace, VSCode ribbon shows Polly page icons

**Implementation:**
- Extend `pollyNavigation.ts` in VSCode fork
- Add Polly page icons to VSCode ribbon
- Handle navigation between Polly pages from VSCode
- Sync active state

**Files:**
- `~/projects/polly-code/src/vs/workbench/browser/parts/ribbon/pollyNavigation.ts`

---

## Testing Checklist

- [ ] VSCode fork loads in Code view
- [ ] Ribbon visible in VSCode
- [ ] Can switch between Polly pages
- [ ] IPC communication works
- [ ] Panel system works in Code workspace
- [ ] Patterns extracted and documented
- [ ] Components created and reusable
- [ ] Dashboard updated with patterns
- [ ] Knowledge page updated
- [ ] Notes page updated
- [ ] Other pages updated
- [ ] UI is consistent across all pages
- [ ] Performance is acceptable
- [ ] No regressions in existing features

---

## Timeline

**Week 1:**
- Days 1-2: BrowserView integration
- Days 3-4: IPC communication setup
- Day 5: Testing and debugging

**Week 2:**
- Days 1-2: Pattern extraction and documentation
- Days 3-4: Component library creation
- Day 5: Apply to Dashboard

**Week 3:**
- Days 1-2: Apply to Knowledge and Notes
- Days 3-4: Apply to other pages
- Day 5: Final polish and testing

---

## Success Criteria

1. ✅ VSCode fork loads seamlessly in Code view
2. ✅ Ribbon visible and functional
3. ✅ Can navigate between Polly pages and Code workspace
4. ✅ UI patterns extracted and documented
5. ✅ Reusable component library created
6. ✅ All Polly pages use consistent UI patterns
7. ✅ UI matches Cursor-like polish
8. ✅ Performance is acceptable
9. ✅ No regressions

---

## Notes

- Start with Code workspace integration
- Extract patterns as we go
- Apply patterns incrementally
- Test after each major change
- Keep existing functionality working
