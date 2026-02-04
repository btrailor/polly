# Phase 1.5: Domain Configuration System

**Status:** ✅ COMPLETE (Backend 100%, UI wizard deferred to Phase 18)  
**Duration:** 6 days (completed January 25, 2026)  
**Prerequisites:** Phase 1 (Basic Chat), Phase 2 (RAG)  
**Enables:** All knowledge organization features (Phases 11, 12, 13, 14, 16, 17), Phase 18 (Onboarding)

**Completion Summary:** See `PHASE1.5_DAY6_COMPLETE.md` for full details

---

## Overview

Phase 1.5 implements a user-definable domain configuration system that allows users to organize their knowledge into custom categories rather than being locked into hardcoded domains. This foundational system enables Polly to adapt to any user's workflow, whether they're doing software development, academic research, creative writing, or personal knowledge management.

### What Are Domains?

Domains are high-level categories that organize your knowledge, notes, patterns, and mental models. Think of them as the "buckets" or "folders" that structure how Polly understands and retrieves information.

**Examples:**
- **Software Development:** Concepts, Patterns, Documentation, Code, Architecture
- **Academic Research:** Questions, Data, Literature, Methods, Insights
- **Creative Writing:** Characters, Plots, Worldbuilding, Drafts, References
- **Personal Knowledge:** Notes, Journal, Ideas, Projects, Archive

### Why User-Definable Domains?

The original Polly used hardcoded domains (Sigils, Signals, Scrolls, Glyphs, Grids) which reflected the creator's personal workflow. To make Polly useful for a broader audience, domains must be:

1. **Customizable** - Users define names, purposes, and properties
2. **Template-based** - Common presets for quick setup
3. **Intelligent** - Smart recommendations based on content analysis
4. **Adaptive** - Learn from user behavior over time

---

## Goals

1. **Enable user-defined knowledge organization** - Users can create, edit, and delete domains to match their workflow
2. **Provide helpful templates** - Common domain structures for different use cases (6 templates)
3. **Smart recommendations** - AI-powered suggestions for domain properties, auto-tagging rules, and organization
4. **Seamless first-run experience** - Guided wizard for domain setup on first launch
5. **Easy ongoing management** - Settings panel for modifying domains anytime
6. **Integration foundation** - Provide domain system for all other phases to use

---

## Domain Data Model

### Core Properties

Each domain has the following properties:

```json
{
  "id": "uuid-v4",
  "name": "Concepts",
  "description": "Core concepts, theories, and foundational knowledge",
  "color": "#9b59b6",
  "icon": "💡",
  "folderPath": "01-Concepts",
  "ragWeight": 0.20,
  "autoTagRules": [
    "concept",
    "theory",
    "principle",
    "definition",
    "fundamental"
  ],
  "created": "2026-01-23T10:00:00Z",
  "modified": "2026-01-23T10:00:00Z",
  "order": 1
}
```

### Property Details

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `id` | string (UUID) | Unique identifier | `"a1b2c3d4-..."` |
| `name` | string | Display name (max 30 chars) | `"Concepts"` |
| `description` | string | Purpose/explanation (max 200 chars) | `"Core theories and principles"` |
| `color` | string (hex) | UI color for visualization | `"#9b59b6"` (purple) |
| `icon` | string (emoji) | Visual identifier | `"💡"` |
| `folderPath` | string | Relative path in notes directory | `"01-Concepts"` or `"Concepts"` |
| `ragWeight` | float (0-1) | Priority in retrieval (normalized) | `0.20` (20% weight) |
| `autoTagRules` | array[string] | Keywords that suggest this domain | `["concept", "theory"]` |
| `created` | ISO 8601 | Creation timestamp | `"2026-01-23T10:00:00Z"` |
| `modified` | ISO 8601 | Last modification timestamp | `"2026-01-23T10:30:00Z"` |
| `order` | integer | Sort order in UI | `1` |

### Storage

Domains are stored in: `~/.polly/domains.json`

```json
{
  "version": "1.0",
  "folderNumbering": true,
  "domains": [
    { /* domain object */ },
    { /* domain object */ }
  ],
  "templates": [
    { /* template metadata */ }
  ],
  "lastModified": "2026-01-23T10:00:00Z"
}
```

### Validation Rules

