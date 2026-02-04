#!/usr/bin/env python3
"""Detailed calendar permission check."""

from EventKit import (
    EKEventStore, 
    EKEntityTypeEvent,
    EKAuthorizationStatusAuthorized,
    EKAuthorizationStatusDenied,
    EKAuthorizationStatusRestricted,
    EKAuthorizationStatusNotDetermined
)

print("Checking Calendar permissions...\n")

store = EKEventStore.alloc().init()
status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeEvent)

print(f"Raw status code: {status}")

status_map = {
    EKAuthorizationStatusNotDetermined: ("NOT DETERMINED", "Permission not yet requested"),
    EKAuthorizationStatusRestricted: ("RESTRICTED", "Access restricted by policy"),
    EKAuthorizationStatusDenied: ("DENIED", "User denied access"),
    EKAuthorizationStatusAuthorized: ("AUTHORIZED", "Access granted")
}

status_name, description = status_map.get(status, ("UNKNOWN", f"Unknown status: {status}"))

print(f"Status: {status_name}")
print(f"Description: {description}")
print()

if status == EKAuthorizationStatusAuthorized:
    print("✅ Calendar access is AUTHORIZED!")
    print("EventKit integration should work.")
    
    # Try to fetch calendars
    print("\nTesting calendar access...")
    calendars = store.calendarsForEntityType_(EKEntityTypeEvent)
    print(f"Found {len(calendars)} calendars:")
    for cal in calendars:
        print(f"  - {cal.title()}")
else:
    print(f"❌ Calendar access is {status_name}")
    print("EventKit integration will NOT work.")
    print("\nTo fix:")
    print("  1. Open System Settings")
    print("  2. Go to Privacy & Security > Calendar")
    print("  3. Enable access for Python/Terminal/iTerm")
