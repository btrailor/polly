#!/usr/bin/env python3
"""
Request Calendar permission specifically.
"""

from Foundation import NSRunLoop, NSDate
from EventKit import EKEventStore, EKEntityTypeEvent

print("🗓️  Requesting Calendar Permission\n")

store = EKEventStore.alloc().init()

def calendar_callback(granted, error):
    if granted:
        print("✅ Calendar access GRANTED!")
        calendars = store.calendarsForEntityType_(EKEntityTypeEvent)
        print(f"Found {len(calendars)} calendars:")
        for cal in calendars:
            print(f"  - {cal.title()}")
    else:
        print("❌ Calendar access DENIED")
        if error:
            print(f"Error: {error}")

print("Requesting permission...")
print("(You should see a system dialog - click 'OK' or 'Allow')\n")

store.requestAccessToEntityType_completion_(EKEntityTypeEvent, calendar_callback)

# Wait for callback
print("Waiting for response...")
NSRunLoop.currentRunLoop().runUntilDate_(
    NSDate.dateWithTimeIntervalSinceNow_(10.0)
)

print("\nDone!")
