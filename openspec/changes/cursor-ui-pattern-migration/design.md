# Design: Cursor UI Pattern Migration

## Layout Structure

### Overall Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Titlebar (with sidebar toggle buttons)                                  │
├─────────┬───────────────────────────────────────────────────────────────┤
│ Ribbon  │                                                               │
│ (40px)  │                                                               │
├─────────┼───────────────────────────────────────────────────────────────┤
│         │ ┌──────────────────────┬─────────────────────┬───────────────┐ │
│ Left    │ │   Main Content       │   Chat Panel        │ Agents        │ │
│ Sidebar │ │   (varies by page)   │   (always visible)  │ Sidebar       │ │
│         │ │   (resizable)        │   (resizable)       │ (collapsible) │ │
│         │ │                      │                     │               │ │
│         │ │ [Page Content]       │   [Agent Tabs]      │ [New Agent]   │ │
│         │ │ - Code: Editor       │   [Messages]        │ [Agent List]  │ │
│         │ │ - Notes: Editor      │   [Input + Controls]│               │ │
│         │ │ - Chat: Messages     │                     │               │ │
│         │ │ - etc.               │                     │               │ │
│         │ └──────────────────────┴─────────────────────┴───────────────┘ │
│         │                    ↑ Resize Handle ↑                            │
│         │                                                               │
├─────────┴───────────────────────────────────────────────────────────────┤
│ Status Bar (Cursor-style)                                                 │
│ [Server Status] [Connection] [Other indicators]                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Left Sidebar (Collapsible)**
   - Collapsible via button or keyboard shortcut (`Cmd+B`)
   - Content varies by page:
     - **Code page:** VSCode-like feature views (Files, Search, Source Control, Extensions, etc.)
     - **Notes page:** Ribbon buttons at top, then note navigation
     - **Chat page:** Conversation list or context tools
     - **Other pages:** Context-appropriate navigation/views

2. **Main Center Column (Split)**
   - Always split into two sub-columns
   - Resize handle between them (draggable, with visual feedback)
   - **Left sub-column:** Main content area (varies by page)
     - **Code page:** Monaco editor with file tabs, terminal, etc.
     - **Notes page:** Note editor
     - **Chat page:** Chat messages (if not using chat panel)
     - **Other pages:** Page-specific main content
   - **Right sub-column:** Chat panel (always visible, persistent)

3. **Chat Panel (Right sub-column of main center)**
   - Always visible in main center area (right side of split)
   - Tabs at top for multiple chats per agent
   - Message area in middle
   - Input area at bottom with:
     - Persona selector (dropdown/chip)
     - Model selector (dropdown/chip)
     - Text input
     - Send button
   - No explicit "mode" selector; personas define available actions

4. **Agents Sidebar (Right edge, separate from main center)**
   - Collapsible right sidebar (separate from main center column)
   - "New Agent" button at top
   - List of available agents
   - Active agent highlighted
   - Click to switch active agent (updates chat panel)

5. **Status Bar (Bottom)**
   - Cursor-style persistent status bar
   - Left side: Server status, connection info
   - Right side: Editor info (cursor position, encoding, etc.) when applicable
   - Always visible across all views

## Detailed Component Specifications

### 1. Left Sidebar (Collapsible, Page-Specific)

**Structure:**
```html
<aside class="left-sidebar" id="left-sidebar">
  <!-- Content varies by page -->
</aside>
```

**Behavior:**
- Collapsible via button or `Cmd+B`
- Content changes based on active page
- Persist collapsed state in localStorage

### 2. Main Center Column Split

**Structure:**
```html
<div class="main-center-column">
  <div class="main-content-area" id="main-content">
    <!-- Page-specific main content -->
    <!-- Code: Monaco editor, file tabs, terminal -->
    <!-- Notes: Note editor -->
    <!-- Chat: Messages (if not using chat panel) -->
    <!-- etc. -->
  </div>
  <div class="resize-handle" id="center-resize-handle"></div>
  <div class="chat-panel" id="chat-panel">
    <!-- Chat content -->
  </div>
</div>
```

