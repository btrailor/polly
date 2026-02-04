"""
macOS Reminders Integration
Fetches and indexes reminders/tasks using EventKit
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)

try:
    from EventKit import (
        EKEventStore, 
        EKEntityTypeReminder,
        EKAuthorizationStatusAuthorized,
        EKAuthorizationStatusDenied,
        EKAuthorizationStatusRestricted,
        EKAuthorizationStatusNotDetermined
    )
    EVENTKIT_AVAILABLE = True
except ImportError:
    logger.warning("EventKit not available - Reminders integration will not work")
    EVENTKIT_AVAILABLE = False


class RemindersIntegration(Integration):
    """
    macOS Reminders integration for Polly.
    
    Fetches and indexes:
    - Incomplete reminders/tasks
    - Reminder details (title, notes, priority, due date)
    - All reminder lists (personal, work, shopping, etc.)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("reminders", config)
        self.event_store: Optional[Any] = None
        self.include_completed = config.get("include_completed", False) if config else False
        
        if not EVENTKIT_AVAILABLE:
            raise IntegrationError("EventKit framework not available. Install pyobjc-framework-EventKit")
    
    async def connect(self, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to macOS Reminders using EventKit.
        No credentials needed - uses system reminders access.
        
        Will prompt for Reminders permissions on first access.
        """
        try:
            # Create event store
            self.event_store = EKEventStore.alloc().init()
            
            # Check/request authorization
            auth_status = EKEventStore.authorizationStatusForEntityType_(EKEntityTypeReminder)
            
            if auth_status == EKAuthorizationStatusAuthorized:
                logger.info("Reminders access already authorized")
                self._set_status(IntegrationStatus.CONNECTED)
                return True
            
            elif auth_status == EKAuthorizationStatusNotDetermined:
                logger.info("Requesting reminders access...")
                # Request access (will show system prompt)
                success = await self._request_access()
                if success:
                    self._set_status(IntegrationStatus.CONNECTED)
                    return True
                else:
                    raise IntegrationError("Reminders access denied by user")
            
            elif auth_status == EKAuthorizationStatusDenied:
                raise IntegrationError(
                    "Reminders access denied. "
                    "Enable in System Settings > Privacy & Security > Reminders"
                )
            
            elif auth_status == EKAuthorizationStatusRestricted:
                raise IntegrationError("Reminders access restricted by system policy")
            
            return False
            
        except Exception as e:
            logger.error(f"Reminders connection failed: {e}")
            raise IntegrationError(f"Failed to connect to Reminders: {e}")
    
    async def _request_access(self) -> bool:
        """Request reminders access from user."""
        import asyncio
        
        # EventKit uses callbacks, we need to wrap it in asyncio
        future = asyncio.get_event_loop().create_future()
        
        def completion_handler(granted, error):
            if error:
                logger.error(f"Reminders access error: {error}")
                future.set_result(False)
            else:
                future.set_result(granted)
        
        self.event_store.requestFullAccessToRemindersWithCompletion_(completion_handler)
        
        result = await future
        return result
    
    async def disconnect(self) -> bool:
        """Disconnect from Reminders."""
        self.event_store = None
        self._set_status(IntegrationStatus.DISCONNECTED)
        return True
    
    async def test_connection(self) -> bool:
        """Test Reminders connection by fetching reminder lists."""
        if not self.event_store:
            return False
        
        try:
            calendars = self.event_store.calendarsForEntityType_(EKEntityTypeReminder)
            return len(calendars) > 0
        except Exception as e:
            logger.error(f"Reminders test failed: {e}")
            return False
    
    async def fetch_data(
        self,
        list_names: List[str] = None,
        include_completed: bool = None
    ) -> Dict[str, Any]:
        """
        Fetch reminders.
        
        Args:
            list_names: Filter by list names (default: all lists)
            include_completed: Include completed reminders (default: False)
            
        Returns:
            Dict with reminders and metadata
        """
        if not self.event_store:
            raise IntegrationError("Not connected to Reminders")
        
        include_completed = include_completed if include_completed is not None else self.include_completed
        
        self._set_status(IntegrationStatus.SYNCING)
        
        try:
            # Get all reminder lists (calendars)
            all_lists = self.event_store.calendarsForEntityType_(EKEntityTypeReminder)
            
            # Filter lists if specified
            if list_names:
                lists = [
                    lst for lst in all_lists 
                    if lst.title() in list_names
                ]
            else:
                lists = all_lists
            
            # Create predicate for incomplete reminders
            if include_completed:
                predicate = self.event_store.predicateForRemindersInCalendars_(lists)
            else:
                predicate = self.event_store.predicateForIncompleteRemindersWithDueDateStarting_ending_calendars_(
                    None,  # No start date filter
                    None,  # No end date filter
                    lists
                )
            
            # Fetch reminders (async callback-based)
            import asyncio
            future = asyncio.get_event_loop().create_future()
            
            def completion_handler(reminders):
                future.set_result(reminders)
            
            self.event_store.fetchRemindersMatchingPredicate_completion_(
                predicate,
                completion_handler
            )
            
            reminders = await future
            
            logger.info(f"Fetched {len(reminders)} reminders from {len(lists)} lists")
            
            # Format reminders for RAG
            formatted_reminders = []
            for reminder in reminders:
                reminder_data = self._format_reminder(reminder)
                formatted_reminders.append(reminder_data)
            
            self._set_status(IntegrationStatus.CONNECTED)
            
            return {
                "reminders": formatted_reminders,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat(),
                    "list_count": len(lists),
                    "reminder_count": len(reminders),
                    "include_completed": include_completed
                }
            }
            
        except Exception as e:
            self._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Failed to fetch reminders: {e}")
    
    def _format_reminder(self, reminder) -> Dict[str, Any]:
        """Format an EventKit reminder for RAG indexing."""
        # Get reminder details
        title = reminder.title() or "Untitled Reminder"
        notes = reminder.notes() or ""
        list_name = reminder.calendar().title()
        completed = reminder.isCompleted()
        priority = reminder.priority()
        
        # Due date
        due_date = reminder.dueDateComponents()
        due_date_str = None
        if due_date:
            try:
                # Convert NSDateComponents to datetime
                year = due_date.year()
                month = due_date.month()
                day = due_date.day()
                if year and month and day:
                    due_date_obj = datetime(year, month, day)
                    due_date_str = due_date_obj.isoformat()
            except:
                pass
        
        # Priority mapping (0=none, 1-4=high, 5=medium, 6-9=low)
        priority_str = "none"
        if 1 <= priority <= 4:
            priority_str = "high"
        elif priority == 5:
            priority_str = "medium"
        elif 6 <= priority <= 9:
            priority_str = "low"
        
        # Create searchable content
        content_parts = [
            f"Task: {title}",
            f"List: {list_name}",
            f"Status: {'Completed' if completed else 'Incomplete'}",
            f"Priority: {priority_str}"
        ]
        
        if due_date_str:
            content_parts.append(f"Due: {due_date_str}")
        
        if notes:
            content_parts.append(f"Notes: {notes}")
        
        content = "\n".join(content_parts)
        
        return {
            "title": title,
            "content": content,
            "source": "macOS Reminders",
            "reminder_id": reminder.calendarItemIdentifier(),
            "list": list_name,
            "completed": completed,
            "priority": priority_str,
            "due_date": due_date_str,
            "notes": notes,
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Format reminders data for RAG indexing.
        
        Returns list of documents with title, content, and metadata.
        """
        if "reminders" not in data:
            return []
        
        documents = []
        for reminder in data["reminders"]:
            doc = {
                "title": reminder["title"],
                "content": reminder["content"],
                "source": reminder["source"],
                "metadata": {
                    "list": reminder["list"],
                    "completed": reminder["completed"],
                    "priority": reminder["priority"],
                    "due_date": reminder["due_date"]
                }
            }
            documents.append(doc)
        
        return documents
