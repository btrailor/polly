# iOS App — Current State

*What is built and running as of Phase 1.*

## Stack

- React Native + Expo (TypeScript)
- MMKV for local storage
- WebSocket connection to OpenClaw gateway
- `react-native-markdown-display` for chat rendering
- `src/theme/colors.ts` — design token source of truth (do not use `src/colors.ts` — duplicate, to be deleted)

## Screens + Features Shipped

| Feature | Status | Notes |
|---------|--------|-------|
| Gateway WebSocket auth + reconnect | ✅ Shipped | Session management |
| Onboarding flow | ✅ Shipped | Gateway setup, team selection (8 templates) |
| Team drawer + agent list | ✅ Shipped | Team-scoped sessions |
| Chat (streaming, markdown) | ✅ Shipped | `react-native-markdown-display` |
| Group chats | ✅ Shipped | Multi-agent |
| Voice mic button | ✅ Scaffolded | `VoiceMicButton.tsx`, `VoiceButtonActive`, `VoiceButtonIdle` |
| Voice recording hook | ⚠️ Scaffolded only | `useVoiceRecording.ts` — no real audio recording yet |
| Vault quick capture | ✅ Shipped | `_inbox/` via expo-document-picker security-scoped bookmarks |
| Mental models (12 built-in) | ✅ Shipped | Tap-to-apply lens system |
| Settings | ✅ Shipped | Security, appearance, model selection |
| Design system | ✅ Shipped | `src/theme/colors.ts` tokens |

## Known Issues (open)

- `VoiceMicButton.tsx` line 269: uses 🎤 emoji — must be replaced with Lucide `Mic` icon (§18.3)
- `useVoiceRecording.ts`: scaffolded, no real audio — `VOICE_BEHAVIOR_TESTS.md` (543 lines) cannot run until fixed
- `VOICE_INTERACTION.md` REQ-VOICE-01: references Swift `UIApplication.shared.isIdleTimerDisabled` — must use `expo-keep-awake`
- `polly-ios/src/colors.ts`: duplicate of `src/theme/colors.ts` — delete
- `PROFESSOR_STUDIES_MODE.md` referenced in `chat.tsx` header but file doesn't exist — Brett to confirm

## Voice Architecture (Phase 1)

- STT/TTS: client-side only. Gateway never handles audio.
- Gateway receives text only; responds with text only.
- Never call a TTS tool from the gateway — playback issues.
- Specs: `VOICE_INTERACTION.md`, `COPY_VOICE.md`, `VOICE_BEHAVIOR_TESTS.md`

## Design Constitution (non-negotiable, §18.3)

- Icons: Lucide only (`lucide-react-native`) — no emoji, no custom SVG without design review
- Colors: `src/theme/colors.ts` tokens only
- Typography: system font stack only
