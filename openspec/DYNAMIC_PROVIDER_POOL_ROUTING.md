# DYNAMIC_PROVIDER_POOL_ROUTING.md

Phase 2–3 — Dynamic Multi-Provider Pool Routing  
**Status:** Proposal  
**Owners:** @code_architect (routing engine), @backend (provider registration, health polling)  
**Last updated:** 2026-03-26  
**Cross-references:** `MODEL_ROUTING_SPEC.md`, `AGENT_BEHAVIOR_CONTRACT.md §3`, `KNOWLEDGE_SERVICE_CONTRACTS.md §2.1`

*Source artifact: https://claude.ai/public/artifacts/a5301f3c-b171-462a-903b-ddf71493f4b9*  
*All spec actions incorporated into openspec — see cross-reference map below.*

---

## What This Document Does

Extends the routing engine defined in `MODEL_ROUTING_SPEC.md` with a dynamic provider pool that:

- Connects to every available free and paid model provider simultaneously
- Tracks real-time rate limit headroom, latency, and availability per provider
- Rotates across providers serving equivalent models to maximize free usage
- Treats local models (Ollama) as always-available Tier 0 with latency-aware promotion
- Escalates to paid frontier models only with concrete evidence cheaper options are insufficient

**Design principle:** Budget isn't a ceiling you manage — it's a signal that the query exceeded the system's ability to solve it cheaply. Monthly cost target for typical usage: under $1.

---

## Design Principles

1. **Free-First, Local-Preferred, Frontier-Last** — every query starts at the cheapest tier and escalates only with evidence (retrieval confidence + complexity classification)
2. **Provider Diversity as Resilience** — pool treats provider diversity the way distributed systems use replica sets; cascade is deep before reaching paid APIs
3. **Agents Don't Know** — routing is transparent to the agent layer; agents never see which provider served them (per `AGENT_BEHAVIOR_CONTRACT.md §5.2`)
4. **Budget as Signal** — paid API calls are logged as information; patterns reveal which query types genuinely need frontier models vs. transient provider unavailability

---

## Provider Landscape (March 2026)

### Permanently Free Models (rate-limited only)
- **Kilo Gateway** — MiniMax M2.1/M2.5, GLM 4.7, Kimi K2.5, kilo-auto/free; 200 req/hr with account
- **OpenRouter** — ~29 free models: Qwen3 Coder 480B, DeepSeek R1, Llama 3.3 70B, MiniMax M2.5, Kimi K2; ~200 req/day
- **NVIDIA NIM** — GLM-4.7, MiniMax M2.1 + 1,000 free credits on signup
- **Routeway** — GLM-4.6, Kimi K2, DeepSeek, MiniMax; ~60 req/hr

### Frontier Free Tiers
- **Google Gemini** — 2.5 Pro (5 RPM, 100 RPD), 2.5 Flash (10 RPM, 250 RPD), Flash-Lite (15 RPM, 1,000 RPD); 1M context; prompts may train
- **Mistral** — All models incl. Large 3, Codestral; 1B tokens/month, 2 RPM; prompts may train
- **GitHub Copilot/Models** — GPT-4o, GPT-4.1, o3, Grok-3, DeepSeek-R1; 50–150 RPD

### Free Credits (depletable)
- **xAI Grok** — $25 signup + $150/month with data sharing; Grok 4, 4.1 Fast (2M context)
- **DeepSeek** — 5M tokens on signup (30 day expiry); V3.2, R1; servers in China, no training opt-out

### Local
- **Ollama** — llama3.2:3b, llama3.1:8b, codestral:latest, qwen2.5-coder:7b; no cost, no limits, no privacy exposure

### The Full Cascade (priority order)
```
Layer 0: Local (Ollama)           — unlimited, no network, no privacy exposure
Layer 1: Free-Unlimited Cloud     — ~3,200+ req/day across Kilo, OpenRouter, NIM, Routeway
Layer 2: Frontier Free Tiers      — Gemini 2.5 Pro/Flash, Mistral, GitHub Models
Layer 3: Free Credits             — xAI, DeepSeek signup credits
Layer 4: Included Subscriptions   — Copilot conversational (GPT-4o-mini — untouched)
Layer 5: Quasi-Free Paid (<$0.50/M) — DeepSeek V3.2 ($0.14/M), Grok 4.1 Fast ($0.20/M)
Layer 6: Frontier Paid            — Claude Sonnet/Opus, GPT-5 — only ABSENT + heavy complexity
```

Conservative daily free capacity: ~7,600+ requests. Typical 200 msg/day user: ~$0.01–0.05/day.

---

## Architecture

### New Component: PoolEvaluator
Inserts BEFORE the existing evaluator chain as the first evaluator. Assembles `PoolCandidate[]` from all registered providers based on real-time health state. Sort: `typePriority` → `cost` → `headroom` → `latencyEstimateMs`. Privacy filter: when `privacySensitive: true`, exclude `may-train` and `will-train` providers.

