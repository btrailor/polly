# Phase 1: iOS Foundation

**Status:** 🔨 In progress — early scaffold  
**Gate:** None — first phase  
**Spec source:** `POLLY_IOS_SPEC.md`, `VOICE_INTERACTION.md`, `COPY_VOICE.md`, `VOICE_BEHAVIOR_TESTS.md`, `ONBOARDING_SPEC.md`

## What Actually Exists Right Now

- Expo Router file structure with screen stubs (most are 13-line placeholder views)
- `chat.tsx` (216 lines): input bar, text field, voice state machine wired to mic button — **no message list, no gateway connection**
- `VoiceMicButton.tsx`, `VoiceDraftPrompt.tsx`: voice UI components
- `useVoiceRecording.ts`: scaffolded — no real audio recording
- `src/theme/colors.ts`: design token system (typography, spacing, colors)
- `app/index.tsx`: redirect stub (`isConfigured = false` hardcoded — not wired to store)
- `app/onboarding.tsx`: title + subtitle text — no actual gateway input or flow
- `app/(main)/_layout.tsx`: Stack wrapper with TODO comment for DrawerPanel

Everything else (Today, Settings, Agents, Shortcuts, Moltbook, Usage) is a 13-line scaffold placeholder.

---

## Tasks

### Dependencies — Install Before Any Implementation
- [ ] `expo-secure-store` — gateway credential storage
- [ ] `react-native-mmkv` — fast local state persistence
- [ ] `zustand` — state management
- [ ] `@shopify/flash-list` — high-performance message list
- [ ] `react-native-markdown-display` — markdown rendering in chat
- [ ] `lucide-react-native` — icon system (design constitution)
- [ ] `expo-keep-awake` — screen-on during voice recording
- [ ] `expo-av` or `expo-audio` — real audio recording
- [ ] `expo-document-picker` — vault security-scoped bookmarks
- [ ] `expo-haptics` — haptic feedback throughout app
- [ ] `expo-sqlite` — local message cache (offline support)
- [ ] Gateway client library (`expo-openclaw-chat` or equivalent — confirm with @backend)

### Lockdown Mode — Phase 1 Architectural Hooks (LOCKDOWN_MODE.md)
*Full Lockdown Mode ships Phase 2, but these architectural decisions are not retrofittable. Must be designed now.*
- [ ] File storage model: all session files use iOS `NSFileProtectionComplete` (Complete Protection class) — @backend + @frontend agree on path
- [ ] Voice buffer policy: voice audio never written to disk — buffers memory-only only. `useVoiceRecording.ts` must enforce this from the start.
- [ ] Secure Enclave key path: document where gateway encryption key will live (Secure Enclave vs. Keychain) — @backend decision, must be locked in Phase 1 before any credential storage is implemented
- [ ] No APNs dependency for core functionality — gateway connection must work without push (polling fallback required)

### Developer Bootstrap
- [ ] `setup.sh` at repo root — prerequisite checks, dep install, gateway verify, .env.local creation (P0 — blocks all dev work)
- [ ] `polly-ios/package.json` updated with full Phase 1 dependency set (see `ONBOARDING_SPEC.md §2.2` for complete list)

### Onboarding — State Machine + Flow (`ONBOARDING_SPEC.md`)
- [ ] `OnboardingState` interface + MMKV persistence (11 phases: welcome → complete)
- [ ] App launch gate: if `phase === 'complete'` → skip to main; if `phase === 'provisioning'` → resume from `currentIndex`; earlier phase → resume from that step
- [ ] Silent initialization on cold start: expo-sqlite message cache, MMKV setup, default prefs, pre-populate 12 mental models
- [ ] Post-connection gateway verification: `models.list` check before team selection — **block if zero models** with actionable message (P0 — critical gap)
- [ ] Post-connection gateway verification: `health` check → degraded warning with continue/retry
- [ ] Post-connection: `config.get` → store gateway version + capabilities in MMKV
- [ ] Provisioning progress UI: progress bar + per-agent status (✅ created, ⏳ in progress, ⚠️ failed, ○ pending)
- [ ] Provisioning crash recovery: resume from `provisioningProgress.currentIndex` on relaunch
- [ ] Permissions timing: contextual only — never upfront, never multiple at once (mic on first voice tap, notifications on first cron, Face ID on first App Lock enable)


- [ ] `expo-secure-store` integration — read/write gateway URL + auth token
- [ ] Wire `app/index.tsx` gateway check to actual secure store (remove `isConfigured = false` hardcode)
- [ ] WebSocket client: connect, authenticate, session management
- [ ] Reconnect logic with exponential backoff
- [ ] Connection state store (Zustand or MMKV): connected/reconnecting/failed
- [ ] Gateway health indicator in UI
- [ ] Per-agent session key construction: `agent:<agentId>:main` format (§3.7)
- [ ] Idempotency key on every send — prevents duplicate messages on retry (§3.5)
- [ ] `NO_REPLY` / `HEARTBEAT_OK` silent reply filtering — never render these in chat (§3.6)
- [ ] `NSAllowsLocalNetworking` in `Info.plist` — required for LAN WebSocket (§3.14)

