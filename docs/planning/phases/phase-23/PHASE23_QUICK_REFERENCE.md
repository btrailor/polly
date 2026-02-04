# Phase 23: Curriculum Learning System - Quick Reference

**Status:** Planning Complete  
**Priority:** High  
**Estimated:** 20-28 hours (MVP: 15-20 hours)

---

## One-Line Summary

Transform Polly's learning system from chat-based outline generation to complete structured curriculum with templates, enrichment, progress tracking, and guided learning.

---

## The Problem

**Current:** Professor generates learning outlines in chat, but they're just text. No structure, tracking, enrichment, or guidance.

**Solution:** Complete curriculum system with:
- Structured storage in vault
- Domain-based templates
- Heavy enrichment (diagrams, examples, exercises)
- Progress tracking per section
- Session + ambient learning modes

---

## Key Decisions

| Topic | Decision |
|-------|----------|
| **Storage** | `vault/.polly/curricula/` (separate from notes) |
| **Templates** | 5 domain-based (not topic-specific) |
| **Enrichment** | Hybrid smart (on-demand, heavy, cached) |
| **Tracking** | Subheading-level (week-1.1, week-1.2, etc.) |
| **Learning Flow** | Sessions + ambient awareness |
| **Creation** | Review/edit dialog before saving |

---

## 5 Domain Templates

1. **Programming Language** - Any language (Python, JS, Lua, etc.)
2. **Framework/Library** - Any framework (React, Flask, etc.)
3. **Skill Acquisition** - Tools/platforms (Norns, Ableton, etc.)
4. **Problem-Solving** - Specific problems (optimize API, etc.)
5. **Domain Exploration** - Broad domains (ML, Audio DSP, etc.)

**Why domain-based?** One template adapts to many topics. Avoids maintaining hundreds of templates.

---

## Implementation Phases

| Phase | Goal | Hours |
|-------|------|-------|
| **1. Core Infrastructure** | Backend object model, API, storage | 4-6 |
| **2. Template System** | 5 templates, auto-detection | 3-4 |
| **3. Creation & Review** | Generate outline → review dialog → save | 3-4 |
| **4. Section Enrichment** | Heavy enrichment on section start | 4-5 |
| **5. Progress UI** | Visual curriculum UI, progress bars | 5-6 |
| **6. Guided Learning** | Sessions + ambient awareness | 3-4 |
| **TOTAL** | | **20-28** |

**MVP (Phases 1-4):** 15-20 hours - Core functionality working

---

## User Flow Example

### Creation
1. User: "Create a learning plan for React"
2. Professor detects → framework-library template (recommended)
3. Professor asks customization questions
4. Generates outline (8 weeks, 16 sections)
5. **Review dialog appears** (left: editable, right: preview)
6. User edits or asks for changes
7. User clicks "Save & Activate"
8. Curriculum created in `vault/.polly/curricula/react-mastery/`

### Following
1. User opens Learning page → sees "React Mastery" (0% complete)
2. Clicks → Curriculum detail view (week/section tree)
3. Clicks "Week 1.1: React Basics"
4. Loading: "Enriching section..." (~15s)
5. **Session view displays:**
   - Explanation
   - Diagram
   - 3 examples
   - 4 exercises
   - Assessment criteria
6. User works through materials
7. User clicks "Mark Complete"
8. Prompt: mastery (1-5), struggles, breakthroughs
9. Progress saved
10. "Continue to Week 1.2?"

---

## Data Models

### Curriculum
- **Metadata:** id, title, goal, status, created, updated
- **Structure:** sections[], current_section_id
- **Progress:** completion_%, total_time, mastery_avg
- **References:** template_id, skills_referenced

### CurriculumSection
- **Identity:** id (week-1.1), title, type, order, parent_id
- **Content:** description, concepts[], estimated_time
- **Enrichment:** resources[], exercises[], diagrams[], examples[]
- **Progress:** status, timestamps, time_spent, mastery, struggles, breakthroughs

---

## API Endpoints

### Curriculum
- `GET /polly/curricula/list?status=active`
- `GET /polly/curricula/{id}`
- `POST /polly/curricula/create`
- `POST /polly/curricula/{id}/activate`

### Sections
- `POST /curricula/{id}/sections/{section}/start`
- `POST /curricula/{id}/sections/{section}/complete`
- `POST /curricula/{id}/sections/{section}/enrich`

### Sessions
- `POST /curricula/{id}/session/start?section_id={section}`
- `POST /curricula/session/end`

### Templates
- `GET /polly/templates/list`
- `POST /polly/templates/detect` (auto-detect from goal)
- `POST /polly/templates/{id}/customize`

---

## Files Created

### Backend
```
learners/
├── curriculum_manager.py          (~600 lines)
└── curriculum_template_manager.py (~300 lines)

vault/.polly/
├── curricula/{id}/
│   ├── CURRICULUM.md
│   ├── curriculum.json
│   ├── progress.json
│   └── resources/
│
└── curriculum-templates/
    ├── programming-language/
    ├── framework-library/
    ├── skill-acquisition/
    ├── problem-solving/
    └── domain-exploration/
```

### Frontend
- Enhanced Learning page (curriculum list, detail view)
- Curriculum review dialog
- Session indicator
- Progress visualization

---

## Success Criteria

### Functional
✅ Create curriculum with template in < 2 minutes  
✅ Review/edit before saving  
✅ Section enrichment in 10-30s  
✅ Subheading-level progress tracking  
✅ Visual progress bars and stats  
✅ Session mode with indicator  
✅ Ambient awareness contextualizes responses  

### UX
✅ Creation feels guided and easy  
✅ Enrichment loading feels polished  
✅ Progress tracking is motivating  
✅ Session mode feels focused  
✅ Ambient mode is helpful not intrusive  

---

## Integration Points

- **Phase 11:** Router selects best model for enrichment
- **Phase 14:** Mental models could guide curriculum pedagogy
- **Phase 16:** Curricula stored in vault, link to notes
- **Phase 21:** Deduplication prevents duplicate curricula
- **Phase 22:** Teaching mode during curriculum sessions
- **Phase 12 (future):** Curriculum sections in knowledge graph

---

## Next Steps

1. **Review planning docs** with team
2. **Confirm design decisions** (all questions answered above)
3. **Start Phase 1:** Core Infrastructure
4. **Build iteratively** through phases 1-6
5. **Test at each phase** before moving forward

---

## Documentation

- **Main Spec:** `PHASE23_CURRICULUM_SYSTEM.md` (30 pages, comprehensive)
- **Planning Session:** `PHASE23_PLANNING_SESSION.md` (detailed design discussion)
- **This File:** Quick reference for implementation

---

**Created:** February 2, 2026  
**Status:** Planning complete, ready to implement  
**Team:** Development Team
