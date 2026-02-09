# Critical Layout Fixes

## Issues Identified

1. **Icon Ribbon (Far Left Vertical)** - Should be visible with main page navigation
2. **Left Sidebar** - Should have horizontal ribbon at top + page-specific content below
3. **Resize Handle** - Not working between main content and chat
4. **Agents Sidebar** - Not collapsible, toggle button not in titlebar
5. **Dead Space** - Huge gap between titlebar and content

## Fix Plan

### Fix 1: Ensure Icon Ribbon is Visible
- Check CSS for `.ribbon` visibility
- Ensure it's positioned correctly (far left, vertical)
- Make sure ribbon buttons work

### Fix 2: Left Sidebar Structure
- Add horizontal ribbon at top of left sidebar for subpage navigation
- Keep page-specific content below
- Remove duplicate navigation from sidebar content

### Fix 3: Resize Handle
- Verify `setupCenterResizeHandle()` is being called
- Check if elements exist when function runs
- Fix any CSS issues preventing drag

### Fix 4: Agents Sidebar Collapsible
- Wire up titlebar toggle button
- Add collapse/expand functionality
- Persist state in localStorage

### Fix 5: Fix Dead Space
- Check spacing between titlebar and main-container
- Remove any extra margins/padding
- Ensure ribbon and main-container are properly positioned
