# Phase 16e: TOC Sidebar & Template System

**Date:** February 1, 2026  
**Status:** 📋 Planning Complete → Ready to Build  
**Effort:** 3-4 days  
**Priority:** High (Core UX Enhancement)

---

## Executive Summary

Two complementary enhancements to the Notes system:

1. **Table of Contents (TOC) in Right Sidebar** - Add TOC view alongside Backlinks/Tags for easy navigation of long notes
2. **Template Gallery System** - Replace restrictive question flow with visual template selection and Obsidian-style markdown templates

**Why Now:**
- Notes system is stable and feature-complete (Phase 16 ✅, 16c ✅)
- Users need better navigation for long documents
- Current AI note creation flow is too restrictive
- Template system enables future extensibility

**Impact:**
- **TOC:** Significantly improves navigation UX for long notes
- **Templates:** Makes AI note creation faster, more flexible, and user-customizable

---

## Part 1: Table of Contents (TOC) in Notes Sidebar

### Problem Statement

**Current State:**
- Right sidebar has Backlinks and Tags panels
- No way to navigate within a long note
- Users must manually scroll to find sections

**User Pain Point:**
"I have notes with 10+ headings. I can't quickly jump to the section I need."

### Solution

**Add TOC View to Right Sidebar:**
- View toggle buttons at top: Backlinks | Tags | TOC
- TOC shows nested/indented heading list (H1-H6)
- Click heading → smooth scroll with highlight animation
- Updates automatically when note content changes

**UI Pattern:**
```
┌─────────────────────────┐
│ [🔗] [🏷️] [📋]        │ ← Toggle buttons
├─────────────────────────┤
│ Table of Contents       │
│                         │
│ Introduction            │ ← H1 (0px indent)
│   Background            │ ← H2 (16px indent)
│   Motivation            │ ← H2 (16px indent)
│ Implementation          │ ← H1 (0px indent)
│   Phase 1               │ ← H2 (16px indent)
│     Backend             │ ← H3 (32px indent)
│     Frontend            │ ← H3 (32px indent)
│   Phase 2               │ ← H2 (16px indent)
│ Conclusion              │ ← H1 (0px indent)
└─────────────────────────┘
```

**Icons (Lucide):**
- Backlinks: `link-2`
- Tags: `tag`
- TOC: `list`

### Implementation Details

**Existing Infrastructure (Leveraged):**
- ✅ All headings already get unique IDs during rendering (notes-manager.js:621-630)
- ✅ `scrollToHeading()` function exists with animation (notes-manager.js:960-987)
- ✅ Collapsible panel UI pattern established
- ✅ Sidebar toggle logic working

**New Components:**
1. View toggle button bar (3 buttons)
2. View container system (show/hide panels)
3. TOC panel with nested heading list
4. TOC generation logic (extract from rendered HTML)
5. Click handlers for heading navigation

**Files Modified:**
- `electron-app/src/renderer/index.html` (add TOC UI structure)
- `electron-app/src/renderer/styles/notes.css` (add TOC styles)
- `electron-app/src/renderer/notes-manager.js` (add TOC logic)

**Effort:** 4-6 hours

### Success Criteria

✅ Users can switch between Backlinks, Tags, and TOC views  
✅ TOC displays all headings with correct indentation  
✅ Clicking heading scrolls smoothly to section  
✅ TOC updates when note changes (edit mode)  
✅ Empty state shows when no headings exist  
✅ UI matches app aesthetic (Obsidian-inspired)

---

## Part 2: Template Gallery System

### Problem Statement

**Current State:**
- AI note creation uses 3-5 question flow (Capture → Organize → Enrich)
- Organize mode asks restrictive radio button questions
- Users can't easily customize note structure
- Templates are buried in questions, not visible upfront

**User Pain Point:**
"The questions feel stifling. I want to see template options first, then let AI fill them in."

### Solution

**Template-First Approach:**
1. User: "Save this as a note"
2. Scribe Capture mode (background analysis)
3. **Template Gallery shows visually** (AI suggests best match)
4. User selects template
5. Note Preview modal (edit before save)
6. Save to knowledge base

**Template Storage:**
- Templates are markdown files in `vault/.polly/templates/`
- Obsidian-style: Just regular markdown with YAML frontmatter
- Users can create/edit templates like regular notes
- Template folder configured in Settings

