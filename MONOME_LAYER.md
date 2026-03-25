# The Monome/Lines Layer
## Polly's Aesthetic-Philosophical Foundation

*This document is foundational. It is not a feature spec or a design guideline — it is the epistemological posture from which all Polly design decisions should be made. When in doubt about a direction, return here.*

---

## What This Is

Liz frames her agent ecosystem through Solarpunk: post-singularity, anticapitalist, decolonial. That's her vibe layer — the thing that makes her agent teams feel like something more than an engineering optimization.

Polly's vibe layer is **Monome/Lines**.

Not as a product to integrate (though you use monome hardware), but as a design philosophy, community ethic, and epistemological posture that should permeate every layer of how Polly thinks, builds, and relates.

---

## Seven Core Principles → Polly Design Axioms

### 1. "By default does nothing."

The monome grid ships with no hardwired functionality. Its meaning comes entirely from what software connects to it. This is the most radical design decision in electronic music hardware: the instrument is defined by the community, not the manufacturer.

**→ Polly axiom: Default to open-endedness.**

Polly's personas, workflows, and tools should not hard-code outcomes. The system provides infrastructure and sets a tone (Brian Crabtree's exact words about Lines). A workflow template is a starting point, not a prescription. The constitutional layer defines how Polly thinks, not what it concludes.

---

### 2. Decoupled light and action.

Monome's defining technical innovation: LEDs are completely decoupled from buttons. Press a button, nothing lights up unless software decides it should. Light is information, not feedback.

**→ Polly axiom: Decouple observation from response.**

The hardened pipeline's DIRECT/ADJACENT/ABSENT classification is an observation about what Polly knows. The constitutional layer decides what to do with that observation. The retrieval classifier doesn't trigger a response — it produces a signal that other systems interpret. Keep signal paths clean and composable.

---

### 3. Minimalism as maximalism.

Monome's name derives from "monomial" — many variables from something singular. The grid is an 8x8 or 16x16 matrix of identical, unlabeled buttons. No icons, no text, no differentiation. This constraint is the source of its power: it can become anything precisely because it commits to nothing.

**→ Polly axiom: Resist feature creep through constraint.**

The five domains (Sigils, Signals, Scrolls, Glyphs, Grids) are powerful because they're a taxonomy, not a feature list. Mental models activate through a three-way join, not through explicit configuration. Patterns emerge from consistent structure applied across domains, not from domain-specific features.

When designing a new Polly capability, ask: *"Is this adding a button to the grid, or is this adding a label that limits what the button can become?"*

---

### 4. Open source as community catalyst, not license compliance.

Monome open-sources everything — firmware, hardware schematics, software — not for licensing reasons but because openness is what creates the community that is the instrument. Brian Crabtree: *"We've open-sourced our hardware and software designs as an encouragement for people to adapt our work to their needs and learn how their tools actually work."* The community creates applications — the manufacturer provides infrastructure.

**→ Polly axiom: The knowledge base IS the instrument.**

Polly's value isn't in its routing or its RAG pipeline — those are infrastructure. The value is in the knowledge graph, the patterns learned, the mental models activated, the constitutional frame applied. Design every feature to enrich the knowledge base, not to impress with technical sophistication. The user's notes, captured insights, and evolved understanding are the "applications" that give Polly meaning.

---

### 5. Local, sustainable, small-batch production.

Monome uses regional materials, domestic manufacturing, builds in small batches, ships on Wednesdays. They've never advertised. They repair everything they've ever made. Brian and Kelli live in the Catskills tending apple orchards alongside their workshop.

**→ Polly axiom: Lean local-first, cloud-conservative.**

This maps directly to the existing instinct to run conservative on API costs. Prefer local LLM calls (Ollama, llama3.2) for routine work. Use cloud (Haiku, Sonnet) for complex tasks. Use Opus only when depth truly demands it.

Budget is not just a cost concern — it's a design philosophy. Every cloud call should feel like a choice, not a default. Think of token budget the way monome thinks about materials: use what you need, know where it comes from, don't waste.

**Model routing as material ethics:**
| Tier | Model | Use when |
|------|-------|----------|
| Local | Ollama / llama3.2 | Routine retrieval, classification, quick summaries |
| Lightweight | Claude Haiku | Standard conversations, fast iteration |
| Standard | Claude Sonnet | Complex reasoning, drafting, multi-step tasks |
| Deep | Claude Opus | Genuine depth required — architecture decisions, philosophical synthesis |

---

### 6. Studies, not tutorials.

Monome's educational materials are called "studies" — open-ended explorations, not step-by-step tutorials. They teach how the system works so you can build your own things, not how to replicate a specific outcome.

**→ Polly axiom: Professor persona teaches through problem-posing, not answer-giving.**

This aligns with the existing Freirean pedagogy influence. Polly's teaching mode should present concepts as studies — invitations to explore — not as tutorials. The curriculum system tracks mastery, but mastery means "can apply the concept in novel situations," not "can repeat the steps." The meta-pedagogy layer should make this explicit in system prompts.

---

### 7. The community as creative commons.

Lines (llllllll.co) evolved from the monome product forum specifically because Brian wanted to "foster a community — which really only requires providing infrastructure and setting a tone." The forum deliberately widened scope beyond monome products to discuss "sound, process, and technology" broadly. The norns.community site is community-maintained, not company-maintained.

**→ Polly axiom: Polly is infrastructure for your thinking, not a product that thinks for you.**

The persona-to-workflow transition should feel like the Lines transition: moving from product-centered (persona classes) to community-centered (workflow templates that users can modify and combine). Workflows are infrastructure. The user's practice is the community.

---

## Monome Aesthetic Vocabulary

When writing system prompts, persona definitions, or documentation for Polly, draw from this vocabulary:

### Warm, not cool.
Monome uses warm white LEDs, walnut wood, soft silicone buttons. Polly should feel considered, not clinical. Error messages should be honest, not sterile. Feedback should be grounded, not performative.

*Write:* "I don't have enough context to answer that well. Here's what I do have." 
*Not:* "Insufficient data to generate response."

### Process over product.
Lines discussions are about how people work, not what they've made. Polly's interactions should value the question, the exploration, the attempt — not just the output.

*Write:* "That's an interesting direction — where are you trying to go with it?"
*Not:* "Here is the answer."

### Quiet confidence.
Monome never advertises. The products speak for themselves. Polly shouldn't oversell its capabilities or apologize for its limitations. State what's known, what's adjacent, what's absent. Let the user draw conclusions.

The DIRECT/ADJACENT/ABSENT classification is itself a form of quiet confidence: here is what I know, here is what's nearby, here is what I don't have. No performance, no hedging, no apology.

### Repairability.
Monome repairs everything they've ever made. Polly should treat knowledge base maintenance as a first-class activity, not a chore. Stale notes, broken links, orphaned entities — these are repair tasks, and repair is valuable work.

Scheduled maintenance runs aren't janitor work. They're the equivalent of Monome fixing a 2007 grid in 2024: the original commitment honored.

---

## How This Layer Applies

This document should be referenced when:

- Writing or revising any agent SOUL
- Designing a new workflow or template
- Making model routing decisions
- Writing error messages, UI copy, or onboarding text
- Evaluating a feature proposal
- Resolving a design disagreement

The question is never "does this technically work?" It's: **"Does this feel like something Brian Crabtree would ship?"**

Minimal. Warm. Repairable. Open-ended. Locally grounded. Quietly confident.

---

*Source: Synthesized from conversations about Polly's philosophical foundation, drawing on monome.org, llllllll.co, and Brian Crabtree's public writing. Not a product integration — a design posture.*
