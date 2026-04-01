# Phase 2: Dynamic Provider Pool Routing

**Status:** 📋 Planned  
**Gate:** Phase 1 complete (manual model selection working)  
**Ships alongside:** Phase 2 model routing (auto-routing evaluators)  
**Spec source:** `DYNAMIC_PROVIDER_POOL_ROUTING.md`  
**Depends on:** `phase-2-model-routing` (existing evaluator chain), `MODEL_ROUTING_SPEC.md`  
**Owners:** @code_architect (routing engine, PoolEvaluator), @backend (provider registration, health polling), @frontend (Settings UI)

## Goal

Extend the routing engine with a dynamic provider pool that tracks all available free and paid model providers in real-time. Rotate across providers to maximize free usage. Escalate to paid frontier models only when the system has concrete evidence cheaper options are insufficient. Monthly cost target: under $1 for typical usage.

**Design principle:** The pool is transparent to agents. Agents never see which provider served them. Routing is an iOS client/gateway concern only (per `AGENT_BEHAVIOR_CONTRACT.md §5.2`).

---

## Phase 2A: Provider Pool Foundation

*Gate: Phase 1 complete*

### Data Models (@backend + @code_architect)
- [ ] `ProviderEntry` schema: id, displayName, baseUrl, apiKeyEnv, type (`free-unlimited | free-tier | free-credit | local | included | paid`), dataPolicy (`local | no-training | may-train | will-train`), openaiCompatible, healthCheckEndpoint, supportsStreaming, headers, enabled
- [ ] `ProviderHealth` schema (runtime state, stored in MMKV `polly.routing.health.{providerId}`): available, rateLimitRemaining, rateLimitResetsAt, rateLimitWindow, latencyP50Ms/P95Ms, lastSuccessAt/FailureAt, consecutiveFailures, circuitBreakerOpen/ResetsAt, requestsToday, requestsThisHour
- [ ] `ModelProviderBinding` schema: modelId, providerId, providerModelId, tier, costPer1kInput/Output, contextWindow, strengths, maxComplexity, available
- [ ] `PoolCandidate` schema: modelId, providerId, providerModelId, tier, cost, headroom (0.0–1.0), latencyEstimateMs, strengths, maxComplexity, contextWindow, reason, dataPolicy
- [ ] Provider registry in gateway config `polly.routing.providers` via `config.patch` — persistent across devices
- [ ] Model-provider matrix: static capabilities in gateway config `polly.routing.models`, dynamic availability in MMKV

### PoolEvaluator (@code_architect)
- [ ] PoolEvaluator inserts BEFORE existing evaluator chain (first evaluator)
- [ ] Assembles ranked `PoolCandidate[]` from all registered providers based on real-time health
- [ ] Filters: skip disabled providers, unavailable providers, open circuit breakers, zero headroom
- [ ] Sort order: `typePriority` (local=0, free-unlimited=1, free-tier=2, free-credit=3, included=4, paid=5) → `cost` ascending → `headroom` descending → `latencyEstimateMs` ascending
- [ ] Privacy filter: if `privacySensitive: true` (from RAGEvaluator Phase 3), exclude `may-train` and `will-train` providers — personal vault content never routes to training-enabled providers
- [ ] Pool assembly is per-request (not cached Phase 2A); evaluate caching in Phase 4 (proposal: 30s cache, invalidate on health change)
- [ ] PoolEvaluator output replaces static model list fed to downstream evaluators

### FallbackGuard Rewrite (@code_architect)
- [ ] Replace tier-first fallback with provider-first fallback:
  1. Same model, different provider
  2. Same tier, different model (meets evaluator constraints)
  3. Next tier down
  4. Tier 0 (local), no constraints
  5. Surface error to user
- [ ] Every fallback step logged with original selection + fallback chain

### Circuit Breaker (@code_architect)
- [ ] Track `consecutiveFailures` per provider
- [ ] Open circuit at 3 consecutive failures; exponential backoff: 3→30s, 4→2m, 5→10m, 6+→30m cap
- [ ] Reset to closed on first success after backoff expires

