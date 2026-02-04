# Polly Electron Safety Mechanisms

## Overview

This document describes the safety mechanisms implemented to prevent crashes in Polly's Electron renderer process. These mechanisms were added after encountering segmentation faults caused by race conditions during IPC bridge initialization.

## The Problem

**Root Cause:** Electron's `contextBridge.exposeInMainWorld()` is asynchronous. If renderer code tries to access `window.polly` before the bridge is ready, it causes null pointer dereferences and crashes.

**Symptoms:**
- Segmentation fault (SIGSEGV) on startup
- `KERN_INVALID_ADDRESS` errors
- Crashes in main UI thread during initialization
- No clear JavaScript error - just native crash

## The Solution: Three-Layer Defense

### 1. PollyBridge - IPC Initialization Guard

**Location:** `/electron-app/src/renderer/app.js` (lines ~56-127)

**Purpose:** Safely wait for `window.polly` to be available before any IPC calls.

**Key Features:**
- **Polling mechanism**: Checks every 50ms if `window.polly` is defined
- **Timeout protection**: Fails gracefully after 10 seconds
- **Promise-based**: Returns a single promise that all callers can await
- **Safe calling**: `safeCall()` method wraps IPC calls with automatic retry

**Example Usage:**
```javascript
// Instead of this (unsafe):
const value = await window.polly.getStore('someKey');

// Use this (safe):
const value = await PollyBridge.safeCall('getStore', 'someKey');
```

**API:**
- `waitForReady()` - Wait for bridge initialization (returns Promise<boolean>)
- `safeCall(method, ...args)` - Safely call any window.polly method
- `isReady()` - Synchronous check (non-blocking)

### 2. safeFetch - Network Error Handler

**Location:** `/electron-app/src/renderer/app.js` (lines ~129-145)

**Purpose:** Wrap fetch calls with graceful error handling.

**Key Features:**
- **Structured error returns**: Always returns `{ok, data, error}`
- **No throws**: Never throws - always returns error info
- **Consistent interface**: Same return format for all outcomes

**Example Usage:**
```javascript
// Instead of this (risky):
try {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed');
  const data = await response.json();
} catch (error) {
  // Handle error
}

// Use this (clean):
const result = await safeFetch(url);
if (result.ok) {
  // Use result.data
} else {
  // Handle result.error
}
```

### 3. withErrorBoundary - Function Wrapper

**Location:** `/electron-app/src/renderer/app.js` (lines ~147-159)

**Purpose:** Wrap async functions to prevent crashes from unhandled exceptions.

**Key Features:**
- **Catch-all protection**: Wraps entire function in try-catch
- **Contextual logging**: Tags errors with function name
- **User notification**: Shows toast for user-facing errors
- **Graceful degradation**: Returns null instead of crashing

**Example Usage:**
```javascript
// Instead of this (can crash):
async function myFunction() {
  // code that might throw
}

// Use this (safe):
const myFunction = withErrorBoundary(async function() {
  // code that might throw
}, 'myFunction');
```

## Implementation Pattern

### Critical Functions (Must Use All Three)

Functions that run during initialization or handle user input should use all three mechanisms:

```javascript
const myFunction = withErrorBoundary(async function() {
  // 1. Wait for IPC bridge
  const ready = await PollyBridge.waitForReady();
  if (!ready) {
    showToast('IPC bridge not available', 'error');
    return;
  }
  
  // 2. Safe IPC calls
  const value = await PollyBridge.safeCall('getStore', 'key');
  
  // 3. Safe API calls
  const result = await safeFetch('http://localhost:11436/api/endpoint');
  if (result.ok) {
    // Process result.data
  }
  
  // Regular logic...
}, 'myFunction');
```

### Functions Already Protected

- ✅ `initialize()` - Main initialization (lines ~233-365)
- ✅ `loadDashboardData()` - Dashboard stats (lines ~3841-3898)
- ✅ `loadKnowledgeData()` - Knowledge stats (lines ~3900-3979)

### When to Use Each Mechanism

| Mechanism | Use When |
|-----------|----------|
| `PollyBridge` | Calling any `window.polly` method, especially during init |
| `safeFetch` | Fetching from Polly server or external APIs |
| `withErrorBoundary` | Any async function that could throw, especially user-facing |

