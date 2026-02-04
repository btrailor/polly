# Post-Mortem: Server Blocking & Notes Not Appearing (Feb 1, 2026)

## Incident Summary

**Duration**: ~2 hours  
**Impact**: Complete app breakage - server hung on all requests, notes browser empty, navigation broken  
**Root Causes**: Multiple cascading issues introduced during CM6 live preview work  
**Resolution**: Fixed IPv6/localhost issue, CSP policy, and server initialization blocking

---

## Timeline of Events

### Initial State (Working)
- CodeMirror 6 live preview working
- Cursor position preserved during edits
- App navigation working
- Notes visible in browser

### Changes Made (That Broke Things)
1. **Attempted to fix file watcher blocking** by disabling it
2. **Disabled Polly initialization** in startup event to prevent blocking
3. **Made health endpoint return immediately** without waiting for Polly
4. **Changed server binding** from `0.0.0.0` to `127.0.0.1`

### Cascading Failures
1. Server appeared to start but couldn't process ANY requests
2. All frontend fetch() calls failed with `ERR_CONNECTION_REFUSED`
3. After fixing connection, CSP blocked all requests
4. After fixing CSP, stats endpoint blocked trying to initialize RAG
5. After fixing stats, notes index was empty (not rebuilt)

---

## Root Causes

### 1. IPv6/IPv4 Resolution Issue ⚠️ **CRITICAL**

**What Happened:**
- Server bound to IPv4 address `127.0.0.1:11436`
- Frontend used `localhost:11436` for all fetch requests
- macOS resolved `localhost` to IPv6 `::1` FIRST, then IPv4 `127.0.0.1`
- Electron's fetch() gave up after IPv6 connection failed
- All requests showed `ERR_CONNECTION_REFUSED` despite server running

**Why We Didn't Catch It:**
```bash
# When testing with curl, this works fine because curl retries IPv4:
curl http://localhost:11436/health
# Output shows: "Trying [::1]:11436... Connection refused, Trying 127.0.0.1... Connected"

# But Electron's fetch() doesn't retry:
fetch('http://localhost:11436/health')
// Fails immediately after IPv6 refuses
```

**The Fix:**
- Changed all frontend URLs from `localhost` to `127.0.0.1`
- Updated CSP to allow both `localhost:*` and `127.0.0.1:*`

**Prevention:**
1. **Always use IP addresses, not hostnames, for local servers in Electron**
2. **Or bind server to both IPv4 and IPv6**: `--host 0.0.0.0` (though this had other issues)
3. **Test with Electron's fetch(), not just curl** - they behave differently

---

### 2. Content Security Policy (CSP) Blocking ⚠️ **CRITICAL**

**What Happened:**
```html
<!-- Before (in index.html) -->
<meta http-equiv="Content-Security-Policy" 
      content="connect-src 'self' http://localhost:*;">

<!-- After changing URLs to 127.0.0.1, CSP blocked them -->
```

**The Error:**
```
Refused to connect to 'http://127.0.0.1:11436/polly/stats' 
because it violates the document's Content Security Policy.
```

**Why We Didn't Catch It:**
- Changed JavaScript URLs but forgot to update CSP in HTML
- Browser console showed CSP errors but they looked like network errors
- The error message mentions "Content Security Policy" but we focused on connection issues first

**The Fix:**
```html
<meta http-equiv="Content-Security-Policy" 
      content="connect-src 'self' http://localhost:* http://127.0.0.1:*;">
```

**Prevention:**
1. **Grep for ALL occurrences** when changing URLs:
   ```bash
   grep -r "localhost\|127.0.0.1" electron-app/src/
   ```
2. **CSP must match fetch URLs** - keep them in sync
3. **Look for "Content Security Policy" in console errors** - don't ignore them
4. **Better yet: Use a config constant** instead of hardcoding URLs

---

### 3. Synchronous Blocking in Async FastAPI Server 🔥 **ARCHITECTURAL**

**What Happened:**
The `/polly/stats` endpoint tried to initialize `UnifiedRAG`:

```python
@app.get("/polly/stats")
async def get_stats():
    # This looks async but the constructor is synchronous!
    rag = UnifiedRAG(
        db_path=config.vector_db_path,
        ollama_host=config.ollama_host,
        embedding_model=config.embedding_model,
        pattern_learner=None
    )
    return {'rag': rag.get_stats()}
```

