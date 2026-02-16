# Teaching & Learning (OpenSpec)

Source of truth for teaching mode, learning tracking (Phase 22), and meta-pedagogy (how Polly teaches users to use Polly). Detail: [docs/planning/phases/phase-22/](../../../docs/planning/phases/phase-22/).

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| LearningTracker, Socratic mode, learning notes | ✅ Implemented | `learners/learning_tracker.py` |
| Professor curriculum generation, section enrichment | ✅ Implemented | Phase 23 |
| Backend API (mode switch, analytics) | ✅ Implemented | interfaces/server.py |
| Learning page center area (Active Session, Curriculum View, Review) | 📐 Partial | ~40% frontend; learning-and-administrator-profiles |
| Meta-pedagogy (prompt injectors, competency tracking) | 💭 Vision | learning-and-administrator-profiles change |

## Current Behavior

- **LearningTracker:** `learners/learning_tracker.py`. Tracks topics, mastery levels (1–5), spaced repetition, learning notes. Storage and API for mode switching and analytics.
- **Professor Socratic mode:** Questioning framework; learning note creation with structured templates. Mode switch via `POST /persona/switch-mode`.
- **Backend:** 100% complete. Frontend: ~40% — mode switcher UI, learning dashboard (topics, mastery, stats), learning note prompts/preview, and visual mode indicators pending. Overall phase ~75% complete; 1–2 days to finish UI.

---

## Learning Page Center Area

The Learning page center area is the **active learning surface** — not an analytics dashboard. Analytics serve reflection, not center-stage display.

### Center-Area States

| State | What | When Active |
|-------|------|-------------|
| **Active Session** | Full-width conversation with Professor in current mode (Explain, Socratic, Curriculum, Quiz). Minimal chrome. | Default when a learning session is in progress |
| **Curriculum View** | Learning path as navigable map — position, upcoming topics, connections. Knowledge graph filtered through pedagogical lens. | Default when no session active but curriculum exists |
| **Practice Space** | Embedded workspace for practice domains. Professor observes and coaches. | When user is in practice-oriented domain + learning mode |
| **Review** | Analytics: study history, competency progression, spaced repetition schedule, knowledge gaps. | When user navigates to Review tab |

**Default:** Active Session → Curriculum View → empty state. Analytics accessible via Review tab.

**Design principle:** Problem-posing over banking (Freire). The tool communicates "your learning interaction is what matters," not "tracking your learning is what matters."

---

## Meta-Pedagogy: How Polly Teaches You to Use Polly

Polly doesn't just serve as a learning tool — it teaches users how to collaborate with AI more effectively. This builds transferable thinking skills, not Polly-dependence.

### The Design Tension

| Approach A: Skill Building | Approach B: Tool Design |
|---------------------------|------------------------|
| Teach user to prompt better | Make prompting unnecessary |
| Progressive independence | Inference from minimal input |
| Transferable skills | Invisible intelligence |

**Resolution:** Both, sequenced. New users get (A) — scaffolding shows what's happening and why. As competency grows, scaffolding fades and (B) takes over. Polly becomes invisible as you learn to work with it.

### Prompt Injector System

Persona-specific teaching moments activate when a user's prompt could be improved. Not error messages — brief, contextual coaching.

**Components:**
1. **Pattern detection** — Recognize improvable prompts before routing (vague requests, missing context, wrong persona, outcome-missing)
2. **Coaching response** — 1–2 sentences max. Framed as "better results" not "wrong prompt"
3. **Competency tracking** — Track which skills the user has internalized per persona

**Per-persona examples:**
- **Professor:** "Tell me what you're trying to accomplish with Docker — that helps me tailor the explanation."
- **Programmer:** "For faster debugging, include: expected behavior, actual behavior, error messages."
- **Designer:** "Design works best with constraints — what style, size, and context?"
- **Architect:** "What are the main entities, common queries, and expected scale?"

### Competency Tracking

Per-persona, per-skill tracking. Five levels:

| Level | Name | Behavior |
|-------|------|----------|
| 0 | Not encountered | Waiting for first trigger |
| 1 | Introduced | First coaching delivered |
| 2 | Reminded | Second coaching — briefer |
| 3 | Competent | No longer coached |
| 4 | Expert | User's corrections improve Polly's defaults |

**Storage:** `_polly/user/prompting-competency.yml`  
**Progression:** Competency increases when user demonstrates skill unprompted. Detected by reverse pattern analysis.

### Progressive Scaffolding Fade

```
New user → Full explanation (show routing, explain persona)
         → Brief reminder (second time)
         → Assume competence (minimal explanation)
         → Invisible operation (surface only when unexpected)
```

This mirrors the progression signals model used throughout Polly. Connects to onboarding spec's "tutorials fade as competency grows." See [onboarding spec](../onboarding/spec.md).

### What Prompt Coaching Really Teaches

