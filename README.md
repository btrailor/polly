# Polly

**A personal AI system built for how you actually think.**

Polly is a native iOS app that connects to your self-hosted OpenClaw gateway, giving you a team of intelligent agents that know your work, your knowledge base, and your mental models — and can act on them.

---

## What it is

- **Team-based agents** — Organized around what you're doing (Dev Squad, Content Studio, Life Team, etc.). Each team has specialized agents that collaborate in group chats.
- **Vault-connected** — Reads and writes to your Obsidian vault via iOS security-scoped bookmarks. Quick captures land in `_inbox/`; the agents help you process them.
- **Mental models** — 12 built-in thinking frameworks (Systems Thinking, Socratic Method, First Principles, etc.) you can apply to any conversation as a lens.
- **Your gateway, your data** — All AI traffic routes through your self-hosted OpenClaw gateway on your Mac. Nothing goes through a third-party server.

---

## Stack

| Layer | Tech |
|-------|------|
| iOS app | React Native + Expo (TypeScript) |
| Navigation | expo-router (file-based) |
| Design tokens | `src/theme/colors.ts` |
| Markdown | `react-native-markdown-display` |
| Local storage | MMKV + expo-sqlite |
| Secrets | expo-secure-store |
| Gateway | OpenClaw (self-hosted, Mac mini) |
| Transport | WebSocket (`wss://`) |

---

## Repo layout

```
POLLY_IOS_SPEC.md          — Full iOS spec (authoritative)
POLLY_AGENT_TEMPLATES.md   — Agent SOUL templates + team definitions
MASTER_ROADMAP.md          — Phased delivery plan
src/
  theme/
    colors.ts              — Design tokens (authoritative)
archive/                   — Pre-iOS legacy docs
```

Old Python backend, Electron app, and openspec are preserved on the `archive/pre-ios-rewrite` branch.

---

## Branches

| Branch | Purpose |
|--------|---------|
| `development` | Active iOS development |
| `master` | Stable releases |
| `archive/pre-ios-rewrite` | Full history of the Python/Electron era |

---

## Gateway setup

Polly requires a running OpenClaw gateway. The iOS app connects via WebSocket at `wss://your-gateway-domain`.

See `POLLY_IOS_SPEC.md §3` for the full WebSocket protocol and `§20.4` for the onboarding flow.

---

## Phase 1 scope

- Core chat UI (agents + group chats)
- Teams + drawer navigation
- Vault quick capture
- Mental models lens system
- Onboarding (gateway connection + team selection)
- Settings (security, appearance, model)

Phase 2+ features (skills marketplace, model routing, plans layer) are stubbed in the spec but not implementation targets for Phase 1.

---

## License

Personal use.
