# Tasks: GitHub Copilot Integration — FIM + Chat Implementation

## Overview
Ordered implementation steps for integrating GitHub Copilot's FIM completions API and Copilot Chat multi-model provider into Polly.

**Principle:** Authentication first (shared), then FIM core, then Chat provider, then server endpoints, then frontend UI.

**Estimated scope:** ~1100 lines across 13 files (3 new, 10 modified)

**Dependencies:**
- Phase 0 (Semantic Response Cache) — for caching FIM completions and Chat responses
- Phase 1 (Context Distillation) — for compressing file header context (optional)

---

## Task 1: Add Configuration
**Goal:** Add Copilot config (FIM + Chat) to config.yaml, core/config.py, and secrets_manager.py

### Subtasks:
1. Add `copilot` section to `config.yaml`:
   ```yaml
   copilot:
     enabled: false
     client_id: "Iv1.b507a08c87ecfe98"
     fim:
       max_tokens: 128
       temperature: 0.0
       stop_sequences:
         - "\n\n"
         - "\nclass "
         - "\ndef "
         - "\n#"
       context_window: 8192
       cache_completions: true
       fallback_to_ollama: true
     chat:
       enabled: true
       premium_budget: null
       prefer_free_models: false
       models:
         - gpt-5-mini
         - gpt-4.1
         - gpt-4.1-mini
         - gpt-5.2
         - claude-sonnet-4.6
         - gemini-3-flash
         - grok-code-fast-1
         - claude-opus-4.6
         - gemini-3-pro
   ```

2. Add `copilot` to `DEFAULT_CONFIG` in `core/config.py` (with both `fim` and `chat` subsections)

3. Add `copilot` credential type to `core/secrets_manager.py`:
   ```python
   'copilot': {
       'key_name': 'COPILOT_ACCESS_TOKEN',
       'env_var': 'COPILOT_ACCESS_TOKEN',
       'description': 'GitHub Copilot access token (via device code flow)',
       'format': 'ghu_...',
       'validate_prefix': ['ghu_']
   }
   ```

### Files:
- `config.yaml`
- `core/config.py`
- `core/secrets_manager.py`

### Validation:
- [ ] Config loads without errors
- [ ] Default values accessible via `config.get("copilot")`
- [ ] secrets_manager recognizes 'copilot' credential type

---

## Task 2: Implement CopilotIntegration — Authentication
**Goal:** Implement device code OAuth flow for Copilot

**File:** `integrations/copilot.py` (~300 lines total, auth portion ~150 lines)

### Subtasks:
1. **Class skeleton:**
   ```python
   class CopilotIntegration:
       def __init__(self, config: dict)
       # Instance attributes: access_token, copilot_token, token_expires_at, _session
   ```

2. **start_device_flow():**
   - POST `https://github.com/login/device/code` with client_id and scope
   - Return `{user_code, verification_uri, device_code, interval}`
   - Handle HTTP errors gracefully

3. **poll_for_token(device_code, interval):**
   - POST `https://github.com/login/oauth/access_token` with device_code
   - Handle responses: `authorization_pending`, `slow_down`, `expired_token`, `access_denied`
   - On success: store access_token, call `_exchange_for_copilot_token()`
   - Return True on success, False on expiry/denial

4. **_exchange_for_copilot_token():**
   - GET `https://api.github.com/copilot_internal/v2/token` with Bearer access_token
   - Parse response: `{token, expires_at}`
   - Store copilot_token and token_expires_at in memory

5. **refresh_copilot_token():**
   - Check if access_token is still valid
   - Call `_exchange_for_copilot_token()` again
   - Return True on success, False on failure (triggers re-auth)

6. **check_subscription():**
   - Attempt `_exchange_for_copilot_token()`
   - 401/403 → no subscription → return False
   - Success → return True

7. **is_authenticated():**
   - Check access_token is not None
   - Check copilot_token is not None
   - Check token_expires_at > now

