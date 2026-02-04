# Phase 9: macOS Permission Handling

**Status:** Not Started  
**Priority:** ⚠️ **CRITICAL** - Blocks 3 Major Integrations  
**Estimated Effort:** 2-3 days (15-22 hours)  
**Dependencies:** None

---

## Overview

Enable Calendar, Reminders, and File System integrations by implementing proper macOS permission request flows. These integrations are already built and tested, but disabled because permission handling doesn't exist yet.

### What's Blocked

**3 Complete Integrations Waiting for Phase 9:**

1. **Calendar** (`/integrations/calendar.py`)
   - ✅ Built and tested
   - ❌ Requires EventKit Calendar permission
   - 📅 Index calendar events, search schedule

2. **Reminders** (`/integrations/reminders.py`)
   - ✅ Built and tested
   - ❌ Requires EventKit Reminders permission
   - ✅ Index reminders, track tasks

3. **File System** (`/integrations/filesystem.py`, `/integrations/filesystem_llm.py`)
   - ✅ Built and tested
   - ❌ Requires Full Disk Access permission
   - 📁 Organize files, add Finder tags, batch operations

**Total Code Ready:** ~1,400 lines of working code just waiting for permissions

---

## Goals

### Primary Goals

1. **Permission Status Checking**
   - Check EventKit authorization (Calendar, Reminders)
   - Check Full Disk Access (read-only test)
   - Cache permission status
   - Return user-friendly messages

2. **Permission Request Flow**
   - Request EventKit permission (system dialog)
   - Guide user through Full Disk Access setup
   - Handle granted/denied states
   - Retry mechanisms

3. **UI/UX Components**
   - Permission status indicators on integration cards
   - "Grant Permission" buttons
   - Permission explanation modals
   - System Settings deep links
   - Success/failure notifications

4. **Graceful Degradation**
   - Detect denied permissions
   - Show helpful error messages
   - Provide documentation links
   - Offer retry

5. **Integration Enable/Disable**
   - Unified toggle per integration
   - Check permissions before enabling
   - Show requirements
   - Guide through setup

### Success Criteria

- ✅ Users see permission status on integration cards
- ✅ Users grant permissions through Polly UI
- ✅ System permission dialogs appear correctly
- ✅ Integrations auto-enable when permissions granted
- ✅ Helpful errors when permissions denied
- ✅ System Settings opens to correct pane
- ✅ All 3 macOS integrations working

---

## Implementation Plan

### Day 1: Permission Manager Backend

**Tasks:**
1. Create `/integrations/permissions.py`
2. Implement `PermissionManager` class
3. Add Calendar permission check (EventKit)
4. Add Reminders permission check (EventKit)
5. Add Full Disk Access check (read-only test)
6. Add permission request methods
7. Test all 3 permission types

**Deliverables:**
- `/integrations/permissions.py` (200 lines)
- Permission checking utilities

**Permission Manager Implementation:**

