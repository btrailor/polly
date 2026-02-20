/**
 * ConfirmDialog Component
 *
 * Promise-based themed confirmation dialog that replaces native confirm().
 * Matches the app's dark theme using CSS variables from main.css.
 *
 * Usage:
 *   const confirmed = await ConfirmDialog.show({
 *     title: 'Delete conversation',
 *     message: 'Are you sure? This cannot be undone.',
 *     confirmLabel: 'Delete',   // default: 'Confirm'
 *     cancelLabel: 'Cancel',    // default: 'Cancel'
 *     destructive: true,        // red confirm button
 *     icon: 'trash-2',          // optional Lucide icon name
 *   });
 *   if (confirmed) { ... }
 */

const ConfirmDialog = (() => {
  let _container = null;
  let _resolvePromise = null;

  // ── DOM bootstrap ────────────────────────────────────────────────────────
  function _init() {
    if (_container) return;

    _container = document.createElement('div');
    _container.id = 'confirm-dialog-container';
    _container.setAttribute('role', 'dialog');
    _container.setAttribute('aria-modal', 'true');
    _container.setAttribute('aria-labelledby', 'confirm-dialog-title');
    _container.setAttribute('aria-describedby', 'confirm-dialog-message');
    _container.className = 'confirm-dialog-container hidden';
    _container.innerHTML = `
      <div class="confirm-dialog-overlay"></div>
      <div class="confirm-dialog-panel">
        <div class="confirm-dialog-header">
          <span class="confirm-dialog-icon" id="confirm-dialog-icon" aria-hidden="true"></span>
          <h3 class="confirm-dialog-title" id="confirm-dialog-title"></h3>
        </div>
        <p class="confirm-dialog-message" id="confirm-dialog-message"></p>
        <div class="confirm-dialog-actions">
          <button class="confirm-dialog-btn confirm-dialog-cancel" id="confirm-dialog-cancel"></button>
          <button class="confirm-dialog-btn confirm-dialog-confirm" id="confirm-dialog-confirm"></button>
        </div>
      </div>
    `;

    document.body.appendChild(_container);

    // Overlay click → cancel
    _container.querySelector('.confirm-dialog-overlay').addEventListener('click', () => _resolve(false));

    // Button clicks
    _container.querySelector('#confirm-dialog-cancel').addEventListener('click', () => _resolve(false));
    _container.querySelector('#confirm-dialog-confirm').addEventListener('click', () => _resolve(true));

    // Keyboard
    _container.addEventListener('keydown', _handleKeydown);
  }

  // ── Keyboard handler ─────────────────────────────────────────────────────
  function _handleKeydown(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      _resolve(false);
      return;
    }

    if (e.key === 'Enter') {
      // Only trigger confirm if focus is not explicitly on Cancel
      if (document.activeElement !== _container.querySelector('#confirm-dialog-cancel')) {
        e.preventDefault();
        _resolve(true);
      }
      return;
    }

    // Focus trap: Tab cycles within Cancel and Confirm
    if (e.key === 'Tab') {
      const cancelBtn = _container.querySelector('#confirm-dialog-cancel');
      const confirmBtn = _container.querySelector('#confirm-dialog-confirm');
      if (e.shiftKey) {
        if (document.activeElement === cancelBtn) {
          e.preventDefault();
          confirmBtn.focus();
        }
      } else {
        if (document.activeElement === confirmBtn) {
          e.preventDefault();
          cancelBtn.focus();
        }
      }
    }
  }

  // ── Resolve and close ────────────────────────────────────────────────────
  function _resolve(value) {
    if (!_resolvePromise) return;

    const panel = _container.querySelector('.confirm-dialog-panel');
    panel.classList.add('confirm-dialog-exit');

    setTimeout(() => {
      _container.classList.add('hidden');
      panel.classList.remove('confirm-dialog-exit');
      document.body.classList.remove('confirm-dialog-open');
      document.removeEventListener('keydown', _trapOuterKeydown);

      const cb = _resolvePromise;
      _resolvePromise = null;
      cb(value);
    }, 100);
  }

  // Prevent keyboard interactions outside the dialog while open
  function _trapOuterKeydown(e) {
    if (!_container || _container.classList.contains('hidden')) return;
    if (!_container.contains(e.target)) {
      e.stopImmediatePropagation();
    }
  }

  // ── Public API ───────────────────────────────────────────────────────────
  /**
   * Show a confirmation dialog.
   * @param {object} options
   * @param {string} options.title           - Dialog heading
   * @param {string} options.message         - Body text
   * @param {string} [options.confirmLabel]  - Confirm button label (default: 'Confirm')
   * @param {string} [options.cancelLabel]   - Cancel button label (default: 'Cancel')
   * @param {boolean} [options.destructive]  - Red confirm button styling
   * @param {string} [options.icon]          - Lucide icon name (e.g. 'trash-2')
   * @returns {Promise<boolean>}
   */
  function show({
    title = 'Are you sure?',
    message = '',
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    destructive = false,
    icon = null,
  } = {}) {
    _init();

    // Populate content
    const titleEl = _container.querySelector('#confirm-dialog-title');
    const messageEl = _container.querySelector('#confirm-dialog-message');
    const iconEl = _container.querySelector('#confirm-dialog-icon');
    const cancelBtn = _container.querySelector('#confirm-dialog-cancel');
    const confirmBtn = _container.querySelector('#confirm-dialog-confirm');

    titleEl.textContent = title;
    messageEl.textContent = message;
    cancelBtn.textContent = cancelLabel;
    confirmBtn.textContent = confirmLabel;

    // Icon
    if (icon) {
      iconEl.innerHTML = `<i data-lucide="${icon}" style="width:18px;height:18px;"></i>`;
      iconEl.style.display = 'inline-flex';
    } else if (destructive) {
      iconEl.innerHTML = `<i data-lucide="alert-triangle" style="width:18px;height:18px;"></i>`;
      iconEl.style.display = 'inline-flex';
    } else {
      iconEl.innerHTML = '';
      iconEl.style.display = 'none';
    }

    // Destructive styling
    if (destructive) {
      confirmBtn.classList.add('confirm-dialog-confirm--destructive');
      iconEl.classList.add('confirm-dialog-icon--destructive');
    } else {
      confirmBtn.classList.remove('confirm-dialog-confirm--destructive');
      iconEl.classList.remove('confirm-dialog-icon--destructive');
    }

    // Show
    _container.classList.remove('hidden');
    document.body.classList.add('confirm-dialog-open');
    document.addEventListener('keydown', _trapOuterKeydown, true);

    // Render Lucide icons if available
    if (window.lucide) {
      try { lucide.createIcons({ nodes: [iconEl] }); } catch (_) {}
    }

    // Default focus on Cancel (safe default)
    requestAnimationFrame(() => cancelBtn.focus());

    return new Promise((resolve) => {
      _resolvePromise = resolve;
    });
  }

  return { show };
})();

window.ConfirmDialog = ConfirmDialog;
