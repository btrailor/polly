#!/usr/bin/env python3
"""
Request Calendar/Reminders permissions with proper event loop handling.
"""

import sys
import time
from Foundation import NSRunLoop, NSDate
from EventKit import EKEventStore

def request_calendar_access():
    """Request Calendar permissions."""
    print("\n🗓  Requesting Calendar access...")
    print("   A system permission prompt should appear.")
    print("   Please click 'OK' to grant access.\n")
    
    store = EKEventStore.alloc().init()
    result = {'granted': None, 'done': False}
    
    def completion(granted, error):
        result['granted'] = granted
        result['done'] = True
        if error:
            print(f"   ✗ Error: {error}")
        elif granted:
            print("   ✓ Calendar access GRANTED!")
        else:
            print("   ✗ Calendar access DENIED")
    
    store.requestFullAccessToEventsWithCompletion_(completion)
    
    # Run the event loop until we get a result
    timeout = time.time() + 30  # 30 second timeout
    while not result['done'] and time.time() < timeout:
        NSRunLoop.currentRunLoop().runUntilDate_(
            NSDate.dateWithTimeIntervalSinceNow_(0.1)
        )
    
    if not result['done']:
        print("   ⏱  Timeout waiting for permission response")
        return False
    
    return result['granted']

def request_reminders_access():
    """Request Reminders permissions."""
    print("\n✅ Requesting Reminders access...")
    print("   A system permission prompt should appear.")
    print("   Please click 'OK' to grant access.\n")
    
    store = EKEventStore.alloc().init()
    result = {'granted': None, 'done': False}
    
    def completion(granted, error):
        result['granted'] = granted
        result['done'] = True
        if error:
            print(f"   ✗ Error: {error}")
        elif granted:
            print("   ✓ Reminders access GRANTED!")
        else:
            print("   ✗ Reminders access DENIED")
    
    store.requestFullAccessToRemindersWithCompletion_(completion)
    
    # Run the event loop until we get a result
    timeout = time.time() + 30  # 30 second timeout
    while not result['done'] and time.time() < timeout:
        NSRunLoop.currentRunLoop().runUntilDate_(
            NSDate.dateWithTimeIntervalSinceNow_(0.1)
        )
    
    if not result['done']:
        print("   ⏱  Timeout waiting for permission response")
        return False
    
    return result['granted']

if __name__ == "__main__":
    print("="*60)
    print("Polly - Calendar & Reminders Permission Request")
    print("="*60)
    
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "both"
    
    calendar_granted = False
    reminders_granted = False
    
    if mode in ["calendar", "both"]:
        calendar_granted = request_calendar_access()
    
    if mode in ["reminders", "both"]:
        reminders_granted = request_reminders_access()
    
    print("\n" + "="*60)
    print("SUMMARY:")
    if mode in ["calendar", "both"]:
        print(f"  Calendar:  {'✓ GRANTED' if calendar_granted else '✗ DENIED'}")
    if mode in ["reminders", "both"]:
        print(f"  Reminders: {'✓ GRANTED' if reminders_granted else '✗ DENIED'}")
    print("="*60)
    
    if (mode == "calendar" and calendar_granted) or \
       (mode == "reminders" and reminders_granted) or \
       (mode == "both" and calendar_granted and reminders_granted):
        print("\n✓ You can now use these integrations in Polly!")
        sys.exit(0)
    else:
        print("\n⚠  Some permissions were denied.")
        print("   You can change this later in System Settings > Privacy & Security")
        sys.exit(1)