### Onboarding Flow (§5)
- [ ] Gateway URL input field with validation
- [ ] Test connection — WebSocket handshake, success/failure feedback
- [ ] Store gateway URL in expo-secure-store on success
- [ ] Team selection screen (8 default team templates)
- [ ] Team template data model
- [ ] Agent roster seeded from selected team template
- [ ] Onboarding → main app navigation on completion

### State Management (§12)
- [ ] Agent/team store (current team, agent list, active agent)
- [ ] Session store (current session ID, message history)
- [ ] Settings store (gateway URL, model selection, appearance)
- [ ] Unread store — per-session unread counts, clear on session focus
- [ ] Persistence layer (MMKV for non-sensitive, expo-secure-store for credentials)
- [ ] `lastActiveSessionKey` — persist in MMKV, restore on launch
- [ ] `draftText.[sessionKey]` — persist unsent input text per session across restarts

### Navigation + Layout (§6)
- [ ] `DrawerPanel` component — custom animated drawer (§6.24: Animated + PanGestureHandler, NOT @react-navigation/drawer)
- [ ] Mount DrawerPanel as overlay in `MainLayout` (remove TODO comment)
- [ ] Agent list inside drawer, team-scoped
- [ ] Team switcher in drawer
- [ ] Session list in drawer TODAY section (sessions.list integration)
- [ ] Swipe-left on session row → delete (with confirmation)
- [ ] Long-press on session row → rename / delete / pin
- [ ] Unread badge dot on hamburger icon when any session has unread > 0
- [ ] Bottom tab bar or equivalent navigation between main surfaces

### Chat Screen — Input Bar (§4)
- [ ] Mic/Send toggle: right button shows `Mic` (Lucide) when input empty, `SendHorizontal` (Lucide) when text present — crossfade ~150ms
- [ ] Send button: disabled (muted) when empty, enabled (accent) when text present
- [ ] `[+]` attachment button left of input — opens bottom sheet with: Vault Note, Mental Model, Quick Capture; Photo + File slots shown as "Phase 2" disabled
- [ ] Send on Enter (hardware keyboard — iPad, Bluetooth); Shift+Enter for newline
- [ ] Send haptic: light impact on send
- [ ] `keyboardDismissMode="interactive"` on message FlatList (keyboard follows finger like iMessage)
- [ ] Stop generation button: during streaming, right button becomes filled square (Lucide `Square`); taps call `chat.abort`
- [ ] Slash command palette: typing `/` as first character opens command list for active agent; filters as user types; tapping populates or executes

### Chat Screen — Core (§4)
- [ ] WebSocket message send (text input → gateway)
- [ ] Streaming message receive (gateway → render)
- [ ] Message list (FlashList, inverted, scrolls to bottom on new message)
- [ ] `keyboardShouldPersistTaps="handled"` on message list
- [ ] Message bubbles: user vs. agent distinction
- [ ] Agent name + avatar in message header
- [ ] Markdown rendering (`react-native-markdown-display`)
- [ ] Code block: copy button top-right (clipboard icon → checkmark, resets 2s), language label, horizontal scroll on long lines
- [ ] Thinking/reasoning panel: collapsible (for extended thinking models) (§3.6, §6.1)
- [ ] Tool call display: collapsible "Searching..." block shown during tool use (§4.1)
- [ ] Typing indicator while streaming
- [ ] Scroll-to-bottom floating button: appears when >200pt from bottom; shows unread count badge; tapping scrolls to bottom
- [ ] Regenerate response: button below completed assistant messages (muted "↻ Regenerate") or in long-press menu; re-sends last user message
- [ ] Long-press message → context menu: Copy, Regenerate, Share (iOS share sheet), Reply/quote
- [ ] Date separators between messages from different days ("Today", "Yesterday", "March 23")
- [ ] "Conversation started [date]" marker at top of loaded history
- [ ] chat.history → pull-to-load older messages (§4.1)
- [ ] Session continuity (reconnect resumes correct session)
- [ ] Error states: disconnected banner ("Disconnected — [Retry]"), failed message retry icon, token-limit error in bubble, session-expired auto-recreate
- [ ] Local message cache (expo-sqlite): persist last N messages per session; render cached messages on launch before gateway connects

