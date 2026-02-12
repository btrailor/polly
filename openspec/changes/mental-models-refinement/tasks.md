# Mental Models Refinement — Tasks

## Backend

1. [x] Replace substring keyword matching with exact equality in `core/mental_models.py`
2. [x] Add minimum score threshold (>= 5) for model inclusion
3. [x] Cap keyword score contribution at +6
4. [x] Narrow Core Philosophy model activation configs (pages, domains, keywords)

## Frontend — Page Tracking

5. [x] Fix second query path: change `page_context` to `page` in app.js
6. [x] Derive effective page from conversation's `page_context` when `currentPage === "chat"`

## Frontend — Override Modal

7. [x] Fix z-index on `#mental-models-override-modal`
8. [x] Redesign disabled-state UX: hide checkboxes when "Use Defaults" checked, show info message
9. [x] Make entire `.override-model-item` row clickable to toggle checkbox

## Frontend — Global Default Models

10. [x] Add "Default Models" picker section to Mental Models settings tab
11. [x] Store global defaults in localStorage
12. [x] Integrate global defaults into query flow (use as override when enabled)

## Specs

13. [x] Update `openspec/specs/mental-models/spec.md`
