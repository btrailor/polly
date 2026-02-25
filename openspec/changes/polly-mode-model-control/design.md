# Design: Polly Mode Toggle + Granular Model Control

## Overview
Replace Polly's current provider:tier model selector with a clean two-state system: **Polly Mode ON** (intelligent auto-routing shaped by per-persona preferences) vs. **Polly Mode OFF** (direct model selection from a comprehensive dropdown). Token conservation pipelines (cache, distillation) remain active in both modes.

## Architecture

### State Diagram
```
┌────────────────────────────────────────────────────────────────┐
│                     POLLY MODE ON (default)                    │
│                                                                │
│  Model dropdown: HIDDEN                                        │
│  Routing: Router V2 (tier + persona preferences + budget)      │
│  Cache: ACTIVE                                                 │
│  Distillation: ACTIVE                                          │
│  Fallback chains: ACTIVE                                       │
│                                                                │
│  ┌──────────────────────────────────────────┐                  │
│  │ Persona Routing Preferences (Settings)   │                  │
│  │  ├── Cloud provider preference           │                  │
│  │  ├── Local model preference              │                  │
│  │  └── Per-mode overrides (optional)       │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                │
│  Query → Persona prefs applied → Router V2 picks model → LLM  │
└────────────────────────────────────────────────────────────────┘
                           │
                      [Toggle]
                           │
┌────────────────────────────────────────────────────────────────┐
│                     POLLY MODE OFF                             │
│                                                                │
│  Model dropdown: VISIBLE (all available models)                │
│  Routing: BYPASSED (direct to selected model)                  │
│  Cache: ACTIVE (still checks/stores)                           │
│  Distillation: ACTIVE (still compresses context)               │
│  Fallback chains: DISABLED (selected model only)               │
│                                                                │
│  Query → Cache check → Distillation → Selected model → LLM    │
└────────────────────────────────────────────────────────────────┘
```

### Component Interaction
```
┌─────────────────────────────────────┐
│        Chat Input Area              │
│                                     │
│  [Persona ▾] [Polly Mode ●○]       │
│                                     │
│  (Polly Mode OFF only:)            │
│  [Claude Opus 4.6 (Copilot) ▾]    │
│                                     │
│  [Message input..................]  │
│  [Send]                             │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  server.py POST /polly/query         │
│                                      │
│  polly_mode: bool                    │
│  model_override: Optional[str]       │  ← null when Polly Mode ON
│  confidence: Optional[str]           │  ← from persona prefs when ON
│  provider_override: Optional[str]    │  ← from persona prefs when ON
│                                      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  polly.py query()                    │
│                                      │
│  if model_override:                  │
│    skip Router V2                    │
│    → cache check → distill →         │
│    → direct LLM call to exact model  │
│  else:                               │
│    apply persona routing prefs       │
│    → cache check → distill →         │
│    → Router V2 (with pref hints) →   │
│    → fallback chain → LLM            │
└──────────────────────────────────────┘
```

## Key Design Decisions

### 1. Polly Mode Toggle — Binary State, System-Wide
**Decision:** A single toggle that applies globally across all personas and general chat. When ON, model selection is fully automated. When OFF, the user selects the exact model.

**Rationale:**
- The existing 27-option provider:tier dropdown is confusing. Users don't think in terms of "anthropic:thorough" — they think in terms of "Claude Opus" or "let Polly decide."
- A binary toggle maps to a clear mental model: "Am I in control, or is Polly in control?"
- The toggle state persists in `sessionStorage` (per browser session) and can optionally be saved as a user default in `config.yaml`

**Toggle behavior:**
- **Default:** ON (Polly Mode active)
- **Persistence:** `sessionStorage` for session, `config.yaml` for default preference
- **Visual:** Compact toggle inline with the persona selector. When ON, a subtle "Polly" indicator shows. When OFF, the model dropdown appears in the same row.

