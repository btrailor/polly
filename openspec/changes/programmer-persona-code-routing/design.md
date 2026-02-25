# Design: Programmer Persona + Code-Aware Routing

## Overview
Implement the Programmer persona — Polly's fourth persona — with six code-aware routing modes that map to existing Router V2 TaskTypes and ConfidenceLevels. Follows the established persona pattern (AgentPersona base class + YAML definitions + PersonaManager registration).

## Architecture

### Persona System Context
```
PersonaManager
  ├── ArchitectPersona     (plan, build)
  ├── ScribePersona        (capture, organize, enrich, edit)
  ├── ProfessorPersona     (explain, socratic, curriculum, quiz)
  └── ProgrammerPersona    [NEW] (complete, explain, refactor, generate, debug, review)

DomainEngine
  └── Sigils (code) ← Programmer's primary domain

Router V2 TaskTypes (all already defined):
  ├── CODE_COMPLETION      ← complete mode
  ├── CODE_GENERATION      ← generate mode
  ├── CODE_REVIEW          ← review mode
  ├── REFACTORING          ← refactor mode
  ├── DEBUGGING            ← debug mode
  └── DOCUMENTATION        ← explain mode
```

### Mode → Routing Matrix

| Mode | TaskType | ConfidenceLevel | Primary Provider | Rationale |
|------|----------|-----------------|-----------------|-----------|
| `complete` | CODE_COMPLETION | FAST | Copilot FIM (Phase 2) / local Ollama | Inline completions need speed, not depth |
| `explain` | DOCUMENTATION | BALANCED | Local Ollama (llama3.1:7b) | Explanation is a local-capable task |
| `refactor` | REFACTORING | THOROUGH | Cloud — Copilot Chat (Claude Opus 4.6, GPT-5.2) or direct API (Claude Sonnet/Opus) | Refactoring needs deep code understanding |
| `generate` | CODE_GENERATION | THOROUGH | Cloud — Copilot Chat (GPT-5.2, Claude Sonnet 4.6) or direct API (Claude Sonnet/GPT-4o) | Generation needs strong reasoning |
| `debug` | DEBUGGING | BALANCED | Cloud — Copilot Chat (Claude Sonnet 4.6, GPT-5.2) or direct API (Claude Sonnet) | Debugging needs pattern recognition |
| `review` | CODE_REVIEW | BALANCED | Cloud — Copilot Chat (Claude Sonnet 4.6, GPT-5.2) or direct API (Claude Sonnet/GPT-4o) | Review needs code quality judgment |

**Note on cloud routing:** Modes that prefer "cloud" go through Router V2's fallback chains, which now include both `copilot_chat/` models and direct API providers (Phase 2). The router selects the best available option based on the tier (fast/balanced/thorough), Copilot premium budget availability, and provider health. The Programmer persona does not need to know which specific cloud provider handles its request — Router V2 handles that transparently.

### Key Design Decisions

#### 1. Follow Existing Persona Pattern Exactly
**Decision:** Implement ProgrammerPersona using the exact same pattern as Scribe and Professor — YAML-defined prompts, AgentPersona base class, lazy-loading via PersonaManager.

**Pattern:**
1. `core/personas/implementations/programmer.py` — Python class (inherits AgentPersona)
2. `core/personas/definitions/programmer.yaml` — YAML prompts per mode
3. Registry entry in `core/personas/manager.py` PERSONA_REGISTRY
4. Dependency injection block in `manager.py` activate_persona()
5. Slash commands in `core/personas/commands.py`
6. Introduction message in `core/pedagogy/coaching_templates.py`
7. Export in `core/personas/__init__.py`

**Rationale:** No new patterns. The persona system is mature and well-established. Following it exactly ensures consistency and minimizes surprises.

#### 2. Mode-Specific System Prompts
**Decision:** Each mode gets a detailed system prompt in `programmer.yaml` that shapes the LLM's behavior for that specific code task.