## Best Practices

### DO ✅

1. **Always wait for bridge in init functions**
   ```javascript
   const ready = await PollyBridge.waitForReady();
   if (!ready) return; // Fail gracefully
   ```

2. **Use safeCall for all IPC during initialization**
   ```javascript
   const value = await PollyBridge.safeCall('getStore', 'key');
   ```

3. **Wrap critical functions with error boundaries**
   ```javascript
   const myFunc = withErrorBoundary(async function() {}, 'myFunc');
   ```

4. **Use safeFetch for all API calls**
   ```javascript
   const result = await safeFetch(url);
   if (result.ok) { /* handle */ }
   ```

### DON'T ❌

1. **Don't call window.polly directly in initialization code**
   ```javascript
   // BAD - can crash if bridge isn't ready
   const value = await window.polly.getStore('key');
   ```

2. **Don't use raw fetch without error handling**
   ```javascript
   // BAD - throws on network errors
   const response = await fetch(url);
   const data = await response.json(); // Can crash
   ```

3. **Don't let async functions throw unhandled errors**
   ```javascript
   // BAD - unhandled errors crash Electron
   async function loadData() {
     await someRiskyOperation(); // No try-catch!
   }
   ```

4. **Don't assume synchronous availability**
   ```javascript
   // BAD - race condition
   if (window.polly) {
     // window.polly might become undefined here!
     window.polly.doSomething();
   }
   ```

## Testing Checklist

After making changes to initialization code:

- [ ] Start Electron from cold state (not just restart)
- [ ] Check for any console errors during first 10 seconds
- [ ] Verify all async operations complete successfully
- [ ] Test with slow network (to catch timing issues)
- [ ] Check Console for "[PollyBridge] IPC bridge ready" message

## Debugging Tips

### If Electron crashes on startup:

1. **Check crash location**: Look for null pointer dereferences at address near 0x0
2. **Review recent changes**: Did you add async/await code?
3. **Check IPC calls**: Are you calling window.polly before it's ready?
4. **Add logging**: Log before and after suspect async operations
5. **Use safeFetch**: Replace all fetch calls with safeFetch

### Console Messages to Watch For:

✅ **Good signs:**
- `[Init] Waiting for Polly IPC bridge...`
- `[PollyBridge] IPC bridge ready`
- `[Init] IPC bridge ready, starting initialization...`

❌ **Bad signs:**
- `[PollyBridge] Timeout waiting for IPC bridge` - Bridge never initialized
- `[PollyBridge] Cannot call X: IPC bridge not available` - Called too early
- `[ErrorBoundary:X] Caught error` - Unhandled exception (but caught safely)

## Architecture Notes

### Why This Pattern?

1. **Defense in Depth**: Multiple layers catch different failure modes
2. **Graceful Degradation**: App continues running even if some operations fail
3. **User Experience**: Users see helpful errors instead of crashes
4. **Maintainability**: Clear patterns make it obvious what's safe

### Performance Impact

Negligible:
- **PollyBridge polling**: Only runs once at startup (50ms intervals, <500ms total)
- **safeFetch wrapper**: Single try-catch, no overhead
- **withErrorBoundary**: Same as manual try-catch

### Future Improvements

Potential enhancements:

1. **Preload optimization**: Signal when bridge is ready via event
2. **Retry logic**: Automatic retry for transient IPC failures
3. **Health monitoring**: Track IPC bridge health throughout session
4. **Error analytics**: Log crash patterns to prevent future issues

## Related Files

- `/electron-app/src/main/preload.js` - Defines window.polly API
- `/electron-app/src/renderer/app.js` - Uses safety mechanisms
- `/electron-app/src/renderer/index.html` - UI that depends on safe init

## Version History

- **v1.0** (2026-01-31): Initial implementation
  - Added PollyBridge initialization guard
  - Added safeFetch network wrapper
  - Added withErrorBoundary function wrapper
  - Protected initialize(), loadDashboardData(), loadKnowledgeData()

---

**Remember:** When in doubt, wrap it! It's better to have redundant safety than a single crash.
