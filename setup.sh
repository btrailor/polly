#!/bin/bash
# setup.sh — Polly developer bootstrap
# Run from repo root: bash setup.sh

set -e

echo "=== Polly Developer Setup ==="

# 1. Check prerequisites
echo "Checking prerequisites..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Install via: brew install node"; exit 1; }
node -e "process.exit(parseInt(process.version.slice(1)) < 18 ? 1 : 0)" 2>/dev/null || { echo "❌ Node.js 18+ required. Current: $(node --version)"; exit 1; }
[[ $(xcode-select -p 2>/dev/null) ]] || { echo "❌ Xcode not found. Install from App Store."; exit 1; }
command -v pod >/dev/null 2>&1 || echo "⚠️  CocoaPods not found. Install: sudo gem install cocoapods"

# 2. Check OpenClaw gateway
echo "Checking OpenClaw gateway..."
GATEWAY_PORT=${OPENCLAW_PORT:-18789}
if ! curl -s --max-time 3 "http://localhost:${GATEWAY_PORT}/health" >/dev/null 2>&1; then
  echo "⚠️  OpenClaw gateway not reachable at localhost:${GATEWAY_PORT}"
  echo "   Install:  npm install -g @openclaw/server"
  echo "   Start:    openclaw start"
  echo "   Then re-run this script."
  exit 1
fi
echo "✅ Gateway reachable"

# 3. Install iOS dependencies
echo "Installing polly-ios dependencies..."
cd polly-ios
npm install

# 4. Pod install
if [ -d "ios" ]; then
  echo "Installing CocoaPods..."
  cd ios && pod install && cd ..
fi

# 5. Verify critical packages
echo "Verifying critical packages..."
MISSING=0
for pkg in zustand react-native-mmkv expo-secure-store expo-haptics expo-sqlite lucide-react-native; do
  if [ ! -d "node_modules/$pkg" ]; then
    echo "  ❌ $pkg not installed"
    MISSING=1
  fi
done
[ $MISSING -eq 1 ] && { echo "Missing packages. Check package.json and re-run npm install."; exit 1; }
echo "✅ Critical packages verified"

# 6. Environment config
cd ..
if [ ! -f "polly-ios/.env.local" ]; then
  cat > polly-ios/.env.local << 'EOF'
EXPO_PUBLIC_GATEWAY_URL=http://localhost:18789
# EXPO_PUBLIC_GATEWAY_TOKEN=your_auth_token_here
EOF
  echo "⚠️  Edit polly-ios/.env.local with your gateway auth token before running."
fi

echo ""
echo "=== Setup Complete ==="
echo "Next: cd polly-ios && npx expo start --ios"
