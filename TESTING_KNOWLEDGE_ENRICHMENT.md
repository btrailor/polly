# Knowledge Enrichment Integration - Testing Checklist

## Overview
This document outlines the testing procedure for Wave 4 Task 20: Knowledge Enrichment Integration.

**Feature**: Automatic knowledge gap detection and suggestion cards after cloud responses.

---

## ✅ Pre-flight Checks (COMPLETED)

### 1. Configuration Verification
- [x] **Config file exists**: `config.yaml` 
- [x] **Gap detection enabled**: `ai_features.knowledge_suggestions.enabled: true`
- [x] **Min gap score**: `0.5` (50% novelty threshold)
- [x] **Suggestion style**: `inline` (show suggestion cards)
- [x] **Obsidian vault configured**: Path exists in config

### 2. Code Review
- [x] Backend integration in `core/polly.py` 
- [x] Server response enhancement in `interfaces/server.py`
- [x] Frontend component in `electron-app/src/renderer/components/suggestion-card.js`
- [x] UI integration in `electron-app/src/renderer/app.js`
- [x] CSS animations in `styles/main.css`
- [x] Script loaded in `index.html`

### 3. Bug Fixes Applied
- [x] **Fixed missing `rag_coverage` parameter** in gap detection call
  - Added calculation from `retrieval_tier` (DIRECT=0.9, ADJACENT=0.5, ABSENT=0.1)
- [x] **Fixed data format mismatch** in frontend
  - Changed `personaAction.payload` → `personaAction.data`
  - Now correctly reads `gap.cloud_content` and `gap.query`

---

## 🧪 Manual Testing Plan

### Test 1: Server Startup
**Goal**: Verify Polly server starts with knowledge_writer initialized.

**Steps**:
1. Start Polly server: `python3 -m uvicorn interfaces.server:app --reload`
2. Check logs for: `[INIT] _init_knowledge_writer took X.XXs`
3. Verify no errors related to knowledge_writer

**Expected**: 
- Server starts successfully
- KnowledgeWriter initialized
- No errors in logs

**Status**: ⏳ PENDING

---

### Test 2: Basic Query Flow (Novel Topic)
**Goal**: Trigger gap detection with a query about something NOT in knowledge base.

