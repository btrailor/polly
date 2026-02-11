# Tasks: Cursor UI Pattern Migration

## Implementation Order

Tasks are ordered so layout foundation is built first, then components, then integration.

## Phase 1: Layout Foundation

### Task 1.1: Create Main Center Column Split Structure
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`

- [ ] Add HTML structure for split center column (main content area + resize handle + chat panel)
- [ ] Add CSS for flex layout with resize handle
- [ ] Main content area will contain page-specific content (Code editor, Notes editor, etc.)
- [ ] Chat panel always visible on right side of split
- [ ] Add visual feedback for resize handle (hover, active states)

**Estimated time:** 4-6 hours

### Task 1.2: Implement Resize Handle Component
**Files:** `electron-app/src/renderer/app.js` (or new `layout.js`)

- [ ] Create resize handle event handlers (mousedown, mousemove, mouseup)
- [ ] Calculate and apply new widths on drag
- [ ] Enforce minimum widths (300px main content, 300px chat)
- [ ] Save split ratio to localStorage
- [ ] Restore split ratio on page load

**Estimated time:** 3-4 hours

### Task 1.3: Create Status Bar Component
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/app.js`

- [ ] Add status bar HTML structure at bottom of app
- [ ] Style status bar (Cursor-like appearance)
- [ ] Add server status indicator (connect to existing server status logic)
- [ ] Add connection status indicator
- [ ] Add editor info (cursor position, encoding, line endings) - show when in editor context
- [ ] Make status bar persistent across all views

**Estimated time:** 2-3 hours

## Phase 2: Left Sidebar (Collapsible, Page-Specific)

### Task 2.1: Update Left Sidebar Structure
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/app.js`

- [ ] Ensure left sidebar is separate from main center column
- [ ] Add collapse/expand functionality (Cmd+B)
- [ ] Add page detection logic (which page is active)
- [ ] Create sidebar content router (shows appropriate content per page)
- [ ] Persist collapsed state in localStorage

**Estimated time:** 2-3 hours

### Task 2.2: Implement Code Page Left Sidebar
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Create VSCode-like feature view buttons (Files, Search, Source Control, etc.)
- [ ] Implement view switching
- [ ] Add Files view (file tree - placeholder for Phase 17)
- [ ] Add Search view (search interface - placeholder for Phase 17)
- [ ] Add Source Control view (git status - placeholder for Phase 17)
- [ ] Style to match VSCode appearance

**Estimated time:** 4-5 hours

### Task 2.3: Implement Notes Page Left Sidebar
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Create ribbon buttons at top (New Note, Templates, Folders, Tags, Search)
- [ ] Implement button actions
- [ ] Add notes navigation below ribbon
- [ ] Style ribbon buttons
- [ ] Integrate with existing notes functionality

**Estimated time:** 3-4 hours

### Task 2.4: Implement Chat Page Left Sidebar with Thread List
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Move conversation list to left sidebar (or create new structure)
- [ ] Improve thread list: clear titles, optional preview/snippet
- [ ] Add right-click context menu (rename, delete, star, category)
- [ ] Add keyboard navigation (arrow keys, Enter to open)
- [ ] Add conversation search/filter
- [ ] Add new conversation button
- [ ] Style thread list (first-class appearance, active thread highlighted)
- [ ] Integrate with existing conversation management

**Estimated time:** 4-5 hours

### Task 2.5: Implement Other Pages Left Sidebars
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Create context menus for remaining pages (Knowledge, Patterns, Curricula, Settings)
- [ ] Add appropriate navigation/views per page
- [ ] Style consistently

**Estimated time:** 3-4 hours

## Phase 3: Main Content Area (Left Sub-Column of Split)

### Task 3.1: Implement Main Content Area Router
**Files:** `electron-app/src/renderer/app.js`, `electron-app/src/renderer/index.html`

- [ ] Create main content area container (left side of split)
- [ ] Add page-specific content routing
- [ ] Code page: Monaco editor setup (placeholder for Phase 17)
- [ ] Notes page: Note editor
- [ ] Chat page: Chat messages (if applicable)
- [ ] Other pages: Page-specific content

**Estimated time:** 3-4 hours

## Phase 4: Chat Panel (Right Sub-Column of Split)

### Task 4.1: Create Chat Panel Structure
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`

