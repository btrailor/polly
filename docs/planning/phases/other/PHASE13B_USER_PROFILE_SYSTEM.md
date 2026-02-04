# Phase 13b: User Profile System

**Status:** 📋 Planned  
**Priority:** HIGH (Foundational for personalization)  
**Estimated Effort:** 2-3 weeks  
**Target Date:** After Phase 24 (Orchestrator Mode)  
**Depends On:** Phase 1.5 ✅, Phase 11 ✅, Phase 13a ✅, Phase 16 ✅, Phase 24

---

## Overview

Phase 13b creates a comprehensive, human-readable user profile system that enables Polly to understand and respond to the user's unique interests, projects, philosophical leanings, communication preferences, and thinking patterns.

**Core Concept:** Unlike Uare.ai's "Human Life Model" (identity replication for monetization), Polly's profile system focuses on **practice augmentation** - helping you work better by understanding how you think, not replacing you.

**Key Differentiator:** Profiles are **human-readable markdown files** the user can edit directly, not proprietary black boxes. This aligns with Polly's autonomist philosophy: infrastructure you own and control.

---

## User Problem

**Current State:**
- Polly treats all users the same way (generic AI assistant)
- No memory of user's communication preferences, expertise levels, or thinking patterns
- User must repeatedly explain context, preferences, and domain expertise
- Responses don't adapt to user's unique way of working

**Example of Current Friction:**
```
User: "Help me build a norns instrument"
Polly: "What's your experience level with Lua? What audio framework 
       are you using? What's your coding background?"
       
[User has to re-explain they're experienced with SuperCollider, 
 norns, Lua, and prefer minimal explanations]
```

**Desired State:**
- Polly knows the user's domains, expertise, communication preferences
- Responses automatically adapt to user's thinking patterns and preferences
- Context persists across sessions
- User can edit profile directly when Polly gets something wrong

**Example with Profile System:**
```
User: "Help me build a norns instrument"
Polly: [Reads Signals domain profile: experienced with norns, 
        SuperCollider, Lua; prefers minimal explanations]
        
Polly: "Here's a norns engine scaffold using SuperCollider:
       [code example]
       
       This assumes you're familiar with Engine.register and 
       poll-based parameter updates. Want me to focus on a 
       specific aspect?"
```

---

## Architecture

### Storage Structure

```
vault/.polly/user/
├── core.md                          # Main profile (required)
├── domains/                         # Domain-specific profiles
│   ├── sigils.md                   # Coding domain
│   ├── signals.md                  # Audio/synthesis domain
│   ├── scrolls.md                  # Writing/theory domain
│   ├── sights.md                   # Visual work domain
│   └── glyphs.md                   # Systems thinking domain
├── patterns/                        # Cross-domain patterns
│   ├── workflow-rhythms.md         # Time/energy patterns
│   ├── decision-heuristics.md      # How user makes decisions
│   └── energy-management.md        # Context switching patterns
└── history/                         # Learning history
    ├── 2026-02-week1.md            # Weekly digest of updates
    └── 2026-02-summary.md          # Monthly summary
```

**Why Markdown:**
- Human-readable (user can open in any text editor)
- User-editable (direct control, no black box)
- Works with Obsidian (user can link profile ↔ notes)
- Version controllable (can track profile changes with git)
- No proprietary lock-in

---

## Profile Structure

### Core Profile (Required Skeleton)

**File:** `vault/.polly/user/core.md`

```markdown
# [User Name]'s Profile

## Active Context
[Current life stage, professional position, primary projects]

## Domains
[User-defined domains with activity levels - from Phase 1.5]

Domain | Focus | Activity Level
-------|-------|---------------
Sigils | Code, infrastructure, systems | High
Signals | Audio programming, performance | Medium
Scrolls | Writing, pedagogy, theory | Medium
Sights | Visual work | Low but building
Glyphs | Systems thinking, meta-organization | Ongoing

→ See domain-specific profiles: [[sigils]], [[signals]], [[scrolls]], [[sights]], [[glyphs]]

## Thinking Patterns

### Core Mental Models
- [Mental model 1]: [Description]
- [Mental model 2]: [Description]

### Decision Heuristics
- [Heuristic 1]
- [Heuristic 2]

### Problem-Solving Approach
- [Approach description]

## Communication Preferences

**Tone:** [Direct, warm, technical, etc.]
**Format:** [Prose, bullets, code-heavy, etc.]
**Depth:** [Match to query, always deep, always concise, etc.]
**Pushback:** [How user handles disagreement]
**Teaching vs Doing:** [When to teach, when to execute]

## Theoretical Influences
[Key thinkers/frameworks that shape user's thinking]

## Infrastructure Context

**Primary hardware:**
- [Hardware 1]
- [Hardware 2]

**Key tools:**
- [Tool 1]
- [Tool 2]

**Development context:**
- [Context 1]
- [Context 2]

## Working With [User]: Guidelines for Personas

**All personas should:**
- [Guideline 1]
- [Guideline 2]

**Avoid:**
- [Anti-pattern 1]
- [Anti-pattern 2]

**When uncertain:**
- [Uncertainty handling]

## Confidence Notes

Aspect | Confidence | Basis
-------|-----------|-------
Domain structure | Very High | Explicitly stated
Theoretical influences | Very High | Explicitly stated
Communication preferences | High | Demonstrated across interactions
Technical proficiency | High | Project discussions
Decision heuristics | Medium-High | Inferred from choices
Current project priorities | Medium | May shift; validate periodically

---

## Custom Sections

[LLM-proposed sections based on user's unique needs]
[Example: Practice Containers, Research Interests, Teaching Philosophy]
```