### 2. Model Dropdown — Complete, Grouped, Individual Models
**Decision:** When Polly Mode is OFF, show a dropdown listing every individual model (not provider:tier combos), grouped by source.

**Rationale:**
- Users who turn off Polly Mode want precision. They should see the exact model name.
- Grouping by source helps distinguish between the same model accessed different ways (e.g., Claude Opus 4.6 via Copilot subscription vs. Anthropic direct API)
- Cost indicator (free/$/$$/$$$) helps users make informed choices without showing exact pricing

**Dropdown structure:**
```
[optgroup: "Copilot Chat"]
  GPT-5 mini                    free
  GPT-4.1                       free
  GPT-4.1-mini                  free
  Grok Code Fast 1              $
  Gemini 3 Flash                $
  GPT-5.2                       $$
  Claude Sonnet 4.6             $$
  Gemini 2.5 Pro                $$
  Gemini 3 Pro                  $$
  Claude Opus 4.6               $$$
  GPT-5.3-Codex                 $$$

[optgroup: "Anthropic (Direct)"]
  Claude 3 Haiku                $
  Claude Sonnet 4               $$
  Claude Opus 4                 $$$

[optgroup: "OpenAI (Direct)"]
  GPT-3.5 Turbo                 $
  GPT-4 Turbo                   $$
  GPT-4o                        $$
  GPT-4o-mini                   $

[optgroup: "GitHub Models"]
  GPT-4o (via GitHub)           $
  GPT-4o-mini (via GitHub)      $

[optgroup: "Gemini (Direct)"]
  Gemini 1.5 Flash              $
  Gemini 1.5 Flash 8B           $
  Gemini 1.5 Pro                $$

[optgroup: "Mistral (Direct)"]
  Mistral Small                 $
  Mistral Medium                $$
  Mistral Large                 $$$

[optgroup: "Local (Ollama)"]
  llama3.2:3b                   local
  llama3.1:7b                   local
  llama3.1:70b                  local
```

**Model list source:** `GET /models/available` endpoint that aggregates:
1. All LiteLLM providers from `litellm_config.yaml` (expanded to individual models)
2. Copilot Chat models (if authenticated) from `copilot.chat.models` config
3. Local Ollama models from Ollama API (`/api/tags`)
4. Only models whose provider is enabled and has valid credentials

**Cost indicator mapping:**
- `free` — 0x Copilot multiplier or free tier
- `$` — cheap (< $1/M tokens or < 0.5x multiplier)
- `$$` — standard (< $10/M tokens or 1x multiplier)
- `$$$` — premium (>= $10/M tokens or >= 3x multiplier)
- `local` — runs on local hardware

### 3. Model Override in Query Pipeline
**Decision:** Add `model_override` parameter to the query pipeline. When set, bypass Router V2 but keep cache and distillation active.

**Rationale:**
- Cache and distillation are model-agnostic optimizations — they reduce redundant work regardless of which model is targeted
- Bypassing only routing (not conservation) means Polly Mode OFF is still token-efficient
- If the selected model fails, the request fails — no silent fallback to another model (user chose explicitly)

**Pipeline with model_override:**
```python
async def query(self, ..., model_override: Optional[str] = None):
    # Phase 0: Cache check (ALWAYS)
    cached = await self.cache.check(query_hash)
    if cached:
        return cached  # Served from cache regardless of model choice
    
    # Phase 1: Distillation (ALWAYS, if enabled)
    context = await self.distill(context)
    
    if model_override:
        # DIRECT: Skip Router V2, call model directly
        provider, model = self._resolve_model_override(model_override)
        response = await provider.complete(messages, model=model)
        # Record as user-directed in metrics
        self._record_routing_decision(route_type="user_override", model=model_override)
    else:
        # AUTO: Router V2 with persona preferences
        response = await self._auto_route(messages, persona_prefs, ...)
```