- [ ] Create chat panel container in right sub-column
- [ ] Add chat tabs area at top
- [ ] Add messages area in middle
- [ ] Add input area at bottom with controls
- [ ] Style chat panel

**Estimated time:** 2-3 hours

### Task 4.2: Implement Chat Tabs
**Files:** `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [x] Create chat tab system (multiple chats per agent)
- [x] Add tab creation (new chat button)
- [x] Add tab switching
- [x] Add tab closing
- [x] Persist active tabs per agent (sessionStorage)
- [x] Style tabs (Cursor-like appearance)

**Estimated time:** 4-5 hours

### Task 4.3: Update Chat Input Area
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Add persona selector to chat input area
- [ ] Add model selector to chat input area
- [ ] Remove explicit mode selector (or hide it)
- [ ] Style selectors as chips or compact dropdowns
- [ ] Position controls above input
- [ ] Integrate with existing persona/model selection logic

**Estimated time:** 3-4 hours

### Task 4.4: Implement Context Pills
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Create context pills component (display pills above input)
- [ ] Add "@" mention handler in input (detect @domain, @note, @folder)
- [ ] Add context picker button (opens context selection UI)
- [ ] Implement pill add/remove functionality
- [ ] Style context pills (Cursor-like appearance)
- [ ] Send context with messages to backend
- [ ] Basic version: @domain, @note, @folder
- [ ] Extended version (Phase 17): @file, @selection, @symbol

**Estimated time:** 4-5 hours

### Task 4.5: Integrate Chat Panel with Existing Chat System
**Files:** `electron-app/src/renderer/app.js`

- [ ] Connect chat panel to existing conversation system
- [ ] Ensure messages render correctly
- [ ] Ensure input sends messages correctly
- [ ] Ensure persona/model selection works
- [ ] Test chat functionality end-to-end

**Estimated time:** 3-4 hours

## Phase 5: Agents Sidebar

### Task 5.1: Create Agents Sidebar Structure
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`

- [x] Create agents sidebar container (right edge)
- [x] Add "New Agent" button
- [x] Add agents list container
- [x] Add collapse/expand functionality
- [x] Style agents sidebar

**Estimated time:** 2-3 hours

### Task 5.2: Implement Agent Selection
**Files:** `electron-app/src/renderer/app.js`

- [x] Create agent list rendering
- [x] Implement agent switching (updates chat panel)
- [x] Add active agent highlighting
- [x] Persist active agent (sessionStorage)
- [x] Load agent's chats when switching

**Estimated time:** 3-4 hours

### Task 5.3: Integrate Agents with Chat System
**Files:** `electron-app/src/renderer/app.js`

- [x] Connect agents to chat tabs
- [x] Ensure each agent has independent chat tabs
- [x] Ensure agent state persists across sessions
- [x] Test agent switching and chat isolation

**Estimated time:** 2-3 hours

## Phase 6: Floating Chat Overhaul

### Task 6.1: Update Floating Chat Structure
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`

- [ ] Update floating chat HTML to match new chat panel design
- [ ] Add persona selector
- [ ] Add model selector
- [ ] Remove explicit mode selector
- [ ] Style to match main chat panel

**Estimated time:** 2-3 hours

### Task 6.2: Sync Floating Chat with Main Chat
**Files:** `electron-app/src/renderer/app.js`

- [ ] Ensure persona/model selections sync between floating and main chat
- [ ] Ensure messages sync (if applicable)
- [ ] Test floating chat functionality

**Estimated time:** 2-3 hours

## Phase 7: Persona/Mode Evolution

### Task 7.1: Remove Explicit Mode Selector from UI
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/app.js`, `electron-app/src/renderer/styles/main.css`

- [ ] Remove mode selector from chat input area
- [ ] Remove mode selector from floating chat
- [ ] Update persona change handlers to not require mode selection
- [ ] Ensure backend still receives mode (use default or detect from context)

**Estimated time:** 2-3 hours

### Task 7.2: Update Persona Activation Logic
**Files:** `electron-app/src/renderer/app.js`

- [ ] Modify persona activation to not require explicit mode
- [ ] Ensure all persona capabilities are available when persona is active
- [ ] Update UI to show available actions contextually (if needed)
- [ ] Test persona functionality (Architect, Scribe, Professor)

