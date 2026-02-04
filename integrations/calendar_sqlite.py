"""
Calendar integration using direct Calendar.app database access.
Works around AppleScript timeout issues by reading the Calendar SQLite database.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class CalendarIntegration(Integration):
    """Fetch calendar events by reading Calendar's SQLite database."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize calendar integration.
        
        Args:
            config: Optional configuration dict with 'days_ahead' key
        """
        super().__init__("calendar", config)
        self.days_ahead = config.get("days_ahead", 7) if config else 7
        self.db_path = Path.home() / "Library" / "Calendars" / "Calendar.sqlitedb"
    
    async def connect(self, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to Calendar database.
        No credentials needed - direct database access.
        """
        try:
            # Check if database exists and is readable
            if not self.db_path.exists():
                raise IntegrationError(f"Calendar database not found at {self.db_path}")
            
            # Try to open and query the database
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ZCALENDARITEM")
            count = cursor.fetchone()[0]
            conn.close()
            
            logger.info(f"Calendar database access successful ({count} items)")
            self._set_status(IntegrationStatus.CONNECTED)
            return True
                
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                raise IntegrationError("Calendar database is locked - Calendar.app may be running")
            raise IntegrationError(f"Cannot access Calendar database: {e}")
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
            if not self.db_path.exists():
                return False
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            conn.close()
            return True
        except Exception:
            return False
    
    async def fetch_data(self, days_ahead: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch calendar events by reading the SQLite database.
        
        Args:
            days_ahead: Override default days_ahead value
            
        Returns:
            Dict with events and metadata
        """
        days = days_ahead if days_ahead is not None else self.days_ahead
        
        # Calculate date range (Calendar uses Core Data timestamps: seconds since 2001-01-01)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Convert to Core Data reference date (2001-01-01 00:00:00 UTC)
        ref_date = datetime(2001, 1, 1)
        start_timestamp = (start_date - ref_date).total_seconds()
        end_timestamp = (end_date - ref_date).total_seconds()
        
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query events in date range
            # ZCALENDARITEM contains events, Z_PK is primary key
            # ZSTARTDATE and ZENDDATE are in Core Data format
            query = """
            SELECT 
                item.ZSUMMARY as title,
                item.ZSTARTDATE as start,
                item.ZENDDATE as end,
                item.ZLOCATION as location,
                item.ZNOTES as notes,
                cal.ZTITLE as calendar_name
            FROM ZCALENDARITEM item
            LEFT JOIN ZCALENDAR cal ON item.ZCALENDAR = cal.Z_PK
            WHERE item.ZSTARTDATE >= ? AND item.ZSTARTDATE <= ?
            AND item.ZSTARTDATE IS NOT NULL
            ORDER BY item.ZSTARTDATE
            """
            
            cursor.execute(query, (start_timestamp, end_timestamp))
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                # Convert Core Data timestamps back to datetime
                start_dt = ref_date + timedelta(seconds=row['start']) if row['start'] else start_date
                end_dt = ref_date + timedelta(seconds=row['end']) if row['end'] else start_dt
                
                events.append({
                    'calendar': row['calendar_name'] or 'Unknown',
                    'title': row['title'] or 'Untitled Event',
                    'start': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': end_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': row['location'] or '',
                    'description': row['notes'] or '',
                    'source': 'calendar'
                })
            
            conn.close()
            
            logger.info(f"Fetched {len(events)} events from Calendar database")
            
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
                    "method": "sqlite"
                }
            }
            
        except sqlite3.Error as e:
            raise IntegrationError(f"Failed to query Calendar database: {str(e)}")
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