8. **Token persistence helpers:**
   - `_store_token(token, key)` — store in env var (keytar handled by Electron)
   - `_load_token(key)` — load from env var or keytar

### Validation:
- [ ] start_device_flow() returns valid device code response
- [ ] poll_for_token() handles all response states
- [ ] Token exchange works with valid access_token
- [ ] Token refresh works before expiry
- [ ] check_subscription() detects active/inactive subscription
- [ ] is_authenticated() returns correct state

---

## Task 3: Implement CopilotIntegration — FIM Completions
**Goal:** Add FIM completion method to CopilotIntegration

**File:** `integrations/copilot.py` (continued, ~100 lines)

### Subtasks:
1. **_ensure_token():**
   - Check if copilot_token is valid and not expired
   - If expired or near-expiry (< 5 min): call refresh_copilot_token()
   - If refresh fails: raise AuthenticationError

2. **complete(prefix, suffix, language, max_tokens, temperature, stop, stream):**
   - Call `_ensure_token()`
   - Build FIM request payload:
     ```python
     {
         "prompt": prefix,
         "suffix": suffix,
         "max_tokens": max_tokens,
         "temperature": temperature,
         "top_p": 1,
         "n": 1,
         "stop": stop or config["stop_sequences"],
         "stream": stream,
         "extra": {"language": language}
     }
     ```
   - POST to `https://api.github.com/copilot_internal/v2/completions`
     (or current Copilot completions endpoint)
   - Parse response into OpenAI-compatible format
   - Handle streaming: return async iterator of text chunks
   - Handle non-streaming: return complete response dict

3. **_build_fim_context(prefix, suffix, language):**
   - Truncate prefix to fit context_window (prioritize code nearest cursor)
   - Truncate suffix to fit remaining budget
   - Add language hint metadata

4. **disconnect():**
   - Clear all tokens
   - Close aiohttp session
   - Set enabled to False

### Validation:
- [ ] _ensure_token() refreshes expired tokens
- [ ] complete() returns valid completion response
- [ ] Streaming returns incremental text chunks
- [ ] Context truncation respects context_window limit
- [ ] Disconnect clears all state

---

## Task 4: Implement CopilotFIMProvider
**Goal:** Create provider adapter for Copilot FIM with cache integration

**File:** `core/providers/copilot_provider.py` (~200 lines)

### Subtasks:
1. **Singleton pattern:**
   ```python
   _instance = None
   def init_copilot_provider(copilot, cache=None) -> CopilotFIMProvider
   def get_copilot_provider() -> Optional[CopilotFIMProvider]
   ```

2. **CopilotFIMProvider class:**
   ```python
   class CopilotFIMProvider:
       def __init__(self, copilot: CopilotIntegration, cache=None)
       async def complete_fim(prefix, suffix, language, **kwargs) -> dict
       def is_available() -> bool
   ```

3. **complete_fim() with cache integration (Phase 0):**
   - If cache enabled and cache exists:
     - Build cache key from `prefix[-500:] + suffix[:500]`
     - Check semantic cache
     - On hit: return cached completion
   - Call `copilot.complete(prefix, suffix, language, ...)`
   - If cache enabled: store result in cache
   - Return OpenAI-compatible completion response

4. **is_available():**
   - Check copilot.is_authenticated()
   - Check copilot.config["enabled"]

5. **Ollama fallback:**
   - If Copilot unavailable and `fallback_to_ollama` config is True:
     - Build FIM-style prompt for Ollama chat endpoint
     - Route through local UnifiedLLM
     - Return in same response format

### Validation:
- [ ] complete_fim() returns valid completion
- [ ] Cache integration works (hit → return cached, miss → call API → store)
- [ ] is_available() reflects actual auth state
- [ ] Ollama fallback works when Copilot unavailable
- [ ] Singleton pattern works

---

## Task 5: Add Server Endpoints
**Goal:** Add /v1/completions FIM endpoint and Copilot auth endpoints

**File:** `interfaces/server.py`