**Template Format:**
```markdown
---
template_name: "Meeting Notes"
template_icon: "calendar"
template_description: "For discussions, decisions, and action items"
template_category: "collaboration"

# AI generation hints
ai_tone: "professional, organized"
ai_focus: "decisions and action items"
ai_linking_priority: ["projects", "people", "tools"]

# Smart defaults
default_domain: "scrolls"
default_folder: "meetings/"
default_tags: [meetings]
---

# {{title}}

**Date:** {{date}}
**Attendees:** {{attendees}}

## Agenda
- {{agenda_items}}

## Discussion Points
{{discussion_notes}}

## Decisions Made
{{decisions}}

## Action Items
{{action_items}}

## Next Steps
{{next_steps}}
```

**Variables:**
- `{{variable}}` - AI extracts from conversation
- `{{date}}` - Auto-filled with current date
- `{{title}}` - Note title

**Template Gallery UI:**
```
┌──────────────────────────────────────────────┐
│  Select a Template                      [×]  │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 📅       │ │ 💡       │ │ 📚       │    │
│  │ Meeting  │ │ Concept  │ │ How-To   │    │
│  │ Notes    │ │ Note     │ │ Guide    │    │
│  │          │ │          │ │          │    │
│  │ (✓ AI)   │ │          │ │          │    │ ← AI suggested
│  └──────────┘ └──────────┘ └──────────┘    │
│                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 🔬       │ │ 📦       │ │ ✏️       │    │
│  │ Research │ │ Project  │ │ Quick    │    │
│  │ Summary  │ │ Note     │ │ Note     │    │
│  └──────────┘ └──────────┘ └──────────┘    │
│                                              │
│  [Template Preview]                         │
│  Selected: Meeting Notes                    │
│  Structure: Agenda, Discussion, Decisions,  │
│            Action Items, Next Steps         │
│                                              │
│           [Cancel]  [Use This Template]     │
└──────────────────────────────────────────────┘
```

### Default Templates (6)

**Shipped with Polly:**

1. **meeting-notes.md** - Icon: `calendar`
   - Sections: Agenda, Discussion, Decisions, Action Items, Next Steps
   - Best for: Team meetings, 1-on-1s, planning sessions

2. **concept-note.md** - Icon: `lightbulb`
   - Sections: Overview, Definition, Key Principles, Examples, Related Concepts
   - Best for: Technical concepts, theories, mental models

3. **howto-guide.md** - Icon: `book-open`
   - Sections: Purpose, Prerequisites, Steps, Verification, Troubleshooting
   - Best for: Tutorials, setup instructions, procedures

4. **research-summary.md** - Icon: `microscope`
   - Sections: Context, Key Findings, Analysis, Implications, Sources
   - Best for: Literature reviews, research notes, investigations

5. **project-note.md** - Icon: `package`
   - Sections: Overview, Goals, Status, Timeline, Phases, Resources
   - Best for: Software projects, personal initiatives, long-term goals

6. **quick-note.md** - Icon: `file-text`
   - Sections: Minimal structure, free-form content
   - Best for: Quick captures, fleeting thoughts, journal entries

### Architecture Changes

**New Backend Components:**

1. **Template Manager** (`core/templates/manager.py`)
   - Scans templates folder for `.md` files
   - Parses YAML frontmatter
   - Extracts template metadata for gallery
   - Validates template structure

2. **Template Model** (`core/templates/template.py`)
   - Represents a template with metadata
   - Extracts `{{variables}}` from markdown
   - Provides AI hints and smart defaults
   - Renders template with filled variables

**Updated Scribe Persona:**

**Capture Mode (MODIFY):**
- Add template suggestion to output
- Return suggested template slug + alternatives
- Include confidence score

**Organize Mode (REMOVE):**
- Delete entirely - no longer needed!
- QuestionForm UI no longer used

**Enrich Mode (REWRITE):**
- Input: template filename + conversation analysis
- Load template via TemplateManager
- Extract variables from template markdown
- Analyze conversation to fill variable values
- Use AI hints (tone, focus, linking priority)
- Replace `{{variables}}` with extracted content
- Generate prose for freeform sections
- Insert [[wiki-links]]
- Apply smart defaults (domain, folder, tags)
- Output: Complete markdown note

**New API Endpoints:**
- `GET /polly/templates` - List all templates (metadata for gallery)
- `GET /polly/templates/<filename>` - Get specific template

