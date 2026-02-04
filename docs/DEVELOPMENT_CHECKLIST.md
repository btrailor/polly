# Polly Development Checklist

Quick reference to avoid common pitfalls. See `POST_MORTEM_server_blocking.md` for detailed explanations.

---

## 🚨 Before Committing Changes

### Server/Backend Changes

- [ ] **No blocking I/O in async functions**
  ```python
  # ❌ BAD
  async def handler():
      data = open('file').read()  # Blocks!
  
  # ✅ GOOD  
  async def handler():
      data = await asyncio.to_thread(lambda: open('file').read())
  ```

- [ ] **Test with timeout**
  ```bash
  curl -m 3 http://127.0.0.1:11436/your-endpoint
  # Should return in <3 seconds
  ```

- [ ] **Profile any new initialization code**
  ```python
  import time
  start = time.time()
  self._init_something()
  print(f"Init took {time.time() - start:.2f}s", flush=True)
  ```

- [ ] **Check server logs show "Application startup complete"**
  ```bash
  tail -f /tmp/polly-fixed.log | grep "startup complete"
  ```

### Frontend/Electron Changes

- [ ] **Use IP addresses, not hostnames**
  ```javascript
  // ❌ BAD
  fetch('http://localhost:11436/api')
  
  // ✅ GOOD
  fetch('http://127.0.0.1:11436/api')
  ```

- [ ] **Update CSP when changing URLs**
  ```bash
  grep -n "Content-Security-Policy" electron-app/src/renderer/index.html
  ```

- [ ] **No CSP errors in browser console**
  - Open DevTools → Console
  - Look for "Content Security Policy" errors

- [ ] **All ribbon buttons work**
  - Click each one to verify navigation

### General

- [ ] **Test in actual Electron app, not just curl**
  - Electron's fetch() behaves differently than curl
  
- [ ] **Grep for hardcoded values when changing URLs/ports**
  ```bash
  grep -r "11436\|localhost" electron-app/src/
  ```

---

## ⚡ Quick Smoke Tests

Run these after any server or frontend changes:

```bash
# 1. Server responds quickly
curl -m 3 http://127.0.0.1:11436/health
# Should return: {"status":"ok","server":"running"}

# 2. Stats endpoint doesn't block
curl -m 3 http://127.0.0.1:11436/polly/stats
# Should return immediately (empty or real data)

# 3. Notes index accessible
curl -m 3 http://127.0.0.1:11436/polly/notes/index?limit=1
# Should return notes list

# 4. Multiple requests don't block each other
curl -m 3 http://127.0.0.1:11436/health &
curl -m 3 http://127.0.0.1:11436/health &
curl -m 3 http://127.0.0.1:11436/health &
wait
# All three should complete quickly
```

---

## 🐛 Debugging Blocked Server

If server starts but doesn't respond:

1. **Check if process is running**
   ```bash
   ps aux | grep uvicorn
   ```

2. **Check if it's consuming CPU**
   ```bash
   top -pid $(pgrep -f uvicorn)
   # If 0% CPU → blocked on I/O
   # If 100% CPU → infinite loop
   ```

3. **Test with timeout**
   ```bash
   curl -v -m 3 http://127.0.0.1:11436/health
   # Look for "Connected to" vs "Connection refused"
   # Connected but no response = server is blocked
   ```

4. **Check logs for last initialization step**
   ```bash
   tail -50 /tmp/polly-fixed.log | grep "INIT\|initialized"
   # See where initialization stopped
   ```

5. **Kill and restart with profiling**
   ```bash
   pkill -9 -f uvicorn
   npm start
   # Watch logs for timing info
   ```

---

## 🎯 Common Anti-Patterns

### ❌ DON'T: Initialize Heavy Objects in Request Handlers

```python
@app.get("/stats")
async def get_stats():
    rag = UnifiedRAG(...)  # Takes 5 seconds, blocks all requests!
    return rag.get_stats()
```

### ✅ DO: Use Lazy Initialization with Caching

```python
@app.get("/stats")
async def get_stats():
    if app.state.rag is None:
        return {"status": "initializing"}
    return app.state.rag.get_stats()
```

---

### ❌ DON'T: Mix Blocking and Async Code

