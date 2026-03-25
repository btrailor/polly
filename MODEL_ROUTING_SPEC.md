# MODEL_ROUTING_SPEC.md

Phase 1–4 — Progressive Model Routing  
Status: Draft — replaces §21 narrative with implementable spec  
Owners: @code_architect (routing engine), @backend (gateway integration), @frontend (iOS surface)  
Last updated: 2026-03-25  
Cross-references: `POLLY_IOS_SPEC.md` §21, `KNOWLEDGE_SKILL.md`, `KNOWLEDGE_SERVICE_CONTRACTS.md`, `POLLY_AGENT_TEMPLATES.md`

---

## 1. Why This Document Exists

§21 of `POLLY_IOS_SPEC.md` describes model routing philosophy, a 4-tier hierarchy, and a decision algorithm. It's the right vision. But §21 can't be built as written:

- The routing algorithm is monolithic — one decision tree mixing voice, context size, complexity, RAG confidence, budget, and user override in a single pass
- §21 doesn't explain how routing interacts with OpenClaw's model assignment API (no per-message model field in `chat.send`)
- User-configurable routing (per-agent model pinning) isn't designed — no data model, no UI, no persistence
- RAG-integrated routing depends on the Knowledge Skill (Phase 2) — Phase 1 routing must work without it

This document decomposes the vision into four buildable phases with clear data models and insertion points.

---

## 2. How OpenClaw Handles Models

### 2.1 The Model Assignment Chain

OpenClaw determines which model handles a message through this chain:

1. Per-agent model (`agents.update → model` field) — "This agent always uses Claude Sonnet"
2. Gateway default model (`config → models.default`) — fallback if agent has no model set
3. Provider fallback chain (`config → models.providers[].fallback`) — if primary unavailable

**There is no per-message model field in `chat.send`.** `ChatSendParams` has `sessionKey`, `message`, `idempotencyKey`, `thinking` — but no model override. The model is determined by the agent's configuration at message processing time.

### 2.2 Routing Insertion Points

| Option | Mechanism | Phase | Status |
|--------|-----------|-------|--------|
| **A. Dynamic `agents.update` before send** | Change agent model before each `chat.send` | Phase 1 | Recommended for Phase 1 — race condition noted but acceptable (Polly is only client) |
| **B. `sessions.patch` with model scope** | Session-scoped override if gateway supports `{ model }` in patch params | Phase 2 | @backend must confirm sessions.patch accepts model field |
| **C. Routing skill intercepts** | Skill runs before agent, rewrites model config as routing middleware | Phase 3+ | Cleanest architecture; requires skill runner (Phase 2) |

---

## 3. Data Model

### 3.1 Routing Profile

```typescript
interface RoutingProfile {
  id: string;           // "default", "conservative", "quality", or user-created
  name: string;         // "Balanced", "Token Saver", "Always Opus", etc.
  description?: string;
  rules: RoutingRules;
  scope: 'global' | 'agent';
  agentId?: string;     // if scope = 'agent', which agent
}

interface RoutingRules {
  pinnedModel?: string;           // overrides all routing logic if set
  preferredTier: 'local-first' | 'balanced' | 'quality-first';
  escalation: {
    contextSizeThreshold: number;         // tokens
    complexityThreshold: 'light' | 'medium' | 'heavy';
    ragConfidenceThreshold: number;       // 0.0–1.0
  };
  budget: {
    tier3DailySoftLimit: number;          // tokens — warn
    tier3DailyHardLimit: number;          // tokens — stop routing to Tier 3
    tier1DailyLimit?: number;
  };
  voiceMode: {
    maxTier: 0 | 1;
    preferredModel?: string;
  };
  domainModels?: {
    [domain: string]: string;             // e.g., { "code": "codestral:latest" }
  };
}
```

### 3.2 Model Registry

```typescript
interface ModelEntry {
  id: string;             // "claude-opus-4-6", "llama3.1:8b"
  provider: string;       // "anthropic", "ollama", "groq"
  displayName: string;
  tier: 0 | 1 | 2 | 3;
  contextWindow: number;  // tokens
  strengths: string[];    // ["general", "code", "analysis", "long-form", "fast"]
  maxComplexity: 'light' | 'medium' | 'heavy';
  costPer1kInput?: number;
  costPer1kOutput?: number;
  available: boolean;
  lastChecked: number;
  userNotes?: string;
}
```

### 3.3 Routing Decision Record

