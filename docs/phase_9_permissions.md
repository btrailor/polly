# Phase 9: macOS Permission Handling

**Status**: 🔜 Planned  
**Dependencies**: Integrations (Calendar, Reminders, File System)  
**Goal**: Implement proper macOS permission request flows

## Overview

Phase 9 will implement the permission infrastructure needed to enable the 3 macOS integrations that are currently disabled: Calendar, Reminders, and File System. All the integration code is complete and tested - they just need proper permission handling.

## Currently Disabled Integrations

### 1. Calendar
- **Code Status**: ✅ Complete (`integrations/calendar.py`)
- **Required Permission**: EventKit (Calendar access)
- **Location**: Commented out in `server.py:116`

### 2. Reminders  
- **Code Status**: ✅ Complete and previously working
- **Required Permission**: EventKit (Reminders access)
- **Location**: Commented out in `server.py:117`

### 3. File System
- **Code Status**: ✅ Complete (`integrations/filesystem.py`)
- **Required Permission**: Full Disk Access
- **Location**: Commented out in `server.py:118`

## Required Permissions

### EventKit (Calendar & Reminders)
- **Framework**: EventKit.framework
- **Info.plist Keys**:
  - `NSCalendarsUsageDescription`: "Polly needs access to your calendars..."
  - `NSRemindersUsageDescription`: "Polly needs access to your reminders..."
- **Permission Type**: Runtime request with system dialog

### Full Disk Access (File System)
- **System Preference**: Security & Privacy > Privacy > Full Disk Access
- **Permission Type**: Manual user configuration in System Settings
- **TCC Database**: `/Library/Application Support/com.apple.TCC/TCC.db`

## Implementation Checklist

### 1. Permission Status Checking
- [ ] Create permission status checker utility
- [ ] Check EventKit authorization status
- [ ] Check Full Disk Access status
- [ ] Return user-friendly status messages

### 2. Permission Request Flow
- [ ] Design UI for permission requests
- [ ] Implement EventKit permission request
- [ ] Implement Full Disk Access instruction modal
- [ ] Show clear step-by-step instructions
- [ ] Handle permission granted/denied states

### 3. UI/UX Components
- [ ] Permission status indicators on integration cards
- [ ] "Grant Permission" buttons
- [ ] Permission explanation modals
- [ ] System Settings deep links (for Full Disk Access)
- [ ] Success/failure notifications

### 4. Graceful Degradation
- [ ] Detect when permissions are denied
- [ ] Show helpful error messages
- [ ] Provide links to documentation
- [ ] Offer retry mechanisms
- [ ] Cache permission status

### 5. Integration Enable/Disable
- [ ] Unified enable/disable toggle
- [ ] Check permissions before enabling
- [ ] Show permission requirements
- [ ] Guide user through permission setup
- [ ] Handle partial permissions (e.g., Calendar granted but not Reminders)

### 6. Testing
- [ ] Test permission request flows
- [ ] Test permission denial handling
- [ ] Test permission revocation
- [ ] Test integration enable/disable with permissions
- [ ] Test cross-integration scenarios

## UI Mockup Ideas

### Integration Card with Permissions

```
┌─────────────────────────────────────┐
│ 📅 Calendar                    [○]  │
│                                      │
│ ⚠️ Requires Calendar Permission     │
│                                      │
│ [ Grant Permission ]                 │
│                                      │
│ Why we need this:                   │
│ • Search your schedule              │
│ • Find meeting notes                │
│ • Context-aware responses           │
└─────────────────────────────────────┘
```

### Permission Request Modal

```
┌─────────────────────────────────────┐
│  Grant Calendar Access               │
│                                      │
│  Polly needs access to your         │
│  calendars to:                      │
│                                      │
│  ✓ Search your schedule             │
│  ✓ Find meeting context             │
│  ✓ Provide time-aware responses     │
│                                      │
│  [ Cancel ]  [ Grant Access → ]     │
└─────────────────────────────────────┘
```

### Full Disk Access Instructions

```
┌─────────────────────────────────────┐
│  Enable Full Disk Access             │
│                                      │
│  To use file organization features:  │
│                                      │
│  1. Open System Settings             │
│  2. Go to Privacy & Security         │
│  3. Click "Full Disk Access"         │
│  4. Toggle on "Polly"                │
│                                      │
│  [ Open System Settings → ]          │
│                                      │
│  [ I've Granted Access ]             │
└─────────────────────────────────────┘
```

## Permission Checker Utility (Pseudocode)

