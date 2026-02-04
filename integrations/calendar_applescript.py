"""
Calendar integration using AppleScript bridge.
This works around permission issues by using AppleScript to access Calendar.
"""

import subprocess
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class CalendarIntegration(Integration):
    """Fetch calendar events using AppleScript bridge."""
    
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
    
    async def fetch_data(self, days_ahead: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch calendar events using AppleScript.
        
        Args:
            days_ahead: Override default days_ahead value
            
        Returns:
            Dict with events and metadata
        """
        days = days_ahead if days_ahead is not None else self.days_ahead
        
        # Calculate date range
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Format dates for AppleScript (YYYY-MM-DD)
        start_str = start_date.strftime("%m/%d/%Y")
        end_str = end_date.strftime("%m/%d/%Y")
        
        # AppleScript to fetch events
        applescript = f'''
        set startDate to date "{start_str}"
        set endDate to date "{end_str}"
        set endDate to endDate + (24 * 60 * 60) -- Add one day to be inclusive
        
        set output to ""
        
        tell application "Calendar"
            set allCalendars to calendars
            repeat with cal in allCalendars
                set calName to name of cal
                set allEvents to events of cal
                
                repeat with evt in allEvents
                    set eventStart to start date of evt
                    
                    -- Check if event is in date range
                    if eventStart ≥ startDate and eventStart ≤ endDate then
                        set eventSummary to summary of evt
                        set eventEnd to end date of evt
                        set eventLocation to ""
                        try
                            set eventLocation to location of evt
                        end try
                        set eventDescription to ""
                        try
                            set eventDescription to description of evt
                        end try
                        
                        -- Format: CALENDAR|||SUMMARY|||START|||END|||LOCATION|||DESCRIPTION
                        set output to output & calName & "|||" & eventSummary & "|||" & (eventStart as string) & "|||" & (eventEnd as string) & "|||" & eventLocation & "|||" & eventLocation & "|||" & eventDescription & "\\n"
                    end if
                end repeat
            end repeat
        end tell
        
        return output
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=120  # Increased to 2 minutes for large calendars
            )
            
            if result.returncode != 0:
                raise Exception(f"AppleScript error: {result.stderr}")
            
            # Parse output
            events = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = line.split('|||')
                if len(parts) >= 6:
                    calendar_name, summary, start, end, location, description = parts[:6]
                    
                    events.append({
                        'calendar': calendar_name,
                        'title': summary,
                        'start': start,
                        'end': end,
                        'location': location,
                        'description': description,
                        'source': 'calendar'
                    })
            
            # Return in expected format with metadata
            return {
                "events": events,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat(),
                    "event_count": len(events),
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    },
                    "method": "applescript"
                }
            }
            
        except subprocess.TimeoutExpired:
            raise IntegrationError("Calendar access timed out - you may need to grant permission")
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
