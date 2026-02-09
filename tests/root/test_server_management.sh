#!/bin/bash
# Test script to verify server management improvements

echo "=== Testing Polly Server Management ==="
echo ""

echo "1. Starting Electron app..."
cd /Users/brettgershon/polly/electron-app

# Start in background and capture output
npm start > /tmp/polly-test.log 2>&1 &
APP_PID=$!

echo "   App started with PID: $APP_PID"
echo ""

echo "2. Waiting for server to start (15 seconds)..."
sleep 15

echo ""
echo "3. Checking if server is running..."
if curl -s http://localhost:11436/health | grep -q '"status":"ok"'; then
    echo "   ✅ Server is running and responding"
else
    echo "   ❌ Server is not responding"
fi

echo ""
echo "4. Checking processes..."
echo "   Electron processes:"
ps aux | grep -E "electron|Electron" | grep polly | grep -v grep | awk '{print "      PID", $2, "-", $11, $12, $13}'

echo ""
echo "   Server processes:"
ps aux | grep uvicorn | grep -v grep | awk '{print "      PID", $2, "(parent", $3") -", $11, $12, $13, $14}'

echo ""
echo "5. Recent log output:"
tail -20 /tmp/polly-test.log

echo ""
echo "=== Test Complete ==="
echo ""
echo "To stop: kill $APP_PID"
echo "Full logs: tail -f /tmp/polly-test.log"
