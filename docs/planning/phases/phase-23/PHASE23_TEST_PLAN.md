# Phase 23: Curriculum Learning System - Comprehensive Test Plan

**Created:** February 3, 2026  
**Status:** Implementation Complete - Testing Pending  
**Purpose:** Systematic testing of all 6 phases of curriculum learning system

---

## Test Environment Setup

### Prerequisites
- ✅ Server running on `http://127.0.0.1:11436`
- ✅ Electron app running
- ✅ Router v2 enabled in config
- ✅ API keys configured (Anthropic, OpenAI, etc.)
- ✅ Vault path configured
- ✅ Professor persona available

### Data Setup
- Test curriculum: "Python Learning Curriculum" (already exists)
- Clean test environment or existing data OK
- Budget limits sufficient for API calls (~$2-3 for full test suite)

---

## Phase 1: Core Infrastructure Tests

### Test 1.1: Curriculum Creation
**Goal:** Verify curriculum can be created and saved

**Steps:**
1. Open Polly Learning page
2. Click "Create Curriculum" (or use existing)
3. Verify curriculum appears in sidebar
4. Check `vault/.polly/curricula/{curriculum-id}/curriculum.json` exists
5. Verify JSON structure matches expected schema

**Expected:**
- Curriculum saved to vault
- JSON contains: id, title, goal, sections, status
- Sections include: id, title, type, description, concepts, estimated_time

**Status:** ⏳ Pending


### Test 1.2: Curriculum Listing
**Goal:** Verify curricula list loads correctly

**Steps:**
1. Refresh Learning page
2. Check sidebar shows all curricula
3. Verify status badges (draft/active/completed/paused)
4. Click different curricula
5. Verify correct curriculum loads

**Expected:**
- All curricula listed
- Status badges accurate
- Click navigation works

**Status:** ⏳ Pending


### Test 1.3: Section Operations
**Goal:** Verify section start/complete workflow

**Steps:**
1. Open curriculum detail view
2. Click "Start" on not-started section
3. Verify status changes to "in_progress"
4. Click "Complete" button
5. Fill mastery level (1-5) and optional reflection
6. Verify section marked completed
7. Refresh and verify state persists

**Expected:**
- Status transitions work (not_started → in_progress → completed)
- Timestamps recorded (started_at, completed_at)
- Mastery level saved
- State persists across refreshes

**Status:** ⏳ Pending


### Test 1.4: Progress Calculation
**Goal:** Verify progress stats calculate correctly

**Steps:**
1. Note initial progress (e.g., 0%)
2. Complete 1 section
3. Verify progress updates (e.g., 1/10 = 10%)
4. Complete another section
5. Verify progress increments (e.g., 2/10 = 20%)

**Expected:**
- Progress percentage accurate
- Completed sections count correct
- In-progress sections tracked
- Stats update in real-time

**Status:** ⏳ Pending

---

## Phase 2: Template System Tests

### Test 2.1: Template Listing
**Goal:** Verify all 5 templates load correctly

**Steps:**
1. Access template selection (via API or future UI)
2. Call `GET /polly/templates/list`
3. Verify 5 templates returned:
   - programming-language
   - framework-library
   - skill-acquisition
   - problem-solving
   - domain-exploration

**Expected:**
- All 5 templates present
- Each has: id, name, category, description, structure

**Status:** ⏳ Pending


### Test 2.2: Template Detection
**Goal:** Verify AI detects correct template from goal

**Test Cases:**
- "Learn Python" → programming-language (confidence ≥0.8)
- "Master React" → framework-library (confidence ≥0.8)
- "Learn Monome Norns" → skill-acquisition (confidence ≥0.7)
- "Optimize my API" → problem-solving (confidence ≥0.7)
- "Explore machine learning" → domain-exploration (confidence ≥0.7)

**Steps:**
1. Call `POST /polly/templates/detect` with each goal
2. Verify template_id matches expected
3. Verify confidence score ≥ threshold

**Expected:**
- Correct template detected for each goal
- Confidence scores reasonable
- Fallback behavior if ambiguous

**Status:** ⏳ Pending


### Test 2.3: Template Customization
**Goal:** Verify templates customize correctly

