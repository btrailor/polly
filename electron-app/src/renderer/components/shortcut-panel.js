/**
 * ShortcutPanel Component
 *
 * Modal overlay listing all keyboard shortcuts from ShortcutRegistry,
 * grouped by category. Triggered by Cmd+? or programmatically.
 *
 * Usage:
 *   ShortcutPanel.toggle();
 *   ShortcutPanel.show();
 *   ShortcutPanel.hide();
 */

const ShortcutPanel = (() => {
  let _container = null;

  // ── DOM bootstrap ──────────────────────────────────────────────────────
  function _init() {
    if (_container) return;

    _container = document.createElement('div');
    _container.id = 'shortcut-panel-container';
    _container.className = 'sp-container hidden';
    _container.setAttribute('role', 'dialog');
    _container.setAttribute('aria-modal', 'true');
    _container.setAttribute('aria-labelledby', 'sp-title');
    _container.innerHTML = `
      <div class="sp-overlay"></div>
      <div class="sp-panel">
        <div class="sp-header">
          <h3 class="sp-title" id="sp-title">Keyboard Shortcuts</h3>
          <span class="sp-hint">Press <kbd>Esc</kbd> or <kbd>⌘?</kbd> to close</span>
          <button class="sp-close btn-icon" aria-label="Close shortcuts panel">
            <i data-lucide="x" style="width:16px;height:16px;"></i>
          </button>
        </div>
        <div class="sp-body" id="sp-body"></div>
      </div>
    `;

    document.body.appendChild(_container);

    _container.querySelector('.sp-overlay').addEventListener('click', hide);
    _container.querySelector('.sp-close').addEventListener('click', hide);

    _container.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { e.preventDefault(); hide(); }
      // Focus trap: keep Tab within the panel
      if (e.key === 'Tab') {
        const focusable = Array.from(
          _container.querySelectorAll('button, [tabindex="0"]')
        ).filter(el => !el.disabled);
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    });

    if (window.lucide) {
      try { lucide.createIcons({ nodes: [_container] }); } catch (_) {}
    }
  }

  // ── Render shortcut list ──────────────────────────────────────────────
  function _render() {
    const body = _container.querySelector('#sp-body');
    if (!body) return;

    if (!window.ShortcutRegistry) {
      body.innerHTML = '<p class="sp-empty">Shortcut registry not available.</p>';
      return;
    }

    const categories = ShortcutRegistry.getCategories();
    const isMac = navigator.platform.toUpperCase().includes('MAC');

    const html = categories.map(cat => {
      const shortcuts = ShortcutRegistry.getAll(cat);
      const rows = shortcuts.map(s => {
        const keys = ShortcutRegistry.displayKeys(s);
        // Split into individual key tokens for badge rendering
        const badges = keys.split('+').map(k =>
          `<kbd class="sp-key">${k.trim()}</kbd>`
        ).join('<span class="sp-key-sep">+</span>');

        return `
          <div class="sp-row">
            <span class="sp-keys">${badges}</span>
            <span class="sp-action">${s.action}</span>
          </div>
        `;
      }).join('');

      return `
        <div class="sp-category">
          <h4 class="sp-category-title">${cat}</h4>
          <div class="sp-category-rows">${rows}</div>
        </div>
      `;
    }).join('');

    body.innerHTML = `<div class="sp-columns">${html}</div>`;
  }

  // ── Public API ─────────────────────────────────────────────────────────
  function show() {
    _init();
    _render();
    _container.classList.remove('hidden');
    document.body.classList.add('sp-open');

    requestAnimationFrame(() => {
      const closeBtn = _container.querySelector('.sp-close');
      if (closeBtn) closeBtn.focus();
    });
  }

  function hide() {
    if (!_container) return;
    _container.classList.add('hidden');
    document.body.classList.remove('sp-open');
  }

  function toggle() {
    if (!_container || _container.classList.contains('hidden')) {
      show();
    } else {
      hide();
    }
  }

  return { show, hide, toggle };
})();

window.ShortcutPanel = ShortcutPanel;
