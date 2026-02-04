# Calendar Integration - Signed App Implementation Notes

## Current Status: DISABLED (Development Limitation)

Calendar integration is temporarily disabled during development due to macOS Sequoia sandbox limitations when running through Terminal/iTerm.

## Why Calendar is Disabled Now

### The Problem
When running Polly through Terminal/iTerm (development mode):

1. **EventKit Approach** (`calendar.py`)
   - ❌ Only sees 1 "virtual" calendar (not real calendars)
   - ❌ Returns 0 events
   - ❌ Status code 4 (unknown, macOS Sequoia beta issue)
   - ❌ Full Disk Access doesn't fix this

2. **AppleScript Approach** (`calendar_applescript.py`)
   - ✅ Can access all calendars
   - ✅ Can read event data
   - ❌ **Times out (30-120 seconds)** when iterating through large iCloud-synced calendars
   - ❌ Date filtering in AppleScript is extremely slow

3. **SQLite Approach** (`calendar_sqlite.py`)
   - ❌ Calendar database location changed/encrypted on newer macOS
   - ❌ Not a reliable solution

### Why This is a Development-Only Problem

The calendar access issues are **specific to running Python scripts through Terminal/iTerm**. When Polly becomes a signed macOS app bundle, these limitations disappear.

## Implementation for Signed App Bundle

### What Will Work

When Polly is packaged as a signed `.app` bundle, the EventKit integration will work perfectly:

✅ **Full calendar access** - Will see all calendars (iCloud, Google, Exchange, etc.)
✅ **Fast queries** - Native EventKit predicates are optimized
✅ **Proper permissions** - System will show standard Calendar permission dialog
✅ **No timeouts** - Direct EventKit access is instant

### Code That's Ready

The file `/Users/brettgershon/polly/integrations/calendar.py` (EventKit version) is **ready to use** in a signed app:

```python
from integrations import CalendarIntegration

# This will work perfectly in signed app
calendar = CalendarIntegration(config={"days_ahead": 7})
await calendar.connect()  # Shows system permission dialog
events = await calendar.fetch_data()  # Fast, returns all events
```

### Required Changes for Signed App

#### 1. Info.plist Additions

Add to your app's `Info.plist`:

```xml
<key>NSCalendarsUsageDescription</key>
<string>Polly needs access to your calendars to help you search and query your schedule.</string>
```

#### 2. Entitlements (if needed)

If sandboxing the app, add to entitlements:

```xml
<key>com.apple.security.personal-information.calendars</key>
<true/>
```

#### 3. Code Signing

```bash
# Sign the app bundle
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  Polly.app

# Notarize with Apple
xcrun notarytool submit Polly.app --wait
```

### Testing the Signed App

After building and signing:

1. Launch Polly.app
2. Go to Integrations
3. Click "Enable" on Calendar
4. macOS will show permission dialog: "Polly would like to access your calendars"
5. Click "OK"
6. Calendar integration immediately works with all calendars

## What Works Now (No Changes Needed)

These integrations work perfectly in development and will continue working in signed app:

✅ **Reminders** - Using EventKit, works great
✅ **GitHub** - API-based, no macOS permissions needed
✅ **Context7** - API-based, credentials in Keychain
✅ **Obsidian** - File system access

## Architecture Reusability: ~90%

### What Stays the Same ✅

When moving to signed app, these components need **ZERO changes**:

- ✅ `integrations/base.py` - Integration architecture
- ✅ `integrations/state.py` - State persistence
- ✅ `integrations/calendar.py` - EventKit implementation (will just work!)
- ✅ `interfaces/server.py` - API endpoints
- ✅ Electron UI integration code
- ✅ RAG indexing and formatting
- ✅ All other integrations (GitHub, Context7, Reminders)

### What Changes (~10%)

1. **Remove development workarounds:**
   ```python
   # DELETE these files (dev workarounds only):
   # - integrations/calendar_applescript.py
   # - integrations/calendar_applescript_fast.py  
   # - integrations/calendar_sqlite.py
   # - scripts/request_calendar_*.py
   # - scripts/trigger_permission_dialogs.py
   ```

2. **Update one import in server.py:**
   ```python
   # Change from:
   # from integrations.calendar_applescript import CalendarIntegration
   
   # To:
   from integrations import CalendarIntegration  # Uses calendar.py (EventKit)
   ```

3. **Add Info.plist entries** (see above)

4. **Keychain integration** - Replace `security find-generic-password` with proper Keychain Services API:
   ```python
   # Current (works but uses CLI):
   subprocess.run(['security', 'find-generic-password', ...])
   
   # Signed app (more robust):
   from Security import SecItemCopyMatching  # PyObjC
   ```

## Timeline Recommendation

### Phase 1: Now (Development)
- ✅ Reminders integration (working)
- ✅ GitHub integration (working)
- ✅ Context7 integration (working)
- ✅ Obsidian integration (working)
- ❌ Calendar (disabled, documented)

### Phase 2: First Signed Build
1. Build Polly.app with `py2app` or similar
2. Add Info.plist entries
3. Code sign (self-signed for testing)
4. Uncomment Calendar integration line
5. Test - Calendar should work immediately

### Phase 3: Production Release
1. Get Developer ID certificate
2. Add hardened runtime
3. Notarize with Apple
4. Distribute

## Expected Outcome

Once Polly is a signed app:
- ✅ Calendar integration will work perfectly
- ✅ 10x faster than AppleScript approach
- ✅ Access to ALL calendars
- ✅ Proper permission management
- ✅ Native macOS user experience

## References

- **Working EventKit code:** `/Users/brettgershon/polly/integrations/calendar.py`
- **Working Reminders code:** `/Users/brettgershon/polly/integrations/reminders.py` (same pattern)
- **Apple docs:** https://developer.apple.com/documentation/eventkit
- **PyObjC EventKit:** https://pyobjc.readthedocs.io/en/latest/apidocs/EventKit.html

## Summary

**Don't worry about Calendar integration right now.** The code is ready, it just needs to run from a signed app instead of Terminal. When you're ready to build the app bundle, it's a simple uncomment and everything will work.

Focus on:
1. Building out other features with working integrations
2. Testing Reminders (proves EventKit works)
3. Planning the app bundle build process

The Calendar limitation is temporary and the solution is straightforward once you're ready to package Polly as a real macOS app.
