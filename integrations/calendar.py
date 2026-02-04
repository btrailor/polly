"""
macOS Calendar Integration
Fetches and indexes calendar events using EventKit
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)

try:
    from EventKit import (
        EKEventStore, 
        EKEntityTypeEvent,
        EKAuthorizationStatusAuthorized,
        EKAuthorizationStatusDenied,
        EKAuthorizationStatusRestricted,
        EKAuthorizationStatusNotDetermined
    )
    EVENTKIT_AVAILABLE = True
except ImportError:
    logger.warning("EventKit not available - Calendar integration will not work")
    EVENTKIT_AVAILABLE = False


class CalendarIntegration(Integration):
    """
    macOS Calendar integration for Polly.
    
    Fetches and indexes:
    - Upcoming calendar events
    - Event details (title, time, location, attendees, notes)
    - All calendar sources (iCloud, Google, Exchange, etc.)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("calendar", config)
        self.event_store: Optional[Any] = None
        self.days_ahead = config.get("days_ahead", 7) if config else 7
        
        if not EVENTKIT_AVAILABLE:
            raise IntegrationError("EventKit framework not available. Install pyobjc-framework-EventKit")
    
    async def connect(self, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to macOS Calendar using EventKit.
        No credentials needed - uses system calendar access.
        
        Note: This will attempt to connect. If access is denied,
        user needs to grant permissions in System Settings.
        """
        try:
            # Create event store
            self.event_store = EKEventStore.alloc().init()
            
            # Check authorization status
            auth_status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeEvent)
            
            if auth_status == EKAuthorizationStatusAuthorized:
                logger.info("Calendar access already authorized")
                self._set_status(IntegrationStatus.CONNECTED)
                return True
            
            elif auth_status == 4:
                # Status 4 appears on macOS Sequoia beta - seems to work despite unknown status
                logger.info("Calendar access status code 4 (unknown, possibly Sequoia beta) - attempting access...")
                # Try to access calendars to verify
                try:
                    calendars = self.event_store.calendarsForEntityType_(EKEntityTypeEvent)
                    logger.info(f"Successfully accessed {len(calendars)} calendars with status 4")
                    self._set_status(IntegrationStatus.CONNECTED)
                    return True
                except Exception as e:
                    raise IntegrationError(f"Calendar access failed despite status 4: {e}")
            
            elif auth_status == EKAuthorizationStatusNotDetermined:
                # Need to request access - this will show system prompt
                logger.info("Requesting calendar access...")
                raise IntegrationError(
                    "Calendar access not yet granted. "
                    "Please go to System Settings > Privacy & Security > Calendars "
                    "and enable access for Terminal/Python, then try again."
                )
            
            elif auth_status == EKAuthorizationStatusDenied:
                raise IntegrationError(
                    "Calendar access denied. "
                    "Enable in System Settings > Privacy & Security > Calendars"
                )
            
            elif auth_status == EKAuthorizationStatusRestricted:
                raise IntegrationError("Calendar access restricted by system policy")
            
            else:
                # Unknown status - try to access anyway
                logger.warning(f"Unknown authorization status: {auth_status} - attempting access...")
                try:
                    calendars = self.event_store.calendarsForEntityType_(EKEntityTypeEvent)
                    logger.info(f"Successfully accessed {len(calendars)} calendars with unknown status")
                    self._set_status(IntegrationStatus.CONNECTED)
                    return True
                except Exception as e:
                    raise IntegrationError(f"Calendar access failed with unknown status {auth_status}: {e}")
            
            return False
            
        except IntegrationError:
            raise
        except Exception as e:
            logger.error(f"Calendar connection failed: {e}")
            raise IntegrationError(f"Failed to connect to Calendar: {e}")
    
    async def _request_access(self) -> bool:
        """
        Request calendar access from user.
        Note: This is deprecated - use system settings instead.
        """
        # The callback-based approach doesn't work well in our async context
        # User should grant permissions via System Settings
        return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Calendar."""
        self.event_store = None
        self._set_status(IntegrationStatus.DISCONNECTED)
        return True
    
    async def test_connection(self) -> bool:
        """Test Calendar connection by fetching calendars."""
        if not self.event_store:
            return False
        
        try:
            calendars = self.event_store.calendarsForEntityType_(EKEntityTypeEvent)
            return len(calendars) > 0
        except Exception as e:
            logger.error(f"Calendar test failed: {e}")
            return False
    
    async def fetch_data(
        self,
        days_ahead: int = None,
        calendar_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch calendar events.
        
        Args:
            days_ahead: How many days ahead to fetch (default: 7)
            calendar_names: Filter by calendar names (default: all calendars)
            
        Returns:
            Dict with events and metadata
        """
        if not self.event_store:
            raise IntegrationError("Not connected to Calendar")
        
        days = days_ahead or self.days_ahead
        
        self._set_status(IntegrationStatus.SYNCING)
        
        try:
            # Get date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            
            # Get all calendars
            all_calendars = self.event_store.calendarsForEntityType_(EKEntityTypeEvent)
            
            # Filter calendars if specified
            if calendar_names:
                calendars = [
                    cal for cal in all_calendars 
                    if cal.title() in calendar_names
                ]
            else:
                calendars = all_calendars
            
            # Create predicate for date range
            predicate = self.event_store.predicateForEventsWithStartDate_endDate_calendars_(
                start_date,
                end_date,
                calendars
            )
            
            # Fetch events
            events = self.event_store.eventsMatchingPredicate_(predicate)
            
            logger.info(f"Fetched {len(events)} events from {len(calendars)} calendars")
            
            # Format events for RAG
            formatted_events = []
            for event in events:
                event_data = self._format_event(event)
                formatted_events.append(event_data)
            
            self._set_status(IntegrationStatus.CONNECTED)
            
            return {
                "events": formatted_events,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat(),
                    "calendar_count": len(calendars),
                    "event_count": len(events),
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    }
                }
            }
            
        except Exception as e:
            self._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Failed to fetch calendar events: {e}")
    
    def _format_event(self, event) -> Dict[str, Any]:
        """Format an EventKit event for RAG indexing."""
        # Get event details
        title = event.title() or "Untitled Event"
        start_date = event.startDate()
        end_date = event.endDate()
        location = event.location() or ""
        notes = event.notes() or ""
        calendar_name = event.calendar().title()
        
        # Format attendees
        attendees = []
        if event.attendees():
            for attendee in event.attendees():
                name = attendee.name() or attendee.emailAddress() or "Unknown"
                attendees.append(name)
        
        # Create searchable content
        content_parts = [
            f"Event: {title}",
            f"When: {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%H:%M')}",
            f"Calendar: {calendar_name}"
        ]
        
        if location:
            content_parts.append(f"Location: {location}")
        
        if attendees:
            content_parts.append(f"Attendees: {', '.join(attendees)}")
        
        if notes:
            content_parts.append(f"Notes: {notes}")
        
        content = "\n".join(content_parts)
        
        return {
            "title": title,
            "content": content,
            "source": "macOS Calendar",
            "event_id": event.eventIdentifier(),
            "calendar": calendar_name,
            "start_time": start_date.isoformat(),
            "end_time": end_date.isoformat(),
            "location": location,
            "attendees": attendees,
            "notes": notes,
            "all_day": event.isAllDay(),
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Format calendar data for RAG indexing.
        
        Returns list of documents with title, content, and metadata.
        """
        if "events" not in data:
            return []
        
        documents = []
        for event in data["events"]:
            doc = {
                "title": event["title"],
                "content": event["content"],
                "source": event["source"],
                "metadata": {
                    "calendar": event["calendar"],
                    "start_time": event["start_time"],
                    "end_time": event["end_time"],
                    "location": event["location"],
                    "attendees": event["attendees"],
                    "all_day": event["all_day"]
                }
            }
            documents.append(doc)
        
        return documents
