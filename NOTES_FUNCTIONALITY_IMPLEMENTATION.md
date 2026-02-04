# Notes Functionality Implementation Plan

**Date:** February 1, 2026  
**Goal:** Make notes mode fully functional with TOC sidebar + streamlined AI note creation

---

## Overview

Two major improvements needed for notes to be truly functional:

1. **TOC Sidebar View** - Alternative view showing document outline
2. **Streamlined AI Note Creation** - Less friction, more templates, better flow

---

## Phase 1: Finish Current Stage (2-4 hours)

### ✅ Already Completed
- Server starts instantly
- Polly initializes in background
- Notes auto-rebuild on startup (108 notes)
- File watcher works
- Sync endpoints fixed

### 🔴 Task 1.1: Test Queries with LLM (30 mins)

**Status**: Server doesn't block, but need to verify queries actually complete

**Steps**:
```bash
# Option A: Start Ollama locally
ollama serve
ollama pull llama3.2:3b

# Option B: Set cloud API key
export ANTHROPIC_API_KEY="..."

# Test query
curl -X POST http://127.0.0.1:11436/polly/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are my notes about?", "stream": false}'
```

**Success Criteria**: Query completes and returns response (not timeout)

---

### 🟢 Task 1.2: Add UI Loading Indicator (1 hour)

**File**: `electron-app/src/renderer/app.js`

**Implementation**:
```javascript
// Add loading overlay to index.html
<div id="polly-init-overlay" class="hidden">
  <div class="init-spinner"></div>
  <p>Initializing Polly...</p>
  <p class="init-status"></p>
</div>

// In app.js - poll Polly status during startup
async function checkPollyInitStatus() {
  try {
    const response = await fetch('http://127.0.0.1:11436/polly/status');
    const data = await response.json();
    
    const overlay = document.getElementById('polly-init-overlay');
    const statusText = overlay.querySelector('.init-status');
    
    if (data.initializing) {
      overlay.classList.remove('hidden');
      statusText.textContent = 'Loading AI models...';
    } else if (data.status === 'ready') {
      overlay.classList.add('hidden');
      clearInterval(window.pollyStatusInterval);
    } else if (data.status === 'error') {
      overlay.classList.add('hidden');
      showError('Polly initialization failed');
      clearInterval(window.pollyStatusInterval);
    }
  } catch (error) {
    console.warn('[Init] Failed to check Polly status:', error);
  }
}

// Poll every 500ms during first 10 seconds
window.pollyStatusInterval = setInterval(checkPollyInitStatus, 500);
setTimeout(() => clearInterval(window.pollyStatusInterval), 10000);
```

**Success Criteria**: User sees loading overlay during first few seconds, then it disappears

---

### 🟡 Task 1.3: Test GitHub Integrations (1 hour - OPTIONAL)

**What to Test**:
- GitHub repository sync
- Context7 integration
- Any other external data sources

**Success Criteria**: No blocking operations, integrations still functional

---

## Phase 2: TOC Sidebar View (4-6 hours)

### Current State

Right sidebar shows:
- **Stats card** (top)
- **Backlinks section** (middle)
- **Tags section** (bottom)

### Target State

Right sidebar has **3 views** (toggle buttons at top):
1. **Overview** (current view) - Stats + Backlinks + Tags
2. **TOC** - Document outline with clickable headings
3. **Graph** (future) - Mini knowledge graph

---

### 🟢 Task 2.1: Add View Toggle Buttons (1 hour)

**File**: `electron-app/src/renderer/index.html`

