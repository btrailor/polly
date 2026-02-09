# Missing Notes API Endpoints Fix

**Date**: 2026-02-09  
**Issue**: HTTP 404 errors when clicking on notes in the browser due to missing backend API endpoints.

## Problem

When selecting notes in the frontend notes browser, the app was making API calls to three endpoints that didn't exist in the backend:

### Errors in Console:
```
POST /polly/notes/sync/start - 404 Not Found
GET /polly/notes/{note_name}/backlinks - 404 Not Found  
PUT /polly/notes/update - 404 Not Found
```

### Impact:
- File watcher wouldn't start automatically when opening notes
- Backlinks panel would remain empty (0 backlinks shown)
- Notes couldn't be saved, showing "Failed to save: Not Found" errors
- User experience was degraded despite notes loading successfully

## Root Cause

The frontend (`notes-manager.js`) was refactored to use these endpoints, but the backend (`interfaces/server.py`) never had them implemented. The disconnection between frontend expectations and backend implementation caused the 404 errors.

## Solution

Added three missing API endpoints to `interfaces/server.py`:

### 1. POST /polly/notes/sync/start (lines 2603-2649)

**Purpose**: Start the notes file watcher for automatic synchronization

**Request**: None required

**Response**:
```json
{
  "success": true,
  "message": "File watcher started",
  "is_running": true
}
```

**Behavior**:
- Checks if Polly is initialized
- Returns success if file watcher is already running
- Starts the file watcher if not running
- Returns error if file watcher failed to initialize

### 2. PUT /polly/notes/update (lines 3149-3211)

**Purpose**: Save/update note content to disk

**Request**:
```json
{
  "path": "/full/path/to/note.md",
  "content": "Updated markdown content..."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Note saved successfully"
}
```

**Behavior**:
- Validates path and content are provided
- Checks note exists (404 if not found)
- Writes content to file
- Re-indexes the note in the notes index
- Gracefully continues even if re-indexing fails
- Logs save operation for debugging

### 3. GET /polly/notes/{note_name}/backlinks (lines 3213-3287)

**Purpose**: Get all notes that link to the specified note

**Request**: None (note name in URL path)

**Response**:
```json
{
  "backlinks": [
    {
      "name": "linking-note",
      "title": "Linking Note Title",
      "path": "/path/to/linking-note.md",
      "domain": "02-Signals"
    }
  ],
  "count": 1
}
```

**Behavior**:
- Finds the target note by name
- Searches all notes in the index
- Checks each note's `links` array for references to target note
- Returns empty array if target note not found (graceful)
- Returns empty array on error (graceful degradation)
- Skips the target note itself in results

## Implementation Details

### File Modified
- `interfaces/server.py`

### Lines Changed
- Added sync/start endpoint: lines 2603-2649 (47 lines)
- Added update endpoint: lines 3149-3211 (63 lines)  
- Added backlinks endpoint: lines 3213-3287 (75 lines)
- **Total**: 185 new lines

### Dependencies
All endpoints use existing modules:
- `core.notes_index.get_notes_index()` - Notes index lookup
- `core.notes_source_manager.NotesSourceManager()` - Notes path configuration
- `pathlib.Path` - File system operations
- Standard FastAPI/HTTPException error handling

### Error Handling
All three endpoints include:
- Input validation with 400 Bad Request responses
- Existence checks with 404 Not Found responses
- Try/catch blocks with 500 Internal Server Error responses
- Graceful degradation (backlinks returns empty on error)
- Detailed logging for debugging

## Testing

### Before Fix
```
[Notes] Opening note: 2025-12-22
POST /polly/notes/sync/start 404 (Not Found)
GET /polly/notes/2025-12-22/backlinks 404 (Not Found)
PUT /polly/notes/update 404 (Not Found)
[Notes] Failed to save note: Error: Not Found
[Notes] Failed to save: Not Found
[Notes] Loaded 0 backlinks for 2025-12-22
```

### After Fix (Expected)
```
[Notes] Opening note: 2025-12-22
POST /polly/notes/sync/start 200 OK - File watcher started
GET /polly/notes/2025-12-22/backlinks 200 OK - 3 backlinks found
PUT /polly/notes/update 200 OK - Note saved successfully
[Notes] Note saved successfully
[Notes] Loaded 3 backlinks for 2025-12-22
```

## How to Apply

### 1. Restart the Python Backend
The backend server must be restarted to load the new endpoints:

```bash
# In the Electron app, the backend should restart automatically when you quit and relaunch
# Alternatively, if running manually:
cd /Users/brettgershon/polly
source venv/bin/activate
# Kill existing server process
pkill -f "uvicorn interfaces.server"
# Start fresh
python -m uvicorn interfaces.server:create_app --host 127.0.0.1 --port 11436 --factory
```

### 2. Reload the Frontend
If the Electron app is running, quit and restart it:
```bash
cd /Users/brettgershon/polly/electron-app
npm start
```

### 3. Verify the Fix
1. Open the Notes view
2. Click on any note in the file browser
3. Check browser console - should see:
   - `POST /polly/notes/sync/start 200 OK` (or "already running")
   - `GET /polly/notes/{name}/backlinks 200 OK`
   - No more 404 errors
4. Edit the note and wait 2 seconds
5. Should see `PUT /polly/notes/update 200 OK`
6. No "Failed to save" errors

## Benefits

1. **File Watcher Auto-Start**: Notes sync now starts automatically when opening notes
2. **Backlinks Work**: Notes properly show which other notes link to them
3. **Auto-Save Works**: Notes are automatically saved after editing without errors
4. **Better UX**: No more error messages when using notes features
5. **Graceful Degradation**: Backlinks endpoint returns empty array on errors instead of failing
6. **Proper Logging**: All operations are logged for debugging

## Related Files

- `interfaces/server.py` - Backend API server (MODIFIED)
- `electron-app/src/renderer/notes-manager.js` - Frontend notes manager (calls these endpoints)
- `core/notes_index.py` - Notes indexing system (used by backlinks)
- `core/notes_source_manager.py` - Notes path configuration (used by update)

## Future Improvements

1. **Batch Backlinks**: Endpoint to get backlinks for multiple notes at once
2. **Backlink Context**: Include surrounding text where the link appears
3. **Bidirectional Links**: Also return notes linked FROM the target note
4. **Link Type**: Distinguish between wiki-style [[links]] and markdown [links]()
5. **Caching**: Cache backlinks to avoid re-scanning all notes on every request
6. **Real-time Updates**: WebSocket push notifications when backlinks change

## Notes

- All endpoints follow FastAPI conventions and error handling patterns
- Endpoints are consistent with existing notes API design
- No breaking changes to existing endpoints
- Backward compatible - old clients will just get 404s as before
- No database migrations required
- No configuration changes required
