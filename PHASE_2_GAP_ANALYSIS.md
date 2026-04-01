# PHASE_2_GAP_ANALYSIS.md

Comprehensive Audit: Phase 2 Spec Coverage, Boundary Conflicts, Missing Changes  
Status: Resolved — decisions locked 2026-03-25  
Source: Artifact 97635384  
Cross-references: `POLLY_IOS_SPEC.md` §13, §3.14, §4.2–4.6, §8.2, §11.1, §15; all Phase 2 task files; `KNOWLEDGE_SKILL.md`; `MODEL_ROUTING_SPEC.md`; `SWARM_COORDINATION_SPEC.md`; `SENSIBILITY_SYSTEM_SPEC.md`; `AGENT_BEHAVIOR_CONTRACT.md`; `KNOWLEDGE_WRITE_PATH.md`; `CREATIVE_CONSTRAINT_ENGINE.md`

---

## 1. The Problem

Phase 2 was defined in three places that disagreed:
- **`POLLY_IOS_SPEC.md §13`**: User-facing feature list (voice, Today CRUD, push, ElevenLabs, integrations, vault browser, mDNS, group chats)
- **`openspec/ROADMAP.md`**: Infrastructure build list (9 changes: Knowledge Skill, Skills Marketplace, Push Security, etc.)
- **Implementation specs**: Deep system design (FAISS, routing evaluators, swarm task tracking, behavior injection)

This audit maps every Phase 2 feature from all sources, documents what was missing, records the decisions made, and the state after resolution.

---

## 2. Phase Boundary Conflicts — Resolutions

### 2.1 Conversation History Adapter

| Source | Says |
|--------|------|
| `phase-2-knowledge-skill/tasks.md` | Full build: memory file watcher + `knowledge_conversation_history` tool |
| `KNOWLEDGE_SKILL.md` phase list | "Phase 2 foundation — full feature Phase 3" |
| `KNOWLEDGE_SERVICE_CONTRACTS.md §6` | "Conversation corpus: Phase 3 dependency" |

**Resolution (locked 2026-03-25):** Split.
- **Phase 2:** Memory file watcher + basic indexing into shared FAISS index. Foundation only.
- **Phase 3:** `knowledge_conversation_history` tool with date/agent/section filters.
- Task file updated accordingly.

### 2.2 Structural Rules (Creative Constraint Engine)

| Source | Says |
|--------|------|
| `phase-2-sensibility-behavior/tasks.md` | Structural mode picker, in-chat structural pill, structural rules injection |
| `CREATIVE_CONSTRAINT_ENGINE.md` | "Phase 3 — Structural Engagement Layer" |
| `SENSIBILITY_SYSTEM_SPEC.md §7` | Phase 3 for structural rules |

**Resolution (locked 2026-03-25):** Remove structural rules from Phase 2 sensibility-behavior.
- Phase 2 = aesthetic behavior injection only (register, vocabulary, compression, artifact aesthetics)
- Structural rules (structural mode picker, structural pill) move to `phase-3-creative-systems`
- Task file updated accordingly.

### 2.3 Vault Write Paths

| Source | Says |
|--------|------|
| `§13 Phase 3` | "Obsidian write-back (opt-in) — agents create/append notes" |
| `KNOWLEDGE_WRITE_PATH.md §9` | Phase 2: promotion + save-conversation; Phase 3: agent write-back |
| `phase-2-knowledge-skill/tasks.md` | Includes promotion pipeline + save conversation |

**Resolution (locked 2026-03-25):** Current task split is correct. Clarifying note added:
> Phase 2 vault writes are **user-initiated only** (quick capture promotion, conversation save).  
> Agent write-back (`vault_write` tool) is **Phase 3 only**.

### 2.4 Today View CRUD

| Source | Says |
|--------|------|
| `§13 Phase 1` | TodayView (display) |
| `§13 Phase 2` | TodayView (triggers, tasks, processes) + Item CRUD |
| `phase-1-ios-foundation/tasks.md` | Includes `aight_item` creation path |

**Resolution (locked 2026-03-25):** Move `aight_item` creation to Phase 2.
- Phase 1 Today View: **display only** — render items from gateway, no creation
- Phase 2 (`phase-2-today-crud`): triggers, tasks, processes, CRUD
- Phase 1 task file updated.

---

## 3. Missing Changes — Created

Eight new change directories created:

| # | Change | Priority | Depends On |
|---|--------|----------|-----------|
| 1 | `phase-2-push-notifications` | P1 | push-security |
| 2 | `phase-2-voice-upgrade` | P1 | Phase 1 voice working |
| 3 | `phase-2-vault-browser` | P1 | Phase 1 vault bookmark |
| 4 | `phase-2-integrations` | P1 | Phase 1 settings |
| 5 | `phase-2-gateway-discovery` | P2 | Phase 1 LAN WebSocket |
| 6 | `phase-2-today-crud` | P1 | Phase 1 Today display |
| 7 | `phase-2-image-attachments` | P1 | Phase 1 chat |
| 8 | `phase-2-message-search` | P2 | Phase 1 message cache |

Plus:

| # | Change | Priority | Note |
|---|--------|----------|------|
| 9 | `phase-2-gateway-changes` | P0 | Consolidates 14 @backend tasks from 6 files |
| 10 | `phase-2-ipad-layout` | P2 | Split-view sidebar |

---

## 4. @backend Gateway Tasks — Consolidated

14 gateway tasks previously scattered across 6 files. All now in `phase-2-gateway-changes/tasks.md`.

