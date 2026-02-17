/**
 * Notes Manager - Handles notes view and file operations
 */

class NotesManager {
  constructor() {
    this.notes = [];
    this.currentNote = null;
    this.backlinks = [];
    this.tags = [];
    this.editor = null;
    this.searchResults = [];
    
    // State
    this.isLoading = false;
    this.syncStatus = 'idle';
    this.fileWatcherStarted = false; // Track if file watcher has been started
    
    // Browse list state (replaces sortMode)
    this.browseFilters = {
      domain: null,
      type: null,
      maturity: null,
      sort: 'recent',
      connectionStatus: null,
      tag: null
    };
    this.activeDomainFilter = null;
    
    // Lower panel state
    this.lowerPanelState = {
      collapsed: true,
      activeTab: 'filters'
    };
    
    // Auto-save state
    this.saveStatus = 'saved'; // 'saved', 'saving', 'unsaved'
    this.saveTimeout = null;
    this.autoSaveDelay = 2000; // 2 seconds
    this.hasUnsavedChanges = false;
    /** Content last successfully saved (normalized). Used so we only save when content actually changed. */
    this.lastSavedContent = null;
    
    // Quick switcher state
    this.quickSwitcherSelectedIndex = 0;
    
    // Wiki-link autocomplete state
    this.isSelectingSuggestion = false;
    
    // Sync polling
    this.syncPollInterval = null;
    this.lastFilesSynced = 0;
  }

  /**
   * Initialize notes manager
   */
  async init() {
    console.log('[Notes] Initializing notes manager...');
    
    // Check notes source
    await this.checkNotesSource();
    console.log('[Notes] Notes source checked:', this.source, this.sourcePath);
    
    // Load notes index
    console.log('[Notes] About to load notes index...');
    try {
      await this.loadNotesIndex();
      console.log('[Notes] Notes index loaded successfully');
    } catch (error) {
      console.error('[Notes] Failed to load notes index in init:', error);
    }
    
    // Setup editor
    this.setupEditor();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Start file watcher
    await this.startFileWatcher();
    
    // Check sync status and setup polling
    await this.checkSyncStatus();
    this.startSyncPolling();
    
    console.log('[Notes] Notes manager initialized');
  }

  /**
   * Check current notes source (Obsidian or native)
   */
  async checkNotesSource() {
    try {
      const response = await fetch('http://127.0.0.1:11436/polly/notes/source');
      const data = await response.json();
      
      this.source = data.source; // 'obsidian' or 'native'
      this.sourcePath = data.path;
      
      // Set global vault path for image resolution
      window.pollyNotesVaultPath = this.sourcePath;
      
      console.log(`[Notes] Source: ${this.source} at ${this.sourcePath}`);
      
      // Update UI
      this.updateSourceIndicator();
      
    } catch (error) {
      console.error('[Notes] Error checking source:', error);
      this.source = 'unknown';
    }
  }

  /**
   * Load notes index from backend
   */
  async loadNotesIndex(domain = null, limit = 1000) {
    this.isLoading = true;
    this.updateLoadingState();
    
    try {
      let url = `http://127.0.0.1:11436/polly/notes/index?limit=${limit}`;
      if (domain) {
        url += `&domain=${domain}`;
      }
      
      console.log(`[Notes] Fetching notes from: ${url}`);
      const response = await fetch(url);
      
      console.log(`[Notes] Response status: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[Notes] HTTP error response:`, errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`[Notes] API response:`, data);
      
      this.notes = data.notes || [];
      this.stats = data.stats || {};
      
      console.log(`[Notes] Loaded ${this.notes.length} notes (total: ${this.stats.total || 0})`);
      console.log(`[Notes] First few notes:`, this.notes.slice(0, 3));
      
      if (data.error) {
        console.warn(`[Notes] API returned error: ${data.error}`);
      }
      
      if (this.notes.length === 0 && this.stats.total === 0) {
        console.warn('[Notes] No notes found. The notes index may be empty or the notes path may not be configured.');
        console.warn('[Notes] Check server logs for index build messages.');
      }
      
      // Update browse list (replaces updateFileTree)
      const container = document.querySelector('#notes-browse-list');
      if (container) {
        this.updateBrowseList(container, {
          ...this.browseFilters,
          onItemClick: (itemEl, item) => this.openNote(item.id)
        });
      } else {
        console.error('[Notes] Could not find #notes-browse-list container');
      }
      
    } catch (error) {
      console.error('[Notes] Error loading notes:', error);
      console.error('[Notes] Error stack:', error.stack);
      this.showError(`Failed to load notes: ${error.message}`);
    } finally {
      this.isLoading = false;
      this.updateLoadingState();
    }
  }

  /**
   * Search notes by query
   */
  async searchNotes(query, limit = 20) {
    if (!query || query.trim().length === 0) {
      this.searchResults = [];
      this.updateSearchResults();
      return;
    }
    
    try {
      const response = await fetch(
        `http://127.0.0.1:11436/polly/notes/search?q=${encodeURIComponent(query)}&limit=${limit}`
      );
      const data = await response.json();
      
      this.searchResults = data.results || [];
      console.log(`[Notes] Found ${this.searchResults.length} results for "${query}"`);
      
      // Update UI
      this.updateSearchResults();
      
    } catch (error) {
      console.error('[Notes] Error searching notes:', error);
    }
  }