**Prompt structure per mode:**
```yaml
modes:
  refactor:
    system_prompt: |
      You are Programmer, Polly's code-focused persona, currently in REFACTOR mode.
      
      Your task is to restructure and improve existing code while preserving its
      exact behavior. Follow these principles:
      
      1. NEVER change functionality — refactoring is behavior-preserving
      2. Apply the readability_ratchet principle: every change must improve readability
      3. Follow restraint_first: prefer small, focused changes over large rewrites
      4. Extract functions when a block has a single clear purpose
      5. Reduce nesting depth (max 3 levels)
      6. Improve naming: variables and functions should read as documentation
      7. Remove dead code and unused imports
      8. Add type hints where missing (Python)
      
      When presenting refactored code:
      - Show the BEFORE and AFTER clearly
      - Explain EACH change and WHY
      - Note any edge cases that need attention
      - Suggest follow-up refactorings if appropriate
    
    routing:
      task_type: REFACTORING
      confidence: THOROUGH
      prefer_provider: cloud
```

#### 3. Route Hints, Not Route Overrides
**Decision:** Each mode provides routing *hints* (task_type, confidence, prefer_provider) that influence the router's decision, but the router makes the final call based on budget, availability, and fallback chains.

**Implementation:**
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
```

The `prefer` field is a hint:
- `"copilot"` → Route to Copilot FIM provider (Phase 2). If unavailable, fall to local Ollama.
- `"local"` → Route to local Ollama. If model unavailable, fall to cloud.
- `"cloud"` → Route to cloud via Router V2. Fallback chains include both Copilot Chat models (`copilot_chat/claude-opus-4.6`, `copilot_chat/gpt-5.2`, etc.) and direct API providers (`anthropic/claude-sonnet-4-20250514`, etc.). Router V2 selects based on tier, availability, and Copilot premium budget.

**Copilot Chat value for cloud modes:** With Copilot Chat in fallback chains (Phase 2), the Programmer persona's cloud modes get access to:
- **Free models** (0x multiplier): GPT-5 mini, GPT-4.1 — great for budget-conscious balanced-tier work
- **Standard models** (1x multiplier): GPT-5.2, Claude Sonnet 4.6, Gemini 3 Pro — subscription-priced instead of per-token
- **Premium models** (3x multiplier): Claude Opus 4.6 — top-tier reasoning at subscription cost instead of $75/M output tokens

#### 3a. Interaction with Polly Mode + Model Control
**Decision:** MODE_ROUTING `prefer` hints are **Layer 0** in the Polly Mode preference hierarchy. Per-persona routing preferences from the Polly Mode spec (Layers 1-2) override these hints when set. Polly Mode OFF (Layer 3) overrides everything.

**Preference layers applied to Programmer:**
```
Layer 3 (highest): Polly Mode OFF → user picks exact model → MODE_ROUTING ignored entirely
Layer 2:          Settings mode override (e.g., Programmer/refactor → anthropic, claude-opus-4) → overrides prefer hint
Layer 1:          Settings persona default (e.g., Programmer → copilot_chat) → overrides prefer hint for all modes
Layer 0 (base):   MODE_ROUTING prefer hints (copilot/local/cloud) → fallback when no prefs set
```

**Example interaction:**
- MODE_ROUTING says `refactor.prefer = "cloud"` (generic cloud routing)
- User sets Programmer/refactor mode override to `cloud_provider: "anthropic"`, `cloud_model: "claude-opus-4-20250514"` in Settings
- Result: refactor mode routes to Anthropic Claude Opus 4 specifically (Layer 2 wins over Layer 0)
- If Anthropic is unavailable: falls through to Router V2's standard fallback chain (preference is soft)

**Key behavior:** The Programmer persona's `_route_with_hints()` method does NOT need to know about persona routing preferences. `polly.py` applies preferences before calling Router V2 (see Polly Mode spec, Task 5). The Programmer just passes `task_type` and `confidence` to the standard routing path — preferences are applied upstream in the query pipeline.

**When Polly Mode is OFF:** MODE_ROUTING hints are completely irrelevant. The user has selected an exact model, and the query goes directly to that model (bypassing routing entirely). Cache and distillation still apply.

#### 4. Mode Detection
**Decision:** Modes are activated via three mechanisms:
1. **Slash commands:** `/code generate`, `/debug`, `/review`, `/refactor`
2. **Explicit activation:** `PersonaManager.activate_persona("programmer", mode="refactor")`
3. **Auto-detection:** When Programmer is active, detect mode from query intent:
   - "Fix this bug..." → debug
   - "Review this code..." → review
   - "Refactor the..." → refactor
   - "Write a function..." → generate
   - "Explain how..." → explain
   - Default: generate (most common code request)

**Auto-detection implementation:**
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

#### 5. Mental Model Activation
**Decision:** When Programmer is active, mental models with `active_for_personas=['programmer']` are automatically loaded and included in gathered context.

**Already defined (14+ models):**
- `restraint_first` — Prefer minimal changes
- `readability_ratchet` — Every change must improve readability
- `local_variables` — Keep scope narrow
- `separation_of_concerns` — Single responsibility per function/module
- `error_handling_patterns` — Defensive coding practices
- And 9+ more

**No work needed:** These models are already defined in `core/mental_models.py` with `active_for_personas=['programmer']`. The existing `_gather_context()` pipeline in `polly.py` automatically includes them when the Programmer persona is active.

#### 6. Copilot Integration Points (Phase 2 Dependency)
**Decision:** The `complete` mode routes FIM requests through Phase 2's `CopilotFIMProvider`. All cloud modes (`refactor`, `generate`, `debug`, `review`) benefit from Copilot Chat models being in Router V2's fallback chains — no special Programmer-side code needed for Chat routing.

**FIM (complete mode):**
```python
async def process(self, context: PersonaContext) -> PersonaResponse:
    mode = context.current_mode
    routing = self.MODE_ROUTING[mode]
    
    if mode == "complete" and routing["prefer"] == "copilot":
        # Try Copilot FIM (Phase 2)
        copilot = get_copilot_provider()
        if copilot and copilot.is_available():
            result = await copilot.complete_fim(
                prefix=context.metadata.get("prefix", ""),
                suffix=context.metadata.get("suffix", ""),
                language=context.metadata.get("language", "python")
            )
            return PersonaResponse(content=result["choices"][0]["text"], mode=mode)
        # Fallback: treat as local code generation
        routing = {**routing, "prefer": "local", "confidence": ConfidenceLevel.FAST}
    
    # Standard routing for all other modes
    # Cloud modes (refactor, generate, debug, review) go through Router V2,
    # which includes copilot_chat/ models in fallback chains (Phase 2).
    # No Copilot-specific code needed here — the router handles it.
    return await self._route_with_hints(context, routing)