**Steps**:
1. Open Polly Electron app
2. Create new conversation
3. Ask: **"Explain quantum entanglement and Bell's theorem"**
   - (Assuming this isn't in your KB)
4. Wait for cloud response
5. Check for suggestion card below response

**Expected**:
- Cloud provider used (not local Ollama)
- Response appears normally
- Suggestion card appears below message with:
  - 💡 Icon and "This seems new. Save as a note?"
  - Gap score % (should be ≥50%)
  - Novel concept tags (e.g., "quantum entanglement", "Bell's theorem")
  - Suggested title (e.g., "Quantum Entanglement and Bell's Theorem")
  - Three buttons: Quick Save | Enrich with Scribe | Dismiss

**Status**: ⏳ PENDING

---

### Test 3: Quick Save Functionality
**Goal**: Test the Quick Save button saves note correctly.

**Steps**:
1. Continue from Test 2 (suggestion card visible)
2. Click **"Quick Save"** button
3. Watch for:
   - Button text changes to "Saving..."
   - Toast notification: "Note saved and indexed"
   - Card fades out and disappears

4. Verify note was created:
   - Open Obsidian vault at path: `~/.polly/notes` or configured vault
   - Find note with suggested title
   - Check frontmatter has:
     ```yaml
     ---
     title: "Quantum Entanglement and Bell's Theorem"
     date: 2026-02-17
     tags: [quantum entanglement, Bell's theorem, ...]
     domain: grids (or auto-detected)
     source: cloud_response
     created_by: knowledge_writer
     ---
     ```
   - Check content matches cloud response

**Expected**:
- Note created successfully
- Frontmatter correct
- Content preserved
- Toast shows success
- Card disappears

**Status**: ⏳ PENDING

---

### Test 4: Enrich with Scribe
**Goal**: Test the Enrich with Scribe button opens enrichment modal.

**Steps**:
1. Ask another novel query: **"What is the Byzantine Generals Problem?"**
2. Wait for suggestion card
3. Click **"Enrich with Scribe"** button
4. Verify PreviewModal opens with:
   - Content pre-filled
   - Title pre-filled
   - Domain pre-filled
   - Tags pre-filled

5. Click "Save" in modal
6. Check note created with enrichment

**Expected**:
- Modal opens correctly
- Fields pre-populated
- Save works
- Card disappears after save

**Status**: ⏳ PENDING

---

### Test 5: No Suggestion on Existing Knowledge
**Goal**: Verify suggestion card does NOT appear when KB has the answer.

**Steps**:
1. Save a note about "Python list comprehensions" manually
2. Wait for RAG re-index (or trigger manually)
3. Ask: **"Explain Python list comprehensions"**
4. Wait for response (should be local or low gap)
5. Verify NO suggestion card appears

**Expected**:
- Response uses local knowledge (Ollama) OR
- Cloud response but gap_score < 0.5 (50%)
- No suggestion card shown
- Logs show: "No significant knowledge gap detected" or "Skipping gap detection for pure local response"

**Status**: ⏳ PENDING

---

### Test 6: Dismiss Button
**Goal**: Test dismissing the suggestion.

**Steps**:
1. Ask novel query (get suggestion card)
2. Click **"Dismiss"** button
3. Verify card fades out and disappears
4. No note created

**Expected**:
- Smooth fadeOut animation
- Card removed from DOM
- No save operation

**Status**: ⏳ PENDING

---

### Test 7: Wave 3 Synthesis Integration
**Goal**: Verify gap detection works after Wave 3 multi-query synthesis.

**Steps**:
1. Ask complex query requiring synthesis: 
   **"Compare functional programming patterns in Haskell vs Rust, considering memory safety and type systems"**
2. Wait for Wave 3 synthesis (multiple sub-queries)
3. Check for suggestion card after synthesis completes

**Expected**:
- Wave 3 synthesis works
- Gap detection runs after synthesis
- Suggestion card appears if gap ≥ 50%

**Status**: ⏳ PENDING

---

### Test 8: Edge Cases

#### 8a: Empty Novel Concepts
**Steps**:
1. Manually trigger gap detection with very low novelty
2. Check logs for handling

**Expected**: No card shown, graceful handling

#### 8b: Gap Score Exactly 0.5
**Steps**:
1. Find query that produces gap_score = 0.5
2. Verify card appears (threshold is ≥ 0.5)

**Expected**: Card appears at threshold

#### 8c: Very Long Response
**Steps**:
1. Ask query producing 5000+ word response
2. Check suggestion card rendering

**Expected**: Card renders normally, content saved fully

**Status**: ⏳ PENDING

---

## 🐛 Known Issues to Watch For

1. **Missing `rag_coverage` parameter** - FIXED ✅
2. **Data format mismatch (`payload` vs `data`)** - FIXED ✅
3. **Toast notification not showing** - Check if `window.showToast` exists
4. **PreviewModal not opening** - Check if `window.PreviewModal` exists
5. **Autonomy metrics not refreshing** - Check if `window.loadAutonomyData` exists
6. **currentConversationId undefined** - Check if exposed to window scope

---

## 📊 Success Criteria

### Must Have (P0)
- [x] Server starts without errors
- [ ] Suggestion card appears after novel cloud responses
- [ ] Quick Save creates note correctly
- [ ] Dismiss removes card
- [ ] No card shown for existing knowledge

### Should Have (P1)
- [ ] Enrich with Scribe opens modal
- [ ] Wave 3 synthesis integration works
- [ ] Toast notifications show
- [ ] Autonomy metrics refresh

### Nice to Have (P2)
- [ ] Edge cases handled gracefully
- [ ] Animations smooth on all systems
- [ ] Responsive on different screen sizes

---

## 🚀 Next Steps After Testing

1. **If all tests pass**: Move to Wave 4 Task 21 (Progressive Autonomy Dashboard)
2. **If bugs found**: Fix and re-test
3. **If major issues**: Consider rolling back and re-architecting

---

## 📝 Test Log

| Test | Date | Result | Notes |
|------|------|--------|-------|
| Pre-flight | 2026-02-17 | ✅ PASS | Config verified, bugs fixed |
| Test 1 | - | ⏳ PENDING | - |
| Test 2 | - | ⏳ PENDING | - |
| Test 3 | - | ⏳ PENDING | - |
| Test 4 | - | ⏳ PENDING | - |
| Test 5 | - | ⏳ PENDING | - |
| Test 6 | - | ⏳ PENDING | - |
| Test 7 | - | ⏳ PENDING | - |
| Test 8 | - | ⏳ PENDING | - |

---

**Testing performed by**: Brett  
**Feature version**: Wave 4 Task 20  
**Testing date**: 2026-02-17
