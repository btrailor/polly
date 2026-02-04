# Phase 0.5: Obsidian-Inspired UI Redesign

**Duration:** 5-7 days  
**Priority:** High (Foundation for all future UI work)  
**Status:** Updated Plan - Obsidian-Inspired with Retro-Brutalist Accents  
**Date:** January 25, 2026

---

## Table of Contents

1. [Vision & Design Philosophy](#vision--design-philosophy)
2. [Design System Overview](#design-system-overview)
3. [Layout Structure](#layout-structure)
4. [Implementation Plan](#implementation-plan)
5. [Component Library](#component-library)
6. [Retro-Brutalist Integration](#retro-brutalist-integration)
7. [Migration Strategy](#migration-strategy)

---

## Vision & Design Philosophy

### The New Polly Aesthetic

**Primary Inspiration:** Obsidian's clean, professional, sidebar-based layout  
**Accent:** Subtle retro-brutalist elements and glitch effects for personality

### Core Principles

1. **Professional First** - Clean, modern, trustworthy interface
2. **Obsidian Familiarity** - Leverage patterns users already know
3. **Subtle Glitch Personality** - Add character without overwhelming
4. **Power User Focused** - Dense information, efficient layouts
5. **Dark Mode Native** - Built for extended use

### Design Philosophy Statement

> "Polly should feel like a professional knowledge tool (like Obsidian) that occasionally winks at you with subtle glitch effects and retro touches. Professional and polished, but with personality."

---

## Design System Overview

### Visual Identity

**Primary Aesthetic:** Clean, minimal, Obsidian-inspired  
**Accent Aesthetic:** Retro-brutalist glitches (5-10% of visual language)

### Color Palette

#### Base Colors (Professional)

```css
/* Dark Mode (Primary) */
--background: #1a1a1a;           /* Near black */
--background-secondary: #242424;  /* Slightly lighter panels */
--background-tertiary: #2d2d2d;   /* Hover states, cards */

--foreground: #e0e0e0;           /* Primary text */
--foreground-muted: #a0a0a0;     /* Secondary text */
--foreground-subtle: #707070;    /* Tertiary text, borders */

--border: #2d2d2d;               /* Subtle borders */
--border-strong: #404040;        /* Emphasized borders */

/* Accent Colors (Primary) */
--accent-primary: #7f6df2;       /* Purple (Obsidian-style) */
--accent-secondary: #00d4ff;     /* Cyan (glitch accent) */
--accent-tertiary: #ff006e;      /* Magenta (glitch accent) */

/* Semantic Colors */
--success: #00ff88;              /* Green (with glitch tint) */
--error: #ff4444;                /* Red */
--warning: #ffaa00;              /* Orange */
--info: #00b4ff;                 /* Blue */
```

#### Glitch Accent Colors (Used Sparingly)

```css
/* Glitch Effects (5-10% usage) */
--glitch-red: #ff006e;
--glitch-cyan: #00d4ff;
--glitch-yellow: #ffff00;
--glitch-green: #00ff88;

/* Retro-Brutalist Accents */
--retro-grid: rgba(0, 255, 136, 0.1);     /* Subtle grid pattern */
--retro-scanline: rgba(0, 212, 255, 0.03); /* Scanline overlay */
--retro-glow: rgba(127, 109, 242, 0.3);    /* Neon glow */
```

### Typography

```css
/* Primary Fonts */
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", "Consolas", monospace;

/* Glitch/Retro Font (Used for logos, headings only) */
--font-display: "Space Grotesk", "Inter", sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### Spacing System

```css
/* Base unit: 4px (Tailwind standard) */
--space-0: 0;
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

### Border Radius

```css
--radius-sm: 3px;    /* Subtle, Obsidian-style */
--radius-md: 6px;    /* Standard cards */
--radius-lg: 8px;    /* Modals, large panels */
--radius-xl: 12px;   /* Feature cards */
--radius-full: 9999px; /* Badges, pills */

/* Glitch variant: sharp corners on occasion */
--radius-none: 0px;  /* Retro-brutalist accent */
```

### Shadows & Elevation

```css
/* Subtle shadows (Obsidian-style) */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
--shadow-md: 0 2px 4px rgba(0, 0, 0, 0.3);
--shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.4);

/* Glitch glow (used sparingly) */
--shadow-glow: 0 0 20px rgba(127, 109, 242, 0.4);
--shadow-glow-cyan: 0 0 20px rgba(0, 212, 255, 0.4);
```

---

## Layout Structure

### Three-Column Obsidian-Inspired Layout

```
┌─────────────────────────────────────────────────────┐
│ [==] Ribbon (40px)  │  Left Pane  │  Main  │  Right │
│  ⚡  Polly Logo      │  (240-400px)│  Area  │  Pane  │
│  ▢  Dashboard        │             │        │(240-400px)
│  💬 Chat             │   File      │ Editor │        │
│  🔍 Search           │   Browser   │  or    │ Panel  │
│  🗂️  Collections     │             │ Chat   │ Area   │
│  📊 Graph            │   Domains   │        │        │
│  📚 Notes            │             │        │ Back-  │
│  💡 Patterns         │   Search    │        │ links  │
│                      │             │        │        │
│  ⚙️  Settings (btm)  │   Recent    │        │ Graph  │
└─────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Ribbon (Left Icon Bar)

**Design:**
- 40px wide vertical strip on far left
- Icon-only buttons with hover tooltips
- Fixed position, always visible
- Dark background with subtle gradient
- Polly logo at top
- Settings icon at bottom
- Subtle glitch effect on hover

**Icons:**
```typescript
const ribbonItems = [
  { icon: "⚡", label: "Dashboard", path: "/" },
  { icon: "💬", label: "Chat", path: "/chat" },
  { icon: "🔍", label: "Search", path: "/search" },
  { icon: "🗂️", label: "Collections", path: "/collections" },
  { icon: "📊", label: "Graph", path: "/graph" },
  { icon: "📚", label: "Notes", path: "/notes" },
  { icon: "💡", label: "Patterns", path: "/patterns" },
  // ... more items
  { icon: "⚙️", label: "Settings", path: "/settings", position: "bottom" }
]
```

**Hover Effect (Glitch Accent):**
```css
.ribbon-item:hover {
  background: linear-gradient(135deg, 
    rgba(127, 109, 242, 0.2) 0%, 
    rgba(0, 212, 255, 0.1) 100%);
  box-shadow: inset 2px 0 0 var(--accent-primary);
  
  /* Subtle glitch on hover */
  animation: glitch-pulse 0.3s ease-in-out;
}

@keyframes glitch-pulse {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-1px); }
  75% { transform: translateX(1px); }
}
```

#### 2. Left Sidebar Pane

**Design:**
- 240-400px wide (resizable)
- Collapsible via ribbon icon click
- Smooth slide-in/out animation
- Contains tabbed content
- File browser, search, domains, etc.

**Structure:**
```typescript
<LeftSidebar isOpen={leftSidebarOpen} width={leftSidebarWidth}>
  <Tabs defaultValue="files">
    <TabsList>
      <TabsTrigger value="files">Files</TabsTrigger>
      <TabsTrigger value="search">Search</TabsTrigger>
      <TabsTrigger value="domains">Domains</TabsTrigger>
      <TabsTrigger value="recent">Recent</TabsTrigger>
    </TabsList>
    
    <TabsContent value="files">
      <FileExplorer />
    </TabsContent>
    
    <TabsContent value="search">
      <SearchPanel />
    </TabsContent>
    
    {/* ... more tabs */}
  </Tabs>
</LeftSidebar>
```

**Styling:**
```css
.left-sidebar {
  background: var(--background-secondary);
  border-right: 1px solid var(--border);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  /* Subtle grid pattern (retro accent) */
  background-image: 
    linear-gradient(rgba(0, 255, 136, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 136, 0.02) 1px, transparent 1px);
  background-size: 20px 20px;
}
```

#### 3. Main Content Area

**Design:**
- Flexible width (fills remaining space)
- Context-dependent content (chat, editor, graph, etc.)
- Tabbed interface for multiple views
- Smooth transitions between views

**Structure:**
```typescript
<MainContent>
  <TabsContainer>
    <Tab id="chat-1" title="Chat" icon="💬">
      <ChatInterface />
    </Tab>
    <Tab id="note-1" title="Project Notes.md" icon="📝">
      <NoteEditor />
    </Tab>
    <Tab id="graph-1" title="Knowledge Graph" icon="📊">
      <GraphView />
    </Tab>
  </TabsContainer>
</MainContent>
```

#### 4. Right Sidebar Pane

**Design:**
- 240-400px wide (resizable)
- Collapsible independently
- Context-aware content
- Backlinks, outline, metadata, etc.

**Content:**
```typescript
<RightSidebar isOpen={rightSidebarOpen} width={rightSidebarWidth}>
  <Tabs defaultValue="backlinks">
    <TabsList>
      <TabsTrigger value="backlinks">Backlinks</TabsTrigger>
      <TabsTrigger value="outline">Outline</TabsTrigger>
      <TabsTrigger value="graph">Local Graph</TabsTrigger>
      <TabsTrigger value="metadata">Info</TabsTrigger>
    </TabsList>
    
    <TabsContent value="backlinks">
      <BacklinksPanel />
    </TabsContent>
    
    {/* ... more tabs */}
  </Tabs>
</RightSidebar>
```

---

## Implementation Plan

### Day 1: Layout Foundation & Ribbon (1 day)

**Goal:** Create the Obsidian-style three-column layout with ribbon

#### Tasks

**1. Create Layout Components**

```typescript
// src/components/layout/AppLayout.tsx
export function AppLayout({ children }: { children: React.ReactNode }) {
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(280)
  const [rightSidebarWidth, setRightSidebarWidth] = useState(280)
  
  return (
    <div className="app-layout">
      <Ribbon 
        onItemClick={(item) => handleRibbonClick(item)}
        activeItem={activeRibbonItem}
      />
      
      <LeftSidebar 
        isOpen={leftSidebarOpen}
        width={leftSidebarWidth}
        onResize={setLeftSidebarWidth}
        onToggle={() => setLeftSidebarOpen(!leftSidebarOpen)}
      />
      
      <MainContent>
        {children}
      </MainContent>
      
      <RightSidebar
        isOpen={rightSidebarOpen}
        width={rightSidebarWidth}
        onResize={setRightSidebarWidth}
        onToggle={() => setRightSidebarOpen(!rightSidebarOpen)}
      />
    </div>
  )
}
```

**2. Build Ribbon Component**

```typescript
// src/components/layout/Ribbon.tsx
interface RibbonItem {
  id: string
  icon: string | React.ReactNode
  label: string
  path?: string
  position?: 'top' | 'bottom'
  onClick?: () => void
}

export function Ribbon({ onItemClick, activeItem }: RibbonProps) {
  const items: RibbonItem[] = [
    { id: 'dashboard', icon: '⚡', label: 'Dashboard', path: '/' },
    { id: 'chat', icon: '💬', label: 'Chat', path: '/chat' },
    { id: 'search', icon: '🔍', label: 'Search', path: '/search' },
    { id: 'collections', icon: '🗂️', label: 'Collections', path: '/collections' },
    { id: 'graph', icon: '📊', label: 'Graph', path: '/graph' },
    { id: 'notes', icon: '📚', label: 'Notes', path: '/notes' },
    { id: 'patterns', icon: '💡', label: 'Patterns', path: '/patterns' },
    { id: 'settings', icon: '⚙️', label: 'Settings', path: '/settings', position: 'bottom' },
  ]
  
  const topItems = items.filter(i => i.position !== 'bottom')
  const bottomItems = items.filter(i => i.position === 'bottom')
  
  return (
    <div className="ribbon">
      <div className="ribbon-logo">
        <PollyLogo className="logo-glitch" />
      </div>
      
      <nav className="ribbon-items-top">
        {topItems.map(item => (
          <RibbonButton
            key={item.id}
            item={item}
            isActive={activeItem === item.id}
            onClick={() => onItemClick(item)}
          />
        ))}
      </nav>
      
      <nav className="ribbon-items-bottom">
        {bottomItems.map(item => (
          <RibbonButton
            key={item.id}
            item={item}
            isActive={activeItem === item.id}
            onClick={() => onItemClick(item)}
          />
        ))}
      </nav>
    </div>
  )
}
```

**3. Ribbon Styling with Glitch Accents**

```css
/* src/styles/ribbon.css */
.ribbon {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 40px;
  background: linear-gradient(180deg, 
    var(--background) 0%, 
    var(--background-secondary) 100%);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  
  /* Subtle scanline effect */
  background-image: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 212, 255, 0.02) 2px,
    rgba(0, 212, 255, 0.02) 4px
  );
}

.ribbon-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--border);
  padding: var(--space-2);
}

.logo-glitch {
  width: 28px;
  height: 28px;
  filter: drop-shadow(0 0 4px rgba(127, 109, 242, 0.5));
  transition: filter 0.3s ease;
}

.logo-glitch:hover {
  animation: logo-glitch 0.5s ease-in-out;
  filter: drop-shadow(0 0 8px rgba(127, 109, 242, 0.8));
}

@keyframes logo-glitch {
  0%, 100% { transform: translate(0, 0); filter: hue-rotate(0deg); }
  10% { transform: translate(-2px, 0); filter: hue-rotate(180deg); }
  20% { transform: translate(2px, 0); filter: hue-rotate(-180deg); }
  30% { transform: translate(0, 0); filter: hue-rotate(0deg); }
}

.ribbon-items-top {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-1) 0;
  gap: var(--space-1);
}

