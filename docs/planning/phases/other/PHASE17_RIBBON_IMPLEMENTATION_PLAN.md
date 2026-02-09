# Phase 17: Ribbon Implementation Plan

**Date:** February 4, 2026  
**Status:** Ready for Implementation  
**Purpose:** Detailed plan for replacing VSCode's activity bar with Polly's ribbon navigation

---

## Architecture Overview

### Current VSCode Structure

```
Workbench
├── Layout (manages all parts)
├── SidebarPart
│   └── ActivitybarPart (48px width, vertical icons)
│       └── ActivityBarCompositeBar
│           └── PaneCompositeBar (manages view containers)
└── Other parts (Editor, Panel, etc.)
```

### Target Polly Structure

```
Workbench
├── Layout (manages all parts)
├── SidebarPart
│   └── RibbonPart (48px width, vertical icons for Polly pages)
│       └── RibbonCompositeBar
│           └── Maps to Polly navigation
│           └── For Code workspace: Also shows VSCode view containers
└── Other parts (Editor, Panel, etc.)
```

---

## Implementation Steps

### Step 1: Create RibbonPart Class

**File:** `polly-integrations/ribbon/ribbonPart.ts`

**Structure:**
```typescript
export class RibbonPart extends Part {
  static readonly ACTION_HEIGHT = 48;
  
  readonly minimumWidth: number = 48;
  readonly maximumWidth: number = 48;
  readonly minimumHeight: number = 0;
  readonly maximumHeight: number = Number.POSITIVE_INFINITY;
  
  private readonly compositeBar = this._register(new MutableDisposable<RibbonCompositeBar>());
  private content: HTMLElement | undefined;
  
  constructor(
    private readonly paneCompositePart: IPaneCompositePart,
    @IInstantiationService private readonly instantiationService: IInstantiationService,
    @IWorkbenchLayoutService layoutService: IWorkbenchLayoutService,
    @IThemeService themeService: IThemeService,
    @IStorageService storageService: IStorageService,
  ) {
    super(Parts.RIBBON_PART, { hasTitle: false }, themeService, storageService, layoutService);
  }
  
  // Similar structure to ActivitybarPart but with Polly navigation
}
```

**Key Differences from ActivitybarPart:**
- Uses `Parts.RIBBON_PART` instead of `Parts.ACTIVITYBAR_PART`
- Creates `RibbonCompositeBar` instead of `ActivityBarCompositeBar`
- Icons map to Polly pages, not just VSCode views

---

### Step 2: Create RibbonCompositeBar

**File:** `polly-integrations/ribbon/ribbonCompositeBar.ts`

**Structure:**
```typescript
export class RibbonCompositeBar extends PaneCompositeBar {
  // Similar to ActivityBarCompositeBar
  // But handles Polly page navigation
  // For Code workspace: Also shows VSCode view containers
}
```

**Features:**
- Manages Polly page icons (Dashboard, Knowledge, Notes, Code, etc.)
- Handles page switching
- For Code workspace: Integrates with VSCode view containers
- Uses Polly's existing navigation system

---

### Step 3: Add RIBBON_PART to Parts Enum

**File:** `src/vs/workbench/services/layout/browser/layoutService.ts`

**Change:**
```typescript
export const enum Parts {
  TITLEBAR_PART = 'workbench.parts.titlebar',
  BANNER_PART = 'workbench.parts.banner',
  ACTIVITYBAR_PART = 'workbench.parts.activitybar', // Keep for compatibility
  RIBBON_PART = 'workbench.parts.ribbon', // NEW
  SIDEBAR_PART = 'workbench.parts.sidebar',
  // ... rest
}
```

---

### Step 4: Replace ActivitybarPart with RibbonPart

**File:** `src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`

**Changes:**
```typescript
// OLD:
import { ActivityBarCompositeBar, ActivitybarPart } from '../activitybar/activitybarPart.js';
private readonly activityBarPart = this._register(this.instantiationService.createInstance(ActivitybarPart, this));

// NEW:
import { RibbonCompositeBar, RibbonPart } from '../../../../polly-integrations/ribbon/ribbonPart.js';
private readonly ribbonPart = this._register(this.instantiationService.createInstance(RibbonPart, this));
```

**Update all references:**
- Replace `activityBarPart` with `ribbonPart`
- Update method calls
- Update visibility checks

---

### Step 5: Update Layout References

**File:** `src/vs/workbench/browser/layout.ts`

**Changes:**
- Add `ribbonPartView` similar to `activityBarPartView`
- Update layout calculations to use `RIBBON_PART`
- Maintain 48px width
- Update positioning logic

---

### Step 6: Update Workbench HTML

**File:** `src/vs/workbench/browser/workbench.ts`

**Changes:**
```typescript
// OLD:
{ id: Parts.ACTIVITYBAR_PART, role: 'none', classes: ['activitybar', ...] }

// NEW:
{ id: Parts.RIBBON_PART, role: 'none', classes: ['ribbon', ...] }
```

---

### Step 7: Create Ribbon CSS

**File:** `polly-integrations/ribbon/ribbon.css`