### Passive Health Updates (@code_architect)
- [ ] Every API response updates `ProviderHealth` in MMKV
- [ ] Parse rate limit headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset` (standard across OpenAI-compatible APIs)
- [ ] Update rolling latency window (last 20 requests → P50, P95)

### Active Health Probes (@backend)
- [ ] Periodic probes: every 5 minutes for cloud providers, every 60 seconds for local
- [ ] Probe endpoint: `GET /models` for OpenAI-compatible; `GET /api/tags` for Ollama
- [ ] Timeout: 3000ms; failure → mark unavailable

### Ollama Integration (@code_architect)
- [ ] Auto-detect Ollama on app launch + every 60s: `GET http://localhost:11434/api/tags`
- [ ] Register detected models dynamically in model-provider matrix
- [ ] Ollama unavailability is not an error — pool continues with cloud providers
- [ ] Local models are always Tier 0, sort headroom: 1.0 (unlimited)

### Initial Provider Registry
Pre-register these providers (all OpenAI-compatible):

| Provider | Type | Key Storage | Free Models |
|---------|------|-------------|------------|
| Kilo Gateway | free-unlimited | Secure Store | MiniMax M2.1/M2.5, GLM 4.7, Kimi K2.5 |
| OpenRouter | free-unlimited | Secure Store | ~29 free models incl. DeepSeek R1, Qwen3 Coder 480B |
| NVIDIA NIM | free-unlimited | Secure Store | GLM-4.7, MiniMax M2.1 (+ 1k credits signup) |
| Routeway | free-unlimited | Secure Store | GLM-4.6, Kimi K2, DeepSeek, MiniMax |
| Google Gemini | free-tier | Secure Store | 2.5 Pro (100 RPD), 2.5 Flash (250 RPD), Flash-Lite (1k RPD) |
| Mistral | free-tier | Secure Store | All models incl. Large 3, Codestral (1B tokens/month) |
| GitHub Copilot | included | Existing auth | GPT-4o, GPT-4.1, o3, Grok-3, DeepSeek-R1 |
| xAI Grok | free-credit | Secure Store | Grok 4, 4.1 Fast ($25 signup + $150/month w/ data sharing) |
| DeepSeek | free-credit | Secure Store | V3.2, R1 (5M tokens on signup) |
| Ollama | local | None | Any installed models |
| Anthropic Direct | paid | Secure Store | Claude Sonnet/Opus 4.6 |

**Privacy classifications:**
- `local` (Ollama): never leaves device — all queries including sensitive
- `no-training` (Anthropic Direct, GitHub Copilot, NVIDIA NIM, Routeway): suitable for all queries
- `may-train` (Gemini free tier, Mistral Experiment, OpenRouter free): non-sensitive only; personal vault content auto-excluded
- `will-train` (DeepSeek, xAI with data sharing): non-sensitive, non-personal only; auto-excluded from vault queries

### Settings UI — Providers Screen (@frontend)
- [ ] Settings → Models → Providers screen showing all connected providers grouped by type
- [ ] Per-provider: name, type, live headroom/remaining requests, available models count
- [ ] Privacy warning badge (⚠️) on `may-train` and `will-train` providers
- [ ] Enable/disable toggle per provider
- [ ] Pool status card: free models available count, local models count, estimated daily free capacity, used today (all free), paid today ($0.00)
- [ ] Routing policy selector: Free-First (default) / Quality-First / Local-Only / Privacy-Only (local + no-training only)

### Add Provider Flow (@frontend)
- [ ] [+ Add Provider] → grouped picker: Free Unlimited / Free Frontier Tier / Free Signup Credits / Local / Paid / Custom OpenAI-Compatible
- [ ] Each provider card shows: what you get free, the catch (training policy, rate limits, credit expiry)
- [ ] Instructions per provider (Gemini: Google account + aistudio.google.com/apikey; Mistral: phone verification required; Ollama: ollama.ai + Detect button)
- [ ] API key input → stored in Secure Store
- [ ] Privacy warning shown for `may-train` / `will-train` providers at add time
- [ ] On save: health probe → model discovery → register in model-provider matrix
- [ ] OpenClaw native Kilo Gateway support via `openclaw onboard --kilocode-api-key` — gateway-side registration streamlined

