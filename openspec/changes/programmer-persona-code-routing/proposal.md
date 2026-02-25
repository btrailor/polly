# Proposal: Programmer Persona + Code-Aware Routing

## What
Implement the Programmer persona — Polly's fourth persona — with six code-aware routing modes (`complete`, `explain`, `refactor`, `generate`, `debug`, `review`) that route to different providers and models based on the type of code task. The Programmer persona is already planned in the codebase (commented out in the persona registry, referenced by 14+ mental models) and completes Polly's persona system.

This is **Phase 3** of a four-phase Copilot integration and token conservation plan.

## Why
**Current state:** Polly has three active personas:
- **Architect** — 2 modes: plan, build (system design and architectural thinking)
- **Scribe** — 4 modes: capture, organize, enrich, edit (writing and note management)
- **Professor** — 4 modes: explain, socratic, curriculum, quiz (teaching and learning)

The Programmer persona is already anticipated:
- `core/personas/manager.py:74` — `# "programmer": ProgrammerPersona,` (commented out)
- `core/pedagogy/coaching_templates.py:53` — `# "programmer": "Hey there! I'm Programmer..."` (placeholder)
- `core/mental_models.py` — 14+ mental models have `active_for_personas=['programmer']` (restraint_first, readability_ratchet, local_variables, etc.)
- The Sigils (code) domain in DomainEngine already detects programming queries
- Router V2's TaskType enum already has all code-relevant types: `CODE_COMPLETION`, `CODE_GENERATION`, `CODE_REVIEW`, `REFACTORING`, `DEBUGGING`, `DOCUMENTATION`

**Problem:**
1. **No code-specialized persona:** Code queries use the generic pipeline with no code-specific system prompts, mode-based routing, or task-type awareness
2. **No mode differentiation:** "Explain this code", "refactor this function", and "complete this snippet" all take the same pipeline path despite having fundamentally different requirements
3. **Routing is task-unaware for code:** The router doesn't know if a code query needs a fast completion (Copilot FIM), a thorough review (Claude Opus), or a quick explanation (local Ollama)
4. **Mental models unused:** 14+ code-specific mental models are defined with `active_for_personas=['programmer']` but never activated because the persona doesn't exist
5. **No Copilot integration point:** Phase 2's FIM completions need a persona mode to route through

**Solution:** A Programmer persona with six modes, each mapping to a specific TaskType, ConfidenceLevel, and preferred provider:

| Mode | Purpose | TaskType | ConfidenceLevel | Primary Provider |
|------|---------|----------|-----------------|-----------------|
| `complete` | Inline code completion | CODE_COMPLETION | FAST | Copilot FIM (Phase 2) / local Ollama fallback |
| `explain` | Explain code logic | DOCUMENTATION | BALANCED | Local Ollama (cheap, good enough) |
| `refactor` | Restructure code | REFACTORING | THOROUGH | Cloud (Claude Sonnet/Opus) |
| `generate` | Write new code | CODE_GENERATION | THOROUGH | Cloud (Claude Sonnet/GPT-4o) |
| `debug` | Find and fix bugs | DEBUGGING | BALANCED | Cloud (Claude Sonnet) |
| `review` | Code review + suggestions | CODE_REVIEW | BALANCED | Cloud (Claude Sonnet/GPT-4o) |

**Benefits:**
1. **Right model for the job:** Fast completions use Copilot FIM; deep analysis uses Claude Opus; explanations stay local
2. **Cost optimization:** `explain` mode defaults to local Ollama (free); `complete` mode uses Copilot (subscription, not per-token); only `refactor`/`generate` use expensive cloud models
3. **14+ mental models activated:** Code-specific mental models (restraint_first, readability_ratchet, etc.) become active for the Programmer persona
4. **Copilot integration point:** The `complete` mode provides the natural routing destination for Phase 2's FIM
5. **Slash commands:** `/code`, `/debug`, `/review`, `/refactor` provide quick mode switching
6. **Follows existing patterns:** Uses the same AgentPersona base class, YAML definition, and registration pattern as Architect/Scribe/Professor

## Scope

### Backend (Python)
- **New file:** `core/personas/implementations/programmer.py` (~400 lines) — ProgrammerPersona class with 6 modes
- **New file:** `core/personas/definitions/programmer.yaml` (~500 lines) — Full prompt definitions per mode
- **Modified:** `core/personas/manager.py` — Uncomment registry entry, add dependency injection block
- **Modified:** `core/personas/commands.py` — Add slash commands (/code, /debug, /review, /refactor, /explain-code, /generate)
- **Modified:** `core/personas/__init__.py` — Export ProgrammerPersona
- **Modified:** `core/pedagogy/coaching_templates.py` — Uncomment/add introduction message

### Frontend (Electron)
- **Modified:** `electron-app/src/renderer/index.html` — Programmer persona in persona selector (if UI exists)
- **Modified:** `electron-app/src/renderer/app.js` — Handle programmer persona modes

### No New Dependencies
- Uses existing AgentPersona base class
- Uses existing YAML definition loading
- Uses existing slash command infrastructure
- Uses existing DomainEngine (Sigils domain)
- Uses existing Router V2 TaskType/ConfidenceLevel system

## Four-Phase Roadmap Context

| Phase | Name | Purpose | Status |
|-------|------|---------|--------|
| 0 | Semantic Response Cache | System-wide query dedup + token savings tracking | Specced |
| 1 | Context Distillation Layer | Local Ollama compresses context before cloud calls | Specced |
| 2 | GitHub Copilot Completions API | Native FIM for inline code completion | Specced |
| **3** | **Programmer Persona + Code Routing** | **Code-aware modes with task-specific routing** | **This proposal** |

Phase 3 ties the previous phases together. The Programmer persona's `complete` mode routes through Phase 2's Copilot FIM. Cloud-routed modes (`refactor`, `generate`, `debug`, `review`) benefit from Phase 1's context distillation. All modes benefit from Phase 0's semantic cache.

## Non-Goals
- Implementing the code workspace editor (that's Phase 17)
- Adding new code analysis tools (linters, formatters, etc.)
- Implementing multi-file refactoring (future enhancement)
- Replacing the Architect persona for system design tasks
- Adding new mental models (14+ already exist for the Programmer persona)
- Implementing file/selection context pills (that's Phase 17's chat panel spec)