### Subtasks:
1. **CompletionRequest model:**
   ```python
   class CompletionRequest(BaseModel):
       model: str = "copilot"
       prompt: str
       suffix: Optional[str] = ""
       max_tokens: int = 128
       temperature: float = 0.0
       stop: Optional[list[str]] = None
       stream: bool = False
       language: Optional[str] = None
   ```

2. **POST /v1/completions:**
   - Parse CompletionRequest
   - If model == "copilot": route to CopilotFIMProvider
   - If Copilot unavailable and fallback enabled: route to Ollama
   - Return OpenAI-compatible CompletionResponse
   - Support streaming via SSE (same pattern as /v1/chat/completions)

3. **POST /copilot/auth/device-code:**
   - Initialize CopilotIntegration if needed
   - Call start_device_flow()
   - Return {user_code, verification_uri, device_code, interval}

4. **POST /copilot/auth/poll:**
   - Accept {device_code} in body
   - Call poll_for_token(device_code)
   - Return {authenticated: bool, error?: str}

5. **GET /copilot/auth/status:**
   - Return {authenticated: bool, subscription: bool, expires_at: float}

6. **DELETE /copilot/auth/disconnect:**
   - Call copilot.disconnect()
   - Return {disconnected: true}

### Validation:
- [ ] POST /v1/completions returns valid completion
- [ ] Streaming works via SSE
- [ ] Auth endpoints handle full device code flow
- [ ] Status endpoint reflects actual state
- [ ] Disconnect clears tokens

---

## Task 6: Add Electron IPC Handlers for Device Code Auth
**Goal:** Add IPC handlers for Copilot authentication in Electron main process

**File:** `electron-app/src/main/main.js`

### Subtasks:
1. **Add IPC handler for device code flow:**
   ```javascript
   ipcMain.handle("copilot-start-auth", async () => {
       // POST to backend /copilot/auth/device-code
       // Return {user_code, verification_uri}
   });
   ```

2. **Add IPC handler for auth polling:**
   ```javascript
   ipcMain.handle("copilot-poll-auth", async (event, deviceCode) => {
       // POST to backend /copilot/auth/poll
       // Return {authenticated, error}
   });
   ```

3. **Add IPC handler for auth status:**
   ```javascript
   ipcMain.handle("copilot-auth-status", async () => {
       // GET from backend /copilot/auth/status
   });
   ```

4. **Add IPC handler for disconnect:**
   ```javascript
   ipcMain.handle("copilot-disconnect", async () => {
       // DELETE to backend /copilot/auth/disconnect
   });
   ```

5. **Token storage in keytar:**
   - Store COPILOT_ACCESS_TOKEN in keytar on successful auth
   - Load from keytar on app start and inject into server env
   - Follow existing pattern from GitHub OAuth (main.js L436-442)

### Validation:
- [ ] All IPC handlers registered
- [ ] Token stored in keytar on successful auth
- [ ] Token loaded from keytar on app restart
- [ ] Token injected into Python backend env

---

## Task 7: Add Settings UI — Copilot Auth
**Goal:** Add Copilot authentication UI to Electron settings

### Subtasks:
1. **HTML** (`electron-app/src/renderer/index.html`):
   - Add "GitHub Copilot" section in Integrations area:
     ```html
     <div class="setting-group" id="copilot-settings">
       <h4>GitHub Copilot</h4>
       <div id="copilot-status">Not Connected</div>
       <button id="copilot-connect-btn">Connect Copilot</button>
       <div id="copilot-device-code" style="display:none">
         <p>Enter code <strong id="copilot-user-code"></strong> at</p>
         <a id="copilot-verify-link" href="#" target="_blank">github.com/login/device</a>
         <p>Waiting for authentication...</p>
         <button id="copilot-cancel-btn">Cancel</button>
       </div>
       <div id="copilot-connected" style="display:none">
         <label><input type="checkbox" id="copilot-enabled"> Enable Copilot completions</label>
         <label><input type="checkbox" id="copilot-cache"> Cache completions</label>
         <label><input type="checkbox" id="copilot-fallback"> Fall back to local model</label>
         <button id="copilot-disconnect-btn">Disconnect</button>
       </div>
     </div>
     ```