**_resolve_model_override(model_id):**
Maps the full model ID to the correct provider adapter:
- `copilot_chat/claude-opus-4.6` → CopilotChat adapter, model `claude-opus-4.6`
- `anthropic/claude-opus-4-20250514` → Anthropic adapter, model `claude-opus-4-20250514`
- `ollama/llama3.1:7b` → Ollama/local adapter, model `llama3.1:7b`
- `github/openai/gpt-4o` → GitHub Models adapter, model `openai/gpt-4o`

### 4. Persona Routing Preferences — Layered Defaults
**Decision:** Three-layer preference system: (1) persona default, (2) per-mode override, (3) per-request override (Polly Mode OFF). Each layer overrides the one above it.

**Layers:**
```
Layer 3 (highest): User turns off Polly Mode → picks exact model → overrides everything
Layer 2:          Per-mode override in Settings → overrides persona default for that mode
Layer 1:          Per-persona default in Settings → shapes all auto-routing for that persona
Layer 0 (base):   Router V2 defaults (fallback chains, tier assignment, budget)
```

**Preference structure per persona:**
```yaml
persona_routing_preferences:
  programmer:
    cloud_provider: copilot_chat      # Prefer Copilot Chat for cloud routing
    local_model: null                 # Use system default (llama3.1:7b)
    mode_overrides:
      refactor:
        cloud_provider: anthropic     # Refactor specifically prefers Anthropic
        cloud_model: claude-opus-4-20250514  # Specific model for refactor
      explain:
        prefer_local: true            # Explain prefers local routing
        local_model: null             # Use persona default
      complete:
        cloud_provider: copilot_chat  # Complete uses Copilot FIM (handled by Phase 2)
  
  scribe:
    cloud_provider: null              # No preference, use Router V2 default
    local_model: null                 # Use system default
    mode_overrides: {}
  
  professor:
    cloud_provider: null
    local_model: null
    mode_overrides:
      explain:
        prefer_local: true            # Professor explain stays local
      socratic:
        prefer_local: true            # Socratic stays local
  
  architect:
    cloud_provider: null
    local_model: null
    mode_overrides: {}
  
  default:                            # For general chat (no persona active)
    cloud_provider: null
    local_model: null
```

**How preferences influence Router V2:**
```python
def _apply_persona_preferences(self, routing_decision, prefs, mode=None):
    """
    Apply persona routing preferences to a Router V2 decision.
    
    Preferences are SOFT — they reorder candidates, not hard-override.
    If the preferred provider is unavailable/over-budget, the router
    falls through to the next candidate as normal.
    """
    # Check for mode-specific override first
    mode_prefs = prefs.get("mode_overrides", {}).get(mode, {})
    
    # Merge: mode overrides > persona defaults
    cloud_provider = mode_prefs.get("cloud_provider") or prefs.get("cloud_provider")
    local_model = mode_prefs.get("local_model") or prefs.get("local_model")
    prefer_local = mode_prefs.get("prefer_local", False)
    cloud_model = mode_prefs.get("cloud_model")
    
    if prefer_local:
        # Boost local model to top of candidate list
        routing_decision.boost_local(model=local_model)
    elif cloud_provider:
        # Boost candidates from preferred provider to top
        routing_decision.boost_provider(cloud_provider)
    
    if cloud_model:
        # Pin to specific model (strongest preference short of model_override)
        routing_decision.pin_model(cloud_model)
    
    return routing_decision
```

**Key distinction:** Persona preferences are *soft* — they reorder the candidate list, boosting preferred providers/models to the front. If the preferred option is unavailable (down, rate-limited, over budget), the normal fallback chain kicks in. This is different from `model_override` (Polly Mode OFF) which is *hard* — no fallback.

### 5. Default Preferences — Optimized Per Persona
**Decision:** Ship with sensible defaults that users can change. Defaults reflect each persona's domain expertise.

