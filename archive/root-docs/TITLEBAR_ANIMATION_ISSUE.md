# Titlebar Button Sliding Animation Issue

**Status:** Unsolved - Documented for Future Work  
**Date:** January 26, 2026  
**Project:** Polly - Phase 0.5 Obsidian-Inspired UI  

---

## Problem Statement

### Desired Behavior
The titlebar toggle buttons should slide horizontally when sidebars open/close, following the sidebar edge:

- **Left button**: Slides from `left: 80px` (closed) → `left: 280px` (open)
- **Right button**: Slides from `right: 0px` (closed) → `right: 296px` (open)
- Buttons should remain **clickable** in both starting and extended positions
- Smooth animation should sync with sidebar slide transition

### Current Behavior
- ✅ Buttons work perfectly when **stationary** (inside `.titlebar-left` and `.titlebar-right`)
- ❌ When positioned with **animation** (position: fixed with left/right transitions OR transforms), buttons become **unclickable in extended positions**
- ❌ Mouse cursor does NOT change to pointer in extended positions
- ❌ No mouse events (mouseenter, click) fire in extended positions
- ✅ **Programmatic clicks work** (`document.getElementById('titlebar-toggle-left').click()`)

This indicates a **mouse hit-testing blocking issue** in specific screen coordinates.

---

## Investigation Summary

### What We Discovered

#### The Blocking Zone
Through testing with extreme positions, we identified that:
- ✅ Buttons at `left: 600px, top: 150px` work perfectly
- ❌ Buttons at `left: 280px, top: 8px` (extended position) fail completely
- ✅ Buttons at `left: 80px, top: 8px` (starting position) work fine

**Conclusion**: The blocking is **location-specific**, not a fundamental CSS/JavaScript issue.

#### Suspected Causes

1. **macOS Traffic Lights Invisible Hit Zone**
   - macOS window controls have a system-level hit-testing region that may extend horizontally
   - Traffic light position: `{ x: 20, y: 20 }`
   - Extended buttons at `left: 280px` may be entering this protected zone
   - Even moving buttons to `top: 50px` (below titlebar) didn't solve the issue

2. **Grid Layout Interference**
   - `.three-column-layout` starts at `left: 48px` (after ribbon)
   - Left sidebar occupies `0-280px` within the grid
   - Grid may be capturing mouse events even with high z-index buttons

3. **Webkit-App-Region Drag Zone**
   - `.titlebar` has `-webkit-app-region: drag`
   - Even with `-webkit-app-region: no-drag` on buttons, Electron may enforce drag at hit-test time
   - This is an Electron-specific behavior that CSS cannot override

4. **Transform vs Absolute Positioning**
   - Theory: CSS transforms don't update browser hit-testing regions in Electron
   - Tested with both approaches - neither worked

---

## Approaches Tried (All Failed)

### Attempt 1: Z-Index Stacking Context
**Date**: Early in debugging session

**What We Did**:
```css
.titlebar {
  z-index: 1000;
  isolation: isolate;
}

.titlebar-btn {
  z-index: 1002;
  position: relative;
}

.three-column-layout {
  z-index: 1;
}
```

**Result**: No effect. Buttons still unclickable in extended positions.

**Why It Failed**: Z-index controls visual stacking, not mouse hit-testing zones set by OS/Electron.

---

### Attempt 2: Pointer Events Management
**Date**: Mid-session

**What We Did**:
```css
.titlebar-center {
  pointer-events: none; /* Don't block clicks */
}

.titlebar-btn {
  pointer-events: auto !important;
}

.titlebar-btn svg {
  pointer-events: none; /* SVG shouldn't intercept */
}
```

**Result**: SVG fix helped with other issues, but didn't solve main blocking.

**Why It Failed**: Blocking happens at a lower level than CSS pointer-events.

---

### Attempt 3: Webkit-App-Region Override
**Date**: Mid-session

**What We Did**:
```css
.titlebar * {
  -webkit-app-region: no-drag;
}

.titlebar-btn {
  -webkit-app-region: no-drag !important;
}
```

**Result**: No effect.

**Why It Failed**: Electron may enforce `-webkit-app-region: drag` from parent elements at OS level, ignoring child overrides in certain coordinate ranges.

---

### Attempt 4: Transform → Absolute Positioning
**Date**: Mid-session

**What We Did**:
Changed from:
```css
#titlebar-toggle-left {
  transform: translateX(200px);
}
```

