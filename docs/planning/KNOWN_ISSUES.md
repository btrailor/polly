# Known Issues & Technical Debt

**Last Updated:** February 3, 2026  
**Purpose:** Track bugs, technical debt, and polish items

---

## Critical Issues (Fix Immediately)

### 1. Resize Handle & Chat Popout Broken
**Severity:** HIGH  
**Affected:** Chat sidebar, Code Workspace  
**Description:** Resize handle and chat popout functionality no longer works  
**Impact:** User can't adjust sidebar width or pop out chat window  
**Related Code:**
- `electron-app/src/renderer/app.js` (resize handlers)
- `electron-app/src/renderer/styles/three-column.css`

**Steps to Reproduce:**
1. Try to drag resize handle between sidebar and main content
2. Click chat popout button

**Expected:** Resize works smoothly, popout opens new window  
**Actual:** Nothing happens

**Fix Estimate:** 2-3 hours  
**Priority:** Fix before next release

---

### 2. Conversation Context Reload Jarring UX
**Severity:** MEDIUM  
**Affected:** Chat UI  
**Description:** On server restart, conversation context reloads briefly, causing UI refresh that's jarring from UX perspective  
**Impact:** Disruptive experience, feels buggy  
**User Experience:**
- User sees chat history
- Server restarts (background)
- Chat briefly flashes/reloads
- Chat reappears (sometimes scrolled to wrong position)

**Desired Behavior:**
- Smooth reload without visible flash
- Maintain scroll position
- Loading indicator if reload takes >500ms

**Fix Estimate:** 4-6 hours  
**Priority:** High (polish issue)

---

## High Priority Issues

### 3. Deduplication System Overhaul Needed
**Severity:** MEDIUM  
**Affected:** Note creation (Phase 21)  
**Description:** Current deduplication model (asking whether to create note when others exist) is not effective  
**Problems:**
- Modal interrupts flow
- User often clicks "Create anyway" without reading
- Doesn't prevent duplicate knowledge
- No good merge workflow

**Your Feedback:**
> "We need to overhaul deduplication. The current model of asking whether or not we want to create the note when these others exist is not effective."

