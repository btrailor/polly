/**
 * focus-trap.js
 *
 * Reusable focus-trap utility for modals and dialogs.
 *
 * Usage:
 *   const cleanup = trapFocus(containerElement);
 *   // ... when modal closes:
 *   cleanup();
 */

const FOCUSABLE_SELECTORS = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ');

/**
 * Trap keyboard focus within `container`.
 * Tab/Shift+Tab wrap around within the container.
 * Escape key calls the optional `onEscape` callback.
 *
 * @param {HTMLElement} container - The element to trap focus within.
 * @param {object} [options]
 * @param {Function} [options.onEscape] - Called when Escape is pressed.
 * @param {HTMLElement} [options.returnFocusTo] - Element to return focus to on cleanup.
 * @returns {Function} cleanup - Call this to remove the trap and restore focus.
 */
function trapFocus(container, options = {}) {
  const { onEscape, returnFocusTo } = options;

  function getFocusable() {
    return Array.from(container.querySelectorAll(FOCUSABLE_SELECTORS)).filter(
      (el) => !el.closest('[hidden]') && el.offsetParent !== null
    );
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      if (typeof onEscape === 'function') onEscape();
      return;
    }

    if (e.key !== 'Tab') return;

    const focusable = getFocusable();
    if (!focusable.length) {
      e.preventDefault();
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement;

    if (e.shiftKey) {
      // Shift+Tab: if on first element, wrap to last
      if (active === first || !container.contains(active)) {
        e.preventDefault();
        last.focus();
      }
    } else {
      // Tab: if on last element, wrap to first
      if (active === last || !container.contains(active)) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  // Focus the first focusable element inside the container
  const focusable = getFocusable();
  if (focusable.length) {
    // Small delay to allow CSS transitions to complete
    setTimeout(() => focusable[0].focus(), 50);
  }

  document.addEventListener('keydown', handleKeydown);

  return function cleanup() {
    document.removeEventListener('keydown', handleKeydown);
    if (returnFocusTo && typeof returnFocusTo.focus === 'function') {
      returnFocusTo.focus();
    }
  };
}

// Expose globally (matches the singleton pattern used in this app)
window.trapFocus = trapFocus;
