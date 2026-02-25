# Tasks: Programmer Persona + Code-Aware Routing Implementation

## Overview
Ordered implementation steps for adding the Programmer persona with six code-aware routing modes.

**Principle:** Follow existing persona pattern exactly. YAML definition first, then Python implementation, then registration, then slash commands, then frontend.

**Estimated scope:** ~900 lines across 8 files (2 new, 6 modified)

**Dependencies:**
- Phase 2 (Copilot Completions API) — for `complete` mode's Copilot FIM routing (graceful fallback if not available)
- Phases 0 and 1 benefit all modes automatically (cache + distillation apply to cloud-routed modes)

---

## Task 1: Create YAML Definition
**Goal:** Define Programmer persona metadata and mode prompts in YAML

**File:** `core/personas/definitions/programmer.yaml` (~500 lines)

### Subtasks:
1. **Metadata section:**
   ```yaml
   metadata:
     slug: programmer
     name: Programmer
     description: "Code-focused persona with specialized modes for writing, reviewing, debugging, and refactoring code"
     icon: "code"
     primary_domain: sigils
     skills:
       - code_generation
       - code_review
       - debugging
       - refactoring
     collaboration_partners:
       - architect
       - professor
   ```

2. **Complete mode prompt:**
   - Focus on inline completion, no explanation
   - Match existing code style
   - Stop at natural boundaries
   - Routing: CODE_COMPLETION / FAST / copilot

3. **Explain mode prompt:**
   - One-sentence summary first
   - Step-by-step logic walkthrough
   - Highlight non-obvious behavior and edge cases
   - Reference design patterns by name
   - Routing: DOCUMENTATION / BALANCED / local

4. **Refactor mode prompt:**
   - Behavior-preserving restructuring
   - Apply readability_ratchet and restraint_first mental models
   - Show BEFORE and AFTER with explanations
   - Routing: REFACTORING / THOROUGH / cloud

5. **Generate mode prompt:**
   - Start with interface/signature
   - Idiomatic code for target language
   - Error handling, type hints
   - Minimum viable code (restraint_first)
   - Routing: CODE_GENERATION / THOROUGH / cloud

6. **Debug mode prompt:**
   - Systematic: READ → IDENTIFY → TRACE → LOCATE → FIX → VERIFY
   - Common bug categories checklist
   - Show exact lines to change + root cause explanation
   - Suggest test case that would have caught the bug
   - Routing: DEBUGGING / BALANCED / cloud

7. **Review mode prompt:**
   - SUMMARY → ISSUES (Critical/Warning/Suggestion) → POSITIVES → RECOMMENDATIONS
   - Review checklist: errors, edge cases, security, performance, readability, testing
   - Severity labels with icons
   - Routing: CODE_REVIEW / BALANCED / cloud

### Validation:
- [ ] Valid YAML, loads without errors
- [ ] All 6 modes defined with system_prompt and routing
- [ ] Metadata matches PersonaMetadata expected fields
- [ ] Prompts reference relevant mental models by name

---

## Task 2: Implement ProgrammerPersona Class
**Goal:** Create Python implementation following AgentPersona pattern

**File:** `core/personas/implementations/programmer.py` (~400 lines)

### Subtasks:
1. **Class skeleton:**
   ```python
   class ProgrammerPersona(AgentPersona):
       MODE_ROUTING = {
           "complete": {"task_type": TaskType.CODE_COMPLETION, "confidence": ConfidenceLevel.FAST, "prefer": "copilot"},
           "explain":  {"task_type": TaskType.DOCUMENTATION,   "confidence": ConfidenceLevel.BALANCED, "prefer": "local"},
           "refactor": {"task_type": TaskType.REFACTORING,     "confidence": ConfidenceLevel.THOROUGH, "prefer": "cloud"},
           "generate": {"task_type": TaskType.CODE_GENERATION, "confidence": ConfidenceLevel.THOROUGH, "prefer": "cloud"},
           "debug":    {"task_type": TaskType.DEBUGGING,       "confidence": ConfidenceLevel.BALANCED, "prefer": "cloud"},
           "review":   {"task_type": TaskType.CODE_REVIEW,     "confidence": ConfidenceLevel.BALANCED, "prefer": "cloud"},
       }
       
       MODE_PATTERNS = { ... }  # Regex patterns for auto-detection
   ```

