# Design: GitHub Copilot Integration — FIM Completions + Copilot Chat

## Overview
Integrate GitHub Copilot's two APIs into Polly:

1. **Copilot FIM** — Code completions API for fill-in-the-middle functionality. Requires device code OAuth, a new integration module, a new `/v1/completions` endpoint, and token management.
2. **Copilot Chat** — Multi-model chat completions API as a LiteLLM-compatible provider. Uses the same auth as FIM. Adds access to GPT-5.x, Claude Opus 4.6, Sonnet 4.6, Gemini 3, Grok, and more on a flat subscription.

Both APIs share the same authentication flow and token. The FIM integration is independent from LiteLLM (separate `/v1/completions` endpoint). The Chat integration plugs into LiteLLM as a `copilot_chat/` provider prefix, participating in Router V2 fallback chains.

## Architecture

### Component Diagram
```
                    ┌──────────────────────────────────────────┐
                    │        GitHub Copilot (Shared Auth)       │
                    │   Device Code OAuth → Session Token       │
                    │   api.github.com/copilot_internal/        │
                    └──────────┬───────────────┬───────────────┘
                               │               │
                    ┌──────────▼──┐    ┌───────▼──────────────┐
                    │ FIM API     │    │ Chat API             │
                    │ /completions│    │ /chat/completions    │
                    │ (codex)     │    │ (GPT-5, Claude, etc) │
                    └──────┬──────┘    └───────┬──────────────┘
                           │                   │
                    ┌──────▼──────┐    ┌───────▼──────────────┐
                    │ CopilotFIM  │    │ CopilotChat          │
                    │ Provider    │    │ Provider              │
                    │ (standalone)│    │ (LiteLLM adapter)     │
                    └──────┬──────┘    └───────┬──────────────┘
                           │                   │
              ┌────────────▼──┐    ┌───────────▼──────────────┐
              │ POST          │    │ Router V2 Fallback Chains│
              │ /v1/completions│   │ (alongside anthropic/,   │
              │ (FIM endpoint)│    │  openai/, github/, etc)  │
              └───────────────┘    └──────────────────────────┘
                     ▲                        ▲
                     │                        │
              ┌──────┴──────┐    ┌────────────┴───────────────┐
              │ Monaco (17) │    │ Polly Chat / Query Pipeline│
              │ External IDE│    │ (same as all other cloud   │
              │ Cursor, etc │    │  providers)                │
              └─────────────┘    └────────────────────────────┘
```

### Three GitHub Integrations (Separate Concerns)
```
integrations/
  ├── github.py              (existing) Data fetching: repos, issues, PRs → RAG
  └── copilot.py             [NEW]     Auth + FIM completions + Chat completions

core/providers/
  ├── copilot_provider.py    [NEW]     FIM provider (standalone, not LiteLLM)
  └── copilot_chat_provider.py [NEW]   Chat provider (LiteLLM adapter pattern)

libs/polly-routing/polly_routing/providers/
  └── litellm.py             [MOD]     Add copilot_chat/ prefix handling

Authentication:
  ├── GitHub PAT/OAuth       (existing) GITHUB_TOKEN — for Models API + data fetching
  └── Copilot Device Code    [NEW]     COPILOT_TOKEN — for FIM + Chat (same token)
```

### Key Design Decisions

#### 1. Authentication: Device Code Flow
**Decision:** Implement GitHub's device code OAuth flow for Copilot authentication, separate from the existing GitHub PAT.

**Rationale:**
- GitHub Copilot uses a different auth mechanism than GitHub Models
- Device code flow is the standard for Copilot CLI/extensions
- Users need an active Copilot subscription ($10/month Individual, or included with Pro/Enterprise)
- The existing `GITHUB_TOKEN` PAT does not grant Copilot access