**Steps:**
1. Get programming-language template
2. Customize with:
   - language: "Python"
   - experience: "Intermediate"
   - goal: "Build web applications"
3. Verify sections adapted:
   - Language-specific content
   - Difficulty appropriate
   - Focus areas included

**Expected:**
- Template sections modified
- Placeholders replaced
- Difficulty adjusted
- Focus areas added/removed as needed

**Status:** ⏳ Pending

---

## Phase 3: Engagement UI Tests

### Test 3.1: Learning Page Navigation
**Goal:** Verify learning page UI works correctly

**Steps:**
1. Click Learning tab in sidebar
2. Verify layout:
   - Left sidebar with curriculum list
   - Center area with detail/dashboard
   - Right panel for chat (if applicable)
3. Click curriculum in sidebar
4. Verify detail view loads

**Expected:**
- Clean navigation
- Responsive layout
- Curriculum list visible
- Detail view renders correctly

**Status:** ⏳ Pending


### Test 3.2: Curriculum Detail View
**Goal:** Verify curriculum detail displays correctly

**Steps:**
1. Open curriculum detail
2. Check header shows:
   - Curriculum title
   - Goal description
   - Progress bar
   - Stats (X/Y sections, completion %)
3. Check outline tree shows:
   - Week headers
   - Section subsections
   - Status icons
   - Action buttons

**Expected:**
- All metadata displays
- Progress bar animates correctly
- Outline tree expandable
- Status icons color-coded
- Buttons appear per status

**Status:** ⏳ Pending


### Test 3.3: Section Interaction
**Goal:** Verify section buttons work

**Test Each Button:**
- "Start" button (not_started sections)
- "View" button (in_progress/completed sections)
- "Complete" button (in_progress sections)

**Steps:**
1. Click "Start" on not-started section
2. Verify enrichment loading indicator appears
3. Wait for enrichment (~10-30s)
4. Verify enriched content displays
5. Click "View" on same section
6. Verify content loads instantly (cached)
7. Click "Complete"
8. Verify dialog appears for mastery/reflection

**Expected:**
- All buttons functional
- Loading states clear
- Enrichment displays correctly
- View loads instantly (cached)
- Complete dialog works

**Status:** ⏳ Pending

---

## Phase 4: Section Enrichment Tests

### Test 4.1: Enrichment Generation
**Goal:** Verify Professor generates rich content

**Steps:**
1. Start unenriched section
2. Wait for enrichment (~10-30s)
3. Check generated content includes:
   - Detailed explanation (markdown formatted)
   - At least 1 diagram (Mermaid)
   - At least 2 code examples
   - At least 2 practice exercises
   - At least 2 resources
   - Assessment criteria (3-5 items)

**Expected:**
- All content types generated
- Explanations detailed and relevant
- Diagrams render correctly (no parse errors)
- Examples have proper syntax
- Exercises have starter code and solutions
- Resources are relevant and accessible

**Status:** ⏳ Pending


### Test 4.2: Skill Package Integration
**Goal:** Verify skill packages enhance enrichment

**Steps:**
1. Enrich section with related skill package
   (e.g., Python data types section may relate to python-fundamentals skill)
2. Check if enrichment references skill content
3. Verify diagrams/exercises adapted from skill

**Expected:**
- Skill packages detected when relevant
- Content appropriately adapted
- No duplicate content
- Seamless integration

**Status:** ⏳ Pending


### Test 4.3: Enrichment Caching
**Goal:** Verify enrichment cached correctly

**Steps:**
1. Enrich section (wait ~10-30s)
2. Close section view
3. Open same section again
4. Verify content loads instantly (<1s)
5. Check `curriculum.json` has `enriched: true`
6. Verify enrichment fields populated

**Expected:**
- Instant load on second view
- JSON shows enriched: true
- All enrichment fields saved
- No re-generation

**Status:** ⏳ Pending


### Test 4.4: Mermaid Diagram Rendering
**Goal:** Verify diagrams render without errors

**Steps:**
1. Enrich section with diagrams
2. Check each diagram:
   - Mermaid syntax valid
   - No parse errors in console
   - Diagram renders visually
   - Caption displays
