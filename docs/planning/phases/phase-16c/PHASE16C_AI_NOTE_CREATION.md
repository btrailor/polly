# Phase 16c: AI Note Creation

**Version:** 1.0  
**Status:** Planning  
**Duration:** 4 weeks  
**Prerequisites:** Phase 16 (Native Notes Frontend) ✅, Phase 11 (Multi-Model Routing) 🔄  
**Next Phase:** Phase 17 (Advanced Search)

---

## Executive Summary

Phase 16c implements intelligent AI-powered note creation using the Architect persona framework. This system analyzes user requests, extracts templates from a user-defined folder, asks clarifying questions in Plan mode, generates structured content in Build mode, and learns from user edits over time (opt-in).

**Key Features:**
- Intent detection for note creation requests
- Template extraction from user-defined folder
- Architect persona with Plan→Build workflow
- Dynamic inline UI in chat interface
- Note preview before saving
- Learning loop from user edits (opt-in)

**User Experience:**
1. User: "Create a note about the Phase 11 planning session"
2. Polly (Plan mode): "I'll help create that note. A few questions..."
3. User answers questions
4. Polly (Build mode): Generates note with template applied
5. User previews, edits if needed, saves to vault

---

## Architecture Overview

### Two-Stage Agent System

```
┌─────────────────────────────────────────────────────────┐
│              User Message                               │
│  "Create a note about X"                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Intent Classification                          │
│  • Is this a note creation request?                    │
│  • What type of note? (meeting, task, concept, etc.)   │
│  • Explicit or implicit request?                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                   ┌──────────┐
                   │ Activate │
                   │Architect │
                   │ Persona  │
                   └──────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
    ┌──────────────┐           ┌──────────────┐
    │  Plan Mode   │           │  Build Mode  │
    │              │           │              │
    │ • Analyze    │──────────▶│ • Generate   │
    │ • Clarify    │  Switch   │ • Apply      │
    │ • Outline    │  (Manual) │   template   │
    │ • Questions  │           │ • Wiki-link  │
    └──────────────┘           └──────────────┘
                                       │
                                       ▼
                               ┌──────────────┐
                               │Note Preview  │
                               │  • Edit      │
                               │  • Approve   │
                               │  • Save      │
                               └──────────────┘
                                       │
                                       ▼
                               ┌──────────────┐
                               │ Learning     │
                               │ (Opt-in)     │
                               │ Track edits  │
                               └──────────────┘
```

### Template System

```
User's Template Folder (configured in settings):
~/Dropbox/Polly/Templates/

Templates discovered:
├── meeting-note.md          (Meeting notes template)
├── daily-note.md            (Daily journal template)
├── concept-note.md          (Concept/idea template)
├── project-overview.md      (Project documentation)
├── decision-record.md       (Decision log template)
└── person-note.md           (Person/contact template)

Template Pattern Extraction:
1. Parse all .md files in templates folder
2. Extract structure (headings, sections, placeholders)
3. Identify variables: {{title}}, {{date}}, {{tags}}
4. Store patterns in template database
5. Match user request to best template
```

---

## Week-by-Week Breakdown

### Week 1: Foundation (Intent Detection + Template System)

**Days 1-2: Intent Classification**

```python
# core/intent/note_detector.py
class NoteCreationDetector:
    """Detect if user message is requesting note creation"""
    
    EXPLICIT_TRIGGERS = [
        "create a note",
        "make a note",
        "write a note",
        "new note about",
        "take notes on",
        "document this",
        "save this as a note"
    ]
    
    IMPLICIT_PATTERNS = [
        r"(?:can you |could you |please )?(?:capture|record|document|write down)",
        r"(?:I want to |let's )(?:capture|document|remember)",
        r"(?:make|create) (?:a|an) (?:meeting|daily|concept|project) note"
    ]
    
    def detect(self, message: str, context: ConversationContext) -> NoteIntent | None:
        """
        Detect note creation intent
        
        Returns:
            NoteIntent with confidence score and extracted info
            None if not a note creation request
        """
        message_lower = message.lower()
        
        # Check explicit triggers
        for trigger in self.EXPLICIT_TRIGGERS:
            if trigger in message_lower:
                return NoteIntent(
                    confidence=0.95,
                    trigger=trigger,
                    type=self._classify_note_type(message),
                    explicit=True
                )
        
        # Check implicit patterns
        for pattern in self.IMPLICIT_PATTERNS:
            if re.search(pattern, message_lower):
                return NoteIntent(
                    confidence=0.75,
                    pattern=pattern,
                    type=self._classify_note_type(message),
                    explicit=False
                )
        
        # Check conversation context
        if self._context_suggests_note_creation(context):
            return NoteIntent(
                confidence=0.60,
                type="concept",
                explicit=False,
                from_context=True
            )
        
        return None
    
    def _classify_note_type(self, message: str) -> str:
        """Determine type of note being requested"""
        keywords = {
            "meeting": ["meeting", "call", "discussion", "sync"],
            "daily": ["daily", "journal", "today", "log"],
            "concept": ["idea", "concept", "thought", "theory"],
            "project": ["project", "initiative", "work", "implementation"],
            "decision": ["decision", "choice", "decided", "conclusion"],
            "person": ["person", "contact", "about", "profile"]
        }
        
        message_lower = message.lower()
        for note_type, triggers in keywords.items():
            if any(trigger in message_lower for trigger in triggers):
                return note_type
        
        return "general"
```

