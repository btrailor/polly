# Phase 0.5: Obsidian-Inspired UI Redesign - Final Implementation Plan

**Status:** Day 1 - In Progress  
**Duration:** 7-10 Days  
**Goal:** Transform Polly from retro-brutalist to professional Obsidian-inspired design with subtle glitch accents

---

## Design Philosophy

### Core Principles
1. **Professional First** - Clean, minimal, Obsidian-inspired aesthetic
2. **Context Everywhere** - Chat visible and contextual on all pages
3. **Subtle Accents** - 5-10% glitch/retro effects on key interactive elements
4. **Page-Based Navigation** - Icon-only ribbon with dedicated pages
5. **Smart Sidebars** - Collapsible, resizable, context-adaptive

### Visual Identity
- **Base Design:** Obsidian (95%)
- **Accent Design:** Retro-brutalist glitch effects (5%)
- **Color Palette:** Dark theme with purple accents
- **Typography:** Inter (UI), JetBrains Mono (code/terminals)
- **Icons:** Lucide v0.562.0

---

## Architecture Overview

### Three-Column Layout
```
┌────┬─────────────────┬──────────────────────┬─────────────────┐
│ R  │  LEFT SIDEBAR   │   MAIN CONTENT       │  RIGHT SIDEBAR  │
│ I  │  (collapsible)  │   (flexible width)   │  (collapsible)  │
│ B  │                 │                      │                 │
│ B  │  Context-       │   Page-specific      │   Chat Panel    │
│ O  │  specific       │   content with       │   (context-     │
│ N  │  panels         │   tabs               │    aware)       │
│    │                 │                      │                 │
│ 40 │  240-600px      │   Flexible           │   280-400px     │
│ px │  (default 280)  │                      │   (default 320) │
└────┴─────────────────┴──────────────────────┴─────────────────┘
```

### Page Structure
Each page has:
- **Left sidebar content** - Context-specific (file explorer, calendar mini, project tree, etc.)
- **Main content area** - Page-specific UI with optional tabs
- **Right sidebar chat** - Persistent, context-aware conversations for that page

---

## Day-by-Day Implementation

### Day 1: Layout Foundation & Routing ✓ IN PROGRESS

**Files to Create:**
- `electron-app/src/renderer/styles/obsidian-theme.css` - Color palette & CSS variables
- `electron-app/src/renderer/styles/layout.css` - Three-column grid system
- `electron-app/src/renderer/styles/glitch-effects.css` - Subtle accent animations
- `electron-app/src/renderer/components/ribbon.js` - Icon navigation component
- `electron-app/src/renderer/components/layout.js` - Sidebar management

**Files to Modify:**
- `electron-app/src/renderer/index.html` - New three-column structure
- `electron-app/src/renderer/app.js` - Add page routing system