```python
# integrations/permissions.py

class PermissionManager:
    @staticmethod
    def check_calendar_permission() -> PermissionStatus:
        """Check EventKit Calendar authorization."""
        # Use EventKit authorization status
        pass
    
    @staticmethod
    def request_calendar_permission() -> bool:
        """Request Calendar permission (shows system dialog)."""
        # EventKit.EKEventStore.requestAccess()
        pass
    
    @staticmethod
    def check_reminders_permission() -> PermissionStatus:
        """Check EventKit Reminders authorization."""
        pass
    
    @staticmethod
    def check_full_disk_access() -> PermissionStatus:
        """Check Full Disk Access (read-only test)."""
        # Try to read from protected location
        try:
            # Attempt to read ~/Library/Safari/History.db
            # If successful, has Full Disk Access
            pass
        except PermissionError:
            return PermissionStatus.DENIED
    
    @staticmethod
    def open_system_settings(pane: str):
        """Open System Settings to specific pane."""
        # x-apple.systempreferences:com.apple.preference.security?Privacy_FullDiskAccess
        pass

class PermissionStatus(Enum):
    GRANTED = "granted"
    DENIED = "denied"
    NOT_DETERMINED = "not_determined"
    RESTRICTED = "restricted"
```

## API Endpoints

### GET `/polly/permissions/status`
Returns current permission status for all integrations:
```json
{
  "calendar": "granted|denied|not_determined",
  "reminders": "granted|denied|not_determined",
  "full_disk_access": "granted|denied"
}
```

### POST `/polly/permissions/request`
Request specific permission (triggers system dialog):
```json
{
  "permission": "calendar|reminders"
}
```

### GET `/polly/permissions/open-settings`
Opens System Settings to relevant pane:
```
?pane=full_disk_access
```

## Server Changes

In `interfaces/server.py`, uncomment these lines after Phase 9:

```python
# BEFORE Phase 9:
# macOS integrations disabled until Phase 9 (permission handling)
# manager.register_integration(CalendarIntegration())
# manager.register_integration(RemindersIntegration())
# manager.register_integration(FileSystemIntegration())

# AFTER Phase 9:
# macOS integrations (requires permissions - see Phase 9)
if PermissionManager.check_calendar_permission().is_granted():
    manager.register_integration(CalendarIntegration())
if PermissionManager.check_reminders_permission().is_granted():
    manager.register_integration(RemindersIntegration())
if PermissionManager.check_full_disk_access().is_granted():
    manager.register_integration(FileSystemIntegration())
```

## Testing Checklist

- [ ] Fresh install with no permissions
- [ ] Grant Calendar → should enable Calendar integration
- [ ] Grant Reminders → should enable Reminders integration  
- [ ] Grant Full Disk Access → should enable File System integration
- [ ] Deny Calendar → should show helpful message
- [ ] Revoke permission → should disable integration gracefully
- [ ] Multiple permission requests
- [ ] Partial permissions (e.g., only Calendar granted)

## Dependencies

### Python Libraries
- **pyobjc-framework-EventKit** - Already installed for EventKit access
- **xattr** - Already installed for File System tags

### macOS Frameworks
- **EventKit.framework** - Calendar & Reminders
- **AppKit.framework** - System dialogs and deep links

### No Additional Dependencies Needed
All required frameworks and libraries are already in place from the integration implementations.

## Timeline Estimate

- **Permission checker utility**: 2-4 hours
- **UI components**: 4-6 hours
- **Backend endpoints**: 2-3 hours
- **Integration with existing code**: 2-3 hours
- **Testing**: 3-4 hours
- **Documentation**: 1-2 hours

**Total**: ~15-22 hours (2-3 days)

## Success Criteria

✅ Users can see permission status on integration cards  
✅ Users can grant permissions through Polly UI  
✅ System permission dialogs appear correctly  
✅ Integrations automatically enable when permissions granted  
✅ Helpful error messages when permissions denied  
✅ System Settings opens to correct pane for Full Disk Access  
✅ All 3 macOS integrations (Calendar, Reminders, File System) working  

## Documentation Updates

After Phase 9 completion, update:
- [ ] `/docs/integration_status.md` - Move integrations from "Disabled" to "Working"
- [ ] `/docs/calendar_signed_app_notes.md` - Update with permission flow notes
- [ ] `/docs/filesystem_integration.md` - Update status from disabled to active
- [ ] User documentation - Add permission setup guide

## Notes

- EventKit permissions show native macOS dialogs automatically
- Full Disk Access requires manual System Settings configuration
- Permission status should be cached and refreshed periodically
- Integrations should handle permission revocation gracefully
- Consider showing permission status in menu bar/tray icon

---

**Once Phase 9 is complete**, simply uncomment 3 lines in `server.py` and all macOS integrations will be fully operational. All the hard work (integration implementations) is already done! 🎉
