# Phase 7: Advanced Calendar Features

**Status:** Not Started  
**Priority:** Low (Optional Enhancement)  
**Estimated Effort:** 5-7 days  
**Dependencies:** 
- Phase 9 (macOS Permission Handling) - **REQUIRED** ⚠️
- Basic Calendar Integration (already built but disabled)

---

## Overview

The Calendar integration is already built and working, but disabled until Phase 9 adds proper permission handling. Phase 7 would add advanced features beyond basic event access.

### Current State

**Built But Disabled:**
- ✅ EventKit integration (`/integrations/calendar.py`)
- ✅ iCloud, Google Calendar, Exchange support
- ✅ Event fetching with date ranges
- ✅ RAG formatting for events
- ✅ API endpoints ready

**Why Disabled:**
- Requires macOS Calendar permission (EventKit)
- Phase 9 needed for permission UI
- Works when run from signed app bundle

**Location:** `/integrations/calendar.py`  
**Documentation:** `/docs/calendar_signed_app_notes.md`

---

## Goals

### What Phase 9 Will Enable (Basic Calendar)

- View calendar events in Polly
- Search events by date/keyword
- RAG-powered event queries
- Calendar context in conversations

### What Phase 7 Adds (Advanced Features)

1. **Multi-Account Support**
   - Simultaneously use iCloud + Google Calendar + Exchange
   - Per-account filtering
   - Unified event view across accounts

2. **Natural Language Queries**
   - "What meetings do I have tomorrow?"
   - "When is my next 1:1 with Sarah?"
   - "Show me all events about the Polly project"

3. **Event Creation from Chat**
   - "Schedule a meeting with John next Tuesday at 2pm"
   - Creates event directly from conversation
   - Suggests attendees based on context

4. **Meeting Notes Integration**
   - Link Obsidian notes to calendar events
   - Auto-create meeting notes
   - Pre-fill notes with event details (attendees, time, agenda)

5. **Smart Scheduling**
   - Find available time slots
   - Suggest meeting times based on patterns
   - Avoid conflicts automatically

---

## Implementation Plan

### Day 1-2: Multi-Account Support

**Tasks:**
1. Update `CalendarIntegration` to support multiple accounts
2. Add account discovery (enumerate all calendar sources)
3. Add per-account enable/disable toggles
4. Add account filtering in queries
5. Test with iCloud + Google Calendar simultaneously

**Deliverables:**
- Multi-account support in `/integrations/calendar.py` (+100 lines)
- Settings UI for account management

**Code Structure:**
```python
class CalendarIntegration:
    def __init__(self):
        self.accounts = {}  # account_id -> account_info
        self._discover_accounts()
    
    def _discover_accounts(self):
        """Enumerate all calendar accounts."""
        # EventKit: get all EKEventStore sources
        pass
    
    async def fetch_events(
        self,
        account_ids: Optional[List[str]] = None,
        start_date: datetime = None,
        end_date: datetime = None
    ):
        """Fetch events from specific accounts or all."""
        pass
```

### Day 3: Natural Language Queries

**Tasks:**
1. Create `/integrations/calendar_nlp.py` for NL parsing
2. Use LLM to parse date/time references
3. Extract query intent (next meeting, all meetings, specific person)
4. Convert NL to structured queries
5. Test with 20+ example queries

**Deliverables:**
- NL query parser (+200 lines)
- Query intent classification

**Example Parsing:**
```
Input: "What meetings do I have tomorrow?"
Output: {
    "intent": "list_events",
    "start_date": "2026-01-22T00:00:00",
    "end_date": "2026-01-22T23:59:59",
    "filters": {}
}

Input: "When is my next 1:1 with Sarah?"
Output: {
    "intent": "find_next_event",
    "query": "1:1",
    "attendee": "Sarah",
    "start_date": "now"
}
```

### Day 4: Event Creation from Chat

**Tasks:**
1. Add event creation method to `CalendarIntegration`
2. Parse "schedule" commands from chat
3. Extract: title, date/time, duration, attendees
4. Create EventKit event
5. Confirm creation to user

