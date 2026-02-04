# Phase 23: Curriculum System - Future Improvements

**Created:** February 3, 2026  
**Status:** Backlog / Nice-to-Have  
**Priority:** Low to Medium

This document tracks potential improvements and refinements for the Phase 23 Curriculum System that are not critical for the initial release but would enhance the user experience.

---

## Category: Content Quality

### 1. Better LLM Prompt Control
**Priority:** Medium  
**Effort:** 2-3 hours

**Problem:**
LLM sometimes ignores section heading instructions in enrichment prompts (e.g., using "Code Examples" instead of "Case Studies" for non-programming topics).

**Current Workaround:**
Frontend post-processes and renames headings based on template type.

**Potential Solutions:**
- Experiment with different prompt formats (XML tags, strict JSON output)
- Use function calling / structured output from LLMs that support it
- Add examples to prompt showing exact desired format
- Use a specialized instruction-following model for generation
- Implement retry logic with format correction

**Files to Change:**
- `core/personas/implementations/professor.py` (_build_enrichment_prompt)

---

### 2. Enrichment Quality Validation
**Priority:** Low  
**Effort:** 3-4 hours

**Description:**
Add validation to enrichment output to catch common issues:
- Missing required fields (explanation, examples)
- Malformed code blocks
- Empty or too-short explanations (< 100 chars)
- Invalid Mermaid syntax
- Exercises without solutions

**Implementation:**
```python
def _validate_enrichment(enrichment: Dict) -> List[str]:
    """
    Validate enrichment quality.
    Returns list of warnings/errors.
    """
    issues = []
    
    if not enrichment.get("explanation") or len(enrichment["explanation"]) < 100:
        issues.append("Explanation too short or missing")
    
    if not enrichment.get("examples") or len(enrichment["examples"]) == 0:
        issues.append("No examples provided")
    
    for diagram in enrichment.get("diagrams", []):
        if not _validate_mermaid(diagram["source"]):
            issues.append(f"Invalid Mermaid syntax in diagram: {diagram.get('caption')}")
    
    return issues
```

**Files to Change:**
- `core/personas/implementations/professor.py` (add validation)
- `interfaces/server.py` (log validation issues)

---

### 3. Template-Specific Exercise Types
**Priority:** Medium  
**Effort:** 4-5 hours

**Description:**
Create more specialized exercise formats for different templates:

**Programming Language:**
- Multiple choice questions for syntax/concepts
- Fill-in-the-blank code
- Code ordering exercises
- Debugging challenges

**Framework/Library:**
- API documentation lookup exercises
- Integration challenges
- Best practices scenarios

**Domain Exploration:**
- Case study analysis questions
- Compare/contrast exercises
- Timeline construction
- Concept mapping

**Problem-Solving:**
- Step-by-step solution breakdown
- Alternative approach brainstorming
- Optimization challenges

**Implementation:**
Add `exercise_type` field and render differently in frontend.

**Files to Change:**
- `core/personas/implementations/professor.py` (generate varied types)
- `electron-app/src/renderer/app.js` (render different types)

---

## Category: Interactive Features

### 4. Code Editor for Programming Exercises
**Priority:** High  
**Effort:** 3-4 hours

**Description:**
Add interactive code editor with execution for programming curricula.

**Features:**
- Monaco editor or CodeMirror integration
- Syntax highlighting for detected language
- "Run Code" button
- Output panel
- "Check Solution" with pass/fail feedback
- Save progress per exercise

**Implementation:**
```javascript
function renderCodingExercise(exercise) {
  // Create Monaco editor instance
  const editor = monaco.editor.create(container, {
    value: exercise.starter_code,
    language: detectLanguage(exercise),
    theme: 'vs-dark'
  });
  
  // Run button
  runButton.addEventListener('click', async () => {
    const code = editor.getValue();
    const result = await executeCode(code, exercise.language);
    displayOutput(result);
  });
  
  // Check button
  checkButton.addEventListener('click', () => {
    const code = editor.getValue();
    const passed = checkSolution(code, exercise.solution, exercise.test_cases);
    displayFeedback(passed);
  });
}
```