.ribbon-items-bottom {
  display: flex;
  flex-direction: column;
  padding: var(--space-1) 0;
  gap: var(--space-1);
  border-top: 1px solid var(--border);
}

.ribbon-button {
  position: relative;
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--foreground-muted);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ribbon-button:hover {
  color: var(--accent-primary);
  background: linear-gradient(135deg, 
    rgba(127, 109, 242, 0.15) 0%, 
    rgba(0, 212, 255, 0.05) 100%);
  
  /* Glitch accent line */
  box-shadow: inset 2px 0 0 var(--accent-primary);
}

.ribbon-button:hover::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 2px;
  height: 100%;
  background: linear-gradient(180deg,
    var(--glitch-cyan),
    var(--accent-primary),
    var(--glitch-red)
  );
  animation: glow-pulse 1.5s ease-in-out infinite;
}

.ribbon-button.active {
  color: var(--accent-primary);
  background: rgba(127, 109, 242, 0.2);
  box-shadow: inset 2px 0 0 var(--accent-primary);
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Tooltip */
.ribbon-button .tooltip {
  position: absolute;
  left: 48px;
  background: var(--background-tertiary);
  color: var(--foreground);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-strong);
  z-index: 1000;
}

.ribbon-button:hover .tooltip {
  opacity: 1;
  transform: translateX(0);
}
```

**Success Criteria:**
- ✅ Three-column layout renders correctly
- ✅ Ribbon displays all icons with tooltips
- ✅ Logo has subtle glitch effect on hover
- ✅ Active states work properly
- ✅ Responsive to window resize

---

### Day 2: Collapsible Sidebars & Resize (1 day)

**Goal:** Implement Obsidian-style collapsible and resizable sidebars

#### Tasks

**1. Left Sidebar with Collapse/Expand**

```typescript
// src/components/layout/LeftSidebar.tsx
export function LeftSidebar({ isOpen, width, onResize, onToggle, children }: LeftSidebarProps) {
  const [isResizing, setIsResizing] = useState(false)
  
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true)
    e.preventDefault()
  }
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return
      
      const newWidth = e.clientX - 40 // 40px for ribbon
      if (newWidth >= 240 && newWidth <= 600) {
        onResize(newWidth)
      }
    }
    
    const handleMouseUp = () => {
      setIsResizing(false)
    }
    
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizing, onResize])
  
  return (
    <div 
      className={cn("left-sidebar", { "collapsed": !isOpen })}
      style={{ width: isOpen ? `${width}px` : '0px' }}
    >
      <div className="sidebar-content">
        {children}
      </div>
      
      {isOpen && (
        <div 
          className="resize-handle"
          onMouseDown={handleMouseDown}
        />
      )}
    </div>
  )
}
```

**2. Resize Handle Styling**

```css
.left-sidebar {
  position: fixed;
  left: 40px; /* After ribbon */
  top: 0;
  bottom: 0;
  background: var(--background-secondary);
  border-right: 1px solid var(--border);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  
  /* Subtle retro grid pattern */
  background-image: 
    linear-gradient(var(--retro-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--retro-grid) 1px, transparent 1px);
  background-size: 20px 20px;
}