**Proposed Solutions:**
1. **Smarter Detection:** Only warn if >80% semantic similarity
2. **Inline Suggestions:** Show similar notes in sidebar (non-blocking)
3. **Post-Creation Merge:** Allow merging after note created
4. **Drag-Drop Editor:** Visual merge interface (from Feature #15 in FEATURES_TO_BUILD.md)

**Fix Estimate:** 2-3 days  
**Priority:** High (core feature quality)

---

### 4. Domain Tagging Misclassification
**Severity:** LOW-MEDIUM  
**Affected:** Domain auto-tagging  
**Description:** Python curriculum getting tagged as "Glyphs" domain when it's clearly a "Sigils" domain thing  
**Impact:** Incorrect organization, user must manually fix  
**Root Cause:** Domain classification logic needs refinement

**Example:**
```
Note: "Python Fundamentals Curriculum"
Tagged as: Glyphs (incorrect)
Should be: Sigils
```

**Fix Approach:**
- Review domain classification rules
- Add keyword weighting
- Improve context analysis
- Allow user to train classifier

**Fix Estimate:** 1-2 days  
**Priority:** Medium (quality of life)

---

### 5. Learning Profile Center UI Too Prominent
**Severity:** LOW  
**Affected:** Learning Profile page  
**Description:** Analytics section is far too prominent, feels unbalanced  
**Impact:** UI feels cluttered, important info buried  
**Feedback:**
> "Need to fix center area UI. The analytics section is far too prominent."

**Fix Approach:**
- Reduce analytics section size
- Move to collapsible panel
- Prioritize learning content over stats
- Better visual hierarchy

**Fix Estimate:** 3-4 hours  
**Priority:** Medium (UI polish)

---

## Medium Priority Issues

### 6. Pattern Learning Utilization Unclear
**Severity:** LOW  
**Status:** Documentation needed  
**Description:** Need conversation about pattern learning features and how they're being used across Polly to enhance capabilities  
**Impact:** Users don't understand when/how patterns are being learned  
**Action Items:**
- Document pattern learning system comprehensively
- Add UI indicators showing when patterns are applied
- User guide for pattern management
- Analytics showing pattern impact

**Priority:** Medium (transparency)

---

### 7. Compression System Utilization Unclear
**Severity:** LOW  
**Status:** Documentation needed  
**Description:** Users don't understand what compression system is compressing and how it decides when to unpack  
**Questions:**
- What content is being compressed?
- When does compression happen?
- How to view compressed vs full content?
- Can users control compression?

**Action Items:**
- Document compression system
- Add UI indicators (compressed token count)
- Settings for compression thresholds
- Ability to view compression savings

**Priority:** Medium (transparency)

---

## Low Priority Issues (Technical Debt)

### 8. Icon System Partially Complete
**Severity:** LOW  
**Status:** In progress  
**Description:** 20+ emoji icons replaced with Lucide icons (Feb 2, 2026), but more remain  
**Remaining Work:**
- Audit all remaining emoji usage
- Replace with appropriate Lucide icons
- Standardize icon sizing/colors
- Document icon usage guidelines

**Priority:** Low (polish, ongoing)

---

### 9. Settings API Endpoints Incomplete
**Severity:** LOW  
**Status:** Backend done, frontend partial  
**Description:** API Keys & Budget endpoints implemented (backend), but frontend UX needs polish  
**Completed:**
- Backend API endpoints ✅
- Basic frontend display ✅

**Needed:**
- Error handling for invalid keys
- Better loading states
- API key validation UI
- Budget alerts/warnings

**Priority:** Low (functional but not polished)

---

### 10. Test Coverage Gaps
**Severity:** LOW  
**Status:** Ongoing  
**Description:** Test coverage varies across modules  
**Current Status:**
- Phase 23: 26 tests (all passing) ✅
- Phase 14: 45 tests (48/51 passing) ⚠️
- Phase 11: Adequate coverage ✅
- UI: Minimal automated tests ⚠️

**Priority:** Low (improve over time)

---

## Features That Need Polish

### 11. Scroll-to-Bottom Button Missing
**Severity:** LOW  
**Affected:** Chat UI  
**Description:** No quick way to jump to bottom of long conversations  
**User Need:** When scrolled up in history, need button to jump to latest messages  
**Fix:** Add floating button (bottom-right) that appears when scrolled up

**UI Mock:**
```
[Chat history...]
[Scrolled up 200 messages]

┌─────────────────────────────┐
│                             │
│  [Older messages...]        │
│                             │
│          ⬇️  [Jump to latest]│
└─────────────────────────────┘
```

**Priority:** Low (quality of life)

---

### 12. Mode Indicator Needs Color
**Severity:** LOW  
**Affected:** Persona/mode UI  
**Description:** Mode dropdown needs colorful indicator for current mode  
**Current:** Text-only dropdown  
**Desired:** Color-coded mode badges

**Proposed:**
```
Current mode: [Architect: Plan] (orange indicator)
               [Designer: Vision] (purple indicator)
               [Programmer: Implement] (blue indicator)
```

**Priority:** Low (visual polish)

---

### 13. Loading Spinners Need Update
**Severity:** LOW  
**Affected:** All loading states  
**Description:** Current spinners are basic, should be cuter small dot/node graphics like OpenCode uses  
**Your Feedback:**
> "Update all loading spinners to cuter small dot/node graphics like OpenCode uses."

**Examples:**
- Three dots bouncing
- Pulsing circles
- Minimalist animated nodes

**Priority:** Low (aesthetic)

---

## Infrastructure Concerns

### 14. Snapshot Management System Needed
**Severity:** MEDIUM  
**Status:** Not implemented  
**Description:** Need smart snapshot management to avoid OpenCode-style bloat  
**Risks:** (from OpenCode research)
- Snapshot folder growing to hundreds of GB
- Git operations becoming slow
- System performance degradation

**Implementation Plan:**
- Phase 26 feature (snapshot system)
- Automatic cleanup of old snapshots
- Configurable retention (default: 7 days)
- Compression of older snapshots
- User control over snapshot frequency

**Priority:** Medium (preventive)

---

### 15. API Key Expiration Detection Missing
**Severity:** MEDIUM  
**Status:** Not implemented  
**Description:** No system to detect when API keys expire or hit rate limits  
**Impact:** Cryptic errors when keys stop working  
**Needed:**
- Detect 401/403 responses
- Alert user: "Your [Provider] API key may be invalid"
- Link to settings page
- Offer to test key validity

**Priority:** Medium (user experience)

---

### 16. Development Guardrails Needed
**Severity:** MEDIUM  
**Status:** Process needed  
**Description:** Once Polly is fully working, need research guardrails for development  
**Goal:** Roll out new features, enhancements without breaking existing functionality  
**Needed:**
- Automated testing suite
- Staging environment
- Feature flags
- Rollback procedures
- Beta testing program

**Your Concern:**
> "Once Polly is fully working we need to research guardrails for development. Ways to roll out new features, enhancements, etc. without breaking any existing functionality for the user."

**Priority:** Medium (stability)

---

## Future Considerations

### 17. Scalability Testing Needed
**Status:** Not started  
**Tests Needed:**
- 10,000+ notes in vault
- 1,000+ conversations
- 100+ curricula
- Large codebase analysis (50k+ files)
- 24-hour continuous operation

**Priority:** Low (before 1.0 release)

---

### 18. Mobile App Support
**Status:** Not planned for near future  
**Consideration:** Will Polly need mobile companion app?  
**Challenges:**
- Desktop-first UI design
- Local LLM on mobile (resource intensive)
- Sync between desktop and mobile

**Priority:** Future (post-1.0)

---

## Issue Tracking Process

### Reporting New Issues:

1. **Add to this document** under appropriate severity
2. **Estimate fix time** (rough guess)
3. **Assign priority** (Critical/High/Medium/Low)
4. **Link related code** (file paths, line numbers)
5. **Optional:** Create GitHub issue for tracking

### Resolving Issues:

1. **Fix the issue**
2. **Test thoroughly**
3. **Update this document** (mark as ✅ Fixed)
4. **Move to "Recently Fixed" section**
5. **Add to CHANGELOG.md**

### Severity Definitions:

- **CRITICAL:** Blocks core functionality, fix immediately
- **HIGH:** Important feature broken or major UX issue
- **MEDIUM:** Non-critical bug or quality-of-life issue
- **LOW:** Polish item, technical debt, nice-to-have

---

## Recently Fixed Issues ✅

### ✅ Chat Input Position (Fixed: TBD)
**Was:** Chat sidebar on right, disconnected from pages  
**Now:** Floating chat input at bottom (OpenCode-style) - **Planned in FEATURES_TO_BUILD.md #13**

### ✅ Lucide Icons Migration (Partial: Feb 2, 2026)
**Was:** Emoji icons throughout  
**Now:** 20+ icons replaced with professional Lucide icons  
**Remaining:** Some emojis still in use (see issue #8)

---

## Technical Debt Backlog

**Definition:** Code that works but needs refactoring for maintainability

1. **Frontend State Management:** Consider migrating to Redux/Zustand
2. **CSS Organization:** SCSS modules vs global CSS
3. **API Error Handling:** Standardize error response format
4. **Logging System:** Implement structured logging
5. **Configuration Validation:** JSON Schema for config.yaml

**Review Frequency:** Quarterly tech debt assessment

---

**Document Maintained By:** Development Team  
**Update Frequency:** Add issues as discovered, review weekly  
**Status Reviews:** Before each phase completion