**Defaults:**
```yaml
persona_routing_preferences:
  programmer:
    cloud_provider: copilot_chat      # Best code models at subscription price
    local_model: null                 # System default (future: code-optimized local model)
    mode_overrides:
      explain:
        prefer_local: true            # Explanation is local-capable
      complete:
        cloud_provider: copilot_chat  # FIM uses Copilot
  
  scribe:
    cloud_provider: null              # No preference — Scribe works well with any model
    local_model: null
    mode_overrides: {}
  
  professor:
    cloud_provider: null              # No preference
    local_model: null
    mode_overrides:
      explain:
        prefer_local: true            # Explanations stay local when possible
      socratic:
        prefer_local: true            # Socratic dialogue stays local
  
  architect:
    cloud_provider: null              # No preference (Architect needs reasoning models)
    local_model: null
    mode_overrides: {}
  
  default:
    cloud_provider: null
    local_model: null
```

### 6. Override Tracking in Metrics
**Decision:** Add a `routing_source` field to routing decisions: `auto`, `auto_with_prefs`, `user_override`.

**Rationale:**
- Phase 11 planning docs already identify "Did user explicitly override routing decision?" as a planned metric
- Tracking overrides helps Polly learn: if a user consistently overrides to Claude Opus for refactoring, the pattern learning system can incorporate that into auto-routing

**Schema change (autonomy_metrics.py, routing_decisions table):**
```sql
ALTER TABLE routing_decisions ADD COLUMN routing_source TEXT DEFAULT 'auto';
-- Values: 'auto', 'auto_with_prefs', 'user_override'

ALTER TABLE routing_decisions ADD COLUMN user_selected_model TEXT DEFAULT NULL;
-- Non-null when routing_source = 'user_override'
```

**Pattern learning integration:**
When `routing_source = 'user_override'`, record a `ROUTING_OUTCOME` pattern with high confidence. Over time, if the user consistently picks Claude Opus for refactoring, Polly Mode ON can learn to prefer it automatically for that persona + mode + query type.

## API Design

### GET /models/available
```python
@app.get("/models/available")
async def get_available_models():
    """
    Return all connected models with metadata.
    
    Used by the frontend to populate the model dropdown when Polly Mode is OFF.
    Also used by Settings to show available models for persona preferences.
    
    Returns:
        {
            "models": [
                {
                    "id": "copilot_chat/claude-opus-4.6",
                    "name": "Claude Opus 4.6",
                    "provider": "Copilot Chat",
                    "provider_key": "copilot_chat",
                    "capabilities": ["chat", "code", "analysis", "reasoning"],
                    "context_length": 200000,
                    "cost_tier": "$$$",
                    "cost_detail": "3x premium request",
                    "available": true
                },
                {
                    "id": "anthropic/claude-opus-4-20250514",
                    "name": "Claude Opus 4",
                    "provider": "Anthropic (Direct)",
                    "provider_key": "anthropic",
                    "capabilities": ["chat", "code", "analysis", "planning", "reasoning"],
                    "context_length": 200000,
                    "cost_tier": "$$$",
                    "cost_detail": "$15/$75 per M tokens",
                    "available": true
                },
                {
                    "id": "ollama/llama3.1:7b",
                    "name": "llama3.1:7b",
                    "provider": "Local (Ollama)",
                    "provider_key": "ollama",
                    "capabilities": ["chat", "code"],
                    "context_length": 128000,
                    "cost_tier": "local",
                    "cost_detail": "runs locally",
                    "available": true
                },
                ...
            ],
            "groups": [
                {"key": "copilot_chat", "label": "Copilot Chat", "order": 1},
                {"key": "anthropic", "label": "Anthropic (Direct)", "order": 2},
                {"key": "openai", "label": "OpenAI (Direct)", "order": 3},
                {"key": "github", "label": "GitHub Models", "order": 4},
                {"key": "gemini", "label": "Gemini (Direct)", "order": 5},
                {"key": "mistral", "label": "Mistral (Direct)", "order": 6},
                {"key": "grok", "label": "Grok (Direct)", "order": 7},
                {"key": "perplexity", "label": "Perplexity", "order": 8},
                {"key": "openrouter", "label": "OpenRouter", "order": 9},
                {"key": "ollama", "label": "Local (Ollama)", "order": 10}
            ]
        }
    """
```