---

### Domain-Specific Profiles

**File:** `vault/.polly/user/domains/{domain}.md`

Each user-defined domain (from Phase 1.5) gets a dedicated profile file.

**Example:** `sigils.md` (Coding Domain)

```markdown
# Coding Profile (Sigils Domain)

## Activity Level
High — Polly development, NAS administration, Docker

## Technical Stack

**Languages:** Python (primary), JavaScript/TypeScript, Lua, Bash
**Tools:** VS Code, Docker, UGREEN NAS, Tailscale
**Preferences:**
- Infrastructure-as-code
- Self-hosted solutions over cloud dependencies
- Tools that teach through use

## Active Projects
- **Polly:** Edge-native AI system with agentic personas
- **UGREEN NAS:** Self-hosted infrastructure hub
- **Workflow Automation:** Alfred, Hazel, Keyboard Maestro integration

## Coding Patterns
- Prefers functional programming style
- Verbose variable names for clarity
- Comments explain *why*, not *what*
- Incremental working versions over big-bang releases

## Current Learning
- Building: Design capacity (p5.js, Processing)
- Strengthening: Docker containerization, Linux sysadmin

## Confidence Level
Very High (self-taught, practical expertise)
```

**One-to-One Mapping:**
- User creates domain "Sigils" in Phase 1.5 → `sigils.md` auto-created
- Polly learns domain-specific patterns over time
- User can edit directly or let Polly populate through conversation

---

### Cross-Domain Patterns

**File:** `vault/.polly/user/patterns/{pattern_name}.md`

Patterns that span multiple domains.

**Example:** `workflow-rhythms.md`

```markdown
# Work Rhythms & Context Switching

## Time Patterns
- **Focused work:** 9am-12pm, 2pm-5pm
- **Break times:** 12pm-2pm
- **Deep work sessions:** 90-120 min blocks

## Context Switching
- **Signals (audio)** → mornings (creative energy)
- **Sigils (coding)** → afternoons (analytical energy)
- **Scrolls (writing/theory)** → evenings (synthesis)

## Energy Management
- **High-energy:** Architectural/design work
- **Medium-energy:** Implementation
- **Low-energy:** Documentation, organization

## Confidence
Medium-High (observed over 20+ sessions)
```

---

## Bootstrap Mechanisms

Phase 13b provides **four complementary mechanisms** for building the user profile. Users can choose which to use based on their preference.

### 1. Corpus Inference (Import Existing Notes)

**When:** User has existing Obsidian vault or markdown notes

**Flow:**
```
┌─────────────────────────────────────────────────┐
│ Welcome to Polly! Let me learn about you.       │
│                                                 │
│ Do you have existing notes I can learn from?   │
│                                                 │
│ [Import Obsidian Vault]                        │
│ [Import Markdown Files]                        │
│ [Start Fresh]                                  │
└─────────────────────────────────────────────────┘
```

**If user imports:**
1. Polly scans notes/vault (respects .pollyignore)
2. Uses cloud model (Claude Opus 4 via Router v2) to extract:
   - **Domains:** From folder structure, note topics, tags
   - **Thinking patterns:** From note content analysis
   - **Projects:** From project notes, TODO lists
   - **Communication style:** From writing voice analysis
   - **Theoretical influences:** From citations, references
3. Generates **draft profile** in `core.md`
4. **User reviews and edits draft** (Polly shows diff)
5. User approves → Profile saved

**Technical Implementation:**
- Endpoint: `POST /profile/import-corpus`
- Parameters: `vault_path` or `file_paths[]`
- Returns: Draft profile markdown for user review

**Privacy:** 
- Corpus analysis happens locally (embeddings via RAG)
- Only profile *summary* sent to cloud model for structuring
- User reviews everything before it's saved

---

### 2. Light Onboarding (5-10 Minute Questionnaire)

**When:** After corpus import (to fill gaps) OR starting fresh

**Flow:**
```
┌─────────────────────────────────────────────────┐
│ I've created a draft profile from your notes.   │
│                                                 │
│ Would you like to answer a few questions to    │
│ fill in gaps? (5-10 minutes)                   │
│                                                 │
│ [Yes, let's refine it]                         │
│ [Skip for now - I'll tell you as we go]       │
└─────────────────────────────────────────────────┘
```

