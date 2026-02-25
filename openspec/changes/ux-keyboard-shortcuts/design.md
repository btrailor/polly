# Design: Keyboard Shortcut Discoverability

## Architecture Impact

### 1. Shortcut Registry

Centralize all shortcut definitions in a registry for consistency and the help panel:

```js
// electron-app/src/renderer/utils/shortcut-registry.js

const SHORTCUTS = [
  { keys: 'Cmd+B', action: 'Toggle left sidebar', handler: toggleLeftSidebar, category: 'Navigation' },
  { keys: 'Cmd+/', action: 'Toggle chat panel', handler: toggleRightSidebar, category: 'Navigation' },
  { keys: 'Cmd+N', action: 'New conversation', handler: createNewConversation, category: 'Chat' },
  { keys: 'Cmd+L', action: 'Focus search', handler: focusSearch, category: 'Navigation' },
  { keys: 'Cmd+1', action: 'Dashboard', handler: () => showView('dashboard'), category: 'Views' },
  { keys: 'Cmd+2', action: 'Chat', handler: () => showView('chat'), category: 'Views' },
  { keys: 'Cmd+3', action: 'Notes', handler: () => showView('notes'), category: 'Views' },
  { keys: 'Cmd+4', action: 'Knowledge', handler: () => showView('knowledge'), category: 'Views' },
  { keys: 'Cmd+5', action: 'Patterns', handler: () => showView('patterns'), category: 'Views' },
  { keys: 'Cmd+6', action: 'Settings', handler: () => showView('settings'), category: 'Views' },
  { keys: 'Cmd+?', action: 'Show keyboard shortcuts', handler: toggleShortcutPanel, category: 'Help' },
  { keys: 'Escape', action: 'Close panel/overlay', handler: closeActiveOverlay, category: 'General' },
];
```

### 2. Keyboard Shortcut Help Panel

A modal or slide-in panel listing all shortcuts grouped by category:

```
┌─────────────────────────────────┐
│  > keyboard shortcuts           │
│                                 │
│  Navigation                     │
│  ⌘B   Toggle left sidebar      │
│  ⌘/   Toggle chat panel        │
│  ⌘L   Focus search             │
│                                 │
│  Views                          │
│  ⌘1   Dashboard                │
│  ⌘2   Chat                     │
│  ⌘3   Notes                    │
│  ...                            │
│                                 │
│  Chat                           │
│  ⌘N   New conversation         │
│  ⌘⏎   Send message             │
│  ⇧⌘⏎  New line in input        │
│  /    Slash commands            │
│                                 │
│  General                        │
│  Esc  Close panel/overlay       │
│  ⌘?   Show this panel          │
└─────────────────────────────────┘
```

- Triggered by `Cmd+?` (Cmd+Shift+/)
- Closes on Escape or clicking outside
- Accessible: `role="dialog"`, focus trapped

### 3. Button Tooltips with Shortcuts

Add native `title` attributes (or custom tooltips) to icon buttons:

```html
<button class="ribbon-item" aria-label="Dashboard" title="Dashboard (⌘1)">
  <i data-lucide="layout-dashboard" aria-hidden="true"></i>
</button>
```

For a more polished experience, implement custom tooltips (CSS-only or minimal JS) that appear on hover with the shortcut key displayed in a distinct style:

```css
.tooltip-shortcut {
  color: var(--text-muted);
  font-size: 11px;
  margin-left: 8px;
  background: var(--bg-tertiary);
  padding: 1px 4px;
  border-radius: 3px;
}
```

### 4. Fix Cmd+B Conflict

**Current:** Two different functions handle `Cmd+B`:
- `app.js:2444`: `toggleLeftSidebar()` (general context)
- `app.js:2676`: `toggleConversationsSidebar()` (input focused context)

**Fix:** Consolidate to one function. `Cmd+B` should always toggle the left sidebar regardless of focus context. Remove the duplicate handler in the input-focused block.

### 5. Guard `/` Key

**Current:** `app.js:2709-2714` listens for `/` and focuses the query input on chat view. No check for whether focus is on a non-input interactive element.

**Fix:** Only trigger when `document.activeElement` is `document.body` or a non-interactive element. Skip if focus is on a button, link, or other interactive element.

```js
if (e.key === '/' && currentView === 'chat' &&
    !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) &&
    !document.activeElement.isContentEditable &&
    document.activeElement.getAttribute('role') !== 'button') {
  e.preventDefault();
  document.getElementById('query-input').focus();
}
```

## Files Affected

| File | Changes |
|------|---------|
| New: `utils/shortcut-registry.js` | Centralized shortcut definitions |
| New: `components/shortcut-panel.js` | Keyboard shortcut help modal |
| New: `components/shortcut-panel.css` | Help panel styles |
| `app.js` | Fix Cmd+B conflict, guard `/` key, add Cmd+1-9 view shortcuts, add Cmd+? trigger, add tooltips to dynamically created buttons |
| `index.html` | Add `title` attributes to ribbon items, register new scripts |
