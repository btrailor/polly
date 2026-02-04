# Phase 0.5-0.7 Roadmap

**Current Status:** Phase 0.5 Day 1 Complete (14% done)  
**Next Steps:** Complete Phase 0.5, then move to critical foundation phases  
**Last Updated:** January 26, 2026

---

## Phase 0.5: Obsidian-Inspired UI Redesign (Current Phase)

**Duration:** 7-10 days  
**Status:** Day 1 Complete ✅ (Layout Foundation)  
**Priority:** Foundation for all future UI work  
**Progress:** 14% complete

### ✅ What's Done (Day 1)

1. **Complete Design System**
   - obsidian-theme.css - Professional dark theme with CSS variables
   - layout.css - Three-column CSS Grid layout
   - glitch-effects.css - Subtle retro accents
   - Changed accent color from purple to orange (#f0903b)

2. **Core Components**
   - Ribbon navigation (40px icon bar)
   - Three-column layout (Left Sidebar | Main Content | Right Sidebar)
   - Sidebar collapse/expand (Cmd+B, Cmd+/)
   - Sidebar resize with drag handles
   - State persistence (localStorage)

3. **Structure**
   - 12 page containers created
   - Page routing system working
   - Backward compatible with existing code

### 🔧 What Needs to Be Done

#### Day 2: Chat System Migration (2-3 days)
**Goal:** Make chat fully functional in new right sidebar layout

**Tasks:**
- [ ] Migrate existing chat content to right sidebar
- [ ] Implement page-specific conversation system
- [ ] Build conversation list UI in right sidebar
- [ ] Add conversation categories (by page/date/starred)
- [ ] Integrate with existing chat backend
- [ ] Test chat streaming, message display, input
- [ ] Add context indicators showing which page chat is associated with

**Files to Work On:**
- `electron-app/src/renderer/index.html` - Right sidebar chat structure
- `electron-app/src/renderer/styles/chat-sidebar.css` - Already created ✅
- `electron-app/src/renderer/app.js` - Chat state management

**Success Criteria:**
- ✅ Chat messages send/receive correctly
- ✅ Conversations persist across sessions
- ✅ Page context is preserved with conversations
- ✅ UI matches Obsidian aesthetic

---

#### Day 3: Left Sidebar Content Panels (2-3 days)
**Goal:** Build context-specific panels for left sidebar

**Tasks:**
- [ ] Create panel system for left sidebar
- [ ] **Dashboard page:** Quick links, recent conversations
- [ ] **Knowledge page:** File explorer tree, domain filter
- [ ] **Patterns page:** Pattern categories, search
- [ ] **Settings page:** Navigation tabs on left
- [ ] Add panel collapse/expand functionality
- [ ] Test panel switching as pages change

**Components to Build:**
- File explorer tree (for knowledge)
- Mini calendar widget
- Quick links panel
- Domain filter widget
- Pattern browser

**Success Criteria:**
- ✅ Each page has appropriate left sidebar content
- ✅ Panels are context-aware
- ✅ Navigation feels intuitive

---

#### Day 4-5: Polish & Fix Bugs (2-3 days)
**Goal:** Make everything work smoothly and look professional

**Tasks:**
- [ ] Fix any styling inconsistencies (DONE: removed white blocks ✅, changed to orange theme ✅)
- [ ] Remove debug code (DONE: removed yellow outlines ✅, cleaned console logs ✅)
- [ ] Fix titlebar button issues (DONE: buttons working, animation documented for later ✅)
- [ ] Ensure all existing features still work:
  - [ ] GitHub integration
  - [ ] Obsidian indexing
  - [ ] Settings persistence
  - [ ] Ollama connection
  - [ ] Domain configuration
  - [ ] Pattern learning
- [ ] Test keyboard shortcuts
- [ ] Verify localStorage persistence
- [ ] Check responsive behavior at different screen sizes
- [ ] Accessibility testing (focus states, keyboard navigation)

**Success Criteria:**
- ✅ No visual bugs
- ✅ All existing features functional
- ✅ Smooth animations
- ✅ Consistent styling throughout

---

#### Day 6-7: Content Migration & Empty States (2-3 days)
**Goal:** Migrate all remaining content to new layout and add polish

**Tasks:**
- [ ] Migrate Settings page content to new structure
- [ ] Migrate Knowledge page content
- [ ] Migrate Patterns page content
- [ ] Create empty state designs for placeholder pages:
  - [ ] Calendar: "Coming soon" with description
  - [ ] Mail: Feature preview
  - [ ] Code: Feature preview
  - [ ] Projects: Feature preview
  - [ ] Notes: Feature preview
  - [ ] Learning: Feature preview
  - [ ] Search: Feature preview
  - [ ] Domains: Feature preview
- [ ] Add tooltips where helpful
- [ ] Create loading states for async operations
- [ ] Add error states with helpful messages

**Success Criteria:**
- ✅ All functional pages work perfectly
- ✅ Placeholder pages look polished
- ✅ User knows what's coming vs what's ready
- ✅ No broken features from old layout

---

### Phase 0.5 Completion Checklist

**Core Functionality:**
- [x] Three-column layout working
- [x] Ribbon navigation functional
- [x] Sidebars collapse/expand
- [ ] Chat fully migrated to right sidebar
- [ ] All existing features working in new layout
- [ ] Settings page functional
- [ ] Knowledge indexing working
- [ ] Pattern learning working

**UI/UX Polish:**
- [x] Dark theme consistent throughout
- [x] Orange accent color applied (#f0903b)
- [x] No white blocks or styling inconsistencies
- [x] Debug code removed
- [ ] Empty states designed
- [ ] Loading states implemented
- [ ] Error states designed
- [ ] Tooltips added where helpful

**Technical:**
- [x] State persistence working
- [x] Keyboard shortcuts functional
- [ ] All localStorage keys working
- [ ] No console errors
- [ ] Performance smooth (no jank)
- [ ] Responsive at all screen sizes

**Documentation:**
- [ ] Update README with new UI screenshots
- [ ] Document keyboard shortcuts
- [ ] Create user guide for new layout
- [ ] Update PHASE_STATUS_SUMMARY.md

---

## Phase 0.6: Essential Feature Completion (Proposed)

**Duration:** 3-5 days  
**Status:** Not started  
**Priority:** High - Fix critical gaps before moving to advanced features

### Goals

1. **Make all functional pages fully working** (not just migrated)
2. **Add missing core features** that users expect
3. **Fix any performance issues**
4. **Ensure data integrity** (no lost conversations, settings, etc.)

### Tasks

#### Settings Page Enhancements
- [ ] Theme settings working (when Theme Customization is implemented)
- [ ] GitHub OAuth connection/disconnection
- [ ] Ollama model selection
- [ ] Domain configuration UI
- [ ] API key management
- [ ] Export/import settings

#### Knowledge Page Improvements
- [ ] File tree navigation
- [ ] File preview in sidebar
- [ ] Search within files
- [ ] Domain filtering
- [ ] Refresh index button
- [ ] Index status indicator

#### Chat Improvements
- [ ] Export conversation
- [ ] Delete conversation
- [ ] Star/favorite conversations
- [ ] Search conversations
- [ ] Conversation categories
- [ ] Context indicators

#### Performance
- [ ] Optimize large file tree rendering
- [ ] Lazy load conversations
- [ ] Debounce search inputs
- [ ] Cache expensive operations
- [ ] Profile and fix any bottlenecks

---

## Phase 0.7: User Experience Refinement (Proposed)

**Duration:** 3-5 days  
**Status:** Not started  
**Priority:** Medium - Make the app delightful to use

### Goals

1. **Smooth out rough edges**
2. **Add micro-interactions**
3. **Improve feedback and clarity**
4. **Make common actions faster**

### Tasks

#### Micro-interactions
- [ ] Hover states for all interactive elements
- [ ] Focus states clear and visible
- [ ] Click feedback (subtle animations)
- [ ] Drag feedback for resize handles
- [ ] Success/error toast notifications
- [ ] Loading spinners consistent

#### Keyboard Power User Features
- [ ] Command palette (Cmd+K) for quick navigation
- [ ] Quick switcher for conversations
- [ ] Search shortcuts
- [ ] Custom keyboard shortcuts in settings

#### User Feedback
- [ ] Toast notifications for actions (saved, deleted, indexed, etc.)
- [ ] Progress indicators for long operations
- [ ] Confirmation dialogs for destructive actions
- [ ] Helpful error messages with solutions
- [ ] Status bar showing connection status, index status

#### Onboarding
- [ ] First-run welcome screen
- [ ] Quick tour of UI elements
- [ ] Tooltips for first-time users
- [ ] Help documentation link
- [ ] Example conversations to demonstrate capabilities

---

## Critical Paths & Dependencies

### Before Starting Phase 1.5 (Domain Configuration)
You need Phase 0.5 complete because:
- Domain UI needs the new Settings page structure
- File explorer needs left sidebar panel system
- User needs stable UI to configure domains

### Before Starting Phase 11 (Multi-Model Routing)
You need Phase 0.5 complete because:
- Model selection UI needs Settings page
- Chat needs to show which model is being used
- Routing indicators need consistent UI

### Before Starting Phase 12 (Knowledge Graph)
You need Phase 0.5 complete because:
- Graph visualization needs main content area
- Node selection needs left sidebar panel
- Chat needs to reference graph nodes

---

## Estimated Timeline

### Current Phase Breakdown

**Phase 0.5 Remaining:** 6-7 days
- Day 2-3: Chat migration & page-specific system (2-3 days)
- Day 4-5: Left sidebar panels (2-3 days)
- Day 6-7: Polish, migration, empty states (2-3 days)

**Phase 0.6:** 3-5 days
- Essential feature completion
- Performance optimization
- Data integrity verification

**Phase 0.7:** 3-5 days
- UX refinement
- Micro-interactions
- Onboarding flow

**Total for 0.5-0.7:** 12-17 days (2-3.5 weeks)

### Recommended Approach

**Option A: Complete 0.5, then move to Phase 1.5**
- Finish Phase 0.5 (6-7 days)
- Skip 0.6 and 0.7 for now
- Start Phase 1.5 Domain Configuration
- Come back to 0.6/0.7 after core intelligence is built
- **Pro:** Faster to advanced features
- **Con:** UI might feel rough in places

**Option B: Complete 0.5-0.7, then Phase 1.5**
- Finish Phase 0.5 (6-7 days)
- Do essential completion 0.6 (3-5 days)
- Do UX refinement 0.7 (3-5 days)
- Start Phase 1.5 with polished UI
- **Pro:** Solid foundation, better user experience
- **Con:** Takes 2-3.5 weeks before advanced features

**Option C: Interleave UI and Backend**
- Finish Phase 0.5 (6-7 days)
- Start Phase 1.5 backend (4-5 days)
- Do Phase 0.6 while testing 1.5 (3-4 days)
- Finish Phase 1.5 UI integration (2 days)
- Do Phase 0.7 as buffer/polish time
- **Pro:** Balanced progress on both fronts
- **Con:** More context switching

---

## My Recommendation

**Do Option A: Complete Phase 0.5, then start Phase 1.5**

### Reasoning

1. **UI is usable now** - With Day 1 done, chat migration, and basic polish, the UI will be functional enough
2. **Core intelligence matters more** - Domain configuration, pattern learning, and knowledge graph are what make Polly special
3. **Can polish later** - Phases 0.6 and 0.7 can be done between major features as "polish sprints"
4. **User testing** - Better to get feedback on core features before perfecting UI

### Immediate Next Steps (This Week)

1. **Finish Phase 0.5 Days 2-3** (Chat migration) - 2-3 days
2. **Quick pass on left sidebar panels** (minimal viable) - 1 day
3. **Polish pass** (fix obvious bugs, clean up) - 1 day
4. **Start Phase 1.5** (Domain Configuration) - Begin next week

### This Gets You

- ✅ Functional new UI with chat working
- ✅ Basic left sidebar content
- ✅ Clean, consistent styling
- ✅ Ready to build advanced features on solid foundation
- ✅ ~1 week to Phase 1.5 (vs 2-3.5 weeks for full polish)

---

## Questions to Consider

1. **Are there any show-stopper bugs in the current UI?**
   - If yes, those need fixing before moving on
   - If no, Phase 0.5 is nearly done

2. **Do you want to user test before advanced features?**
   - If yes, need more polish (Option B)
   - If no, can move faster (Option A)

3. **How important is the first impression?**
   - Very important → Do Option B (full polish)
   - Somewhat important → Do Option C (balanced)
   - Less important → Do Option A (fast to features)

4. **What's your availability?**
   - Full-time on Polly → Option A or C work
   - Part-time → Option B spreads work better
   - Sporadic → Option A gets to milestone faster

---

## Phase 0.5 Known Issues & Decisions Made

### Issues Documented
1. **Titlebar button animation** - Buttons work but don't slide with sidebar
   - Documented in TITLEBAR_ANIMATION_ISSUE.md
   - Deferred to future work
   - Functional workaround in place

2. **Chat white blocks** - Fixed ✅
   - CSS variables were set to light theme
   - Updated to dark theme values

3. **Purple theme** - Changed to orange ✅
   - All #7f6df2 replaced with #f0903b
   - Consistent orange accent throughout

### Features Documented for Later
1. **Theme customization** - Documented in FEATURES_TO_BUILD.md
   - Light/dark mode toggle
   - Custom accent colors
   - Auto theme based on time
   - Planned for Phase 0.8 or 1.0

---

**Next Action:** Resume Phase 0.5 Day 2 - Chat System Migration

Focus on getting chat fully working in the right sidebar, then do a quick polish pass. After that, you'll have a solid UI foundation to build the core intelligence features (Phases 1.5, 11-16).