3. Test different diagram types (flowchart, graph, sequence)

**Expected:**
- All diagrams render correctly
- No "diagram" icon error (fixed to "git-graph")
- No parse errors with parentheses (fixed)
- Captions display below diagrams

**Status:** ⏳ Pending


### Test 4.5: View Button Functionality
**Goal:** Verify View buttons work for all states

**Test Cases:**
1. In-progress section with View button
2. Completed section with View button

**Steps:**
1. Complete a section
2. Return to curriculum outline
3. Click "View" button
4. Verify enriched content displays
5. Verify mastery stars show for completed sections

**Expected:**
- View button present for in_progress/completed
- Content loads from cache
- Mastery stars visible for completed
- No errors in console

**Status:** ⏳ Pending

---

## Phase 5: Progress Visualization Tests

### Test 5.1: Progress Bar Display
**Goal:** Verify animated progress bar works

**Steps:**
1. Open curriculum with partial completion (e.g., 3/10 sections)
2. Check progress bar:
   - Shows correct percentage (e.g., 30%)
   - Gradient bar fills to correct width
   - Breakdown shows: X completed, Y in progress, Z not started
3. Complete another section
4. Verify progress bar updates

**Expected:**
- Progress bar accurate
- Gradient animation smooth
- Percentage displays correctly
- Breakdown counts match actual status
- Real-time updates after completion

**Status:** ⏳ Pending


### Test 5.2: Section Card Enhancements
**Goal:** Verify section cards show all progress info

**Check Each Card Shows:**
- Estimated time (e.g., "2 hours")
- Concepts count (e.g., "3 concepts")
- Time spent (if started, e.g., "45m spent")
- Completion timestamp (if completed, e.g., "Completed Feb 3, 2026")
- Color-coded left border (green/orange/gray)

**Steps:**
1. Check not-started section card
2. Check in-progress section card
3. Check completed section card
4. Verify all metadata displays correctly

**Expected:**
- All fields present and formatted
- Time calculations correct
- Timestamps in readable format
- Colors match status

**Status:** ⏳ Pending


### Test 5.3: Mastery Stars Display
**Goal:** Verify star ratings work correctly

**Test Cases:**
- Mastery 1/5 → ★☆☆☆☆
- Mastery 3/5 → ★★★☆☆
- Mastery 5/5 → ★★★★★

**Steps:**
1. Complete section with mastery level 3
2. Verify stars display: ★★★☆☆
3. Hover over stars
4. Verify tooltip shows "Mastery Level: 3/5"
5. Complete another section with level 5
6. Verify stars display: ★★★★★