**Based on:** `electron-app/src/renderer/styles/ribbon.css`

**Adaptations:**
- Match VSCode's part structure
- Use VSCode theme variables
- Maintain 48px width
- Vertical icon layout
- Small, sleek icons (match Polly design)

---

### Step 8: Integrate Polly Navigation

**File:** `polly-integrations/ribbon/pollyNavigation.ts`

**Features:**
- Maps Polly pages to ribbon icons
- Handles page switching
- Integrates with existing Polly navigation
- Maintains state across switches

**Icon Mapping:**
```typescript
const POLLY_PAGE_ICONS = {
  dashboard: 'layout-dashboard',
  knowledge: 'brain',
  notes: 'file-text',
  code: 'code',
  patterns: 'sparkles',
  learning: 'graduation-cap',
  // ... etc
};
```

---

### Step 9: Handle Code Workspace Views

**For Code Workspace:**
- Ribbon shows "Code" icon (active when in Code workspace)
- Left panel shows horizontal icon navigation (Explorer, Search, Git, Debug)
- These are VSCode view containers
- Use existing PaneCompositeBar for this

**Implementation:**
- Detect when in Code workspace
- Show VSCode view containers in left panel
- Add horizontal icon navigation to left panel
- Small, sleek icons (16-18px) under panel title

---

### Step 10: Update Theme Integration

**File:** `polly-integrations/ribbon/ribbonPart.ts`

**Add:**
```typescript
import { RIBBON_BACKGROUND, RIBBON_FOREGROUND, RIBBON_ACTIVE_BORDER } from '../../../common/theme.js';

// Register theme colors
registerThemingParticipant((theme, collector) => {
  // Match Polly's ribbon styling
  // Use VSCode theme system
});
```

---

## File Structure

```
polly-integrations/
├── ribbon/
│   ├── ribbonPart.ts          # Main ribbon part (replaces ActivitybarPart)
│   ├── ribbonCompositeBar.ts  # Ribbon composite bar
│   ├── pollyNavigation.ts     # Polly page navigation logic
│   ├── ribbon.css             # Ribbon styles
│   └── ribbonTheme.ts         # Theme integration
└── MODIFICATIONS.md           # Track all changes
```

---

## Integration Points Summary

### Files to Modify

1. **`src/vs/workbench/services/layout/browser/layoutService.ts`**
   - Add `RIBBON_PART` to Parts enum

2. **`src/vs/workbench/browser/parts/sidebar/sidebarPart.ts`**
   - Replace `ActivitybarPart` with `RibbonPart`
   - Update all references

3. **`src/vs/workbench/browser/layout.ts`**
   - Add ribbon part view
   - Update layout calculations

4. **`src/vs/workbench/browser/workbench.ts`**
   - Update HTML part registration

### Files to Create

1. **`polly-integrations/ribbon/ribbonPart.ts`**
2. **`polly-integrations/ribbon/ribbonCompositeBar.ts`**
3. **`polly-integrations/ribbon/pollyNavigation.ts`**
4. **`polly-integrations/ribbon/ribbon.css`**

---

## Testing Strategy

### Unit Tests
- RibbonPart creation and initialization
- Icon rendering
- Page switching logic
- View container integration

### Integration Tests
- Ribbon appears in workbench
- Icons are clickable
- Page switching works
- VSCode views still accessible in Code workspace
- Layout calculations correct

### Visual Tests
- Ribbon matches Polly design
- Icons properly sized and styled
- Active state highlighting
- Smooth transitions

---

## Migration Path

### Phase 1: Basic Ribbon (Week 1)
- Create RibbonPart skeleton
- Replace ActivitybarPart registration
- Basic icon rendering
- Page switching

### Phase 2: Integration (Week 2)
- Integrate with Polly navigation
- Handle Code workspace views
- Theme integration
- Polish styling

### Phase 3: Horizontal Icons (Week 3)
- Add horizontal icon navigation to left panel
- Implement for Code workspace first
- Small, sleek icons
- Contextual per page

### Phase 4: Polish (Week 4)
- Smooth animations
- Visual feedback
- Keyboard navigation
- Accessibility

---

## Risk Mitigation

### Risk 1: Breaking VSCode Views
**Mitigation:**
- Keep view container system intact
- Test all VSCode views still work
- Gradual migration

### Risk 2: Navigation Conflicts
**Mitigation:**
- Clear separation: Ribbon = Polly pages, Horizontal icons = VSCode views
- Test navigation flow thoroughly

### Risk 3: Performance
**Mitigation:**
- Lazy load page content
- Optimize icon rendering
- Profile and optimize

---

## Success Criteria

### Functional
- ✅ Ribbon appears in workbench
- ✅ Icons map to Polly pages
- ✅ Clicking icon switches page
- ✅ Code workspace shows VSCode views
- ✅ All VSCode functionality preserved

### Visual
- ✅ Matches Polly ribbon design
- ✅ Small, sleek icons
- ✅ Smooth transitions
- ✅ Professional polish

### Technical
- ✅ Clean integration
- ✅ Maintainable code
- ✅ No performance issues
- ✅ Backward compatible

---

**Status:** Ready for implementation