### Modified QueryRequest
```python
class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    # Existing fields
    confidence: Optional[str] = None          # Tier hint (fast/balanced/thorough)
    provider_override: Optional[str] = None   # Legacy: provider-level override
    # New fields
    polly_mode: bool = True                   # True = auto routing, False = direct model
    model_override: Optional[str] = None      # Exact model ID when polly_mode=False
```

### Persona Routing Preferences API
```python
@app.get("/settings/persona-routing")
async def get_persona_routing_preferences():
    """
    Get all persona routing preferences.
    
    Returns:
        {
            "preferences": {
                "programmer": {
                    "cloud_provider": "copilot_chat",
                    "local_model": null,
                    "mode_overrides": {
                        "explain": {"prefer_local": true},
                        "refactor": {"cloud_provider": "anthropic", "cloud_model": "claude-opus-4-20250514"}
                    }
                },
                ...
            },
            "available_providers": ["copilot_chat", "anthropic", "openai", ...],
            "available_local_models": ["llama3.2:3b", "llama3.1:7b", ...],
            "personas": [
                {"slug": "programmer", "name": "Programmer", "modes": ["complete", "explain", "refactor", "generate", "debug", "review"]},
                {"slug": "scribe", "name": "Scribe", "modes": ["capture", "organize", "enrich", "edit"]},
                ...
            ]
        }
    """

@app.put("/settings/persona-routing/{persona_slug}")
async def update_persona_routing(persona_slug: str, prefs: PersonaRoutingPrefs):
    """
    Update routing preferences for a specific persona.
    
    Body:
        {
            "cloud_provider": "copilot_chat",
            "local_model": null,
            "mode_overrides": {
                "refactor": {"cloud_model": "claude-opus-4-20250514"}
            }
        }
    """
```

## Settings UI — Persona Routing Preferences

### Layout in Settings Panel
```
┌─────────────────────────────────────────────────────────────────┐
│  Routing Preferences                                            │
│                                                                 │
│  Default Polly Mode: [● ON / ○ OFF]                            │
│  (When ON, Polly selects models automatically using these       │
│   preferences. When OFF, you choose the model directly.)       │
│                                                                 │
│  ┌─── Programmer ─────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  Cloud provider:  [Copilot Chat ▾]                     │    │
│  │  Local model:     [System default ▾]                   │    │
│  │                                                         │    │
│  │  Mode overrides:  [+ Add override]                     │    │
│  │                                                         │    │
│  │  ┌─ refactor ──────────────────────────────────────┐   │    │
│  │  │  Cloud: [Anthropic ▾]  Model: [Claude Opus 4 ▾] │   │    │
│  │  │  [Remove]                                        │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  ┌─ explain ───────────────────────────────────────┐   │    │
│  │  │  [✓] Prefer local model                          │   │    │
│  │  │  [Remove]                                        │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── Scribe ─────────────────────────────────────────────┐    │
│  │  Cloud provider:  [Auto (no preference) ▾]             │    │
│  │  Local model:     [System default ▾]                   │    │
│  │  Mode overrides:  [+ Add override]                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── Professor ──────────────────────────────────────────┐    │
│  │  Cloud provider:  [Auto (no preference) ▾]             │    │
│  │  Local model:     [System default ▾]                   │    │
│  │  Mode overrides:  [+ Add override]                     │    │
│  │  ┌─ explain ──────────────────────────────────────┐    │    │
│  │  │  [✓] Prefer local model                         │    │    │
│  │  │  [Remove]                                       │    │    │
│  │  └────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── Architect ──────────────────────────────────────────┐    │
│  │  Cloud provider:  [Auto (no preference) ▾]             │    │
│  │  Local model:     [System default ▾]                   │    │
│  │  Mode overrides:  [+ Add override]                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── General Chat ───────────────────────────────────────┐    │
│  │  Cloud provider:  [Auto (no preference) ▾]             │    │
│  │  Local model:     [System default ▾]                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Reset to Defaults]                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Mode Override Add Flow
```
User clicks [+ Add override] on Programmer
  ↓