**Location**: Inside `<div class="right-sidebar-header">` (create if doesn't exist)

**HTML**:
```html
<div class="right-sidebar-header">
  <div class="sidebar-view-toggle">
    <button class="sidebar-view-btn active" data-view="overview" title="Overview">
      <i class="lucide-layout-dashboard"></i>
    </button>
    <button class="sidebar-view-btn" data-view="toc" title="Table of Contents">
      <i class="lucide-list"></i>
    </button>
    <button class="sidebar-view-btn" data-view="graph" title="Graph (Coming Soon)" disabled>
      <i class="lucide-network"></i>
    </button>
  </div>
</div>

<!-- Overview view (existing content) -->
<div class="sidebar-view" data-view="overview">
  <!-- Stats card, backlinks, tags (existing) -->
</div>

<!-- TOC view (new) -->
<div class="sidebar-view hidden" data-view="toc">
  <div class="toc-container">
    <h3>Table of Contents</h3>
    <div id="toc-list" class="toc-list">
      <!-- Generated dynamically -->
    </div>
  </div>
</div>
```

**CSS**:
```css
.sidebar-view-toggle {
  display: flex;
  gap: 4px;
  padding: 8px;
  background: var(--background-secondary);
  border-radius: 6px;
}

.sidebar-view-btn {
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.2s;
}

.sidebar-view-btn:hover:not(:disabled) {
  opacity: 1;
  background: var(--background-modifier-hover);
}

.sidebar-view-btn.active {
  opacity: 1;
  background: var(--interactive-accent);
  color: white;
}

.sidebar-view-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.sidebar-view.hidden {
  display: none;
}
```

**JavaScript** (in `notes-manager.js`):
```javascript
initSidebarViewToggle() {
  const buttons = document.querySelectorAll('.sidebar-view-btn');
  const views = document.querySelectorAll('.sidebar-view');
  
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetView = btn.dataset.view;
      
      // Update button states
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Update view visibility
      views.forEach(view => {
        if (view.dataset.view === targetView) {
          view.classList.remove('hidden');
        } else {
          view.classList.add('hidden');
        }
      });
      
      // Generate TOC if switching to TOC view
      if (targetView === 'toc') {
        this.generateTOC();
      }
    });
  });
}
```

---

### 🟢 Task 2.2: Generate TOC from Markdown (2 hours)

**File**: `electron-app/src/renderer/notes-manager.js`

**Implementation**:
```javascript
/**
 * Generate Table of Contents from current note's markdown
 */
generateTOC() {
  const tocList = document.getElementById('toc-list');
  if (!tocList) return;
  
  // Get current note content
  const noteContent = this.currentNoteContent || '';
  
  // Extract headings (support # through ###### )
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;
  const headings = [];
  let match;
  
  while ((match = headingRegex.exec(noteContent)) !== null) {
    const level = match[1].length; // Number of # symbols
    const text = match[2].trim();
    const id = this.slugify(text); // Convert to URL-safe slug
    
    headings.push({ level, text, id });
  }
  
  // Clear existing TOC
  tocList.innerHTML = '';
  
  if (headings.length === 0) {
    tocList.innerHTML = '<div class="toc-empty">No headings in this note</div>';
    return;
  }
  
  // Build hierarchical TOC HTML
  headings.forEach(heading => {
    const item = document.createElement('div');
    item.className = `toc-item toc-level-${heading.level}`;
    item.dataset.headingId = heading.id;
    
    const link = document.createElement('a');
    link.href = `#${heading.id}`;
    link.textContent = heading.text;
    link.addEventListener('click', (e) => {
      e.preventDefault();
      this.scrollToHeading(heading.id);
    });
    
    item.appendChild(link);
    tocList.appendChild(item);
  });
  
  console.log('[TOC] Generated TOC with', headings.length, 'headings');
}

/**
 * Convert heading text to URL-safe slug
 */
slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special chars
    .replace(/\s+/g, '-')      // Replace spaces with -
    .replace(/--+/g, '-')      // Replace multiple - with single -
    .trim();
}

/**
 * Scroll to heading in preview or edit mode
 */
scrollToHeading(headingId) {
  if (this.editMode) {
    // In edit mode: scroll CodeMirror editor
    const editor = this.editor;
    if (!editor) return;
    
    // Find line with heading
    const content = editor.state.doc.toString();
    const lines = content.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const match = line.match(/^#{1,6}\s+(.+)$/);
      if (match && this.slugify(match[1]) === headingId) {
        // Scroll to line
        const pos = editor.state.doc.line(i + 1).from;
        editor.dispatch({
          selection: { anchor: pos },
          scrollIntoView: true
        });
        break;
      }
    }
  } else {
    // In preview mode: scroll preview container
    const preview = document.getElementById('note-preview-content');
    if (!preview) return;
    
    // Find heading element
    const heading = preview.querySelector(`[id="${headingId}"]`);
    if (heading) {
      heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
      
      // Highlight briefly
      heading.classList.add('highlight-heading');
      setTimeout(() => heading.classList.remove('highlight-heading'), 2000);
    }
  }
}
```

**CSS**:
```css
.toc-container {
  padding: 16px;
}