**Expected:**
- Correct number of filled/empty stars
- Golden color (#f0c030)
- Tooltip informative
- Visible in section cards

**Status:** ⏳ Pending


### Test 5.4: Time Tracking Accuracy
**Goal:** Verify time tracking works

**Steps:**
1. Note time before starting section
2. Start section
3. Work for 5 minutes
4. Complete section
5. Check `time_spent_minutes` in JSON
6. Verify it's approximately 5 minutes

**Note:** Manual verification needed - automatic time tracking not yet implemented

**Expected:**
- Time tracking field exists
- Manual entry works in complete dialog
- Displays correctly in UI

**Status:** ⏳ Pending

---

## Phase 6: Guided Learning Tests

### Test 6.1: Code Editor Functionality
**Goal:** Verify code editor works properly

**Steps:**
1. Open section with exercises
2. Check code editor:
   - Starter code pre-filled
   - Editable textarea
   - Syntax highlighting (basic monospace styling)
   - Resizable (vertical drag)
3. Edit code
4. Verify changes persist while on page
5. Test "Reset" button
6. Verify starter code restored

**Expected:**
- Editor functional
- Code editable
- Reset works
- Clean UI

**Status:** ⏳ Pending


### Test 6.2: Code Execution - Success Case
**Goal:** Verify successful code execution

**Test Code:**
```python
print("Hello World")
name = "Alice"
print(f"My name is {name}")
```

**Steps:**
1. Paste test code into editor
2. Click "Run Code" button
3. Verify output console appears
4. Check output shows:
   ```
   Hello World
   My name is Alice
   ```
5. Verify output color is green (success)

**Expected:**
- Code executes successfully
- Output displays correctly
- Green color coding
- Console visible
- No errors

**Status:** ⏳ Pending


### Test 6.3: Code Execution - Syntax Error
**Goal:** Verify syntax error handling

**Test Code:**
```python
print("missing closing quote)
```

**Steps:**
1. Paste code with syntax error
2. Click "Run Code"
3. Verify error message displays
4. Check error color is red
5. Verify error message is helpful

**Expected:**
- Error caught and displayed
- Red color coding
- Clear error message
- No app crash

**Status:** ⏳ Pending


### Test 6.4: Code Execution - Runtime Error
**Goal:** Verify runtime error handling

**Test Code:**
```python
x = 10 / 0
```

**Steps:**
1. Paste code with runtime error
2. Click "Run Code"
3. Verify error message displays
4. Check for "ZeroDivisionError"

**Expected:**
- Runtime error caught
- Clear error message
- Stack trace visible
- Red color coding

**Status:** ⏳ Pending


### Test 6.5: Code Execution - Timeout
**Goal:** Verify timeout protection works

**Test Code:**
```python
while True:
    pass
```

**Steps:**
1. Paste infinite loop code
2. Click "Run Code"
3. Wait 5 seconds
4. Verify timeout message displays
5. Check color is orange
6. Verify message: "Code execution timed out after 5 seconds"

**Expected:**
- Execution stops after 5s
- Timeout message clear
- Orange color coding
- No system hang

**Status:** ⏳ Pending


### Test 6.6: Solution Validation - Correct
**Goal:** Verify Professor validates correct solutions

**Exercise:** "Assign and Print Variables"

**Correct Solution:**
```python
name = "Alice"
age = 25
is_student = True
print(f"My name is {name}, I am {age} years old, and it is {is_student} that I am a student.")
```

**Steps:**
1. Paste correct solution
2. Click "Check Solution" button
3. Wait ~5-10 seconds for Professor feedback
4. Verify feedback panel shows:
   - ✓ icon (green)
   - "Great work!" or similar positive message
   - Constructive feedback
   - Strengths identified

**Expected:**
- Validation completes in ~5-10s
- Feedback is positive and constructive
- Green success indicator
- Toast notification "Exercise completed successfully!"

**Status:** ⏳ Pending


### Test 6.7: Solution Validation - Incorrect
**Goal:** Verify Professor provides helpful feedback for wrong solutions

**Incorrect Solution:**
```python
name = "Alice"
age = 25
# Missing is_student
print(name, age)
```

**Steps:**
1. Paste incorrect solution
2. Click "Check Solution"
3. Wait for feedback
4. Verify feedback shows:
   - ⓘ icon (orange)
   - "Keep trying!" or similar encouraging message
   - Specific improvements needed
   - Helpful hints

**Expected:**
- Validation completes
- Feedback is constructive, not discouraging
- Identifies specific issues
- Provides actionable hints
- Orange indicator

**Status:** ⏳ Pending


### Test 6.8: Solution Reveal
**Goal:** Verify solution reveal works

**Steps:**
1. Find exercise with solution
2. Click "Show Solution" expandable
3. Verify solution code displays
4. Check code formatting

**Expected:**
- Solution expandable works
- Code displays in monospace
- Syntax highlighting (basic)
- Properly escaped HTML

**Status:** ⏳ Pending


### Test 6.9: Multiple Exercises
**Goal:** Verify multiple exercises work independently

**Steps:**
1. Open section with 2+ exercises
2. Complete Exercise 1 (run code, validate)
3. Scroll to Exercise 2
4. Verify Exercise 2 state independent:
   - Separate editor
   - Separate output console
   - Separate feedback panel
5. Complete Exercise 2
6. Verify both exercises show individual results

**Expected:**
- Each exercise isolated
- No state interference
- All buttons functional per exercise
- Clean UI separation

**Status:** ⏳ Pending


### Test 6.10: Exercise Reset
**Goal:** Verify reset functionality

**Steps:**
1. Edit exercise code significantly
2. Run modified code
3. Click "Reset" button
4. Verify starter code restored
5. Verify output console cleared (or hidden)
6. Verify feedback panel cleared
7. Check toast: "Code reset to starter template"

**Expected:**
- Code reverts to starter
- All state cleared
- Toast notification shown
- Ready for fresh attempt

**Status:** ⏳ Pending

---

## Integration Tests

### Test I.1: End-to-End Curriculum Flow
**Goal:** Verify complete user journey

**Scenario:** New user wants to learn Python

**Steps:**
1. User clicks Learning tab
2. User clicks "Create Curriculum" (future feature - or creates in chat)
3. Professor generates Python curriculum outline
4. User reviews and saves curriculum
5. Curriculum appears in sidebar
6. User clicks curriculum
7. User clicks "Start" on Week 1.1
8. Section enriches (~10-30s)
9. User reads explanation
10. User views diagram
11. User reads examples
12. User attempts exercise
13. User runs code
14. User gets feedback from Professor
15. User iterates and improves
16. User clicks "Complete"
17. User rates mastery (4/5)
18. Progress updates (1/X sections, Y%)
19. User continues to next section

**Expected:**
- Smooth flow, no errors
- All features work together
- Progress tracked accurately
- User feels guided and supported

**Status:** ⏳ Pending


### Test I.2: Multiple Curricula Management
**Goal:** Verify managing multiple curricula works

**Steps:**
1. Create/activate 2+ curricula (e.g., Python, React)
2. Work on Python curriculum
3. Switch to React curriculum
4. Verify correct curriculum loads
5. Complete section in React
6. Switch back to Python
7. Verify progress preserved in both

**Expected:**
- Multiple curricula coexist
- Switching works cleanly
- Progress isolated per curriculum
- No state interference

**Status:** ⏳ Pending


### Test I.3: Browser Refresh Persistence
**Goal:** Verify state persists across refresh

**Steps:**
1. Start section, enrich, complete exercise
2. Refresh browser (Cmd+R / Ctrl+R)
3. Navigate back to Learning page
4. Open same curriculum
5. Verify:
   - Enrichment still present (cached)
   - Progress maintained
   - Section status correct

**Expected:**
- All state persists
- No data loss
- Immediate load (no re-enrichment)

**Status:** ⏳ Pending


### Test I.4: Error Recovery
**Goal:** Verify graceful error handling

**Test Scenarios:**
1. **Network failure during enrichment:**
   - Disconnect network
   - Start section
   - Verify error message
   - Reconnect
   - Retry enrichment

2. **API timeout:**
   - Simulate slow API
   - Verify timeout message
   - Retry works

3. **Invalid code execution:**
   - Covered in individual tests

**Expected:**
- Clear error messages
- No app crashes
- Retry mechanisms work
- User not blocked

**Status:** ⏳ Pending

---

## Performance Tests

### Test P.1: Enrichment Speed
**Goal:** Measure enrichment performance

**Benchmarks:**
- Simple section: <15 seconds
- Complex section: 15-30 seconds
- Very complex section: 30-45 seconds (acceptable)

**Steps:**
1. Start timer
2. Click "Start" on unenriched section
3. Wait for enrichment
4. Stop timer when content displays
5. Record time

**Test 5 sections, calculate average**

**Expected:**
- Average <20 seconds
- No enrichment >45 seconds
- Loading indicator visible entire time

**Status:** ⏳ Pending


### Test P.2: Code Execution Speed
**Goal:** Measure execution performance

**Benchmarks:**
- Simple print: <500ms
- Complex calculation: <2 seconds
- Timeout: 5 seconds (by design)

**Test Code:**
```python
# Simple
print("Hello")

# Complex
total = sum(range(1000000))
print(total)
```

**Steps:**
1. Run simple code, measure time
2. Run complex code, measure time
3. Verify acceptable

**Expected:**
- Simple: instant (<500ms)
- Complex: fast (<2s)
- Consistent performance

**Status:** ⏳ Pending


### Test P.3: UI Responsiveness
**Goal:** Verify UI stays responsive during operations

**Steps:**
1. Start section enrichment
2. While loading, try:
   - Scrolling
   - Switching curricula
   - Clicking other buttons
3. Verify UI responsive (no blocking)

**Expected:**
- No UI freeze
- Operations async
- Smooth user experience

**Status:** ⏳ Pending

---

## Regression Tests

### Test R.1: Existing Features Unaffected
**Goal:** Verify Phase 23 doesn't break existing functionality

**Test Areas:**
- Chat functionality
- Note-taking system
- Integrations page
- Settings page
- Mental models system
- Pattern learning

**Steps:**
1. Test each major feature
2. Verify works as before
3. Check for console errors

**Expected:**
- No regressions
- Clean console
- All features operational

**Status:** ⏳ Pending


### Test R.2: Router v2 Integration
**Goal:** Verify curriculum system uses Router v2 correctly

**Steps:**
1. Monitor server logs during enrichment
2. Check which models used
3. Verify intelligent routing
4. Check budget tracking updates

**Expected:**
- Router v2 active
- Appropriate models selected
- Budget tracked
- No fallback to v1

**Status:** ⏳ Pending

---

## Acceptance Criteria

### Must Pass (Critical)
- ✅ All Phase 1 tests pass (core infrastructure)
- ✅ All Phase 6 tests pass (guided learning)
- ✅ Integration Test I.1 passes (end-to-end flow)
- ✅ No data loss or corruption
- ✅ No security vulnerabilities in code execution
- ✅ Error handling graceful

### Should Pass (Important)
- ✅ All Phase 2 tests pass (templates)
- ✅ All Phase 3 tests pass (UI)
- ✅ All Phase 4 tests pass (enrichment)
- ✅ All Phase 5 tests pass (progress)
- ✅ Performance tests within benchmarks
- ✅ No regressions in existing features

### Nice to Have (Enhancement)
- Advanced error recovery
- Performance optimization
- UI polish
- Additional test coverage

---

## Known Issues & Limitations

### Current Limitations
1. **Code execution language:** Python only (intentional - curriculum focused)
2. **Enrichment time:** 10-30 seconds (unavoidable with LLM generation)
3. **Time tracking:** Manual entry in complete dialog (automatic tracking not implemented)
4. **Template creation:** UI not yet built (Phase 23b future work)

### Fixed Issues
1. ✅ Mermaid diagram parsing errors (fixed with guideline updates)
2. ✅ Lucide icon "diagram" error (fixed to "git-graph")
3. ✅ View button missing for completed sections (fixed)
4. ✅ Learning session div hidden (fixed)

### Future Enhancements
- Automatic time tracking with timers
- More languages for code execution (JavaScript, etc.)
- Collaborative learning features
- Adaptive difficulty based on performance
- Spaced repetition integration
- Calendar integration for scheduled learning

---

## Test Execution Log

### Test Run 1: [Date]
**Tester:** [Name]  
**Duration:** [Time]  
**Results:** [Pass/Fail counts]  
**Notes:** [Observations]

[Add more test runs as executed]

---

## Summary

**Total Tests Defined:** 47 tests
- Phase 1: 4 tests
- Phase 2: 3 tests
- Phase 3: 3 tests
- Phase 4: 5 tests
- Phase 5: 4 tests
- Phase 6: 10 tests
- Integration: 4 tests
- Performance: 3 tests
- Regression: 2 tests

**Test Coverage:**
- ✅ Core infrastructure
- ✅ Template system
- ✅ UI/UX flows
- ✅ Content enrichment
- ✅ Progress tracking
- ✅ Interactive exercises
- ✅ Code execution
- ✅ AI validation
- ✅ Error handling
- ✅ Performance
- ✅ Regression

**Estimated Test Time:** 4-6 hours for full suite

**Priority Order:**
1. Integration Test I.1 (end-to-end flow)
2. Phase 6 tests (guided learning core value)
3. Phase 1 tests (data integrity)
4. Phase 4 tests (enrichment quality)
5. Phase 5 tests (progress tracking)
6. Phase 3 tests (UI/UX)
7. Phase 2 tests (templates)
8. Performance tests
9. Regression tests

---

**Next Steps:**
1. Execute high-priority tests first
2. Document results in test log
3. File issues for any failures
4. Iterate fixes and re-test
5. Update documentation with findings
6. Mark Phase 23 fully tested when all critical tests pass