```python
# /integrations/permissions.py

import os
from enum import Enum
from typing import Optional
import subprocess

try:
    import EventKit
    HAS_EVENTKIT = True
except ImportError:
    HAS_EVENTKIT = False

class PermissionStatus(Enum):
    """Permission status states."""
    GRANTED = "granted"
    DENIED = "denied"
    NOT_DETERMINED = "not_determined"
    RESTRICTED = "restricted"
    UNAVAILABLE = "unavailable"

class PermissionManager:
    """Manage macOS permissions for integrations."""
    
    @staticmethod
    def check_calendar_permission() -> PermissionStatus:
        """Check EventKit Calendar authorization status."""
        if not HAS_EVENTKIT:
            return PermissionStatus.UNAVAILABLE
        
        try:
            store = EventKit.EKEventStore.alloc().init()
            status = EventKit.EKEventStore.authorizationStatusForEntityType_(
                EventKit.EKEntityTypeEvent
            )
            
            if status == EventKit.EKAuthorizationStatusAuthorized:
                return PermissionStatus.GRANTED
            elif status == EventKit.EKAuthorizationStatusDenied:
                return PermissionStatus.DENIED
            elif status == EventKit.EKAuthorizationStatusRestricted:
                return PermissionStatus.RESTRICTED
            else:
                return PermissionStatus.NOT_DETERMINED
        except Exception as e:
            print(f"Error checking calendar permission: {e}")
            return PermissionStatus.UNAVAILABLE
    
    @staticmethod
    def check_reminders_permission() -> PermissionStatus:
        """Check EventKit Reminders authorization status."""
        if not HAS_EVENTKIT:
            return PermissionStatus.UNAVAILABLE
        
        try:
            store = EventKit.EKEventStore.alloc().init()
            status = EventKit.EKEventStore.authorizationStatusForEntityType_(
                EventKit.EKEntityTypeReminder
            )
            
            if status == EventKit.EKAuthorizationStatusAuthorized:
                return PermissionStatus.GRANTED
            elif status == EventKit.EKAuthorizationStatusDenied:
                return PermissionStatus.DENIED
            elif status == EventKit.EKAuthorizationStatusRestricted:
                return PermissionStatus.RESTRICTED
            else:
                return PermissionStatus.NOT_DETERMINED
        except Exception as e:
            print(f"Error checking reminders permission: {e}")
            return PermissionStatus.UNAVAILABLE
    
    @staticmethod
    def check_full_disk_access() -> PermissionStatus:
        """
        Check Full Disk Access by attempting to read a protected file.
        
        We try to read ~/Library/Safari/History.db which requires Full Disk Access.
        """
        test_path = os.path.expanduser("~/Library/Safari/History.db")
        
        if not os.path.exists(test_path):
            # Safari history doesn't exist, try another protected location
            test_path = os.path.expanduser("~/Library/Mail")
        
        try:
            # Try to list directory or read file
            if os.path.isdir(test_path):
                os.listdir(test_path)
            else:
                with open(test_path, 'rb') as f:
                    f.read(1)
            return PermissionStatus.GRANTED
        except PermissionError:
            return PermissionStatus.DENIED
        except Exception:
            # File doesn't exist or other error
            return PermissionStatus.NOT_DETERMINED
    
    @staticmethod
    async def request_calendar_permission() -> bool:
        """
        Request Calendar permission (triggers system dialog).
        
        Returns True if granted, False otherwise.
        """
        if not HAS_EVENTKIT:
            return False
        
        try:
            store = EventKit.EKEventStore.alloc().init()
            
            # This triggers the system permission dialog
            def completion_handler(granted, error):
                pass
            
            store.requestAccessToEntityType_completion_(
                EventKit.EKEntityTypeEvent,
                completion_handler
            )
            
            # Wait a moment for user response (in real app, this would be async callback)
            import time
            time.sleep(0.5)
            
            # Check status again
            status = PermissionManager.check_calendar_permission()
            return status == PermissionStatus.GRANTED
        except Exception as e:
            print(f"Error requesting calendar permission: {e}")
            return False
    
    @staticmethod
    async def request_reminders_permission() -> bool:
        """
        Request Reminders permission (triggers system dialog).
        
        Returns True if granted, False otherwise.
        """
        if not HAS_EVENTKIT:
            return False
        
        try:
            store = EventKit.EKEventStore.alloc().init()
            
            def completion_handler(granted, error):
                pass
            
            store.requestAccessToEntityType_completion_(
                EventKit.EKEntityTypeReminder,
                completion_handler
            )
            
            import time
            time.sleep(0.5)
            
            status = PermissionManager.check_reminders_permission()
            return status == PermissionStatus.GRANTED
        except Exception as e:
            print(f"Error requesting reminders permission: {e}")
            return False
    
    @staticmethod
    def open_system_settings(pane: str = "full_disk_access"):
        """
        Open System Settings to specific pane.
        
        Args:
            pane: "full_disk_access", "calendar", "reminders"
        """
        urls = {
            "full_disk_access": "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles",
            "privacy": "x-apple.systempreferences:com.apple.preference.security",
        }
        
        url = urls.get(pane, urls["privacy"])
        subprocess.run(["open", url])
    
    @staticmethod
    def get_all_permissions_status() -> dict:
        """Get status of all permissions."""
        return {
            "calendar": PermissionManager.check_calendar_permission().value,
            "reminders": PermissionManager.check_reminders_permission().value,
            "full_disk_access": PermissionManager.check_full_disk_access().value
        }
```

### Day 2: API Endpoints & Server Integration

**Tasks:**
1. Add `/polly/permissions/status` endpoint
2. Add `/polly/permissions/request` endpoint
3. Add `/polly/permissions/open-settings` endpoint
4. Update `/interfaces/server.py` to use `PermissionManager`
5. Enable integrations when permissions granted
6. Test API endpoints

**Deliverables:**
- 3 API endpoints in `/interfaces/server.py` (+80 lines)
- Integration enable/disable logic

**API Endpoints:**

