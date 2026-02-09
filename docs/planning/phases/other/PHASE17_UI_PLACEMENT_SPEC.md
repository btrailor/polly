# Phase 17: UI Placement Specification

**Date:** February 4, 2026  
**Purpose:** Define where every UI element should live in VSCode fork  
**Status:** In Progress

---

## Navigation Structure

### Activity Bar (Left Side - 48px)
**Decision:** Replace VSCode activity bar with Polly page navigation

**Icons (Top to Bottom):**
1. **Dashboard** - `layout-dashboard` icon
2. **Knowledge** - `network` icon
3. **Notes** - `book-open` icon
4. **Code** - `code-2` icon (shows VSCode native views when active)
5. **Learning** - `graduation-cap` icon
6. **Patterns** - `sparkles` icon
7. **Settings** - `settings` icon (bottom)

**Behavior:**
- Clicking icon switches to that workspace
- Code workspace: Shows VSCode native activity bar views (Explorer, Search, Source Control, etc.)
- Other workspaces: Show Polly-specific views in sidebar

---

## Status Bar (Bottom)

### Server Status Indicator
**Location:** Left side of status bar
**Format:** 
- Online: `$(server) Polly Server` (green)
- Offline: `$(error) Polly Server Offline` (red)
**Action:** Click to show server details/restart dialog

### Additional Status Items (if needed):
- Indexing status (when indexing)
- Connection status (if applicable)

---

## Sidebar (Left - when workspace active)

### Dashboard Workspace
**Sidebar Content:**
- Stats summary (tree view)
- Quick actions (tree view)
- Mental models status (tree view)
- Recent activity (tree view)

**Main Area:**
- Dashboard webview (complex UI with charts, stats)

### Knowledge Workspace
**Sidebar Content:**
- Knowledge graph nodes (tree view)
- Search/filter controls
- Indexing status

**Main Area:**
- Knowledge graph visualization (webview)

### Notes Workspace
**Sidebar Content:**
- Notes list (tree view)
- Folders/domains (tree view)
- Search

**Main Area:**
- Note editor (webview with CodeMirror)
- Preview mode toggle

### Code Workspace
**Sidebar Content:**
- VSCode native views (Explorer, Search, Source Control, etc.)
- No Polly-specific sidebar content

**Main Area:**
- VSCode editor (native)

### Learning Workspace
**Sidebar Content:**
- Curricula list (tree view)
- Progress summary (tree view)

**Main Area:**
- Curriculum details (webview)
- Section content (webview)

### Patterns Workspace
**Sidebar Content:**
- Patterns list (tree view)
- Pattern categories (tree view)

**Main Area:**
- Pattern details (webview)
- Pattern editor (webview)

### Settings Workspace
**Sidebar Content:**
- Settings categories (tree view)
  - General
  - Personas
  - Domains
  - Integrations
  - Routing
  - Mental Models

**Main Area:**
- Settings webview (VSCode settings UI pattern)

---

## Panel (Bottom)

### Chat Panel
**Location:** Bottom panel (can be toggled)
**Content:**
- Conversation list (tree view in sidebar when panel open)
- Message history (webview in panel)
- Input area (webview)
- Persona/mode switcher (webview)

**Behavior:**
- Always accessible via keyboard shortcut
- Can be toggled on/off
- Retains context when hidden

---

## Webviews

### When to Use Webviews:
- Complex UI that doesn't fit VSCode native components
- Rich text editing (Notes editor)
- Visualizations (Knowledge graph)
- Forms with complex interactions (Mental Models Editor)
- Settings UI (complex forms)

### When to Use Native VSCode Components:
- Simple lists → Tree views
- Simple forms → VSCode input components
- Simple dialogs → VSCode native dialogs
- Status indicators → Status bar items

---

## Commands & Keyboard Shortcuts

### Navigation Commands:
- `polly.switchToDashboard` - Switch to Dashboard
- `polly.switchToKnowledge` - Switch to Knowledge
- `polly.switchToNotes` - Switch to Notes
- `polly.switchToCode` - Switch to Code
- `polly.switchToLearning` - Switch to Learning
- `polly.switchToPatterns` - Switch to Patterns
- `polly.switchToSettings` - Switch to Settings

### Chat Commands:
- `polly.chat.toggle` - Toggle chat panel
- `polly.chat.focus` - Focus chat input

### General Commands:
- `polly.server.restart` - Restart Python server
- `polly.server.status` - Show server status

---

## UI Element Placement Summary

| Element | Location | Type |
|---------|----------|------|
| Page Navigation | Activity Bar (left) | Icons |
| Server Status | Status Bar (bottom left) | Status item |
| Dashboard Content | Sidebar + Main Area | Tree view + Webview |
| Knowledge Graph | Sidebar + Main Area | Tree view + Webview |
| Notes List | Sidebar | Tree view |
| Notes Editor | Main Area | Webview |
| Chat | Panel (bottom) | Webview + Tree view |
| Learning Curricula | Sidebar + Main Area | Tree view + Webview |
| Patterns | Sidebar + Main Area | Tree view + Webview |
| Settings | Sidebar + Main Area | Tree view + Webview |
| Mental Models Editor | Modal/Webview | Webview |
| Template Gallery | Modal/Webview | Webview |

---

## Design Principles

1. **Consistency:** Use VSCode's native UI patterns where possible
2. **Accessibility:** All UI elements accessible via keyboard
3. **Discoverability:** Clear icons, labels, and tooltips
4. **Efficiency:** Common actions easily accessible
5. **Clean:** No redundant UI, everything has a purpose

---

## Color Scheme

### Preserve from Polly:
- Primary accent: `#f0903b` (Polly orange)
- Use VSCode theme colors for everything else
- Dark theme by default (VSCode standard)

---

## Next Steps

1. ✅ Complete UI placement specification
2. ⏳ Begin implementation
3. ⏳ Test placement with users