### Chat Screen — Empty State / Cold Start
- [ ] Suggested prompts: when session is empty, show 3–4 tappable prompt chips
- [ ] Agent `suggested_prompts: string[]` field in template (3–4 items per agent)
- [ ] Tapping a suggestion populates input and sends immediately
- [ ] Agent `one_question_frame` as subtitle below agent name in empty state

### Offline + Disconnected (§4)
- [ ] On app open with no network: render cached messages, input bar disabled with "No connection" state
- [ ] Network drops mid-conversation: queue unsent messages, show "Sending..." state, auto-retry on reconnect
- [ ] Distinguish "gateway offline" from "no internet" in error messaging
- [ ] Offline vault access: vault notes browsable offline; quick capture writes to local queue, syncs on connect

### Loading States
- [ ] `SkeletonLoader` component — pulsing gray rectangles matching content layout
- [ ] Use SkeletonLoader on: chat history load, agent list, Today, Settings, session list
- [ ] Full-screen connection state on first launch while handshake in progress

### Haptics Policy (expo-haptics)
- [ ] Send message — light impact
- [ ] Receive first streaming token — soft notification
- [ ] Long-press context menu open — medium impact
- [ ] Swipe delete threshold cross — light impact
- [ ] Error states — error notification

### In-App Notifications
- [ ] Badge dot on drawer hamburger icon when any non-active session has unread > 0
- [ ] In-app toast banner when non-active agent posts (brief, dismissible, tappable to navigate)
- [ ] Multi-agent session support
- [ ] Agent header shows active participants
- [ ] Message routing to correct agent
- [ ] Turn management display

### Voice — Real Implementation (§7)
- [ ] Replace `useVoiceRecording.ts` scaffold with real audio recording (`expo-av` or `expo-audio`)
- [ ] STT pipeline: send audio buffer to gateway or client-side STT
- [ ] Idle timer suppression during recording (`expo-keep-awake`)
- [ ] Background interruption handling (phone call, app background) — save draft
- [ ] Waveform amplitude data from real audio buffer
- [ ] Replace 🎤 emoji with Lucide `Mic` icon in `VoiceMicButton.tsx` line 269
- [ ] Remove Swift `UIApplication.shared.isIdleTimerDisabled` from `VOICE_INTERACTION.md` REQ-VOICE-01 spec (use `expo-keep-awake`)

### Vault Quick Capture (§10 + KNOWLEDGE_WRITE_PATH.md §3.1)
- [ ] `expo-document-picker` security-scoped bookmark for Obsidian vault
- [ ] Write to `_inbox/YYYY-MM-DD-HHmm-{slug}.md` using standard frontmatter (KNOWLEDGE_WRITE_PATH.md §2)
- [ ] Quick capture entry point in chat screen or home
- [ ] **Offline degradation**: if gateway unavailable at capture time, write with `domain: null` and `tags: []` — no silent failures, deferred enrichment at promotion
- [ ] Fallback destination: `~/.polly/inbox/` on gateway if no vault configured; sync when vault connected

### Mental Models (§11)
- [ ] Mental model data definitions (12 built-in models)
- [ ] Tap-to-apply lens system — inject model framing into message (Layer 1 prompt injection)
- [ ] Mental model selector UI

### Agents Screen (§6)
- [ ] Agent list screen (`agents/index.tsx` — currently 6-line stub)
- [ ] Agent detail screen (`agents/[id].tsx` — currently 8-line stub)
- [ ] Agent SOUL display (name, description, current team)

### Settings Screen (§9)
- [ ] Gateway URL settings (change/reconnect)
- [ ] Appearance (theme selection)
- [ ] `settings/integrations.tsx` — integration list (currently 6-line stub)
- [ ] Settings → Models → Routing screen (MODEL_ROUTING_SPEC.md §6):
  - [ ] `models.list` RPC call → populate model list grouped by tier
  - [ ] Routing policy selector (Token Saver / Balanced / Quality First)
  - [ ] Per-agent overrides list (pinned model or domain routing per agent)

### Model Routing — Phase 1 (MODEL_ROUTING_SPEC.md)
*Phase 1 = manual selection only. No auto-routing. User chooses.*
- [ ] `ModelEntry` type + MMKV model registry (populated from `models.list`)
- [ ] `RoutingProfile` type + gateway config storage (`config.patch polly.routing.profiles` — @backend confirmed `config.patch` supports arbitrary keys; gateway is source of truth not MMKV)
- [ ] `OverrideEvaluator` only — check `pinnedModel` before every send
- [ ] Model picker component (used in: agent creation, agent detail, chat nav bar)
- [ ] "Always use this model" toggle in agent creation + agent detail → sets `pinnedModel`
- [ ] Dynamic `agents.update` before `chat.send` when override is active (Option A — accept race condition, document it)
- [ ] Model attribution in chat bubble footer ("via llama3.1:8b")
- [ ] Model pill in chat nav bar (shows active model for session)
- [ ] `RoutingReason` enum — start with: `pinned_model`, `user_override`, `default`, `fallback`
- [ ] `RoutingDecision` type — log to MMKV ring buffer (last 100)
- [ ] @backend: confirm 6 open questions in `MODEL_ROUTING_SPEC.md §9` before Phase 2

