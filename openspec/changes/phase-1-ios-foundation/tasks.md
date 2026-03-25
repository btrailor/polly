# Phase 1: iOS Foundation

**Status:** 🔨 In progress  
**Gate:** None — first phase  
**Spec source:** `POLLY_IOS_SPEC.md`, `VOICE_INTERACTION.md`, `COPY_VOICE.md`, `VOICE_BEHAVIOR_TESTS.md`

## Goal

A working iOS app you can use day-to-day: connect to your OpenClaw gateway, chat with your agent team, capture vault notes, use voice.

## Tasks

### Gateway Connection
- [x] WebSocket auth + session management
- [x] Reconnect logic

### Onboarding
- [x] Gateway setup flow
- [x] Team selection (8 default templates)
- [x] Conversational onboarding UI

### Teams + Agents
- [x] Team drawer navigation
- [x] Agent list per team
- [x] Team-scoped chat sessions

### Chat
- [x] Streaming message rendering
- [x] Markdown rendering (`react-native-markdown-display`)
- [x] Group chats (multi-agent)

### Vault
- [x] Quick capture to `_inbox/`
- [x] Security-scoped Obsidian bookmark (expo-document-picker)

### Mental Models
- [x] 12 built-in models
- [x] Tap-to-apply lens system

### Settings
- [x] Security settings
- [x] Appearance settings
- [x] Model selection

### Design System
- [x] `src/theme/colors.ts` token system

### Voice
- [x] `VoiceMicButton.tsx` scaffold
- [x] `VoiceButtonActive`, `VoiceButtonIdle` components
- [ ] `useVoiceRecording.ts` — real audio recording (currently scaffolded only)
- [ ] Replace 🎤 emoji with Lucide `Mic` icon in `VoiceMicButton.tsx` line 269
- [ ] Replace Swift idle timer API in `VOICE_INTERACTION.md` REQ-VOICE-01 with `expo-keep-awake`
- [ ] `VOICE_BEHAVIOR_TESTS.md` — run full 543-line test suite (blocked until real audio impl)

### Cleanup
- [ ] Delete `polly-ios/src/colors.ts` (duplicate of `src/theme/colors.ts`)
- [ ] Confirm `PROFESSOR_STUDIES_MODE.md` reference in `chat.tsx` — real spec or stale comment?

### Design Constitution compliance audit
- [ ] Full Lucide icon audit (no emoji, no custom SVG without review)
- [ ] `src/theme/colors.ts` usage — no hardcoded hex anywhere

## Done when
All tasks checked. Voice test suite passing. No design constitution violations. @qa_guy sign-off.