.toc-list {
  margin-top: 12px;
}

.toc-item {
  margin: 4px 0;
  position: relative;
}

.toc-item a {
  display: block;
  padding: 4px 8px;
  color: var(--text-normal);
  text-decoration: none;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.4;
  transition: all 0.2s;
}

.toc-item a:hover {
  background: var(--background-modifier-hover);
  color: var(--text-accent);
}

/* Indentation for heading levels */
.toc-level-1 { padding-left: 0; font-weight: 600; }
.toc-level-2 { padding-left: 16px; }
.toc-level-3 { padding-left: 32px; font-size: 12px; }
.toc-level-4 { padding-left: 48px; font-size: 12px; opacity: 0.9; }
.toc-level-5 { padding-left: 64px; font-size: 11px; opacity: 0.8; }
.toc-level-6 { padding-left: 80px; font-size: 11px; opacity: 0.7; }

.toc-empty {
  padding: 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

/* Heading highlight animation */
.highlight-heading {
  background: var(--text-accent);
  color: white;
  padding: 4px 8px;
  margin: 0 -8px;
  border-radius: 4px;
  transition: all 0.3s ease-out;
}
```

---

### 🟢 Task 2.3: Auto-Update TOC on Content Change (1 hour)

**File**: `electron-app/src/renderer/notes-manager.js`

**Hook into existing content update functions**:
```javascript
// In renderNotePreview()
renderNotePreview(markdown) {
  // ... existing rendering code ...
  
  // Update TOC if TOC view is active
  const tocView = document.querySelector('[data-view="toc"]');
  if (tocView && !tocView.classList.contains('hidden')) {
    this.generateTOC();
  }
}

// In CodeMirror update handler
setupEditorUpdateListener() {
  if (!this.editor) return;
  
  // Debounce TOC updates (wait 500ms after typing stops)
  let tocUpdateTimeout;
  
  this.editor.on('change', () => {
    clearTimeout(tocUpdateTimeout);
    tocUpdateTimeout = setTimeout(() => {
      const tocView = document.querySelector('[data-view="toc"]');
      if (tocView && !tocView.classList.contains('hidden')) {
        this.currentNoteContent = this.editor.getValue();
        this.generateTOC();
      }
    }, 500);
  });
}
```

**Success Criteria**:
- TOC view appears when clicking TOC button
- Shows document headings in hierarchical list
- Clicking heading scrolls to that section
- TOC updates automatically when content changes

---

## Phase 3: AI Note Creation Refinement (1-2 days)

### Current Issues

**Problem**: Scribe's "Organize" mode asks too many questions upfront, creating friction:
- Domain selection
- Note type
- Key concepts
- Related notes
- Additional context

**User Pain**: "Just create the note!" - questions feel like homework

---

### Research: How Other Tools Handle This

Let me research how top AI tools handle note creation...

#### Notion AI
- **Pattern**: Inline generation, no upfront questions
- **Flow**: Type `/AI` → select template → AI generates → user edits
- **Templates**: Meeting notes, Blog post, To-do list, Pros & cons
- **Key Insight**: Templates replace questions

#### Reflect.app
- **Pattern**: "Daily note" is primary pattern
- **Flow**: AI suggestions appear contextually as you write
- **No questions**: AI adapts to your writing style over time
- **Key Insight**: Context comes from usage, not interrogation

#### Obsidian Canvas
- **Pattern**: Visual thinking, then capture
- **Flow**: Drag conversation → Canvas → Export to note
- **Minimal friction**: One click to capture
- **Key Insight**: Capture first, organize later

---

### Proposed Solution: Template-First Approach

**Core Principle**: **Templates replace questions**

Instead of asking questions, offer smart templates:
1. **Quick Capture** - No questions, just save conversation
2. **Meeting Notes** - Auto-extract attendees, topics, action items
3. **Research Note** - Extract key findings, sources, questions
4. **Project Plan** - Goals, tasks, timeline, resources
5. **Daily Log** - Date-based, bullet points
6. **Custom** - User answers questions (current flow)

---

### 🟢 Task 3.1: Design Template System (2 hours)

**File**: `core/personas/templates.py` (NEW)

**Architecture**:
```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum

class TemplateType(Enum):
    QUICK_CAPTURE = "quick_capture"
    MEETING = "meeting"
    RESEARCH = "research"
    PROJECT = "project"
    DAILY = "daily"
    CUSTOM = "custom"

@dataclass
class NoteTemplate:
    """Template for AI-generated notes"""
    id: str
    name: str
    description: str
    icon: str  # Lucide icon name
    type: TemplateType
    
    # Markdown template with placeholders
    markdown_template: str
    
    # Fields to extract (used by AI)
    extract_fields: List[str]
    
    # Prompt for AI extraction
    extraction_prompt: str
    
    # Skip organize mode (no questions)
    skip_questions: bool = True
    
    # Default domain (or None for user selection)
    default_domain: Optional[str] = None

# Built-in templates
TEMPLATES = {
    "quick_capture": NoteTemplate(
        id="quick_capture",
        name="Quick Capture",
        description="Save conversation without questions",
        icon="zap",
        type=TemplateType.QUICK_CAPTURE,
        markdown_template="""# {title}

**Created:** {date}
**Source:** Conversation

## Content

{content}

## Key Points

{key_points}
""",
        extract_fields=["title", "content", "key_points"],
        extraction_prompt="""Extract from this conversation:
- title: Short descriptive title
- content: Main conversation text (preserve structure)
- key_points: Bullet list of main takeaways""",
        skip_questions=True
    ),
    
    "meeting": NoteTemplate(
        id="meeting",
        name="Meeting Notes",
        description="Extract attendees, topics, and action items",
        icon="users",
        type=TemplateType.MEETING,
        markdown_template="""# {title}

**Date:** {date}
**Attendees:** {attendees}

## Topics Discussed

{topics}

## Key Decisions

{decisions}

## Action Items

{action_items}

## Next Steps

{next_steps}
""",
        extract_fields=["title", "attendees", "topics", "decisions", "action_items", "next_steps"],
        extraction_prompt="""Extract from this conversation:
- title: Meeting title
- attendees: List of people mentioned
- topics: Main discussion topics (bullet points)
- decisions: Key decisions made
- action_items: Tasks with owners (use [ ] for checkboxes)
- next_steps: What happens next""",
        skip_questions=True,
        default_domain="03-Meetings"
    ),
    
    "research": NoteTemplate(
        id="research",
        name="Research Note",
        description="Capture findings, sources, and questions",
        icon="book-open",
        type=TemplateType.RESEARCH,
        markdown_template="""# {title}

**Topic:** {topic}
**Date:** {date}

## Overview

{overview}

## Key Findings

{findings}

## Sources

{sources}

## Open Questions

{questions}

## Related Topics

{related}
""",
        extract_fields=["title", "topic", "overview", "findings", "sources", "questions", "related"],
        extraction_prompt="""Extract from this conversation:
- title: Research topic
- topic: Main area of study
- overview: Summary paragraph
- findings: Key discoveries (bullet points)
- sources: Mentioned references/links
- questions: Unanswered questions
- related: Related topics to explore""",
        skip_questions=True,
        default_domain="02-Research"
    ),
    
    "project": NoteTemplate(
        id="project",
        name="Project Plan",
        description="Goals, tasks, timeline, resources",
        icon="target",
        type=TemplateType.PROJECT,
        markdown_template="""# {title}

**Status:** Planning
**Start Date:** {date}

## Goal

{goal}

## Tasks

{tasks}

## Timeline

{timeline}

## Resources

{resources}

## Risks

{risks}
""",
        extract_fields=["title", "goal", "tasks", "timeline", "resources", "risks"],
        extraction_prompt="""Extract from this conversation:
- title: Project name
- goal: Main objective
- tasks: List of tasks (use [ ] for checkboxes)
- timeline: Key milestones and dates
- resources: People, tools, or materials needed
- risks: Potential challenges""",
        skip_questions=True,
        default_domain="01-Projects"
    ),
    
    "daily": NoteTemplate(
        id="daily",
        name="Daily Log",
        description="Date-based journal entry",
        icon="calendar",
        type=TemplateType.DAILY,
        markdown_template="""# Daily Log - {date}

## Today's Focus

{focus}

## Accomplishments

{accomplishments}

## Challenges

{challenges}

## Notes

{notes}

## Tomorrow

{tomorrow}
""",
        extract_fields=["focus", "accomplishments", "challenges", "notes", "tomorrow"],
        extraction_prompt="""Extract from this conversation:
- focus: Main goal for today
- accomplishments: What was completed
- challenges: Problems encountered
- notes: Miscellaneous observations
- tomorrow: Plans for next day""",
        skip_questions=True,
        default_domain="04-Journal"
    ),
    
    "custom": NoteTemplate(
        id="custom",
        name="Custom Note",
        description="Answer questions for structured note",
        icon="edit",
        type=TemplateType.CUSTOM,
        markdown_template="",  # Generated from questions
        extract_fields=[],
        extraction_prompt="",
        skip_questions=False  # Use existing Organize mode
    )
}
```

---

### 🟢 Task 3.2: Update Scribe to Use Templates (3 hours)

**File**: `core/personas/implementations/scribe.py`

**Changes**:

1. **Add template selection step** (before Organize mode):
```python
async def handle_capture_to_template_selection(
    self, 
    analysis: Dict, 
    conversation_history: List[Dict]
) -> AsyncIterator[str]:
    """
    After Capture mode, show template selection instead of questions.
    """
    from core.personas.templates import TEMPLATES
    
    # Generate template selection message
    templates_list = "\n".join([
        f"{i+1}. **{t.name}** - {t.description}"
        for i, t in enumerate(TEMPLATES.values())
    ])
    
    yield f"""I've analyzed the conversation. Which template would you like to use?

{templates_list}

Reply with the template number, or describe what kind of note you want."""
    
    # Store analysis for next step
    self._pending_analysis = analysis
    self._pending_conversation = conversation_history
```

2. **Skip Organize mode for template-based notes**:
```python
async def handle_template_selection(
    self,
    template_choice: str,
    conversation_history: List[Dict]
) -> AsyncIterator[str]:
    """
    User selected template - extract fields and generate note.
    """
    from core.personas.templates import TEMPLATES
    
    # Parse template choice
    template_id = self._parse_template_choice(template_choice)
    template = TEMPLATES.get(template_id)
    
    if not template:
        yield "I don't recognize that template. Please choose 1-6."
        return
    
    if template.skip_questions:
        # Skip Organize mode - go straight to Enrich
        yield f"Creating {template.name}..."
        
        # Extract fields using AI
        extracted_data = await self._extract_template_fields(
            template,
            conversation_history
        )
        
        # Generate markdown
        markdown = template.markdown_template.format(**extracted_data)
        
        # Show preview
        yield f"\n\n## Preview\n\n{markdown}\n\n"
        yield "Would you like to save this note? (yes/no)"
        
    else:
        # Custom template - use existing Organize mode
        yield "Let me ask you a few questions to structure the note..."
        # ... existing Organize mode code ...
```

3. **Template field extraction**:
```python
async def _extract_template_fields(
    self,
    template: NoteTemplate,
    conversation_history: List[Dict]
) -> Dict[str, str]:
    """
    Use AI to extract template fields from conversation.
    """
    # Build extraction prompt
    conversation_text = "\n\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in conversation_history
    ])
    
    prompt = f"""{template.extraction_prompt}

Conversation:
{conversation_text}

Return fields as JSON."""
    
    # Call AI to extract
    response = await self._call_llm(prompt, tier="fast")
    
    # Parse JSON response
    import json
    extracted = json.loads(response)
    
    # Add auto-generated fields
    from datetime import datetime
    extracted['date'] = datetime.now().strftime('%Y-%m-%d')
    
    return extracted
