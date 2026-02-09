# Phase 17: VSCode Fork Proof of Concept

**Status:** 📋 Planned  
**Duration:** 2 weeks  
**Purpose:** Validate VSCode fork approach for Polly Code by creating a working prototype  
**Prerequisites:** Research complete (PHASE17_CURSOR_FORK_RESEARCH.md)

---

## Overview

This POC will fork VSCodium, add basic Polly features (ribbon navigation, chat panel), and test the merge process with one upstream update. The goal is to **validate that maintenance is manageable** and **integration is feasible** before committing to full Phase 17 implementation.

---

## Success Criteria

### Must Have (POC Success)

✅ Fork VSCodium successfully  
✅ Add Polly ribbon navigation (replace activity bar)  
✅ Add basic Polly chat panel (right sidebar)  
✅ Test merge process with one VSCode update  
✅ Document maintenance complexity  
✅ Evaluate integration feasibility  

### Nice to Have (If Time Permits)

- Customize theme to match Polly design system
- Add Polly-specific command to command palette
- Test extension API for future features

---

## Week 1: Fork & Basic Integration

### Day 1-2: Fork Setup

**Tasks:**
1. **Fork VSCodium Repository**
   ```bash
   git clone https://github.com/VSCodium/vscodium.git polly-code
   cd polly-code
   git remote add upstream https://github.com/VSCodium/vscodium.git
   ```

2. **Build and Test Base**
   - Follow VSCodium build instructions
   - Verify it builds and runs
   - Test basic functionality (open file, edit, save)

3. **Create Polly Branch**
   ```bash
   git checkout -b polly-integration
   ```

4. **Document Base State**
   - Note current VSCode version
   - Document build process
   - Create build script for Polly

**Deliverables:**
- Working VSCodium fork
- Build documentation
- Base state documented

---

### Day 3-4: Ribbon Navigation

**Goal:** Replace VSCode's activity bar with Polly's ribbon navigation

**Tasks:**
1. **Study Activity Bar Implementation**
   - Locate activity bar code in VSCode source
   - Understand how it integrates with workbench
   - Document extension points

2. **Create Ribbon Component**
   - Port Polly's ribbon CSS/HTML from electron-app
   - Create TypeScript component for ribbon
   - Match Polly's icon set (Lucide icons)

3. **Replace Activity Bar**
   - Modify workbench to use ribbon instead of activity bar
   - Maintain panel system (just change navigation)
   - Ensure all views still accessible

4. **Test Integration**
   - Verify all views work with ribbon
   - Test panel collapsing/expanding
   - Ensure keyboard shortcuts still work

**Files to Modify:**
- `src/vs/workbench/browser/parts/activitybar/` (activity bar code)
- `src/vs/workbench/browser/workbench.html` (workbench template)
- `src/vs/workbench/browser/workbench.ts` (workbench initialization)

**Deliverables:**
- Ribbon navigation working
- Activity bar replaced
- All views accessible via ribbon

---

### Day 5: Chat Panel Integration

**Goal:** Add basic Polly chat panel to right sidebar

**Tasks:**
1. **Study Panel System**
   - Understand VSCode's panel architecture
   - Locate right sidebar/panel code
   - Document how to add new panel types

2. **Create Chat Panel Extension**
   - Use extension API to add chat view
   - Port basic chat UI from Polly electron-app
   - Connect to Polly backend API

3. **Integrate with Ribbon**
   - Add chat icon to ribbon
   - Make chat panel toggleable
   - Ensure panel state persists

4. **Test Chat Functionality**
   - Send test message
   - Receive response
   - Verify UI updates correctly

**Files to Create/Modify:**
- `extensions/polly-chat/` (new extension)
- `src/vs/workbench/browser/parts/sidebar/` (panel system)

**Deliverables:**
- Chat panel working
- Integrated with ribbon
- Basic chat functionality

---

## Week 2: Merge Test & Evaluation

### Day 6-7: Theme Customization

**Goal:** Apply Polly design system to VSCode theme

**Tasks:**
1. **Study VSCode Theme System**
   - Locate theme files
   - Understand color token system
   - Document theme extension points

2. **Create Polly Theme**
   - Apply Polly color system (from DESIGN_SYSTEM.md)
   - Match typography (Inter for UI, JetBrains Mono for code)
   - Add glitch effects to key elements (if possible)

3. **Test Theme**
   - Verify all UI elements styled correctly
   - Test in light/dark mode (if applicable)
   - Ensure readability and contrast

**Files to Create:**
- `extensions/polly-theme/` (new theme extension)
- Theme JSON files with Polly colors

**Deliverables:**
- Polly theme applied
- Design system integrated
- Visual consistency with Polly

---

### Day 8-9: Merge Process Test

**Goal:** Test merging one VSCode update to validate maintenance complexity

**Tasks:**
1. **Identify Next VSCode Release**
   - Check VSCode release schedule
   - Pick next minor/patch release (not major)
   - Document what changed in release

