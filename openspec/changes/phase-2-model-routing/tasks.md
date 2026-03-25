# Phase 2: Model Routing — Auto-Routing

**Status:** 📋 Planned  
**Gate:** Phase 1 iOS Foundation complete (manual model selection shipped)  
**Spec source:** `MODEL_ROUTING_SPEC.md` §8 Phase 2  
**Depends on:** Phase 1 routing foundation (OverrideEvaluator, MMKV profiles, model picker)  
**@backend prerequisite:** Confirm 6 open questions in `MODEL_ROUTING_SPEC.md §9` before starting

## Goal

Polly routes messages automatically based on query complexity, context size, and voice mode. Users see routing decisions. Three preset profiles + per-agent overrides. No RAG yet — that's Phase 3.

## Tasks

### Gateway Clarification — @backend (prerequisite)
- [ ] [BLOCKED: @backend] Does `sessions.patch` accept a `model` field? → determines if Option B is viable
- [ ] [BLOCKED: @backend] Does `agents.update` apply to current message or only next? → race condition severity
- [ ] [BLOCKED: @backend] Does `chat` event include `model` field in response payload? → model attribution
- [ ] [BLOCKED: @backend] Can `models.list` return `contextWindow` per model?
- [ ] [BLOCKED: @backend] Is there a per-message usage event with token counts?
- [ ] [BLOCKED: @backend] Does `config.patch` accept arbitrary keys (`polly.routing.profiles`)?

### Routing Engine — Evaluators
- [ ] `ComplexityEvaluator`: heuristic only (message length, `?` count, code blocks, multi-part detection)
- [ ] `ConstraintEvaluator`: estimate input tokens, filter models whose context window can't handle them
- [ ] `VoiceEvaluator`: if voice input → cap at `voiceMode.maxTier`, prefer `voiceMode.preferredModel`
- [ ] `Resolver`: priority order (Override → Voice → Constraint → Complexity)
- [ ] `BudgetGuard`: Tier 3 soft/hard limit check after resolver
- [ ] `FallbackGuard`: try model → fail → next in tier → next lower tier → Tier 0 → error

### Routing Profiles UI
- [ ] Settings → Models → Routing: 3 preset policy cards (Token Saver / Balanced / Quality First)
- [ ] Per-agent overrides list with edit/delete
- [ ] Custom Routing Rule builder: 3 types only (Pin, Domain, Budget cap)
- [ ] Save rules to `RoutingProfile` in MMKV (Phase 2) or gateway config (if @backend confirms)

### Model Attribution — Tap to Explain
- [ ] Chat bubble footer tap → bottom sheet: "Why this model?" showing `RoutingReason` + context
- [ ] Routing decision stored in MMKV linked to message ID

### Routing Decision Log
- [ ] Extend MMKV ring buffer to include `complexityClassification` and `ConstraintEvaluator` output
- [ ] Usage view routing summary card: today's decisions by tier (Tier 0: X, Tier 1: Y, Tier 3: Z)

### If @backend confirms sessions.patch model scope (Option B)
- [ ] Migrate from agents.update (Option A) to sessions.patch (Option B) — remove race condition
- [ ] Update mutex/lock if staying on Option A

## Done when
Auto-routing working end-to-end. Complexity classifier routes simple queries to local models. Voice messages capped at Tier 1. Routing reason visible on tap. Budget guard active. @backend questions answered.
