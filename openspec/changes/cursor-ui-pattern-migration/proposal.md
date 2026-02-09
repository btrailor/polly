# Proposal: Cursor UI Pattern Migration

## What we're doing

Migrate Polly's UI to adopt **Cursor's layout patterns** as the primary interface paradigm. The main center column will always be split into two sub-columns with a resize handle: left (context-specific menu) and right (chat panel). The right sidebar becomes an agents selection panel. We also overhaul the floating chat interface and introduce a Cursor-style bottom status bar.

## Why

- **User goal:** A Cursor-like experience where chat is always accessible on the right side of the main content area, with context-aware left panels and agent management.
- **Consistency:** Align Polly's UI with proven patterns from Cursor that users are familiar with, creating a more intuitive and professional experience.
- **Better organization:** Separate context navigation (left) from chat (right) in the main area, with agents as a dedicated right sidebar, creates clearer mental models.
- **Persona evolution:** Move from explicit mode selection to action-based persona capabilities, where personas define available actions rather than requiring explicit mode switching.

## Scope

### In scope

1. **Left sidebar (collapsible, separate from main center):**
   - Collapsible left sidebar that varies by page
   - Code page: VSCode-like feature views (Files, Source Control, Search, Extensions, etc.)
   - Notes page: Ribbon buttons at top of sidebar
   - Other pages: Context-appropriate navigation/views

2. **Main center column split:**
   - Always split into two sub-columns with resize handle
   - Left sub-column: Main content area (varies by page - Code editor, Notes editor, etc.)
   - Right sub-column: Chat panel (always visible, persistent)

3. **Right agents sidebar:**
   - Collapsible right sidebar for agent selection
   - "New Agent" button
   - List of agents with ability to switch active agent
   - Each agent supports multiple chat tabs (shown at top of chat area)

4. **Chat panel overhaul:**
   - Persona selector (dropdown/chip)
   - Model selector (dropdown/chip)
   - Chat tabs for multiple conversations per agent
   - Context pills (@-mentions) for attaching context to messages
   - Remove explicit "mode" selection; personas define available actions contextually

5. **Thread list improvements:**
   - First-class conversation list with clear titles and previews
   - Right-click context menu (rename, delete, star, category)
   - Keyboard navigation
   - Search/filter conversations

6. **Floating chat interface:**
   - Overhaul to match new patterns
   - Persona and model selectors
   - Simplified interface (no explicit mode selection)

7. **Bottom status bar:**
   - Cursor-style status bar at bottom of window
   - Server status, connection info, and other status indicators
   - Persistent across all views

8. **Settings page redesign:**
   - Two-column layout (navigation sidebar + main content)
   - User account section at top of sidebar
   - Settings search with keyboard shortcut (⌘F)
   - Cursor-style toggle switches and action buttons
   - Clear section organization with descriptions
   - Consistent with Cursor settings patterns

### Out of scope

- Backend persona/mode logic changes (this is UI/UX only; backend APIs stay the same)
- Full Code workspace implementation (Phase 17 handles that)
- Agent creation/configuration UI (basic selection only for this change)

## Backend vs frontend

**Frontend-only:** This is a UI/UX overhaul in `electron-app/src/renderer/`. Layout, components, styling, and navigation changes. Backend APIs remain unchanged; we're changing how we present and interact with existing functionality.

## Relationship to other work

- **Phase 17 (Code Workspace):** This change prepares the layout structure that Phase 17 will use. The Code page will use the left sidebar for file tree, source control, etc. Extended context pills (@file, @selection) will be implemented in Phase 17.
- **Supersedes ux-pivot-cursor-patterns:** This change consolidates and extends the general Cursor patterns from `ux-pivot-cursor-patterns`, adding detailed layout specifications, agent management, and status bar. All patterns from the UX pivot are included here.
- **Persona system:** UI changes only; persona backend logic remains unchanged, but we're changing how modes are presented (action-based rather than explicit selection).
- **Void setup patterns:** See [specs/VOID_SETUP_AND_MODEL_PATTERNS.md](specs/VOID_SETUP_AND_MODEL_PATTERNS.md) for first-time setup and model integration patterns (design reference from Void fork).

## Design reference

- **Cursor:** Screenshots and UX patterns for layout, chat placement, status bar, agent/chat management
- **VSCode:** Feature views in left sidebar (Files, Search, Source Control, etc.) as reference for Code page context menu
- **Current Polly:** Existing three-column layout, chat system, persona selectors
