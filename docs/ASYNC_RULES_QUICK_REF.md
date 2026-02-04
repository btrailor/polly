# 🚨 POLLY ASYNC RULES - KEEP THIS VISIBLE WHILE CODING

## The Golden Rules

1. **`async def` ≠ non-blocking**  
   Blocking code in async functions still blocks the entire server.

2. **One blocking call breaks everything**  
   A single `time.sleep(1)` or `open('file').read()` hangs ALL requests.

3. **Use IP addresses in Electron**  
   `localhost` → IPv6 → fails on macOS. Use `127.0.0.1` instead.

4. **CSP must match fetch URLs**  
   Change URL? Update `Content-Security-Policy` in `index.html` too.

5. **Test with timeouts**  
   `curl -m 3` catches blocking immediately. Don't test without it.

---

## Quick Reference

### ❌ Blocks Server (DON'T)

```python
@app.get("/stats")
async def get_stats():
    rag = UnifiedRAG(...)        # Blocks for 5 seconds!
    data = open('file').read()   # Blocks!
    time.sleep(1)                 # Blocks!
    requests.get('http://...')    # Blocks!
```

### ✅ Non-Blocking (DO)

```python
@app.get("/stats")
async def get_stats():
    # Use lazy init
    if app.state.rag is None:
        return {"status": "initializing"}
    
    # Thread blocking calls
    data = await asyncio.to_thread(
        lambda: open('file').read()
    )
    
    # Use async sleep
    await asyncio.sleep(1)
    
    # Use async HTTP
    async with httpx.AsyncClient() as client:
        response = await client.get('http://...')
```

---

## Emergency Debugging

```bash
# Server hung?
curl -m 3 http://127.0.0.1:11436/health
# No response = something is blocking

# Find the culprit:
tail -50 /tmp/polly-fixed.log | grep "INIT"
# Shows where initialization stopped

# Kill and restart:
pkill -9 -f uvicorn && npm start
```

---

## Before Committing

```bash
# 1. Server responds quickly
curl -m 3 http://127.0.0.1:11436/health

# 2. No blocking in logs
grep -i "blocking\|took.*[0-9][0-9][0-9][0-9]ms" /tmp/polly-fixed.log

# 3. Frontend works
# Open app → click all ribbon buttons → no errors

# 4. CSP allows connections
# Open DevTools → Console → no "Content Security Policy" errors
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `fetch('http://localhost:11436')` | Use `'http://127.0.0.1:11436'` |
| `UnifiedRAG()` in endpoint | Initialize in startup event |
| `open('file').read()` in async | `await asyncio.to_thread(lambda: open('file').read())` |
| Forgot to update CSP | Grep for "Content-Security-Policy" |
| No timeout in test | Add `-m 3` to curl |

---

## File Locations

- CSP: `electron-app/src/renderer/index.html` (line 6)
- Server URLs: `electron-app/src/renderer/app.js` (67 places)
- Server binding: `electron-app/src/main/main.js` (line 217)
- Stats endpoint: `interfaces/server.py` (line 732)

---

**PRINT THIS AND PUT IT ON YOUR DESK**

Full details: `docs/POST_MORTEM_server_blocking.md`