**Questions (Conversational Style):**
1. "What are your primary domains of work? (e.g., coding, writing, audio, design)"
2. "What's your current life stage or constraints? (e.g., student, working parent, freelancer)"
3. "How do you prefer to communicate? (tone, format, depth)"
4. "What thinkers, frameworks, or philosophies influence your work?"
5. "What infrastructure do you use? (tools, hardware, platforms)"
6. "What are you actively working on right now?"
7. "How do you like to learn new things? (deep dives, quick references, examples)"

**Technical Implementation:**
- Modal dialog in UI with conversational questions
- Professor persona conducts interview (warm, pedagogical)
- Answers populate `core.md` sections
- User can skip questions (progressive disclosure fills gaps later)

---

### 3. Progressive Disclosure (Ongoing Learning)

**When:** Continuously, throughout all conversations

**Mechanism:**
- Polly observes patterns in user's queries, corrections, preferences
- Proposes profile updates when confidence > 0.7
- User approves/rejects updates

**Example Flow:**
```
[During conversation]

User: "I prefer to work on audio projects in the morning when 
       I have creative energy, and coding in the afternoon."

Polly: [Detects workflow pattern]

💭 Profile Update Suggestion

I've noticed you mentioned workflow timing preferences. 
Should I add this to your profile?

**Proposed Section:** workflow-rhythms.md
**Content:**
- Signals (audio) → mornings (creative energy)
- Sigils (coding) → afternoons (analytical energy)

[Preview Full Section] [Yes, Add It] [No, Ignore]
```

**Technical Implementation:**
- Background analysis after each conversation
- Pattern detection uses Phase 13a pattern learner
- Quality scoring filters low-confidence suggestions
- UI shows non-intrusive notification (bottom-right toast)

**Triggers for Suggestions:**
- Repeated mentions (e.g., "I prefer X" said 3+ times)
- Corrections to Polly's responses
- Explicit statements ("Remember that I...")
- Domain-specific expertise demonstrated
- Communication preference violations (e.g., user edits verbose response to be concise)

---

### 4. Manual Invocation (@profile Command)

**When:** User explicitly wants to add something to profile

**Syntax:**
```
@profile [statement]              # Add to general profile
@profile:sigils [statement]       # Add to Sigils domain
@profile:patterns [statement]     # Add to cross-domain patterns
```

**Example Usage:**
```
User: "@profile I prefer to avoid cloud dependencies 
       when self-hosted alternatives exist"

Polly: "Got it. I'll add this to your decision heuristics:
       
       'Prefers self-hosted solutions over cloud dependencies'
       
       Where should I save this?
       - Decision Heuristics (core.md)
       - Sigils domain (sigils.md)
       - Both
       
User: "Both"

Polly: [Updates core.md and sigils.md]
       ✓ Profile updated
```

**Technical Implementation:**
- Detect `@profile` prefix in user input
- Parse scope (`:sigils`, `:patterns`, etc.)
- Extract statement
- Show preview before saving
- Update appropriate markdown file(s)

---

## Quality Scoring System (Preventing Slop)

One of the key challenges: **LLMs can generate generic, non-actionable profile content** (slop). We need quality scoring to filter this.

### Quality Dimensions

Each profile section is scored on these dimensions:

1. **Specificity** (0-1)
   - **High:** "Prefers functional programming with verbose variable names"
   - **Low:** "Likes to write clean code"
   - **Scoring:** Count specific terms vs. generic platitudes

2. **Actionability** (0-1)
   - **High:** Personas can use this to modify behavior
   - **Low:** Vague statements that don't inform responses
   - **Test:** "Can a persona change its output based on this?"

3. **Consistency** (0-1)
   - **High:** Matches user's demonstrated behavior
   - **Low:** Contradicts conversation history
   - **Scoring:** Compare to interaction logs

4. **Conciseness** (0-1)
   - **High:** Information-dense, no fluff
   - **Low:** Verbose, padded, repetitive
   - **Scoring:** Information content per word

5. **Cross-Reference** (0-1)
   - **High:** Links to other profile sections, domains, patterns
   - **Low:** Isolated, no connections
   - **Scoring:** Count internal links

**Overall Quality Score:**
```python
quality_score = (
    specificity * 0.3 +
    actionability * 0.3 +
    consistency * 0.2 +
    conciseness * 0.1 +
    cross_reference * 0.1
)
```

**Thresholds:**
- **>= 0.7:** High quality, auto-save
- **0.5-0.7:** Medium quality, ask user to review
- **< 0.5:** Low quality, flag for user edit or reject

---

### Implementation

**File:** `core/profile/quality_scorer.py`

