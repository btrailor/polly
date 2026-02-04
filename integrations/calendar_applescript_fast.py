"""
Calendar integration using AppleScript (optimized version).
Fetches all events from primary calendar, filters in Python.
"""

import subprocess
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class CalendarIntegration(Integration):
    """Fetch calendar events using AppleScript (fast, limited to primary calendar)."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize calendar integration.
        
        Args:
            config: Optional configuration dict with 'days_ahead' key
        """
        super().__init__("calendar", config)
        self.days_ahead = config.get("days_ahead", 7) if config else 7
    
    async def connect(self, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to Calendar via AppleScript.
        No credentials needed - uses AppleScript access.
        """
        try:
            # Test access by trying to get calendar list
            test_script = 'tell application "Calendar" to get name of calendars'
            result = subprocess.run(
                ['osascript', '-e', test_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("Calendar access via AppleScript successful")
                self._set_status(IntegrationStatus.CONNECTED)
                return True
            else:
                raise IntegrationError(f"Calendar access failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise IntegrationError("Calendar access timed out")
        except Exception as e:
            logger.error(f"Calendar connection failed: {e}")
            raise IntegrationError(f"Failed to connect to Calendar: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from Calendar."""
        self._set_status(IntegrationStatus.DISCONNECTED)
        return True
    
    async def test_connection(self) -> bool:
        """Test Calendar connection."""
        try:
            test_script = 'tell application "Calendar" to get name of calendars'
            result = subprocess.run(
                ['osascript', '-e', test_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _parse_applescript_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse AppleScript date string to datetime.
        Format: "Monday, January 20, 2026 at 3:00:00 PM"
        """
        try:
            # Remove day of week
            date_str = re.sub(r'^[A-Za-z]+day,\s+', '', date_str)
            # Parse: "January 20, 2026 at 3:00:00 PM"
            return datetime.strptime(date_str, "%B %d, %Y at %I:%M:%S %p")
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None
    
    async def fetch_data(self, days_ahead: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch calendar events using AppleScript.
        Gets ALL events from primary calendar, filters in Python.
        
        Args:
            days_ahead: Override default days_ahead value
            
        Returns:
            Dict with events and metadata
        """
        days = days_ahead if days_ahead is not None else self.days_ahead
        
        # Calculate date range for filtering
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Simple AppleScript - get all events from first calendar (fast!)
        applescript = '''
        tell application "Calendar"
            set output to ""
            set cal to calendar 1
            set calName to title of cal
            set allEvents to events of cal
            
            repeat with evt in allEvents
                try
                    set eventSummary to summary of evt
                    set eventStart to start date of evt
                    set eventEnd to end date of evt
                    set eventLocation to ""
                    try
                        set eventLocation to location of evt
                    end try
                    set eventDescription to ""
                    try
                        set eventDescription to description of evt
                    end try
                    
                    set output to output & calName & "|||" & eventSummary & "|||" & (eventStart as string) & "|||" & (eventEnd as string) & "|||" & eventLocation & "|||" & eventDescription & return
                end try
            end repeat
            
            return output
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=30  # Should be fast now
            )
            
            if result.returncode != 0:
                raise Exception(f"AppleScript error: {result.stderr}")
            
            # Parse output and filter by date in Python
            all_events = []
            filtered_events = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = line.split('|||')
                if len(parts) >= 6:
                    calendar_name, summary, start_str, end_str, location, description = parts[:6]
                    
                    # Parse dates
                    start_dt = self._parse_applescript_date(start_str)
                    end_dt = self._parse_applescript_date(end_str)
                    
                    if start_dt:
                        all_events.append({
                            'calendar': calendar_name,
                            'title': summary,
                            'start': start_dt,
                            'end': end_dt or start_dt,
                            'location': location if location != 'NONE' else '',
                            'description': description if description != 'NONE' else '',
                            'source': 'calendar'
                        })
                        
                        # Filter by date range
                        if start_date <= start_dt <= end_date:
                            filtered_events.append(all_events[-1])
            
            logger.info(f"Fetched {len(all_events)} total events, {len(filtered_events)} in date range")
            
            # Format for output
            output_events = []
            for evt in filtered_events:
                output_events.append({
                    'calendar': evt['calendar'],
                    'title': evt['title'],
                    'start': evt['start'].strftime('%Y-%m-%d %H:%M:%S'),
                    'end': evt['end'].strftime('%Y-%m-%d %H:%M:%S'),
                    'location': evt['location'],
                    'description': evt['description'],
                    'source': evt['source']
                })
            
            # Return in expected format with metadata
            return {
                "events": output_events,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat(),
                    "event_count": len(output_events),
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    },
                    "method": "applescript-fast"
                }
            }
            
        except subprocess.TimeoutExpired:
            raise IntegrationError("Calendar access timed out")
        except Exception as e:
            raise IntegrationError(f"Failed to fetch calendar events: {str(e)}")
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Format calendar events for RAG indexing.
        
        Args:
            data: Dict with 'events' key containing list of event dictionaries
            
        Returns:
            List of formatted documents for indexing
        """
        # Extract events from data dict
        events = data.get("events", []) if isinstance(data, dict) else data
        
        documents = []
        
        for event in events:
            # Create searchable text
            text_parts = [
                f"Calendar Event: {event['title']}",
                f"Calendar: {event['calendar']}",
                f"Start: {event['start']}",
                f"End: {event['end']}"
            ]
            
            if event.get('location'):
                text_parts.append(f"Location: {event['location']}")
            
            if event.get('description'):
                text_parts.append(f"Description: {event['description']}")
            
            content = '\n'.join(text_parts)
            
            # Create metadata
            metadata = {
                'source': 'calendar',
                'calendar': event['calendar'],
                'title': event['title'],
                'start': event['start'],
                'type': 'calendar_event'
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        return documents
