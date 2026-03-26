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
## setup.sh — Polly Developer Bootstrap

Run from the repo root to verify prerequisites and install all dependencies.

```bash
#!/bin/bash
# setup.sh — Polly developer bootstrap
# Run from repo root: bash setup.sh

set -e

echo "=== Polly Developer Setup ==="

# 1. Check prerequisites
echo "Checking prerequisites..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Install via: brew install node"; exit 1; }
node_version=$(node -e "process.exit(parseInt(process.version.slice(1)) < 18 ? 1 : 0)" 2>/dev/null) || { echo "❌ Node.js 18+ required. Current: $(node --version)"; exit 1; }
[[ $(xcode-select -p 2>/dev/null) ]] || { echo "❌ Xcode not found. Install from App Store."; exit 1; }
command -v pod >/dev/null 2>&1 || { echo "⚠️  CocoaPods not found. Install: sudo gem install cocoapods"; }

# 2. Check OpenClaw gateway
echo "Checking OpenClaw gateway..."
GATEWAY_PORT=${OPENCLAW_PORT:-18789}
if ! curl -s --max-time 3 http://localhost:${GATEWAY_PORT}/health >/dev/null 2>&1; then
  echo "⚠️  OpenClaw gateway not reachable at localhost:${GATEWAY_PORT}"
  echo "   Install:  npm install -g @openclaw/server"
  echo "   Start:    openclaw start"
  echo "   Then re-run this script."
  echo ""
  echo "   (Or set OPENCLAW_PORT if using a non-default port)"
  exit 1
fi
echo "✅ Gateway reachable at localhost:${GATEWAY_PORT}"

# 3. Install iOS dependencies
echo "Installing polly-ios dependencies..."
cd polly-ios
npm install
echo "✅ npm install complete"

# 4. Pod install (for native modules)
if [ -d "ios" ]; then
  echo "Installing CocoaPods..."
  cd ios && pod install && cd ..
  echo "✅ Pod install complete"
fi

# 5. Verify critical packages
echo "Verifying critical packages..."
MISSING=0
for pkg in expo-openclaw-chat zustand react-native-mmkv expo-secure-store expo-haptics expo-sqlite lucide-react-native; do
  if [ ! -d "node_modules/$pkg" ]; then
    echo "  ❌ $pkg not installed"
    MISSING=1
  fi
done
if [ $MISSING -eq 1 ]; then
  echo "Some packages are missing. Check package.json and re-run npm install."
  exit 1
fi
echo "✅ Critical packages verified"

# 6. Environment config
cd ..
if [ ! -f "polly-ios/.env.local" ]; then
  echo "Creating polly-ios/.env.local..."
  cat > polly-ios/.env.local << 'EOF'
# Gateway configuration — edit before running
EXPO_PUBLIC_GATEWAY_URL=http://localhost:18789
# EXPO_PUBLIC_GATEWAY_TOKEN=your_auth_token_here
EOF
  echo "⚠️  Edit polly-ios/.env.local with your gateway auth token before running."
fi

echo ""
echo "=== Setup Complete ==="
echo "Next steps:"
echo "  1. Edit polly-ios/.env.local with your gateway auth token"
echo "  2. cd polly-ios && npx expo start --ios"
echo "  3. Open in Simulator or scan QR with Expo Go"
echo ""
echo "First-time gateway setup:"
echo "  - Open OpenClaw on your Mac"
echo "  - Copy your auth token from Settings → Security"
echo "  - Paste it in polly-ios/.env.local"
```

