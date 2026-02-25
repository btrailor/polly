# Tasks: Accessibility Overhaul

Ordered by impact and dependency. Foundation (focus, ARIA landmarks) first, then component-level work.

---

## Phase 1: Focus Indicators (Foundation)

### 1.1 Remove all outline: none declarations

- [ ] Audit `main.css` for all `outline: none` (26 instances) — remove each one
- [ ] Audit `notes.css` for `outline: none` — remove
- [ ] Audit `persona-ui.css` for `outline: none` — remove
- [ ] Audit `persona-switch-dialog.css`, `template-gallery.css`, `curriculum.css` — remove any `outline: none`
- [ ] Audit component CSS files (`mental-models-editor.css`, `confirm-dialog.css`) — remove any `outline: none`

### 1.2 Add :focus-visible styles

- [ ] Add global `:focus-visible` rule in `main.css`: `outline: 2px solid var(--accent-primary); outline-offset: 2px`
- [ ] Add `:focus:not(:focus-visible) { outline: none; }` to suppress focus ring on mouse clicks
- [ ] Add `box-shadow` variant for rounded elements (buttons, nav items, ribbon items)
- [ ] Add `:focus-visible` styles for inputs, textareas, selects (border-color change + subtle glow)
- [ ] Test: Tab through entire app — every interactive element should show a visible focus ring

### 1.3 Create focus-trap utility

- [ ] Create `electron-app/src/renderer/utils/focus-trap.js`
- [ ] Implement `trapFocus(container)` returning a cleanup function
- [ ] Handles Tab and Shift+Tab wrapping within container
- [ ] Queries all focusable elements dynamically (handles DOM changes within modal)
- [ ] Register script in `index.html`

---

## Phase 2: ARIA Landmarks and Semantic Structure

### 2.1 Add landmark roles to index.html

- [ ] Add `role="navigation" aria-label="Main navigation"` to `.ribbon`
- [ ] Add `role="complementary" aria-label="Sidebar"` to `.left-sidebar`
- [ ] Add `<main>` element or `role="main"` to `.main-content`, add `id="main-content"`
- [ ] Add `role="complementary" aria-label="Chat"` to `.chat-panel`
- [ ] Add `role="status" aria-live="polite"` to `#polly-toast-container`

### 2.2 Add skip-to-content link

- [ ] Add `<a href="#main-content" class="skip-link">Skip to main content</a>` as first child of `<body>`
- [ ] Add `.skip-link` CSS: visually hidden until focused, then positioned at top of viewport
- [ ] Test: Tab from page load — skip link should appear and jump to main content

### 2.3 Add aria-current to active navigation

- [ ] In `showView()` function in `app.js`, set `aria-current="page"` on the active ribbon item
- [ ] Remove `aria-current` from previously active item
- [ ] Apply the same pattern to sidebar nav items if applicable

---

## Phase 3: Dynamic Content Announcements

### 3.1 Toast notification aria-live

- [ ] Add `role="status" aria-live="polite" aria-atomic="false"` to the toast container element
- [ ] Ensure new toast messages are announced by screen readers when they appear
- [ ] Test with macOS VoiceOver: trigger a toast → should be announced

### 3.2 Chat messages aria-live

- [ ] Add `role="log" aria-live="polite" aria-label="Chat messages"` to the chat messages container
- [ ] New messages should be announced automatically
- [ ] Typing indicator should have `aria-label="Assistant is typing"` and `role="status"`

### 3.3 Loading state announcements

- [ ] All loading indicators should have `role="status" aria-live="polite"`
- [ ] Spinner icons should have `aria-hidden="true"`
- [ ] Accompanying text ("Loading dashboard...") serves as the announced content

---

## Phase 4: Icon Button Labels

### 4.1 Audit and label all icon-only buttons in index.html

- [ ] Find all `<button>` elements with only an `<i data-lucide="...">` child and no text
- [ ] Add `aria-label` describing the action (e.g., "New conversation", "Toggle sidebar", "Close")
- [ ] Add `aria-hidden="true"` to all decorative `<i data-lucide>` icons

### 4.2 Label dynamically created buttons in app.js