```python
class ProfileQualityScorer:
    """Evaluates quality of profile content to prevent slop."""
    
    def __init__(self):
        self.generic_terms = [
            'clean code', 'best practices', 'good documentation',
            'efficient', 'organized', 'productive', 'focused'
        ]
        self.specific_indicators = [
            'prefers', 'avoids', 'uses', 'implements', 'follows'
        ]
    
    def score_section(
        self, 
        content: str, 
        interaction_history: List[Dict]
    ) -> Dict:
        """
        Score a profile section on quality dimensions.
        
        Returns:
            {
                'overall': 0.75,
                'specificity': 0.8,
                'actionability': 0.7,
                'consistency': 0.8,
                'conciseness': 0.6,
                'cross_reference': 0.5
            }
        """
        scores = {
            'specificity': self._score_specificity(content),
            'actionability': self._score_actionability(content),
            'consistency': self._score_consistency(content, interaction_history),
            'conciseness': self._score_conciseness(content),
            'cross_reference': self._score_cross_reference(content)
        }
        
        scores['overall'] = (
            scores['specificity'] * 0.3 +
            scores['actionability'] * 0.3 +
            scores['consistency'] * 0.2 +
            scores['conciseness'] * 0.1 +
            scores['cross_reference'] * 0.1
        )
        
        return scores
    
    def _score_specificity(self, content: str) -> float:
        """Higher score for specific terms vs generic platitudes."""
        words = content.lower().split()
        generic_count = sum(1 for term in self.generic_terms if term in content.lower())
        specific_count = sum(1 for term in self.specific_indicators if term in content.lower())
        
        if len(words) < 10:
            return 0.3  # Too short to be specific
        
        # Penalize generic terms, reward specific indicators
        score = max(0, 1.0 - (generic_count * 0.2))
        score += specific_count * 0.1
        
        return min(1.0, score)
    
    def _score_actionability(self, content: str) -> float:
        """Can personas change behavior based on this?"""
        actionable_patterns = [
            r'prefer[s]? (to|using|writing)',
            r'avoid[s]? (using|writing)',
            r'(always|never|typically|usually) (use|write|implement)',
            r'when .+, (I|user) (prefer|use|choose)'
        ]
        
        import re
        matches = sum(1 for pattern in actionable_patterns 
                     if re.search(pattern, content, re.IGNORECASE))
        
        return min(1.0, matches * 0.3)
    
    def _score_consistency(self, content: str, history: List[Dict]) -> float:
        """Compare to demonstrated behavior in conversations."""
        # Simplified: check if profile claims match recent interactions
        # In production: semantic similarity between profile and history
        
        if not history:
            return 0.5  # Neutral if no history
        
        # TODO: Implement semantic consistency check
        # For now, return neutral score
        return 0.7
    
    def _score_conciseness(self, content: str) -> float:
        """Information density (penalize padding)."""
        words = content.split()
        sentences = content.split('.')
        
        if len(sentences) == 0:
            return 0.5
        
        # Ideal: 10-20 words per sentence
        avg_words_per_sentence = len(words) / len(sentences)
        
        if avg_words_per_sentence > 25:
            return 0.4  # Too verbose
        elif avg_words_per_sentence < 5:
            return 0.6  # Too terse
        else:
            return 1.0  # Good density
    
    def _score_cross_reference(self, content: str) -> float:
        """Count internal links to other profile sections."""
        import re
        # Count [[links]] and explicit domain references
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        domain_refs = re.findall(r'(sigils|signals|scrolls|sights|glyphs)', 
                                 content, re.IGNORECASE)
        
        total_refs = len(links) + len(domain_refs)
        
        return min(1.0, total_refs * 0.2)
```

---

## Profile-Aware Context Injection

Once the profile exists, every persona interaction includes relevant profile context.

### For Local Models (Librarian, Router)

**Context Window Structure:**
```
[System Prompt]
You are Polly's Librarian...

[User Profile Context]
USER PROFILE:
- Name: Brett Gershon
- Communication: Direct, substantive, minimal formatting
- Current Domain: Sigils (coding)
- Expertise: High in Python, Docker, self-hosted infrastructure
- Preferences: Functional programming, verbose variable names

[User Query]
How do I set up Docker networking for my NAS?
```

**Implementation:**
```python
def build_context_with_profile(
    query: str,
    active_domain: str,
    user_profile: UserProfile
) -> str:
    """Inject profile context into system prompt."""
    
    # Load relevant profile sections
    core_prefs = user_profile.get_communication_preferences()
    domain_profile = user_profile.get_domain_profile(active_domain)
    
    profile_context = f"""
USER PROFILE:
- Name: {user_profile.name}
- Communication: {core_prefs['tone']}, {core_prefs['format']}
- Current Domain: {active_domain}
- Expertise: {domain_profile.get('expertise_summary')}
- Preferences: {', '.join(domain_profile.get('preferences', []))}
"""
    
    return f"{system_prompt}\n\n{profile_context}\n\n{query}"
```

---

### For Cloud Models (Meta-Queries)

When escalating to cloud models, include profile context in the **meta-query** itself.

**Example:**

**Without Profile:**
```
User query: "Explain Docker networking"

Cloud query: "Explain Docker networking"
```

**With Profile:**
```
User query: "Explain Docker networking for my NAS"

Cloud query: "Explain Docker networking for someone who:
- Has self-hosted UGREEN NAS
- Prefers infrastructure-as-code
- Values self-hosted solutions over cloud dependencies
- Has working proficiency with Docker containerization
- Context: Setting up services with Tailscale networking"
```