Mini dropdown appears: [Select mode ▾]
  → complete, explain, refactor, generate, debug, review
  ↓
User selects "refactor"
  ↓
Override row appears with:
  Cloud: [provider dropdown]  Model: [model dropdown]
  [✓] Prefer local model (checkbox)
  [Remove] button
```

## Chat Input Area — Toggle + Dropdown

### Polly Mode ON (default)
```
┌──────────────────────────────────────────────────────────────┐
│  [Programmer ▾]  [● Polly]                                   │
│                                                               │
│  [Type your message...                                    ]   │
│  [Send]                                                       │
└──────────────────────────────────────────────────────────────┘
```
- Persona selector on the left
- "Polly" toggle on the right, visually active (filled/highlighted)
- No model dropdown visible
- Clean, minimal

### Polly Mode OFF
```
┌──────────────────────────────────────────────────────────────┐
│  [Programmer ▾]  [○ Polly]  [Claude Opus 4.6 (Copilot) ▾]  │
│                                                               │
│  [Type your message...                                    ]   │
│  [Send]                                                       │
└──────────────────────────────────────────────────────────────┘
```
- "Polly" toggle dimmed/inactive
- Model dropdown appears inline
- Dropdown shows individual models grouped by source

### Response Metadata (both modes)
```
✓ claude-opus-4.6 (copilot_chat) • 3x premium • 2,847 tokens
  → user selected | copilot chat
```
or when in Polly Mode:
```
✓ claude-opus-4.6 (copilot_chat) • 3x premium • 2,847 tokens
  → polly auto (programmer prefs) | thorough tier | copilot chat
```

The metadata footer already exists (`app.js:8558-8586`). The change is adding routing source info: "user selected" vs. "polly auto" with preference context.

## Data Flow

### 1. Polly Mode ON — Auto Routing with Preferences
```
User sends query (Programmer persona, refactor mode, Polly Mode ON)
    │
Frontend: queryOptions = {
    polly_mode: true,
    model_override: null,
    confidence: null,     # Let persona prefs decide
    provider_override: null
}
    │
    ▼
server.py → polly.query(polly_mode=True)
    │
[Phase 0] Cache check (query hash)
    │ MISS
    ▼
polly.py: Load persona routing prefs for "programmer"
    │
    ├── Mode override for "refactor"?
    │   → Yes: cloud_provider="anthropic", cloud_model="claude-opus-4-20250514"
    │
[Phase 1] Context distillation
    │
    ▼
Router V2: route(task_type=REFACTORING, confidence=THOROUGH)
    │
    ├── Candidates: [anthropic/claude-opus-4-20250514, copilot_chat/claude-opus-4.6,
    │                github/openai/gpt-4o, anthropic/claude-sonnet-4-20250514, ...]
    │
    ├── Apply persona prefs: boost anthropic, pin claude-opus-4-20250514
    │   → Reordered: [anthropic/claude-opus-4-20250514, copilot_chat/claude-opus-4.6, ...]
    │
    ├── anthropic/claude-opus-4-20250514 available? → YES → use it
    │
    ▼
Response: {content, metadata: {provider: "anthropic", model: "claude-opus-4-20250514",
           routing_source: "auto_with_prefs"}}
```

### 2. Polly Mode OFF — Direct Model Selection
```
User sends query (Programmer persona, selects "Claude Opus 4.6 (Copilot)")
    │