To:
```css
#titlebar-toggle-left {
  position: absolute;
  left: 280px;
}
```

With class-based toggling instead of inline style transforms.

**Result**: No effect. Still blocked.

**Why It Failed**: Issue is not about how elements are positioned, but about the screen coordinates they occupy.

---

### Attempt 5: Portal Buttons Outside Titlebar
**Date**: Late in session

**What We Did**:
Moved buttons completely outside `.titlebar` as direct children of `#app`:

```html
<div id="app">
  <button class="titlebar-btn-floating" id="titlebar-toggle-left">...</button>
  <button class="titlebar-btn-floating" id="titlebar-toggle-right">...</button>
  
  <div class="titlebar">...</div>
</div>
```

```css
.titlebar-btn-floating {
  position: fixed;
  top: 8px;
  z-index: 9999;
  pointer-events: auto !important;
  -webkit-app-region: no-drag !important;
}
```

**Result**: Made things WORSE. Now BOTH buttons failed in extended positions (right button had worked before this change).

**Why It Failed**: Moving buttons outside titlebar structure removed them from proper stacking context. Also, this approach inadvertently introduced additional blocking issues.

**Key Learning**: The right button working before this change tells us the original structure wasn't fundamentally broken.

---

### Attempt 6: Pointer-Events None on Grid Layout
**Date**: Late in session

**What We Did**:
```css
.three-column-layout {
  pointer-events: none;
}

.three-column-layout * {
  pointer-events: auto;
}
```

Theory: Allow buttons to receive clicks "through" the layout.

**Result**: Made ALL buttons unclickable everywhere. Reverted immediately.

**Why It Failed**: The `*` selector re-enabled pointer-events on ALL children, but buttons outside the layout didn't get `pointer-events: auto`, effectively disabling them.

---

### Attempt 7: Extreme Position Testing (SUCCESS)
**Date**: Late in session

**What We Did**:
Moved buttons to extreme coordinates far from all UI:
```css
.titlebar-btn-floating {
  top: 150px;
  left: 600px;
}
```

**Result**: ✅ **BUTTONS WORKED PERFECTLY!**

**Conclusion**: This proved the blocking is location-specific, not a fundamental flaw in our approach. Certain screen coordinates are "dead zones" where mouse events don't reach the buttons.

---

## Diagnostic Results

### Hit-Testing Query
When running `document.elementsFromPoint(buttonX, buttonY)` with sidebar OPEN:

```javascript
const leftBtn = document.getElementById('titlebar-toggle-left');
const rect = leftBtn.getBoundingClientRect();
const elementsAtPoint = document.elementsFromPoint(
  rect.left + rect.width/2,
  rect.top + rect.height/2
);

console.log(elementsAtPoint);
// Output:
// 0. BUTTON.titlebar-btn (✅ Button IS the top element!)
// 1. DIV.titlebar
```

**Strange Finding**: The browser CORRECTLY identifies the button as the top element at that coordinate, yet the button doesn't receive mouse events. This suggests **OS-level or Electron-level hit-testing override**.

### Programmatic Click Test
```javascript
document.getElementById('titlebar-toggle-left').click();
// ✅ WORKS! Sidebar toggles successfully
```

This proves:
- JavaScript event system is working
- Button element is accessible and functional
- Issue is ONLY with mouse-triggered events

---

## Current Working Solution

### Status
Buttons are **functional but stationary** - they do not slide with sidebar animation.

### Implementation
Buttons are positioned inside `.titlebar-left` and `.titlebar-right` containers:

```html
<div class="titlebar">
  <div class="titlebar-left">
    <button class="titlebar-btn" id="titlebar-toggle-left">
      <i data-lucide="chevron-left"></i>
    </button>
  </div>
  
  <div class="titlebar-center"></div>
  
  <div class="titlebar-right">
    <button class="titlebar-btn" id="titlebar-toggle-right">
      <i data-lucide="chevron-right"></i>
    </button>
  </div>
</div>
```

```css
.titlebar-btn {
  position: relative;
  z-index: 1002;
  pointer-events: auto !important;
  -webkit-app-region: no-drag !important;
  /* No transforms or position animations */
}
```

### Behavior
- ✅ Both buttons fully clickable
- ✅ Sidebars toggle smoothly
- ✅ Arrow icons flip direction based on state
- ❌ Buttons do NOT slide with sidebar animation
- ❌ Visual disconnect between button position and sidebar edge

