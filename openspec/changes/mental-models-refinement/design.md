# Mental Models Refinement — Design

## 1. Backend: Scoring Algorithm Fixes

### Keyword Matching
- Replace substring matching (`model_kw in kw or kw in model_kw`) with exact whole-word equality (`kw == model_kw`).
- This prevents false positives like "form" matching "information".

### Minimum Score Threshold
- Raise the inclusion threshold from `score > 0` to `score >= 5`.
- A single keyword match (+2) no longer qualifies a model.

### Keyword Score Cap
- Cap keyword contribution at +6 (max 3 keyword matches count).
- This prevents keyword flooding from overwhelming page/persona signals.

### Core Philosophy Model Configs
- Remove overly broad `active_on_pages` and `applies_to` from Core Philosophy models.
- Give them narrow, distinctive keywords that only match philosophical/meta-level queries.

## 2. Frontend: Page Tracking Fix

### Second Query Path
- Change `page_context: currentView` to `page: currentPage` in the floating chat query path.

### Chat View Page Derivation
- When `currentPage === "chat"`, derive the effective page from the active conversation's `page_context` field instead of sending the literal string "chat".

## 3. Frontend: Override Modal Fix

### z-index
- Set `#mental-models-override-modal` to `z-index: 10001`.

### Disabled State UX
- When "Use Defaults" is checked: hide checkboxes entirely and show a read-only info message explaining auto-assignment is active.
- When unchecked: show the full checkbox list, enabled and interactive.
- Add a click handler on the entire `.override-model-item` row to toggle its checkbox.

## 4. Frontend: Global Default Models Picker

### Settings Tab
- Add a "Default Models" section under the existing Mental Models settings tab.
- Show all models with checkboxes for the user to pick their preferred defaults.
- Store in localStorage as `mm_global_defaults` (`{ enabled: boolean, modelIds: string[] }`).

### Integration
- When a query has no per-conversation override, check for global defaults before falling back to auto-assignment.
- Pass global defaults as `mental_models_override` in query options when enabled.

## Impact

- `core/mental_models.py` — scoring logic and default model configs
- `electron-app/src/renderer/app.js` — page tracking, override modal, global defaults picker, query options
- `electron-app/src/renderer/index.html` — override modal structure, settings tab additions
- `electron-app/src/renderer/styles/main.css` — override modal styles
- `electron-app/src/main/main.js` — no changes needed (already forwards `page` and `mental_models_override`)
