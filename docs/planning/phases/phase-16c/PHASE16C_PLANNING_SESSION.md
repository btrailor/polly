# Phase 16c: AI Note Creation - Planning Session

**Date:** January 29, 2026  
**Purpose:** Detailed planning and design review before implementation  
**Duration:** 4 weeks implementation

---

## Quick Reference: What You're Recalling

**You mentioned:** In-window dialogues for AI note generation in the chat window

**From the spec:** Yes! The spec includes **dynamic inline UI components** embedded directly in chat messages:

1. **Inline Q&A Interface** - Questions appear as interactive forms in the chat
2. **Note Preview Modal** - Full-screen preview with tabs (Preview/Edit/Raw)
3. **Mode Switcher UI** - Toggle between Plan and Build modes
4. **Progress Indicators** - Show generation status

**Significance:** This requires substantial chat UI updates to support **rich interactive components** beyond simple text messages.

---

## Architecture Overview

### High-Level Flow

```
User: "Create a note about the Phase 11 meeting"
    ↓
[Intent Detection] Detects note creation request
    ↓
[Architect Persona Activated] Default mode: Plan
    ↓
[Plan Mode] 
    → Analyzes request
    → Identifies template (meeting-note.md)
    → Asks clarifying questions **[INLINE UI]**
    ↓
User answers questions in chat interface
    ↓
[User switches to Build Mode] **[MODE SWITCHER UI]**
    ↓
[Build Mode]
    → Generates note using template
    → Adds wiki-links to related notes
    → Shows preview **[PREVIEW MODAL]**
    ↓
User reviews → edits if needed → saves
    ↓
[Learning Loop] Tracks edits (opt-in)
```

---

## Key Questions & Design Decisions

### 1. Chat UI Architecture

**Current State:**
- Chat displays text messages only
- Messages are strings rendered as markdown
- No support for interactive components

**Required Changes:**
- Messages need to support `ui_component` type field
- Renderer needs to handle different component types
- Components must be reactive (answer submitted → UI updates)

**Question for you:**

**Q1.1:** Do you want inline components (questions appear as cards in the message stream) or should they be in a dedicated panel/sidebar?