**Days 3-4: Template Configuration**

```python
# core/templates/manager.py
class TemplateManager:
    """Manage note templates from user-configured folder"""
    
    def __init__(self, config: Config):
        self.template_folder = config.get("notes.templates_folder")
        self.templates: dict[str, Template] = {}
        self.db = Database()
    
    async def load_templates(self):
        """
        Scan templates folder and extract patterns
        
        Process:
        1. Find all .md files in folder
        2. Parse structure and variables
        3. Extract common patterns
        4. Store in database for quick access
        """
        if not os.path.exists(self.template_folder):
            logger.warning(f"Templates folder not found: {self.template_folder}")
            return
        
        template_files = glob.glob(f"{self.template_folder}/*.md")
        
        for file_path in template_files:
            template = await self._parse_template(file_path)
            self.templates[template.name] = template
            await self.db.upsert("templates", template.to_dict())
        
        logger.info(f"Loaded {len(self.templates)} templates")
    
    async def _parse_template(self, file_path: str) -> Template:
        """
        Parse template file and extract structure
        
        Example template:
        ---
        title: {{title}}
        date: {{date}}
        tags: {{tags}}
        ---
        
        # {{title}}
        
        ## Overview
        {{overview}}
        
        ## Key Points
        {{key_points}}
        
        ## Related Notes
        {{related_notes}}
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split frontmatter and body
        parts = content.split('---', 2)
        frontmatter = yaml.safe_load(parts[1]) if len(parts) > 2 else {}
        body = parts[2] if len(parts) > 2 else content
        
        # Extract variables
        variables = re.findall(r'\{\{(\w+)\}\}', content)
        
        # Extract structure (headings)
        headings = re.findall(r'^#+\s+(.+)$', body, re.MULTILINE)
        
        return Template(
            name=os.path.basename(file_path).replace('.md', ''),
            path=file_path,
            variables=list(set(variables)),
            headings=headings,
            frontmatter_schema=frontmatter,
            raw_content=content
        )
    
    async def match_template(self, note_type: str, context: dict) -> Template | None:
        """
        Find best matching template for note type
        
        Matching strategy:
        1. Exact name match (e.g., "meeting" → meeting-note.md)
        2. Keyword match in template content
        3. Structure similarity
        4. Default to general template
        """
        # Exact match
        if f"{note_type}-note" in self.templates:
            return self.templates[f"{note_type}-note"]
        
        if note_type in self.templates:
            return self.templates[note_type]
        
        # Keyword match
        for name, template in self.templates.items():
            if note_type in template.raw_content.lower():
                return template
        
        # Default
        return self.templates.get("general", None)
```

**Days 5-7: Template Storage Configuration**

```yaml
# config.yaml additions
notes:
  vault_path: ~/Dropbox/Polly Notes/
  templates_folder: ~/Dropbox/Polly/Templates/
  
  # Template settings
  auto_detect_templates: true
  reload_templates_on_change: true
  
  # Note creation settings
  default_folder: "Inbox"
  auto_link_threshold: 0.7  # for wiki-link suggestions
  
  # Learning settings
  track_edits: false  # opt-in
  learning_mode: "passive"  # passive, active, off
```

