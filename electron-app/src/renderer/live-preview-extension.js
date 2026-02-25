/**
 * Live Preview Extension for CodeMirror 6
 * Hides markdown syntax on lines where the cursor is NOT present
 * Similar to Obsidian's live preview mode
 */

console.log('[LivePreview] MODULE LOADED - live-preview-extension.js')

import { ViewPlugin, Decoration, WidgetType } from "@codemirror/view"
import { syntaxTree } from "@codemirror/language"
import { RangeSetBuilder } from "@codemirror/state"

/**
 * Empty widget to hide text
 */
class HiddenWidget extends WidgetType {
  toDOM() {
    return document.createTextNode('')
  }
  
  eq(other) {
    return true
  }
  
  ignoreEvent() {
    return false
  }
}

/**
 * Widget for rendering bold text without markers
 */
class BoldWidget extends WidgetType {
  constructor(text) {
    super()
    this.text = text
  }
  
  toDOM() {
    const span = document.createElement("strong")
    span.textContent = this.text
    span.style.fontWeight = "bold"
    return span
  }
  
  eq(other) {
    return other.text === this.text
  }
  
  ignoreEvent() {
    return false
  }
}

/**
 * Widget for rendering italic text without markers
 */
class ItalicWidget extends WidgetType {
  constructor(text) {
    super()
    this.text = text
  }
  
  toDOM() {
    const span = document.createElement("em")
    span.textContent = this.text
    span.style.fontStyle = "italic"
    return span
  }
  
  eq(other) {
    return other.text === this.text
  }
  
  ignoreEvent() {
    return false
  }
}

/**
 * Widget for rendering inline code without backticks
 */
class InlineCodeWidget extends WidgetType {
  constructor(text) {
    super()
    this.text = text
  }
  
  toDOM() {
    const span = document.createElement("code")
    span.textContent = this.text
    span.style.backgroundColor = "var(--bg-tertiary, rgba(255, 255, 255, 0.1))"
    span.style.padding = "2px 4px"
    span.style.borderRadius = "3px"
    span.style.fontFamily = "'SF Mono', 'Monaco', 'Consolas', monospace"
    return span
  }
  
  eq(other) {
    return other.text === this.text
  }
  
  ignoreEvent() {
    return false
  }
}

/**
 * Widget for rendering wiki links
 */
class WikiLinkWidget extends WidgetType {
  constructor(text, noteName, onClickCallback) {
    super()
    this.text = text
    this.noteName = noteName
    this.onClickCallback = onClickCallback
  }
  
  toDOM() {
    const a = document.createElement("a")
    a.textContent = this.noteName
    a.className = "wiki-link cm-wiki-link"
    a.style.color = "var(--link-color, #4a90e2)"
    a.style.textDecoration = "none"
    a.style.cursor = "pointer"
    a.style.borderBottom = "1px solid var(--link-color, #4a90e2)"
    
    a.addEventListener('click', (e) => {
      e.preventDefault()
      e.stopPropagation()
      if (this.onClickCallback) {
        this.onClickCallback(this.noteName)
      }
    })
    
    return a
  }
  
  eq(other) {
    return other.noteName === this.noteName
  }
  
  ignoreEvent() {
    return false // Allow clicks
  }
}

/**
 * Live Preview ViewPlugin
 * Decorates markdown to hide syntax on non-cursor lines
 */
