# Reload and Restart Notes

## Backend (Python) code changes

The Polly Python server is started by Electron. To pick up backend code changes:

- **Quit and reopen Polly (Cmd+Q, then open again)** — Server is fully stopped on quit and restarted on next launch.
- **In dev: close the window (hide to tray), then click the tray icon to open again** — The backend is restarted when you open from the tray so the latest code is loaded.
- **Dashboard or tray: Stop Server, then Start Server** — Stop now waits for the process to exit; Start then runs a fresh server.

---

# How to See the Titlebar Button Changes

The CSS and JavaScript have been updated, but you need to force-reload to see the changes.

## Steps to Force Reload:

1. **Open the app** (if not already open)

2. **Open DevTools** (they should open automatically in dev mode, or press `Cmd+Option+I`)

3. **Clear localStorage** - In the DevTools Console tab, paste this and press Enter:

   ```javascript
   localStorage.removeItem("sidebar-left-collapsed");
   localStorage.removeItem("sidebar-right-collapsed");
   console.log("Storage cleared!");
   ```

4. **Hard Reload** - In DevTools, right-click the reload button and select "Empty Cache and Hard Reload"
   - OR press `Cmd+Shift+R`
   - OR in Console type: `location.reload(true)`

5. **If that doesn't work**, quit and restart:

   ```bash
   # Kill all Electron processes
   ps aux | grep -i electron | grep -v grep | awk '{print $2}' | xargs kill -9

   # Clear Electron cache
   rm -rf ~/Library/Application\ Support/polly/Cache
   rm -rf ~/Library/Application\ Support/polly/GPUCache

   # Restart
   cd /Users/brettgershon/polly/electron-app
   npm start
   ```

## What Should Change:

### Visual Changes:

- **Titlebar height:** 38px → 40px (traffic lights centered)
- **Toggle buttons:** 38×38px → 24×24px (small, subtle)
- **Button icons:** 16×16px → 14×14px
- **Button shape:** Square → Rounded (3px border-radius)
- **Hover color:** Brighter → Softer (#b4b4b4)

### Functional Changes:

- Left sidebar should toggle on/off with both:
  - Titlebar button (top left)
  - Sidebar header button
  - Keyboard: `Cmd+B`
- Right sidebar should toggle with:
  - Titlebar button (top right)
  - Sidebar header button
  - Keyboard: `Cmd+/`

## Debugging:

If left sidebar still won't close, check Console for these debug messages:

```
[DEBUG] toggleLeftSidebar called
[DEBUG] threeColumnLayout exists: true
[DEBUG] Current state - isCollapsed: false
[DEBUG] Classes before toggle: three-column-layout
[DEBUG] Classes after toggle: three-column-layout left-collapsed
```

## Files Changed:

1. `styles/main.css` - Lines 97-165 (titlebar & button styling)
2. `styles/ribbon.css` - Lines 9, 138 (positioning for 40px titlebar)
3. `app.js` - Lines 973-1035 (button position logic + debug logging)