**Why This Blocks:**
- `UnifiedRAG.__init__()` does heavy I/O:
  - Opens ChromaDB database (disk I/O)
  - Possibly initializes BM25 index (reads all documents)
  - Validates Ollama connection (network call)
- Python `async def` doesn't make blocking code non-blocking
- FastAPI uses a single event loop for all requests
- When one request blocks, ALL requests hang

**The Symptom:**
```bash
curl http://127.0.0.1:11436/health  # Hangs forever
ps aux | grep uvicorn                # Process exists, consuming 0% CPU
```

The server is alive but frozen, waiting for synchronous I/O to complete.

**The Fix:**
Don't initialize heavy objects in request handlers - use lazy initialization or startup events:

```python
@app.get("/polly/stats")
async def get_stats():
    # Check if already initialized
    polly = app.state.polly
    if polly:
        return polly.get_stats()
    
    # Return empty stats if not ready
    # Frontend will retry
    return {
        'user': 'unknown',
        'rag': {'notes': {'count': 0}, 'codebase': {'count': 0}},
        'patterns': 0
    }
```

**Prevention Rules:**
1. ⛔ **NEVER instantiate heavy objects in request handlers**
2. ⛔ **NEVER do blocking I/O in `async def` without `await asyncio.to_thread()`**
3. ✅ **Use startup events for initialization**
4. ✅ **Use lazy initialization with caching**
5. ✅ **Make constructors lightweight** - defer I/O to explicit `async def initialize()` methods
6. ✅ **Test with** `curl -m 3` (3 second timeout) to detect hangs

---

### 4. File Watcher Blocking Event Loop 🔥 **ARCHITECTURAL**

**What Happened:**
`watchdog.Observer` uses threads but still blocks when started:

```python
def _init_notes_sync(self):
    from core.notes_file_watcher import NotesFileWatcher
    # This blocks for several seconds while scanning iCloud directory
    self.notes_sync = NotesFileWatcher(self.config)
    self.notes_sync.start()  # Starts background thread but __init__ already blocked
```

**Why This Blocks:**
- `watchdog` scans the entire directory tree on initialization
- iCloud directories can be slow (network-backed filesystem)
- Even though Observer uses threads, the initial scan happens synchronously
- This blocked Polly initialization, which blocked the first request handler

**The Temporary Fix:**
Disabled file watcher entirely:
```python
def _init_notes_sync(self):
    logger.info("!!! NOTES SYNC TEMPORARILY DISABLED !!!")
    self.notes_sync = None
    return
```

**The Proper Fix** (TODO):
```python
def _init_notes_sync(self):
    """Initialize file watcher asynchronously in background."""
    if not self.config.get("notes.sync.enabled", False):
        self.notes_sync = None
        return
    
    # Don't block - start in background
    import threading
    def init_watcher():
        from core.notes_file_watcher import NotesFileWatcher
        self.notes_sync = NotesFileWatcher(self.config)
        self.notes_sync.start()
        logger.info("File watcher initialized in background")
    
    thread = threading.Thread(target=init_watcher, daemon=True)
    thread.start()
```

**Prevention:**
1. ⛔ **NEVER scan filesystems synchronously during init**
2. ⛔ **NEVER assume "it's in a thread so it's non-blocking"** - check the constructor
3. ✅ **Use background threads/tasks for slow initialization**
4. ✅ **Add timeouts to all init steps** and log if they exceed threshold
5. ✅ **Profile initialization** with timestamps (we added this)

---

### 5. Notes Index Not Built 📊 **DATA**

**What Happened:**
- Notes existed in `/Users/.../iCloud/Polly/notes/` (108 files)
- But `NotesIndex` was empty (0 notes)
- Frontend showed empty list

**Why:**
- The notes index is separate from RAG
- It's stored in `~/.polly/notes_index.json`
- It only rebuilds when explicitly triggered
- No auto-rebuild on app startup or file changes (because file watcher was disabled)

**The Fix:**
```bash
curl -X POST http://127.0.0.1:11436/polly/notes/index/build \
  -H "Content-Type: application/json" \
  -d '{"notes_path": "...", "recursive": true}'
```

