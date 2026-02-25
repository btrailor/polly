# Proposal: GitHub Copilot Integration — FIM Completions + Copilot Chat

## What
Integrate GitHub Copilot's two distinct APIs into Polly:
1. **Copilot FIM Completions** — Fill-in-the-middle inline code completion for Monaco editor and external IDEs
2. **Copilot Chat** — Multi-model conversational AI (GPT-5.x, Claude Opus 4.6, Sonnet 4.6, Gemini 3, Grok) as a LiteLLM-compatible chat provider

Both APIs share the same authentication (device code OAuth) and the same Copilot subscription. FIM provides inline code suggestions; Chat provides access to top-tier models on a subscription instead of per-token API pricing.

This is **Phase 2** of a four-phase Copilot integration and token conservation plan.

## Why
**Current state:** Polly has:
- **GitHub Models** configured as the primary provider in all fallback chains (GPT-4o, GPT-4o-mini via `https://models.github.ai`), authenticated with `GITHUB_TOKEN`
- **Phase 17 Monaco Code Workspace** specced but not yet implemented, with LSP scoped to "Monaco built-in only; no custom LSP in Phase 17"
- **An OpenAI-compatible chat completions endpoint** (`POST /v1/chat/completions`) that works with IDEs like Cursor and Continue
- **No FIM/code completions capability** — there is no `/v1/completions` endpoint, no prefix/suffix/middle protocol, and no Copilot-specific integration
- **No access to Copilot Chat models** — Claude Opus 4.6, GPT-5.2, Gemini 3 Pro, and other premium models are available through Copilot Chat on a flat subscription, but Polly currently only accesses these (where available) through per-token API providers

**Problem:**
1. **No inline code completion:** Polly's code workspace (Phase 17) will have only basic Monaco IntelliSense — no AI-powered inline suggestions
2. **Chat completions ≠ code completions:** Chat endpoints generate conversational responses; FIM endpoints generate contextual code insertions optimized for the cursor position
3. **Copilot's FIM models are purpose-built:** GitHub Copilot uses specialized models trained specifically for FIM code completion — general chat models produce inferior inline suggestions
4. **GitHub Models ≠ GitHub Copilot:** The existing GitHub integration uses the Models inference API. Copilot has separate APIs with different authentication (device code flow) and different endpoints
5. **No IDE integration path:** Without FIM support, external editors connecting to Polly via the OpenAI-compatible API cannot get code completions
6. **Per-token costs for premium models:** Polly pays per-token for Claude, GPT-4o, etc. through their respective API providers. Copilot Chat offers many of these same models (and newer ones like GPT-5.2, Claude Opus 4.6) on a flat monthly subscription
7. **Missing model coverage:** Models like GPT-5.2, GPT-5.3-Codex, Gemini 3 Pro, and Grok Code Fast 1 are only available through Copilot Chat — no direct API access exists

**Solution:**

### Part A: Copilot FIM
- Authenticates with GitHub Copilot via device code OAuth flow (separate from existing GitHub PAT)
- Sends FIM requests (prefix + suffix + cursor position) to Copilot's completions API
- Exposes a `/v1/completions` endpoint for both Polly's Monaco editor and external IDE tools
- Caches frequent completion patterns via Phase 0's semantic cache
- Distills code context via Phase 1's distillation layer before sending to Copilot

### Part B: Copilot Chat
- Uses the same device code auth as FIM (no additional authentication)
- Integrates as a LiteLLM-compatible provider with `copilot_chat/` prefix
- Adds Copilot Chat models to Router V2 fallback chains
- Tracks premium request multipliers for budget management
- Uses standard `/chat/completions` protocol — compatible with existing LiteLLM adapter patterns

**Benefits:**
1. **Native FIM quality:** Copilot's models are the industry standard for inline code completion
2. **Works in Polly + external IDEs:** The `/v1/completions` endpoint serves both Monaco and tools like Cursor/Continue/Neovim
3. **Token-efficient:** FIM requests are smaller than chat requests (just prefix + suffix, not full conversation)
4. **Stacks with Phases 0-1:** Cache absorbs repeated completion patterns; distillation compresses surrounding code context
5. **Familiar auth flow:** Device code flow is the standard for GitHub Copilot CLI/extensions — well-documented
6. **Subscription-based:** Copilot Individual ($10/month) or included with GitHub Pro/Enterprise — covers both FIM and Chat
7. **Premium models at flat cost:** Access Claude Opus 4.6 (normally $15/$75 per M tokens), GPT-5.2, Gemini 3 Pro, and more on a monthly subscription
8. **Router V2 integration:** Copilot Chat models participate in fallback chains — if a direct API provider fails, Copilot Chat can serve as a fallback (and vice versa)
9. **Budget-aware routing:** Premium request multipliers allow Router V2 to factor in Copilot subscription budget alongside per-token API costs

## Scope

### Backend (Python)

