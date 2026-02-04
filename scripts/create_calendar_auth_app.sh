#!/bin/bash

# Create a temporary app bundle that will request Calendar permission
# App bundles have better luck triggering permission dialogs

APP_NAME="PollyCalendarAuth"
APP_DIR="/tmp/${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "Creating temporary app bundle to request Calendar permission..."

# Clean up old app if exists
rm -rf "${APP_DIR}"

# Create app structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>run</string>
    <key>CFBundleIdentifier</key>
    <string>com.polly.calendarauth</string>
    <key>CFBundleName</key>
    <string>PollyCalendarAuth</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSCalendarsUsageDescription</key>
    <string>Polly needs access to your Calendar to help you search and query your schedule.</string>
</dict>
</plist>
EOF

# Create executable script
cat > "${MACOS_DIR}/run" << 'EOF'
#!/bin/bash
cd /Users/brettgershon/polly
source venv/bin/activate
python scripts/request_calendar_only.py
read -p "Press Enter to close..."
EOF

chmod +x "${MACOS_DIR}/run"

echo "App bundle created at: ${APP_DIR}"
echo "Opening app to trigger permission dialog..."
echo ""

# Open the app
open "${APP_DIR}"

echo "✓ App launched!"
echo ""
echo "You should see:"
echo "  1. A permission dialog for Calendar access"
echo "  2. A terminal window showing the result"
echo ""
echo "After granting permission, the app will close automatically."
