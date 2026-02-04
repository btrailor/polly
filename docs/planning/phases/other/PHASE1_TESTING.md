# Phase 1: UI Foundation - Testing Guide

## ✅ Implementation Complete

All Phase 1 code changes have been successfully implemented:

1. **HTML Structure Updated** (`electron-app/src/renderer/index.html`)
   - Added tabbed navigation (General, Integrations, Advanced)
   - Created 4 integration cards (GitHub, Context7, Calendar, macOS Control)
   - Reorganized settings into logical tabs

2. **CSS Styling Added** (`electron-app/src/renderer/styles/main.css`)
   - Brutalist tab design with active state underlines
   - Integration card hover effects (translate + box-shadow)
   - Expandable configuration panels
   - Responsive design for mobile/tablet

3. **JavaScript Added** (`electron-app/src/renderer/app.js`)
   - Tab switching functionality
   - Integration config panel toggle
   - Placeholder connect buttons
   - Helper functions for status updates

## 🧪 Manual Testing Checklist

### To Run the App:

```bash
cd electron-app
npm run dev
```

### Test 1: Tab Navigation
- [ ] Open Polly app
- [ ] Navigate to Settings view (bottom of sidebar)
- [ ] Click "general" tab → verify Paths and Model Routing sections show
- [ ] Click "integrations" tab → verify 4 integration cards appear
- [ ] Click "advanced" tab → verify Server and OpenCode Integration sections show
- [ ] Verify active tab has underline and border
- [ ] Verify smooth transitions between tabs

### Test 2: Integration Cards (Integrations Tab)
- [ ] Verify GitHub card displays with GitHub icon
- [ ] Verify Context7 card displays with book icon
- [ ] Verify Calendar card displays with calendar icon
- [ ] Verify macOS Control card displays with monitor icon
- [ ] Verify all status dots are gray (disconnected)
- [ ] Verify "connect" / "add account" / "enable" buttons are visible
- [ ] Verify "sync now" and "configure" buttons are hidden

### Test 3: Integration Card Interactions
- [ ] Click "configure" on GitHub card → verify panel expands with placeholder text
- [ ] Click "configure" again → verify panel collapses
- [ ] Click "connect" on GitHub → verify alert: "GitHub OAuth will be implemented in Phase 2"
- [ ] Click "connect" on Context7 → verify alert: "Context7 API key prompt will be implemented in Phase 3"
- [ ] Click "add account" on Calendar → verify alert: "Calendar account modal will be implemented in Phase 4"
- [ ] Click "enable" on macOS Control → verify alert: "macOS permissions will be implemented in Phase 9"

### Test 4: Card Hover Effects
- [ ] Hover over each integration card
- [ ] Verify card translates up-left (-2px, -2px)
- [ ] Verify box shadow appears (4px 4px 0)
- [ ] Verify smooth animation

### Test 5: General Tab (Existing Functionality)
- [ ] Click "Change" button for Obsidian Vault → verify file picker opens
- [ ] Click "+ Add" for Code Directories → verify directory picker opens
- [ ] Change "Default Mode" dropdown → verify selection works
- [ ] Enter API key → verify input accepts text
- [ ] Click "save settings" → verify alert shows "Settings saved!"

### Test 6: Advanced Tab
- [ ] Verify Port input shows "11436"
- [ ] Verify "Start server automatically" checkbox is checked
- [ ] Verify OpenCode API Key shows "polly-local-key"
- [ ] Click "Regenerate" → verify new key is generated and alert shows
- [ ] Verify new key starts with "polly-local-"

### Test 7: Footer Actions
- [ ] Click "save settings" → verify alert shows
- [ ] Click "reset setup" → verify confirmation dialog appears (existing functionality)

### Test 8: Responsive Design
- [ ] Resize window to < 900px width
- [ ] Verify integration cards stack vertically (single column)
- [ ] Verify tab labels hide, only icons remain
- [ ] Verify tabs become scrollable horizontally if needed
- [ ] Resize back to full width → verify grid returns to 2 columns

### Test 9: Visual Consistency
- [ ] Verify all text is lowercase
- [ ] Verify letter-spacing matches existing design
- [ ] Verify 2px solid borders throughout
- [ ] Verify monospace font (Courier New) everywhere
- [ ] Verify colors match domain colors (if any)
- [ ] Verify no rounded corners (border-radius: 0)

### Test 10: Browser Console
- [ ] Open DevTools (Cmd+Option+I)
- [ ] Check Console for JavaScript errors
- [ ] Verify Lucide icons render (no 404s)
- [ ] Verify no CSS warnings

## 🐛 Known Issues / Expected Behavior

1. **Placeholder Alerts**: All integration "connect" buttons show alerts - this is expected! Functionality will be added in Phases 2-10.

2. **Empty Config Panels**: Configuration panels show placeholder text - this is expected! Panels will be populated in later phases.

3. **Code Signing Warning**: The build warning about code signing is normal for development. You can ignore it.

## ✅ Success Criteria

Phase 1 is successful if:
- ✅ All three tabs are functional and clickable
- ✅ Tab navigation works smoothly
- ✅ All four integration cards display correctly
- ✅ Card hover effects work
- ✅ Config panels expand/collapse
- ✅ Existing settings functionality still works
- ✅ Brutalist design matches existing Polly aesthetic
- ✅ No JavaScript console errors

## 🚀 Next Steps

After Phase 1 testing is complete:

**Phase 2: Credential Storage** (Next)
- Install `keytar` for OS keychain storage
- Add IPC handlers for secure credentials
- Implement GitHub OAuth flow
- Test on macOS Keychain

**Phases 3-8**: Build actual integrations
**Phase 9**: macOS Control integration
**Phase 10**: OpenCode hook

## 📝 Notes

- **Backup files created**: `.backup` files in same directories
- **Restore command** (if needed): 
  ```bash
  cp electron-app/src/renderer/index.html.backup electron-app/src/renderer/index.html
  cp electron-app/src/renderer/styles/main.css.backup electron-app/src/renderer/styles/main.css
  cp electron-app/src/renderer/app.js.backup electron-app/src/renderer/app.js
  ```

## 🎨 Design Highlights

- **Tab Underlines**: 4px thick underline on active tab (brutalist style)
- **Card Shadows**: `4px 4px 0` offset shadow (no blur)
- **Status Dots**: Green with glow when connected, gray when disconnected
- **Animations**: Smooth 250ms transitions for all interactions
- **Grid Layout**: Auto-fills based on available width (min 400px per card)

---

**Ready to test?** Run `npm run dev` in the `electron-app` directory and go through the checklist above!