```

---

### 🟢 Task 3.3: Update Frontend Template Selection UI (2 hours)

**File**: `electron-app/src/renderer/app.js`

**Add template selection dialog** (appears after "Save as note" clicked):
```html
<!-- Template Selection Modal -->
<div id="template-selection-modal" class="modal hidden">
  <div class="modal-content">
    <div class="modal-header">
      <h2>Choose Note Template</h2>
      <button class="modal-close">&times;</button>
    </div>
    
    <div class="modal-body">
      <div class="template-grid">
        <!-- Quick Capture -->
        <div class="template-card" data-template="quick_capture">
          <div class="template-icon">⚡</div>
          <h3>Quick Capture</h3>
          <p>Save without questions</p>
          <span class="template-badge">Instant</span>
        </div>
        
        <!-- Meeting Notes -->
        <div class="template-card" data-template="meeting">
          <div class="template-icon">👥</div>
          <h3>Meeting Notes</h3>
          <p>Attendees, topics, action items</p>
        </div>
        
        <!-- Research Note -->
        <div class="template-card" data-template="research">
          <div class="template-icon">📚</div>
          <h3>Research Note</h3>
          <p>Findings, sources, questions</p>
        </div>
        
        <!-- Project Plan -->
        <div class="template-card" data-template="project">
          <div class="template-icon">🎯</div>
          <h3>Project Plan</h3>
          <p>Goals, tasks, timeline</p>
        </div>
        
        <!-- Daily Log -->
        <div class="template-card" data-template="daily">
          <div class="template-icon">📅</div>
          <h3>Daily Log</h3>
          <p>Date-based journal entry</p>
        </div>
        
        <!-- Custom -->
        <div class="template-card" data-template="custom">
          <div class="template-icon">✏️</div>
          <h3>Custom</h3>
          <p>Answer questions</p>
          <span class="template-badge">Guided</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

