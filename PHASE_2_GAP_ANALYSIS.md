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
| `gesture-ward-agent-builder` | P1 | Coordinated cluster — see §6 below |

### Critical Path

**Phase 1 → push-security → knowledge-skill → Phase 3**

Knowledge Skill is the only Phase 2 change that blocks Phase 3. Start it on day 1 of Phase 2. Everything else is parallel.

---

## 6. Gesture + Ward + Agent Builder — New Phase 2 @backend Requirements

Added 2026-03-30. Three new specs (`GESTURE_LAYER.md`, `WARD.md`, `AGENT_BUILDER.md`) introduce the following Phase 2 @backend requirements not previously captured. Flagged for @backend awareness.

| # | Requirement | Source | Priority | Notes |
|---|-------------|--------|----------|-------|
| 1 | **Gesture library data store at gateway** | `GESTURE_LAYER.md` §3.1, §4 | P1 | Embedding storage + cosine similarity query path. Schema design required before implementation — bring proposal to @code_architect. See `GESTURE_LAYER.md` §12 Q2 for embedding model decision. |
| 2 | **Gesture recognizer (embedding similarity, pre-routing pass)** | `GESTURE_LAYER.md` §4 | P1 | Runs on every utterance ≤ 8 words before agent routing. Latency-sensitive — must not meaningfully impact response latency. |
| 3 | **Gesture invocation log** | `GESTURE_LAYER.md` §14, `PHASE_1` | **Phase 1 — start now** | Must start in Phase 1. Log short utterances (≤ 8 words) with no gesture match to `gesture_candidate_log`. Required before gesture layer exists so training data accumulates. See Phase 1 pre-work note. |
| 4 | **Ward context assembly pipeline** | `WARD.md` §6 | P1 | Active thread topic summary generation (lightweight 5-message pass, cached), recency filter (7-day threads, 14-day teams), context block assembly. Performance target: < 50ms added to Ward invocation latency. Design proposal required before implementation. |
| 5 | **Topic summary generation per thread** | `WARD.md` §6.2 | P1 | Lightweight summary cache per thread. Invalidate on 3+ new messages. Cache hit path must be very fast (cache read + format). |
| 6 | **`ward_mode` flag handling on Liaison invocations** | `WARD.md` §10, `AGENT_BUILDER.md` §3 | P1 | Gateway must detect Liaison invocation context (solo vs. group) and route to correct mode. `solo_context_injection: ward_context_v1` triggers Ward context assembly. |
| 7 | **Agent Builder system agent registration** | `AGENT_BUILDER.md` §5.1 | P1 | Custom agents must be validated at registration time: `autonomy_level` must be `reactive`, `config_write` must not be in `allowed_modes`, `ward_mode` must be `false`. These constraints are **architectural** — enforced at registration, not in the Builder SOUL. |

### Phase 1 Pre-Work — Gesture Candidate Log

This is the **only gesture-related hook needed in Phase 1**. All other gesture layer work is Phase 2.

```
if message.text word_count ≤ 8 and no gesture match:
    log {timestamp, text, session_id, domain_context, active_agent}
    to gesture_candidate_log
```

When complete, flag in `PROJECT_STATUS.md`.