**Files to Change:**
- `electron-app/src/renderer/index.html` (add editor container)
- `electron-app/src/renderer/app.js` (editor integration)
- `package.json` (add monaco-editor dependency)

---

### 5. Mermaid Diagram Renderer with Zoom
**Priority:** Medium  
**Effort:** 2 hours

**Description:**
Render Mermaid diagrams with interactive controls.

**Features:**
- Auto-render diagrams in enrichment view
- Zoom in/out controls
- Pan/drag
- Click to expand fullscreen
- Export as PNG

**Implementation:**
```javascript
function renderMermaidDiagram(diagram) {
  mermaid.initialize({ startOnLoad: false, theme: 'dark' });
  
  const container = document.createElement('div');
  container.innerHTML = diagram.source;
  
  mermaid.init(undefined, container);
  
  // Add zoom controls
  addZoomControls(container);
}
```

**Files to Change:**
- `electron-app/src/renderer/app.js` (diagram rendering)
- `electron-app/src/renderer/index.html` (zoom controls)
- `package.json` (add mermaid dependency)

---

### 6. Self-Assessment Checklist
**Priority:** Medium  
**Effort:** 1-2 hours

**Description:**
Make assessment criteria interactive checkboxes.

**Features:**
- Checkbox for each criterion
- Visual progress (3/5 checked)
- "I'm ready to complete" button appears when all checked
- Save completion state

**Implementation:**
```javascript
function renderAssessmentCriteria(criteria) {
  const checkedCount = criteria.filter(c => c.checked).length;
  const progress = (checkedCount / criteria.length) * 100;
  
  // Show complete button only when all checked
  if (checkedCount === criteria.length) {
    showCompleteButton();
  }
}
```

**Files to Change:**
- `electron-app/src/renderer/app.js` (checklist rendering)
- `learners/curriculum_manager.py` (save completion state)

---

## Category: User Experience

### 7. Empty Sections Bug Investigation
**Priority:** High  
**Effort:** 2-3 hours

**Description:**
Sometimes curriculum generation on first pass produces empty sections, but works on regeneration.

**Current Status:**
- Added preamble stripping to handle conversational LLM responses
- Added better error logging

**Next Steps:**
- Monitor logs to see actual LLM responses
- Identify specific cases where parsing fails
- Improve parser to handle edge cases
- Add fallback prompts if first attempt fails

**Files to Review:**
- `core/personas/implementations/professor.py` (lines 704-730, 785-825)

---

### 8. "Next Section" Suggestion Flow
**Priority:** Medium  
**Effort:** 1-2 hours

**Description:**
After completing a section, automatically suggest next section.

**Current Status:** Partially implemented in Phase 3

**Implementation:**
```javascript
async function handleSectionComplete(curriculumId, sectionId) {
  // Mark complete
  await completeSection(curriculumId, sectionId, reflectionData);
  
  // Find next section
  const nextSection = getNextSection(curriculumId, sectionId);
  
  if (nextSection) {
    // Show modal
    showNextSectionPrompt({
      current: sectionId,
      next: nextSection,
      onContinue: () => startCurriculumSection(curriculumId, nextSection.id),
      onBackToOutline: () => loadCurriculumDetail(curriculumId)
    });
  } else {
    // Curriculum complete!
    showCurriculumCompleteModal(curriculumId);
  }
}

function getNextSection(curriculumId, currentSectionId) {
  const curriculum = getCurriculum(curriculumId);
  const sections = curriculum.sections.filter(s => s.type === 'subheading');
  
  const currentIndex = sections.findIndex(s => s.id === currentSectionId);
  const nextIncomplete = sections.slice(currentIndex + 1).find(s => s.status !== 'completed');
  
  return nextIncomplete;
}
```

**Files to Change:**
- `electron-app/src/renderer/app.js` (add next section logic)
- `electron-app/src/renderer/index.html` (add next section modal)

---

### 9. Session Indicator Improvements
**Priority:** Low  
**Effort:** 2 hours

**Description:**
Enhance the session indicator for Phase 6.

**Features:**
- Floating indicator shows current section
- Time elapsed in session
- Quick actions: "Mark Complete", "End Session", "Ask Professor"
- Non-intrusive positioning
- Keyboard shortcut to show/hide (Cmd+Shift+L)