2. **JavaScript** (`electron-app/src/renderer/app.js`):
   - `checkCopilotStatus()`: IPC call → update status display
   - `startCopilotAuth()`:
     - IPC call to start device flow → show user_code + verification_uri
     - Open github.com/login/device in browser
     - Start polling interval
   - `pollCopilotAuth(deviceCode)`:
     - IPC call to poll → check authenticated
     - On success: hide device code, show connected state
     - On failure/timeout: show error
   - `disconnectCopilot()`:
     - IPC call to disconnect → update UI
   - `saveCopilotSettings()`: Read checkboxes → PUT settings
   - Wire up all event listeners
   - Call `checkCopilotStatus()` on settings page load

### Files:
- `electron-app/src/renderer/index.html`
- `electron-app/src/renderer/app.js`

### Validation:
- [ ] "Connect Copilot" button starts device code flow
- [ ] User code displayed correctly
- [ ] "Open GitHub" opens browser to verification URI
- [ ] Polling detects successful authentication
- [ ] Connected state shows settings checkboxes
- [ ] Disconnect clears auth and returns to initial state
- [ ] Settings persist across app restart

---

## Task 8: Extend AutonomyMetrics
**Goal:** Track FIM completion statistics and Copilot Chat premium request usage

**File:** `core/autonomy_metrics.py`

### Subtasks:
1. Add FIM fields to `AutonomySnapshot`:
   ```python
   fim_completions: int = 0
   fim_cache_hits: int = 0
   fim_tokens_used: int = 0
   fim_fallback_to_local: int = 0
   ```

2. Add Copilot Chat fields to `AutonomySnapshot`:
   ```python
   copilot_chat_requests: int = 0
   copilot_chat_premium_used: float = 0.0    # Sum of multipliers
   copilot_chat_premium_budget: float = None  # Monthly budget
   copilot_chat_by_model: dict = {}           # {model: count}
   ```

3. Update `get_snapshot()` to query FIM stats from CopilotFIMProvider

4. Update `get_snapshot()` to query Chat stats from CopilotChatProvider

5. Accept `route_type='copilot_fim'` and `route_type='copilot_chat'` in `record_routing_decision()`

### Validation:
- [ ] AutonomySnapshot includes FIM and Chat fields
- [ ] FIM stats populate when Copilot is active
- [ ] Chat premium usage tracking works
- [ ] route_type='copilot_fim' and 'copilot_chat' recorded correctly

---

## Task 9: Implement CopilotChatProvider
**Goal:** Create LiteLLM-compatible provider adapter for Copilot Chat

**File:** `core/providers/copilot_chat_provider.py` (~250 lines)

### Subtasks:
1. **Singleton pattern:**
   ```python
   _instance = None
   def init_copilot_chat_provider(copilot, config) -> CopilotChatProvider
   def get_copilot_chat_provider() -> Optional[CopilotChatProvider]
   ```

2. **CopilotChatProvider class:**
   ```python
   class CopilotChatProvider:
       def __init__(self, copilot: CopilotIntegration, config: dict)
       async def get_token(self) -> Optional[str]
       def get_available_models(self) -> list[dict]
       def get_multiplier(self, model_id: str) -> float
       def record_usage(self, model_id: str)
       def get_monthly_usage(self) -> dict
       def is_available(self) -> bool
       def is_budget_available(self, model_id: str) -> bool
   ```

3. **Premium request multiplier table:**
   - Store multipliers in config (updatable without code changes)
   - Default multipliers from Copilot docs
   - Unknown models default to 1x multiplier

4. **Monthly usage tracking:**
   - Store usage records in `usage.db` (same DB as BudgetManager)
   - Table: `copilot_chat_usage(id, model, multiplier, timestamp)`
   - `get_monthly_usage()` queries current month's records
   - Reset tracking at month boundary