.left-sidebar.collapsed {
  width: 0 !important;
  border-right: none;
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

.resize-handle {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: transparent;
  cursor: ew-resize;
  transition: background 0.2s ease;
  z-index: 10;
}

.resize-handle:hover {
  background: var(--accent-primary);
  box-shadow: 0 0 8px var(--accent-primary);
}

.resize-handle::before {
  content: '';
  position: absolute;
  left: -2px;
  top: 0;
  bottom: 0;
  width: 8px;
}
```

**3. Right Sidebar (Similar Implementation)**

```typescript
// src/components/layout/RightSidebar.tsx
export function RightSidebar({ isOpen, width, onResize, onToggle, children }: RightSidebarProps) {
  // Similar implementation to LeftSidebar but mirrored
  // Resize handle on left side instead of right
  // Position: fixed; right: 0;
}
```

**Success Criteria:**
- ✅ Sidebars collapse/expand smoothly
- ✅ Resize handles work correctly
- ✅ Width constraints enforced (240px - 600px)
- ✅ Resize cursor shows on hover
- ✅ Layout adjusts when sidebars toggle

---

### Day 3: Tab System & Navigation (1 day)

**Goal:** Implement Obsidian-style tab navigation for main content area

#### Tasks

**1. Tab Container Component**

```typescript
// src/components/layout/TabContainer.tsx
interface Tab {
  id: string
  title: string
  icon?: string | React.ReactNode
  content: React.ReactNode
  closeable?: boolean
  modified?: boolean
}

export function TabContainer({ tabs, activeTab, onTabChange, onTabClose }: TabContainerProps) {
  return (
    <div className="tab-container">
      <div className="tab-bar">
        {tabs.map(tab => (
          <TabButton
            key={tab.id}
            tab={tab}
            isActive={activeTab === tab.id}
            onClick={() => onTabChange(tab.id)}
            onClose={() => onTabClose?.(tab.id)}
          />
        ))}
        
        <button className="tab-new" onClick={onNewTab}>
          <PlusIcon />
        </button>
      </div>
      
      <div className="tab-content">
        {tabs.find(t => t.id === activeTab)?.content}
      </div>
    </div>
  )
}
```

**2. Tab Styling with Glitch Accents**

```css
.tab-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--background);
}