  /**
   * Open a note
   * @param {string} noteName - Name of the note to open
   * @param {string} heading - Optional heading to scroll to
   * @param {boolean} preserveScroll - If true, preserve current scroll position (for reloads)
   */
  async openNote(noteName, heading = null, preserveScroll = false) {
    try {
      // Find note in index (check name, title, and aliases)
      const note = this.notes.find(n => 
        n.name === noteName || 
        n.title === noteName ||
        (n.aliases && n.aliases.includes(noteName))
      );
      
      if (!note) {
        console.warn(`[Notes] Note not found: ${noteName}`);
        return;
      }
      
      console.log(`[Notes] Opening note: ${note.name}${heading ? ' #' + heading : ''}${noteName !== note.name ? ` (via alias: ${noteName})` : ''}`);
      
      // Read file content
      const response = await window.polly.readFile(note.path);
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to read file');
      }
      
      const content = response.content;
      
      // Save current scroll and cursor position if needed
      const savedScrollPosition = preserveScroll && this.editor ? this.editor.getScrollPosition() : null;
      const savedCursorPosition = preserveScroll && this.editor ? this.editor.getCursorPosition() : null;
      
      // Set current note
      this.currentNote = note;
      
      // Only reset to view mode if not using CM6 (CM6 is always in edit mode)
      // If we're using CM6 and already in edit mode, stay in edit mode
      if (!this.cm6Editor) {
        this.editorMode = 'view';
        console.log('[Notes] Editor mode set to: view (using legacy editor)');
      } else {
        console.log('[Notes] Keeping editor mode as:', this.editorMode, '(using CM6)');
      }
      
      // Update editor
      if (this.editor) {
        this.editor.setValue(content);
        this.lastSavedContent = this._normalizeContentForCompare(content);
        
        // Restore scroll and cursor position or reset to top
        if (preserveScroll && savedScrollPosition) {
          this.editor.setScrollPosition(savedScrollPosition);
          if (savedCursorPosition !== null) {
            this.editor.setCursorPosition(savedCursorPosition);
          }
        } else {
          this.editor.setScrollPosition({ scrollTop: 0 });
        }
      }
      
      // Load backlinks
      await this.loadBacklinks(note.name);
      
      // Update UI
      this.updateNoteHeader();
      this.updateBacklinksPanel();
      this.updateTOCPanel();
      
      // TODO: If heading specified, implement scroll-to-heading for CM6 using scrollToLine()
      
    } catch (error) {
      console.error('[Notes] Error opening note:', error);
      this.showError(`Failed to open note: ${noteName}`);
    }
  }

  /**
   * Load backlinks for a note
   */
  async loadBacklinks(noteName) {
    try {
      const response = await fetch(
        `http://127.0.0.1:11436/polly/notes/${encodeURIComponent(noteName)}/backlinks`
      );
      const data = await response.json();
      
      this.backlinks = data.backlinks || [];
      console.log(`[Notes] Loaded ${this.backlinks.length} backlinks for ${noteName}`);
      
    } catch (error) {
      console.error('[Notes] Error loading backlinks:', error);
      this.backlinks = [];
    }
  }

  /**
   * Get all tags
   */
  async loadTags() {
    try {
      const response = await fetch('http://127.0.0.1:11436/polly/notes/tags');
      const data = await response.json();
      
      this.tags = data.tags || [];
      this.tagsStats = data.stats || {};
      
      console.log(`[Notes] Loaded ${this.tags.length} tags`);
      
      // Update tags panel
      this.updateTagsPanel();
      
    } catch (error) {
      console.error('[Notes] Error loading tags:', error);
    }
  }

  /**
   * Check sync manager status
   */
  async checkSyncStatus() {
    try {
      const response = await fetch('http://127.0.0.1:11436/polly/notes/sync/status');
      const data = await response.json();
      
      this.syncStatus = data.is_running ? 'active' : 'inactive';
      this.syncStats = data.stats || {};
      
      // Update UI
      this.updateSyncIndicator();
      
    } catch (error) {
      console.error('[Notes] Error checking sync status:', error);
      this.syncStatus = 'error';
    }
  }
  
  /**
   * Start file watcher for automatic syncing
   */
  async startFileWatcher() {
    // Don't start if already started
    if (this.fileWatcherStarted) {
      console.log('[Notes] File watcher already started, skipping');
      return;
    }
    
    try {
      console.log('[Notes] Starting file watcher...');
      
      const response = await fetch('http://127.0.0.1:11436/polly/notes/sync/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes_path: this.sourcePath,
          initial_build: false // Don't rebuild since we just loaded the index
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('[Notes] File watcher started successfully');
        this.syncStatus = 'active';
        this.fileWatcherStarted = true; // Mark as started
        this.updateSyncIndicator();
      } else {
        console.warn('[Notes] File watcher already running or failed to start:', data.message);
        this.fileWatcherStarted = true; // Mark as started even if already running
      }
      
    } catch (error) {
      console.error('[Notes] Error starting file watcher:', error);
    }
  }
  
  /**
   * Start polling sync status to detect changes
   */
  startSyncPolling() {
    // Don't start if already polling
    if (this.syncPollInterval) {
      console.log('[Notes] Sync polling already started, skipping');
      return;
    }
    
    // Poll every 5 seconds
    this.syncPollInterval = setInterval(async () => {
      const prevFilesCount = this.notes.length;
      
      // Check sync status
      await this.checkSyncStatus();
      
      // If sync is active and files have changed, reload
      if (this.syncStatus === 'active' && this.syncStats.sync_manager) {
        const filesSynced = this.syncStats.sync_manager.files_synced || 0;
        
        // If files were synced since last check, reload the index
        if (filesSynced > (this.lastFilesSynced || 0)) {
          console.log(`[Notes] Detected ${filesSynced - (this.lastFilesSynced || 0)} file changes, reloading...`);
          await this.reloadAfterSync();
          this.lastFilesSynced = filesSynced;
        }
      }
    }, 5000);
    
    console.log('[Notes] Sync polling started (every 5 seconds)');
  }
  
  /**
   * Reload notes after sync detected changes
   */
  async reloadAfterSync() {
    // Don't reload if we just saved (to prevent bouncing from our own saves)
    if (this.justSaved) {
      console.log('[Notes] Skipping reload - just saved a note');
      return;
    }
    
    // Don't reload if we're in edit mode - wait until user exits
    if (this.editorMode === 'edit') {
      console.log('[Notes] Skipping reload - currently in edit mode');
      return;
    }
    
    const currentNoteName = this.currentNote ? this.currentNote.name : null;
    const currentContent = this.editor ? this.editor.getValue() : null;
    
    // Show syncing indicator
    this.updateSyncIndicator('syncing');
    
    // Reload notes index
    await this.loadNotesIndex();
    
    // If a note was open, check if it needs reloading
    if (currentNoteName) {
      const note = this.notes.find(n => n.name === currentNoteName);
      if (note) {
        // Read the file to check if content actually changed
        const response = await window.polly.readFile(note.path);
        if (response.success && response.content !== currentContent) {
          console.log('[Notes] Note content changed, reloading...');
          // Reload the current note, preserving scroll and cursor position
          await this.openNote(currentNoteName, null, true);
        } else {
          console.log('[Notes] Note content unchanged, skipping reload');
        }
      } else {
        // Note was deleted, clear editor
        console.log('[Notes] Current note was deleted');
        this.currentNote = null;
        this.updateNoteHeader();
      }
    }
    
    // Reload backlinks if panel is visible
    if (this.currentNote) {
      await this.loadBacklinks(this.currentNote.name);
      this.updateBacklinksPanel();
    }
    
    console.log('[Notes] Reload after sync complete');
  }

  /**
   * Setup CodeMirror 6 editor
   */
  setupEditor() {
    console.log('[Notes] setupEditor called - using CodeMirror 6');
    const editorContainer = document.getElementById('notes-editor');
    
    if (!editorContainer) {
      console.warn('[Notes] Editor container not found');
      return;
    }
    
    // Check if CodeMirror 6 bundle is loaded
    if (typeof MarkdownEditorCM6 === 'undefined' || !MarkdownEditorCM6.MarkdownEditor) {
      console.error('[Notes] CodeMirror 6 bundle not loaded, using fallback');
      this.setupFallbackEditor(editorContainer);
      return;
    }
    
    // Clear container and create CodeMirror editor
    editorContainer.innerHTML = '';
    
    // Create the CodeMirror 6 editor
    try {
      this.cm6Editor = new MarkdownEditorCM6.MarkdownEditor(editorContainer, {
        initialContent: '',
        theme: 'dark',
        autoSave: true,
        autoSaveDelay: 2000,
        onChange: (content) => {
          this.hasUnsavedChanges = true;
          this.updateSaveStatus('unsaved');
          
          // Update TOC with debounce
          if (this.tocUpdateTimeout) {
            clearTimeout(this.tocUpdateTimeout);
          }
          this.tocUpdateTimeout = setTimeout(() => {
            this.updateTOCPanel();
          }, 500); // Update TOC 500ms after user stops typing
        },
        onSave: async (content) => {
          await this.saveCurrentNote();
        },
        onWikiLinkClick: (noteName) => {
          // Handle wiki link clicks
          console.log('[Notes] Wiki link clicked in editor:', noteName);
          this.openNote(noteName);
        }
      });
      
      // Set editor mode to 'edit' since CM6 is always in edit mode
      this.editorMode = 'edit';
      console.log('[Notes] Editor mode set to: edit (CM6 is always editable)');
      
      console.log('[Notes] CodeMirror 6 editor initialized successfully');
      
      // Create editor interface for compatibility with existing code
      this.editor = {
        setValue: (value) => {
          if (this.cm6Editor) {
            this.cm6Editor.setValue(value);
          }
        },
        getValue: () => {
          return this.cm6Editor ? this.cm6Editor.getValue() : '';
        },
        focus: () => {
          if (this.cm6Editor) {
            this.cm6Editor.focus();
          }
        },
        getCursorPosition: () => {
          return this.cm6Editor ? this.cm6Editor.getCursorPosition() : 0;
        },
        setCursorPosition: (pos) => {
          if (this.cm6Editor) {
            this.cm6Editor.setCursorPosition(pos);
          }
        },
        insertText: (text) => {
          if (this.cm6Editor) {
            this.cm6Editor.insertText(text);
          }
        },
        replaceSelection: (text) => {
          if (this.cm6Editor) {
            this.cm6Editor.replaceSelection(text);
          }
        },
        getSelection: () => {
          return this.cm6Editor ? this.cm6Editor.getSelection() : { from: 0, to: 0, text: '' };
        },
        getScrollPosition: () => {
          // Get current scroll position from CodeMirror 6
          if (this.cm6Editor && this.cm6Editor.view) {
            const scroller = this.cm6Editor.view.scrollDOM;
            if (scroller) {
              return { scrollTop: scroller.scrollTop };
            }
          }
          return { scrollTop: 0 };
        },
        setScrollPosition: ({ scrollTop }) => {
          // CodeMirror 6 handles scrolling automatically
          if (this.cm6Editor && this.cm6Editor.view) {
            const scroller = this.cm6Editor.view.scrollDOM;
            if (scroller) {
              scroller.scrollTop = scrollTop;
            }
          }
        }
      };
      
    } catch (error) {
      console.error('[Notes] Error initializing CodeMirror 6:', error);
      // Fallback to basic textarea if CM6 fails
      this.setupFallbackEditor(editorContainer);
    }
    
    console.log('[Notes] Editor initialized');
  }
  
  /**
   * Fallback to basic textarea if CodeMirror fails
   */
  setupFallbackEditor(editorContainer) {
    console.warn('[Notes] Using fallback textarea editor');
    editorContainer.innerHTML = `
      <textarea id="notes-editor-textarea" class="notes-editor-textarea" style="width: 100%; height: 100%; display: block;"></textarea>
    `;
    
    const textarea = document.getElementById('notes-editor-textarea');
    
    this.editor = {
      setValue: (value) => { textarea.value = value; },
      getValue: () => textarea.value,
      focus: () => textarea.focus(),
      getCursorPosition: () => textarea.selectionStart,
      setCursorPosition: (pos) => {
        textarea.selectionStart = pos;
        textarea.selectionEnd = pos;
      },
      insertText: (text) => {
        const pos = textarea.selectionStart;
        const before = textarea.value.substring(0, pos);
        const after = textarea.value.substring(pos);
        textarea.value = before + text + after;
        textarea.selectionStart = pos + text.length;
        textarea.selectionEnd = pos + text.length;
      },
      replaceSelection: (text) => {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const before = textarea.value.substring(0, start);
        const after = textarea.value.substring(end);
        textarea.value = before + text + after;
        textarea.selectionStart = start + text.length;
        textarea.selectionEnd = start + text.length;
      },
      getSelection: () => {
        return {
          from: textarea.selectionStart,
          to: textarea.selectionEnd,
          text: textarea.value.substring(textarea.selectionStart, textarea.selectionEnd)
        };
      }
    };
    
    // Add change listener
    textarea.addEventListener('input', () => {
      this.hasUnsavedChanges = true;
      this.updateSaveStatus('unsaved');
      this.scheduleAutoSave();
    });
  }



  /**
   * Fetch embedded note content
   */
  async fetchEmbeddedNote(noteName, section = null) {
    try {
      console.log(`[Notes] Fetching embedded note: "${noteName}"`);
      
      // Find the note in our cached index
      const note = this.notes.find(n => 
        n.name === noteName || 
        n.title === noteName ||
        (n.aliases && n.aliases.includes(noteName))
      );
      
      if (!note) {
        console.warn(`[Notes] Embedded note not found in index: "${noteName}"`);
        console.log('[Notes] Available notes:', this.notes.map(n => ({ name: n.name, title: n.title })));
        return null;
      }
      
      console.log(`[Notes] Found note in index:`, { name: note.name, title: note.title, path: note.path });
      
      // Read the note content
      const response = await window.polly.readFile(note.path);
      
      if (!response.success) {
        console.error(`[Notes] Failed to read embedded note file: ${response.error}`);
        return null;
      }
      
      const content = response.content;
      
      if (!content) {
        console.warn(`[Notes] Embedded note has no content: ${noteName}`);
        return null;
      }
      
      // Remove frontmatter
      let processed = content.replace(/^---\n[\s\S]*?\n---\n/, '');
      
      // If a section is specified, extract just that section
      if (section) {
        processed = this.extractSection(processed, section);
      }
      
      console.log(`[Notes] Successfully fetched embedded note: "${noteName}"`);
      return processed;
      
    } catch (error) {
      console.error(`[Notes] Error fetching embedded note ${noteName}:`, error);
      return null;
    }
  }
  
  /**
   * Extract a specific section from markdown content
   */
  extractSection(markdown, sectionHeading) {
    const lines = markdown.split('\n');
    const sectionRegex = new RegExp(`^#+\\s+${sectionHeading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`, 'i');
    
    let startIndex = -1;
    let endIndex = lines.length;
    let sectionLevel = 0;
    
    // Find the start of the section
    for (let i = 0; i < lines.length; i++) {
      if (sectionRegex.test(lines[i])) {
        startIndex = i;
        sectionLevel = (lines[i].match(/^#+/) || [''])[0].length;
        break;
      }
    }
    
    if (startIndex === -1) {
      return `Section "${sectionHeading}" not found`;
    }
    
    // Find the end of the section (next heading of same or higher level)
    for (let i = startIndex + 1; i < lines.length; i++) {
      const headingMatch = lines[i].match(/^(#+)\s/);
      if (headingMatch && headingMatch[1].length <= sectionLevel) {
        endIndex = i;
        break;
      }
    }
    
    // Extract the section (excluding the heading itself)
    return lines.slice(startIndex + 1, endIndex).join('\n');
  }
  
  /**
   * Resolve image path for Obsidian vault
   */
  resolveImagePath(imagePath) {
    // If it's already an absolute path or URL, return as-is
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://') || imagePath.startsWith('/')) {
      return imagePath;
    }
    
    // For Obsidian vaults, images can be in various locations
    // Common patterns:
    // - Same folder as note
    // - Attachments folder at vault root
    // - Subdirectories
    
    // For now, we'll use the vault base path + image path
    // This works if images are at vault root or in subfolders
    const vaultPath = window.pollyNotesVaultPath || '';
    
    if (vaultPath) {
      // Convert to file:// URL for Electron
      const fullPath = `${vaultPath}/${imagePath}`;
      return `file://${fullPath}`;
    }
    
    return imagePath;
  }
  
  /**
   * Slugify heading text for ID generation
   * Converts "My Section Title" to "my-section-title"
   */
  slugifyHeading(text) {
    // Handle undefined, null, or empty text
    if (!text || typeof text !== 'string') {
      return 'heading-' + Math.random().toString(36).substr(2, 9);
    }
    
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '') // Remove special chars
      .replace(/\s+/g, '-')      // Spaces to hyphens
      .replace(/-+/g, '-')       // Multiple hyphens to single
      .trim();
  }




  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('notes-search-input');
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          this.searchNotes(e.target.value);
        }, 300); // Debounce 300ms
      });
    }
    
    // Collapsible panel headers
    document.querySelectorAll('.notes-panel-header.collapsible').forEach(header => {
      header.addEventListener('click', () => {
        const panel = header.closest('.notes-panel');
        panel.classList.toggle('collapsed');
        
        // Re-initialize Lucide icons for the chevron
        if (typeof lucide !== 'undefined') {
          lucide.createIcons();
        }
      });
    });
    
    // Right sidebar toggle
    const sidebarToggle = document.getElementById('notes-sidebar-toggle');
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        const sidebar = document.querySelector('.notes-right-sidebar');
        sidebar.classList.toggle('collapsed');
        
        // Re-initialize Lucide icons for the chevron
        if (typeof lucide !== 'undefined') {
          lucide.createIcons();
        }
      });
    }
    
    // New "+" dropdown button in sidebar
    const addBtn = document.getElementById('notes-add-btn');
    const addMenu = document.getElementById('notes-add-menu');
    const newNoteMenuItem = document.getElementById('notes-menu-new-note');
    const newFolderMenuItem = document.getElementById('notes-menu-new-folder');
    
    if (addBtn && addMenu) {
      // Toggle dropdown
      addBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isVisible = addMenu.style.display !== 'none';
        addMenu.style.display = isVisible ? 'none' : 'block';
        
        // Re-initialize icons when showing menu
        if (!isVisible && typeof lucide !== 'undefined') {
          setTimeout(() => lucide.createIcons(), 10);
        }
      });
      
      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
        if (addMenu && !addMenu.contains(e.target) && e.target !== addBtn) {
          addMenu.style.display = 'none';
        }
      });
      
      // New Note menu item
      if (newNoteMenuItem) {
        newNoteMenuItem.addEventListener('click', () => {
          addMenu.style.display = 'none';
          this.showCreateNoteModal();
        });
      }
      
      // New Folder menu item
      if (newFolderMenuItem) {
        newFolderMenuItem.addEventListener('click', () => {
          addMenu.style.display = 'none';
          this.showCreateFolderModal();
        });
      }
    }
    
    // Quick switcher (Cmd+O)
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'o') {
        e.preventDefault();
        this.openQuickSwitcher();
      }
    });
  }

  /**
   * Update the browse list (graph-based flat list) -  replaces updateFileTree()
   * 
   * @param {HTMLElement} container - Target container element
   * @param {Object} options - Configuration options
   * @param {string} options.sort - Sort mode ('authority', 'recent', 'alpha', 'created')
   * @param {string} options.domain - Domain filter
   * @param {string} options.type - Type filter (comma-separated: "note,conversation")
   * @param {number} options.maturity - Maturity filter (10, 20, 30)
   * @param {string} options.connectionStatus - Connection status filter ('hub', 'bridge', 'isolated', 'all')
   * @param {string} options.q - Search query
   * @param {Function} options.onItemClick - Click handler for items
   */
  async updateBrowseList(container, options = {}) {
    if (!container) {
      console.error('[Notes] updateBrowseList: container not provided');
      return;
    }

    console.log('[Notes] updateBrowseList: starting with options:', options);

    const {
      sort = 'recent',
      domain = null,
      type = null,
      maturity = null,
      connectionStatus = null,
      q = null,
      tag = null,
      onItemClick = null
    } = options;

    // Show loading state
    container.innerHTML = `
      <div class="browse-list-loading" style="padding: 24px; text-align: center; color: var(--text-secondary);">
        <div class="loading-spinner" style="font-size: 13px;">Loading...</div>
      </div>
    `;

    try {
      // Build query params
      const params = new URLSearchParams();
      params.append('sort', sort);
      params.append('limit', '100');
      
      if (domain) params.append('domain', domain);
      if (type) params.append('type', type);
      if (maturity) params.append('maturity', maturity.toString());
      if (connectionStatus) params.append('connection_status', connectionStatus);
      if (q) params.append('q', q);
      if (tag) params.append('tag', tag);

      console.log('[Notes] updateBrowseList: fetching from /polly/graph/list with params:', params.toString());

      // Fetch from /polly/graph/list
      const response = await fetch(`http://127.0.0.1:11436/polly/graph/list?${params.toString()}`);
      console.log('[Notes] updateBrowseList: fetch completed with status:', response.status);
      
      if (!response.ok) {
        console.warn('[Notes] /polly/graph/list returned', response.status, '- falling back to notes list');
        // Fallback: use the notes list we already have
        const items = this.notes.map(note => ({
          id: note.name,
          name: note.title || note.name,
          type: 'note',
          primary_domain: note.domain || '',
          secondary_domains: [],
          authority_score: 0,
          connection_count: 0,
          inbound_count: 0,
          outbound_count: 0,
          connection_status: 'normal',
          maturity: 20,
          tags: note.tags || [],
          updated_at: note.modified,
          created_at: note.created,
          path: note.path,
          preview_snippet: ''
        }));
        console.log('[Notes] Using fallback notes list:', items.length, 'items');
        this.renderBrowseItems(container, items, onItemClick);
        return;
      }

      const data = await response.json();
      console.log('[Notes] updateBrowseList: received', data.items?.length || 0, 'items');
      const items = data.items || [];

      // Handle empty state
      if (items.length === 0) {
        container.innerHTML = `
          <div class="browse-list-empty" style="padding: 24px; text-align: center; color: var(--text-secondary);">
            <i data-lucide="search-x" style="width: 48px; height: 48px; margin: 0 auto 16px; opacity: 0.3; display: block;"></i>
            <p style="font-size: 13px; margin: 0;">No items match filters</p>
            ${(domain || type || maturity || connectionStatus || q) ? 
              '<button class="btn-reset-filters" style="margin-top: 12px; padding: 6px 12px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); cursor: pointer; font-size: 12px;">Reset Filters</button>' : 
              '<p style="font-size: 11px; margin: 8px 0 0; opacity: 0.7;">No notes found in the index.</p>'}
          </div>
        `;
        
        // Re-initialize icons
        if (typeof lucide !== 'undefined') {
          lucide.createIcons();
        }
        
        // Wire reset filters button
        const resetBtn = container.querySelector('.btn-reset-filters');
        if (resetBtn) {
          resetBtn.addEventListener('click', () => {
            this.updateBrowseList(container, { sort });
          });
        }
        
        return;
      }

      // Render items
      this.renderBrowseItems(container, items, onItemClick);

    } catch (error) {
      console.error('[Notes] updateBrowseList failed:', error);
      container.innerHTML = `
        <div class="browse-list-error" style="padding: 24px; text-align: center; color: var(--text-error);">
          <i data-lucide="alert-circle" style="width: 32px; height: 32px; margin: 0 auto 12px; display: block;"></i>
          <p style="font-size: 13px; margin: 0;">Failed to load items</p>
          <p style="font-size: 11px; margin: 8px 0 0; opacity: 0.7;">${error.message}</p>
        </div>
      `;
      
      if (typeof lucide !== 'undefined') {
        lucide.createIcons();
      }
    }
  }

  /**
   * Get icon for content type
   */
  getTypeIcon(type) {
    const icons = {
      'note': '●',           // circle
      'conversation': '◆',   // diamond
      'book': '⬢',          // hexagon
      'capture': '▲',       // triangle
      'code': '■'           // square
    };
    return icons[type] || '●';
  }

  /**
   * Render browse items to container
   */
  renderBrowseItems(container, items, onItemClick = null) {
    let html = '<div class="browse-list">';
    
    for (const item of items) {
      const typeIcon = this.getTypeIcon(item.type);
      const date = item.updated_at ? new Date(item.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '';
      const authorityBadge = item.authority_score >= 0.7 ? '⭐' : (item.authority_score >= 0.4 ? '✦' : '');
      const secondaryDomainDots = item.secondary_domains && item.secondary_domains.length > 0 
        ? item.secondary_domains.slice(0, 3).map(d => `<span class="domain-dot" title="${d}">●</span>`).join('')
        : '';

      html += `
        <div class="browse-list-item" data-note-name="${item.id}" data-path="${item.path}" data-type="${item.type}">
          <div class="browse-item-main">
            <span class="browse-item-icon ${item.type}">${typeIcon}</span>
            <span class="browse-item-title">${item.name}</span>
            <span class="browse-item-date">${date}</span>
          </div>
          <div class="browse-item-meta">
            ${authorityBadge ? `<span class="browse-item-authority" title="High authority">${authorityBadge}</span>` : ''}
            ${item.connection_count > 0 ? `<span class="browse-item-connections" title="${item.connection_count} connections">${item.connection_count}⇄</span>` : ''}
            ${secondaryDomainDots ? `<span class="browse-item-domains">${secondaryDomainDots}</span>` : ''}
          </div>
        </div>
      `;
    }
    
    html += '</div>';
    container.innerHTML = html;

    // Wire click handlers
    const listItems = container.querySelectorAll('.browse-list-item');
    listItems.forEach((itemEl, index) => {
      itemEl.addEventListener('click', () => {
        if (onItemClick) {
          onItemClick(itemEl, items[index]);
        } else {
          // Default: open note
          const noteName = itemEl.dataset.noteName;
          if (noteName) {
            this.openNote(noteName);
          }
        }
      });

      // Keyboard navigation
      itemEl.setAttribute('tabindex', '0');
      itemEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          itemEl.click();
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          const next = itemEl.nextElementSibling;
          if (next) next.focus();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          const prev = itemEl.previousElementSibling;
          if (prev) prev.focus();
        }
      });
    });

    // Re-initialize icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  /**
   * Start inline rename in file tree
   */
  /**
   * Start inline rename in browse list
   */
  startInlineRename(item) {
    const noteName = item.dataset.noteName;
    const note = this.notes.find(n => n.name === noteName);
    
    if (!note) return;
    
    // Try both old (.file-name) and new (.browse-item-title) DOM structures
    const titleSpan = item.querySelector('.browse-item-title') || item.querySelector('.file-name');
    if (!titleSpan) return;
    
    const originalText = titleSpan.textContent;
    
    // Create input
    const input = document.createElement('input');
    input.type = 'text';
    input.value = note.title || note.name;
    input.className = 'browse-rename-input';
    input.style.cssText = 'flex: 1; background: #2a2a2a; border: 1px solid #4a9eff; padding: 2px 4px; color: #e0e0e0; font-size: 13px;';
    
    // Replace span with input
    titleSpan.style.display = 'none';
    titleSpan.parentNode.insertBefore(input, titleSpan.nextSibling);
    input.focus();
    input.select();
    
    const finishRename = async (save = false) => {
      if (save) {
        const newTitle = input.value.trim();
        
        if (newTitle && newTitle !== note.title && newTitle !== note.name) {
          await this.renameNote(note.name, newTitle);
        }
      }
      
      // Remove input and show span again
      input.remove();
      titleSpan.style.display = '';
    };
    
    // Enter to save, Escape to cancel
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        finishRename(true);
      } else if (e.key === 'Escape') {
        finishRename(false);
      }
    });
    
    // Blur to save
    input.addEventListener('blur', () => {
      setTimeout(() => finishRename(true), 100);
    });
    
    // Stop click from bubbling to prevent opening note
    input.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  /**
   * Move a note to a different folder
   */
  async moveNote(noteName, targetDomain, sourceDomain) {
    try {
      console.log(`[Notes] Moving "${noteName}" from "${sourceDomain}" to "${targetDomain}"`);
      
      // Show loading indicator
      const statusDiv = this.showToast(`Moving note to ${targetDomain}...`, 'info', 0);
      
      // Call API to move note
      const response = await fetch('http://127.0.0.1:11436/polly/notes/move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: noteName,
          target_domain: targetDomain
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to move note');
      }
      
      const result = await response.json();
      console.log('[Notes] Note moved successfully:', result);
      
      // Remove loading indicator
      if (statusDiv) statusDiv.remove();
      
      // Show success message
      this.showToast(`Moved "${noteName}" to ${targetDomain}`, 'success', 3000);
      
      // Reload notes index to reflect changes
      await this.loadNotesIndex();
      
      // If the moved note is currently open, update its display
      if (this.currentNote && this.currentNote.name === noteName) {
        this.currentNote.domain = targetDomain;
      }
      
    } catch (error) {
      console.error('[Notes] Failed to move note:', error);
      this.showToast(`Failed to move note: ${error.message}`, 'error', 5000);
    }
  }

  /**
   * Show a toast notification
   */
  showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 16px;
      border-radius: 4px;
      z-index: 10000;
      font-size: 13px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      gap: 8px;
    `;
    
    // Set color based on type
    switch (type) {
      case 'success':
        toast.style.background = 'var(--success-color, #98c379)';
        toast.style.color = 'var(--bg-primary)';
        break;
      case 'error':
        toast.style.background = '#ef4444';
        toast.style.color = '#fff';
        break;
      case 'info':
      default:
        toast.style.background = 'var(--bg-secondary)';
        toast.style.color = 'var(--text-primary)';
        toast.style.border = '1px solid var(--border-color)';
        break;
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Auto-remove after duration (if duration > 0)
    if (duration > 0) {
      setTimeout(() => {
        toast.remove();
      }, duration);
    }
    
    return toast;
  }

  /**
   * Update backlinks panel
   */
  updateBacklinksPanel() {
    // Target lower panel content area when backlinks tab is active
    const lowerPanel = document.querySelector('.lower-panel[data-view="notes"]');
    if (!lowerPanel) return;
    
    const content = lowerPanel.querySelector('.lower-panel-content');
    const activeTab = content?.dataset.activeTab;
    
    // Only render if backlinks tab is active
    if (!content || activeTab !== 'backlinks') return;
    
    if (this.backlinks.length === 0) {
      content.innerHTML = `
        <div class="lower-panel-empty">
          <i data-lucide="link" style="width: 24px; height: 24px;"></i>
          <p>No backlinks to this note</p>
        </div>
      `;
    } else {
      let html = '<div class="backlinks-list">';
      
      this.backlinks.forEach(backlink => {
        html += `
          <div class="backlink-item" data-note-name="${backlink.source_name}">
            <div class="backlink-header">
              <i data-lucide="arrow-left" class="backlink-icon"></i>
              <span class="backlink-name">${backlink.source_name}</span>
            </div>
            <div class="backlink-context">${this.escapeHtml(backlink.context)}</div>
          </div>
        `;
      });
      
      html += '</div>';
      content.innerHTML = html;
      
      // Add click handlers
      content.querySelectorAll('.backlink-item').forEach(item => {
        item.addEventListener('click', () => {
          const noteName = item.dataset.noteName;
          this.openNote(noteName);
        });
      });
    }
    
    // Re-initialize lucide icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  /**
   * Update tags panel
   */
  updateTagsPanel() {
    // Target lower panel content area when tags tab is active
    const lowerPanel = document.querySelector('.lower-panel[data-view="notes"]');
    if (!lowerPanel) return;
    
    const content = lowerPanel.querySelector('.lower-panel-content');
    const activeTab = content?.dataset.activeTab;
    
    // Only render if tags tab is active
    if (!content || activeTab !== 'tags') return;
    
    if (this.tags.length === 0) {
      content.innerHTML = `
        <div class="lower-panel-empty">
          <i data-lucide="tag" style="width: 24px; height: 24px;"></i>
          <p>No tags in current notes</p>
        </div>
      `;
    } else {
      let html = '<div class="tags-list">';
      
      // Show top 20 tags
      const topTags = this.tags.slice(0, 20);
      
      topTags.forEach(tag => {
        html += `
          <div class="tag-item" data-tag="${tag}">
            <i data-lucide="tag" class="tag-icon"></i>
            <span class="tag-name">#${tag}</span>
          </div>
        `;
      });
      
      html += '</div>';
      content.innerHTML = html;
      
      // Add click handlers
      content.querySelectorAll('.tag-item').forEach(item => {
        item.addEventListener('click', async () => {
          const tag = item.dataset.tag;
          await this.filterByTag(tag);
        });
      });
    }
    
    // Re-initialize lucide icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }



  /**
   * Extract headings from CodeMirror document and build TOC
   */
  updateTOCPanel() {
    console.log('[TOC] updateTOCPanel called');
    
    // Target lower panel content area when TOC tab is active
    const lowerPanel = document.querySelector('.lower-panel[data-view="notes"]');
    if (!lowerPanel) return;
    
    const content = lowerPanel.querySelector('.lower-panel-content');
    const activeTab = content?.dataset.activeTab;
    
    // Only render if TOC tab is active
    if (!content || activeTab !== 'toc') return;
    
    // Extract headings from CodeMirror document text
    if (!this.editor || !this.cm6Editor) {
      this.renderEmptyTOC(content);
      return;
    }
    
    // Get document content from CodeMirror
    const docContent = this.editor.getValue();
    if (!docContent) {
      this.renderEmptyTOC(content);
      return;
    }
    
    // Parse markdown for headings
    const lines = docContent.split('\n');
    const headings = [];
    
    lines.forEach((line, index) => {
      // Match markdown headings: # Heading, ## Heading, etc.
      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        const level = match[1].length; // Number of # characters
        const text = match[2].trim();
        const id = this.slugifyHeading(text);
        headings.push({ level, text, id, lineNumber: index + 1 });
      }
    });
    
    console.log('[TOC] Found headings:', headings.length);
    
    if (headings.length === 0) {
      this.renderEmptyTOC(content);
      return;
    }
    
    // Build TOC items
    let html = '<div id="notes-toc-list">';
    headings.forEach(heading => {
      html += `
        <div class="toc-item level-${heading.level}" data-heading-id="${heading.id}" data-line="${heading.lineNumber}">
          <span class="toc-item-text">${this.escapeHtml(heading.text)}</span>
        </div>
      `;
    });
    html += '</div>';
    
    content.innerHTML = html;
    
    // Attach click handlers
    content.querySelectorAll('.toc-item').forEach(item => {
      item.addEventListener('click', () => {
        const lineNumber = parseInt(item.dataset.line);
        this.scrollToLine(lineNumber);
      });
    });
  }

  /**
   * Render empty state for TOC
   */
  renderEmptyTOC(container) {
    container.innerHTML = `
      <div class="lower-panel-empty">
        <i data-lucide="list" style="width: 24px; height: 24px;"></i>
        <div>No headings in this note</div>
      </div>
    `;
    
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }

  /**
   * Escape HTML for safe rendering
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Scroll to a specific line in CodeMirror editor
   */
  scrollToLine(lineNumber) {
    if (!this.cm6Editor || !this.cm6Editor.view) {
      console.warn('[TOC] Cannot scroll: editor not initialized');
      return;
    }
    
    try {
      const view = this.cm6Editor.view;
      
      // Get the position at the start of the line
      const line = view.state.doc.line(lineNumber);
      const pos = line.from;
      
      // Scroll to the line with "start" alignment (line at top of viewport)
      view.dispatch({
        selection: { anchor: pos, head: pos },
        effects: view.constructor.scrollIntoView(pos, { y: "start", yMargin: 20 })
      });
      
      // Focus the editor
      view.focus();
      
      console.log('[TOC] Scrolled to line:', lineNumber);
    } catch (error) {
      console.error('[TOC] Error scrolling to line:', lineNumber, error);
    }
  }

  /**
   * Filter notes by tag
   */
  async filterByTag(tag) {
    try {
      // Update browse filters
      this.browseFilters.tag = tag;
      
      // Update browse list with tag filter
      const container = document.querySelector('#notes-browse-list');
      if (container) {
        await this.updateBrowseList(container, {
          ...this.browseFilters,
          onItemClick: (itemEl, item) => this.openNote(item.id)
        });
      } else {
        console.error('[Notes] Could not find #notes-browse-list container for tag filter');
      }
      
      // Show filter indicator
      this.showFilterIndicator(`#${tag}`);
      
    } catch (error) {
      console.error('[Notes] Error filtering by tag:', error);
    }
  }

  /**
   * Open quick switcher modal
   */
  /**
   * Open quick switcher modal
   */
  openQuickSwitcher() {
    const modal = document.getElementById('quick-switcher-modal');
    const input = document.getElementById('quick-switcher-input');
    const results = document.getElementById('quick-switcher-results');
    
    if (!modal || !input || !results) {
      console.error('[Notes] Quick switcher elements not found');
      return;
    }
    
    // Reset state
    this.quickSwitcherSelectedIndex = 0;
    input.value = '';
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Focus input
    setTimeout(() => input.focus(), 100);
    
    // Show recent/all notes by default
    this.updateQuickSwitcherResults('');
    
    // Setup event listeners if not already done
    if (!this._quickSwitcherListenersSetup) {
      this._setupQuickSwitcherListeners();
      this._quickSwitcherListenersSetup = true;
    }
    
    console.log('[Notes] Quick switcher opened');
  }

  /**
   * Setup quick switcher event listeners
   */
  _setupQuickSwitcherListeners() {
    const modal = document.getElementById('quick-switcher-modal');
    const input = document.getElementById('quick-switcher-input');
    
    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        this.closeQuickSwitcher();
      }
    });
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.closeQuickSwitcher();
      }
    });
    
    // Search input
    input.addEventListener('input', (e) => {
      this.quickSwitcherSelectedIndex = 0;
      this.updateQuickSwitcherResults(e.target.value);
    });
    
    // Keyboard navigation
    input.addEventListener('keydown', (e) => {
      const results = document.querySelectorAll('.quick-switcher-result-item');
      
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.quickSwitcherSelectedIndex = Math.min(
          this.quickSwitcherSelectedIndex + 1,
          results.length - 1
        );
        this.updateQuickSwitcherSelection();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.quickSwitcherSelectedIndex = Math.max(
          this.quickSwitcherSelectedIndex - 1,
          0
        );
        this.updateQuickSwitcherSelection();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const selectedItem = results[this.quickSwitcherSelectedIndex];
        if (selectedItem) {
          const noteName = selectedItem.dataset.noteName;
          this.openNote(noteName);
          this.closeQuickSwitcher();
        }
      }
    });
  }

  /**
   * Update quick switcher results based on search query
   */
  updateQuickSwitcherResults(query) {
    const resultsContainer = document.getElementById('quick-switcher-results');
    if (!resultsContainer) return;
    
    let filteredNotes;
    
    if (!query || query.trim() === '') {
      // Show all notes (or recent notes if we track them)
      filteredNotes = this.notes.slice(0, 50); // Limit to 50
    } else {
      // Fuzzy search through notes
      filteredNotes = this.fuzzySearchNotes(query);
    }
    
    // Render results
    if (filteredNotes.length === 0) {
      resultsContainer.innerHTML = '<div class="quick-switcher-empty">No notes found</div>';
      return;
    }
    
    let html = '';
    filteredNotes.forEach((note, index) => {
      const isSelected = index === this.quickSwitcherSelectedIndex;
      
      // Show aliases if they exist
      let aliasText = '';
      if (note.aliases && note.aliases.length > 0) {
        aliasText = `<span class="note-aliases">aka: ${note.aliases.join(', ')}</span>`;
      }
      
      html += `
        <div class="quick-switcher-result-item ${isSelected ? 'selected' : ''}" 
             data-note-name="${note.name}"
             data-index="${index}">
          <div class="quick-switcher-result-title">${this.escapeHtml(note.title || note.name)}</div>
          <div class="quick-switcher-result-meta">
            <span>📁 ${note.domain || 'No domain'}</span>
            ${note.modified ? `<span>📅 ${new Date(note.modified).toLocaleDateString()}</span>` : ''}
            ${aliasText}
          </div>
        </div>
      `;
    });
    
    resultsContainer.innerHTML = html;
    
    // Add click handlers
    resultsContainer.querySelectorAll('.quick-switcher-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const noteName = item.dataset.noteName;
        this.openNote(noteName);
        this.closeQuickSwitcher();
      });
    });
  }

  /**
   * Fuzzy search notes by name, title, and aliases
   */
  fuzzySearchNotes(query) {
    const lowerQuery = query.toLowerCase();
    const tokens = lowerQuery.split(/\s+/).filter(t => t.length > 0);
    
    // Score each note based on match quality
    const scored = this.notes.map(note => {
      let score = 0;
      const lowerTitle = (note.title || note.name).toLowerCase();
      const lowerName = note.name.toLowerCase();
      const lowerDomain = (note.domain || '').toLowerCase();
      
      // Exact matches get highest score
      if (lowerTitle === lowerQuery || lowerName === lowerQuery) {
        score += 1000;
      }
      
      // Starts with query
      if (lowerTitle.startsWith(lowerQuery) || lowerName.startsWith(lowerQuery)) {
        score += 500;
      }
      
      // Contains all tokens
      let allTokensMatch = true;
      tokens.forEach(token => {
        if (lowerTitle.includes(token)) {
          score += 100;
        } else if (lowerName.includes(token)) {
          score += 80;
        } else if (lowerDomain.includes(token)) {
          score += 50;
        } else if (note.aliases && note.aliases.some(a => a.toLowerCase().includes(token))) {
          score += 60;
        } else {
          allTokensMatch = false;
        }
      });
      
      if (!allTokensMatch) {
        score = 0;
      }
      
      return { note, score };
    });
    
    // Filter out zero scores and sort by score
    return scored
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 50) // Limit to 50 results
      .map(item => item.note);
  }

  /**
   * Update selected item in quick switcher
   */
  updateQuickSwitcherSelection() {
    const items = document.querySelectorAll('.quick-switcher-result-item');
    items.forEach((item, index) => {
      if (index === this.quickSwitcherSelectedIndex) {
        item.classList.add('selected');
        // Scroll into view
        item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      } else {
        item.classList.remove('selected');
      }
    });
  }

  /**
   * Close quick switcher modal
   */
  closeQuickSwitcher() {
    const modal = document.getElementById('quick-switcher-modal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  /**
   * Update various UI elements
   */
  updateSourceIndicator() {
    const indicator = document.getElementById('notes-source-indicator');
    if (indicator) {
      indicator.textContent = this.source === 'native' ? '📝 Native' : '📚 Obsidian';
    }
  }

  updateSyncIndicator(status = null) {
    const indicator = document.getElementById('notes-sync-indicator');
    if (indicator) {
      const currentStatus = status || this.syncStatus;
      
      let statusText = '';
      switch (currentStatus) {
        case 'active':
          statusText = '🟢 Auto-sync';
          break;
        case 'syncing':
          statusText = '🔄 Syncing...';
          break;
        case 'error':
          statusText = '🔴 Error';
          break;
        default:
          statusText = '⚪ Idle';
      }
      
      indicator.textContent = statusText;
    }
  }

  updateLoadingState() {
    const loader = document.getElementById('notes-loader');
    if (loader) {
      loader.style.display = this.isLoading ? 'block' : 'none';
    }
  }

  updateNoteHeader() {
    const header = document.getElementById('notes-current-note-header');
    if (header && this.currentNote) {
      header.innerHTML = `
        <div class="note-header-title">
          <h2 class="note-title-display" id="note-title-display">${this.currentNote.title || this.currentNote.name}</h2>
          <input 
            type="text" 
            class="note-title-input hidden" 
            id="note-title-input"
            value="${this.escapeHtml(this.currentNote.title || this.currentNote.name)}"
          >
          <button class="btn-icon" id="edit-title-btn" title="Edit title">
            <i data-lucide="edit-2" style="width: 16px; height: 16px;"></i>
          </button>
        </div>
        <div class="note-meta">
          <span>${this.currentNote.domain || 'No domain'}</span>
          ${this.currentNote.tags ? this.currentNote.tags.map(t => `<span class="tag">#${t}</span>`).join('') : ''}
        </div>
      `;
      
      // Re-initialize icons
      if (typeof lucide !== 'undefined') {
        lucide.createIcons();
      }
      
      // Setup title editing
      this.setupTitleEditing();
    }
  }

  /**
   * Setup title editing in note header
   */
  setupTitleEditing() {
    const displayEl = document.getElementById('note-title-display');
    const inputEl = document.getElementById('note-title-input');
    const editBtn = document.getElementById('edit-title-btn');
    
    if (!displayEl || !inputEl || !editBtn) return;
    
    const enterEditMode = () => {
      displayEl.classList.add('hidden');
      editBtn.classList.add('hidden');
      inputEl.classList.remove('hidden');
      inputEl.focus();
      inputEl.select();
    };
    
    const exitEditMode = async (save = false) => {
      if (save && this.currentNote) {
        const newTitle = inputEl.value.trim();
        
        if (newTitle && newTitle !== this.currentNote.title && newTitle !== this.currentNote.name) {
          await this.renameNote(this.currentNote.name, newTitle);
        }
      }
      
      inputEl.classList.add('hidden');
      displayEl.classList.remove('hidden');
      editBtn.classList.remove('hidden');
    };
    
    // Click edit button or click title to edit
    editBtn.addEventListener('click', enterEditMode);
    displayEl.addEventListener('click', enterEditMode);
    
    // Enter to save
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        exitEditMode(true);
      } else if (e.key === 'Escape') {
        inputEl.value = this.currentNote.title || this.currentNote.name;
        exitEditMode(false);
      }
    });
    
    // Blur to save
    inputEl.addEventListener('blur', () => {
      // Small delay to allow button clicks to register
      setTimeout(() => exitEditMode(true), 100);
    });
  }

  /**
   * Rename a note
   */
  async renameNote(oldName, newTitle) {
    try {
      console.log(`[Notes] Renaming "${oldName}" to "${newTitle}"`);
      
      // Show loading
      const toast = this.showToast(`Renaming note and updating references...`, 'info', 0);
      
      // Call API
      const response = await fetch('http://127.0.0.1:11436/polly/notes/rename', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          old_name: oldName,
          new_name: newTitle
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to rename note');
      }
      
      const result = await response.json();
      console.log('[Notes] Note renamed:', result);
      
      // Remove loading toast
      if (toast) toast.remove();
      
      // Show success with reference count
      const refCount = result.note.references_updated || 0;
      let successMsg = `Renamed to "${result.note.new_name}"`;
      if (refCount > 0) {
        successMsg += ` (updated ${refCount} reference${refCount !== 1 ? 's' : ''})`;
      }
      this.showToast(successMsg, 'success', 4000);
      
      // Update current note
      this.currentNote.name = result.note.new_name;
      this.currentNote.title = result.note.title;
      
      // Reload notes index
      await this.loadNotesIndex();
      
      // Update header display
      this.updateNoteHeader();
      
    } catch (error) {
      console.error('[Notes] Failed to rename note:', error);
      this.showToast(`Failed to rename: ${error.message}`, 'error', 5000);
    }
  }

  updateSearchResults() {
    const container = document.getElementById('notes-search-results');
    
    if (!container) return;
    
    if (this.searchResults.length === 0) {
      container.innerHTML = '';
      container.style.display = 'none';
      return;
    }
    
    let html = '<div class="search-results-list">';
    
    this.searchResults.forEach(result => {
      html += `
        <div class="search-result-item" data-note-name="${result.name}">
          <div class="result-title">${result.title || result.name}</div>
          <div class="result-meta">
            <span>${result.domain || 'No domain'}</span>
            ${result.modified ? `<span>${new Date(result.modified).toLocaleDateString()}</span>` : ''}
          </div>
        </div>
      `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    container.style.display = 'block';
    
    // Add click handlers
    container.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const noteName = item.dataset.noteName;
        this.openNote(noteName);
        container.style.display = 'none';
      });
    });
  }

  showError(message) {
    console.error(`[Notes] ${message}`);
    if (typeof showToast === 'function') {
      showToast(message, 'error');
    }
  }

  showFilterIndicator(filter) {
    const indicator = document.getElementById('notes-filter-indicator');
    if (indicator) {
      indicator.textContent = `Filtered by: ${filter}`;
      indicator.style.display = 'block';
      
      // Add clear button
      const clearBtn = document.createElement('button');
      clearBtn.textContent = '×';
      clearBtn.onclick = () => {
        this.loadNotesIndex();
        indicator.style.display = 'none';
      };
      indicator.appendChild(clearBtn);
    }
  }

  /**
   * Normalize content for change detection (line endings only; no trim to avoid losing intentional changes).
   */
  _normalizeContentForCompare(content) {
    if (content == null) return '';
    return String(content).replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  }

  onEditorChange() {
    // Mark as unsaved and trigger debounced auto-save
    this.hasUnsavedChanges = true;
    this.updateSaveStatus('unsaved');
    
    // Clear existing timeout
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
    
    // Set new timeout for auto-save
    this.saveTimeout = setTimeout(() => {
      this.saveCurrentNote();
    }, this.autoSaveDelay);
  }

  /**
   * Save the current note
   */
  async saveCurrentNote() {
    if (!this.currentNote) {
      console.warn('[Notes] No current note to save');
      return;
    }
    
    // Get content from editor (works with both CM6 and fallback)
    if (!this.editor) {
      console.error('[Notes] Editor not initialized');
      return;
    }
    
    const content = this.editor.getValue();
    const normalized = this._normalizeContentForCompare(content);
    
    // Change detection: skip save when content is unchanged (avoids redundant PUTs and reloads)
    if (this.lastSavedContent !== null && normalized === this.lastSavedContent) {
      this.hasUnsavedChanges = false;
      this.updateSaveStatus('saved');
      setTimeout(() => { if (this.saveStatus === 'saved') this.updateSaveStatus(null); }, 1500);
      return;
    }
    
    // Update status to saving
    this.updateSaveStatus('saving');
    
    try {
      const response = await fetch('http://127.0.0.1:11436/polly/notes/update', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          path: this.currentNote.path,
          content: content
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save note');
      }
      
      const result = await response.json();
      console.log('[Notes] Note saved:', result.note ?? result);
      
      // Update current note metadata if server returned it
      if (result.note && result.note.modified != null && this.currentNote) {
        this.currentNote.modified = result.note.modified;
      }
      
      // Mark as saved and remember content so we don't re-save unchanged
      this.hasUnsavedChanges = false;
      this.lastSavedContent = this._normalizeContentForCompare(content);
      this.updateSaveStatus('saved');
      
      // Set flag to prevent reload from our own save
      this.justSaved = true;
      setTimeout(() => {
        this.justSaved = false;
      }, 6000); // Clear flag after 6 seconds (longer than sync interval)
      
      // Hide save status after 2 seconds
      setTimeout(() => {
        if (this.saveStatus === 'saved') {
          this.updateSaveStatus(null);
        }
      }, 2000);
      
    } catch (error) {
      console.error('[Notes] Failed to save note:', error);
      this.updateSaveStatus('error');
      this.showError(`Failed to save: ${error.message}`);
      
      // Keep error visible for 5 seconds
      setTimeout(() => {
        if (this.saveStatus === 'error') {
          this.updateSaveStatus('unsaved');
        }
      }, 5000);
    }
  }

  /**
   * Update save status indicator
   */
  updateSaveStatus(status) {
    this.saveStatus = status;
    const statusEl = document.getElementById('notes-save-status');
    
    if (!statusEl) return;
    
    if (!status) {
      statusEl.style.display = 'none';
      return;
    }
    
    statusEl.style.display = 'inline';
    
    switch (status) {
      case 'unsaved':
        statusEl.textContent = '● Unsaved';
        statusEl.style.color = 'var(--text-secondary, #888)';
        break;
      case 'saving':
        statusEl.textContent = '⏳ Saving...';
        statusEl.style.color = 'var(--text-primary, #fff)';
        break;
      case 'saved':
        statusEl.textContent = '✓ Saved';
        statusEl.style.color = 'var(--success-color, #98c379)';
        break;
      case 'error':
        statusEl.textContent = '✗ Error';
        statusEl.style.color = 'var(--error-color, #e06c75)';
        break;
    }
  }

  /**
   * Show note creation modal
   */
  async showCreateNoteModal(prefillName = '') {
    const modal = document.getElementById('note-creation-modal');
    const nameInput = document.getElementById('note-name-input');
    const folderSelect = document.getElementById('note-folder-select');
    const templateSelect = document.getElementById('note-template-select');
    const contentInput = document.getElementById('note-content-input');
    const errorDiv = document.getElementById('note-creation-error');
    
    if (!modal || !nameInput || !folderSelect || !contentInput) {
      console.error('[Notes] Modal elements not found');
      return;
    }
    
    // Prefill name if provided
    nameInput.value = prefillName;
    
    // Load folders
    try {
      const response = await fetch('http://127.0.0.1:11436/polly/notes/folders');
      const data = await response.json();
      
      folderSelect.innerHTML = '<option value="">Select a folder...</option>';
      data.folders.forEach(folder => {
        const option = document.createElement('option');
        option.value = folder;
        option.textContent = folder;
        folderSelect.appendChild(option);
      });
      
      // Pre-select default: use activeDomainFilter if set, otherwise first folder
      if (this.activeDomainFilter && data.folders.includes(this.activeDomainFilter)) {
        folderSelect.value = this.activeDomainFilter;
      } else if (data.folders.length > 0) {
        // Default to first folder alphabetically
        folderSelect.value = data.folders[0];
      }
      
    } catch (error) {
      console.error('[Notes] Failed to load folders:', error);
      errorDiv.textContent = 'Failed to load folders';
      errorDiv.classList.remove('hidden');
    }
    
    // Load templates (Phase 16e)
    if (templateSelect) {
      try {
        const response = await fetch('http://127.0.0.1:11436/polly/templates');
        const data = await response.json();
        
        templateSelect.innerHTML = '<option value="">No template (blank note)</option>';
        
        if (data.templates && data.templates.length > 0) {
          data.templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.filename;
            option.textContent = `${template.name} - ${template.description}`;
            option.dataset.template = JSON.stringify(template);
            templateSelect.appendChild(option);
          });
        }
        
      } catch (error) {
        console.error('[Notes] Failed to load templates:', error);
        // Non-critical error, just log it
      }
    }
    
    // Clear previous content and errors
    contentInput.value = '';
    errorDiv.classList.add('hidden');
    
    // Hide similar notes warning (Phase 21)
    const warningDiv = document.getElementById('similar-notes-warning');
    if (warningDiv) {
      warningDiv.classList.add('hidden');
    }
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Focus name input
    setTimeout(() => nameInput.focus(), 100);
    
    // Setup modal event listeners (only once)
    if (!this._noteCreationListenersSetup) {
      this._setupNoteCreationListeners();
      this._noteCreationListenersSetup = true;
    }
  }

  /**
   * Setup note creation modal event listeners
   */
  _setupNoteCreationListeners() {
    const modal = document.getElementById('note-creation-modal');
    const closeBtn = document.getElementById('close-note-creation');
    const cancelBtn = document.getElementById('cancel-note-creation');
    const createBtn = document.getElementById('create-note-button');
    
    // Close modal handlers
    const closeModal = () => {
      modal.classList.add('hidden');
    };
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });
    
    // Create note handler
    createBtn.addEventListener('click', async () => {
      await this.createNote();
    });
    
    // Enter to submit
    document.getElementById('note-name-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.createNote();
      }
    });
    
    // Update title in template when name changes (Phase 16e)
    document.getElementById('note-name-input').addEventListener('input', (e) => {
      const templateSelect = document.getElementById('note-template-select');
      const contentInput = document.getElementById('note-content-input');
      
      // Only update if a template is selected and content has template markers
      if (templateSelect && templateSelect.value && contentInput.value.includes('_[')) {
        // Re-render template with new title
        this._handleTemplateSelection(templateSelect.value);
      }
    });
    
    // Template selection handler (Phase 16e)
    const templateSelect = document.getElementById('note-template-select');
    if (templateSelect) {
      templateSelect.addEventListener('change', async (e) => {
        await this._handleTemplateSelection(e.target.value);
      });
    }
  }
  
  /**
   * Handle template selection (Phase 16e)
   * Load template and populate content textarea
   */
  async _handleTemplateSelection(templateFilename) {
    const nameInput = document.getElementById('note-name-input');
    const contentInput = document.getElementById('note-content-input');
    
    if (!templateFilename) {
      // No template selected, clear content
      contentInput.value = '';
      return;
    }
    
    try {
      // Load template from API
      const response = await fetch(`http://127.0.0.1:11436/polly/templates/${templateFilename}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load template: ${response.statusText}`);
      }
      
      const template = await response.json();
      
      // Get note name for title substitution
      const noteName = nameInput.value.trim() || 'Untitled Note';
      
      // Render template with basic substitutions
      let content = template.markdown_content;
      
      // Replace {{title}} with note name
      content = content.replace(/\{\{title\}\}/g, noteName);
      
      // Replace {{date}} with today's date
      const today = new Date().toISOString().split('T')[0];
      content = content.replace(/\{\{date\}\}/g, today);
      
      // Replace other common variables with placeholder text
      content = content.replace(/\{\{([^}]+)\}\}/g, (match, varName) => {
        // Leave placeholders for user to fill in
        return `_[${varName}]_`;
      });
      
      // Set content
      contentInput.value = content;
      
      console.log('[Notes] Template loaded:', template.name);
      
    } catch (error) {
      console.error('[Notes] Failed to load template:', error);
      // Show error but don't block user
      contentInput.value = `# ${nameInput.value.trim() || 'Note'}\n\nFailed to load template. Starting with blank note.`;
    }
  }

  /**
   * Create a new note
   */
  async createNote() {
    const nameInput = document.getElementById('note-name-input');
    const folderSelect = document.getElementById('note-folder-select');
    const contentInput = document.getElementById('note-content-input');
    const errorDiv = document.getElementById('note-creation-error');
    const modal = document.getElementById('note-creation-modal');
    const createBtn = document.getElementById('create-note-button');
    
    const name = nameInput.value.trim();
    const folder = folderSelect.value;
    const content = contentInput.value.trim();
    
    // Validation
    if (!name) {
      errorDiv.textContent = 'Note name is required';
      errorDiv.classList.remove('hidden');
      nameInput.focus();
      return;
    }
    
    if (!folder) {
      errorDiv.textContent = 'Please select a folder';
      errorDiv.classList.remove('hidden');
      folderSelect.focus();
      return;
    }
    
    // Disable button while creating
    createBtn.disabled = true;
    createBtn.textContent = 'Creating...';
    errorDiv.classList.add('hidden');
    
    try {
      // Create note via API (with duplicate checking enabled)
      const response = await fetch('http://127.0.0.1:11436/polly/notes/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name,
          domain: folder,
          content: content || `# ${name}\n\n`,
          check_duplicates: true  // Enable dedup checking (Phase 21)
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create note');
      }
      
      const result = await response.json();
      
      // Check if similar notes were found (Phase 21)
      if (result.status === 'similar_found') {
        console.log('[Notes] Similar notes found:', result.similar_notes);
        this.showSimilarNotesWarning(result.similar_notes, result.proposed_note);
        createBtn.disabled = false;
        createBtn.textContent = 'Create Note';
        return;
      }
      
      // No duplicates - note created successfully
      console.log('[Notes] Note created:', result.note);
      
      // Reload notes index to include new note
      await this.loadNotesIndex();
      
      // Close modal
      modal.classList.add('hidden');
      
      // Open the newly created note (use small delay to ensure UI updates)
      setTimeout(() => {
        this.openNote(result.note.name);
        // Switch to edit mode so user can immediately start editing
        setTimeout(() => {
          this.enterEditMode();
        }, 100);
      }, 100);
      
    } catch (error) {
      console.error('[Notes] Failed to create note:', error);
      errorDiv.textContent = error.message || 'Failed to create note';
      errorDiv.classList.remove('hidden');
    } finally {
      createBtn.disabled = false;
      createBtn.textContent = 'Create Note';
    }
  }

  /**
   * Show similar notes warning with actions (Phase 21)
   */
  showSimilarNotesWarning(similarNotes, proposedNote) {
    const warningDiv = document.getElementById('similar-notes-warning');
    const countSpan = document.getElementById('similar-notes-count');
    const listDiv = document.getElementById('similar-notes-list');
    
    if (!warningDiv || !countSpan || !listDiv) {
      console.error('[Notes] Similar notes warning elements not found');
      return;
    }
    
    // Update count
    countSpan.textContent = similarNotes.length;
    
    // Clear previous list
    listDiv.innerHTML = '';
    
    // Store proposed note for later use
    this.proposedNote = proposedNote;
    this.selectedSimilarNote = null;
    
    // Populate list with similar notes
    similarNotes.forEach((note, index) => {
      const card = document.createElement('div');
      card.className = 'similar-note-card';
      card.dataset.index = index;
      
      // Determine badge style based on similarity
      const badgeClass = note.similarity >= 0.90 ? 'high' : 'medium';
      const similarityPercent = Math.round(note.similarity * 100);
      
      card.innerHTML = `
        <div class="similar-note-card-content">
          <div class="similar-note-card-title">
            <span>${note.title}</span>
            <span class="similarity-badge ${badgeClass}">${similarityPercent}% similar</span>
          </div>
          <div class="similar-note-card-path">${note.domain}/${note.name}</div>
          <p class="similar-note-card-snippet">${note.snippet}</p>
        </div>
      `;
      
      // Click to select note for appending
      card.addEventListener('click', () => {
        // Remove selection from all cards
        listDiv.querySelectorAll('.similar-note-card').forEach(c => {
          c.classList.remove('selected');
        });
        // Select this card
        card.classList.add('selected');
        this.selectedSimilarNote = note;
        console.log('[Notes] Selected similar note:', note.name);
      });
      
      listDiv.appendChild(card);
    });
    
    // Show warning
    warningDiv.classList.remove('hidden');
    
    // Set up action buttons
    this.setupDedupActions();
  }

  /**
   * Set up deduplication action buttons (Phase 21)
   */
  setupDedupActions() {
    const appendBtn = document.getElementById('append-to-note-btn');
    const linkBtn = document.getElementById('create-with-links-btn');
    const anywayBtn = document.getElementById('create-anyway-btn');
    
    // Remove existing listeners by cloning
    const newAppendBtn = appendBtn.cloneNode(true);
    const newLinkBtn = linkBtn.cloneNode(true);
    const newAnywayBtn = anywayBtn.cloneNode(true);
    appendBtn.replaceWith(newAppendBtn);
    linkBtn.replaceWith(newLinkBtn);
    anywayBtn.replaceWith(newAnywayBtn);
    
    // Append to selected note
    newAppendBtn.addEventListener('click', () => this.appendToSelectedNote());
    
    // Create with links to similar notes
    newLinkBtn.addEventListener('click', () => this.createWithLinks());
    
    // Create anyway (bypass dedup)
    newAnywayBtn.addEventListener('click', () => this.createAnyway());
  }

  /**
   * Append content to selected similar note (Phase 21)
   */
  async appendToSelectedNote() {
    if (!this.selectedSimilarNote) {
      alert('Please select a note to append to');
      return;
    }
    
    const errorDiv = document.getElementById('note-creation-error');
    const modal = document.getElementById('note-creation-modal');
    
    try {
      const separator = '\n\n---\n\n';
      const response = await fetch('http://127.0.0.1:11436/polly/notes/append', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          path: this.selectedSimilarNote.path,
          content: this.proposedNote.content,
          separator: separator
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to append to note');
      }
      
      const result = await response.json();
      console.log('[Notes] Content appended:', result);
      
      // Reload notes index
      await this.loadNotesIndex();
      
      // Close modal
      modal.classList.add('hidden');
      
      // Open the updated note
      setTimeout(() => {
        this.openNote(this.selectedSimilarNote.name);
      }, 100);
      
    } catch (error) {
      console.error('[Notes] Failed to append content:', error);
      errorDiv.textContent = error.message || 'Failed to append content';
      errorDiv.classList.remove('hidden');
    }
  }

  /**
   * Create note with links to similar notes (Phase 21)
   */
  async createWithLinks() {
    const errorDiv = document.getElementById('note-creation-error');
    const modal = document.getElementById('note-creation-modal');
    
    try {
      // Add "Related Notes" section with wikilinks
      const similarNotes = Array.from(document.querySelectorAll('.similar-note-card'))
        .map(card => {
          const title = card.querySelector('.similar-note-card-title span').textContent;
          const name = card.querySelector('.similar-note-card-path').textContent.split('/')[1];
          return { title, name };
        });
      
      const relatedSection = '\n\n## Related Notes\n\n' +
        similarNotes.map(note => `- [[${note.name}]]`).join('\n');
      
      const contentWithLinks = this.proposedNote.content + relatedSection;
      
      // Create note with check_duplicates=false to bypass dedup
      const response = await fetch('http://127.0.0.1:11436/polly/notes/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: this.proposedNote.title,
          domain: this.proposedNote.domain,
          content: contentWithLinks,
          check_duplicates: false  // Bypass dedup since user confirmed
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create note');
      }
      
      const result = await response.json();
      console.log('[Notes] Note created with links:', result.note);
      
      // Reload notes index
      await this.loadNotesIndex();
      
      // Close modal
      modal.classList.add('hidden');
      
      // Open the new note
      setTimeout(() => {
        this.openNote(result.note.name);
      }, 100);
      
    } catch (error) {
      console.error('[Notes] Failed to create note with links:', error);
      errorDiv.textContent = error.message || 'Failed to create note with links';
      errorDiv.classList.remove('hidden');
    }
  }

  /**
   * Create note anyway, bypassing deduplication (Phase 21)
   */
  async createAnyway() {
    const errorDiv = document.getElementById('note-creation-error');
    const modal = document.getElementById('note-creation-modal');
    
    try {
      // Create note with check_duplicates=false to bypass dedup
      const response = await fetch('http://127.0.0.1:11436/polly/notes/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: this.proposedNote.title,
          domain: this.proposedNote.domain,
          content: this.proposedNote.content,
          check_duplicates: false  // Bypass dedup since user confirmed
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create note');
      }
      
      const result = await response.json();
      console.log('[Notes] Note created (bypassed dedup):', result.note);
      
      // Reload notes index
      await this.loadNotesIndex();
      
      // Close modal
      modal.classList.add('hidden');
      
      // Open the new note
      setTimeout(() => {
        this.openNote(result.note.name);
      }, 100);
      
    } catch (error) {
      console.error('[Notes] Failed to create note:', error);
      errorDiv.textContent = error.message || 'Failed to create note';
      errorDiv.classList.remove('hidden');
    }
  }

  /**
   * Show folder creation modal
   */
  async showCreateFolderModal() {
    const modal = document.getElementById('folder-creation-modal');
    const nameInput = document.getElementById('folder-name-input');
    const errorDiv = document.getElementById('folder-creation-error');
    
    if (!modal || !nameInput) {
      console.error('[Notes] Folder modal elements not found');
      return;
    }
    
    // Clear previous input and errors
    nameInput.value = '';
    errorDiv.classList.add('hidden');
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Focus name input
    setTimeout(() => nameInput.focus(), 100);
    
    // Setup modal event listeners (only once)
    if (!this._folderCreationListenersSetup) {
      this._setupFolderCreationListeners();
      this._folderCreationListenersSetup = true;
    }
  }

  /**
   * Setup folder creation modal event listeners
   */
  _setupFolderCreationListeners() {
    const modal = document.getElementById('folder-creation-modal');
    const closeBtn = document.getElementById('close-folder-creation');
    const cancelBtn = document.getElementById('cancel-folder-creation');
    const createBtn = document.getElementById('create-folder-button');
    
    // Close modal handlers
    const closeModal = () => {
      modal.classList.add('hidden');
    };
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });
    
    // Create folder handler
    createBtn.addEventListener('click', async () => {
      await this.createFolder();
    });
    
    // Enter to submit
    document.getElementById('folder-name-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.createFolder();
      }
    });
  }

  /**
   * Create a new folder
   */
  async createFolder() {
    const nameInput = document.getElementById('folder-name-input');
    const errorDiv = document.getElementById('folder-creation-error');
    const modal = document.getElementById('folder-creation-modal');
    const createBtn = document.getElementById('create-folder-button');
    
    const name = nameInput.value.trim();
    
    // Validation
    if (!name) {
      errorDiv.textContent = 'Folder name is required';
      errorDiv.classList.remove('hidden');
      nameInput.focus();
      return;
    }
    
    // Disable button while creating
    createBtn.disabled = true;
    createBtn.textContent = 'Creating...';
    errorDiv.classList.add('hidden');
    
    try {
      // Create folder via API
      const response = await fetch('http://127.0.0.1:11436/polly/notes/create-folder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create folder');
      }
      
      const result = await response.json();
      console.log('[Notes] Folder created:', result.folder);
      
      // Reload notes index to show new folder
      await this.loadNotesIndex();
      
      // Close modal
      modal.classList.add('hidden');
      
      // Show success message briefly
      const statusDiv = document.createElement('div');
      statusDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 12px 16px; background: var(--success-color, #98c379); color: var(--bg-primary); border-radius: 4px; z-index: 10000; font-size: 13px;';
      statusDiv.textContent = `Folder "${result.folder.name}" created successfully`;
      document.body.appendChild(statusDiv);
      
      setTimeout(() => {
        statusDiv.remove();
      }, 3000);
      
    } catch (error) {
      console.error('[Notes] Failed to create folder:', error);
      errorDiv.textContent = error.message || 'Failed to create folder';
      errorDiv.classList.remove('hidden');
    } finally {
      createBtn.disabled = false;
      createBtn.textContent = 'Create Folder';
    }
  }
  
  /**
   * Cleanup when notes view is closed
   */
  cleanup() {
    console.log('[Notes] Cleaning up notes manager...');
    
    // Stop sync polling
    if (this.syncPollInterval) {
      clearInterval(this.syncPollInterval);
      this.syncPollInterval = null;
      console.log('[Notes] Sync polling stopped');
    }
    
    // Clear auto-save timeout
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
      this.saveTimeout = null;
    }
    
    console.log('[Notes] Notes manager cleanup complete');
  }
  
}

// Global instance
window.notesManager = new NotesManager();