**Implementation:**
```python
def build_cloud_meta_query(
    query: str,
    user_profile: UserProfile,
    active_domain: str
) -> str:
    """Contextualize cloud query with profile."""
    
    domain_profile = user_profile.get_domain_profile(active_domain)
    infrastructure = user_profile.get_infrastructure_context()
    
    context_lines = []
    
    if domain_profile:
        context_lines.append(f"- Domain expertise: {domain_profile['expertise_summary']}")
        context_lines.append(f"- Technical stack: {', '.join(domain_profile['tools'])}")
    
    if infrastructure:
        context_lines.append(f"- Infrastructure: {', '.join(infrastructure['hardware'])}")
    
    preferences = user_profile.get_decision_heuristics()
    if preferences:
        context_lines.extend([f"- {pref}" for pref in preferences])
    
    if context_lines:
        contextualized = f"{query} for someone who:\n" + "\n".join(context_lines)
    else:
        contextualized = query
    
    return contextualized
```

**Result:**
- Cloud model response is **pre-contextualized**
- Response is more relevant to user's specific situation
- Resulting note is already personalized

---

## Profile-Aware Confidence Threshold

The local model's confidence threshold can be **profile-informed**.

**Logic:**
- **High expertise domain** → Escalate faster (user will notice errors)
- **Learning domain** → More permissive threshold (user expects to learn)

**Example:**

```python
def get_confidence_threshold(
    query: str,
    user_profile: UserProfile,
    active_domain: str
) -> float:
    """Adjust confidence threshold based on user expertise."""
    
    domain_profile = user_profile.get_domain_profile(active_domain)
    expertise = domain_profile.get('expertise_level', 'medium')
    
    base_threshold = 0.7
    
    if expertise == 'very_high':
        # User is expert, they'll catch errors - escalate more
        return base_threshold - 0.1  # 0.6
    elif expertise == 'high':
        return base_threshold
    elif expertise == 'medium':
        return base_threshold
    elif expertise == 'low':
        # User is learning, local model can try more
        return base_threshold + 0.1  # 0.8
    else:
        return base_threshold
```

---

## Integration with Phase 24 (Orchestrator Mode)

When Orchestrator Mode is active, the profile system enhances multi-persona workflows.

### Without Profile (Current State):
```
User: "Build a norns instrument, write docs, create learning path"

Orchestrator routes:
1. Programmer → build instrument (generic response)
2. Scribe → write docs (generic response)
3. Professor → create learning path (generic response)
```

### With Profile (Phase 13b):
```
User: "Build a norns instrument, write docs, create learning path"

Orchestrator reads profile:
- Signals domain: experienced with norns, SuperCollider, Lua
- Scrolls domain: prefers pedagogical framing, Freire influence
- Communication: direct, minimal formatting

Orchestrator routes with context:
1. Programmer → Signals domain profile → focused code, no basics
2. Scribe → Scrolls domain profile → pedagogical framing, concise
3. Professor → Signals domain profile → assumes SuperCollider knowledge

All personas respect Brett's communication preferences.
```

**Implementation:**
```python
# In Orchestrator
def route_with_profile(
    tasks: List[Task],
    user_profile: UserProfile
) -> List[PersonaExecution]:
    """Route tasks to personas with profile context."""
    
    executions = []
    
    for task in tasks:
        persona = self.select_persona(task)
        domain = self.detect_domain(task)
        
        # Inject profile context
        domain_profile = user_profile.get_domain_profile(domain)
        comm_prefs = user_profile.get_communication_preferences()
        
        execution = PersonaExecution(
            persona=persona,
            task=task,
            profile_context={
                'domain': domain_profile,
                'communication': comm_prefs,
                'thinking_patterns': user_profile.get_thinking_patterns()
            }
        )
        
        executions.append(execution)
    
    return executions
```

---

## User Editing & Approval Flows

A core principle: **User maintains control over their profile.**

### Direct Editing

**User can edit profile markdown directly:**
1. Open `vault/.polly/user/core.md` in any text editor
2. Edit sections
3. Save
4. Polly detects changes on next query
5. Polly respects edits as ground truth

**No special UI needed** - just standard file editing.

---

### Approval Flow (for LLM Suggestions)

When Polly proposes profile updates, user sees:

```
┌─────────────────────────────────────────────────┐
│ 💭 Profile Update Suggestion                    │
├─────────────────────────────────────────────────┤
│                                                 │
│ I've noticed you frequently reference           │
│ "Practice Containers" as a framework for        │
│ organizing creative work.                       │
│                                                 │
│ Should I add this as a custom section?          │
│                                                 │
│ [Preview Section ▼]                             │
│                                                 │
│ Quality Score: 0.82 (High)                      │
│ - Specificity: 0.9                              │
│ - Actionability: 0.8                            │
│ - Consistency: 0.85                             │
│                                                 │
│ [Yes, Add It]  [Edit First]  [No, Ignore]      │
└─────────────────────────────────────────────────┘
```