```typescript
interface RoutingDecision {
  timestamp: number;
  sessionKey: string;
  agentId: string;
  selectedModel: string;
  selectedTier: number;
  reason: RoutingReason;
  context: {
    inputTokenEstimate: number;
    complexityClassification: 'light' | 'medium' | 'heavy';
    ragConfidence?: number;
    ragDomain?: string;
    retrievalTier?: 'DIRECT' | 'ADJACENT' | 'ABSENT';
    voiceMode: boolean;
    userOverride: boolean;
    profileUsed: string;
  };
  actualTokensUsed?: number;
  responseTimeMs?: number;
  userSatisfactionSignal?: 'regenerated' | 'continued' | 'switched_model';
}

type RoutingReason =
  | 'pinned_model'
  | 'voice_mode_latency'
  | 'context_too_large'
  | 'rag_high_confidence'
  | 'rag_moderate_confidence'
  | 'no_rag_match'
  | 'complexity_light'
  | 'complexity_heavy'
  | 'domain_specialist'
  | 'budget_exhausted'
  | 'user_override'
  | 'fallback'
  | 'default';
```

### 3.4 Storage Locations

| Data | Phase 1 | Phase 2+ |
|------|---------|---------|
| Routing profiles | MMKV `polly.routing.profiles` | Gateway config via `config.patch polly.routing.profiles` |
| Model registry | `models.list` response + user annotations in MMKV | Same |
| Routing decisions | MMKV `polly.routing.history` (ring buffer, last 100) | SQLite `~/.polly/routing_decisions.db` |
| Per-agent model override | `agents.update({ agentId, model })` | Same |
| Budget tracking | MMKV | Gateway config `polly.routing.budget.{tier}.used` |

---

## 4. Routing Engine — Decomposed

Five independent evaluators, each returning a recommendation. A resolver picks the winner.

```
Incoming message
 │
 ├──→ [OverrideEvaluator]    → "user pinned claude-opus-4-6" (hard override)
 ├──→ [ConstraintEvaluator]  → "context is 12k tokens, local models can't handle it"
 ├──→ [VoiceEvaluator]       → "voice mode active, max Tier 1"
 ├──→ [RAGEvaluator]         → "0.91 confidence in code domain → local code model" (Phase 2+)
 ├──→ [ComplexityEvaluator]  → "medium complexity, reasoning required"
 │
 ▼
[Resolver] → highest-priority applicable recommendation → selected model
 │
 ▼
[BudgetGuard] → "Tier 3 budget exhausted, downgrade to Tier 1"
 │
 ▼
[FallbackGuard] → "selected model unavailable, use fallback chain"
 │
 ▼
Selected model → agents.update → chat.send
```

### Resolver Priority Order
1. OverrideEvaluator (hard override — done)
2. VoiceEvaluator (caps tier, continues)
3. ConstraintEvaluator (filters candidate list)
4. RAGEvaluator (if returns result → prefer it)
5. ComplexityEvaluator (fallback)

Within tier: prefer domain-specialist → matching strength → lowest cost → first available.

### BudgetGuard
```
if selectedModel.tier == 3:
  if daily_tier3_used >= hard_limit:
    downgrade to best Tier 2 (or Tier 1 if none)
    log reason: 'budget_exhausted'
  elif daily_tier3_used >= soft_limit:
    proceed but emit usage.warning event to iOS
```

### FallbackGuard
```
try selected model
  → fail? try next model in same tier
  → fail? try next lower tier
  → fail? try Tier 0
  → fail? surface error: "No models available"
```

Every fallback logged with original selection and fallback chain.

---

## 5. User-Facing: "Always Use Opus" Flow

### Agent Creation / Model Pin

Agent creation flow, under Model section:
- Model picker (all configured models)
- "Always use this model" toggle (off by default)
- Toggle on → creates `RoutingProfile` with `pinnedModel` set for this agent

### Model Attribution in Chat

- Nav bar: model pill showing current model (e.g., "Opus 4.6")
- Message footer: "via claude-opus-4-6" — tap to see routing reason
- Pinned: shows "[pinned]" indicator

### Budget vs. Pin Precedence

Budget wins. A pin is a preference; budget is a spending control. If Tier 3 hard limit is hit, even pinned agents are downgraded with message: "Budget limit reached for today. You can adjust your limit in Settings → Models → Budget."

---

## 6. Settings → Models → Routing Screen