---

## Future Approaches to Try

### Option 1: Move Buttons to Ribbon
**Feasibility**: High

The icon ribbon at `left: 0, top: 40px, width: 48px` works perfectly with click events.

**Implementation**:
- Add two small toggle buttons at top of ribbon (above main icons)
- Position them at `top: 45px` (just below titlebar)
- Style as icon buttons matching ribbon aesthetic
- They would be stationary but outside the problematic zone

**Pros**:
- Guaranteed to work (ribbon buttons have no issues)
- Clear visual hierarchy (controls on left, content on right)
- Matches Obsidian's left-side control pattern

**Cons**:
- Not the sliding animation you envisioned
- Different visual pattern than titlebar controls

---

### Option 2: Remove Sliding Animation
**Feasibility**: Immediate

Keep buttons in current positions, only animate the arrow direction.

**Implementation**:
```css
.titlebar-btn svg {
  transition: transform 0.2s ease;
}

.titlebar-btn.collapsed svg {
  transform: scaleX(-1); /* Flip arrow direction */
}
```

**Pros**:
- Already works
- Simple and reliable
- Still provides visual feedback

**Cons**:
- No spatial relationship between button and sidebar edge
- Less visually interesting

---

### Option 3: Investigate Electron BrowserWindow Options
**Feasibility**: Low (requires deep Electron knowledge)

The issue might be solvable with different Electron window configuration:

**Research Areas**:
```javascript
// In main.js
const win = new BrowserWindow({
  titleBarStyle: 'hiddenInset', // vs 'hidden'
  trafficLightPosition: { x: 20, y: 20 },
  // Try different combinations:
  // - 'customButtonsOnHover'
  // - frame: false (fully custom titlebar)
});
```

**Investigation Needed**:
- Does `titleBarStyle: 'hiddenInset'` change the hit-testing zone?
- Can we increase `trafficLightPosition.x` to push the zone left?
- Would a frameless window (`frame: false`) give us full control?

**Pros**:
- Might solve the root cause
- Would enable the desired animation

**Cons**:
- Time-consuming research
- May introduce other UI issues
- Could break macOS native behavior users expect

---

### Option 4: Hybrid Approach - Animate Container Instead
**Feasibility**: Medium

Instead of moving buttons, animate the entire `.titlebar-left` and `.titlebar-right` containers.

**Implementation**:
```css
.titlebar-left {
  padding-left: 80px;
  transition: padding-left 0.2s ease;
}

.three-column-layout:not(.left-collapsed) ~ .titlebar .titlebar-left {
  padding-left: 280px;
}
```

Use sibling selectors or JavaScript to toggle classes on `.titlebar` based on sidebar state.

**Theory**: If the container moves instead of individual buttons, hit-testing might work differently.

**Pros**:
- Keeps buttons in working structure
- Might bypass the coordinate-specific blocking

**Cons**:
- Complex selector logic
- May still hit the same dead zone
- Untested - could fail for same reasons

---

### Option 5: Use Keyboard Shortcuts Primarily
**Feasibility**: Immediate

De-emphasize mouse interaction, promote keyboard shortcuts:

- `Cmd+B` - Toggle left sidebar (already works)
- `Cmd+/` - Toggle right sidebar (already works)

**Implementation**:
- Keep current button layout
- Add prominent tooltip hints
- Consider a keyboard shortcut cheatsheet modal

**Pros**:
- Keyboard shortcuts always work
- Power users prefer this anyway
- Matches Obsidian's keyboard-first philosophy

**Cons**:
- Less discoverable for new users
- Doesn't solve the visual/UX issue

---

## Technical Deep Dive

### Why Location Matters

The blocking happens in a specific coordinate range:
- **Safe zone**: `left: 600px+` (far right)
- **Safe zone**: `left: 0-80px` (far left, before sidebar width)
- **Dead zone**: `left: 80-328px, top: 0-40px` (titlebar area over sidebar)

This pattern suggests:

1. **macOS Traffic Lights Protected Zone**:
   - System reserves horizontal space for window controls
   - Even though traffic lights are at `x: 20`, the "hover zone" extends much further right
   - This allows users to hover near the window edge to reveal controls
   - Electron cannot override this OS-level behavior

2. **Webkit Drag Region Priority**:
   - When `-webkit-app-region: drag` is set on a parent, Electron prioritizes drag behavior
   - In the coordinate range where sidebar overlaps titlebar, drag region may take precedence
   - CSS `z-index` and `pointer-events` don't override Electron's compositor-level decisions