**Mockup:**
```
┌─────────────────────────────────────┐
│ 📚 Learning: Week 1.2 Data Types    │
│ ⏱️ 15 min                            │
│ [✓ Complete] [✕ End] [? Ask]        │
└─────────────────────────────────────┘
```

**Files to Change:**
- `electron-app/src/renderer/index.html` (indicator HTML)
- `electron-app/src/renderer/app.js` (indicator logic)
- `electron-app/src/renderer/styles.css` (indicator styling)

---

### 10. Curriculum Regeneration UX
**Priority:** Medium  
**Effort:** 1-2 hours

**Description:**
Improve the curriculum regeneration experience.

**Current Issues:**
- When clicking "Regenerate", dialog closes immediately
- User loses context of what they were looking at
- No feedback during regeneration

**Improvements:**
- Keep dialog open during regeneration
- Show loading spinner: "Regenerating curriculum..."
- Progress indicator if possible
- When complete, update dialog content in-place
- Show notification: "Curriculum regenerated with 18 sections"

**Implementation:**
```javascript
async function regenerateCurriculum() {
  // Don't close dialog
  // Show loading state
  showRegenerateLoadingState();
  
  // Regenerate
  const message = buildRegenerateMessage();
  const response = await sendQuery(message);
  
  // Wait for new curriculum data
  // Update dialog in place
  populateCurriculumReviewDialog(newCurriculumData);
  
  // Hide loading
  hideRegenerateLoadingState();
}
```

**Files to Change:**
- `electron-app/src/renderer/app.js` (regeneration flow)

---

## Category: Performance

### 11. Enrichment Caching Strategy
**Priority:** Medium  
**Effort:** 2-3 hours

**Description:**
Optimize enrichment to avoid expensive LLM calls.

**Current Status:**
Enrichment is saved to curriculum.json and not regenerated.

**Improvements:**
- Add "Regenerate Enrichment" button on section view
- Option to regenerate specific parts (e.g., just exercises)
- Background pre-enrichment for upcoming sections
- Batch enrich multiple sections at once

**Implementation:**
```python
async def pre_enrich_next_sections(curriculum_id, current_section_id, count=3):
    """
    Pre-enrich the next N sections in background.
    """
    next_sections = get_next_n_sections(curriculum_id, current_section_id, count)
    
    for section in next_sections:
        if not section.enriched:
            await enrich_section(curriculum_id, section.id, section.to_dict())
```

**Files to Change:**
- `core/personas/implementations/professor.py` (pre-enrichment)
- `interfaces/server.py` (background enrichment endpoint)
- `electron-app/src/renderer/app.js` (trigger pre-enrichment)

---

### 12. Progressive Enrichment Loading
**Priority:** Low  
**Effort:** 2 hours

**Description:**
Show enrichment content as it's generated rather than waiting for everything.

**Implementation:**
- Stream enrichment sections (explanation first, then diagrams, etc.)
- Show "Loading exercises..." while waiting
- Use WebSocket or SSE for streaming

**Files to Change:**
- `interfaces/server.py` (streaming endpoint)
- `electron-app/src/renderer/app.js` (handle streaming)

---

## Category: Content Customization

### 13. Difficulty Level Adjustment
**Priority:** Medium  
**Effort:** 3-4 hours

**Description:**
Allow users to adjust difficulty level of curriculum.

**Features:**
- Difficulty selector: Beginner / Intermediate / Advanced
- More/fewer sections based on difficulty
- Adjusted exercise complexity
- Modified pacing (estimated time per section)

**Implementation:**
Add difficulty parameter to template customization.

**Files to Change:**
- `learners/curriculum_template_manager.py` (difficulty logic)
- `electron-app/src/renderer/index.html` (difficulty selector in review dialog)

---

### 14. User-Created Templates
**Priority:** Low  
**Effort:** 6-8 hours

**Description:**
Allow users to create and save their own curriculum templates.

**Features:**
- "Save as Template" button on curriculum
- Template metadata (name, description, category)
- Template sharing (export/import JSON)
- Template library view

**Files to Create:**
- `learners/user_curriculum_templates.py` (user template storage)

