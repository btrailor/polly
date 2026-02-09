# Comprehensive Layout Fix

## Critical Issues to Fix

### 1. Icon Ribbon (Far Left Vertical) - MISSING CSS
- Ribbon HTML exists but has NO CSS styles
- Need to add complete ribbon styling
- Should be 40px wide, vertical, on far left
- Contains main page navigation buttons

### 2. Left Sidebar Structure
- Should have horizontal ribbon at TOP for subpage navigation
- Then page-specific content below
- Currently showing wrong content

### 3. Resize Handle Not Working
- Function exists but may not be attaching properly
- Need to verify event handlers

### 4. Agents Sidebar Not Collapsible
- Toggle button exists but not wired to titlebar button
- Need to connect titlebar-toggle-right to agents sidebar

### 5. Dead Space
- Gap between titlebar and content
- Need to check margins/padding on main-container

## Implementation Order

1. Add ribbon CSS (critical - ribbon invisible without it)
2. Fix left sidebar structure (horizontal ribbon + content)
3. Wire up agents sidebar collapse
4. Fix resize handle
5. Fix spacing
