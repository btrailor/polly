/**
 * ConflictDialog Component
 *
 * Three-option dialog for resolving note edit conflicts when external
 * changes arrive while the user is editing.
 *
 * Usage:
 *   const result = await ConflictDialog.show({
 *     myContent: '...',        // user's current unsaved edits
 *     theirContent: '...',     // external (on-disk) version
 *   });
 *   // result: 'mine' | 'theirs' | null (dismissed)
 */

const ConflictDialog = (() => {
  let _container = null;
  let _resolvePromise = null;

  // ── Minimal line-by-line diff ─────────────────────────────────────────
  function _computeDiff(oldText, newText) {
    const oldLines = oldText.split('\n');
    const newLines = newText.split('\n');

    // LCS-based diff (simple O(n*m) for short notes; adequate here)
    const m = oldLines.length;
    const n = newLines.length;
    const dp = [];

    for (let i = 0; i <= m; i++) {
      dp[i] = new Array(n + 1).fill(0);
    }
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (oldLines[i - 1] === newLines[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1] + 1;
        } else {
          dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
        }
      }
    }

    // Backtrack
    const diff = [];
    let i = m, j = n;
    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && oldLines[i - 1] === newLines[j - 1]) {
        diff.unshift({ type: 'equal', line: oldLines[i - 1] });
        i--; j--;
      } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
        diff.unshift({ type: 'add', line: newLines[j - 1] });
        j--;
      } else {
        diff.unshift({ type: 'remove', line: oldLines[i - 1] });
        i--;
      }
    }
    return diff;
  }

  function _renderDiff(myContent, theirContent) {
    const diff = _computeDiff(myContent, theirContent);
    return diff.map(({ type, line }) => {
      const escaped = _escapeHtml(line);
      if (type === 'add') {
        return `<div class="cd-diff-line cd-diff-add">+ ${escaped}</div>`;
      } else if (type === 'remove') {
        return `<div class="cd-diff-line cd-diff-remove">- ${escaped}</div>`;
      }
      return `<div class="cd-diff-line cd-diff-equal">  ${escaped}</div>`;
    }).join('');
  }

  function _escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // ── DOM bootstrap ──────────────────────────────────────────────────────
  function _init() {
    if (_container) return;

    _container = document.createElement('div');
    _container.id = 'conflict-dialog-container';
    _container.className = 'cd-container hidden';
    _container.setAttribute('role', 'dialog');
    _container.setAttribute('aria-modal', 'true');
    _container.setAttribute('aria-labelledby', 'cd-title');
    _container.innerHTML = `
      <div class="cd-overlay"></div>
      <div class="cd-panel">
        <div class="cd-header">
          <span class="cd-icon" aria-hidden="true">
            <i data-lucide="git-merge" style="width:18px;height:18px;"></i>
          </span>
          <h3 class="cd-title" id="cd-title">Resolve edit conflict</h3>
        </div>
        <p class="cd-message">
          This note was changed externally while you were editing.
          Choose how to resolve the conflict.
        </p>

        <!-- Main choices -->
        <div class="cd-choices" id="cd-choices">
          <button class="cd-choice-btn" id="cd-btn-mine">
            <i data-lucide="user" style="width:16px;height:16px;"></i>
            <span class="cd-choice-label">Keep my changes</span>
            <span class="cd-choice-desc">Discard the external version and save your edits</span>
          </button>
          <button class="cd-choice-btn" id="cd-btn-theirs">
            <i data-lucide="download" style="width:16px;height:16px;"></i>
            <span class="cd-choice-label">Load external version</span>
            <span class="cd-choice-desc">Replace your edits with the version from disk</span>
          </button>
          <button class="cd-choice-btn" id="cd-btn-diff">
            <i data-lucide="split" style="width:16px;height:16px;"></i>
            <span class="cd-choice-label">View differences</span>
            <span class="cd-choice-desc">See what changed, then decide</span>
          </button>
        </div>

        <!-- Diff view (hidden until user clicks "View diff") -->
        <div class="cd-diff-view hidden" id="cd-diff-view">
          <div class="cd-diff-legend">
            <span class="cd-diff-legend-item cd-diff-add">+ External additions</span>
            <span class="cd-diff-legend-item cd-diff-remove">- Your changes (removed by external)</span>
          </div>
          <div class="cd-diff-content" id="cd-diff-content"></div>
          <div class="cd-diff-actions">
            <button class="cd-diff-action-btn" id="cd-diff-keep-mine">Keep my changes</button>
            <button class="cd-diff-action-btn cd-diff-action-btn--primary" id="cd-diff-take-theirs">Take external version</button>
          </div>
        </div>

        <button class="cd-cancel" id="cd-cancel">Cancel</button>
      </div>
    `;

    document.body.appendChild(_container);

    _container.querySelector('.cd-overlay').addEventListener('click', () => _resolve(null));
    _container.querySelector('#cd-cancel').addEventListener('click', () => _resolve(null));
    _container.querySelector('#cd-btn-mine').addEventListener('click', () => _resolve('mine'));
    _container.querySelector('#cd-btn-theirs').addEventListener('click', () => _resolve('theirs'));
    _container.querySelector('#cd-btn-diff').addEventListener('click', _showDiff);
    _container.querySelector('#cd-diff-keep-mine').addEventListener('click', () => _resolve('mine'));
    _container.querySelector('#cd-diff-take-theirs').addEventListener('click', () => _resolve('theirs'));

    _container.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { e.preventDefault(); _resolve(null); }
    });

    if (window.lucide) {
      try { lucide.createIcons({ nodes: [_container] }); } catch (_) {}
    }
  }

  function _showDiff() {
    _container.querySelector('#cd-choices').classList.add('hidden');
    _container.querySelector('#cd-diff-view').classList.remove('hidden');
    _container.querySelector('#cd-cancel').classList.add('hidden');
  }

  function _resolve(value) {
    if (!_resolvePromise) return;

    _container.classList.add('hidden');
    document.body.classList.remove('cd-open');

    // Reset diff view for next open
    const choices = _container.querySelector('#cd-choices');
    const diffView = _container.querySelector('#cd-diff-view');
    const cancelBtn = _container.querySelector('#cd-cancel');
    choices.classList.remove('hidden');
    diffView.classList.add('hidden');
    cancelBtn.classList.remove('hidden');

    const cb = _resolvePromise;
    _resolvePromise = null;
    cb(value);
  }

  // ── Public API ─────────────────────────────────────────────────────────
  /**
   * @param {object} options
   * @param {string} options.myContent     - User's current (unsaved) content
   * @param {string} options.theirContent  - External (on-disk) content
   * @returns {Promise<'mine'|'theirs'|null>}
   */
  function show({ myContent = '', theirContent = '' } = {}) {
    _init();

    // Populate diff
    const diffContent = _container.querySelector('#cd-diff-content');
    diffContent.innerHTML = _renderDiff(myContent, theirContent);

    _container.classList.remove('hidden');
    document.body.classList.add('cd-open');

    requestAnimationFrame(() => {
      const firstBtn = _container.querySelector('#cd-btn-mine');
      if (firstBtn) firstBtn.focus();
    });

    return new Promise((resolve) => {
      _resolvePromise = resolve;
    });
  }

  return { show };
})();

window.ConflictDialog = ConflictDialog;