Frontend: queryOptions = {
    polly_mode: false,
    model_override: "copilot_chat/claude-opus-4.6",
    confidence: null,
    provider_override: null
}
    │
    ▼
server.py → polly.query(polly_mode=False, model_override="copilot_chat/claude-opus-4.6")
    │
[Phase 0] Cache check (query hash — same cache, model is part of key)
    │ MISS
    ▼
[Phase 1] Context distillation (still runs)
    │
    ▼
polly.py: _resolve_model_override("copilot_chat/claude-opus-4.6")
    → provider=CopilotChat, model="claude-opus-4.6"
    │
    ▼
Direct call: CopilotChat.complete(messages, model="claude-opus-4.6")
    │
    ├── If fails: return error (no fallback — user chose explicitly)
    │
    ▼
Response: {content, metadata: {provider: "copilot_chat", model: "claude-opus-4.6",
           routing_source: "user_override", user_selected_model: "copilot_chat/claude-opus-4.6"}}
```

### 3. Polly Mode ON — No Persona Preferences Set
```
User sends query (Scribe persona, no prefs configured)
    │
polly.py: Load persona routing prefs for "scribe"
    → cloud_provider: null, local_model: null, mode_overrides: {}
    │
Router V2: route() with NO preference hints
    → Uses default fallback chain for the tier
    → Same behavior as today
```

## Configuration

### config.yaml Addition
```yaml
polly_mode:
  default_enabled: true          # Polly Mode ON by default

persona_routing_preferences:
  programmer:
    cloud_provider: copilot_chat
    local_model: null
    mode_overrides:
      explain:
        prefer_local: true
      complete:
        cloud_provider: copilot_chat
  scribe:
    cloud_provider: null
    local_model: null
    mode_overrides: {}
  professor:
    cloud_provider: null
    local_model: null
    mode_overrides:
      explain:
        prefer_local: true
      socratic:
        prefer_local: true
  architect:
    cloud_provider: null
    local_model: null
    mode_overrides: {}
  default:
    cloud_provider: null
    local_model: null
