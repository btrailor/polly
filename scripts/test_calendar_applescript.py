#!/usr/bin/env python3
"""Test the AppleScript-based calendar integration."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.calendar_applescript import CalendarIntegration


async def main():
    print("=" * 60)
    print("Testing AppleScript Calendar Integration")
    print("=" * 60)
    print()
    
    # Create integration
    calendar = CalendarIntegration(days_ahead=7)
    
    print("Fetching calendar events for the next 7 days...")
    print()
    
    try:
        # Fetch events
        events = await calendar.fetch_data()
        
        print(f"✅ Successfully fetched {len(events)} events!")
        print()
        
        if events:
            print("Events:")
            print("-" * 60)
            for i, event in enumerate(events, 1):
                print(f"\n{i}. {event['title']}")
                print(f"   Calendar: {event['calendar']}")
                print(f"   Start: {event['start']}")
                print(f"   End: {event['end']}")
                if event.get('location'):
                    print(f"   Location: {event['location']}")
                if event.get('description'):
                    desc = event['description'][:100]
                    if len(event['description']) > 100:
                        desc += "..."
                    print(f"   Description: {desc}")
            
            print()
            print("=" * 60)
            print("Formatting for RAG...")
            print()
            
            # Format for RAG
            documents = calendar.format_for_rag(events)
            
            print(f"✅ Created {len(documents)} RAG documents")
            print()
            print("Sample document:")
            print("-" * 60)
            print(documents[0]['content'])
            print()
            print("Metadata:", documents[0]['metadata'])
            
        else:
            print("No events found in the next 7 days.")
        
        print()
        print("=" * 60)
        print("✅ Calendar integration working via AppleScript!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
