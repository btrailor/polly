# ONBOARDING_SPEC.md

Phase 1 — Full Journey: Download to First Useful Conversation  
Status: Draft  
Owners: @code_architect (flow), @frontend (UI), @backend (gateway verification), @security_audit (auth flows)  
Last updated: 2026-03-25  
Cross-references: `POLLY_IOS_SPEC.md` §20.4, §3.3, §3.14, §4.1, §12; `POLLY_AGENT_TEMPLATES.md`; `phase-1-ios-foundation/tasks.md`

---

## 1. What This Document Covers

The existing onboarding spec (§20.4) focuses on the in-app conversational flow — the bootstrap AI guiding gateway connection. This document covers the full journey from "I want to use Polly" to "I just had my first useful conversation," including everything the spec currently assumes without saying.

Three distinct onboarding contexts:

| Context | Who | Starting Point | End State |
|---------|-----|---------------|-----------|
| A. Developer bootstrap | Brett (building Polly) | Cloned repo, no deps installed | App running on device, connected to local gateway |
| B. User first run | End user installs Polly | App downloaded from TestFlight | Connected to gateway, team selected, first message sent |
| C. User device migration | Existing user, new device | App installed on new iPhone | Reconnected to existing gateway, sessions restored |

---

## 2. Context A: Developer Bootstrap

This is the journey from cloned repo to working app. **`setup.sh` at the repo root covers this.** See `setup.sh` for the automated script.

### 2.1 Prerequisites

| Prerequisite | Why | Verification |
|-------------|-----|-------------|
| macOS (Sonoma or later) | Gateway runs on macOS. Xcode requires macOS. | `sw_vers` |
| Node.js 18+ | Expo, gateway, expo-openclaw-chat all require Node. | `node --version` |
| Xcode 15+ | iOS simulator and device builds. | `xcode-select -p` |
| Expo CLI | `npx expo` must work. | `npx expo --version` |
| OpenClaw gateway installed | The server Polly connects to. | `openclaw --version` |
| OpenClaw gateway running | Must be actively serving on a port. | `curl http://localhost:18789/health` |
| At least one LLM provider configured | Gateway needs a model to run agents. | OpenClaw Settings → Models |
| CocoaPods | Required for Expo native modules. | `pod --version` |

### 2.2 Complete Phase 1 package.json

The current `polly-ios/package.json` is missing ~15 critical dependencies. The complete Phase 1 set:

```json
{
  "dependencies": {
    "expo": "~55.0.8",
    "react": "19.2.0",
    "react-native": "0.83.2",
    "expo-router": "^55.0.7",
    "react-native-gesture-handler": "^2.30.0",
    "react-native-reanimated": "^4.2.3",
    "react-native-safe-area-context": "^5.7.0",
    "react-native-screens": "^4.24.0",
    "@react-navigation/native": "^7.2.0",
    "@react-navigation/native-stack": "^7.14.7",

    "expo-openclaw-chat": "0.2.3",

    "zustand": "^4.5.0",
    "react-native-mmkv": "^2.12.0",

    "expo-secure-store": "~14.0.0",
    "@noble/ed25519": "^2.0.0",
    "@noble/hashes": "^1.3.0",

    "@shopify/flash-list": "^1.6.0",
    "react-native-markdown-display": "^7.0.0",
    "lucide-react-native": "^0.400.0",
    "react-native-svg": "^15.0.0",
    "zeego": "^1.0.0",

    "expo-speech-recognition": "~1.0.0",
    "expo-speech": "~12.0.0",
    "expo-keep-awake": "~14.0.0",

    "expo-sqlite": "~15.0.0",
    "expo-haptics": "~14.0.0",
    "expo-local-authentication": "~15.0.0",
    "expo-notifications": "~0.29.0",
    "expo-document-picker": "~12.0.0",
    "expo-clipboard": "~7.0.0",
    "expo-status-bar": "~55.0.4",
    "uuid": "^9.0.0"
  }
}
```

---

## 3. Context B: User First Run

### 3.1 The Full Journey

Steps 5–10 are covered by §20.4. Steps 1–4 and 11 were previously unspecced.

```
1. User hears about Polly
2. User goes to TestFlight link, installs Polly
3. User opens Polly for the first time
   ↓
4. [SILENT] Device identity initialization (Ed25519 keygen, §20.4 Phase A)
   + create local message cache (expo-sqlite)
   + initialize MMKV storage
   + set default preferences
   + pre-populate mental model definitions
   ↓
5. Welcome screen — "Hi, I'm Polly" + API key or free model choice
   ↓
6. Conversational onboarding — OpenClaw install guidance (§20.4 Phase B)
   ↓
7. Gateway URL entry + connection test
   ↓
8. Auth token entry + TOFU cert pinning
   ↓
9. [GATEWAY CONNECTED] → Post-connection verification (§3.4 below)
   ↓
10. Team selection → agent provisioning → enter main app
    ↓
11. FIRST CONVERSATION — cold start (§3.6 below)
```