```python
# Add to /interfaces/server.py

from integrations.permissions import PermissionManager, PermissionStatus

@app.get("/polly/permissions/status")
async def get_permissions_status():
    """Get status of all macOS permissions."""
    return {
        "success": True,
        "permissions": PermissionManager.get_all_permissions_status()
    }

@app.post("/polly/permissions/request")
async def request_permission(request: dict):
    """
    Request a specific permission.
    
    Body: {"permission": "calendar" | "reminders"}
    """
    permission = request.get("permission")
    
    if permission == "calendar":
        granted = await PermissionManager.request_calendar_permission()
    elif permission == "reminders":
        granted = await PermissionManager.request_reminders_permission()
    else:
        raise HTTPException(status_code=400, detail="Invalid permission type")
    
    return {
        "success": True,
        "granted": granted,
        "status": PermissionManager.get_all_permissions_status()[permission]
    }

@app.get("/polly/permissions/open-settings")
async def open_system_settings(pane: str = "full_disk_access"):
    """
    Open System Settings to specific pane.
    
    Query param: pane = "full_disk_access" | "privacy"
    """
    try:
        PermissionManager.open_system_settings(pane)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update integration registration
def register_integrations():
    """Register all integrations based on permissions."""
    
    # Always register these (no special permissions)
    manager.register_integration(ObsidianIntegration())
    manager.register_integration(GitHubIntegration())
    manager.register_integration(Context7Integration())
    
    # macOS integrations (require permissions)
    if PermissionManager.check_calendar_permission() == PermissionStatus.GRANTED:
        from integrations.calendar import CalendarIntegration
        manager.register_integration(CalendarIntegration())
        logger.info("Calendar integration enabled")
    
    if PermissionManager.check_reminders_permission() == PermissionStatus.GRANTED:
        from integrations.reminders import RemindersIntegration
        manager.register_integration(RemindersIntegration())
        logger.info("Reminders integration enabled")
    
    if PermissionManager.check_full_disk_access() == PermissionStatus.GRANTED:
        from integrations.filesystem import FileSystemIntegration
        manager.register_integration(FileSystemIntegration())
        logger.info("File System integration enabled")
```

### Day 3: Frontend UI & Polish

**Tasks:**
1. Add IPC handlers for permission APIs
2. Expose permission APIs in preload.js
3. Update integration cards to show permission status
4. Add "Grant Permission" buttons
5. Add permission explanation modals
6. Add "Open System Settings" button for Full Disk Access
7. Test entire flow end-to-end

**Deliverables:**
- IPC handlers in `/electron-app/src/main/main.js` (+60 lines)
- Preload API exposure (+15 lines)
- UI components in index.html (+100 lines)
- Permission logic in app.js (+120 lines)

**UI Mockup:**

```
┌─────────────────────────────────────────────────────────┐
│  Integrations                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📅 Calendar                               [○]    │  │
│  │                                                   │  │
│  │ ⚠️ Requires Calendar Permission                  │  │
│  │                                                   │  │
│  │ Status: Not Granted                              │  │
│  │                                                   │  │
│  │ [ Grant Permission ]                             │  │
│  │                                                   │  │
│  │ Why we need this:                                │  │
│  │ • Search your schedule                           │  │
│  │ • Find meeting notes                             │  │
│  │ • Context-aware responses                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📁 File System                            [○]    │  │
│  │                                                   │  │
│  │ ⚠️ Requires Full Disk Access                     │  │
│  │                                                   │  │
│  │ Status: Not Granted                              │  │
│  │                                                   │  │
│  │ To enable:                                       │  │
│  │ 1. Click "Open System Settings" below            │  │
│  │ 2. Go to Privacy & Security                      │  │
│  │ 3. Click "Full Disk Access"                      │  │
│  │ 4. Toggle on "Polly"                             │  │
│  │ 5. Restart Polly                                 │  │
│  │                                                   │  │
│  │ [ Open System Settings ]                         │  │
│  │                                                   │  │
│  │ [ I've Granted Access ]                          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**IPC Handlers:**

```javascript
// In /electron-app/src/main/main.js

