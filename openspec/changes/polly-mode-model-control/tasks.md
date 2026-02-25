# Tasks: Polly Mode Toggle + Granular Model Control Implementation

## Overview
Ordered implementation steps for replacing Polly's provider:tier model selector with a clean two-state system: Polly Mode ON (intelligent auto-routing with persona preferences) vs. Polly Mode OFF (direct model selection).

**Principle:** Backend model registry and pipeline changes first, then config and metrics, then Settings UI, then chat input area UX last.

**Estimated scope:** ~1400 lines across 11 files (1 new, 10 modified)

**Dependencies:**
- Phase 2 (Copilot Integration) — Copilot Chat models populate the dropdown when authenticated. Without Phase 2, dropdown shows only direct API + local models.
- Phase 3 (Programmer Persona) — Persona routing preferences interact with Programmer's MODE_ROUTING hints. Preferences take priority when set.
- Can be implemented independently of Phases 0-1 (cache/distillation apply regardless of how the model was selected)

---

## Task 1: Add Configuration
**Goal:** Add `polly_mode` and `persona_routing_preferences` to config.yaml and core/config.py

### Subtasks:
1. Add `polly_mode` section to `config.yaml`:
   ```yaml
   polly_mode:
     default_enabled: true
   ```

2. Add `persona_routing_preferences` section to `config.yaml`:
   ```yaml
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

3. Add both sections to `DEFAULT_CONFIG` in `core/config.py` with matching defaults

### Files:
- `config.yaml`
- `core/config.py`

### Validation:
- [ ] Config loads without errors
- [ ] `config.get("polly_mode")` returns `{"default_enabled": True}`
- [ ] `config.get("persona_routing_preferences")` returns full preference tree
- [ ] Missing keys fall back to defaults gracefully

---

## Task 2: Create ModelRegistry
**Goal:** Aggregate all available models from all providers into a unified list with metadata

**File:** `core/model_registry.py` (~200 lines)

### Subtasks:
1. **Singleton pattern:**
   ```python
   _instance = None
   def init_model_registry(config, litellm_config) -> ModelRegistry
   def get_model_registry() -> Optional[ModelRegistry]
   ```

2. **ModelRegistry class:**
   ```python
   class ModelRegistry:
       def __init__(self, config: dict, litellm_config: dict)
       async def get_available_models(self) -> list[dict]
       async def refresh(self) -> None
       def get_model_info(self, model_id: str) -> Optional[dict]
       def get_provider_groups(self) -> list[dict]
       def resolve_model(self, model_id: str) -> tuple[str, str]
   ```

3. **get_available_models():**
   - Parse `litellm_config.yaml` to extract all provider models (expand provider:tier → individual models)
   - Query Copilot Chat models from `copilot.chat.models` config (if authenticated)
   - Query local Ollama models from Ollama API (`/api/tags`)
   - Filter to only providers with valid credentials / enabled status
   - Return list of model dicts with: `id`, `name`, `provider`, `provider_key`, `capabilities`, `context_length`, `cost_tier`, `cost_detail`, `available`

4. **Cost tier mapping:**
   ```python
   def _compute_cost_tier(self, provider_key, model_id, multiplier=None):
       # "free" — 0x Copilot multiplier or free tier
       # "$"    — cheap (< $1/M tokens or < 0.5x multiplier)
       # "$$"   — standard (< $10/M tokens or 1x multiplier)
       # "$$$"  — premium (>= $10/M tokens or >= 3x multiplier)
       # "local" — runs on local hardware
   ```

5. **resolve_model(model_id):**
   - Parse `provider_key/model_name` format
   - Return `(provider_key, model_name)` tuple
   - Handle all prefixes: `copilot_chat/`, `anthropic/`, `openai/`, `github/`, `ollama/`, `gemini/`, `mistral/`, `grok/`, `perplexity/`, `openrouter/`

6. **get_provider_groups():**
   - Return ordered list of `{"key": str, "label": str, "order": int}` for frontend optgroup rendering

### Validation:
- [ ] Singleton pattern works
- [ ] All LiteLLM config models extracted
- [ ] Copilot Chat models included when authenticated
- [ ] Ollama models discovered via API
- [ ] Cost tiers computed correctly
- [ ] resolve_model() handles all provider prefixes
- [ ] Models with invalid/missing credentials excluded

---

## Task 3: Add Model Override to Query Pipeline
**Goal:** Accept `model_override` in query pipeline; bypass Router V2 but keep cache and distillation active

**File:** `core/polly.py`

### Subtasks:
1. **Update query() signature (~L1450):**
   ```python
   async def query(self, ..., polly_mode: bool = True, model_override: Optional[str] = None):
   ```

2. **Add model_override branch in query pipeline (~L1500-1550):**
   ```python
   if model_override:
       # DIRECT: Skip Router V2, call model directly
       provider_key, model_name = self.model_registry.resolve_model(model_override)
       response = await self._call_model_direct(provider_key, model_name, messages)
       # Record as user-directed in metrics
       self._record_routing_decision(route_type="user_override", model=model_override)
   else:
       # AUTO: existing routing pipeline (with optional persona prefs)
       ...
   ```

3. **Implement _call_model_direct(provider_key, model_name, messages):**
   - Map provider_key to the correct adapter (LiteLLM for cloud, Ollama for local)
   - For LiteLLM providers: call `litellm_provider.complete(f"{provider_key}/{model_name}", messages)`
   - For Ollama: call `local_llm.complete(model_name, messages)`
   - No fallback chain — if the model fails, propagate error to user
   - Error message: "Claude Opus 4.6 (Copilot) is currently unavailable. Turn on Polly Mode for automatic fallback, or select a different model."

4. **Cache key awareness:**
   - When `model_override` is set: include model ID in cache key
   - When Polly Mode ON (no override): cache key does NOT include model (varies by routing)

### Files:
- `core/polly.py`

### Validation:
- [ ] model_override bypasses Router V2
- [ ] Cache and distillation still run with model_override
- [ ] _call_model_direct routes to correct adapter
- [ ] Error propagated (no silent fallback) when model unavailable
- [ ] Cache key includes model for overrides, excludes for auto
- [ ] Existing routing unaffected when model_override is None

---

## Task 4: Add Persona Routing Preferences to Router
**Goal:** Accept soft routing hints (provider_hint, model_hint, prefer_local) that reorder candidates without breaking fallback chains

**File:** `libs/polly-routing/polly_routing/router.py`

### Subtasks:
1. **Add preference parameters to route() method:**
   ```python
   def route(self, ..., provider_hint: Optional[str] = None,
             model_hint: Optional[str] = None,
             prefer_local: bool = False):
   ```

2. **Implement candidate reordering:**
   ```python
   def _apply_routing_hints(self, candidates, provider_hint, model_hint, prefer_local):
       if prefer_local:
           # Boost local models to front of candidate list
           local = [c for c in candidates if c.is_local]
           cloud = [c for c in candidates if not c.is_local]
           return local + cloud
       if model_hint:
           # Pin specific model to front
           pinned = [c for c in candidates if c.model_id == model_hint]
           rest = [c for c in candidates if c.model_id != model_hint]
           return pinned + rest
       if provider_hint:
           # Boost candidates from preferred provider
           preferred = [c for c in candidates if c.provider == provider_hint]
           rest = [c for c in candidates if c.provider != provider_hint]
           return preferred + rest
       return candidates
   ```

3. **Key behavior:** Hints are SOFT — they reorder, not hard-override. If the hinted provider/model is unavailable, over-budget, or rate-limited, the normal fallback chain continues.

### Validation:
- [ ] provider_hint boosts matching candidates to front
- [ ] model_hint pins specific model to front
- [ ] prefer_local boosts local models to front
- [ ] Fallback chain still works when hinted option unavailable
- [ ] No hints = existing behavior unchanged (regression-safe)
- [ ] Hints compose correctly with existing tier/budget logic

---

## Task 5: Apply Persona Preferences in Query Pipeline
**Goal:** Load persona routing preferences and pass them as hints to Router V2

**File:** `core/polly.py`

### Subtasks:
1. **Load preferences at query time (~L1460):**
   ```python
   def _get_persona_routing_prefs(self, persona_slug: str, mode: Optional[str] = None) -> dict:
       prefs = self.config.get("persona_routing_preferences", {}).get(persona_slug, {})
       if not prefs:
           prefs = self.config.get("persona_routing_preferences", {}).get("default", {})
       
       # Merge mode overrides
       mode_prefs = prefs.get("mode_overrides", {}).get(mode, {}) if mode else {}
       
       return {
           "cloud_provider": mode_prefs.get("cloud_provider") or prefs.get("cloud_provider"),
           "cloud_model": mode_prefs.get("cloud_model"),
           "local_model": mode_prefs.get("local_model") or prefs.get("local_model"),
           "prefer_local": mode_prefs.get("prefer_local", False),
       }
   ```

2. **Pass hints to Router V2 in auto-routing path:**
   ```python
   # In the auto-routing branch (polly_mode=True, model_override=None):
   prefs = self._get_persona_routing_prefs(persona_slug, mode)
   result = self.router.route(
       ...,
       provider_hint=prefs.get("cloud_provider"),
       model_hint=prefs.get("cloud_model"),
       prefer_local=prefs.get("prefer_local", False),
   )
   ```

3. **Record preference usage in routing decision:**
   - If any prefs were applied: `routing_source = "auto_with_prefs"`
   - If no prefs (all None/default): `routing_source = "auto"`

### Validation:
- [ ] Persona prefs loaded correctly from config
- [ ] Mode overrides take priority over persona defaults
- [ ] Prefs passed as hints to Router V2
- [ ] routing_source distinguishes "auto" vs "auto_with_prefs"
- [ ] No prefs configured = existing behavior unchanged

---

## Task 6: Add Override Tracking to AutonomyMetrics
**Goal:** Track routing_source and user_selected_model in routing decisions

**File:** `core/autonomy_metrics.py`

### Subtasks:
1. **Schema migration — Add columns to routing_decisions table:**
   ```sql
   ALTER TABLE routing_decisions ADD COLUMN routing_source TEXT DEFAULT 'auto';
   -- Values: 'auto', 'auto_with_prefs', 'user_override'
   
   ALTER TABLE routing_decisions ADD COLUMN user_selected_model TEXT DEFAULT NULL;
   -- Non-null when routing_source = 'user_override'
   ```

2. **Update record_routing_decision():**
   ```python
   def record_routing_decision(self, ..., routing_source: str = "auto",
                                user_selected_model: Optional[str] = None):
   ```

3. **Update AutonomySnapshot with override stats:**
   ```python
   user_override_count: int = 0          # Count of user_override decisions this period
   auto_with_prefs_count: int = 0        # Count of auto_with_prefs decisions
   override_models: dict = {}            # {model: count} for user_override decisions
   ```

4. **Pattern learning integration:**
   - When `routing_source = 'user_override'`, record a `ROUTING_OUTCOME` pattern
   - Over time, frequent overrides for a persona+mode can inform auto-routing defaults

### Validation:
- [ ] Schema migration runs without errors
- [ ] routing_source recorded correctly for all three values
- [ ] user_selected_model populated for overrides
- [ ] AutonomySnapshot includes override stats
- [ ] Existing code that calls record_routing_decision() still works (default params)

---

## Task 7: Add Server Endpoints
**Goal:** Add GET /models/available, accept polly_mode and model_override in QueryRequest, add persona routing preferences CRUD

**File:** `interfaces/server.py`

### Subtasks:
1. **GET /models/available:**
   ```python
   @app.get("/models/available")
   async def get_available_models():
       registry = get_model_registry()
       models = await registry.get_available_models()
       groups = registry.get_provider_groups()
       return {"models": models, "groups": groups}
   ```

2. **Update QueryRequest model (~L78-91):**
   ```python
   class QueryRequest(BaseModel):
       query: str
       conversation_id: Optional[str] = None
       confidence: Optional[str] = None
       provider_override: Optional[str] = None    # Legacy, still supported
       polly_mode: bool = True                     # New: True = auto, False = direct
       model_override: Optional[str] = None        # New: exact model ID
   ```

3. **Update query handler (~L86-91) to pass new fields:**
   ```python
   response = await polly.query(
       ...,
       polly_mode=request.polly_mode,
       model_override=request.model_override,
   )
   ```

4. **Backward compatibility:** When `model_override` is set, `polly_mode` is implicitly False. When `provider_override` is set (legacy), it still works as before.

### Files:
- `interfaces/server.py`

### Validation:
- [ ] GET /models/available returns model list with groups
- [ ] QueryRequest accepts polly_mode and model_override
- [ ] model_override flows through to polly.query()
- [ ] Legacy provider_override still works
- [ ] Error response when model_override points to unavailable model

---

## Task 8: Add Persona Routing Preferences API
**Goal:** CRUD endpoints for per-persona routing preferences in Settings

**File:** `interfaces/settings_api.py`

### Subtasks:
1. **GET /settings/persona-routing:**
   ```python
   @app.get("/settings/persona-routing")
   async def get_persona_routing_preferences():
       prefs = config.get("persona_routing_preferences", {})
       registry = get_model_registry()
       return {
           "preferences": prefs,
           "available_providers": [g["key"] for g in registry.get_provider_groups()],
           "available_local_models": [m["id"] for m in await registry.get_available_models()
                                      if m["provider_key"] == "ollama"],
           "personas": _get_persona_modes_list(),
       }
   ```

2. **PUT /settings/persona-routing/{persona_slug}:**
   ```python
   @app.put("/settings/persona-routing/{persona_slug}")
   async def update_persona_routing(persona_slug: str, prefs: PersonaRoutingPrefs):
       # Validate persona_slug exists
       # Validate provider/model references exist
       # Update config.yaml
       # Reload in-memory config
   ```

3. **POST /settings/persona-routing/reset:**
   - Reset all preferences to DEFAULT_CONFIG defaults
   - Write defaults to config.yaml

4. **PersonaRoutingPrefs Pydantic model:**
   ```python
   class ModeOverride(BaseModel):
       cloud_provider: Optional[str] = None
       cloud_model: Optional[str] = None
       local_model: Optional[str] = None
       prefer_local: bool = False
   
   class PersonaRoutingPrefs(BaseModel):
       cloud_provider: Optional[str] = None
       local_model: Optional[str] = None
       mode_overrides: dict[str, ModeOverride] = {}
   ```

### Files:
- `interfaces/settings_api.py`

### Validation:
- [ ] GET returns current prefs with available providers and models
- [ ] PUT updates prefs for a single persona
- [ ] Reset restores defaults
- [ ] Invalid persona_slug returns 404
- [ ] Invalid provider/model references return 400
- [ ] Config persists across restart

---

## Task 9: Initialize ModelRegistry in Polly
**Goal:** Add ModelRegistry init to Polly startup sequence

**File:** `core/polly.py`

### Subtasks:
1. **Add _init_model_registry() method:**
   ```python
   def _init_model_registry(self):
       from core.model_registry import init_model_registry
       litellm_config = self._load_litellm_config()
       init_model_registry(self.config, litellm_config)
   ```

2. **Call in __init__ sequence** — after RAG init (line ~69) and before router init (line ~74):
   ```python
   self._init_model_registry()
   ```

3. **Wire model_registry reference:**
   ```python
   from core.model_registry import get_model_registry
   self.model_registry = get_model_registry()
   ```

### Validation:
- [ ] ModelRegistry initializes at startup
- [ ] get_model_registry() returns instance after init
- [ ] Init order: RAG → ModelRegistry → Router
- [ ] Startup not blocked if Ollama is offline (graceful skip for local models)

---

## Task 10: Add Electron IPC Handlers
**Goal:** Add IPC handlers for model list fetching and persona routing preferences

**File:** `electron-app/src/main/main.js`

### Subtasks:
1. **Add IPC handler for model list:**
   ```javascript
   ipcMain.handle("get-available-models", async () => {
       // GET from backend /models/available
       // Return {models, groups}
   });
   ```

2. **Add IPC handler for persona routing preferences:**
   ```javascript
   ipcMain.handle("get-persona-routing", async () => {
       // GET from backend /settings/persona-routing
   });
   
   ipcMain.handle("update-persona-routing", async (event, { personaSlug, prefs }) => {
       // PUT to backend /settings/persona-routing/{personaSlug}
   });
   
   ipcMain.handle("reset-persona-routing", async () => {
       // POST to backend /settings/persona-routing/reset
   });
   ```

3. **Follow existing IPC pattern** (same as queryPolly at main.js L882-923)

### Validation:
- [ ] All IPC handlers registered
- [ ] Model list returns correct data shape
- [ ] Preference CRUD works through IPC
- [ ] Error handling follows existing patterns

---

## Task 11: Update Chat Input Area — Polly Mode Toggle + Model Dropdown
**Goal:** Replace the current model selector with a Polly Mode toggle and conditional model dropdown

### Subtasks:
1. **HTML** (`electron-app/src/renderer/index.html`):
   - Remove existing model selector dropdown (~L2241)
   - Remove non-functional orchestrator toggle (~L2396)
   - Add Polly Mode toggle inline with persona selector:
     ```html
     <div class="polly-mode-controls">
       <label class="polly-mode-toggle">
         <input type="checkbox" id="polly-mode-toggle" checked>
         <span class="polly-mode-label">Polly</span>
       </label>
       <select id="model-override-select" class="model-dropdown" style="display:none">
         <!-- Populated dynamically from /models/available -->
       </select>
     </div>
     ```

2. **JavaScript** (`electron-app/src/renderer/app.js`):
   - **Remove** existing MODEL_PROVIDERS array (~L4914) and buildModelSelectorOptions (~L4933)
   - **Remove** existing handleModelChange (~L4986)
   - **Remove** orchestrator toggle handler (~L4031-4046)
   - **Add pollyModeToggle():**
     - Toggle ON: hide model dropdown, set `pollyMode = true` in sessionStorage
     - Toggle OFF: show model dropdown, fetch model list, set `pollyMode = false`
   - **Add fetchAvailableModels():**
     - IPC call to `get-available-models`
     - Populate `<select>` with `<optgroup>` per provider group
     - Each `<option>` shows model name + cost tier indicator
     - Cache response (refresh on toggle or manual)
   - **Add buildModelDropdown(models, groups):**
     - Sort groups by `order`
     - Within each group, sort models: free first, then $, $$, $$$, local
     - Format: `"Claude Opus 4.6    $$$"` (name + cost indicator)
   - **Update queryOptions assembly (~L8525-8536):**
     ```javascript
     const queryOptions = {
         ...existingOptions,
         polly_mode: sessionStorage.getItem('pollyMode') !== 'false',
         model_override: pollyModeEnabled ? null : document.getElementById('model-override-select').value,
     };
     ```
   - **Initialize toggle state from sessionStorage on page load**
   - **Load default state from config** (first visit: check `polly_mode.default_enabled`)

3. **CSS** (`electron-app/src/renderer/styles/main.css`):
   - Style Polly Mode toggle (compact, inline with persona selector)
   - Style model dropdown (grouped, with cost indicators right-aligned)
   - Remove existing model selector styles (~L688-718) or restyle
   - Remove orchestrator toggle CSS from `persona-ui.css` (~L600-652) or restyle

4. **Update response metadata footer (~L8558-8586):**
   - When `routing_source = "user_override"`: show `"→ user selected | {provider}"`
   - When `routing_source = "auto_with_prefs"`: show `"→ polly auto ({persona} prefs) | {tier} | {provider}"`
   - When `routing_source = "auto"`: show existing format

### Files:
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/styles/main.css`
- `electron-app/src/renderer/styles/persona-ui.css`