export const livePreviewExtension = (options = {}) => {
  const { onWikiLinkClick } = options
  
  console.log('[LivePreview] Extension created')
  
  return ViewPlugin.fromClass(class {
    decorations = Decoration.none
    
    constructor(view) {
      console.log('[LivePreview] Plugin constructed')
      this.decorations = this.buildDecorations(view)
      this.view = view
      
      // Store bound handler so the same reference is used for add/remove
      if (onWikiLinkClick) {
        this._clickHandler = this.handleClick.bind(this)
        view.dom.addEventListener('click', this._clickHandler)
      }
    }
    
    destroy() {
      if (this._clickHandler) {
        this.view.dom.removeEventListener('click', this._clickHandler)
        this._clickHandler = null
      }
    }
    
    handleClick(event) {
      const target = event.target
      if (target.classList && target.classList.contains('wiki-link')) {
        const noteName = target.getAttribute('data-note-name')
        if (noteName && onWikiLinkClick) {
          console.log('[LivePreview] Wiki link clicked:', noteName)
          event.preventDefault()
          onWikiLinkClick(noteName)
        }
      }
    }
    
    update(update) {
      // Rebuild decorations when document changes, selection moves, or viewport changes
      if (update.docChanged || update.selectionSet || update.viewportChanged) {
        this.decorations = this.buildDecorations(update.view)
      }
    }
    
    buildDecorations(view) {
      // Get cursor position
      const cursorPos = view.state.selection.main.head
      const cursorLine = view.state.doc.lineAt(cursorPos).number
      console.log('[LivePreview] Building decorations, cursor at position:', cursorPos, 'line:', cursorLine)
      
      let decorationCount = 0
      
      // Collect all decorations first (to handle nested formats)
      const decorations = []
      
      // Iterate through visible ranges
      for (const { from, to } of view.visibleRanges) {
        syntaxTree(view.state).iterate({
          from,
          to,
          enter: (node) => {
            const nodeFrom = node.from
            const nodeTo = node.to
            const nodeLine = view.state.doc.lineAt(nodeFrom).number
            
            const text = view.state.doc.sliceString(nodeFrom, nodeTo)
            
            // Check if cursor is inside this specific node
            const isCursorInside = (cursorPos >= nodeFrom && cursorPos <= nodeTo)
            
            try {
              
              // Handle bold **text**
              if (node.name === "StrongEmphasis") {
                console.log('[LivePreview] Found StrongEmphasis:', text, 'on line', nodeLine)
                // Check if it's actually ** markers (not __)
                if (text.startsWith('**') && text.endsWith('**') && text.length > 4) {
                  
                  if (isCursorInside) {
                    // Cursor is inside - style markers as gray but keep text bold
                    decorations.push({ from: nodeFrom, to: nodeFrom + 2, decoration: Decoration.mark({
                      attributes: { style: "color: var(--text-secondary, #808080); opacity: 0.6;" }
                    })})
                    decorations.push({ from: nodeFrom + 2, to: nodeTo - 2, decoration: Decoration.mark({
                      attributes: { style: "font-weight: bold;" }
                    })})
                    decorations.push({ from: nodeTo - 2, to: nodeTo, decoration: Decoration.mark({
                      attributes: { style: "color: var(--text-secondary, #808080); opacity: 0.6;" }
                    })})
                    console.log('[LivePreview] Styled ** markers (cursor inside)')
                  } else {
                    // Cursor is elsewhere - hide markers only (don't style content, let nested formats handle it)
                    decorations.push({ from: nodeFrom, to: nodeFrom + 2, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    decorations.push({ from: nodeTo - 2, to: nodeTo, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    // Only apply bold styling to content if cursor is NOT in a nested child
                    decorations.push({ from: nodeFrom + 2, to: nodeTo - 2, decoration: Decoration.mark({
                      attributes: { style: "font-weight: bold;" }
                    })})
                    console.log('[LivePreview] Hid ** markers (cursor elsewhere)')
                  }
                  
                  decorationCount++
                }
              }
              
              // Handle italic *text* or _text_
              else if (node.name === "Emphasis") {
                console.log('[LivePreview] Found Emphasis:', text, 'on line', nodeLine)
                if ((text.startsWith('*') && text.endsWith('*') && text.length > 2) ||
                    (text.startsWith('_') && text.endsWith('_') && text.length > 2)) {
                  
                  if (isCursorInside) {
                    // Cursor is inside - style markers as gray but keep text italic
                    decorations.push({ from: nodeFrom, to: nodeFrom + 1, decoration: Decoration.mark({
                      attributes: { style: "color: var(--text-secondary, #808080); opacity: 0.6;" }
                    })})
                    decorations.push({ from: nodeFrom + 1, to: nodeTo - 1, decoration: Decoration.mark({
                      attributes: { style: "font-style: italic;" }
                    })})
                    decorations.push({ from: nodeTo - 1, to: nodeTo, decoration: Decoration.mark({
                      attributes: { style: "color: var(--text-secondary, #808080); opacity: 0.6;" }
                    })})
                    console.log('[LivePreview] Styled * markers (cursor inside)')
                  } else {
                    // Cursor is elsewhere - hide markers completely
                    decorations.push({ from: nodeFrom, to: nodeFrom + 1, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    decorations.push({ from: nodeFrom + 1, to: nodeTo - 1, decoration: Decoration.mark({
                      attributes: { style: "font-style: italic;" }
                    })})
                    decorations.push({ from: nodeTo - 1, to: nodeTo, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    console.log('[LivePreview] Hid * markers (cursor elsewhere)')
                  }
                  
                  decorationCount++
                }
              }
              
              // Handle inline code `code`
              else if (node.name === "InlineCode") {
                console.log('[LivePreview] Found InlineCode:', text, 'on line', nodeLine)
                if (text.startsWith('`') && text.endsWith('`') && text.length > 2) {
                  
                  if (isCursorInside) {
                    // Cursor is inside - style backticks as gray but keep code styling
                    decorations.push({ from: nodeFrom, to: nodeFrom + 1, decoration: Decoration.mark({
                      attributes: { style: "color: var(--text-secondary, #808080); opacity: 0.6; font-family: monospace;" }
                    })})
                    decorations.push({ from: nodeFrom + 1, to: nodeTo - 1, decoration: Decoration.mark({
                      attributes: { style: "font-family: monospace; background: rgba(255, 255, 255, 0.1); padding: 2px 4px; border-radius: 3px;" }
                    })})
                    decorations.push({ from: nodeTo - 1, to: nodeTo, decoration: Decoration.mark({
                      attributes: { style: "color: var(--text-secondary, #808080); opacity: 0.6; font-family: monospace;" }
                    })})
                    console.log('[LivePreview] Styled ` markers (cursor inside)')
                  } else {
                    // Cursor is elsewhere - hide markers completely
                    decorations.push({ from: nodeFrom, to: nodeFrom + 1, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    decorations.push({ from: nodeFrom + 1, to: nodeTo - 1, decoration: Decoration.mark({
                      attributes: { style: "font-family: monospace; background: rgba(255, 255, 255, 0.1); padding: 2px 4px; border-radius: 3px;" }
                    })})
                    decorations.push({ from: nodeTo - 1, to: nodeTo, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    console.log('[LivePreview] Hid ` markers (cursor elsewhere)')
                  }
                  
                  decorationCount++
                }
              }
              
              
              // Handle headings # Heading
              else if (node.name === "ATXHeading1" || node.name === "ATXHeading2" || 
                       node.name === "ATXHeading3" || node.name === "ATXHeading4" ||
                       node.name === "ATXHeading5" || node.name === "ATXHeading6") {
                console.log('[LivePreview] Found Heading:', text, 'on line', nodeLine)
                
                // Count the number of # symbols
                const hashMatch = text.match(/^(#{1,6})\s/)
                if (hashMatch) {
                  const hashCount = hashMatch[1].length
                  const hashEnd = nodeFrom + hashMatch[0].length - 1 // -1 to keep the space
                  
                  // Check if cursor is on this heading's line
                  const isCursorOnHeading = (nodeLine === cursorLine)
                  
                  // Font sizes for each heading level
                  const fontSizes = {
                    1: '2em',
                    2: '1.5em',
                    3: '1.25em',
                    4: '1.1em',
                    5: '1em',
                    6: '0.9em'
                  }
                  
                  if (isCursorOnHeading) {
                    // Style the # markers as muted/gray at the same size as the heading
                    decorations.push({ from: nodeFrom, to: hashEnd, decoration: Decoration.mark({
                      attributes: {
                        style: `color: var(--text-secondary, #808080); opacity: 0.6; font-weight: normal; font-size: ${fontSizes[hashCount]};`
                      }
                    })})
                    console.log('[LivePreview] Styled # markers (cursor on line)')
                  } else {
                    // Hide the # symbols when cursor is on a different line
                    decorations.push({ from: nodeFrom, to: hashEnd, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                    console.log('[LivePreview] Hid # markers (cursor on different line)')
                  }
                  
                  // Style the heading text based on level (always applied)
                  decorations.push({ from: hashEnd, to: nodeTo, decoration: Decoration.mark({
                    attributes: {
                      style: `font-size: ${fontSizes[hashCount]}; font-weight: bold;`
                    }
                  })})
                  
                  decorationCount++
                }
              }
              
              // Handle strikethrough ~~text~~
              else if (node.name === "Strikethrough") {
                console.log('[LivePreview] Found Strikethrough:', text, 'on line', nodeLine)
                if (text.startsWith('~~') && text.endsWith('~~') && text.length > 4) {
                  // Hide the opening ~~
                  decorations.push({ from: nodeFrom, to: nodeFrom + 2, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                  // Add strikethrough styling
                  decorations.push({ from: nodeFrom + 2, to: nodeTo - 2, decoration: Decoration.mark({
                    attributes: {
                      style: "text-decoration: line-through;"
                    }
                  })})
                  // Hide the closing ~~
                  decorations.push({ from: nodeTo - 2, to: nodeTo, decoration: Decoration.replace({ widget: new HiddenWidget() }) })
                  decorationCount++
                  console.log('[LivePreview] Added strikethrough decoration (hide markers with widgets)')
                }
              }
            } catch (error) {
              console.error('[LivePreview] Error processing node:', node.name, error)
            }
          }
        })
      }
      
      // Handle wiki links [[Note Name]] — scan raw text per visible line
      // (lezer-markdown does not parse [[...]] as Link nodes)
      const wikiLinkRe = /\[\[([^\]\n]+)\]\]/g
      for (const { from, to } of view.visibleRanges) {
        const rangeText = view.state.doc.sliceString(from, to)
        let m
        wikiLinkRe.lastIndex = 0
        while ((m = wikiLinkRe.exec(rangeText)) !== null) {
          const matchFrom = from + m.index
          const matchTo   = matchFrom + m[0].length
          const noteName  = m[1]
          const matchLine = view.state.doc.lineAt(matchFrom).number
          const isCursorOnLine = (matchLine === cursorLine)
          if (isCursorOnLine) {
            // Cursor on this line — show raw [[...]] in muted style so user can edit
            decorations.push({ from: matchFrom, to: matchFrom + 2, decoration: Decoration.mark({
              attributes: { style: 'color: var(--text-secondary, #808080); opacity: 0.6;' }
            })})
            decorations.push({ from: matchFrom + 2, to: matchTo - 2, decoration: Decoration.mark({
              attributes: {
                style: 'color: #8ab4f8; cursor: pointer; text-decoration: underline;',
                'data-note-name': noteName,
                class: 'wiki-link'
              }
            })})
            decorations.push({ from: matchTo - 2, to: matchTo, decoration: Decoration.mark({
              attributes: { style: 'color: var(--text-secondary, #808080); opacity: 0.6;' }
            })})
          } else {
            // Cursor elsewhere — hide [[ ]] markers, show only the link text
            decorations.push({ from: matchFrom, to: matchFrom + 2,
              decoration: Decoration.replace({ widget: new HiddenWidget() }) })
            decorations.push({ from: matchFrom + 2, to: matchTo - 2, decoration: Decoration.mark({
              attributes: {
                style: 'color: #8ab4f8; cursor: pointer; text-decoration: underline;',
                'data-note-name': noteName,
                class: 'wiki-link'
              }
            })})
            decorations.push({ from: matchTo - 2, to: matchTo,
              decoration: Decoration.replace({ widget: new HiddenWidget() }) })
          }
          decorationCount++
        }
      }

      // Sort decorations by start position, then by end position
      decorations.sort((a, b) => {
        if (a.from !== b.from) return a.from - b.from
        return a.to - b.to
      })
      
      // Build the decoration set from sorted decorations
      const builder = new RangeSetBuilder()
      for (const { from, to, decoration } of decorations) {
        builder.add(from, to, decoration)
      }
      
      console.log('[LivePreview] Built', decorationCount, 'decorations')
      return builder.finish()
    }
  }, {
    decorations: v => v.decorations
  })
}