ipcMain.handle('permissions-status', async () => {
    try {
        const response = await axios.get('http://localhost:11436/polly/permissions/status');
        return response.data;
    } catch (error) {
        console.error('Error fetching permission status:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('permissions-request', async (event, permission) => {
    try {
        const response = await axios.post('http://localhost:11436/polly/permissions/request', {
            permission
        });
        return response.data;
    } catch (error) {
        console.error('Error requesting permission:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('permissions-open-settings', async (event, pane) => {
    try {
        const response = await axios.get(
            `http://localhost:11436/polly/permissions/open-settings?pane=${pane}`
        );
        return response.data;
    } catch (error) {
        console.error('Error opening settings:', error);
        return { success: false, error: error.message };
    }
});
```

**Preload API:**

```javascript
// In /electron-app/src/main/preload.js

contextBridge.exposeInMainWorld('polly', {
    // ... existing APIs
    
    // Permission APIs
    permissionsStatus: () => ipcRenderer.invoke('permissions-status'),
    permissionsRequest: (permission) => ipcRenderer.invoke('permissions-request', permission),
    permissionsOpenSettings: (pane) => ipcRenderer.invoke('permissions-open-settings', pane),
});
```

**Frontend Logic:**

```javascript
// In /electron-app/src/renderer/app.js

async function checkPermissions() {
    const result = await window.polly.permissionsStatus();
    if (result.success) {
        updatePermissionUI(result.permissions);
    }
}

function updatePermissionUI(permissions) {
    // Update Calendar integration card
    const calendarStatus = permissions.calendar;
    if (calendarStatus === 'granted') {
        document.getElementById('calendar-status').textContent = '✅ Granted';
        document.getElementById('calendar-grant-btn').style.display = 'none';
        document.getElementById('calendar-toggle').disabled = false;
    } else {
        document.getElementById('calendar-status').textContent = '⚠️ Not Granted';
        document.getElementById('calendar-grant-btn').style.display = 'block';
        document.getElementById('calendar-toggle').disabled = true;
    }
    
    // Similar for Reminders and File System
}

async function requestCalendarPermission() {
    const result = await window.polly.permissionsRequest('calendar');
    if (result.granted) {
        showNotification('Calendar permission granted! Restarting integration...');
        // Reload integrations
        await checkPermissions();
    } else {
        showNotification('Calendar permission denied. Please grant in System Settings.', 'error');
    }
}

async function openFullDiskAccessSettings() {
    await window.polly.permissionsOpenSettings('full_disk_access');
    showNotification('Please grant Full Disk Access in System Settings, then click "I\'ve Granted Access"');
}

// Check permissions on app startup
window.addEventListener('DOMContentLoaded', () => {
    checkPermissions();
});
```

---

## Testing Checklist

- [ ] **Fresh install with no permissions**
  - All 3 integrations show "Not Granted"
  - Grant buttons are visible

- [ ] **Grant Calendar permission**
  - Click "Grant Permission"
  - System dialog appears
  - Grant permission
  - Calendar integration enables automatically

- [ ] **Grant Reminders permission**
  - Click "Grant Permission"
  - System dialog appears
  - Grant permission
  - Reminders integration enables automatically

- [ ] **Grant Full Disk Access**
  - Click "Open System Settings"
  - System Settings opens to Privacy & Security
  - User toggles on "Polly"
  - User clicks "I've Granted Access"
  - File System integration enables

- [ ] **Deny Calendar permission**
  - Click "Grant Permission"
  - Deny in system dialog
  - Helpful message shows
  - Integration stays disabled

- [ ] **Revoke permission**
  - Revoke Calendar permission in System Settings
  - Restart Polly
  - Calendar integration disabled
  - UI shows "Not Granted"

- [ ] **Partial permissions**
  - Grant Calendar but not Reminders
  - Only Calendar integration enabled
  - Reminders still shows "Grant Permission" button

---

## Dependencies

**Python Libraries:**
- `pyobjc-framework-EventKit` - Already installed ✅
- `xattr` - Already installed ✅

**macOS Frameworks:**
- EventKit.framework - Calendar & Reminders
- AppKit.framework - System dialogs

**No additional dependencies needed!**

---

## Documentation Updates

After Phase 9 completion:

- [ ] Update `/docs/integration_status.md` - Move Calendar, Reminders, FileSystem from "Disabled" to "Working"
- [ ] Update `/docs/calendar_signed_app_notes.md` - Add permission flow documentation
- [ ] Update `/docs/filesystem_integration.md` - Update status to "Working"
- [ ] Add user guide: How to grant permissions

---

## Why This Is Critical

**3 major integrations are complete but unusable:**
- Calendar: 200+ lines of working code
- Reminders: 150+ lines of working code
- File System: 900+ lines of working code

**Total impact:** ~1,400 lines of code and 3 major features unlocked by 2-3 days of work.

**User value:**
- Calendar context in conversations
- Reminder tracking
- File organization with natural language

**This phase has the highest ROI of any remaining work.**

---

**Last Updated:** January 21, 2026  
**Status:** Not Started  
**Priority:** ⚠️ CRITICAL - Should Be Done FIRST