**Preview Section** expands to show:
```markdown
## Practice Containers

Brett maintains 10 ongoing practices as containers for creative engagement:

1. Capture Your Environment
2. Compose and Compost
3. Build Instruments Not Tracks
4. Embrace Constraint as Generative
5. Performance as Live Thinking
6. Document as Thinking Tool
7. Build Systems That Sustain Practice
8. Interrogate Tools as Ideology
9. Cultivate Creative Community
10. Situate Work in Broader Context

These are supported by exercises building specific capacities within each area.

**Confidence:** High (referenced 12 times across 8 conversations)
```

**Actions:**
- **Yes, Add It:** Saves to `core.md` immediately
- **Edit First:** Opens modal editor, user refines, then saves
- **No, Ignore:** Dismisses (and marks as "user rejected" so Polly doesn't suggest again)

---

### Confidence Tracking UI

**Option A: Always Visible** (chosen for Phase 13b)

At the bottom of every profile file, a confidence table:

```markdown
## Confidence Notes

Aspect | Confidence | Basis | Last Updated
-------|-----------|-------|-------------
Domain structure | Very High | Explicitly stated | 2026-02-03
Theoretical influences | Very High | Explicitly stated | 2026-02-03
Communication preferences | High | Demonstrated 25+ times | 2026-02-05
Technical proficiency | High | Project discussions | 2026-02-04
Decision heuristics | Medium-High | Inferred from 15 choices | 2026-02-06
Workflow rhythms | Medium | Observed 8 sessions | 2026-02-07
```

**Why always visible:**
- User can see what Polly is confident about
- Low confidence items prompt user to clarify
- Transparency builds trust

---

### Review Frequency

**Monthly Review Prompts:**

On the 1st of each month, Polly shows:

```
┌─────────────────────────────────────────────────┐
│ 📊 Monthly Profile Review                       │
├─────────────────────────────────────────────────┤
│                                                 │
│ Here's what I learned about you this month:     │
│                                                 │
│ New Insights:                                   │
│ • Added Signals workflow timing preference      │
│ • Updated Sigils domain with p5.js learning     │
│ • Refined communication preference (less bullets)│
│                                                 │
│ Low Confidence Areas (review recommended):      │
│ • Workflow rhythms (only 8 observations)        │
│ • Energy management patterns (inconsistent)     │
│                                                 │
│ [Review Profile]  [Looks Good]  [Remind Later] │
└─────────────────────────────────────────────────┘
```

**User can also:**
- View profile anytime: "Show my profile"
- Request specific review: "Review my Signals domain profile"
- Disable monthly prompts: Settings → Profile → Auto-review: Off

---

## API Endpoints

### Profile Management

```
POST /profile/create
    Create new user profile from scratch or imported corpus
    
GET /profile/core
    Return core profile (core.md)
    
GET /profile/domain/{domain}
    Return domain-specific profile (domains/{domain}.md)
    
GET /profile/patterns/{pattern}
    Return cross-domain pattern (patterns/{pattern}.md)
    
PUT /profile/update
    Update profile section
    Body: {file: 'core.md', section: 'Communication Preferences', content: '...'}
    
POST /profile/suggest-update
    LLM suggests profile update for user approval
    Body: {observation: '...', confidence: 0.82, section: '...'}
    
POST /profile/approve-suggestion
    User approves suggested update
    Body: {suggestion_id: '...', edits: {...}}
    
POST /profile/reject-suggestion
    User rejects suggested update
    Body: {suggestion_id: '...', reason: 'optional'}
```

### Profile Import

```
POST /profile/import-corpus
    Import existing notes/vault to bootstrap profile
    Body: {vault_path: '...'}
    Returns: {draft_profile: '...', quality_scores: {...}}
    
POST /profile/onboarding-start
    Start onboarding questionnaire
    Returns: {questions: [...]}
    
POST /profile/onboarding-answer
    Submit onboarding answer
    Body: {question_id: '...', answer: '...'}
    
POST /profile/onboarding-complete
    Finish onboarding, generate profile
    Returns: {profile: '...'}
```

### Profile Context

```
POST /profile/context-for-query
    Get profile context for a query
    Body: {query: '...', domain: 'sigils'}
    Returns: {profile_context: '...', confidence: 0.9}
    
POST /profile/meta-query
    Build cloud meta-query with profile context
    Body: {query: '...', domain: 'sigils'}
    Returns: {meta_query: '...', context_summary: '...'}
```

---

## File Structure

```
core/profile/
├── __init__.py
├── profile_manager.py          # Main profile CRUD
├── quality_scorer.py            # Quality scoring system
├── bootstrap/
│   ├── __init__.py
│   ├── corpus_analyzer.py      # Import from existing notes
│   ├── onboarding.py            # Questionnaire system
│   └── progressive_learner.py  # Ongoing learning
├── context/
│   ├── __init__.py
│   ├── context_injector.py     # Inject profile into queries
│   └── meta_query_builder.py  # Build cloud meta-queries
└── ui/
    ├── __init__.py
    ├── suggestion_manager.py    # Manage update suggestions
    └── review_scheduler.py      # Monthly review prompts

vault/.polly/user/
├── core.md                      # Main profile
├── domains/                     # Domain profiles
│   ├── sigils.md
│   ├── signals.md
│   ├── scrolls.md
│   ├── sights.md
│   └── glyphs.md
├── patterns/                    # Cross-domain patterns
│   ├── workflow-rhythms.md
│   ├── decision-heuristics.md
│   └── energy-management.md
└── history/                     # Learning history
    ├── 2026-02-week1.md
    └── 2026-02-summary.md
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Goal:** Basic profile storage and CRUD

**Tasks:**
- [ ] Create `core/profile/profile_manager.py`
- [ ] Implement profile markdown reading/writing
- [ ] Create profile storage structure in `vault/.polly/user/`
- [ ] API endpoints for profile CRUD
- [ ] Basic UI for viewing profile

**Deliverables:**
- Profile manager class
- File I/O for markdown profiles
- API: GET/PUT profile endpoints
- UI: Profile viewer page

**Testing:**
- Create profile manually, verify storage
- Update profile, verify persistence
- Read profile, verify correct sections loaded

---

### Phase 2: Bootstrap Mechanisms (Week 1-2)

**Goal:** All four bootstrap methods working

**Tasks:**
- [ ] Corpus analyzer (import notes)
  - Scan vault/files
  - Extract domains, patterns, preferences
  - Generate draft profile
- [ ] Onboarding questionnaire
  - 7 conversational questions
  - Professor persona conducts interview
  - Populate profile from answers
- [ ] Progressive learner
  - Detect patterns in conversations
  - Suggest profile updates
  - Quality scoring
- [ ] Manual invocation (`@profile` command)
  - Parse `@profile` syntax
  - Update appropriate files

**Deliverables:**
- 4 working bootstrap mechanisms
- UI for onboarding
- UI for suggestion approval
- `@profile` command parser

**Testing:**
- Import test vault, verify profile accuracy
- Complete onboarding, verify profile populated
- Trigger progressive updates, verify suggestions
- Use `@profile` command, verify updates

---

### Phase 3: Quality Scoring & Validation (Week 2)

**Goal:** Prevent slop, ensure high-quality profiles

**Tasks:**
- [ ] Implement `ProfileQualityScorer`
  - Specificity scoring
  - Actionability scoring
  - Consistency scoring
  - Conciseness scoring
  - Cross-reference scoring
- [ ] Quality thresholds
  - Auto-save high quality (>0.7)
  - Prompt review medium (0.5-0.7)
  - Reject low quality (<0.5)
- [ ] User review UI
  - Show quality scores
  - Allow editing before approval

**Deliverables:**
- Quality scorer class
- Quality scoring tests
- Review UI with scores

**Testing:**
- Test generic content (low specificity) → flagged
- Test actionable content (high actionability) → approved
- Test inconsistent content (contradicts history) → flagged

---

### Phase 4: Context Injection (Week 2-3)

**Goal:** Use profile to improve all responses

**Tasks:**
- [ ] Local model context injection
  - Build context from profile
  - Inject into system prompt
  - Test with Librarian queries
- [ ] Cloud model meta-queries
  - Build contextualized queries
  - Test with Router escalations
  - Verify improved responses
- [ ] Profile-aware confidence threshold
  - Adjust threshold by domain expertise
  - Test escalation behavior

**Deliverables:**
- Context injector
- Meta-query builder
- Confidence threshold adjuster

**Testing:**
- Query in high-expertise domain → verify escalation threshold
- Query in learning domain → verify permissive threshold
- Compare cloud responses (with vs without profile context)

---

### Phase 5: UI & User Flows (Week 3)

**Goal:** Polished user experience

**Tasks:**
- [ ] Profile viewer page
  - Display core.md
  - Links to domain profiles
  - Confidence table
- [ ] Profile editor
  - Markdown editor with preview
  - Save directly to files
- [ ] Suggestion notifications
  - Toast notifications for updates
  - Approval modal
  - Preview and edit
- [ ] Monthly review flow
  - Summary of monthly learnings
  - Low confidence areas highlighted
  - Review UI

**Deliverables:**
- Profile viewer UI
- Profile editor UI
- Suggestion system UI
- Monthly review UI

**Testing:**
- View profile → verify all sections visible
- Edit profile → verify changes persist
- Receive suggestion → verify approval flow
- Monthly review → verify summary accuracy

---

### Phase 6: Integration with Phase 24 (Week 3 or Post-Phase 24)

**Goal:** Orchestrator uses profiles for multi-persona coordination

**Tasks:**
- [ ] Profile context in Orchestrator
  - Load domain profiles per task
  - Pass to personas
  - Coordinate communication preferences
- [ ] Cross-persona consistency
  - All personas respect same communication prefs
  - Domain expertise shared across personas

**Deliverables:**
- Orchestrator profile integration
- Multi-persona context passing

**Testing:**
- Multi-task query → verify all personas use profile
- Check response consistency (tone, format, depth)

---

## Success Metrics

### Quantitative

1. **Profile Completeness**
   - Target: 80%+ profile sections populated after 1 week of use
   - Measure: Count filled sections / total sections

2. **Quality Scores**
   - Target: 90%+ profile content scores >0.7 (high quality)
   - Measure: Average quality score across all sections

3. **Response Personalization**
   - Target: 70%+ responses demonstrate profile awareness
   - Measure: User survey + automated detection (profile terms in responses)

4. **User Approval Rate**
   - Target: 80%+ suggested updates approved by user
   - Measure: Approved suggestions / total suggestions

5. **Edit Frequency**
   - Target: <10% user edits to LLM-generated profile sections
   - Measure: User edits / total generated sections

---

### Qualitative

1. **User Feels Understood**
   - "Polly knows how I like to work"
   - "I don't have to repeat context"

2. **Responses Are Relevant**
   - Appropriate depth for user's expertise
   - Right tone and format
   - Contextualized to user's infrastructure

3. **User Trusts Profile System**
   - Can see what Polly knows (transparency)
   - Can edit when wrong (control)
   - Confidence tracking is accurate

---

## Risks & Mitigations

### Risk 1: Profile Inaccuracies

**Risk:** LLM generates incorrect profile content (hallucinations, misunderstandings)

**Mitigation:**
- Quality scoring catches low-confidence content
- User approval required for all updates
- User can edit directly (markdown files)
- Confidence tracking makes uncertainty visible

---

### Risk 2: Profile Slop (Generic Content)

**Risk:** Profile becomes filled with generic platitudes that don't help

**Mitigation:**
- Quality scoring emphasizes specificity and actionability
- Reject content <0.5 quality score
- User review for medium quality (0.5-0.7)
- Examples in specification show high-quality content

---

### Risk 3: Privacy Concerns

**Risk:** User uncomfortable with AI analyzing their notes/behavior

**Mitigation:**
- Corpus analysis happens locally (only summary sent to cloud)
- User controls what gets imported (can exclude sensitive notes)
- Profile stored locally in markdown (not cloud)
- User can view/edit/delete any profile content

---

### Risk 4: Over-Constraint (Profile Too Rigid)

**Risk:** Profile makes Polly responses too narrow, misses new interests

**Mitigation:**
- Confidence tracking shows when profile is stale
- Monthly review prompts updates
- User can always override profile with explicit query context
- Progressive learning allows profile to evolve

---

### Risk 5: Maintenance Burden

**Risk:** Profile becomes stale, user has to manually update frequently

**Mitigation:**
- Progressive learning does most updates automatically
- Monthly review is optional (can dismiss)
- Profile decay mechanism (old content marked low confidence)
- User only reviews low-confidence areas

---

## Competitive Positioning

### Polly vs. Uare.ai

Feature | Polly | Uare.ai
--------|-------|--------
**Architecture** | Edge-native, local-first | Cloud-hosted SaaS
**Storage** | Markdown files you own | Proprietary containers
**Purpose** | Practice augmentation | Identity replication for monetization
**Editability** | Direct file editing | Limited user control
**Privacy** | Local analysis, minimal cloud | Full data in cloud
**Business Model** | Infrastructure you own | Subscription rental
**Philosophy** | Autonomist (reduce dependence) | Platform economy

**Key Differentiator:** 
> "Polly: Personal AI you own. Not rented, not black-boxed, not optimized for monetizing your expertise. Infrastructure for augmenting your practice, not replicating your identity."

---

## Next Steps After Phase 13b

### Future Enhancements (Post-Phase 13b)

1. **Profile Sharing** (Phase 30+)
   - Export profile for collaboration
   - Import profile templates from others
   - "Pedagogical profile" for teaching contexts

2. **Multi-User Profiles** (Phase 30+)
   - Team profiles for shared projects
   - Aggregate preferences for collaboration

3. **Profile Analytics** (Phase 30+)
   - Visualize how profile has evolved
   - Show most-used patterns
   - Identify learning trajectories

4. **Profile-Based Recommendations** (Phase 30+)
   - "Based on your Signals work, you might like [tool/resource]"
   - Cross-domain connection suggestions

---

## Dependencies

**Required (Must be complete):**
- ✅ Phase 1.5: Domain Configuration
- ✅ Phase 11: Multi-Model Routing (for cloud meta-queries)
- ✅ Phase 13a: Pattern Learning (hybrid with profile system)
- ✅ Phase 16: Native Notes (profile stored as markdown)

**Optional (Enhances but not blocking):**
- Phase 24: Orchestrator Mode (profile-aware multi-persona coordination)

---

## Related Documents

- `PHASE13A_PATTERN_LEARNING_CORE.md` - Hybrid system (JSON patterns + markdown profiles)
- `PHASE24_ORCHESTRATOR_MODE.md` - Multi-persona coordination with profiles
- `DESIGN_PHILOSOPHY.md` - Progressive Capability principle
- `KNOWN_ISSUES.md` - Pattern system evaluation needed before migration
- `RESEARCH_QUEUE.md` - Uare.ai competitive analysis

---

**Created:** February 4, 2026  
**Last Updated:** February 4, 2026  
**Status:** Ready for implementation after Phase 24  
**Estimated Effort:** 2-3 weeks (3 weeks with Phase 24 integration)
