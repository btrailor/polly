# iOS App — Spec Domain

The iOS App domain covers the Polly iOS client — the React Native (Expo) app that is the primary user-facing surface of the system.

## Specs in this domain

| File | What it covers | Status |
|------|---------------|--------|
| `ios-spec.md` | Master iOS spec (6972 lines) — all screens, flows, components, skill integration, agent management, themes, group chats, Today view, swarm mode, voice, mental models, domain system | Active — canonical |
| `voice-interaction.md` | Voice mode: STT/TTS pipeline, wake-word, push-to-talk, conversation mode, voice-native UX | Active |
| `voice-behavior-tests.md` | Behavioral test suite for voice mode | Active |
| `copy-voice.md` | Copy and microcopy guidelines — Polly's voice, tone, empty states, onboarding | Active |
| `asset-state-machine.md` | State machine for asset loading/error/empty states across the app | Active |
| `figma-integration.md` | Figma → iOS component handoff spec | Active |
| `influence-guide.md` | Design influence references — motion, spatial audio, material, interaction models | Active |

## Key decisions locked

- Aight is the iOS app name. OpenClaw is the gateway.
- Voice: STT/TTS handled client-side. Never use TTS tool from gateway — causes playback issues.
- Today view: personal dashboard for reminders, tasks, deadlines, background processes.
- Domain system: user-declared domains (name, color, icon, keywords) stored in MMKV `polly.domains`, synced to gateway as `polly.knowledge.domain_seeds`.
- Theme behavior: `polly.ios.aestheticStance` config key, Layer 5 in prompt injection hierarchy.
- Mental model framing: Layer 1 (closest to message), client-side, `<framing>` block.

## Cross-domain dependencies

- Domain seeds → Knowledge Skill domain taxonomy (`knowledge/knowledge-skill.md`)
- Theme config key → Prompt injection Layer 5 (`knowledge/service-contracts.md §4`)
- Somatic/prosodic state detection → Agent Somatic Interface (`agent-system/somatic-interface.md`)
- Ambient Agent "Polly noticed…" card → Ambient Agent behavioral spec (`cognitive-features/`)
- Mental model framing → Knowledge Skill `knowledge_search` (vault note injection at Layer 1)
- export/manifest.json → Cognitive Artifact spec (`knowledge/cognitive-artifact.md`)