**Behavior:**
- Resize handle is draggable
- Minimum widths: Main content 300px, Chat panel 300px
- Default split: 60% main content / 40% chat (adjustable)
- Persist split ratio in localStorage
- Visual feedback on hover/drag

**CSS:**
```css
.main-center-column {
  display: flex;
  height: 100%;
  position: relative;
  flex: 1;
}

.main-content-area {
  flex: 1;
  min-width: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.resize-handle {
  width: 4px;
  cursor: col-resize;
  background: var(--border-color);
  transition: background 0.2s;
}

.resize-handle:hover {
  background: var(--accent-primary);
}

.chat-panel {
  width: 40%;
  min-width: 300px;
  max-width: 50%;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border-color);
}
```

### 3. Left Sidebar Content (Page-Specific)

#### Code Page Left Sidebar

**VSCode-like feature views:**
- Files (file tree)
- Search (search across workspace)
- Source Control (git status, changes)
- Extensions (if applicable)
- Debug (if applicable)
- Other VSCode-like views

**Structure:**
```html
<aside class="left-sidebar code-sidebar">
  <div class="sidebar-header">
    <button class="sidebar-view-btn active" data-view="files">
      <i data-lucide="folder"></i>
      <span>Files</span>
    </button>
    <button class="sidebar-view-btn" data-view="search">
      <i data-lucide="search"></i>
      <span>Search</span>
    </button>
    <!-- More views -->
  </div>
  <div class="sidebar-content">
    <!-- View-specific content -->
  </div>
</aside>
```

**Main Content Area (Code page):**
- Monaco editor
- File tabs
- Terminal (if applicable)
- Editor content

#### Notes Page Left Sidebar

**Ribbon buttons at top:**
- New Note
- Templates
- Folders
- Tags
- Search

**Structure:**
```html
<aside class="left-sidebar notes-sidebar">
  <div class="ribbon-buttons">
    <button class="ribbon-btn" data-action="new-note">
      <i data-lucide="file-plus"></i>
      <span>New Note</span>
    </button>
    <!-- More buttons -->
  </div>
  <div class="notes-navigation">
    <!-- Note list, folders, etc. -->
  </div>
</aside>
```

**Main Content Area (Notes page):**
- Note editor
- Note content
- Markdown rendering

#### Chat Page Left Sidebar

**Conversation management:**
- Conversation list
- Categories
- Search conversations
- New conversation button

**Main Content Area (Chat page):**
- Chat messages (if not using chat panel exclusively)
- Or can be empty if chat panel handles all chat UI

### 4. Chat Panel

**Structure:**
```html
<div class="chat-panel">
  <div class="chat-tabs">
    <button class="chat-tab active" data-chat-id="chat-1">
      <span>Chat 1</span>
      <button class="tab-close">×</button>
    </button>
    <button class="chat-tab" data-chat-id="chat-2">
      <span>Chat 2</span>
      <button class="tab-close">×</button>
    </button>
    <button class="chat-tab-new">+</button>
  </div>
  
  <div class="chat-messages">
    <!-- Messages -->
  </div>
  
  <div class="chat-input-area">
    <div class="chat-controls">
      <select class="persona-selector" id="chat-persona-select">
        <option value="">Default</option>
        <option value="architect">Architect</option>
        <option value="scribe">Scribe</option>
        <option value="professor">Professor</option>
      </select>
      <select class="model-selector" id="chat-model-select">
        <!-- Model options -->
      </select>
    </div>
    <textarea class="chat-input" id="chat-input" placeholder="Ask Polly anything..."></textarea>
    <button class="send-button" id="chat-send">Send</button>
  </div>
</div>
```

**Persona/Mode Behavior:**
- Persona selector shows available personas
- No explicit "mode" selector
- When persona is selected, available actions are contextually available
- Example: Professor persona can create curriculum when user says "I want to make a learning plan for X" (triggers curriculum action, no explicit mode selection needed)

### 5. Agents Sidebar

