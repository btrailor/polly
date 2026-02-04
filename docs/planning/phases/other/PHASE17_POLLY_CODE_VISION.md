# Phase 17: Polly Code - Complete Vision Document

**Status:** 📋 Planned (Expansion of Phase 17)  
**Priority:** CRITICAL (Major Differentiator)  
**Estimated Effort:** 14-18 weeks (4-part implementation)  
**Target Date:** Q2-Q3 2026  
**Depends On:** Phase 13b (Profiles), Phase 24 (Orchestrator), Phase 27 (Designer)

---

**Document Purpose:** This is a comprehensive vision document that expands the existing Phase 17 (Code Workspace) into a full integrated development environment with Polly's unique advantages.

---

## Table of Contents

**Part 1: Executive Vision** (Pages 1-10)
- Executive Summary
- The Problem with Current AI Code Editors
- The Polly Code Solution
- Relationship to Phase 17 Foundation
- Success Visualization

**Part 2: Core Differentiation** (Pages 11-22)
- Context Beyond Code
- Designer-Coder Integration
- Edge-Native Advantages
- Polymathic Coding Workflows
- Competitive Analysis

**Part 3: Technical Architecture** (Pages 23-37)
- Why Monaco Over VSCode Fork
- Monaco Editor Foundation
- Custom IDE Shell Architecture
- Language Intelligence Layer
- RAG Pipeline Integration
- Persona System Integration
- Profile-Aware Coding
- System Architecture Diagram

**Part 4: User Experience** (Pages 38-47)
- User Personas
- Day-in-the-Life Scenarios
- UI/UX Wireframes
- Designer-Coder Workflow
- Interaction Patterns

**Part 5: Implementation Roadmap** (Pages 48-57)
- Phase 17a: Monaco Foundation
- Phase 17b: Language Intelligence
- Phase 17c: RAG & Polly Integration
- Phase 17d: Designer-Coder Integration
- Timeline & Resources
- Dependencies
- Risk Assessment

**Part 6: Future Vision** (Pages 58-62)
- Beyond MVP
- Plugin Ecosystem
- Research Questions
- Long-term Market Position

---

# PART 1: EXECUTIVE VISION

## 1. Executive Summary

### Vision in One Sentence

**Polly Code transforms coding from interacting with a codebase to conversing with your entire knowledge system—where documentation, design philosophy, past decisions, and domain expertise are as accessible as the code itself.**

### The Core Differentiator

Every AI code editor today treats **code as the primary context**. Cursor, GitHub Copilot, Windsurf—they're brilliant at understanding your codebase. They parse imports, suggest completions, and understand dependencies.

But they don't know:

- **Why you made that architectural decision** (it's in your design notes)
- **The constraint-based thinking that guides your design** (Bogost's influence on your work)
- **How your audio programming patterns inform your visual code** (cross-domain learning from Signals to Sigils)
- **What you learned from the SuperCollider book last month** (epub vectors in your vault)
- **Your philosophy about "instruments not tracks"** (documented in your Scrolls domain)

**Polly Code knows all of this.** Because in Polly, code isn't siloed from knowledge—it's woven into it.

### What Makes This Possible

1. **Edge-Native RAG Architecture**
   - Your epub vectors, notes, and domain knowledge live alongside code
   - Sub-100ms local retrieval (faster than cloud API round-trips)
   - Full privacy—your code never leaves your machine

2. **Polymathic Context**
   - Signals (audio) + Sigils (code) + Scrolls (philosophy) + Sights (visual) + Glyphs (systems) inform each other
   - Cross-domain learning: Your norns instruments inform React components
   - Institutional memory: Not just *what* changed (git) but *why* (your documented reasoning)

3. **Designer-Coder Integration**
   - Constraint-based design → implementation → feedback loops
   - Living specs that evolve with code
   - Visual-to-code pipeline guided by design philosophy

4. **Profile-Aware Coding**
   - Learns your style, mental models, domain expertise (Phase 13b)
   - Adapts suggestions to your communication preferences
   - Remembers your "why" across projects

5. **Persona-Orchestrated Workflows**
   - Architect → Designer → Coder → Scribe coordination
   - Each persona brings specialized expertise
   - Seamless handoffs with full context preservation

### Build Approach: Monaco + Custom Shell

After extensive research evaluating VSCode forks, Zed, Helix, Lapce, and Neovim, the clear winner is:

**Monaco Editor (VSCode's editor component) + Custom IDE Shell**

**Why Monaco:**
- ✅ Production-ready (powers VSCode, GitHub, Azure DevOps)
- ✅ Just the editor, no IDE baggage
- ✅ MIT licensed, no restrictions
- ✅ Perfect match for Polly's TypeScript/Electron stack
- ✅ 3-5 month timeline to functional IDE
- ✅ Deep integration with RAG/personas possible
- ✅ No VSCode fork maintenance burden
- ✅ LSP support via `monaco-languageclient`
- ✅ Already familiar (Polly uses Monaco for Notes in Phase 16)

**What You Build:**
- File tree with git status
- Tab management
- Terminal integration (xterm.js)
- Status bar
- Settings UI
- **Polly-specific:** RAG results display, persona UI, chat interface, profile integration

**What Monaco Provides:**
- Text editing core
- Syntax highlighting
- IntelliSense
- Find/replace
- Diff editor
- Keyboard shortcuts
- Accessibility

### Relationship to Existing Phase 17

The current Phase 17 spec (PHASE17_CODE_WORKSPACE.md) provides the **foundation**:

✅ **Already Specified:**
- Monaco editor integration approach
- File tree with git status
- Integrated terminal (xterm.js)
- Git operations UI
- Basic chat panel with context
- Timeline: 3 weeks

**This Vision Document Expands Phase 17:**

We transform the 3-week basic workspace into a **4-part phased implementation**:

- **Phase 17a: Foundation** (2-3 weeks)
  - Everything from current Phase 17
  - Monaco editor, file tree, terminal, git ops
  
- **Phase 17b: Language Intelligence** (3-4 weeks)
  - LSP integration via `monaco-languageclient`
  - tree-sitter for enhanced parsing
  - IntelliSense and diagnostics
  
- **Phase 17c: RAG & Polly Integration** (4-5 weeks)
  - Epub vector pipeline to editor
  - Cross-domain retrieval in coding context
  - Institutional memory integration
  
- **Phase 17d: Designer-Coder Integration** (5-6 weeks)
  - Designer persona UI in editor
  - Spec → Code workflow
  - Visual-to-code pipeline

**Total Timeline:** 14-18 weeks (vs original 3 weeks)

This isn't scope creep—it's **scope clarity**. The original Phase 17 was too limited. This vision realizes what Polly Code should be.

### Market Context

**The AI Code Editor Landscape (2026):**

- **Cursor:** VSCode fork, $400M valuation, codebase-only context
- **GitHub Copilot:** Microsoft-owned, cloud-based, $10/month
- **Windsurf:** New entrant, AI-native, codebase-focused
- **Cline:** Assistant-based, VSCode extension

**All share the same limitation:** Code is the primary context.

**Meanwhile, personalized AI is emerging:**

- **Uare.ai:** Raised $10.3M for "Human Life Model"
  - Cloud SaaS, proprietary containers
  - Identity replication for monetization
  - Subscription model

**Polly's Positioning:**

> **"Context that thinks like you do"**
>
> Polly Code isn't just another AI code editor. It's the first IDE that treats your entire knowledge system—documentation, design philosophy, past decisions, domain expertise—as equal to the codebase itself.
>
> **Personal AI you own** (not rent). **Edge-native** (not cloud-dependent). **Practice augmentation** (not identity replication).

---

## 2. The Problem with Current AI Code Editors

### The Codebase-Only Context Trap

Cursor, Copilot, and Windsurf excel at understanding your codebase:
- ✅ Parse code structure
- ✅ Understand dependencies and imports
- ✅ Suggest completions based on surrounding code
- ✅ Know what functions are called where

But this creates a fundamental limitation: **They only know what's in the code.**

### Real-World Friction Examples

#### Example 1: The SuperCollider Developer

**Scenario:** You're building a feedback delay in SuperCollider with cross-channel routing.

**With Cursor:**
```
You: "Create a feedback delay with cross-channel routing"

Cursor searches:
- Your current .scd file
- Other SuperCollider files in project
- Maybe GitHub examples

Cursor suggests:
Generic feedback delay code from common patterns
```

**The Problem:**
- Cursor doesn't know you read Eli Fieldsteel's SuperCollider Book Chapter 7
- Cursor doesn't know your "Audio Routing Patterns" note has your preferred cross-channel approach
- Cursor doesn't know your Phemto project used similar feedback patterns successfully
- Cursor doesn't connect this to your "Feedback as Compositional Material" essay

**With Polly Code:**
```
You: "Create a feedback delay using Fieldsteel Chapter 7 technique with my cross-channel routing pattern"

Polly retrieves:
1. Eli Fieldsteel SuperCollider Book Chapter 7 (epub vector)
2. Your "Audio Routing Patterns" note (Signals domain)
3. Your Phemto project feedback code (Sigils domain)
4. Your "Feedback as Compositional Material" essay (Scrolls domain)

Polly suggests:
Code combining Fieldsteel's technique + your routing pattern + your compositional philosophy

Polly auto-annotates:
"Based on Fieldsteel Ch7 feedback approach, using your preferred cross-channel routing from Phemto, aligned with your 'feedback as compositional material' principle"
```

**The Difference:** Context compounds instead of being repeatedly lost.

#### Example 2: The norns Script Developer

**Scenario:** You're designing a sequencer for a norns instrument.

**With Cursor:**
```
You: "Design a sequencer for this norns instrument"

Cursor sees:
- Your Lua code
- norns API (if in codebase)
- Maybe norns documentation online

Cursor suggests:
"Here's a basic clock-driven sequencer with fixed step counts..."
```

**The Problem:**
- Doesn't know you prefer event-based over clock-based sequencing
- Doesn't know Euclidean patterns fit your workflow
- Doesn't know your "instruments not tracks" principle
- Doesn't connect to your p5.js rhythm visualization work
- Doesn't understand your modular system design philosophy

**With Polly Code:**
```
You: "Design a sequencer for this instrument"

Polly analyzes across domains:

Sigils (Code):
- Your Lua patterns
- norns API knowledge

Signals (Audio):
- "Prefer event-based over clock-based sequencing"
- "Euclidean patterns fit my workflow"

Sights (Visual):
- Your p5.js rhythm visualization sketches
- "Visual rhythm informs temporal structure"

Scrolls (Philosophy):
- "Instruments not tracks" principle
- Notes on Bogost's constraint-based design
- "Emergent vs prescribed patterns" essay

Glyphs (Systems):
- Your modular system design approach
- Composition over inheritance preference

Polly suggests:
"Based on your 'instruments not tracks' philosophy and preference for emergent patterns, I suggest an event-based sequencer with Euclidean pattern generation. This matches your visual rhythm work in p5.js and your modular system design principles.

Here's a structure using norns' `clock.run()` with event triggering:
[code follows...]

This approach allows patterns to emerge rather than being prescribed, aligned with your constraint-based design thinking."
```

**The Difference:** One suggestion understands your thinking. The other just knows Lua.

#### Example 3: The Architecture Decision

**Scenario:** Six months ago you refactored Two Tangles. Now you're looking at the code again.

**With Cursor + Git:**
```
You: "Why is this structured with a separate audio module and event bus?"

Git history shows:
commit a3b4c5d
Refactor Two Tangles architecture

Move audio processing to separate module
Add event bus for parameter changes
Extract pattern generators
```

**The Problem:** Git tells you *what* changed, not *why*.

**With Polly Code + Institutional Memory:**
```
You: "Why is this structured with a separate audio module and event bus?"

Polly retrieves your actual design note:

---
Two Tangles Architecture Decision
Date: [6 months ago]
Domain: Signals

I'm refactoring Two Tangles to separate concerns:

WHY:
- Current monolithic structure makes it hard to test audio processing
- Want to experiment with different pattern generators independently
- Event bus allows future parameter automation without coupling

CONSIDERED:
- Option A: Keep monolithic (simple but inflexible)
- Option B: Full plugin architecture (over-engineered)
- Option C: Module separation with event bus (CHOSEN)

REASONING:
Aligns with my "modular instruments" philosophy. Event bus pattern worked well in Phemto—proven approach. Avoids premature abstraction while enabling future extensibility.

CONSTRAINTS:
- Must maintain <10ms audio latency
- norns CPU budget is tight
- Want to keep Lua memory footprint low

OUTCOME:
Architecture supports independent testing, parameter automation path clear, pattern generators now reusable across projects.
---

Polly: "Six months ago you chose module separation with an event bus because it balanced flexibility with simplicity. You specifically avoided full plugin architecture as over-engineering, and the event bus pattern had worked well in Phemto. The key constraints were <10ms latency and low memory usage on norns."
```

**The Difference:** Institutional memory preserves the *why*, not just the *what*.

### The Cost of Context Switching

**Current Workflow (Without Polly Code):**

1. Open VSCode for code
2. Open SuperCollider Book PDF in Preview
3. Switch to Obsidian to check your notes on UGens
4. Back to VSCode to implement
5. Google for similar patterns
6. Find example on SC forum
7. Copy back to VSCode
8. **Lose context** about why Fieldsteel's approach was better
9. Come back tomorrow, **forgot** which tutorial technique you were using
10. Re-search everything

**Time wasted:** 20-30% of coding time is context switching and re-finding information

**With Polly Code:**

1. Open Polly Code
2. Type: "Create feedback delay with Fieldsteel Ch7 + my cross-channel routing"
3. Polly retrieves all relevant context automatically
4. Suggests code combining all sources
5. You accept, modify, iterate
6. Save with automatic annotation linking to source materials

**Context never leaves. Knowledge compounds. Flow state maintained.**

---

## 3. The Polly Code Solution

### Context Beyond Code: The Three Pillars

#### Pillar 1: Documentation as First-Class Context

**The Principle:** Epub vectors aren't auxiliary—they're the actual substrate you learn from.

**How It Works:**

When you're coding in SuperCollider, Polly's retrieval space includes:
- ✅ Your current .scd file
- ✅ Related SuperCollider files in your project
- ✅ **SuperCollider Book (epub, fully vectorized)**
- ✅ **Eli Fieldsteel tutorials (epub, fully vectorized)**
- ✅ **YOUR notes on "Audio Routing Patterns" (Signals domain)**
- ✅ **YOUR norns scripts using similar routing (Sigils domain)**
- ✅ **YOUR essay "Feedback as Compositional Material" (Scrolls domain)**

**Competitive Advantage:**

| Feature | Cursor | Copilot | Windsurf | **Polly Code** |
|---------|--------|---------|----------|----------------|
| Codebase understanding | ✅ Excellent | ✅ Good | ✅ Excellent | ✅ Excellent |
| Documentation retrieval | ⚠️ If in codebase | ❌ No | ⚠️ Basic | ✅ **Epub vectors** |
| Your notes/philosophy | ❌ No | ❌ No | ❌ No | ✅ **First-class** |

**Real Example:**

```
SuperCollider Coding Session:

User: "How do I create a feedback delay with cross-channel routing?"

Cursor's Context:
- Your current SC file
- Related SC files in project
- Maybe GitHub SuperCollider examples

Polly's Context:
- Your current SC file
- Related SC files
- SuperCollider Book Chapter 8 (UGens): "LocalOut and LocalIn for feedback paths"
- Fieldsteel Tutorial 6: "Delay techniques with cross-channel modulation"
- YOUR note "Audio Routing Patterns": "Prefer LocalBuf for cleaner routing"
- YOUR norns Phemto script: Similar routing pattern (lines 45-67)
- YOUR essay "Feedback as Compositional Material": Design philosophy

Result: Polly suggests code that combines official docs + your preferred patterns + your philosophy
```

#### Pillar 2: Cross-Domain Learning (Polymathic Context)

**The Principle:** Your work in one domain informs work in another. Polly makes these connections explicit.

**The Five Domains:**

1. **Sigils** (Code): Programming, systems, infrastructure
2. **Signals** (Audio): SuperCollider, norns, synthesis, audio programming
3. **Scrolls** (Writing/Philosophy): Essays, design thinking, theoretical frameworks
4. **Sights** (Visual): p5.js, Processing, visual design, UI/UX
5. **Glyphs** (Systems Thinking): Architecture, meta-organization, patterns

**Cross-Domain Inference Example:**

```
Scenario: Building a norns sequencer

Task: "Design a sequencer for this norns instrument"

Cursor Sees:
├─ Your Lua code (Sigils)
└─ norns API docs (if in context)

Polly Sees:
├─ Sigils (Code)
│  ├─ Your Lua code
│  ├─ norns API docs (vectorized)
│  └─ Your coding patterns
├─ Signals (Audio Programming)
│  ├─ "I prefer event-based over clock-based sequencing"
│  ├─ "Euclidean patterns fit my workflow"
│  └─ Your SuperCollider sequencer patterns
├─ Scrolls (Philosophy)
│  ├─ "Instruments not tracks" principle
│  ├─ Bogost on constraint-based design
│  └─ "Emergent vs prescribed patterns" essay
├─ Sights (Visual Thinking)
│  ├─ p5.js rhythm visualization sketches
│  └─ "Visual rhythm informs temporal structure"
└─ Glyphs (System Design)
   ├─ Modular system design preferences
   └─ Composition over inheritance

Polly's Suggestion:
"Based on your 'instruments not tracks' philosophy and preference for emergent patterns, I suggest an event-based sequencer with Euclidean pattern generation.

This matches your visual rhythm work in p5.js (Sights) and your modular system design principles (Glyphs).

Here's a structure:
[code that reflects ALL these influences]

This approach allows patterns to emerge rather than being prescribed, aligned with your Bogost-influenced constraint-based design thinking."
```

**Why This Matters:**

Your audio programming philosophy **should** inform your visual code. Your systems thinking **should** guide your architecture. Your constraint-based design thinking **should** shape your implementations.

Polly makes these connections automatically. Cursor can't, because it doesn't know these domains exist.

#### Pillar 3: Institutional Memory (The "Why" Not Just "What")

**The Principle:** Git tracks *what* changed. Polly tracks *why* you made decisions.

**Git's Limitation:**

```bash
$ git log

commit a3b4c5d
Author: You
Date: 6 months ago

Refactor Two Tangles architecture

Move audio processing to separate module
Add event bus for parameter changes
Extract pattern generators
```

You know *what* changed. But in 6 months, **why did you make these choices?**

**Polly's Institutional Memory:**

When you refactored, you documented your reasoning:

```markdown
# Two Tangles Architecture Decision

Date: [6 months ago]
Domain: Signals

## Decision
Refactor to separate audio module + event bus

## Why
- Current monolithic structure makes testing audio hard
- Want to experiment with pattern generators independently
- Event bus enables future parameter automation without coupling

## Alternatives Considered
1. Keep monolithic (simple but inflexible) ❌
2. Full plugin architecture (over-engineered for this) ❌
3. Module separation + event bus (CHOSEN) ✅

## Reasoning
- Aligns with my "modular instruments" philosophy
- Event bus pattern worked well in Phemto (proven)
- Avoids premature abstraction while enabling extensibility

## Constraints
- Must maintain <10ms audio latency (norns requirement)
- CPU budget is tight on norns
- Keep Lua memory footprint low

## Outcome
- Architecture supports independent testing ✓
- Parameter automation path clear ✓
- Pattern generators now reusable across projects ✓
```

**Six months later:**

```
You: "Why did I separate the audio processing module?"

Polly retrieves your decision document:

"Six months ago you chose module separation with an event bus because:
1. It made testing easier
2. Allowed independent pattern generator experimentation
3. Enabled future parameter automation

You specifically avoided a full plugin architecture as over-engineering. The event bus pattern had worked well in Phemto.

Key constraints were <10ms latency and low memory on norns."
```

**The Difference:**

- **Git:** "You moved audio to separate module" (what)
- **Polly:** "You moved audio to separate module to enable independent testing while maintaining <10ms latency, following your modular instruments philosophy proven in Phemto" (why)

**Implementation in Polly Code:**

When you make significant architectural changes:
1. Polly prompts: "This looks like an architectural decision. Would you like to document your reasoning?"
2. You write (or voice dictate) the why
3. Polly saves to vault with links to relevant code
4. Future you (or future Polly) can retrieve this context

---

### Designer-Coder Integration: Living Specs

**The Problem with Current Workflows:**

```
Traditional Design → Development:

1. Designer creates mockup in Figma
2. Designer sends PNG screenshot to developer
3. Developer interprets (often incorrectly)
4. Implementation doesn't match design
5. Designer frustrated, developer confused
6. Multiple revision cycles
```

**The Polly Code Solution:**

```
Polly Designer → Coder Workflow:

1. Architect (Plan mode)
   └─ Designs system architecture
   └─ Output: Architecture document

2. Architect → Designer handoff
   └─ "I need UI for login, registration, password reset"

3. Designer (Vision mode)
   └─ Analyzes architecture
   └─ Proposes user flows
   └─ Output: UX strategy document

4. Designer (Mockup mode)
   └─ Creates visual designs with specs
   └─ Output: ASCII mockups + design tokens + component specs

5. Designer → Programmer handoff
   └─ Design specs passed as structured data

6. Programmer (Implement mode)
   └─ Receives design tokens, spacing, colors, typography
   └─ Implements to spec
   └─ Output: Code that matches design

7. Feedback loop
   └─ Implementation → Designer for review
   └─ Designer validates or suggests refinements
```

**What Makes This Different:**

1. **Architecture First:** Polly enforces Architect → Designer flow
2. **Structured Handoff:** Not PNGs, but design tokens + specs
3. **Living Specs:** Design evolves with code
4. **Constraint-Based:** Designer respects architectural constraints
5. **Persona Coordination:** Orchestrator manages entire flow

**Example Design Handoff:**

```json
{
  "component": "LoginForm",
  "design_spec": {
    "layout": {
      "type": "flex",
      "direction": "column",
      "gap": "16px",
      "padding": "24px"
    },
    "elements": [
      {
        "type": "input",
        "label": "Email",
        "placeholder": "you@example.com",
        "validation": "email",
        "styles": {
          "padding": "12px 16px",
          "border": "1px solid var(--border)",
          "borderRadius": "8px",
          "fontSize": "16px"
        }
      },
      {
        "type": "button",
        "text": "Sign In",
        "variant": "primary",
        "styles": {
          "backgroundColor": "var(--primary)",
          "color": "var(--primary-foreground)",
          "padding": "12px 24px",
          "borderRadius": "8px",
          "fontSize": "16px",
          "fontWeight": "600"
        }
      }
    ]
  },
  "design_tokens": {
    "colors": {
      "primary": "#2563eb",
      "border": "#e5e5e5",
      "primary-foreground": "#ffffff"
    },
    "spacing": {
      "md": "16px",
      "lg": "24px"
    },
    "typography": {
      "body": "16px"
    }
  },
  "accessibility": {
    "aria_labels": true,
    "keyboard_navigation": true,
    "contrast_ratio": "4.5:1"
  }
}
```

Programmer receives this as structured data—no interpretation needed.

---

### Edge-Native Advantages: Privacy, Speed, Ownership

**Why Edge-Native Matters:**

#### Advantage 1: Privacy (Your Code Never Leaves)

**Cloud-Based Competitors:**
- Cursor: Sends code to cloud for analysis
- Copilot: Microsoft servers process all suggestions
- Windsurf: Cloud-based inference

**Polly Code:**
- All RAG retrieval happens locally
- Embeddings generated on-device
- Only explicit cloud queries sent to providers
- You control what leaves your machine

**Who This Matters For:**
- Proprietary code developers
- Privacy-conscious users
- Security-sensitive projects
- Anyone who values autonomy

#### Advantage 2: Speed (Sub-100ms Retrieval)

**Cloud Round-Trip:**
```
Request → Internet → Cloud Server → LLM → Response → Internet → You
Latency: 200-500ms (optimistic), 1-2s (realistic)
```

**Local Retrieval:**
```
Request → Local Vector DB → Response
Latency: 50-100ms
```

**Why This Matters:**
- Suggestions feel instant, not delayed
- Maintains flow state
- Multiple queries don't feel expensive
- Works on trains, planes, cafes (offline)

#### Advantage 3: Cost (No Per-Token Billing)

**Cloud-Based:**
- Cursor: Charges per query or monthly fee
- Copilot: $10-19/month
- Windsurf: Subscription model

**Polly Code:**
- Local inference: $0 per query
- Cloud escalation: Only when needed, you control budget
- One-time purchase or expansion model
- No subscription fatigue

#### Advantage 4: Ownership (Your Data, Your System)

**Cloud SaaS Model (e.g., Uare.ai):**
- Your profile stored in proprietary containers
- Subscription required for access
- Data portability limited
- Company goes away = your data goes away

**Polly Code:**
- Profile stored locally in markdown
- Vault is yours (portable, readable)
- No vendor lock-in
- Works forever, no subscription expiration

**Market Framing:**

> **"Polly Code: Personal AI you own"**
>
> Not rented. Not black-boxed. Not optimized for monetizing your expertise.
> 
> Infrastructure for augmenting your practice, not replicating your identity.

---

### Profile-Aware Coding: Learns Your Style

**Integration with Phase 13b (User Profile System):**

Polly Code doesn't just know your codebase—it knows **how you think about code**.

**Profile-Aware Suggestions:**

```markdown
# Your Coding Profile (Sigils Domain)

## Technical Stack
- Languages: Python (primary), JavaScript/TypeScript, Lua, Bash
- Tools: Docker, Tailscale, self-hosted infrastructure
- Preferences: Functional style, verbose variable names, comments explain "why"

## Coding Patterns
- Prefers functional programming style
- Verbose variable names for clarity (e.g., `userAuthenticationToken` not `token`)
- Comments explain *why*, not *what*
- Incremental working versions over big-bang releases
- Infrastructure-as-code approach

## Architecture Preferences
- Modular over monolithic
- Composition over inheritance
- Event-driven when appropriate
- Avoid premature optimization
- Self-hosted solutions over cloud dependencies

## Active Projects
- Polly: Edge-native AI system with agentic personas
- UGREEN NAS: Self-hosted infrastructure hub
- norns scripts: Lua-based instrument development

## Learning Focus
- Building: Design capacity (p5.js, Processing)
- Strengthening: Docker containerization, Linux sysadmin
```

**How This Changes Suggestions:**

**Without Profile:**
```python
You: "Write a function to validate user tokens"

Generic Suggestion:
def validate(token):
    if not token:
        return False
    return check(token)
```

**With Profile:**
```python
You: "Write a function to validate user tokens"

Profile-Aware Suggestion:
def validate_user_authentication_token(authentication_token):
    """
    Validates JWT authentication token for user session.
    
    Why: Token validation must happen before any authenticated endpoint.
    Approach: Verify signature + expiration, following security best practices.
    """
    if not authentication_token:
        return False
    
    # Verify token signature and expiration
    return verify_jwt_token_signature_and_expiration(authentication_token)
```

**What Changed:**
- ✅ Verbose variable names (your preference)
- ✅ Docstring explains "why" (your style)
- ✅ Descriptive function names (your pattern)
- ✅ Functional approach (your preference)

---

## 4. Relationship to Phase 17 Foundation

### Current Phase 17 Scope

The existing `PHASE17_CODE_WORKSPACE.md` defines a **3-week basic workspace**:

**Week 1: Core Editor**
- Monaco editor for code
- File tree with git status
- Integrated terminal (xterm.js)
- Git operations UI

**Week 2: Polly Integration**
- Chat panel with full context
- Model routing for code
- RAG-powered code search
- Language/library support

**Week 3: Advanced Features**
- Code actions (explain, refactor, save as note)
- Multi-file context
- Pattern-aware suggestions
- Code → Note creation

**Total Scope:** Basic coding environment integrated with Polly

---

### The Vision Document Expands This

This document recognizes that Phase 17's original scope was **too limited** for Polly's ambitions.

**The Gap:**

Original Phase 17 gives you:
- ✅ Basic code editor
- ✅ Git integration
- ✅ AI chat with code context
- ⚠️ But not a full IDE
- ⚠️ No language intelligence (LSP)
- ⚠️ No epub vector integration
- ⚠️ No Designer-Coder workflow
- ⚠️ No profile-aware coding

**This Vision Fills The Gap:**

We break Phase 17 into **four sub-phases (17a/b/c/d)**:

#### Phase 17a: Monaco Foundation (2-3 weeks)
*This is essentially the current Phase 17 spec*

**Deliverables:**
- Monaco editor integrated into Polly
- Basic editor configuration (syntax highlighting, themes)
- File tree with file icons and git status
- Multi-file tabs
- Integrated terminal (xterm.js)
- Git operations UI (stage, commit, push, diff viewer)
- Basic chat panel

**Acceptance Criteria:**
- ✓ Can edit code in 9+ languages
- ✓ File tree shows project structure with git status
- ✓ Terminal works with multiple tabs
- ✓ Git operations function correctly
- ✓ Chat panel has access to current file

---

#### Phase 17b: Language Intelligence (3-4 weeks)
*Adds professional IDE features*

**Deliverables:**
- `monaco-languageclient` integration
- Language Server Protocol (LSP) support
- LSP servers for primary languages:
  - TypeScript/JavaScript (tsserver)
  - Python (pyright or pylsp)
  - Rust (rust-analyzer)
  - Go (gopls)
- tree-sitter integration for enhanced parsing
- IntelliSense and autocompletion
- Real-time diagnostics (errors, warnings)
- Go-to-definition, find references

**Acceptance Criteria:**
- ✓ IntelliSense works in TypeScript/Python/Rust
- ✓ Errors and warnings appear in real-time
- ✓ Go-to-definition navigates correctly
- ✓ Find references shows all usages
- ✓ Performance acceptable (<100ms response time)

---

#### Phase 17c: RAG & Polly Integration (4-5 weeks)
*This is where Polly Code becomes unique*

**Deliverables:**
- Epub vector pipeline integration with editor
- Documentation retrieval while coding:
  - SuperCollider Book
  - Fieldsteel tutorials
  - React docs
  - Language-specific documentation
- Cross-domain retrieval in coding context:
  - Pull from Signals, Scrolls, Sights, Glyphs when relevant
- Institutional memory integration:
  - Retrieve design decision notes
  - Link commits to reasoning documents
- Context-aware chat panel:
  - Automatically includes relevant epub vectors
  - Shows cross-domain connections
  - Displays institutional memory

**Acceptance Criteria:**
- ✓ Epub vectors retrieved when coding in relevant language
- ✓ Cross-domain suggestions appear appropriately
- ✓ Institutional memory surfaces when viewing old code
- ✓ Chat understands full polymathic context
- ✓ Performance: <200ms for context retrieval

---

#### Phase 17d: Designer-Coder Integration (5-6 weeks)
*Completes the vision with persona coordination*

**Deliverables:**
- Designer persona UI within editor
- Spec → Code workflow:
  - Architect creates architecture
  - Designer creates mockups + specs
  - Programmer receives structured handoff
- Visual-to-code pipeline:
  - Design tokens passed to code
  - Component specs guide implementation
- Constraint-based design system integration
- Feedback loops:
  - Implementation → Designer for review
  - Designer suggests refinements
- Profile-aware coding (Phase 13b integration):
  - Suggestions match your style
  - Learns from your patterns
  - Adapts to your mental models

**Acceptance Criteria:**
- ✓ Designer persona accessible from editor
- ✓ Design specs passed to Programmer correctly
- ✓ Code generated matches design tokens
- ✓ Feedback loop functional (implementation → review)
- ✓ Profile-aware suggestions demonstrably better

---

### Timeline Comparison

**Original Phase 17:**
- 3 weeks
- Basic workspace
- Chat + git + editor

**Expanded Phase 17 (this vision):**
- **17a:** 2-3 weeks (foundation)
- **17b:** 3-4 weeks (language intelligence)
- **17c:** 4-5 weeks (RAG integration)
- **17d:** 5-6 weeks (Designer-Coder)
- **Total:** 14-18 weeks

**Why the expansion is justified:**

The original Phase 17 would have given you a "coding notepad with AI chat." Useful, but not transformative.

This expanded vision gives you:
- A **full IDE** with professional language intelligence
- **Context beyond code** via epub vectors and cross-domain retrieval
- **Institutional memory** that preserves the "why" of decisions
- **Designer-Coder workflows** that integrate design and development
- **Profile-aware coding** that learns your style

This isn't scope creep—it's **scope realization**. This is what Polly Code should be.

---

### Integration Points with Existing Phases

**Phase 17 depends on:**

- ✅ **Phase 1.5 (Domains):** Sigils, Signals, Scrolls, Sights, Glyphs structure
- ✅ **Phase 2 (RAG):** Epub vectors, retrieval system
- ✅ **Phase 11 (Multi-Model):** Router for intelligent model selection
- ✅ **Phase 12 (Knowledge Graph):** Related files, cross-references
- ✅ **Phase 16 (Notes):** Monaco already integrated for notes
- 🔄 **Phase 13b (User Profile):** Profile-aware coding (planned)
- 🔄 **Phase 24 (Orchestrator):** Persona coordination (planned)
- 🔄 **Phase 27 (Designer):** Designer-Coder workflows (planned)

**Phase 17 enables:**

- **Phase 26 (Project Management):** Code-aware project tracking
- **Future phases:** Code generation, testing, deployment

---

## 5. Success Visualization

### What Does Success Look Like?

**Scenario: Building a norns Instrument (Day in the Life)**

**8:00 AM - Morning Concept**

You wake up with an idea for a new norns instrument based on Euclidean rhythms.

You open Polly Code and create a quick brain dump note:
```
norns instrument idea: euclidean rhythm generator
- uses my "instruments not tracks" philosophy
- visual feedback (inspired by p5.js rhythm sketches)
- event-based sequencing (not clock-based)
- cross-domain: Signals + Sights + Scrolls
```

Polly automatically tags this with domains: Signals (primary), Sights (visual), Scrolls (philosophy).

---

**9:00 AM - Architecture Phase**

You switch to Architect persona:

```
You: "Design architecture for a norns Euclidean rhythm instrument"

Architect analyzes your profile and notes:
- Signals domain: Experienced with norns, Lua, SuperCollider
- Your philosophy: "Instruments not tracks"
- Past projects: References similar patterns from your Phemto instrument

Architect: "Based on your 'instruments not tracks' philosophy, I propose a modular architecture:

┌─────────────────────────────────────┐
│ Euclidean Rhythm Instrument         │
├─────────────────────────────────────┤
│ 1. Engine (SuperCollider)           │
│    ├─ Synthesis engine              │
│    └─ Parameter polling             │
│                                     │
│ 2. Script (Lua)                     │
│    ├─ Euclidean rhythm generator    │
│    ├─ Event scheduler               │
│    ├─ UI (visual rhythm feedback)   │
│    └─ Parameter controls            │
│                                     │
│ 3. State Management                 │
│    ├─ Pattern state                 │
│    └─ Sequence state                │
└─────────────────────────────────────┘

Key decisions:
- Event-based (your preference over clock-based)
- Visual rhythm display (connects to your p5.js work)
- Modular pattern generator (reusable component)

Should I hand this to Designer for UI mockups?"
```

You: "Yes, create UI mockups"

---

**9:30 AM - Design Phase**

Polly switches to Designer persona:

```
Designer (Vision mode):
"Based on Architect's plan, here's the user experience:

User Flow:
1. Select Euclidean parameters (steps, pulses, rotation)
2. Visual feedback shows rhythm pattern
3. Play/pause controls
4. Parameter modulation options

Interaction Patterns:
- Encoders: Parameter adjustment
- Keys: Play/pause, pattern selection
- Screen: Visual rhythm display (inspired by your p5.js sketches)
```

Designer (Mockup mode):
[Creates ASCII mockup of norns screen]

```
╔════════════════════════════════════╗
║  EUCLIDEAN RHYTHM                  ║
╠════════════════════════════════════╣
║  Steps:  [=========16===========]  ║
║  Pulses: [=====5=====]             ║
║  Rotate: [==2==]                   ║
║                                    ║
║  ● ○ ● ○ ○ ● ○ ○ ● ○ ● ○ ○ ● ○ ○  ║
║  ▲                                 ║
║                                    ║
║  [K2: Play] [K3: Pattern]          ║
╚════════════════════════════════════╝

Design Tokens:
- Font: Monospace (norns standard)
- Visual rhythm: Circles (filled = pulse)
- Animation: Position indicator moves
- Encoder mapping: E1=steps, E2=pulses, E3=rotation
```

Designer: "Mockup ready. Handing off to Programmer with design specs."

---

**10:00 AM - Implementation Phase**

Polly switches to Programmer persona:

```
Programmer: "I have the architecture from Architect and design specs from Designer.

I'll also retrieve:
- Your norns Lua patterns (from past projects)
- Euclidean rhythm algorithm (from your notes)
- norns API documentation (epub vectors)
- Your 'instruments not tracks' implementation philosophy

Starting implementation..."

[Programmer generates Lua code]

-- euclidean.lua
-- Euclidean Rhythm Instrument
-- Based on "instruments not tracks" philosophy

engine.name = "EuclideanSynth"

local Euclidean = {}

function Euclidean.generate(steps, pulses, rotation)
  -- Implementation based on Bjorklund algorithm
  -- (Retrieved from your "Rhythm Algorithms" note)
  -- ...
end

function Euclidean.init()
  -- Event-based sequencing (your preference)
  -- Visual feedback (connects to your p5.js work)
  -- ...
end

-- [Full implementation follows...]
```

Programmer: "Implementation complete. Code follows your style:
- Verbose variable names ✓
- Event-based sequencing ✓
- Modular structure ✓
- Comments explain 'why' ✓

Ready for testing."

---

**11:00 AM - Documentation**

You: "Create documentation for this instrument"

Polly switches to Scribe persona:

```
Scribe: "I'll document this instrument. I have context from:
- Architect's design document
- Designer's UI mockups
- Programmer's implementation
- Your Scrolls domain philosophy

Creating comprehensive documentation..."

[Scribe generates markdown documentation]

# Euclidean Rhythm Instrument

## Philosophy
This instrument embodies the "instruments not tracks" approach—a generative tool for rhythm creation rather than a fixed sequencer.

## How It Works
[Explains Euclidean algorithm with references to Bjorklund]

## Usage
[Step-by-step guide with screenshots]

## Design Decisions
[Links to your architecture decision notes]

## Related Work
[Connects to your p5.js rhythm visualization]
```

Scribe: "Documentation saved to `vault/Signals/norns/euclidean-docs.md`"

---

**11:30 AM - Reflection**

You realize you want to save the implementation pattern for future instruments.

You: "Save the event-based sequencing pattern from this code"

```
Polly: "Extracting pattern from code...

Pattern: Event-Based Sequencing for norns
Domain: Signals
Confidence: High

Structure:
- clock.run() for main loop
- Event queue for note triggering
- State machine for playback control

This pattern matches your preference for event-based over clock-based sequencing (noted 8 times in your profile).

Should I add this to your Pattern Library?"
```

You: "Yes"

Polly: "Pattern saved. I'll suggest this pattern in future norns projects."

---

**Result:**

In **2.5 hours**, you went from idea to fully implemented instrument with:
- ✅ Architecture designed (respecting your philosophy)
- ✅ UI mockup created (inspired by your visual work)
- ✅ Code implementation (following your patterns)
- ✅ Comprehensive documentation
- ✅ Pattern extracted for future reuse

**All coordinated across 4 personas with full context from 5 domains.**

**Without Polly Code:**
- Switch between multiple tools (VSCode, Figma, Obsidian)
- Re-explain context to each tool
- Manually connect design → code
- Write documentation separately
- Lose architectural reasoning
- Estimated time: **1-2 days**

**With Polly Code:**
- One tool, coordinated personas
- Context automatically shared
- Design → code pipeline seamless
- Documentation auto-generated with full context
- Architecture reasoning preserved
- Actual time: **2.5 hours**

---

This is what success looks like. Not just faster coding—**better, more coherent, more aligned with your thinking.**

---

*[End of Part 1 - Continue to Part 2: Core Differentiation]*


---

# PART 2: CORE DIFFERENTIATION

## 6. Context Beyond Code (Deep Dive)

### The Retrieval Space Architecture

**Traditional AI Code Editors:**
```
Retrieval Space = {
  current_file,
  related_files_in_project,
  maybe_github_examples
}
```

**Polly Code:**
```
Retrieval Space = {
  // Code Context
  current_file,
  related_files_in_project,
  cross_project_references,
  
  // Documentation Context
  epub_vectors {
    SuperCollider_Book,
    Fieldsteel_Tutorials,
    React_Docs,
    Language_Specific_Docs
  },
  
  // Your Knowledge Context
  domains {
    Signals: audio_programming_notes,
    Sigils: coding_patterns,
    Scrolls: design_philosophy,
    Sights: visual_work,
    Glyphs: systems_thinking
  },
  
  // Institutional Memory
  design_decisions {
    architecture_notes,
    reasoning_documents,
    constraint_analysis,
    alternative_evaluations
  },
  
  // Profile Context
  user_profile {
    coding_style,
    preferences,
    mental_models,
    expertise_levels
  }
}
```

### Real-World Retrieval Examples

#### Example 1: SuperCollider Development

**Query:** "Create a granular synthesis engine with stereo panning"

**Polly's Retrieval Process:**

```
1. Code Context (Sigils Domain)
   ├─ Your existing SuperCollider files
   ├─ Your norns engine implementations
   └─ Related synthesis code

2. Documentation (Epub Vectors)
   ├─ SuperCollider Book Chapter 12: "Granular Synthesis"
   ├─ Fieldsteel Tutorial 8: "Granulation Techniques"
   └─ SuperCollider Source Documentation: GrainBuf, TGrains

3. Your Knowledge (Signals Domain)
   ├─ "Granular Synthesis Patterns" note
   ├─ "Stereo Panning Techniques" note
   └─ "Performance Considerations for norns" note

4. Cross-Domain Insights (Scrolls)
   ├─ "Texture as Compositional Material" essay
   └─ Philosophy on grain density vs. clarity

5. Past Work (Sigils + Signals)
   ├─ Phemto project: Similar granular implementation
   └─ Two Tangles: Stereo field considerations

6. Profile Context
   ├─ Preference: Functional programming style
   ├─ Pattern: Verbose parameter names
   └─ Constraint: norns CPU budget awareness
```

**Polly's Response:**

```supercollider
// Granular Synthesis Engine with Stereo Panning
// Based on Fieldsteel Tutorial 8 + SuperCollider Book Ch12
// Follows your "texture as compositional material" philosophy

(
Engine_GranularStereo : CroneEngine {
  var <granulator_left;
  var <granulator_right;
  var <grain_density_parameter;
  var <stereo_width_parameter;
  
  *new { arg context, doneCallback;
    ^super.new(context, doneCallback);
  }
  
  alloc {
    // Allocate buffers for grain sources
    // Using TGrains (per Fieldsteel Ch8) for CPU efficiency on norns
    
    granulator_left = {
      arg grain_density = 20,
          grain_duration = 0.1,
          stereo_position = -0.5,  // Left channel bias
          buffer_position = 0;
      
      var trigger_signal, grain_output;
      
      // Grain triggering (density controls texture)
      trigger_signal = Impulse.ar(grain_density);
      
      // TGrains for CPU efficiency (norns constraint)
      grain_output = TGrains.ar(
        numChannels: 1,
        trigger: trigger_signal,
        bufnum: b.bufnum,
        rate: 1,
        centerPos: buffer_position,
        dur: grain_duration,
        pan: stereo_position,
        amp: 0.5
      );
      
      grain_output;
    }.play;
    
    // Similar for granulator_right...
    
    // Add parameter polling for norns control
    this.addCommand(\grain_density, "f", { arg msg;
      grain_density_parameter = msg[1];
      granulator_left.set(\grain_density, msg[1]);
      granulator_right.set(\grain_density, msg[1]);
    });
    
    this.addCommand(\stereo_width, "f", { arg msg;
      stereo_width_parameter = msg[1];
      // Adjust pan positions based on width
      granulator_left.set(\stereo_position, -0.5 * msg[1]);
      granulator_right.set(\stereo_position, 0.5 * msg[1]);
    });
  }
  
  free {
    granulator_left.free;
    granulator_right.free;
  }
}
)
```

**Auto-Generated Annotation:**

```markdown
## Implementation Notes

**Source Context:**
- Technique from Fieldsteel Tutorial 8 (TGrains for efficiency)
- Architecture inspired by SuperCollider Book Ch12
- Follows your Phemto granular implementation pattern

**Design Decisions:**
- TGrains chosen over GrainBuf for norns CPU efficiency
- Stereo implementation uses dual granulators (your preference from Two Tangles)
- Parameter polling follows norns engine conventions

**Philosophy Alignment:**
- "Texture as compositional material": Grain density as primary expressive parameter
- Stereo width as spatial texture control
- CPU-conscious design (norns constraint awareness)

**Related Work:**
- Links to: [[Phemto Engine]], [[Two Tangles Stereo]], [[Texture Philosophy Essay]]
```

---

#### Example 2: React Component Development

**Query:** "Build a user profile card component"

**Polly's Retrieval Process:**

```
1. Code Context
   ├─ Your existing React components
   ├─ Component patterns from your projects
   └─ Styling approach (Tailwind/CSS-in-JS)

2. Design Context (Phase 27: Designer Persona)
   ├─ Your design system tokens
   ├─ Component library patterns
   └─ Accessibility guidelines you follow

3. Your Knowledge (Sigils Domain)
   ├─ "React Component Patterns" note
   ├─ "Composition vs Props Drilling" decision document
   └─ TypeScript usage preferences

4. Profile Context
   ├─ Preference: Functional components with hooks
   ├─ Pattern: Props interface definitions
   ├─ Style: Verbose prop names, TypeScript strictly typed

5. Cross-Domain (Glyphs: Systems Thinking)
   ├─ "Component Modularity" principles
   └─ "Reusable vs Specialized" decision heuristics
```

**Polly's Response:**

```typescript
// UserProfileCard.tsx
// Reusable profile card component following your composition patterns

import React from 'react';

/**
 * Props interface for UserProfileCard component.
 * 
 * Why separate interface: Enables type reuse and composition
 * (follows your "composition over props drilling" pattern)
 */
interface UserProfileCardProps {
  user_id: string;
  user_display_name: string;
  user_avatar_url: string;
  user_bio_text?: string;
  user_email_address: string;
  is_verified_user: boolean;
  on_profile_click_handler?: (userId: string) => void;
}

/**
 * UserProfileCard Component
 * 
 * Purpose: Display user profile information in card format
 * 
 * Design: Follows your design system tokens
 * - Spacing: Uses spacing.md (16px) from tokens
 * - Colors: Uses colors.primary and colors.neutral
 * - Typography: Uses typography.body (16px)
 * 
 * Accessibility: 
 * - ARIA labels for screen readers
 * - Keyboard navigation support
 * - Verified badge with accessible description
 */
export const UserProfileCard: React.FC<UserProfileCardProps> = ({
  user_id,
  user_display_name,
  user_avatar_url,
  user_bio_text,
  user_email_address,
  is_verified_user,
  on_profile_click_handler
}) => {
  
  const handle_card_click = () => {
    if (on_profile_click_handler) {
      on_profile_click_handler(user_id);
    }
  };
  
  return (
    <div 
      className="user-profile-card"
      onClick={handle_card_click}
      role="button"
      tabIndex={0}
      aria-label={`Profile card for ${user_display_name}`}
    >
      <div className="profile-card-header">
        <img 
          src={user_avatar_url} 
          alt={`${user_display_name} avatar`}
          className="avatar-image"
        />
        <div className="profile-info">
          <h3 className="user-name">
            {user_display_name}
            {is_verified_user && (
              <span 
                className="verified-badge"
                aria-label="Verified user"
              >
                ✓
              </span>
            )}
          </h3>
          <p className="user-email">{user_email_address}</p>
        </div>
      </div>
      
      {user_bio_text && (
        <p className="user-bio">{user_bio_text}</p>
      )}
    </div>
  );
};

/**
 * Styling Notes:
 * - Uses your design system tokens (see vault/Design/design-system.md)
 * - Follows your Tailwind configuration
 * - Responsive: Adapts to mobile/desktop (your standard breakpoints)
 * 
 * Component Pattern:
 * - Functional component with TypeScript (your preference)
 * - Verbose prop names for clarity (your style)
 * - Optional props with ? (your pattern)
 * - Event handlers prefixed with "on_" (your convention)
 */

// Associated styles (Tailwind or CSS-in-JS based on your project)
```

**What's Different:**

- ✅ Verbose prop names (`user_display_name` not `name`)
- ✅ TypeScript strictly typed (your preference)
- ✅ Comments explain "why" not "what" (your style)
- ✅ Follows your design system tokens
- ✅ Accessibility baked in (your requirement)
- ✅ Functional components (your pattern)

---

### Documentation as Living Context

**The Problem with Static Docs:**

Traditional approach:
1. You read SuperCollider Book
2. You learn something
3. You close the book
4. **Context is lost**
5. You need to re-look-up later

**Polly's Approach:**

1. You read SuperCollider Book (epub in vault)
2. Polly indexes it (epub vectors)
3. **Context persists forever**
4. When coding SC, Polly retrieves relevant sections automatically
5. You never lose the knowledge

**Example: The "I Remember Reading About This" Moment**

```
You (3 months ago): Reading SuperCollider Book Chapter 9 on UGens

You (today): Writing synthesis code in Polly Code

You: "I remember reading about a UGen that does pitch shifting..."

Polly retrieves:
├─ SuperCollider Book Ch9, Section 4: "PitchShift UGen"
├─ Your note from 3 months ago: "PitchShift considerations for performance"
└─ Your comment in old code: "PitchShift CPU-intensive, use sparingly"

Polly: "You're thinking of PitchShift from SuperCollider Book Ch9. 
Three months ago you noted it's CPU-intensive. Here's the usage pattern 
you documented..."
```

**This is impossible for Cursor/Copilot** because they don't have your epub vectors or notes.

---

## 7. Designer-Coder Integration (Deep Dive)

### The Current Broken Workflow

**Traditional Design → Development Process:**

```
Week 1: Design Phase
├─ Designer opens Figma
├─ Creates beautiful mockups
├─ Exports PNGs
└─ Sends to developer via Slack

Week 2: Development Phase
├─ Developer opens PNGs
├─ Eyeballs spacing ("looks like 16px?")
├─ Guesses colors ("#3B82F6? #2563EB?")
├─ Implements best-guess version
└─ Sends back for review

Week 3: Revision Hell
├─ Designer: "That blue is wrong"
├─ Designer: "Spacing should be 24px not 16px"
├─ Designer: "Border radius is too small"
├─ Developer: "Can you be more specific?"
└─ Multiple back-and-forth iterations

Week 4: Compromise
├─ Developer: "Close enough?"
├─ Designer: "I guess..."
└─ Ship something that matches neither vision
```

**Total Time:** 4 weeks, frustration high, quality compromised

---

### The Polly Code Solution: Living Specs

**Polly's Integrated Workflow:**

```
Day 1: Architecture (30 minutes)
User: "I need a user profile page with settings"

Architect (Plan mode):
├─ Analyzes requirements
├─ Designs system architecture
├─ Defines components needed:
│  ├─ ProfileHeader
│  ├─ ProfileInfo
│  ├─ SettingsPanel
│  └─ ActionButtons
└─ Hands off to Designer: "Need UI for these components"

Day 1: Design (2 hours)
Designer (Vision mode):
├─ Creates UX strategy
├─ Defines user flows
└─ Plans information architecture

Designer (Mockup mode):
├─ Creates visual mockups (ASCII + specs)
├─ Generates design tokens:
│  ├─ Colors: { primary: "#2563eb", ... }
│  ├─ Spacing: { sm: "8px", md: "16px", lg: "24px" }
│  ├─ Typography: { body: "16px", heading: "24px" }
│  └─ Border radius: { default: "8px", full: "9999px" }
└─ Creates component specs (structured JSON)

Designer → Programmer Handoff:
{
  "component": "ProfileHeader",
  "design_spec": {
    "layout": "flex-row",
    "gap": "var(--spacing-md)",
    "elements": [
      {
        "type": "avatar",
        "size": "80px",
        "borderRadius": "var(--radius-full)"
      },
      {
        "type": "text-group",
        "elements": [
          { "type": "heading", "fontSize": "var(--font-heading)" },
          { "type": "subtext", "fontSize": "var(--font-body)" }
        ]
      }
    ]
  }
}

Day 1-2: Implementation (4 hours)
Programmer (Implement mode):
├─ Receives structured design specs
├─ Uses design tokens (no guessing)
├─ Implements components to spec:
│  ├─ Spacing: 16px (from tokens.spacing.md)
│  ├─ Colors: #2563eb (from tokens.colors.primary)
│  ├─ Border radius: 8px (from tokens.radius.default)
│  └─ Typography: 16px body, 24px heading (from tokens)
└─ Code matches design exactly

Day 2: Review & Iteration (30 minutes)
Designer (Critic mode):
├─ Reviews implementation
├─ Checks against design specs
├─ Validates:
│  ├─ Colors ✓ (matches tokens)
│  ├─ Spacing ✓ (uses correct variables)
│  ├─ Typography ✓ (follows scale)
│  └─ Accessibility ✓ (ARIA labels present)
└─ Approves or suggests minor tweaks

Total Time: 2 days (vs 4 weeks)
Quality: High (exact match to design)
Frustration: Low (no guessing, clear specs)
```

---

### Design Tokens as Single Source of Truth

**The Problem with Current Approaches:**

Designers use Figma variables:
```
Primary Color: #2563EB
Spacing Unit: 16px
```

Developers use CSS variables:
```css
:root {
  --primary: #3B82F6;  /* Wrong shade! */
  --spacing: 16px;      /* Right... by luck */
}
```

**Mismatch inevitable.** No single source of truth.

**Polly's Solution:**

Design tokens live in vault, shared by Designer and Programmer:

```javascript
// vault/.polly/design/tokens.js
export const designTokens = {
  colors: {
    primary: "#2563eb",
    secondary: "#10b981",
    neutral: "#6b7280",
    error: "#ef4444"
  },
  spacing: {
    xs: "4px",
    sm: "8px",
    md: "16px",
    lg: "24px",
    xl: "32px"
  },
  typography: {
    display: { size: "48px", lineHeight: "56px" },
    heading: { size: "24px", lineHeight: "32px" },
    body: { size: "16px", lineHeight: "24px" }
  },
  borderRadius: {
    sm: "4px",
    default: "8px",
    lg: "12px",
    full: "9999px"
  }
};
```

**Designer persona** uses these tokens when creating mockups.
**Programmer persona** uses these tokens when implementing.
**One source of truth.** No drift.

---

### Feedback Loops: Implementation → Design

**Traditional:** One-way street (Design → Dev, no feedback)

**Polly Code:** Bidirectional

```
Programmer implements component
├─ Discovers: "This spacing feels too tight on mobile"
├─ Flags for Designer review
└─ Designer (Critic mode) evaluates

Designer receives feedback:
├─ Analyzes implementation on mobile
├─ Agrees: Spacing should be 24px on mobile, 16px on desktop
├─ Updates tokens with responsive values
└─ Programmer receives updated spec

Programmer updates implementation:
├─ Uses new responsive spacing
├─ Implementation now optimal for both desktop and mobile
└─ Learning captured in design system
```

**This feedback loop improves the design system over time.**

---

### Constraint-Based Design Integration

**Your Philosophy:** Bogost-influenced constraint-based design

**How Polly Respects This:**

```
Architect defines constraints:
├─ "Must work on norns (128x64 screen)"
├─ "CPU budget: <70% (audio priority)"
├─ "Encoders only (no keyboard)"
└─ "Monospace font only"

Designer (Vision mode) receives constraints:
├─ Analyzes: "128x64 is very small"
├─ Applies constraint thinking:
│  ├─ Limited screen → minimal UI
│  ├─ Encoders only → parameter-focused design
│  ├─ Monospace → ASCII art aesthetics
│  └─ CPU budget → no animations
└─ Creates design respecting ALL constraints

Designer (Mockup mode):
Creates mockup that embraces constraints as generative:

╔════════════════════════════════╗
║ SEQ  16  5  2            [>]  ║  ← Line 1: Title + status
║ ●○●○○●○○●○●○○●○○              ║  ← Line 2: Visual rhythm
║ ▲                              ║  ← Line 3: Position indicator
║ E1:steps E2:pulse E3:rot  K2:▶ ║  ← Line 4: Controls
╚════════════════════════════════╝

Design decisions driven BY constraints:
✓ ASCII art rhythm display (monospace font constraint)
✓ Minimal UI (screen size constraint)
✓ Encoder labels (no keyboard constraint)
✓ Static display (CPU budget constraint)
```

**Polly's Designer doesn't fight constraints—it uses them generatively.**

This aligns with your Bogost-influenced design philosophy.

---

## 8. Edge-Native Advantages (Deep Dive)

### Advantage 1: Privacy & Data Ownership

**The Cloud Problem:**

When you use Cursor, Copilot, or Windsurf:
```
Your Code
    ↓
Sent to Cloud
    ↓
Processed on Remote Servers
    ↓  (Your IP may be retained)
    ↓  (Code analyzed for model training)
    ↓  (Stored in logs for N days)
    ↓
Response Sent Back
```

**Who has seen your code?**
- The company's servers ✓
- Their model training pipeline (maybe)
- Their security team (for monitoring)
- Law enforcement (with warrant)
- Hackers (if breached)

**Polly Code's Approach:**

```
Your Code
    ↓
Local RAG Retrieval (your machine)
    ↓
Local Inference (your machine) OR
    ↓ (explicit cloud escalation with your approval)
Cloud LLM (only specific query, not full codebase)
```

**Who has seen your code?**
- Your local machine only
- Cloud provider (if you explicitly escalate a specific query)
- **That's it.**

**Why This Matters:**

**Scenario: Proprietary Startup**
```
You're building stealth startup with novel algorithm.

With Cursor:
├─ Every code completion → sent to Cursor servers
├─ Your novel algorithm → analyzed by their models
├─ IP potentially exposed in logs
└─ Risk: Competitor uses similar AI tool, gets suggestions based on patterns from your code

With Polly Code:
├─ All code completion → local inference only
├─ Your novel algorithm → never leaves your machine
├─ Zero IP exposure
└─ Risk: None (unless you explicitly send specific queries to cloud)
```

**Scenario: Enterprise Developer**
```
Company policy: No code leaves corporate network

With Cursor/Copilot:
├─ Cannot use (violates policy)
└─ Back to no AI assistance

With Polly Code:
├─ Fully local mode (no cloud dependency)
├─ RAG on internal docs (company wikis, specs)
├─ Policy compliant
└─ Full AI assistance maintained
```

---

### Advantage 2: Speed (Sub-100ms Retrieval)

**The Physics of Cloud Latency:**

```
Cloud-Based AI Code Editor:

User types → 
Request serialized → 
Sent over internet (20-100ms) → 
Cloud server receives → 
Model inference (50-200ms) → 
Response serialized → 
Sent over internet (20-100ms) → 
User receives response

TOTAL: 90-400ms (optimistic), often 500ms-2s (realistic)
```

**Polly Code (Local-First):**

```
User types → 
Local RAG retrieval (30-50ms) → 
Local embedding match (20-30ms) → 
Local inference (50-100ms) OR context preparation (10ms) → 
Response displayed

TOTAL: 50-100ms (local only), 200-300ms (if cloud escalation)
```

**Why This Matters:**

**Flow State Preservation:**

```
You're coding, in flow state...

With Cloud-Based (500ms latency):
You: "Create function to..."
[Wait... wait... wait...]
Brain: "Oh, I could also..."
[Response appears]
Brain: "Wait, what was I thinking?"
↓
Flow interrupted

With Polly Code (80ms latency):
You: "Create function to..."
[Response appears immediately]
Brain: "Perfect, now I'll..."
↓
Flow maintained
```

**Compound Time Savings:**

```
Coding session: 4 hours
Queries per hour: 20
Total queries: 80

Cloud latency: 500ms per query
Time waiting: 80 × 500ms = 40 seconds
Plus context switching cost: ~10 minutes
Total lost: ~11 minutes per 4-hour session

Polly latency: 80ms per query
Time waiting: 80 × 80ms = 6.4 seconds
Context switching: Minimal (feels instant)
Total lost: ~10 seconds per 4-hour session

Time saved: 10+ minutes per session
Over a year (250 work days): 2,500 minutes = 41 hours saved
```

---

### Advantage 3: Offline Capability

**Cloud Dependency Problem:**

```
Scenario: Coding on a train

With Cursor/Copilot:
├─ Train enters tunnel
├─ Internet drops
├─ AI assistance: GONE
└─ Back to raw text editor

With Windsurf:
├─ Coffee shop WiFi down
├─ AI assistance: GONE
└─ Cannot work
```

**Polly Code:**

```
Scenario: Coding anywhere

On a train (no internet):
├─ Full local RAG retrieval ✓
├─ Epub vectors accessible ✓
├─ Your notes available ✓
├─ Local inference works ✓
└─ AI assistance: FULLY FUNCTIONAL

At a cafe (no WiFi):
├─ Continue coding ✓
├─ Full context retrieval ✓
├─ Only missing: Cloud model escalation
└─ 90% of functionality available offline

On a plane (airplane mode):
├─ Everything works ✓
└─ Deep work environment (no distractions)
```

**Why This Matters:**

**Deep Work Environments:**

Best coding often happens in:
- ✈️ Planes (no WiFi)
- 🚂 Trains (spotty connection)
- ☕ Cafes (unreliable WiFi)
- 🏔️ Remote locations (no signal)
- 🌙 Late night (don't want distractions)

**Polly Code works everywhere.** Cursor/Copilot only work online.

---

### Advantage 4: Cost Structure

**Cloud-Based Pricing:**

```
GitHub Copilot:
├─ $10/month individual
├─ $19/month business
└─ $39/month enterprise

Cursor:
├─ $20/month Pro
├─ Usage limits
└─ Overage charges

Annual cost: $120-240 per developer
Over 5 years: $600-1200
```

**Polly Code Pricing (Proposed):**

```
Polly Code:
├─ $99 one-time purchase (or free with Polly)
├─ Local inference: $0 per query
├─ Cloud escalation: Pay-per-use with budget controls
└─ Optional expansions: $29-49 each

Cost over 5 years: $99-300 (vs $600-1200 for subscriptions)
```

**Budget Control:**

```
Polly allows you to set monthly cloud budget:

Settings → Cloud Budget:
├─ Maximum monthly spend: $10
├─ When approaching limit:
│  ├─ Show warning at 80%
│  ├─ Require confirmation at 90%
│  └─ Block escalation at 100%
└─ Local inference: Always available (never blocked)

Result: Predictable costs, never surprised by bill
```

---

## 9. Polymathic Coding Workflows (Deep Dive)

### The Five Domains in Practice

**Your Polymathic Structure:**

1. **Sigils** (Code/Systems): Programming, infrastructure, technical work
2. **Signals** (Audio): SuperCollider, norns, synthesis, audio programming
3. **Scrolls** (Writing/Philosophy): Essays, theory, design thinking
4. **Sights** (Visual): p5.js, Processing, visual design, UI/UX
5. **Glyphs** (Systems Thinking): Meta-organization, architecture, patterns

**How Polly Code Uses All Five:**

---

### Workflow 1: norns Instrument Development

**Cross-Domain Context:**

```
Task: Build a new norns instrument

Sigils (Code) provides:
├─ Lua programming patterns
├─ norns API knowledge
├─ Your modular code structure preferences
└─ Error handling patterns

Signals (Audio) provides:
├─ SuperCollider synthesis knowledge
├─ Audio routing preferences
├─ Performance optimization for norns
├─ Your "instruments not tracks" philosophy
└─ References to similar instruments you've built

Scrolls (Philosophy) provides:
├─ Design philosophy: Constraint-based thinking
├─ Bogost influence on your approach
├─ "Emergent vs prescribed" pattern preference
└─ Essays on instrument design

Sights (Visual) provides:
├─ p5.js rhythm visualization work
├─ Visual feedback preferences
├─ Screen layout aesthetics
└─ How visual rhythm informs temporal structure

Glyphs (Systems Thinking) provides:
├─ Modular architecture principles
├─ Composition over inheritance preference
├─ How you structure reusable components
└─ Your system design mental models
```

**Polly's Synthesis:**

```
Polly: "I see you're building a norns instrument. Let me pull context from all five domains:

From Signals: Your audio programming shows preference for event-based sequencing and Euclidean patterns.

From Sigils: Your Lua code follows modular structure with clear separation of engine/script.

From Scrolls: Your 'instruments not tracks' philosophy suggests generative rather than prescribed patterns.

From Sights: Your p5.js work shows visual rhythm display improves performance UX.

From Glyphs: Your system architecture prefers composition and reusable modules.

Synthesizing these, I suggest:
- Event-based sequencer (Signals preference)
- Modular Lua script structure (Sigils pattern)
- Generative Euclidean patterns (Scrolls philosophy)
- Visual rhythm feedback on screen (Sights influence)
- Reusable pattern generator module (Glyphs principle)

Here's the architecture..."
```

**This is impossible without polymathic context.** Cursor would only see your Lua code, not the philosophy guiding it.

---

### Workflow 2: Web App UI Development

**Cross-Domain Context:**

```
Task: Build user profile page UI

Sigils (Code) provides:
├─ React component patterns
├─ TypeScript preferences
├─ State management approach
└─ Your coding style

Sights (Visual) provides:
├─ Design system tokens
├─ Visual hierarchy preferences
├─ Color palette choices
└─ Typography scale

Scrolls (Philosophy) provides:
├─ UI philosophy: Progressive disclosure
├─ Accessibility as priority
└─ User agency over automation

Glyphs (Systems Thinking) provides:
├─ Component composition strategy
├─ Reusability patterns
└─ Modularity principles

Signals (Audio) provides:
├─ [Unexpected connection!]
└─ Your audio work emphasizes "feedback as compositional material"
    → Suggests real-time visual feedback in UI
```

**Polly's Synthesis:**

```
Polly: "Building user profile UI with cross-domain insights:

From Sights: Your design system uses 16px spacing scale and #2563eb primary color.

From Sigils: Your React patterns prefer functional components with TypeScript strict typing.

From Glyphs: Your architecture favors composition—ProfileCard should compose ProfileHeader + ProfileInfo + ProfileActions.

From Scrolls: Your progressive disclosure philosophy suggests hiding advanced settings initially.

From Signals: (Interesting!) Your audio work emphasizes feedback—in UI, this suggests real-time save status feedback as user edits profile.

Here's the component architecture..."
```

**The Signals → Sights connection is what makes Polly unique.** Your audio philosophy about feedback informs your UI design. Traditional AI tools can't make these leaps.

---

### Workflow 3: Technical Writing (Documentation)

**Cross-Domain Context:**

```
Task: Document API for norns library

Scrolls (Writing) provides:
├─ Your writing style (clear, pedagogical)
├─ Preference for "why" not just "what"
└─ Learning-oriented documentation approach

Signals (Audio) provides:
├─ Technical knowledge to document
├─ SuperCollider and norns context
└─ Common use cases

Sigils (Code) provides:
├─ Code examples
├─ API structure
└─ Implementation details

Glyphs (Systems Thinking) provides:
├─ How concepts relate
├─ Mental models to teach
└─ Conceptual architecture

Sights (Visual) provides:
├─ Diagram preferences
├─ Visual examples
└─ Layout aesthetics
```

**Polly's Synthesis:**

```
Polly (Scribe persona): "Creating documentation with full context:

From Scrolls: Your pedagogical approach suggests starting with 'why' before 'how'.

From Signals: You've built 8 norns instruments—I'll use your Phemto project as the primary example (most representative).

From Sigils: Your code comments show you prefer explaining reasoning, not just syntax.

From Glyphs: You teach concepts by showing relationships—I'll create a concept map showing how Engine → Script → Parameters connect.

From Sights: Your preference for visual clarity suggests including ASCII art diagrams for norns screen layouts.

Here's the documentation structure:

# norns Library Documentation

## Why This Library Exists
[Explains the problem it solves]

## Core Concepts
[Concept map showing relationships]

## Quick Start Example
[Uses your Phemto project as reference]

## API Reference
[Organized by your mental model]

## Advanced Patterns
[Based on your actual implementations]
```

**Cross-domain documentation is richer, clearer, and more useful.**

---

## 10. Competitive Analysis

### Head-to-Head Comparison

#### Polly Code vs. Cursor

**Cursor Strengths:**
- ✅ Excellent codebase understanding
- ✅ Fast code suggestions
- ✅ Large user base
- ✅ VSCode fork (familiar UI)
- ✅ GitHub integration

**Cursor Weaknesses:**
- ❌ Codebase-only context (no epub vectors)
- ❌ Cloud-dependent (privacy concerns)
- ❌ Subscription model ($20/month)
- ❌ No cross-domain learning
- ❌ No institutional memory
- ❌ No design integration

**Polly Code Advantages:**
- ✅ Context beyond code (epub vectors + domains)
- ✅ Edge-native (privacy + speed)
- ✅ One-time purchase (ownership)
- ✅ Cross-domain learning (polymathic)
- ✅ Institutional memory (why + what)
- ✅ Designer-Coder integration
- ✅ Profile-aware coding

**When to Choose Cursor:**
- You only code (no broader knowledge work)
- You're fine with cloud dependency
- You don't read technical books (no epub needs)
- You work in isolated codebases

**When to Choose Polly Code:**
- You're a polymath (work across domains)
- You value privacy and ownership
- You learn from technical documentation
- You want design-code integration
- You document your reasoning (institutional memory)

---

#### Polly Code vs. GitHub Copilot

**Copilot Strengths:**
- ✅ Trained on massive code corpus
- ✅ Excellent inline suggestions
- ✅ IDE integration (VSCode, JetBrains, etc.)
- ✅ $10/month (affordable)

**Copilot Weaknesses:**
- ❌ GitHub/Microsoft controlled
- ❌ Cloud-only (no offline)
- ❌ No customization (generic suggestions)
- ❌ No cross-domain context
- ❌ No documentation integration
- ❌ Subscription required

**Polly Code Advantages:**
- ✅ Your own AI (not Microsoft's)
- ✅ Offline capable
- ✅ Learns your style (profile-aware)
- ✅ Cross-domain context
- ✅ Documentation vectors integrated
- ✅ One-time purchase

**When to Choose Copilot:**
- You're happy with Microsoft integration
- You want minimal setup
- You don't need customization
- You're always online

**When to Choose Polly Code:**
- You want ownership and control
- You work offline frequently
- You want AI that learns your style
- You have domain expertise to leverage

---

#### Polly Code vs. Windsurf

**Windsurf Strengths:**
- ✅ AI-native (built for AI from ground-up)
- ✅ Modern architecture
- ✅ Intelligent code understanding

**Windsurf Weaknesses:**
- ❌ New/unproven (early stage)
- ❌ Cloud-dependent
- ❌ Subscription model
- ❌ Limited customization
- ❌ No domain integration

**Polly Code Advantages:**
- ✅ Proven foundation (Polly ecosystem)
- ✅ Edge-native architecture
- ✅ Ownership model
- ✅ Deep customization (domains, personas)
- ✅ Full domain integration

**When to Choose Windsurf:**
- You want bleeding-edge AI features
- You're early adopter type
- You value novelty

**When to Choose Polly Code:**
- You want proven, stable foundation
- You value privacy and ownership
- You have existing knowledge base (Polly vault)

---

### Competitive Matrix

| Feature | Cursor | Copilot | Windsurf | **Polly Code** |
|---------|--------|---------|----------|----------------|
| **Context Understanding** |
| Codebase analysis | ✅ Excellent | ✅ Good | ✅ Excellent | ✅ Excellent |
| Documentation (epub) | ❌ | ❌ | ❌ | ✅ **First-class** |
| Your notes/philosophy | ❌ | ❌ | ❌ | ✅ **Integrated** |
| Cross-domain learning | ❌ | ❌ | ❌ | ✅ **Polymathic** |
| Institutional memory | ⚠️ Git only | ❌ | ⚠️ Git only | ✅ **Why + What** |
| **Privacy & Ownership** |
| Data privacy | ⚠️ Cloud logs | ❌ Microsoft | ⚠️ Cloud | ✅ **Local-first** |
| Offline capability | ⚠️ Limited | ❌ | ⚠️ Limited | ✅ **Full** |
| Data ownership | ⚠️ Vendor | ❌ Vendor | ⚠️ Vendor | ✅ **You own it** |
| **Personalization** |
| Profile-aware | ❌ | ⚠️ Basic | ❌ | ✅ **Deep learning** |
| Learns your style | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited | ✅ **Comprehensive** |
| Custom workflows | ❌ | ❌ | ❌ | ✅ **Personas** |
| **Integration** |
| Designer integration | ❌ | ❌ | ❌ | ✅ **Living specs** |
| Multi-persona | ❌ | ❌ | ❌ | ✅ **Orchestrated** |
| Knowledge base | ❌ | ❌ | ❌ | ✅ **Polly vault** |
| **Pricing** |
| Model | Subscription | Subscription | Subscription | **One-time** |
| Monthly cost | $20 | $10 | TBD | **$0*** |
| 5-year cost | $1,200 | $600 | TBD | **$99-300** |

*After initial purchase, local inference is free. Cloud escalation pay-per-use.

---

### Market Positioning

**The AI Code Editor Quadrant:**

```
                    Integrated
                        ↑
                        |
        Windsurf        |      Cursor
            ●           |        ●
                        |
                        |
    Cloud ←─────────────+─────────────→ Local
                        |
                        |
         Copilot        |   POLLY CODE
            ●           |        ★
                        |
                        ↓
                    Standalone
```

**Polly Code's Unique Position:**
- **Local-first** (edge-native, privacy-focused)
- **Integrated** (part of Polly ecosystem, not isolated tool)
- **Context-rich** (beyond code: domains + documentation + philosophy)

**Tagline:**
> **"Context that thinks like you do"**

**Positioning Statement:**
> Every AI code editor treats code as the primary context. Polly Code is the first IDE that treats your entire knowledge system—documentation, design philosophy, past decisions, domain expertise—as equal to the codebase itself.

---

### Why Developers Will Switch

**Scenario 1: The Polymath Developer**

```
Current: Uses Cursor + Obsidian + Figma
Problem: Context constantly lost between tools

Switch to Polly Code:
├─ Code + notes + design in one place
├─ Context never lost (integrated)
├─ Cross-domain insights automatic
└─ Result: 30% faster, much better flow
```

**Scenario 2: The Privacy-Conscious Developer**

```
Current: Uses Copilot, worried about code privacy
Problem: Proprietary code sent to Microsoft

Switch to Polly Code:
├─ Fully local inference
├─ Zero cloud dependency (optional escalation)
├─ Company policy compliant
└─ Result: Same AI power, full privacy
```

**Scenario 3: The Learning Developer**

```
Current: Uses Cursor, constantly re-looking up docs
Problem: Context doesn't persist (reads docs, forgets, repeats)

Switch to Polly Code:
├─ Epub vectors indexed forever
├─ Documentation retrieved automatically
├─ "I remember reading..." moments solved
└─ Result: Learn faster, retain more
```

**Scenario 4: The Design-Conscious Developer**

```
Current: Uses Windsurf + Figma
Problem: Design → code handoff broken

Switch to Polly Code:
├─ Designer persona creates living specs
├─ Design tokens as single source of truth
├─ Implementation matches design exactly
└─ Result: Better designs, faster implementation
```

---

### Competitive Threats & Mitigations

**Threat 1: Cursor adds documentation integration**

**Likelihood:** Medium  
**Timeline:** 6-12 months  
**Mitigation:**
- Polly's cross-domain learning still unique
- Polly's edge-native architecture advantage remains
- Polly's persona system and orchestration can't be easily copied
- Move fast on Phase 17c (RAG integration) to build lead

**Threat 2: GitHub Copilot adds profile learning**

**Likelihood:** High  
**Timeline:** 12-18 months (Microsoft moves slowly)  
**Mitigation:**
- Polly's local-first approach still differentiated
- Polly's institutional memory deeper
- Polly's Designer integration unique
- Polly's ownership model appealing vs Microsoft control

**Threat 3: New entrant with similar vision**

**Likelihood:** Medium  
**Timeline:** 12-24 months  
**Mitigation:**
- First-mover advantage in polymathic coding
- Existing Polly ecosystem (Phase 1-16 complete)
- Community and user base building
- Strong design philosophy documented (this vision)

---

*[End of Part 2 - Core Differentiation]*


---

# PART 3: TECHNICAL ARCHITECTURE

## 11. Why Monaco Over VSCode Fork

### The Research Process

We evaluated five approaches for Polly Code's editor foundation:

1. **VSCode Fork** (Cursor's approach)
2. **Zed** (Modern Rust editor)
3. **Helix** (Terminal-based modal editor)
4. **Lapce** (Rust, modern architecture)
5. **Neovim** (Lua-scriptable, embeddable)
6. **Monaco Editor** (VSCode's editor component) ⭐

### Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Extensibility** | 30% | How easily can we integrate RAG, personas, domains? |
| **Maintenance** | 25% | Ongoing cost to maintain and update |
| **Stack Match** | 20% | Compatibility with Polly's TypeScript/Electron |
| **Timeline** | 15% | Time to functional IDE |
| **License** | 10% | Legal freedom to modify and distribute |

---

### Option 1: VSCode Fork (Cursor's Approach)

**How Cursor Did It:**

Cursor forked VSCodium (open-source VSCode) and added AI features:
- Forked entire VSCode codebase (~160,000 lines)
- Added AI chat panel
- Modified editor for inline suggestions
- Maintained fork separately from upstream

**Pros:**
- ✅ Full-featured IDE from day 1
- ✅ Huge extension ecosystem
- ✅ Users already familiar
- ✅ MIT licensed (free to fork)

**Cons:**
- ❌ **Massive maintenance burden**
  - 160,000+ lines of code to maintain
  - Monthly VSCode releases to merge
  - Conflicts with upstream changes
  - Breaking changes frequently
- ❌ **Limited deep integration**
  - Extension API restrictions
  - Can't modify core architecture easily
  - Workarounds for RAG/persona integration
- ❌ **Extension marketplace restrictions**
  - Microsoft controls marketplace
  - Must use alternative marketplace or sideload
- ❌ **Heavy bundle size**
  - Full Electron app ~200MB
  - Includes features Polly doesn't need

**Score:**
- Extensibility: 7/10 (good but constrained by extension API)
- Maintenance: 3/10 (very high ongoing cost)
- Stack Match: 10/10 (TypeScript/Electron)
- Timeline: 8/10 (2-3 months to AI-enhanced fork)
- License: 9/10 (MIT, but marketplace complications)
- **Overall: 6.8/10**

**Verdict:** ❌ Not recommended. Maintenance burden too high.

---

### Option 2: Zed Editor

**Overview:**
- Modern editor written in Rust
- GPU-accelerated rendering
- Collaborative features built-in
- 74.7k GitHub stars

**Pros:**
- ✅ Blazing fast performance
- ✅ Modern architecture (not legacy baggage)
- ✅ Built for collaboration
- ✅ Active development

**Cons:**
- ❌ **Different stack (Rust vs TypeScript)**
  - Polly is TypeScript/Electron
  - Would need Rust team
  - Integration challenging
- ❌ **Not embeddable**
  - Zed is standalone app
  - Can't embed in Polly
  - Would be separate tool
- ❌ **Less mature ecosystem**
  - Fewer extensions than VSCode
  - Smaller community

**Score:**
- Extensibility: 8/10 (good architecture)
- Maintenance: 6/10 (medium, but Rust learning curve)
- Stack Match: 2/10 (Rust, not TypeScript)
- Timeline: 7/10 (6-9 months with Rust learning)
- License: 10/10 (Apache 2.0)
- **Overall: 6.1/10**

**Verdict:** ❌ Not recommended. Stack mismatch.

---

### Option 3: Helix

**Overview:**
- Terminal-based modal editor
- Rust implementation
- Kakoune-inspired keybindings

**Pros:**
- ✅ Fast, efficient
- ✅ Good language support

**Cons:**
- ❌ **Terminal-only** (no GUI)
- ❌ Modal editing (vim-like) - not familiar to most users
- ❌ Not suitable for Polly's GUI needs

**Score:**
- Extensibility: 6/10
- Maintenance: 5/10
- Stack Match: 1/10
- Timeline: 8/10
- License: 10/10
- **Overall: 5.0/10**

**Verdict:** ❌ Not viable. Terminal-only doesn't fit Polly's GUI.

---

### Option 4: Lapce

**Overview:**
- Modern code editor in Rust
- Similar goals to Zed
- Native GUI (not Electron)

**Pros:**
- ✅ Fast, modern
- ✅ Cross-platform

**Cons:**
- ❌ Less mature than Zed
- ❌ Rust stack (same issue as Zed)
- ❌ Smaller community

**Score:**
- Extensibility: 7/10
- Maintenance: 6/10
- Stack Match: 2/10
- Timeline: 7/10
- License: 10/10
- **Overall: 5.8/10**

**Verdict:** ❌ Not recommended. Similar issues to Zed, less mature.

---

### Option 5: Neovim

**Overview:**
- Modern fork of Vim
- Lua-scriptable
- Embeddable via `--embed` flag

**Pros:**
- ✅ **Extremely extensible** (Lua scripting)
- ✅ **Embeddable** (can run in Polly)
- ✅ Huge plugin ecosystem
- ✅ Efficient, fast

**Cons:**
- ❌ **Modal editing** (steep learning curve)
- ❌ **Need to build full GUI** around it
  - Neovim is headless
  - Would need to implement entire UI layer
  - Massive development effort
- ❌ **9-12 month timeline**

**Score:**
- Extensibility: 10/10 (best extensibility)
- Maintenance: 7/10 (medium maintenance)
- Stack Match: 5/10 (embeddable but need GUI layer)
- Timeline: 3/10 (9-12 months)
- License: 10/10 (Apache 2.0)
- **Overall: 6.5/10**

**Verdict:** ⚠️ Interesting but timeline too long.

---

### Option 6: Monaco Editor ⭐ WINNER

**Overview:**
- VSCode's editor component extracted
- Powers VSCode, GitHub, Azure DevOps, StackBlitz
- Just the editor, no IDE

**Pros:**
- ✅ **Production-ready**
  - Used by millions daily
  - Battle-tested in VSCode
  - Mature, stable
- ✅ **Perfect stack match**
  - TypeScript/JavaScript
  - Runs in Electron (Polly's stack)
  - NPM package
- ✅ **Just the editor**
  - No IDE baggage
  - Build only what you need
  - Full control over features
- ✅ **MIT licensed**
  - Free to use commercially
  - No restrictions
- ✅ **Rich API**
  - Full programmatic control
  - LSP integration via `monaco-languageclient`
  - Custom language support
  - Theme customization
- ✅ **Deep integration possible**
  - Can inject RAG results anywhere
  - Full persona integration
  - No extension API limitations
- ✅ **Manageable maintenance**
  - Track Monaco (not full VSCode)
  - Breaking changes rare
  - Stable API
- ✅ **Reasonable timeline**
  - 3-5 months to functional IDE
  - Already familiar (used in Phase 16 Notes)

**Cons:**
- ⚠️ Need to build IDE shell
  - File tree (not included)
  - Terminal (use xterm.js)
  - Status bar (custom)
  - Settings UI (custom)
- ⚠️ No built-in extension marketplace
  - Need custom extension system if desired

**These "cons" are actually pros for Polly:**
- We want full control anyway
- We're building Polly-specific features (RAG, personas)
- Custom UI lets us match Polly's design language

**Score:**
- Extensibility: 10/10 (full control, no API limits)
- Maintenance: 7/10 (reasonable, manageable)
- Stack Match: 10/10 (perfect TypeScript/Electron fit)
- Timeline: 8/10 (3-5 months to functional IDE)
- License: 10/10 (MIT, completely free)
- **Overall: 9.2/10** ⭐

**Verdict:** ✅ **WINNER.** Best balance of all criteria.

---

### Monaco vs VSCode Fork: Direct Comparison

| Aspect | VSCode Fork | Monaco + Custom Shell |
|--------|-------------|----------------------|
| **Codebase Size** | 160,000+ lines | ~5,000 lines (Monaco) + your shell |
| **Maintenance** | Track entire VSCode | Track Monaco only |
| **Breaking Changes** | Monthly (VSCode releases) | Rare (stable API) |
| **Deep Integration** | Limited (extension API) | Full (direct access) |
| **Bundle Size** | ~200MB | ~50MB (just what you need) |
| **Customization** | Hard (modify core) | Easy (build your shell) |
| **RAG Integration** | Workarounds needed | Native integration |
| **Persona UI** | Extension API limits | Full control |
| **Timeline** | 2-3 months | 3-5 months |
| **Long-term Cost** | High (constant merging) | Low (stable foundation) |

**Monaco + Custom Shell wins on almost every dimension except initial timeline (only 1-2 months longer).**

---

### What Monaco Provides

**Editor Core:**
```typescript
import * as monaco from 'monaco-editor';

const editor = monaco.editor.create(container, {
  value: 'function hello() {\n\treturn "Hello, World!";\n}',
  language: 'javascript',
  theme: 'vs-dark',
  
  // Rich features built-in:
  automaticLayout: true,
  fontSize: 14,
  fontFamily: 'SF Mono, Consolas, monospace',
  minimap: { enabled: true },
  lineNumbers: 'on',
  folding: true,
  bracketPairColorization: { enabled: true },
  suggest: { enabled: true },
  quickSuggestions: true,
  wordWrap: 'on',
  
  // Full keyboard shortcuts
  // Multi-cursor editing
  // Find/replace with regex
  // Diff viewer
  // And 100+ more options
});
```

**Language Support (Built-in):**
- JavaScript/TypeScript
- Python
- Java
- C/C++/C#
- Go
- Rust
- Lua
- HTML/CSS
- JSON/YAML
- Markdown
- 60+ languages total

**Features (Out of Box):**
- Syntax highlighting
- Code folding
- Bracket matching
- Auto-indentation
- Multi-cursor editing
- Find/replace (regex support)
- Command palette
- Keyboard shortcuts
- Accessibility (ARIA, screen readers)
- RTL language support

---

### What You Build Around Monaco

**File Management:**
```
Custom File Tree:
├─ Directory browsing
├─ File icons
├─ Git status indicators
├─ Right-click context menu
├─ Drag-and-drop
└─ Search/filter
```

**Terminal Integration:**
```
xterm.js Terminal:
├─ Multiple terminal tabs
├─ Split terminals
├─ Shell selection (bash, zsh, fish)
├─ Color themes
└─ Copy/paste support
```

**IDE Chrome:**
```
Custom UI:
├─ Top menu bar
├─ Sidebar (files, git, search)
├─ Status bar (bottom)
├─ Activity bar (left)
└─ Panel (terminal, output)
```

**Polly-Specific:**
```
Polly Integration:
├─ RAG results panel
├─ Persona UI
├─ Chat interface
├─ Profile display
├─ Domain indicators
└─ Cross-domain links
```

**Total Custom Code:** ~5,000-10,000 lines (manageable)

---

### LSP Integration: `monaco-languageclient`

**Language Server Protocol (LSP):**

LSP provides professional IDE features:
- Go-to-definition
- Find references
- Hover information
- Code completion (IntelliSense)
- Diagnostics (errors, warnings)
- Code actions (quick fixes)
- Rename symbol

**monaco-languageclient:**

Connects Monaco to LSP servers:
```typescript
import { MonacoLanguageClient } from 'monaco-languageclient';
import { CloseAction, ErrorAction } from 'vscode-languageclient';

// Connect to TypeScript LSP server
const client = new MonacoLanguageClient({
  name: 'TypeScript Language Client',
  clientOptions: {
    documentSelector: ['typescript', 'javascript'],
    errorHandler: {
      error: () => ErrorAction.Continue,
      closed: () => CloseAction.DoNotRestart
    }
  },
  connectionProvider: {
    get: async () => {
      const connection = await createConnection();
      return connection;
    }
  }
});

client.start();
```

**LSP Servers Supported:**
- **TypeScript:** `tsserver` (Microsoft)
- **Python:** `pyright`, `pylsp`
- **Rust:** `rust-analyzer`
- **Go:** `gopls`
- **C/C++:** `clangd`
- **Java:** `eclipse.jdt.ls`
- **And 100+ more languages**

**Result:** Monaco + LSP = Professional IDE experience.

---

### Decision Matrix Summary

| Option | Extensibility | Maintenance | Stack Match | Timeline | License | **Total** |
|--------|--------------|-------------|-------------|----------|---------|-----------|
| VSCode Fork | 7/10 | 3/10 | 10/10 | 8/10 | 9/10 | 6.8/10 |
| Zed | 8/10 | 6/10 | 2/10 | 7/10 | 10/10 | 6.1/10 |
| Helix | 6/10 | 5/10 | 1/10 | 8/10 | 10/10 | 5.0/10 |
| Lapce | 7/10 | 6/10 | 2/10 | 7/10 | 10/10 | 5.8/10 |
| Neovim | 10/10 | 7/10 | 5/10 | 3/10 | 10/10 | 6.5/10 |
| **Monaco** | **10/10** | **7/10** | **10/10** | **8/10** | **10/10** | **9.2/10** ⭐ |

**Monaco wins decisively.**

---

## 12. Monaco Editor Foundation

### Integration Architecture

```
Polly App (Electron)
├─ Main Process
│  ├─ Window management
│  ├─ IPC with renderer
│  └─ LSP server processes
│
└─ Renderer Process
   ├─ React UI Framework
   ├─ Polly Code Tab
   │  ├─ Monaco Editor
   │  │  ├─ Editor instance
   │  │  ├─ Model manager
   │  │  └─ Language services
   │  ├─ File Tree Component
   │  ├─ Terminal Component (xterm.js)
   │  ├─ Git Panel Component
   │  ├─ Chat Panel Component
   │  └─ RAG Results Display
   └─ Other Polly Tabs (Notes, Graph, etc.)
```

### Core Implementation

**File:** `frontend/src/components/code/MonacoEditor.tsx`

```typescript
import React, { useEffect, useRef } from 'react';
import * as monaco from 'monaco-editor';
import { setupMonacoEnvironment } from './monaco-config';

interface MonacoEditorProps {
  initialValue?: string;
  language?: string;
  theme?: 'vs-dark' | 'vs-light' | 'hc-black';
  onChange?: (value: string) => void;
  onSave?: (value: string) => void;
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  initialValue = '',
  language = 'typescript',
  theme = 'vs-dark',
  onChange,
  onSave
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const editorInstance = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  
  useEffect(() => {
    if (!editorRef.current) return;
    
    // Setup Monaco environment (workers, etc.)
    setupMonacoEnvironment();
    
    // Create editor instance
    editorInstance.current = monaco.editor.create(editorRef.current, {
      value: initialValue,
      language: language,
      theme: theme,
      
      // Editor options
      fontSize: 13,
      fontFamily: 'SF Mono, Monaco, Consolas, Courier New, monospace',
      lineHeight: 20,
      letterSpacing: 0.5,
      
      // Features
      automaticLayout: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      folding: true,
      lineNumbers: 'on',
      renderLineHighlight: 'all',
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: true,
      
      // Bracket pair colorization
      bracketPairColorization: {
        enabled: true,
        independentColorPoolPerBracketType: true
      },
      
      // Suggestions
      quickSuggestions: {
        other: true,
        comments: false,
        strings: true
      },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnCommitCharacter: true,
      acceptSuggestionOnEnter: 'on',
      
      // Word wrap
      wordWrap: 'on',
      wordWrapColumn: 80,
      
      // Accessibility
      accessibilitySupport: 'auto',
      
      // Scrollbar
      scrollbar: {
        useShadows: false,
        verticalScrollbarSize: 10,
        horizontalScrollbarSize: 10
      }
    });
    
    // Listen to content changes
    editorInstance.current.onDidChangeModelContent(() => {
      const value = editorInstance.current?.getValue() || '';
      if (onChange) {
        onChange(value);
      }
    });
    
    // Listen to save command (Cmd+S / Ctrl+S)
    editorInstance.current.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
      () => {
        const value = editorInstance.current?.getValue() || '';
        if (onSave) {
          onSave(value);
        }
      }
    );
    
    // Cleanup
    return () => {
      editorInstance.current?.dispose();
    };
  }, []);
  
  // Update theme when it changes
  useEffect(() => {
    if (editorInstance.current) {
      monaco.editor.setTheme(theme);
    }
  }, [theme]);
  
  return (
    <div 
      ref={editorRef} 
      className="monaco-editor-container"
      style={{ width: '100%', height: '100%' }}
    />
  );
};
```

---

### Monaco Configuration

**File:** `frontend/src/components/code/monaco-config.ts`

```typescript
import * as monaco from 'monaco-editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';
import cssWorker from 'monaco-editor/esm/vs/language/css/css.worker?worker';
import htmlWorker from 'monaco-editor/esm/vs/language/html/html.worker?worker';
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker';

export function setupMonacoEnvironment() {
  // Setup web workers for Monaco
  self.MonacoEnvironment = {
    getWorker(_: any, label: string) {
      if (label === 'json') {
        return new jsonWorker();
      }
      if (label === 'css' || label === 'scss' || label === 'less') {
        return new cssWorker();
      }
      if (label === 'html' || label === 'handlebars' || label === 'razor') {
        return new htmlWorker();
      }
      if (label === 'typescript' || label === 'javascript') {
        return new tsWorker();
      }
      return new editorWorker();
    }
  };
}

/**
 * Custom Polly Code theme for Monaco
 */
export function definePollyTheme() {
  monaco.editor.defineTheme('polly-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'C586C0' },
      { token: 'string', foreground: 'CE9178' },
      { token: 'number', foreground: 'B5CEA8' },
      { token: 'function', foreground: 'DCDCAA' },
      { token: 'variable', foreground: '9CDCFE' },
      { token: 'type', foreground: '4EC9B0' }
    ],
    colors: {
      'editor.background': '#1e1e1e',
      'editor.foreground': '#d4d4d4',
      'editor.lineHighlightBackground': '#2a2a2a',
      'editorCursor.foreground': '#aeafad',
      'editor.selectionBackground': '#264f78',
      'editor.inactiveSelectionBackground': '#3a3d41'
    }
  });
  
  monaco.editor.setTheme('polly-dark');
}
```

---

### Model Management

**File:** `frontend/src/components/code/ModelManager.ts`

```typescript
import * as monaco from 'monaco-editor';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Manages Monaco editor models (one per open file)
 */
export class ModelManager {
  private models: Map<string, monaco.editor.ITextModel> = new Map();
  private editor: monaco.editor.IStandaloneCodeEditor;
  
  constructor(editor: monaco.editor.IStandaloneCodeEditor) {
    this.editor = editor;
  }
  
  /**
   * Open a file in the editor
   */
  async openFile(filePath: string): Promise<void> {
    // Check if model already exists
    let model = this.models.get(filePath);
    
    if (!model) {
      // Read file content
      const content = await fs.promises.readFile(filePath, 'utf-8');
      
      // Detect language
      const language = this.detectLanguage(filePath);
      
      // Create model
      const uri = monaco.Uri.file(filePath);
      model = monaco.editor.createModel(content, language, uri);
      
      // Store model
      this.models.set(filePath, model);
      
      // Listen for changes
      model.onDidChangeContent(() => {
        this.markDirty(filePath);
      });
    }
    
    // Set model as active in editor
    this.editor.setModel(model);
    
    // Focus editor
    this.editor.focus();
  }
  
  /**
   * Save current file
   */
  async saveCurrentFile(): Promise<void> {
    const model = this.editor.getModel();
    if (!model) return;
    
    const filePath = model.uri.fsPath;
    const content = model.getValue();
    
    await fs.promises.writeFile(filePath, content, 'utf-8');
    
    // Mark as saved (remove dirty indicator)
    this.markClean(filePath);
  }
  
  /**
   * Close a file
   */
  closeFile(filePath: string): void {
    const model = this.models.get(filePath);
    if (model) {
      model.dispose();
      this.models.delete(filePath);
    }
  }
  
  /**
   * Get all open files
   */
  getOpenFiles(): string[] {
    return Array.from(this.models.keys());
  }
  
  /**
   * Detect language from file extension
   */
  private detectLanguage(filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();
    
    const languageMap: Record<string, string> = {
      '.js': 'javascript',
      '.jsx': 'javascript',
      '.ts': 'typescript',
      '.tsx': 'typescript',
      '.py': 'python',
      '.rs': 'rust',
      '.go': 'go',
      '.c': 'c',
      '.cpp': 'cpp',
      '.h': 'c',
      '.hpp': 'cpp',
      '.cs': 'csharp',
      '.java': 'java',
      '.lua': 'lua',
      '.rb': 'ruby',
      '.php': 'php',
      '.html': 'html',
      '.css': 'css',
      '.scss': 'scss',
      '.json': 'json',
      '.md': 'markdown',
      '.yaml': 'yaml',
      '.yml': 'yaml',
      '.xml': 'xml',
      '.sh': 'shell',
      '.bash': 'shell'
    };
    
    return languageMap[ext] || 'plaintext';
  }
  
  private markDirty(filePath: string): void {
    // TODO: Update UI to show file is modified
    // (e.g., add dot or asterisk to tab)
  }
  
  private markClean(filePath: string): void {
    // TODO: Update UI to show file is saved
  }
}
```

---

## 13. Custom IDE Shell Architecture

### Component Structure

```
Polly Code IDE
│
├─ Top Bar
│  ├─ Menu (File, Edit, View, etc.)
│  ├─ Breadcrumb (current file path)
│  └─ Persona selector
│
├─ Activity Bar (Left)
│  ├─ Files (file tree)
│  ├─ Search (project-wide search)
│  ├─ Git (source control)
│  ├─ RAG (context retrieval)
│  └─ Settings
│
├─ Sidebar (Left, conditional)
│  ├─ File Tree Panel
│  ├─ Search Results Panel
│  ├─ Git Status Panel
│  ├─ RAG Results Panel
│  └─ Settings Panel
│
├─ Editor Area (Center)
│  ├─ Tab Bar (open files)
│  ├─ Monaco Editor
│  ├─ Diff Viewer (for git diffs)
│  └─ Split Editor (side-by-side)
│
├─ Chat Panel (Right, collapsible)
│  ├─ Persona indicator
│  ├─ Context display
│  ├─ Chat messages
│  └─ Input area
│
├─ Panel Area (Bottom, collapsible)
│  ├─ Integrated Terminal (xterm.js)
│  ├─ Problems (diagnostics)
│  ├─ Output (build output)
│  └─ Debug Console (future)
│
└─ Status Bar (Bottom)
   ├─ Git branch
   ├─ File info (language, encoding, line endings)
   ├─ Cursor position (line:column)
   ├─ Errors/warnings count
   └─ Active persona indicator
```

---

### File Tree Implementation

**File:** `frontend/src/components/code/FileTree.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import * as fs from 'fs';
import * as path from 'path';
import { FileTreeNode, GitStatus } from './types';
import { getGitStatus } from './git-utils';

interface FileTreeProps {
  projectPath: string;
  onFileClick: (filePath: string) => void;
  currentFile?: string;
}

export const FileTree: React.FC<FileTreeProps> = ({
  projectPath,
  onFileClick,
  currentFile
}) => {
  const [tree, setTree] = useState<FileTreeNode[]>([]);
  const [gitStatus, setGitStatus] = useState<Map<string, GitStatus>>(new Map());
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());
  
  useEffect(() => {
    loadFileTree();
  }, [projectPath]);
  
  async function loadFileTree() {
    const git = await getGitStatus(projectPath);
    setGitStatus(git);
    
    const nodes = await buildTreeNodes(projectPath, projectPath, git);
    setTree(nodes);
  }
  
  async function buildTreeNodes(
    dirPath: string,
    rootPath: string,
    gitStatus: Map<string, GitStatus>
  ): Promise<FileTreeNode[]> {
    const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
    const nodes: FileTreeNode[] = [];
    
    for (const entry of entries) {
      // Skip hidden files and node_modules
      if (entry.name.startsWith('.') || entry.name === 'node_modules') {
        continue;
      }
      
      const fullPath = path.join(dirPath, entry.name);
      const relativePath = path.relative(rootPath, fullPath);
      
      if (entry.isDirectory()) {
        const children = await buildTreeNodes(fullPath, rootPath, gitStatus);
        nodes.push({
          type: 'directory',
          name: entry.name,
          path: fullPath,
          children,
          expanded: expandedDirs.has(fullPath)
        });
      } else {
        nodes.push({
          type: 'file',
          name: entry.name,
          path: fullPath,
          gitStatus: gitStatus.get(relativePath)
        });
      }
    }
    
    // Sort: directories first, then files
    return nodes.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'directory' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
  }
  
  function toggleDirectory(dirPath: string) {
    setExpandedDirs(prev => {
      const next = new Set(prev);
      if (next.has(dirPath)) {
        next.delete(dirPath);
      } else {
        next.add(dirPath);
      }
      return next;
    });
  }
  
  function renderNode(node: FileTreeNode, depth: number = 0) {
    const indent = depth * 16;
    const isCurrentFile = node.type === 'file' && node.path === currentFile;
    
    if (node.type === 'directory') {
      return (
        <div key={node.path}>
          <div
            className="file-tree-node directory"
            style={{ paddingLeft: `${indent}px` }}
            onClick={() => toggleDirectory(node.path)}
          >
            <span className="icon">
              {node.expanded ? '📂' : '📁'}
            </span>
            <span className="name">{node.name}</span>
          </div>
          {node.expanded && node.children && (
            <div className="children">
              {node.children.map(child => renderNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    } else {
      return (
        <div
          key={node.path}
          className={`file-tree-node file ${isCurrentFile ? 'active' : ''}`}
          style={{ paddingLeft: `${indent}px` }}
          onClick={() => onFileClick(node.path)}
        >
          <span className="icon">{getFileIcon(node.name)}</span>
          <span className="name">{node.name}</span>
          {node.gitStatus && (
            <span className={`git-status ${node.gitStatus}`}>
              {getGitStatusIndicator(node.gitStatus)}
            </span>
          )}
        </div>
      );
    }
  }
  
  return (
    <div className="file-tree">
      <div className="file-tree-header">
        <span>Files</span>
        <button onClick={loadFileTree}>⟳</button>
      </div>
      <div className="file-tree-content">
        {tree.map(node => renderNode(node))}
      </div>
    </div>
  );
};

function getFileIcon(fileName: string): string {
  const ext = path.extname(fileName).toLowerCase();
  const iconMap: Record<string, string> = {
    '.js': '📜',
    '.ts': '📘',
    '.py': '🐍',
    '.rs': '🦀',
    '.go': '🐹',
    '.java': '☕',
    '.html': '🌐',
    '.css': '🎨',
    '.json': '📋',
    '.md': '📝'
  };
  return iconMap[ext] || '📄';
}

function getGitStatusIndicator(status: GitStatus): string {
  switch (status) {
    case 'modified': return 'M';
    case 'added': return 'A';
    case 'deleted': return 'D';
    case 'untracked': return 'U';
    default: return '';
  }
}
```

---

### Terminal Integration

**File:** `frontend/src/components/code/Terminal.tsx`

```typescript
import React, { useEffect, useRef } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import * as pty from 'node-pty';

interface TerminalProps {
  shell?: string;
  cwd?: string;
  onExit?: () => void;
}

export const Terminal: React.FC<TerminalProps> = ({
  shell = process.env.SHELL || 'bash',
  cwd = process.cwd(),
  onExit
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const ptyProcessRef = useRef<any>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Create xterm instance
    const xterm = new XTerm({
      cursorBlink: true,
      fontSize: 13,
      fontFamily: 'SF Mono, Monaco, Consolas, Courier New, monospace',
      lineHeight: 1.5,
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#aeafad',
        selection: '#264f78',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#ffffff'
      },
      allowTransparency: false,
      scrollback: 10000
    });
    
    // Add addons
    const fitAddon = new FitAddon();
    xterm.loadAddon(fitAddon);
    xterm.loadAddon(new WebLinksAddon());
    
    // Open terminal
    xterm.open(containerRef.current);
    fitAddon.fit();
    
    // Create PTY process
    const ptyProcess = pty.spawn(shell, [], {
      name: 'xterm-256color',
      cols: xterm.cols,
      rows: xterm.rows,
      cwd: cwd,
      env: process.env as any
    });
    
    // Wire up data flow
    ptyProcess.onData(data => {
      xterm.write(data);
    });
    
    xterm.onData(data => {
      ptyProcess.write(data);
    });
    
    // Handle resize
    xterm.onResize(({ cols, rows }) => {
      ptyProcess.resize(cols, rows);
    });
    
    // Handle process exit
    ptyProcess.onExit(() => {
      if (onExit) {
        onExit();
      }
    });
    
    // Store refs
    xtermRef.current = xterm;
    ptyProcessRef.current = ptyProcess;
    fitAddonRef.current = fitAddon;
    
    // Handle window resize
    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      ptyProcess.kill();
      xterm.dispose();
    };
  }, [shell, cwd]);
  
  return (
    <div 
      ref={containerRef} 
      className="terminal-container"
      style={{ width: '100%', height: '100%' }}
    />
  );
};
```

---

*[To be continued in next part...]*


#### 4. Git Integration Component

The Git integration provides visual status indicators and common operations without leaving the editor:

```typescript
// src/renderer/components/git/GitPanel.tsx
import React, { useState, useEffect } from 'react';
import simpleGit, { SimpleGit, StatusResult } from 'simple-git';
import { FileIcon } from '../icons/FileIcon';

interface GitPanelProps {
  workspaceRoot: string;
}

export const GitPanel: React.FC<GitPanelProps> = ({ workspaceRoot }) => {
  const [git, setGit] = useState<SimpleGit | null>(null);
  const [status, setStatus] = useState<StatusResult | null>(null);
  const [branch, setBranch] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const gitInstance = simpleGit(workspaceRoot);
    setGit(gitInstance);
    refreshStatus(gitInstance);
  }, [workspaceRoot]);

  const refreshStatus = async (gitInstance: SimpleGit) => {
    try {
      setLoading(true);
      const status = await gitInstance.status();
      const branch = await gitInstance.branch();
      setStatus(status);
      setBranch(branch.current);
    } catch (error) {
      console.error('Git status error:', error);
    } finally {
      setLoading(false);
    }
  };

  const stageFile = async (file: string) => {
    if (!git) return;
    try {
      await git.add(file);
      await refreshStatus(git);
    } catch (error) {
      console.error('Git add error:', error);
    }
  };

  const unstageFile = async (file: string) => {
    if (!git) return;
    try {
      await git.reset(['HEAD', file]);
      await refreshStatus(git);
    } catch (error) {
      console.error('Git reset error:', error);
    }
  };

  const commit = async (message: string) => {
    if (!git) return;
    try {
      await git.commit(message);
      await refreshStatus(git);
    } catch (error) {
      console.error('Git commit error:', error);
    }
  };

  const push = async () => {
    if (!git) return;
    try {
      setLoading(true);
      await git.push();
      await refreshStatus(git);
    } catch (error) {
      console.error('Git push error:', error);
    } finally {
      setLoading(false);
    }
  };

  const pull = async () => {
    if (!git) return;
    try {
      setLoading(true);
      await git.pull();
      await refreshStatus(git);
    } catch (error) {
      console.error('Git pull error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!status) {
    return <div className="git-panel loading">Loading git status...</div>;
  }

  return (
    <div className="git-panel">
      {/* Branch info */}
      <div className="git-header">
        <div className="branch-info">
          <span className="branch-icon">⎇</span>
          <span className="branch-name">{branch}</span>
          {status.ahead > 0 && (
            <span className="ahead-badge">↑{status.ahead}</span>
          )}
          {status.behind > 0 && (
            <span className="behind-badge">↓{status.behind}</span>
          )}
        </div>
        <div className="git-actions">
          <button onClick={pull} disabled={loading}>Pull</button>
          <button onClick={push} disabled={loading}>Push</button>
          <button onClick={() => refreshStatus(git!)}>Refresh</button>
        </div>
      </div>

      {/* Changes section */}
      <div className="git-changes">
        {/* Staged changes */}
        {status.staged.length > 0 && (
          <div className="change-group">
            <div className="group-header">
              <span className="group-title">Staged Changes ({status.staged.length})</span>
            </div>
            <div className="file-list">
              {status.staged.map(file => (
                <div key={file} className="git-file staged">
                  <FileIcon filename={file} />
                  <span className="file-path">{file}</span>
                  <button 
                    className="unstage-btn"
                    onClick={() => unstageFile(file)}
                  >
                    −
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Modified files */}
        {status.modified.length > 0 && (
          <div className="change-group">
            <div className="group-header">
              <span className="group-title">Changes ({status.modified.length})</span>
            </div>
            <div className="file-list">
              {status.modified.map(file => (
                <div key={file} className="git-file modified">
                  <FileIcon filename={file} />
                  <span className="file-path">{file}</span>
                  <button 
                    className="stage-btn"
                    onClick={() => stageFile(file)}
                  >
                    +
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Untracked files */}
        {status.not_added.length > 0 && (
          <div className="change-group">
            <div className="group-header">
              <span className="group-title">Untracked ({status.not_added.length})</span>
            </div>
            <div className="file-list">
              {status.not_added.map(file => (
                <div key={file} className="git-file untracked">
                  <FileIcon filename={file} />
                  <span className="file-path">{file}</span>
                  <button 
                    className="stage-btn"
                    onClick={() => stageFile(file)}
                  >
                    +
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Commit section */}
      {status.staged.length > 0 && (
        <CommitBox onCommit={commit} disabled={loading} />
      )}
    </div>
  );
};

interface CommitBoxProps {
  onCommit: (message: string) => Promise<void>;
  disabled: boolean;
}

const CommitBox: React.FC<CommitBoxProps> = ({ onCommit, disabled }) => {
  const [message, setMessage] = useState('');

  const handleCommit = async () => {
    if (message.trim()) {
      await onCommit(message);
      setMessage('');
    }
  };

  return (
    <div className="commit-box">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Commit message..."
        rows={3}
      />
      <button 
        onClick={handleCommit}
        disabled={disabled || !message.trim()}
      >
        Commit
      </button>
    </div>
  );
};
```

**Why This Matters**: Unlike VSCode extensions that use the Git API through an abstraction layer, we have direct access to the git process. This enables:
- Real-time status updates without polling
- Direct integration with Polly's institutional memory (commit messages inform context)
- Custom workflows (e.g., "Ask Architect before committing breaking changes")

#### 5. Chat Panel Component

The Chat panel is where Polly personas interact with the code. This is the key differentiator—chat isn't a sidebar, it's integrated into the development flow:

```typescript
// src/renderer/components/chat/ChatPanel.tsx
import React, { useState, useEffect, useRef } from 'react';
import { PersonaType } from '@shared/types/personas';
import { ChatMessage } from '@shared/types/chat';
import { CodeBlock } from './CodeBlock';
import { PersonaSelector } from './PersonaSelector';

interface ChatPanelProps {
  workspaceRoot: string;
  currentFile: string | null;
  selection: { text: string; range: any } | null;
  onInsertCode: (code: string, location?: any) => void;
  onOpenFile: (path: string, line?: number) => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  workspaceRoot,
  currentFile,
  selection,
  onInsertCode,
  onOpenFile
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [activePersona, setActivePersona] = useState<PersonaType>('programmer');
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
      context: {
        currentFile,
        selection: selection?.text,
        workspaceRoot
      }
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);

    try {
      // Send to Polly backend with full context
      const response = await window.electron.invoke('chat:send', {
        message: input,
        persona: activePersona,
        context: {
          currentFile,
          selection: selection?.text,
          workspaceRoot,
          // Include RAG context
          ragContext: await window.electron.invoke('rag:retrieve', {
            query: input,
            workspaceRoot,
            domains: ['code', 'docs', 'design'] // Cross-domain retrieval
          })
        }
      });

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content,
        persona: activePersona,
        timestamp: new Date(),
        codeBlocks: response.codeBlocks,
        references: response.references
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsThinking(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      sendMessage();
    }
  };

  return (
    <div className="chat-panel">
      {/* Persona selector */}
      <PersonaSelector
        activePersona={activePersona}
        onChange={setActivePersona}
      />

      {/* Messages */}
      <div className="chat-messages">
        {messages.map(message => (
          <ChatMessageView
            key={message.id}
            message={message}
            onInsertCode={onInsertCode}
            onOpenFile={onOpenFile}
          />
        ))}
        {isThinking && (
          <div className="thinking-indicator">
            <span className="persona-name">{activePersona}</span> is thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        {selection && (
          <div className="context-badge">
            Context: {selection.text.length} chars selected
          </div>
        )}
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask ${activePersona} anything... (Cmd+Enter to send)`}
          rows={3}
        />
        <button onClick={sendMessage} disabled={isThinking || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

interface ChatMessageViewProps {
  message: ChatMessage;
  onInsertCode: (code: string, location?: any) => void;
  onOpenFile: (path: string, line?: number) => void;
}

const ChatMessageView: React.FC<ChatMessageViewProps> = ({
  message,
  onInsertCode,
  onOpenFile
}) => {
  return (
    <div className={`chat-message ${message.role}`}>
      {message.persona && (
        <div className="message-header">
          <span className="persona-badge">{message.persona}</span>
          <span className="timestamp">
            {message.timestamp.toLocaleTimeString()}
          </span>
        </div>
      )}
      
      <div className="message-content">
        {message.content}
      </div>

      {/* Code blocks with insert button */}
      {message.codeBlocks?.map((block, idx) => (
        <CodeBlock
          key={idx}
          code={block.code}
          language={block.language}
          onInsert={() => onInsertCode(block.code)}
        />
      ))}

      {/* References (from RAG) */}
      {message.references?.map((ref, idx) => (
        <div key={idx} className="reference">
          <span className="reference-type">{ref.type}</span>
          <a onClick={() => onOpenFile(ref.path, ref.line)}>
            {ref.title}
          </a>
        </div>
      ))}
    </div>
  );
};
```

**Key Innovation**: The chat panel receives RAG context from ALL domains (code, docs, design, audio, philosophy). When you ask "How should I structure this synth?", the Programmer persona can reference:
- Your SuperCollider documentation (Scrolls domain)
- Past norns instrument code (Sigils domain)
- Your design philosophy on constraint-based systems (Scrolls domain)
- Similar synthesis patterns from your knowledge graph (Signals domain)

**No competitor does this**—Cursor/Copilot only see code context.

#### 6. Status Bar Component

The status bar provides at-a-glance information about the editor state, LSP status, and Polly context:

```typescript
// src/renderer/components/statusbar/StatusBar.tsx
import React from 'react';
import { EditorState } from '@shared/types/editor';

interface StatusBarProps {
  editorState: EditorState;
  lspStatus: LSPStatus;
  ragStatus: RAGStatus;
  gitBranch?: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  editorState,
  lspStatus,
  ragStatus,
  gitBranch
}) => {
  return (
    <div className="status-bar">
      {/* Left side - file info */}
      <div className="status-left">
        {editorState.currentFile && (
          <>
            <span className="file-name">{editorState.currentFile}</span>
            <span className="separator">|</span>
            <span className="position">
              Ln {editorState.cursor.line}, Col {editorState.cursor.column}
            </span>
            {editorState.selection && (
              <span className="selection">
                ({editorState.selection.length} selected)
              </span>
            )}
          </>
        )}
      </div>

      {/* Center - LSP status */}
      <div className="status-center">
        {lspStatus.servers.map(server => (
          <div key={server.language} className="lsp-indicator">
            <span 
              className={`status-dot ${server.status}`}
              title={`${server.language} LSP: ${server.status}`}
            />
            <span className="language">{server.language}</span>
          </div>
        ))}
      </div>

      {/* Right side - git, RAG, encoding */}
      <div className="status-right">
        {/* RAG status - unique to Polly */}
        <div className="rag-indicator" title={ragStatus.tooltip}>
          <span className="rag-icon">🧠</span>
          <span className="rag-count">{ragStatus.vectorCount} vectors</span>
          {ragStatus.isIndexing && <span className="spinner">⟳</span>}
        </div>

        {gitBranch && (
          <div className="git-indicator">
            <span className="git-icon">⎇</span>
            <span className="branch">{gitBranch}</span>
          </div>
        )}

        <span className="encoding">{editorState.encoding || 'UTF-8'}</span>
        <span className="eol">{editorState.eol || 'LF'}</span>
        <span className="language">{editorState.language || 'Plain Text'}</span>
      </div>
    </div>
  );
};

interface LSPStatus {
  servers: Array<{
    language: string;
    status: 'connected' | 'connecting' | 'error' | 'disconnected';
  }>;
}

interface RAGStatus {
  vectorCount: number;
  isIndexing: boolean;
  tooltip: string;
}
```

**The RAG indicator** in the status bar is unique to Polly—it shows how much context is available and whether new vectors are being indexed. This gives developers confidence that their documentation, past code, and domain knowledge are actively informing suggestions.

#### 7. Full Shell Integration

Now we wire everything together in the main IDE shell:

```typescript
// src/renderer/components/IDEShell.tsx
import React, { useState, useEffect } from 'react';
import { SplitPane } from './layout/SplitPane';
import { FileTree } from './filetree/FileTree';
import { MonacoEditor } from './editor/MonacoEditor';
import { Terminal } from './terminal/Terminal';
import { GitPanel } from './git/GitPanel';
import { ChatPanel } from './chat/ChatPanel';
import { StatusBar } from './statusbar/StatusBar';
import { TabBar } from './tabs/TabBar';

export const IDEShell: React.FC = () => {
  const [workspaceRoot, setWorkspaceRoot] = useState<string>('');
  const [openFiles, setOpenFiles] = useState<OpenFile[]>([]);
  const [activeFileIndex, setActiveFileIndex] = useState<number>(0);
  const [editorState, setEditorState] = useState<EditorState>({});
  const [showSidebar, setShowSidebar] = useState(true);
  const [showTerminal, setShowTerminal] = useState(true);
  const [showChat, setShowChat] = useState(true);
  const [activeSidebarPanel, setActiveSidebarPanel] = useState<'files' | 'git'>('files');

  // Initialize workspace
  useEffect(() => {
    const initWorkspace = async () => {
      const root = await window.electron.invoke('workspace:getRoot');
      setWorkspaceRoot(root);
    };
    initWorkspace();
  }, []);

  // File operations
  const openFile = async (path: string) => {
    // Check if already open
    const existingIndex = openFiles.findIndex(f => f.path === path);
    if (existingIndex !== -1) {
      setActiveFileIndex(existingIndex);
      return;
    }

    // Read file content
    const content = await window.electron.invoke('file:read', path);
    const newFile: OpenFile = {
      path,
      content,
      isDirty: false,
      model: null // Monaco model will be created by editor
    };

    setOpenFiles(prev => [...prev, newFile]);
    setActiveFileIndex(openFiles.length);
  };

  const closeFile = (index: number) => {
    const file = openFiles[index];
    if (file.isDirty) {
      // TODO: Show save dialog
    }

    setOpenFiles(prev => prev.filter((_, i) => i !== index));
    if (activeFileIndex >= openFiles.length - 1) {
      setActiveFileIndex(Math.max(0, openFiles.length - 2));
    }
  };

  const saveFile = async (index: number) => {
    const file = openFiles[index];
    await window.electron.invoke('file:write', {
      path: file.path,
      content: file.content
    });

    setOpenFiles(prev => prev.map((f, i) => 
      i === index ? { ...f, isDirty: false } : f
    ));
  };

  const insertCode = (code: string, location?: any) => {
    // Insert code at cursor or specified location
    const activeFile = openFiles[activeFileIndex];
    if (!activeFile) return;

    // Monaco editor will handle the actual insertion
    window.electron.send('editor:insertCode', {
      path: activeFile.path,
      code,
      location
    });
  };

  return (
    <div className="ide-shell">
      {/* Top menu bar */}
      <div className="menu-bar">
        <button onClick={() => setShowSidebar(!showSidebar)}>
          Toggle Sidebar
        </button>
        <button onClick={() => setShowTerminal(!showTerminal)}>
          Toggle Terminal
        </button>
        <button onClick={() => setShowChat(!showChat)}>
          Toggle Chat
        </button>
      </div>

      {/* Main layout */}
      <div className="ide-body">
        {/* Sidebar - File tree or Git panel */}
        {showSidebar && (
          <div className="sidebar">
            <div className="sidebar-tabs">
              <button
                className={activeSidebarPanel === 'files' ? 'active' : ''}
                onClick={() => setActiveSidebarPanel('files')}
              >
                Files
              </button>
              <button
                className={activeSidebarPanel === 'git' ? 'active' : ''}
                onClick={() => setActiveSidebarPanel('git')}
              >
                Git
              </button>
            </div>
            {activeSidebarPanel === 'files' ? (
              <FileTree
                rootPath={workspaceRoot}
                onFileClick={openFile}
              />
            ) : (
              <GitPanel workspaceRoot={workspaceRoot} />
            )}
          </div>
        )}

        {/* Editor area */}
        <SplitPane
          split="horizontal"
          primary="first"
          defaultSize="70%"
        >
          {/* Top: Editor + Chat */}
          <SplitPane
            split="vertical"
            primary="first"
            defaultSize={showChat ? "70%" : "100%"}
          >
            {/* Editor */}
            <div className="editor-pane">
              {openFiles.length > 0 && (
                <>
                  <TabBar
                    files={openFiles}
                    activeIndex={activeFileIndex}
                    onTabClick={setActiveFileIndex}
                    onTabClose={closeFile}
                  />
                  <MonacoEditor
                    file={openFiles[activeFileIndex]}
                    onChange={(content) => {
                      setOpenFiles(prev => prev.map((f, i) => 
                        i === activeFileIndex 
                          ? { ...f, content, isDirty: true }
                          : f
                      ));
                    }}
                    onStateChange={setEditorState}
                  />
                </>
              )}
            </div>

            {/* Chat panel */}
            {showChat && (
              <ChatPanel
                workspaceRoot={workspaceRoot}
                currentFile={openFiles[activeFileIndex]?.path}
                selection={editorState.selection}
                onInsertCode={insertCode}
                onOpenFile={openFile}
              />
            )}
          </SplitPane>

          {/* Bottom: Terminal */}
          {showTerminal && (
            <Terminal
              cwd={workspaceRoot}
              onExit={() => setShowTerminal(false)}
            />
          )}
        </SplitPane>
      </div>

      {/* Status bar */}
      <StatusBar
        editorState={editorState}
        lspStatus={{
          servers: [] // TODO: Connect to LSP
        }}
        ragStatus={{
          vectorCount: 0, // TODO: Connect to RAG
          isIndexing: false,
          tooltip: 'RAG vectors available'
        }}
      />
    </div>
  );
};

interface OpenFile {
  path: string;
  content: string;
  isDirty: boolean;
  model: any; // monaco.editor.ITextModel
}

interface EditorState {
  currentFile?: string;
  cursor?: { line: number; column: number };
  selection?: { text: string; length: number; range: any };
  encoding?: string;
  eol?: string;
  language?: string;
}
```

**Why This Architecture Works**:

1. **Composable**: Each component is independent and can be developed/tested separately
2. **Flexible**: Layout can be adjusted (side-by-side chat vs. bottom panel)
3. **Performant**: React components update only when their props change
4. **Extensible**: Easy to add new panels (Settings, Search, Problems, etc.)

**Key Advantages Over VSCode Extension**:
- Direct access to all components (no extension API bottleneck)
- Custom layout engine (not constrained by VSCode's panel system)
- Real-time coordination between panels (Chat can directly modify Editor)
- No message passing overhead (everything in one process)

---

### Section 14: Language Intelligence Layer

The Language Intelligence Layer provides code completion, diagnostics, hover information, and other IDE features through Language Server Protocol (LSP) integration. This is what makes Polly Code feel like a "real" IDE rather than just a text editor.

#### LSP Integration Architecture

We use **monaco-languageclient** to bridge Monaco Editor with LSP servers:

```typescript
// src/renderer/services/lsp/LSPManager.ts
import {
  MonacoLanguageClient,
  CloseAction,
  ErrorAction,
  MonacoServices,
  createConnection
} from 'monaco-languageclient';
import {
  toSocket,
  WebSocketMessageReader,
  WebSocketMessageWriter
} from 'vscode-ws-jsonrpc';
import * as monaco from 'monaco-editor';

interface LSPServerConfig {
  language: string;
  command: string;
  args: string[];
  initializationOptions?: any;
}

export class LSPManager {
  private clients: Map<string, MonacoLanguageClient> = new Map();
  private serverConfigs: LSPServerConfig[] = [];

  constructor() {
    // Install Monaco language client services
    MonacoServices.install(monaco);
  }

  // Register language server configuration
  registerServer(config: LSPServerConfig) {
    this.serverConfigs.push(config);
  }

  // Start language server for a specific language
  async startServer(language: string): Promise<void> {
    const config = this.serverConfigs.find(c => c.language === language);
    if (!config) {
      throw new Error(`No LSP server configured for ${language}`);
    }

    // Spawn language server process
    const serverProcess = await window.electron.invoke('lsp:spawn', {
      command: config.command,
      args: config.args
    });

    // Create WebSocket connection to server
    const socket = new WebSocket(`ws://localhost:${serverProcess.port}`);
    socket.onopen = () => {
      const connection = createConnection(
        new WebSocketMessageReader(toSocket(socket)),
        new WebSocketMessageWriter(toSocket(socket)),
        console
      );

      // Create language client
      const client = new MonacoLanguageClient({
        name: `${language} Language Client`,
        clientOptions: {
          documentSelector: [{ language }],
          errorHandler: {
            error: () => ErrorAction.Continue,
            closed: () => CloseAction.Restart
          },
          initializationOptions: config.initializationOptions
        },
        connectionProvider: {
          get: (errorHandler, closeHandler) => {
            return Promise.resolve(connection);
          }
        }
      });

      // Start client
      client.start();
      connection.listen();

      this.clients.set(language, client);
    };
  }

  // Stop language server
  async stopServer(language: string): Promise<void> {
    const client = this.clients.get(language);
    if (client) {
      await client.stop();
      this.clients.delete(language);
      await window.electron.invoke('lsp:kill', language);
    }
  }

  // Stop all servers
  async stopAll(): Promise<void> {
    await Promise.all(
      Array.from(this.clients.keys()).map(lang => this.stopServer(lang))
    );
  }
}
```

#### Main Process LSP Server Management

The main process handles spawning and managing LSP server processes:

```typescript
// src/main/services/LSPService.ts
import { spawn, ChildProcess } from 'child_process';
import { WebSocketServer } from 'ws';
import { createMessageConnection, StreamMessageReader, StreamMessageWriter } from 'vscode-jsonrpc/node';

interface SpawnedServer {
  process: ChildProcess;
  port: number;
  wsServer: WebSocketServer;
}

export class LSPService {
  private servers: Map<string, SpawnedServer> = new Map();
  private nextPort = 9000;

  async spawnServer(language: string, command: string, args: string[]): Promise<number> {
    // Spawn LSP server process
    const serverProcess = spawn(command, args, {
      stdio: 'pipe'
    });

    if (!serverProcess.stdout || !serverProcess.stdin) {
      throw new Error('Failed to spawn LSP server');
    }

    // Create WebSocket server to proxy LSP messages
    const port = this.nextPort++;
    const wsServer = new WebSocketServer({ port });

    wsServer.on('connection', (ws) => {
      // Create JSON-RPC connection to LSP server process
      const connection = createMessageConnection(
        new StreamMessageReader(serverProcess.stdout!),
        new StreamMessageWriter(serverProcess.stdin!)
      );

      // Forward WebSocket messages to LSP server
      ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        connection.sendNotification(message.method, message.params);
      });

      // Forward LSP server messages to WebSocket
      connection.onNotification((method, params) => {
        ws.send(JSON.stringify({ method, params }));
      });

      connection.listen();
    });

    this.servers.set(language, {
      process: serverProcess,
      port,
      wsServer
    });

    return port;
  }

  async killServer(language: string): Promise<void> {
    const server = this.servers.get(language);
    if (server) {
      server.process.kill();
      server.wsServer.close();
      this.servers.delete(language);
    }
  }

  async killAll(): Promise<void> {
    await Promise.all(
      Array.from(this.servers.keys()).map(lang => this.killServer(lang))
    );
  }
}
```

#### Supported Languages and Servers

Out of the box, Polly Code will support common languages with well-maintained LSP servers:

```typescript
// src/renderer/services/lsp/languageConfigs.ts
import { LSPServerConfig } from './LSPManager';

export const DEFAULT_LSP_CONFIGS: LSPServerConfig[] = [
  // TypeScript/JavaScript
  {
    language: 'typescript',
    command: 'typescript-language-server',
    args: ['--stdio']
  },
  {
    language: 'javascript',
    command: 'typescript-language-server',
    args: ['--stdio']
  },

  // Python
  {
    language: 'python',
    command: 'pylsp',
    args: []
  },

  // Rust
  {
    language: 'rust',
    command: 'rust-analyzer',
    args: []
  },

  // Go
  {
    language: 'go',
    command: 'gopls',
    args: []
  },

  // C/C++
  {
    language: 'c',
    command: 'clangd',
    args: []
  },
  {
    language: 'cpp',
    command: 'clangd',
    args: []
  },

  // SuperCollider (custom LSP - we'll build this!)
  {
    language: 'supercollider',
    command: 'sclang-lsp',
    args: ['--stdio'],
    initializationOptions: {
      // Custom options for SC
      sclangPath: '/usr/local/bin/sclang'
    }
  }
];
```

**SuperCollider LSP** - This is a differentiator for Polly Code. Most IDEs have poor SuperCollider support. We can build a custom LSP server that understands SC's unique syntax and provides:
- Code completion for UGens, Synths, Patterns
- Hover documentation from schelp files (indexed in epub vectors!)
- Jump to definition for SynthDefs
- Real-time error checking

This aligns with our polymathic vision—supporting niche languages that matter to creative coders.

#### Tree-sitter Integration for Syntax Highlighting

While LSP provides semantic analysis, tree-sitter provides fast, accurate syntax highlighting:

```typescript
// src/renderer/services/treesitter/TreeSitterManager.ts
import Parser from 'web-tree-sitter';
import * as monaco from 'monaco-editor';

export class TreeSitterManager {
  private parser: Parser | null = null;
  private languages: Map<string, Parser.Language> = new Map();

  async init() {
    await Parser.init();
    this.parser = new Parser();

    // Load language grammars
    await this.loadLanguage('typescript', 'tree-sitter-typescript.wasm');
    await this.loadLanguage('python', 'tree-sitter-python.wasm');
    await this.loadLanguage('rust', 'tree-sitter-rust.wasm');
    await this.loadLanguage('supercollider', 'tree-sitter-supercollider.wasm');
  }

  private async loadLanguage(name: string, wasmPath: string) {
    const language = await Parser.Language.load(wasmPath);
    this.languages.set(name, language);
  }

  // Parse code and return syntax tree
  parse(code: string, language: string): Parser.Tree | null {
    if (!this.parser) return null;

    const lang = this.languages.get(language);
    if (!lang) return null;

    this.parser.setLanguage(lang);
    return this.parser.parse(code);
  }

  // Convert tree-sitter tree to Monaco tokens
  toMonacoTokens(tree: Parser.Tree): monaco.editor.IToken[] {
    const tokens: monaco.editor.IToken[] = [];
    
    const visit = (node: Parser.SyntaxNode) => {
      tokens.push({
        startIndex: node.startIndex,
        scopes: `${node.type}.${node.grammarType}`
      });

      for (const child of node.children) {
        visit(child);
      }
    };

    visit(tree.rootNode);
    return tokens;
  }
}
```

**Why tree-sitter?**: 
- **Fast**: Incremental parsing (only re-parses changed regions)
- **Accurate**: True syntax understanding (not regex-based like TextMate)
- **Composable**: Can query syntax tree for custom features (code folding, structure view)

#### Connecting LSP to Monaco Editor

Now we wire LSP diagnostics, hover, and completion into Monaco:

```typescript
// src/renderer/components/editor/MonacoEditorWithLSP.tsx
import React, { useEffect, useRef } from 'react';
import * as monaco from 'monaco-editor';
import { LSPManager } from '../../services/lsp/LSPManager';
import { TreeSitterManager } from '../../services/treesitter/TreeSitterManager';

interface MonacoEditorWithLSPProps {
  file: OpenFile;
  onChange: (content: string) => void;
  onStateChange: (state: EditorState) => void;
}

export const MonacoEditorWithLSP: React.FC<MonacoEditorWithLSPProps> = ({
  file,
  onChange,
  onStateChange
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const lspManagerRef = useRef<LSPManager>(new LSPManager());
  const treeSitterRef = useRef<TreeSitterManager>(new TreeSitterManager());

  useEffect(() => {
    // Initialize tree-sitter
    treeSitterRef.current.init();
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    // Create editor
    const editor = monaco.editor.create(containerRef.current, {
      value: file.content,
      language: getLanguageFromPath(file.path),
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      fontSize: 14,
      fontFamily: 'SF Mono, Monaco, Consolas, Courier New, monospace',
      lineNumbers: 'on',
      rulers: [80, 120],
      renderWhitespace: 'selection',
      tabSize: 2,
      insertSpaces: true
    });

    editorRef.current = editor;

    // Start LSP for this language
    const language = getLanguageFromPath(file.path);
    lspManagerRef.current.startServer(language);

    // Handle content changes
    editor.onDidChangeModelContent(() => {
      const content = editor.getValue();
      onChange(content);

      // Re-parse with tree-sitter for updated highlighting
      const tree = treeSitterRef.current.parse(content, language);
      if (tree) {
        // Update Monaco tokens (custom highlighting)
        const tokens = treeSitterRef.current.toMonacoTokens(tree);
        // Apply tokens to editor
      }
    });

    // Track cursor and selection
    editor.onDidChangeCursorPosition((e) => {
      onStateChange({
        cursor: {
          line: e.position.lineNumber,
          column: e.position.column
        }
      });
    });

    editor.onDidChangeCursorSelection((e) => {
      const selection = editor.getModel()?.getValueInRange(e.selection);
      onStateChange({
        selection: selection ? {
          text: selection,
          length: selection.length,
          range: e.selection
        } : undefined
      });
    });

    // Cleanup
    return () => {
      editor.dispose();
      lspManagerRef.current.stopServer(language);
    };
  }, [file.path]);

  // Update content when file changes
  useEffect(() => {
    if (editorRef.current) {
      const currentValue = editorRef.current.getValue();
      if (currentValue !== file.content) {
        editorRef.current.setValue(file.content);
      }
    }
  }, [file.content]);

  return (
    <div 
      ref={containerRef} 
      className="monaco-editor-container"
      style={{ width: '100%', height: '100%' }}
    />
  );
};

function getLanguageFromPath(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase();
  const langMap: Record<string, string> = {
    'ts': 'typescript',
    'tsx': 'typescript',
    'js': 'javascript',
    'jsx': 'javascript',
    'py': 'python',
    'rs': 'rust',
    'go': 'go',
    'c': 'c',
    'cpp': 'cpp',
    'h': 'c',
    'hpp': 'cpp',
    'scd': 'supercollider',
    'sc': 'supercollider'
  };
  return langMap[ext || ''] || 'plaintext';
}
```

**What This Achieves**:
- Real-time diagnostics (errors/warnings as you type)
- IntelliSense completion (Cmd+Space to trigger)
- Hover documentation (hover over symbols)
- Go to definition (Cmd+Click)
- Find references (Cmd+Shift+F12)
- Rename symbol (F2)

All powered by industry-standard LSP servers, giving Polly Code feature parity with VSCode/Cursor for language intelligence.

---


### Section 15: RAG Pipeline Integration

This is where Polly Code becomes truly differentiated. The RAG (Retrieval-Augmented Generation) pipeline connects the editor to the entire knowledge graph—epub vectors from documentation, past code, design philosophy, and cross-domain expertise.

#### RAG Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      POLLY CODE EDITOR                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User types code  →  Query Generator  →  RAG Retrieval       │
│                           │                      │            │
│                           ↓                      ↓            │
│                    Context Analyzer      Vector Search       │
│                           │                      │            │
│                           └──────────┬───────────┘            │
│                                      ↓                         │
│                           Cross-Domain Ranker                 │
│                                      │                         │
│                                      ↓                         │
│                            LLM Context Injection              │
│                                      │                         │
│                                      ↓                         │
│                           Code Suggestions                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Innovation**: Unlike Cursor/Copilot (which only search code), Polly's RAG searches across **five domains**:
1. **Sigils** (Code): Functions, classes, past implementations
2. **Signals** (Audio): SuperCollider docs, synthesis patterns
3. **Scrolls** (Writing): Design philosophy, architectural decisions
4. **Sights** (Visual): p5.js sketches, visual patterns
5. **Glyphs** (Systems): Meta-organization, project structure

#### Query Generation from Editor Context

When you're coding, Polly automatically generates queries based on what you're working on:

```typescript
// src/renderer/services/rag/QueryGenerator.ts
import * as monaco from 'monaco-editor';
import Parser from 'web-tree-sitter';

interface EditorContext {
  currentFile: string;
  cursorPosition: monaco.Position;
  surroundingCode: string;
  syntaxTree: Parser.Tree | null;
  recentEdits: Edit[];
}

interface Edit {
  timestamp: Date;
  range: monaco.Range;
  text: string;
}

export class QueryGenerator {
  // Generate RAG queries from editor state
  generateQueries(context: EditorContext): RAGQuery[] {
    const queries: RAGQuery[] = [];

    // Query 1: Current function/class context
    const enclosingScope = this.getEnclosingScope(context);
    if (enclosingScope) {
      queries.push({
        text: `Similar implementations of ${enclosingScope.name}`,
        type: 'code_similarity',
        domains: ['sigils'], // Search code domain
        weight: 1.0
      });
    }

    // Query 2: Import statements (what libraries/patterns are in use)
    const imports = this.extractImports(context);
    if (imports.length > 0) {
      queries.push({
        text: `Documentation for ${imports.join(', ')}`,
        type: 'documentation',
        domains: ['sigils', 'scrolls'], // Code + docs
        weight: 0.8
      });
    }

    // Query 3: Comments/TODOs (user intent)
    const comments = this.extractRecentComments(context);
    if (comments.length > 0) {
      queries.push({
        text: comments.join(' '),
        type: 'intent',
        domains: ['sigils', 'scrolls', 'signals', 'sights'], // All domains
        weight: 1.2 // High weight - user explicitly stated intent
      });
    }

    // Query 4: Domain-specific patterns
    const domain = this.detectDomain(context);
    if (domain === 'audio') {
      // User is working on audio code - search audio domain
      queries.push({
        text: `SuperCollider synthesis patterns related to ${enclosingScope?.name}`,
        type: 'domain_specific',
        domains: ['signals'],
        weight: 0.9
      });
    }

    return queries;
  }

  private getEnclosingScope(context: EditorContext): { name: string; type: string } | null {
    if (!context.syntaxTree) return null;

    const node = context.syntaxTree.rootNode.descendantForPosition({
      row: context.cursorPosition.lineNumber - 1,
      column: context.cursorPosition.column - 1
    });

    // Walk up tree to find function/class
    let current = node;
    while (current) {
      if (current.type === 'function_declaration' || 
          current.type === 'class_declaration' ||
          current.type === 'method_definition') {
        const nameNode = current.childForFieldName('name');
        if (nameNode) {
          return {
            name: nameNode.text,
            type: current.type
          };
        }
      }
      current = current.parent!;
    }

    return null;
  }

  private extractImports(context: EditorContext): string[] {
    // Parse import statements from surrounding code
    const importRegex = /import\s+(?:{([^}]+)}|(\w+))\s+from\s+['"]([^'"]+)['"]/g;
    const imports: string[] = [];
    
    let match;
    while ((match = importRegex.exec(context.surroundingCode)) !== null) {
      imports.push(match[3]); // Package name
    }

    return imports;
  }

  private extractRecentComments(context: EditorContext): string[] {
    // Look at recent edits for comments
    const comments: string[] = [];
    
    for (const edit of context.recentEdits) {
      const commentMatch = edit.text.match(/\/\/\s*(.+)|\/\*\s*(.+)\s*\*\//);
      if (commentMatch) {
        comments.push(commentMatch[1] || commentMatch[2]);
      }
    }

    return comments;
  }

  private detectDomain(context: EditorContext): string | null {
    const filename = context.currentFile.toLowerCase();
    
    // Audio domain
    if (filename.includes('synth') || 
        filename.includes('audio') || 
        filename.endsWith('.scd') ||
        filename.endsWith('.sc')) {
      return 'audio';
    }

    // Visual domain
    if (filename.includes('sketch') ||
        filename.includes('visual') ||
        filename.includes('p5')) {
      return 'visual';
    }

    // Design domain
    if (filename.includes('design') ||
        filename.includes('component') ||
        filename.includes('style')) {
      return 'design';
    }

    return null;
  }
}

interface RAGQuery {
  text: string;
  type: 'code_similarity' | 'documentation' | 'intent' | 'domain_specific';
  domains: Array<'sigils' | 'signals' | 'scrolls' | 'sights' | 'glyphs'>;
  weight: number;
}
```

**Example in Action**:

User is editing `synth.scd` (SuperCollider file) and types:

```supercollider
// Create a granular reverb effect
SynthDef(\granularReverb, {
  |in, out, grainSize=0.1|
  // [cursor here]
```

Polly generates queries:
1. "Similar implementations of granularReverb" (code domain)
2. "Documentation for SynthDef, granular synthesis" (code + docs)
3. "Create a granular reverb effect" (all domains - from comment)
4. "SuperCollider synthesis patterns related to granularReverb" (audio domain)

#### Vector Search Across Domains

Now we search the vector database for relevant context:

```typescript
// src/main/services/RAGService.ts
import { ChromaClient, Collection } from 'chromadb';
import { OpenAI } from 'openai';

interface VectorResult {
  id: string;
  content: string;
  metadata: {
    domain: string;
    filePath: string;
    timestamp: Date;
    type: string;
  };
  distance: number;
}

export class RAGService {
  private chroma: ChromaClient;
  private openai: OpenAI;
  private collections: Map<string, Collection> = new Map();

  constructor() {
    this.chroma = new ChromaClient({
      path: 'http://localhost:8000' // Local ChromaDB instance
    });
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  async init() {
    // Create collections for each domain
    const domains = ['sigils', 'signals', 'scrolls', 'sights', 'glyphs'];
    
    for (const domain of domains) {
      const collection = await this.chroma.getOrCreateCollection({
        name: `polly_${domain}`,
        metadata: { domain }
      });
      this.collections.set(domain, collection);
    }
  }

  // Retrieve relevant vectors for queries
  async retrieve(queries: RAGQuery[], limit: number = 10): Promise<VectorResult[]> {
    const allResults: VectorResult[] = [];

    // Search each query across specified domains
    for (const query of queries) {
      for (const domain of query.domains) {
        const collection = this.collections.get(domain);
        if (!collection) continue;

        // Generate embedding for query
        const embedding = await this.generateEmbedding(query.text);

        // Search collection
        const results = await collection.query({
          queryEmbeddings: [embedding],
          nResults: limit,
          where: this.buildWhereClause(query)
        });

        // Transform results
        if (results.ids && results.documents && results.distances) {
          for (let i = 0; i < results.ids[0].length; i++) {
            allResults.push({
              id: results.ids[0][i],
              content: results.documents[0][i] as string,
              metadata: {
                domain,
                filePath: results.metadatas?.[0][i]?.filePath as string || '',
                timestamp: new Date(results.metadatas?.[0][i]?.timestamp as string || ''),
                type: results.metadatas?.[0][i]?.type as string || ''
              },
              distance: results.distances[0][i] * query.weight // Apply query weight
            });
          }
        }
      }
    }

    // Rank and deduplicate results
    return this.rankResults(allResults, limit);
  }

  private async generateEmbedding(text: string): Promise<number[]> {
    const response = await this.openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: text
    });
    return response.data[0].embedding;
  }

  private buildWhereClause(query: RAGQuery): any {
    // Filter by query type
    const where: any = {};

    if (query.type === 'documentation') {
      where.type = { $in: ['doc', 'comment', 'readme'] };
    } else if (query.type === 'code_similarity') {
      where.type = { $in: ['function', 'class', 'module'] };
    }

    return where;
  }

  private rankResults(results: VectorResult[], limit: number): VectorResult[] {
    // Sort by weighted distance (lower is better)
    const sorted = results.sort((a, b) => a.distance - b.distance);

    // Deduplicate based on content similarity
    const deduped: VectorResult[] = [];
    for (const result of sorted) {
      const isDuplicate = deduped.some(d => 
        this.cosineSimilarity(result.content, d.content) > 0.95
      );
      if (!isDuplicate) {
        deduped.push(result);
      }
      if (deduped.length >= limit) break;
    }

    return deduped;
  }

  private cosineSimilarity(a: string, b: string): number {
    // Simple character-based similarity (in practice, use embeddings)
    const aChars = new Set(a);
    const bChars = new Set(b);
    const intersection = new Set([...aChars].filter(c => bChars.has(c)));
    return intersection.size / Math.max(aChars.size, bChars.size);
  }

  // Index new content (called when files change)
  async indexContent(content: string, metadata: any): Promise<void> {
    const collection = this.collections.get(metadata.domain);
    if (!collection) return;

    const embedding = await this.generateEmbedding(content);

    await collection.add({
      ids: [metadata.id],
      embeddings: [embedding],
      documents: [content],
      metadatas: [metadata]
    });
  }
}
```

#### Cross-Domain Ranking

The magic happens in cross-domain ranking. When multiple domains return results, we need to intelligently combine them:

```typescript
// src/renderer/services/rag/CrossDomainRanker.ts
interface RankedResult extends VectorResult {
  finalScore: number;
  reasons: string[];
}

export class CrossDomainRanker {
  // Rank results from multiple domains based on context
  rank(results: VectorResult[], context: EditorContext): RankedResult[] {
    return results.map(result => {
      const reasons: string[] = [];
      let finalScore = 0;

      // Base score from distance
      const distanceScore = 1 - (result.distance / 2); // Normalize to 0-1
      finalScore += distanceScore * 0.4;
      reasons.push(`Similarity: ${(distanceScore * 100).toFixed(0)}%`);

      // Recency bonus
      const ageInDays = (Date.now() - result.metadata.timestamp.getTime()) / (1000 * 60 * 60 * 24);
      const recencyScore = Math.exp(-ageInDays / 30); // Decay over 30 days
      finalScore += recencyScore * 0.2;
      if (recencyScore > 0.5) {
        reasons.push('Recent');
      }

      // Domain relevance
      const domainScore = this.calculateDomainRelevance(result.metadata.domain, context);
      finalScore += domainScore * 0.3;
      if (domainScore > 0.7) {
        reasons.push(`${result.metadata.domain} domain match`);
      }

      // Project locality (same project = higher score)
      if (this.isFromSameProject(result.metadata.filePath, context.currentFile)) {
        finalScore += 0.1;
        reasons.push('Same project');
      }

      return {
        ...result,
        finalScore,
        reasons
      };
    }).sort((a, b) => b.finalScore - a.finalScore);
  }

  private calculateDomainRelevance(domain: string, context: EditorContext): number {
    const filename = context.currentFile.toLowerCase();

    // Audio files → signals domain is highly relevant
    if (domain === 'signals' && (filename.includes('synth') || filename.endsWith('.scd'))) {
      return 1.0;
    }

    // Visual files → sights domain is highly relevant
    if (domain === 'sights' && (filename.includes('sketch') || filename.includes('p5'))) {
      return 1.0;
    }

    // Code files → sigils domain always relevant
    if (domain === 'sigils') {
      return 0.8; // Always somewhat relevant
    }

    // Documentation → scrolls domain moderately relevant
    if (domain === 'scrolls') {
      return 0.6;
    }

    // Systems thinking → glyphs domain for architecture decisions
    if (domain === 'glyphs' && this.isArchitecturalContext(context)) {
      return 0.9;
    }

    return 0.3; // Default relevance
  }

  private isFromSameProject(filePath: string, currentFile: string): boolean {
    // Simple heuristic: same top-level directory
    const getProjectRoot = (path: string) => path.split('/').slice(0, 3).join('/');
    return getProjectRoot(filePath) === getProjectRoot(currentFile);
  }

  private isArchitecturalContext(context: EditorContext): boolean {
    // Check if user is working on high-level structure
    const architecturalKeywords = ['class', 'module', 'interface', 'architecture', 'design'];
    return architecturalKeywords.some(kw => 
      context.surroundingCode.toLowerCase().includes(kw)
    );
  }
}
```

#### Injecting RAG Context into LLM

Finally, we inject the ranked results into the LLM prompt:

```typescript
// src/renderer/services/rag/ContextInjector.ts
interface LLMPrompt {
  system: string;
  user: string;
  context: RAGContext[];
}

interface RAGContext {
  source: string;
  content: string;
  relevance: string;
}

export class ContextInjector {
  // Build LLM prompt with RAG context
  buildPrompt(
    userQuery: string,
    rankedResults: RankedResult[],
    editorContext: EditorContext
  ): LLMPrompt {
    const ragContext: RAGContext[] = rankedResults.slice(0, 5).map(result => ({
      source: `${result.metadata.domain}:${result.metadata.filePath}`,
      content: result.content,
      relevance: result.reasons.join(', ')
    }));

    return {
      system: this.buildSystemPrompt(rankedResults),
      user: this.buildUserPrompt(userQuery, editorContext),
      context: ragContext
    };
  }

  private buildSystemPrompt(results: RankedResult[]): string {
    const domains = new Set(results.map(r => r.metadata.domain));
    
    let prompt = `You are Polly Code, an AI programming assistant with access to the user's complete knowledge graph across ${domains.size} domains:\n\n`;

    if (domains.has('sigils')) {
      prompt += `- Code domain (Sigils): Past implementations, functions, and patterns\n`;
    }
    if (domains.has('signals')) {
      prompt += `- Audio domain (Signals): SuperCollider docs, synthesis techniques\n`;
    }
    if (domains.has('scrolls')) {
      prompt += `- Writing domain (Scrolls): Design philosophy, architectural decisions\n`;
    }
    if (domains.has('sights')) {
      prompt += `- Visual domain (Sights): p5.js sketches, visual patterns\n`;
    }
    if (domains.has('glyphs')) {
      prompt += `- Systems domain (Glyphs): Meta-organization, project structure\n`;
    }

    prompt += `\nYour responses should:\n`;
    prompt += `1. Draw from ALL relevant domains, not just code\n`;
    prompt += `2. Reference the user's past work and design philosophy\n`;
    prompt += `3. Maintain consistency with their coding style\n`;
    prompt += `4. Suggest patterns they've used successfully before\n\n`;

    prompt += `Context from knowledge graph:\n\n`;

    for (const result of results.slice(0, 5)) {
      prompt += `--- ${result.metadata.domain} (${result.reasons.join(', ')}) ---\n`;
      prompt += `${result.content}\n\n`;
    }

    return prompt;
  }

  private buildUserPrompt(query: string, context: EditorContext): string {
    let prompt = `Current context:\n`;
    prompt += `File: ${context.currentFile}\n`;
    prompt += `\n\`\`\`\n${context.surroundingCode}\n\`\`\`\n\n`;
    prompt += `User query: ${query}\n`;
    return prompt;
  }
}
```

#### Real-World Example: SuperCollider Development

**Scenario**: User is creating a new granular synth in SuperCollider.

**User types in `synth.scd`**:
```supercollider
// Create a granular reverb with pitch shifting
SynthDef(\granularReverb, {
  |in, out, grainSize=0.1|
  // [cursor here]
```

**Polly's RAG Pipeline**:

1. **Query Generation**:
   - "Similar implementations of granularReverb" (code)
   - "Documentation for SynthDef, granular synthesis" (code + docs)
   - "Create a granular reverb with pitch shifting" (all domains)
   - "SuperCollider synthesis patterns related to granular" (audio)

2. **Vector Search**:
   - **Signals domain**: Finds past SuperCollider docs on `GrainBuf`, `PitchShift`
   - **Sigils domain**: Finds previous granular synth implementations
   - **Scrolls domain**: Finds essay on "Constraint-Based Synthesis Design"

3. **Cross-Domain Ranking**:
   - Signals domain results ranked highest (audio context detected)
   - Scrolls result about constraints also ranks high (architectural guidance)
   - Past code ranked medium (provides concrete examples)

4. **LLM Suggestion**:
   ```supercollider
   // Polly suggests (with context from all three domains):
   var sig, grains;
   sig = In.ar(in, 2);
   
   // Granular buffer (from past implementation)
   grains = GrainBuf.ar(
     numChannels: 2,
     trigger: Impulse.ar(grainSize.reciprocal),
     dur: grainSize,
     sndbuf: LocalBuf.new(44100),
     // Pitch shifting with constraint (from design philosophy)
     rate: LFNoise1.kr(0.5).range(0.5, 2.0), // Bounded variation
     pos: LFNoise1.kr(0.1).range(0, 1)
   );
   
   // Subtle reverb (from SC docs)
   sig = FreeVerb2.ar(grains[0], grains[1], mix: 0.33, room: 0.5);
   
   Out.ar(out, sig);
   ```

**Why This Is Powerful**:
- Code structure from past implementations (Sigils)
- Specific UGens from SuperCollider docs (Signals)
- Design constraint (bounded variation) from user's philosophy essay (Scrolls)

**Cursor/Copilot cannot do this**—they only see code, not documentation or philosophy.

---


### Section 16: Persona System Integration

Polly Code integrates with Phase 24 (Orchestrator Mode) and Phase 27 (Designer Persona) to enable multi-persona coordination during development. This is a key differentiator—instead of a single AI assistant, you have a team of specialized personas working together.

#### Persona Architecture in Code Editor

```typescript
// src/renderer/services/personas/PersonaCoordinator.ts
import { PersonaType, PersonaMode } from '@shared/types/personas';
import { RAGService } from '../rag/RAGService';

interface PersonaState {
  type: PersonaType;
  mode: PersonaMode;
  active: boolean;
  context: any;
}

export class PersonaCoordinator {
  private activePersonas: Map<PersonaType, PersonaState> = new Map();
  private ragService: RAGService;

  constructor(ragService: RAGService) {
    this.ragService = ragService;
  }

  // Activate a persona with specific mode
  async activatePersona(type: PersonaType, mode: PersonaMode): Promise<void> {
    // Load persona-specific context from RAG
    const personaContext = await this.ragService.retrieve([{
      text: `${type} persona past interactions and preferences`,
      type: 'intent',
      domains: ['glyphs', 'scrolls'], // Personas live in systems thinking
      weight: 1.0
    }]);

    this.activePersonas.set(type, {
      type,
      mode,
      active: true,
      context: personaContext
    });
  }

  // Route query to appropriate persona(s)
  async routeQuery(
    query: string,
    editorContext: EditorContext
  ): Promise<PersonaResponse[]> {
    const responses: PersonaResponse[] = [];

    // Determine which personas should respond
    const relevantPersonas = this.determineRelevantPersonas(query, editorContext);

    for (const personaType of relevantPersonas) {
      const persona = this.activePersonas.get(personaType);
      if (!persona) continue;

      const response = await this.queryPersona(personaType, query, editorContext);
      responses.push(response);
    }

    // If multiple personas respond, coordinate their answers
    if (responses.length > 1) {
      return this.coordinateResponses(responses);
    }

    return responses;
  }

  private determineRelevantPersonas(
    query: string,
    context: EditorContext
  ): PersonaType[] {
    const personas: PersonaType[] = [];

    // Architect: For high-level structure questions
    if (this.isArchitecturalQuery(query)) {
      personas.push('architect');
    }

    // Designer: For UI/UX questions
    if (this.isDesignQuery(query)) {
      personas.push('designer');
    }

    // Programmer: For implementation questions (always relevant)
    personas.push('programmer');

    return personas;
  }

  private isArchitecturalQuery(query: string): boolean {
    const architecturalKeywords = [
      'architecture', 'structure', 'organize', 'design pattern',
      'system', 'module', 'component hierarchy', 'should I'
    ];
    return architecturalKeywords.some(kw => 
      query.toLowerCase().includes(kw)
    );
  }

  private isDesignQuery(query: string): boolean {
    const designKeywords = [
      'layout', 'style', 'color', 'spacing', 'component',
      'visual', 'ui', 'ux', 'design token', 'responsive'
    ];
    return designKeywords.some(kw => 
      query.toLowerCase().includes(kw)
    );
  }

  private async queryPersona(
    type: PersonaType,
    query: string,
    context: EditorContext
  ): Promise<PersonaResponse> {
    // Send query to backend with persona context
    const response = await window.electron.invoke('persona:query', {
      persona: type,
      query,
      editorContext: context,
      personaContext: this.activePersonas.get(type)?.context
    });

    return {
      persona: type,
      content: response.content,
      confidence: response.confidence,
      suggestions: response.suggestions
    };
  }

  private coordinateResponses(responses: PersonaResponse[]): PersonaResponse[] {
    // Architect has highest authority for structural decisions
    const architect = responses.find(r => r.persona === 'architect');
    
    // Designer has authority for visual/UX decisions
    const designer = responses.find(r => r.persona === 'designer');
    
    // Programmer provides implementation details
    const programmer = responses.find(r => r.persona === 'programmer');

    // Merge responses in order of authority
    const coordinated: PersonaResponse[] = [];

    if (architect) {
      coordinated.push({
        ...architect,
        content: `**[Architect]** ${architect.content}\n`
      });
    }

    if (designer) {
      coordinated.push({
        ...designer,
        content: `**[Designer]** ${designer.content}\n`
      });
    }

    if (programmer) {
      coordinated.push({
        ...programmer,
        content: `**[Programmer]** ${programmer.content}\n`
      });
    }

    return coordinated;
  }
}

interface PersonaResponse {
  persona: PersonaType;
  content: string;
  confidence: number;
  suggestions: CodeSuggestion[];
}

interface CodeSuggestion {
  code: string;
  description: string;
  location?: monaco.Range;
}
```

#### Designer → Programmer Flow

The most powerful integration is Designer → Programmer, where design specs automatically inform code:

```typescript
// src/renderer/services/personas/DesignerProgrammerBridge.ts
interface DesignSpec {
  component: string;
  constraints: Constraint[];
  tokens: DesignToken[];
  layoutMode: 'flex' | 'grid' | 'absolute';
  responsiveBreakpoints: Breakpoint[];
}

interface Constraint {
  type: 'spacing' | 'color' | 'typography' | 'layout';
  rule: string;
  rationale: string;
}

export class DesignerProgrammerBridge {
  // Convert design spec to code
  async generateCodeFromSpec(spec: DesignSpec): Promise<string> {
    let code = '';

    // Generate component structure
    code += `// Component: ${spec.component}\n`;
    code += `// Design rationale:\n`;
    for (const constraint of spec.constraints) {
      code += `// - ${constraint.type}: ${constraint.rationale}\n`;
    }
    code += `\n`;

    // Generate React component (or other framework)
    code += `import React from 'react';\n`;
    code += `import { styled } from 'styled-components';\n\n`;

    // Design tokens as constants
    code += `const tokens = {\n`;
    for (const token of spec.tokens) {
      code += `  ${token.name}: '${token.value}',\n`;
    }
    code += `};\n\n`;

    // Styled component with constraints
    code += `const ${spec.component}Wrapper = styled.div\`\n`;
    
    // Apply layout mode
    if (spec.layoutMode === 'flex') {
      code += `  display: flex;\n`;
      // Apply spacing constraints
      const spacingConstraint = spec.constraints.find(c => c.type === 'spacing');
      if (spacingConstraint) {
        code += `  gap: ${this.extractSpacingValue(spacingConstraint)};\n`;
      }
    } else if (spec.layoutMode === 'grid') {
      code += `  display: grid;\n`;
      code += `  grid-template-columns: ${this.inferGridColumns(spec)};\n`;
    }

    // Apply color constraints
    const colorConstraint = spec.constraints.find(c => c.type === 'color');
    if (colorConstraint) {
      code += `  background-color: \${tokens.${this.extractTokenName(colorConstraint)}};\n`;
    }

    // Apply typography constraints
    const typographyConstraint = spec.constraints.find(c => c.type === 'typography');
    if (typographyConstraint) {
      code += `  font-family: \${tokens.fontFamily};\n`;
      code += `  font-size: \${tokens.fontSize};\n`;
    }

    // Responsive breakpoints
    for (const breakpoint of spec.responsiveBreakpoints) {
      code += `\n  @media (max-width: ${breakpoint.width}px) {\n`;
      code += `    /* ${breakpoint.adjustments} */\n`;
      code += `  }\n`;
    }

    code += `\`;\n\n`;

    // Component implementation
    code += `export const ${spec.component}: React.FC = () => {\n`;
    code += `  return (\n`;
    code += `    <${spec.component}Wrapper>\n`;
    code += `      {/* Component content */}\n`;
    code += `    </${spec.component}Wrapper>\n`;
    code += `  );\n`;
    code += `};\n`;

    return code;
  }

  private extractSpacingValue(constraint: Constraint): string {
    // Parse spacing value from constraint rule
    const match = constraint.rule.match(/(\d+(?:\.\d+)?(?:px|rem|em))/);
    return match ? match[1] : '1rem';
  }

  private extractTokenName(constraint: Constraint): string {
    // Extract token reference from constraint
    const match = constraint.rule.match(/\$\{tokens\.(\w+)\}/);
    return match ? match[1] : 'primaryColor';
  }

  private inferGridColumns(spec: DesignSpec): string {
    // Infer grid layout from constraints
    return 'repeat(auto-fit, minmax(200px, 1fr))';
  }
}

interface DesignToken {
  name: string;
  value: string;
  category: 'color' | 'spacing' | 'typography' | 'shadow' | 'border';
}

interface Breakpoint {
  width: number;
  adjustments: string;
}
```

#### Example: Architect → Designer → Programmer Flow

**User Query**: "I need a dashboard for norns performance metrics"

**Polly's Multi-Persona Response**:

1. **Architect Persona** responds first:
   ```
   [Architect] For a norns metrics dashboard, I recommend:
   
   Structure:
   - MetricsDashboard (container)
     - MetricsHeader (title, refresh controls)
     - MetricsGrid (auto-layout metrics cards)
       - CPUUsageCard
       - MemoryUsageCard  
       - AudioEngineCard
       - SystemStatusCard
   
   Rationale: Modular cards allow independent updates without 
   re-rendering entire dashboard. Grid layout adapts to screen size.
   
   Dependencies: Need to integrate with norns system API 
   (from your past norns-monitor library in Sigils domain).
   ```

2. **Designer Persona** responds second:
   ```
   [Designer] Visual design for metrics dashboard:
   
   Constraints:
   - Spacing: 16px grid system (from your design tokens)
   - Color: Monochrome with accent for alerts 
     (consistent with norns aesthetic)
   - Typography: Monospace for numeric values (SF Mono)
   - Layout: CSS Grid, 2 columns on tablet, 4 on desktop
   
   Design tokens to create:
   - metrics.background: #1a1a1a
   - metrics.cardBorder: #333
   - metrics.accentAlert: #ff6b6b
   - metrics.textPrimary: #e0e0e0
   ```

3. **Programmer Persona** responds third:
   ```
   [Programmer] Here's the implementation integrating 
   Architect's structure and Designer's constraints:
   
   [Generates full React code with styled-components, 
   hooks for norns API polling, grid layout matching 
   design spec]
   ```

**Key Innovation**: The three personas **coordinate automatically**. Architect provides structure, Designer adds constraints, Programmer implements. This mirrors how human teams work.

**No competitor does this**. Cursor/Copilot give you a single response. Polly gives you a coordinated team.

---

### Section 17: Profile-Aware Coding

Polly Code integrates with Phase 13b (User Profile System) to learn your coding style and adapt suggestions accordingly.

#### Profile Learning Architecture

```typescript
// src/main/services/ProfileLearningService.ts
interface CodingProfile {
  userId: string;
  preferences: CodingPreferences;
  patterns: CodingPattern[];
  style: CodingStyle;
  history: InteractionHistory;
}

interface CodingPreferences {
  language: {
    preferred: string[];
    avoided: string[];
  };
  frameworks: {
    preferred: string[];
    avoided: string[];
  };
  patterns: {
    preferred: string[]; // e.g., "functional", "class-based"
    avoided: string[];
  };
  formatting: {
    indentation: 'tabs' | 'spaces';
    indentSize: number;
    lineLength: number;
    quotes: 'single' | 'double';
    semicolons: boolean;
    trailingCommas: boolean;
  };
}

interface CodingPattern {
  name: string;
  description: string;
  examples: string[];
  frequency: number; // How often user applies this pattern
  lastUsed: Date;
}

interface CodingStyle {
  naming: {
    variables: 'camelCase' | 'snake_case' | 'PascalCase';
    functions: 'camelCase' | 'snake_case';
    classes: 'PascalCase' | 'snake_case';
    constants: 'UPPER_CASE' | 'camelCase';
  };
  comments: {
    frequency: number; // Comments per 100 LOC
    style: 'block' | 'inline' | 'jsdoc';
    prefer: 'explanatory' | 'technical' | 'minimal';
  };
  errorHandling: {
    style: 'try-catch' | 'return-error' | 'throw';
    verbosity: 'detailed' | 'minimal';
  };
  architecture: {
    preferredPatterns: string[]; // e.g., "MVC", "functional composition"
    fileOrganization: 'feature-based' | 'layer-based' | 'domain-based';
  };
}

interface InteractionHistory {
  acceptedSuggestions: number;
  rejectedSuggestions: number;
  editedSuggestions: number;
  avgEditDistance: number; // How much user modifies suggestions
}

export class ProfileLearningService {
  private profile: CodingProfile | null = null;

  async loadProfile(userId: string): Promise<void> {
    this.profile = await this.fetchProfile(userId);
  }

  // Learn from user's code
  async learnFromCode(filePath: string, content: string): Promise<void> {
    if (!this.profile) return;

    // Analyze code for patterns
    const patterns = this.extractPatterns(content);
    const style = this.analyzeStyle(content);

    // Update profile
    for (const pattern of patterns) {
      this.updatePattern(pattern);
    }

    this.updateStyle(style);

    // Save profile
    await this.saveProfile();
  }

  // Learn from user's edits to suggestions
  async learnFromEdit(
    suggestion: string,
    userEdit: string,
    accepted: boolean
  ): Promise<void> {
    if (!this.profile) return;

    // Track acceptance
    if (accepted) {
      this.profile.history.acceptedSuggestions++;
    } else {
      this.profile.history.rejectedSuggestions++;
    }

    // Measure edit distance
    if (userEdit !== suggestion) {
      this.profile.history.editedSuggestions++;
      const distance = this.levenshteinDistance(suggestion, userEdit);
      this.profile.history.avgEditDistance = 
        (this.profile.history.avgEditDistance * 
         (this.profile.history.editedSuggestions - 1) + distance) /
        this.profile.history.editedSuggestions;

      // Learn what user changed
      this.analyzeEdit(suggestion, userEdit);
    }

    await this.saveProfile();
  }

  // Apply profile to suggestion
  applyStylingToSuggestion(code: string): string {
    if (!this.profile) return code;

    let styled = code;

    // Apply indentation preference
    if (this.profile.preferences.formatting.indentation === 'tabs') {
      styled = styled.replace(/  /g, '\t');
    }

    // Apply quote preference
    if (this.profile.preferences.formatting.quotes === 'single') {
      styled = styled.replace(/"/g, "'");
    }

    // Apply semicolon preference
    if (!this.profile.preferences.formatting.semicolons) {
      styled = styled.replace(/;$/gm, '');
    }

    // Apply naming conventions
    styled = this.applyNamingConventions(styled);

    return styled;
  }

  // Get relevant patterns for current context
  getRelevantPatterns(context: EditorContext): CodingPattern[] {
    if (!this.profile) return [];

    // Sort by frequency and recency
    return this.profile.patterns
      .filter(p => this.isRelevantToContext(p, context))
      .sort((a, b) => {
        const aScore = a.frequency * (1 + this.recencyBonus(a.lastUsed));
        const bScore = b.frequency * (1 + this.recencyBonus(b.lastUsed));
        return bScore - aScore;
      });
  }

  private extractPatterns(code: string): CodingPattern[] {
    const patterns: CodingPattern[] = [];

    // Detect functional patterns
    if (code.includes('.map(') || code.includes('.filter(') || code.includes('.reduce(')) {
      patterns.push({
        name: 'functional-array-methods',
        description: 'Uses functional array methods',
        examples: [code],
        frequency: 1,
        lastUsed: new Date()
      });
    }

    // Detect async/await vs promises
    if (code.includes('async ') && code.includes('await ')) {
      patterns.push({
        name: 'async-await',
        description: 'Prefers async/await over promises',
        examples: [code],
        frequency: 1,
        lastUsed: new Date()
      });
    }

    // Detect destructuring
    if (code.includes('const {') || code.includes('const [')) {
      patterns.push({
        name: 'destructuring',
        description: 'Uses destructuring',
        examples: [code],
        frequency: 1,
        lastUsed: new Date()
      });
    }

    return patterns;
  }

  private analyzeStyle(code: string): Partial<CodingStyle> {
    return {
      naming: this.detectNamingConvention(code),
      comments: this.analyzeComments(code)
    };
  }

  private detectNamingConvention(code: string): any {
    // Simple heuristics
    const camelCaseVars = (code.match(/const [a-z][a-zA-Z0-9]+/g) || []).length;
    const snakeCaseVars = (code.match(/const [a-z][a-z0-9_]+/g) || []).length;

    return {
      variables: camelCaseVars > snakeCaseVars ? 'camelCase' : 'snake_case'
    };
  }

  private analyzeComments(code: string): any {
    const lines = code.split('\n').length;
    const commentLines = (code.match(/\/\/.+/g) || []).length;
    const blockComments = (code.match(/\/\*[\s\S]*?\*\//g) || []).length;

    return {
      frequency: (commentLines + blockComments) / lines * 100,
      style: blockComments > commentLines ? 'block' : 'inline'
    };
  }

  private updatePattern(pattern: CodingPattern): void {
    if (!this.profile) return;

    const existing = this.profile.patterns.find(p => p.name === pattern.name);
    if (existing) {
      existing.frequency++;
      existing.lastUsed = new Date();
      existing.examples.push(...pattern.examples);
    } else {
      this.profile.patterns.push(pattern);
    }
  }

  private updateStyle(style: Partial<CodingStyle>): void {
    if (!this.profile) return;
    this.profile.style = { ...this.profile.style, ...style };
  }

  private analyzeEdit(suggestion: string, userEdit: string): void {
    // Detect what user changed and update preferences
    // Example: If user consistently removes semicolons, learn that
    if (suggestion.includes(';') && !userEdit.includes(';')) {
      this.profile!.preferences.formatting.semicolons = false;
    }

    // If user changes quotes
    if (suggestion.includes('"') && userEdit.includes("'")) {
      this.profile!.preferences.formatting.quotes = 'single';
    }
  }

  private levenshteinDistance(a: string, b: string): number {
    const matrix: number[][] = [];

    for (let i = 0; i <= b.length; i++) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }

    for (let i = 1; i <= b.length; i++) {
      for (let j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }

    return matrix[b.length][a.length];
  }

  private applyNamingConventions(code: string): string {
    // Apply user's preferred naming conventions
    // This is complex - would need proper AST parsing
    return code;
  }

  private isRelevantToContext(pattern: CodingPattern, context: EditorContext): boolean {
    // Check if pattern applies to current context
    const currentCode = context.surroundingCode.toLowerCase();
    return pattern.name.split('-').some(word => currentCode.includes(word));
  }

  private recencyBonus(lastUsed: Date): number {
    const ageInDays = (Date.now() - lastUsed.getTime()) / (1000 * 60 * 60 * 24);
    return Math.exp(-ageInDays / 30); // Decay over 30 days
  }

  private async fetchProfile(userId: string): Promise<CodingProfile> {
    // Fetch from backend
    return {} as CodingProfile;
  }

  private async saveProfile(): Promise<void> {
    // Save to backend
  }
}
```

#### Real-World Example: Profile Learning in Action

**Week 1**: User starts using Polly Code. Profile is empty.

**Week 2**: Polly observes:
- User consistently uses single quotes
- User prefers functional array methods over for loops
- User writes detailed comments for complex logic
- User organizes files by feature (not layer)
- User uses async/await (never `.then()`)

**Week 3**: Polly's suggestions now automatically:
- Use single quotes
- Suggest `.map()/.filter()` over loops
- Include explanatory comments for complex code
- Place new files in feature-based structure
- Generate async/await syntax

**Week 4**: User edits suggestions less (50% edit distance reduction).

**Why This Matters**: Over time, Polly Code becomes **your personal coding assistant**, not a generic one. It learns your style and respects your preferences.

**Cursor/Copilot don't do this**—they give everyone the same generic suggestions.

---


### Section 18: Complete System Architecture

This section provides a comprehensive view of how all components fit together—from Monaco editor to RAG pipeline to personas to profile learning.

#### Full System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            POLLY CODE EDITOR                                 │
│                         (Electron Application)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        RENDERER PROCESS                               │  │
│  │                         (React + Monaco)                              │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                        │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  File Tree  │  │   Monaco     │  │  Chat Panel  │               │  │
│  │  │  Component  │  │   Editor     │  │  (Personas)  │               │  │
│  │  └──────┬──────┘  └───────┬──────┘  └──────┬───────┘               │  │
│  │         │                 │                 │                        │  │
│  │  ┌──────▼──────────────────▼─────────────────▼──────┐               │  │
│  │  │           IDE Shell Coordinator                   │               │  │
│  │  │  - Manages layout                                 │               │  │
│  │  │  - Routes events between components               │               │  │
│  │  │  - Coordinates file operations                    │               │  │
│  │  └───────────────────────┬────────────────────────────┘               │  │
│  │                          │                                            │  │
│  │  ┌───────────────────────▼──────────────────────────┐               │  │
│  │  │         Language Intelligence Layer               │               │  │
│  │  │  ┌──────────────┐    ┌──────────────┐           │               │  │
│  │  │  │ LSP Manager  │    │  TreeSitter  │           │               │  │
│  │  │  │ - Manages    │    │  - Syntax    │           │               │  │
│  │  │  │   language   │    │    parsing   │           │               │  │
│  │  │  │   servers    │    │  - Tokens    │           │               │  │
│  │  │  └──────┬───────┘    └──────┬───────┘           │               │  │
│  │  │         │                    │                    │               │  │
│  │  │         └──────────┬─────────┘                    │               │  │
│  │  │                    ↓                              │               │  │
│  │  │          Monaco Editor API                        │               │  │
│  │  └───────────────────────────────────────────────────┘               │  │
│  │                          │                                            │  │
│  │  ┌───────────────────────▼──────────────────────────┐               │  │
│  │  │          RAG Integration Layer                    │               │  │
│  │  │  ┌──────────────────┐  ┌──────────────────────┐ │               │  │
│  │  │  │ Query Generator  │  │  Context Injector    │ │               │  │
│  │  │  │ - Editor context │  │  - Build LLM prompts │ │               │  │
│  │  │  │ - Intent         │  │  - Inject results    │ │               │  │
│  │  │  └────────┬─────────┘  └───────────▲──────────┘ │               │  │
│  │  │           │                         │             │               │  │
│  │  │           └────────────┬────────────┘             │               │  │
│  │  │                        │                          │               │  │
│  │  └────────────────────────┼──────────────────────────┘               │  │
│  │                           │                                           │  │
│  │  ┌────────────────────────▼──────────────────────────┐               │  │
│  │  │        Persona Coordination Layer                  │               │  │
│  │  │  ┌──────────────────────────────────────────────┐ │               │  │
│  │  │  │  Architect │ Designer │ Programmer │ ...     │ │               │  │
│  │  │  │  - Query routing                              │ │               │  │
│  │  │  │  - Response coordination                      │ │               │  │
│  │  │  │  - Context awareness                          │ │               │  │
│  │  │  └────────────────────┬──────────────────────────┘ │               │  │
│  │  └───────────────────────┼────────────────────────────┘               │  │
│  │                          │                                            │  │
│  │  ┌───────────────────────▼──────────────────────────┐               │  │
│  │  │      Profile Learning Layer                       │               │  │
│  │  │  - Code style analysis                            │               │  │
│  │  │  - Pattern detection                              │               │  │
│  │  │  - Preference learning                            │               │  │
│  │  │  - Suggestion adaptation                          │               │  │
│  │  └──────────────────────────────────────────────────┘               │  │
│  │                                                                        │  │
│  └────────────────────────┬───────────────────────────────────────────┘  │
│                           │ IPC (Electron)                                │
│  ┌────────────────────────▼───────────────────────────────────────────┐  │
│  │                       MAIN PROCESS                                  │  │
│  │                   (Node.js Backend)                                 │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │  │
│  │  │  LSP Service │  │  RAG Service │  │Profile Service│            │  │
│  │  │  - Spawn LSP │  │  - ChromaDB  │  │  - Learn from │            │  │
│  │  │    servers   │  │  - Embeddings│  │    code       │            │  │
│  │  │  - Proxy msg │  │  - Vector    │  │  - Track      │            │  │
│  │  │              │  │    search    │  │    patterns   │            │  │
│  │  └──────────────┘  └──────┬───────┘  └──────┬────────┘             │  │
│  │                           │                  │                       │  │
│  │  ┌──────────────┐  ┌──────▼──────────────────▼────┐                │  │
│  │  │ File System  │  │    Backend API                │                │  │
│  │  │  - Read/Write│  │    - Coordinates services     │                │  │
│  │  │  - Watch     │  │    - Handles IPC              │                │  │
│  │  └──────────────┘  └───────────────────────────────┘                │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                       EXTERNAL INTEGRATIONS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐           │
│  │   ChromaDB      │  │  LSP Servers    │  │   OpenAI API     │           │
│  │   (Local)       │  │  (typescript-   │  │   (Embeddings)   │           │
│  │  - 5 domain     │  │   language-     │  │                  │           │
│  │    collections  │  │   server, etc.) │  │                  │           │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘           │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EXISTING POLLY PHASES                             │   │
│  │  - Phase 13b: User Profile System                                    │   │
│  │  - Phase 24: Orchestrator Mode (Persona coordination)                │   │
│  │  - Phase 27: Designer Persona                                        │   │
│  │  - Phase ??: Epub Vector System                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Data Flow Example: User Types Code

Let's trace what happens when a user types code in the editor:

**Step 1: User types in Monaco Editor**
```
User types: "function calculateGrainDensity"
                                           ↓
            Monaco Editor detects change
```

**Step 2: Multiple parallel processes activate**
```
┌──────────────────────┬───────────────────────┬─────────────────────────┐
│   LSP Process        │   TreeSitter Process  │   RAG Process           │
├──────────────────────┼───────────────────────┼─────────────────────────┤
│ 1. LSP receives text │ 1. Parse new syntax   │ 1. Generate queries:    │
│ 2. Analyze for       │ 2. Identify tokens    │    - "grain density"    │
│    diagnostics       │ 3. Update highlighting│    - "calculate"        │
│ 3. Provide           │                       │    - Current file ctx   │
│    completion        │                       │ 2. Search vectors:      │
│    suggestions       │                       │    - Signals domain     │
│                      │                       │    - Sigils domain      │
│                      │                       │ 3. Rank results         │
└──────────────────────┴───────────────────────┴─────────────────────────┘
                               ↓
                    Results merged in IDE Shell
                               ↓
            ┌──────────────────────────────────────┐
            │  Monaco Editor displays:             │
            │  - Syntax highlighting (TreeSitter)  │
            │  - Completion popup (LSP)            │
            │  - Context panel (RAG results)       │
            └──────────────────────────────────────┘
```

**Step 3: User selects completion**
```
User selects completion: "calculateGrainDensity(grainSize, overlap)"
                               ↓
        Profile Learning Service observes
                               ↓
        ┌────────────────────────────────────────┐
        │ Learn:                                 │
        │ - User accepts function-style naming   │
        │ - User prefers descriptive params      │
        │ - Pattern: Audio-domain calculations   │
        └────────────────────────────────────────┘
                               ↓
            Updated profile influences next suggestion
```

**Step 4: User continues typing (body of function)**
```
User asks in Chat: "How should I implement this?"
                               ↓
        Persona Coordinator activates
                               ↓
        ┌────────────────────────────────────────┐
        │ Determine relevant personas:           │
        │ - Programmer (implementation)          │
        │ - [Detect audio context]               │
        │   → Include past SC patterns from RAG  │
        └────────────────────────────────────────┘
                               ↓
        ┌────────────────────────────────────────┐
        │ RAG retrieves from Signals domain:     │
        │ - Past grain synthesis code            │
        │ - SuperCollider docs on overlap        │
        │ - User's essay on granular aesthetics  │
        └────────────────────────────────────────┘
                               ↓
        ┌────────────────────────────────────────┐
        │ Programmer persona responds:           │
        │ - Suggests implementation              │
        │ - References user's past patterns      │
        │ - Applies profile style preferences    │
        └────────────────────────────────────────┘
```

#### Integration Points with Existing Polly Phases

**Phase 13b: User Profile System**
- **Integration**: Profile Learning Service reads/writes to Phase 13b profile database
- **Data flow**: Editor observations → Profile updates → Suggestion adaptation
- **Files**: `src/main/services/ProfileLearningService.ts` connects to Phase 13b API

**Phase 24: Orchestrator Mode**
- **Integration**: Persona Coordinator uses Phase 24's persona routing logic
- **Data flow**: Chat queries → Orchestrator routes to personas → Coordinated responses
- **Files**: `src/renderer/services/personas/PersonaCoordinator.ts` extends Phase 24

**Phase 27: Designer Persona**
- **Integration**: Designer-Programmer Bridge converts Phase 27 design specs to code
- **Data flow**: Design constraints → Token extraction → Code generation
- **Files**: `src/renderer/services/personas/DesignerProgrammerBridge.ts`

**Epub Vector System** (assumed from earlier phases)
- **Integration**: RAG Service queries epub vector collections
- **Data flow**: Editor context → Vector search → Cross-domain results
- **Files**: `src/main/services/RAGService.ts` connects to ChromaDB collections

#### Technology Stack Summary

**Frontend (Renderer Process)**:
- React 18
- Monaco Editor 0.45+
- TypeScript 5.0+
- styled-components 6.0+
- xterm.js 5.0+ (terminal)
- web-tree-sitter 0.20+ (syntax parsing)

**Backend (Main Process)**:
- Electron 28+
- Node.js 20+
- simple-git 3.0+ (git operations)
- node-pty 1.0+ (terminal PTY)
- ws 8.0+ (WebSocket for LSP)

**LSP Integration**:
- monaco-languageclient 7.0+
- vscode-jsonrpc 8.0+
- vscode-languageserver-protocol 3.17+

**RAG/Vector Storage**:
- ChromaDB 0.4+ (local vector database)
- OpenAI API (embeddings via text-embedding-3-small)

**LSP Servers** (installed separately):
- typescript-language-server
- pylsp (Python)
- rust-analyzer
- gopls (Go)
- clangd (C/C++)
- sclang-lsp (custom SuperCollider server)

#### Performance Characteristics

**Editor Operations**:
- File open: <50ms (Monaco model creation)
- Keystroke latency: <16ms (60fps rendering)
- Syntax highlighting: <10ms (tree-sitter incremental parse)
- LSP completion: 50-200ms (server-dependent)

**RAG Operations**:
- Query generation: <10ms (local analysis)
- Vector search: 50-150ms (ChromaDB query across 5 domains)
- Result ranking: <20ms (in-memory sort)
- Total latency: 100-200ms (acceptable for non-blocking UI)

**Profile Learning**:
- Pattern extraction: <50ms per file edit
- Profile update: <20ms (in-memory)
- Profile persistence: Async, non-blocking

**Memory Usage**:
- Base application: ~200MB
- Monaco editor (per open file): ~5-10MB
- LSP servers (all running): ~300-500MB
- ChromaDB vectors: ~100-500MB (depending on corpus size)
- **Total**: ~1-1.5GB (reasonable for modern dev machines)

**Comparison to VSCode**:
- VSCode: ~300-800MB base + extensions
- Polly Code: ~200-300MB base (Monaco + custom shell)
- **Advantage**: Lighter base, since we don't load unused VSCode features

---

## PART 3 COMPLETE

Part 3 (Technical Architecture) is now complete. We've covered:
- ✅ Section 11: Why Monaco Over VSCode Fork
- ✅ Section 12: Monaco Editor Foundation  
- ✅ Section 13: Custom IDE Shell Architecture
- ✅ Section 14: Language Intelligence Layer
- ✅ Section 15: RAG Pipeline Integration
- ✅ Section 16: Persona System Integration
- ✅ Section 17: Profile-Aware Coding
- ✅ Section 18: Complete System Architecture

**Current page count**: ~30-35 pages

**Remaining**: Parts 4, 5, 6 (~25-30 pages)

---


---

## PART 4: USER EXPERIENCE

This section explores Polly Code from the user's perspective—who it's for, how it feels to use, and what makes the day-to-day experience unique.

---

### Section 19: User Personas

Polly Code is designed for specific types of developers who will benefit most from its unique features. These are not mainstream developers—they're polymaths, niche domain specialists, and systems thinkers.

#### Primary Persona: The Polymath Developer

**Profile**:
- **Name**: Alex (composite based on Brett)
- **Background**: Audio engineer + programmer + writer + designer
- **Works across domains**: SuperCollider, norns, web development, documentation, visual sketches
- **Pain points**:
  - Constant context switching between domains
  - Documentation scattered across tools (Notion, Obsidian, code comments, schelp files)
  - AI tools don't understand niche domains (SuperCollider, norns)
  - Generic code suggestions don't match their aesthetic/philosophy
  - Design specs and code implementations drift apart

**Why Polly Code Works for Alex**:
- **Cross-domain context**: When coding a norns script, Polly retrieves SuperCollider patterns, design philosophy essays, and past norns code
- **Niche language support**: First-class SuperCollider LSP with schelp integration
- **Institutional memory**: Polly remembers past architectural decisions and design constraints
- **Profile-aware**: Learns Alex's coding style (functional, minimal, constraint-based)
- **Designer-Coder integration**: Design tokens automatically become code

**Quote**: *"Polly is the first IDE that understands I'm not just a coder—I'm building an aesthetic system across music, code, and philosophy."*

---

#### Secondary Persona: The Audio Developer

**Profile**:
- **Name**: Jordan
- **Background**: Sound designer, live performer, DSP researcher
- **Primary tools**: SuperCollider, Max/MSP, norns, Faust
- **Pain points**:
  - Most IDEs have poor audio language support
  - Documentation for audio libraries is fragmented
  - Hard to remember UGen parameters and behaviors
  - No AI assistance for synthesis patterns
  - Copilot/Cursor don't understand audio-specific contexts

**Why Polly Code Works for Jordan**:
- **SuperCollider-first**: Custom LSP with schelp hover docs, UGen completion
- **Audio domain RAG**: Retrieves synthesis patterns from past work and indexed documentation
- **Real-time reference**: Ask "What's the difference between GrainBuf and GrainSin?" while coding
- **Pattern library**: Polly learns Jordan's preferred synthesis techniques (e.g., always uses bounded randomness)

**Quote**: *"Finally, an IDE that knows what a SynthDef is. Cursor kept trying to autocomplete C++ syntax in my .scd files."*

---

#### Tertiary Persona: The Systems Thinker

**Profile**:
- **Name**: Morgan
- **Background**: Software architect, technical writer, open-source maintainer
- **Mindset**: Thinks in systems, not features. Cares deeply about naming, structure, and rationale
- **Pain points**:
  - Needs to document *why* decisions were made, not just what
  - AI suggestions don't respect existing architecture
  - Hard to maintain consistency across large codebases
  - Documentation and code drift apart
  - Generic AI doesn't understand project-specific constraints

**Why Polly Code Works for Morgan**:
- **Institutional memory**: Polly remembers architecture decisions from past commits and docs
- **Architect persona**: Can ask "Should this be a service or a component?" and get contextual guidance
- **Design philosophy integration**: Morgan's essays on software design inform code suggestions
- **Consistency enforcement**: Profile learning ensures new code matches existing patterns

**Quote**: *"Polly doesn't just suggest code—it suggests code that fits my system's philosophy."*

---

### Section 20: Day-in-the-Life Scenarios

These scenarios illustrate what it's like to use Polly Code for real work.

#### Scenario 1: Building a norns Instrument (2.5 hours)

**Context**: Alex wants to create a new granular looping instrument for norns, inspired by a recent essay they wrote about "constrained improvisation."

**9:00 AM - Starting the project**

Alex opens Polly Code and creates a new file: `lib/grainloop.lua`

Polly immediately activates:
- **File tree** shows existing norns libraries for reference
- **RAG status indicator** shows "1,247 vectors available" (includes past norns code, SuperCollider docs, and Alex's essays)
- **Chat panel** opens with Architect persona active

Alex types in chat:
> "I want to build a granular looper for norns that enforces constraints—limited grain size, no infinite feedback. How should I structure it?"

**Architect responds** (after querying RAG across domains):
```
[Architect] Based on your essay "Constraint-Based Design" and your past 
norns instruments (wrms, buoys), I recommend:

Structure:
- GrainLoop engine (SuperCollider SynthDef)
  - Bounded parameters (your philosophy: "freedom through limits")
  - RecBuf for loop storage
  - GrainBuf for playback with pitch/density control
  
- Lua script (norns UI)
  - Minimal controls (3 params max - your design principle)
  - Grid integration (following your wrms pattern)
  - Visual feedback (simple waveform)

Rationale: Keep engine and UI separate for testability. Use bounded
random variation (0.8-1.2x) for grain pitch - from your "subtle chaos" 
principle.

Reference: lib/wrms.lua:45 (similar buffer management pattern)
```

Alex clicks "Open Reference" → Polly opens `lib/wrms.lua` in a split pane.

**9:15 AM - Writing the SuperCollider engine**

Alex creates `lib/sc/grainloop.sc` and starts typing:

```supercollider
// GrainLoop - Constrained granular looper
Engine_GrainLoop : CroneEngine {
```

Polly's **SuperCollider LSP** activates:
- Autocomplete suggests `CroneEngine` methods (`alloc`, `addCommand`)
- **Hover docs** show CroneEngine API (from schelp files indexed in Signals domain)

Alex types:
```supercollider
var buf;
var synth;

*new { arg context, doneCallback;
  ^super.new(context, doneCallback);
}

alloc {
  // [cursor here - types "create buffer"]
```

Polly's **RAG retrieval** activates:
- Finds similar buffer allocation in `wrms.sc`
- Finds SuperCollider Buffer documentation
- Finds Alex's note on "always use 2-second buffers for live input"

**Programmer persona suggests**:
```supercollider
// Create 2-second stereo buffer (your standard for live looping)
buf = Buffer.alloc(context.server, context.server.sampleRate * 2, 2);

// RecBuf synth with bounded feedback (constraint: max 0.8)
synth = {
  arg in=0, gate=1, feedback=0.5;
  var sig, rec;
  sig = SoundIn.ar(in, 2);
  rec = RecBuf.ar(sig, buf.bufnum, loop: 1);
  // Feedback clamped to prevent infinite buildup
  sig = sig + (PlayBuf.ar(2, buf.bufnum, loop: 1) * feedback.clip(0, 0.8));
  Out.ar(0, sig);
}.play(context.server);

this.addCommand(\record, "i", { arg msg;
  synth.set(\gate, msg[1]);
});
```

Alex accepts the suggestion with minor edits (changes `feedback.clip` threshold to 0.7).

**Polly learns**: "User prefers 0.7 feedback limit, not 0.8"

**9:45 AM - Building the Lua UI**

Alex switches to `grainloop.lua` and types:

```lua
-- grainloop
-- constrained granular looper
--
```

Polly detects this is a norns script (from file structure and comments).

**RAG retrieval** finds:
- norns scripting patterns from past instruments
- Documentation on norns parameters
- Alex's design principle: "3 parameters max"

Alex types:
```lua
engine.name = "GrainLoop"

local grain_size = 1
local density = 4
local pitch_var = 0.1

function init()
  -- [cursor here - types "setup params"]
```

**Programmer suggests** (following norns conventions from RAG):
```lua
params:add_control("grain_size", "grain size", 
  controlspec.new(0.05, 0.5, 'lin', 0.01, 0.1, "s"))
params:add_control("density", "density",
  controlspec.new(1, 16, 'lin', 1, 4, "grains"))
params:add_control("pitch_var", "pitch variation",
  controlspec.new(0, 0.5, 'lin', 0.01, 0.1, ""))

params:set_action("grain_size", function(x)
  grain_size = x
  engine.grain_size(x)
end)

-- Grid integration (following your wrms pattern)
g = grid.connect()
g.key = function(x, y, z)
  if z == 1 then
    -- Trigger recording
    engine.record(1)
  else
    engine.record(0)
  end
  grid_redraw()
end
```

Alex accepts with one change: renames `pitch_var` to `chaos` (more poetic).

**Polly learns**: "User prefers evocative parameter names"

**10:30 AM - Testing and refinement**

Alex tests the instrument on norns. Discovers the grain pitch variation is too subtle.

Returns to Polly, asks in Chat:
> "The pitch variation feels too constrained. But I don't want wild pitch shifts—just more noticeable variation."

**Architect responds**:
```
[Architect] Based on your "constrained improvisation" philosophy:
Current range: 0-0.5 (subtle)
Suggested: 0-1.2 (noticeable but bounded - your wrms instrument uses 1.5x max)

This maintains your "subtle chaos" principle while being more audible.
```

Alex updates the controlspec range to `0-1.2`.

**11:30 AM - Documentation**

Alex adds a README:

```markdown
# grainloop

Constrained granular looper for norns.

## Philosophy

Based on "freedom through limits" - this instrument enforces:
- Max 0.7 feedback (no infinite buildup)
- Bounded pitch variation (0-1.2x)
- 3 parameters only
```

Polly indexes this README → future queries will reference this design philosophy.

**11:45 AM - Done**

Alex commits the code. Polly's git panel shows:
```
Staged:
  lib/grainloop.lua
  lib/sc/grainloop.sc
  README.md
```

Alex writes commit message: "Add grainloop instrument - constrained granular design"

**Total time**: 2.5 hours (vs. 4-5 hours without Polly's context)

**Key wins**:
- Architect provided structural guidance based on past work
- SuperCollider LSP gave real-time docs for UGens
- RAG retrieved relevant patterns from past instruments
- Profile learning adapted to Alex's aesthetic preferences
- Design philosophy from essays informed implementation

---

#### Scenario 2: Refactoring a React Component with Designer Integration

**Context**: Morgan is refactoring a dashboard component. The Designer persona created a spec yesterday.

**2:00 PM - Opening the design spec**

Morgan opens Chat panel, asks:
> "Show me the design spec for DashboardCard"

**Designer persona responds**:
```
[Designer] Design spec created yesterday:

Component: DashboardCard
Layout: CSS Grid (auto-fit columns)
Spacing: 16px grid system
Colors:
  - Background: ${tokens.surface}
  - Border: ${tokens.border}
  - Text: ${tokens.textPrimary}
Constraints:
  - Max width: 400px
  - Min width: 280px
  - Aspect ratio: 1:1 for metric cards
Responsive:
  - Mobile: 1 column
  - Tablet: 2 columns
  - Desktop: 4 columns
```

Morgan clicks "Generate Code" in the chat panel.

**Designer-Programmer Bridge activates**:
- Reads design spec
- Extracts design tokens
- Generates React component with styled-components

**Programmer generates**:
```typescript
// DashboardCard.tsx
import React from 'react';
import { styled } from 'styled-components';

const tokens = {
  surface: '#2a2a2a',
  border: '#404040',
  textPrimary: '#e0e0e0',
  spacing: '16px'
};

const CardWrapper = styled.div`
  background-color: ${tokens.surface};
  border: 1px solid ${tokens.border};
  color: ${tokens.textPrimary};
  padding: ${tokens.spacing};
  border-radius: 8px;
  
  /* Constraints from design spec */
  max-width: 400px;
  min-width: 280px;
  aspect-ratio: 1 / 1;
  
  /* Responsive breakpoints */
  @media (max-width: 768px) {
    grid-column: span 1;
  }
  
  @media (min-width: 769px) and (max-width: 1024px) {
    grid-column: span 2;
  }
  
  @media (min-width: 1025px) {
    grid-column: span 4;
  }
`;

export const DashboardCard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <CardWrapper>{children}</CardWrapper>;
};
```

Morgan reviews, accepts. The code **exactly matches the design spec** — no drift.

**2:15 PM - Done**

**Time saved**: 30-45 minutes (no manual translation from design to code)

---


#### Scenario 3: SuperCollider DSP Research with Documentation

**Context**: Jordan is researching granular synthesis techniques and wants to implement a new grain envelope.

**4:00 PM - Starting research**

Jordan opens Polly Code, creates `research/grain_envelopes.scd`

Types in Chat:
> "What grain envelopes are available in SuperCollider?"

**Programmer responds** (with RAG from Signals domain):
```
[Programmer] SuperCollider has several grain envelope options:

From sc3-plugins:
- Hanning window (default, smooth)
- Welch window (wider, less artifacts)
- Custom Env (arbitrary shape)

Example from your past code (lib/grains.scd:23):
GrainBuf.ar(
  envbufnum: -1, // Hanning (default)
  // or:
  envbufnum: Buffer.sendCollection(s, 
    Env.sine.discretize(512)
  ).bufnum // Sine envelope
)

Reference docs: [Click to open: schelp/GrainBuf.html]
```

Jordan clicks the schelp reference → opens in a side panel (rendered markdown from indexed docs).

**4:15 PM - Experimenting**

Jordan types:
```supercollider
// Compare different envelopes
(
~envs = [
  Buffer.sendCollection(s, Env.sine.discretize(512)),
  Buffer.sendCollection(s, Env.perc(0.1, 0.9).discretize(512)),
  // [cursor here - wants to try custom envelope]
```

**Polly suggests** (from past patterns):
```supercollider
Buffer.sendCollection(s, 
  Env([0, 1, 0.7, 0], [0.3, 0.4, 0.3], \sine).discretize(512)
) // Custom multi-segment
```

Jordan experiments, settles on a custom envelope.

**4:45 PM - Documenting findings**

Jordan switches to `research/grain_envelopes.md` and writes:

```markdown
# Grain Envelope Research

Tested three envelope types:
1. Sine - smoothest, least artifacts
2. Perc - more attack, sharper transients
3. Custom - [describes envelope shape]

Conclusion: Custom envelope with slight decay works best for 
percussive grain clouds.
```

Polly indexes this → future queries about grain envelopes will reference Jordan's research.

**Total time**: 45 minutes (including experimentation)

**Key wins**:
- Instant access to SuperCollider docs without leaving editor
- Past code examples surfaced automatically
- Research documented and indexed for future reference

---

### Section 21: UI/UX Wireframes

This section shows key screens and interactions in Polly Code.

#### Main Editor Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ File  Edit  View  Persona  Help                          Polly Code     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐ ┌───────────────────────────────────┐ ┌────────────┐ │
│  │ FILE TREE    │ │ EDITOR                            │ │ CHAT       │ │
│  ├──────────────┤ ├───────────────────────────────────┤ ├────────────┤ │
│  │              │ │ grainloop.lua [×]                 │ │ Architect  │ │
│  │ 📁 lib/      │ ├───────────────────────────────────┤ │ Designer   │ │
│  │  📁 sc/      │ │  1  -- grainloop                  │ │ Programmer │ │
│  │   grainloop  │ │  2  -- constrained granular       │ ├────────────┤ │
│  │  grainloop ● │ │  3                                │ │            │ │
│  │ 📁 data/     │ │  4  engine.name = "GrainLoop"     │ │ > How      │ │
│  │ 📄 README    │ │  5                                │ │ should I   │ │
│  │              │ │  6  local grain_size = 0.1        │ │ structure  │ │
│  │ GIT          │ │  7  local density = 4             │ │ this?      │ │
│  │ ──────────   │ │  8  local chaos = 0.1             │ │            │ │
│  │ ⎇ main ↑1    │ │  9                                │ │ [Architect]│ │
│  │ 3 changes    │ │ 10  function init()               │ │ Based on   │ │
│  │  M grainloop │ │ 11    params:add...               │ │ your past  │ │
│  │  M grainloop │ │ 12  end                           │ │ norns...   │ │
│  │  A README    │ │                                   │ │            │ │
│  │              │ │                                   │ │ [Show more]│ │
│  └──────────────┘ └───────────────────────────────────┘ └────────────┘ │
│                   ┌───────────────────────────────────┐                 │
│                   │ TERMINAL                          │                 │
│                   ├───────────────────────────────────┤                 │
│                   │ ~/dust/code/grainloop             │                 │
│                   │ $ maiden rerun                    │                 │
│                   │ restarting...                     │                 │
│                   │ DONE                              │                 │
│                   │                                   │                 │
│                   └───────────────────────────────────┘                 │
├─────────────────────────────────────────────────────────────────────────┤
│ grainloop.lua | Ln 10, Col 18 | LSP:✓ | 🧠 1247 vectors | ⎇ main | UTF-8│
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements**:
1. **File Tree** (left): Standard tree with git status indicators (`●` = modified)
2. **Git Panel** (left, collapsible): Shows branch, ahead/behind, staged files
3. **Editor** (center): Monaco with tab bar, syntax highlighting
4. **Chat Panel** (right): Persona selector at top, conversation below
5. **Terminal** (bottom): Integrated terminal for running commands
6. **Status Bar** (bottom): File info, LSP status, **RAG indicator** (unique to Polly), git branch

---

#### RAG Context Visualization

When RAG retrieves context, it appears inline:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ EDITOR                                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  1  function calculateGrainDensity(grainSize, overlap)                  │
│  2    // [cursor here]                                                  │
│  3  end                                                                 │
│                                                                          │
│  ╭───────────────────────────────────────────────────────────────────╮ │
│  │ 💡 Context from knowledge graph:                                   │ │
│  ├───────────────────────────────────────────────────────────────────┤ │
│  │ 📄 signals:supercollider_patterns.md (Similar implementation)      │ │
│  │    "Grain density = 1 / (grainSize * overlap)"                    │ │
│  │                                                                    │ │
│  │ 📖 scrolls:constraint_design.md (Design philosophy)                │ │
│  │    "Use bounded randomness to prevent chaotic behavior"           │ │
│  │                                                                    │ │
│  │ 💻 sigils:lib/wrms.lua:45 (Past code)                              │ │
│  │    density = util.clamp(1 / (size * 0.5), 1, 32)                 │ │
│  ╰───────────────────────────────────────────────────────────────────╯ │
│                                                                          │
│  [Apply Pattern 1] [Apply Pattern 2] [Dismiss]                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Interactions**:
- **Click "Apply Pattern"** → Insert code at cursor
- **Click source link** → Open file/doc in split pane
- **Dismiss** → Hide context panel
- **Auto-dismiss**: Panel fades after 10 seconds of no interaction

---

#### Persona Coordination UI

When multiple personas respond, they're clearly separated:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CHAT PANEL                                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ [Architect ▼] [Designer] [Programmer]                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ You (2:34 PM):                                                          │
│ Should I use a service or a component for metrics collection?           │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 🏛️ Architect (2:34 PM):                                             │ │
│ │                                                                      │ │
│ │ Use a service. Rationale:                                           │ │
│ │ - Metrics collection is cross-cutting (not UI-specific)             │ │
│ │ - Multiple components will need access                              │ │
│ │ - Easier to test in isolation                                       │ │
│ │                                                                      │ │
│ │ Structure: MetricsService (singleton) → MetricsContext (React)      │ │
│ │ → MetricsCard components                                            │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 🎨 Designer (2:34 PM):                                              │ │
│ │                                                                      │ │
│ │ If using a service, visual representation:                          │ │
│ │ - MetricsCard should be "dumb" (presentation only)                  │ │
│ │ - Service provides data, cards just render                          │ │
│ │ - Keep card styling consistent with your design system tokens       │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ 💻 Programmer (2:35 PM):                                            │ │
│ │                                                                      │ │
│ │ Here's the implementation:                                          │ │
│ │                                                                      │ │
│ │ ```typescript                                                        │ │
│ │ // MetricsService.ts                                                │ │
│ │ class MetricsService {                                              │ │
│ │   private metrics: Map<string, number> = new Map();                │ │
│ │   ...                                                               │ │
│ │ ```                                                                  │ │
│ │                                                                      │ │
│ │ [Insert Code] [Copy]                                                │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │ Type your message... (Cmd+Enter to send)                          │  │
│ └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Visual Hierarchy**:
- Each persona has a distinct icon (🏛️ Architect, 🎨 Designer, 💻 Programmer)
- Responses ordered by authority (Architect → Designer → Programmer)
- Code blocks have action buttons (Insert, Copy)

---

#### Design-to-Code Flow

When Designer creates a spec, Programmer can generate code directly:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CHAT PANEL - Designer Mode                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ 🎨 Designer (Constraint Mode):                                          │
│                                                                          │
│ Component: DashboardCard                                                │
│                                                                          │
│ Constraints:                                                            │
│  ✓ Spacing: 16px grid                                                  │
│  ✓ Colors: monochrome + accent                                         │
│  ✓ Max width: 400px                                                    │
│  ✓ Layout: CSS Grid                                                    │
│                                                                          │
│ Design Tokens:                                                          │
│  - surface: #2a2a2a                                                    │
│  - border: #404040                                                     │
│  - textPrimary: #e0e0e0                                                │
│                                                                          │
│ [💻 Generate Code] [📋 Export Spec] [✏️ Edit]                           │
│                                                                          │
│ ─────────────────────────────────────────────────────────────────────── │
│                                                                          │
│ [User clicks "Generate Code"]                                           │
│                                                                          │
│ ─────────────────────────────────────────────────────────────────────── │
│                                                                          │
│ 💻 Programmer:                                                          │
│                                                                          │
│ Generated component from design spec:                                   │
│                                                                          │
│ ```typescript                                                            │
│ // DashboardCard.tsx                                                    │
│ import React from 'react';                                              │
│ import { styled } from 'styled-components';                             │
│ ...                                                                      │
│ ```                                                                      │
│                                                                          │
│ [Insert in Editor] [Save to File] [Revise]                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Workflow**:
1. Designer creates spec with constraints
2. User clicks "Generate Code"
3. Programmer generates implementation
4. User reviews, inserts into editor
5. **Design and code stay in sync** (single source of truth)

---

### Section 22: Designer-Coder Workflow

This section details the complete flow from design to implementation.

#### Step 1: Design Constraints Definition

**Designer persona** in "Constraint Mode" lets you define design rules:

```
Designer: What component are you designing?
User: A metrics dashboard card

Designer: Let's define constraints. Current context suggests:
- You use 16px grid spacing (from design_tokens.ts)
- You prefer monochrome with accent colors
- Your components are typically 300-400px wide

Constraints:
1. Spacing: 16px grid ✓ (from tokens)
2. Colors: Monochrome + accent ✓ (from tokens)
3. Typography: SF Mono ✓ (from tokens)
4. Layout: [Flex | Grid | Absolute]
5. Max width: [input]
6. Responsive breakpoints: [input]

[Continue]
```

User fills in missing constraints. Designer saves spec.

---

#### Step 2: Living Spec Storage

Design spec stored as structured data (not just markdown):

```json
{
  "component": "DashboardCard",
  "version": 1,
  "constraints": [
    {
      "type": "spacing",
      "rule": "${tokens.spacing.base}",
      "value": "16px",
      "rationale": "Consistent with grid system"
    },
    {
      "type": "layout",
      "rule": "CSS Grid with auto-fit",
      "value": "repeat(auto-fit, minmax(280px, 1fr))",
      "rationale": "Responsive without media queries"
    }
  ],
  "tokens": {
    "surface": "#2a2a2a",
    "border": "#404040",
    "textPrimary": "#e0e0e0"
  },
  "references": [
    "design_tokens.ts",
    "design_system.md"
  ]
}
```

This spec is:
- **Versioned** (track changes over time)
- **Indexed** (searchable via RAG)
- **Linked** (references design tokens file)
- **Executable** (can generate code deterministically)

---

#### Step 3: Code Generation from Spec

When user requests code, **Designer-Programmer Bridge**:

1. Parses spec JSON
2. Extracts constraints and tokens
3. Generates framework-specific code (React, Vue, Svelte—user's preference learned by profile)
4. Applies user's coding style (from profile learning)

**Generated code includes**:
- Inline comments explaining constraints
- References to design tokens
- Responsive breakpoints
- Accessibility attributes (from design system)

---

#### Step 4: Constraint Enforcement

If user later edits the component code in a way that **violates constraints**, Polly warns:

```
⚠️ Constraint Violation Detected

You changed max-width to 600px, but design spec specifies 400px.

Original constraint: "Max width: 400px - ensures cards fit grid"

[Update Spec] [Revert Change] [Ignore]
```

**Options**:
- **Update Spec**: Change design spec to match code (spec evolves with code)
- **Revert Change**: Undo code change
- **Ignore**: Allow deviation (tracked for review)

This prevents **design-code drift**, a major pain point for designers and developers.

---

#### Step 5: Design Evolution

When design system changes (e.g., new spacing tokens), Polly detects affected components:

```
🎨 Design Token Update Detected

Token changed: spacing.base (16px → 20px)

Affected components:
- DashboardCard (uses spacing.base)
- MetricCard (uses spacing.base)
- HeaderNav (uses spacing.base)

[Preview Changes] [Apply All] [Review Each]
```

User can:
- **Preview**: See diffs before applying
- **Apply All**: Auto-update all components
- **Review Each**: Approve changes individually

**Result**: Design system updates propagate automatically to code.

---

### Section 23: Interaction Patterns

This section covers specific UI interactions that make Polly Code feel responsive and intelligent.

#### Pattern 1: Context-Aware Completion

**Trigger**: User types in Monaco editor

**Behavior**:
1. **LSP completion** appears immediately (50-200ms)
2. **RAG context panel** slides in from right (100-300ms) if relevant context found
3. **Profile-adjusted suggestions** appear at top of completion list

**Visual**:
```
User types: "function calc"

┌─────────────────────────────────────────────────────┐
│  function calc█                                     │
│  ┌────────────────────────────────────────┐        │
│  │ 💡 calculateGrainDensity                │ ← LSP │
│  │ 💡 calculateBPM                         │        │
│  │ 💡 calculate                            │        │
│  └────────────────────────────────────────┘        │
│                                                     │
│  ╭──────────────────────────────────╮              │
│  │ 📄 Past pattern:                 │ ← RAG        │
│  │ calculateGrainDensity used 3x    │              │
│  │ [Apply]                          │              │
│  ╰──────────────────────────────────╯              │
└─────────────────────────────────────────────────────┘
```

**User can**:
- Use arrows to select LSP completion (standard)
- Click "Apply" in RAG panel to insert past pattern
- Press `Cmd+K` to open full RAG results in chat

---

#### Pattern 2: Inline Documentation Hover

**Trigger**: User hovers over symbol

**Behavior**:
1. **LSP hover** shows type signature (immediate)
2. **Polly enriches** with:
   - Past usage examples (from RAG)
   - Related documentation (from Scrolls domain)
   - User's comments about this symbol (from profile)

**Visual**:
```
User hovers over: GrainBuf

┌─────────────────────────────────────────────────────┐
│ GrainBuf.ar(numChannels, trigger, dur, ...)        │
│ ─────────────────────────────────────────────────── │
│ LSP: Granular synthesis UGen                        │
│                                                     │
│ 📖 From SuperCollider docs:                        │
│ "GrainBuf plays back samples from a buffer         │
│  with user-defined grain envelopes."               │
│                                                     │
│ 💡 Your past usage (3 times):                      │
│ lib/wrms.lua:67 - Used with Hanning window         │
│ lib/grainloop.sc:23 - Custom envelope              │
│                                                     │
│ 📝 Your note:                                      │
│ "GrainBuf is CPU-intensive - limit to 32 grains"   │
│                                                     │
│ [Open Docs] [See All Usage]                        │
└─────────────────────────────────────────────────────┘
```

**Unique to Polly**: Personal notes and past usage context.

---

#### Pattern 3: Persona Quick Switch

**Trigger**: User types `@` in chat

**Behavior**:
- Autocomplete shows personas: `@architect`, `@designer`, `@programmer`
- Select persona to direct query

**Visual**:
```
Chat input:
@ar█

┌────────────────────┐
│ @architect         │
│ @artist (disabled) │
└────────────────────┘

User selects @architect, types:
@architect should this be a service or component?

[Only Architect responds]
```

**Use case**: Direct questions to specific expertise.

---

#### Pattern 4: RAG Feedback Loop

**Trigger**: User accepts/rejects RAG suggestion

**Behavior**:
- **Accept**: Polly learns this context was useful, boosts similar patterns
- **Reject**: Polly learns this context was not useful, downranks
- Over time, RAG becomes more accurate for user's workflow

**Visual**:
```
RAG suggests pattern X
User clicks "Apply"

[Toast notification]
✓ Pattern learned - I'll suggest similar patterns in the future

---

RAG suggests pattern Y
User clicks "Dismiss"

[No notification, but internally downranked]
```

**Result**: RAG adapts to user's preferences without explicit configuration.

---

## PART 4 COMPLETE

Part 4 (User Experience) is now complete. We've covered:
- ✅ Section 19: User Personas (Polymath, Audio Developer, Systems Thinker)
- ✅ Section 20: Day-in-the-Life Scenarios (norns development, React refactoring, SC research)
- ✅ Section 21: UI/UX Wireframes (Main layout, RAG visualization, Persona UI)
- ✅ Section 22: Designer-Coder Workflow (Constraint definition → Code generation)
- ✅ Section 23: Interaction Patterns (Context-aware completion, hover docs, persona switching)

**Current page count**: ~45-50 pages

**Remaining**: Parts 5 & 6 (~15-20 pages)

---


---

## PART 5: IMPLEMENTATION ROADMAP

This section breaks down the implementation into four sub-phases (17a, 17b, 17c, 17d) with detailed week-by-week plans, milestones, and dependencies.

---

### Section 24: Phase 17a - Monaco Foundation (2-3 weeks)

**Goal**: Build the core IDE shell with Monaco editor, file tree, terminal, and git integration. No AI features yet—just a functional code editor.

**Duration**: 2-3 weeks (10-15 working days)

**Team Size**: 1 developer (you)

---

#### Week 1: Electron Shell + Monaco Integration

**Days 1-2: Project Setup**

Tasks:
- Initialize Electron project with TypeScript
- Set up React with Vite bundler
- Configure build pipeline (main + renderer processes)
- Install dependencies:
  - `electron`: 28+
  - `react`: 18
  - `monaco-editor`: 0.45+
  - `styled-components`: 6.0+

Files to create:
```
polly-code/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── src/
│   ├── main/
│   │   └── index.ts (Electron main process)
│   └── renderer/
│       ├── index.html
│       ├── index.tsx (React entry)
│       └── App.tsx
```

Deliverable: Empty Electron window with React rendering

**Days 3-5: Monaco Editor Integration**

Tasks:
- Implement Monaco editor component
- Set up editor configuration (theme, fonts, settings)
- Implement model management (open/close files)
- Add tab bar for open files
- Implement file open/close/save operations

Files to create:
```
src/renderer/components/
├── editor/
│   ├── MonacoEditor.tsx
│   └── MonacoConfig.ts
├── tabs/
│   └── TabBar.tsx
└── IDEShell.tsx
```

Deliverable: Can open .txt files in Monaco and edit them

---

#### Week 2: File System Integration

**Days 6-8: File Tree Component**

Tasks:
- Implement recursive file tree rendering
- Add file/folder icons
- Implement expand/collapse
- Handle file/folder operations (create, delete, rename)
- Add context menu (right-click)

Files to create:
```
src/renderer/components/filetree/
├── FileTree.tsx
├── FileTreeNode.tsx
├── FileIcon.tsx
└── ContextMenu.tsx

src/main/services/
└── FileSystemService.ts (IPC handlers)
```

Deliverable: Browse and open files from tree

**Days 9-10: Terminal Integration**

Tasks:
- Install xterm.js and node-pty
- Implement terminal component
- Wire up PTY process spawning
- Handle terminal resize
- Support multiple terminal instances

Files to create:
```
src/renderer/components/terminal/
└── Terminal.tsx

src/main/services/
└── PTYService.ts
```

Deliverable: Integrated terminal with shell access

---

#### Week 3: Git Integration

**Days 11-13: Git Panel**

Tasks:
- Install simple-git
- Implement git status parsing
- Display staged/unstaged changes
- Implement stage/unstage operations
- Add commit UI with message input
- Implement push/pull operations

Files to create:
```
src/renderer/components/git/
├── GitPanel.tsx
├── GitFileList.tsx
└── CommitBox.tsx

src/main/services/
└── GitService.ts
```

Deliverable: Can view git status, stage files, and commit

**Days 14-15: Polish & Testing**

Tasks:
- Add keyboard shortcuts (Cmd+S for save, etc.)
- Implement status bar with file info
- Add error handling and loading states
- Write integration tests
- Fix bugs and improve performance

Files to create:
```
src/renderer/components/statusbar/
└── StatusBar.tsx

src/renderer/hooks/
└── useKeyboardShortcuts.ts
```

Deliverable: Polished, stable editor with git integration

---

#### Phase 17a Milestones

| Day | Milestone | Success Criteria |
|-----|-----------|------------------|
| 2 | Electron + React working | Empty window renders |
| 5 | Monaco integrated | Can edit text files |
| 8 | File tree working | Can browse and open files |
| 10 | Terminal integrated | Can run shell commands |
| 13 | Git panel complete | Can commit changes |
| 15 | **Phase 17a DONE** | Functional code editor |

---

### Section 25: Phase 17b - Language Intelligence (3-4 weeks)

**Goal**: Add LSP support, tree-sitter syntax highlighting, and language-specific features. Make Polly Code feel like a real IDE.

**Duration**: 3-4 weeks (15-20 working days)

---

#### Week 1: LSP Foundation

**Days 1-3: LSP Client Setup**

Tasks:
- Install monaco-languageclient and dependencies
- Implement LSP manager service
- Set up WebSocket bridge for LSP servers
- Test with TypeScript language server

Files to create:
```
src/renderer/services/lsp/
├── LSPManager.ts
└── languageConfigs.ts

src/main/services/
└── LSPService.ts (spawn/manage LSP servers)
```

Deliverable: TypeScript completion working

**Days 4-7: Multi-Language Support**

Tasks:
- Add language server configs (Python, Rust, Go, C/C++)
- Install language servers (typescript-language-server, pylsp, rust-analyzer, gopls, clangd)
- Implement language detection from file extension
- Auto-start appropriate LSP servers
- Handle server lifecycle (start/stop/restart)

Files to update:
```
src/renderer/services/lsp/languageConfigs.ts
  - Add configs for 5+ languages
```

Deliverable: LSP working for TypeScript, Python, Rust, Go, C/C++

---

#### Week 2: SuperCollider LSP (Custom)

**Days 8-10: Research & Design**

Tasks:
- Research SuperCollider language structure
- Review existing SC editor implementations (scnvim, scide)
- Design LSP server architecture for SC
- Plan integration with sclang interpreter

Deliverable: Design doc for SC LSP

**Days 11-14: SuperCollider LSP Implementation**

Tasks:
- Implement basic SC LSP server in TypeScript/Node.js
- Add completion for UGens (SinOsc, GrainBuf, etc.)
- Parse schelp files for hover documentation
- Implement basic diagnostics (syntax errors)
- Add jump-to-definition for SynthDefs

Files to create:
```
src/lsp-servers/supercollider/
├── server.ts
├── parser.ts (SC syntax parser)
├── completion.ts
├── hover.ts
├── diagnostics.ts
└── schelp/
    └── indexer.ts (parse schelp docs)
```

Deliverable: Basic SC LSP working (completion + hover)

---

#### Week 3: Tree-sitter Integration

**Days 15-17: Tree-sitter Setup**

Tasks:
- Install web-tree-sitter
- Set up tree-sitter parser manager
- Load grammars for supported languages
- Implement token-based syntax highlighting
- Integrate with Monaco editor

Files to create:
```
src/renderer/services/treesitter/
├── TreeSitterManager.ts
└── grammars/ (WASM files)
```

Deliverable: Enhanced syntax highlighting for all languages

**Days 18-21: Advanced Features**

Tasks:
- Implement code folding (using tree-sitter)
- Add breadcrumb navigation (current scope)
- Implement outline view (tree-sitter structure)
- Add semantic highlighting
- Optimize performance (incremental parsing)

Files to create:
```
src/renderer/components/editor/
├── Breadcrumb.tsx
└── OutlineView.tsx
```

Deliverable: Advanced editor features enabled

---

#### Phase 17b Milestones

| Day | Milestone | Success Criteria |
|-----|-----------|------------------|
| 3 | LSP client working | TypeScript completion |
| 7 | Multi-language LSP | 5+ languages supported |
| 10 | SC LSP designed | Design doc complete |
| 14 | SC LSP implemented | SC completion working |
| 17 | Tree-sitter integrated | Enhanced highlighting |
| 21 | **Phase 17b DONE** | Full language intelligence |

---

### Section 26: Phase 17c - RAG & Polly Integration (4-5 weeks)

**Goal**: Integrate RAG pipeline, connect to epub vector database, enable cross-domain context retrieval. This is where Polly Code becomes differentiated.

**Duration**: 4-5 weeks (20-25 working days)

---

#### Week 1: RAG Infrastructure

**Days 1-3: ChromaDB Setup**

Tasks:
- Install ChromaDB client
- Set up local ChromaDB instance (Docker)
- Create collections for five domains (sigils, signals, scrolls, sights, glyphs)
- Implement connection and health checks

Files to create:
```
src/main/services/rag/
├── ChromaService.ts
└── collections.ts (domain definitions)

docker-compose.yml (ChromaDB service)
```

Deliverable: ChromaDB running and connected

**Days 4-7: Vector Indexing Pipeline**

Tasks:
- Implement file watcher for workspace
- Parse and chunk code files
- Generate embeddings (OpenAI API)
- Index vectors into ChromaDB
- Handle incremental updates (only re-index changed files)

Files to create:
```
src/main/services/rag/
├── IndexingService.ts
├── Chunker.ts (split files into chunks)
└── EmbeddingGenerator.ts (OpenAI API)

src/main/watchers/
└── FileWatcher.ts
```

Deliverable: Code files automatically indexed into vectors

---

#### Week 2: Query Generation

**Days 8-10: Context Extraction**

Tasks:
- Implement editor context analyzer
- Extract surrounding code, imports, comments
- Detect domain from file patterns
- Generate intent-based queries

Files to create:
```
src/renderer/services/rag/
├── QueryGenerator.ts
├── ContextAnalyzer.ts
└── DomainDetector.ts
```

Deliverable: Editor context → RAG queries

**Days 11-14: Vector Search**

Tasks:
- Implement vector search across domains
- Handle multi-query retrieval
- Implement cross-domain ranking algorithm
- Cache search results for performance

Files to create:
```
src/main/services/rag/
├── RAGService.ts
└── CrossDomainRanker.ts

src/renderer/services/rag/
└── RAGCache.ts
```

Deliverable: RAG search working end-to-end

---

#### Week 3: UI Integration

**Days 15-17: RAG Context Panel**

Tasks:
- Design RAG results UI
- Implement context panel component
- Show retrieved documents with relevance scores
- Add "Apply" buttons to insert code
- Implement auto-dismiss behavior

Files to create:
```
src/renderer/components/rag/
├── RAGPanel.tsx
├── RAGResult.tsx
└── RAGActions.tsx
```

Deliverable: RAG results visible in editor

**Days 18-21: Chat Integration**

Tasks:
- Implement chat panel component
- Connect chat to RAG pipeline
- Inject RAG context into LLM prompts
- Display references in chat responses
- Add feedback mechanism (accept/reject)

Files to create:
```
src/renderer/components/chat/
├── ChatPanel.tsx
├── ChatMessage.tsx
├── CodeBlock.tsx
└── Reference.tsx

src/renderer/services/rag/
└── ContextInjector.ts
```

Deliverable: Chat uses RAG context

---

#### Week 4: Documentation Integration

**Days 22-25: Epub Vector Integration**

Tasks:
- Connect to existing epub vector system (from earlier phases)
- Index epub documents into Scrolls domain
- Implement epub-specific retrieval
- Handle cross-references between code and docs

Files to create:
```
src/main/services/rag/
├── EpubIndexer.ts
└── EpubRetriever.ts
```

Deliverable: Documentation searchable from editor

---

#### Week 5: Optimization & Testing

**Days 26-30: Performance Tuning**

Tasks:
- Optimize vector search (batch queries)
- Implement caching strategy
- Profile and fix slow paths
- Add loading indicators
- Write integration tests
- Test with large codebases (1000+ files)

Files to create:
```
src/renderer/components/common/
└── LoadingIndicator.tsx

tests/integration/
└── rag.test.ts
```

Deliverable: RAG system performant and stable

---

#### Phase 17c Milestones

| Day | Milestone | Success Criteria |
|-----|-----------|------------------|
| 3 | ChromaDB running | Collections created |
| 7 | Indexing working | Code files indexed |
| 10 | Queries generated | Editor → queries |
| 14 | Search working | Retrieve relevant results |
| 17 | UI integrated | See RAG results |
| 21 | Chat integrated | Chat uses RAG |
| 25 | Docs integrated | Epub vectors searchable |
| 30 | **Phase 17c DONE** | Full RAG pipeline |

---

### Section 27: Phase 17d - Designer-Coder Integration (5-6 weeks)

**Goal**: Integrate personas (Architect, Designer, Programmer), implement Designer-Coder workflow, enable constraint-based design. This completes the unique Polly Code vision.

**Duration**: 5-6 weeks (25-30 working days)

---

#### Week 1-2: Persona Coordination

**Days 1-5: Persona System Setup**

Tasks:
- Connect to Phase 24 (Orchestrator Mode) API
- Implement persona coordinator
- Add persona selector UI
- Route queries to appropriate personas
- Handle multi-persona responses

Files to create:
```
src/renderer/services/personas/
├── PersonaCoordinator.ts
└── PersonaRouter.ts

src/renderer/components/chat/
└── PersonaSelector.tsx
```

Deliverable: Can switch between personas

**Days 6-10: Architect Persona Integration**

Tasks:
- Implement Architect-specific query handling
- Retrieve architectural decisions from RAG (Glyphs domain)
- Generate structural guidance
- Reference past architectural patterns

Files to create:
```
src/main/services/personas/
├── ArchitectService.ts
└── ArchitectPrompts.ts
```

Deliverable: Architect persona provides structural guidance

---

#### Week 3: Designer Persona

**Days 11-15: Designer Constraint Mode**

Tasks:
- Implement constraint definition UI
- Design spec storage (JSON format)
- Connect to Phase 27 (Designer Persona)
- Extract design tokens from existing code
- Version design specs

Files to create:
```
src/renderer/components/designer/
├── ConstraintEditor.tsx
├── DesignSpecView.tsx
└── TokenExtractor.tsx

src/main/services/designer/
├── DesignSpecService.ts
└── DesignSpecStorage.ts (store specs)
```

Deliverable: Can define design constraints

---

#### Week 4: Designer-Programmer Bridge

**Days 16-20: Code Generation from Specs**

Tasks:
- Implement Designer-Programmer bridge
- Parse design specs and extract tokens
- Generate framework-specific code (React)
- Apply user's coding style (from profile)
- Add constraint enforcement

Files to create:
```
src/renderer/services/personas/
├── DesignerProgrammerBridge.ts
├── CodeGenerator.ts
└── ConstraintEnforcer.ts
```

Deliverable: Generate code from design specs

**Days 21-22: Constraint Violation Detection**

Tasks:
- Monitor code changes for constraint violations
- Show warnings when code drifts from spec
- Implement "Update Spec" workflow
- Track intentional deviations

Files to create:
```
src/renderer/services/designer/
└── ConstraintMonitor.ts

src/renderer/components/designer/
└── ConstraintViolationWarning.tsx
```

Deliverable: Warns when code violates design

---

#### Week 5: Profile Learning

**Days 23-27: Profile Integration**

Tasks:
- Connect to Phase 13b (User Profile System)
- Implement coding pattern extraction
- Analyze user's style (naming, formatting, patterns)
- Track suggestion acceptance/rejection
- Adapt suggestions based on profile

Files to create:
```
src/main/services/profile/
├── ProfileLearningService.ts
├── PatternExtractor.ts
└── StyleAnalyzer.ts

src/renderer/services/profile/
└── ProfileAdapter.ts (apply profile to suggestions)
```

Deliverable: Suggestions adapt to user's style

---

#### Week 6: Final Integration & Polish

**Days 28-30: End-to-End Testing**

Tasks:
- Test complete workflows (norns instrument, React component)
- Fix integration bugs
- Optimize performance
- Add missing error handling
- Write user documentation

Files to create:
```
docs/
├── user-guide.md
├── keyboard-shortcuts.md
└── troubleshooting.md
```

Deliverable: Polly Code fully functional

---

#### Phase 17d Milestones

| Day | Milestone | Success Criteria |
|-----|-----------|------------------|
| 5 | Personas working | Can switch personas |
| 10 | Architect integrated | Gets structural guidance |
| 15 | Designer constraints | Can define design rules |
| 20 | Code generation | Design → code working |
| 22 | Constraint enforcement | Warns on violations |
| 27 | Profile learning | Suggestions adapt |
| 30 | **Phase 17d DONE** | Polly Code complete |

---


### Section 28: Timeline & Resources

This section summarizes the overall timeline, resource requirements, and cost estimates for building Polly Code.

#### Overall Timeline

```
Phase 17a: Monaco Foundation         ████████░░░░░░░░░░░░░░░░░░  2-3 weeks
Phase 17b: Language Intelligence     ░░░░░░░░████████████░░░░░░  3-4 weeks
Phase 17c: RAG & Polly Integration   ░░░░░░░░░░░░░░░░████████░░  4-5 weeks
Phase 17d: Designer-Coder Integration ░░░░░░░░░░░░░░░░░░░░████  5-6 weeks
────────────────────────────────────────────────────────────────
Total:                                                           14-18 weeks
```

**Estimated Duration**: 14-18 weeks (3.5-4.5 months)

**Variance Factors**:
- SuperCollider LSP complexity (Week 2 of 17b)
- RAG performance optimization (Week 5 of 17c)
- Integration debugging (Week 6 of 17d)

---

#### Resource Requirements

**Human Resources**:
- **1 Full-Time Developer** (you): All development work
- **Optional**: Part-time designer for UI/UX polish (Week 6 of 17d)

**Hardware**:
- Development machine: MacBook Pro or equivalent (16GB+ RAM recommended)
- Test devices: norns (for SuperCollider testing)

**Software/Services**:
- **Electron**: Free, MIT licensed
- **Monaco Editor**: Free, MIT licensed
- **ChromaDB**: Free, open-source
- **OpenAI API**: ~$20-50/month for embeddings (development)
- **LSP Servers**: All free, open-source
- **GitHub**: For version control (free tier sufficient)

**Estimated Costs**:
```
OpenAI API (development):  $20-50/month × 4 months  = $80-200
LSP servers:               Free
ChromaDB:                  Free (self-hosted)
Tools/IDE:                 Free (VSCode, etc.)
──────────────────────────────────────────────────────
Total Cost:                                            ~$200
```

**Opportunity Cost**:
- 14-18 weeks @ ~30 hours/week = 420-540 hours
- At $100/hour freelance rate = $42,000-54,000 (if you were billing)
- This is the **real cost** (your time)

---

#### Development Environment Setup

**Prerequisites**:
```bash
# Node.js 20+
node --version  # v20.0.0+

# pnpm (faster than npm)
npm install -g pnpm

# ChromaDB (Docker)
docker pull chromadb/chroma

# LSP servers
npm install -g typescript-language-server
pip install python-lsp-server
brew install rust-analyzer gopls clangd
```

**Initial Setup** (Day 1):
```bash
# Clone/create repo
mkdir polly-code && cd polly-code
git init

# Initialize project
pnpm init
pnpm add electron react react-dom monaco-editor styled-components
pnpm add -D @types/react @types/react-dom typescript vite

# Start ChromaDB
docker run -p 8000:8000 chromadb/chroma

# Run dev server
pnpm dev
```

**Estimated Setup Time**: 2-3 hours

---

### Section 29: Dependencies

Polly Code depends on several existing Polly phases and external systems. This section maps all dependencies and integration points.

#### Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         POLLY CODE                              │
│                        (Phase 17a/b/c/d)                        │
└────────┬────────────┬───────────────┬──────────────────┬────────┘
         │            │               │                  │
         ▼            ▼               ▼                  ▼
┌────────────┐ ┌──────────┐ ┌─────────────────┐ ┌──────────────┐
│ Phase 13b  │ │ Phase 24 │ │   Phase 27      │ │ Epub Vectors │
│ User       │ │ Orch.    │ │   Designer      │ │ System       │
│ Profile    │ │ Mode     │ │   Persona       │ │ (RAG)        │
└────────────┘ └──────────┘ └─────────────────┘ └──────────────┘
     ▲              ▲               ▲                   ▲
     │              │               │                   │
  Profile API   Persona API    Design API         Vector DB
```

---

#### Phase 13b: User Profile System

**Integration Point**: Profile Learning Service

**Required APIs**:
- `GET /api/profile/:userId` - Fetch user's coding profile
- `PUT /api/profile/:userId` - Update profile with new patterns
- `GET /api/profile/:userId/patterns` - Retrieve coding patterns
- `PUT /api/profile/:userId/preferences` - Update preferences

**Data Flow**:
1. Polly Code observes user edits
2. Profile Learning Service extracts patterns
3. Sends patterns to Phase 13b API
4. Phase 13b stores in profile database
5. Future suggestions use updated profile

**Fallback**: If Phase 13b not available, profile learning runs locally (no persistence).

**Implementation Priority**: Medium (Phase 17d, Week 5)

---

#### Phase 24: Orchestrator Mode

**Integration Point**: Persona Coordinator

**Required APIs**:
- `POST /api/orchestrator/route` - Route query to appropriate persona(s)
- `GET /api/orchestrator/personas` - List available personas
- `POST /api/orchestrator/query` - Query specific persona with context

**Data Flow**:
1. User asks question in Chat
2. Persona Coordinator calls Orchestrator API
3. Orchestrator routes to Architect/Designer/Programmer
4. Personas respond with coordinated answers
5. Responses displayed in Chat panel

**Fallback**: If Phase 24 not available, use single "Programmer" persona (no coordination).

**Implementation Priority**: High (Phase 17d, Week 1)

---

#### Phase 27: Designer Persona

**Integration Point**: Designer-Programmer Bridge

**Required APIs**:
- `POST /api/designer/spec` - Create design spec
- `GET /api/designer/spec/:id` - Retrieve design spec
- `PUT /api/designer/spec/:id` - Update design spec
- `POST /api/designer/tokens/extract` - Extract design tokens from code
- `POST /api/designer/validate` - Validate code against spec

**Data Flow**:
1. User defines constraints in Designer mode
2. Spec stored via Phase 27 API
3. User requests code generation
4. Designer-Programmer Bridge retrieves spec
5. Generates code matching constraints

**Fallback**: If Phase 27 not available, store design specs locally (JSON files).

**Implementation Priority**: High (Phase 17d, Week 3)

---

#### Epub Vector System

**Integration Point**: RAG Service

**Required APIs/Access**:
- ChromaDB collections: `polly_scrolls` (epub documents)
- Embedding service (OpenAI or local)
- Document indexer (watches epub files)

**Data Flow**:
1. User adds epub/markdown docs to workspace
2. Indexing Service chunks and embeds documents
3. Vectors stored in ChromaDB `polly_scrolls` collection
4. RAG retrieves relevant docs when coding

**Fallback**: If epub vectors not available, only code and local docs indexed.

**Implementation Priority**: Medium (Phase 17c, Week 4)

---

#### External Dependencies

**LSP Servers** (critical):
- typescript-language-server (TypeScript/JavaScript)
- pylsp (Python)
- rust-analyzer (Rust)
- gopls (Go)
- clangd (C/C++)
- **sclang-lsp** (SuperCollider - custom, build in Phase 17b)

**Mitigation**: Package recommended LSP servers with Polly Code installer.

---

**OpenAI API** (critical for embeddings):
- Used for generating embeddings in RAG pipeline
- Required for vector search

**Mitigation**: 
- Option 1: User provides their own API key
- Option 2: Fall back to local embedding model (sentence-transformers)
- Option 3: Polly provides shared API key (rate-limited)

---

**ChromaDB** (critical for RAG):
- Local vector database
- Runs as Docker container or standalone

**Mitigation**: Bundle ChromaDB standalone binary with Polly Code (no Docker required).

---

#### Dependency Risk Assessment

| Dependency | Risk Level | Impact if Unavailable | Mitigation |
|------------|-----------|----------------------|------------|
| Phase 13b | Low | No profile learning | Local profile storage |
| Phase 24 | Medium | No multi-persona | Single persona mode |
| Phase 27 | Medium | No design specs | Local spec storage |
| Epub vectors | Low | Less context | Code-only indexing |
| LSP servers | High | No language intelligence | Bundle with installer |
| OpenAI API | Medium | No embeddings | Local model fallback |
| ChromaDB | High | No RAG | Bundle standalone |

**Overall Risk**: Medium-Low (good fallback strategies for all dependencies)

---

### Section 30: Risk Assessment

This section identifies potential risks and mitigation strategies for building Polly Code.

#### Technical Risks

**Risk 1: Monaco Performance with Large Files**

**Description**: Monaco editor can slow down with files >10,000 lines

**Likelihood**: Medium
**Impact**: High (poor user experience)

**Mitigation**:
- Use Monaco's diff editor mode for large files (render only visible lines)
- Implement file size warnings (>5,000 lines)
- Optimize syntax highlighting (tree-sitter incremental parsing)
- Add "Load Full File" button for large files (lazy loading)

**Contingency**: Implement virtual scrolling for Monaco models

---

**Risk 2: LSP Server Crashes**

**Description**: Language servers may crash or hang, breaking IDE functionality

**Likelihood**: Medium
**Impact**: High (blocking work)

**Mitigation**:
- Implement automatic LSP restart on crash
- Add health check pings (30-second interval)
- Provide manual "Restart LSP Server" command
- Log crashes for debugging

**Contingency**: Graceful degradation (editor still works, just no completion)

---

**Risk 3: RAG Performance with Large Codebases**

**Description**: Vector search may be slow with 10,000+ code chunks

**Likelihood**: Medium
**Impact**: Medium (annoying latency)

**Mitigation**:
- Implement aggressive caching (cache searches for 5 minutes)
- Use approximate nearest neighbor search (faster than exact)
- Limit search to active project (not all indexed code)
- Show partial results while searching

**Contingency**: Make RAG opt-in (disable if too slow)

---

**Risk 4: SuperCollider LSP Complexity**

**Description**: Building a custom LSP for SuperCollider may take longer than estimated

**Likelihood**: High
**Impact**: Medium (delays Phase 17b)

**Mitigation**:
- Start with minimal LSP (completion only, no diagnostics)
- Reuse existing SC parser libraries (scsynth)
- Scope creep: defer advanced features to later
- Allocate extra buffer time (4 weeks instead of 2)

**Contingency**: Ship without SC LSP initially (add in Phase 17b.1)

---

**Risk 5: Embedding Cost Explosion**

**Description**: OpenAI embedding costs may be higher than expected with frequent re-indexing

**Likelihood**: Low
**Impact**: Low (cost)

**Mitigation**:
- Implement smart caching (only embed changed chunks)
- Batch embedding requests (cheaper)
- Rate limit re-indexing (max once per 5 minutes)
- Provide local model option (free but slower)

**Contingency**: Switch to sentence-transformers (local, free)

---

#### Product Risks

**Risk 6: User Adoption**

**Description**: Developers may not switch from Cursor/VSCode due to habit

**Likelihood**: High
**Impact**: High (low usage)

**Mitigation**:
- Target niche audiences first (audio developers, polymaths)
- Provide VSCode import tool (migrate settings/extensions)
- Offer free trial period (no commitment)
- Build community (Discord, showcase norns projects)

**Contingency**: Position as "VSCode companion" rather than replacement

---

**Risk 7: RAG Context Quality**

**Description**: RAG may retrieve irrelevant context, confusing users

**Likelihood**: Medium
**Impact**: Medium (annoying suggestions)

**Mitigation**:
- Implement feedback loop (learn from rejections)
- Show relevance scores (let users judge)
- Allow manual context selection (power user mode)
- Start conservative (only show high-confidence results)

**Contingency**: Make RAG suggestions opt-in (manual trigger)

---

#### Timeline Risks

**Risk 8: Scope Creep**

**Description**: Adding "just one more feature" delays launch

**Likelihood**: High
**Impact**: High (delays)

**Mitigation**:
- Define strict MVP scope (no features beyond 17a/b/c/d)
- Maintain "Phase 18" backlog for future features
- Weekly scope review (cut if behind schedule)

**Contingency**: Ship Phase 17a-c only (defer 17d to v1.1)

---

**Risk 9: Integration Delays**

**Description**: Integrating with Phase 13b/24/27 may take longer than expected

**Likelihood**: Medium
**Impact**: Medium (delays Phase 17d)

**Mitigation**:
- Implement local fallbacks (no dependencies on other phases)
- Test integration early (Week 1 of Phase 17d)
- Maintain API contracts (mock APIs for testing)

**Contingency**: Ship with local storage (add phase integrations in v1.1)

---

#### Mitigation Summary

**Overall Strategy**:
1. **Build incrementally**: Each phase (17a/b/c/d) is independently usable
2. **Provide fallbacks**: Core features work without external dependencies
3. **Defer, don't cut**: Move risky features to later phases (not abandoned)
4. **User feedback**: Beta test after Phase 17c (validate approach)

**Success Probability**: 75-85% (high confidence in timeline if scope controlled)

---

## PART 5 COMPLETE

Part 5 (Implementation Roadmap) is now complete. We've covered:
- ✅ Section 24: Phase 17a - Monaco Foundation (2-3 weeks)
- ✅ Section 25: Phase 17b - Language Intelligence (3-4 weeks)
- ✅ Section 26: Phase 17c - RAG & Polly Integration (4-5 weeks)
- ✅ Section 27: Phase 17d - Designer-Coder Integration (5-6 weeks)
- ✅ Section 28: Timeline & Resources (14-18 weeks total, ~$200 cost)
- ✅ Section 29: Dependencies (Phase 13b, 24, 27, epub vectors)
- ✅ Section 30: Risk Assessment (Technical, product, timeline risks)

**Current page count**: ~55-58 pages

**Remaining**: Part 6 (Future Vision) - ~5-8 pages

---


---

## PART 6: FUTURE VISION

This final section explores what Polly Code could become beyond the MVP—longer-term capabilities, ecosystem opportunities, and the ultimate vision.

---

### Section 31: Beyond MVP (Year 2-3)

Once Phases 17a-d are complete, here are natural next steps to expand Polly Code's capabilities.

#### Phase 18: Collaborative Coding

**Concept**: Real-time collaboration with other developers or Polly personas

**Features**:
- **Live sharing**: Share editor session with other developers (like VSCode Live Share)
- **Persona collaboration**: Work alongside Architect/Designer personas in real-time
  - Example: Architect suggests structure, you implement, Designer reviews UI
- **Async code review**: Personas can review PRs and suggest improvements
- **Pair programming mode**: Split screen with persona-driven TDD

**Technical Approach**:
- WebRTC for peer-to-peer connection
- CRDTs for conflict-free editing
- Persona sessions run in separate processes

**Timeline**: 6-8 weeks after MVP

---

#### Phase 19: Visual Programming Interface

**Concept**: Drag-and-drop interface for non-coders to build with Polly

**Features**:
- **Node-based editor**: Connect blocks (like Max/MSP, but for code)
- **Design tokens as nodes**: Visual manipulation of design system
- **Audio graph builder**: Visual SuperCollider patching
- **Code generation**: Nodes compile to real code (not abstraction layer)

**Use Cases**:
- Musicians building norns instruments without Lua knowledge
- Designers creating React components visually
- Educators teaching programming concepts

**Technical Approach**:
- React Flow for node editor
- Code generation from graph structure
- Round-trip editing (visual ↔ code)

**Timeline**: 8-12 weeks after MVP

---

#### Phase 20: AI-Driven Refactoring

**Concept**: Intelligent code refactoring using institutional memory

**Features**:
- **Pattern-based refactoring**: "Apply the pattern from my last refactor"
- **Architecture-aware**: Suggests refactors that match your design philosophy
- **Safe refactoring**: Detects breaking changes before applying
- **Learning refactors**: Profile learns your refactoring preferences

**Examples**:
- "Extract this into a service, like you did for MetricsService"
- "Apply your functional composition pattern to this code"
- "Refactor to match your naming conventions"

**Technical Approach**:
- AST-based refactoring (Babel, TypeScript compiler)
- RAG retrieves past refactor patterns
- Persona coordination (Architect validates safety)

**Timeline**: 4-6 weeks after MVP

---

#### Phase 21: Multi-Project Intelligence

**Concept**: Learn from all your projects, not just the current one

**Features**:
- **Cross-project RAG**: Search vectors from all past projects
- **Pattern library**: Build personal library of reusable patterns
- **Architecture templates**: Generate new projects from your past structures
- **Consistency enforcement**: "This doesn't match your usual pattern"

**Use Cases**:
- Starting a new norns project: "Use my wrms project as template"
- Consistent error handling across projects
- Reuse authentication patterns from past web apps

**Technical Approach**:
- Unified ChromaDB across projects
- Project tagging/categorization
- Similarity search across project boundaries

**Timeline**: 3-4 weeks after MVP

---

#### Phase 22: Voice Coding

**Concept**: Code by speaking (accessibility + hands-free)

**Features**:
- **Voice commands**: "Create a function called calculateGrainDensity"
- **Natural language**: "Add error handling to this function"
- **Persona voice**: Ask questions by voice, get spoken responses
- **Dictation mode**: Speak code, AI writes it

**Use Cases**:
- Accessibility for motor impairments
- Thinking out loud while coding
- Hands-free coding (standing desk, whiteboard sessions)

**Technical Approach**:
- Whisper API for speech-to-text
- LLM interprets intent
- TTS for persona responses

**Timeline**: 4-5 weeks after MVP

---

### Section 32: Plugin Ecosystem

Polly Code should be extensible by the community. Here's a vision for a plugin system.

#### Plugin Architecture

**Concept**: Allow third-party developers to extend Polly Code

**Plugin Types**:
1. **Language Support**: Add new language LSP servers
2. **Persona Extensions**: Create custom personas (e.g., "Security Auditor")
3. **RAG Domains**: Add custom knowledge domains (e.g., "Hardware domain" for embedded dev)
4. **UI Themes**: Custom color schemes and layouts
5. **Workflow Plugins**: Automate common tasks (e.g., "Deploy to norns")

**Plugin API**:
```typescript
// Example: Custom persona plugin
export default {
  name: 'security-auditor',
  type: 'persona',
  
  async onQuery(query: string, context: EditorContext) {
    // Analyze code for security issues
    const vulnerabilities = await analyzeCode(context.code);
    return {
      content: `Found ${vulnerabilities.length} potential issues...`,
      suggestions: vulnerabilities.map(v => v.fix)
    };
  },
  
  async onCodeChange(code: string) {
    // Real-time security linting
  }
};
```

**Distribution**:
- Plugin registry (like npm)
- In-app plugin browser
- Community ratings/reviews

**Monetization**:
- Free plugins (open-source)
- Paid plugins (developer revenue share)
- Premium Polly plugins (official, supported)

---

#### Example Community Plugins

**1. norns Workflow Plugin**

Features:
- One-click deploy to norns
- Real-time code sync (save in editor → updates on norns)
- Maiden console integration
- Parameter visualization

**2. Tone.js Integration Plugin**

Features:
- Tone.js snippets and templates
- Audio graph visualizer
- Live coding environment (hear changes instantly)

**3. Design System Plugin**

Features:
- Import Figma design tokens
- Keep Figma and code in sync
- Component library browser

**4. ML Code Plugin**

Features:
- TensorFlow/PyTorch snippets
- Model architecture visualizer
- Training metrics dashboard

---

### Section 33: Research Questions

These are open questions that would benefit from experimentation and user research.

#### Research Question 1: Optimal RAG Retrieval Strategy

**Question**: How many RAG results should we show, and how should they be ranked?

**Hypothesis**: 3-5 results, ranked by domain relevance + recency + similarity

**Experiment**:
- A/B test: 3 results vs. 5 results vs. 10 results
- Measure: acceptance rate, dismissal rate, time to decision
- Learn: optimal result count and ranking weights

---

#### Research Question 2: Persona Voice and Tone

**Question**: Should personas have distinct "voices" (formal, casual, technical)?

**Hypothesis**: Yes—Architect is formal, Designer is visual, Programmer is technical

**Experiment**:
- User testing with different persona tones
- Measure: user preference, comprehension, trust

---

#### Research Question 3: Profile Learning Timeframe

**Question**: How long before profile learning becomes accurate?

**Hypothesis**: 2-3 weeks of daily use

**Experiment**:
- Track profile accuracy over time
- Measure: suggestion acceptance rate, edit distance
- Learn: when to start showing profile-influenced suggestions

---

#### Research Question 4: Context Panel Placement

**Question**: Where should RAG results appear? (Right panel, bottom panel, inline hover)

**Hypothesis**: Right panel for exploration, inline hover for quick reference

**Experiment**:
- A/B test different placements
- Measure: usage frequency, dismissal rate, user preference

---

#### Research Question 5: Cross-Domain Weighting

**Question**: How should we weight different domains when ranking RAG results?

**Hypothesis**: Current domain = 1.0x, adjacent domains = 0.6x, distant domains = 0.3x

**Experiment**:
- Collect user feedback on result relevance
- Adjust weights based on acceptance patterns
- Learn: optimal domain weighting per user

---

### Section 34: Long-Term Market Position

Looking 3-5 years out, where does Polly Code fit in the market?

#### Market Positioning: "Context That Thinks Like You Do"

**Target Market** (Year 3):
- **Primary**: Polymathic developers (creative coders, audio programmers, systems thinkers)
- **Secondary**: Solo developers building niche tools
- **Tertiary**: Small teams (2-5 people) with shared knowledge base

**Market Size**:
- Polymathic developers: ~50,000 globally (est.)
- Audio developers: ~10,000 (SuperCollider, Max/MSP, norns)
- Creative coders: ~100,000 (p5.js, Processing, openFrameworks)
- **Total addressable**: ~150,000 developers

**Pricing Strategy**:
- **Free tier**: Monaco editor + LSP (basic IDE functionality)
- **Pro tier**: RAG + personas + profile learning ($15/month or $150/year)
- **Lifetime license**: $500 (ownership model)

**Revenue Projections** (Year 3, conservative):
- 1,000 Pro monthly subscribers: $15,000/month = $180,000/year
- 500 Lifetime licenses: $250,000 (one-time)
- Plugin revenue share: $20,000/year
- **Total**: ~$450,000/year

This is **sustainable** for a solo developer or small team.

---

#### Competitive Moat

**What prevents competitors from copying Polly Code?**

1. **Institutional memory**: Years of indexed epub vectors and personal knowledge
2. **Profile learning**: Deep understanding of individual coding style
3. **Niche language support**: SuperCollider LSP, norns workflow
4. **Ownership model**: One-time purchase vs. subscription fatigue
5. **Community**: norns/audio dev community built around Polly

**Cursor/Copilot can't copy**:
- They're cloud-dependent (can't do edge-native)
- They're subscription-locked (can't offer lifetime licenses)
- They're mainstream-focused (won't support niche languages)

**Polly's sustainable advantage**: Serving underserved niches with ownership model.

---

#### Year 5 Vision

By Year 5, Polly Code could become:

**"The IDE for polymaths"**

Characteristics:
- **Polyglot**: Supports 20+ languages (mainstream + niche)
- **Cross-domain**: Indexes code, audio, visuals, writing, hardware
- **Personal**: Deep profile learning (knows your style better than you do)
- **Collaborative**: Real-time pairing with personas
- **Extensible**: 100+ community plugins
- **Sustainable**: 5,000+ paying users, $1M+ ARR

**Cultural Impact**:
- norns instruments cite "Built with Polly Code" (like "Powered by WordPress")
- Audio programming tutorials assume Polly Code (like web dev assumes VSCode)
- "Polly-style coding" becomes a recognized approach (context-driven, persona-assisted)

**Ultimate Goal**: Not to replace VSCode/Cursor, but to be the **best tool for polymathic developers who think across domains**.

---

## DOCUMENT COMPLETE

---

## Summary

This vision document has outlined a comprehensive plan to build **Polly Code**, an AI-native code editor differentiated by:

1. **Context beyond code**: RAG retrieval across five domains (Sigils, Signals, Scrolls, Sights, Glyphs)
2. **Designer-Coder integration**: Living specs, constraint-based design, automatic code generation
3. **Edge-native advantages**: Privacy, speed, offline capability, ownership model
4. **Polymathic workflows**: Supports niche languages (SuperCollider), creative coding, systems thinking

**Implementation**: 14-18 weeks across four phases (17a/b/c/d)
- Phase 17a: Monaco Foundation (2-3 weeks)
- Phase 17b: Language Intelligence (3-4 weeks)
- Phase 17c: RAG & Polly Integration (4-5 weeks)
- Phase 17d: Designer-Coder Integration (5-6 weeks)

**Key Differentiators vs. Cursor/Copilot/Windsurf**:
- Only IDE that treats documentation and design philosophy as equal to code
- Only IDE with first-class SuperCollider support
- Only IDE with Designer-Coder bridge (design tokens → code)
- Only IDE with ownership model (no subscription lock-in)
- Only IDE with profile learning that adapts to individual style

**Market Position**: "Context that thinks like you do" — serving polymathic developers, audio programmers, and creative coders underserved by mainstream tools.

**Success Criteria**: 
- MVP ships in 4-5 months
- 100+ early adopters from norns/audio community (6 months)
- 1,000+ Pro users by Year 3
- Self-sustainable revenue by Year 2

This is not just an IDE—it's **your AI development partner that understands your entire creative practice, not just your code**.

---

**Document Status**: COMPLETE
**Pages**: ~60 pages
**Word Count**: ~18,000 words
**Completion Date**: 2026-02-04

---

**Next Steps**:
1. Review this vision document
2. Validate technical approach with proof-of-concept (Monaco + LSP)
3. Begin Phase 17a implementation
4. Establish feedback loop with norns community
5. Iterate based on real-world usage

---