.tab-bar {
  display: flex;
  align-items: center;
  height: 40px;
  background: var(--background-secondary);
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  overflow-y: hidden;
  
  /* Hide scrollbar but keep functionality */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tab-bar::-webkit-scrollbar {
  display: none;
}

.tab-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 100%;
  padding: 0 var(--space-4);
  background: transparent;
  border: none;
  border-right: 1px solid var(--border);
  color: var(--foreground-muted);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-button:hover {
  background: var(--background-tertiary);
  color: var(--foreground);
}

.tab-button.active {
  background: var(--background);
  color: var(--foreground);
  border-bottom: 2px solid var(--accent-primary);
  
  /* Subtle glitch effect on active tab */
  box-shadow: 
    0 0 10px rgba(127, 109, 242, 0.2),
    inset 0 -2px 0 var(--accent-primary);
}

.tab-button.modified::after {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-secondary);
  box-shadow: 0 0 6px var(--accent-secondary);
}

.tab-icon {
  font-size: 16px;
}

.tab-close {
  margin-left: var(--space-1);
  padding: var(--space-1);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tab-button:hover .tab-close {
  opacity: 1;
}

.tab-close:hover {
  color: var(--error);
}

.tab-new {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 100%;
  background: transparent;
  border: none;
  color: var(--foreground-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-new:hover {
  background: var(--background-tertiary);
  color: var(--accent-primary);
}

.tab-content {
  flex: 1;
  overflow: auto;
  background: var(--background);
}
```

**Success Criteria:**
- ✅ Multiple tabs can be open
- ✅ Tab switching works smoothly
- ✅ Close buttons appear on hover
- ✅ Active tab visually distinct
- ✅ Modified indicator shows when needed

---

### Day 4: Shadcn Components + Glitch Variants (1 day)

**Goal:** Install Shadcn components and create glitch-accented variants

#### Tasks

**1. Install Core Shadcn Components**

```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card dialog tabs select textarea badge separator tooltip dropdown-menu scroll-area
```

**2. Create Glitch Button Variant**

```typescript
// src/components/ui/button.tsx (extend Shadcn button)
const buttonVariants = cva(
  "...", // base styles
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        // ... other Shadcn variants
        
        // New glitch variants
        glitch: cn(
          "bg-gradient-to-r from-accent-primary to-accent-secondary",
          "text-white font-medium",
          "hover:shadow-glow transition-all duration-200",
          "relative overflow-hidden",
          // Glitch animation on hover
          "hover:before:content-[''] hover:before:absolute hover:before:inset-0",
          "hover:before:bg-glitch-overlay hover:before:animate-glitch"
        ),
        
        retro: cn(
          "bg-background-tertiary",
          "border-2 border-accent-primary",
          "text-accent-primary font-mono font-bold",
          "hover:bg-accent-primary hover:text-background",
          "transition-all duration-200",
          "shadow-[4px_4px_0px_0px_rgba(127,109,242,0.3)]",
          "hover:shadow-[2px_2px_0px_0px_rgba(127,109,242,0.5)]",
          "hover:translate-x-[2px] hover:translate-y-[2px]"
        ),
      },
    },
  }
)
```

**3. Glitch CSS Animations**

```css
/* src/styles/glitch-effects.css */

