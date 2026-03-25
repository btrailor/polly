# Polly Influence Guide: Liz's Agentic SDLC + Monome/Lines Philosophy

> This document provides two interlocking influence layers for Polly: **operational methodology** (from Liz's Agentic SDLC) and **aesthetic-philosophical foundation** (from Monome/Lines). Where Liz uses Solarpunk as her meta-frame, Polly uses Monome/Lines.

See `MONOME_LAYER.md` for the full treatment of Part 1. This document focuses on Part 2 (Agentic SDLC patterns) and the integration synthesis.

---

## Part 2: The Agentic SDLC Layer (Polly's Operational Methodology)

### What to Adopt from Liz's Framework

Liz's Agentic SDLC course teaches developers to manage teams of AI agents building software. The framework is production-tested (4,600+ commits in 23 days). Many of its patterns map directly to Polly's architecture — but Polly is a *knowledge system*, not just a software factory. Adapt accordingly.

---

### 1. Conversation-First Planning → Polly's Interaction Model

Liz's Phase 1 is "The Brain Dump Conversation" — start by talking with the AI, explore the idea through dialogue, *then* formalize into specs.

**→ For Polly:** Every interaction begins as conversation. The persona system should detect when conversation is crystallizing into something more structured (a note, a curriculum topic, a knowledge graph entity) and offer to capture it — but never force the transition. The Scribe persona's capture mode should feel like the natural next step after a good conversation, not like a separate tool.

**Implementation note:** Liz's OpenSpec workflow (`brain dump → proposal.md → tasks.md → status.json`) maps to Polly's existing OpenSpec change workflow. When Polly itself is being developed, use the same conversation-first → formalize pattern.

---

### 2. The CTO Mindset → Your Relationship to Polly

Liz's central metaphor: "You are the CTO now. Fire yourself from the developer job."

| Level | Description |
|-------|-------------|
| 0 | You do everything manually |
| 1 | AI helps you |
| 2 | AI does it, you review |
| 3 | Multiple agents work in parallel |
| 4 | Agents work autonomously |
| 5 | Agents evolve themselves |
| 6 | Self-improving agent team |

**→ For Polly development:** Your role should evolve from building Polly to *directing* Polly. The persona-to-workflow transition is exactly this move — replacing hard-coded persona classes with workflow templates that agents can execute. Track where you are on this maturity scale for each of Polly's subsystems.

**→ For Polly usage:** Map progressive feature disclosure (Phase 18) explicitly to these levels: user starts by chatting → uses personas → runs workflows → composes their own workflows. The `user_journey` module tracks this progression.

---

### 3. The 5-Layer Memory System → Polly's Memory Architecture

Liz's memory hierarchy:

| Layer | Contents | Lifecycle |
|-------|----------|-----------|
| Core | Identity, non-negotiable rules, formative failures | Permanent |
| Long-term | Learned patterns, domain expertise, proven approaches | Persists across sessions, updated weekly |
| Medium-term | Current project context, recent decisions | Decays over days-weeks |
| Recent | Current session history, working context | Current session only |
| Compost | Failed approaches, abandoned ideas, things to avoid | Review weekly, extract lessons, discard |

**→ For Polly — two critical refinements:**

**Core memories as identity anchors.** Liz's "embarrassment drives behavior change" pattern maps to Polly's constitutional layer. The constitutional principles aren't just rules; they should feel like hard-won lessons. The "Citation Crisis" story is a perfect Polly pattern: Cynthia (research agent) fabricated citations, got caught, now triple-checks everything. Polly's DualValidator and RetrievalClassifier serve this function — they're the scar tissue from times when unvalidated information caused problems.

**Compost as active resource.** Failed approaches aren't garbage — they're compost. Polly's knowledge graph should have an explicit lifecycle state for "tried this, didn't work, here's why." The PARA + Maturity Lifecycle (Phase 31) should include a "compost" stage. Pattern learning should track negative patterns as actively as positive ones.

**REM Sleep consolidation:** Liz's weekly consolidation (500 recent learnings → 50 patterns → 10 insights) maps to Polly's existing compression system. Make this a *scheduled* operation, not just on-demand. The SessionExtractor already does end-of-session extraction; add periodic cross-session consolidation.

---

### 4. Anti-Pattern Detection → Polly's Quality Pipeline

Liz's Workshop 5: "AI agents develop habits. Some are good. Some are terrible." The solution is TDD for agent behavior.

The improvement loop: **Find Pattern → Defeat with Test → Teach Discipline → Repeat**

**→ For Polly:** This directly informs the Knowledge Quality Pipeline (Phase 12b-ext). Patterns in Polly aren't just code patterns — they're thinking patterns. When Polly's retrieval classifier consistently marks certain queries as ABSENT, that's a signal: the knowledge base has a gap. When entity extraction keeps finding the same entity type in certain domains, that's a signal: reinforce it.

**Specific implementation:** Add "defeat tests" to the hardened pipeline. When a new failure mode is discovered (e.g., DualValidator catches a provenance issue), create a test case that exercises that failure. Run these tests periodically. This turns quality maintenance from reactive to proactive.

---

### 5. The Probabilistic Mindset → Polly's Epistemological Posture

Liz's shift: from "this code is correct" to "this code passes all tests." Software is probabilistic, not deterministic.

**→ For Polly:** Polly should never say "I know X" — it should express confidence shaped by the retrieval classifier:
- DIRECT retrieval with high provenance trust → high confidence
- ADJACENT retrieval → qualified confidence
- ABSENT retrieval → honest uncertainty

**Six Sigma for knowledge quality:** Track defect rates through the pipeline. What percentage of retrieved content gets classified as ADJACENT when it should be DIRECT? What percentage of entities get extracted correctly on first pass? Drive these down systematically.

| Quality Stage | Defect Rate | Review Mode |
|---------------|-------------|-------------|
| Alpha | ~30% | Heavy human review |
| Beta | ~10% | Automated review |
| Production | ~1% | Automated detection |
| Mature | ~0.1% | Continuous improvement |

---

### 6. Agent Character Sheets → Persona Definitions

Liz gives each agent: name, personality, core memories (including formative failures), responsibilities, tools, coordination interfaces. Agents have version history: v1.0 → v1.1 (after the N+1 query incident) → v1.2 (after the API versioning disaster).

**→ For Polly:** Each persona should have:

- **Core memories:** What formative experiences shaped this persona? The Scribe should remember why wiki-linking matters (unlinked knowledge is invisible knowledge). The Professor should remember why Socratic method beats lecturing.
- **Version history:** Track when persona prompts change and why. Use versioning (v1.0, v1.1) with explicit breaking changes documented.
- **Failure modes:** What does this persona get wrong? The Architect over-plans. The Scribe over-captures. The Professor lectures when it should question. Acknowledging failure modes makes them self-correcting.

---

### 7. File-Based Coordination + Coffee Talk → Polly's Inter-System Communication

Liz's agents coordinate through task files (JSON work queues) and "coffee talk" (shared markdown files where agents post updates and @ each other). Simple, human-readable, debuggable.

**→ For Polly:** For the OpenClaw migration, simplify toward Liz's model. Markdown-based inter-agent communication is more transparent than complex protocols. The coffee talk pattern is especially relevant for the persona-to-workflow transition: when the Scribe captures something during a Professor-led teaching session, that should feel like one agent posting a note for another, not like a complex orchestration event.

---

### 8. Token Conservation Mode → Polly's Budget Philosophy

Liz documents a real production pattern: when costs spike, activate conservation mode.

**→ For Polly (CRITICAL DIVERGENCE):** Liz is comfortable spending $100–800/month during active development. Polly should be *permanently* in a version of conservation mode. Not out of poverty but out of philosophy — the Monome principle of using what you need, knowing where it comes from, not wasting.

**Polly's token budget tiers:**

| Tier | Model | Use when |
|------|-------|----------|
| Free | Ollama / llama3.2 | Session extraction, routine pattern matching, simple entity recognition |
| Lightweight | Claude Haiku | Note enrichment, query classification, simple curriculum generation |
| Standard | Claude Sonnet | Query decomposition, knowledge graph intelligence, cross-domain synthesis |
| Deep | Claude Opus | Constitutional analysis, complex multi-source synthesis, novel problem decomposition |

Every cloud call should pass through the budget allocator. Track cost per domain. Identify expensive patterns and find cheaper alternatives. This is not austerity — it's the design philosophy of a system that respects its resources.

---

### 9. The Diarrhea Phase → Managing Polly Development Scope

Liz's warning: sudden AI capability creates manic energy. "You have years of backlogged projects. Suddenly you can build them. All at once. Right now." She recommends financial guardrails, time boundaries, and the mantra: **"Capture ideas, don't execute them. Add it to the roadmap."**

**→ For Polly development:** The SALVAGE_AUDIT.md, the 35+ OpenSpec specs, the five tiers of roadmap phases — this is a system that has been through the diarrhea phase. The monome principle applies: do less, better. When a new idea strikes, it goes into the backlog with a value analysis attached.

**→ For Polly as a tool:** When the user is in creative overflow (many rapid-fire questions, escalating scope, "one more thing" patterns), Polly should gently surface the roadmap. The Architect persona's plan mode is designed for this: channel creative energy into structure without killing it.

---

### 10. Behavior Testing for Prompt Changes → Persona Regression Testing

Liz's insight: when you change an agent's prompt, its personality can drift. The solution is behavior tests — regression tests for personality.

**→ For Polly:** Every persona prompt change should be validated against a behavior test suite. Define expected responses to canonical queries:

- Does the Professor still use Socratic questioning by default?
- Does the Scribe still produce wiki-linked markdown?
- Does the Architect still ask clarifying questions before planning?
- Does the constitutional layer still flag scapegoat reasoning?

These aren't unit tests — they're personality regression tests. Run them whenever persona definitions change.

---

## Part 3: Integration — Where Monome/Lines and Agentic SDLC Meet

### The Synthesis

Liz provides the **machinery** — how to run agent teams, manage memory, defeat anti-patterns, scale operations. Monome/Lines provides the **soul** — why you're building, what values guide the building, what aesthetic the system embodies.

| Dimension | Liz's Contribution | Monome/Lines Contribution | Polly Synthesis |
|-----------|-------------------|---------------------------|-----------------|
| Architecture | Multi-agent orchestration, task queues | Decoupled systems, minimalist interfaces | Workflow templates that compose like norns scripts |
| Memory | 5-layer hierarchy, REM sleep, compost | Studies as living knowledge | Knowledge base as living instrument — maintained, not just accumulated |
| Quality | TDD for agents, defeat tests, Six Sigma | Repairability, long-term support | Knowledge quality pipeline as ongoing maintenance practice |
| Learning | Maturity model (Level 0→6) | Studies not tutorials, open-ended exploration | Professor problem-poses; curriculum tracks application not recitation |
| Economics | Budget tracking, conservation mode | Local materials, small-batch, no waste | Local-first LLM routing, cloud as conscious choice |
| Identity | Character sheets, core memories, version history | "Does nothing by default," meaning from use | Personas define *how* to approach, not *what* to conclude |
| Community | Coffee talk, agent-to-agent communication | Infrastructure + tone = community | User's knowledge practice as the community; Polly as infrastructure |
| Ethics | "Let mistakes happen, then systematize fixes" | Open source as mutual benefit | Constitutional epistemology: observe, question, enrich |

---

### Priority Actions for OpenClaw Spec

**Immediate** (feeds directly into SOUL.md / AGENTS.md):
- Rewrite constitutional layer as SOUL.md with Monome-inflected voice: warm, quiet, honest about uncertainty
- Translate persona definitions to AGENTS.md files with Liz-style character sheets: core memories, version history, failure modes
- Add Monome vocabulary to design spec: "studies not tutorials," "by default does nothing," "infrastructure and tone"
- Define Polly's token budget philosophy explicitly: local default, cloud as conscious choice, Opus as rare investment

**Near-term** (architectural patterns from Liz):
- Implement 5-layer memory with explicit compost tier in scalable memory layers
- Add REM Sleep as scheduled consolidation operation (weekly, automatable)
- Design behavior test suite for persona regression testing
- Implement defeat-test pattern in hardened knowledge pipeline
- Simplify inter-system communication toward coffee-talk pattern (markdown-based, human-readable)

**Strategic** (long-term alignment):
- Map user journey to Liz's maturity model: chat → persona → workflow → compose-your-own
- Design knowledge base maintenance as repair practice
- Integrate "capture, don't execute" philosophy into Architect persona's plan mode
- Develop "studies" format for Professor persona's teaching mode

---

## Part 4: What NOT to Adopt

### From Liz — Where Polly Diverges

- **Cloud-heavy cost tolerance.** Liz's system uses Opus freely, runs continuous overnight workers, expects $100–800/month. Polly should be dramatically more conservative. This isn't limitation — it's Monome philosophy.
- **Speed-as-primary-value.** Liz celebrates velocity (318 commits in one day). Polly should not optimize for throughput. The constitutional layer means Polly should sometimes be slower than possible — taking time to validate, consider, flag uncertainty.
- **Solarpunk framing.** Liz's Solarpunk is explicitly post-singularity, anticapitalist. Polly's Monome/Lines frame is more understated: local, sustainable, open, minimal. Both are anti-extractive, but Polly's frame is quieter — more Catskills apple orchard than solar-punk commune.
- **The video game analogy.** Liz compares agents to video game characters you can spawn infinitely. Polly's personas are like instruments you reconfigure. You don't spawn five Professors — you reconfigure how the Professor approaches a topic. The monome grid doesn't clone; it reconfigures.

### From Monome — Where Polly Diverges

- **Product minimalism pushed to extremes.** Monome can ship a grid that "does nothing" because users are sophisticated musicians. Polly needs progressive disclosure because its users may not be technical. The philosophy is minimalist; the experience should be approachable.
- **Sparse documentation.** Monome's documentation is famously sparse and community-maintained. Polly should have excellent documentation — but in the "studies" spirit: explaining *why* and *how*, not just *what*.

---

## Appendix: Key Resources from Liz's Toolkit

| Resource | URL | Polly Relevance |
|----------|-----|-----------------|
| Production System Prompt Template | https://gist.github.com/lizTheDeveloper/035e2084c554702b3ac677ccdcee3156 | Study for persona prompt construction patterns |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | Already in use; continue as coordination backbone |
| Student Handbook | https://github.com/lizTheDeveloper/multiverse_student_handbook | Inform Professor persona, meta-pedagogy layer |
| Admin Handbook | https://github.com/lizTheDeveloper/multiverse-admin-handbook | Teaching neurodivergent adults |
| Solarpunk Automation Research | (80-page feasibility report) | Relevant to Polly's distributed/mesh vision (DRM Phase 1-6) |
| Multiverse Studios | https://multiversestudios.xyz/ | Production example of agentic SDLC |

---

## Quick Reference: Concept Mapping

| Liz Concept | Polly Equivalent | Notes |
|-------------|-----------------|-------|
| Brain Dump → OpenSpec | Conversation → Knowledge capture | Same pattern, different domain |
| Roy/Jen/Cynthia (named agents) | Architect/Professor/Scribe (personas) | Add character sheets, core memories, version history |
| Task files + Matrix | Nexus workflows + coffee talk | Simplify toward file-based coordination |
| Pre-commit hooks | Hardened pipeline validation | Automated enforcement |
| Senior Developer Checklist | Knowledge quality pipeline | Evolving checklist of quality rules |
| REM Sleep consolidation | Session extraction + cross-session compression | Add scheduled consolidation |
| Defeat tests | Knowledge base regression tests | When a quality issue is found, test for it permanently |
| Token Conservation Mode | Default operating mode | Polly runs conservative by philosophy, not emergency |
| Maturity Levels 0-6 | User journey progression | Map feature disclosure to maturity |
| Character Sheets | Persona YAML + core memories + version history | Richer persona definitions |
| Coffee Talk | Markdown-based inter-persona communication | Simple, human-readable, debuggable |
| The Diarrhea Phase | Architect plan mode, roadmap capture | Channel creative overflow into structure |
| Compost | Knowledge lifecycle: archive → compost → lessons | Failed approaches are learning resources |
| Behavior tests | Persona regression tests | Validate personality across prompt changes |
