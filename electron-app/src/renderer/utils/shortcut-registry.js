/**
 * ShortcutRegistry — centralized keyboard shortcut definitions.
 *
 * Each entry has:
 *   keys     {string}   Human-readable shortcut label (for the help panel)
 *   action   {string}   Description of what it does
 *   category {string}   Group for the help panel
 *   mac      {string}   Mac symbol string for display (optional)
 *
 * Actual handler wiring lives in app.js; this registry is the single source
 * of truth for shortcut metadata rendered in the help panel.
 */

const ShortcutRegistry = (() => {
  const _shortcuts = [
    // ── Navigation ──────────────────────────────────────────────────────
    {
      keys: 'Cmd+B',
      mac: '⌘B',
      action: 'Toggle left sidebar',
      category: 'Navigation',
    },
    {
      keys: 'Cmd+/',
      mac: '⌘/',
      action: 'Toggle chat panel',
      category: 'Navigation',
    },
    {
      keys: 'Cmd+L',
      mac: '⌘L',
      action: 'Focus search',
      category: 'Navigation',
    },

    // ── Views ────────────────────────────────────────────────────────────
    {
      keys: 'Cmd+1',
      mac: '⌘1',
      action: 'Dashboard',
      category: 'Views',
    },
    {
      keys: 'Cmd+2',
      mac: '⌘2',
      action: 'Code',
      category: 'Views',
    },
    {
      keys: 'Cmd+3',
      mac: '⌘3',
      action: 'Notes',
      category: 'Views',
    },
    {
      keys: 'Cmd+4',
      mac: '⌘4',
      action: 'Knowledge',
      category: 'Views',
    },
    {
      keys: 'Cmd+5',
      mac: '⌘5',
      action: 'Patterns',
      category: 'Views',
    },
    {
      keys: 'Cmd+6',
      mac: '⌘6',
      action: 'Settings',
      category: 'Views',
    },

    // ── Chat ─────────────────────────────────────────────────────────────
    {
      keys: 'Cmd+N',
      mac: '⌘N',
      action: 'New conversation',
      category: 'Chat',
    },
    {
      keys: 'Enter',
      mac: '↵',
      action: 'Send message',
      category: 'Chat',
    },
    {
      keys: 'Shift+Enter',
      mac: '⇧↵',
      action: 'New line in message',
      category: 'Chat',
    },
    {
      keys: '/',
      mac: '/',
      action: 'Focus chat input',
      category: 'Chat',
    },

    // ── Notes ────────────────────────────────────────────────────────────
    {
      keys: 'Cmd+S',
      mac: '⌘S',
      action: 'Save note',
      category: 'Notes',
    },

    // ── General ──────────────────────────────────────────────────────────
    {
      keys: 'Escape',
      mac: 'Esc',
      action: 'Close panel / overlay',
      category: 'General',
    },
    {
      keys: 'Cmd+?',
      mac: '⌘?',
      action: 'Show keyboard shortcuts',
      category: 'General',
    },
  ];

  /**
   * Get all shortcuts, optionally filtered by category.
   * @param {string} [category]
   * @returns {Array}
   */
  function getAll(category) {
    if (category) return _shortcuts.filter(s => s.category === category);
    return _shortcuts.slice();
  }

  /**
   * Get all unique category names in display order.
   * @returns {string[]}
   */
  function getCategories() {
    const seen = new Set();
    const result = [];
    for (const s of _shortcuts) {
      if (!seen.has(s.category)) {
        seen.add(s.category);
        result.push(s.category);
      }
    }
    return result;
  }

  /**
   * Get the display string for a shortcut key on the current platform.
   * @param {object} shortcut
   * @returns {string}
   */
  function displayKeys(shortcut) {
    const isMac = navigator.platform.toUpperCase().includes('MAC');
    if (isMac && shortcut.mac) return shortcut.mac;
    // Fall back to keys with Cmd→Ctrl substitution on Windows/Linux
    return shortcut.keys.replace('Cmd', 'Ctrl');
  }

  return { getAll, getCategories, displayKeys };
})();

window.ShortcutRegistry = ShortcutRegistry;
