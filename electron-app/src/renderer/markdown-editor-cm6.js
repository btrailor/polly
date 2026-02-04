/**
 * CodeMirror 6-based Markdown Editor for Polly
 * Provides seamless live-preview editing similar to Obsidian
 */

import { EditorView, keymap, lineNumbers, highlightActiveLine } from "@codemirror/view"
import { EditorState, Compartment } from "@codemirror/state"
import { markdown } from "@codemirror/lang-markdown"
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands"
import { searchKeymap, highlightSelectionMatches } from "@codemirror/search"
import { autocompletion, completionKeymap, closeBrackets } from "@codemirror/autocomplete"
import { bracketMatching, foldGutter, foldKeymap, syntaxTree } from "@codemirror/language"
import { livePreviewExtension } from "./live-preview-extension.js"

console.log('[MarkdownEditor] MODULE LOADED - markdown-editor-cm6.js')
console.log('[MarkdownEditor] livePreviewExtension imported:', typeof livePreviewExtension)

export class MarkdownEditor {
  /**
   * @param {HTMLElement} container - Container element for the editor
   * @param {Object} options - Configuration options
   * @param {string} options.initialContent - Initial markdown content
   * @param {Function} options.onChange - Callback when content changes
   * @param {Function} options.onSave - Callback to save content
   * @param {Object} options.theme - Theme configuration
   */
  constructor(container, options = {}) {
    this.container = container
    this.options = {
      initialContent: '',
      onChange: null,
      onSave: null,
      theme: 'dark',
      autoSave: true,
      autoSaveDelay: 2000,
      ...options
    }
    
    this.saveTimeout = null
    this.themeConfig = new Compartment()
    
    // Create the editor
    this.view = new EditorView({
      state: this.createEditorState(this.options.initialContent),
      parent: container
    })
    
    console.log('[MarkdownEditor] CodeMirror 6 editor initialized')
  }
  