/* Glitch text effect (used sparingly) */
.glitch-text {
  position: relative;
  display: inline-block;
}

.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
}

.glitch-text:hover::before {
  animation: glitch-1 0.3s ease-in-out;
  color: var(--glitch-cyan);
  transform: translate(-2px, 0);
  clip-path: inset(0 0 0 0);
}

.glitch-text:hover::after {
  animation: glitch-2 0.3s ease-in-out;
  color: var(--glitch-red);
  transform: translate(2px, 0);
  clip-path: inset(0 0 0 0);
}

@keyframes glitch-1 {
  0%, 100% { 
    opacity: 0; 
    transform: translate(0, 0); 
  }
  33% { 
    opacity: 0.8; 
    transform: translate(-3px, 0); 
  }
  66% { 
    opacity: 0.6; 
    transform: translate(3px, 0); 
  }
}

@keyframes glitch-2 {
  0%, 100% { 
    opacity: 0; 
    transform: translate(0, 0); 
  }
  33% { 
    opacity: 0.6; 
    transform: translate(2px, 0); 
  }
  66% { 
    opacity: 0.8; 
    transform: translate(-2px, 0); 
  }
}

/* Scanline overlay */
.scanlines {
  position: relative;
  overflow: hidden;
}

.scanlines::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    var(--retro-scanline) 2px,
    var(--retro-scanline) 4px
  );
  pointer-events: none;
  z-index: 1;
}