#### Part A: FIM
- **New file:** `integrations/copilot.py` (~400 lines) — CopilotIntegration class with device code auth + FIM completions + Chat completions
- **New file:** `core/providers/copilot_provider.py` (~200 lines) — CopilotFIMProvider for FIM routing
- **Modified:** `interfaces/server.py` — Add `POST /v1/completions` FIM endpoint
- **Modified:** `interfaces/server.py` — Add `POST /copilot/auth/device-code` and `POST /copilot/auth/poll` endpoints

#### Part B: Chat
- **New file:** `core/providers/copilot_chat_provider.py` (~250 lines) — CopilotChatProvider as LiteLLM-compatible adapter
- **Modified:** `libs/polly-routing/polly_routing/providers/litellm.py` — Add `copilot_chat/` prefix handling (same pattern as `github/` at L315-328)
- **Modified:** `config/litellm_config.yaml` — Add `copilot_chat` provider with models and fallback chain entries
- **Modified:** `core/autonomy_metrics.py` — Track premium request multipliers and Copilot Chat usage

#### Shared
- **Modified:** `core/config.py` — Add `copilot` to DEFAULT_CONFIG (covers both FIM and Chat)
- **Modified:** `config.yaml` — Add `copilot:` configuration section
- **Modified:** `core/secrets_manager.py` — Add `copilot_token` credential type

### Frontend (Electron)
- **Modified:** `electron-app/src/main/main.js` — Add Copilot device code auth IPC handlers
- **Modified:** `electron-app/src/renderer/index.html` — Copilot auth UI in settings (device code display, status indicator, Chat model preferences)
- **Modified:** `electron-app/src/renderer/app.js` — Copilot auth flow JS, status polling

### Future Integration Points (not in this phase)
- Monaco editor inline completions provider (Phase 17 implementation)
- Programmer persona's `complete` mode routing to Copilot FIM (Phase 3)
- Programmer persona's cloud modes routing through Copilot Chat (Phase 3)

## Three Distinct GitHub AI Services

| Service | API Endpoint | Auth | Purpose | Polly Status |
|---------|-------------|------|---------|------------|
| **GitHub Models** | `https://models.github.ai` | PAT with `models:read` scope | Chat completions for GPT-4o, etc. | Currently used — `github` provider in litellm_config.yaml |
| **Copilot FIM** | `https://api.github.com/copilot_internal/` | Device code OAuth → session token | FIM code completions (codex-based) | **This proposal — Part A** |
| **Copilot Chat** | `https://api.github.com/copilot_internal/` | Same device code OAuth | Multi-model chat completions (GPT-5.x, Claude, Gemini, Grok) | **This proposal — Part B** |

### Copilot Chat Models and Premium Request Multipliers

| Model | Multiplier | Notes |
|-------|-----------|-------|
| GPT-5 mini | 0x (free) | No premium request cost |
| GPT-4.1 | 0x (free) | No premium request cost |
| GPT-5.2 | 1x | Standard premium request |
| Claude Sonnet 4.6 | 1x | Standard premium request |
| Claude Sonnet 4.5 | 1x | Standard premium request |
| Gemini 2.5 Pro | 1x | Standard premium request |
| Grok Code Fast 1 | 0.25x | Very cheap |
| Gemini 3 Flash | 0.33x | Very cheap |
| Gemini 3 Pro | 1x | Standard premium request |
| Claude Opus 4.6 | 3x | Most expensive |
| GPT-5.3-Codex | 3x | Most expensive |

### Device Code Flow (shared by FIM and Chat)
```
1. Polly requests device code from GitHub
2. User sees: "Enter code XXXX-YYYY at https://github.com/login/device"
3. User authenticates in browser
4. Polly polls for token completion
5. Copilot session token stored in keytar (macOS Keychain)
6. Token auto-refreshes on expiry
7. Same token used for both FIM and Chat requests
```

## Four-Phase Roadmap Context

| Phase | Name | Purpose | Status |
|-------|------|---------|--------|
| 0 | Semantic Response Cache | System-wide query dedup + token savings tracking | Specced |
| 1 | Context Distillation Layer | Local Ollama compresses context before cloud calls | Specced |
| **2** | **GitHub Copilot Integration** | **FIM completions + Chat provider** | **This proposal** |
| 3 | Programmer Persona + Code Routing | Modes: complete/explain/refactor/generate/debug/review | Planned |

Phase 2 builds on Phases 0 and 1: cached FIM patterns skip the Copilot API entirely, code context is distilled before sending prefix/suffix to Copilot, and Copilot Chat responses benefit from the semantic cache. Phase 3 routes the Programmer persona's `complete` mode through FIM and cloud modes through Copilot Chat as a preferred provider.

## Non-Goals
- Implementing the Monaco editor or code workspace (that's Phase 17)
- Replacing all direct API providers with Copilot Chat (Copilot Chat is an additional provider option, not a replacement — direct APIs remain for reliability and model version pinning)
- Building a full LSP server (Phase 17 defers this; Copilot completions are invoked via HTTP, not LSP)
- Multi-line code generation via FIM (that's chat territory; FIM is for inline/single-expression completions)
- Implementing Copilot's @workspace, @terminal, or other agent features (those are VS Code-specific)
