#!/usr/bin/env python3
"""
Direct permission request using subprocess to call osascript.
This should trigger permission dialogs for the Python/Terminal process.
"""

import subprocess
import sys

def request_calendar_permission():
    """Request Calendar permission by accessing via AppleScript."""
    print("🗓️  Requesting Calendar permission...")
    
    applescript = '''
    tell application "Calendar"
        try
            set calendarCount to count of calendars
            return "SUCCESS: Found " & calendarCount & " calendars"
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"   Result: {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("   ⏱️  Timed out - you may need to respond to a dialog")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def request_reminders_permission():
    """Request Reminders permission by accessing via AppleScript."""
    print("\n✅ Requesting Reminders permission...")
    
    applescript = '''
    tell application "Reminders"
        try
            set listCount to count of lists
            return "SUCCESS: Found " & listCount & " reminder lists"
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"   Result: {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("   ⏱️  Timed out - you may need to respond to a dialog")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Polly Permission Request")
    print("=" * 60)
    print("\nThis will attempt to trigger macOS permission dialogs.")
    print("If you see dialogs, please click 'OK' or 'Allow'.\n")
    
    input("Press Enter to continue...")
    
    calendar_ok = request_calendar_permission()
    reminders_ok = request_reminders_permission()
    
    print("\n" + "=" * 60)
    print("Permission Request Complete")
    print("=" * 60)
    
    if calendar_ok and reminders_ok:
        print("\n✅ Both permissions granted successfully!")
        print("\nNext steps:")
        print("  1. Restart the Polly server")
        print("  2. Try enabling Calendar and Reminders integrations")
    else:
        print("\n⚠️  Some permissions may not have been granted.")
        print("\nYou can also try manually:")
        print("  1. Open System Settings > Privacy & Security")
        print("  2. Go to Calendar and Reminders")
        print("  3. Enable access for iTerm/Terminal")

if __name__ == "__main__":
    main()
