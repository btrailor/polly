# Phase 1: iOS Foundation

**Status:** 🔨 In progress — early scaffold  
**Gate:** None — first phase  
**Spec source:** `POLLY_IOS_SPEC.md`, `VOICE_INTERACTION.md`, `COPY_VOICE.md`, `VOICE_BEHAVIOR_TESTS.md`

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
- [ ] Gateway client library (`expo-openclaw-chat` or equivalent — confirm with @backend)

### Lockdown Mode — Phase 1 Architectural Hooks (LOCKDOWN_MODE.md)
*Full Lockdown Mode ships Phase 2, but these architectural decisions are not retrofittable. Must be designed now.*
- [ ] File storage model: all session files use iOS `NSFileProtectionComplete` (Complete Protection class) — @backend + @frontend agree on path
- [ ] Voice buffer policy: voice audio never written to disk — buffers memory-only only. `useVoiceRecording.ts` must enforce this from the start.
- [ ] Secure Enclave key path: document where gateway encryption key will live (Secure Enclave vs. Keychain) — @backend decision, must be locked in Phase 1 before any credential storage is implemented
- [ ] No APNs dependency for core functionality — gateway connection must work without push (polling fallback required)

### Gateway Connection (§3)
- [ ] `expo-secure-store` integration — read/write gateway URL + auth token
- [ ] Wire `app/index.tsx` gateway check to actual secure store (remove `isConfigured = false` hardcode)
- [ ] WebSocket client: connect, authenticate, session management
- [ ] Reconnect logic with exponential backoff
- [ ] Connection state store (Zustand or MMKV): connected/reconnecting/failed
- [ ] Gateway health indicator in UI

### Onboarding Flow (§5)
- [ ] Gateway URL input field with validation
- [ ] Test connection — WebSocket handshake, success/failure feedback
- [ ] Store gateway URL in expo-secure-store on success
- [ ] Team selection screen (8 default team templates)
- [ ] Team template data model
- [ ] Agent roster seeded from selected team template
- [ ] Onboarding → main app navigation on completion

### State Management
- [ ] Agent/team store (current team, agent list, active agent)
- [ ] Session store (current session ID, message history)
- [ ] Settings store (gateway URL, model selection, appearance)
- [ ] Persistence layer (MMKV for non-sensitive, expo-secure-store for credentials)

### Navigation + Layout (§6)
- [ ] `DrawerPanel` component — custom animated drawer (§6.24: Animated + PanGestureHandler, NOT @react-navigation/drawer)
- [ ] Mount DrawerPanel as overlay in `MainLayout` (remove TODO comment)
- [ ] Agent list inside drawer, team-scoped
- [ ] Team switcher in drawer
- [ ] Bottom tab bar or equivalent navigation between main surfaces

### Chat Screen — Core (§4)
- [ ] WebSocket message send (text input → gateway)
- [ ] Streaming message receive (gateway → render)
- [ ] Message list (FlatList, inverted, scrolls to bottom on new message)
- [ ] Message bubbles: user vs. agent distinction
- [ ] Agent name + avatar in message header
- [ ] Markdown rendering (`react-native-markdown-display`)
- [ ] Typing indicator while streaming
- [ ] Session continuity (reconnect resumes correct session)

### Chat Screen — Group Chats (§22)
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

### Vault Quick Capture (§10)
- [ ] `expo-document-picker` security-scoped bookmark for Obsidian vault
- [ ] Write to `_inbox/` on capture
- [ ] Quick capture entry point in chat screen or home

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
- [ ] Model selection per agent
- [ ] Appearance (theme selection)
- [ ] `settings/integrations.tsx` — integration list (currently 6-line stub)

### Today Screen (§8)
- [ ] Reminders list
- [ ] Tasks list
- [ ] Deadlines
- [ ] Background process indicators
- [ ] `aight_item` creation path (trigger, item, process types)

### Design Constitution Compliance
- [ ] Full Lucide icon audit — no emoji, no custom SVG without design review
- [ ] `src/theme/colors.ts` tokens used everywhere — no hardcoded hex values
- [ ] Delete `polly-ios/src/colors.ts` (duplicate)
- [ ] Resolve `PROFESSOR_STUDIES_MODE.md` reference in `chat.tsx` comment

### QA Gate
- [ ] `VOICE_BEHAVIOR_TESTS.md` test suite (543 lines) — all passing
- [ ] @qa_guy sign-off

## Done when
App is functionally usable end-to-end: gateway connects, onboarding works, chat sends/receives messages with streaming, voice records real audio, drawer navigation works, Today view shows items. @qa_guy sign-off.
