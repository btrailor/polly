# Phase 17: Architecture Study Summary

**Date:** February 4, 2026  
**Status:** Complete  
**Purpose:** Summary of architecture analysis for ribbon integration

---

## Key Findings

### Activity Bar Architecture

**Core Class:** `ActivitybarPart` extends `Part`
- Fixed width: 48px
- Flexible height
- Manages `PaneCompositeBar` for icons
- Registered as `Parts.ACTIVITYBAR_PART`

**Integration:**
- Created by `SidebarPart` (line 66 in sidebarPart.ts)
- Registered in workbench layout system
- Uses view container system for VSCode views

**Icon Management:**
- `ActivityBarCompositeBar` extends `PaneCompositeBar`
- Vertical orientation
- Icon size: 24px
- Action height: 48px
- Manages view containers (Explorer, Search, Git, etc.)

### Part Base Class

**Key Methods:**
- `create(parent, options)` - Called by workbench
- `createContentArea(parent)` - Override to create content
- `createTitleArea(parent)` - Override for title (optional)
- `layout(width, height)` - Handle layout
- `updateStyles()` - Theme updates
- `show()` / `hide()` - Visibility

**Lifecycle:**
1. Constructor - Register with layout service
2. `create()` - Create DOM structure
3. `layout()` - Handle sizing
4. `updateStyles()` - Apply theme

---

## Ribbon Replacement Strategy

### Approach: Direct Replacement

**Why:**
- Clean separation of concerns
- Maintains VSCode patterns
- Easier to maintain
- Clear integration points

### Implementation Model

**RibbonPart Structure:**
```typescript
class RibbonPart extends Part {
  // Same dimensions as ActivitybarPart (48px)
  // Uses RibbonCompositeBar instead of ActivityBarCompositeBar
  // Icons map to Polly pages
}
```

**Key Differences:**
1. **Part ID:** `Parts.RIBBON_PART` instead of `Parts.ACTIVITYBAR_PART`
2. **Composite Bar:** `RibbonCompositeBar` with Polly navigation
3. **Icon Mapping:** Polly pages instead of VSCode views
4. **Navigation:** Integrates with Polly's existing system

---

## Integration Points

### 1. Part Registration

**Location:** `src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`

**Current:**
```typescript
private readonly activityBarPart = this._register(
  this.instantiationService.createInstance(ActivitybarPart, this)
);
```

**New:**
```typescript
private readonly ribbonPart = this._register(
  this.instantiationService.createInstance(RibbonPart, this)
);
```

### 2. Layout System

**Location:** `src/vs/workbench/browser/layout.ts`

**Changes:**
- Add `ribbonPartView` to layout
- Update width calculations (keep 48px)
- Update positioning logic
- Replace `ACTIVITYBAR_PART` references with `RIBBON_PART`

### 3. Workbench HTML

**Location:** `src/vs/workbench/browser/workbench.ts`

**Changes:**
- Update part registration
- Change CSS classes from `activitybar` to `ribbon`
- Maintain same DOM structure

### 4. Parts Enum

**Location:** `src/vs/workbench/services/layout/browser/layoutService.ts`

**Changes:**
- Add `RIBBON_PART = 'workbench.parts.ribbon'`
- Keep `ACTIVITYBAR_PART` for compatibility (or remove if not needed)

---

## Polly Navigation Integration

### Current Polly Navigation

**Location:** `electron-app/src/renderer/app.js`

**Function:** `showView(view)` - Switches between Polly pages

**Pages:**
- dashboard
- knowledge
- notes
- code
- patterns
- learning
- etc.

### Integration Approach

**Option 1: IPC Communication**
- RibbonPart communicates with Electron main process
- Uses existing IPC bridge
- Maintains separation

**Option 2: Shared State**
- Create shared navigation service
- Both VSCode and Electron app use it
- More integrated

**Option 3: Event System**
- RibbonPart emits events
- Electron app listens
- Decoupled

**Recommendation:** Option 1 (IPC) - Cleanest separation, uses existing infrastructure

---

## Code Workspace Views