**Configuration:**
```yaml
# Add to config.yaml
templates:
  folder: ".polly/templates"  # Relative to vault root
  auto_reload: true           # Watch for template changes
```

### Files Summary

**NEW Files (11):**
- `vault/.polly/templates/meeting-notes.md`
- `vault/.polly/templates/concept-note.md`
- `vault/.polly/templates/howto-guide.md`
- `vault/.polly/templates/research-summary.md`
- `vault/.polly/templates/project-note.md`
- `vault/.polly/templates/quick-note.md`
- `core/templates/__init__.py`
- `core/templates/manager.py`
- `core/templates/template.py`
- `electron-app/src/renderer/components/template-gallery.js`
- `electron-app/src/renderer/styles/template-gallery.css`

**MODIFIED Files (5):**
- `core/personas/implementations/scribe.py` (update Capture, remove Organize, rewrite Enrich)
- `interfaces/server.py` (add template API endpoints)
- `electron-app/src/renderer/app.js` (replace QuestionForm with TemplateGallery)
- `config.yaml` (add templates section)
- `electron-app/src/renderer/index.html` (add TemplateGallery modal container)

**Effort:** 2-3 days

### Success Criteria

✅ Templates load from vault folder  
✅ Template gallery displays visually with Lucide icons  
✅ AI suggested template is highlighted  
✅ Selecting template triggers note generation  
✅ Variables extracted from conversation correctly  
✅ AI hints affect generation (tone, focus, linking)  
✅ Smart defaults applied (domain, folder, tags)  
✅ Generated note follows template structure  
✅ Wiki-links inserted automatically  
✅ Preview modal allows editing before save  
✅ Saved note appears in knowledge base  

---

## Implementation Schedule

### Day 1: TOC Sidebar (4-6 hours)

**Morning (3 hours):**
- [ ] Modify HTML structure (view toggle buttons + TOC panel)
- [ ] Add CSS styling for TOC UI
- [ ] Test static layout and styling

**Afternoon (3 hours):**
- [ ] Add JavaScript logic (view switching, TOC generation)
- [ ] Wire up integration points (init, loadNote, etc.)
- [ ] Test all TOC functionality
- [ ] Fix any bugs

**Deliverable:** Working TOC view in Notes sidebar

---

### Day 2: Template Backend (6-8 hours)

**Morning (4 hours):**
- [ ] Create 6 default template markdown files
- [ ] Implement TemplateManager class
- [ ] Implement Template model class
- [ ] Test template loading and parsing

**Afternoon (4 hours):**
- [ ] Add API endpoints for templates
- [ ] Add config section for templates
- [ ] Update Scribe Capture to suggest templates
- [ ] Test backend template system

**Deliverable:** Template system loads markdown files, API returns metadata

---

### Day 3: Template Frontend + Scribe (6-8 hours)

**Morning (4 hours):**
- [ ] Create TemplateGallery component
- [ ] Add template gallery CSS
- [ ] Test gallery UI standalone

**Afternoon (4 hours):**
- [ ] Rewrite Scribe Enrich mode for templates
- [ ] Remove Scribe Organize mode
- [ ] Test Enrich mode with templates
- [ ] Test variable extraction and replacement

**Deliverable:** Template gallery shows, Enrich mode generates notes from templates

---

### Day 4: Integration & Testing (4-6 hours)

**Morning (3 hours):**
- [ ] Update app.js Scribe flow
- [ ] Remove QuestionForm usage
- [ ] Wire up complete flow (Capture → Gallery → Enrich → Preview)

**Afternoon (3 hours):**
- [ ] End-to-end testing
- [ ] Edge case testing
- [ ] Bug fixes
- [ ] Final polish

**Deliverable:** Complete working system, ready for production

---

## Testing Checklist

### TOC Feature
- [ ] View toggle buttons render correctly
- [ ] Clicking Backlinks/Tags/TOC switches views
- [ ] Active button highlighted with accent color
- [ ] TOC extracts all heading levels (H1-H6)
- [ ] Headings indented correctly by level
- [ ] Clicking heading scrolls smoothly to section
- [ ] Heading highlight animation plays
- [ ] Empty state shows when no headings
- [ ] TOC updates when switching notes
- [ ] TOC updates in live preview mode
- [ ] Sidebar collapse/expand still works
- [ ] Lucide icons render after view switches