**Flow:**
```
1. POST https://github.com/login/device/code
   → {device_code, user_code, verification_uri, interval}

2. Display to user: "Enter code XXXX-YYYY at https://github.com/login/device"

3. Poll: POST https://github.com/login/oauth/access_token
   grant_type=urn:ietf:params:oauth:grant-type:device_code
   device_code={device_code}
   → Eventually: {access_token, token_type}

4. Exchange for Copilot token:
   GET https://api.github.com/copilot_internal/v2/token
   Authorization: Bearer {access_token}
   → {token: "tid=...", expires_at: ...}

5. Store Copilot token in keytar (macOS Keychain)
6. Auto-refresh before expiry
```

**Token storage:**
- Device code access token → `keytar: COPILOT_ACCESS_TOKEN`
- Copilot session token → in-memory (short-lived, auto-refreshed)
- Both tokens managed by `CopilotIntegration`, not `secrets_manager.py`

#### 2. FIM Request Format
**Decision:** Implement the standard FIM protocol used by Copilot: prefix + suffix with a special separator token.

**Request format:**
```json
{
    "prompt": "<code_before_cursor>",
    "suffix": "<code_after_cursor>",
    "max_tokens": 128,
    "temperature": 0.0,
    "top_p": 1,
    "n": 1,
    "stop": ["\n\n", "\nclass ", "\ndef ", "\n#"],
    "stream": true
}
```

**Response format (OpenAI-compatible):**
```json
{
    "id": "cmpl-...",
    "object": "text_completion",
    "created": 1234567890,
    "model": "copilot-codex",
    "choices": [{
        "text": "<inserted_code>",
        "index": 0,
        "logprobs": null,
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 150,
        "completion_tokens": 23,
        "total_tokens": 173
    }
}
```

#### 3. Context Window Construction
**Decision:** Build the FIM context from the current file content + relevant imports/types from other open files.

**Context strategy:**
```
[File header: imports, class definitions from other open files]
[Current file content before cursor] ← prefix
<CURSOR>
[Current file content after cursor]  ← suffix
```

