# Polly Master Roadmap

**Polly** is a native iOS app (React Native + Expo) that connects to a self-hosted OpenClaw gateway, giving you a team of intelligent agents that know your work, your Obsidian vault, and your mental models.

For full feature specs, see `POLLY_IOS_SPEC.md`. For agent/team definitions, see `POLLY_AGENT_TEMPLATES.md`. For all active specs and their status, see `SPEC_INDEX.md`.

---

## Phase 1 — Core iOS App *(current)*

**Goal:** A working iOS app you can actually use day-to-day.

| Area | What ships |
|------|-----------|
| Gateway connection | WebSocket auth, reconnect, session management |
| Onboarding | Gateway setup, team selection (8 templates), conversational UI |
| Teams + Agents | Drawer navigation, agent list, team-scoped sessions |
| Chat | Streaming messages, markdown rendering, group chats |
| Vault | Quick capture → `_inbox/`, security-scoped Obsidian bookmark |
| Mental models | 12 built-in models, tap-to-apply lens system |
| Settings | Security, appearance, model selection |
| Voice interaction | Mic button, waveform, idle timer suppression, interruption recovery (`VOICE_INTERACTION.md`, `COPY_VOICE.md`) |
| Design system | `src/theme/colors.ts` tokens, `react-native-markdown-display` |

**Not in Phase 1:** Skills marketplace, model routing tiers, plans layer, Moltbook, full accessibility audit.

---

## Phase 2 — Skills + Polish

| Area | What ships |
|------|-----------|
| Figma integration | Link surfacing in chat, deep-link to boards (`FIGMA_INTEGRATION.md`) |
| Knowledge Skill | Unified semantic search over Obsidian vault + BookLore/EPUB library. Pluggable adapter architecture, FAISS HNSW, source cards UI (`KNOWLEDGE_SKILL.md`) |
| Skills Marketplace | ClawHub browser, install flow, §8.8 security model enforcement |
| Push notifications | APNs relay, `sendKey` hardening, push registration security fix |
| Image attachments | Photo/file attach in chat |
| Chat history search | Full-text search across sessions |
| Accessibility | Full VoiceOver audit + fixes |
| Group chat turn management | Gateway two-step dispatch (§22.5) |
| **Gesture + Ward + Agent Builder** | Vocal gesture system, universal mic button entry point (Ward/Liaison dual-mode), custom agent creation. Coordinated feature cluster — see below. |

### Gesture + Ward + Agent Builder Feature Cluster

Three interdependent Phase 2 features that must ship together:

| Spec | What ships |
|------|-----------|
| `GESTURE_LAYER.md` | Gesture recognizer (embedding similarity, pre-routing), gesture library, Gesture Builder system agent, `TellPollyIntent` + `OpenListeningIntent` Apple platform intents, Action Button onboarding suggestion |
| `WARD.md` | Universal mic button behavior, Ward/Liaison dual-mode (solo context injection, compressed state summary), routing protocol |
| `AGENT_BUILDER.md` | Agent Builder system agent, custom agent manifest registration, gesture vocabulary integration during creation |

**Dependencies (must be resolved in this order):**

1. Phase 1 voice pipeline must be live (voice transcription, mic button, gateway audio path)
2. Gesture pre-computation pipeline must run before Ward receives invocation (`GESTURE_LAYER.md` §4)
3. Gesture Layer must be live before Agent Builder gesture vocabulary integration works (`AGENT_BUILDER.md` §4.4)
4. Phase 1 gesture candidate log must start in Phase 1 — see `GESTURE_LAYER.md` §4.3

**Phase 1 prerequisite (immediate):** Add the gesture candidate log hook to the Phase 1 gateway message pipeline. Short utterances (≤ 8 words) with no routing match are logged for future gesture suggestion engine use. This is the only Phase 1 action required for this cluster.

**Pre-Phase 2 gate:** Push registration security fix must ship before Phase 2 goes to production.

---

## Phase 3 — Intelligence Layer

| Area | What ships |
|------|-----------|
| Cross-team bridges | Liaison agent (§22.9 Tier 1, SOUL-based team registry) |
| Context management in swarms | `::CONTEXT_FLUSH::` signal handling (§22.9) |
| Usage warnings | `usage.warning` event handling |

---

## Phase 4+ — Aspirational

| Area | Notes |
|------|-------|
| Model routing tiers | 4-tier system (§21) — Phase 3+ aspirational |
| Cross-team async mailbox | `_mailbox/[team-id]/` pattern (§22.9 Tier 2) |
| Plans layer | §23 design document only — not a Phase 1–3 target |
| Real-time cross-team sessions | Blocked on OpenClaw upstream (§22.9 Tier 3) |
| Moltbook | Full spec Phase 2+ content work |

---

## Open Infrastructure Items

| Item | Owner | Priority |
|------|-------|---------|
| Brave API key on gateway (`openclaw configure --section web`, `BRAVE_API_KEY`) | @infra | Medium — blocks agent web search |
| Push registration security fix | @backend | Required pre-production |

---

## Branch Structure

| Branch | Purpose |
|--------|---------|
| `development` | Active iOS development |
| `master` | Stable releases |
| `archive/pre-ios-rewrite` | Full history of Python/Electron era |
