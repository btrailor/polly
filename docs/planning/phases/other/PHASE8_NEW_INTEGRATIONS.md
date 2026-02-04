# Phase 8: New Integrations

**Status:** Future Planning  
**Priority:** Low (Future Enhancements)  
**Estimated Effort:** Varies by integration (1-2 weeks each)  
**Dependencies:** Phase 5 (Backend Integration Framework) - Complete ✅

---

## Overview

Expand Polly's knowledge sources by adding new integrations beyond Obsidian, GitHub, Context7, Calendar, Reminders, and FileSystem.

### Integration Candidates

Based on the Master Roadmap "Future Enhancements" section:

1. **Email** (IMAP/Gmail API)
2. **Slack** (API)
3. **Browser History** (SQLite)
4. **Apple Notes** (AppleScript/EventKit)
5. **Photos** (Photos.framework)
6. **Music** (Music.app)

---

## Phase 8.1: Email Integration

**Priority:** Medium  
**Estimated Effort:** 1-2 weeks

### Goals
- Index email messages (subject, body, sender, date)
- Search email content via RAG
- Extract knowledge from email threads
- Support IMAP and Gmail API

### Implementation

**Providers:**
- IMAP (generic: Gmail, Outlook, iCloud Mail)
- Gmail API (richer metadata, labels, threads)

**Features:**
- Fetch recent emails (last 30 days or 1000 messages)
- Filter by folder/label
- Exclude spam, trash
- Privacy controls (which folders to index)

**RAG Document Format:**
```python
{
    "content": "Subject: Meeting Notes\n\nBody content...",
    "metadata": {
        "source": "email",
        "type": "message",
        "subject": "Meeting Notes",
        "from": "john@example.com",
        "to": ["brett@example.com"],
        "date": "2026-01-20T10:00:00",
        "folder": "Inbox",
        "message_id": "abc123",
        "has_attachments": false
    }
}
```

**Privacy Considerations:**
- User controls which folders to index
- Option to exclude sender addresses
- Option to exclude subject patterns
- Credentials stored in Keychain

**Estimated Effort:** 7-10 days

---

## Phase 8.2: Slack Integration

**Priority:** Medium  
**Estimated Effort:** 1 week

### Goals
- Index Slack channels and DMs
- Search message history
- Extract team knowledge
- Support workspace switching

### Implementation

**Slack API:**
- OAuth authentication
- Channels list + history
- DMs list + history
- File attachments (links only)

**Features:**
- Select channels to index (not all)
- Index last 90 days of messages
- Exclude bot messages (optional)
- Thread context preservation

**RAG Document Format:**
```python
{
    "content": "Message content with @mentions and #channels",
    "metadata": {
        "source": "slack",
        "type": "message",
        "channel": "general",
        "user": "Brett Gershon",
        "timestamp": "2026-01-20T10:00:00",
        "thread_ts": "1234567890",
        "reactions": ["👍", "🔥"],
        "permalink": "https://workspace.slack.com/archives/..."
    }
}
```

**Privacy Considerations:**
- User selects which channels to index
- Exclude private channels by default
- Option to exclude DMs
- Workspace-level enable/disable

**Estimated Effort:** 5-7 days

---

## Phase 8.3: Browser History Integration

**Priority:** Low  
**Estimated Effort:** 3-5 days

### Goals
- Index browser history (visited URLs, page titles)
- Search browsing patterns
- Extract research topics
- Support Safari, Chrome, Firefox

### Implementation

**Data Sources:**
- Safari: `~/Library/Safari/History.db` (SQLite)
- Chrome: `~/Library/Application Support/Google/Chrome/.../History` (SQLite)
- Firefox: `~/Library/Application Support/Firefox/Profiles/.../places.sqlite`

**Features:**
- Index last 30 days of history
- Exclude sensitive URLs (banking, private sites)
- Extract page titles and visit frequency
- Detect research patterns (multiple visits to related pages)

**RAG Document Format:**
```python
{
    "content": "Page title and URL",
    "metadata": {
        "source": "browser_history",
        "type": "visit",
        "url": "https://example.com/article",
        "title": "How to Build AI Systems",
        "visit_count": 5,
        "last_visit": "2026-01-20T10:00:00",
        "browser": "Safari"
    }
}
```

**Privacy Considerations:**
- User controls date range
- URL pattern exclusions (e.g., `*bank.com/*`)
- Option to disable entirely
- Clear history option

**Permission Required:**
- Full Disk Access (same as FileSystem integration)

**Estimated Effort:** 3-5 days

---

## Phase 8.4: Apple Notes Integration

**Priority:** Low  
**Estimated Effort:** 5-7 days

### Goals
- Index Apple Notes
- Search note content
- Sync with Obsidian (optional)
- Support folders and tags

### Implementation

**Access Methods:**
- **Option A:** AppleScript (slower but reliable)
- **Option B:** Direct SQLite access (faster but fragile)
- **Recommended:** AppleScript for safety

**Features:**
- Fetch all notes (or last 6 months)
- Extract note title, body, folder, creation date
- Handle rich text (strip formatting for RAG)
- Detect note attachments (images, PDFs)