**Context budget (Copilot's context window ~8K tokens):**
- Prefix: up to 4K tokens (code before cursor, prioritizing nearby lines)
- Suffix: up to 2K tokens (code after cursor)
- File header: up to 2K tokens (imports, type definitions from open tabs)

**Phase 1 interaction:** Context distillation can compress the file header portion before sending to Copilot, reducing token usage while preserving type information.

#### 4. Endpoint Design
**Decision:** Expose a standard OpenAI-compatible `/v1/completions` endpoint that works with both Polly's Monaco editor and external IDE tools.

**Rationale:**
- The `/v1/completions` endpoint is the industry standard for code completions
- Cursor, Continue, Copilot.vim, and other tools can connect to this endpoint
- Polly's Monaco editor (Phase 17) can use the same endpoint
- Distinct from the existing `/v1/chat/completions` (chat) endpoint

**Endpoint:**
```
POST /v1/completions
Content-Type: application/json

{
    "model": "copilot",           // or "copilot-codex"
    "prompt": "def fibonacci(n):\n    ",
    "suffix": "\n    return result",
    "max_tokens": 128,
    "temperature": 0.0,
    "stream": true,
    "stop": ["\n\n"]
}
```

#### 5. Caching Strategy (Phase 0 Integration)
**Decision:** Cache FIM completions in the semantic cache, keyed by prefix + suffix hash.

**Cache key:** Embed the last ~500 chars of prefix + first ~500 chars of suffix. This captures the local code context around the cursor without embedding the entire file.

**When to cache:**
- Completion returned successfully
- Completion is non-trivial (> 5 characters)

**When to skip cache:**
- Very short prefix (< 50 chars — too early in file to be meaningful)
- User is typing rapidly (debounce at client level)

#### 6. Subscription Verification
**Decision:** Check Copilot subscription status during auth and display clear messaging if not subscribed.

**Verification:** After device code auth, call `GET /copilot_internal/v2/token`. If this returns 401/403, the user doesn't have a Copilot subscription.

**UI messaging:**
- "Copilot requires a GitHub Copilot subscription ($10/month or included with GitHub Pro)"
- Link to subscription page: `https://github.com/features/copilot`

---

### Part B: Copilot Chat Design Decisions

#### 7. Copilot Chat as a LiteLLM Provider
**Decision:** Integrate Copilot Chat as a LiteLLM-compatible provider using the existing `copilot_chat/` prefix pattern, following the same approach as the `github/` provider.

**Rationale:**
- Copilot Chat uses the standard `/chat/completions` protocol — it's structurally identical to OpenAI/Anthropic chat APIs
- The LiteLLM adapter already has special handling for the `github/` prefix (L315-328 in litellm.py). The same pattern works for `copilot_chat/`
- This means Copilot Chat models can participate in Router V2 fallback chains, tier assignments, and budget tracking — no new routing infrastructure needed
- Models are referenced as `copilot_chat/gpt-5.2`, `copilot_chat/claude-opus-4.6`, etc.

**LiteLLM adapter changes (litellm.py `_prepare_kwargs`):**
```python
# Existing github/ handling (L315-328):
if model_id.startswith("github/"):
    kwargs["api_base"] = self.config.get("providers", {}).get("github", {}).get("base_url")
    kwargs["api_key"] = os.environ.get("GITHUB_TOKEN")

# NEW copilot_chat/ handling (same pattern):
if model_id.startswith("copilot_chat/"):
    kwargs["api_base"] = "https://api.github.com/copilot_internal"
    kwargs["api_key"] = get_copilot_token()  # From CopilotIntegration
    # Strip prefix for LiteLLM: "copilot_chat/gpt-5.2" → "gpt-5.2"
```

**Model ID stripping in `complete()` and `stream()`:**
```python
# Existing (L373-381):
if original_model.startswith("github/"):
    model = original_model.replace("github/", "", 1)

# NEW:
if original_model.startswith("copilot_chat/"):
    model = original_model.replace("copilot_chat/", "", 1)
```

#### 8. Premium Request Tracking
**Decision:** Track Copilot Chat usage in terms of premium request multipliers, stored in AutonomyMetrics alongside existing per-token cost tracking.

**Rationale:**
- Copilot subscriptions have a monthly premium request allowance (varies by plan)
- Different models consume different amounts: Claude Opus 4.6 = 3x, GPT-5 mini = 0x (free)
- Polly's BudgetManager needs to know the "cost" of a Copilot Chat request to make routing decisions
- The multiplier system maps cleanly to BudgetManager's existing cost-per-request tracking

**Multiplier table (stored in config):**
```python
COPILOT_CHAT_MULTIPLIERS = {
    "gpt-5-mini": 0,           # Free
    "gpt-4.1": 0,              # Free
    "gpt-4.1-mini": 0,         # Free
    "grok-code-fast-1": 0.25,
    "gemini-3-flash": 0.33,
    "gpt-5.2": 1,
    "claude-sonnet-4.6": 1,
    "claude-sonnet-4.5": 1,
    "gemini-2.5-pro": 1,
    "gemini-3-pro": 1,
    "claude-opus-4.6": 3,
    "gpt-5.3-codex": 3,
}
```

**Budget integration:**
- Each request records: `{model, multiplier, timestamp}`
- Monthly usage: `sum(multipliers)` vs. monthly allowance
- Router V2 can factor this in: if premium budget is running low, prefer free models (GPT-5 mini, GPT-4.1) or direct API providers

#### 9. Copilot Chat in Fallback Chains
**Decision:** Add Copilot Chat models to Router V2 fallback chains as additional options, not replacements.

**Rationale:**
- Copilot Chat provides access to models that may be down or rate-limited on their primary API
- Having `copilot_chat/claude-opus-4.6` as a fallback for `anthropic/claude-opus-4-20250514` provides redundancy
- Free/cheap Copilot Chat models (GPT-5 mini, GPT-4.1) are excellent fallbacks for the `fast` tier

**Updated fallback chains (litellm_config.yaml):**
```yaml
fallback_chains:
  fast:
    - github/openai/gpt-4o-mini
    - copilot_chat/gpt-5-mini          # FREE — 0x multiplier
    - copilot_chat/gpt-4.1             # FREE — 0x multiplier
    - anthropic/claude-3-haiku-20240307
    - gemini/gemini-1.5-flash-8b-latest
  balanced:
    - github/openai/gpt-4o-mini
    - copilot_chat/gpt-5.2             # 1x multiplier
    - copilot_chat/claude-sonnet-4.6   # 1x multiplier
    - anthropic/claude-sonnet-4-20250514
    - gemini/gemini-1.5-flash-latest
  thorough:
    - github/openai/gpt-4o
    - copilot_chat/claude-opus-4.6     # 3x multiplier
    - copilot_chat/gpt-5.2             # 1x multiplier
    - anthropic/claude-opus-4-20250514
    - gemini/gemini-1.5-pro-latest
```

#### 10. Copilot Chat Token Injection
**Decision:** Copilot Chat uses the same short-lived session token as FIM. The CopilotIntegration class manages the token lifecycle; the LiteLLM adapter retrieves the current token via `get_copilot_token()`.

**Token flow:**
```
CopilotIntegration (manages auth + refresh)
    |
    ├── FIM requests: copilot.complete(prefix, suffix) — uses token directly
    |
    └── Chat requests: get_copilot_token() → LiteLLM adapter → api_key kwarg
```

**Thread safety:** The token is refreshed before expiry by `_ensure_token()`. Both FIM and Chat calls go through this method. No concurrent refresh issues because Python's asyncio is single-threaded.

## API Design

### CopilotIntegration Class

```python
class CopilotIntegration:
    """
    GitHub Copilot integration for FIM code completions.
    
    Handles device code authentication, token management,
    and FIM API calls.
    """
    
    def __init__(self, config: dict):
        """
        Args:
            config: copilot config section with keys:
                    enabled, client_id, max_tokens, temperature
        """
        self.config = config
        self.access_token: Optional[str] = None
        self.copilot_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    # --- Authentication ---
    
    async def start_device_flow(self) -> dict:
        """
        Start device code OAuth flow.
        
        Returns:
            {
                "user_code": "XXXX-YYYY",
                "verification_uri": "https://github.com/login/device",
                "device_code": "...",
                "interval": 5
            }
        """
    
    async def poll_for_token(self, device_code: str, interval: int = 5) -> bool:
        """
        Poll GitHub for token after user completes device auth.
        
        Returns True when authenticated, False if expired/denied.
        """
    
    async def refresh_copilot_token(self) -> bool:
        """
        Refresh the short-lived Copilot session token using
        the long-lived access token.
        """
    
    async def check_subscription(self) -> bool:
        """Check if user has active Copilot subscription."""
    
    def is_authenticated(self) -> bool:
        """Check if Copilot tokens are valid and not expired."""
    
    # --- FIM Completions ---
    
    async def complete(
        self,
        prefix: str,
        suffix: str = "",
        language: str = "python",
        max_tokens: int = 128,
        temperature: float = 0.0,
        stop: Optional[list[str]] = None,
        stream: bool = False
    ) -> Union[dict, AsyncIterator[str]]:
        """
        Request FIM completion from Copilot.
        
        Args:
            prefix: Code before cursor
            suffix: Code after cursor
            language: Programming language hint
            max_tokens: Max completion length
            temperature: Sampling temperature (0.0 = deterministic)
            stop: Stop sequences
            stream: Whether to stream response
        
        Returns:
            OpenAI-compatible completion response dict,
            or async iterator of text chunks if streaming
        """
    
    # --- Token Management ---
    
    async def _ensure_token(self):
        """Ensure Copilot token is valid, refresh if needed."""
    
    async def _store_token(self, token: str, key: str):
        """Store token in keytar via Electron IPC or env."""
    
    async def _load_token(self, key: str) -> Optional[str]:
        """Load token from keytar or env."""
```

### CopilotFIMProvider Class

```python
class CopilotFIMProvider:
    """
    Provider adapter for Copilot FIM, used by the Programmer
    persona's 'complete' mode (Phase 3).
    
    This is NOT a ProviderAdapter (chat interface) — it's a
    separate FIM-specific provider.
    """
    
    def __init__(self, copilot: CopilotIntegration, cache=None):
        self.copilot = copilot
        self.cache = cache    # SemanticCache from Phase 0
    
    async def complete_fim(
        self,
        prefix: str,
        suffix: str,
        language: str = "python",
        **kwargs
    ) -> dict:
        """
        FIM completion with optional caching.
        
        1. Check cache (Phase 0) for similar prefix+suffix
        2. If miss, call Copilot API
        3. Cache result
        4. Return OpenAI-compatible response
        """
    
    def is_available(self) -> bool:
        """Check if Copilot is authenticated and ready."""
```

### CopilotChatProvider Class

```python
class CopilotChatProvider:
    """
    LiteLLM-compatible provider adapter for Copilot Chat.
    
    Provides access to Copilot Chat's multi-model chat completions
    (GPT-5.x, Claude, Gemini, Grok) via the standard /chat/completions
    protocol. Integrates with the LiteLLM adapter using the
    copilot_chat/ prefix pattern.
    """
    
    def __init__(self, copilot: CopilotIntegration, config: dict):
        """
        Args:
            copilot: Shared CopilotIntegration instance (same as FIM)
            config: copilot.chat config section with keys:
                    enabled, models, premium_budget, multipliers
        """
        self.copilot = copilot
        self.config = config
        self.multipliers = config.get("multipliers", COPILOT_CHAT_MULTIPLIERS)
        self._monthly_usage: list[dict] = []  # [{model, multiplier, timestamp}]
    
    async def get_token(self) -> Optional[str]:
        """
        Get current Copilot session token for LiteLLM adapter injection.
        
        Called by litellm.py _prepare_kwargs when model starts with copilot_chat/.
        Ensures token is fresh via CopilotIntegration._ensure_token().
        """
    
    def get_available_models(self) -> list[dict]:
        """
        Return list of available Copilot Chat models with metadata.
        
        Returns:
            [{
                "id": "copilot_chat/gpt-5.2",
                "name": "GPT-5.2 (via Copilot)",
                "multiplier": 1,
                "capabilities": ["chat", "code", "analysis"],
                "context_length": 128000
            }, ...]
        """
    
    def get_multiplier(self, model_id: str) -> float:
        """Get premium request multiplier for a model."""
    
    def record_usage(self, model_id: str):
        """Record a premium request for budget tracking."""
    
    def get_monthly_usage(self) -> dict:
        """
        Get current month's premium request usage.
        
        Returns:
            {
                "total_multiplier": 45.5,
                "request_count": 38,
                "by_model": {"gpt-5.2": 20, "claude-opus-4.6": 6, ...},
                "budget_remaining": 254.5  # if budget configured
            }
        """
    
    def is_available(self) -> bool:
        """Check if Copilot is authenticated and Chat is enabled."""
    
    def is_budget_available(self, model_id: str) -> bool:
        """
        Check if premium budget allows this model request.
        
        If no budget configured, always returns True.
        If budget exhausted, only free models (0x multiplier) return True.
        """
```

### Module-Level Token Accessor

```python
# In integrations/copilot.py — for use by LiteLLM adapter

_instance: Optional[CopilotIntegration] = None

def init_copilot(config: dict) -> CopilotIntegration:
    """Initialize the shared CopilotIntegration singleton."""
    global _instance
    _instance = CopilotIntegration(config)
    return _instance

def get_copilot() -> Optional[CopilotIntegration]:
    """Get the CopilotIntegration singleton."""
    return _instance

async def get_copilot_token() -> Optional[str]:
    """
    Get current Copilot session token.
    Called by LiteLLM adapter for copilot_chat/ prefix handling.
    Returns None if not authenticated.
    """
    if _instance and _instance.is_authenticated():
        await _instance._ensure_token()
        return _instance.copilot_token
    return None
```

### Server Endpoints

```python
# --- FIM Completions ---

@app.post("/v1/completions")
async def text_completions(request: CompletionRequest):
    """
    OpenAI-compatible completions endpoint for FIM.
    Works with Monaco editor, Cursor, Continue, Neovim, etc.
    
    Routes to Copilot when model="copilot", falls back to
    Ollama for local completion if Copilot unavailable.
    """

# --- Copilot Auth ---

@app.post("/copilot/auth/device-code")
async def copilot_start_auth():
    """
    Start Copilot device code authentication.
    Returns user_code and verification_uri for display.
    """

@app.post("/copilot/auth/poll")
async def copilot_poll_auth(device_code: str):
    """
    Poll for Copilot auth completion.
    Returns {authenticated: true/false, error?: string}.
    """

@app.get("/copilot/auth/status")
async def copilot_auth_status():
    """
    Get current Copilot auth status.
    Returns {authenticated: bool, subscription: bool, expires_at: float}.
    """

@app.delete("/copilot/auth/disconnect")
async def copilot_disconnect():
    """Revoke Copilot tokens and disconnect."""
```

## Data Flow

### 1. FIM Completion Request
```
Client (Monaco/IDE) → POST /v1/completions
    {prefix: "def fib(n):\n    ", suffix: "\n    return result"}
    |
[Phase 0] Cache check (embed prefix[-500:] + suffix[:500])
    |
    ├── CACHE HIT → return cached completion
    |
    └── CACHE MISS
        |
        CopilotIntegration._ensure_token()
        |
        [Phase 1] Distill file header context (if provided)
        |
        POST https://api.github.com/copilot_internal/v2/completions
            Authorization: Bearer {copilot_token}
            {prompt: prefix, suffix: suffix, max_tokens: 128}
        |
        Response: {choices: [{text: "if n <= 1:\n        return n\n    ..."}]}
        |
        [Phase 0] Cache store
        |
        Return to client
```

### 2. Device Code Authentication
```
User clicks "Connect Copilot" in Settings
    |
Frontend → POST /copilot/auth/device-code
    |
Backend → POST https://github.com/login/device/code
    client_id=Iv1.XXXXX
    scope=read:user
    |
Response: {user_code: "ABCD-1234", verification_uri, device_code, interval}
    |
Frontend displays: "Enter ABCD-1234 at github.com/login/device"
    |
Frontend polls: POST /copilot/auth/poll every {interval} seconds
    |
Backend polls: POST https://github.com/login/oauth/access_token
    |
    ├── pending → {authenticated: false}
    ├── expired → {authenticated: false, error: "expired"}
    └── success → {authenticated: true}
        |
        Backend: GET https://api.github.com/copilot_internal/v2/token
        → copilot_token stored in memory + access_token in keytar
```

### 3. Token Refresh
```
FIM request arrives
    |
_ensure_token() checks token_expires_at
    |
    ├── Valid → proceed with request
    └── Expired/Near-expiry →
        GET https://api.github.com/copilot_internal/v2/token
        Authorization: Bearer {access_token}
        → New copilot_token + new expires_at
        → Proceed with request
```

## Configuration

### config.yaml Addition
```yaml
copilot:
  enabled: false                 # Disabled until user authenticates
  client_id: "Iv1.b507a08c87ecfe98"  # GitHub Copilot CLI client ID
  
  # FIM Completions
  fim:
    max_tokens: 128                # Default max completion length
    temperature: 0.0               # Deterministic completions
    stop_sequences:                # Default stop sequences
      - "\n\n"
      - "\nclass "
      - "\ndef "
      - "\n#"
    context_window: 8192           # Max tokens for prefix + suffix
    cache_completions: true        # Use Phase 0 cache for FIM
    fallback_to_ollama: true       # Use local Ollama if Copilot unavailable
  
  # Copilot Chat
  chat:
    enabled: true                  # Enable Chat when Copilot is authenticated
    premium_budget: null           # Monthly premium request budget (null = unlimited)
    prefer_free_models: false      # Prefer 0x multiplier models when possible
    models:                        # Which Copilot Chat models to enable
      - gpt-5-mini                 # 0x — free
      - gpt-4.1                    # 0x — free
      - gpt-4.1-mini              # 0x — free
      - gpt-5.2                    # 1x
      - claude-sonnet-4.6         # 1x
      - gemini-3-flash            # 0.33x
      - grok-code-fast-1          # 0.25x
      - claude-opus-4.6           # 3x
      - gemini-3-pro              # 1x
```

### core/config.py DEFAULT_CONFIG Addition
```python
"copilot": {
    "enabled": False,
    "client_id": "Iv1.b507a08c87ecfe98",
    "fim": {
        "max_tokens": 128,
        "temperature": 0.0,
        "stop_sequences": ["\n\n", "\nclass ", "\ndef ", "\n#"],
        "context_window": 8192,
        "cache_completions": True,
        "fallback_to_ollama": True,
    },
    "chat": {
        "enabled": True,
        "premium_budget": None,
        "prefer_free_models": False,
        "models": [
            "gpt-5-mini", "gpt-4.1", "gpt-4.1-mini",
            "gpt-5.2", "claude-sonnet-4.6", "gemini-3-flash",
            "grok-code-fast-1", "claude-opus-4.6", "gemini-3-pro",
        ],
    },
}
```

### core/secrets_manager.py Addition
```python
'copilot': {
    'key_name': 'COPILOT_ACCESS_TOKEN',
    'env_var': 'COPILOT_ACCESS_TOKEN',
    'description': 'GitHub Copilot access token (via device code flow)',
    'format': 'ghu_...',
    'validate_prefix': ['ghu_']
}
```

## Settings UI

### Electron Settings (Integrations section)
```
GitHub Copilot
  Status: [Connected ✓] / [Not Connected]
  Subscription: [Active] / [Not Found]
  [Connect Copilot]  ← starts device code flow
  
  When "Connect" clicked:
  ┌─────────────────────────────────────────┐
  │  Enter code ABCD-1234 at               │
  │  github.com/login/device                │
  │                                         │
  │  [Open GitHub] [Cancel]                 │
  │                                         │
  │  Waiting for authentication...          │
  └─────────────────────────────────────────┘
  
  After connected:
  
  FIM Completions
  [x] Enable Copilot completions
  [x] Cache completions (Phase 0)
  [x] Fall back to local model
  
  Copilot Chat
  [x] Enable Copilot Chat models
  Premium usage this month: 23/300 requests
  
  Available models:
  [x] GPT-5 mini (free)          0x
  [x] GPT-4.1 (free)             0x
  [x] GPT-5.2                    1x
  [x] Claude Sonnet 4.6          1x
  [x] Gemini 3 Flash             0.33x
  [ ] Claude Opus 4.6            3x  ← expensive, opt-in
  [ ] GPT-5.3-Codex              3x  ← expensive, opt-in
  
  [Disconnect]
```

## Files to Create/Modify

### New Files
1. `integrations/copilot.py` (~400 lines) — Shared auth, FIM completions, token accessor
2. `core/providers/copilot_provider.py` (~200 lines) — FIM provider with cache integration
3. `core/providers/copilot_chat_provider.py` (~250 lines) — Chat provider with premium tracking

### Modified Files
1. `interfaces/server.py` — POST /v1/completions, copilot auth endpoints, copilot chat status endpoint
2. `core/config.py` — Add copilot to DEFAULT_CONFIG (FIM + Chat sections)
3. `config.yaml` — Add copilot section (FIM + Chat config)
4. `core/secrets_manager.py` — Add copilot_token credential type
5. `core/autonomy_metrics.py` — Track FIM stats + Chat premium request usage
6. `libs/polly-routing/polly_routing/providers/litellm.py` — Add `copilot_chat/` prefix handling in `_prepare_kwargs`, `complete`, `stream`
7. `config/litellm_config.yaml` — Add `copilot_chat` provider with models, update fallback chains
8. `electron-app/src/main/main.js` — Copilot device code IPC handlers
9. `electron-app/src/renderer/index.html` — Copilot auth UI + Chat model preferences
10. `electron-app/src/renderer/app.js` — Copilot auth flow JS + Chat model display

### Unchanged Files
- `integrations/github.py` — Data fetching integration is separate
- `core/polly.py` — FIM is a separate endpoint; Chat goes through standard LiteLLM routing
- `libs/polly-routing/polly_routing/router.py` — Router V2 logic unchanged; Copilot Chat models are just more entries in fallback chains
- `libs/polly-routing/polly_routing/providers/base.py` — ProviderAdapter ABC unchanged

## Edge Cases

### 1. No Copilot Subscription
**Handling:** `check_subscription()` returns False → display "Requires Copilot subscription" with link to `github.com/features/copilot`. Auth endpoints return clear error.

### 2. Token Expiry During Completion
**Handling:** `_ensure_token()` checks expiry before every request. If token refresh fails (access_token also expired), return error and prompt re-authentication.

### 3. Copilot Rate Limiting
**Handling:** Copilot has rate limits (~30 requests/minute for Individual). Return 429 to client with `Retry-After` header. Client-side debouncing (300ms) prevents most rate limit hits.

### 4. Copilot Service Outage
**Handling:** If `fallback_to_ollama` is true, route FIM to local Ollama model (Code Llama or similar) for basic completions. Quality will be lower but service continues.

### 5. Network Offline
**Handling:** Copilot requires internet. Fall back to Ollama if configured, or return empty completion with error flag.

### 6. Large Files
**Handling:** Context window is 8K tokens. Prefix and suffix are truncated to fit: prioritize code nearest the cursor, then file header (imports/types).

### 7. Copilot Chat Premium Budget Exhausted
**Handling:** When monthly premium budget is exhausted, `is_budget_available()` returns False for paid models. Router V2 skips `copilot_chat/` entries in fallback chains (except free models like GPT-5 mini, GPT-4.1). Falls through to direct API providers or other fallbacks.

### 8. Copilot Chat Model Unavailable
**Handling:** Copilot Chat model availability can change. If a model returns 404 or is removed, the LiteLLM adapter treats it as a provider failure → Router V2 falls through to the next entry in the fallback chain. The model is marked as unavailable in the CopilotChatProvider until the next health check.

### 9. Copilot Chat Rate Limiting
**Handling:** Copilot Chat has separate rate limits from FIM. If rate limited (429), the LiteLLM adapter returns the error → Router V2 tries the next fallback. The `Retry-After` header is respected for subsequent requests to the same model.

## Testing Strategy

### Unit Tests — FIM
1. Device code flow initiation returns user_code
2. Token polling handles pending/success/expired states
3. Token refresh works before expiry
4. FIM request builds correct payload
5. Response parsing handles all Copilot response formats
6. Cache integration works for completions

### Unit Tests — Copilot Chat
1. `copilot_chat/` prefix detected and handled in LiteLLM adapter
2. Token injection via `get_copilot_token()` works
3. Model ID stripping: `copilot_chat/gpt-5.2` → `gpt-5.2`
4. Premium multiplier lookup returns correct values
5. Monthly usage tracking accumulates correctly
6. Budget check allows free models when budget exhausted
7. Budget check blocks paid models when budget exhausted

### Integration Tests — FIM
1. Full auth flow: device code → poll → token → completion
2. FIM completion for Python, JavaScript, TypeScript, Rust
3. Streaming completions work
4. Token auto-refresh works
5. Fallback to Ollama when Copilot unavailable
6. Cache hit/miss for repeated completions

### Integration Tests — Copilot Chat
1. Chat completion through LiteLLM adapter with `copilot_chat/gpt-5.2`
2. Streaming chat completion works
3. Fallback chain: `copilot_chat/` model fails → next provider works
4. Router V2 selects Copilot Chat model in `fast` tier (free models)
5. Router V2 selects Copilot Chat model in `thorough` tier
6. Premium budget tracking persists across requests
7. Same auth token serves both FIM and Chat requests

## Success Metrics
1. FIM completions return in < 500ms (excluding auth)
2. Device code auth completes successfully
3. Token auto-refresh works without user intervention (for both FIM and Chat)
4. Cache hit rate > 5% for FIM completions
5. Fallback to Ollama works when Copilot unavailable
6. External IDE tools (Cursor, Continue) can connect via /v1/completions
7. Copilot Chat models appear in Router V2 fallback chains and are selectable
8. Copilot Chat completions work through standard Polly query pipeline
9. Premium request tracking accurately reflects multipliers
10. Budget exhaustion gracefully falls through to direct API providers