**Structure:**
```html
<aside class="agents-sidebar" id="agents-sidebar">
  <div class="agents-header">
    <button class="new-agent-btn" id="new-agent-btn">
      <i data-lucide="plus"></i>
      <span>New Agent</span>
    </button>
  </div>
  <div class="agents-list">
    <div class="agent-item active" data-agent-id="agent-1">
      <div class="agent-icon">A</div>
      <div class="agent-info">
        <div class="agent-name">Agent 1</div>
        <div class="agent-status">Active</div>
      </div>
    </div>
    <!-- More agents -->
  </div>
</aside>
```

**Behavior:**
- Click agent to switch active agent
- Active agent's chats appear in chat panel tabs
- Collapsible via button or keyboard shortcut
- Persist collapsed state

### 6. Floating Chat Interface

**Overhaul:**
- Match new chat panel design
- Persona and model selectors
- Simplified (no explicit mode selector)
- Can be minimized/maximized
- When maximized, shows same structure as main chat panel

### 7. Status Bar

**Structure:**
```html
<div class="status-bar">
  <div class="status-left">
    <span class="status-item" id="server-status">
      <i data-lucide="server"></i>
      <span>Server: Running</span>
    </span>
    <span class="status-item" id="connection-status">
      <i data-lucide="wifi"></i>
      <span>Connected</span>
    </span>
  </div>
  <div class="status-right">
    <span class="status-item" id="cursor-info">Ln 1, Col 1</span>
    <span class="status-item" id="encoding">UTF-8</span>
    <span class="status-item" id="line-endings">LF</span>
  </div>
</div>
```

**CSS:**
```css
.status-bar {
  height: 22px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
  font-size: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
}
```

## Main Content Area by Page

### Code Page
- Monaco editor with syntax highlighting
- File tabs for open files
- Terminal panel (optional, can be in main area or separate)
- Editor features (find, replace, etc.)

### Notes Page
- Note editor (Monaco or CodeMirror)
- Markdown preview (optional split view)
- Note metadata

### Chat Page
- Can show chat messages in main area (if not using chat panel exclusively)
- Or can be empty/minimal if chat panel handles all chat UI

### Other Pages
- Page-specific main content
- Each page defines its own main content area

## Additional Cursor Patterns

### Context Pills / @-Mentions

**Pattern:** User can attach "context" to the next message: files, symbols, selection, domains, notes. Shown as pills/chips above or beside input.

**Implementation:**
- Context pills displayed above chat input
- Add context via "@" mentions or context picker button
- Basic version: "@domain", "@note", "@folder"
- Extended version (Code profile): "@file", "@selection", "@symbol"
- Pills show context name and can be removed with × button
- Context sent with message to backend

**Structure:**
```html
<div class="chat-input-area">
  <div class="context-pills" id="context-pills">
    <!-- Pills appear here when context is attached -->
    <!-- Example: -->
    <div class="context-pill" data-context-type="domain" data-context-id="domain-1">
      <span>@domain: Python</span>
      <button class="pill-remove">×</button>
    </div>
  </div>
  <!-- Rest of input area -->
</div>
```

### Thread List Improvements

**Pattern:** Conversation list is first-class with clear titles, optional preview, easy rename/delete, keyboard navigation.

**Implementation:**
- Clean thread list in left sidebar (Chat page) or chat panel
- Thread titles with optional snippet/preview
- Right-click context menu: rename, delete, star, category
- Keyboard navigation (arrow keys, Enter to open)
- Search/filter conversations
- Visual hierarchy: active thread highlighted

### Visual Polish

**Pattern:** Dense but scannable layout with consistent iconography, spacing, and panel styling.

**Implementation:**
- Consistent iconography (Lucide icons throughout)
- Consistent spacing system (use CSS variables)
- Panel styling: subtle borders, clear hierarchy
- Typography: monospace for code/technical, sans-serif for UI
- Reduce visual clutter where possible
- Clear visual hierarchy: primary actions prominent, secondary actions subtle

## Persona/Mode Evolution

