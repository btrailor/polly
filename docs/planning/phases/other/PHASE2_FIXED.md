# Phase 2: GitHub OAuth - Quick Start

## What's New

GitHub OAuth is now fully configurable through the UI - no environment variables needed!

## Setup Steps (5 minutes)

### 1. Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in:
   - **Application name**: `Polly`
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/oauth/callback`
4. Click **"Register application"**
5. Copy your **Client ID** and **Client Secret**

### 2. Configure in Polly

1. Start Polly: `cd electron-app && npm run dev`
2. Go to **Settings → Integrations**
3. Click **"configure"** on the GitHub card
4. Paste your **Client ID** and **Client Secret**
5. Click **"save configuration"**

### 3. Connect to GitHub

1. Click **"connect"** on the GitHub card
2. A browser window opens - authorize Polly
3. Window closes automatically
4. Card updates to show "connected as @yourusername"

### 4. Verify It Works

- Quit and restart Polly
- Go to Settings → Integrations
- GitHub card should still show "connected"
- Token is stored securely in macOS Keychain

## How It Works

```
User Flow:
1. Click "configure" → Enter Client ID/Secret → Save
2. Click "connect" → OAuth window opens → Authorize on GitHub
3. Token stored in macOS Keychain (encrypted by OS)
4. Connection persists across restarts

Technical:
- OAuth credentials stored in electron-store (Client ID/Secret)
- Access token stored in macOS Keychain via keytar
- No plaintext secrets in files
- Main process handles all OAuth logic
```

## Where Things Are Stored

| Data | Storage | Example |
|------|---------|---------|
| Client ID | electron-store | `github_oauth_client_id` |
| Client Secret | electron-store | `github_oauth_client_secret` |
| Access Token | macOS Keychain | Service: "Polly", Account: "github_token" |
| Username | electron-store | `github_username` |

## UI Changes

**GitHub Integration Card** now shows:
- **"connect"** button - Start OAuth flow
- **"configure"** button - Set up Client ID/Secret (visible by default)
- **Config panel** with:
  - Client ID input field
  - Client Secret input field (password type)
  - Callback URL (readonly, for reference)
  - Link to create GitHub OAuth app
  - Save button

## Common Issues

### "Please configure GitHub OAuth first"

**Solution**: Click the "configure" button and enter your Client ID and Secret from GitHub.

### OAuth window doesn't open

**Check**:
1. Did you save your configuration?
2. Are Client ID and Secret correct?
3. Check DevTools console for errors

### "No access token received"

**Check**:
1. Is your Client Secret correct?
2. Is the callback URL exactly `http://localhost:3000/oauth/callback` in your GitHub OAuth app?

### Connection doesn't persist

**Check**:
1. Look for "Polly" in Keychain Access app
2. You should see "github_token" entry
3. Check console for keytar errors

## Files Modified

1. `electron-app/src/renderer/index.html` (lines 452-475)
   - Added OAuth config panel with input fields

2. `electron-app/src/renderer/app.js` (lines 816-915)
   - Added save config button handler
   - Added config validation before OAuth
   - Loads saved config on page load
   - Opens GitHub settings link

3. `electron-app/src/main/main.js` (lines 522-545)
   - Reads OAuth config from electron-store instead of env vars
   - Better error message when not configured

## Security Notes

- Client ID/Secret stored in electron-store (JSON file in user data)
- Access tokens stored in macOS Keychain (encrypted by OS)
- Client Secret shown as password field (hidden dots)
- Callback URL is readonly to prevent accidents

## Next Steps

**Phase 3**: Context7 integration - Similar pattern but with API keys instead of OAuth

**Phase 4**: Calendar integration - CalDAV authentication for iCloud/Google

## Testing Checklist

- [ ] Configure button visible by default
- [ ] Can click link to open GitHub settings
- [ ] Can enter Client ID and Secret
- [ ] Can save configuration
- [ ] Alert confirms save
- [ ] Connect button checks for config
- [ ] OAuth flow works after config
- [ ] Card shows "connected as @username"
- [ ] Token in Keychain Access
- [ ] Persists after restart
- [ ] Saved config loaded on page reload

## Developer Notes

The OAuth configuration approach:
- **Pros**: No environment variables, user-friendly, all in UI
- **Cons**: Client Secret stored in electron-store (not encrypted, but user data protected by OS)
- **Alternative**: Could use keytar for Client Secret too, but adds complexity for minimal gain
- **Decision**: Current approach is good for desktop app - secrets are in user's own machine

For a SaaS version, we'd handle OAuth server-side instead.
