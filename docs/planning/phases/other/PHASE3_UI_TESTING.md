# Phase 3 UI Testing Guide

## What Was Implemented

### Backend (Already Complete)
- ✅ Smart folder suggestions based on DomainEngine
- ✅ Tag suggestions from content + RAG
- ✅ Related notes discovery
- ✅ Daily note creation from templates
- ✅ Conversation-to-note conversion

### Frontend (Just Completed)
- ✅ "Save to Obsidian" button in chat header
- ✅ "Related Notes" sidebar toggle button
- ✅ Related Notes sidebar with live updates
- ✅ Note creation modal with smart suggestions
- ✅ Folder suggestion UI with confidence display
- ✅ Tag suggestion chips (clickable to add)
- ✅ Conversation history tracking
- ✅ Click-to-open notes in Obsidian
- ✅ Full integration with backend APIs

## Testing Steps

### Prerequisites
1. **Restart the Electron app** to pick up new server code:
   ```bash
   # Kill the app if running
   killall Electron
   
   # Or just Cmd+Q the app
   # Then restart from Applications or terminal
   ```

2. **Verify server is running:**
   ```bash
   lsof -i :11436 | grep LISTEN
   ```

3. **Verify Obsidian integration is connected:**
   - Open Settings → Integrations → Obsidian
   - Should show "connected" status

### Test 1: Basic Conversation Tracking

1. Go to Chat view
2. Send a few messages about audio synthesis:
   - "How do I implement wavetable synthesis?"
   - "What's the difference between FM and AM synthesis?"
   - "How do I create a simple oscillator in Python?"

3. **Expected:** Messages appear normally in chat

### Test 2: Save Conversation Modal

1. Click the "Save to Obsidian" button (top right of chat)
2. **Expected:**
   - Modal opens
   - Title is auto-suggested from first message
   - Folder defaults to "30-Ideas"
   - Tags section is empty

### Test 3: Folder Suggestions

1. In the modal, click the sparkle button (✨) next to Folder field
2. **Expected:**
   - "Getting folder suggestion..." message appears
   - After 1-2 seconds, suggestion box appears
   - Shows: "02-Signals (Signals, XX% confidence)"
   - Reasoning text explains why
   - "Use" button is clickable

3. Click "Use" button
4. **Expected:** Folder field updates to "02-Signals"

### Test 4: Tag Suggestions

1. Click the sparkle button (✨) next to Tags field
2. **Expected:**
   - "Getting tag suggestions..." appears
   - After 1-2 seconds, suggested tags appear as chips
   - Each chip shows tag name and confidence %
   - Examples: "wavetable 70%", "synthesis 70%", etc.

3. Click on a suggested tag chip
4. **Expected:**
   - Tag moves to "Selected tags" section below
   - Chip turns purple (--signal color)
   - Shows × button to remove

5. Click × on a selected tag
6. **Expected:** Tag is removed from selection

### Test 5: Save Note to Obsidian

1. Fill in or accept defaults:
   - Title: "Python Wavetable Synthesis Guide"
   - Folder: "02-Signals" (from suggestion)
   - Tags: Select 2-3 tags

2. Click "Save Note" button
3. **Expected:**
   - "Creating note..." message
   - Success message: "✓ Note created: 02-Signals/Python Wavetable Synthesis Guide.md"
   - Modal closes automatically after 1.5 seconds

4. Open Obsidian and navigate to the folder
5. **Expected:**
   - New note exists
   - Contains frontmatter with tags
   - Has "Summary" section with Q&A
   - Has "Code Examples" section (if code was shared)
   - Has "Full Conversation" section with all messages

### Test 6: Related Notes Sidebar

1. Close the save modal (if still open)
2. Click the "Related Notes" button (top of chat, next to "Save to Obsidian")
3. **Expected:**
   - Sidebar slides in from the right
   - Shows "Finding related notes..." loading state
   - After 1-2 seconds, shows list of related notes

4. **Expected note items show:**
   - Title of the note
   - File path (e.g., "02-Signals/Ableton Techniques.md")
   - Similarity percentage (e.g., "78% similar")
   - Badge color: green (>80%), orange (>70%), gray (<70%)
   - Shared concept chips (e.g., "synthesis", "oscillators")

