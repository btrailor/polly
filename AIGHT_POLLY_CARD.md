# Aight "Polly Noticed…" Card Pattern
*iOS surface spec. Owner: @frontend + @design_eng. Part of the Polly framework. Created: 2026-03-25.*
*Cross-reference: AMBIENT_AGENT_SPEC.md (behavioral triggers), POLLY.md (round-machine philosophy)*

---

## Overview

The "Polly noticed…" card is the iOS surface for Ambient Agent observations. It lives in the **Today view** as a distinct card type — separate from reminders, tasks, and process items. It is non-blocking, non-urgent, and dismissible. It respects attention.

This is the round-machine design philosophy expressed as UI: the card invites play, disappears when dismissed without consequence, and rewards the user who pauses to engage with it.

---

## Card Anatomy

```
┌─────────────────────────────────────────────┐
│  🔮  Polly noticed…              [dismiss ×] │
│                                              │
│  [Observation — 1-2 sentences, specific]     │
│                                              │
│  [Action button — optional]   [→ open]       │
└─────────────────────────────────────────────┘
```

### Elements

| Element | Notes |
|---------|-------|
| **Header icon** | 🔮 fixed — distinguishes Polly cards from task/reminder items |
| **Header text** | Always "Polly noticed…" — no variation. Consistent signal. |
| **Dismiss button** | Top-right ×. Tap to dismiss permanently (not "remind me later"). No guilt, no re-surfacing. |
| **Observation body** | 1-2 sentences max. Specific, earned. See message format rules in AMBIENT_AGENT_SPEC.md. |
| **Action button** | Optional. Present only when a concrete next move exists. See action types below. |
| **Open arrow** | "→ open" links to full context: vault note, conversation, or agent. Tapping expands without leaving Today view. |

---

## Card Visual Design

**Background:** Slightly differentiated from standard task cards — subtle tint or border treatment to signal "this is observational, not actionable." Suggested: muted purple/indigo tint matching the 🔮 icon, opacity ~8-10% on the card background. Not distracting. Just different.

**Typography:** Same as standard cards. No special treatment. The content earns attention, not the formatting.

**Animation:** Cards appear without push notification or badge. They surface silently on Today view refresh — no modal, no alert, no buzz. Present when you look, not demanding before you look.

**Stacking:** Max 1 Polly card visible at a time. If a new observation arrives while a previous one is still undismissed, the new one queues and surfaces after dismissal. Cards do not stack visually or badge the count. One observation at a time — same economy principle as the message format.

---

## Action Button Types

| Trigger | Action Label | Behavior |
|---------|-------------|----------|
| T1 Cross-Domain | "Open in vault" | Opens linked Obsidian note or knowledge search |
| T2 Temporal Resurface | "Open note" | Opens the resurfaced vault note |
| T3 Vault Health (orphaned) | "Capture with Scribe" | Opens Scribe chat with context pre-populated: orphaned notes named, domain suggested |
| T3 Vault Health (domain quiet) | "Capture with Scribe" | Opens Scribe with domain context |
| T4 Constitutional Flag | *(no action button)* | Observation only. No prescribed next move — user decides how to engage with it |
| T5 Continuation Probe | "Open note" | Opens the in-progress vault note with its current state |

**Action button is optional.** If no clean action exists (especially T4), the card surfaces the observation only. No forced CTA.

---

## Placement in Today View

The Today view currently organizes items by type and time. Polly cards sit in their own section:

```
TODAY
──────────────────────────────
⏰  Reminders (time-ordered)
──────────────────────────────
✅  Tasks (active)
──────────────────────────────
🔮  Polly noticed…            ← This section
──────────────────────────────
⚡  Background processes
──────────────────────────────
```

**Section header:** "Polly noticed…" — same as the card header. No count badge. Just the section label.

**If empty:** Section is hidden entirely. The absence of a Polly card is not a failure state — it means nothing was earned. Don't show "Polly hasn't noticed anything" placeholder. Absence = silence = fine.

---

## Dismissal Behavior

**Dismiss (×):** Card is removed from Today view permanently. Not re-queued. Not archived. The observation was surfaced once; Brett saw it; that's complete.

**Engage (→ open / action button):** Card remains visible but in a "seen" state (slightly reduced opacity or soft checkmark indicator) until manually dismissed. Engaging doesn't auto-dismiss — the observation may still be relevant while Brett explores it.

**Session end:** Undismissed cards persist until explicitly dismissed. They do not expire on a time schedule. (The content is specific enough that it's either relevant or not — time doesn't decay it.)

**One exception:** Vault health cards (T3) that are resolved — e.g., the orphaned notes were captured, or the quiet domain got a new note — should auto-dismiss without user action. The condition they were observing no longer exists.

---

## Notification Behavior

**No push notifications for Polly cards.** This is a hard rule.

The Ambient Agent communicates through the Today view, not through the notification system. Push notifications are for time-sensitive, user-initiated requests. Polly observations are neither. The user finds Polly cards when they look at their Today view — not before.