```

**Chat (cloud modes — transparent via Router V2):**
When the Programmer routes `refactor`, `generate`, `debug`, or `review` queries to the cloud, Router V2's fallback chains now include Copilot Chat models alongside direct API providers. For example, a `THOROUGH` tier request might try:
1. `github/openai/gpt-4o`
2. `copilot_chat/claude-opus-4.6` (3x premium request)
3. `copilot_chat/gpt-5.2` (1x premium request)
4. `anthropic/claude-opus-4-20250514` (direct API, per-token)

The Programmer persona doesn't need to know about this — `_route_with_hints()` passes the task_type and confidence to Router V2, which does the rest.

**Before Phase 2 is implemented:** The `complete` mode will always fall back to the local Ollama route, providing basic code completion via the chat interface. Cloud modes will use only direct API providers (no Copilot Chat in fallback chains). Not as good, but functional.

## API Design

### ProgrammerPersona Class

```python
class ProgrammerPersona(AgentPersona):
    """
    Polly's code-focused persona with six routing modes.
    
    Modes:
        complete - Inline code completion (Copilot FIM / local)
        explain  - Explain code logic (local Ollama)
        refactor - Restructure code (cloud)
        generate - Write new code (cloud)
        debug    - Find and fix bugs (cloud)
        review   - Code review (cloud)
    """
    
    MODE_ROUTING = {
        "complete": {"task_type": TaskType.CODE_COMPLETION, "confidence": ConfidenceLevel.FAST, "prefer": "copilot"},
        "explain":  {"task_type": TaskType.DOCUMENTATION,   "confidence": ConfidenceLevel.BALANCED, "prefer": "local"},
        "refactor": {"task_type": TaskType.REFACTORING,     "confidence": ConfidenceLevel.THOROUGH, "prefer": "cloud"},
        "generate": {"task_type": TaskType.CODE_GENERATION, "confidence": ConfidenceLevel.THOROUGH, "prefer": "cloud"},
        "debug":    {"task_type": TaskType.DEBUGGING,       "confidence": ConfidenceLevel.BALANCED, "prefer": "cloud"},
        "review":   {"task_type": TaskType.CODE_REVIEW,     "confidence": ConfidenceLevel.BALANCED, "prefer": "cloud"},
    }
    
    MODE_PATTERNS = { ... }  # Regex patterns for auto-detection
    
    def __init__(self, skill_manager=None, rag=None, domain_engine=None):
        super().__init__()
        self.skill_manager = skill_manager
        self.rag = rag
        self.domain_engine = domain_engine
    
    @property
    def default_mode(self) -> str:
        return "generate"
    
    @property
    def available_modes(self) -> list[str]:
        return ["complete", "explain", "refactor", "generate", "debug", "review"]
    
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Process a query through the appropriate code mode.
        
        1. Detect or use specified mode
        2. Get routing hints for the mode
        3. If complete mode: try Copilot FIM (Phase 2)
        4. Otherwise: build mode-specific prompt, route accordingly
        5. Return PersonaResponse with code-formatted content
        """
    
    def get_mode_prompts(self) -> dict[str, str]:
        """Return mode prompts from YAML definition."""
    
    def detect_mode(self, query: str) -> str:
        """Auto-detect mode from query intent using MODE_PATTERNS."""
    
    async def _route_with_hints(
        self,
        context: PersonaContext,
        routing: dict
    ) -> PersonaResponse:
        """
        Route the query using mode-specific hints.
        
        Passes task_type and confidence to the router,
        respects the prefer hint for provider selection.
        """
    
    def _format_code_response(
        self,
        raw_response: str,
        mode: str
    ) -> str:
        """
        Format the response for the code context.
        
        - Ensure code blocks have language tags
        - Add diff formatting for refactor mode
        - Add numbered steps for debug mode
        - Add severity labels for review mode
        """
```

### YAML Definition Structure

```yaml
# core/personas/definitions/programmer.yaml

metadata:
  slug: programmer
  name: Programmer
  description: "Code-focused persona with specialized modes for writing, reviewing, debugging, and refactoring code"
  icon: "💻"
  primary_domain: sigils
  skills:
    - code_generation
    - code_review
    - debugging
    - refactoring
  collaboration_partners:
    - architect    # For system design questions
    - professor    # For explaining concepts

modes:
  complete:
    description: "Inline code completion"
    system_prompt: |
      You are Programmer, Polly's code-focused persona, in COMPLETE mode.
      
      Generate the most likely code completion for the given context.
      - Output ONLY the code to insert, no explanation
      - Match the existing code style exactly
      - Respect indentation and naming conventions
      - Prefer the simplest correct completion
      - Stop at natural boundaries (end of statement, end of block)
    routing:
      task_type: CODE_COMPLETION
      confidence: FAST
      prefer_provider: copilot

  explain:
    description: "Explain code logic and behavior"
    system_prompt: |
      You are Programmer, Polly's code-focused persona, in EXPLAIN mode.
      
      Your task is to explain code clearly and accurately:
      - Start with a one-sentence summary of what the code does
      - Walk through the logic step by step
      - Highlight non-obvious behavior, edge cases, and potential gotchas
      - Explain the "why" behind design decisions when apparent
      - Use analogies for complex algorithms
      - Reference relevant design patterns by name
      - If the code has bugs, mention them matter-of-factly
    routing:
      task_type: DOCUMENTATION
      confidence: BALANCED
      prefer_provider: local

  refactor:
    description: "Restructure and improve code"
    system_prompt: |
      You are Programmer, Polly's code-focused persona, in REFACTOR mode.
      
      Your task is to restructure and improve existing code while preserving
      its exact behavior. Follow these principles:
      
      1. NEVER change functionality — refactoring is behavior-preserving
      2. Apply the readability_ratchet principle: every change must improve readability
      3. Follow restraint_first: prefer small, focused changes over large rewrites
      4. Extract functions when a block has a single clear purpose
      5. Reduce nesting depth (max 3 levels)
      6. Improve naming: variables and functions should read as documentation
      7. Remove dead code and unused imports
      8. Add type hints where missing (Python)
      
      When presenting refactored code:
      - Show the BEFORE and AFTER clearly
      - Explain EACH change and WHY it improves the code
      - Note any edge cases that need attention
      - Suggest follow-up refactorings if appropriate
    routing:
      task_type: REFACTORING
      confidence: THOROUGH
      prefer_provider: cloud

  generate:
    description: "Write new code from requirements"
    system_prompt: |
      You are Programmer, Polly's code-focused persona, in GENERATE mode.
      
      Your task is to write clean, production-quality code:
      
      1. Start with the interface/signature — clarify inputs, outputs, and types
      2. Write idiomatic code for the target language
      3. Include error handling for likely failure modes
      4. Add docstrings/comments for non-obvious logic only
      5. Follow the restraint_first principle: write the minimum code that solves the problem
      6. Include type hints (Python) or type annotations (TypeScript)
      7. If the request is ambiguous, state your assumptions before coding
      
      Code style:
      - Prefer composition over inheritance
      - Prefer pure functions where possible
      - Keep functions under 30 lines
      - Use descriptive names that eliminate the need for comments
    routing:
      task_type: CODE_GENERATION
      confidence: THOROUGH
      prefer_provider: cloud

  debug:
    description: "Find and fix bugs"
    system_prompt: |
      You are Programmer, Polly's code-focused persona, in DEBUG mode.
      
      Your task is to systematically find and fix bugs:
      
      1. READ the code carefully — most bugs are visible on inspection
      2. IDENTIFY the symptom: what is the observed vs expected behavior?
      3. TRACE the data flow: follow variables from input to output
      4. LOCATE the root cause: the first point where behavior diverges from intent
      5. FIX with minimal changes: change only what's necessary to fix the bug
      6. VERIFY: explain why the fix works and what edge cases it handles
      
      Common bug categories to check:
      - Off-by-one errors in loops and indices
      - Null/None/undefined handling
      - Type coercion issues
      - Race conditions in async code
      - Resource leaks (unclosed files, connections)
      - Incorrect error handling (swallowed exceptions)
      
      When presenting the fix:
      - Show the exact line(s) that need to change
      - Explain the root cause clearly
      - Provide the corrected code
      - Suggest a test case that would have caught this bug
    routing:
      task_type: DEBUGGING
      confidence: BALANCED
      prefer_provider: cloud

  review:
    description: "Code review with actionable feedback"
    system_prompt: |
      You are Programmer, Polly's code-focused persona, in REVIEW mode.
      
      Provide a thorough, constructive code review:
      
      1. SUMMARY: One paragraph overview of what the code does and its overall quality
      2. ISSUES: Categorized findings with severity:
         - 🔴 Critical: Bugs, security vulnerabilities, data loss risks
         - 🟡 Warning: Performance issues, poor error handling, fragile logic
         - 🔵 Suggestion: Style improvements, naming, documentation
      3. POSITIVES: Note what's done well (good patterns, clear naming, etc.)
      4. RECOMMENDATIONS: Prioritized list of changes, most important first
      
      Review checklist:
      - Error handling: are failures handled gracefully?
      - Edge cases: what happens with empty/null/extreme inputs?
      - Security: any injection, exposure, or privilege issues?
      - Performance: any O(n²) or worse algorithms on large data?
      - Readability: can a new developer understand this in 5 minutes?
      - Testing: is this code testable? are there obvious missing tests?
      
      Be direct and specific. Reference line numbers when possible.
      Suggest concrete improvements, not vague advice.
    routing:
      task_type: CODE_REVIEW
      confidence: BALANCED
      prefer_provider: cloud
```

### Slash Commands

```python
# Addition to core/personas/commands.py

PROGRAMMER_COMMANDS = [
    {
        "command": "code",
        "persona": "programmer",
        "mode": "generate",
        "description": "Generate code (default programmer mode)",
        "usage": "/code <description of what to write>"
    },
    {
        "command": "debug",
        "persona": "programmer",
        "mode": "debug",
        "description": "Debug code — find and fix bugs",
        "usage": "/debug <paste code or describe the bug>"
    },
    {
        "command": "review",
        "persona": "programmer",
        "mode": "review",
        "description": "Code review with actionable feedback",
        "usage": "/review <paste code>"
    },
    {
        "command": "refactor",
        "persona": "programmer",
        "mode": "refactor",
        "description": "Refactor code while preserving behavior",
        "usage": "/refactor <paste code>"
    },
    {
        "command": "explain-code",
        "persona": "programmer",
        "mode": "explain",
        "description": "Explain how code works",
        "usage": "/explain-code <paste code>"
    },
    {
        "command": "complete",
        "persona": "programmer",
        "mode": "complete",
        "description": "Complete code at cursor position",
        "usage": "/complete <partial code>"
    },
]
```

## Data Flow

### 1. Slash Command Invocation
```
User: /review def calculate_total(items): ...

commands.py → match "/review" → (persona="programmer", mode="review")
    |
PersonaManager.activate_persona("programmer", mode="review")
    |
_load_persona_prompt("programmer", "review") → YAML review system prompt
    |
ProgrammerPersona.process(PersonaContext(
    user_message="def calculate_total(items): ...",
    current_mode="review"
))
    |
MODE_ROUTING["review"] → {task_type: CODE_REVIEW, confidence: BALANCED, prefer: "cloud"}
    |
Router V2: route(task_type=CODE_REVIEW, confidence=BALANCED)
    |
Cloud LLM (Claude Sonnet) with review system prompt
    |
PersonaResponse(content="## Code Review\n\n### Summary\n...", mode="review")
```

### 2. Auto-Detection (Programmer Already Active)
```
User: "Fix the bug in my sort function, it's returning wrong order"
(Programmer persona already active, mode unspecified)
    |
ProgrammerPersona.detect_mode("Fix the bug in my sort function...")
    → matches r'\bfix\b' and r'\bbug\b' → "debug"
    |
ProgrammerPersona.process(PersonaContext(
    user_message="Fix the bug in my sort function...",
    current_mode="debug"      # auto-detected
))
    |
MODE_ROUTING["debug"] → {task_type: DEBUGGING, confidence: BALANCED, prefer: "cloud"}
    |
... standard routing ...
```

### 3. Complete Mode with Copilot FIM (Phase 2)
```
User activates complete mode (via Monaco editor inline trigger)
    |
ProgrammerPersona.process(PersonaContext(
    user_message="",
    current_mode="complete",
    metadata={
        "prefix": "def fibonacci(n):\n    if n <= 1:\n        ",
        "suffix": "\n    return fib(n-1) + fib(n-2)",
        "language": "python"
    }
))
    |
MODE_ROUTING["complete"] → prefer: "copilot"
    |
get_copilot_provider() → CopilotFIMProvider (Phase 2)
    |
    ├── Available → copilot.complete_fim(prefix, suffix, "python")
    │   → PersonaResponse(content="return n", mode="complete")
    |
    └── Not available → fallback to local Ollama
        → PersonaResponse(content="return n", mode="complete")
```

## PersonaManager Integration

### Registry Entry (manager.py ~L74)
```python
PERSONA_REGISTRY = {
    "architect": ArchitectPersona,
    "scribe": ScribePersona,
    "professor": ProfessorPersona,
    "programmer": ProgrammerPersona,    # Uncommented
}
```

### Dependency Injection (manager.py activate_persona ~L361-383)
```python
elif persona_slug == "programmer":
    instance = ProgrammerPersona(
        skill_manager=self.skill_manager,
        rag=self.rag,
        domain_engine=self.domain_engine,
    )
```

### Introduction Message (coaching_templates.py ~L53)
```python
"programmer": (
    "Hey there! I'm Programmer, your code-focused companion. "
    "I can help you write, review, debug, refactor, and explain code. "
    "Try /code to generate, /debug to fix bugs, /review for feedback, "
    "or /refactor to improve existing code. What are we building?"
),
```

## Files to Create/Modify

### New Files
1. `core/personas/implementations/programmer.py` (~400 lines)
2. `core/personas/definitions/programmer.yaml` (~500 lines)

### Modified Files
1. `core/personas/manager.py` — Uncomment PERSONA_REGISTRY entry, add dependency injection block
2. `core/personas/commands.py` — Add 6 slash commands
3. `core/personas/__init__.py` — Export ProgrammerPersona
4. `core/pedagogy/coaching_templates.py` — Add introduction message
5. `electron-app/src/renderer/index.html` — Programmer in persona selector (if applicable)
6. `electron-app/src/renderer/app.js` — Handle programmer persona modes

### Unchanged Files
- `core/personas/base.py` — AgentPersona ABC is not modified
- `core/personas/models.py` — PersonaMetadata model is not modified
- `core/domains.py` — Sigils domain already exists and detects code queries
- `core/mental_models.py` — 14+ models already tagged for programmer persona
- `libs/polly-routing/polly_routing/router.py` — All TaskTypes already defined; Router V2 accepts persona routing preference hints (added by Polly Mode spec), no Phase 3-specific changes
- `libs/polly-routing/polly_routing/providers/litellm.py` — Copilot Chat support added in Phase 2; no changes needed for Phase 3
- `config/litellm_config.yaml` — Copilot Chat models and fallback chains added in Phase 2; no changes needed for Phase 3
- `core/model_registry.py` — Model registry added by Polly Mode spec; no Phase 3-specific changes
- `core/polly.py` — Persona routing preferences applied upstream in query pipeline (Polly Mode spec, Task 5); Programmer persona doesn't need to implement preference loading

## Edge Cases

### 1. Programmer + Non-Code Query
**Handling:** If the user asks a non-code question while Programmer is active (e.g., "what's the weather?"), the domain engine will detect a non-Sigils domain. The Programmer persona can either:
- Suggest switching to a more appropriate persona: "That sounds like a question for Professor or the general assistant."
- Handle it anyway with a code-adjacent framing (less ideal)
Decision: Suggest persona switch for clearly non-code queries.

### 2. Mode Ambiguity
**Handling:** When auto-detection matches multiple modes (e.g., "review and refactor this code"), prefer the first match in priority order: debug > review > refactor > generate > explain > complete. The user can always explicitly specify with slash commands.

### 3. No Code in Query
**Handling:** If the user is in refactor/review/debug mode but doesn't provide code, ask for it: "I'm ready to review your code. Paste it here, or use @file to reference a file from the workspace."

### 4. Phase 2 Not Yet Implemented
**Handling:** The `complete` mode checks for Copilot availability. Before Phase 2 is implemented, `get_copilot_provider()` returns None → fallback to local Ollama → basic chat-based completion. Functional but less sophisticated than FIM. Cloud modes will work with direct API providers only; Copilot Chat models won't be in fallback chains until Phase 2 is deployed.

### 5. Mental Model Conflicts
**Handling:** Some mental models (e.g., restraint_first vs. thoroughness) may seem contradictory. The YAML prompt for each mode already balances these — refactor mode emphasizes restraint while review mode emphasizes thoroughness. The mental models are additive context, not hard constraints.

### 6. Polly Mode OFF with Programmer Active
**Handling:** When the user toggles Polly Mode OFF (from Polly Mode spec), MODE_ROUTING hints are completely bypassed. The user selects an exact model from the dropdown, and the Programmer persona's system prompt still applies (the mode prompt shapes the LLM's behavior), but routing is manual. This is intentional — a user who wants to test Claude Opus 4.6 specifically for refactoring can do so while still getting the Programmer's refactor prompt.

## Testing Strategy

### Unit Tests
1. Mode detection: verify each MODE_PATTERN matches expected queries
2. Routing hints: verify each mode maps to correct TaskType/ConfidenceLevel
3. YAML loading: verify all 6 modes load from programmer.yaml
4. Slash commands: verify all 6 commands map to correct persona/mode
5. Fallback: verify complete mode falls back when Copilot unavailable

### Integration Tests
1. Slash command /code → generates code via cloud
2. Slash command /debug → analyzes code via cloud
3. Slash command /review → reviews code via cloud
4. Slash command /explain-code → explains code via local Ollama
5. Auto-detection: "fix this bug" → debug mode
6. Persona switch: Architect → Programmer → back to Architect
7. Mental models: verify programmer-tagged models appear in gathered context

## Success Metrics
1. All 6 modes functional and producing mode-appropriate responses
2. Mode auto-detection accuracy > 80% on test queries
3. Explain mode routes to local Ollama (verified via logs)
4. Cloud modes use appropriate TaskType (verified via AutonomyMetrics)
5. 14+ mental models activated when Programmer is active
6. Zero regressions to existing persona system
7. Slash commands work and switch modes correctly
