#!/bin/bash

# Script to request Calendar and Reminders permissions via AppleScript
# This will trigger macOS system permission dialogs

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "Polly Permission Request Helper"
echo "=========================================="
echo ""
echo "This script will request permissions for:"
echo "  1. Calendar access"
echo "  2. Reminders access"
echo ""
echo "You'll see macOS system dialogs asking you to grant access."
echo "Please click 'OK' or 'Allow' on each dialog."
echo ""
read -p "Press Enter to continue..."

echo ""
echo "🗓️  Requesting Calendar permissions..."
osascript "$SCRIPT_DIR/request_calendar_permission.applescript"

echo ""
echo "✅ Requesting Reminders permissions..."
osascript "$SCRIPT_DIR/request_reminders_permission.applescript"

echo ""
echo "=========================================="
echo "✅ Permission requests complete!"
echo "=========================================="
echo ""
echo "Now checking if Python can access the data..."
echo ""

# Check permissions using the Python script
cd "$SCRIPT_DIR/.."
source venv/bin/activate
python scripts/check_permissions.py

echo ""
echo "If permissions show as 'Authorized', you can now:"
echo "  1. Restart the Polly server"
echo "  2. Click 'Enable' on Calendar and Reminders integrations"
echo ""