---

## Phase 2B: Free-First Routing + Rotation

*Gate: Phase 2A complete + Phase 2 ComplexityEvaluator working*

### Headroom-Proportional Rotation (@code_architect)
- [ ] Within same cost tier, sort by headroom descending → naturally spreads load across providers without explicit round-robin
- [ ] Conservation mode: when provider headroom < 10%, mark as `conserve`; only use for ABSENT-tier queries or when all non-conserved providers exhausted

### Routing Profiles Extended (@code_architect)
- [ ] Free-First profile: local → free-unlimited → free-tier → free-credit → included → quasi-free paid → frontier paid
- [ ] Quality-First profile: frontier free tiers preferred, paid escalation lower threshold
- [ ] Local-Only profile: Ollama only; cloud providers filtered out (convenience mode — distinct from Lockdown which is security-motivated)
- [ ] Privacy-Only profile: local + no-training providers only; `may-train` and `will-train` filtered

### Pool Status Dashboard (@frontend)
- [ ] Estimated daily free capacity calculation from provider health data
- [ ] "Used today" breakdown: local / free-unlimited / free-tier / paid
- [ ] Daily paid cost display ($0.00 baseline)

---

## Phase 2: Provider-Level Open Questions (require resolution before implementation)

| # | Question | Owner | Proposal |
|---|----------|-------|---------|
| 1 | Does OpenClaw's `models.list` already return provider health / rate limit info, or must Polly track this client-side? | @backend | Client-side tracking assumed in this spec |
| 2 | Can OpenClaw register multiple providers for the same model natively, or does Polly manage the model-provider matrix separately? | @backend | Polly manages matrix assumed |
| 3 | What happens on fresh install with no providers configured? | @code_architect | Onboarding gate: require at least one provider; show "Add a free provider" prompt with Kilo Gateway as default (zero-cost, one-click) |
| 4 | How to handle free tier changes (e.g., Gemini reduced quotas)? | @code_architect | Circuit breaker handles outages; add weekly capacity reclassification pass: adjust estimated limits based on actual 429 rates over 7 days |
| 5 | Gemini client: Google AI SDK vs. generic OpenAI-compatible wrapper? | @backend | Recommend `@google/generative-ai` SDK directly, wrapped behind `ProviderEntry` interface |
| 6 | Mistral at 2 RPM — treat as interactive provider or background-only? | @code_architect | Background-only (session summarization, entity extraction). Not for interactive chat. |
| 7 | DeepSeek: auto-exclude from privacy-sensitive queries or require user opt-out? | @design_eng | Auto-exclude (`will-train` + servers in China). User can override in Settings. |
| 8 | Pre-register all known free providers on first launch (unconfigured, to motivate sign-up)? | @design_eng | Open — motivational but verify with Brett before implementing |
| 9 | Should domain taxonomy migrate from MMKV to gateway config? | @code_architect | Propose yes (Phase 2): `polly.domains` in gateway config, MMKV as read cache |

---

## Lockdown Mode Interaction (hard rule)

In Lockdown Mode, all cloud providers (including free) are filtered by PoolEvaluator. Only `type: 'local'` providers available. This is a security boundary (`can't`), not a preference (`don't`). PoolEvaluator respects lockdown flag — not configurable. See `LOCKDOWN_MODE.md`.

## Done When
Phase 2A: PoolEvaluator assembling candidates, circuit breaker live, passive health tracking, Settings → Providers UI, Add Provider flow for Kilo + OpenRouter + Ollama. Phase 2B: headroom-proportional rotation, conservation mode, Free-First routing profile active, pool status card. Open questions resolved.