5. **Budget checking:**
   - `is_budget_available(model_id)` checks `sum(multipliers) < premium_budget`
   - If budget is None (unlimited), always returns True
   - Free models (0x multiplier) always available regardless of budget

### Validation:
- [ ] Singleton pattern works
- [ ] get_token() returns fresh token from CopilotIntegration
- [ ] get_available_models() returns model list with metadata
- [ ] Premium multiplier lookup works for all models
- [ ] Monthly usage tracking accumulates correctly
- [ ] Budget check works (allows when under, blocks when over)
- [ ] Free models always available regardless of budget

---

## Task 10: Add LiteLLM Adapter Support for copilot_chat/ Prefix
**Goal:** Add `copilot_chat/` prefix handling to the LiteLLM adapter, following the existing `github/` pattern

**File:** `libs/polly-routing/polly_routing/providers/litellm.py`

### Subtasks:
1. **_prepare_kwargs (~L315-328) — Add copilot_chat/ handling:**
   ```python
   if model_id.startswith("copilot_chat/"):
       from integrations.copilot import get_copilot_token
       token = await get_copilot_token()
       if token:
           kwargs["api_base"] = "https://api.github.com/copilot_internal"
           kwargs["api_key"] = token
       else:
           raise ProviderError("Copilot not authenticated")
   ```

2. **complete (~L373-381) — Strip copilot_chat/ prefix:**
   ```python
   if original_model.startswith("copilot_chat/"):
       model = original_model.replace("copilot_chat/", "", 1)
   ```

3. **stream (~L468-474) — Same stripping for streaming:**
   ```python
   if original_model.startswith("copilot_chat/"):
       model = original_model.replace("copilot_chat/", "", 1)
   ```

4. **Post-completion hook — Record premium usage:**
   After successful completion/stream, call:
   ```python
   if original_model.startswith("copilot_chat/"):
       from core.providers.copilot_chat_provider import get_copilot_chat_provider
       provider = get_copilot_chat_provider()
       if provider:
           provider.record_usage(model)
   ```

### Validation:
- [ ] copilot_chat/ prefix detected in _prepare_kwargs
- [ ] Token injection works (api_base + api_key)
- [ ] Prefix stripped before LiteLLM call
- [ ] Premium usage recorded after successful completion
- [ ] Streaming works with copilot_chat/ models
- [ ] Graceful error when Copilot not authenticated

---

## Task 11: Update litellm_config.yaml with Copilot Chat Models
**Goal:** Add copilot_chat provider and models to litellm_config.yaml, update fallback chains

**File:** `config/litellm_config.yaml`

### Subtasks:
1. **Add copilot_chat provider:**
   ```yaml
   copilot_chat:
     api_key_env: COPILOT_ACCESS_TOKEN
     base_url: https://api.github.com/copilot_internal
     enabled: false    # Auto-enabled when Copilot authenticated
     models:
       - id: gpt-5-mini
         name: GPT-5 mini (via Copilot)
         capabilities: [chat, code]
         context_length: 128000
         premium_multiplier: 0
       - id: gpt-4.1
         name: GPT-4.1 (via Copilot)
         capabilities: [chat, code]
         context_length: 128000
         premium_multiplier: 0
       - id: gpt-5.2
         name: GPT-5.2 (via Copilot)
         capabilities: [chat, code, analysis, reasoning]
         context_length: 128000
         premium_multiplier: 1
       - id: claude-sonnet-4.6
         name: Claude Sonnet 4.6 (via Copilot)
         capabilities: [chat, code, analysis]
         context_length: 200000
         premium_multiplier: 1
       - id: claude-opus-4.6
         name: Claude Opus 4.6 (via Copilot)
         capabilities: [chat, code, analysis, reasoning]
         context_length: 200000
         premium_multiplier: 3
       - id: gemini-3-flash
         name: Gemini 3 Flash (via Copilot)
         capabilities: [chat, code]
         context_length: 1000000
         premium_multiplier: 0.33
       - id: gemini-3-pro
         name: Gemini 3 Pro (via Copilot)
         capabilities: [chat, code, analysis, reasoning]
         context_length: 1000000
         premium_multiplier: 1
       - id: grok-code-fast-1
         name: Grok Code Fast 1 (via Copilot)
         capabilities: [chat, code]
         context_length: 131072
         premium_multiplier: 0.25
   ```

