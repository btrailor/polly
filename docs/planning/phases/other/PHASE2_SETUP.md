# Phase 2: Secure Credential Storage & GitHub OAuth

## Overview

Phase 2 implements secure credential storage using OS-native keychains and GitHub OAuth authentication.

## Implementation Summary

### Files Modified

1. **electron-app/src/main/main.js** (815 lines, +20 lines)
   - Added IPC handlers for keytar operations (lines 756-769)
   - Keytar functions already implemented (lines 477-639)

2. **electron-app/src/main/preload.js** (57→65 lines, +8 lines)
   - Exposed credential storage functions to renderer
   - Exposed GitHub OAuth function

3. **electron-app/src/renderer/app.js** (844→891 lines, +47 lines)
   - Updated GitHub connect button with OAuth flow (lines 798-836)
   - Added `restoreIntegrationStatus()` function (lines 799-816)
   - Modified DOMContentLoaded to restore integration status (line 891)

### Architecture

```
User clicks "Connect"
  ↓
Renderer (app.js) calls window.polly.githubOAuth()
  ↓
Preload (preload.js) invokes 'github-oauth' IPC
  ↓
Main (main.js) startGitHubOAuth() opens OAuth window
  ↓
User authorizes on GitHub
  ↓
GitHub redirects to localhost:3000/oauth/callback?code=...
  ↓
Main exchanges code for access_token
  ↓
Main stores token via keytar.setPassword('Polly', 'github_token', token)
  ↓
macOS Keychain stores credential securely
  ↓
Main returns {success: true, username: 'user123'}
  ↓
Renderer updates UI and stores username in electron-store
```

## Setup Instructions

### Step 1: Verify keytar Installation

Keytar should already be installed from Phase 2 prep:

```bash
cd electron-app
npm list keytar
```

If not installed:
```bash
npm install keytar
```

### Step 2: Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in the form:
   - **Application name**: `Polly`
   - **Homepage URL**: `http://localhost:3000`
   - **Application description**: `Edge-native personal AI assistant`
   - **Authorization callback URL**: `http://localhost:3000/oauth/callback`
4. Click **"Register application"**
5. On the next page, note your **Client ID**
6. Click **"Generate a new client secret"** and note the **Client Secret**

### Step 3: Set Environment Variables

Add these to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export GITHUB_CLIENT_ID="Iv1.abc123..."
export GITHUB_CLIENT_SECRET="gho_xyz789..."
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

**For Development Sessions**: You can also set them temporarily:

```bash
cd electron-app
GITHUB_CLIENT_ID="Iv1.abc123..." GITHUB_CLIENT_SECRET="gho_xyz789..." npm run dev
```

### Step 4: Test the OAuth Flow

1. Start the app:
   ```bash
   cd electron-app
   npm run dev
   ```

2. Navigate to **Settings → Integrations**

3. Click **"connect"** on the GitHub card

4. A browser window should open asking you to authorize Polly

5. After authorizing:
   - The window should close
   - The GitHub card should update to show "connected as @yourusername"
   - An alert should confirm the connection

### Step 5: Verify Credential Storage

Open **Keychain Access** on macOS:

1. Open `/Applications/Utilities/Keychain Access.app`
2. Search for **"Polly"**
3. You should see an entry named **"github_token"**
4. Double-click it to view details (password is hidden)

### Step 6: Test Persistence

1. Quit and restart the Polly app
2. Navigate to **Settings → Integrations**
3. The GitHub card should still show "connected as @yourusername"
4. This means the credential was successfully restored from the keychain

## OAuth Scopes

The GitHub OAuth flow requests these scopes:
- **`repo`**: Full control of private repositories (read/write)
- **`read:user`**: Read user profile data

These scopes are defined in `main.js:559`.

## Credential Account Names

All credentials are stored under the service name **"Polly"** with these account names:

| Integration | Account Name | Type |
|-------------|-------------|------|
| GitHub | `github_token` | OAuth access token |
| Context7 | `context7_api_key` | API key (Phase 3) |
| iCal | `ical_{account_name}_username` | Username (Phase 4) |
| iCal | `ical_{account_name}_password` | Password (Phase 4) |

## Security Notes

1. **OS-Native Storage**: Credentials are stored in macOS Keychain, which is encrypted and managed by the OS
2. **No Plaintext**: Tokens never stored in electron-store or files
3. **Process Isolation**: Only main process can access keytar (renderer cannot)
4. **Secure Communication**: IPC bridge ensures renderer uses main process for credential operations

## Troubleshooting

### OAuth Window Doesn't Open

**Error**: "GitHub OAuth not configured"

**Solution**: Make sure `GITHUB_CLIENT_ID` is set:
```bash
echo $GITHUB_CLIENT_ID
```

### OAuth Window Opens but Fails

**Error**: "No access token received from GitHub"

**Possible causes**:
1. `GITHUB_CLIENT_SECRET` not set or incorrect
2. Callback URL mismatch (must be exactly `http://localhost:3000/oauth/callback`)

**Solution**: Verify environment variables and GitHub OAuth app settings

### Keychain Access Denied

**Error**: "Failed to store credential"

**Solution**: Grant Polly access to Keychain:
1. Open Keychain Access
2. When prompted, click "Always Allow" for Polly

### Token Not Persisting

**Issue**: Connection status not restored after app restart

**Debug**:
1. Check if token is in Keychain (see Step 5 above)
2. Check if `github_username` is in electron-store:
   ```javascript
   // In DevTools Console:
   await window.polly.getStore('github_username')
   ```
3. Check console logs for errors during `restoreIntegrationStatus()`

### Network Errors

