# iOS App — Current State

*What is built and running as of Phase 1. Verified against actual polly-ios/ source.*

## Stack

- React Native 0.83.2 + Expo ~55.0.8 (TypeScript)
- Expo Router ^55.0.7
- `src/theme/colors.ts` — design token source of truth

## Critical: Missing Dependencies

The following Phase 1-required packages are **not yet in `package.json`** and must be installed before implementation can begin:

| Package | Purpose |
|---------|---------|
| `expo-secure-store` | Gateway credential storage |
| `react-native-mmkv` | Fast local state persistence |
| `zustand` | State management |
| `@shopify/flash-list` | High-performance message list |
| `react-native-markdown-display` | Markdown rendering in chat |
| `lucide-react-native` | Icon system (design constitution) |
| `expo-keep-awake` | Screen-on during voice recording |
| `expo-av` or `expo-audio` | Real audio recording |
| `expo-document-picker` | Vault security-scoped bookmarks |

No gateway client library (`expo-openclaw-chat` or equivalent) installed.

## Actual Feature State

| Feature | Status | Notes |
|---------|--------|-------|
| Design system | ✅ Shipped | `src/theme/colors.ts` — tokens, typography, spacing (249 lines) |
| Voice mic button | ✅ Scaffolded | `VoiceMicButton.tsx` (337 lines), `VoiceDraftPrompt.tsx` (137 lines) |
| Voice recording hook | ⚠️ Scaffold only | `useVoiceRecording.ts` (279 lines) — simulated data, no real audio |
| Chat input bar | ✅ Scaffolded | Input field + voice button wired to state machine in `chat.tsx` (216 lines) |
| Expo Router file structure | ✅ Scaffolded | All routes exist as 6–33 line stubs |
| Gateway WebSocket auth | ❌ Not started | No gateway client anywhere; `isConfigured = false` hardcoded |
| Onboarding flow | ❌ Not started | Title + subtitle text only (33 lines) |
| Team drawer + agent list | ❌ Not started | TODO comment in `_layout.tsx`; no DrawerPanel component |
| Chat streaming + markdown | ❌ Not started | "Messages will render here" placeholder |
| Group chats | ❌ Not started | No code exists |
| Vault quick capture | ❌ Not started | No `expo-document-picker` |
| Mental models | ❌ Not started | No data, no UI, no store |
| Settings | ❌ Not started | Stub placeholders (6 lines each) |
| Today screen | ❌ Not started | Stub placeholder |

## Known Issues (open)

- `VoiceMicButton.tsx` line 269: uses 🎤 emoji — must be replaced with Lucide `Mic` icon (§18.3)
- `useVoiceRecording.ts`: simulated audio — voice test suite cannot run until fixed
- `VOICE_INTERACTION.md` REQ-VOICE-01: references Swift `UIApplication.shared.isIdleTimerDisabled` — must use `expo-keep-awake`
- `polly-ios/src/colors.ts`: duplicate of `src/theme/colors.ts` — delete

## Voice Architecture (Phase 1)

- STT/TTS: client-side only. Gateway never handles audio.
- Gateway receives text only; responds with text only.
- Never call a TTS tool from the gateway — playback issues.

## Design Constitution (non-negotiable, §18.3)

- Icons: Lucide only (`lucide-react-native`) — not yet installed
- Colors: `src/theme/colors.ts` tokens only
- Typography: system font stack only

---

## Polly Card — "Polly noticed…"

*Full source: `AIGHT_POLLY_CARD.md`. Behavioral spec: `openspec/specs/agent-system/ambient-agent.md`. Change set: `phase-1-polly-ambient-card`.*

### Card Anatomy

```
┌─────────────────────────────────────────────┐
│  🔮  Polly noticed…              [dismiss ×] │
│                                              │
│  [Observation — 1-2 sentences, specific]     │
│                                              │
│  [Action button — optional]   [→ open]       │
└─────────────────────────────────────────────┘
```

Header always "Polly noticed…" — no variation. 🔮 fixed. Dismiss × top-right.

### Today View Placement

```
TODAY
──────────────────────────────
⏰  Reminders
──────────────────────────────
✅  Tasks
──────────────────────────────
🔮  Polly noticed…   ← this section
──────────────────────────────
⚡  Background processes
──────────────────────────────
```

Section hidden entirely when no card present — no empty state, no placeholder.

### Locked Design Decisions

| # | Decision | Locked Value |
|---|----------|-------------|
| Q1 | Background tint | Token `polly-card-bg-tint` — deferred to dark mode palette lock. No hardcoded color. |
| Q2 | Engaged-state opacity | **65%** — calibrated to default body font + standard line height. Must re-validate if font spec changes. |
| Q3 | Vault note open behavior | **Bottom sheet only.** Inline expand explicitly rejected (scroll collision). |
| Q4 | Queue visibility | **None.** No badge, counter, or "1 more" indicator under any condition. |

### Visual Behavior

- Background: `polly-card-bg-tint` token (3–5% desaturated primary surface) — bind token, do not hardcode
- Cards appear silently on Today view refresh — no animation entry that demands attention
- ENGAGED state (user tapped → open): 65% opacity, animated
- DISMISSED: card removed from Today view immediately

### Dismissal Behavior

- **Permanent dismiss:** × tap removes card. Not re-queued. Not archived. Terminal.
- **Engage then dismiss:** Card goes to 65% ENGAGED state on → open; explicit × still required to dismiss.
- **Session persistence:** Undismissed cards survive app restart. They do not expire on time schedule.
- **T3 exception (Phase 2 only):** Vault health cards auto-dismiss when condition resolves. Not Phase 1.

### First-Run Inline Explanation

One-time only. Inline below first-ever card body — not a modal, not a tutorial:

> *Polly surfaces connections and observations when they're genuinely useful. Cards appear rarely and on purpose.*

Auto-removes when that first card is dismissed. Never shown again.

### Notification Constraints (hard rules)

- No push notifications — ever
- No app icon badge
- No sounds or haptics on card appearance

### Implementation Requirements

- `[BLOCKED: phase-1-today-crud]` — Today view scaffold required first
- Observation IDs MUST be opaque UUIDs (security requirement)
- `aight.polly.dismissedIDs` AsyncStorage key: dismissed ID array only, eviction policy enforced on launch (cap 500, oldest-first, 90-day guidance)
- Defensive reads on the dismissed store — must not throw on corrupt/missing key