**Estimated time:** 3-4 hours

## Phase 8: Settings Page Redesign

### Task 8.1: Redesign Settings Page Layout
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/app.js`

- [ ] Create two-column settings layout (sidebar + main content)
- [ ] Add user account section at top of sidebar (avatar, email, plan)
- [ ] Add settings search bar with ⌘F keyboard shortcut
- [ ] Reorganize settings navigation menu with icons
- [ ] Style active navigation item highlighting
- [ ] Update main content area structure
- [ ] Organize settings into logical sections

**Estimated time:** 4-5 hours

### Task 8.2: Implement Settings Item Patterns
**Files:** `electron-app/src/renderer/index.html`, `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/app.js`

- [ ] Create toggle switch component (Cursor-style)
- [ ] Create action button component (with icons)
- [ ] Update all settings items to use new patterns
- [ ] Add descriptions to all settings
- [ ] Ensure consistent spacing and hierarchy
- [ ] Test all settings functionality

**Estimated time:** 3-4 hours

### Task 8.3: Settings Search Functionality
**Files:** `electron-app/src/renderer/app.js`

- [ ] Implement settings search (filter by name/description)
- [ ] Add keyboard shortcut (⌘F) to focus search
- [ ] Highlight matching text in results
- [ ] Navigate to matching settings section
- [ ] Clear search functionality

**Estimated time:** 2-3 hours

## Phase 9: Integration & Polish

### Task 9.1: Keyboard Shortcuts
**Files:** `electron-app/src/renderer/app.js`

- [ ] Implement `Cmd+B` (toggle context menu)
- [ ] Implement `Cmd+/` (toggle agents sidebar)
- [ ] Implement `Cmd+J` (focus chat input)
- [ ] Implement `Cmd+K` (quick agent switch)
- [ ] Implement `Cmd+T` (new chat tab)
- [ ] Implement `Cmd+W` (close chat tab)

**Estimated time:** 2-3 hours

### Task 9.2: State Persistence
**Files:** `electron-app/src/renderer/app.js`

- [ ] Ensure all state persists correctly (split widths, collapsed states, active agent, chat tabs)
- [ ] Test state restoration on page reload
- [ ] Fix any persistence issues

**Estimated time:** 2-3 hours

### Task 9.3: Responsive Behavior
**Files:** `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/app.js`

- [ ] Add responsive breakpoints
- [ ] Implement collapse-to-icons for narrow windows
- [ ] Implement overlay mode for very narrow windows
- [ ] Test at various window sizes

**Estimated time:** 3-4 hours

### Task 9.4: Visual Polish Pass
**Files:** `electron-app/src/renderer/styles/main.css`, `electron-app/src/renderer/index.html`

- [ ] Apply consistent iconography (Lucide icons throughout)
- [ ] Apply consistent spacing system (CSS variables)
- [ ] Panel styling: subtle borders, clear hierarchy
- [ ] Typography consistency (monospace for code, sans-serif for UI)
- [ ] Reduce visual clutter where possible
- [ ] Ensure clear visual hierarchy across all pages
- [ ] Test visual consistency across Chat, Notes, Code, Learning pages

**Estimated time:** 3-4 hours

### Task 9.5: Testing & Bug Fixes
**Files:** All

- [ ] Test all pages with new layout
- [ ] Test chat functionality
- [ ] Test agent switching
- [ ] Test persona/model selection
- [ ] Test context pills
- [ ] Test thread list improvements
- [ ] Test resize handle
- [ ] Test keyboard shortcuts
- [ ] Fix any bugs or issues
- [ ] Test state persistence

**Estimated time:** 4-6 hours

## Total Estimated Time

**Approximately 80-95 hours** (2-2.5 weeks for one developer, or 1-1.5 weeks with 2 developers)

*Note: Updated to include context pills, thread list improvements, and settings page redesign.*

## Dependencies

- Existing chat system must be functional
- Existing persona system must be functional
- Existing conversation management must be functional
- Phase 17 (Code Workspace) can build on this layout structure

## Notes

- This is a frontend-only change; backend APIs remain unchanged
- Some Code page context menu items will be placeholders until Phase 17
- Persona/mode evolution may require backend coordination if we want to change how modes work (but UI can hide mode selector regardless)
