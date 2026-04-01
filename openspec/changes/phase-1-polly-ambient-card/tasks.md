# Phase 1: Polly Ambient Card

**Status:** 🔒 Spec complete — awaiting implementation gate  
**Gate:** Phase 1 iOS Foundation (Today view scaffold must exist before card component can land)  
**Spec sources:** `AIGHT_POLLY_CARD.md`, `AMBIENT_AGENT_SPEC.md`  
**Full behavioral spec:** `openspec/specs/agent-system/ambient-agent.md`  
**Full iOS surface spec:** `openspec/specs/ios-app/spec.md §Polly Card`  
**Reviews completed:** @design_eng ✅, @backend ✅, @infra ✅, @security_audit ✅ (pending ID opacity confirmation)

---

## Locked Design Decisions (do not reopen without new design review)

| # | Decision | Value |
|---|----------|-------|
| Q1 | Card background tint | Token: `polly-card-bg-tint` — deferred to Aight dark mode palette lock. No hardcoded color. |
| Q2 | Seen/engaged state opacity | 65% — calibrated to default body font + standard line height. Re-validate if font spec changes. |
| Q3 | Vault note open behavior | Bottom sheet only. Inline expand explicitly rejected (scroll collision). |
| Q4 | Queue visibility | None. Queue is invisible to user. No counter, no badge, no "1 more" indicator. |

## Locked Scope Decisions (Phase 1)

| Decision | Phase 1 | Deferred |
|----------|---------|----------|
| T3 auto-resolve | ❌ Not implemented | Phase 2 — state machine supports it architecturally, trigger mechanism TBD |
| Dismissal sync | Client-side only (`aight.polly.dismissedIDs` / UserDefaults) | Cross-device sync out of scope |
| Triggers in scope | T3 (vault health) + T5 (continuation probe) only | T1, T2, T4 blocked on Knowledge Skill (Phase 2) |

---

## Tasks

### iOS — Polly Card Component (`@frontend`)
- [ ] `PollyCard` component — card anatomy per spec (🔮 header, observation body, optional action button, dismiss ×, → open)
- [ ] `polly-card-bg-tint` token binding — no hardcoded tint. Block on palette lock if dark mode palette not yet shipped. Check with @design_eng before picking placeholder.
- [ ] 65% opacity ENGAGED state — animated transition from ACTIVE. Calibrated to `fontSize:17/lineHeight:22`. Add QA legibility check.
- [ ] Permanent dismiss handler — removes card from Today view, writes ID to dismissed store. No re-queue.
- [ ] Bottom sheet for vault note opens (`→ open`, `"Open note"` actions). Scribe navigation remains the one full-navigation exception.
- [ ] First-run inline explanation — one-time, inline below card body, auto-removes on first dismiss. Not a modal.
- [ ] Today view section header: "Polly noticed…" — hidden entirely when no card present (no empty state placeholder)
- [ ] `[BLOCKED: phase-1-today-crud]` — Today view scaffold must exist before card component lands

### iOS — Observation Store (`@frontend`)
- [ ] `aight.polly.dismissedIDs` in AsyncStorage (maps to UserDefaults on iOS)
- [ ] Eviction policy on app launch: cap at 500 entries; evict oldest-first only when cap is hit; 90-day age guidance
- [ ] Defensive read — eviction logic must not throw or silently fail on corrupted/missing key
- [ ] Observation IDs MUST be opaque UUIDs — not human-readable, not derived from observation content (security requirement, @security_audit)
- [ ] Scope tight — nothing persisted to `aight.polly.dismissedIDs` beyond the dismissed ID array

### iOS — State Machine (`@frontend`)
- [ ] Implement `QUEUED → ACTIVE → ENGAGED → DISMISSED` transitions client-side
- [ ] DISMISSED is terminal — no re-queue, no re-surface after dismiss
- [ ] On DISMISSED: immediately surface next QUEUED card without waiting for next trigger cycle
- [ ] Max 1 ACTIVE card at a time
- [ ] ENGAGED state: 65% opacity, persists until explicit × dismiss
- [ ] T3 auto-resolve path: NOT implemented in Phase 1. State machine must not include this path.

### Backend / Ambient Agent (`@backend`)
- [ ] T3 trigger: vault health — domain quiet (≥ 14 days, any domain)
- [ ] T3 trigger: orphaned notes (≥ 3 unlinked, no recent access)
- [ ] T5 trigger: continuation probe (related note in organize/enrich, new note on same topic being created)
- [ ] Observation ID generation: opaque UUIDs only — no human-readable IDs
- [ ] Queue management: on observation fire, if card already ACTIVE → enqueue. Queue surfacing: immediate on prior card dismissed.
- [ ] Phase 2 placeholder: T3 auto-resolve detection + client signal (do not implement Phase 1)

### QA (`@qa_guy`)
- [ ] Legibility check: ENGAGED state (65% opacity) at `fontSize:17/lineHeight:22` — pass/fail baseline
- [ ] Re-validate opacity if font spec changes (must be explicitly retested)
- [ ] Rapid dismiss sequence: user burns through queued backlog — verify no jank in DISMISSED → ACTIVE transition
- [ ] FIFO ordering: multiple queued cards surface in `createdAt` order on sequential dismissals
- [ ] Dedup on enqueue: same `observationId` delivered twice → queue contains it once only
- [ ] Dismissed card does not re-surface after: (a) explicit dismiss, (b) app restart, (c) reinstall (expect re-surface on reinstall — acceptable per spec)
- [ ] Max 1 active card enforced — no stacking
- [ ] Queue invisible — no UI indicator of depth under any condition
- [ ] Dismissed ID store: eviction fires correctly at 500 cap; defensive read on corrupt key

### Security (`@security_audit`)
- [ ] Confirm observation IDs are opaque UUIDs before implementation ships (if IDs are human-readable, escalate)
- [ ] Verify `aight.polly.dismissedIDs` key contains only the dismissed ID array — no observation content stored

---

## Queue Behavior (locked)

On dismissal (× tap), the next queued card surfaces **immediately** — no waiting for the next Polly trigger cycle. The trigger is what causes Polly to evaluate and enqueue; once queued, dismissal of the current card is sufficient to dequeue and show the next.

```
DISMISSED event fires
  → client checks queue
  → queue non-empty: surface next card immediately (FIFO by createdAt)
  → queue empty: card layer goes dormant until next trigger evaluation
```

**Queue ordering:** Client-side, FIFO by `createdAt`. Backend delivers observations; it does not manage queue ordering or expiration post-delivery. Once delivered, the client owns surfacing order.

**Dedup on enqueue (required):** If the backend delivers the same `observationId` twice (network retry, etc.), the client MUST deduplicate before enqueue — queue contains each observation ID at most once. Check `observationId` against both the active card, the pending queue, and the dismissed IDs store before enqueuing.

**Expired observations (Phase 1: no TTL):** Phase 1 observations have no TTL — all queued items surface eventually. If a TTL field is added in a future phase, the client must skip expired items on dequeue rather than surfacing a stale card. @frontend: write the dequeue path to handle a TTL check (even if it's a no-op in Phase 1) so it's not a retrofit.

---

## Notification Constraints (hard rules)

- No push notifications for Polly cards — ever
- No app icon badge for Polly card presence
- No sounds or haptic feedback on card appearance
- Cards surface silently on Today view refresh only