**RAG Document Format:**
```python
{
    "content": "Note title\n\nNote body content...",
    "metadata": {
        "source": "apple_notes",
        "type": "note",
        "title": "Project Ideas",
        "folder": "Work",
        "created": "2026-01-15T10:00:00",
        "modified": "2026-01-20T15:00:00",
        "has_attachments": true
    }
}
```

**Privacy Considerations:**
- User controls which folders to index
- Option to exclude specific notes
- No attachment content (just note text)

**Permission Required:**
- None (AppleScript has user consent dialog)

**Estimated Effort:** 5-7 days

---

## Phase 8.5: Photos Integration

**Priority:** Low  
**Estimated Effort:** 1-2 weeks

### Goals
- Index photo metadata (EXIF, dates, locations)
- Search photos by content (using ML)
- Extract photo concepts
- Support albums and smart albums

### Implementation

**Photos.framework:**
- PHAsset queries (all photos)
- EXIF metadata extraction
- Location data (if available)
- ML-based content classification (built-in iOS/macOS)

**Features:**
- Index photo metadata only (not image files)
- Extract dates, locations, camera info
- Use Photos' built-in ML labels ("dog", "sunset", etc.)
- Search photos by: date, location, content, album

**RAG Document Format:**
```python
{
    "content": "Photo taken at Golden Gate Park, sunset, landscape",
    "metadata": {
        "source": "photos",
        "type": "photo",
        "date": "2025-12-15T18:30:00",
        "location": "Golden Gate Park, SF",
        "camera": "iPhone 15 Pro",
        "labels": ["sunset", "landscape", "park"],
        "album": "Favorites",
        "asset_id": "abc123"
    }
}
```

**Privacy Considerations:**
- User controls which albums to index
- Location data optional
- No image content stored (just metadata)
- Photos stay in Photos app (links only)

**Permission Required:**
- Photos Library Access (system permission dialog)

**Estimated Effort:** 7-10 days

---

## Phase 8.6: Music Integration

**Priority:** Very Low  
**Estimated Effort:** 3-5 days

### Goals
- Index music library metadata
- Analyze listening patterns
- Extract playlist themes
- Support Apple Music and local files

### Implementation

**Music.app/iTunes Library:**
- SQLite database or AppleScript
- Track metadata: title, artist, album, genre, play count
- Playlist information
- Recently played tracks

**Features:**
- Index music library metadata
- Track listening patterns (most played, recent)
- Analyze playlist composition
- Suggest music based on context

**RAG Document Format:**
```python
{
    "content": "Song: Stella by Jai Paul, Genre: Electronic, Album: Leak 04-13",
    "metadata": {
        "source": "music",
        "type": "track",
        "title": "Stella",
        "artist": "Jai Paul",
        "album": "Leak 04-13",
        "genre": "Electronic",
        "play_count": 47,
        "last_played": "2026-01-20T19:00:00"
    }
}
```

**Privacy Considerations:**
- No streaming service credentials needed
- Local library only
- Playlist privacy (don't share)

**Estimated Effort:** 3-5 days

---

## Implementation Priority

**If implementing Phase 8, do in this order:**

1. **Email** (highest value, broadly useful)
2. **Slack** (high value for teams)
3. **Apple Notes** (complements Obsidian)
4. **Browser History** (research context)
5. **Photos** (niche but interesting)
6. **Music** (low priority, niche use case)

---

## General Integration Pattern

**All Phase 8 integrations follow the same pattern:**

1. **Create integration class** (inherits from `Integration`)
2. **Implement authentication** (OAuth, API key, or permission)
3. **Implement data fetching** (`fetch_data()` method)
4. **Transform for RAG** (`format_for_rag()` method)
5. **Create API endpoints** (list, sync, configure)
6. **Build UI** (settings card, enable/disable)
7. **Test with real data**

**Estimated time per integration:** 5-10 days

---

## Success Criteria

For each integration:
- ✅ Authentication works smoothly
- ✅ Data fetching is reliable
- ✅ RAG indexing provides useful results
- ✅ Privacy controls are clear
- ✅ Performance is acceptable (<30s sync)

---

## Why These Are Low Priority

**Current integrations already provide:**
- Knowledge (Obsidian, Context7)
- Code (GitHub, local codebase)
- Time management (Calendar, Reminders)
- File management (FileSystem)

**Phase 8 integrations add:**
- Communication context (Email, Slack)
- Research context (Browser History)
- Personal content (Notes, Photos, Music)

**Useful, but not essential for core Polly functionality.**

---

## Future: Plugin System

**Instead of building all these integrations into Polly, consider:**

**Phase 15: Plugin/Extension System**
- Third-party integration support
- Community-built integrations
- Plugin marketplace
- Standardized integration API

**This would allow:**
- Users to build custom integrations
- Community to contribute integrations
- Faster integration development
- Better maintenance (community-driven)

---

**Last Updated:** January 21, 2026  
**Status:** Future Planning  
**Priority:** Low (Each integration is optional)
