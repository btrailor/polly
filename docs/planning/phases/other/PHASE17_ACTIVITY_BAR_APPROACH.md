# Phase 17: Activity Bar Integration Approach

**Date:** February 4, 2026  
**Status:** Planning

---

## Challenge

The activity bar currently shows VSCode's native view containers (Explorer, Search, Source Control, etc.). We need to replace these with Polly pages (Dashboard, Knowledge, Notes, Code, Learning, Patterns, Settings).

## Approach Options

### Option 1: Extension-Based View Containers (Recommended)
**Approach:** Register view containers for each Polly page via extension API
**Pros:**
- Uses VSCode's native extension API
- No core modifications needed
- Cleaner, more maintainable

**Cons:**
- May not give full control over activity bar appearance
- Need to work within VSCode's view container system

**Implementation:**
- In extension `package.json`, register view containers for each Polly page
- Each view container appears in activity bar
- Clicking switches workspace context
- Code workspace: Show VSCode native views
- Other workspaces: Show Polly-specific views

### Option 2: Core Modification
**Approach:** Modify `activitybarPart.ts` to show Polly pages directly
**Pros:**
- Full control over activity bar
- Can customize appearance completely

**Cons:**
- Requires core VSCode modification
- More complex to maintain
- Harder to merge upstream updates

**Implementation:**
- Modify `ActivitybarPart` to show Polly pages instead of view containers
- Wire clicks to extension commands
- Handle workspace switching

## Recommended Approach

**Use Option 1 (Extension-Based)** for initial implementation:
1. Register view containers for each Polly page
2. Use extension commands to switch workspaces
3. Show/hide views based on workspace context
4. If more control needed later, consider Option 2

## Implementation Steps

1. **Register View Containers** (in extension `package.json`):
   ```json
   "viewsContainers": {
     "activitybar": [
       {
         "id": "polly.dashboard",
         "title": "Dashboard",
         "icon": "$(layout-dashboard)"
       },
       // ... other pages
     ]
   }
   ```

2. **Create Views** for each container:
   ```json
   "views": {
     "polly.dashboard": [
       {
         "id": "polly.dashboard.stats",
         "name": "Stats"
       }
     ]
   }
   ```

3. **Wire Commands** to switch workspaces:
   - Each view container click triggers workspace switch
   - Update context variable `polly.workspace`
   - Show/hide views based on workspace

4. **Handle Code Workspace**:
   - When Code workspace active, show VSCode native views
   - Hide Polly-specific views
   - When other workspace active, show Polly views

## Next Steps

1. Implement view container registration in extension
2. Create tree view providers for each workspace
3. Implement workspace switching logic
4. Test activity bar integration
5. If needed, consider core modification for more control

---

## Current Status

- ✅ Extension foundation complete
- ✅ API client complete
- ✅ Status bar integration complete
- ⏳ Activity bar integration - Ready to implement using Option 1
