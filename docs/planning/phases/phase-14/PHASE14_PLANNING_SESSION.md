# Phase 14: Mental Models - Planning Session Summary

**Date:** January 29, 2026  
**Duration:** ~3 hours  
**Status:** Planning Complete → Ready for Implementation  

---

## Session Overview

Conducted comprehensive planning session for Phase 14: Mental Models System. Original spec called for 5 models with basic activation. After deep design discussions, we evolved the spec significantly to create a more powerful, future-proof system.

---

## Key Design Decisions Made

### 1. Three-Tier Activation System

**Decision:** Implement three-tier context-aware activation (Domain + Page + Persona)

**Rationale:**
- User insight: "I want mental models to be called per Domain, but also per mode (page) that the user is working in, and per persona (architect, teacher, etc.)"
- Page-level provides strongest signal (user is actively in that workspace)
- Persona-level captures explicit AI behavior mode
- Domain-level maintains content-based matching

**Scoring:**
- Page match: +10 points (strongest)
- Persona/mode match: +8 points
- Category trigger: +5 points
- Domain match: +3 points
- Keyword match: +2 per keyword

**Alternative Considered:** Two-tier (domain + keyword only)  
**Why Rejected:** Missed critical context about where user is working and what AI mode is active

---

### 2. Unified PIL Compression

**Decision:** Create Polly Internal Language (PIL) format extending existing conversation compressor

**Rationale:**
- User preference: "Use a shorthand like Polly internal language, custom designed for ultra efficient routing"
- Achievable 2.5-3x compression ratio (conservative vs original 5-10x goal)
- Consistent with existing compression architecture
- Symbol system preserves semantic meaning compactly

**Format:**
```
MM:id|m:mode|p:[principles]|pi:prompt|d:[domains]|pg:[pages]|ps:[personas]|pm:[modes]|k:[keywords]
```

**Symbols:** `>` (over), `↻` (evolving), `↑` (increase), `→` (leads to), `⇄` (mutual), `?` (question), `!` (emphasis)

**Alternative Considered:** No compression, store full YAML in context  
**Why Rejected:** Token bloat, inefficient for conversation context

---

### 3. Expand to 12 Default Models

**Decision:** Ship with 12 models across 4 tiers (vs original 5)

**Rationale:**
- User: "I think we need all of those models"
- Covers broader use cases (philosophy, learning, systems, communication)
- Future-proof: 3 models for Phase 20 (Mail/Calendar) even though not built yet
- No significant implementation cost (just YAML data)

**4 Tiers:**
1. Core Philosophy (3): Infinite Games, Instruments Over Tracks, Constraint as Meaning
2. Learning & Thinking (3): Freire, Reverse Engineering, Socratic Method
3. Systems & Technical (3): Systems Thinking, First Principles, Design Thinking
4. Communication (3): Inbox Zero, Async-First, Time Blocking

**Alternative Considered:** Start with 5, add more later  
**Why Rejected:** No benefit to deferring, data is cheap, users benefit immediately

---

### 4. Template + Customize Creation Flow

**Decision:** Provide 6 high-quality templates with inline help text

**Rationale:**
- Lowers barrier to entry for creating custom models
- Guides users toward well-structured models
- Blank option available for power users
- Inline help prevents confusion

**6 Templates:**
1. Blank - Start from scratch
2. Learning Framework
3. Creative Process
4. Productivity System
5. Systems Approach
6. Communication Style

**Alternative Considered:** Blank form only  
**Why Rejected:** Too intimidating, users wouldn't know what to write

---

### 5. Hybrid Activation (Base + Dynamic)

**Decision:** Start with static base models, support dynamic re-evaluation in future

**Rationale:**
- User insight: "Real-world: user shifts topics mid-conversation"
- Base models (3-5) loaded at session start
- Can re-evaluate per query or every N exchanges (implementation choice)
- Handles topic drift without over-complicating

**Implementation for Phase 14:**
- Load top 3-5 models per query based on context
- Store compressed in system prompt
- Dynamic re-evaluation can be added later if needed

**Alternative Considered:** Static only (load once per session)  
**Why Rejected:** Misses topic shifts, but can be revisited if performance issues

