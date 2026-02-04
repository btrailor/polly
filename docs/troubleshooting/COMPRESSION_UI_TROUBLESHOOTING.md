# Compression UI Settings - Troubleshooting Guide

## Issue: Compression Tab Not Visible in Settings UI

### Root Cause
The Polly server was started **before** the compression endpoints were added to the codebase. FastAPI loads the route definitions at startup, so changes to endpoints require a server restart.

---

## ✅ Solution: Restart the Polly Server

### Step 1: Stop the Current Server

Find and stop the running Polly server:

```bash
# Find the process
ps aux | grep "polly serve" | grep -v grep
# or
ps aux | grep "uvicorn" | grep -v grep

# Kill it (replace PID with actual process ID)
kill <PID>

# Or use pkill
pkill -f "polly serve"
```

### Step 2: Start the Server Again

```bash
cd /Users/brettgershon/polly
source venv/bin/activate  # if using virtualenv

# Start server
python -m polly serve

# You should see:
# INFO:     Started server process [xxxxx]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:11436
```

### Step 3: Verify Endpoints Are Loaded

Run the test script:

```bash
python test_compression_endpoints.py
```

Expected output:
```
1. GET /api/settings/compression
   Status: 200
   ✅ Success!
   Settings: {
      "success": true,
      "settings": {
         "enabled": true,
         "message_threshold": 20,
         "age_hours": 24,
         "keep_recent": 10,
         "show_stats": false
      }
   }

2. GET /api/settings/compression/stats
   Status: 200
   ✅ Success!
   ...

3. POST /api/settings/compression
   Status: 200
   ✅ Success!
   ...
```

### Step 4: Open the Settings UI

Navigate to: **http://localhost:11436/settings**

You should now see 4 tabs:
1. API Keys
2. Budget & Usage
3. **Compression** ← NEW!
4. Provider Info

---

## 🔍 Verification Checklist

After restarting the server, verify:

- [ ] Server starts without errors
- [ ] `GET /api/settings/compression` returns 200 (not 404)
- [ ] Settings page loads at http://localhost:11436/settings
- [ ] "Compression" tab is visible in the navigation
- [ ] Clicking "Compression" tab shows the compression settings form
- [ ] Settings load with default values (enabled=true, threshold=20, etc.)
- [ ] Toggling "Enable Automatic Compression" enables/disables inputs
- [ ] Clicking "Save Compression Settings" shows success message
- [ ] Changes are saved to `~/.polly/config.yaml`

---

## 🐛 Still Not Working?

### Check 1: Verify Files Were Modified

```bash
# Check settings_api.py has compression endpoints
grep -n "def get_compression_settings" interfaces/settings_api.py
# Should show line 266

# Check HTML has compression tab
grep "Compression" web/templates/settings.html
# Should show multiple matches

# Check JavaScript has compression functions
grep "loadCompressionSettings" web/static/js/settings.js
# Should show line 412
```

### Check 2: Check Browser Console

1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Navigate to http://localhost:11436/settings
4. Look for any JavaScript errors
5. Click "Compression" tab
6. Check for API errors (failed to load, 404, etc.)

### Check 3: Check Server Logs

Look at the terminal where you ran `python -m polly serve`:
- Any errors loading settings_api.py?
- Any import errors for CompressionManager?
- Any FastAPI route registration errors?

### Check 4: Verify Config Properties

```bash
# Test that config properties exist
python3 -c "
from core.config import get_config
config = get_config()
print('Enabled:', config.compression_enabled)
print('Threshold:', config.compression_threshold)
print('Age:', config.compression_age_hours)
print('Keep:', config.compression_keep_recent)
print('Stats:', config.compression_show_stats)
"
```

Expected output:
```
Enabled: True
Threshold: 20
Age: 24
Keep: 10
Stats: False
```

### Check 5: Manual API Test

```bash
# Test endpoint directly
curl http://localhost:11436/api/settings/compression

# Expected response:
# {"success":true,"settings":{"enabled":true,"message_threshold":20,"age_hours":24,"keep_recent":10,"show_stats":false}}
```

---

## 📝 Files Modified

These files were modified to add compression UI:

1. `/Users/brettgershon/polly/interfaces/settings_api.py`
   - Lines 42-47: Added `UpdateCompressionRequest` model
   - Lines 265-390: Added 3 compression endpoints

2. `/Users/brettgershon/polly/web/templates/settings.html`
   - Line 19: Added "Compression" tab button
   - Lines 77-130: Added compression tab content

3. `/Users/brettgershon/polly/web/static/js/settings.js`
   - Lines 51-56: Added compression tab loading in `switchTab()`
   - Lines 411-561: Added 5 compression functions

4. `/Users/brettgershon/polly/web/static/css/settings.css`
   - Lines 514-548: Added compression-specific styles

5. `/Users/brettgershon/polly/core/config.py` (already had these)
   - Lines 189-206: Compression property methods

---

## 🎯 Expected Behavior After Fix

Once the server is restarted:

1. **Settings Page Loads**
   - Navigate to http://localhost:11436/settings
   - See 4 tabs including "Compression"

2. **Compression Tab Works**
   - Click "Compression" tab
   - Form loads with current settings
   - Checkbox and inputs are interactive

3. **Settings Save**
   - Change values
   - Click "Save Compression Settings"
   - See green success message
   - Check `~/.polly/config.yaml` - changes are there

4. **Stats Display**
   - Initially shows "No compression data yet"
   - After compression occurs (25+ messages in conversation)
   - Stats show: conversations, tokens saved, compression ratio

---

## 💡 Why This Happened

The compression endpoints were added to `settings_api.py` **while the server was running**.

FastAPI (like most web frameworks) loads all routes when the application starts. Changes to route definitions don't take effect until the application restarts.

This is normal behavior and not a bug in the code!

---

## Contact

If issues persist after restart:
1. Share server logs
2. Share browser console errors  
3. Share output of `test_compression_endpoints.py`