2. **Update fallback chains to include Copilot Chat models:**
   ```yaml
   fallback_chains:
     fast:
       - github/openai/gpt-4o-mini
       - copilot_chat/gpt-5-mini
       - copilot_chat/gpt-4.1
       - anthropic/claude-3-haiku-20240307
       - gemini/gemini-1.5-flash-8b-latest
     balanced:
       - github/openai/gpt-4o-mini
       - copilot_chat/gpt-5.2
       - copilot_chat/claude-sonnet-4.6
       - anthropic/claude-sonnet-4-20250514
       - gemini/gemini-1.5-flash-latest
     thorough:
       - github/openai/gpt-4o
       - copilot_chat/claude-opus-4.6
       - copilot_chat/gpt-5.2
       - anthropic/claude-opus-4-20250514
       - gemini/gemini-1.5-pro-latest
   ```

3. **Add model_mappings for Copilot Chat models:**
   ```yaml
   gpt-5-mini: copilot_chat/gpt-5-mini
   gpt-5.2: copilot_chat/gpt-5.2
   claude-opus-4.6: copilot_chat/claude-opus-4.6
   # etc.
   ```

### Validation:
- [ ] Config loads without errors
- [ ] copilot_chat models appear in provider list
- [ ] Fallback chains include copilot_chat entries
- [ ] Model mappings resolve correctly
- [ ] Router V2 can select copilot_chat models

---

## Task 12: Testing — Authentication Flow
**Goal:** Verify full device code authentication lifecycle

### Test Cases:
1. **Happy path:**
   - Start device flow → get user_code
   - Poll → pending → pending → success
   - Verify access_token stored
   - Verify copilot_token obtained
   - Verify is_authenticated() returns True

2. **Expired device code:**
   - Start device flow → wait past expiry
   - Poll → expired
   - Verify error returned, is_authenticated() False

3. **Access denied:**
   - Start device flow → user denies
   - Poll → access_denied
   - Verify error returned

4. **No subscription:**
   - Authenticate successfully
   - check_subscription() → 403
   - Verify subscription status returned correctly

5. **Token refresh:**
   - Set copilot_token expires_at to past
   - Make FIM request → auto-refresh triggered
   - Verify new token obtained and request succeeds

6. **Disconnect:**
   - Authenticate → disconnect
   - Verify all tokens cleared
   - Verify is_authenticated() returns False

### Validation:
- [ ] All auth states handled correctly
- [ ] Token lifecycle (store, refresh, clear) works
- [ ] Error messages are user-friendly

---

## Task 13: Testing — FIM Completions
**Goal:** Verify FIM completion quality and correctness

### Test Cases:
1. **Python completion:**
   ```python
   prefix = "def fibonacci(n):\n    if n <= 1:\n        "
   suffix = "\n    return fibonacci(n-1) + fibonacci(n-2)"
   # Expected: "return n" or similar
   ```

2. **JavaScript completion:**
   ```javascript
   prefix = "function greet(name) {\n    "
   suffix = "\n}"
   # Expected: "return `Hello, ${name}!`;" or similar
   ```

3. **Multi-language support:**
   - Test Python, JavaScript, TypeScript, Rust, Go
   - Verify language hint affects completion quality

4. **Context window limits:**
   - Very long file (> 8K tokens) → verify truncation works
   - Very short prefix (< 50 chars) → verify reasonable completion

5. **Streaming:**
   - Request streaming completion
   - Verify chunks arrive incrementally
   - Verify full response assembled correctly

6. **Cache integration (Phase 0):**
   - Request completion → cache miss → API call → cache store
   - Request same completion → cache hit → fast return
   - Verify cached completion matches original

