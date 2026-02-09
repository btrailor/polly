/**
 * SaveMessageForm — Inline form component for per-message knowledge save.
 *
 * Shown when user right-clicks an assistant message and selects "Save to Knowledge Base".
 * Expands below the message with title, domain, tags, and save mode options.
 *
 * Usage:
 *   showSaveMessageForm(messageDiv, rawContent);
 */

(function () {
  'use strict';

  const DOMAIN_OPTIONS = [
    { value: '', label: 'Auto-detect' },
    { value: 'sigils', label: '01-Sigils (Code)' },
    { value: 'signals', label: '02-Signals (Audio)' },
    { value: 'scrolls', label: '03-Scrolls (Writing)' },
    { value: 'glyphs', label: '04-Glyphs (Design)' },
    { value: 'grids', label: '05-Grids (Systems)' },
  ];

  /**
   * Show the inline save form below a message element.
   *
   * @param {HTMLElement} messageDiv - The .message div to attach to
   * @param {string} rawContent - The plain-text content of the message
   */
  function showSaveMessageForm(messageDiv, rawContent) {
    // Remove any previously open form
    const existingForm = document.querySelector('.save-message-form');
    if (existingForm) existingForm.remove();

    // Auto-generate title from first line / heading
    const firstLine = rawContent.split('\n')[0].replace(/^#+\s*/, '').trim();
    const autoTitle = firstLine.length > 60 ? firstLine.substring(0, 57) + '...' : firstLine || 'Knowledge Note';

    // Auto-generate tags from content
    const autoTags = extractQuickTags(rawContent);

    const form = document.createElement('div');
    form.className = 'save-message-form';
    form.style.cssText = `
      background: #1a1a2e; border: 1px solid #333; border-radius: 8px;
      padding: 12px 16px; margin-top: 8px; font-size: 13px; color: #e0e0e0;
    `;

    form.innerHTML = `
      <div style="font-weight: 600; margin-bottom: 10px; font-size: 14px;">
        Save to Knowledge Base
      </div>

      <div style="margin-bottom: 8px;">
        <label style="display: block; font-size: 11px; color: #808080; margin-bottom: 2px;">Title</label>
        <div style="display: flex; align-items: center; gap: 6px;">
          <input type="text" class="smf-title" value="${escapeAttr(autoTitle)}"
            style="flex:1; background: #12121e; border: 1px solid #333; border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 13px;" />
          <button class="smf-edit-title" title="Edit" style="background: none; border: none; color: #808080; cursor: pointer; font-size: 14px;">✎</button>
        </div>
      </div>

      <div style="margin-bottom: 8px;">
        <label style="display: block; font-size: 11px; color: #808080; margin-bottom: 2px;">Domain</label>
        <select class="smf-domain"
          style="width: 100%; background: #12121e; border: 1px solid #333; border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 13px;">
          ${DOMAIN_OPTIONS.map(d => `<option value="${d.value}">${d.label}</option>`).join('')}
        </select>
      </div>

      <div style="margin-bottom: 10px;">
        <label style="display: block; font-size: 11px; color: #808080; margin-bottom: 2px;">Tags</label>
        <input type="text" class="smf-tags" value="${escapeAttr(autoTags.join(', '))}"
          placeholder="tag1, tag2, ..."
          style="width: 100%; background: #12121e; border: 1px solid #333; border-radius: 4px; padding: 5px 8px; color: #e0e0e0; font-size: 13px; box-sizing: border-box;" />
      </div>

      <div style="margin-bottom: 10px;">
        <label style="display: block; font-size: 11px; color: #808080; margin-bottom: 4px;">Save mode</label>
        <label style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px; cursor: pointer;">
          <input type="radio" name="smf-mode" value="quick" checked style="accent-color: #4caf50;"/>
          <span>Save as-is (quick)</span>
        </label>
        <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
          <input type="radio" name="smf-mode" value="scribe" style="accent-color: #4caf50;"/>
          <span>Generate structured note (Scribe)</span>
        </label>
      </div>

      <div style="display: flex; gap: 8px; justify-content: flex-end;">
        <button class="smf-cancel"
          style="background: transparent; color: #808080; border: 1px solid #333; padding: 5px 14px; border-radius: 4px; cursor: pointer; font-size: 12px;">
          Cancel
        </button>
        <button class="smf-save"
          style="background: #2d5a27; color: #c8e6c9; border: none; padding: 5px 14px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;">
          Save
        </button>
      </div>
    `;

    // Insert after the message div
    messageDiv.after(form);

    // Focus title input
    const titleInput = form.querySelector('.smf-title');
    titleInput.focus();
    titleInput.select();

    // Cancel button
    form.querySelector('.smf-cancel').addEventListener('click', () => form.remove());

    // Save button
    form.querySelector('.smf-save').addEventListener('click', async () => {
      const title = form.querySelector('.smf-title').value.trim();
      const domain = form.querySelector('.smf-domain').value || null;
      const tagsStr = form.querySelector('.smf-tags').value.trim();
      const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(Boolean) : null;
      const mode = form.querySelector('input[name="smf-mode"]:checked').value;

      const saveBtn = form.querySelector('.smf-save');
      saveBtn.disabled = true;
      saveBtn.textContent = 'Saving...';

      try {
        const response = await fetch('http://127.0.0.1:11436/api/settings/knowledge/save-message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message_content: rawContent,
            message_role: 'assistant',
            conversation_id: window.currentConversationId || 'unknown',
            save_mode: mode,
            title: title || null,
            domain: domain,
            tags: tags
          })
        });

        const result = await response.json();

        if (mode === 'scribe' && result.content && window.PreviewModal) {
          // Scribe mode returns enriched note for preview
          form.remove();
          window.PreviewModal.show(result, async (noteData) => {
            await window.saveNoteToKnowledgeBase(noteData);
          });
        } else if (result.success) {
          form.innerHTML = `
            <div style="color: #4caf50; font-size: 12px; padding: 4px 0;">
              ✓ Saved to KB: ${escapeHtml(result.title || title)}
            </div>
          `;
          if (typeof showToast === 'function') {
            showToast('Saved: ' + (result.title || title) + ' — RAG will include this next time', 'success');
          }
          setTimeout(() => form.remove(), 3000);
        } else {
          throw new Error(result.error || 'Save failed');
        }
      } catch (err) {
        console.error('[SaveMessageForm] Save failed:', err);
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save';
        if (typeof showToast === 'function') {
          showToast('Save failed: ' + err.message, 'error');
        }
      }
    });
  }

  /**
   * Quick tag extraction from text (no LLM).
   */
  function extractQuickTags(text) {
    const tags = new Set();
    // Backtick-wrapped terms
    const codeTerms = text.match(/`([^`]+)`/g);
    if (codeTerms) {
      codeTerms.slice(0, 3).forEach(t => {
        const clean = t.replace(/`/g, '').trim().toLowerCase();
        if (clean.length > 1 && clean.length < 30) tags.add(clean);
      });
    }
    // Bold terms
    const boldTerms = text.match(/\*\*([^*]+)\*\*/g);
    if (boldTerms) {
      boldTerms.slice(0, 2).forEach(t => {
        const clean = t.replace(/\*\*/g, '').trim().toLowerCase();
        if (clean.length > 1 && clean.length < 30) tags.add(clean);
      });
    }
    return [...tags].slice(0, 5);
  }

  function escapeAttr(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Expose globally
  window.showSaveMessageForm = showSaveMessageForm;
})();
