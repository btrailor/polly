#!/usr/bin/env python3
"""
Directly attempt to access Calendar and Reminders using EventKit.
This should trigger macOS permission dialogs for the Python/Terminal process.
"""

import sys
import objc
from Foundation import NSRunLoop, NSDate
from EventKit import EKEventStore, EKEntityTypeEvent, EKEntityTypeReminder

print("=" * 60)
print("Polly Permission Trigger")
print("=" * 60)
print("\nThis script will attempt to access Calendar and Reminders.")
print("You should see macOS permission dialogs.")
print("Please click 'OK' or 'Allow' when prompted.\n")

# Create EventKit store
store = EKEventStore.alloc().init()

print("\n🗓️  Attempting to access Calendar...")
print("   (You should see a permission dialog now)")

# Request Calendar access
def calendar_callback(granted, error):
    if granted:
        print("\n✅ Calendar access GRANTED!")
        calendars = store.calendarsForEntityType_(EKEntityTypeEvent)
        print(f"   Found {len(calendars)} calendars")
        for cal in calendars[:5]:  # Show first 5
            print(f"   - {cal.title()}")
    else:
        print(f"\n❌ Calendar access DENIED")
        if error:
            print(f"   Error: {error}")

# Request Reminders access
def reminders_callback(granted, error):
    if granted:
        print("\n✅ Reminders access GRANTED!")
        # Try to get reminder lists
        calendars = store.calendarsForEntityType_(EKEntityTypeReminder)
        print(f"   Found {len(calendars)} reminder lists")
        for cal in calendars[:5]:  # Show first 5
            print(f"   - {cal.title()}")
    else:
        print(f"\n❌ Reminders access DENIED")
        if error:
            print(f"   Error: {error}")

# Request both permissions
print("   Requesting Calendar permission...")
store.requestAccessToEntityType_completion_(EKEntityTypeEvent, calendar_callback)

print("\n✅ Attempting to access Reminders...")
print("   (You should see another permission dialog)")
print("   Requesting Reminders permission...")
store.requestAccessToEntityType_completion_(EKEntityTypeReminder, reminders_callback)

# Run the event loop to wait for callbacks
print("\n⏳ Waiting for permission responses...")
print("   (This may take a few seconds after you respond to dialogs)")

# Wait for callbacks to complete
NSRunLoop.currentRunLoop().runUntilDate_(
    NSDate.dateWithTimeIntervalSinceNow_(10.0)
)

print("\n" + "=" * 60)
print("Permission Request Complete")
print("=" * 60)
print("\nNow checking final permission status...")

# Check final status
from EventKit import EKAuthorizationStatusAuthorized, EKAuthorizationStatusDenied, EKAuthorizationStatusRestricted, EKAuthorizationStatusNotDetermined

cal_status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeEvent)
rem_status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeReminder)

status_names = {
    EKAuthorizationStatusNotDetermined: "NOT DETERMINED",
    EKAuthorizationStatusRestricted: "RESTRICTED",
    EKAuthorizationStatusDenied: "DENIED",
    EKAuthorizationStatusAuthorized: "AUTHORIZED ✅"
}

print(f"\nCalendar: {status_names.get(cal_status, 'UNKNOWN')}")
print(f"Reminders: {status_names.get(rem_status, 'UNKNOWN')}")

if cal_status == EKAuthorizationStatusAuthorized and rem_status == EKAuthorizationStatusAuthorized:
    print("\n🎉 SUCCESS! Both permissions granted!")
    print("\nNext steps:")
    print("  1. Restart the Polly server")
    print("  2. Click 'Enable' on Calendar and Reminders in Polly UI")
else:
    print("\n⚠️  Permissions not fully granted.")
    print("\nIf you clicked 'Don't Allow' by mistake:")
    print("  1. Open System Settings > Privacy & Security")
    print("  2. Go to Calendar / Reminders")
    print("  3. Find iTerm or Terminal in the list")
    print("  4. Toggle it ON")
    print("  5. Re-run this script")
