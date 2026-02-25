# Design: Accessibility Overhaul

## Architecture Impact

No new subsystems. This is a systematic enhancement of existing components and styles.

### 1. Focus Management System

**Replace all `outline: none` with `:focus-visible` indicators:**

```css
/* Remove all existing outline: none declarations */
/* Add global focus-visible style */
:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* For elements where outline doesn't work well (e.g., rounded buttons) */
.btn:focus-visible,
.nav-item:focus-visible,
.ribbon-item:focus-visible {
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--accent-primary);
}

/* Reset for elements that should not show focus ring on mouse click */
:focus:not(:focus-visible) {
  outline: none;
}
```

**Focus trapping utility:**

Create a reusable `trapFocus(container)` utility function:

```js
// electron-app/src/renderer/utils/focus-trap.js
function trapFocus(container) {
  const focusableSelectors = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const focusableElements = container.querySelectorAll(focusableSelectors);
  const first = focusableElements[0];
  const last = focusableElements[focusableElements.length - 1];

  function handleKeydown(e) {
    if (e.key !== 'Tab') return;
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  container.addEventListener('keydown', handleKeydown);
  return () => container.removeEventListener('keydown', handleKeydown);
}
```

Apply to: `ConfirmDialog`, rename modal, category modal, API key modal, template gallery, preview modal, question form, package approval dialog.

### 2. ARIA Landmark Roles

Add semantic roles to the app shell in `index.html`:

```html
<!-- Navigation ribbon -->
<div class="ribbon" role="navigation" aria-label="Main navigation">
  <button class="ribbon-item" aria-label="Dashboard" aria-current="page">...</button>
  ...
</div>

<!-- Left sidebar -->
<aside class="left-sidebar" role="complementary" aria-label="Sidebar">
  ...
</aside>

<!-- Main content area -->
<main class="main-content" role="main" aria-label="Content">
  ...
</main>

<!-- Chat panel -->
<aside class="chat-panel" role="complementary" aria-label="Chat">
  ...
</aside>
```

### 3. Dynamic Content Announcements

**Toast notifications:**
```html
<div id="polly-toast-container" role="status" aria-live="polite" aria-atomic="false">
  <!-- toasts injected here -->
</div>
```

**Chat message area:**
```html
<div class="chat-messages" role="log" aria-live="polite" aria-label="Chat messages">
  <!-- messages injected here -->
</div>
```

**Loading states:**
```html
<div class="loading" role="status" aria-live="polite">
  <div class="loading-spinner" aria-hidden="true"></div>
  <span>Loading dashboard...</span>
</div>
```

### 4. Keyboard Navigation for Lists

**Conversation list — roving tabindex pattern:**

```js
// Only the active/focused item has tabindex="0", others have tabindex="-1"
// Arrow keys move focus, Enter/Space activates
function setupListKeyboardNav(container, itemSelector) {
  const items = () => container.querySelectorAll(itemSelector);
  let currentIndex = 0;

  container.addEventListener('keydown', (e) => {
    const allItems = items();
    if (!allItems.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      currentIndex = Math.min(currentIndex + 1, allItems.length - 1);
      allItems[currentIndex].focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      currentIndex = Math.max(currentIndex - 1, 0);
      allItems[currentIndex].focus();
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      allItems[currentIndex].click();
    }
  });
}
```

Apply to: conversation list, ribbon items, sidebar nav items, notes list, patterns list.

### 5. Icon Button Labels

All icon-only buttons must have `aria-label`:

```html
<!-- Currently -->
<button onclick="createNewConversation()"><i data-lucide="plus"></i></button>

<!-- Target -->
<button onclick="createNewConversation()" aria-label="New conversation">
  <i data-lucide="plus" aria-hidden="true"></i>
</button>
```

All Lucide `<i>` icons that are decorative should have `aria-hidden="true"`. Icons that are the sole content of a button need an `aria-label` on the parent button instead.

### 6. Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .glitch-effect,
  .glitch-box,
  .scan-line {
    display: none !important;
  }

  .loading-spinner {
    animation: none;
    /* Show a static indicator instead */
    border-color: var(--accent-primary);
    border-top-color: transparent;
  }
}
```

### 7. Color Contrast Fixes

| Token | Current | Proposed | New Ratio |
|-------|---------|----------|-----------|
| `--text-muted` | `#606060` | `#8a8a8a` | ~4.6:1 (passes AA) |
| `--text-secondary` | `#808080` | `#999999` | ~5.6:1 (passes AA at all sizes) |

These changes are subtle — the visual hierarchy is preserved (muted < secondary < primary) while meeting contrast requirements.

### 8. Skip-to-Content Link

```html
<!-- First element inside <body> -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 10000;
  padding: 8px 16px;
  background: var(--accent-primary);
  color: var(--bg-primary);
  font-weight: bold;
}
.skip-link:focus {
  top: 0;
}
```

### 9. Modal Accessibility Pattern

All modals should follow this pattern:

```html
<div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title" aria-describedby="modal-desc">
  <div class="modal-content">
    <h2 id="modal-title">Modal Title</h2>
    <p id="modal-desc">Description text</p>
    <!-- focusable content -->
    <button>Cancel</button>
    <button>Confirm</button>
  </div>
</div>
```

Requirements:
- `role="dialog"` + `aria-modal="true"`
- `aria-labelledby` pointing to the title
- Focus trapped within modal
- Escape to close
- Focus restored to trigger element on close
- Body scroll locked

## Files Affected

| File | Changes |
|------|---------|
| `index.html` | Add landmark roles, `aria-label` to navigation, skip-link, `id="main-content"` |
| `styles/main.css` | Remove `outline: none` (26 instances), add `:focus-visible` styles, add reduced-motion query, fix contrast variables, add skip-link styles |
| `styles/notes.css` | Remove `outline: none`, add `:focus-visible` |
| `styles/persona-ui.css` | Remove `outline: none`, add `:focus-visible` |
| `styles/persona-switch-dialog.css` | Add `role="dialog"` styles, focus indicator |
| `styles/template-gallery.css` | Focus indicator for gallery items |
| `styles/glitch-effects.css` | Wrap in `@media not (prefers-reduced-motion: reduce)` |
| `app.js` | Add `aria-label` to dynamically created buttons, add roving tabindex to lists, add `aria-live` to dynamic regions, add `aria-current="page"` to active nav item |
| `notes-manager.js` | Add `aria-label` to note action buttons, keyboard nav for note list |
| `api-keys-manager.js` | Add `role="dialog"` to modal, focus trap, `aria-label` on buttons |
| `components/confirm-dialog.js` | Built with full accessibility from the start (see ux-custom-dialogs change) |
| `components/question-form.js` | Add `role="dialog"`, `aria-label` to radio buttons, focus trap |
| `components/preview-modal.js` | Add `role="dialog"`, focus trap, `aria-label` on tabs |
| `components/template-gallery.js` | Add `role="dialog"`, keyboard nav for gallery grid, focus trap |
| `components/package-approval-dialog.js` | Add `role="dialog"`, focus trap |
| New: `utils/focus-trap.js` | Reusable focus trap utility |