- [ ] In conversation list rendering: add `aria-label` to star, menu, delete buttons
- [ ] In chat area: add `aria-label` to send, stop, attachment buttons
- [ ] In view headers: add `aria-label` to action buttons (refresh, export, etc.)
- [ ] Search for `createElement('button')` and `<button` in innerHTML assignments — ensure all have labels

### 4.3 Label buttons in component files

- [ ] `notes-manager.js`: label edit, delete, save, cancel buttons
- [ ] `api-keys-manager.js`: label test, delete, add buttons
- [ ] All 7 component files in `components/`: audit and label icon buttons

---

## Phase 5: Keyboard Navigation for Lists

### 5.1 Implement roving tabindex utility

- [ ] Create `setupListKeyboardNav(container, itemSelector, options)` utility
- [ ] Support ArrowUp/ArrowDown for vertical lists, ArrowLeft/ArrowRight for horizontal (ribbon)
- [ ] Enter/Space to activate (click) the focused item
- [ ] Home/End to jump to first/last item
- [ ] Maintain `tabindex="0"` on focused item, `tabindex="-1"` on others

### 5.2 Apply to conversation list

- [ ] Conversation items get `tabindex` attributes
- [ ] ArrowUp/ArrowDown navigates between conversations
- [ ] Enter switches to the focused conversation
- [ ] Delete key opens delete confirmation for focused conversation (stretch)

### 5.3 Apply to ribbon navigation

- [ ] Ribbon items get roving tabindex
- [ ] ArrowUp/ArrowDown navigates between ribbon items (vertical ribbon)
- [ ] Enter/Space activates the navigation

### 5.4 Apply to sidebar nav items

- [ ] Settings tabs, notes list, patterns list — all get keyboard nav
- [ ] Arrow keys move focus, Enter activates

---

## Phase 6: Modal Accessibility

### 6.1 Add dialog roles to all existing modals

- [ ] Rename modal in `app.js`: add `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- [ ] Category modal in `app.js`: same treatment
- [ ] Agent creation modal in `app.js`: same treatment
- [ ] API key modal in `api-keys-manager.js`: same treatment
- [ ] All 7 component modals: add dialog roles

### 6.2 Apply focus trap to all modals

- [ ] Use `trapFocus()` utility on every modal open
- [ ] Clean up trap on every modal close
- [ ] Ensure Escape key closes all modals
- [ ] Restore focus to the trigger element on close

---

## Phase 7: Reduced Motion and Color Contrast

### 7.1 Add prefers-reduced-motion support

- [ ] Add `@media (prefers-reduced-motion: reduce)` block in `main.css`
- [ ] Disable all `animation` and `transition` properties (set duration to near-zero)
- [ ] Hide glitch effects entirely (`.glitch-effect { display: none }`)
- [ ] Wrap glitch-effects.css content in `@media not (prefers-reduced-motion: reduce)` or add the reduce override
- [ ] Ensure loading spinners show a static visual indicator when animation is disabled
- [ ] Test: enable "Reduce motion" in macOS System Preferences → verify no animations play

### 7.2 Fix color contrast

- [ ] Change `--text-muted` from `#606060` to `#8a8a8a` (achieves ~4.6:1 ratio)
- [ ] Change `--text-secondary` from `#808080` to `#999999` (achieves ~5.6:1 ratio)
- [ ] Audit any hardcoded color values that are used for text on dark backgrounds
- [ ] Verify `--accent-primary` (`#f0903b`) on dark backgrounds maintains 4.5:1+ for text usage
- [ ] Test: use browser DevTools accessibility audit to verify contrast ratios

---

## Completion Criteria

- [ ] Zero `outline: none` declarations remain in CSS
- [ ] Every interactive element shows a visible focus ring when navigated via keyboard
- [ ] All landmark roles are present: navigation, main, complementary, status
- [ ] All icon-only buttons have `aria-label` attributes
- [ ] All modals have `role="dialog"`, `aria-modal="true"`, and focus trapping
- [ ] Toast notifications and chat messages have `aria-live` regions
- [ ] Conversation list, ribbon, and sidebar nav are keyboard-navigable with arrow keys
- [ ] `prefers-reduced-motion: reduce` disables all animations
- [ ] All text meets WCAG 2.1 AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- [ ] Skip-to-content link works on first Tab press
- [ ] macOS VoiceOver can navigate the core flows: open app → navigate ribbon → switch views → send chat message
