# Phase 2: Agent Builder

**Status:** 📋 Planned  
**Gate:** Phase 1 Agent System complete (SOUL templates, manifest schema) + Phase 1 iOS Foundation complete  
**Spec source:** `AGENT_BUILDER.md`  
**Owners:** @frontend (iOS UI — all five screens), @backend (SOUL template validation, manifest write), @design_eng (empty state illustrations, card layouts)

## Goal

Any user can create a custom agent from their phone in under 2 minutes. Advanced users can craft precise SOUL templates. The builder is not a form — it's a guided conversation that produces a validated agent ready for immediate use.

**Design principle:** The iOS builder is the primary creation surface, not a simplified version of a desktop tool. It must be fully capable without feeling complex.

---

## Five-Screen Flow

```
Drawer (+) → Name & Emoji → Personality (Quick/Advanced) → Capabilities → Preview → Done
```

### Screen 1: Name & Emoji
- [ ] Agent name text field (autofocus)
- [ ] Emoji picker (custom scroll-wheel or emoji keyboard integration)
- [ ] Name validation: unique within user's agent list, non-empty
- [ ] Emoji defaults to 🤖 if not selected before Next

### Screen 2: Personality

Two paths — Quick Craft and Advanced (SOUL Template).

#### Quick Craft Path (default)
- [ ] Role description field: "This agent is a ___" — single text field
- [ ] Tone picker: 5 presets displayed as horizontal chips
  - Precise & Direct
  - Warm & Encouraging  
  - Playful & Creative
  - Analytical & Thorough
  - Concise & Efficient
- [ ] Domain picker: multi-select chips — Writing, Code, Research, Strategy, Design, Health, Finance, Personal
- [ ] "I also want this agent to..." — optional freeform field for additional instructions
- [ ] Quick Craft generates a SOUL template silently (gateway side) — user never sees the generated text unless they tap "Advanced"

#### Advanced Path (SOUL Template)
- [ ] Accessed via "Advanced" button on Quick Craft screen
- [ ] Full-screen code-style text editor with `SOUL.md` syntax highlighting (markdown)
- [ ] SOUL template structure enforced by validation (not form fields):
  - Required sections: `## Identity`, `## Voice`, `## What I Do`, `## What I Won't Do`, `## Working Style`
  - Optional sections: `## Prosodic Calibration`, `## Domain Expertise`, `## Signature Patterns`
- [ ] Validation on save: checks required sections present, non-empty
- [ ] "Quick Craft → Advanced" transition: show generated SOUL template from Quick Craft as starting point — not a blank editor
- [ ] SOUL template character cap: 3,000 characters (prevents prompt injection surface; shows counter)
- [ ] @backend: SOUL template sanitization — strip any tool call syntax, gateway command injection patterns

### Screen 3: Capabilities
- [ ] Mode toggles: Conversational (always on), Voice, Web Search, Vault Access, Code Execution (Phase 3+)
- [ ] Each toggle shows 1-line description: "Can search the web for current information"
- [ ] Vault Access: shows scope picker when toggled on (All Domains / specific domain selection)
- [ ] Knowledge Skill mode selector: Search / Graph / Search+Graph — maps to `allowed_modes` manifest field
- [ ] Autonomy level: Reactive (default) / Proactive (heartbeat-triggered) — Autonomous is system-only (Ambient Agent, Janitor), not user-selectable

### Screen 4: Preview
- [ ] Agent card rendered with name, emoji, description (first line of SOUL `## What I Do`)
- [ ] Suggested prompts preview: 3 auto-generated from SOUL content (gateway call)
- [ ] Send a test message field: "Try asking this agent something..."
- [ ] Test message sends to a preview session — real inference against the SOUL, capped at 3 turns
- [ ] [Create Agent] button — writes manifest + SOUL to gateway

### Screen 5: Done
- [ ] Confirmation card with agent emoji + name
- [ ] "Added to your agents" — appears in Drawer immediately
- [ ] Primary CTA: [Start a conversation] → opens new chat with agent
- [ ] Secondary: [Edit] → opens agent edit screen
- [ ] Share sheet (Phase 3+): export agent as `.polly-agent` bundle

---

## Agent Edit Screen (@frontend)

Accessed via long-press on agent in Drawer or from agent info sheet.

- [ ] All Quick Craft fields editable inline
- [ ] "Advanced (SOUL Template)" button — same editor as builder
- [ ] Model selector (Layer 1 routing override, see `phase-2-model-routing`)
- [ ] "Customize Routing" disclosure (Layer 2)
- [ ] Delete agent: destructive action, confirmation required, clears all agent memory
- [ ] Duplicate agent: creates copy with "(copy)" suffix, opens edit screen

---

## SOUL Template Spec (for @backend validation + @design_eng template)

### Required Sections

```markdown
## Identity
[1–2 sentences. Who this agent is. Written in first person.]

## Voice
[How this agent communicates. Tone, pace, what it avoids.]

## What I Do
[Core capabilities and expertise. 2–5 sentences.]

## What I Won't Do  
[Hard constraints. What this agent refuses or redirects. At least 1 item.]

## Working Style
[How this agent approaches problems. Preferences for depth, structure, proactivity.]
```

### Optional Sections

```markdown
## Prosodic Calibration
[Only if agent should respond differently to voice prosodics.]

## Domain Expertise  
[Specific knowledge domains. Signals to DomainEvaluator.]

## Signature Patterns
[Recurring patterns in how this agent structures responses — e.g., always asks a clarifying question, always offers 3 options.]
```

### Validation Rules (@backend)
- [ ] All 5 required sections present
- [ ] Each required section non-empty (min 20 chars)
- [ ] Total length ≤ 3,000 characters
- [ ] No tool call syntax (`<tool_call>`, `{function:`, etc.)
- [ ] No gateway command injection (`config.patch`, `session.delete`, etc.)
- [ ] `## What I Won't Do` must contain at least one line starting with "I won't" or "I don't" or "-"

### Quick Craft → SOUL Template Generation (@backend)
- [ ] Generate SOUL template from Quick Craft inputs using a fast LLM call (Tier 1 — not frontier)
- [ ] Inject Polly Standard SOUL Baseline footer automatically (user never writes this; gateway appends it)
- [ ] Generate 3 `suggested_prompts` from the SOUL content (second LLM call or same call)

---

## Agent Manifest Write (@backend)

On [Create Agent] tap:
- [ ] Write `agent/soul.md` to agent workspace on gateway
- [ ] Write agent manifest entry: `id`, `category`, `allowed_modes`, `autonomy_level`, `suggested_prompts`
- [ ] Append agent to `agents.list` in `openclaw.json` via `config.patch`
- [ ] Return agent ID + workspace path to iOS client
- [ ] Error handling: name collision → "This name is taken, try another"; validation failure → return section list that failed

---

## Agent Discovery (future, Phase 3+)
- [ ] Export agent as `.polly-agent` bundle (manifest + SOUL, no memory)
- [ ] Import `.polly-agent` via share sheet
- [ ] Agent library in Skills Marketplace (community-shared agents)

---

## Done When
Five-screen builder flow working end-to-end. Quick Craft generates valid SOUL. Advanced editor with validation. Capabilities screen wiring to manifest. Preview with test session. Agent appears in Drawer immediately after creation. Edit screen functional. @backend SOUL sanitization live.