```python
async def process():
    data = open('file.txt').read()  # Blocks event loop!
    return data
```

### ✅ DO: Make Blocking Calls Explicit

```python
async def process():
    data = await asyncio.to_thread(
        lambda: open('file.txt').read()
    )
    return data
```

---

### ❌ DON'T: Assume Threads Mean Non-Blocking

```python
def __init__(self):
    self.watcher = Observer()
    self.watcher.schedule(...)  # Still blocks for 5s scanning directory!
    self.watcher.start()
```

### ✅ DO: Move Entire Init to Background Thread

```python
def __init__(self):
    self.watcher = None
    threading.Thread(target=self._init_watcher, daemon=True).start()

def _init_watcher(self):
    self.watcher = Observer()
    self.watcher.schedule(...)
    self.watcher.start()
```

---

### ❌ DON'T: Use Hostname 'localhost' in Electron

```javascript
fetch('http://localhost:11436/api')
// Tries IPv6 first, may fail on macOS
```

### ✅ DO: Use IP Address

```javascript
fetch('http://127.0.0.1:11436/api')
// Direct IPv4 connection
```

---

## 📋 Pre-Deployment Checklist

Before considering a feature "done":

- [ ] Server starts in <5 seconds
- [ ] Health endpoint responds in <1 second
- [ ] No initialization steps take >2 seconds (profile them!)
- [ ] All endpoints respond within timeout
- [ ] Multiple simultaneous requests work
- [ ] Browser console has no errors
- [ ] All navigation buttons work
- [ ] Can create/read/update notes
- [ ] Server logs show no warnings
- [ ] CSP allows all necessary connections

---

## 🔧 When Adding New Features

### Adding New Endpoint

1. Make it work without Polly initialized:
   ```python
   @app.get("/new-feature")
   async def new_feature():
       if app.state.polly is None:
           return {"status": "initializing"}
       # ... rest of logic
   ```

2. Add to smoke test:
   ```bash
   curl -m 3 http://127.0.0.1:11436/new-feature
   ```

### Adding New Component

1. Profile initialization:
   ```python
   start = time.time()
   self._init_new_component()
   duration = time.time() - start
   if duration > 1.0:
       logger.warning(f"Component init took {duration:.2f}s")
   ```

2. Make it optional:
   ```python
   if self.config.get("new_component.enabled", False):
       self._init_new_component()
   ```

3. Allow graceful degradation:
   ```python
   if self.new_component is None:
       logger.info("Feature disabled")
       return default_value
   ```

### Changing URLs/Ports

1. Grep for all occurrences:
   ```bash
   grep -r "old_url\|old_port" .
   ```

2. Update CSP in `index.html`:
   ```html
   <meta http-equiv="Content-Security-Policy" 
         content="connect-src 'self' http://NEW_URL:*">
   ```

3. Update server binding in `main.js`:
   ```javascript
   '--host', 'NEW_HOST', '--port', 'NEW_PORT'
   ```

---

## 📚 Required Reading

- `POST_MORTEM_server_blocking.md` - Detailed analysis of what went wrong
- `docs/architecture.md` - System architecture (TODO: create this)
- `docs/async_best_practices.md` - FastAPI async patterns (TODO: create this)

---

## 🆘 Emergency Fixes

### Server completely hung, need to ship now:

1. **Disable the blocking component**:
   ```python
   def _init_blocking_thing(self):
       logger.warning("Temporarily disabled")
       self.blocking_thing = None
       return
   ```

2. **Make endpoint return empty data**:
   ```python
   @app.get("/endpoint")
   async def endpoint():
       return {"status": "disabled", "data": []}
   ```

3. **Document it**:
   ```python
   # TODO: Re-enable after fixing blocking initialization
   # See: POST_MORTEM_server_blocking.md
   ```

### Frontend can't connect:

1. **Check CSP first**:
   - Open DevTools → Console
   - Look for "Content Security Policy"

2. **Check URL format**:
   - Use `127.0.0.1`, not `localhost`

3. **Check server is actually running**:
   ```bash
   curl http://127.0.0.1:11436/health
   ```

---

**Last Updated**: February 1, 2026  
**Next Review**: When adding async components or changing URLs