**Deliverables:**
- Event creation (+150 lines)
- Chat command parsing

**Command Examples:**
```
"Schedule a meeting with John next Tuesday at 2pm"
→ Creates: "Meeting with John", Jan 23 2026, 2:00 PM, 1hr

"Add a reminder: Call Mom on Friday"
→ Creates: "Call Mom", Jan 26 2026, all-day event

"Block 2 hours tomorrow morning for deep work"
→ Creates: "Deep Work", Jan 22 2026, 9:00 AM, 2hr
```

### Day 5: Meeting Notes Integration

**Tasks:**
1. Add Obsidian note creation linked to events
2. Template for meeting notes (attendees, agenda, date)
3. Auto-suggest note creation before meetings
4. Link events to existing notes (by title matching)
5. Test note creation flow

**Deliverables:**
- Meeting notes feature (+120 lines)
- Obsidian template

**Meeting Note Template:**
```markdown
---
type: meeting
event_id: abc123
date: 2026-01-22
attendees: [John, Sarah]
calendar: Work Calendar
---

# Meeting: Project Sync

**Date:** January 22, 2026 at 2:00 PM  
**Attendees:** John, Sarah  
**Duration:** 1 hour

## Agenda
- 

## Notes
- 

## Action Items
- [ ] 

## Next Steps
- 
```

### Day 6-7: Smart Scheduling & Polish

**Tasks:**
1. Find available time slots
2. Suggest meeting times based on patterns
3. Detect scheduling conflicts
4. Add "Find time" command
5. UI polish and testing
6. Documentation

**Deliverables:**
- Smart scheduling (+100 lines)
- Complete testing
- User documentation

---

## Technical Design

### API Endpoints

**New Endpoints:**
- `POST /polly/calendar/query-nl` - Natural language query
- `POST /polly/calendar/create-event` - Create event from structured data
- `POST /polly/calendar/create-note` - Create meeting note
- `GET /polly/calendar/find-time` - Find available slots
- `GET /polly/calendar/accounts` - List calendar accounts

### Event Creation Schema

```json
{
  "title": "Meeting with John",
  "start_date": "2026-01-23T14:00:00",
  "end_date": "2026-01-23T15:00:00",
  "location": "Office",
  "attendees": ["john@example.com"],
  "notes": "Discuss Q1 roadmap",
  "calendar": "Work Calendar",
  "reminders": [15]  // 15 minutes before
}
```

### Meeting Note Link Schema

```json
{
  "event_id": "abc123",
  "note_path": "~/vault/meetings/2026-01-22-project-sync.md",
  "created_at": "2026-01-21T10:00:00",
  "auto_generated": true
}
```

---

## Success Criteria

- ✅ Multiple calendar accounts work simultaneously
- ✅ NL queries return correct events 90%+ of the time
- ✅ Event creation from chat works smoothly
- ✅ Meeting notes auto-create before meetings
- ✅ Find available time slots in <2 seconds

---

## Why This Requires Phase 9 First

**Phase 9 provides:**
- ✅ Permission request UI
- ✅ Permission status checking
- ✅ Graceful permission denial handling
- ✅ EventKit authorization flow

**Without Phase 9:**
- ❌ Can't request Calendar permission
- ❌ Can't enable Calendar integration
- ❌ Can't test any calendar features

**Phase 7 must wait until Phase 9 is complete.**

---

## Future Enhancements

### Phase 7.5: Calendar Intelligence
- Learn scheduling preferences
- Auto-decline conflicting meetings
- Travel time calculations
- Meeting priority scoring

### Phase 7.6: Team Features
- Shared calendar views
- Team availability
- Room/resource booking
- Recurring meeting management

---

## Why This Is Optional

**Basic calendar integration (Phase 9) provides:**
- Event viewing and search
- Calendar context in conversations
- RAG-powered event queries

**Phase 7 adds convenience features:**
- Faster event creation
- Better multi-account support
- NL queries

**But the core functionality works without Phase 7.**

---

**Last Updated:** January 21, 2026  
**Status:** Not Started - Requires Phase 9 First  
**Priority:** Low (Optional Enhancement)
