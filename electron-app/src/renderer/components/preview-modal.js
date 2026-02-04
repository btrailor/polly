/**
 * Preview Modal Component (Phase 16c Day 11)
 * 
 * Displays generated note preview with Edit/Preview/Raw tabs.
 * Allows user to review note before saving to knowledge base.
 * 
 * Usage:
 *   PreviewModal.show(noteData, onSave);
 *   
 * Example noteData:
 * {
 *   "content": "# Note Title\n\nMarkdown content...",
 *   "title": "Note Title",
 *   "metadata": {
 *     "domain": "scrolls",
 *     "folder": "knowledge-base/Scrolls/",
 *     "filename": "note-title.md",
 *     "template_used": "concept-note",
 *     "link_count": 5
 *   }
 * }
 */

const PreviewModal = {
  /**
   * Current note data
   */
  currentNote: null,
  
  /**
   * Callback when note is saved
   */
  onSaveCallback: null,
  
  /**
   * Current active tab
   */
  activeTab: 'preview',
  
  /**
   * Initialize the preview modal (call once on page load)
   */
  init() {
    // Add container to DOM if not exists
    if (!document.getElementById('preview-modal-container')) {
      const container = document.createElement('div');
      container.id = 'preview-modal-container';
      container.className = 'preview-modal-container hidden';
      container.innerHTML = `
        <div class="preview-modal-overlay"></div>
        <div class="preview-modal">
          <div class="preview-modal-header">
            <h3 class="preview-modal-title">Preview Note</h3>
            <div class="preview-modal-tabs">
              <button class="preview-tab active" data-tab="preview">
                <i data-lucide="eye" style="width: 14px; height: 14px;"></i>
                Preview
              </button>
              <button class="preview-tab" data-tab="edit">
                <i data-lucide="edit" style="width: 14px; height: 14px;"></i>
                Edit
              </button>
              <button class="preview-tab" data-tab="raw">
                <i data-lucide="code" style="width: 14px; height: 14px;"></i>
                Raw
              </button>
            </div>
            <button class="preview-modal-close" aria-label="Close">×</button>
          </div>
          <div class="preview-modal-body">
            <!-- Preview Tab -->
            <div class="preview-tab-content active" data-tab-content="preview">
              <div class="preview-rendered"></div>
            </div>
            
            <!-- Edit Tab -->
            <div class="preview-tab-content" data-tab-content="edit">
              <textarea class="preview-edit-textarea" placeholder="Edit your note..."></textarea>
            </div>
            
            <!-- Raw Tab -->
            <div class="preview-tab-content" data-tab-content="raw">
              <pre class="preview-raw-content"></pre>
            </div>
          </div>
          <div class="preview-modal-footer">
            <div class="preview-metadata">
              <span class="preview-meta-item">
                <i data-lucide="folder" style="width: 12px; height: 12px;"></i>
                <span class="preview-meta-value preview-meta-domain"></span>
              </span>
              <span class="preview-meta-item">
                <i data-lucide="link" style="width: 12px; height: 12px;"></i>
                <span class="preview-meta-value preview-meta-links"></span>
              </span>
              <span class="preview-meta-item">
                <i data-lucide="file-text" style="width: 12px; height: 12px;"></i>
                <span class="preview-meta-value preview-meta-template"></span>
              </span>
            </div>
            <div class="preview-actions">
              <button class="btn btn-secondary preview-modal-cancel">Cancel</button>
              <button class="btn btn-primary preview-modal-save">
                <i data-lucide="save" style="width: 14px; height: 14px;"></i>
                Save to Knowledge Base
              </button>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(container);
      
      // Attach event listeners
      this._attachListeners();
    }
  },
  
  /**
   * Attach event listeners to modal elements
   */
  _attachListeners() {
    const container = document.getElementById('preview-modal-container');
    
    // Close button
    container.querySelector('.preview-modal-close').addEventListener('click', () => {
      this.hide();
    });
    
    // Cancel button
    container.querySelector('.preview-modal-cancel').addEventListener('click', () => {
      this.hide();
    });
    
    // Save button
    container.querySelector('.preview-modal-save').addEventListener('click', () => {
      this._handleSave();
    });
    
    // Tab switching
    container.querySelectorAll('.preview-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        this._switchTab(tab.dataset.tab);
      });
    });
    
    // Close on overlay click
    container.querySelector('.preview-modal-overlay').addEventListener('click', () => {
      this.hide();
    });
    
    // Prevent modal close on modal content click
    container.querySelector('.preview-modal').addEventListener('click', (e) => {
      e.stopPropagation();
    });
    
    // Sync edit textarea changes back to content
    container.querySelector('.preview-edit-textarea').addEventListener('input', (e) => {
      if (this.currentNote) {
        this.currentNote.content = e.target.value;
        // Update preview and raw tabs
        this._updatePreview();
        this._updateRaw();
      }
    });
  },
  
  /**
   * Show the preview modal with given note data
   * 
   * @param {Object} noteData - Note data from Scribe Enrich mode
   * @param {Function} onSave - Callback when note is saved: (noteData) => {}
   */
  show(noteData, onSave) {
    this.currentNote = noteData;
    this.onSaveCallback = onSave;
    this.activeTab = 'preview';
    
    // Render note in all tabs
    this._updatePreview();
    this._updateEdit();
    this._updateRaw();
    this._updateMetadata();
    
    // Show container
    const container = document.getElementById('preview-modal-container');
    container.classList.remove('hidden');
    
    // Ensure preview tab is active
    this._switchTab('preview');
    
    // Refresh icons
    if (window.lucide) {
      window.lucide.createIcons();
    }
  },
  
  /**
   * Hide the preview modal
   */
  hide() {
    const container = document.getElementById('preview-modal-container');
    container.classList.add('hidden');
    this.currentNote = null;
    this.onSaveCallback = null;
  },
  
  /**
   * Switch active tab
   */
  _switchTab(tabName) {
    this.activeTab = tabName;
    
    const container = document.getElementById('preview-modal-container');
    
    // Update tab buttons
    container.querySelectorAll('.preview-tab').forEach(tab => {
      if (tab.dataset.tab === tabName) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    // Update tab content
    container.querySelectorAll('.preview-tab-content').forEach(content => {
      if (content.dataset.tabContent === tabName) {
        content.classList.add('active');
      } else {
        content.classList.remove('active');
      }
    });
  },
  
  /**
   * Update preview tab content (rendered markdown)
   */
  _updatePreview() {
    const previewEl = document.querySelector('.preview-rendered');
    if (!previewEl || !this.currentNote) return;
    
    // Render markdown using marked.js
    if (window.marked) {
      previewEl.innerHTML = window.marked.parse(this.currentNote.content);
    } else {
      // Fallback: show plain text
      previewEl.textContent = this.currentNote.content;
    }
  },
  
  /**
   * Update edit tab content (editable textarea)
   */
  _updateEdit() {
    const editEl = document.querySelector('.preview-edit-textarea');
    if (!editEl || !this.currentNote) return;
    
    editEl.value = this.currentNote.content;
  },
  
  /**
   * Update raw tab content (plain markdown)
   */
  _updateRaw() {
    const rawEl = document.querySelector('.preview-raw-content');
    if (!rawEl || !this.currentNote) return;
    
    rawEl.textContent = this.currentNote.content;
  },
  
  /**
   * Update metadata display in footer
   */
  _updateMetadata() {
    if (!this.currentNote || !this.currentNote.metadata) return;
    
    const metadata = this.currentNote.metadata;
    
    // Domain
    const domainEl = document.querySelector('.preview-meta-domain');
    if (domainEl) {
      domainEl.textContent = metadata.domain || 'scrolls';
    }
    
    // Link count
    const linksEl = document.querySelector('.preview-meta-links');
    if (linksEl) {
      const linkCount = metadata.link_count || metadata.links_created?.length || 0;
      linksEl.textContent = `${linkCount} links`;
    }
    
    // Template
    const templateEl = document.querySelector('.preview-meta-template');
    if (templateEl) {
      templateEl.textContent = metadata.template_used || 'quick-note';
    }
  },
  
  /**
   * Handle save button click
   */
  _handleSave() {
    if (!this.currentNote) return;
    
    // Get current content (might have been edited)
    const editTextarea = document.querySelector('.preview-edit-textarea');
    if (editTextarea) {
      this.currentNote.content = editTextarea.value;
    }
    
    // Call callback with updated note
    if (this.onSaveCallback) {
      this.onSaveCallback(this.currentNote);
    }
    
    // Hide modal
    this.hide();
  },
  
  /**
   * Get current note content (for external access)
   */
  getCurrentContent() {
    return this.currentNote ? this.currentNote.content : null;
  },
  
  /**
   * Update note content programmatically
   */
  updateContent(newContent) {
    if (!this.currentNote) return;
    
    this.currentNote.content = newContent;
    this._updatePreview();
    this._updateEdit();
    this._updateRaw();
  }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => PreviewModal.init());
} else {
  PreviewModal.init();
}

// Export to global scope for browser use
window.PreviewModal = PreviewModal;

// Export for Node.js modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PreviewModal;
}