/* CRT glow effect */
.crt-glow {
  text-shadow: 
    0 0 10px var(--retro-glow),
    0 0 20px var(--retro-glow),
    0 0 30px var(--retro-glow);
}

/* Grid background (subtle) */
.retro-grid {
  background-image: 
    linear-gradient(var(--retro-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--retro-grid) 1px, transparent 1px);
  background-size: 20px 20px;
}

/* Terminal-style text */
.terminal-text {
  font-family: var(--font-mono);
  color: var(--success);
  text-shadow: 0 0 5px var(--success);
  letter-spacing: 0.05em;
}

/* Pixelated border (retro-brutalist) */
.pixelated-border {
  border: 2px solid var(--accent-primary);
  box-shadow: 
    4px 0 0 var(--accent-primary),
    0 4px 0 var(--accent-primary),
    4px 4px 0 var(--accent-primary),
    -4px 0 0 var(--accent-primary),
    0 -4px 0 var(--accent-primary),
    -4px -4px 0 var(--accent-primary);
}
```

**Success Criteria:**
- ✅ All Shadcn components installed
- ✅ Glitch button variant works
- ✅ Retro button variant works
- ✅ CSS animations smooth
- ✅ Effects used sparingly (5-10% of UI)

---

### Day 5: Update Existing Components (1 day)

**Goal:** Apply new design system to high-visibility components

#### Components to Update

**1. Navigation/Header**
- Replace with new ribbon + sidebars
- Update settings button to use new icon
- Add dark mode toggle with glitch effect

**2. Integration Cards**
- Use new `Card` component with subtle grid background
- Add status indicators with glow effects
- Update buttons to use new variants

**3. Chat Interface**
- Keep clean Obsidian aesthetic
- Add subtle scanlines to message container (very subtle)
- Update input field styling
- Glitch effect on "Send" button only

**4. Settings Panel**
- Use Shadcn tabs, inputs, selects
- Clean, professional layout
- Glitch accents only on section headers

**Success Criteria:**
- ✅ All updated components look professional
- ✅ Glitch effects subtle, not overwhelming
- ✅ Obsidian aesthetic maintained
- ✅ No regressions in functionality

---

### Day 6: File Explorer & Search Panel (1 day)

**Goal:** Build Obsidian-style file explorer and search

#### Tasks

**1. File Explorer Component**

```typescript
// src/components/panels/FileExplorer.tsx
interface FileNode {
  id: string
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
  icon?: string
  modified?: Date
}

export function FileExplorer({ files, onFileClick }: FileExplorerProps) {
  return (
    <div className="file-explorer">
      <div className="explorer-header">
        <h3 className="explorer-title">Files</h3>
        <div className="explorer-actions">
          <button className="icon-button" title="New file">
            <FileIcon />
          </button>
          <button className="icon-button" title="New folder">
            <FolderIcon />
          </button>
        </div>
      </div>
      
      <ScrollArea className="explorer-content">
        <FileTree nodes={files} onNodeClick={onFileClick} />
      </ScrollArea>
    </div>
  )
}
```

**2. File Tree Styling**

```css
.file-explorer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.explorer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border);
}

