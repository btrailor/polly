# Phase 17: CSS Cleanup

**Date:** February 4, 2026  
**Purpose:** Inventory CSS files, remove stale CSS, document needed patterns  
**Status:** In Progress

---

## CSS Files Inventory

### Files to Remove (Will rebuild in VSCode):

1. **`chat-sidebar.css`** - Chat sidebar styles
   - **Action:** REMOVE
   - **Rationale:** Will rebuild using VSCode panel system

2. **`chat.css`** - Chat styles
   - **Action:** REMOVE
   - **Rationale:** Will rebuild using VSCode design system

3. **`floating-chat.css`** - Floating chat styles
   - **Action:** REMOVE
   - **Rationale:** Chat will be in panel, not floating

4. **`layout.css`** - Main layout styles
   - **Action:** REMOVE
   - **Rationale:** VSCode has its own layout system

5. **`ribbon.css`** - Ribbon navigation styles
   - **Action:** REMOVE
   - **Rationale:** Using activity bar instead

6. **`three-column.css`** - Three column layout
   - **Action:** REMOVE
   - **Rationale:** VSCode has its own layout system

### Files to Review (May need patterns):

7. **`curriculum.css`** - Learning/curriculum styles
   - **Action:** REVIEW
   - **Rationale:** May need some patterns for curriculum UI
   - **Decision:** Extract only essential patterns, rebuild in VSCode

8. **`glitch-effects.css`** - Glitch animation effects
   - **Action:** REVIEW
   - **Rationale:** May want to preserve glitch effects
   - **Decision:** Extract if desired, otherwise remove

9. **`main.css`** - Main styles
   - **Action:** REVIEW
   - **Rationale:** May have essential patterns
   - **Decision:** Extract only essential patterns (colors, etc.)

10. **`notes.css`** - Notes styles
    - **Action:** REVIEW
    - **Rationale:** May need some patterns for notes UI
    - **Decision:** Extract only essential patterns, rebuild in VSCode

11. **`obsidian-theme.css`** - Obsidian theme
    - **Action:** REVIEW
    - **Rationale:** May want to preserve Obsidian theme colors
    - **Decision:** Extract color scheme if desired

12. **`persona-switch-dialog.css`** - Persona dialog styles
    - **Action:** REVIEW
    - **Rationale:** May need patterns for persona UI
    - **Decision:** Extract only essential patterns, use VSCode dialogs

13. **`persona-ui.css`** - Persona UI styles
    - **Action:** REVIEW
    - **Rationale:** May need patterns for persona UI
    - **Decision:** Extract only essential patterns, rebuild in VSCode

14. **`template-gallery.css`** - Template gallery styles
    - **Action:** REVIEW
    - **Rationale:** May need patterns for template gallery
    - **Decision:** Extract only essential patterns, rebuild in VSCode

---

## Patterns to Preserve (if any)

### Color Scheme:
- Primary accent: `#f0903b` (Polly orange)
- Background colors (if Obsidian theme desired)
- Text colors (if Obsidian theme desired)

### Animations:
- Glitch effects (if desired)
- Smooth transitions (VSCode has its own)

### Typography:
- Font families (use VSCode defaults)
- Font sizes (use VSCode defaults)

---

## CSS Cleanup Actions

### Immediate Actions:
1. ✅ Delete backup CSS file (`main.css.backup`)
2. ⏳ Remove chat-related CSS files
3. ⏳ Remove layout CSS files
4. ⏳ Remove ribbon CSS
5. ⏳ Review remaining CSS files
6. ⏳ Extract essential patterns (if any)
7. ⏳ Document preserved patterns

### Before Migration:
1. Create CSS pattern library (if any patterns preserved)
2. Document color scheme
3. Ensure no CSS dependencies in ported code

---

## Migration Strategy

### For Webviews:
- Use VSCode's webview CSS variables
- Build fresh CSS using VSCode design tokens
- No porting of old CSS

### For Native Components:
- Use VSCode's built-in styling
- No custom CSS needed

### For Custom UI:
- Build fresh CSS using VSCode design system
- Reference VSCode CSS variables
- Follow VSCode UI guidelines

---

## VSCode CSS Variables Reference

When building new UI, use VSCode's CSS variables:
- `--vscode-editor-background`
- `--vscode-editor-foreground`
- `--vscode-sideBar-background`
- `--vscode-sideBar-foreground`
- `--vscode-button-background`
- `--vscode-button-foreground`
- etc.

See: https://code.visualstudio.com/api/references/theme-color

---

## Next Steps

1. ✅ Complete CSS cleanup
2. ⏳ Begin migration with clean slate
3. ⏳ Build fresh UI using VSCode design system