  /**
   * Create the editor state with all extensions
   */
  createEditorState(content) {
    return EditorState.create({
      doc: content,
      extensions: [
        // Basic setup
        lineNumbers(),
        highlightActiveLine(),
        history(),
        foldGutter(),
        
        // Markdown language support
        markdown(),
        
        // Live preview - hide syntax on non-cursor lines
        (() => {
          console.log('[MarkdownEditor] About to call livePreviewExtension')
          const ext = livePreviewExtension({
            onWikiLinkClick: (noteName) => {
              console.log('[MarkdownEditor] Wiki link clicked:', noteName)
              // Callback will be provided by notes-manager
              if (this.options.onWikiLinkClick) {
                this.options.onWikiLinkClick(noteName)
              }
            }
          })
          console.log('[MarkdownEditor] livePreviewExtension returned:', ext)
          return ext
        })(),
        
        // Editing enhancements
        closeBrackets(),
        bracketMatching(),
        autocompletion(),
        highlightSelectionMatches(),
        
        // Line wrapping
        EditorView.lineWrapping,
        
        // Key bindings - custom bindings FIRST so they take precedence over defaults
        keymap.of([
          // Markdown formatting shortcuts
          {
            key: 'Mod-b',
            run: (view) => {
              this.toggleMarkdownFormat(view, '**', '**')
              return true
            }
          },
          {
            key: 'Mod-i',
            run: (view) => {
              // Use underscores for italic to allow nesting inside bold: **bold _italic_ text**
              this.toggleMarkdownFormat(view, '_', '_')
              return true
            }
          },
          {
            key: 'Mod-e',
            run: (view) => {
              this.toggleMarkdownFormat(view, '`', '`')
              return true
            }
          },
          {
            key: 'Mod-k',
            run: (view) => {
              this.insertWikiLink(view)
              return true
            }
          },
          {
            key: 'Mod-s',
            run: () => {
              this.save()
              return true
            }
          },
          // Default keymaps come after so our custom bindings override them
          ...defaultKeymap,
          ...historyKeymap,
          ...foldKeymap,
          ...searchKeymap,
          ...completionKeymap,
          indentWithTab
        ]),
        
        // Theme
        this.themeConfig.of(this.getTheme()),
        
        // Auto-save on change
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            this.handleChange()
          }
        })
      ]
    })
  }
  
  /**
   * Get theme configuration matching Polly's design
   */
  getTheme() {
    return EditorView.theme({
      "&": {
        backgroundColor: "var(--bg-primary, #1e1e1e)",
        color: "var(--text-primary, #ffffff)",
        height: "100%",
        fontSize: "14px",
        fontFamily: "'SF Mono', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', monospace"
      },
      ".cm-content": {
        caretColor: "var(--text-primary, #ffffff)",
        padding: "20px 0"
      },
      ".cm-scroller": {
        overflow: "auto",
        fontFamily: "'SF Mono', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', monospace"
      },
      ".cm-line": {
        padding: "0 20px",
        lineHeight: "1.6"
      },
      ".cm-gutters": {
        backgroundColor: "var(--bg-secondary, #252525)",
        color: "var(--text-tertiary, #666666)",
        border: "none"
      },
      ".cm-activeLineGutter": {
        backgroundColor: "var(--bg-tertiary, #2d2d2d)"
      },
      ".cm-activeLine": {
        backgroundColor: "var(--bg-tertiary, rgba(255, 255, 255, 0.05))"
      },
      ".cm-selectionBackground": {
        backgroundColor: "var(--selection-bg, rgba(74, 144, 226, 0.3)) !important"
      },
      ".cm-focused .cm-selectionBackground": {
        backgroundColor: "var(--selection-bg, rgba(74, 144, 226, 0.3)) !important"
      },
      ".cm-cursor": {
        borderLeftColor: "var(--text-primary, #ffffff)"
      },
      
      // Markdown-specific styling
      ".cm-header": {
        fontWeight: "bold",
        color: "var(--text-primary, #ffffff)"
      },
      ".cm-header.cm-header-1": { fontSize: "2em" },
      ".cm-header.cm-header-2": { fontSize: "1.5em" },
      ".cm-header.cm-header-3": { fontSize: "1.25em" },
      ".cm-header.cm-header-4": { fontSize: "1.1em" },
      ".cm-header.cm-header-5": { fontSize: "1em" },
      ".cm-header.cm-header-6": { fontSize: "0.9em" },
      
      ".cm-strong": {
        fontWeight: "bold"
      },
      ".cm-em": {
        fontStyle: "italic"
      },
      ".cm-link": {
        color: "var(--link-color, #4a90e2)",
        textDecoration: "none"
      },
      ".cm-url": {
        color: "var(--link-color, #4a90e2)",
        textDecoration: "underline"
      },
      ".cm-strikethrough": {
        textDecoration: "line-through"
      },
      ".cm-code": {
        backgroundColor: "var(--bg-tertiary, rgba(255, 255, 255, 0.1))",
        padding: "2px 4px",
        borderRadius: "3px",
        fontFamily: "'SF Mono', 'Monaco', 'Consolas', monospace"
      },
      ".cm-meta": {
        color: "var(--text-secondary, #888888)"
      },
      ".cm-comment": {
        color: "var(--text-tertiary, #666666)"
      },
      ".cm-quote": {
        color: "var(--text-secondary, #888888)",
        fontStyle: "italic"
      },
      
      // Search/selection
      ".cm-searchMatch": {
        backgroundColor: "var(--search-match-bg, rgba(255, 255, 0, 0.2))",
        outline: "1px solid var(--search-match-border, rgba(255, 255, 0, 0.5))"
      },
      ".cm-searchMatch.cm-searchMatch-selected": {
        backgroundColor: "var(--search-match-selected-bg, rgba(255, 255, 0, 0.4))"
      },
      
      // Autocomplete
      ".cm-tooltip.cm-tooltip-autocomplete": {
        backgroundColor: "var(--bg-secondary, #252525)",
        border: "1px solid var(--border-color, #3a3a3a)",
        "& > ul": {
          fontFamily: "'SF Mono', 'Monaco', 'Consolas', monospace",
          "& > li": {
            padding: "4px 8px",
            color: "var(--text-primary, #ffffff)"
          },
          "& > li[aria-selected]": {
            backgroundColor: "var(--bg-tertiary, #2d2d2d)",
            color: "var(--text-primary, #ffffff)"
          }
        }
      }
    }, { dark: this.options.theme === 'dark' })
  }
  
  /**
   * Handle content changes
   */
  handleChange() {
    // Call onChange callback if provided
    if (this.options.onChange) {
      this.options.onChange(this.getValue())
    }
    
    // Schedule auto-save
    if (this.options.autoSave && this.options.onSave) {
      if (this.saveTimeout) {
        clearTimeout(this.saveTimeout)
      }
      
      this.saveTimeout = setTimeout(() => {
        this.save()
      }, this.options.autoSaveDelay)
    }
  }
  
  /**
   * Save the current content
   */
  save() {
    if (this.options.onSave) {
      this.options.onSave(this.getValue())
      console.log('[MarkdownEditor] Content saved')
    }
  }
  
  /**
   * Get the current editor content
   */
  getValue() {
    return this.view.state.doc.toString()
  }
  
  /**
   * Set the editor content
   */
  setValue(content) {
    this.view.dispatch({
      changes: {
        from: 0,
        to: this.view.state.doc.length,
        insert: content
      }
    })
  }
  
  /**
   * Focus the editor
   */
  focus() {
    this.view.focus()
  }
  
  /**
   * Get the current cursor position
   */
  getCursorPosition() {
    return this.view.state.selection.main.head
  }
  
  /**
   * Set the cursor position
   */
  setCursorPosition(pos) {
    this.view.dispatch({
      selection: { anchor: pos, head: pos }
    })
  }
  
  /**
   * Get the current selection
   */
  getSelection() {
    const { from, to } = this.view.state.selection.main
    return {
      from,
      to,
      text: this.view.state.doc.sliceString(from, to)
    }
  }
  
  /**
   * Insert text at cursor position
   */
  insertText(text) {
    const pos = this.getCursorPosition()
    this.view.dispatch({
      changes: { from: pos, insert: text },
      selection: { anchor: pos + text.length }
    })
  }
  
  /**
   * Replace selection with text
   */
  replaceSelection(text) {
    const { from, to } = this.view.state.selection.main
    this.view.dispatch({
      changes: { from, to, insert: text },
      selection: { anchor: from + text.length }
    })
  }
  
  /**
   * Toggle markdown formatting (bold, italic, code)
   * Simple and predictable:
   * - With selection: wrap or unwrap the selection
   * - Without selection: insert empty markers with cursor between
   * 
   * @param {EditorView} view - The editor view
   * @param {string} startMarker - Opening marker (e.g., '**', '*', '`')
   * @param {string} endMarker - Closing marker (e.g., '**', '*', '`')
   */
  toggleMarkdownFormat(view, startMarker, endMarker) {
    const { state } = view
    const { from, to } = state.selection.main
    const selectedText = state.doc.sliceString(from, to)
    
    // No selection - insert empty markers with cursor between
    if (from === to) {
      view.dispatch({
        changes: { from, to, insert: startMarker + endMarker },
        selection: { anchor: from + startMarker.length }
      })
      return
    }
    
    // Has selection - check if markers are adjacent to selection
    const beforeStart = Math.max(0, from - startMarker.length)
    const afterEnd = Math.min(state.doc.length, to + endMarker.length)
    const beforeText = state.doc.sliceString(beforeStart, from)
    const afterText = state.doc.sliceString(to, afterEnd)
    
    const isWrapped = beforeText === startMarker && afterText === endMarker
    
    if (isWrapped) {
      // Remove the adjacent markers
      view.dispatch({
        changes: [
          { from: beforeStart, to: from, insert: '' },
          { from: to, to: afterEnd, insert: '' }
        ],
        selection: { anchor: beforeStart, head: beforeStart + selectedText.length }
      })
    } else if (selectedText.startsWith(startMarker) && selectedText.endsWith(endMarker) && 
               selectedText.length > startMarker.length + endMarker.length) {
      // Selection includes the markers - remove them
      const innerText = selectedText.slice(startMarker.length, -endMarker.length)
      view.dispatch({
        changes: { from, to, insert: innerText },
        selection: { anchor: from, head: from + innerText.length }
      })
    } else {
      // Wrap the selection with markers
      view.dispatch({
        changes: { from, to, insert: startMarker + selectedText + endMarker },
        selection: { anchor: from + startMarker.length, head: to + startMarker.length }
      })
    }
  }
  
  /**
   * Insert or wrap selection with wiki link brackets
   * @param {EditorView} view - The editor view
   */
  insertWikiLink(view) {
    const { state } = view
    const { from, to } = state.selection.main
    const selectedText = state.doc.sliceString(from, to)
    
    if (from === to) {
      // No selection - insert [[ ]] and place cursor between them
      view.dispatch({
        changes: { from, to, insert: '[[]]' },
        selection: { anchor: from + 2 }
      })
    } else {
      // Wrap selection with [[ ]]
      view.dispatch({
        changes: { from, to, insert: '[[' + selectedText + ']]' },
        selection: { anchor: from + 2, head: to + 2 }
      })
    }
  }
  
  /**
   * Destroy the editor
   */
  destroy() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout)
    }
    this.view.destroy()
    console.log('[MarkdownEditor] Editor destroyed')
  }
}
