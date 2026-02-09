# Void-style first-time setup and model integration (design reference)

**Purpose:** Document patterns we want Polly to adopt from Void (and Cursor) for **first-time setup** and **model integration**. We reimplement these in Polly's stack; Void is design reference only. This spec also provides a **Void codebase audit guide** so you can inspect the fork and fill in concrete UX/details.

**Void fork location (for audit):** `~/projects/polly-void` or `/Users/brettgershon/projects/polly-void` (not in the Polly repo).

---

## 1. First-time setup patterns (Void/Cursor-style)

### Target patterns we want in Polly

| Pattern | Description | Polly today | Target |
|--------|-------------|-------------|--------|
| **Single entry, clear steps** | First launch shows a short, linear flow (e.g. welcome → pick folder → configure AI → done). No “wizard hell”; minimal steps. | Multi-step setup (vault path, code paths, install, optional pull models); `setupComplete` gate; steps in renderer. | Keep step count low; optional “quick start” vs “custom”; match Void’s clarity. |
| **Dependency check before use** | Before marking setup complete, verify required services (e.g. backend, optional Ollama). Show status and retry. | We check server + Ollama; show status; block “Finish” until server OK. | Align with Void: show what’s required vs optional; allow “continue anyway” for optional deps. |
| **Skip / resume** | User can close and resume later; state persisted. No forced completion in one sitting. | We persist vault/code paths and `setupComplete`; can reset from Settings. | Same idea; ensure “resume” reopens at the right step. |
| **Welcome / get-started content** | After setup, first-time users see a short “Get started” or welcome content (recent files, quick actions, or tips). | Dashboard with stats; no dedicated “first run” welcome. | Optional: one-time “Get started” panel or first-run tips (Phase 18 alignment). |
| **No duplicate configuration** | API keys and model config live in one place (e.g. Settings → AI/Models). Setup doesn’t ask for keys unless we choose a “minimal” path that defers to Settings. | API keys in Settings → API Keys; model choice in chat/session. | Single source of truth; setup either collects minimal info (folder, optional “add key later”) or deep-links to Settings for keys. |

### Implementation direction (Polly)

- **Keep** current flow: check `setupComplete` → show setup view vs main app; persist vault path, code paths, `setupComplete`.
- **Adopt Void-style UX:** Reduce perceived steps (e.g. combine “paths” into one screen); show required vs optional deps clearly; “Add API keys later” → Settings.
- **Optional (Phase 18):** First-run welcome / get-started view after setup; onboarding questionnaire can reference same patterns.

---

## 2. Model integration patterns (Void/Cursor-style)

### Target patterns we want in Polly

| Pattern | Description | Polly today | Target |
|--------|-------------|-------------|--------|
| **Provider-agnostic** | Support multiple backends: OpenAI, Anthropic, Ollama, OpenAI-compatible (e.g. LiteLLM, local). User picks provider and optionally model. | Multi-model routing (Phase 11); provider/tier in model selector; API keys per provider in Settings. | Keep; ensure UI makes “provider + model” obvious (Void-style). |
| **Direct connection** | Keys and model config are client-side (or our backend stores keys); we don’t route through a third-party proxy. Void emphasizes “connect directly to your LLM.” | We store keys in backend/settings; our server talks to providers. | Same idea: user’s keys, our backend as orchestrator; no opaque third-party middleman. |
| **API keys in one place** | One Settings surface for all API keys (OpenAI, Anthropic, etc.). Optional: “test connection” before saving. | Settings → API Keys tab; per-provider keys. | Add “Test” where feasible; keep single place. |
| **Model selector at point of use** | Current model (and optionally provider) visible near chat input; one click to change. | Model selector in chat (provider:tier or auto:tier); stored in sessionStorage. | Already aligned with UX pivot (model/persona at input); ensure copy and behavior match Void’s “at a glance” feel. |
| **Local / Ollama first-class** | Ollama (and similar) as a first-class option, not buried. No key required for local. | We check Ollama status; use in routing. | Keep; in setup and Settings, show “Ollama (no key required)” clearly. |
| **Optional base URL** | For OpenAI-compatible endpoints, allow custom base URL + optional API key (e.g. LiteLLM, vLLM). | May exist in backend; confirm in Settings UI. | Expose in Settings if not already; match Void’s “any LLM” story. |