**Tasks:**
1. ✓ Create implementation plan document
2. Back up current index.html and app.js
3. Create obsidian-theme.css with:
   - CSS variables (colors, spacing, typography)
   - Dark theme palette
   - Purple accent color (#7f6df2)
   - Font definitions (Inter, JetBrains Mono)
4. Create layout.css with:
   - Three-column CSS Grid
   - Responsive breakpoints
   - Collapse/expand states
5. Create glitch-effects.css with:
   - Logo glitch effect
   - Button hover effects
   - Active tab glow
   - 5-10% usage only
6. Build ribbon.js component:
   - Icon-only navigation
   - Lucide icons
   - Hover tooltips
   - Active state highlighting
   - Logo with glitch effect at top
   - Settings at bottom
7. Build layout.js component:
   - Sidebar collapse/expand
   - Resize handles
   - Width persistence (localStorage)
   - Keyboard shortcuts (Cmd+B, Cmd+/)
8. Update index.html:
   - Replace current structure
   - Add three-column layout
   - Include new CSS files
   - Add ribbon container
   - Add sidebar containers
9. Update app.js:
   - Add page routing system
   - Replace view-based navigation with page-based
   - Preserve state between page switches
10. Test layout foundation

**Success Criteria:**
- ✓ Three-column layout displays correctly
- ✓ Ribbon shows with all page icons
- ✓ Sidebars can collapse/expand
- ✓ Page switching works
- ✓ Obsidian color palette applied
- ✓ Glitch effects visible on logo/buttons

---

### Day 2: Page-Specific Chat System

**Files to Create:**
- `components/chat-manager.js` - Chat state management for all pages
- `components/chat-panel.js` - Right sidebar chat UI
- `components/conversation-list.js` - Page-specific conversation lists
- `styles/chat.css` - Chat panel styling

**Tasks:**
1. Create chat-manager.js:
   - Page-specific conversation storage
   - Active conversation tracking by page
   - Cross-page context awareness
   - Global conversation search
   - Conversation linking system
2. Build chat-panel.js:
   - Right sidebar chat UI
   - Page context indicator
   - Conversation switcher
   - Message display with streaming
   - Input area with send button
   - Quick actions (context-specific)
3. Build conversation-list.js:
   - Grouped by page
   - Search/filter functionality
   - Star/favorite conversations
   - Context menu (rename, delete, etc.)
4. Integrate with existing chat backend:
   - Preserve current WebSocket logic
   - Add page context to queries
   - Update RAG retrieval to use page context
5. Test chat across pages:
   - Create conversations in different pages
   - Switch pages and verify chat updates
   - Test cross-page context queries

**Success Criteria:**
- ✓ Chat visible in right sidebar on all pages
- ✓ Each page has separate conversation list
- ✓ Chat updates when switching pages
- ✓ Can create new conversations per page
- ✓ Cross-page context queries work
- ✓ Existing chat functionality preserved

---

### Day 3: Collapsible/Resizable Sidebars

**Files to Modify:**
- `components/layout.js` - Add resize logic
- `styles/layout.css` - Add resize handle styles

**Tasks:**
1. Implement collapse/expand animations:
   - Smooth transitions (200-300ms)
   - Preserve content state
   - Update main content width
2. Add resize handles:
   - Draggable dividers
   - Min/max width constraints (240px-600px)
   - Visual feedback on hover/drag
   - Snap points at min/default widths
3. Implement width persistence:
   - Save to localStorage on resize
   - Restore on app launch
   - Per-sidebar settings (left/right independent)
4. Add keyboard shortcuts:
   - Cmd+B - Toggle left sidebar
   - Cmd+/ - Toggle right sidebar
   - Cmd+Shift+B - Reset left sidebar width
   - Cmd+Shift+/ - Reset right sidebar width
5. Test responsiveness:
   - Window resize behavior
   - Small screen adaptations
   - Sidebar collision prevention

**Success Criteria:**
- ✓ Sidebars collapse/expand smoothly
- ✓ Can resize sidebars by dragging
- ✓ Widths persist between sessions
- ✓ Keyboard shortcuts work
- ✓ No layout breaks on small windows

---

### Day 4: Tailwind CSS + Component Library

**Files to Create:**
- `tailwind.config.js` - Tailwind configuration
- `styles/tailwind.css` - Tailwind base/utilities
- `components/ui/button.js` - Reusable button component
- `components/ui/card.js` - Card container component
- `components/ui/input.js` - Input field component
- `components/ui/badge.js` - Badge/tag component
- `components/ui/modal.js` - Modal dialog component

**Tasks:**
1. Install Tailwind CSS:
   - Add to package.json
   - Configure PostCSS for Electron
   - Set up build pipeline
2. Configure Tailwind:
   - Extend with Obsidian colors
   - Add custom spacing
   - Define typography scale
   - Add glitch effect utilities
3. Create base UI components:
   - Button (primary, secondary, danger, icon-only)
   - Card (with header, body, footer)
   - Input (text, password, search)
   - Badge (status, tag, domain)
   - Modal (standard dialog)
4. Add glitch effect variants:
   - `.glitch-hover` - Hover effect
   - `.glitch-active` - Active state
   - `.glitch-pulse` - Pulsing animation
   - Use sparingly (5-10% of UI)
5. Refactor existing components:
   - Update buttons to use new system
   - Replace inline styles with Tailwind
   - Standardize spacing/sizing

**Success Criteria:**
- ✓ Tailwind CSS working in Electron
- ✓ Obsidian colors in Tailwind config
- ✓ All UI components created
- ✓ Glitch effects on key elements
- ✓ Existing UI updated to new system

---

### Day 5: Left Sidebar Adaptive Panels

**Files to Create:**
- `components/panels/file-explorer.js` - File tree navigation
- `components/panels/calendar-mini.js` - Mini calendar view
- `components/panels/project-tree.js` - Project/repository tree
- `components/panels/domain-browser.js` - Domain navigation
- `components/panels/search-panel.js` - Global search
- `styles/panels.css` - Panel styling

**Tasks:**
1. Build file-explorer.js:
   - Tree view of files
   - Folder collapse/expand
   - File type icons
   - Search/filter
   - Context menu (open, reveal, etc.)
   - Used on: Notes, Knowledge pages
2. Build calendar-mini.js:
   - Mini month view
   - Current day highlight
   - Event indicators
   - Click to go to full calendar
   - Used on: Calendar page
3. Build project-tree.js:
   - Repository list
   - File tree per repo
   - Git status indicators
   - Quick navigation
   - Used on: Code, Projects pages
4. Build domain-browser.js:
   - List all domains
   - Domain stats (files, chunks)
   - Quick filter by domain
   - Used on: All pages (universal panel)
5. Build search-panel.js:
   - Global search input
   - Recent searches
   - Filter by type (notes, code, calendar, etc.)
   - Quick results preview
   - Used on: Search page + global overlay
6. Implement panel switching:
   - Left sidebar adapts to current page
   - Smooth transitions between panels
   - Preserve panel state per page
   - Option to pin secondary panel

**Success Criteria:**
- ✓ All panel types created
- ✓ Left sidebar adapts to page
- ✓ Panels functional and styled
- ✓ Smooth transitions between panels
- ✓ Panel state persists per page

---

### Day 6: Migrate Existing Features

**Files to Modify:**
- `app.js` - Major refactoring for new architecture
- All existing components - Update to new layout

**Tasks:**
1. Migrate chat interface:
   - Move to right sidebar chat-panel.js
   - Update message rendering
   - Preserve streaming logic
   - Update related notes panel
2. Migrate setup wizard:
   - Keep as modal overlay or dedicated page
   - Update styling to Obsidian theme
   - Remove brutalist elements
3. Migrate dashboard:
   - Move stats to Dashboard page main area
   - Update domain cards
   - Update service status indicators
4. Migrate knowledge view:
   - Move to Knowledge page
   - Update indexing UI
   - Update source cards
5. Migrate patterns view:
   - Move to Patterns page
   - Update pattern list
   - Update controls
6. Migrate settings:
   - Move to Settings page
   - Keep tab structure
   - Update styling
7. Update conversation management:
   - Integrate with chat-manager.js
   - Update conversation list UI
   - Update context menus
8. Update integrations:
   - Keep existing backend logic
   - Update UI cards
   - Update status indicators
9. Update all Lucide icon usage:
   - Verify all icons render
   - Update sizes/colors for Obsidian theme
   - Add glitch effects to key icons
10. Test all features:
    - Chat with RAG
    - Indexing
    - Integrations
    - Settings changes
    - Conversation management

**Success Criteria:**
- ✓ All existing features work in new layout
- ✓ Chat fully functional with page context
- ✓ Setup wizard works
- ✓ Dashboard displays correctly
- ✓ Knowledge indexing works
- ✓ Patterns view functional
- ✓ Settings save correctly
- ✓ Integrations work
- ✓ No regressions in functionality

---

### Day 7: Polish, Testing & Documentation

**Tasks:**
1. Visual polish:
   - Fine-tune spacing/sizing
   - Adjust colors for accessibility
   - Smooth all animations
   - Add loading states
   - Add empty states
   - Add error states
2. Performance optimization:
   - Lazy load heavy components
   - Optimize icon rendering
   - Debounce resize handlers
   - Optimize chat rendering
3. Cross-browser testing:
   - Test in Chrome (main)
   - Test in Safari (Electron uses Chromium, but verify WebKit behaviors)
   - Test on different screen sizes
4. Dark mode verification:
   - Ensure all colors readable
   - Check contrast ratios
   - Verify glitch effects visible
5. Keyboard navigation:
   - Tab order correct
   - All shortcuts work
   - Focus indicators visible
6. Accessibility:
   - ARIA labels on icons
   - Screen reader support
   - Keyboard-only navigation
7. Create DESIGN_SYSTEM.md:
   - Color palette reference
   - Typography scale
   - Component documentation
   - Usage guidelines
   - Glitch effect guidelines
8. Update developer documentation:
   - New architecture overview
   - Component structure
   - Styling conventions
   - Adding new pages
   - Creating new panels
9. Create migration guide:
   - Before/after comparison
   - Feature mapping
   - Keyboard shortcuts
   - Known issues
10. Final testing:
    - End-to-end user flows
    - Edge cases
    - Error handling
    - Performance under load

**Success Criteria:**
- ✓ UI polished and professional
- ✓ No visual bugs
- ✓ All animations smooth
- ✓ Good performance
- ✓ Fully accessible
- ✓ Documentation complete
- ✓ Ready for user testing

---

## Technical Specifications

### Color Palette (Obsidian-Inspired)

```css
:root {
  /* Background colors */
  --bg-primary: #1e1e1e;      /* Main background */
  --bg-secondary: #252525;    /* Cards, panels */
  --bg-tertiary: #2a2a2a;     /* Hover states */
  --bg-hover: #2f2f2f;        /* Interactive hover */
  
  /* Text colors */
  --text-primary: #e0e0e0;    /* Main text */
  --text-secondary: #a0a0a0;  /* Secondary text */
  --text-muted: #707070;      /* Disabled/muted */
  
  /* Accent colors */
  --accent-purple: #7f6df2;   /* Primary accent */
  --accent-purple-hover: #9785f7;
  --accent-purple-active: #6c5dd8;
  
  /* Semantic colors */
  --success: #10b981;         /* Success states */
  --warning: #f59e0b;         /* Warning states */
  --error: #ef4444;           /* Error states */
  --info: #3b82f6;            /* Info states */
  
  /* Border colors */
  --border-primary: #3a3a3a;  /* Main borders */
  --border-secondary: #2f2f2f;/* Subtle borders */
  --border-accent: #7f6df2;   /* Accent borders */
  
  /* Special effects */
  --glitch-primary: #00ff88;  /* Glitch color 1 */
  --glitch-secondary: #ff00ff;/* Glitch color 2 */
  
  /* Layout dimensions */
  --ribbon-width: 40px;
  --sidebar-min: 240px;
  --sidebar-max: 600px;
  --sidebar-default-left: 280px;
  --sidebar-default-right: 320px;
}
```

### Typography

```css
:root {
  /* Font families */
  --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
  
  /* Font sizes */
  --text-xs: 11px;
  --text-sm: 13px;
  --text-base: 14px;
  --text-lg: 16px;
  --text-xl: 18px;
  --text-2xl: 24px;
  --text-3xl: 32px;
  
  /* Line heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Spacing Scale

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
}
```

### Layout Grid

```css
.app-container {
  display: grid;
  grid-template-columns: var(--ribbon-width) var(--sidebar-left-width) 1fr var(--sidebar-right-width);
  grid-template-rows: 100vh;
  height: 100vh;
  overflow: hidden;
}

.app-container.left-collapsed {
  grid-template-columns: var(--ribbon-width) 0 1fr var(--sidebar-right-width);
}

.app-container.right-collapsed {
  grid-template-columns: var(--ribbon-width) var(--sidebar-left-width) 1fr 0;
}

.app-container.both-collapsed {
  grid-template-columns: var(--ribbon-width) 0 1fr 0;
}
```

### Glitch Effect Implementation

**Usage Guidelines:**
- Apply to logo (always)
- Apply to primary action buttons (Send, Connect, Generate)
- Apply to active ribbon items
- Apply to active tabs (subtle glow)
- DO NOT apply to body text, forms, or data tables

**CSS Implementation:**
```css
@keyframes glitch {
  0% {
    text-shadow: 0.05em 0 0 var(--glitch-primary), -0.05em -0.025em 0 var(--glitch-secondary);
  }
  14% {
    text-shadow: 0.05em 0 0 var(--glitch-primary), -0.05em -0.025em 0 var(--glitch-secondary);
  }
  15% {
    text-shadow: -0.05em -0.025em 0 var(--glitch-primary), 0.025em 0.025em 0 var(--glitch-secondary);
  }
  49% {
    text-shadow: -0.05em -0.025em 0 var(--glitch-primary), 0.025em 0.025em 0 var(--glitch-secondary);
  }
  50% {
    text-shadow: 0.025em 0.05em 0 var(--glitch-primary), 0.05em 0 0 var(--glitch-secondary);
  }
  99% {
    text-shadow: 0.025em 0.05em 0 var(--glitch-primary), 0.05em 0 0 var(--glitch-secondary);
  }
  100% {
    text-shadow: -0.025em 0 0 var(--glitch-primary), -0.025em -0.025em 0 var(--glitch-secondary);
  }
}

.glitch-hover:hover {
  animation: glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both infinite;
}

.glitch-active {
  animation: glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
}
```

---

## Page Specifications

### Ribbon Navigation Items

1. **Polly Logo** (top)
   - Icon: Zap (⚡) or custom Polly icon
   - Glitch effect on hover
   - Click: Go to general chat

2. **Divider**

3. **Chat** (General/Cross-domain)
   - Icon: MessageSquare
   - Page: General chat view
   - Left panel: All conversations
   - Right panel: Chat

4. **Calendar**
   - Icon: Calendar
   - Page: Calendar view with events
   - Left panel: Mini calendar + upcoming
   - Right panel: Calendar-specific chat

5. **Mail**
   - Icon: Mail
   - Page: Email interface
   - Left panel: Folders/labels
   - Right panel: Mail-specific chat

6. **Code**
   - Icon: Code2
   - Page: Code editor/viewer
   - Left panel: Project tree
   - Right panel: Code-specific chat

7. **Projects**
   - Icon: FolderKanban
   - Page: Project management
   - Left panel: Project list
   - Right panel: Project-specific chat

8. **Knowledge Graph**
   - Icon: Network
   - Page: Graph visualization
   - Left panel: Entity browser
   - Right panel: Knowledge chat

9. **Notes**
   - Icon: BookOpen
   - Page: Note browser/editor
   - Left panel: File explorer
   - Right panel: Notes chat

10. **Learning**
    - Icon: GraduationCap
    - Page: Teaching mode interface
    - Left panel: Curriculum/topics
    - Right panel: Learning chat

11. **Search**
    - Icon: Search
    - Page: Global search results
    - Left panel: Filters/facets
    - Right panel: Search chat

12. **Patterns**
    - Icon: Sparkles
    - Page: Learned patterns view (Phase 13a)
    - Left panel: Pattern categories
    - Right panel: Patterns chat

13. **Domains**
    - Icon: FolderTree
    - Page: Domain management (Phase 1.5)
    - Left panel: Domain list
    - Right panel: Domains chat

14. **Divider**

15. **Settings** (bottom)
    - Icon: Settings
    - Page: Settings with tabs
    - Left panel: Settings navigation
    - Right panel: Settings help chat

---

## File Structure

```
electron-app/src/renderer/
├── index.html (NEW STRUCTURE)
├── app.js (REFACTORED)
├── lucide.min.js (existing)
│
├── components/
│   ├── ribbon.js (NEW)
│   ├── layout.js (NEW)
│   ├── chat-manager.js (NEW)
│   ├── chat-panel.js (NEW)
│   ├── conversation-list.js (NEW)
│   │
│   ├── panels/ (NEW)
│   │   ├── file-explorer.js
│   │   ├── calendar-mini.js
│   │   ├── project-tree.js
│   │   ├── domain-browser.js
│   │   └── search-panel.js
│   │
│   ├── pages/ (NEW)
│   │   ├── chat-page.js
│   │   ├── calendar-page.js
│   │   ├── code-page.js
│   │   ├── projects-page.js
│   │   ├── knowledge-page.js
│   │   ├── notes-page.js
│   │   ├── learning-page.js
│   │   ├── search-page.js
│   │   ├── patterns-page.js
│   │   ├── domains-page.js
│   │   └── settings-page.js
│   │
│   └── ui/ (NEW)
│       ├── button.js
│       ├── card.js
│       ├── input.js
│       ├── badge.js
│       └── modal.js
│
└── styles/
    ├── main.css (existing, will refactor)
    ├── obsidian-theme.css (NEW)
    ├── layout.css (NEW)
    ├── glitch-effects.css (NEW)
    ├── chat.css (NEW)
    ├── panels.css (NEW)
    └── tailwind.css (NEW)
```

---

## Testing Checklist

### Functionality Testing
- [ ] All existing features work
- [ ] Chat with RAG retrieval
- [ ] Page-specific conversations
- [ ] Cross-page context queries
- [ ] Indexing (Obsidian + Code)
- [ ] Integration connections
- [ ] Settings persistence
- [ ] Conversation management
- [ ] Setup wizard

### UI/UX Testing
- [ ] Layout responsive
- [ ] Sidebars collapse/expand smoothly
- [ ] Sidebars resize correctly
- [ ] Page switching smooth
- [ ] Glitch effects visible but subtle
- [ ] All icons render
- [ ] Dark mode colors correct
- [ ] Typography readable
- [ ] Spacing consistent

### Keyboard Testing
- [ ] Cmd+B toggles left sidebar
- [ ] Cmd+/ toggles right sidebar
- [ ] Tab navigation works
- [ ] Ribbon navigation via keyboard
- [ ] Chat input focus shortcuts
- [ ] All modals keyboard-accessible

### Performance Testing
- [ ] Initial load time < 2s
- [ ] Page switching < 200ms
- [ ] Chat rendering smooth
- [ ] Large conversation lists performant
- [ ] Icon rendering optimized
- [ ] No memory leaks

### Accessibility Testing
- [ ] All interactive elements have ARIA labels
- [ ] Screen reader support
- [ ] Keyboard-only navigation
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA
- [ ] No flashing animations > 3Hz

---

## Migration Notes

### What Changes for Users

**Layout:**
- Old: Single sidebar on left, main content on right
- New: Ribbon + two sidebars + main content

**Navigation:**
- Old: Sidebar with text labels
- New: Icon-only ribbon with hover labels

**Chat:**
- Old: Full-page chat view
- New: Right sidebar chat, visible on all pages

**Conversations:**
- Old: Single conversation list
- New: Conversations grouped by page

### What Stays the Same

**Backend:**
- All Python backend code unchanged
- RAG retrieval logic intact
- Integration systems working
- Pattern learning functional
- Domain detection operational

**Features:**
- All existing features preserved
- No functionality removed
- Same keyboard shortcuts (where applicable)
- Same settings structure

### Breaking Changes

**None** - This is a UI-only redesign with full backward compatibility

---

## Success Metrics

### Phase 0.5 Complete When:
1. ✅ Three-column Obsidian-style layout working
2. ✅ Icon-only ribbon with all planned pages
3. ✅ Collapsible/resizable sidebars functional
4. ✅ Page-specific chat system working
5. ✅ Left sidebar adapts to each page
6. ✅ All existing Polly features migrated
7. ✅ Obsidian aesthetic with 5-10% glitch accents
8. ✅ Dark mode polished
9. ✅ Keyboard navigation working
10. ✅ Documentation complete (DESIGN_SYSTEM.md)
11. ✅ All existing functionality preserved
12. ✅ Performance meets targets
13. ✅ Accessibility standards met
14. ✅ User testing feedback positive

---

## Next Steps After Phase 0.5

1. **User Feedback Round** - Gather feedback on new UI
2. **Implement Calendar Page** (Phase 7)
3. **Implement Mail Page** (Phase 8)
4. **Implement Code Page** - Enhanced code viewer/editor
5. **Implement Projects Page** - Project management
6. **Implement Learning Page** (Phase 11)
7. **Continue with remaining roadmap phases**

---

## Resources

### Design References
- Obsidian app (primary inspiration)
- VS Code (sidebar/panel behavior)
- Linear (clean modern UI)
- Notion (page structure)

### Technical References
- Lucide Icons: https://lucide.dev/
- Tailwind CSS: https://tailwindcss.com/
- Electron: https://www.electronjs.org/
- CSS Grid: https://css-tricks.com/snippets/css/complete-guide-grid/

---

**Implementation Status: Day 1 - In Progress**  
**Last Updated:** January 25, 2026