**CSS**:
```css
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.template-card {
  padding: 20px;
  border: 2px solid var(--background-modifier-border);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.template-card:hover {
  border-color: var(--interactive-accent);
  background: var(--background-modifier-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.template-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.template-card h3 {
  font-size: 16px;
  margin: 8px 0 4px;
  color: var(--text-normal);
}

.template-card p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.template-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  background: var(--interactive-accent);
  color: white;
  font-size: 11px;
  border-radius: 12px;
  font-weight: 600;
}
```

**JavaScript**:
```javascript
// Show template selection when user clicks "Save as note"
function showTemplateSelection() {
  const modal = document.getElementById('template-selection-modal');
  modal.classList.remove('hidden');
  
  // Handle template selection
  document.querySelectorAll('.template-card').forEach(card => {
    card.addEventListener('click', () => {
      const templateId = card.dataset.template;
      selectTemplate(templateId);
    });
  });
}

async function selectTemplate(templateId) {
  // Hide template modal
  document.getElementById('template-selection-modal').classList.add('hidden');
  
  // Send to Scribe with template choice
  await sendMessage(`Use template: ${templateId}`, {
    persona: 'scribe',
    template: templateId
  });
}
```

---

### 🟢 Task 3.4: Create Default Template Files (1 hour)

**Files**: `core/personas/templates/*.md`