### Validation:
- [ ] Toggle visible and functional
- [ ] Toggle ON: model dropdown hidden, queries use auto-routing
- [ ] Toggle OFF: model dropdown visible with all available models
- [ ] Model dropdown grouped by provider with cost indicators
- [ ] Selected model flows through as model_override in query
- [ ] Toggle state persists across page reloads (sessionStorage)
- [ ] Response metadata shows routing source info
- [ ] No regressions to existing chat input UX

---

## Task 12: Add Settings UI — Persona Routing Preferences
**Goal:** Add per-persona routing preference controls to the Settings panel

### Subtasks:
1. **HTML** (`electron-app/src/renderer/index.html`):
   - Add "Routing Preferences" section in Settings:
     - Default Polly Mode toggle (ON/OFF) — sets `config.yaml` default
     - Per-persona collapsible sections (Programmer, Scribe, Professor, Architect, General Chat)
     - Each section: cloud provider dropdown, local model dropdown, mode overrides area
     - "[+ Add override]" button per persona
     - "[Reset to Defaults]" button at bottom

2. **JavaScript** (`electron-app/src/renderer/app.js`):
   - **loadPersonaRoutingPrefs():**
     - IPC call to `get-persona-routing`
     - Populate provider dropdowns from `available_providers`
     - Populate local model dropdowns from `available_local_models`
     - Render existing overrides for each persona
   - **renderModeOverride(persona, mode, prefs):**
     - Show cloud provider + model dropdowns
     - Show "prefer local" checkbox
     - Show "[Remove]" button
   - **addModeOverride(persona):**
     - Show mode selector dropdown (from persona's available modes)
     - On selection: render override row
   - **savePersonaRouting(persona):**
     - Collect form values
     - IPC call to `update-persona-routing`
     - Show success indicator
   - **resetAllPreferences():**
     - Confirm dialog
     - IPC call to `reset-persona-routing`
     - Reload UI

3. **CSS** (`electron-app/src/renderer/styles/main.css`):
   - Style persona preference cards (collapsible, bordered)
   - Style mode override rows (nested, removable)
   - Style "[+ Add override]" button

### Files:
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/app.js`
- `electron-app/src/renderer/styles/main.css`

### Validation:
- [ ] All personas shown with correct modes
- [ ] Provider dropdowns populated from actual connected providers
- [ ] Local model dropdown populated from Ollama
- [ ] Mode overrides can be added and removed
- [ ] Preferences save and persist across restart
- [ ] Reset restores defaults
- [ ] Changes take effect immediately for new queries

---

## Task 13: Testing — Polly Mode Toggle
**Goal:** Verify toggle behavior and state persistence

### Test Cases:
1. **Default state:**
   - Fresh session → Polly Mode ON
   - Model dropdown hidden
   - Query routes through Router V2

2. **Toggle OFF:**
   - Click toggle → model dropdown appears
   - Model dropdown populated with all available models
   - Select model → query uses exact model
   - Response metadata shows "user selected"

3. **Toggle ON:**
   - Click toggle back → model dropdown hides
   - Query routes through Router V2 again
   - Response metadata shows "polly auto"

4. **Persistence:**
   - Toggle OFF → reload page → still OFF
   - Toggle ON → reload page → still ON
   - New session (new tab) → uses config.yaml default

5. **Interaction with persona switch:**
   - Polly Mode OFF, Programmer selected → shows all models
   - Switch to Professor → still shows all models (toggle state persists)
   - Toggle ON → preferences for Professor applied

### Validation:
- [ ] Toggle state accurate across reloads
- [ ] Model dropdown shows/hides correctly
- [ ] Query pipeline respects toggle state
- [ ] No interference between toggle and persona selection

---

## Task 14: Testing — Model Override Pipeline
**Goal:** Verify direct model selection works end-to-end

### Test Cases:
1. **Direct model call — cloud:**
   - Select `copilot_chat/claude-opus-4.6` → query → response from Claude Opus 4.6
   - Verify Router V2 NOT called (check logs)
   - Verify response metadata shows model + "user selected"

2. **Direct model call — local:**
   - Select `ollama/llama3.1:7b` → query → response from local model
   - Verify zero cloud cost

3. **Model unavailable:**
   - Select model with expired credentials
   - Query → error message: "... is currently unavailable. Turn on Polly Mode..."
   - No silent fallback to another model

4. **Cache interaction:**
   - Select `anthropic/claude-sonnet-4-20250514` → query "what is 2+2?"
   - Same model, same query → cache hit
   - Different model, same query → cache miss (model in cache key)

5. **Distillation active:**
   - Select any model → long context query → verify distillation still runs
   - Response quality unaffected by direct selection

6. **Legacy provider_override compatibility:**
   - Send `provider_override: "anthropic"` (legacy) → still works as before
   - Send `model_override: "anthropic/claude-opus-4-20250514"` (new) → works

### Validation:
- [ ] Direct model call works for cloud and local
- [ ] No fallback on failure
- [ ] Cache key includes model for overrides
- [ ] Distillation still active
- [ ] Legacy provider_override unchanged

---

## Task 15: Testing — Persona Routing Preferences
**Goal:** Verify preferences shape auto-routing without breaking fallback chains

### Test Cases:
1. **Persona default applied:**
   - Set Programmer `cloud_provider: copilot_chat`
   - Polly Mode ON, Programmer active → query → Copilot Chat model preferred
   - Verify in logs: candidate list reordered, Copilot Chat models first

2. **Mode override applied:**
   - Set Programmer/refactor `cloud_provider: anthropic, cloud_model: claude-opus-4-20250514`
   - Polly Mode ON, /refactor query → Anthropic Claude Opus preferred
   - Non-refactor query (e.g., /code) → Copilot Chat (persona default)

3. **prefer_local applied:**
   - Set Professor/explain `prefer_local: true`
   - Polly Mode ON, Professor explain query → local model used
   - Verify zero cloud cost

4. **Fallback when preferred unavailable:**
   - Set Programmer `cloud_provider: copilot_chat`
   - Disconnect Copilot → query → falls through to next provider in chain
   - Verify fallback is seamless (no error)

5. **No preferences set:**
   - Clear all prefs for Scribe
   - Polly Mode ON, Scribe active → query → existing Router V2 behavior
   - Identical to pre-feature behavior

6. **Settings UI round-trip:**
   - Set prefs in Settings → save → reload → prefs still set
   - Change prefs → verify immediate effect on next query
   - Reset to defaults → verify defaults restored

### Validation:
- [ ] Persona defaults shape routing
- [ ] Mode overrides take priority over persona defaults
- [ ] prefer_local routes locally
- [ ] Fallback chain works when preferred option unavailable
- [ ] No prefs = existing behavior
- [ ] Settings persist across restart

---

## Task 16: Testing — Metrics and Tracking
**Goal:** Verify routing_source and override tracking in AutonomyMetrics

### Test Cases:
1. **Auto routing:**
   - Polly Mode ON, no prefs → `routing_source = "auto"`
   - Polly Mode ON, with prefs → `routing_source = "auto_with_prefs"`

2. **User override:**
   - Polly Mode OFF, select model → `routing_source = "user_override"`
   - `user_selected_model` populated with exact model ID

3. **Override stats in snapshot:**
   - Make 5 auto + 3 override queries
   - AutonomySnapshot shows `user_override_count: 3, auto_with_prefs_count: 0`
   - `override_models` shows model frequency

4. **Pattern learning:**
   - Override to Claude Opus for refactoring 10 times
   - Verify ROUTING_OUTCOME pattern recorded with model + persona + mode context

### Validation:
- [ ] routing_source values correct for all three scenarios
- [ ] user_selected_model populated for overrides only
- [ ] Snapshot stats aggregate correctly
- [ ] Schema migration backward-compatible

---

## Task 17: Documentation & Specs Update
**Goal:** Update relevant docs

### Subtasks:
1. Update architecture spec:
   - Add Polly Mode toggle to UX diagram
   - Document model_override pipeline branch
   - Document persona routing preferences layer

2. Update project status:
   - Mark Polly Mode feature as completed

3. Add changelog entry:
   ```markdown
   ## YYYY-MM-DD - Polly Mode Toggle + Model Control
   - Added Polly Mode toggle (ON = intelligent routing, OFF = direct model access)
   - Added comprehensive model dropdown listing all connected models
   - Added model_override to query pipeline (bypass routing, keep cache + distillation)
   - Added per-persona routing preferences with mode-level overrides
   - Added ModelRegistry aggregating models from all providers
   - Added routing_source tracking in AutonomyMetrics
   - Added GET /models/available API endpoint
   - Added persona routing preferences CRUD in Settings
   ```

4. Archive this change folder

### Validation:
- [ ] All specs updated
- [ ] Changelog entry added

---

## Task 18: Final Validation
**Goal:** Comprehensive end-to-end testing

### Test Scenarios:
1. **Fresh install:**
   - [ ] Polly Mode ON by default
   - [ ] No model dropdown visible
   - [ ] Queries route through Router V2 as before
   - [ ] No regressions to existing behavior

2. **Toggle to OFF:**
   - [ ] Model dropdown appears with all connected models
   - [ ] Models grouped by provider
   - [ ] Cost indicators visible
   - [ ] Direct selection works end-to-end

3. **Persona preferences:**
   - [ ] Settings UI shows all personas with modes
   - [ ] Preferences save and take effect
   - [ ] Mode overrides work
   - [ ] Reset to defaults works

4. **Provider availability:**
   - [ ] Only authenticated/enabled providers show in dropdown
   - [ ] Copilot Chat models appear only when Copilot is authenticated
   - [ ] Ollama models appear only when Ollama is running
   - [ ] Model list refreshes when provider status changes

5. **Backward compatibility:**
   - [ ] Legacy provider_override still works
   - [ ] Existing API clients unaffected (polly_mode defaults to True)
   - [ ] No changes to existing routing when no preferences set

### Success Criteria:
- Polly Mode toggle functional and persists across page reloads
- Model dropdown shows all available models from all connected providers
- Direct model selection works end-to-end (query → exact model → response)
- Persona preferences shape auto-routing without breaking fallback chains
- Override tracking accurately distinguishes auto vs. user-directed
- Cache and distillation remain active in both modes
- No regression in existing routing behavior when no preferences set

---

## Dependency Order

```
Task 1 (Config — polly_mode + persona prefs)
    ↓
Task 2 (ModelRegistry)
    ↓
Task 3 (Model Override in polly.py) ──→ Task 4 (Router Hints)
    ↓                                        ↓
Task 5 (Persona Prefs in Pipeline) ←────────┘
    ↓
Task 6 (AutonomyMetrics — routing_source)
    ↓
Task 7 (Server Endpoints — /models/available, QueryRequest)
    ↓
Task 8 (Settings API — Persona Routing CRUD)
    ↓
Task 9 (ModelRegistry Init in Polly)
    ↓
Task 10 (Electron IPC Handlers)
    ↓
Task 11 (Chat Input — Toggle + Dropdown) ──→ Task 12 (Settings UI — Preferences)
    ↓                                             ↓
    └──────────────┬──────────────────────────────┘
                   ↓
Tasks 13-16 (Testing) ← can run in parallel
                   ↓
Task 17 (Docs)
                   ↓
Task 18 (Final Validation)
```

Tasks 3-4 can be done in parallel. Tasks 11-12 can be done in parallel. Tasks 13-16 can run in parallel.

---

## Coordination Notes

### Interacts with Phase 2 (Copilot Integration):
- ModelRegistry includes Copilot Chat models when authenticated
- `copilot_chat/` models appear in dropdown when Phase 2 is implemented
- Without Phase 2: dropdown shows direct API + local models only — feature works fully
- CopilotChatProvider.get_available_models() feeds into ModelRegistry

### Interacts with Phase 3 (Programmer Persona):
- Programmer's MODE_ROUTING defines `prefer` hints (local/cloud/copilot)
- Persona routing preferences can override or refine these hints
- Layer precedence: persona prefs (Layer 1-2) override MODE_ROUTING hints (Layer 0)
- When no prefs set, MODE_ROUTING hints are the only influence

### Benefits from Phase 0 (Semantic Cache):
- Cache applies in both Polly Mode ON and OFF
- model_override cache key includes model ID (model-specific caching)
- Auto-routing cache key excludes model (any model's response can be reused)

### Benefits from Phase 1 (Context Distillation):
- Distillation applies in both modes
- Reduces token usage for direct model selection too (not just auto-routing)

### Existing infrastructure used (no changes needed):
- `libs/polly-routing/polly_routing/providers/litellm.py` — Provider adapters unchanged; model_override resolves to same adapter calls
- `libs/polly-routing/polly_routing/budget.py` — Budget tracking unchanged; direct model calls still record usage
- `core/compression/` — Distillation pipeline unchanged; runs in both modes
- `core/personas/` — Persona implementations unchanged; preferences are external to persona code