### Current System
- User selects persona
- User explicitly selects mode (e.g., "Curriculum" mode in Professor persona)
- Mode determines available actions

### New System
- User selects persona
- Persona defines available actions/capabilities
- Actions trigger contextually based on user intent
- Example: Professor persona can create curriculum when user says "I want to make a learning plan for X"
- No explicit mode selector; actions are suggested or triggered naturally

### Implementation Notes
- Backend persona system remains unchanged
- UI removes explicit mode selector
- Persona activation includes all available actions
- Action triggers based on user intent (detected via natural language or explicit action buttons when contextually relevant)

## Responsive Behavior

- **Narrow windows:** Context menu and agents sidebar can collapse to icons only
- **Very narrow:** Chat panel takes full width, context menu becomes overlay
- **Minimum widths enforced:** Prevent unusable layouts

## Keyboard Shortcuts

- `Cmd+B`: Toggle left context menu
- `Cmd+/`: Toggle agents sidebar
- `Cmd+J`: Focus chat input
- `Cmd+K`: Quick agent switch (command palette style)
- `Cmd+T`: New chat tab
- `Cmd+W`: Close current chat tab

## State Persistence

- Split column widths (localStorage)
- Collapsed state of sidebars (localStorage)
- Active agent (sessionStorage)
- Active chat tabs per agent (sessionStorage)
- Persona/model selections (localStorage per agent)

## Settings Page Pattern (Cursor Reference)

### Cursor Settings Structure Analysis

Based on Cursor's settings page, we adopt the following patterns:

#### Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Left Sidebar (Settings Navigation)    │ Main Content    │
│                                         │                 │
│ [User Account Section]                 │ [Page Title]    │
│ - Avatar                                │                 │
│ - Email                                 │ [Sections]      │
│ - Plan                                  │ - Manage Account│
│                                         │ - Upgrade       │
│ [Search: ⌘F]                           │ - Preferences   │
│                                         │ - Notifications │
│ [Navigation Menu]                      │                 │
│ - General (active)                     │ [Settings Items] │
│ - Agents                                │ - Toggle switches│
│ - Tab                                   │ - Action buttons│
│ - Models                                │ - Descriptions  │
│ - Cloud Agents                          │                 │
│ - Tools & MCP                           │                 │
│ - Rules and Commands                    │                 │
│ - Indexing & Docs                       │                 │
│ - Network                               │                 │
│ - Beta                                  │                 │
│ - Docs                                  │                 │
└─────────────────────────────────────────────────────────┘
```

#### Key Patterns

1. **Left Sidebar Navigation**
   - User account section at top (avatar, email, plan/subscription)
   - Search bar with keyboard shortcut indicator (⌘F)
   - Navigation menu with icons and labels
   - Active item highlighted with background color
   - Clear visual hierarchy

2. **Main Content Area**
   - Page title at top
   - Sections organized into logical groups
   - Each section has:
     - Title/heading
     - Description text
     - Settings items (toggles, buttons, inputs)
   - Action buttons (Open, Upgrade, Import, etc.) with icons
   - Toggle switches for boolean preferences
   - Clear descriptions for each setting

3. **Settings Item Patterns**
   - **Toggle switches:** For boolean preferences (on/off states clearly visible)
   - **Action buttons:** For opening external pages, importing, resetting (with icons)
   - **Descriptions:** Helpful text explaining what each setting does
   - **Grouping:** Related settings grouped in sections

### Polly Settings Page Implementation

#### Left Sidebar Structure

**User Account Section (Top):**
```html
<div class="settings-account-section">
  <div class="account-avatar">P</div>
  <div class="account-info">
    <div class="account-email">user@example.com</div>
    <div class="account-plan">Free Plan</div>
  </div>
</div>
```

**Search Bar:**
```html
<div class="settings-search">
  <input type="text" placeholder="Search settings ⌘F" id="settings-search-input">
  <i data-lucide="search" class="search-icon"></i>
