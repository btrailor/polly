# Proposal: Polly Mode Toggle + Granular Model Control

## What
Redesign Polly's model selection UX around a single toggle: **Polly Mode ON** (intelligent routing with token conservation) vs. **Polly Mode OFF** (direct model access). Add per-persona routing preferences in Settings that shape how Polly routes when in auto mode.

This replaces the current provider:tier dropdown with a cleaner two-state system that gives users full control when they want it and full automation when they don't.

## Why
**Current state:** Polly has:
- A **model selector dropdown** with 27 options: 3 "Polly (Auto)" tiers + 24 provider:tier combos (e.g., "anthropic:thorough")
- An **orchestrator toggle** in the UI that is non-functional (`"(not yet implemented)"` in app.js:4036)
- **No way to select a specific model** — users pick a provider + tier, and the router picks the model within that tier
- **No per-persona routing preferences** — all personas use the same routing logic regardless of their domain
- **No visibility into available models** — the dropdown shows providers, not the actual models behind them (user sees "anthropic:thorough" not "Claude Opus 4")
- When Phase 2 adds Copilot Chat models, there will be even more model options with no clean way to expose them

**Problem:**
1. **No direct model access:** A user who knows they want Claude Opus 4.6 for a specific refactoring task can't select it. They can only say "anthropic:thorough" and hope the router picks Opus.
2. **Confusing mental model:** The provider:tier dropdown conflates two decisions (which provider vs. which quality level) and hides the actual model being used.
3. **No persona-aware routing:** The Programmer persona should prefer code-optimized models (Copilot Chat, code-specialized local models). The Professor should prefer local models for explanation tasks. Today, all personas route identically.
4. **All or nothing:** Either you use auto-routing (which you can't customize) or you override to a specific provider (but still can't pick the exact model).
5. **Phase 2 makes this worse:** Adding 8+ Copilot Chat models to the mix without a clean UX creates cognitive overload.

**Solution:**

### Polly Mode Toggle (system-wide)
A prominent toggle in the chat input area:
- **ON (default):** Intelligent routing. Model dropdown is hidden. Polly selects model, tier, and provider based on query complexity, persona, budget, and availability. Token conservation pipelines (cache, distillation) are fully active. Persona routing preferences shape the selection.
- **OFF:** Direct model access. A comprehensive dropdown appears listing every available model individually. User picks exactly which model to use. Cache and distillation still apply (only routing is bypassed). No fallback chains — if the selected model fails, the request fails.

### Model Dropdown (Polly Mode OFF)
A flat, comprehensive list of every connected model, grouped by source:
```
── Copilot Chat ──────────
  GPT-5 mini (free)
  GPT-4.1 (free)
  GPT-5.2
  Claude Opus 4.6
  Claude Sonnet 4.6
  Gemini 3 Flash
  ...
── Anthropic (Direct API) ─
  Claude Opus 4
  Claude Sonnet 4
  Claude 3 Haiku
── OpenAI (Direct API) ────
  GPT-4o
  GPT-4o-mini
  GPT-4 Turbo
── GitHub Models ──────────
  GPT-4o (via GitHub)
  GPT-4o-mini (via GitHub)
── Local (Ollama) ─────────
  llama3.2:3b
  llama3.1:7b
  llama3.1:70b
...
```

### Persona Routing Preferences (Settings)
Per-persona configuration that shapes how Polly routes when in auto mode:
- **Cloud provider preference:** Which provider family to prefer (Copilot Chat, Anthropic Direct, OpenAI Direct, GitHub Models, etc.)
- **Local model preference:** Which Ollama model to use for local routing (e.g., Programmer → code-specialized model, Scribe → general model)
- **Per-mode overrides (optional):** Programmer/refactor can prefer Claude Opus while Programmer/explain prefers local. Overrides the persona-level default for that specific mode.
- **Ships with sensible defaults** optimized per persona

**Benefits:**
1. **Clean binary UX:** One toggle, two states. No confusion about what "anthropic:thorough" means.
2. **Direct model access when needed:** User picks exactly `Claude Opus 4.6 (Copilot)` — no guessing.
3. **Full automation when trusted:** Polly Mode ON hides complexity. Users who trust the system don't see model options at all.
4. **Persona-aware routing:** Each persona routes through models that best serve its domain, not a one-size-fits-all tier.
5. **Token conservation preserved:** Cache and distillation apply in both modes. Only the routing intelligence toggles.
6. **Copilot Chat visibility:** Users see both `Claude Opus 4.6 (Copilot)` and `Claude Opus 4 (Anthropic Direct)` — they can choose subscription-based or per-token.
7. **Future-proof:** As new models and providers are added, they automatically appear in the dropdown.

## Scope

### Backend (Python)
- **Modified:** `interfaces/server.py` — Accept `model_override` (exact model ID) in addition to existing `provider_override`
- **Modified:** `core/polly.py` — Handle `model_override` in query pipeline; skip routing but keep cache/distillation
- **Modified:** `libs/polly-routing/polly_routing/router.py` — Accept persona routing preferences (provider_hint, local_model_hint) to influence selection
- **New endpoint:** `GET /models/available` — Returns comprehensive list of all connected models with metadata (name, provider, capabilities, cost indicator)
- **Modified:** `core/config.py` — Add `persona_routing_preferences` to DEFAULT_CONFIG
- **Modified:** `config.yaml` — Add persona routing preference defaults
- **Modified:** `core/autonomy_metrics.py` — Track `user_override` vs. `auto_routed` in routing decisions
- **Modified:** `interfaces/settings_api.py` — Endpoints for reading/writing persona routing preferences

### Frontend (Electron)
- **Modified:** `electron-app/src/renderer/index.html` — Replace model selector with Polly Mode toggle + conditional model dropdown
- **Modified:** `electron-app/src/renderer/app.js` — Toggle logic, model list fetching, preference management
- **Modified:** `electron-app/src/renderer/styles/main.css` — Toggle styling, dropdown styling
- **Modified:** Settings panel — Per-persona routing preferences UI

## Dependencies
- **Phase 2 (Copilot Integration):** Copilot Chat models populate the dropdown when Copilot is authenticated. Without Phase 2, the dropdown shows only direct API + local models.
- **Phase 3 (Programmer Persona):** Programmer persona's mode routing respects persona preferences. The `MODE_ROUTING` hints interact with persona preferences (preferences take priority when set).
- **Can be implemented independently** of Phases 0-1 (cache/distillation). Those pipelines apply regardless of how the model was selected.

## Non-Goals
- Removing or changing the existing routing tiers (fast/balanced/thorough) — these still power Polly Mode ON
- Building a model comparison or benchmarking UI
- Token-level cost estimation in the dropdown (cost is shown in the response metadata after the fact, as today)
- Supporting model fine-tuning or custom model endpoints (use litellm_config.yaml for that)
- Changing how streaming works based on model selection
