# Phase 2 Quick Start Guide

## What Was Implemented

✅ Secure credential storage using OS keychain (keytar)
✅ GitHub OAuth authentication flow
✅ Persistent connection status across app restarts
✅ IPC handlers for credential operations
✅ Integration card status updates

## Quick Setup (5 minutes)

### 1. Create GitHub OAuth App

Visit: https://github.com/settings/developers

Click "New OAuth App" and fill in:
- Name: `Polly`
- Homepage: `http://localhost:3000`
- Callback: `http://localhost:3000/oauth/callback`

Copy your Client ID and Client Secret.

### 2. Set Environment Variables

```bash
export GITHUB_CLIENT_ID="Iv1.your_client_id"
export GITHUB_CLIENT_SECRET="your_client_secret"
```

Or add to `~/.zshrc` for persistence.

### 3. Start the App

```bash
cd electron-app
npm run dev
```

### 4. Test OAuth

1. Go to Settings → Integrations
2. Click "connect" on GitHub card
3. Authorize on GitHub
4. Verify card shows "connected as @yourusername"

### 5. Verify Keychain Storage

Open Keychain Access app, search for "Polly", verify "github_token" entry exists.

### 6. Test Persistence

Quit and restart app. GitHub card should still show connected status.

## Common Issues

### "GitHub OAuth not configured"
- Environment variable not set
- Restart terminal after setting variables
- Or run: `GITHUB_CLIENT_ID="..." GITHUB_CLIENT_SECRET="..." npm run dev`

### OAuth window doesn't close
- Check callback URL matches exactly: `http://localhost:3000/oauth/callback`

### Connection not persisting
- Check Keychain Access for "Polly" → "github_token" entry
- Check DevTools console for errors

## Files Changed

1. `electron-app/src/main/main.js` - Added IPC handlers (lines 756-769)
2. `electron-app/src/main/preload.js` - Exposed functions (lines 41-48)
3. `electron-app/src/renderer/app.js` - OAuth logic (lines 798-891)

## What's Next

**Phase 2.1 (Optional)**: Add disconnect button, token validation, better error handling

**Phase 3**: Context7 integration (API key authentication, library search)

**Phase 4**: Multi-calendar integration (iCloud, Google Calendar via CalDAV)

## Need Help?

See detailed documentation: `PHASE2_SETUP.md`

## Testing Checklist

- [ ] GitHub OAuth app created
- [ ] Environment variables set
- [ ] App starts without errors
- [ ] OAuth window opens
- [ ] Can authorize on GitHub
- [ ] Card updates to "connected"
- [ ] Token in Keychain
- [ ] Persists after restart