### Today Screen (§8)
- [ ] Reminders list (cron.list integration)
- [ ] Tasks list
- [ ] Deadlines
- [ ] Background process indicators
- [ ] `aight_item` creation path (trigger, item, process types)

### Group Chat — Phase 1 Foundation (SWARM_COORDINATION_SPEC.md §7 Phase 1)
- [ ] Group creation UI (name + member selection)
- [ ] Fan-out via `agent` RPC with `groupId`
- [ ] Multi-agent message rendering: agent label, accent color, @mention highlighting
- [ ] `defaultResponder` for messages with no @mention
- [ ] `mention` and `always` activation modes per agent (set at group creation)
- [ ] Per-agent thinking toast (requires `chat.typing` event with agent identity — @backend §8 Q2)
- [ ] Group sessions in drawer (grouped under group name)
- [ ] `GroupStreamState` in Zustand: key by `${agentId}:${runId}`, multiple bubbles streaming simultaneously
- [ ] Auto-scroll follows most recently updated bubble; scroll lock per-bubble-cluster (not per-bubble)
- [ ] **Forward-compatible data model additions (required Phase 1 — not deferrable):**
  - [ ] `topology` field on message objects: `"chat"` (default), `"chorus"`, `"architecture"` — unused in Phase 1 but must exist
  - [ ] `chorus_position: null` nullable field on message objects

### P2 — Nice to Have (don't block Phase 1 completion)
- [ ] Edit and resend: long-press user message → Edit → populates input → resend replaces history from that point
- [ ] Conversation export to vault: one tap saves conversation as Obsidian note
- [ ] Swipe between agents: swipe left/right on chat view to switch recent agents
- [ ] Response time indicator: show duration ("3.2s") in message footer
- [ ] Copy conversation as markdown: action to copy full conversation

### Sensibility Foundation — Phase 1 (SENSIBILITY_SYSTEM_SPEC.md §7 Phase 1)
*Decisions locked: replace useColors() now, all 7 theme files now, Reas default, bubbleStyle field but rounded-only render*
- [ ] `ThemeTokens` interface (`src/theme/tokens.ts`) — all fields from §3.2
- [ ] Reas theme file (`src/theme/themes/reas.ts`) — token values matching current `colors.ts` (visual appearance unchanged)
- [ ] All 6 remaining theme files (`fidenza.ts`, `ghostbox.ts`, `martens.ts`, `jetset.ts`, `riley.ts`, `albers.ts`) — values from §19.6 (not selectable, but files exist)
- [ ] `ThemeContext` + `ThemeProvider` (`src/theme/ThemeContext.tsx`)
- [ ] `useTheme()` hook (`src/theme/useTheme.ts`)
- [ ] Migrate ALL components from `useColors()` → `useTheme().tokens`
- [ ] Delete `useColors()`, `semanticColors` alias layer, `light` export from `colors.ts`
- [ ] Fix all `(colors as any).bgPrimary` casts — proper typing via `ThemeTokens`
- [ ] `bubbleStyle` field in `ThemeTokens` — Reas = `'rounded'`, all others set per §19.6 (ChatBubble renders rounded only regardless)
- [ ] MMKV `polly.sensibility` key — always `"reas"` in Phase 1 (picker ships Phase 3)
- [ ] `structural_rules: null` field in agent manifest schema — empty in Phase 1, Phase 3 activation

### Design Constitution Compliance
- [ ] Full Lucide icon audit — no emoji, no custom SVG without design review
- [ ] `src/theme/colors.ts` tokens used everywhere — no hardcoded hex values
- [ ] Delete `polly-ios/src/colors.ts` (duplicate)
- [ ] Resolve `PROFESSOR_STUDIES_MODE.md` reference in `chat.tsx` comment

### QA Gate
- [ ] `VOICE_BEHAVIOR_TESTS.md` test suite (543 lines) — all passing
- [ ] @qa_guy sign-off

## iPad
Phase 1 target is iPhone. iPad renders phone layout at full width — acceptable. Navigation architecture must not paint itself into a phone-only corner (split-view sidebar is Phase 2). Add `// TODO: iPad adaptive layout` markers at drawer and chat layout.

## Done when
All P0 tasks checked. App is functionally usable end-to-end: gateway connects, onboarding works, chat sends/receives with streaming, stop generation works, cached messages load offline, voice records real audio, drawer navigation works, Today view shows items. @qa_guy sign-off.