**Prevention:**
1. ✅ **Auto-rebuild index on first startup** if empty
2. ✅ **Rebuild on file watcher events** (once file watcher is fixed)
3. ✅ **Add "Refresh Index" button** in UI (already exists)
4. ✅ **Show index stats** in UI so user knows if it's empty

---

## Prevention Guidelines

### 🚨 Critical Rules for Async FastAPI

1. **Never instantiate heavy objects in request handlers**
   ```python
   # ❌ BAD
   @app.get("/stats")
   async def get_stats():
       rag = UnifiedRAG(...)  # BLOCKS!
   
   # ✅ GOOD
   @app.get("/stats")
   async def get_stats():
       if app.state.rag is None:
           return {"status": "initializing"}
       return app.state.rag.get_stats()
   ```

2. **Use startup events for initialization**
   ```python
   @app.on_event("startup")
   async def startup():
       # Still use background thread for blocking I/O
       app.state.rag = await asyncio.to_thread(initialize_rag)
   ```

3. **Make all I/O async or explicitly threaded**
   ```python
   # ❌ BAD - blocks event loop
   async def slow_operation():
       data = open('file.txt').read()  # Blocks!
       return data
   
   # ✅ GOOD - explicitly threaded
   async def slow_operation():
       data = await asyncio.to_thread(
           lambda: open('file.txt').read()
       )
       return data
   ```

4. **Test with timeouts**
   ```bash
   # Always test with -m (max time) to detect hangs
   curl -m 3 http://127.0.0.1:11436/endpoint
   ```

### 🌐 Network & Connectivity Rules

1. **Use IP addresses, not hostnames, in Electron**
   ```javascript
   // ❌ BAD - IPv6 issues on macOS
   fetch('http://localhost:11436/api')
   
   // ✅ GOOD
   fetch('http://127.0.0.1:11436/api')
   ```

2. **Keep CSP in sync with fetch URLs**
   ```javascript
   // When changing API_URL, grep for CSP too:
   grep -r "Content-Security-Policy" electron-app/
   ```

3. **Use constants for URLs**
   ```javascript
   // ✅ GOOD - single source of truth
   const API_URL = 'http://127.0.0.1:11436';
   fetch(`${API_URL}/polly/stats`);
   ```

### 📊 Initialization & State Management

1. **Profile all initialization steps**
   ```python
   import time
   _start = time.time()
   self._init_rag()
   print(f"_init_rag took {time.time() - _start:.2f}s")
   ```

2. **Set timeouts for initialization steps**
   ```python
   def _init_component(self, timeout=10):
       try:
           with timeout_context(timeout):
               self.component = Component()
       except TimeoutError:
           logger.error(f"Component init exceeded {timeout}s")
           self.component = None
   ```

3. **Make components independently functional**
   - Notes browser should work without RAG
   - RAG should work without file watcher
   - Each component has graceful degradation

4. **Add health checks that don't require initialization**
   ```python
   @app.get("/health")
   async def health():
       # Just return OK - don't check dependencies
       return {"status": "ok"}
   
   @app.get("/health/detailed")
   async def detailed_health():
       # This one can check components
       return {
           "polly": app.state.polly is not None,
           "rag": app.state.rag is not None,
       }
   ```

---

## Architectural Improvements Needed

### 1. Separate Data Layer from Application Layer

**Current Problem:**
- `UnifiedRAG` does everything: database, embedding, search
- Can't get stats without initializing entire RAG system

**Better Architecture:**
```
┌─────────────────────────────────────┐
│  FastAPI Endpoints (Async)          │
├─────────────────────────────────────┤
│  Service Layer (Async facades)      │
│  - StatsService                     │
│  - NotesService                     │
│  - QueryService                     │
├─────────────────────────────────────┤
│  Data Layer (Lazy initialization)   │
│  - ChromaDB (on-demand)             │
│  - NotesIndex (on-demand)           │
│  - PatternLearner (on-demand)       │
└─────────────────────────────────────┘
```

**Benefits:**
- Can get stats without initializing RAG
- Each component initializes independently
- Better testability

### 2. Async-First Design

**Convert blocking constructors to async methods:**

```python
# ❌ Current (blocking)
class UnifiedRAG:
    def __init__(self):
        self.db = ChromaDB(...)  # Blocks!
        self.client = OllamaClient(...)  # Blocks!

# ✅ Better (async)
class UnifiedRAG:
    def __init__(self):
        self.db = None
        self.client = None
    
    async def initialize(self):
        self.db = await asyncio.to_thread(ChromaDB, ...)
        self.client = await asyncio.to_thread(OllamaClient, ...)
```