Settings UI:
```
┌─────────────────────────────────────────────────────────┐
│  Settings > Notes > Templates                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Templates Folder:                                      │
│  [~/Dropbox/Polly/Templates/        ] [Browse...]      │
│                                                          │
│  ✓ Auto-detect templates                               │
│  ✓ Reload templates when files change                  │
│                                                          │
│  Templates Found: 6                                     │
│  ├─ meeting-note.md                                    │
│  ├─ daily-note.md                                      │
│  ├─ concept-note.md                                    │
│  ├─ project-overview.md                                │
│  ├─ decision-record.md                                 │
│  └─ person-note.md                                     │
│                                                          │
│  [Reload Templates] [Create New Template]              │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  AI Note Creation:                                      │
│  Default folder: [Inbox          ▼]                    │
│  Auto-link threshold: [●─────────] 0.7                 │
│                                                          │
│  Learning Mode:                                         │
│  ○ Off - Don't track edits                             │
│  ● Passive - Track edits, don't show UI (recommended)  │
│  ○ Active - Track edits, show feedback UI              │
│                                                          │
│  Privacy: Edit tracking is stored locally and never    │
│  leaves your device.                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Deliverables (Week 1):**
- ✅ Intent detection working for explicit/implicit requests
- ✅ Template folder configuration in settings
- ✅ Template parsing and pattern extraction
- ✅ Template matching algorithm
- ✅ Settings UI for templates

---

### Week 2: Architect Planning Mode

**Days 8-10: Planning System**

```python
# core/personas/architect_planning.py
class ArchitectPlanner:
    """Architect persona in Planning mode"""
    
    PLANNING_PROMPT = """You are Architect, Polly's planning persona for note creation.

Your job is to analyze the user's request and create a structured plan for the note.

Process:
1. Review conversation context
2. Identify what you know about the topic
3. Identify what you need to clarify
4. Ask 2-5 targeted questions (if needed)
5. Create a structured outline

Guidelines:
- Be concise but thorough
- Focus on understanding intent
- Ask specific, actionable questions
- Suggest structure based on note type
- Don't generate content yet (that's Build mode)

Available context:
- Conversation history
- Existing notes in vault
- Detected note type
- Matched template

Output format:
1. What I understand: [summary]
2. Questions: [2-5 questions if needed]
3. Proposed outline: [headings and sections]
4. Suggested template: [template name]
"""
    
    def __init__(self, router: IntelligentRouter, vault: NoteVault):
        self.router = router
        self.vault = vault
    
    async def plan(self, intent: NoteIntent, context: ConversationContext) -> Plan:
        """
        Create planning response for note creation
        
        Steps:
        1. Gather context from conversation and vault
        2. Generate clarifying questions
        3. Create outline based on template
        4. Return structured plan
        """
        # Gather context
        related_notes = await self.vault.find_related(intent.topic)
        template = await self.template_manager.match_template(intent.type, context)
        
        # Build planning prompt
        messages = [
            {"role": "system", "content": self.PLANNING_PROMPT},
            {"role": "user", "content": self._construct_planning_query(
                intent, context, related_notes, template
            )}
        ]
        
        # Use balanced tier (Sonnet 4 preferred)
        response = await self.router.complete_with_fallback(
            messages,
            task_type="planning",
            confidence="balanced"
        )
        
        # Parse response into structured plan
        plan = self._parse_plan_response(response.content, template)
        
        return plan
    
    def _construct_planning_query(self, 
                                  intent: NoteIntent,
                                  context: ConversationContext,
                                  related_notes: list[Note],
                                  template: Template) -> str:
        """Build comprehensive planning query"""
        
        query = f"""User wants to create a {intent.type} note.

Topic: {intent.topic}

Conversation context:
{self._summarize_context(context)}

Related notes in vault:
{self._format_related_notes(related_notes)}

Matched template: {template.name}
Template structure:
{self._format_template_structure(template)}

Please analyze this request and create a plan for the note.
"""
        return query
    
    def _parse_plan_response(self, content: str, template: Template) -> Plan:
        """
        Parse LLM response into structured Plan object
        
        Expected format:
        1. What I understand: ...
        2. Questions: ...
        3. Proposed outline: ...
        4. Suggested template: ...
        """
        # Parse sections using regex
        understanding = self._extract_section(content, "What I understand")
        questions = self._extract_list(content, "Questions")
        outline = self._extract_outline(content, "Proposed outline")
        
        return Plan(
            understanding=understanding,
            questions=questions,
            outline=outline,
            template=template,
            needs_clarification=len(questions) > 0
        )
```

**Days 11-12: Question/Answer Flow**

```python
# core/personas/qa_flow.py
class QuestionAnswerFlow:
    """Manage clarifying question/answer flow"""
    
    def __init__(self):
        self.current_plan: Plan | None = None
        self.answers: dict[str, str] = {}
    
    async def start_flow(self, plan: Plan) -> Message:
        """
        Start Q&A flow with user
        
        Returns message to display in chat UI
        """
        self.current_plan = plan
        self.answers = {}
        
        # Format questions for UI
        questions_ui = self._format_questions_ui(plan.questions)
        
        return Message(
            role="assistant",
            content=f"""I'll help create that {plan.template.name}.

**What I understand:**
{plan.understanding}

**A few questions to make this note more useful:**
{questions_ui}

Once you answer these, I'll generate the note in Build mode.
[Skip questions and generate now]
""",
            ui_component="question_list",
            metadata={"plan_id": plan.id}
        )
    
    async def process_answer(self, question_num: int, answer: str):
        """Record user's answer to a question"""
        if not self.current_plan:
            raise ValueError("No active plan")
        
        question = self.current_plan.questions[question_num]
        self.answers[question] = answer
    
    def is_complete(self) -> bool:
        """Check if all questions have been answered"""
        if not self.current_plan:
            return False
        return len(self.answers) == len(self.current_plan.questions)
    
    def get_enriched_plan(self) -> Plan:
        """Return plan with answers incorporated"""
        plan = self.current_plan
        plan.user_answers = self.answers
        return plan
```

**Days 13-14: Dynamic Inline UI**

```javascript
// frontend/js/note-creation-ui.js
class NoteCreationUI {
    /**
     * Render inline Q&A interface in chat
     */
    renderQuestionList(questions, planId) {
        const container = document.createElement('div');
        container.className = 'note-planning-questions';
        
        questions.forEach((question, index) => {
            const questionEl = this.createQuestionElement(question, index, planId);
            container.appendChild(questionEl);
        });
        
        // Add skip button
        const skipBtn = document.createElement('button');
        skipBtn.textContent = 'Skip and generate now';
        skipBtn.className = 'skip-questions-btn';
        skipBtn.onclick = () => this.skipQuestions(planId);
        container.appendChild(skipBtn);
        
        return container;
    }
    