2. **__init__(self, skill_manager=None, rag=None, domain_engine=None):**
   - Call super().__init__()
   - Store injected dependencies
   - Follow Scribe/Professor pattern

3. **Properties:**
   - `default_mode` → `"generate"`
   - `available_modes` → `["complete", "explain", "refactor", "generate", "debug", "review"]`

4. **detect_mode(query: str) → str:**
   - Iterate MODE_PATTERNS, match against query
   - Priority order: debug > review > refactor > generate > explain > complete
   - Default to "generate" if no match
   - Case-insensitive matching

5. **MODE_PATTERNS dict:**
   ```python
   MODE_PATTERNS = {
       "complete": [r'\bcomplete\b', r'\bfinish\b', r'\bcontinue\s+(?:the\s+)?code'],
       "explain":  [r'\bexplain\b', r'\bwhat\s+does\b', r'\bhow\s+does\b', r'\bwalk\s+(?:me\s+)?through'],
       "refactor": [r'\brefactor\b', r'\brestructure\b', r'\bclean\s+up\b', r'\bimprove\b'],
       "generate": [r'\bwrite\b', r'\bcreate\b', r'\bgenerate\b', r'\bimplement\b', r'\bbuild\b'],
       "debug":    [r'\bdebug\b', r'\bfix\b', r'\bbug\b', r'\berror\b', r'\bwhy\s+(?:is|does|doesn\'t)'],
       "review":   [r'\breview\b', r'\bcheck\b', r'\blook\s+(?:at|over)\b', r'\bfeedback\b'],
   }
   ```

6. **process(context: PersonaContext) → PersonaResponse:**
   - Detect or use specified mode
   - Get routing hints from MODE_ROUTING
   - If complete mode + copilot available: route to CopilotFIMProvider
   - Otherwise: build messages with mode-specific system prompt
   - Route based on prefer hint (local/cloud/copilot)
   - Format response via `_format_code_response()`
   - Return PersonaResponse

7. **get_mode_prompts() → dict[str, str]:**
   - Load from YAML definition
   - Return {mode_name: system_prompt} dict

8. **_route_with_hints(context, routing) → PersonaResponse:**
   - Build messages via `_build_messages()` (from AgentPersona base)
   - If prefer == "local": route to local Ollama
   - If prefer == "cloud": route to cloud via Router V2 with task_type and confidence
   - If prefer == "copilot": try CopilotFIMProvider, fall back to local
   - Wrap in try/except with fallback to alternative routing

9. **_format_code_response(raw_response, mode) → str:**
   - Ensure code blocks have language tags
   - For refactor: ensure diff-like BEFORE/AFTER formatting
   - For debug: ensure numbered steps
   - For review: ensure severity labels present
   - Light-touch: don't alter content, just validate structure

10. **_handle_non_code_query(context) → PersonaResponse:**
    - Detect non-code queries when Programmer is active
    - Return suggestion to switch persona
    - "That sounds like a question for Professor. Would you like me to switch?"

### Validation:
- [ ] Inherits AgentPersona correctly
- [ ] All abstract methods implemented (default_mode, available_modes, process, get_mode_prompts)
- [ ] Mode detection works for representative queries
- [ ] process() routes to correct provider based on mode
- [ ] Copilot FIM integration works (or falls back gracefully)
- [ ] Code response formatting is light-touch and correct

---

## Task 3: Register in PersonaManager
**Goal:** Add ProgrammerPersona to registry and dependency injection

**File:** `core/personas/manager.py`

### Subtasks:
1. **Import ProgrammerPersona** at top of file (or lazy import in activation)

2. **Uncomment/add registry entry** (~L74):
   ```python
   PERSONA_REGISTRY = {
       "architect": ArchitectPersona,
       "scribe": ScribePersona,
       "professor": ProfessorPersona,
       "programmer": ProgrammerPersona,
   }
   ```