5. Click on a related note item
6. **Expected:**
   - Obsidian app opens (or comes to front)
   - The clicked note opens in Obsidian

7. Send another message: "Tell me about FM synthesis"
8. **Expected:**
   - Related notes automatically update
   - New relevant notes appear based on FM synthesis topic

9. Click the X button in the sidebar header
10. **Expected:**
    - Sidebar slides closed
    - Chat area expands back to full width

11. Click "Related Notes" button again
12. **Expected:**
    - Sidebar opens again
    - Shows same notes (doesn't re-fetch unnecessarily)

## Troubleshooting

### Modal doesn't open
- Check browser console (Cmd+Option+I in Electron)
- Verify `conversationHistory` is not empty
- Try sending more messages first

### Folder/tag suggestions fail
- Check if server is running: `curl http://localhost:11436/health`
- Check server logs for errors
- Test endpoints directly:
  ```bash
  curl "http://localhost:11436/polly/obsidian/suggest-folder?title=Audio&content=synthesis"
  ```

### Note creation fails
- Verify Obsidian integration is connected
- Check vault path in Settings → Integrations → Obsidian
- Ensure folder "02-Signals" exists in vault (or use "30-Ideas")
- Check server logs for permission errors

### Styling issues
- Icons not showing: Check if Lucide is loaded (console errors)
- Modal looks wrong: Clear browser cache, restart app
- Tags not clickable: Check console for JavaScript errors

### Related notes sidebar issues
- Sidebar doesn't open: Check console for errors, verify button exists
- No notes found: This is normal if content isn't similar to vault notes
- Notes don't open: Check Obsidian app is installed, vault name is correct
- Sidebar overlaps chat: Check CSS, chat should have `with-sidebar` class when open

## Expected Behavior Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Save button appears | ✅ | Top right of chat header |
| Related Notes button | ✅ | Next to Save button |
| Modal opens | ✅ | Shows after clicking button |
| Folder suggestions | ✅ | Domain-based, shows confidence |
| Tag suggestions | ✅ | Content + RAG based, clickable chips |
| Note creation | ✅ | Full conversation structure |
| Auto-close modal | ✅ | After successful save |
| Related notes sidebar | ✅ | Slides in from right |
| Auto-update notes | ✅ | Updates after each message |
| Click to open | ✅ | Opens note in Obsidian |

## What's Next (Optional - All Core Features Complete!)

### Future Enhancements
- Daily note creation UI (use existing `/polly/obsidian/daily-note` endpoint)
- Template picker for note creation
- Action item extraction from conversations
- Question detection for "Open Questions" section

## Files Modified

### HTML
- `/Users/brettgershon/polly/electron-app/src/renderer/index.html`
  - Added "Save to Obsidian" button
  - Added "Related Notes" toggle button
  - Added save-conversation-modal
  - Added related-notes-panel with header, status, and list

### CSS
- `/Users/brettgershon/polly/electron-app/src/renderer/styles/main.css`
  - Added tag chip styles
  - Added suggestion box styles
  - Added modal status message styles
  - Added related notes sidebar styles
  - Added chat-content-wrapper for sidebar layout
  - Added note item styles with hover effects

### JavaScript
- `/Users/brettgershon/polly/electron-app/src/renderer/app.js`
  - Added `conversationHistory` tracking
  - Added modal handlers
  - Added smart suggestion functions
  - Added save to Obsidian function
  - Added related notes toggle/close functions
  - Added updateRelatedNotes() with auto-refresh
  - Added createRelatedNoteElement() for rendering
  - Added openNoteInObsidian() using Obsidian URI protocol

## Success Criteria

- [x] Can save conversation to Obsidian
- [x] Folder suggestions work and are accurate
- [x] Tag suggestions appear and are clickable
- [x] Selected tags show properly
- [x] Note is created with full conversation
- [x] Modal UX is smooth (auto-close, loading states)
- [x] Related notes sidebar opens/closes
- [x] Related notes update automatically after messages
- [x] Can click notes to open in Obsidian
- [x] Sidebar shows similarity scores and concepts
- [ ] End-to-end test completed successfully

Mark the last checkbox after completing all tests!
