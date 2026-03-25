# Phase 2: Model Routing — Auto-Routing

**Status:** 📋 Planned  
**Gate:** Phase 1 iOS Foundation complete (manual model selection shipped)  
**Spec source:** `MODEL_ROUTING_SPEC.md` §8 Phase 2  
**Depends on:** Phase 1 routing foundation (OverrideEvaluator, gateway-stored profiles, model picker)  

## @backend Status (updated 2026-03-25)

**Confirmed:**
- ✅ `agents.update` — new messages only, not in-flight. Phase 1 Option A race condition low-risk with single client.
- ✅ Chat response event includes model used at dispatch. @backend confirming exact field name.
- ✅ Completion event has token counts. @backend confirming field names + iOS exposure.
- ✅ `config.patch` supports arbitrary keys — `polly.routing.profiles` works.

**Gateway changes required before this change ships (@backend owns):**
- [ ] Add `model` field to `sessions.patch` params — eliminates Phase 1 race condition for Phase 2+
- [ ] Extend `models.list` response: add `contextWindow: number` + `strengths: string[]` per model
- [ ] Confirm completion event field names; ensure token counts exposed to iOS (not server-only)

**Phase 1 storage correction (@backend decision 2026-03-25):**
Routing profiles go to gateway config from Phase 1 — `config.patch polly.routing.profiles`. Not MMKV. MMKV is device-local; re-install wipes profiles. See `MODEL_ROUTING_SPEC.md §3.4`.

## Goal

Polly routes messages automatically based on query complexity, context size, and voice mode. Users see routing decisions. Three preset profiles + per-agent overrides. No RAG yet — that's Phase 3.

## Tasks

### Routing Engine — Evaluators
- [ ] `ComplexityEvaluator`: heuristic only (message length, `?` count, code blocks, multi-part detection) — no LLM call in Phase 2
- [ ] `ConstraintEvaluator`: estimate input tokens, filter models whose context window can't handle them (requires `models.list` context window — @backend gateway change above)
- [ ] `VoiceEvaluator`: if voice input → cap at `voiceMode.maxTier`, prefer `voiceMode.preferredModel`
- [ ] `Resolver`: priority order (Override → Voice → Constraint → Complexity)
- [ ] `BudgetGuard`: Tier 3 soft/hard limit check after resolver
- [ ] `FallbackGuard`: try model → fail → next in tier → next lower tier → Tier 0 → error

### Storage Migration (from Phase 1)
- [ ] Migrate routing profile reads from MMKV → `config.get polly.routing.profiles`
- [ ] Migrate routing profile writes to `config.patch polly.routing.profiles`
- [ ] Migrate to `sessions.patch` model scope (Option B) once @backend ships it — remove Option A race condition

### Routing Profiles UI
- [ ] Settings → Models → Routing: 3 preset policy cards (Token Saver / Balanced / Quality First)
- [ ] Per-agent overrides list with edit/delete
- [ ] Custom Routing Rule builder: 3 types only (Pin, Domain, Budget cap)

### Model Attribution — Tap to Explain
- [ ] Chat bubble footer tap → bottom sheet: "Why this model?" showing `RoutingReason` + context
- [ ] Routing decision stored in MMKV linked to message ID

### Routing Decision Log
- [ ] Extend MMKV ring buffer to include `complexityClassification` and evaluator outputs
- [ ] Usage view routing summary card: today's decisions by tier

## Done when
Auto-routing working end-to-end. Complexity classifier routes simple queries to local models. Voice messages capped at Tier 1. Routing reason visible on tap. Budget guard active. @backend gateway changes shipped.