- **Name:** 1-30 characters, unique across domains
- **Description:** 0-200 characters
- **Color:** Valid hex code (#RRGGBB)
- **Icon:** Single emoji character
- **Folder path:** Valid filename, unique, no special chars except hyphen/underscore
- **RAG weight:** 0.0-1.0, all weights should sum to ~1.0 (normalized automatically)
- **Auto-tag rules:** Array of lowercase strings, no duplicates within domain

---

## Domain Templates

### Six Default Templates

Phase 1.5 provides six pre-configured templates to help users get started quickly:

#### 1. Software Development

**Target users:** Developers, engineers, technical leads

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Concepts | Core programming concepts and theory | Purple `#9b59b6` | 💡 | concept, theory, principle, algorithm, data structure |
| Patterns | Design patterns and best practices | Blue `#3498db` | 🔷 | pattern, practice, idiom, architecture, design |
| Documentation | Technical docs, API references, guides | Green `#27ae60` | 📄 | documentation, guide, reference, API, tutorial |
| Code | Code snippets, implementations, examples | Teal `#16a085` | 💻 | code, implementation, snippet, example, function |
| Architecture | System design, architecture decisions | Orange `#e67e22` | 🏛️ | architecture, system, design, infrastructure, component |

#### 2. Academic Research

**Target users:** Researchers, students, academics

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Questions | Research questions and hypotheses | Red `#e74c3c` | ❓ | question, hypothesis, inquiry, problem, investigation |
| Data | Datasets, observations, measurements | Blue `#3498db` | 📊 | data, dataset, observation, measurement, statistics |
| Literature | Papers, books, related work | Green `#27ae60` | 📚 | paper, literature, study, research, citation |
| Methods | Research methods and protocols | Purple `#9b59b6` | 🔬 | method, protocol, procedure, experiment, technique |
| Insights | Findings, conclusions, analysis | Orange `#e67e22` | 💡 | insight, finding, conclusion, analysis, result |

#### 3. Creative Writing

**Target users:** Authors, screenwriters, game designers

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Characters | Character profiles, development, arcs | Pink `#e91e63` | 👤 | character, protagonist, antagonist, personality, backstory |
| Plots | Plot lines, story arcs, conflicts | Red `#e74c3c` | 📖 | plot, story, arc, conflict, climax |
| Worldbuilding | Settings, history, rules, cultures | Blue `#3498db` | 🌍 | world, setting, culture, history, geography |
| Drafts | Work in progress, scenes, chapters | Orange `#e67e22` | ✍️ | draft, scene, chapter, writing, revision |
| References | Research, inspiration, resources | Green `#27ae60` | 🗂️ | reference, research, inspiration, source, resource |

#### 4. Personal Knowledge

**Target users:** General knowledge management, personal learning

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Notes | General notes and quick captures | Gray `#95a5a6` | 📝 | note, capture, thought, idea, reminder |
| Journal | Personal reflections, daily logs | Purple `#9b59b6` | 📔 | journal, reflection, log, entry, diary |
| Ideas | Brainstorms, concepts, future projects | Yellow `#f1c40f` | 💡 | idea, brainstorm, concept, possibility, future |
| Projects | Active projects and plans | Blue `#3498db` | 🎯 | project, plan, goal, objective, initiative |
| Archive | Completed or reference material | Green `#27ae60` | 📦 | archive, completed, reference, old, historical |

#### 5. Academic/Student

**Target users:** Students, educators

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Courses | Course materials, syllabi, schedules | Blue `#3498db` | 🎓 | course, class, syllabus, lecture, lesson |
| Notes | Class notes, study notes, summaries | Green `#27ae60` | 📝 | notes, summary, key points, lecture notes |
| Papers | Essays, assignments, research papers | Purple `#9b59b6` | 📄 | paper, essay, assignment, report, thesis |
| Projects | Course projects, group work | Orange `#e67e22` | 🔨 | project, assignment, homework, lab, group work |
| Resources | Textbooks, articles, study materials | Teal `#16a085` | 📚 | resource, textbook, article, reading, material |

#### 6. Polly Creator

**Target users:** Original Polly workflow (for reference/nostalgia)

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Sigils | Core concepts, symbols, archetypes | Purple `#9b59b6` | ⚡ | sigil, symbol, archetype, core, essence |
| Signals | Data patterns, trends, observations | Blue `#3498db` | 📡 | signal, pattern, trend, observation, data |
| Scrolls | Documentation, procedures, knowledge | Green `#27ae60` | 📜 | scroll, documentation, procedure, knowledge, guide |
| Glyphs | Code patterns, syntax, implementations | Orange `#e67e22` | ⌨️ | glyph, code, syntax, implementation, pattern |
| Grids | Structures, frameworks, systems | Red `#e74c3c` | ⬜ | grid, structure, framework, system, organization |

#### 7. Custom

**Target users:** Users with unique workflows

- Blank slate - user defines all domains from scratch
- Wizard guides through creating first 3-5 domains
- Provides suggestions based on detected content (if migrating from Obsidian)

---

## Zero-Config Quick Start

### Overview

For users who want to start working immediately without upfront configuration, Polly provides a zero-config quick start option. This aligns with the "Stop organizing. Start working." marketing theme—users can begin creating content immediately while Polly handles organization invisibly.

### Quick Start Domains

When users choose zero-config, Polly automatically creates three general-purpose domains:

| Domain | Description | Color | Icon | Auto-tag Keywords |
|--------|-------------|-------|------|-------------------|
| Work | Professional work, projects, tasks | Blue `#3498db` | 💼 | work, project, task, meeting, client, professional |
| Personal | Personal notes, life, health, home | Purple `#9b59b6` | 🏠 | personal, life, family, health, home, private |
| Learning | Study, research, new skills, interests | Green `#27ae60` | 📚 | learn, study, research, course, skill, education |

**Key Characteristics:**
- Broad, non-prescriptive categories
- Accommodate most use cases without specialization
- Easy to understand for any user
- Minimal cognitive overhead

### Auto-Filing Intelligence

With zero-config domains, Polly's auto-filing becomes critical:

1. **Content Analysis:** Examine note title, body, and context
2. **Keyword Matching:** Use expanded keyword sets for broad categories
3. **Contextual Clues:** Time of day, related emails, calendar events
4. **User Correction Learning:** When users manually refile, learn from it

**Auto-Filing Logic:**
```typescript
async function autoFileNote(note: Note, userContext: UserContext): Promise<string> {
  // 1. Check for explicit domain hints in title/frontmatter
  const explicitDomain = extractExplicitDomain(note);
  if (explicitDomain) return explicitDomain;
  
  // 2. Analyze content keywords
  const keywordScores = analyzeKeywords(note.content, userContext.domains);
  
  // 3. Check contextual signals
  const contextSignals = analyzeContext(note, userContext);
  
  // 4. Combine signals with learned user preferences
  const domainScores = combineScores(keywordScores, contextSignals, userContext.corrections);
  
  // 5. If confident (>0.7), auto-file; otherwise, ask user
  const topDomain = getTopScoringDomain(domainScores);
  if (topDomain.confidence > 0.7) {
    return topDomain.id;
  } else {
    return await promptUserForDomain(note, topDomain);
  }
}
```

### Progressive Domain Suggestions

After users accumulate 25-50 notes, Polly analyzes content clusters and proactively suggests new domains:

**Example:**
```
┌─────────────────────────────────────────────────────────┐
│          New Domain Suggestion                          │
│                                                         │
│  Polly has detected 12 notes about "Music Production"   │
│  in your Learning domain.                               │
│                                                         │
│  Would you like to create a dedicated "Music" domain?   │
│                                                         │
│  📝 Notes that would move:                              │
│  • DAW Setup Guide                                      │
│  • MIDI Controller Notes                                │
│  • Mixing Techniques                                    │
│  • Sound Design Basics                                  │
│  • ... and 8 more                                       │
│                                                         │
│            [Create Domain] [Not Now] [Never]            │
└─────────────────────────────────────────────────────────┘
```

**Suggestion Logic:**
- Minimum 10-12 notes on similar topic within single domain
- Topic cohesion score >0.75 (semantic clustering)
- Not suggested more than once per topic
- User can dismiss permanently

### Upgrading from Zero-Config

Users can switch from zero-config to custom domains anytime:

1. **Keep existing structure** - Add new domains alongside Work/Personal/Learning
2. **Replace entirely** - Choose a template and refile all notes
3. **Hybrid approach** - Rename and expand zero-config domains

**Migration Flow:**
```
Settings → Domains → [Customize Domains]
  ↓
"You're currently using Quick Start domains. Choose an option:"
  → Add more domains (keep current 3)
  → Start fresh with template
  → Advanced customization
```

### Marketing Alignment

**Positioning:**
- "Working in 30 seconds" - Immediate value, no setup friction
- "Stop organizing. Start working." - Polly handles structure
- Progressive revelation - Complexity appears when ready

**Target Users:**
- ADHD/neurodivergent users (setup paralysis)
- Casual users who just want to try Polly
- Users migrating from unstructured systems
- Anyone intimidated by domain configuration

### Implementation Notes

**User Choice:**
- First-run wizard presents **both** options equally (not forcing zero-config)
- Clear explanation of tradeoffs:
  - Zero-config: Start immediately, customize later
  - Templates: More structure upfront, better organization from day one

**Metrics to Track:**
- % of users choosing zero-config vs. templates
- Time to first note created (should be <60 seconds for zero-config)
- Upgrade rate (zero-config → custom domains)
- User satisfaction with auto-filing accuracy

---

## First-Run Wizard

### Wizard Flow

When a user launches Polly for the first time (or when `~/.polly/domains.json` doesn't exist), they're guided through domain setup:

#### Step 1: Welcome Screen

```
┌─────────────────────────────────────────────────────────┐
│                    Welcome to Polly!                    │
│                                                         │
│  Let's get started. Choose your setup approach:        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ⚡ Quick Start (Recommended)                   │   │
│  │                                                  │   │
│  │  Start working immediately with smart defaults.  │   │
│  │  Polly will organize as you go.                  │   │
│  │                                                  │   │
│  │  • 3 general domains (Work, Personal, Learning) │   │
│  │  • Auto-filing based on content                  │   │
│  │  • Customize anytime                             │   │
│  │                                                  │   │
│  │               [Quick Start →]                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ⚙️  Custom Setup                               │   │
│  │                                                  │   │
│  │  Choose a template that matches your workflow.   │   │
│  │  More structure upfront.                         │   │
│  │                                                  │   │
│  │  • 6 templates available                         │   │
│  │  • Tailored to your use case                     │   │
│  │  • Full customization                            │   │
│  │                                                  │   │
│  │              [Choose Template →]                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Interaction:**
- Two equal-prominence options presented
- Quick Start creates Work/Personal/Learning immediately
- Custom Setup goes to template selection (Step 2)
- User can return to this choice anytime from settings

#### Step 2: Template Selection (Custom Setup Path Only)

```
┌─────────────────────────────────────────────────────────┐
│            Choose Your Knowledge Structure              │
│                                                         │
│  Select a template that matches your primary use case.  │
│  You can customize it later.                            │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 💻 Software  │  │ 🎓 Research  │  │ ✍️  Writing  │ │
│  │ Development  │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 📚 Personal  │  │ 🎒 Student   │  │ ⚡ Polly     │ │
│  │ Knowledge    │  │              │  │ Creator      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐                                      │
│  │ ⚙️  Custom   │                                      │
│  │ (Advanced)   │                                      │
│  └──────────────┘                                      │
│                                                         │
│                         [Back] [Next]                   │
└─────────────────────────────────────────────────────────┘
```

**Interaction:**
- User clicks a template card to select
- Selected card highlights with border
- Hover shows brief description
- "Next" button enabled after selection

#### Step 3: Template Preview

```
┌─────────────────────────────────────────────────────────┐
│            Software Development Domains                 │
│                                                         │
│  These 5 domains will organize your technical knowledge: │
│                                                         │
│  💡 01-Concepts                                         │
│     Core programming concepts and theory                │
│     Keywords: concept, theory, algorithm...             │
│                                                         │
│  🔷 02-Patterns                                         │
│     Design patterns and best practices                  │
│     Keywords: pattern, practice, idiom...               │
│                                                         │
│  📄 03-Documentation                                    │
│     Technical docs, API references, guides              │
│     Keywords: documentation, guide, API...              │
│                                                         │
│  💻 04-Code                                             │
│     Code snippets, implementations, examples            │
│     Keywords: code, implementation, snippet...          │
│                                                         │
│  🏛️  05-Architecture                                    │
│     System design, architecture decisions               │
│     Keywords: architecture, system, design...           │
│                                                         │
│  Your notes will be organized in:                       │
│  ~/.polly/notes/01-Concepts/, 02-Patterns/, etc.        │
│                                                         │
│              [Back] [Customize] [Create Domains]        │
└─────────────────────────────────────────────────────────┘
```

**Interaction:**
- Shows all domains in selected template
- "Customize" button opens editor (Step 4)
- "Create Domains" accepts template as-is and creates domains

#### Step 4: Customization (Optional)

```
┌─────────────────────────────────────────────────────────┐
│              Customize Your Domains                     │
│                                                         │
│  Edit, add, or remove domains to fit your needs.        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 💡 Concepts                             [Edit] [×]│  │
│  │ Core programming concepts and theory             │  │
│  │ Folder: 01-Concepts  │  Weight: ●●●○○ (20%)     │  │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🔷 Patterns                             [Edit] [×]│  │
│  │ Design patterns and best practices               │  │
│  │ Folder: 02-Patterns  │  Weight: ●●●○○ (20%)     │  │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [+ Add Domain]                                         │
│                                                         │
│  Folder Structure:                                      │
│  ○ Plain names (Concepts/, Patterns/, ...)             │
│  ● Numbered (01-Concepts/, 02-Patterns/, ...) ✓        │
│                                                         │
│                      [Back] [Create Domains]            │
└─────────────────────────────────────────────────────────┘
```

**Interaction:**
- Each domain is a card with inline editing
- [Edit] opens modal with full property editor
- [×] removes domain (with confirmation)
- [+ Add Domain] opens blank domain editor
- Radio buttons for folder structure preference
- Drag handles (⋮⋮) to reorder domains

#### Step 5: Domain Editor Modal (when editing/adding)

```
┌─────────────────────────────────────────────────────────┐
│                   Edit Domain                           │
│                                                         │
│  Name:        [Concepts_____________________]           │
│  Description: [Core programming concepts and theory___] │
│               [______________________________________]   │
│                                                         │
│  Appearance:                                            │
│  Icon: [💡 ▼]  Color: [■ #9b59b6] [Color picker]       │
│                                                         │
│  Organization:                                          │
│  Folder: [01-Concepts] (auto-generated from name)       │
│                                                         │
│  RAG Weight: [●●●○○○○○○○] 20%                          │
│  ℹ️  Higher weight = prioritized in search results      │
│                                                         │
│  Auto-tag Keywords: (AI suggested ✨)                   │
│  [concept ×] [theory ×] [principle ×] [algorithm ×]    │
│  [+ Add keyword]                                        │
│                                                         │
│                         [Cancel] [Save]                 │
└─────────────────────────────────────────────────────────┘
```

**Smart Suggestions (✨):**
- As user types name/description, AI suggests keywords
- Shows suggestions below input: "Suggested: [algorithm] [data structure] [paradigm]"
- User can click to add or ignore
- Based on semantic analysis of name + description

#### Step 6: Confirmation & Creation

```
┌─────────────────────────────────────────────────────────┐
│                   All Set! 🎉                           │
│                                                         │
│  Polly will create 5 domains in:                        │
│  ~/.polly/notes/                                        │
│                                                         │
│  ✓ Creating domain folders...                          │
│  ✓ Setting up RAG weights...                           │
│  ✓ Configuring auto-tagging...                         │
│  ✓ Initializing knowledge graph...                     │
│                                                         │
│  You can modify these anytime in Settings > Domains.    │
│                                                         │
│                    [Start Using Polly]                  │
└─────────────────────────────────────────────────────────┘
```

**Behind the scenes:**
1. Create `~/.polly/domains.json` with selected/customized domains
2. Create folder structure in `~/.polly/notes/`
3. Initialize RAG weights in Phase 2 system
4. Create template files in `~/.polly/notes/_Templates/` (basic note templates)
5. Set flag: `~/.polly/first_run_complete = true`

### Custom Template Flow

If user selects "Custom" template:

1. **Step 2a:** Explain custom setup
   - "You'll create your own domains from scratch"
   - "We recommend starting with 3-5 domains"
   
2. **Step 2b:** Guided domain creation
   - "What's your first domain?" → user enters name
   - AI suggests description, keywords based on name
   - Repeat for 2-4 more domains
   
3. **Step 2c:** Optional Obsidian analysis
   - "Do you have an existing Obsidian vault?"
   - If yes: detect vault, analyze content, suggest domains
   - "We found 127 notes. Here are suggested domains based on your content:"
     - Domain suggestions with note counts

4. Continue to Step 3 (Preview) with custom domains

---

## Smart Recommendations System

### 1. Auto-Tag Rule Suggestions (Semantic Analysis)

**When:** User creates or edits a domain

**How it works:**

1. **Input:** Domain name + description
2. **NLP Analysis:**
   - Extract key nouns and concepts
   - Identify domain/topic (using lightweight model or keyword extraction)
   - Generate related terms using word embeddings
3. **Suggestion:**
   - Return 5-10 relevant keywords
   - User can accept, edit, or reject

**Example:**

```
User creates domain: "Machine Learning"
Description: "ML algorithms, models, and techniques"

AI suggests keywords:
✓ machine learning
✓ neural network
✓ model
✓ training
✓ algorithm
✓ deep learning
○ artificial intelligence (user can add)
○ dataset (user can add)
```

**Implementation approach:**

```python
def suggest_auto_tag_keywords(name: str, description: str) -> list[str]:
    """
    Generate keyword suggestions using semantic analysis.
    
    Approach:
    1. Combine name + description into text
    2. Extract key terms (nouns, noun phrases)
    3. Generate related terms using word embeddings or LLM
    4. Filter for relevance and uniqueness
    5. Return top 5-10 suggestions
    """
    text = f"{name}. {description}"
    
    # Option A: Use spaCy for entity extraction + word vectors
    doc = nlp(text)
    key_terms = [chunk.text.lower() for chunk in doc.noun_chunks]
    
    # Option B: Use local LLM for suggestions
    prompt = f"Given this domain: '{name}' - {description}\nSuggest 8 keywords for auto-tagging content to this domain."
    keywords = llm.generate(prompt).split(',')
    
    # Combine and rank
    suggestions = rank_keywords(key_terms, keywords, text)
    return suggestions[:10]
```

**UI Integration:**

```
Auto-tag Keywords: (AI suggested ✨)
[concept ×] [theory ×] [principle ×] [algorithm ×]

Suggestions: [data structure] [paradigm] [programming]
             Click to add ↑

[+ Add keyword]
```

### 2. RAG Weight Recommendations

**When:** User creates domain or after 50 queries

**Initial Suggestion (on creation):**

- **Default:** Equal weights across all domains (e.g., 0.20 for 5 domains)
- **Semantic hints:** If domain name suggests technical content, slightly higher weight
  - "Code", "Implementation", "Technical" → 0.25
  - "Journal", "Thoughts", "Ideas" → 0.15
  - Others → 0.20
- Normalize to sum to 1.0

**Adaptive Suggestion (after 50 queries):**

```python
def suggest_rag_weight_adjustments(query_history: list, domains: list) -> dict:
    """
    Analyze query patterns and suggest RAG weight adjustments.
    
    Algorithm:
    1. Group queries by domain (which domain had best results)
    2. Calculate hit rate per domain
    3. Compare to current weights
    4. Suggest adjustments if misaligned
    """
    domain_hits = count_hits_per_domain(query_history)
    total_queries = len(query_history)
    
    suggestions = {}
    for domain in domains:
        hit_rate = domain_hits[domain.id] / total_queries
        current_weight = domain.ragWeight
        
        # If hit rate is much higher than weight, suggest increase
        if hit_rate > current_weight + 0.10:
            suggestions[domain.id] = {
                'current': current_weight,
                'suggested': min(hit_rate, current_weight + 0.15),
                'reason': f'{domain.name} is used in {hit_rate*100:.0f}% of queries but only weighted {current_weight*100:.0f}%'
            }
    
    return suggestions
```

**UI Notification:**

```
┌─────────────────────────────────────────────────────────┐
│  💡 RAG Weight Suggestion                               │
│                                                         │
│  After analyzing 50 queries, we noticed:                │
│                                                         │
│  • "Code" domain appears in 35% of results but is       │
│    only weighted 20%. Consider increasing to 30%.      │
│                                                         │
│  • "Journal" domain rarely matches your queries.        │
│    Consider decreasing from 20% to 10%.                │
│                                                         │
│                  [Review Weights] [Dismiss]             │
└─────────────────────────────────────────────────────────┘
```

### 3. Obsidian Import Clustering

**When:** User has existing Obsidian vault and chooses to import

**How it works:**

1. **Scan vault:** Find all `.md` files
2. **Extract content:** Read file contents, parse frontmatter, extract links
3. **Analyze topics:**
   - Generate embeddings for each note (using local model or simple TF-IDF)
   - Cluster notes into 3-7 groups (k-means clustering)
   - Identify cluster themes (most common terms in each cluster)
4. **Suggest domains:**
   - Each cluster → suggested domain name
   - Show sample notes from each cluster
5. **User review:**
   - Accept/reject/modify suggested domains
   - Assign notes to domains during import

**Example Flow:**

```
┌─────────────────────────────────────────────────────────┐
│        Analyzing Your Obsidian Vault...                 │
│                                                         │
│  Found 147 notes in ~/Documents/Obsidian/MyVault        │
│                                                         │
│  ████████████████░░░░ 80% - Clustering content...       │
└─────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────┐
│        Suggested Domains from Your Content              │
│                                                         │
│  We found these topic clusters in your notes:           │
│                                                         │
│  ✓ Cluster 1: "Python Development" (42 notes)          │
│    Sample notes: "Django Setup", "Python Decorators"    │
│    Suggested domain: 💻 Code                            │
│    [Edit name] [×]                                      │
│                                                         │
│  ✓ Cluster 2: "Machine Learning" (28 notes)            │
│    Sample notes: "Neural Networks", "Gradient Descent"  │
│    Suggested domain: 🧠 ML Concepts                     │
│    [Edit name] [×]                                      │
│                                                         │
│  ✓ Cluster 3: "Project Notes" (35 notes)               │
│    Sample notes: "Website Redesign", "API Migration"    │
│    Suggested domain: 📋 Projects                        │
│    [Edit name] [×]                                      │
│                                                         │
│  ○ Uncategorized (42 notes)                             │
│    [Create new domain for these]                        │
│                                                         │
│              [Back] [Customize] [Import with These]     │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
def analyze_vault_and_suggest_domains(vault_path: str) -> list[DomainSuggestion]:
    """
    Cluster Obsidian vault notes and suggest domain structure.
    """
    # 1. Read all notes
    notes = read_markdown_files(vault_path)
    
    # 2. Generate embeddings (simple approach: TF-IDF)
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    embeddings = vectorizer.fit_transform([n.content for n in notes])
    
    # 3. Cluster (k-means, optimal k via elbow method)
    from sklearn.cluster import KMeans
    k = find_optimal_clusters(embeddings, min_k=3, max_k=7)
    kmeans = KMeans(n_clusters=k)
    labels = kmeans.fit_predict(embeddings)
    
    # 4. Analyze each cluster
    suggestions = []
    for cluster_id in range(k):
        cluster_notes = [n for i, n in enumerate(notes) if labels[i] == cluster_id]
        
        # Extract common terms
        common_terms = get_top_terms_for_cluster(cluster_notes, vectorizer)
        
        # Suggest domain name (use most common term or LLM)
        suggested_name = suggest_domain_name(common_terms, cluster_notes)
        
        suggestions.append(DomainSuggestion(
            name=suggested_name,
            note_count=len(cluster_notes),
            sample_notes=cluster_notes[:5],
            keywords=common_terms
        ))
    
    return suggestions
```

### 4. Behavioral Learning (Future Enhancement)

**When:** After user manually tags 10+ notes to a domain

**How it works:**

1. **Track manual tagging:** When user moves note to domain or changes domain tag
2. **Analyze patterns:** 
   - What keywords appear frequently in notes user tags to this domain?
   - Are there terms user associates with this domain that aren't in auto-tag rules?
3. **Suggest new rules:**
   - "We noticed you often tag notes containing 'neural network' to ML domain. Add as auto-tag rule?"

**UI Notification:**

```
┌─────────────────────────────────────────────────────────┐
│  💡 Auto-tag Suggestion                                 │
│                                                         │
│  You've tagged 12 notes containing "neural network"     │
│  to your "ML Concepts" domain.                          │
│                                                         │
│  Add "neural network" as an auto-tag keyword?           │
│                                                         │
│                      [Add] [Not Now] [Never]            │
└─────────────────────────────────────────────────────────┘
```

### 5. Domain Relationship Suggestions (Future Enhancement)

**When:** Knowledge graph has sufficient data (Phase 12)

**How it works:**

1. **Analyze graph edges:** Which domains have notes that frequently link to each other?
2. **Identify patterns:**
   - "Code" domain notes often reference "Concepts" domain notes
   - "Projects" domain notes often reference "Documentation"
3. **Suggest relationships:**
   - "Should we link Code → Concepts in the graph?"
   - "This helps Polly include Concepts when answering Code questions"

---

## Color & Icon System

### Semantic Color Mapping

Default colors based on domain purpose:

| Purpose | Color | Hex | Use Cases |
|---------|-------|-----|-----------|
| Code/Implementation | Blue | `#3498db` | Code, Programming, Development |
| Concepts/Theory | Purple | `#9b59b6` | Concepts, Theory, Principles |
| Documentation | Green | `#27ae60` | Docs, Guides, References |
| Research/Data | Orange | `#e67e22` | Research, Data, Analysis |
| Creative/Design | Pink | `#e91e63` | Creative, Design, Art |
| Personal/Notes | Gray | `#95a5a6` | Personal, Notes, Journal |
| Projects/Tasks | Teal | `#16a085` | Projects, Tasks, Goals |
| Archive/Reference | Brown | `#795548` | Archive, History, Old |

### Color Palette (20 colors)

Users can choose from a curated palette:

**Primary Colors:**
- Red: `#e74c3c`
- Orange: `#e67e22`
- Yellow: `#f1c40f`
- Green: `#27ae60`
- Teal: `#16a085`
- Blue: `#3498db`
- Purple: `#9b59b6`
- Pink: `#e91e63`

**Neutral Colors:**
- Dark Gray: `#34495e`
- Gray: `#95a5a6`
- Light Gray: `#bdc3c7`
- Brown: `#795548`

**Additional Colors:**
- Lime: `#8bc34a`
- Cyan: `#00bcd4`
- Indigo: `#3f51b5`
- Deep Purple: `#673ab7`
- Amber: `#ffc107`
- Deep Orange: `#ff5722`
- Red-Pink: `#ff4081`
- Teal Dark: `#009688`

### Icon Library (50+ icons)

**Common icons by category:**

**General:**
- 📝 Note
- 💡 Idea/Concept
- 📄 Document
- 📁 Folder
- 📦 Archive
- 🗂️ Reference

**Technical:**
- 💻 Code
- ⌨️ Programming
- 🔧 Tool
- ⚙️ Settings
- 🏛️ Architecture
- 🔷 Pattern
- 🌐 Web

**Academic:**
- 📚 Books/Literature
- 🎓 Education
- 🔬 Science
- 📊 Data
- 📈 Analysis
- 🧪 Experiment
- ❓ Question

**Creative:**
- ✍️ Writing
- 🎨 Art
- 🎭 Theater/Drama
- 🎬 Film
- 🎵 Music
- 🌍 World
- 👤 Character

**Organization:**
- 🎯 Goal/Target
- 📋 List/Project
- 🔨 Build/Work
- 📌 Pin/Important
- 🚀 Launch/Start
- ✅ Complete
- ⏰ Time

**Abstract:**
- ⚡ Energy/Signal
- 🔥 Hot/Trending
- ⭐ Star/Favorite
- 💎 Gem/Value
- 🌟 Special
- 🔑 Key/Important
- 🎁 Gift/Bonus

Users can also enter any emoji character directly.

---

## Folder Structure

### Two Modes

Users choose folder naming convention in first-run wizard:

#### Mode 1: Numbered (Default)

```
~/.polly/notes/
├── _Drafts/              # Special folder for review queue
├── _Templates/           # Note templates
├── attachments/          # Images, PDFs, etc.
├── 01-Concepts/
├── 02-Patterns/
├── 03-Documentation/
├── 04-Code/
└── 05-Architecture/
```

**Benefits:**
- Explicit ordering
- Easy to see structure at a glance
- Natural sort in file browsers

#### Mode 2: Plain Names

```
~/.polly/notes/
├── _Drafts/
├── _Templates/
├── attachments/
├── Architecture/
├── Code/
├── Concepts/
├── Documentation/
└── Patterns/
```

**Benefits:**
- Cleaner names
- Easier to type
- More flexible (no need to renumber when reordering)

### Special Folders

Two folders have special meaning and always start with `_`:

- **`_Drafts/`** - Review queue for AI-generated notes (Phase 11)
- **`_Templates/`** - Note templates for quick creation

These folders:
- Don't correspond to domains
- Are excluded from RAG indexing (unless user explicitly includes a draft)
- Have special UI treatment (different icons, separate sections)

### Folder Path Generation

When user creates a domain, folder path is auto-generated:

```python
def generate_folder_path(domain_name: str, order: int, use_numbering: bool) -> str:
    """
    Generate folder path from domain name.
    
    Rules:
    - Remove special characters
    - Replace spaces with hyphens
    - Add number prefix if numbering enabled
    - Ensure uniqueness
    """
    # Sanitize name
    safe_name = re.sub(r'[^\w\s-]', '', domain_name)
    safe_name = re.sub(r'[\s]+', '-', safe_name)
    
    # Add number prefix if enabled
    if use_numbering:
        return f"{order:02d}-{safe_name}"
    else:
        return safe_name

# Examples:
generate_folder_path("Machine Learning", 3, True)   → "03-Machine-Learning"
generate_folder_path("ML Concepts", 3, False)        → "ML-Concepts"
```

### Changing Folder Structure

User can change numbering preference in settings:

1. **Disable numbering:** Rename all folders to remove prefixes
2. **Enable numbering:** Rename all folders to add prefixes based on current order

**Migration handled gracefully:**
- Update `domains.json` with new folder paths
- Rename physical folders on disk
- Update all wiki-links in notes (if any reference folder names)
- Update RAG index with new paths
- Log any errors (e.g., naming conflicts)

---

## Settings Panel UI

### Settings Location

Accessible via: **Settings > Domains**

### UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  Settings                                               │
├──────────────┬──────────────────────────────────────────┤
│  General     │  Domains                                 │
│  Domains  ✓  │                                          │
│  Models      │  Folder Structure:                       │
│  Integrations│  ● Numbered (01-Name/)                   │
│  Advanced    │  ○ Plain (Name/)                         │
│              │  [Apply Changes]                         │
│              │                                          │
│              │  Your Domains:                           │
│              │                                          │
│              │  ┌─────────────────────────────────────┐│
│              │  │ ⋮⋮ 💡 Concepts               [Edit] ││
│              │  │    Core concepts and theory         ││
│              │  │    Folder: 01-Concepts              ││
│              │  │    Weight: ●●●○○ 20%                ││
│              │  │    Keywords: concept, theory... +5  ││
│              │  └─────────────────────────────────────┘│
│              │                                          │
│              │  ┌─────────────────────────────────────┐│
│              │  │ ⋮⋮ 🔷 Patterns               [Edit] ││
│              │  │    Design patterns and practices    ││
│              │  │    Folder: 02-Patterns              ││
│              │  │    Weight: ●●●○○ 20%                ││
│              │  │    Keywords: pattern, design... +3  ││
│              │  └─────────────────────────────────────┘│
│              │                                          │
│              │  [+ Add Domain]                         │
│              │                                          │
│              │  [Reset to Template ▼] [Export] [Import]│
└──────────────┴──────────────────────────────────────────┘
```

### Domain Card (Collapsed State)

```
┌─────────────────────────────────────────────────────────┐
│ ⋮⋮ 💡 Concepts                                  [Edit] │
│    Core concepts and theory                            │
│    Folder: 01-Concepts  │  Weight: ●●●○○ 20%           │
│    Keywords: concept, theory, principle, algorithm +3  │
└─────────────────────────────────────────────────────────┘
```

**Interactions:**
- **⋮⋮** (drag handle) - Reorder domains (changes order number)
- **[Edit]** - Open edit modal
- **Click card** - Expand/collapse details

### Domain Card (Expanded State)

```
┌─────────────────────────────────────────────────────────┐
│ ⋮⋮ 💡 Concepts                            [Edit] [Delete]│
│    Core concepts and theory                            │
│                                                        │
│  Details:                                              │
│  • Folder: ~/.polly/notes/01-Concepts/                 │
│  • Created: Jan 15, 2026                               │
│  • Modified: Jan 20, 2026                              │
│  • Notes in this domain: 42                            │
│                                                        │
│  RAG Weight: ●●●○○○○○○○ 20%                           │
│  Higher weight = prioritized in search                 │
│                                                        │
│  Auto-tag Keywords:                                    │
│  [concept ×] [theory ×] [principle ×] [algorithm ×]   │
│  [data structure ×] [paradigm ×]                       │
│                                                        │
│  [+ Add keyword]                                       │
│                                                        │
│  Recent notes in this domain:                          │
│  • Object-Oriented Programming (Jan 20)                │
│  • Functional Composition (Jan 18)                     │
│  • SOLID Principles (Jan 15)                           │
│  [View all →]                                          │
└─────────────────────────────────────────────────────────┘
```

### Edit Domain Modal

Same as first-run wizard edit modal (see above).

### Bulk Operations

**Reset to Template:**
- Dropdown menu: "Software Development", "Research", "Writing", etc.
- Confirmation: "This will replace your current domains. Continue?"
- Option: "Keep existing notes and map to new domains" vs "Start fresh"

**Export:**
- Saves `domains.json` to user-selected location
- Can share with other Polly users

**Import:**
- Load `domains.json` from file
- Preview changes before applying
- Option to merge or replace

---

## Integration Points

Phase 1.5 provides the domain system used by all other phases:

### Phase 2: RAG System

**How domains are used:**

1. **Document chunking:** Each note is tagged with its domain
2. **Retrieval weighting:** Use `ragWeight` to prioritize domains in search results
3. **Query routing:** Match query to relevant domains using auto-tag rules

**Example:**
```python
def retrieve_chunks(query: str, domains: list[Domain]) -> list[Chunk]:
    """
    Retrieve relevant chunks, weighted by domain.
    """
    # Match query to domains
    relevant_domains = match_query_to_domains(query, domains)
    
    # Get chunks from all domains
    all_chunks = get_all_chunks(query)
    
    # Re-weight by domain
    for chunk in all_chunks:
        domain = get_domain_for_chunk(chunk)
        if domain in relevant_domains:
            chunk.score *= domain.ragWeight * 1.5  # Boost relevant domains
        else:
            chunk.score *= domain.ragWeight
    
    return sorted(all_chunks, key=lambda c: c.score, reverse=True)[:10]
```

### Phase 11: Multi-Model + Intelligent Routing

**How domains are used:**

1. **Meta-query generation:** Suggest which domain a new note should go in
2. **Auto-tagging:** Use domain auto-tag rules to categorize AI-generated content
3. **Confidence scoring:** Domain match affects pre-flight confidence

**Example:**
```python
def suggest_domain_for_note(note_content: str, domains: list[Domain]) -> Domain:
    """
    Suggest best domain for AI-generated note.
    """
    scores = {}
    for domain in domains:
        score = 0
        for keyword in domain.autoTagRules:
            if keyword.lower() in note_content.lower():
                score += 1
        scores[domain.id] = score
    
    best_domain_id = max(scores, key=scores.get)
    return get_domain_by_id(best_domain_id)
```

### Phase 12: Knowledge Graph

**How domains are used:**

1. **Node coloring:** Nodes colored by their domain
2. **Clustering:** Group nodes by domain in visualization
3. **Filtering:** Show/hide domains in graph view

**Example:**
```python
def render_knowledge_graph(nodes: list[Node], domains: list[Domain]):
    """
    Render graph with domain-based coloring.
    """
    for node in nodes:
        domain = get_domain_for_note(node.note_id)
        node.color = domain.color
        node.icon = domain.icon
    
    # Group by domain
    clusters = group_by_domain(nodes, domains)
    
    # Render with domain legend
    render_graph(nodes, clusters, domain_legend=domains)
```

### Phase 13: Pattern Learning

**How domains are used:**

1. **Pattern categorization:** Patterns tagged with domain
2. **Context-aware suggestions:** Suggest patterns from relevant domain

**Example:**
```python
def learn_pattern(code: str, context: dict) -> Pattern:
    """
    Learn coding pattern and tag with domain.
    """
    pattern = extract_pattern(code)
    
    # Determine domain based on context
    if context.get('file_path'):
        note = find_related_note(context['file_path'])
        if note:
            pattern.domain = note.domain
    
    return pattern
```

### Phase 14: Mental Models

**How domains are used:**

1. **Model-domain associations:** Mental models can be specific to domains
2. **Application suggestions:** "Apply SOLID principles to Code domain"

**Example:**
```python
class MentalModel:
    name: str
    description: str
    applicable_domains: list[str]  # List of domain IDs
    
    def applies_to_domain(self, domain_id: str) -> bool:
        return domain_id in self.applicable_domains or not self.applicable_domains

# SOLID principles apply to Code, Patterns domains
solid = MentalModel(
    name="SOLID Principles",
    applicable_domains=["code", "patterns"]
)
```

### Phase 16: Native Notes

**How domains are used:**

1. **Folder structure:** Notes organized in domain folders
2. **Auto-tagging:** New notes auto-tagged to domain based on content
3. **Navigation:** Browse notes by domain

**Example:**
```python
def auto_tag_note_to_domain(note: Note, domains: list[Domain]) -> Domain:
    """
    Automatically suggest domain for a note based on content.
    """
    content_lower = note.content.lower()
    
    scores = {}
    for domain in domains:
        score = sum(1 for keyword in domain.autoTagRules if keyword in content_lower)
        scores[domain.id] = score
    
    if max(scores.values()) > 0:
        return get_domain_by_id(max(scores, key=scores.get))
    else:
        return None  # User must manually assign
```

### Phase 17: Code Workspace

**How domains are used:**

1. **Code → Note creation:** Suggest domain when creating note from code
2. **Context inclusion:** Include notes from relevant domains in context

**Example:**
```python
def create_note_from_code(code: str, file_path: str, domains: list[Domain]) -> Note:
    """
    Create a note from code snippet, suggest domain.
    """
    # Analyze code to determine domain
    if is_implementation(code):
        suggested_domain = get_domain_by_name("Code")
    elif is_pattern(code):
        suggested_domain = get_domain_by_name("Patterns")
    else:
        suggested_domain = get_domain_by_name("Concepts")
    
    note = generate_note_from_code(code, file_path)
    note.suggested_domain = suggested_domain
    
    return note
```

---

## Implementation Timeline

**Total Duration:** 5 days

### Day 1-2: Data Model & Storage (2 days)

**Tasks:**
- Define domain data model (TypeScript interfaces)
- Implement `domains.json` storage and loading
- CRUD operations:
  - `createDomain(domain: Domain): Promise<Domain>`
  - `getDomain(id: string): Promise<Domain>`
  - `updateDomain(id: string, updates: Partial<Domain>): Promise<Domain>`
  - `deleteDomain(id: string): Promise<void>`
  - `listDomains(): Promise<Domain[]>`
  - `reorderDomains(order: string[]): Promise<void>`
- Validation functions
- Migration from hardcoded domains (if existing Polly installation)

**Acceptance criteria:**
- ✓ Can create, read, update, delete domains
- ✓ Data persists across app restarts
- ✓ Validation prevents invalid data

### Day 3: First-Run Wizard (1 day)

**Tasks:**
- Detect first run (`~/.polly/first_run_complete` flag)
- Implement wizard UI (6 screens):
  - Welcome
  - Template selection
  - Preview
  - Customization
  - Confirmation
  - Success
- Implement template system (6 predefined templates)
- Create domain folders on disk
- Set first-run flag

**Acceptance criteria:**
- ✓ Wizard appears on first run
- ✓ User can select template and customize
- ✓ Domains created successfully
- ✓ Folders created in `~/.polly/notes/`

### Day 4: Settings Panel & UI (1 day)

**Tasks:**
- Settings panel UI:
  - Domain list (with drag-to-reorder)
  - Domain cards (collapsed and expanded states)
  - Edit domain modal
  - Add domain flow
  - Delete domain (with confirmation)
- Folder structure preference toggle
- Bulk operations (reset, export, import)
- Real-time updates (domains list updates when modified)

**Acceptance criteria:**
- ✓ Can view all domains in settings
- ✓ Can edit any domain property
- ✓ Can add/delete domains
- ✓ Can reorder domains
- ✓ Can change folder structure mode

### Day 5: Smart Recommendations (1 day)

**Tasks:**
- Implement auto-tag keyword suggestions:
  - Semantic analysis of domain name/description
  - Keyword extraction
  - UI for showing suggestions
- Implement RAG weight suggestions:
  - Equal weights by default
  - Semantic hints based on domain name
  - UI for adjusting weights
- Implement Obsidian vault clustering (optional, for custom template):
  - Vault scanning
  - Content clustering (k-means on TF-IDF embeddings)
  - Domain suggestions from clusters
  - UI for reviewing suggestions

**Acceptance criteria:**
- ✓ AI suggests keywords when creating domain
- ✓ RAG weights are reasonable by default
- ✓ (If Obsidian vault exists) Can analyze and suggest domains

---

## Success Criteria

Phase 1.5 is complete when:

1. **First-run experience:**
   - ✓ New users see domain setup wizard
   - ✓ Can choose from 6 templates or custom
   - ✓ Can customize domains before creating
   - ✓ Domains created successfully with folders

2. **Domain management:**
   - ✓ Can view all domains in settings
   - ✓ Can create new domains
   - ✓ Can edit any domain property
   - ✓ Can delete domains (with safety checks)
   - ✓ Can reorder domains (drag-and-drop)

3. **Smart features:**
   - ✓ AI suggests auto-tag keywords
   - ✓ RAG weights are balanced and adjustable
   - ✓ Folder structure is clean and organized
   - ✓ (Optional) Obsidian vault analysis works

4. **Integration:**
   - ✓ Phase 2 (RAG) uses domain weights
   - ✓ Phase 11 (Multi-model) uses domains for meta-query
   - ✓ Phase 16 (Notes) uses domains for folder structure
   - ✓ All other phases can access domain configuration

5. **User experience:**
   - ✓ Wizard is intuitive and fast (<5 min)
   - ✓ Settings panel is easy to navigate
   - ✓ Changes apply immediately
   - ✓ No data loss when modifying domains

---

## Future Enhancements

### Phase 1.5b: Advanced Domain Features (2-3 days)

Potential future additions:

1. **Behavioral Learning:**
   - Track manual tagging patterns
   - Suggest new auto-tag rules after 10+ manual tags
   - Improve suggestions over time

2. **Domain Relationships:**
   - Define relationships between domains (parent/child, related)
   - Use relationships in knowledge graph
   - "Code implements Concepts", "Projects use Patterns"

3. **Smart Domain Merging:**
   - Detect overlapping domains
   - Suggest merging similar domains
   - Handle note migration

4. **Domain Analytics:**
   - Dashboard showing domain usage
   - Most active domains
   - Growth over time
   - Underutilized domains

5. **Advanced Templates:**
   - Community template marketplace
   - Import/export templates
   - Template versioning

6. **Multi-level Domains:**
   - Sub-domains (hierarchical structure)
   - "Code/Python", "Code/JavaScript"
   - Nested folder structure

---

## Technical Notes

### Storage Format

`~/.polly/domains.json`:

```json
{
  "version": "1.0",
  "folderNumbering": true,
  "domains": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Concepts",
      "description": "Core programming concepts and theory",
      "color": "#9b59b6",
      "icon": "💡",
      "folderPath": "01-Concepts",
      "ragWeight": 0.20,
      "autoTagRules": [
        "concept",
        "theory",
        "principle",
        "algorithm",
        "data structure"
      ],
      "created": "2026-01-23T10:00:00Z",
      "modified": "2026-01-23T10:00:00Z",
      "order": 1
    }
  ],
  "templates": [
    {
      "id": "software-development",
      "name": "Software Development",
      "description": "For developers and engineers",
      "domains": [ /* ... */ ]
    }
  ],
  "lastModified": "2026-01-23T10:00:00Z"
}
```

### TypeScript Interfaces

```typescript
interface Domain {
  id: string;  // UUID v4
  name: string;  // 1-30 chars
  description: string;  // 0-200 chars
  color: string;  // Hex color
  icon: string;  // Emoji
  folderPath: string;  // Relative path
  ragWeight: number;  // 0.0-1.0
  autoTagRules: string[];  // Lowercase keywords
  created: string;  // ISO 8601
  modified: string;  // ISO 8601
  order: number;  // Sort order
}

interface DomainConfig {
  version: string;
  folderNumbering: boolean;
  domains: Domain[];
  templates: DomainTemplate[];
  lastModified: string;
}

interface DomainTemplate {
  id: string;
  name: string;
  description: string;
  domains: Omit<Domain, 'id' | 'created' | 'modified'>[];
}
```

### API Functions

```typescript
class DomainManager {
  // CRUD operations
  async createDomain(domain: Omit<Domain, 'id' | 'created' | 'modified'>): Promise<Domain>;
  async getDomain(id: string): Promise<Domain | null>;
  async updateDomain(id: string, updates: Partial<Domain>): Promise<Domain>;
  async deleteDomain(id: string): Promise<void>;
  async listDomains(): Promise<Domain[]>;
  
  // Ordering
  async reorderDomains(domainIds: string[]): Promise<void>;
  
  // Templates
  async getTemplates(): Promise<DomainTemplate[]>;
  async applyTemplate(templateId: string): Promise<void>;
  
  // Folder structure
  async setFolderNumbering(enabled: boolean): Promise<void>;
  async migrateFolderStructure(): Promise<void>;
  
  // Smart features
  async suggestKeywords(name: string, description: string): Promise<string[]>;
  async suggestDomainsFromVault(vaultPath: string): Promise<DomainSuggestion[]>;
  async normalizeRAGWeights(): Promise<void>;
  
  // Validation
  validateDomain(domain: Partial<Domain>): ValidationResult;
  isNameUnique(name: string, excludeId?: string): boolean;
}
```

---

## Dependencies

**Phase 1.5 depends on:**
- Phase 1: Basic Chat UI (for settings panel location)
- Phase 2: RAG System (will use domain weights)

**Phase 1.5 enables:**
- Phase 11: Multi-Model (domain suggestions for meta-query notes)
- Phase 12: Knowledge Graph (domain-based coloring and clustering)
- Phase 13: Pattern Learning (domain tagging for patterns)
- Phase 14: Mental Models (domain associations for models)
- Phase 16: Native Notes (domain-based folder structure)
- Phase 17: Code Workspace (domain suggestions for code→note)

---

## References

- MASTER_ROADMAP.md - Overall project plan
- PHASE2_RAG_IMPLEMENTATION.md - RAG system that uses domain weights
- PHASE11_MULTI_MODEL_ENHANCED.md - Meta-query domain suggestions
- PHASE16_NATIVE_NOTES.md - Note organization using domains
- PHASE_STATUS_SUMMARY.md - Current implementation status

---

**End of Phase 1.5 specification**
