# Phase 17 POC: Ribbon Navigation Integration

**Status:** 📋 Planned  
**Purpose:** Detailed guide for replacing VSCode's activity bar with Polly's ribbon navigation

---

## Overview

This document provides detailed steps for integrating Polly's ribbon navigation into the VSCode fork, replacing the activity bar while maintaining all existing functionality.

---

## Understanding VSCode's Activity Bar

### Current Structure

**Activity Bar Component:**
- Location: `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
- Purpose: Primary navigation between views (Explorer, Search, Git, Debug, Extensions)
- Integration: Part of workbench shell

**How It Works:**
1. Activity bar renders icons vertically on far left
2. Clicking icon shows corresponding view in sidebar
3. Active icon is highlighted
4. Views are managed by view container system

### Key Files

```
src/vs/workbench/browser/
├── parts/
│   ├── activitybar/
│   │   ├── activitybarPart.ts      # Main activity bar component
│   │   └── activitybarActions.ts   # Actions/commands
│   └── sidebar/
│       └── sidebarPart.ts          # Sidebar that shows views
├── workbench.html                  # HTML template
└── workbench.ts                    # Workbench initialization
```

---

## Integration Strategy

### Approach: Replace Activity Bar, Keep Views

**What We Change:**
- Replace activity bar UI with Polly ribbon
- Keep view container system (views still work)
- Maintain all existing functionality

**What We Keep:**
- View container system
- Sidebar panel system
- All existing views (Explorer, Search, etc.)
- Keyboard shortcuts
- Extension API

---

## Implementation Steps

### Step 1: Study Activity Bar Implementation

**Read Key Files:**
1. `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
   - Understand how activity bar is created
   - See how icons are rendered
   - Understand click handling

2. `src/vs/workbench/browser/workbench.html`
   - Find where activity bar is in template
   - Understand DOM structure

3. `src/vs/workbench/browser/workbench.ts`
   - See how activity bar is initialized
   - Understand workbench lifecycle

**Key Insights to Document:**
- How are view containers registered?
- How does clicking an icon show a view?
- How is active state managed?
- What CSS classes are used?

### Step 2: Port Polly Ribbon

**From Polly Electron App:**
- Source: `electron-app/src/renderer/styles/ribbon.css`
- Icons: Lucide icons (same as VSCode uses)
- Structure: Vertical icon bar

**Create Ribbon Component:**

```typescript
// polly-integrations/ribbon/ribbonPart.ts
import { Disposable } from 'vs/base/common/lifecycle';
import { IWorkbenchContribution } from 'vs/workbench/common/contributions';

export class RibbonPart extends Disposable implements IWorkbenchContribution {
  // Port Polly ribbon implementation
  // Replace activity bar functionality
}
```

**Key Features:**
- Vertical icon layout (like current ribbon)
- Icon highlighting on active
- Click to switch views
- Tooltips on hover

### Step 3: Replace Activity Bar in Workbench

**Modify `workbench.html`:**

```html
<!-- Replace this: -->
<div class="part activitybar" id="workbench.parts.activitybar"></div>

<!-- With this: -->
<div class="part ribbon" id="workbench.parts.ribbon"></div>
```

**Modify `workbench.ts`:**

```typescript
// Replace activity bar registration
// registerWorkbenchContribution(ActivityBarPart, ...)
// With:
registerWorkbenchContribution(RibbonPart, ...)
```

### Step 4: Map Ribbon Icons to Views

**View Mapping:**

```typescript
const RIBBON_VIEW_MAP = {
  'dashboard': 'workbench.view.explorer',      // Use Explorer for now
  'knowledge': 'workbench.view.search',        // Use Search
  'notes': 'workbench.view.explorer',          // Use Explorer
  'code': 'workbench.view.explorer',           // Use Explorer
  'patterns': 'workbench.view.search',         // Use Search
  // ... map Polly pages to VSCode views
};
```

**For POC:**
- Start with basic mapping
- Can refine later
- Goal is to prove integration works

### Step 5: Test Integration

**Test Cases:**
1. ✅ Ribbon appears on left
2. ✅ Can click ribbon icons
3. ✅ Views switch correctly
4. ✅ Active icon highlights
5. ✅ Keyboard shortcuts still work
6. ✅ No console errors
7. ✅ Performance acceptable

---

## Visual Design

### Ribbon Styling

**Match Polly's Current Ribbon:**
- Width: 48px (same as current)
- Icons: 18-20px
- Spacing: 8px between icons
- Colors: Match Polly design system
- Active state: Purple accent with left border

**CSS Location:**
- Create: `polly-integrations/ribbon/ribbon.css`
- Import in workbench

### Integration with VSCode Theme

**Theme Variables:**
- Use VSCode's CSS variables where possible
- Override with Polly colors
- Ensure dark/light mode support

---

## Code Structure

### Files to Create

```
polly-integrations/
├── ribbon/
│   ├── ribbonPart.ts          # Main ribbon component
│   ├── ribbon.css             # Ribbon styles
│   └── ribbonViewMap.ts       # View mapping
└── MODIFICATIONS.md           # Document changes
```

### Files to Modify

```
src/vs/workbench/browser/
├── workbench.html             # Replace activity bar div
├── workbench.ts               # Register RibbonPart
└── parts/
    └── activitybar/           # Study (don't modify yet)
```

---

## Testing Checklist

### Functional Tests

- [ ] Ribbon renders correctly
- [ ] All ribbon icons visible
- [ ] Clicking icon switches view
- [ ] Active icon highlighted
- [ ] Tooltips show on hover
- [ ] Views load correctly
- [ ] No broken functionality

### Visual Tests

- [ ] Ribbon matches Polly design
- [ ] Icons properly sized
- [ ] Spacing correct
- [ ] Colors match design system
- [ ] No visual glitches
- [ ] Responsive to window resize

### Integration Tests

- [ ] Works with existing views
- [ ] Keyboard shortcuts work
- [ ] Extension system works
- [ ] No console errors
- [ ] Performance acceptable

---

## Troubleshooting

### Ribbon Doesn't Appear

**Check:**
- Is RibbonPart registered in workbench.ts?
- Is CSS loaded?
- Check browser console for errors

### Views Don't Switch

**Check:**
- Is view mapping correct?
- Are view IDs correct?
- Check view container registration

### Styling Issues

**Check:**
- CSS variables available?
- Theme applied correctly?
- No conflicting styles?

---

## Next Steps After Ribbon

Once ribbon is working:

1. **Add Chat Panel** (Day 5)
2. **Customize Theme** (Day 6-7)
3. **Test Merge** (Day 8-9)
4. **Evaluate** (Day 10)

---

**Status:** Ready for implementation after fork setup