3. **Add dependency injection block** in `activate_persona()` (~L361-383):
   ```python
   elif persona_slug == "programmer":
       instance = ProgrammerPersona(
           skill_manager=self.skill_manager,
           rag=self.rag,
           domain_engine=self.domain_engine,
       )
   ```

### Validation:
- [ ] ProgrammerPersona in PERSONA_REGISTRY
- [ ] activate_persona("programmer") creates instance with correct dependencies
- [ ] Lazy loading works (metadata loads without Python class)
- [ ] Deactivation works (switching away from Programmer)

---

## Task 4: Add Slash Commands
**Goal:** Register Programmer slash commands

**File:** `core/personas/commands.py`

### Subtasks:
1. Add PROGRAMMER_COMMANDS list with 6 commands:
   - `/code` → programmer/generate
   - `/debug` → programmer/debug
   - `/review` → programmer/review
   - `/refactor` → programmer/refactor
   - `/explain-code` → programmer/explain
   - `/complete` → programmer/complete

2. Register commands with existing command system (follow existing pattern)

3. Add usage descriptions and help text for each command

### Validation:
- [ ] All 6 slash commands registered
- [ ] Each command maps to correct persona and mode
- [ ] Help text available for each command
- [ ] No conflicts with existing commands

---

## Task 5: Add Introduction Message
**Goal:** Add Programmer's first-time introduction message

**File:** `core/pedagogy/coaching_templates.py`

### Subtasks:
1. Uncomment/add programmer introduction (~L53):
   ```python
   "programmer": (
       "Hey there! I'm Programmer, your code-focused companion. "
       "I can help you write, review, debug, refactor, and explain code. "
       "Try /code to generate, /debug to fix bugs, /review for feedback, "
       "or /refactor to improve existing code. What are we building?"
   ),
   ```

### Validation:
- [ ] Introduction message displays on first activation
- [ ] Message mentions all key slash commands
- [ ] Only shows once (user_journey tracks first encounter)

---

## Task 6: Update Package Exports
**Goal:** Export ProgrammerPersona from personas package

**File:** `core/personas/__init__.py`

### Subtasks:
1. Add `ProgrammerPersona` to imports:
   ```python
   from core.personas.implementations.programmer import ProgrammerPersona
   ```

2. Add to `__all__` if present

### Validation:
- [ ] `from core.personas import ProgrammerPersona` works
- [ ] No circular import issues

---

## Task 7: Update Frontend (If Applicable)
**Goal:** Add Programmer persona to frontend persona selector

### Subtasks:
1. **Check if persona selector exists** in `electron-app/src/renderer/index.html`
   - If yes: add Programmer option with code icon
   - If no: skip (personas may be activated via slash commands only)

2. **If persona selector exists** (`electron-app/src/renderer/app.js`):
   - Add Programmer to persona list
   - Handle mode display (show 6 modes when Programmer active)
   - Wire up mode switching UI

### Files:
- `electron-app/src/renderer/index.html` (if applicable)
- `electron-app/src/renderer/app.js` (if applicable)

### Validation:
- [ ] Programmer appears in persona selector (if exists)
- [ ] Mode switching works from UI (if applicable)
- [ ] Falls back to slash commands if no selector UI

---

## Task 8: Testing — Mode Detection
**Goal:** Verify auto-detection matches correct modes

### Test Cases:
1. **Debug mode:**
   - "Fix the bug in my sort function" → debug
   - "Why is this returning None?" → debug
   - "There's an error in line 42" → debug

2. **Review mode:**
   - "Review this code for me" → review
   - "Can you check this implementation?" → review
   - "Give me feedback on my PR" → review

3. **Refactor mode:**
   - "Refactor this function" → refactor
   - "Clean up this code" → refactor
   - "Improve the readability" → refactor

4. **Generate mode:**
   - "Write a function that sorts" → generate
   - "Create a REST API endpoint" → generate
   - "Implement binary search" → generate

5. **Explain mode:**
   - "Explain how this works" → explain
   - "What does this function do?" → explain
   - "Walk me through this algorithm" → explain