**Options:**
- **A. Inline in message stream** (spec's approach)
  - Pros: Conversational flow, everything in one place
  - Cons: Can get cluttered with long conversations
  - Example: Questions appear as expandable cards in the chat

- **B. Dedicated right panel** 
  - Pros: Clean separation, doesn't clutter chat
  - Cons: Context switching between chat and panel
  - Example: Right sidebar shows "Note Planning" panel when active

- **C. Hybrid**
  - Pros: Best of both worlds
  - Cons: More complex
  - Example: Summary card in chat, click to open detailed panel

**My recommendation:** Start with **Option A (inline)** as spec describes, but design components to be portable to panel later.

---

### 2. Mode Switching UI

**The Architect persona has two modes:**
- **Plan Mode:** Ask questions, analyze, outline
- **Build Mode:** Generate content, apply template

**Question for you:**

**Q2.1:** How should users switch between modes?

**Options:**
- **A. Explicit mode switch button** (spec's approach)
  - Button in chat input area: `[Plan Mode ▼] [Switch to Build]`
  - Pros: Clear, intentional
  - Cons: Extra click

- **B. Automatic progression**
  - After all questions answered, auto-switch to Build
  - Pros: Seamless
  - Cons: Less user control

- **C. Manual trigger phrase**
  - User types "build it" or "generate" to switch
  - Pros: Natural language
  - Cons: May be ambiguous

**My recommendation:** **Option A** for clarity, with **Option B** as optional auto-progression setting.

**Q2.2:** Should the mode be visible in the UI?

**Options:**
- Badge in chat header: `🏗️ Architect | Plan Mode`
- Mode indicator in each message: `[Plan] Polly: I'll help create...`
- Both

**My recommendation:** Both - header badge + subtle message indicator.

---

### 3. Template System

**Spec proposes:** User-configured template folder (e.g., `~/Dropbox/Polly/Templates/`)

**Question for you:**

**Q3.1:** Should we ship with default templates or require user to create them?

**Options:**
- **A. Ship with 5-10 default templates**
  - meeting-note.md, daily-note.md, concept-note.md, etc.
  - User can override or add more
  - Pros: Works immediately
  - Cons: May not match user's style

- **B. Start empty, user creates all templates**
  - Pros: Fully personalized
  - Cons: Friction to get started

- **C. Hybrid: Defaults + easy customization**
  - Ship with defaults
  - "Customize template" button in settings
  - Copy default to user folder for editing
  - Pros: Best of both

**My recommendation:** **Option C** - Ship with sensible defaults, make customization easy.

**Q3.2:** Where should templates be stored?

**Options:**
- **A. In notes vault** (e.g., `~/.polly/notes/_Templates/`)
  - Pros: Everything in one place
  - Cons: Mixes templates with notes

- **B. Separate location** (e.g., `~/.polly/templates/`)
  - Pros: Clear separation
  - Cons: User manages two folders

- **C. In config** (stored as JSON in `config.yaml`)
  - Pros: Portable, versionable
  - Cons: Less flexible for complex templates

**My recommendation:** **Option A** - Use `_Templates/` folder in vault (same pattern as `_Drafts/`).

---

### 4. Note Preview & Editing

**Spec includes:** Full-screen modal with three tabs (Preview, Edit, Raw Markdown)

**Question for you:**

**Q4.1:** Should the preview be modal (overlay) or inline (in chat)?

**Options:**
- **A. Full-screen modal** (spec's approach)
  - Pros: Space to edit, professional
  - Cons: Leaves chat context

- **B. Expandable card in chat**
  - Pros: Stays in context
  - Cons: Limited space

- **C. Opens in Notes page**
  - Pros: Full editor with all features
  - Cons: Context switch away from chat

**My recommendation:** **Option A (modal)** for serious editing, with quick "Open in Notes" button.

**Q4.2:** Should editing happen before or after saving?

**Options:**
- **A. Edit before save** (spec's approach)
  - Preview → Edit → Save to vault
  - Pros: Only final version saved
  - Cons: No undo if you close modal

- **B. Save as draft, then edit**
  - Generate → Save to `_Drafts/` → Edit in Notes page → Move to final folder
  - Pros: Never lose work, familiar workflow
  - Cons: Extra step

**My recommendation:** **Option B** - Always save to `_Drafts/` first, then user can edit and approve.

---

### 5. Intent Detection

**How should Polly know when to activate note creation?**

**Question for you:**

**Q5.1:** Explicit trigger or automatic detection?

**Options:**
- **A. Explicit triggers only**
  - User must say "create a note about X"
  - Pros: No false positives
  - Cons: User must remember syntax

- **B. Implicit detection** (spec's approach)
  - Analyze message for note-creation intent
  - "Can you document this for me?" triggers note creation
  - Pros: Natural language
  - Cons: May activate incorrectly

- **C. Hybrid with confirmation**
  - Detect intent, ask "Did you want to create a note about X?"
  - Pros: Flexible + safe
  - Cons: Extra confirmation step

**My recommendation:** **Option C** - Detect intent, show quick confirmation: "I can help create a note. [Yes, create] [No, just chat]"

---

### 6. Learning Loop (Privacy-Sensitive)

**Spec proposes:** Track how users edit AI-generated notes to improve future generation (opt-in)

**Question for you:**

**Q6.1:** Should we include learning loop in v1 or defer?

**Options:**
- **A. Include in Phase 16c (week 4)**
  - Full feature as spec describes
  - Pros: Complete system
  - Cons: More complexity, privacy concerns

- **B. Defer to Phase 16d**
  - Get basic note creation working first
  - Add learning later
  - Pros: Faster to v1
  - Cons: No improvement over time

**My recommendation:** **Option B** - Defer learning loop. Focus on core workflow first, add learning in Phase 16d if users request it.

---

### 7. Dependencies & Prerequisites

**Spec says:** Requires Phase 11 (Multi-Model Router v2) for Architect persona

**Current State:**
- Phase 11 is NOT complete yet
- Architect persona framework doesn't exist yet

**Question for you:**

**Q7.1:** Should we build Architect persona first, or create a simplified version for Phase 16c?

**Options:**
- **A. Wait for Phase 11, build full Architect persona**
  - Do Phase 11 first (10-14 days)
  - Then do Phase 16c with Architect (4 weeks)
  - Total: ~8-10 weeks
  - Pros: Proper architecture, reusable persona system
  - Cons: Long time to working feature

- **B. Build simplified note-creation system now**
  - No persona framework
  - Direct note creation without Plan/Build modes
  - Simpler workflow: Detect intent → Ask questions → Generate → Preview → Save
  - Pros: Faster to working feature (2-3 weeks)
  - Cons: Will need refactoring when Architect is built

- **C. Build minimal Architect persona just for note creation**
  - Create lightweight persona system
  - Only Architect persona, no framework for others
  - Pros: Gets Plan/Build workflow
  - Cons: May need refactoring for Phase 11

**My recommendation:** **Option B (simplified)** or **Option C (minimal Architect)** depending on how important Plan/Build workflow is to you.

**Follow-up:** How important is the Plan/Build two-stage workflow vs. getting note creation working quickly?

---

## Proposed Simplified Flow (Option B)

If we go with simplified approach, here's the workflow:

```
User: "Create a note about X"
    ↓
[Intent Detection] Confirmed with button: "Create note about X?"
    ↓
[Template Selection] Auto-match or user chooses from dropdown
    ↓
[Clarifying Questions] 3-5 questions appear inline in chat
    ↓
User answers questions (or skips)
    ↓
[Generation] Polly generates note using template + answers
    ↓
[Draft Saved] Note saved to _Drafts/ folder
    ↓
[Preview Shown] Inline card in chat: "Note created: [Open in Notes]"
    ↓
User opens in Notes page → edits → moves to final folder
```

**Advantages:**
- No persona framework needed
- No Plan/Build modes to manage
- Simpler UI (no mode switcher)
- Still gets core value: AI-generated notes from conversations
- 2-3 weeks vs 4+ weeks

**Disadvantages:**
- No Plan/Build workflow separation
- No reusable persona architecture
- May need refactoring for Phase 11

---

## Technical Questions

### T1. Message Format Changes

**Current:** Messages are simple objects: `{role: "user"|"assistant", content: string}`

**Required:** Messages with UI components: `{role, content, ui_component?: string, metadata?: object}`

**Question:** Should we update the message format now or create a separate "interactive message" type?

---

### T2. Real-Time Q&A

**How should questions/answers work?**

**Options:**
- **A. Each answer is a separate message**
  - Question appears in assistant message
  - User types answer as new user message
  - Pros: Simple, uses existing chat
  - Cons: Verbose, many messages

- **B. Inline form submission**
  - Questions rendered as form in assistant message
  - Answers submitted via API, don't appear as messages
  - Only final "All questions answered" appears as message
  - Pros: Clean, concise
  - Cons: More complex

**My recommendation:** **Option B** - Inline forms for cleaner UX.

---

### T3. Template Variables

**Spec uses:** `{{title}}`, `{{date}}`, `{{tags}}` placeholders

**Question:** Should we support advanced templating (loops, conditionals) or keep it simple?

**Options:**
- **A. Simple variable replacement only**
  - `{{var}}` → value
  - Pros: Easy to implement
  - Cons: Limited flexibility

- **B. Use templating engine (e.g., Handlebars, Nunjucks)**
  - `{{#if tags}}Tags: {{tags}}{{/if}}`
  - Pros: Powerful
  - Cons: Learning curve for users

**My recommendation:** **Option A** for v1, upgrade to Option B if users request it.

---

## Your Input Needed

**Please share your thoughts on:**

1. **Inline UI vs Sidebar** (Q1.1) - Where should planning interface appear?
2. **Mode Switching** (Q2.1, Q2.2) - How to handle Plan/Build modes?
3. **Templates** (Q3.1, Q3.2) - Defaults? Where to store?
4. **Preview & Editing** (Q4.1, Q4.2) - Modal vs inline? Edit before or after save?
5. **Intent Detection** (Q5.1) - Explicit, automatic, or hybrid?
6. **Learning Loop** (Q6.1) - Include now or defer?
7. **Architecture** (Q7.1) - Full Architect persona, simplified, or minimal?

**Most Important:**
- **Question 7 (Architecture):** This affects timeline the most
  - Full system with Architect: 8-10 weeks (Phase 11 + 16c)
  - Simplified system: 2-3 weeks (just 16c)
  - Minimal Architect: 3-4 weeks (lightweight persona + 16c)

**What do you think? Which approach aligns best with your vision?**

---

## Next Steps After Planning

Once we agree on architecture and design decisions:

1. Create detailed implementation plan
2. Break into smaller milestones
3. Start with backend (intent detection, template system)
4. Then frontend (UI components, chat integration)
5. Test and iterate

**Ready to discuss?**
