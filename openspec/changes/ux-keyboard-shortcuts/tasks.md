# Tasks: Keyboard Shortcut Discoverability

---

## Phase 1: Fix Existing Issues

### 1.1 Fix Cmd+B conflict

- [ ] Remove duplicate `Cmd+B` handler in the input-focused block (`app.js:2676-2679`)
- [ ] Ensure `Cmd+B` always calls `toggleLeftSidebar()` regardless of focus context
- [ ] Test: focus chat input → press Cmd+B → left sidebar toggles (not conversations sidebar)

### 1.2 Guard `/` key handler

- [ ] Add check for `document.activeElement` tag name and role before triggering
- [ ] Skip if focused on button, link, or other interactive element
- [ ] Test: focus a button → press `/` → nothing happens (key passes through normally)

---

## Phase 2: Shortcut Registry

### 2.1 Create shortcut registry

- [ ] Create `electron-app/src/renderer/utils/shortcut-registry.js`
- [ ] Define all shortcuts with: keys, action description, handler, category
- [ ] Expose as `window.ShortcutRegistry`
- [ ] Register in `index.html`

### 2.2 Add view-switching shortcuts

- [ ] Add `Cmd+1` through `Cmd+6` (or more) for direct view navigation
- [ ] Map to: Dashboard, Chat, Notes, Knowledge, Patterns, Settings
- [ ] Add handlers in the keydown event listener
- [ ] Test: `Cmd+3` from any view → navigates to Notes

---

## Phase 3: Shortcut Help Panel

### 3.1 Create shortcut panel component

- [ ] Create `components/shortcut-panel.js`
- [ ] Renders all shortcuts from the registry, grouped by category
- [ ] Modal/overlay with dark theme styling
- [ ] `role="dialog"`, `aria-modal="true"`, focus trapped, Escape to close

### 3.2 Create shortcut panel styles

- [ ] Create `components/shortcut-panel.css`
- [ ] Clean two-column layout: shortcut key on left, description on right
- [ ] Category headings
- [ ] Key badges with monospace font and subtle background
- [ ] Register in `index.html`

### 3.3 Wire Cmd+? trigger

- [ ] Add `Cmd+?` (Cmd+Shift+/) to open the shortcut panel
- [ ] Toggle: pressing again closes it
- [ ] Escape also closes it

---

## Phase 4: Button Tooltips

### 4.1 Add title attributes to ribbon items

- [ ] In `index.html`, add `title="Dashboard (⌘1)"` etc. to all ribbon buttons
- [ ] Include the keyboard shortcut in the title text

### 4.2 Add tooltips to dynamically created buttons

- [ ] In `app.js`, add `title` attributes to buttons created in JS (conversation actions, chat controls, etc.)
- [ ] For the send button: `title="Send message (⏎)"`
- [ ] For sidebar toggle buttons: include shortcut in title

### 4.3 Optional: Custom tooltip component

- [ ] If native `title` tooltips are too slow/ugly, implement a lightweight CSS-only tooltip
- [ ] Show on hover after 500ms delay, hide on mouse leave
- [ ] Include shortcut key in a distinct badge style

---

## Completion Criteria

- [ ] Cmd+B always toggles the left sidebar (no conflict)
- [ ] `/` key only triggers when appropriate (not on focused buttons)
- [ ] Cmd+? opens a keyboard shortcut help panel
- [ ] Cmd+1 through Cmd+6 navigate between views
- [ ] All ribbon buttons show tooltips with keyboard shortcuts
- [ ] Shortcut help panel is accessible (dialog role, focus trap, Escape to close)
- [ ] All shortcuts are defined in a central registry