**Error**: "Failed to connect: timeout" or "Network request failed"

**Possible causes**:
1. GitHub is down
2. Firewall blocking requests
3. No internet connection

**Solution**: 
- Check https://www.githubstatus.com/
- Try connecting from browser
- Check network/firewall settings

## Testing Checklist

- [ ] OAuth window opens when clicking "connect"
- [ ] User can authorize on GitHub
- [ ] OAuth window closes after authorization
- [ ] GitHub card updates to show "connected as @username"
- [ ] Alert confirms successful connection
- [ ] Token appears in macOS Keychain under "Polly"
- [ ] Connection status persists after app restart
- [ ] Can disconnect (Phase 2.1 - not implemented yet)

## Next Steps: Phase 2.1 (Optional Enhancements)

Before moving to Phase 3 (Context7), consider these improvements:

1. **Disconnect Button**:
   - Add "disconnect" button to GitHub card config panel
   - Implement `window.polly.deleteCredential('github_token')`
   - Clear `github_username` from electron-store
   - Update card to show "not connected"

2. **Token Validation**:
   - Add function to validate token by calling GitHub API
   - Show error if token is invalid/expired
   - Prompt user to reconnect

3. **Better Error Handling**:
   - Show specific error messages for common failure modes
   - Add retry button for failed connections
   - Log detailed error info for debugging

4. **Loading States**:
   - Show spinner while OAuth is in progress
   - Disable other integration buttons during OAuth
   - Show "verifying..." while checking token

## Files Reference

```
electron-app/
├── src/
│   ├── main/
│   │   ├── main.js          # IPC handlers (lines 756-769), OAuth flow (lines 524-639)
│   │   └── preload.js       # Exposed functions (lines 41-48)
│   └── renderer/
│       ├── app.js           # GitHub connect logic (lines 798-891)
│       ├── index.html       # Integration cards (GitHub ~line 495)
│       └── styles/main.css  # Integration styles (lines 1303+)
└── package.json             # keytar dependency

core/                        # Python backend (Phase 5)
interfaces/                  # FastAPI server (Phase 5)
```

## Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Electron App                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Renderer Process (app.js)                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │ User clicks "connect"                              │   │
│  │  ↓                                                  │   │
│  │ window.polly.githubOAuth()                         │   │
│  └────────────────────────────────────────────────────┘   │
│                         ↓ IPC                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Preload (preload.js)                               │   │
│  │ ipcRenderer.invoke('github-oauth')                 │   │
│  └────────────────────────────────────────────────────┘   │
│                         ↓ IPC                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Main Process (main.js)                             │   │
│  │ 1. Opens OAuth window (BrowserWindow)              │   │
│  │ 2. Listens for redirect with code                  │   │
│  │ 3. Exchanges code for token (fetch)                │   │
│  │ 4. Stores token (keytar.setPassword)               │   │
│  │ 5. Gets user info (GitHub API)                     │   │
│  │ 6. Returns {success, username}                     │   │
│  └────────────────────────────────────────────────────┘   │
│                         ↓                                   │
│                    ┌────────┐                              │
│                    │ keytar │                              │
│                    └────────┘                              │
│                         ↓                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
              ┌──────────────────────┐
              │  macOS Keychain      │
              │  Service: "Polly"    │
              │  Account: "github_   │
              │           token"     │
              │  Password: "gho_..." │
              └──────────────────────┘
```

## Code Examples

### Storing a Credential

```javascript
// From renderer
const result = await window.polly.setCredential('my_service_key', 'secret123');
if (result.success) {
  console.log('Credential stored securely');
}
```

### Retrieving a Credential

```javascript
// From renderer
const result = await window.polly.getCredential('my_service_key');
if (result.success && result.password) {
  console.log('Retrieved:', result.password);
}
```

### Deleting a Credential

```javascript
// From renderer
const result = await window.polly.deleteCredential('my_service_key');
if (result.success) {
  console.log('Credential deleted');
}
```

### Starting OAuth Flow

```javascript
// From renderer
const result = await window.polly.githubOAuth();
if (result.success) {
  console.log('Connected as:', result.username);
  console.log('Token:', result.token); // Available but not needed
}
```

## Environment Variable Summary

```bash
# Required for GitHub OAuth
export GITHUB_CLIENT_ID="Iv1.abc123..."        # From GitHub OAuth app
export GITHUB_CLIENT_SECRET="gho_xyz789..."    # From GitHub OAuth app

# Optional (already set by app)
# KEYTAR_SERVICE="Polly"                       # Service name for keychain
```

## Success Criteria

Phase 2 is complete when:

1. ✅ Keytar is installed and working
2. ✅ GitHub OAuth app is created and configured
3. ✅ Environment variables are set
4. ✅ User can click "connect" and authorize on GitHub
5. ✅ Token is stored in macOS Keychain
6. ✅ GitHub card shows "connected as @username"
7. ✅ Connection persists after app restart
8. ✅ Token can be retrieved by main process for API calls (Phase 5)

## Known Limitations

1. **No Disconnect**: User cannot disconnect once connected (Phase 2.1)
2. **No Token Refresh**: GitHub tokens don't expire, but no refresh logic exists
3. **No Multiple Accounts**: Only one GitHub account can be connected
4. **macOS Only**: Keytar works on Windows/Linux but untested
5. **No Token Usage**: Token stored but not used for API calls yet (Phase 5)

## Next: Phase 3 - Context7 Integration

Once Phase 2 is working, we'll implement:
- Context7 API key input modal
- Library search functionality
- "Add to Knowledge" button integration
- Similar credential storage pattern (API key instead of OAuth)