### Updated Evaluator Chain
```
[PoolEvaluator]         ← NEW Phase 2 — assembles PoolCandidate[]
[OverrideEvaluator]     ← existing
[VoiceEvaluator]        ← existing
[ConstraintEvaluator]   ← existing
[RAGEvaluator]          ← Phase 3 — adds privacySensitive flag + DIRECT/ADJACENT/ABSENT pool filter
[ComplexityEvaluator]   ← existing
[DomainEvaluator]       ← NEW Phase 3 — promotes domain-specialist models
[Resolver]
[BudgetGuard]
[FallbackGuard]         ← REWRITTEN — provider-first, then tier
```

### FallbackGuard Rewrite (provider-first)
1. Same model, different provider
2. Same tier, different model (meets constraints)
3. Next tier down
4. Tier 0 local, no constraints
5. Surface error to user

### Circuit Breaker
Open at 3 consecutive failures. Exponential backoff: 30s → 2m → 10m → 30m cap. Reset on first success after backoff.

### Rate Limit Rotation
Headroom-proportional: sort by `rateLimitRemaining / estimatedLimit` within each cost tier. Naturally spreads load. Conservation mode when headroom < 10%: provider used only for ABSENT queries or as last resort.

---

## User Override — Three-Layer Progressive Disclosure

**Layer 1:** Agent model dropdown — Polly Routing profiles (Free-First/Quality-First/Privacy-Only) OR pin to specific model. One dropdown, clear labels.

**Layer 2:** "Customize Routing for This Agent" — collapsed disclosure. Preferred tier, domain specialty, per-agent budget cap.

**Layer 3:** Settings → Models → Domain Routing — per-domain model preferences (local/free cloud/paid cloud, all default "auto").

Override resolution: pinned model → per-agent preferences → PoolEvaluator with global policy.

---

## Privacy Routing Rules

| Provider | Data Policy | Suitable For |
|---------|-------------|-------------|
| Ollama | local | Everything including sensitive |
| Anthropic Direct, GitHub, NIM | no-training | All queries |
| Gemini free, Mistral Experiment, OpenRouter free | may-train | Non-sensitive only |
| DeepSeek, xAI with data sharing | will-train | Non-sensitive, non-personal only |

When RAGEvaluator marks query `privacySensitive: true` (retrieved chunks contain personal data), pool auto-filters to `local` and `no-training` providers. No user action required.

Lockdown Mode: all cloud providers filtered regardless of preference. Local only. Security boundary, not configurable.

---

## Open Questions (11 items)

See `phase-2-provider-pool/tasks.md` §Open Questions for full list. Key ones:
- Q1: Does OpenClaw `models.list` return provider health, or must Polly track client-side?
- Q2: Can OpenClaw register multiple providers for the same model natively?
- Q9: Should domain taxonomy migrate from MMKV to gateway config (consistency with routing prefs)?

---

## Cross-Reference Map

| This document section | Incorporated into |
|----------------------|------------------|
| §3 Provider landscape + cascade | `phase-2-provider-pool/tasks.md` §Initial Provider Registry |
| §4 Data models (ProviderEntry, ProviderHealth, ModelProviderBinding, PoolCandidate) | `phase-2-provider-pool/tasks.md` §Data Models |
| §5 PoolEvaluator + updated evaluator chain | `phase-2-provider-pool/tasks.md` + `phase-2-model-routing/tasks.md` |
| §5.3 FallbackGuard rewrite | `phase-2-provider-pool/tasks.md` §FallbackGuard Rewrite |
| §6 RAG × pool integration | `phase-3-rag-routing/tasks.md` §RAGEvaluator × Provider Pool |
| §6.2 DomainEvaluator + domain routing profiles | `phase-3-rag-routing/tasks.md` §DomainEvaluator |
| §7 Rate limit rotation + conservation mode | `phase-2-provider-pool/tasks.md` §Phase 2B |
| §8 Health monitoring + circuit breaker | `phase-2-provider-pool/tasks.md` §Phase 2A |
| §9 Local model integration (Ollama) | `phase-2-provider-pool/tasks.md` §Phase 2A |
| §10 Settings UI + Add Provider flow | `phase-2-provider-pool/tasks.md` + `openspec/specs/ios-app/spec.md` |
| §11 Phase plan | `phase-2-provider-pool/tasks.md` phases 2A/2B + `phase-3-rag-routing/tasks.md` |
| §12 Interaction with existing specs | `phase-2-model-routing/tasks.md` + `phase-3-rag-routing/tasks.md` |
| §13 Open questions | `phase-2-provider-pool/tasks.md` §Open Questions |
| §14 User override, 3-layer disclosure | `phase-2-model-routing/tasks.md` §Per-Agent Routing Overrides |