---

### 6. Future-Proof Schema Design

**Decision:** Include page/persona fields even for features not yet built

**Rationale:**
- User: "We should design for Phase 20 and Phase 22 even though they're not built"
- Models like Inbox Zero, Time Blocking work when Mail/Calendar built
- Teacher persona models work when Phase 22 Teaching Mode built
- Zero refactoring needed later

**Future Integrations:**
- Phase 20a (Mail): Inbox Zero, Async-First auto-activate
- Phase 20b (Calendar): Time Blocking auto-activates
- Phase 22 (Teaching Mode): Freire, Socratic, Reverse Engineering auto-activate

**Alternative Considered:** Simple schema now, extend later  
**Why Rejected:** Would require migration, breaking changes

---

## What We Researched

### Polly's Architecture Discovery

To support three-tier activation, we researched:

**12 Pages/Views:**
- dashboard, calendar, mail, code, projects, knowledge, notes, learning, search, patterns, domains, settings
- Found in `electron-app/src/renderer/index.html` lines 41-91

**Agent Personas (Phase 11):**
- Architect: plan/build modes (Phase 11c, 16c)
- Teacher: socratic/guide modes (Phase 22)
- Librarian: organize/link/summarize (future)
- Critic: review/suggest/validate (future)

**5 User Domains (Phase 1.5):**
- Sigils (code), Signals (audio), Scrolls (writing), Glyphs (design), Grids (systems)
- User-configurable

---

## Implementation Plan Created

**Document:** `PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md` (77 KB, ~2,000 lines)

**Contents:**
1. Complete schema specification with three-tier fields
2. PIL compression system with symbol definitions
3. All 12 default models in full YAML format
4. Three-tier activation logic with scoring examples
5. Day-by-day breakdown (5 days, 8 hours each)
6. Success criteria checklist
7. Files to create/modify (~2,400 lines of code)
8. Risk assessment and mitigation
9. Future enhancement paths

---

## Files to be Created/Modified

### New Files (~1,250 lines)

1. `/core/mental_models.py` (500 lines) - Core manager, dataclass, activation logic
2. `~/.polly/mental_models.yaml` (400 lines) - All 12 default models
3. `tests/test_mental_models.py` (200 lines) - Unit tests for manager
4. `tests/test_mental_model_compression.py` (150 lines) - PIL compression tests

### Modified Files (~1,150 lines)

1. `/core/compression/compressor.py` (+190 lines) - PIL compression methods
2. `/core/polly.py` (+150 lines) - Integration, system prompt building
3. `/interfaces/server.py` (+150 lines) - 7 REST API endpoints
4. `/electron-app/src/renderer/index.html` (+250 lines) - Settings UI, modal, context menu
5. `/electron-app/src/renderer/app.js` (+400 lines) - UI logic, templates, CRUD
6. `/electron-app/src/renderer/styles/main.css` (+150 lines) - Styling
7. `config.yaml` (+5 lines) - Add mental_models config

### Documentation Updates

1. `PHASE14_MENTAL_MODELS.md` - Updated status and summary
2. `MASTER_ROADMAP.md` - Updated Phase 14 section with enhanced features
3. `PHASE14_MENTAL_MODELS_IMPLEMENTATION_PLAN.md` - NEW comprehensive spec
4. `PHASE14_PLANNING_SESSION.md` - NEW this document

**Total New/Modified:** ~2,400 lines of code

---

## Timeline

**Estimated Effort:** 5 days (8 hours/day = 40 hours)

**Daily Breakdown:**
- Day 1: Core system (MentalModelManager) + PIL compression (8h)
- Day 2: Polly integration + REST API endpoints (8h)
- Day 3: Settings UI with three-tier fields + templates (8h)
- Day 4: Per-conversation override + active model indicator (8h)
- Day 5: Integration testing + documentation (8h)

---

## Success Criteria

