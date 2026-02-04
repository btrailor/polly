# Quick Fix: Domains Not Loading in Settings

## Issue
- Dashboard shows domains (hardcoded in HTML)
- Settings → Domains shows "Failed to load domains"
- Error: `GET http://localhost:11436/polly/domains/config` returns 404 Not Found

## Root Cause
The Polly server was started **before** the new domain configuration endpoints were added to `interfaces/server.py`. The running server doesn't have the new routes.

## Solution
**Restart the Polly server** to load the new domain endpoints.

### Steps:

1. **Stop the current server:**
   ```bash
   # Find the Python server process
   ps aux | grep "python.*server.py"
   
   # Kill it (replace PID with actual process ID)
   kill <PID>
   
   # Or use pkill
   pkill -f "python.*server.py"
   ```

2. **Start the server again:**
   ```bash
   cd /Users/brettgershon/polly
   source venv/bin/activate
   python -m interfaces.server
   ```
   
   Or however you normally start the Polly server.

3. **Verify the endpoint is available:**
   ```bash
   curl http://localhost:11436/polly/domains/config
   ```
   
   Should return JSON with your domains config (not a 404 error).

4. **Refresh the Electron app** and navigate to Settings → Domains

## Expected Result
After restarting the server, the Settings → Domains tab should load successfully and show your 5 domains (Sigils, Signals, Scrolls, Glyphs, Grids) with full CRUD functionality.

## Alternative: Check Config File
If the endpoint works but still shows an error, check if the domains.json file exists:

```bash
ls -la ~/.polly/domains.json
```

If it doesn't exist, the migration might not have run. Check:

```bash
cat ~/.polly/domains.json
```

Should show your 5 domains in JSON format.

## Verification Checklist
- [ ] Server restarted
- [ ] `GET /polly/domains/config` returns 200 OK (not 404)
- [ ] `~/.polly/domains.json` exists
- [ ] Settings → Domains tab loads without errors
- [ ] Can see all 5 domains in the list
- [ ] Can edit, create, delete domains

## If Still Not Working

Check server logs for errors:
```bash
# Look for errors when loading domains config
grep -i "domain\|error" server.log
```

Or run the domain test script:
```bash
cd /Users/brettgershon/polly
python test_domain_api.py
```

This will verify the backend domain configuration system is working correctly.