### 3.2 Pre-Install Requirements (TestFlight / App Store description)

The user needs an OpenClaw gateway running before Polly is useful. This must be stated clearly:

> **Requirements:** A Mac running OpenClaw (free at openclaw.app) and at least one AI provider (Anthropic, OpenAI, Ollama, etc.) configured. Polly connects to your OpenClaw gateway — it doesn't work without one.

### 3.3 Step 4: Silent Initialization

Ed25519 keygen is specced in §20.4 Phase A. Additionally:

- Create local message cache database (`expo-sqlite`)
- Initialize MMKV storage buckets
- Set default preferences: `theme: "reas"`, `routing: "balanced"`, `language: system`
- Pre-populate mental model definitions in MMKV (12 built-in models — no network required)

### 3.4 Step 9: Post-Connection Verification

After gateway connection succeeds, before team selection — verify the gateway is actually usable:

```
[GATEWAY CONNECTED]
  ↓
1. models.list → at least one model configured?
   → No models: "Your gateway doesn't have any AI models configured yet.
                 Open OpenClaw on your Mac and add at least one provider
                 (Anthropic, OpenAI, or Ollama). I'll wait."
                 [Retry] button — do NOT proceed until at least one model exists.

2. health → gateway healthy?
   → Degraded: "Your gateway is running but reporting issues: [details].
                You can continue, but some features may not work."
                [Continue Anyway] [Check Again]

3. config.get → store gateway version + capabilities + model list in MMKV
               (Used for adaptive UI — e.g., hide model routing if only one model)
```

**Why this matters:** Without the model check, users complete multi-step setup and create 9 agents only to discover none can respond.

### 3.5 Step 10: Team Selection + Provisioning Progress UI

Provisioning involves 18–27 RPC calls (create + SOUL.md + MEMORY.md per agent). Show progress:

```
┌─────────────────────────────────────┐
│                                     │
│       Setting up Dev Squad          │
│                                     │
│   ████████░░░░  6 of 9 agents       │
│                                     │
│   ✅ Code Architect                 │
│   ✅ Frontend Developer             │
│   ✅ Backend Architect              │
│   ✅ QA Engineer                    │
│   ✅ Security Auditor               │
│   ⏳ Infra Engineer...              │
│   ○  Design Engineer                │
│   ○  Researcher                     │
│   ○  AI Expert                      │
│                                     │
└─────────────────────────────────────┘
```

Agent states: `✅` created, `⏳` in progress, `⚠️` failed (will retry), `○` pending.

### 3.6 Step 11: First Conversation (Cold Start)

After onboarding, user lands in chat. Do not show an empty screen.

```
┌─────────────────────────────────────┐
│ [≡]  🖥 Code Architect        [🧠] │
├─────────────────────────────────────┤
│                                     │
│  🖥 Code Architect                  │
│  ┌───────────────────────────────┐  │
│  │ Hey! I'm your architecture    │  │
│  │ and systems persona. I help   │  │
│  │ with design decisions, code   │  │
│  │ reviews, and technical        │  │
│  │ planning.                     │  │
│  │                               │  │
│  │ What are you working on?      │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌─ Try asking ──────────────────┐  │
│  │  "Review my architecture"     │  │  ← tappable chip → sends immediately
│  │  "Help me plan a feature"     │  │
│  │  "What should I build next?"  │  │
│  └───────────────────────────────┘  │
│                                     │
├─────────────────────────────────────┤
│ [+] [Type a message...    ] [🎤]   │
└─────────────────────────────────────┘
```

- Agent template field: `suggested_prompts: string[]` (3–4 items)
- Tapping a suggestion populates input and sends immediately
- Suggestions disappear after the first message is sent — never return for that session
- `one_question_frame` shown as subtitle below agent name

---

## 4. Context C: Device Migration

Already specced in §20.4 (TOFU re-pinning, secure store mismatch detection). One addition:

**Session restoration.** After re-pairing:

- `sessions.list` with `includeDerivedTitles: true`, `includeLastMessage: true`
- Populate drawer TODAY section with existing sessions
- Restore `lastActiveSessionKey` if available
- Banner: "Welcome back. I found [N] existing conversations on your gateway."

User should not feel like they're starting over. Agents and history are on the gateway — the new device just needs to reconnect.

---

## 5. Onboarding State Machine

Persist in MMKV so onboarding can resume after crash or force-quit:

```typescript
interface OnboardingState {
  phase:
    | 'welcome'
    | 'api_key'
    | 'gateway_url'
    | 'gateway_verify'
    | 'auth_token'
    | 'cert_pin'
    | 'connected'
    | 'model_check'
    | 'team_select'
    | 'provisioning'
    | 'complete';
  gatewayUrl?: string;           // persisted after connection test passes
  // authToken stored in expo-secure-store, not here
  selectedTeamId?: string;       // persisted after team selection
  provisioningProgress?: {
    teamId: string;
    agents: { id: string; status: 'pending' | 'created' | 'failed' }[];
    currentIndex: number;
  };
  completedAt?: number;          // timestamp when onboarding finished
}
```

On app launch:
- `phase === 'complete'` → skip to main app
- `phase === 'provisioning'` → resume from `currentIndex`
- Any earlier phase → resume from that step
- No state → fresh start

---

## 6. Permissions Timing

Never request permissions upfront. Always contextual:

| Permission | When Requested | Trigger |
|-----------|---------------|---------|
| Notifications | First cron job created, or user enables in Settings | "Polly needs notification permission to alert you when tasks complete." |
| Microphone | First tap on mic button | "Polly needs microphone access for voice input." |
| Camera | First tap Photo in attachment menu (Phase 2) | "Polly needs camera access to take photos." |
| Photo Library | First tap Photo in attachment menu (Phase 2) | "Polly needs photo library access to attach images." |
| Face ID | First enable App Lock in Settings → Security | "Polly uses Face ID to keep your conversations private." |
| Local Network (mDNS) | Gateway auto-discovery (Phase 2) | iOS system prompt — no custom rationale needed |

**Never** request multiple permissions at once. **Never** request before the user has taken an action that needs the permission.

---

## 7. Failure Recovery

| Failure | Recommended Handling |
|---------|---------------------|
| No internet on first launch | Show cached state if exists; "Connect to Wi-Fi or cellular to continue." Don't re-show welcome on every launch. |
| Gateway URL unreachable | Add: "Is your Mac on the same network? Is OpenClaw running?" with expandable troubleshooting |
| Auth token wrong | Add: "Where to find your token" link with OpenClaw UI instructions |
| Provisioning fails mid-team | Non-blocking per-agent retry (specced in §20.4) ✅ |
| App killed during provisioning | On next launch: detect partial state → show "Finishing setup..." → resume from `currentIndex` |
| Gateway connected but zero models | **Critical.** Block team selection until at least one model configured. See §3.4. |

---

## 8. Ongoing Gateway Health Checks

Post-onboarding background checks (never modal interruptions — surface as banners or Today cards):

| Check | When | Action on Failure |
|-------|------|------------------|
| `health` | Every reconnect | Amber banner: "Gateway reporting issues" |
| `models.list` | App foreground after 24h | "Your AI models are no longer configured. Check your gateway." |
| `agents.list` | On team switch | "Some agents couldn't be found. [Repair Team]" |
| `push.status` | On notification setting change | "Push notifications aren't configured on your gateway. [How to set up]" |
| Gateway version | On connect | "Your gateway may need an update for all features to work." |

---

## 9. Phase 1 Task List (What This Adds)

| Task | Component | Priority |
|------|-----------|----------|
| Write `setup.sh` developer bootstrap script | Repo root | P0 — blocks all dev work |
| Install all Phase 1 dependencies in `package.json` | `polly-ios/` | P0 — blocks all dev work |
| `OnboardingState` state machine in MMKV | iOS — stores | P0 |
| Post-connection gateway verification (model check, health) | iOS — onboarding | P1 |
| Provisioning progress UI | iOS — onboarding | P1 |
| Crash recovery: resume provisioning from `currentIndex` | iOS — onboarding | P1 |
| `suggested_prompts` field on all 43 agent templates | Agent templates | P1 |
| First-conversation UI (intro message + suggested prompt chips) | iOS — chat | P1 |
| Zero-models error handling | iOS — onboarding | P0 |
| App-killed-during-provisioning recovery | iOS — onboarding | P1 |
| Device migration: session restoration after re-pair | iOS — onboarding variant | P2 |
| Contextual permission request timing | iOS — throughout | P1 |
| Silent post-onboarding verification pass | iOS — background | P2 |

---

## 10. What This Doesn't Cover

- **Gateway installation itself.** `openclaw start` happens on the Mac — outside Polly's scope. The onboarding agent guides verbally.
- **LLM provider account creation.** Polly can link to signup pages but can't create accounts.
- **Obsidian vault setup.** Phase 1 vault integration is manual (document picker bookmark). Not part of onboarding — it's a post-onboarding Settings flow.