| # | Task | Blocks | Source File |
|---|------|--------|------------|
| 1 | Auth-gate `aight.push.register` | push-notifications | push-security |
| 2 | Encrypt sendKey in devices.json | push-notifications | push-security |
| 3 | `polly.security.protectionLevel` startup key | lockdown-mode | push-security |
| 4 | Scrub API keys from config change logs | all config.patch callers | push-security |
| 5 | `targetAgentIds` on agent RPC | structured conversations | swarm-coordination |
| 6 | Per-agent-per-group `activationMode` | group chat UX | swarm-coordination |
| 7 | `sessions.patch` model field | routing race condition | model-routing |
| 8 | `models.list` extension (contextWindow + strengths) | complexity evaluator | model-routing |
| 9 | Confirm token count field names | usage tracking | model-routing |
| 10 | `vault.write_complete` event | incremental indexing | knowledge-skill |
| 11 | `skills.install` RPC | skill installation | skills-marketplace |
| 12 | Per-device config scoping | multi-client themes | sensibility-behavior |
| 13 | Network enforcement (IP-range, APNs block) | lockdown constraints | lockdown-mode |
| 14 | Gateway encryption at rest | lockdown data protection | lockdown-mode |

---

## 5. Build Order Update

### Wave 1 — Immediately after Phase 1

| Change | Priority | Why First |
|--------|----------|-----------|
| `push-security` | P0 | Pre-production gate — blocks all production use |
| `knowledge-skill` | P0 | Blocks Phase 3 — longest effort in Phase 2 |
| `message-search` | P2 | Parallel, self-contained, high user value |
| `gateway-discovery` | P2 | Parallel, self-contained |

### Wave 2 — After push-security ships

| Change | Priority | Depends On |
|--------|----------|-----------|
| `push-notifications` | P1 | push-security |
| `integrations` | P1 | Phase 1 settings |
| `today-crud` | P1 | Phase 1 Today display |
| `image-attachments` | P1 | Phase 1 chat |
| `voice-upgrade` | P1 | Phase 1 voice |

### Wave 3 — After knowledge-skill ships or in parallel

| Change | Priority | Depends On |
|--------|----------|-----------|
| `model-routing` | P1 | Phase 1 routing + @backend changes |
| `swarm-coordination` | P1 | Phase 1 groups + @backend changes |
| `sensibility-behavior` | P1 | Phase 1 ThemeContext |
| `skills-marketplace` | P1 | @security_audit |
| `vault-browser` | P1 | Phase 1 bookmark + knowledge-skill |

### Wave 4

| Change | Priority | Notes |
|--------|----------|-------|
| `lockdown-mode` | P1 | Complex — heavy @backend |
| `cognitive-artifact` | P2 | |
| `ipad-layout` | P2 | |
| `shortcuts` | P2 | Native Swift module |
| `figma-integration` | P3 | Low priority |

### Critical Path

**Phase 1 → push-security → knowledge-skill → Phase 3**

Knowledge Skill is the only Phase 2 change that blocks Phase 3. Start it on day 1 of Phase 2. Everything else is parallel.

---

## 6. Conversational Onboarding (`conversational-onboarding`)

**Source:** `IOS_SPEC_AUDIT.md §1.3` — decision 2026-04-01  
**Priority:** P2 (high value, not a blocker)  
**Depends on:** Phase 1A complete (manual form onboarding working)

### What It Is
Replace the Phase 1A manual form onboarding with a conversational experience powered by a Gemini Flash API key baked into the app bundle. The user's first interaction with Polly is a chat — `PollyOnboardingAgent` explains the app, walks them through OpenClaw installation, and guides them to their first gateway connection.

### Why Phase 2 (Not Phase 1)
Phase 1A priority is getting a TestFlight build in hand fast. The manual form is fully functional and zero-dependency. Conversational onboarding requires provisioning a Google AI Studio project, baking a key, and writing a persona — meaningful pre-flight overhead that shouldn't block the first build.

### Implementation Requirements
- **Pre-build provisioning (one-time — @code_architect):**
  - Provision dedicated Google AI Studio project for Polly onboarding bootstrap
  - Configure hard rate limits (requests/day + tokens/day) — key economically useless for abuse
  - Generate API key scoped to this project only
  - Add to `.env.local` template as `POLLY_BOOTSTRAP_GEMINI_KEY`
  - Set `expiresAtMs` build-time constant: 12 months from build date
- **Implementation (@frontend):**
  - Bootstrap key loaded from build-time env constant (not runtime fetch)
  - `expiresAtMs` check: `Date.now() < expiresAtMs` → conversational; else → fall back to Phase 1A manual form
  - `PollyOnboardingAgent` SOUL baked in: knows OpenClaw install steps, common errors, Mac-specific quirks
  - Gemini Flash API called directly from client (gateway doesn't exist yet during onboarding)
  - Bootstrap conversations NOT persisted — cleared on onboarding complete
  - Agent steps aside cleanly on gateway connect: "All done — switching to your full setup now"
  - `PollyOnboardingAgent` NOT visible post-onboarding — no agent list entry, no access post-setup
  - EAS OTA rotation path documented in release runbook (new key + updated `expiresAtMs` every ~12 months)
- **Security:**
  - IPA extraction risk accepted and documented in `POLLY_IOS_SPEC.md §20.4` — no further mitigation required
  - Free-tier key = low abuse ceiling; rate limits = additional ceiling

### "Done When"
User opens Polly fresh, is greeted by `PollyOnboardingAgent` in a chat interface, completes setup conversationally, and lands in the main chat with their first agent ready. Manual form fallback works when key is expired or offline.