**No badges.** The app icon does not badge for Polly card presence.

**No sounds.** No haptic feedback on card appearance.

The card is ambient, not intrusive. It's there when you look.

---

## Empty State and First-Run

**Before first Polly card:** No placeholder, no "Polly is watching" messaging. The section simply doesn't exist. The first card appears when it's earned.

**Onboarding note (one-time, dismissible):** When the first Polly card ever appears, show a brief inline explanation below the card body:
> *Polly surfaces connections and observations when they're genuinely useful. Cards appear rarely and on purpose.*

This appears once, inline in the first card only. Not a modal, not a tutorial. Just a line. Auto-removes after the card is dismissed.

---

## Relationship to Agent Chat

Tapping the card's "→ open" or action button does not navigate away from Today view for simple vault note opens. It should use an **inline expand** or **sheet presentation** — the card grows to show the note content, or a bottom sheet presents the note, keeping Today view visible underneath.

For "Capture with Scribe" actions: navigate to the Scribe agent chat with context passed as a system prompt pre-fill. This is the one case where navigation away from Today view is correct — Scribe needs a full chat context.

For constitutional flag observations (T4, no action button): tapping the card body opens the relevant conversation in the agent chat where the pattern was detected. Brett can explore it with Polly directly.

---

## Phase 1 Scope

In Phase 1, the card UI ships fully — all visual design, dismissal behavior, placement, animation. The content rendered comes only from Phase 1 Ambient Agent triggers (T3 vault health, T5 continuation probe).

The card is forward-compatible with Phase 2/3 triggers. No UI changes needed when T1, T2, T4 come online — they populate the same card format with different observation text and action types.

**Phase 1 deliverables:**
- Card component (Today view)
- Section header (hidden when empty)
- Dismissal + "seen" state logic
- "Capture with Scribe" deep link
- "Open note" Obsidian deep link
- First-run inline explanation text

---

## Design Notes for @design_eng

A few open questions to resolve together:

1. **Tint color:** 🔮 purple/indigo is the natural read, but check contrast against both light/dark Today view backgrounds. If it reads too "mystical" or clashes with Brett's established palette, neutral with just the emoji as the distinguishing signal is fine.

2. **Seen vs. unseen state:** The reduced opacity treatment for "engaged but not dismissed" needs a defined opacity delta. Suggest: 100% → 65%, but test with actual card content — the body text needs to stay readable.

3. **Sheet vs. inline expand:** For vault note opens, bottom sheet is cleaner than inline expand given the Today view scroll context. Confirm with Brett's preference — he may want to stay in Today view or prefer the full note context.

4. **Stacking queue visualization:** When a card is queued but not yet surfaced, there's no UI for it — it doesn't exist from the user's perspective. Confirm this is the right call vs. a subtle "1 more observation" indicator at the bottom of the card.

---

## Design Decisions (Locked) — 2026-04-01

Four open questions from "Design Notes for @design_eng" above were resolved in group design review. These are locked decisions; do not reopen without a new design review pass.

**Q1 — Tint color: Neutral (deferred to Aight dark mode palette)**
The 🔮 emoji is the primary visual differentiator; the card tint is subtlety, not signal. Decision: use a 3–5% desaturated version of the app's primary surface color once the Aight dark mode palette is finalized. Until then, tint is deferred — do NOT hardcode a purple/indigo value. @frontend: treat this as a palette-locked token (`polly-card-bg-tint`) and bind it when the dark mode palette ships. If palette is still fluid at implementation time, check with @design_eng before picking a value.

**Q2 — Seen-state opacity: 65%**
Cards in the "engaged but not dismissed" state render at 65% opacity. Constraint: this value is calibrated to the **default body font + standard line height**. If the observation text font size or line height changes in a future design pass, this number must be re-validated — 65% may not maintain sufficient legibility at smaller sizes or tighter leading. Flag for QA and design review if font spec changes. (@qa_guy: add a legibility check for the seen-state to the iOS component validation plan.)

**Q3 — Vault note opens: Bottom sheet (not inline expand)**
Tapping "→ open" or an action button that opens a vault note presents a bottom sheet. Inline expand inside a scroll container is explicitly rejected — scroll collision is a known UX regression. Bottom sheet keeps Today view visible underneath and avoids scroll context conflicts. Dismissal from the sheet does not affect card state. "Capture with Scribe" remains the one exception: it navigates away to the Scribe chat (full context needed).

**Q4 — Queue visibility: None (invisible queue)**
When a second Polly card is queued behind an undismissed card, there is no UI indicator of the queue. No "1 more observation" badge, no counter, no hint. Consistent with the "ambient, not intrusive" principle. The queue is an implementation detail, not a user-visible concept. Users see one card when conditions trigger; they do not need to know a queue exists.

---

*Document lives at `~/.openclaw/workspace/AIGHT_POLLY_CARD.md`*
*Behavioral triggers: `~/.openclaw/workspace/AMBIENT_AGENT_SPEC.md`*