### Template Feature
- [ ] TemplateManager loads 6 default templates
- [ ] Template YAML frontmatter parses correctly
- [ ] Variables extracted from template markdown
- [ ] `/polly/templates` endpoint returns metadata
- [ ] `/polly/templates/<filename>` endpoint works
- [ ] Config templates.folder setting works
- [ ] Template gallery modal displays
- [ ] All 6 cards render with Lucide icons
- [ ] AI suggested template has "(✓ AI)" badge
- [ ] Clicking card shows preview panel
- [ ] Selected card has accent border + checkmark
- [ ] "Use Template" triggers note generation
- [ ] Variables replaced with conversation content
- [ ] AI hints affect generation (tone, focus)
- [ ] Smart defaults applied (domain, folder, tags)
- [ ] Wiki-links inserted correctly
- [ ] Preview modal shows generated note
- [ ] Editing in preview works
- [ ] Saving creates file in correct location

### Edge Cases
- [ ] No templates found (show error)
- [ ] Template has invalid YAML (validation error)
- [ ] Template missing required fields (validation)
- [ ] Variable not extracted from conversation (placeholder or skip)
- [ ] User cancels template selection (return to chat)
- [ ] Templates folder doesn't exist (create it)
- [ ] Note with no headings (show empty state)

---

## Risk Assessment

### Low Risk
- **TOC sidebar:** Leverages existing infrastructure
- **Template markdown format:** Simple, debuggable
- **Template gallery UI:** Standard modal pattern

### Medium Risk
- **Scribe Enrich rewrite:** Core logic change
- **Variable extraction:** Depends on AI accuracy
- **Template validation:** Need robust error handling

### Mitigation
- **Incremental testing:** Test components independently
- **Fallback handling:** Sensible defaults if extraction fails
- **User control:** Preview modal lets user edit
- **Validation:** Template manager validates before loading

---

## Future Enhancements (Phase 2)

**Not in Initial Scope:**

### Custom Template Creation
- Fix titlebar button blocking in main right sidebar
- Add "Create Template" button in Settings
- Template editor (or just use Notes editor)
- Template validation and preview
- Template rename/delete/duplicate

### Advanced Template Features
- Template inheritance (base templates)
- Conditional sections based on content
- Template variables with types/validation
- Template sharing/marketplace
- Template versioning
- Template analytics (usage tracking)

---

## Dependencies

**None!** This work can start immediately.

**Prerequisites (All Met):**
- ✅ Phase 16: Notes Frontend complete
- ✅ Phase 16c: Scribe persona complete
- ✅ Vault system operational
- ✅ Lucide icons integrated

---

## Success Metrics

**TOC Feature:**
- Users can navigate long notes 10x faster
- Reduced scrolling time by 80%
- UI feels native to Obsidian aesthetic

**Template Feature:**
- Note creation time reduced by 50%
- Users create custom templates within first week
- Template system enables future extensibility
- AI-generated notes more consistent and structured

---

## Documentation Updates Needed

After implementation:
- [ ] Update PHASE16_COMPLETE.md with new features
- [ ] Update MASTER_ROADMAP.md (mark Phase 16e complete)
- [ ] Create user guide for templates (in .polly/help/)
- [ ] Document template variable syntax
- [ ] Add template creation tutorial

---

## Relationship to Roadmap

**This is Phase 16e** - Natural extension of Phase 16 (Notes Frontend) and Phase 16c (Scribe Persona).

**Unlocks:**
- Better user experience for existing features
- Template system foundation for future personas
- User extensibility path (custom templates)

**Blocks Nothing:** Other phases can proceed in parallel.

---

## Review & Approval

**Planning Complete:** February 1, 2026  
**Reviewed By:** Brett  
**Approved To Proceed:** ✅ Yes

**Next Action:** Begin Day 1 implementation (TOC Sidebar)

---

## Notes

- **Icons:** Always use Lucide icons (not emoji)
- **Templates:** Obsidian-style markdown keeps it simple
- **User Control:** Preview before save is critical
- **Extensibility:** Template system designed for future expansion
- **Migration:** None needed - just ship new flow

**Philosophy:** 
- Start with good defaults (6 templates)
- Make it easy to customize (markdown templates)
- Let AI do the heavy lifting (variable extraction)
- Give users final control (preview modal)