### Core Functionality
- ✅ Mental models stored in `~/.polly/mental_models.yaml`
- ✅ 12 default models included and load correctly
- ✅ Three-tier activation works (domain + page + persona)
- ✅ Unified PIL compression achieves ≥2.5x ratio
- ✅ Models visible in Settings UI
- ✅ Can create/edit/delete models via UI
- ✅ Template system helps users create models
- ✅ Models automatically applied based on context
- ✅ Keyword matching triggers relevant models
- ✅ System prompt includes compressed models
- ✅ Per-conversation model override works
- ✅ Category-based auto-activation works

### Quality Standards
- ✅ All CRUD operations reliable
- ✅ No performance impact (<5ms per query)
- ✅ Responses reflect mental model principles
- ✅ UI intuitive and well-documented
- ✅ Error handling prevents invalid models
- ✅ Future-proof: Works with Pages/Personas not yet built

---

## Key Insights from Planning Session

### User's Design Philosophy

**Universal Solutions Over Quick Fixes:**
- "We learned from cross-domain RAG work to design universal solutions"
- "Don't botch important features - take time to plan properly"
- "I'm willing to spend 3+ hours planning if it means better design"

**Compression-First Mindset:**
- "Use a shorthand like Polly internal language"
- "Custom designed for ultra efficient routing"
- Target efficiency even when not strictly necessary

**Future-Proof Thinking:**
- "Design for Phase 20 and Phase 22 even though they're not built"
- "Three-tier system should work for features not yet implemented"
- "Schema should scale to new contexts"

---

## Risks Identified & Mitigation

### Technical Risks

**Risk:** Compression ratio lower than expected  
**Mitigation:** Conservative 2.5x target (vs ambitious 5-10x), still valuable

**Risk:** Three-tier activation too complex  
**Mitigation:** Simple scoring system, can simplify to two-tier if needed

**Risk:** Performance impact on query  
**Mitigation:** Pre-compress models at load time, not per-query

### Implementation Risks

**Risk:** Day estimates too optimistic  
**Mitigation:** Buffer built into each day, Day 5 is polish/testing

**Risk:** Integration breaks existing code  
**Mitigation:** Extensive testing, small incremental changes

### UX Risks

**Risk:** Users don't understand activation  
**Mitigation:** Clear inline help, examples, "Why did this activate?" tooltip

**Risk:** Too many models active at once  
**Mitigation:** Limit to top 5, clear ranking in UI

---

## Next Steps

**Immediate:**
1. ✅ Document planning session (this file)
2. ✅ Update `PHASE14_MENTAL_MODELS.md` status
3. ✅ Update `MASTER_ROADMAP.md`
4. ⏭️ **BEGIN DAY 1 IMPLEMENTATION**

**Day 1 Tasks:**
- Create `/core/mental_models.py` with MentalModel dataclass
- Implement MentalModelManager with three-tier activation
- Implement get_models_for_context() with scoring
- Create all 12 default models
- Extend `/core/compression/compressor.py` with PIL compression
- Write unit tests

**Ready to implement!**

---

## Planning Session Participants

- **User (Brett):** Product owner, design decisions, requirements
- **AI (OpenCode):** Technical architecture, implementation planning, documentation

**Session Duration:** ~3 hours  
**Documents Produced:** 3 (Implementation Plan, this Planning Summary, updates to existing docs)  
**Lines of Planning Documentation:** ~2,500 lines  
**Code Ready to Write:** ~2,400 lines  

---

## Appendix: Design Alternatives Not Chosen

### Storage Format
- **SQLite database** - Rejected: Overkill for small dataset, less portable
- **Individual YAML files per model** - Rejected: Complex management, no clear benefit
- **JSON format** - Rejected: Less human-readable than YAML

### Activation Strategy
- **Manual only** - Rejected: Too much user friction
- **Fully automatic (no override)** - Rejected: Users want control
- **Global enable/disable only** - Rejected: Not granular enough

### Compression Approach
- **No compression** - Rejected: Token bloat in context
- **Generic text compression (gzip)** - Rejected: Not LLM-friendly
- **Embedding-based semantic compression** - Deferred: Too complex for Phase 14, good for Phase 14.5

### UI Approach
- **Code editor for YAML** - Rejected: Too technical for average user
- **No templates** - Rejected: Too intimidating
- **AI-assisted creation** - Deferred: Good for future, not MVP

---

**Planning Session Complete - Ready for Implementation**