6. **Complete mode:**
   - "Complete this function" → complete
   - "Finish the code" → complete

7. **Ambiguous queries:**
   - "Fix and improve this code" → debug (higher priority)
   - "Review and refactor" → review (higher priority)

8. **No match (default):**
   - "Make a calculator" → generate (default)
   - "Help with my project" → generate (default)

### Validation:
- [ ] > 80% accuracy on test set
- [ ] Priority ordering works for ambiguous queries
- [ ] Default fallback to generate works

---

## Task 9: Testing — Routing Per Mode
**Goal:** Verify each mode routes to the correct provider

### Test Cases:
1. **complete** → Copilot FIM (or local Ollama fallback)
   - Verify TaskType.CODE_COMPLETION passed to router
   - Verify ConfidenceLevel.FAST used

2. **explain** → Local Ollama
   - Verify routes to local (not cloud)
   - Verify ConfidenceLevel.BALANCED used
   - Check token usage is $0 (local)

3. **refactor** → Cloud (Claude Sonnet/Opus)
   - Verify TaskType.REFACTORING passed
   - Verify ConfidenceLevel.THOROUGH used

4. **generate** → Cloud
   - Verify TaskType.CODE_GENERATION passed
   - Verify ConfidenceLevel.THOROUGH used

5. **debug** → Cloud
   - Verify TaskType.DEBUGGING passed
   - Verify ConfidenceLevel.BALANCED used

6. **review** → Cloud
   - Verify TaskType.CODE_REVIEW passed
   - Verify ConfidenceLevel.BALANCED used

### Validation:
- [ ] Each mode uses correct TaskType
- [ ] Each mode uses correct ConfidenceLevel
- [ ] Local modes stay local (explain)
- [ ] Cloud modes route through Router V2 (refactor, generate, debug, review)
- [ ] complete mode tries Copilot first, falls back gracefully

---

## Task 10: Testing — Slash Commands
**Goal:** Verify all slash commands activate correct persona and mode

### Test Cases:
1. `/code write a fibonacci function` → Programmer/generate
2. `/debug fix the null pointer` → Programmer/debug
3. `/review check this code` → Programmer/review
4. `/refactor improve this function` → Programmer/refactor
5. `/explain-code how does this work` → Programmer/explain
6. `/complete finish this code` → Programmer/complete

### Validation:
- [ ] All 6 commands activate Programmer persona
- [ ] Correct mode activated for each command
- [ ] Query text passed through to process()
- [ ] Persona switch works (e.g., from Architect to Programmer via slash command)

---

## Task 11: Testing — Persona Lifecycle
**Goal:** Verify persona activation, deactivation, and switching

### Test Cases:
1. **Activation:**
   - Activate Programmer → verify introduction message (first time)
   - Verify mental models with `active_for_personas=['programmer']` appear in context

2. **Mode switching:**
   - Activate in generate mode → switch to debug → switch to review
   - Verify system prompt changes with each mode

3. **Persona switching:**
   - Activate Programmer → switch to Architect → switch back to Programmer
   - Verify state preserved (or reset correctly)

4. **Non-code query while active:**
   - Activate Programmer → ask "what's the weather?"
   - Verify suggestion to switch persona

5. **No code provided:**
   - Activate review mode → submit without code
   - Verify prompt asking for code

### Validation:
- [ ] Introduction shows on first activation only
- [ ] Mental models activated correctly
- [ ] Mode switching preserves persona
- [ ] Persona switching works cleanly
- [ ] Edge cases handled gracefully

---

## Task 12: Testing — Mental Model Integration
**Goal:** Verify programmer-tagged mental models appear in gathered context

### Test Cases:
1. Activate Programmer persona
2. Make a query (e.g., /code "write a sort function")
3. Inspect gathered context in logs/debug
4. Verify at least these models present:
   - `restraint_first`
   - `readability_ratchet`
   - `local_variables`
   - `separation_of_concerns`
   - `error_handling_patterns`
5. Switch to Architect persona
6. Verify programmer-specific models no longer in context