### Challenge

When in Code workspace:
- Ribbon shows "Code" icon (Polly page)
- But left panel needs VSCode views (Explorer, Search, Git, Debug)
- These need horizontal icon navigation (like Cursor)

### Solution

**Two-Level Navigation:**
1. **Ribbon (vertical, 48px):** Polly pages
2. **Left Panel Icons (horizontal, under title):** VSCode views (Code workspace only)

**Implementation:**
- RibbonPart detects Code workspace
- Shows VSCode view containers in left panel
- Adds horizontal icon navigation to left panel
- Small icons (16-18px) under panel title

---

## File Modifications Summary

### Files to Create

1. `polly-integrations/ribbon/ribbonPart.ts` - Main ribbon part
2. `polly-integrations/ribbon/ribbonCompositeBar.ts` - Icon management
3. `polly-integrations/ribbon/pollyNavigation.ts` - Navigation logic
4. `polly-integrations/ribbon/ribbon.css` - Styles
5. `polly-integrations/ribbon/ribbonTheme.ts` - Theme integration

### Files to Modify

1. `src/vs/workbench/services/layout/browser/layoutService.ts`
   - Add `RIBBON_PART` enum

2. `src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`
   - Replace `ActivitybarPart` with `RibbonPart`
   - Update all references

3. `src/vs/workbench/browser/layout.ts`
   - Add ribbon part view
   - Update layout calculations

4. `src/vs/workbench/browser/workbench.ts`
   - Update part registration

---

## Next Steps

### Immediate (This Week)

1. **Create RibbonPart skeleton**
   - Basic class structure
   - Extend Part
   - Register in workbench

2. **Port Polly ribbon CSS**
   - Adapt to VSCode structure
   - Use VSCode theme variables
   - Match Polly design

3. **Test basic integration**
   - Verify ribbon appears
   - Test icon rendering
   - Verify layout

### Short Term (Next 2 Weeks)

4. **Integrate Polly navigation**
   - Connect to IPC
   - Handle page switching
   - Maintain state

5. **Add Code workspace views**
   - Show VSCode views in left panel
   - Add horizontal icon navigation
   - Test integration

6. **Polish and refine**
   - Smooth animations
   - Visual feedback
   - Keyboard navigation

---

## Technical Decisions

### Decision 1: Keep or Remove ACTIVITYBAR_PART?

**Recommendation:** Keep for now, add RIBBON_PART
- Easier migration
- Can remove later if not needed
- Less risk of breaking things

### Decision 2: How to Handle View Containers?

**Recommendation:** 
- Ribbon: Polly pages only
- Left panel (Code workspace): VSCode view containers with horizontal icons
- Clear separation of concerns

### Decision 3: Navigation Communication?

**Recommendation:** IPC communication
- Uses existing infrastructure
- Clean separation
- Maintainable

---

## Questions Resolved

✅ **How to replace activity bar?** - Direct replacement with RibbonPart  
✅ **How to integrate Polly navigation?** - IPC communication  
✅ **How to handle Code workspace views?** - Horizontal icons in left panel  
✅ **What about view containers?** - Keep system, use for Code workspace  
✅ **How to maintain compatibility?** - Keep ACTIVITYBAR_PART enum, add RIBBON_PART  

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│           Workbench Layout               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│  SidebarPart   │    │   EditorPart    │
│                │    │                 │
│ ┌───────────┐  │    └─────────────────┘
│ │RibbonPart │  │
│ │ (48px)    │  │
│ │           │  │
│ │ Icons:    │  │
│ │ - Dashboard│ │
│ │ - Knowledge│ │
│ │ - Notes   │  │
│ │ - Code    │  │
│ └───────────┘  │
│                │
│ ┌───────────┐  │
│ │Left Panel │  │
│ │           │  │
│ │ Code:     │  │
│ │ [Explorer]│ │ ← Horizontal icons
│ │ [Search]  │ │
│ │ [Git]     │ │
│ └───────────┘  │
└────────────────┘
```

---

**Status:** Architecture analysis complete, ready for implementation
