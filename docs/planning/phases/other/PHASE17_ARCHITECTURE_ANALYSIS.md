# Phase 17: Architecture Analysis - Activity Bar to Ribbon

**Date:** February 4, 2026  
**Status:** In Progress  
**Purpose:** Analyze VSCode's activity bar implementation to plan ribbon replacement

---

## Activity Bar Architecture

### Core Components

**1. ActivitybarPart** (`src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`)
- Extends `Part` base class
- Fixed width: 48px
- Fixed height: flexible (0 to infinity)
- Manages `PaneCompositeBar` for icon rendering

**2. ActivityBarCompositeBar** (extends `PaneCompositeBar`)
- Handles icon rendering and interaction
- Vertical orientation
- Icon size: 24px
- Action height: 48px
- Manages view containers (Explorer, Search, Git, Debug, etc.)

**3. PaneCompositeBar** (`src/vs/workbench/browser/parts/paneCompositeBar.ts`)
- Generic composite bar for managing panel views
- Handles pinning, ordering, visibility
- Integrates with view container system
- Supports drag-and-drop reordering

### Key Integration Points

**Workbench Integration:**
- Registered in `workbench.ts` with `Parts.ACTIVITYBAR_PART`
- Created by `SidebarPart` (line 308 in sidebarPart.ts)
- Managed by `Layout` class for positioning

**View Container System:**
- Uses `IViewDescriptorService` to discover views
- Integrates with `IViewsService` to show/hide views
- Supports extension-based view containers

**Storage:**
- Pinned containers: `workbench.activity.pinnedViewlets2`
- Placeholder containers: `workbench.activity.placeholderViewlets`
- Workspace state: `workbench.activity.viewletsWorkspaceState`

---

## Current Activity Bar Structure

### HTML Structure (from CSS analysis)
```html
<div class="part activitybar left">
  <div class="content">
    <!-- Menu bar (if compact) -->
    <div class="menubar">...</div>
    
    <!-- Composite bar (icons) -->
    <div class="monaco-action-bar composite-bar">
      <!-- Activity icons -->
    </div>
    
    <!-- Global composite bar (bottom) -->
    <div class="global-composite-bar">...</div>
  </div>
</div>
```

### CSS Structure
- Width: 48px (fixed)
- Height: 100% (flexible)
- Flexbox layout: column, space-between
- Icons: 24px size, 48px action height
- Vertical orientation

---

## Ribbon Replacement Strategy

### Approach: Replace ActivitybarPart with RibbonPart

**Option 1: Direct Replacement (Recommended)**
- Create `RibbonPart` extending `Part`
- Replace `ActivitybarPart` registration
- Keep `PaneCompositeBar` functionality (or adapt it)
- Maintain view container integration

**Option 2: Modify ActivitybarPart**
- Rename to `RibbonPart`
- Modify styling and layout
- Keep existing functionality
- Less clean but faster

**Option 3: Extension-Based**
- Create ribbon as extension
- Hide activity bar
- Add ribbon as custom view
- More complex, less integrated

### Recommended: Option 1

**Why:**
- Clean separation
- Maintains VSCode patterns
- Easier to maintain
- Clear integration points

---

## Implementation Plan

### Step 1: Create RibbonPart

**File:** `polly-integrations/ribbon/ribbonPart.ts`

**Key Features:**
- Extends `Part` (like ActivitybarPart)
- Same dimensions (48px width)
- Uses `PaneCompositeBar` for icon management
- Integrates with Polly's ribbon navigation

**Differences from Activity Bar:**
- Icons map to Polly pages (Dashboard, Knowledge, Notes, Code, etc.)
- Clicking icon switches Polly context (not just VSCode view)
- Maintains VSCode view containers for Code workspace

### Step 2: Register RibbonPart

**Modify:** `src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`

**Changes:**
- Replace `ActivitybarPart` with `RibbonPart`
- Keep same integration pattern
- Maintain view container support

### Step 3: Integrate Polly Navigation

**Create:** `polly-integrations/ribbon/pollyNavigation.ts`

**Features:**
- Maps Polly pages to ribbon icons
- Handles page switching
- Integrates with Polly's existing navigation
- Maintains VSCode views for Code workspace

### Step 4: Update Styling

**Create:** `polly-integrations/ribbon/ribbon.css`

**Features:**
- Match Polly's ribbon design
- Small, sleek icons (16-18px)
- Horizontal icon navigation in panels (future)
- Maintains 48px width for ribbon itself

---

## Key Technical Details

### Part Registration

**Current:**
```typescript
// In sidebarPart.ts
private readonly activityBarPart = this._register(
  this.instantiationService.createInstance(ActivitybarPart, this)
);
```

**New:**
```typescript
// In sidebarPart.ts
private readonly ribbonPart = this._register(
  this.instantiationService.createInstance(RibbonPart, this)
);
```

### View Container Integration

**Current:**
- Activity bar shows VSCode view containers (Explorer, Search, Git, etc.)
- Clicking icon opens corresponding view in sidebar

**New:**
- Ribbon shows Polly pages (Dashboard, Knowledge, Notes, Code, etc.)
- Clicking icon switches Polly context
- For Code workspace: Also shows VSCode view containers in left panel

### Panel System

**Current:**
- Left panel shows view container content
- Right panel shows secondary views (Problems, Output, Terminal)

**Future (After Ribbon):**
- Left panel: Contextual content per Polly page
  - Code: File explorer, Search, Git, Debug (with horizontal icon nav)
  - Notes: Files, Tags, Search (with horizontal icon nav)
  - Knowledge: Sources, Domains, Indexing (with horizontal icon nav)
- Right panel: Chat, RAG, Personas (with horizontal icon nav)

---

## Integration Points

### 1. Workbench Layout

**File:** `src/vs/workbench/browser/layout.ts`

**Changes:**
- Update part references from `ACTIVITYBAR_PART` to `RIBBON_PART`
- Maintain same layout calculations
- Keep width at 48px

### 2. Sidebar Part

**File:** `src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`

**Changes:**
- Replace ActivitybarPart with RibbonPart
- Update pinned containers key references
- Maintain view container integration

### 3. Workbench HTML

**Location:** Generated in `workbench.ts`

**Changes:**
- Update part ID from `ACTIVITYBAR_PART` to `RIBBON_PART`
- Update CSS classes from `activitybar` to `ribbon`
- Maintain same DOM structure

---

## Next Steps

1. **Create RibbonPart skeleton**
   - Basic class structure
   - Extend Part
   - Register in workbench

2. **Port Polly ribbon**
   - Copy ribbon CSS/HTML from electron-app
   - Adapt to VSCode patterns
   - Integrate with PaneCompositeBar

3. **Test integration**
   - Verify ribbon appears
   - Test page switching
   - Ensure VSCode views still work

4. **Add horizontal icon navigation**
   - Implement in left panel
   - Small, sleek icons
   - Contextual per page

---

## Questions to Resolve

1. **How to handle Code workspace views?**
   - Should ribbon show both Polly pages AND VSCode views?
   - Or separate: Ribbon for pages, horizontal icons for Code views?

2. **Navigation flow:**
   - Click ribbon icon → Switch Polly page
   - In Code page → Horizontal icons switch VSCode views
   - Is this the right model?

3. **View container persistence:**
   - How to maintain VSCode view state when switching Polly pages?
   - Should view containers be page-specific?

---

**Status:** Architecture analysis complete, ready for implementation planning
