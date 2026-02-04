#!/bin/bash
# Create app icons for Polly
# Requires: ImageMagick (brew install imagemagick)

ASSETS_DIR="$(dirname "$0")/../assets"
mkdir -p "$ASSETS_DIR"

# Create a simple parrot emoji placeholder icon
# In production, replace with actual icon file

# Create iconset directory
ICONSET="$ASSETS_DIR/icon.iconset"
mkdir -p "$ICONSET"

# Generate placeholder icon using sips (macOS built-in)
# This creates a simple colored square - replace with real icon

cat > "$ASSETS_DIR/icon.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#e94560"/>
      <stop offset="100%" style="stop-color:#c678dd"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="80" fill="url(#bg)"/>
  <text x="256" y="340" font-size="280" text-anchor="middle" fill="white">🦜</text>
</svg>
EOF

echo "Created placeholder icon.svg in $ASSETS_DIR"
echo ""
echo "To create proper macOS icons:"
echo "1. Replace icon.svg with your actual icon"
echo "2. Use an online tool or Sketch/Figma to export to .icns"
echo "3. Or use iconutil:"
echo "   iconutil -c icns $ICONSET -o $ASSETS_DIR/icon.icns"

# Create simple tray icon (16x16 template)
cat > "$ASSETS_DIR/tray-icon.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <text x="8" y="13" font-size="14" text-anchor="middle">🦜</text>
</svg>
EOF

echo "Created tray-icon.svg"