7. **Ollama fallback:**
   - Disconnect Copilot
   - Request completion with fallback_to_ollama=true
   - Verify local completion returned

### Validation:
- [ ] Completions are syntactically valid code
- [ ] Language-appropriate completions
- [ ] Context truncation doesn't break completions
- [ ] Streaming works end-to-end
- [ ] Cache reduces redundant API calls
- [ ] Fallback provides reasonable completions

---

## Task 14: Testing — Server Endpoints (FIM)
**Goal:** Verify /v1/completions endpoint works with external tools

### Test Cases:
1. **curl test:**
   ```bash
   curl -X POST http://localhost:11436/v1/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"copilot","prompt":"def hello():\n    ","suffix":"","max_tokens":50}'
   ```

2. **OpenAI client compatibility:**
   ```python
   import openai
   client = openai.OpenAI(base_url="http://localhost:11436/v1", api_key="dummy")
   response = client.completions.create(
       model="copilot",
       prompt="def hello():\n    ",
       max_tokens=50
   )
   ```

3. **Streaming via SSE:**
   - Request with stream=true
   - Verify SSE event format matches OpenAI spec

4. **Error handling:**
   - Copilot not authenticated → 401 with clear message
   - Rate limited → 429 with Retry-After header
   - Invalid request → 400 with validation errors

### Validation:
- [ ] Endpoint works with curl
- [ ] Endpoint works with OpenAI Python client
- [ ] Streaming works via SSE
- [ ] Error responses follow OpenAI error format

---

## Task 15: Testing — Copilot Chat Provider
**Goal:** Verify Copilot Chat works as a LiteLLM provider in Router V2

### Test Cases:
1. **Direct Chat completion:**
   - Authenticate Copilot
   - Route query through `copilot_chat/gpt-5.2`
   - Verify response returned correctly

2. **Free model routing:**
   - Configure `prefer_free_models: true`
   - Verify Router V2 selects `copilot_chat/gpt-5-mini` or `copilot_chat/gpt-4.1`
   - Verify 0x multiplier recorded

3. **Premium model routing:**
   - Route query through `copilot_chat/claude-opus-4.6`
   - Verify 3x multiplier recorded in usage tracking
   - Verify monthly usage updated correctly

4. **Fallback chain integration:**
   - Simulate `copilot_chat/gpt-5.2` failure (e.g., 503)
   - Verify Router V2 falls through to `anthropic/claude-sonnet-4-20250514`
   - Verify fallback is transparent to the user

5. **Budget exhaustion:**
   - Set `premium_budget: 10`
   - Make enough requests to exhaust budget
   - Verify paid models blocked, free models still available
   - Verify Router V2 skips blocked Copilot Chat models in fallback chain

6. **Streaming:**
   - Request streaming completion through `copilot_chat/` model
   - Verify chunks arrive incrementally
   - Verify premium usage recorded after stream completes

7. **Shared auth:**
   - Authenticate once via device code
   - Verify both FIM and Chat work with same token
   - Verify token refresh covers both FIM and Chat

### Validation:
- [ ] Chat completion works through LiteLLM adapter
- [ ] Premium multiplier tracking accurate
- [ ] Budget enforcement works
- [ ] Fallback chains work correctly
- [ ] Streaming works
- [ ] Shared auth covers both services

---

## Task 16: Documentation & Specs Update
**Goal:** Update relevant docs

### Subtasks:
1. Update architecture spec with Copilot integration layer (FIM + Chat)
2. Update project status
3. Add changelog entry:
   ```markdown
   ## YYYY-MM-DD - GitHub Copilot Integration (Phase 2)
   - Added device code OAuth for GitHub Copilot authentication
   - Added /v1/completions endpoint for FIM code completion
   - Added Copilot Chat as LiteLLM provider (copilot_chat/ prefix)
   - Added premium request tracking and budget management
   - Integrated with semantic cache (Phase 0) for completion caching
   - Added Copilot Chat models to Router V2 fallback chains
   - Added Ollama fallback for offline/unauthenticated use
   - Added Copilot settings UI with auth flow in Electron
   ```