**Files to Change:**
- `electron-app/src/renderer/app.js` (template creation UI)
- `interfaces/server.py` (user template endpoints)

---

## Category: Integration

### 15. Skill Package Auto-Detection Improvements
**Priority:** Medium  
**Effort:** 2 hours

**Description:**
Better integration with existing skill packages.

**Current Status:**
Simple keyword matching in section titles.

**Improvements:**
- Fuzzy matching with similarity scores
- Check concept lists, not just titles
- Detect skill packages for entire curriculum (not per-section)
- Show "Related skills" in curriculum detail view
- "Import from Skill" action to create curriculum from skill package

**Files to Change:**
- `core/personas/implementations/professor.py` (_detect_skill_package)

---

### 16. Export Curriculum to PDF/Markdown
**Priority:** Low  
**Effort:** 3-4 hours

**Description:**
Export curriculum with all enrichment to portable format.

**Features:**
- Export to PDF with table of contents
- Export to Markdown with proper formatting
- Include diagrams as images
- Code blocks with syntax highlighting

**Files to Change:**
- `learners/curriculum_manager.py` (export methods)
- `interfaces/server.py` (export endpoint)
- `electron-app/src/renderer/app.js` (export button)

---

### 17. Calendar Integration
**Priority:** Low  
**Effort:** 4-5 hours

**Description:**
Integrate curriculum progress with calendar.

**Features:**
- Suggested study schedule
- Add sections to calendar automatically
- Reminder notifications
- Time blocking for learning sessions

**Files to Change:**
- `core/integrations/calendar_integration.py` (new file)
- `learners/curriculum_manager.py` (scheduling logic)

---

## Category: Gamification (Future)

### 18. Achievement System
**Priority:** Low  
**Effort:** 6-8 hours

**Description:**
Add achievements and badges for motivation.

**Examples:**
- "First Steps" - Complete first section
- "Week Warrior" - Complete entire week in one day
- "Mastery Master" - Achieve mastery level 5 on 10 sections
- "Consistent Learner" - 7-day learning streak

**Files to Create:**
- `learners/achievement_manager.py` (achievement tracking)

---

### 19. Learning Streaks
**Priority:** Low  
**Effort:** 2-3 hours

**Description:**
Track consecutive days of learning.

**Features:**
- Daily streak counter
- Streak preservation (1 missed day grace period)
- Visual streak indicator in UI
- Notifications to maintain streak

**Files to Change:**
- `learners/curriculum_manager.py` (streak tracking)
- `electron-app/src/renderer/app.js` (streak display)

---

### 20. Visual Progress Animations
**Priority:** Low  
**Effort:** 2 hours

**Description:**
Add celebrations and animations.

**Features:**
- Confetti on curriculum completion
- Smooth progress bar animations
- Status change transitions
- Mastery level star animations

**Files to Change:**
- `electron-app/src/renderer/app.js` (animations)
- `electron-app/src/renderer/styles.css` (transitions)

---

## Implementation Priority

### High Priority (Next Session)
1. ✅ Template-aware enrichment (DONE - Feb 3)
2. ✅ Frontend template-based display (DONE - Feb 3)
3. Empty sections bug investigation
4. Code editor for exercises

### Medium Priority (Phase 4 Completion)
5. Better LLM prompt control
6. Mermaid diagram renderer
7. Self-assessment checklist
8. "Next section" suggestion
9. Template-specific exercise types

### Low Priority (Post Phase 23)
10. Enrichment caching improvements
11. Difficulty level adjustment
12. Skill package auto-detection
13. Session indicator improvements
14. Export to PDF/Markdown
15. Calendar integration

### Future Phases (Nice-to-Have)
16. User-created templates
17. Achievement system
18. Learning streaks
19. Visual animations
20. Progressive enrichment loading

---

## Notes

**Created:** February 3, 2026  
**Last Updated:** February 3, 2026  
**Status:** Living document - add new items as discovered

**Related Documents:**
- `PHASE23_PROGRESS_SUMMARY.md` - Current progress
- `PHASE23_CURRICULUM_SYSTEM.md` - Main specification
- `PHASE23_QUICK_REFERENCE.md` - Quick reference
