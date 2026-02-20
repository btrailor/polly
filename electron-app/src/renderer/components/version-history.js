/**
 * VersionHistory Component
 *
 * Slide-in panel that shows version history for the currently open note.
 * Opens when the "History" toolbar button is clicked.
 *
 * Usage:
 *   await VersionHistory.show(notePath, onRevert);
 *   VersionHistory.hide();
 */

const VersionHistory = (() => {
  let _container = null;
  let _currentPath = null;
  let _onRevert = null;
  let _previewVersionId = null;

  // ── Source badge labels ────────────────────────────────────────────────
  const SOURCE_LABELS = {
    'auto-save':    { label: 'Auto',   cls: 'vh-badge--auto' },
    'manual-save':  { label: 'Manual', cls: 'vh-badge--manual' },
    'revert':       { label: 'Revert', cls: 'vh-badge--revert' },
  };

  // ── DOM bootstrap ──────────────────────────────────────────────────────
  function _init() {
    if (_container) return;

    _container = document.createElement('div');
    _container.id = 'version-history-panel';
    _container.className = 'vh-panel hidden';
    _container.setAttribute('role', 'complementary');
    _container.setAttribute('aria-label', 'Version history');
    _container.innerHTML = `
      <div class="vh-overlay"></div>
      <div class="vh-drawer">
        <div class="vh-header">
          <span class="vh-title">
            <i data-lucide="history" style="width:16px;height:16px;"></i>
            Version History
          </span>
          <button class="vh-close btn-icon" aria-label="Close version history">
            <i data-lucide="x" style="width:16px;height:16px;"></i>
          </button>
        </div>

        <div class="vh-body">
          <!-- Version list pane -->
          <div class="vh-list-pane" id="vh-list-pane">
            <div id="vh-list-content">
              <div class="vh-loading">Loading versions...</div>
            </div>
          </div>

          <!-- Preview pane -->
          <div class="vh-preview-pane hidden" id="vh-preview-pane">
            <div class="vh-preview-header">
              <button class="btn-icon vh-back" id="vh-back-btn" aria-label="Back to list">
                <i data-lucide="arrow-left" style="width:14px;height:14px;"></i>
                <span>Back</span>
              </button>
              <span class="vh-preview-title" id="vh-preview-title"></span>
              <button class="vh-restore-btn" id="vh-restore-btn">Restore this version</button>
            </div>
            <pre class="vh-preview-content" id="vh-preview-content"></pre>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(_container);

    // Overlay click → close
    _container.querySelector('.vh-overlay').addEventListener('click', hide);

    // Close button
    _container.querySelector('.vh-close').addEventListener('click', hide);

    // Back button
    _container.querySelector('#vh-back-btn').addEventListener('click', _showList);

    // Restore button
    _container.querySelector('#vh-restore-btn').addEventListener('click', _restoreVersion);

    // Keyboard: Escape closes
    _container.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { e.preventDefault(); hide(); }
    });

    if (window.lucide) {
      try { lucide.createIcons({ nodes: [_container] }); } catch (_) {}
    }
  }

  // ── Load and render version list ──────────────────────────────────────
  async function _loadVersions() {
    const listContent = _container.querySelector('#vh-list-content');
    listContent.innerHTML = '<div class="vh-loading">Loading versions...</div>';

    if (!window.polly || !window.polly.noteVersions) {
      listContent.innerHTML = '<div class="vh-empty">Version history is not available.</div>';
      return;
    }

    try {
      const versions = await window.polly.noteVersions.list(_currentPath);

      if (!versions || versions.length === 0) {
        listContent.innerHTML = `
          <div class="vh-empty">
            <i data-lucide="clock" style="width:24px;height:24px;opacity:0.4;"></i>
            <p>No versions saved yet.</p>
            <p class="vh-empty-hint">Versions are saved automatically as you edit.</p>
          </div>
        `;
        if (window.lucide) {
          try { lucide.createIcons({ nodes: [listContent] }); } catch (_) {}
        }
        return;
      }

      const items = versions.map((v) => {
        const badge = SOURCE_LABELS[v.source] || { label: v.source, cls: 'vh-badge--auto' };
        const date = new Date(v.saved_at * 1000);
        const dateStr = _formatDate(date);
        const preview = v.preview ? _escapeHtml(v.preview) : '<em class="vh-no-preview">Empty</em>';

        return `
          <div class="vh-version-item" data-version-id="${v.id}" role="button" tabindex="0"
               aria-label="Version from ${dateStr}">
            <div class="vh-version-meta">
              <span class="vh-version-date">${dateStr}</span>
              <span class="vh-badge ${badge.cls}">${badge.label}</span>
            </div>
            <div class="vh-version-preview">${preview}</div>
          </div>
        `;
      });

      listContent.innerHTML = `<div class="vh-version-list">${items.join('')}</div>`;

      // Attach click/keypress listeners
      listContent.querySelectorAll('.vh-version-item').forEach((el) => {
        el.addEventListener('click', () => _previewVersion(el.dataset.versionId));
        el.addEventListener('keypress', (e) => {
          if (e.key === 'Enter' || e.key === ' ') _previewVersion(el.dataset.versionId);
        });
      });

      if (window.lucide) {
        try { lucide.createIcons({ nodes: [listContent] }); } catch (_) {}
      }
    } catch (err) {
      console.error('[VersionHistory] Failed to load versions:', err);
      listContent.innerHTML = '<div class="vh-empty vh-empty--error">Failed to load versions.</div>';
    }
  }

  // ── Preview a version ─────────────────────────────────────────────────
  async function _previewVersion(versionId) {
    _previewVersionId = versionId;

    const previewPane = _container.querySelector('#vh-preview-pane');
    const listPane = _container.querySelector('#vh-list-pane');
    const previewContent = _container.querySelector('#vh-preview-content');
    const previewTitle = _container.querySelector('#vh-preview-title');

    previewContent.textContent = 'Loading...';
    listPane.classList.add('hidden');
    previewPane.classList.remove('hidden');

    try {
      const version = await window.polly.noteVersions.get(versionId);
      if (!version) throw new Error('Version not found');

      const date = new Date(version.saved_at * 1000);
      const badge = SOURCE_LABELS[version.source] || { label: version.source, cls: '' };
      previewTitle.textContent = `${_formatDate(date)} · ${badge.label}`;
      previewContent.textContent = version.content;
    } catch (err) {
      console.error('[VersionHistory] Failed to get version:', err);
      previewContent.textContent = 'Failed to load version content.';
    }
  }

  // ── Back to list ──────────────────────────────────────────────────────
  function _showList() {
    _previewVersionId = null;
    _container.querySelector('#vh-list-pane').classList.remove('hidden');
    _container.querySelector('#vh-preview-pane').classList.add('hidden');
  }

  // ── Restore version ───────────────────────────────────────────────────
  async function _restoreVersion() {
    if (!_previewVersionId || !_currentPath) return;

    const restoreBtn = _container.querySelector('#vh-restore-btn');
    restoreBtn.disabled = true;
    restoreBtn.textContent = 'Restoring...';

    try {
      const result = await window.polly.noteVersions.revert(_currentPath, _previewVersionId);
      if (!result || !result.content) throw new Error('Revert returned no content');

      // Invoke the callback so notes-manager can update the editor
      if (_onRevert) {
        await _onRevert(result.content);
      }

      const date = _container.querySelector('#vh-preview-title').textContent;
      if (window.NotesManager) {
        window.NotesManager.showToast(`Reverted to version from ${date}`);
      } else if (typeof showNotification === 'function') {
        showNotification(`Reverted to version from ${date}`, 'success');
      }

      hide();
    } catch (err) {
      console.error('[VersionHistory] Revert failed:', err);
      restoreBtn.disabled = false;
      restoreBtn.textContent = 'Restore this version';
      if (typeof showNotification === 'function') {
        showNotification('Failed to restore version', 'error');
      }
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  function _formatDate(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffH = Math.floor(diffMs / 3600000);
    const diffD = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffH < 24) return `${diffH}h ago`;
    if (diffD < 7) return `${diffD}d ago`;

    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) +
      ' ' + date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  }

  function _escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // ── Public API ────────────────────────────────────────────────────────
  /**
   * Show the version history panel for a note.
   * @param {string} notePath - Absolute path to the note file
   * @param {Function} onRevert - Called with (content) when user restores a version
   */
  function show(notePath, onRevert) {
    _init();
    _currentPath = notePath;
    _onRevert = onRevert || null;
    _previewVersionId = null;

    // Reset to list pane
    _showList();

    _container.classList.remove('hidden');
    document.body.classList.add('vh-open');

    _loadVersions();

    // Focus close button
    requestAnimationFrame(() => {
      const closeBtn = _container.querySelector('.vh-close');
      if (closeBtn) closeBtn.focus();
    });
  }

  function hide() {
    if (!_container) return;
    _container.classList.add('hidden');
    document.body.classList.remove('vh-open');
    _currentPath = null;
    _onRevert = null;
  }

  return { show, hide };
})();

window.VersionHistory = VersionHistory;