4. Archive this change folder

### Validation:
- [ ] All specs updated
- [ ] Changelog entry added

---

## Task 17: Final Validation
**Goal:** Comprehensive end-to-end testing of both FIM and Chat

### Test Scenarios:
1. **Fresh install:**
   - [ ] Copilot section shows "Not Connected" in settings
   - [ ] "Connect" button starts device code flow
   - [ ] Full auth flow completes
   - [ ] FIM completions work after auth
   - [ ] Copilot Chat models appear in provider list

2. **App restart:**
   - [ ] Copilot token loaded from keytar
   - [ ] Auth status restored
   - [ ] FIM completions work without re-auth
   - [ ] Copilot Chat routing works without re-auth

3. **Token expiry:**
   - [ ] Auto-refresh works transparently for FIM
   - [ ] Auto-refresh works transparently for Chat
   - [ ] No user action needed

4. **Copilot unavailable:**
   - [ ] FIM fallback to Ollama works (if configured)
   - [ ] Chat fallback through Router V2 works (next provider in chain)
   - [ ] Clear error message (if no fallback)

5. **External IDE:**
   - [ ] /v1/completions works with standard OpenAI client
   - [ ] Streaming works

6. **Copilot Chat routing:**
   - [ ] Fast tier uses free models (GPT-5 mini, GPT-4.1)
   - [ ] Thorough tier uses premium models (Claude Opus 4.6, GPT-5.2)
   - [ ] Premium budget tracking visible in settings
   - [ ] Budget exhaustion handled gracefully

### Success Criteria:
- Device code auth completes successfully
- FIM completions return in < 500ms
- Copilot Chat completions work through standard Polly query pipeline
- Token auto-refresh works without user intervention (covers both FIM and Chat)
- Cache hit rate > 5% for FIM completions
- Ollama fallback works when Copilot unavailable
- External IDE tools can connect via /v1/completions
- Premium request tracking accurate and visible in UI
- Budget exhaustion gracefully falls through to direct API providers

---

## Dependency Order

```
Task 1 (Config — FIM + Chat)
    ↓
Task 2 (Auth Implementation)
    ↓
Task 3 (FIM Completions)
    ↓
Task 4 (CopilotFIMProvider + Cache)
    ↓
Task 5 (Server Endpoints — FIM + Auth) ──→ Task 6 (Electron IPC)
    ↓                                            ↓
Task 7 (Settings UI — FIM + Chat) ←─────────────┘
    ↓
Task 8 (AutonomyMetrics — FIM + Chat)
    ↓
Task 9 (CopilotChatProvider)
    ↓
Task 10 (LiteLLM Adapter — copilot_chat/ prefix)
    ↓
Task 11 (litellm_config.yaml — models + fallback chains)
    ↓
Tasks 12-15 (Testing) ← can run in parallel
    ↓
Task 16 (Docs)
    ↓
Task 17 (Final Validation)
```

---

## Coordination Notes

### Depends on Phase 0 (Semantic Cache):
- FIM completions cached via SemanticCache
- Cache key: embed last 500 chars prefix + first 500 chars suffix
- Cache hit skips Copilot API call entirely
- Copilot Chat responses also benefit from semantic cache (standard chat caching)

### Depends on Phase 1 (Context Distillation) — optional:
- File header portion of FIM context can be distilled
- Reduces token usage for prefix with large import sections
- Not required — distillation is applied opportunistically

### Feeds into Phase 3 (Programmer Persona):
- Programmer persona's `complete` mode routes through CopilotFIMProvider
- Programmer persona's cloud modes (refactor, generate, debug, review) can route through Copilot Chat models
- `get_copilot_provider()` returns the FIM singleton provider
- `get_copilot_chat_provider()` returns the Chat singleton provider
- Router V2 handles Copilot Chat routing automatically via fallback chains
- If Copilot unavailable, complete mode falls back to local Ollama; chat modes fall back to direct API providers