    createQuestionElement(question, index, planId) {
        const wrapper = document.createElement('div');
        wrapper.className = 'planning-question';
        
        wrapper.innerHTML = `
            <div class="question-number">${index + 1}.</div>
            <div class="question-text">${question}</div>
            <textarea 
                class="question-answer" 
                data-question-index="${index}"
                data-plan-id="${planId}"
                placeholder="Type your answer..."
                rows="2"
            ></textarea>
            <button 
                class="submit-answer-btn"
                data-question-index="${index}"
                data-plan-id="${planId}"
            >
                ✓
            </button>
        `;
        
        // Auto-resize textarea
        const textarea = wrapper.querySelector('textarea');
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        
        // Submit on Enter (Shift+Enter for new line)
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.submitAnswer(planId, index, textarea.value);
            }
        });
        
        // Submit button click
        const btn = wrapper.querySelector('.submit-answer-btn');
        btn.onclick = () => this.submitAnswer(planId, index, textarea.value);
        
        return wrapper;
    }
    
    async submitAnswer(planId, questionIndex, answer) {
        // Send to backend
        await window.api.invoke('note:answer-question', {
            planId,
            questionIndex,
            answer
        });
        
        // Update UI to show answer submitted
        const questionEl = document.querySelector(
            `[data-question-index="${questionIndex}"][data-plan-id="${planId}"]`
        );
        questionEl.classList.add('answered');
        
        // Check if all questions answered
        const allQuestions = document.querySelectorAll(
            `[data-plan-id="${planId}"] .planning-question`
        );
        const allAnswered = Array.from(allQuestions)
            .every(q => q.classList.contains('answered'));
        
        if (allAnswered) {
            this.showBuildPrompt(planId);
        }
    }
    
    showBuildPrompt(planId) {
        const prompt = document.createElement('div');
        prompt.className = 'build-mode-prompt';
        prompt.innerHTML = `
            <p>✓ All questions answered!</p>
            <button onclick="noteCreation.switchToBuildMode('${planId}')">
                Generate Note (Build Mode)
            </button>
        `;
        
        document.querySelector(`[data-plan-id="${planId}"]`)
            .appendChild(prompt);
    }
}
```

**Deliverables (Week 2):**
- ✅ Architect Planning mode operational
- ✅ Clarifying questions generated
- ✅ Q&A flow in chat interface
- ✅ Dynamic inline UI for questions
- ✅ Plan enrichment with user answers

---

### Week 3: Architect Building Mode

**Days 15-17: Content Generation**

```python
# core/personas/architect_building.py
class ArchitectBuilder:
    """Architect persona in Building mode"""
    
    BUILDING_PROMPT = """You are Architect, Polly's building persona for note creation.

Your job is to generate high-quality note content based on the plan.

Process:
1. Review the plan and user's answers
2. Apply the template structure
3. Generate content for each section
4. Add wiki-links to related notes
5. Ensure consistency and quality

Guidelines:
- Follow the template structure exactly
- Use markdown formatting
- Add [[wiki-links]] to related notes naturally
- Be thorough but concise
- Maintain user's voice and terminology
- Include all user-provided information

Output format:
Complete markdown note with:
- Frontmatter (title, date, tags)
- Structured headings
- Rich content
- Wiki-links
"""
    
    def __init__(self, router: IntelligentRouter, vault: NoteVault):
        self.router = router
        self.vault = vault
    
    async def build(self, plan: Plan) -> Note:
        """
        Generate note content from plan
        
        Steps:
        1. Load template
        2. Gather all context (plan, answers, related notes)
        3. Generate content using thorough tier
        4. Apply template structure
        5. Add wiki-links
        6. Validate output
        """
        # Gather context
        template = plan.template
        related_notes = await self.vault.find_related(plan.topic)
        
        # Build generation prompt
        messages = [
            {"role": "system", "content": self.BUILDING_PROMPT},
            {"role": "user", "content": self._construct_building_query(
                plan, template, related_notes
            )}
        ]
        
        # Use thorough tier (Opus 4 or Sonnet 4)
        response = await self.router.complete_with_fallback(
            messages,
            task_type="content_creation",
            confidence="thorough"
        )
        
        # Parse and validate
        note_content = self._parse_note_content(response.content)
        note = self._create_note_object(note_content, plan)
        
        # Add wiki-links
        note = await self._add_wiki_links(note, related_notes)
        
        return note
    
    def _construct_building_query(self,
                                  plan: Plan,
                                  template: Template,
                                  related_notes: list[Note]) -> str:
        """Build comprehensive generation query"""
        
        query = f"""Generate a {template.name} based on this plan.

**Topic:** {plan.topic}

**User's Answers:**
{self._format_answers(plan.user_answers)}

**Proposed Outline:**
{self._format_outline(plan.outline)}

**Template Structure:**
{template.raw_content}

**Related Notes (for wiki-linking):**
{self._format_related_notes(related_notes)}

Please generate the complete note following the template structure.
"""
        return query
    
    async def _add_wiki_links(self, note: Note, related_notes: list[Note]) -> Note:
        """
        Add [[wiki-links]] to related notes
        
        Strategy:
        1. Find mentions of related note titles in content
        2. Check semantic similarity threshold
        3. Add [[links]] naturally without over-linking
        """
        content = note.content
        
        for related in related_notes:
            # Check if note title appears in content
            title = related.title
            if title.lower() in content.lower():
                # Replace with wiki-link (case-insensitive, first occurrence)
                content = re.sub(
                    f'\\b{re.escape(title)}\\b',
                    f'[[{title}]]',
                    content,
                    count=1,
                    flags=re.IGNORECASE
                )
        
        note.content = content
        return note