Create markdown files for each template that users can customize:

```
core/personas/templates/
├── quick_capture.md
├── meeting.md
├── research.md
├── project.md
├── daily.md
└── custom.md
```

Users can edit these files to customize their templates!

---

## Success Criteria

### Phase 1: Current Stage Complete
- [x] Server starts instantly
- [x] Polly initializes in background
- [x] Notes auto-rebuild
- [x] File watcher works
- [x] Sync endpoints work
- [ ] Queries complete successfully with LLM
- [ ] UI shows initialization status

### Phase 2: TOC Sidebar Working
- [ ] Right sidebar has 3 view buttons (Overview, TOC, Graph)
- [ ] TOC view shows document headings
- [ ] Clicking heading scrolls to that section
- [ ] TOC updates automatically on content change
- [ ] Works in both edit and preview mode

### Phase 3: AI Note Creation Streamlined
- [ ] Template selection modal appears first
- [ ] 6 templates available (Quick, Meeting, Research, Project, Daily, Custom)
- [ ] Quick Capture creates note in <5 seconds (no questions)
- [ ] Template-based notes skip Organize mode
- [ ] Only Custom template uses existing question flow
- [ ] Users can edit template files

---

## Timeline Estimate

**Phase 1**: 2-4 hours
**Phase 2**: 4-6 hours  
**Phase 3**: 1-2 days

**Total**: 2-3 days of focused work

---

## Next Steps

1. **Test Ollama** - Verify queries work (30 mins)
2. **Add loading indicator** - Show Polly initialization (1 hour)
3. **Implement TOC sidebar** - Document outline (4-6 hours)
4. **Build template system** - Streamline AI notes (1-2 days)

**Ready to start?** Let me know which task to tackle first! 🚀