### 3. Configuration Constants

**Create a single source of truth for URLs:**

```javascript
// electron-app/src/config.js
export const API_CONFIG = {
    HOST: '127.0.0.1',
    PORT: 11436,
    get BASE_URL() {
        return `http://${this.HOST}:${this.PORT}`;
    }
};

// Update CSP in build script
const CSP = `connect-src 'self' http://${API_CONFIG.HOST}:*`;
```

### 4. Startup Health Monitoring

**Add visibility into what's initializing:**

```python
@app.get("/health/startup")
async def startup_status():
    return {
        "components": {
            "polly": {
                "status": "ready" if app.state.polly else "initializing",
                "initialized_at": app.state.polly_init_time
            },
            "rag": {
                "status": "ready" if app.state.rag else "pending",
                "blocking": False
            }
        }
    }
```

---

## Testing Checklist

Before considering server/app changes complete:

### Server Tests
- [ ] `curl -m 3 http://127.0.0.1:11436/health` returns in <1s
- [ ] `curl -m 3 http://127.0.0.1:11436/polly/stats` returns in <1s (empty or real data)
- [ ] Multiple simultaneous requests don't block each other
- [ ] Server startup completes in <5 seconds
- [ ] No "blocking" warnings in logs

### Frontend Tests
- [ ] All ribbon buttons work (navigation)
- [ ] Notes browser loads notes
- [ ] Dashboard shows stats (even if 0)
- [ ] No CSP errors in console
- [ ] No connection refused errors
- [ ] Can switch between views smoothly

### Integration Tests
- [ ] Create a note → appears in notes browser
- [ ] Query Polly → gets response (even if it's "initializing")
- [ ] File changes → detected by watcher (when re-enabled)

---

## Lessons Learned

1. **"Async" doesn't mean "non-blocking"** - Python async/await only helps if you await async operations. Blocking I/O still blocks.

2. **Network resolution is platform-specific** - `localhost` behaves differently on macOS vs Linux vs Windows. Use IPs in Electron.

3. **CSP is easy to break** - When changing URLs, grep for CSP too.

4. **One blocking call breaks everything** - In an async server, a single `time.sleep(1)` or file read can hang all requests.

5. **Test with timeouts** - `curl -m 3` would have immediately shown the blocking issue.

6. **Separate concerns** - Notes browser shouldn't depend on Polly initialization. Each feature should work independently.

7. **Profile initialization** - We added timestamp logging which immediately showed where the blocking happened.

8. **Read error messages carefully** - "Content Security Policy" was right there in the console, but we initially focused on "connection refused".

---

## Action Items

### Immediate (Before Next Session)
- [x] Fix IPv6/localhost issue
- [x] Fix CSP to allow 127.0.0.1
- [x] Make stats endpoint non-blocking
- [x] Build notes index
- [ ] Add API_URL constant to frontend
- [ ] Add startup profiling to all init methods

### Short Term (Next Week)
- [ ] Convert UnifiedRAG to async initialization
- [ ] Fix file watcher to not block (background thread)
- [ ] Add detailed health check endpoint
- [ ] Add "initializing" state to frontend
- [ ] Add auto-rebuild for empty notes index

### Long Term (Next Month)
- [ ] Refactor to async-first architecture
- [ ] Separate data layer from application layer
- [ ] Add integration test suite
- [ ] Add startup timeout monitoring
- [ ] Document all blocking operations

---

## Reference: Key Files Modified

### Frontend
1. `electron-app/src/renderer/index.html` - CSP update
2. `electron-app/src/renderer/app.js` - URL changes (67 occurrences)
3. `electron-app/src/renderer/notes-manager.js` - URL changes (18 occurrences)
4. `electron-app/src/renderer/api-keys-manager.js` - URL changes (1 occurrence)

### Backend
1. `interfaces/server.py` - Stats endpoint made non-blocking
2. `core/polly.py` - Added initialization profiling, disabled file watcher

### Configuration
1. `electron-app/src/main/main.js` - Server binding to 127.0.0.1

---

**Date**: February 1, 2026  
**Author**: Code session with Brett  
**Status**: Resolved  
**Follow-up**: See Action Items above