.explorer-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--foreground-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.explorer-actions {
  display: flex;
  gap: var(--space-1);
}

.icon-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--foreground-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-button:hover {
  background: var(--background-tertiary);
  color: var(--accent-primary);
}

.file-tree-node {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 2px solid transparent;
}

.file-tree-node:hover {
  background: var(--background-tertiary);
  border-left-color: var(--accent-primary);
}

.file-tree-node.active {
  background: rgba(127, 109, 242, 0.2);
  border-left-color: var(--accent-primary);
  color: var(--accent-primary);
}

.file-tree-node .icon {
  font-size: 16px;
  opacity: 0.7;
}

.file-tree-node .name {
  flex: 1;
  font-size: var(--text-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-tree-node.folder {
  font-weight: 500;
}

/* Indent levels */
.file-tree-node[data-depth="1"] { padding-left: calc(var(--space-3) + 20px); }
.file-tree-node[data-depth="2"] { padding-left: calc(var(--space-3) + 40px); }
.file-tree-node[data-depth="3"] { padding-left: calc(var(--space-3) + 60px); }
```

**3. Search Panel**

```typescript
// src/components/panels/SearchPanel.tsx
export function SearchPanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  
  return (
    <div className="search-panel">
      <div className="search-header">
        <Input
          type="search"
          placeholder="Search notes..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />
      </div>
      
      <ScrollArea className="search-results">
        {results.map(result => (
          <SearchResultItem key={result.id} result={result} />
        ))}
      </ScrollArea>
    </div>
  )
}
```

**Success Criteria:**
- ✅ File explorer works like Obsidian
- ✅ Folders expand/collapse smoothly
- ✅ Search panel functional
- ✅ Keyboard navigation works
- ✅ Clean, professional styling

---

### Day 7: Polish, Testing & Documentation (1 day)

**Goal:** Final polish, test everything, document design system

#### Tasks

**1. Polish Pass**
- Adjust spacing inconsistencies
- Fine-tune animations
- Test all glitch effects
- Ensure glitch accents are subtle (5-10% usage)

**2. Testing**
- Light/dark mode
- Sidebar collapse/expand
- Resize functionality
- Tab navigation
- Keyboard shortcuts
- Cross-browser (Chrome, Safari)

**3. Documentation**
- Update DESIGN_SYSTEM.md
- Document when to use glitch effects
- Component usage examples
- Color palette reference
- Spacing guidelines

**Success Criteria:**
- ✅ All components polished
- ✅ No bugs or regressions
- ✅ Documentation complete
- ✅ Design system ready for Phases 1.5+

---

## Retro-Brutalist Integration

### Where to Use Glitch/Retro Elements (5-10% of UI)

#### ✅ Appropriate Uses

1. **Logo & Branding**
   - Polly logo in ribbon (glitch on hover)
   - Loading screens (glitch animation)
   - Splash screens

2. **Accent Highlights**
   - Active tab bottom border (subtle glow)
   - Ribbon item hover (glitch line)
   - Button hover states (primary actions only)
   - Status indicators (success/error with glow)

3. **Section Headers**
   - H1/H2 headings (optional glitch text effect)
   - Panel titles (subtle scanlines in background)

4. **Special Actions**
   - "Send" button in chat (glitch variant)
   - "Connect" button for integrations (retro variant)
   - "Generate" or "Analyze" actions (glitch accent)

#### ❌ Avoid Overuse

1. **Body Text** - Keep clean and readable
2. **Form Inputs** - Professional only
3. **Data Tables** - Clean, no effects
4. **Navigation** - Subtle accents only
5. **Backgrounds** - Minimal grid patterns

### Glitch Effect Guidelines

```typescript
// When to use each effect
const glitchUsage = {
  // High-impact, rare (< 1% of UI)
  glitchAnimation: [
    'Logo on hover',
    'Loading screens',
    'Major error states'
  ],
  
  // Medium-impact, occasional (2-3% of UI)
  glitchText: [
    'Section headers',
    'Feature callouts',
    'Welcome messages'
  ],
  
  // Low-impact, common (5-10% of UI)
  glitchAccents: [
    'Active states',
    'Hover effects',
    'Status indicators',
    'CTA buttons'
  ],
  
  // Subtle, pervasive (throughout)
  subtleEffects: [
    'Grid backgrounds',
    'Scanlines',
    'Glow on interactive elements'
  ]
}
```

---

## Success Criteria

### By End of Phase 0.5

✅ **Layout Foundation**
- Three-column Obsidian-style layout
- Ribbon with icon-only navigation
- Collapsible left/right sidebars
- Resizable sidebar widths
- Tab-based main content area

✅ **Design System**
- Professional color palette defined
- Typography system documented
- Spacing system consistent
- Component library established

✅ **Shadcn Integration**
- All core components installed
- Glitch/retro variants created
- Custom Polly components built

✅ **Glitch/Retro Accents**
- Used sparingly (5-10% of UI)
- Subtle and professional
- Enhance rather than distract
- Document when/where to use

✅ **High-Visibility Updates**
- Ribbon navigation working
- File explorer Obsidian-style
- Settings panel updated
- Integration cards redesigned

✅ **Documentation**
- DESIGN_SYSTEM.md complete
- Component usage documented
- Glitch effect guidelines written
- Color palette reference

---

## Migration Strategy

### Phase 0.5 Focus (This Phase)

**Update Immediately:**
- Layout structure (ribbon + sidebars)
- Navigation system
- File explorer
- Search panel
- Settings UI
- Integration cards

**Create Foundation:**
- Design system documentation
- Component library
- CSS variables
- Animation utilities

### Phases 1.5-17 (Gradual Application)

**For Each New Feature:**
1. Use Obsidian-inspired layout by default
2. Apply design system components
3. Add glitch accents only where appropriate (5-10%)
4. Document new patterns if needed

**Examples:**

**Phase 12 (Knowledge Graph):**
- Use sidebar for graph controls
- Clean Obsidian aesthetic for node details
- Subtle glow effect on active nodes only
- Glitch effect on "Analyze Connections" button

**Phase 16 (Native Notes):**
- File explorer in left sidebar (already built)
- Note editor in main area (clean, no effects)
- Backlinks in right sidebar (clean)
- Glitch accent on "Create Note" button only

### After Tier 1 (UI Polish Sprint)

**Final Consistency Pass:**
- Update any remaining old components
- Ensure glitch effects consistent across app
- Polish animations
- Fine-tune spacing
- Accessibility audit

---

## Technical Notes

### CSS Architecture

```
src/styles/
├── globals.css           # Tailwind + CSS variables
├── layout.css            # Ribbon, sidebars, tabs
├── components.css        # Component-specific styles
├── glitch-effects.css    # Glitch/retro animations (separate file)
└── obsidian-theme.css    # Obsidian-inspired base theme
```

### Component Organization

```
src/components/
├── layout/
│   ├── AppLayout.tsx
│   ├── Ribbon.tsx
│   ├── LeftSidebar.tsx
│   ├── RightSidebar.tsx
│   └── TabContainer.tsx
├── panels/
│   ├── FileExplorer.tsx
│   ├── SearchPanel.tsx
│   ├── DomainsPanel.tsx
│   └── RecentPanel.tsx
├── ui/                   # Shadcn components + custom
│   ├── button.tsx        # Extended with glitch variant
│   ├── card.tsx
│   ├── input.tsx
│   └── ... (more Shadcn)
└── glitch/               # Glitch-specific components
    ├── GlitchText.tsx
    ├── GlitchButton.tsx
    └── PollyLogo.tsx
```

### Design Tokens

All design tokens should be defined as CSS variables:

```css
:root {
  /* Obsidian-inspired base */
  --background: #1a1a1a;
  --foreground: #e0e0e0;
  /* ... more tokens */
  
  /* Glitch accents */
  --glitch-red: #ff006e;
  --glitch-cyan: #00d4ff;
  /* ... glitch palette */
}
```

This allows themes to override colors without changing component code.

---

## Next Steps After Phase 0.5

1. **Phase 1.5 (Domain Configuration)**
   - Use new layout system
   - Apply design system components
   - Add subtle glitch to domain cards

2. **Future Phases**
   - Build on Obsidian foundation
   - Maintain 90/10 split (professional/glitch)
   - Iterate based on user feedback

3. **Community Themes**
   - Design system supports theming
   - Users can create custom themes
   - Glitch effects can be disabled via settings

---

**Document Status:** Complete  
**Last Updated:** January 25, 2026  
**Next Phase:** Implement Phase 0.5 according to this plan