### Validation:
- [ ] 14+ programmer-tagged mental models activated
- [ ] Models appear in gathered context
- [ ] Models deactivate when switching away from Programmer
- [ ] No interference with other persona's mental models

---

## Task 13: Documentation & Specs Update
**Goal:** Update relevant docs

### Subtasks:
1. Update architecture spec:
   - Add Programmer to persona diagram (4 personas now)
   - Document 6 modes and their routing

2. Update project status:
   - Mark Programmer persona as completed
   - Update persona count (3 → 4)

3. Add changelog entry:
   ```markdown
   ## YYYY-MM-DD - Programmer Persona (Phase 3)
   - Added Programmer persona with 6 code-aware modes
   - Modes: complete, explain, refactor, generate, debug, review
   - Each mode routes to appropriate provider (local/cloud/Copilot)
   - 14+ code-specific mental models activated
   - Slash commands: /code, /debug, /review, /refactor, /explain-code, /complete
   - Auto-detection of code task type from natural language queries
   ```

4. Archive this change folder

### Validation:
- [ ] All specs updated
- [ ] Changelog entry added

---

## Task 14: Final Validation
**Goal:** Comprehensive end-to-end testing

### Test Scenarios:
1. **All 6 modes functional:**
   - [ ] /code generates production-quality code
   - [ ] /debug finds and explains bugs
   - [ ] /review provides structured code review
   - [ ] /refactor preserves behavior while improving structure
   - [ ] /explain-code explains logic clearly
   - [ ] /complete provides reasonable completions

2. **Routing correctness:**
   - [ ] explain routes to local Ollama (verified in logs)
   - [ ] refactor/generate route to cloud Thorough tier
   - [ ] debug/review route to cloud Balanced tier
   - [ ] complete tries Copilot, falls back gracefully

3. **Persona system integrity:**
   - [ ] All 4 personas work (Architect, Scribe, Professor, Programmer)
   - [ ] Switching between personas works
   - [ ] No regressions to existing personas

4. **Mental models:**
   - [ ] Programmer-tagged models active
   - [ ] Code responses reflect mental model principles

### Success Criteria:
- All 6 modes functional and producing mode-appropriate responses
- Mode auto-detection accuracy > 80%
- Explain mode stays local (zero cloud cost)
- Cloud modes use correct TaskType/ConfidenceLevel
- 14+ mental models activated
- Zero regressions to existing persona system
- All slash commands work

---

## Dependency Order

```
Task 1 (YAML Definition)
    ↓
Task 2 (Python Implementation)
    ↓
Task 3 (Manager Registration) ──→ Task 4 (Slash Commands)
    ↓                                ↓
Task 5 (Introduction Message)    Task 6 (Package Exports)
    ↓                                ↓
    └────────────┬───────────────────┘
                 ↓
Task 7 (Frontend — if applicable)
                 ↓
Tasks 8-12 (Testing) ← can run in parallel
                 ↓
Task 13 (Docs)
                 ↓
Task 14 (Final Validation)
```

Tasks 3-6 can be done in parallel after Task 2. Tasks 8-12 can run in parallel.

---

## Coordination Notes

### Depends on Phase 2 (Copilot FIM) — soft dependency:
- `complete` mode tries `get_copilot_provider()` for FIM
- If Phase 2 not implemented: returns None → falls back to local Ollama
- Programmer persona works fully without Phase 2 — just `complete` mode is less capable

### Benefits from Phase 0 (Semantic Cache):
- Cloud-routed modes (refactor, generate, debug, review) benefit from cache hits
- No explicit integration needed — cache operates at pipeline level

### Benefits from Phase 1 (Context Distillation):
- Cloud-routed modes benefit from distilled context (fewer tokens)
- No explicit integration needed — distillation operates at pipeline level

### Existing infrastructure used (no changes needed):
- `core/domains.py` — Sigils domain already detects code queries
- `core/mental_models.py` — 14+ models already tagged `active_for_personas=['programmer']`
- `libs/polly-routing/polly_routing/router.py` — All TaskTypes already defined
- `core/personas/base.py` — AgentPersona ABC unchanged
