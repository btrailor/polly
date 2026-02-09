# Startup Race Condition Fix

**Date**: 2026-02-09  
**Issue**: Console errors (`ERR_CONNECTION_REFUSED`, HTTP 500) during app startup due to frontend trying to connect before backend server is ready.

## Root Cause

The Electron frontend initializes immediately on `DOMContentLoaded` and makes API calls to the Python backend at `http://127.0.0.1:11436`. However, the backend server takes a few seconds to start up, causing connection failures during the initial page load.

## Solution

Implemented comprehensive retry logic and server readiness checking across the frontend.

### Changes Made

#### 1. Created Reusable API Client Utility
**File**: `electron-app/src/renderer/utils/api-client.js`

New centralized utility for all API calls with built-in retry logic:
- `fetchWithRetry(endpoint, options, retries, delay)` - Fetch with automatic retry on network errors
- `fetchJSON(endpoint, options, retries, delay)` - Fetch and parse JSON with retry
- `waitForServer(maxAttempts, delay)` - Wait for server health check to pass
- Exports to `window.APIClient` for use throughout the app

**Default behavior**: 3 retries with 1-second delays between attempts.

#### 2. Updated Mental Models Editor
**File**: `electron-app/src/renderer/components/mental-models-editor.js`

- Updated `loadModels()` with retry logic (3 attempts, 1-second delays)
- Updated `loadActiveModels()` with same retry logic
- Provides informative console warnings showing attempt numbers
- Gracefully falls back to empty array on final failure

#### 3. Updated Template Gallery
**File**: `electron-app/src/renderer/components/template-gallery.js`

- Replaced direct `fetch()` call with `window.APIClient.fetchJSON()`
- Now retries failed template loads during startup

#### 4. Enhanced safeFetch in app.js
**File**: `electron-app/src/renderer/app.js`

Updated the existing `safeFetch()` helper function:
- Now uses `APIClient.fetchWithRetry()` for local API calls (127.0.0.1:11436)
- Falls back to original implementation for non-API calls
- Automatically retries failed requests 3 times
- All existing code using `safeFetch()` now gets retry logic for free

This affects:
- `/polly/stats` endpoint calls
- `/polly/integrations/*` endpoint calls
- All dashboard API requests
- All knowledge page API requests

#### 5. Added Server Readiness Check
**File**: `electron-app/src/renderer/app.js`

Updated `DOMContentLoaded` initialization:
- Shows loading overlay with status text
- Waits for server health check before proceeding
- Updates status text to inform user ("Waiting for server to start...")
- Proceeds with initialization once server is ready
- Maximum wait time: 10 seconds

#### 6. Updated Agents Sidebar Initialization
**File**: `electron-app/src/renderer/app.js`

- Updated `initializeAgents()` to use `APIClient.fetchWithRetry()`
- Persona list fetching now retries on failure
- Gracefully falls back to default agent if all retries fail

#### 7. Fixed Duplicate API_BASE_URL Declaration
**File**: `electron-app/src/renderer/api-keys-manager.js`

- Renamed `API_BASE_URL` to `SETTINGS_API_BASE_URL` to avoid conflict
- Updated all references in the file
- Eliminates "Identifier 'API_BASE_URL' has already been declared" error

#### 8. Added API Client to HTML
**File**: `electron-app/src/renderer/index.html`

- Added `<script src="utils/api-client.js"></script>` before other components
- Ensures `window.APIClient` is available during initialization

## Testing

### Before Fix
```
GET http://127.0.0.1:11436/polly/mental-models/list net::ERR_CONNECTION_REFUSED
GET http://127.0.0.1:11436/polly/stats net::ERR_CONNECTION_REFUSED
GET http://127.0.0.1:11436/persona/state net::ERR_CONNECTION_REFUSED
GET http://127.0.0.1:11436/polly/templates net::ERR_CONNECTION_REFUSED
GET http://127.0.0.1:11436/persona/list net::ERR_CONNECTION_REFUSED
Uncaught SyntaxError: Identifier 'API_BASE_URL' has already been declared
```

### After Fix (Expected)
```
[API Client] Waiting for server... (attempt 1/10)
[API Client] Waiting for server... (attempt 2/10)
[API Client] Server is ready
[MentalModelsEditor] Load attempt 1/3 failed: Failed to fetch
[MentalModelsEditor] Retrying in 1000ms...
[MentalModelsEditor] Loaded 34 models
[TemplateGallery] Loaded 12 templates
[Agents] Fetched 5 personas
```

## Benefits

1. **No more startup errors**: Graceful retry logic handles server startup timing
2. **Better UX**: Loading overlay with informative status messages
3. **Resilient**: Automatic retry on transient network failures
4. **Reusable**: `APIClient` utility can be used throughout the codebase
5. **Maintainable**: Centralized retry logic, easy to adjust retry counts/delays
6. **Backward compatible**: Existing code using `safeFetch()` gets retry logic automatically

## Configuration

Default retry settings:
- **Retries**: 3 attempts
- **Delay**: 1000ms (1 second) between attempts
- **Server wait**: 10 attempts with 1 second delays (10 seconds total)

These can be adjusted by passing parameters to the utility functions:
```javascript
// Custom retry settings
await window.APIClient.fetchJSON('/endpoint', {}, 5, 2000); // 5 retries, 2s delay
await window.APIClient.waitForServer(20, 500); // 20 attempts, 500ms delay
```

## Future Improvements

1. **Exponential backoff**: Increase delay between retries (e.g., 1s, 2s, 4s)
2. **Visual retry indicator**: Show retry attempts in UI, not just console
3. **Server status monitor**: Real-time health check indicator in status bar
4. **Offline mode**: Gracefully handle extended server downtime
5. **Apply to remaining components**: Update any remaining direct `fetch()` calls

## Related Files

- `electron-app/src/renderer/utils/api-client.js` (NEW)
- `electron-app/src/renderer/components/mental-models-editor.js`
- `electron-app/src/renderer/components/template-gallery.js`
- `electron-app/src/renderer/api-keys-manager.js`
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/index.html`

## Verification

To verify the fix:
1. Stop the Electron app
2. Start fresh with `npm start`
3. Check console for retry warnings (not errors)
4. Verify all components load successfully after retries
5. Confirm no syntax errors about `API_BASE_URL`
