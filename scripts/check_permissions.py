#!/usr/bin/env python3
"""
Check current Calendar/Reminders permission status.
"""

from EventKit import (
    EKEventStore,
    EKEntityTypeEvent,
    EKEntityTypeReminder,
    EKAuthorizationStatusAuthorized,
    EKAuthorizationStatusDenied,
    EKAuthorizationStatusRestricted,
    EKAuthorizationStatusNotDetermined
)

def status_name(status):
    if status == EKAuthorizationStatusAuthorized:
        return "✓ AUTHORIZED"
    elif status == EKAuthorizationStatusDenied:
        return "✗ DENIED"
    elif status == EKAuthorizationStatusRestricted:
        return "⚠ RESTRICTED"
    elif status == EKAuthorizationStatusNotDetermined:
        return "? NOT DETERMINED (not yet requested)"
    else:
        return f"UNKNOWN ({status})"

# Check Calendar
calendar_status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeEvent)
print(f"Calendar: {status_name(calendar_status)}")

# Check Reminders
reminders_status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeReminder)
print(f"Reminders: {status_name(reminders_status)}")

print("\n" + "="*60)
if calendar_status == EKAuthorizationStatusDenied or reminders_status == EKAuthorizationStatusDenied:
    print("TO FIX DENIED PERMISSIONS:")
    print("1. Open System Settings")
    print("2. Go to Privacy & Security")
    print("3. Click 'Calendars' or 'Reminders'")
    print("4. Find 'Python' or 'Terminal' in the list")
    print("5. Enable the checkbox")
    print("6. Restart Polly")
elif calendar_status == EKAuthorizationStatusNotDetermined or reminders_status == EKAuthorizationStatusNotDetermined:
    print("Permissions not yet requested. Run the request script to trigger prompts.")
elif calendar_status == EKAuthorizationStatusAuthorized and reminders_status == EKAuthorizationStatusAuthorized:
    print("All permissions granted! You can use Calendar and Reminders integrations.")