The coaching isn't about prompts — it's about thinking:
- Articulating goals before jumping to execution (reverse engineering)
- Specifying constraints as generative rather than restrictive (Bogost)
- Understanding which kind of help you need (delegation vs. learning)
- Recognizing explore mode vs. exploit mode
- Examining who benefits from a narrative (constitutional: cui bono)
- Distinguishing structural causes from essentialist claims (constitutional: material analysis)
- Recognizing scapegoat patterns (constitutional: scapegoat suspicion)

These are transferable skills. Problem-posing, not banking.

### Inoculation Pedagogy

Connected to the constitutional epistemology layer. Polly teaches *about* harmful ideologies to build resistance, not hides them to create fragility. A user who understands *how* fascist recruitment works — what emotional needs it exploits (belonging, purpose, grievance validation), what material conditions it feeds on (economic precarity, social isolation), and whose interests it serves — is far more resistant than one who's simply been told it's bad.

This is quarantine vs. inoculation:
- **Quarantine:** Hide dangerous ideas. Creates fragility. Doesn't build analytical capacity.
- **Inoculation:** Explain how dangerous ideas work — their construction, their appeals, their failure points. Builds durable resistance.

Professor persona can teach critical analysis of propaganda, media framing, and recruitment patterns as a natural extension of its pedagogical mission. This isn't a special mode — it's what good education does.

See [ethics spec](../ethics/spec.md) for the full constitutional epistemology system.

---

## Deferred Enhancements

### Critical Consciousness as Teachable Skills

**Status:** DEFERRED to Phase 22 meta-pedagogy implementation  
**Cross-reference:** [ethics spec](../ethics/spec.md) — Constitutional Epistemology  
**Implemented:** February 15, 2026 — Constitutional layer is active in all system prompts

When implementing meta-pedagogy (Wave 2 of learning-and-administrator-profiles), add constitutional critical consciousness as explicit teachable skills:

**What to implement:**
1. **Four constitutional thinking skills** with 5-level progression (0-4):
   - **Cui Bono Analysis** — Learning to ask "who benefits from this framing?"
   - **Scapegoat Pattern Recognition** — Identifying when blame is misdirected to outgroups
   - **Historical Construction Analysis** — Seeing how ideas were constructed over time
   - **Structural vs Essentialist Thinking** — Distinguishing systems from group qualities

2. **Competency tracking** — Extend learning tracker with:
   ```python
   constitutional_competency = {
       "cui_bono_analysis": 2,  # Level 0-4
       "scapegoat_recognition": 1,
       "historical_construction": 3,
       "structural_vs_essentialist": 2
   }
   ```

3. **Professor persona teaching methods:**
   - Socratic questioning that develops constitutional consciousness
   - Inoculation pedagogy: teach ABOUT harmful ideologies analytically
   - Examples from user's knowledge base
   - Progressive scaffolding that fades as competency grows

4. **Skill progression indicators** in Learning page Review tab:
   - Track growth in constitutional thinking skills
   - Suggest practice opportunities
   - Celebrate milestones (e.g., "You're now independently applying cui bono!")

**Implementation location:**
- `core/pedagogy/constitutional_skills.py` — Skill definitions with level progressions
- `core/personas/implementations/professor.py` — Teaching methods for constitutional skills
- Extend `LearningTracker` with constitutional competency fields
- Learning page UI for skill progression display

**Why deferred:**
Constitutional epistemology is implemented and active (February 2026). Making it explicitly teachable makes most sense when:
1. Meta-pedagogy infrastructure is built (prompt coaching, competency tracking)
2. Professor persona is actively used for teaching
3. Learning page has Review tab for progression display

The constitutional layer already shapes all of Polly's analysis. This enhancement would make those analytical moves explicitly teachable as transferable thinking skills.

**Reference:**
- Constitutional principles: `core/constitutional/principles.py`
- Constitutional layer prompt: `core/constitutional/layer.py`
- Implementation discussion: Development log, February 15, 2026

---

## Implementation

- **Backend:** `core/pedagogy/prompt_coach.py`, `core/pedagogy/competency_tracker.py`, `core/pedagogy/coaching_templates.py`
- **Frontend:** Learning page center area refactor, Review tab, coaching display
- **Change folder:** [openspec/changes/learning-and-administrator-profiles/](../../changes/learning-and-administrator-profiles/)

## Reference

- [PHASE22_TEACHING_MODE.md](../../../docs/planning/phases/phase-22/PHASE22_TEACHING_MODE.md) — Spec
- [PHASE22_STATUS_ASSESSMENT.md](../../../docs/planning/phases/phase-22/PHASE22_STATUS_ASSESSMENT.md) — Implementation assessment
- Onboarding: [onboarding spec](../onboarding/spec.md) — progressive feature revelation, persona introductions
- Analytics: [analytics spec](../analytics/spec.md) — Review tab content
- Personas: [personas spec](../personas/spec.md) — Professor modes, coaching integration