</div>
```

**Navigation Menu:**
```html
<nav class="settings-nav">
  <button class="settings-nav-item active" data-section="general">
    <i data-lucide="settings" class="nav-icon"></i>
    <span class="nav-label">General</span>
  </button>
  <button class="settings-nav-item" data-section="api-keys">
    <i data-lucide="key" class="nav-icon"></i>
    <span class="nav-label">API Keys</span>
  </button>
  <!-- More items -->
</nav>
```

#### Main Content Structure

**Section Pattern:**
```html
<div class="settings-section">
  <h3>Section Title</h3>
  <p class="section-description">Optional description of the section</p>
  
  <div class="settings-item">
    <div class="settings-item-header">
      <label class="settings-label">Setting Name</label>
      <div class="settings-control">
        <!-- Toggle, button, or input -->
      </div>
    </div>
    <p class="settings-description">What this setting does</p>
  </div>
  
  <!-- More settings items -->
</div>
```

**Toggle Switch Pattern:**
```html
<div class="settings-item">
  <div class="settings-item-header">
    <label class="settings-label">Sync layouts across windows</label>
    <div class="toggle-switch">
      <input type="checkbox" id="sync-layouts" checked>
      <label for="sync-layouts" class="toggle-label"></label>
    </div>
  </div>
  <p class="settings-description">When enabled, all windows share the same layout</p>
</div>
```

**Action Button Pattern:**
```html
<div class="settings-item">
  <div class="settings-item-header">
    <label class="settings-label">Editor Settings</label>
    <button class="settings-action-btn">
      <span>Open</span>
      <i data-lucide="external-link"></i>
    </button>
  </div>
  <p class="settings-description">Configure font, formatting, minimap and more</p>
</div>
```

#### CSS Patterns

```css
.settings-page {
  display: flex;
  height: 100%;
}

.settings-sidebar {
  width: 240px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.settings-account-section {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 12px;
}

.account-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.settings-search {
  padding: 12px;
  position: relative;
}

.settings-search input {
  width: 100%;
  padding: 8px 12px 8px 32px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.settings-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.settings-nav-item {
  width: 100%;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.2s;
}

.settings-nav-item:hover {
  background: var(--bg-hover);
}

.settings-nav-item.active {
  background: var(--bg-active);
  color: var(--accent-primary);
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.settings-section {
  margin-bottom: 32px;
}

.settings-section h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.section-description {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.settings-item {
  margin-bottom: 24px;
}

.settings-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.settings-label {
  font-weight: 500;
  font-size: 14px;
}

.settings-description {
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 4px;
}

.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-label {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary);
  border-radius: 24px;
  transition: background 0.2s;
}

.toggle-label:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-switch input:checked + .toggle-label {
  background-color: var(--accent-primary);
}

.toggle-switch input:checked + .toggle-label:before {
  transform: translateX(20px);
}

.settings-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.settings-action-btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
}
```

### Settings Page Navigation (Polly)

**Proposed Settings Sections:**
- **General:** Account, preferences, editor settings, keyboard shortcuts, imports
- **Agents:** Agent management and configuration (when implemented)
- **API Keys:** API key management for providers
- **Models:** Model configuration and routing
- **Domains:** Domain configuration and management
- **Notes:** Notes-specific settings
- **Compression:** Compression settings and stats
- **Integrations:** Third-party integrations (Obsidian, etc.)
- **Mental Models:** Mental model management
- **Advanced:** Advanced settings and debugging

### General UI Principles from Settings Pattern

1. **Two-Column Layout:** Navigation sidebar + main content area
2. **Search Functionality:** Quick search with keyboard shortcut
3. **Clear Hierarchy:** Sections → Settings items → Descriptions
4. **Visual Feedback:** Active states, hover states, toggle states
5. **Action Affordances:** Buttons clearly indicate actions (Open, Import, etc.)
6. **Descriptive Text:** Every setting has helpful description
7. **Grouping:** Related settings grouped logically
8. **Consistent Spacing:** Predictable padding and margins
9. **Icon Usage:** Icons for navigation items and action buttons
10. **Account Context:** User account info visible in sidebar

These patterns can be applied to other pages beyond settings for consistency.