```

**Days 18-19: Template Application**

```python
# core/templates/applicator.py
class TemplateApplicator:
    """Apply templates to generated content"""
    
    def apply(self, content: str, template: Template, variables: dict) -> str:
        """
        Apply template structure to content
        
        Process:
        1. Parse generated content into sections
        2. Map sections to template structure
        3. Fill template variables
        4. Ensure all required sections present
        5. Format frontmatter
        """
        # Parse content
        sections = self._parse_sections(content)
        
        # Start with template
        output = template.raw_content
        
        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            output = output.replace(placeholder, str(var_value))
        
        # Fill sections
        for heading, section_content in sections.items():
            # Find matching section in template
            pattern = f"## {heading}\\n{{{{\\w+}}}}"
            output = re.sub(
                pattern,
                f"## {heading}\n{section_content}",
                output
            )
        
        return output
    
    def _parse_sections(self, content: str) -> dict[str, str]:
        """Parse markdown content into sections by heading"""
        sections = {}
        current_heading = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                # Save previous section
                if current_heading:
                    sections[current_heading] = '\n'.join(current_content).strip()
                
                # Start new section
                current_heading = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_heading:
            sections[current_heading] = '\n'.join(current_content).strip()
        
        return sections
```

**Days 20-21: Note Object Creation**

```python
# core/notes/note.py
class Note:
    """Represents a note with metadata"""
    
    def __init__(self,
                 title: str,
                 content: str,
                 tags: list[str] = None,
                 folder: str = "Inbox",
                 **metadata):
        self.title = title
        self.content = content
        self.tags = tags or []
        self.folder = folder
        self.metadata = metadata
        
        # Generation metadata
        self.created_at = datetime.now()
        self.created_by = "ai"
        self.template_used = metadata.get("template")
        self.plan_id = metadata.get("plan_id")
    
    def to_markdown(self) -> str:
        """Convert to markdown with frontmatter"""
        frontmatter = {
            "title": self.title,
            "date": self.created_at.strftime("%Y-%m-%d"),
            "tags": self.tags,
            "created_by": "polly",
            **self.metadata
        }
        
        return f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---