```

### core/config.py DEFAULT_CONFIG Addition
```python
"polly_mode": {
    "default_enabled": True,
},
"persona_routing_preferences": {
    "programmer": {
        "cloud_provider": "copilot_chat",
        "local_model": None,
        "mode_overrides": {
            "explain": {"prefer_local": True},
            "complete": {"cloud_provider": "copilot_chat"},
        },
    },
    "scribe": {
        "cloud_provider": None,
        "local_model": None,
        "mode_overrides": {},
    },
    "professor": {
        "cloud_provider": None,
        "local_model": None,
        "mode_overrides": {
            "explain": {"prefer_local": True},
            "socratic": {"prefer_local": True},
        },
    },
    "architect": {
        "cloud_provider": None,
        "local_model": None,
        "mode_overrides": {},
    },
    "default": {
        "cloud_provider": None,
        "local_model": None,
    },
}
```

## Files to Create/Modify

### New Files
1. `core/model_registry.py` (~200 lines) — Aggregates all available models from all providers into a unified list with metadata. Powers `GET /models/available`.

### Modified Files
1. `interfaces/server.py` — Add `GET /models/available`, accept `polly_mode` and `model_override` in QueryRequest
2. `core/polly.py` — Handle `model_override` in query pipeline, apply persona routing prefs, `_resolve_model_override()`
3. `libs/polly-routing/polly_routing/router.py` — Accept `provider_hint`, `model_hint` to influence candidate ordering
4. `core/config.py` — Add `polly_mode` and `persona_routing_preferences` to DEFAULT_CONFIG
5. `config.yaml` — Add default persona routing preferences
6. `core/autonomy_metrics.py` — Add `routing_source` and `user_selected_model` columns
7. `interfaces/settings_api.py` — Persona routing preferences CRUD endpoints
8. `electron-app/src/renderer/index.html` — Replace model selector with Polly Mode toggle + conditional dropdown
9. `electron-app/src/renderer/app.js` — Toggle logic, model list fetching, dropdown population, preference UI
10. `electron-app/src/renderer/styles/main.css` — Toggle and dropdown styling
11. `electron-app/src/main/main.js` — IPC handlers for model list and preferences

### Unchanged Files
- `libs/polly-routing/polly_routing/providers/litellm.py` — Provider adapters unchanged; model_override resolves to the same adapter calls
- `libs/polly-routing/polly_routing/budget.py` — Budget tracking unchanged; direct model calls still record usage
- `core/compression/` — Distillation pipeline unchanged; runs in both modes
- `core/personas/` — Persona implementations unchanged; preferences are external to persona code

## Edge Cases

### 1. Selected Model Unavailable
**Handling:** When Polly Mode is OFF and the selected model is unavailable (provider down, rate limited, credentials expired), return an error to the user: "Claude Opus 4.6 (Copilot) is currently unavailable. Turn on Polly Mode for automatic fallback, or select a different model." No silent fallback.

### 2. Copilot Not Authenticated But Copilot Chat Model Selected
**Handling:** Copilot Chat models only appear in the dropdown when Copilot is authenticated. If auth expires between page load and request, return: "Copilot session expired. Reconnect in Settings." Model list refreshes on toggle or can be manually refreshed.

### 3. Persona Changes While Polly Mode ON
**Handling:** When the user switches personas, the routing preferences update to the new persona's config. No user action needed — the toggle state (ON/OFF) persists, but the routing behavior changes to match the new persona.

### 4. No Preferences Set
**Handling:** When no preferences are configured for a persona, routing falls back to Layer 0 (Router V2 defaults). This is identical to today's behavior. The feature is opt-in for customization.

### 5. Conflicting Preferences
**Handling:** Mode override always wins over persona default. If Programmer defaults to `copilot_chat` but Programmer/refactor overrides to `anthropic`, refactor uses Anthropic. Other modes use Copilot Chat.

### 6. Local Model Preference But Local Unavailable
**Handling:** If `prefer_local: true` is set but the local model isn't running (Ollama offline), the preference is ignored and cloud routing proceeds as normal. The preference is a soft hint, not a hard requirement.

### 7. Model Override With Cache Hit
**Handling:** Cache key includes the model ID when `model_override` is set. This means cache hits are model-specific: a cached response from Claude Opus won't be served when the user selects GPT-5.2. When Polly Mode is ON, cache key does NOT include the model (since the model varies by routing decision).

## Testing Strategy

### Unit Tests
1. Polly Mode toggle persists in sessionStorage
2. Model dropdown populates from /models/available response
3. model_override bypasses Router V2 in query pipeline
4. Persona preferences loaded from config
5. Mode override takes priority over persona default
6. _resolve_model_override maps all provider prefixes correctly
7. routing_source recorded correctly (auto, auto_with_prefs, user_override)
8. Cache key includes model when model_override is set

### Integration Tests
1. Full flow: Polly Mode OFF → select model → query → response shows selected model
2. Full flow: Polly Mode ON → persona prefs applied → response shows auto-selected model
3. Persona switch: change persona → preferences update
4. Model unavailable: Polly Mode OFF → selected model down → error returned (no fallback)
5. Preferences CRUD: save prefs → restart → prefs loaded
6. Model list: reflects all connected providers and models

## Success Metrics
1. Polly Mode toggle functional and persists across page reloads
2. Model dropdown shows all available models from all connected providers
3. Direct model selection works end-to-end (query → exact model → response)
4. Persona preferences shape auto-routing without breaking fallback chains
5. Override tracking accurately distinguishes auto vs. user-directed
6. Cache and distillation remain active in both modes
7. No regression in existing routing behavior when no preferences set