2. **Perform Merge**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   # Resolve conflicts if any
   git checkout polly-integration
   git rebase main
   ```

3. **Resolve Conflicts**
   - Document any conflicts
   - Resolve conflicts carefully
   - Test after each conflict resolution

4. **Test After Merge**
   - Build and run
   - Test ribbon navigation
   - Test chat panel
   - Test basic editor functionality
   - Run automated tests (if available)

5. **Document Merge Experience**
   - Time taken
   - Number of conflicts
   - Complexity of conflicts
   - What broke (if anything)
   - What worked well

**Deliverables:**
- Successful merge
- Merge documentation
- Conflict resolution notes
- Time/complexity metrics

---

### Day 10: Evaluation & Documentation

**Goal:** Evaluate POC results and document findings

**Tasks:**
1. **Compile Metrics**
   - Time to fork and integrate: ___ hours
   - Time to merge: ___ hours
   - Number of conflicts: ___
   - Complexity rating: 1-10
   - Integration feasibility: ✅/❌

2. **Document Findings**
   - What worked well
   - What was challenging
   - Maintenance complexity assessment
   - Integration feasibility assessment
   - Recommendations

3. **Create Decision Document**
   - POC results summary
   - Go/No-Go recommendation
   - Risk assessment
   - Next steps if proceeding

4. **Present Results**
   - Create summary presentation
   - Highlight key findings
   - Make recommendation

**Deliverables:**
- POC evaluation document
- Decision recommendation
- Next steps plan

---

## Technical Details

### Fork Structure

```
polly-code/
├── .vscode/              # VSCode/VSCodium source
├── extensions/
│   ├── polly-chat/       # Chat panel extension
│   └── polly-theme/      # Theme extension
├── polly-integrations/   # Core modifications
│   ├── ribbon/          # Ribbon navigation
│   └── workbench/        # Workbench modifications
└── docs/
    ├── build.md         # Build instructions
    ├── merge-process.md # Merge documentation
    └── integration.md   # Integration notes
```

### Core Modifications (Minimal)

**Must Modify:**
1. **Activity Bar → Ribbon**
   - File: `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
   - Change: Replace activity bar with ribbon component
   - Risk: Medium (core workbench change)

2. **Workbench Template**
   - File: `src/vs/workbench/browser/workbench.html`
   - Change: Update HTML to include ribbon
   - Risk: Low (template change)

**Should Use Extension API:**
1. **Chat Panel**
   - Extension: `extensions/polly-chat/`
   - Use: `vscode.window.createTreeView()` or webview
   - Risk: Low (extension API)

2. **Theme**
   - Extension: `extensions/polly-theme/`
   - Use: Theme extension API
   - Risk: Low (standard extension)

### Integration Points

**Backend Integration:**
- Chat panel connects to Polly server API
- Use existing Polly backend (no changes needed)
- API endpoint: `http://localhost:8000/api/chat`

**Frontend Integration:**
- Ribbon uses Lucide icons (same as Polly)
- Chat UI matches Polly's chat component
- Theme matches Polly design system

---

## Risk Mitigation

### Risk 1: Merge Conflicts

**Mitigation:**
- Start with minimal changes
- Use extension API where possible
- Document all core modifications
- Test merge early (Day 8-9)

### Risk 2: Integration Complexity

**Mitigation:**
- Study VSCode architecture first
- Use extension API for most features
- Only modify core when necessary
- Document integration points

### Risk 3: Build Issues

**Mitigation:**
- Follow VSCodium build instructions exactly
- Test base build before modifications
- Document any build customizations
- Create reproducible build script

### Risk 4: Time Overrun

**Mitigation:**
- Focus on core features (ribbon, chat)
- Skip nice-to-haves if needed
- Prioritize merge test (critical for decision)
- Document what's incomplete

---

## Success Metrics

### Technical Metrics

- **Fork Setup:** < 4 hours
- **Ribbon Integration:** < 8 hours
- **Chat Panel:** < 8 hours
- **Theme:** < 4 hours
- **Merge Test:** < 8 hours
- **Total:** < 32 hours (1 week developer time)

### Quality Metrics

- **Build Success:** ✅ Builds without errors
- **Functionality:** ✅ All core features work
- **Merge Success:** ✅ Merge completes without major issues
- **Conflict Count:** < 5 conflicts (acceptable)
- **Integration Feasibility:** ✅/❌ Clear assessment

### Decision Metrics

- **Maintenance Complexity:** 1-10 rating
- **Integration Feasibility:** ✅/❌
- **Time Estimate Accuracy:** Compare actual vs estimated
- **Go/No-Go Recommendation:** Clear decision

---

## Deliverables

### Code

- ✅ VSCodium fork with Polly integrations
- ✅ Ribbon navigation component
- ✅ Chat panel extension
- ✅ Polly theme extension
- ✅ Build scripts and documentation

### Documentation

- ✅ Build instructions
- ✅ Integration notes
- ✅ Merge process documentation
- ✅ POC evaluation report
- ✅ Decision recommendation

### Decision

- ✅ Go/No-Go recommendation
- ✅ Risk assessment
- ✅ Next steps plan

---

## Next Steps After POC

### If POC Succeeds (Go Decision)

1. **Proceed with Full Phase 17**
   - Use POC as foundation
   - Add remaining Polly features
   - Refine UI/UX
   - Production release

### If POC Fails (No-Go Decision)

1. **Re-evaluate Approach**
   - Consider Monaco + custom shell
   - Alternative integration strategies
   - Revised timeline and scope

### If POC Partially Succeeds

1. **Address Issues**
   - Fix identified problems
   - Re-test merge process
   - Make informed decision

---

## Timeline Summary

| Week | Days | Focus | Deliverable |
|------|------|-------|-------------|
| 1 | 1-2 | Fork Setup | Working fork |
| 1 | 3-4 | Ribbon | Ribbon navigation |
| 1 | 5 | Chat Panel | Chat integration |
| 2 | 6-7 | Theme | Polly theme |
| 2 | 8-9 | Merge Test | Merge validation |
| 2 | 10 | Evaluation | Decision document |

**Total: 2 weeks (10 working days)**

---

## Resources

- VSCodium GitHub: https://github.com/VSCodium/vscodium
- VSCode Extension API: https://code.visualstudio.com/api
- VSCode Source Code: https://github.com/microsoft/vscode
- Polly Design System: `/DESIGN_SYSTEM.md`
- Polly Ribbon Implementation: `/electron-app/src/renderer/styles/ribbon.css`

---

**Status:** Ready to begin POC