{self.content}
"""
    
    def get_file_path(self, vault_path: str) -> str:
        """Get full file path for saving"""
        # Sanitize filename
        filename = re.sub(r'[^\w\s-]', '', self.title)
        filename = filename.replace(' ', '-').lower()
        
        return os.path.join(vault_path, self.folder, f"{filename}.md")
```

**Deliverables (Week 3):**
- ✅ Architect Building mode operational
- ✅ Content generation with thorough tier
- ✅ Template application working
- ✅ Wiki-link insertion
- ✅ Note object creation

---

### Week 4: Preview, Learning, and Polish

**Days 22-24: Note Preview & Editing**

```javascript
// frontend/js/note-preview.js
class NotePreview {
    /**
     * Show note preview before saving
     */
    async showPreview(note) {
        const modal = document.createElement('div');
        modal.className = 'note-preview-modal';
        
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Note Preview</h2>
                
                <div class="preview-metadata">
                    <input 
                        type="text" 
                        class="note-title" 
                        value="${note.title}"
                        placeholder="Note title"
                    />
                    <input 
                        type="text" 
                        class="note-folder" 
                        value="${note.folder}"
                        placeholder="Folder"
                    />
                    <input 
                        type="text" 
                        class="note-tags" 
                        value="${note.tags.join(', ')}"
                        placeholder="Tags (comma-separated)"
                    />
                </div>
                
                <div class="preview-tabs">
                    <button class="tab-btn active" data-tab="preview">Preview</button>
                    <button class="tab-btn" data-tab="edit">Edit</button>
                    <button class="tab-btn" data-tab="raw">Raw Markdown</button>
                </div>
                
                <div class="preview-content">
                    <div class="tab-panel active" data-tab="preview">
                        ${marked.parse(note.content)}
                    </div>
                    <div class="tab-panel" data-tab="edit">
                        <textarea class="note-editor">${note.content}</textarea>
                    </div>
                    <div class="tab-panel" data-tab="raw">
                        <pre>${note.to_markdown()}</pre>
                    </div>
                </div>
                
                <div class="preview-actions">
                    <button class="cancel-btn">Cancel</button>
                    <button class="save-btn primary">Save to Vault</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Tab switching
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.onclick = () => this.switchTab(btn.dataset.tab);
        });
        
        // Save button
        modal.querySelector('.save-btn').onclick = async () => {
            const editedNote = this.getEditedNote(modal, note);
            await this.saveNote(editedNote);
            modal.remove();
        };
        
        // Cancel button
        modal.querySelector('.cancel-btn').onclick = () => {
            modal.remove();
        };
    }
    
    getEditedNote(modal, originalNote) {
        return {
            ...originalNote,
            title: modal.querySelector('.note-title').value,
            folder: modal.querySelector('.note-folder').value,
            tags: modal.querySelector('.note-tags').value
                .split(',')
                .map(t => t.trim())
                .filter(t => t),
            content: modal.querySelector('.note-editor').value
        };
    }
    
    async saveNote(note) {
        const result = await window.api.invoke('note:save', note);
        
        if (result.success) {
            this.showSuccess(`Note saved: ${note.title}`);
            
            // Track edit changes if enabled
            if (window.settings.trackEdits) {
                await this.trackEdits(note, result.file_path);
            }
        } else {
            this.showError(`Failed to save note: ${result.error}`);
        }
    }
    
    async trackEdits(note, filePath) {
        // Compare original AI-generated content with user edits
        const original = note._original_content;
        const edited = note.content;
        
        if (original !== edited) {
            const diff = this.computeDiff(original, edited);
            
            await window.api.invoke('learning:track-edit', {
                note_id: note.id,
                plan_id: note.plan_id,
                template: note.template_used,
                diff: diff,
                timestamp: Date.now()
            });
        }
    }
}
```

**Days 25-26: Learning Loop (Opt-in)**

```python
# core/learning/edit_tracker.py
class EditTracker:
    """Track user edits to improve future note generation"""
    
    def __init__(self, config: Config):
        self.enabled = config.get("notes.track_edits", False)
        self.mode = config.get("notes.learning_mode", "passive")
        self.db = Database()
    
    async def track_edit(self, 
                        note_id: str,
                        plan_id: str,
                        template: str,
                        diff: dict):
        """
        Record user edit for learning
        
        Privacy: All data stored locally, never sent externally
        """
        if not self.enabled:
            return
        
        await self.db.insert("note_edits", {
            "note_id": note_id,
            "plan_id": plan_id,
            "template": template,
            "diff_summary": self._summarize_diff(diff),
            "edit_type": self._classify_edit(diff),
            "timestamp": datetime.now()
        })
        
        # Update template patterns
        await self._update_template_patterns(template, diff)
    
    def _classify_edit(self, diff: dict) -> str:
        """
        Classify type of edit
        
        Types:
        - structure: Changed headings, sections
        - content: Changed wording, added/removed content
        - formatting: Changed markdown formatting
        - links: Added/removed wiki-links
        - metadata: Changed title, tags, folder
        """
        if diff.get("headings_changed"):
            return "structure"
        elif diff.get("links_changed"):
            return "links"
        elif diff.get("metadata_changed"):
            return "metadata"
        elif diff.get("significant_content_change"):
            return "content"
        else:
            return "formatting"
    
    async def _update_template_patterns(self, template: str, diff: dict):
        """
        Learn from edits to improve future generations
        
        Examples:
        - User always removes a section → don't include in future
        - User always adds a section → include in template
        - User changes heading names → use preferred names
        """
        patterns = await self.db.query(
            "template_patterns",
            {"template": template}
        )
        
        # Update patterns based on edit
        if diff["edit_type"] == "structure":
            # User changed structure, learn preference
            await self._learn_structure_preference(template, diff)
        
        elif diff["edit_type"] == "content":
            # User added content, identify gaps
            await self._learn_content_gaps(template, diff)
    
    async def get_insights(self, template: str) -> dict:
        """
        Get learning insights for a template
        
        Returns common edit patterns and suggestions
        """
        edits = await self.db.query(
            "note_edits",
            {"template": template},
            limit=100
        )
        
        return {
            "total_edits": len(edits),
            "common_edit_types": self._aggregate_edit_types(edits),
            "frequently_removed": self._find_removed_sections(edits),
            "frequently_added": self._find_added_sections(edits),
            "suggested_improvements": self._generate_suggestions(edits)
        }
```

**Days 27-28: Testing & Polish**

Integration testing:
- [ ] End-to-end note creation flow
- [ ] All template types working
- [ ] Q&A flow validation
- [ ] Preview and editing
- [ ] Save to vault
- [ ] Learning tracking (opt-in)

UI polish:
- [ ] Smooth transitions between Plan/Build
- [ ] Loading states during generation
- [ ] Error handling and recovery
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements

**Deliverables (Week 4):**
- ✅ Note preview interface complete
- ✅ Edit tracking system (opt-in)
- ✅ Learning loop operational
- ✅ Full integration testing
- ✅ UI polish and accessibility

---

## Complete Workflow Example

### User Journey

**Step 1: User Request**
```
Brett: Create a note about today's Phase 11 planning session
```

**Step 2: Intent Detection**
```python
intent = NoteIntent(
    confidence=0.95,
    trigger="create a note",
    type="meeting",
    topic="Phase 11 planning session",
    explicit=True
)
```

**Step 3: Architect Plan Mode Activated**
```
Polly (Plan Mode): I'll help create a meeting note about the Phase 11 
planning session.

What I understand:
• This is about the Phase 11 (Multi-Model Routing) planning session
• You want to document decisions and next steps
• Template: meeting-note.md

A few questions to make this note more useful:

1. Who attended this planning session?
2. What were the main decisions made?
3. What are the immediate next steps?
4. What open questions remain?

[Skip questions and generate now]
```

**Step 4: User Answers Questions**
```
1. Just me and Polly
2. Decided on 8 providers, 5-week timeline, Grok safety filters
3. Create all planning docs, then start Phase 11a
4. None - all decisions finalized
```

**Step 5: Switch to Build Mode**
```
Polly: ✓ All questions answered!

Switching to Build mode to generate the note...
[Uses Opus 4 via thorough tier]
```

**Step 6: Note Preview**
```
┌─────────────────────────────────────────────────────────┐
│  Note Preview                                           │
├─────────────────────────────────────────────────────────┤
│  Title: [Phase 11 Planning Session - Jan 28 2026]      │
│  Folder: [Meetings]                                     │
│  Tags: [phase-11, planning, multi-model-routing]       │
│                                                          │
│  [Preview] [Edit] [Raw Markdown]                       │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  # Phase 11 Planning Session - Jan 28 2026             │
│                                                          │
│  ## Attendees                                           │
│  - Brett Gershon                                        │
│  - Polly (AI)                                           │
│                                                          │
│  ## Key Decisions                                       │
│  1. Support for 8 cloud AI providers                   │
│     - [[Anthropic]], [[OpenAI]], [[GitHub Copilot]]   │
│     - [[OpenRouter]], [[Google AI]], [[Mistral AI]]   │
│     - [[Grok]] (with safety filters), [[Perplexity]]  │
│                                                          │
│  2. 5-week implementation timeline                     │
│     - Phase 11a: Core routing (2 weeks)                │
│     - Phase 11b: Extended providers (2 weeks)          │
│     - Phase 11c: Orchestration (1 week)                │
│                                                          │
│  3. [[Grok Safety Filters]] are mandatory              │
│     - Whitelist: code, technical, math                 │
│     - Blacklist: politics, history, news               │
│     - Content filtering for conspiracy/extremist       │
│                                                          │
│  ## Next Steps                                          │
│  - [ ] Create 7 planning documents                     │
│  - [ ] Update [[Master Roadmap]]                       │
│  - [ ] Begin [[Phase 11a]] Day 1 implementation        │
│                                                          │
│  ## Open Questions                                      │
│  None - all decisions finalized                        │
│                                                          │
│  ## Related                                             │
│  - [[PHASE11_MULTI_MODEL_ENHANCED_V2]]                │
│  - [[PHASE16C_AI_NOTE_CREATION]]                      │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  [Cancel]  [Save to Vault]                             │
└─────────────────────────────────────────────────────────┘
```

**Step 7: User Edits (Optional)**
- Switches to Edit tab
- Adds more detail to "Next Steps"
- Saves to vault

**Step 8: Learning (Opt-in)**
```python
# If tracking enabled, record edit
edit_tracker.track_edit(
    note_id="phase-11-planning-jan-28",
    template="meeting-note",
    diff={
        "sections_added": [],
        "sections_removed": [],
        "content_expanded": ["Next Steps"],
        "links_added": 3
    }
)
```

---

## Configuration Schema

```yaml
# config.yaml additions for Phase 16c

notes:
  # Vault settings (from Phase 16)
  vault_path: ~/Dropbox/Polly Notes/
  default_folder: Inbox
  
  # Template settings (Phase 16c)
  templates_folder: ~/Dropbox/Polly/Templates/
  auto_detect_templates: true
  reload_templates_on_change: true
  
  # AI note creation settings
  ai_creation:
    enabled: true
    confidence_threshold: 0.7  # for intent detection
    auto_link_threshold: 0.7   # for wiki-link suggestions
    max_related_notes: 10      # for context
    
    # Planning mode
    planning:
      max_questions: 5
      always_ask: false  # if true, always ask questions
      use_tier: balanced  # fast, balanced, thorough
    
    # Building mode
    building:
      use_tier: thorough  # prefer high-quality models
      add_wiki_links: true
      validate_output: true
  
  # Learning settings
  learning:
    track_edits: false  # opt-in, default false
    mode: passive       # passive, active, off
    store_original: true  # keep original AI version
    privacy_mode: true    # never send data externally

# Architect persona settings
personas:
  architect:
    enabled: true
    default_mode: plan  # plan or build
    allow_manual_switch: true
    planning_tier: balanced
    building_tier: thorough
```

---

## Database Schema

```sql
-- Note creation plans
CREATE TABLE note_plans (
    id TEXT PRIMARY KEY,
    conversation_id INTEGER,
    intent_type TEXT NOT NULL,
    topic TEXT NOT NULL,
    template_name TEXT,
    understanding TEXT,
    questions TEXT,  -- JSON array
    outline TEXT,    -- JSON array
    user_answers TEXT,  -- JSON object
    created_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Generated notes metadata
CREATE TABLE generated_notes (
    id TEXT PRIMARY KEY,
    plan_id TEXT,
    file_path TEXT NOT NULL,
    title TEXT NOT NULL,
    template_used TEXT,
    tokens_used INTEGER,
    cost REAL,
    provider TEXT,
    model TEXT,
    created_at DATETIME,
    FOREIGN KEY (plan_id) REFERENCES note_plans(id)
);

-- Edit tracking (opt-in)
CREATE TABLE note_edits (
    id INTEGER PRIMARY KEY,
    note_id TEXT NOT NULL,
    plan_id TEXT,
    template TEXT,
    edit_type TEXT,  -- structure, content, formatting, links, metadata
    diff_summary TEXT,  -- JSON
    timestamp DATETIME,
    FOREIGN KEY (note_id) REFERENCES generated_notes(id)
);

-- Template patterns (learned from edits)
CREATE TABLE template_patterns (
    id INTEGER PRIMARY KEY,
    template_name TEXT NOT NULL,
    pattern_type TEXT,  -- structure, content, style
    pattern_data TEXT,  -- JSON
    confidence REAL,
    sample_size INTEGER,
    last_updated DATETIME
);
```

---

## Testing Strategy

### Unit Tests
- [ ] Intent detection (explicit, implicit, context-based)
- [ ] Template parsing and matching
- [ ] Q&A flow state management
- [ ] Wiki-link insertion
- [ ] Diff computation for learning

### Integration Tests
- [ ] Full Plan→Build workflow
- [ ] Template application
- [ ] Note saving to vault
- [ ] Edit tracking (when enabled)

### UI Tests
- [ ] Question list rendering
- [ ] Answer submission
- [ ] Note preview modal
- [ ] Edit interface
- [ ] Mode switching

### End-to-End Tests
```python
async def test_complete_note_creation():
    # 1. User requests note
    response = await chat.send("Create a note about my project idea")
    assert "Architect" in response.persona
    assert response.mode == "plan"
    
    # 2. Polly asks questions
    assert len(response.questions) > 0
    
    # 3. User answers
    for i, question in enumerate(response.questions):
        await chat.send(f"Answer to question {i+1}")
    
    # 4. Switch to build mode
    await chat.send("/build")
    
    # 5. Note generated
    note = await chat.get_generated_note()
    assert note is not None
    assert note.title
    assert note.content
    
    # 6. User previews and saves
    await chat.save_note(note, vault_path)
    
    # 7. Verify file exists
    assert os.path.exists(note.file_path)
```

---

## Performance Targets

**Intent Detection:**
- Latency: < 100ms (local regex matching)
- Accuracy: > 95% for explicit triggers
- Accuracy: > 80% for implicit patterns

**Planning Mode:**
- Response time: < 5s (using balanced tier)
- Question quality: 2-5 relevant questions
- Outline quality: Matches template structure

**Building Mode:**
- Response time: < 15s (using thorough tier)
- Content quality: Professional, well-structured
- Wiki-link accuracy: > 90% relevant links

**Template Matching:**
- Latency: < 50ms (cached templates)
- Accuracy: > 90% correct template selection

**Learning Loop:**
- Edit tracking latency: < 100ms
- Pattern update latency: < 1s
- Storage: Local only, no external network

---

## Dependencies

**Backend (Python):**
```
# Already have from Phase 11
anthropic>=0.20.0
openai>=1.10.0

# New for Phase 16c
pyyaml>=6.0  # template parsing
python-frontmatter>=1.0  # frontmatter handling
difflib  # built-in, for diff computation
```

**Frontend (JavaScript):**
```
// Already have
marked.js  # markdown rendering

// New for Phase 16c
diff-match-patch  # visual diff display (optional)
```

---

## Migration Plan

### Phase 16 → Phase 16c

**Existing Features to Preserve:**
- Note viewing and editing
- Folder structure
- Search functionality
- Wikilink navigation

**New Features to Add:**
- AI note creation command
- Template system
- Architect persona UI
- Preview modal

**Migration Steps:**
1. Add template configuration to settings
2. Create default templates folder
3. Add Architect UI components
4. Enable AI creation feature flag
5. Test with existing vault

---

## Risk Assessment

### High Risk
**1. User Expects Proactive Suggestions**
- Risk: User said "Only explicit requests" but might expect suggestions
- Mitigation: Clear UI indicating when AI mode is active
- Fallback: Add preference toggle

**2. Learning Loop Privacy Concerns**
- Risk: Users uncomfortable with edit tracking
- Mitigation: Opt-in only, clear privacy policy, local-only storage
- Transparency: Show what's being tracked in UI

### Medium Risk
**1. Template Matching Accuracy**
- Risk: Wrong template selected for note type
- Mitigation: Manual template override in UI
- Fallback: Generic template always available

**2. Question Relevance**
- Risk: AI asks irrelevant or redundant questions
- Mitigation: Context-aware question generation
- Escape: "Skip questions" button

**3. Wiki-Link Over-linking**
- Risk: Too many or irrelevant links added
- Mitigation: Threshold-based linking, user review in preview
- Fix: Easy to remove in edit mode

---

## Success Metrics

**Phase 16c Success Criteria:**
- [ ] Intent detection: 95%+ accuracy for explicit requests
- [ ] Template matching: 90%+ correct selection
- [ ] Note quality: 80%+ of notes saved without major edits
- [ ] User satisfaction: Positive feedback on Plan/Build flow
- [ ] Performance: < 20s total time from request to preview
- [ ] Learning: Measurable improvement in note quality over time (if enabled)

---

## Future Enhancements

**Phase 16d (Future):**
- Voice note transcription + AI structuring
- Batch note creation from multiple sources
- Note templates with conditional logic
- Collaborative note creation (multi-user)

**Advanced Features:**
- Automatic note linking after creation
- Note quality scoring and suggestions
- Template marketplace (share templates)
- Multi-language template support

---

## Documentation Requirements

**User Documentation:**
- AI note creation guide
- Template creation tutorial
- Architect persona explanation
- Learning system transparency

**Developer Documentation:**
- Intent detection API
- Template system architecture
- Adding new persona modes
- Learning system internals

---

## Timeline Summary

| Week | Focus | Key Deliverables |
|------|-------|-----------------|
| 1 | Foundation | Intent detection, Template system, Configuration |
| 2 | Planning | Architect Plan mode, Q&A flow, Dynamic UI |
| 3 | Building | Architect Build mode, Content generation, Wiki-links |
| 4 | Polish | Preview UI, Learning loop, Testing, Documentation |

**Total Duration:** 4 weeks

**Dependencies:** Phase 11 (routing system), Phase 16 (notes frontend)

**Next Phase:** Phase 17 (Advanced Search)

---

## Approval Status

**Status:** ✅ Ready for Implementation

**Approved By:** User (Brett)

**Date:** January 28, 2026

**Next Step:** Begin Week 1 Day 1 after Phase 11 completion

---

## Related Documents

- [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md) - Multi-model routing
- [PHASE11_AGENT_PERSONAS.md](./PHASE11_AGENT_PERSONAS.md) - Agent persona framework
- [PHASE16_COMPLETE.md](./PHASE16_COMPLETE.md) - Native notes frontend
- [master_roadmap.md](./master_roadmap.md) - Overall project roadmap