### Implementation direction (Polly)

- **Settings:** Single “API keys / Models” surface: list providers (OpenAI, Anthropic, Ollama, Custom/OpenAI-compatible); per-provider key and optional base URL; “Test connection” where applicable.
- **Chat / Code:** Model (and persona) selector at input; show current provider/model; no hunting in Settings for normal use.
- **Setup:** Either “Add keys in Settings after” or one optional step “Connect your first model” that deep-links to Settings or a minimal key entry.

---

## 3. Void codebase audit guide

Use this when you have the Void fork at `~/projects/polly-void` (or your clone). Goal: find **concrete** first-time setup flow and model integration UI/flow so we can document or copy patterns (conceptually) into Polly.

### 3.1 First-time setup / welcome

**Where to look (VSCode/Void structure):**

- `src/vs/workbench/contrib/welcome*/` — welcome, get started, walkthrough
- `src/vs/workbench/parts/welcome/` — legacy welcome parts
- `extensions/` — look for `getStarted`, `welcome`, `onboarding` in extension names or package.json
- Search for:
  - `firstRun`, `first run`, `welcome`, `getStarted`, `onboarding`
  - `setupComplete`, `setup complete`, `hasCompletedOnboarding`
  - `workbench.contrib.welcome`

**What to capture:**

- How many “steps” or screens does the user see on first launch?
- Where is “setup complete” or “onboarding done” stored (storage key, file)?
- Is there a “skip” or “configure later” path?
- Any “dependency check” (e.g. check for Ollama) before finishing?

### 3.2 Model / provider integration

**Where to look:**

- `extensions/` — search for `ai`, `ollama`, `openai`, `anthropic`, `model`, `provider`, `llm`
- `src/vs/workbench/contrib/` — any `ai`, `chat`, `model`, `provider` contrib
- Search for:
  - `apiKey`, `api_key`, `API_KEY`, `secretStorage`
  - `modelProvider`, `model provider`, `ModelProvider`
  - `ollama`, `openai`, `anthropic`, `litellm`
  - `baseUrl`, `base_url`, `endpoint`

**What to capture:**

- Where are API keys stored (e.g. SecretStorage, keychain)?
- How does the user add a new provider (UI flow: Settings → …)?
- How is “current model” or “current provider” chosen and where is it shown (sidebar, input bar, status)?
- Is there a “test connection” or “verify key” action?
- How does Void support “custom” or “OpenAI-compatible” endpoints (base URL + key)?

### 3.3 Commands to run in the Void fork

```bash
cd ~/projects/polly-void   # or your Void clone

# First-time setup / welcome
rg -i "firstRun|welcome|getStarted|onboarding|setupComplete" --type-add 'src:*.ts' -t src -l
rg -i "firstRun|welcome|getStarted|onboarding" --type-add 'src:*.json' -t src -l

# Model / API keys
rg -i "apiKey|api_key|modelProvider|ollama|secretStorage" --type-add 'src:*.ts' -t src -l
rg -i "model.*provider|provider.*model" --type-add 'src:*.ts' -t src -l

# Extensions that might ship AI/model UI
ls extensions/
rg -i "ollama|openai|anthropic|llm|chat" extensions/ --glob 'package.json' -l
```

### 3.4 After the audit

- Update this spec with a short “Void findings” section: file paths, flow summary, and any screenshots or copy that we want to mirror.
- Optionally add a one-page “Void setup flow” and “Void model flow” to `openspec/changes/ux-pivot-cursor-patterns/` (e.g. `design-reference/void-setup-flow.md`) with bullet points or wireframes.

---

## 4. References

- [UX pivot proposal](../proposal.md) — Cursor-type patterns across Polly
- [UX pivot design](../design.md) — Chat, model/persona at input, context pills
- [void-migration/VOID_VS_MONACO_DECISION_FEB2026.md](../../../../void-migration/VOID_VS_MONACO_DECISION_FEB2026.md) — Void as design reference only; Monaco path for implementation
- Void: https://github.com/voideditor/void (and your fork at `~/projects/polly-void`)