```
┌─────────────────────────────────────┐
│  ROUTING POLICY                     │
│  ┌─────────────────────────────┐    │
│  │ ○ Token Saver               │    │
│  │ ● Balanced (recommended)    │    │
│  │ ○ Quality First             │    │
│  └─────────────────────────────┘    │
│                                     │
│  DAILY BUDGET                       │
│  Premium API (Tier 3)               │
│  ████████░░  8,240 / 50,000 tokens  │
│  Warn at [10,000 ▾]                 │
│  Hard limit [50,000 ▾]              │
│                                     │
│  CONFIGURED MODELS              Edit│
│  Tier 0 — Local                     │
│    llama3.1:8b  general             │
│    codestral:latest  code           │
│  Tier 1 — Free Cloud                │
│    groq:llama-3.3-70b  fast         │
│  Tier 3 — Paid API                  │
│    claude-opus-4-6  premium         │
│    claude-sonnet-4-5  balanced      │
│                                     │
│  PER-AGENT OVERRIDES                │
│  🧠 Deep Thinker                    │
│     Pinned: Claude Opus 4.6         │
│  🖥 Code Architect                  │
│     Domain: code → Codestral        │
│  All other agents                   │
│     Using: Balanced routing         │
│                                     │
│  [+ Add Custom Routing Rule]        │
└─────────────────────────────────────┘
```

Custom Routing Rule types (3 only — intentionally limited):
- **Pin to model** — always use a specific model
- **Domain routing** — route by detected topic (code → Codestral, writing → Claude)
- **Budget cap** — per-agent token limit

---

## 7. RAG → Routing Integration (Phase 2+)

When Knowledge Skill is available, `RAGEvaluator` calls `knowledge_search` on every message:

```
knowledge_search returns:
  DIRECT (≥0.75) → Tier 0, augment with top 2–3 chunks
  ADJACENT (0.45–0.75) → Tier 1, augment with top chunk + "related" note
  ABSENT (<0.45) → no augmentation, Tier 2/3

Augmentation target:
  Tier 0 model → summary only (300 words, fits local context window)
  Tier 1+ model → summary + full source
```

RAG results injected at Layer 2 (domain context) in the 7-layer injection hierarchy. See `KNOWLEDGE_SERVICE_CONTRACTS.md §3`.

---

## 8. Phase-by-Phase Build Plan

### Phase 1: Manual Model Selection
- `models.list` → populate model picker
- Per-agent model assignment via `agents.update`
- Model picker in: agent creation, agent detail, chat nav bar
- "Always use this model" toggle → `pinnedModel` in routing profile
- Model attribution in chat bubbles
- MMKV storage for routing profiles
- **No automatic routing** — user chooses

### Phase 2: Basic Auto-Routing
- `ComplexityEvaluator` (heuristic — message length, keywords, code blocks; no LLM call)
- `ConstraintEvaluator` (context size guard)
- `VoiceEvaluator` (cap tier for voice input)
- Routing profile UI in Settings → Models (3 presets + per-agent override)
- Routing decision logging (MMKV, last 100)
- Model attribution shows routing reason on tap
- Investigate `sessions.patch` model scope (Option B) — @backend confirm

### Phase 3: RAG-Integrated Routing
- `RAGEvaluator` (calls `knowledge_search`, reads confidence + domain)
- Domain routing (code → Codestral, etc.)
- Dense summary decision based on model context window
- Budget tracking (SQLite, daily reset, soft/hard limits)
- Usage view routing summary card
- Custom routing rules UI

### Phase 4: Full System
- LLM-based complexity classification (replaces heuristic)
- Feedback loop (regeneration rate calibrates classifier)
- Routing decision history (searchable)
- Model capability auto-detection from provider API

---

## 9. Open Questions for @backend

| Question | Impact |
|----------|--------|
| Does `sessions.patch` accept a `model` field? | Determines Phase 2 routing insertion point (Option B) |
| Does `agents.update` apply immediately or only to new messages? | Race condition severity for Option A |
| Does `chat` event payload include the model that was actually used? | Required for model attribution in chat bubbles |
| Can `models.list` return context window size per model? | Auto-populates model registry without manual entry |
| Is there a usage event per-message with token counts? | Required for budget tracking |
| Can `config.patch` write to arbitrary keys (`polly.routing.profiles`)? | Determines Phase 2+ routing config storage |

---

## 10. Open Design Questions

**Q1: Budget override pin?** → Budget wins. Preference doesn't override spending control.

**Q2: LLM complexity classification in Phase 2?** → No. Heuristic in Phase 2 (no 200ms latency penalty per message). LLM classification in Phase 3 when RAG makes the decision consequential.

**Q3: Routing in group chats?** → Each agent has its own routing profile. Routing runs independently per-agent on group message dispatch.

**Q4: All models unavailable?** → Surface error in chat: "No models available right now." Never silently fail.

**Q5: Abort mid-stream and re-route?** → No. Too complex, confusing UX. Let response complete; user regenerates (logs negative signal for routing).
