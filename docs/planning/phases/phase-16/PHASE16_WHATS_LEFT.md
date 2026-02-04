# Phase 16: What's Left to Do

**Date:** January 29, 2026  
**Current Status:** Phase 16 (Notes Frontend) ✅ Complete | Phase 16c (AI Enhancements) 📋 Not Started

---

## What Was Completed (Phase 16)

✅ **Notes Browser** - File tree, folder organization  
✅ **Markdown Editor** - View/edit modes  
✅ **Wiki-Links** - Click to navigate, create from broken links  
✅ **Auto-Save** - 2-second debounced save  
✅ **Quick Switcher** - Cmd+O fuzzy search  
✅ **Note Creation** - Modal with folder selection  
✅ **Folder Management** - Create folders  
✅ **Drag-and-Drop** - Move notes between folders  
✅ **Title Editing** - Click to edit in header and file tree  
✅ **Backlinks Panel** - Shows incoming wiki-link references  

**Result:** Beautiful, functional notes interface that works with Obsidian vaults

---

## What's Left to Build (Phase 16c)

### Phase 16c: AI Note Creation & Polly Enhancements
**Effort:** 4 weeks (original plan) or 3-5 days (simplified)  
**Status:** 📋 Not Started  
**Spec:** `PHASE16C_AI_NOTE_CREATION.md`

### Two Options for Phase 16c

#### Option A: Full AI Note Creation (4 weeks)
**Complex, feature-rich implementation from the spec:**

**Week 1:** Intent Detection + Template System
- Note creation intent classifier
- Template folder scanning and pattern extraction
- Template matching algorithm

**Week 2:** Architect Persona Integration
- Plan mode: Ask clarifying questions
- Build mode: Generate structured content
- Mode switching UI in chat

**Week 3:** Note Preview & Learning
- Inline note preview in chat
- Edit before saving
- Learning loop from user edits (opt-in)

**Week 4:** UI Polish & Advanced Features
- Dynamic inline UI components
- Template variables ({{title}}, {{date}}, {{tags}})
- Auto-wikilink related notes

**Features:**
- Natural language: "Create a note about the Phase 11 meeting"
- Polly asks clarifying questions in Plan mode
- Generates structured content in Build mode
- Template extraction from user folder
- Learning from edits over time

---

#### Option B: Simplified AI Note Creation (3-5 days)
**Pragmatic implementation, skip the complex parts:**

**Day 1:** Domain Auto-Tagging
- Analyze note content on save
- Match against Phase 1.5 domain auto-tag rules
- Suggest domain if not set (30% threshold)
- Add to frontmatter

**Day 2:** Save Conversation as Note
- "Save as Note" button on Polly responses
- Modal with title, domain, tags fields
- Pre-populate content from conversation
- Add source attribution: "Source: Conversation on [date]"

**Day 3:** Quick Note Templates
- Basic template support (no folder scanning)
- 3-5 hardcoded templates: Meeting, Daily, Concept, Task, Person
- Simple variable replacement: {{title}}, {{date}}, {{time}}
- Template selector in Create Note modal

**Days 4-5:** Polish & Testing
- Error handling
- Visual feedback
- Testing with real notes

**Features:**
- Save any Polly response as a note (one click)
- Auto-suggest domain based on content
- Basic templates for common note types
- No complex AI planning/building workflow

---

## Recommendation

**Start with Option B (3-5 days)** for these reasons:

1. **High value, lower complexity** - Most users just want to save Polly responses
2. **Faster time to value** - Get working feature in days, not weeks
3. **Foundation for Option A** - Can build on this later if needed
4. **Dependencies met** - Doesn't require Phase 11 (Architect persona)

**Option A can wait** until:
- Phase 11 is complete (Architect persona framework)
- User feedback shows demand for complex template system
- Phase 16c simplified is proven valuable

---

## What's Actually Blocking

**Nothing is blocking!** Phase 16c can start immediately with Option B.

**If choosing Option A:**
- Phase 11 (Multi-Model Router v2) should be done first for Architect persona
- Read `PHASE11_AGENT_PERSONAS.md` for Architect framework

---

## Files That Need Work (Option B)

### Backend
1. **`interfaces/server.py`** - Add `/polly/notes/create-from-conversation` endpoint
2. **`core/domain_config.py`** - Add `suggest_domain(content)` method

### Frontend
3. **`electron-app/src/renderer/app.js`** - Add "Save as Note" button to chat messages
4. **`electron-app/src/renderer/notes-manager.js`** - Add domain auto-tagging function
5. **`electron-app/src/renderer/index.html`** - Add "Save as Note" modal
6. **`electron-app/src/renderer/styles/main.css`** - Style the new button/modal

**Total:** ~6 files, ~500-800 lines of code

---

## Next Steps

**Choose your path:**

1. **Option B (Recommended):** "Let's build simplified Phase 16c - save conversations as notes"
2. **Option A:** "Let's build the full AI note creation system with Architect persona"
3. **Skip for now:** "Let's work on Phase 22 (Teaching Mode) or Phase 12a (Knowledge Graph)"

**What would you like to do?**