### Why Programmatic Clicks Work

```javascript
document.getElementById('titlebar-toggle-left').click();
```

This works because:
- JavaScript event dispatch bypasses browser/OS hit-testing
- It directly invokes the click handler on the element
- No mouse coordinates involved, no hit-testing performed

This proves the element is fully functional and accessible via DOM.

---

## File Reference

### Key Files Modified
1. `/Users/brettgershon/polly/electron-app/src/renderer/index.html` (lines 16-41)
   - Button DOM structure
   
2. `/Users/brettgershon/polly/electron-app/src/renderer/styles/main.css` (lines 96-230)
   - Titlebar and button styling
   
3. `/Users/brettgershon/polly/electron-app/src/renderer/app.js` (lines 973-1080)
   - Button positioning logic and event listeners
   
4. `/Users/brettgershon/polly/electron-app/src/main/main.js`
   - Electron window config: `trafficLightPosition: { x: 20, y: 20 }`

### Current Working CSS
```css
/* Titlebar */
.titlebar {
  height: 40px;
  background: #1e1e1e;
  -webkit-app-region: drag;
  position: relative;
  z-index: 1000;
}

.titlebar * {
  -webkit-app-region: no-drag;
}

/* Button containers */
.titlebar-left {
  padding-left: 80px; /* Space for traffic lights */
  display: flex;
  align-items: center;
  -webkit-app-region: no-drag !important;
  z-index: 1001;
  pointer-events: auto !important;
}

.titlebar-right {
  display: flex;
  align-items: center;
  -webkit-app-region: no-drag !important;
  z-index: 1001;
  pointer-events: auto !important;
}

/* Buttons */
.titlebar-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: #808080;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.2s ease;
  -webkit-app-region: no-drag !important;
  z-index: 1002;
  position: relative;
  pointer-events: auto !important;
}

.titlebar-btn:hover {
  background: #2a2a2a;
  color: #b4b4b4;
}

.titlebar-btn svg {
  width: 14px;
  height: 14px;
  pointer-events: none;
}

.titlebar-btn.collapsed {
  color: #7f6df2; /* Purple when sidebar collapsed */
}
```

---

## Recommended Next Steps

### Short Term (When Resuming Work)
1. **Try Option 1 (Ribbon Buttons)** first - highest chance of success
2. **Try Option 4 (Animate Container)** second - novel approach, might bypass issue
3. Document findings and decide on permanent solution

### Medium Term
1. Research Electron window configuration options
2. Check if Electron has open issues about macOS titlebar hit-testing
3. Consider filing Electron bug report with reproducible test case

### Long Term
1. Monitor Electron updates for fixes to webkit-app-region behavior
2. Consider frameless window with fully custom titlebar (major undertaking)
3. Evaluate if animated buttons are worth the complexity vs keyboard shortcuts

---

## Questions for Future Investigation

1. **Does this issue exist on Windows/Linux?**
   - Test on other platforms
   - May be macOS-specific traffic lights issue

2. **What exact coordinates are blocked?**
   - Write a script to test every 10px across the titlebar
   - Create a "heat map" of clickable vs blocked zones

3. **Can we detect the dead zone at runtime?**
   - Use `document.elementsFromPoint()` on load
   - Dynamically adjust button positions based on findings

4. **Does frameless window solve it?**
   - Build test app with `frame: false`
   - Implement fully custom window controls
   - Test if buttons work in all positions

---

## Conclusion

**Current Status**: Buttons are **functional but not animated** to follow sidebars.

**Root Cause**: Mouse hit-testing is blocked in specific screen coordinates (`left: 80-328px, top: 0-40px`) due to either:
- macOS traffic lights protected zone
- Electron webkit-app-region compositor behavior
- Grid layout interference with titlebar

**Recommendation**: Move forward with stationary buttons for now. When ready to revisit:
1. Try moving buttons to ribbon (Option 1)
2. Research Electron window configuration options
3. Consider if animated buttons are essential vs nice-to-have

The current implementation is **fully functional** - users can toggle sidebars with both mouse clicks and keyboard shortcuts. The sliding animation is a UX enhancement, not a critical feature.

---

**Document Created**: January 26, 2026  
**Last Updated**: January 26, 2026  
**Status**: Open Issue - Future Work
