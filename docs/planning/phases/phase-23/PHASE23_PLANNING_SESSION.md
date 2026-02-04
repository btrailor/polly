# Phase 23: Curriculum System - Planning Session Notes

**Date:** February 2, 2026  
**Status:** Planning Complete  
**Session Type:** Detailed Design Discussion

---

## Session Overview

This document captures a comprehensive planning session for Phase 23: Curriculum Learning System. The session explored the gaps in Polly's current learning capabilities and designed a complete solution for structured curriculum creation, enrichment, progress tracking, and guided learning.

---

## Problem Identification

### Current Capabilities
- Professor can generate learning path outlines in chat (curriculum mode)
- Outlines exist only as text in conversation history
- No structured storage or tracking
- No enrichment workflow (outlines don't become detailed lessons)
- No UI for viewing or following curricula
- Professor doesn't know user is "following a curriculum"

### User Pain Point
**Current workflow:**
1. User: "Create learning plan for X"
2. Professor: Generates text outline
3. User: "Now what?" - outline is just text in chat
4. User must manually track progress, build materials, follow outline

**Problem:** No bridge between chat-based outline generation and actual structured learning experience.

---

## Key Design Decisions

### 1. Curriculum Storage

**Question:** Where should curricula live?

**Decision:** `vault/.polly/curricula/` (separate from notes, parallel to skills)

**Rationale:**
- Keep curricula separate from regular notes (different use case)
- Similar to skill packages structure
- User's knowledge base, but organized differently

**Structure per curriculum:**
```
vault/.polly/curricula/{curriculum-id}/
├── CURRICULUM.md         # Human-readable
├── curriculum.json       # Machine-readable structure
├── progress.json         # Progress tracking
└── resources/            # Diagrams, exercises, examples
    ├── week-1/
    └── week-2/
```

### 2. Template Strategy

**Initial Idea:** Topic-specific templates (React template, Python template, etc.)

**Problem:** Would need hundreds of templates, maintenance nightmare

**Revised Decision:** 5 domain-based templates that adapt to any topic

**Final Templates:**
1. **Programming Language** - Any language (Python, JS, Lua, Rust, etc.)
2. **Framework/Library** - Any framework (React, Flask, Express, etc.)
3. **Skill Acquisition** - Tools/platforms (Norns, Ableton, Figma, etc.)
4. **Problem-Solving** - Specific problems (optimize API, build synth, etc.)
5. **Domain Exploration** - Broad domains (ML, Audio DSP, Web3, etc.)

**Template Selection:**
- Auto-detection with "recommended" label
- User can override if recommendation is wrong
- Hybrid customization: keep structure, heavily adapt content

**Example: Programming Language Template**
- Detects: "learn Python", "get better at JavaScript", "master Lua"
- Structure: Week 1 (Syntax), Week 2 (Core Concepts), Week 3 (Paradigms), etc.
- Customization questions:
  - Which language?
  - Prior experience?
  - What do you want to build?
  - Focus areas?
- Adapts: Changes language examples, adjusts pace, focuses on user goals

**Extensibility:** Users can save curricula as custom templates (Phase 23b)

### 3. Enrichment Strategy

**Question:** When and how should curriculum sections be enriched with detailed content?

**Options Considered:**

**Option A: Automatic Progressive Enrichment**
- Pros: Always one step ahead, minimal user effort
- Cons: Uses resources upfront, may generate unneeded content

**Option B: On-Demand Enrichment**
- Pros: Full user control, no wasted resources
- Cons: More manual work, may delay learning

**Option C: Hybrid Smart Enrichment** ✅ CHOSEN
- Auto-enrich current section when user starts it
- Preview next section (summary only)
- Can manually request enrichment of future sections
- Adapts based on progress (if user struggles, add more examples)

**Enrichment Depth:** Heavy
- Detailed explanations
- Diagrams (Mermaid)
- Code examples (3-4 progressive)
- Exercises (4-5 with solutions)
- Resources (skill packages, docs)
- Assessment criteria

**Timing:** Triggered when user clicks "Start Section"
- Loading indicator: "Enriching section with materials..."
- Takes ~10-30 seconds
- Cached (section.enriched = true)
- No re-generation on restart

### 4. Learning Flow

**Question:** How should users interact with curricula during learning?

**Options Considered:**

**Flow A: Explicit Session Mode**
- Start/end sessions manually
- Clear boundaries, structured time
- Cons: Rigid, requires ceremony

**Flow B: Ambient Curriculum Awareness**
- Professor always knows active curricula
- No formal sessions
- Cons: May lose track, less structure

**Flow C: Sessions + Ambient** ✅ CHOSEN
- Formal sessions for structured learning
- Ambient awareness for flexible help
- Best of both worlds

**Session Experience:**
- User clicks "Start Section" → session begins
- Session indicator appears (floating UI element)
- Professor in "session mode" (contextualized responses)
- Complete section → session ends automatically
- Can manually end session early

**Ambient Experience:**
- User asks question outside session
- Professor checks active curricula
- If question relates to curriculum topic, adds helpful context
- Example: "(This relates to your React Mastery curriculum - Week 2)"
- Non-intrusive, just adds awareness

### 5. Progress Tracking

**Question:** How granular should progress tracking be?

**Levels Considered:**
1. High-level milestones (completed weeks)
2. Individual topics within weeks
3. Concept mastery + exercises completed
4. All of above + time spent, struggles, breakthroughs

**Decision:** Subheading-level tracking (Level 3-4)

**Track per section (week-1.1, week-1.2, etc.):**
- Status: not_started, in_progress, completed, skipped
- Timestamps: started_at, completed_at
- Time spent: total minutes
- Mastery level: 1-5 (self-reported)
- Struggles: text notes
- Breakthroughs: text notes
- Notes created: linked file paths
- Exercises completed: IDs

**Reflection on Completion:**
- Prompt user for:
  - Mastery level (1-5)
  - What was challenging? (optional)
  - Any breakthroughs? (optional)
- Saves to progress.json
- Informs future section adaptations

### 6. Curriculum Creation Flow

**Question:** When user creates curriculum in chat, what happens?

**Options:**

**A: Immediately save, ask "Ready to start?"**
- Fast, but user can't review first

**B: Show outline, let user review/edit, then save** ✅ CHOSEN
- User has control, can iterate before committing

**C: Save automatically in "draft", activate later**
- Middle ground, but still no review step

**Chosen Flow:**
1. User requests curriculum in chat
2. Professor generates outline using template
3. **Review dialog appears:**
   - Left panel: Editable markdown textarea
   - Right panel: Preview (metadata + structure tree)
   - Actions: "Cancel", "Ask for Changes", "Save & Activate"
4. User can:
   - Edit outline directly in textarea
   - OR click "Ask for Changes" to iterate with Professor
5. User clicks "Save & Activate"
6. Curriculum created in vault, status = "active"
7. Notification: "Curriculum created! Ready to start Week 1?"

---

## Architecture Decisions

### Data Models

**CurriculumSection:**
```python
@dataclass
class CurriculumSection:
    id: str                    # "week-1.1"
    title: str                 # "Platform Overview"
    type: str                  # "lesson", "hands-on", "project"
    order: int
    parent_id: str             # "week-1"
    
    # Content
    description: str
    concepts: List[str]
    estimated_time: str
    
    # Enrichment (added when section starts)
    enriched: bool
    resources: List[Dict]
    exercises: List[str]
    diagrams: List[str]
    examples: List[str]
    
    # Progress
    status: str                # "not_started", "in_progress", "completed"
    started_at: datetime
    completed_at: datetime
    time_spent_minutes: int
    mastery_level: int         # 1-5
    struggles: List[str]
    breakthroughs: List[str]
    notes_created: List[str]
```

**Curriculum:**
```python
@dataclass
class Curriculum:
    id: str
    title: str
    version: str
    
    # Metadata
    created: datetime
    last_updated: datetime
    status: str                # "draft", "active", "completed", "paused"
    
    # Learning context
    goal: str
    current_level: str
    estimated_duration: str
    
    # Structure
    sections: List[CurriculumSection]
    current_section_id: str
    
    # References
    curriculum_template_id: str
    skills_referenced: List[str]
    
    # Stats
    total_sections: int
    completed_sections: int
    completion_percentage: float
    total_time_minutes: int
    mastery_average: float
```

### API Endpoints

**Curriculum CRUD:**
- `GET /polly/curricula/list?status=active`
- `GET /polly/curricula/{id}`
- `POST /polly/curricula/create`
- `POST /polly/curricula/{id}/activate`
- `DELETE /polly/curricula/{id}`

**Section Operations:**
- `POST /polly/curricula/{id}/sections/{section}/start`
- `POST /polly/curricula/{id}/sections/{section}/complete`
- `POST /polly/curricula/{id}/sections/{section}/enrich`
- `GET /polly/curricula/{id}/progress`

**Session Management:**
- `POST /polly/curricula/{id}/session/start?section_id={section}`
- `POST /polly/curricula/session/end`

**Templates:**
- `GET /polly/templates/list`
- `GET /polly/templates/{id}`
- `POST /polly/templates/detect` (body: {goal: "..."})
- `POST /polly/templates/{id}/customize`

### File Organization

**Backend:**
```
core/
├── learners/
│   ├── curriculum_manager.py          # Phase 1
│   └── curriculum_template_manager.py # Phase 2

vault/.polly/
├── curricula/                          # Phase 1
│   └── {curriculum-id}/
│       ├── CURRICULUM.md
│       ├── curriculum.json
│       ├── progress.json
│       └── resources/
│
└── curriculum-templates/               # Phase 2
    ├── programming-language/
    ├── framework-library/
    ├── skill-acquisition/
    ├── problem-solving/
    └── domain-exploration/
```

**Frontend:**
- Enhance Learning page with curriculum UI
- Add curriculum review dialog
- Add session indicator
- Add curriculum detail view (week/section tree)

---

## Implementation Strategy

### Phased Approach

**Phase 1: Core Infrastructure** (4-6 hours)
- Backend: CurriculumManager class
- API endpoints (CRUD, sections, progress)
- Basic frontend functions
- Testing: Create/load/save curricula

**Phase 2: Template System** (3-4 hours)
- CurriculumTemplateManager class
- 5 domain templates
- Auto-detection logic in Professor
- Template customization
- Testing: Detect correct template, customize

**Phase 3: Creation & Review Flow** (3-4 hours)
- Professor curriculum generation (with templates)
- Review dialog UI
- Markdown parser
- Save flow
- Testing: End-to-end curriculum creation

**Phase 4: Section Enrichment** (4-5 hours)
- Professor enrichment method
- Heavy enrichment (diagrams, examples, exercises)
- Skill package integration
- Display enriched materials
- Testing: Enrichment generation and display

**Phase 5: Progress Tracking & UI** (5-6 hours)
- Curriculum list view
- Curriculum detail view (week/section tree)
- Progress bars and stats
- Completion flow with reflection
- Testing: Visual progress tracking

**Phase 6: Guided Learning** (3-4 hours)
- Session management in Professor
- Session indicator UI
- Ambient awareness
- Context-aware responses
- Testing: Session flow, ambient context

**Total:** 20-28 hours

### MVP vs. Full System

**MVP (Phases 1-4):** ~15-20 hours
- Can create curricula with templates
- Can enrich sections with materials
- Basic progress tracking
- **Gets core value proposition working**

**Full System (Phases 1-6):** ~20-28 hours
- All above +
- Visual curriculum UI
- Session management
- Ambient awareness
- **Complete polished experience**

---

## User Experience Examples

### Example 1: Learning Monome Norns (Skill Acquisition Template)

**Creation:**
```
User: "Create a learning plan for Monome Norns scripting"

Professor: "Great! Norns is a creative platform. I'll use the 
Skill Acquisition template. Let me customize it for you:

- What's your Lua experience? [Beginner/Intermediate/Advanced]
- What's your audio/synthesis background?
- What do you want to create on Norns?
- Do you have a Norns device already?"

User: "Beginner Lua, some audio background, want to make generative 
music, yes I have a Norns."

Professor: [Generates outline]

[Review dialog appears]
Left: Editable markdown outline
Right: Preview
  - Title: Programming Monome Norns Scripts
  - Goal: Build custom audio processing scripts
  - Duration: 8 weeks
  - 16 sections
  - Structure tree showing Week 1-8

User: [Reviews, looks good]
User: [Clicks "Save & Activate"]

Notification: "Curriculum created! Ready to start Week 1?"
```

**Following:**
```
[Learning page]
Sidebar: "Active Curricula"
  - Monome Norns (0% complete)

[User clicks card]

Curriculum Detail View:
  Progress: 0/16 sections (0%)
  
  Week 1: Norns Fundamentals (0/3)
    ⭕ 1.1 Platform Overview (2 hours)
    ⭕ 1.2 Setup Environment (1 hour)
    ⭕ 1.3 Basic Script Structure (2 hours)
  
  Week 2: Audio Engine Basics (0/4)
    ...

[User clicks "1.1 Platform Overview"]

[Loading: "Enriching section with materials..." ~15s]

[Session view displays:]

📚 Learning: Week 1.1 (Session Active) [End Session]

# Week 1.1: Platform Overview

## What You'll Learn
- Norns architecture (SuperCollider + Lua)
- Hardware capabilities
- Development workflow

## Understanding Norns

[Detailed explanation...]

## Visual Guide

[Diagram: Norns Architecture]
┌─────────────┐
│   Scripts   │ (Lua)
└──────┬──────┘
       │
┌──────┴──────┐
│   Engine    │ (SuperCollider)
└──────┬──────┘
       │
┌──────┴──────┐
│   Hardware  │
└─────────────┘

## Examples

Example 1: Hello Norns
```lua
function init()
  print("Hello Norns!")
end
```

[2 more examples...]

## Practice Exercises

1. **Explore maiden:** Connect to your Norns and...
2. **Modify hello world:** Change the script to...
3. **Analyze existing script:** Load awake.lua and...

## You've Mastered This When You Can:
- Explain Norns architecture to someone else
- Navigate maiden IDE confidently
- Load and run existing Norns scripts

[Mark Complete]

[User works through materials]

[User clicks "Mark Complete"]

Prompt:
  How well did you master this section? [1-5]: 3
  What was challenging? (optional): SuperCollider concepts unclear
  Any breakthroughs? (optional): Understood the Lua/SC split

[Saves progress]

Notification: "Week 1.1 complete! 🎉
Continue to Week 1.2: Setup Environment? [Yes] [No]"
```

### Example 2: Ambient Awareness

```
[User in normal chat, not in curriculum session]
[Active curriculum: React Mastery (Week 2)]

User: "How do I optimize React component rendering?"

Professor: "(This relates to your React Mastery curriculum - 
you're on Week 2, and performance optimization is coming in Week 4. 
Here's a preview...)

There are several strategies..."

[No interruption to curriculum progress, just helpful context]
```

---

## Integration Points

### With Existing Systems

**Phase 11 (Multi-Model Routing):**
- Enrichment uses THOROUGH confidence → best model
- Quality is critical for learning materials
- Budget-aware (enrichment is expensive operation)

**Phase 14 (Mental Models):**
- Could activate teaching mode mental model during curriculum sessions
- Mental models guide Professor's pedagogical approach
- User's mental models could inform curriculum customization

**Phase 16 (Native Notes):**
- Curricula stored in vault (parallel to notes)
- Section resources can link to notes via wikilinks
- Learning notes created during curriculum can reference sections

**Phase 21 (Deduplication):**
- Detect similar curricula before creating
- Suggest appending to existing vs. creating new
- Prevent knowledge fragmentation

**Phase 22 (Teaching Mode):**
- Teaching mode mental model during curriculum sessions
- Socratic questioning in enrichment
- Progressive difficulty adjustment
- Learning tracker integration

### With Future Systems

**Phase 12 (Knowledge Graph):**
- Curriculum sections as graph nodes
- Visualize learning paths
- Concept dependency mapping
- "Explore from here" suggestions

**Phase 23b (Custom Templates):**
- Save curriculum as template
- Share templates with community
- Import/export functionality

---

## Open Questions & Considerations

### 1. Enrichment Cost
**Q:** Heavy enrichment uses expensive models. How to manage cost?

**Options:**
- Set budget limits per curriculum
- Show estimated cost before enrichment
- Tiered enrichment (light/medium/heavy)
- Cache aggressively (we chose this)

### 2. Template Detection Accuracy
**Q:** What if auto-detection picks wrong template?

**Solution:** Show "recommended" label, allow override
**Fallback:** User can always manually select template

### 3. Non-Linear Learning
**Q:** What if user wants to jump around, not follow linear path?

**Solution:** Allow clicking any section
**Track:** Mark curriculum as "non-linear" in metadata
**Adapt:** Don't enforce prerequisites (trust user)

### 4. Curriculum Completion
**Q:** What happens when curriculum is 100% complete?

**Options:**
- Move to "completed" status
- Suggest related curricula
- Offer to create "advanced" follow-up curriculum
- Archive to keep stats but remove from active list

### 5. Collaborative Learning
**Q:** Should users be able to share curricula?

**Decision:** Defer to Phase 23b (future enhancement)
**Rationale:** Focus on individual learning first, add collaboration later

---

## Success Metrics

### Quantitative
- Time to create curriculum: < 2 minutes
- Section enrichment time: 10-30 seconds
- User completes at least 1 section per week (engagement)
- Average curriculum completion rate > 60%
- User creates at least 3 curricula (demonstrates value)

### Qualitative
- Users report feeling "guided" rather than "lost"
- Review dialog feels intuitive
- Progress tracking is motivating
- Enrichment quality is high (useful diagrams/examples)
- Session mode feels focused
- Ambient mode is helpful not annoying

---

## Risks & Mitigations

### Risk 1: Enrichment Quality Varies
**Problem:** LLM-generated content may be inconsistent

**Mitigations:**
- Use THOROUGH confidence (best models)
- Provide detailed enrichment prompts
- Include skill package content when available
- Allow user to re-generate enrichment
- Future: User can edit enriched content

### Risk 2: Template Limitations
**Problem:** 5 templates may not cover all learning scenarios

**Mitigations:**
- Templates are flexible (adapt to topic)
- User can edit generated outline
- Phase 23b adds custom templates
- Can always request changes from Professor

### Risk 3: User Abandonment
**Problem:** Users create curricula but don't follow through

**Mitigations:**
- Visible progress tracking (motivating)
- Spaced repetition reminders (from Phase 22)
- Achievable section sizes (1-3 hours each)
- Session mode creates focused learning time
- Next-section suggestions reduce friction

### Risk 4: Loading Time Frustration
**Problem:** 10-30s enrichment may feel slow

**Mitigations:**
- Clear loading indicators
- Show what's being generated
- Cache aggressively (one-time cost)
- Allow browsing other sections while loading
- Future: Pre-enrich next section in background

---

## Future Vision

### Phase 23 Establishes Foundation For:

**Personalized Learning Paths:**
- AI-powered curriculum recommendations
- Adaptive difficulty based on performance
- Prerequisite detection and auto-adjustment

**Collaborative Learning:**
- Share curricula with community
- Collaborative progress tracking
- Group learning sessions

**Advanced Features:**
- Voice-guided learning sessions
- Interactive exercises with live feedback
- Integration with external learning platforms
- Certification/credentials for completed curricula

**Analytics:**
- Learning velocity tracking
- Concept mastery heatmaps
- Optimal learning time recommendations
- Struggle pattern analysis

---

## Conclusion

Phase 23 transforms Polly from a tool that generates learning outlines into a complete curriculum learning system. It bridges the gap between chat-based outline generation and structured, guided learning experiences.

**Key Innovations:**
1. Domain-based templates (not topic-specific)
2. Hybrid smart enrichment (on-demand, heavy, cached)
3. Review/edit workflow before saving
4. Subheading-level progress tracking
5. Sessions + ambient learning flow

**User Value:**
- Structure: Clear path from beginner to mastery
- Guidance: Professor actively guides each step
- Progress: Visual tracking shows growth
- Depth: Heavy enrichment provides real understanding
- Flexibility: Linear or exploratory learning

**Technical Excellence:**
- Clean separation of concerns (Manager classes)
- Extensible template system
- Rich API for future features
- Integration with existing systems (Personas, Mental Models, Notes)

**Timeline:** 20-28 hours to full implementation

---

**Document Status:** Complete  
**Next Step:** Begin Phase 1 implementation (Core Infrastructure)

**References:**
- Main planning doc: `PHASE23_CURRICULUM_SYSTEM.md`
- Related: `PHASE22_TEACHING_MODE.md` (already implemented)
- Integration: Phase 11, 14, 16, 21, 22

---

**Session Participants:** Development Team  
**Date:** February 2, 2026  
**Duration:** Comprehensive planning session  
**Outcome:** Complete technical specification ready for implementation
