# Ambient Agent — Behavioral Spec

*Part of the agent-system domain. Cross-reference: `AMBIENT_AGENT_SPEC.md` (authoritative source), `AIGHT_POLLY_CARD.md` (iOS surface)*

---

## What Is the Ambient Agent?

The Ambient Agent is Polly's proactive observation mode. It runs as a background autonomous process (`autonomy_level: "autonomous"` in agent manifest), fires on cron/vault events, and surfaces observations to the iOS Today view as "Polly noticed…" cards. It does not participate in conversations. It does not respond to user messages.

**Core principle — Earned Interruption:** The agent speaks rarely, specifically, and only when genuinely earned. Signal-to-noise is non-negotiable. Test: *Would Brett be glad to have been interrupted by this?* If uncertain, don't surface it.

---

## Trigger Taxonomy

| Trigger | Name | Phase | Activation |
|---------|------|-------|-----------|
| T1 | Cross-Domain Connection | Phase 2 | Cross-domain semantic bridge ≥ 0.80 similarity. Blocked on Knowledge Skill. |
| T2 | Temporal Resurface | Phase 2 | Note maturity thresholds or semantic similarity ≥ 0.85. Blocked on Knowledge Skill. |
| T3 | Vault Health | **Phase 1** | Domain quiet ≥ 14 days; orphaned cluster ≥ 3 unlinked notes; concept absent from vault despite ≥ 3 cross-session appearances |
| T4 | Constitutional Flag | Phase 2 | Cui bono / scapegoat / defamiliarization pattern at high salience. Blocked on Knowledge Skill + session history adapter. |
| T5 | Continuation Probe | **Phase 1** | Related note in `organize`/`enrich` state, no update ≥ 7 days, new note on same topic being created |

**Phase 1 ships T3 + T5 only.** T1, T2, T4 are Phase 2 items dependent on Knowledge Skill expanded architecture.

---

## Dismissal State Machine

Each observation instance (card) has exactly one lifecycle. States are terminal where marked.

```
QUEUED → ACTIVE → ENGAGED → DISMISSED (terminal)
                ↘            ↗
              ACTIVE → DISMISSED (direct, no engage)
```

### States

| State | Description | Card Opacity | Entry Condition |
|-------|-------------|-------------|-----------------|
| QUEUED | Trigger fired; prior ACTIVE card exists; waiting | — | T3/T5 fires while ACTIVE card present |
| ACTIVE | Visible in Today view; no user interaction | 100% | Queue empty when trigger fires, or prior card dismissed |
| ENGAGED | User tapped → open or action button | 65% | User engagement action |
| DISMISSED | Terminal. Card gone. No re-queue. No re-surface. | — | User taps × from ACTIVE or ENGAGED |

### Transition Rules

1. **QUEUED → ACTIVE:** When prior ACTIVE card is dismissed, oldest queued card surfaces **immediately** — no waiting for next trigger cycle.
2. **ACTIVE → DISMISSED:** User taps × (no prior engagement). Log: `{ status: "dismissed", engaged: false }`.
3. **ACTIVE → ENGAGED:** User taps → open or any action button. Log: `{ status: "engaged", engaged: true }`.
4. **ENGAGED → DISMISSED:** User taps × after engaging. Log: `{ status: "dismissed", engaged: true }`.
5. **T3 auto-resolve → DISMISSED: PHASE 2 ONLY.** State machine architecturally supports this path (condition resolves → auto-dismiss). Not implemented Phase 1. All Phase 1 dismissals are user-initiated only.
6. **No reverse transitions.** DISMISSED is permanent.

### Constraints

- Max 1 ACTIVE card at a time. MUST be enforced.
- Queue is invisible — no UI indicator of depth (Q4 locked decision).
- DISMISSED state persists across app restarts (see Persistence below).

---

## Persistence — Dismissed Observation IDs

**Mechanism:** `AsyncStorage` key `aight.polly.dismissedIDs` (maps to UserDefaults on iOS).  
**Scope:** Client-side only. Backend does not receive or store dismissal events (Phase 1 by design).  
**Cross-device:** Out of scope Phase 1. Dismissed cards re-surface on new device / fresh install — acceptable.

**Eviction policy:**
- Cap: 500 entries maximum
- Eviction: oldest-first, only when cap is hit
- Age guidance: 90-day entries are candidates for eviction at cap
- Defensive reads: eviction logic MUST NOT throw or silently fail on corrupt/missing key

**Security:**
- Observation IDs MUST be opaque UUIDs — not human-readable, not derived from observation content
- Only the dismissed ID array is stored at this key — no observation content, no metadata

---

## Observation Format

Card body follows strict economy:

```
[One sentence — what was noticed, specific not vague]
[Optional: One sentence — why relevant now]
[One concrete next move, if applicable]
```

**Good:** "Your Signals/Grids bridge concept from January maps directly onto what you're building now — the constraint architecture handles this same pattern differently. Worth a look before continuing?"  
**Bad:** "I noticed you've been working across multiple domains lately. There might be some interesting connections!"

---

## Session Mode Behavior

| Context | T1 | T2 | T3 Vault Health | T4 Constitutional | T5 Continuation |
|---------|----|----|-----------------|-------------------|-----------------|
| Sigils (code/infra) | Ph2 | Ph2 | ❌ suppressed | ❌ suppressed | ✅ |
| Signals (audio) | Ph2 | Ph2 | ✅ | ❌ suppressed | ✅ |
| Scrolls / Grids / Glyphs | Ph2 | Ph2 | ✅ | Ph2 | ✅ |
| General/unclassified | Ph2 | Ph2 | ❌ suppressed | ❌ suppressed | ✅ |

T4 never fires during execution/code tasks. T3 vault health suppressed during Sigils and unclassified contexts.

---

## Notification Constraints (hard rules — no exceptions)

- No push notifications for Polly cards
- No app icon badge for Polly card presence  
- No sounds or haptic on card appearance
- Cards surface silently on Today view refresh only
- The Ambient Agent communicates through Today view, not the notification system

---

## Phase 2+ Roadmap

- **T1 Cross-Domain Connection** — requires Knowledge Skill graph layer
- **T2 Temporal Resurface** — requires Knowledge Skill conversation adapter + searchable session history
- **T4 Constitutional Flag** — requires Knowledge Skill + session history; evolves into full Epistemic Immune System (Phase 3)
- **T3 Auto-resolve** — backend detection of condition resolution + client push signal; deferred from Phase 1
- **Ambient Agent SOUL template** — stub only; full template pending (`phase-1-agent-system` tasks)
