#!/usr/bin/env python3
"""Test the EventKit-based calendar integration."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.calendar import CalendarIntegration


async def main():
    print("=" * 60)
    print("Testing EventKit Calendar Integration")
    print("=" * 60)
    print()
    
    # Create integration
    calendar = CalendarIntegration(config={"days_ahead": 7})
    
    print("Connecting to Calendar...")
    try:
        connected = await calendar.connect()
        if not connected:
            print("❌ Failed to connect to Calendar")
            return 1
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return 1
    
    print("Fetching calendar events for the next 7 days...")
    print()
    
    try:
        # Fetch events
        result = await calendar.fetch_data()
        events = result.get("events", [])
        
        print(f"✅ Successfully fetched {len(events)} events!")
        print()
        
        if events:
            print("Events:")
            print("-" * 60)
            for i, event in enumerate(events[:5], 1):  # Show first 5
                print(f"\n{i}. {event['title']}")
                print(f"   Calendar: {event['calendar']}")
                print(f"   Start: {event['start']}")
                print(f"   End: {event['end']}")
                if event.get('location'):
                    print(f"   Location: {event['location']}")
            
            if len(events) > 5:
                print(f"\n... and {len(events) - 5} more events")
            
            print()
            print("=" * 60)
            print("✅ EventKit Calendar integration working!")
            print("=" * 60)
        else:
            print("No events found in the next 7 days.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
