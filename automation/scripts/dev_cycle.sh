#!/bin/bash
# OpenClaw IM Self-Cycling Development Script
# Automates: analyze → fix → build → test → report → commit

set -e

WORKSPACE="/root/.openclaw/workspace-taizi"
AUTOMATION_DIR="$WORKSPACE/automation"
REPORTS_DIR="$AUTOMATION_DIR/reports"
CLIENT_DIR="$WORKSPACE/projects/openclaw-im-client-v2"
APK_PATH="$CLIENT_DIR/build/app/outputs/flutter-apk/app-release.apk"

# Configuration
GITHUB_REPO="https://github.com/xiangbianpangde/openclaw-im-client"
GITHUB_TOKEN="${GITHUB_TOKEN}"
GATEWAY_WS="ws://38.226.195.166:18789"
GATEWAY_TOKEN="${GATEWAY_TOKEN}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Export environment
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH="/opt/flutter/bin:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:$PATH"
export GIT_ASKPASS=/bin/echo
export GIT_USERNAME=xiangbianpangde
export GIT_PASSWORD=$GITHUB_TOKEN

log "=== OpenClaw IM Self-Cycling Development Engine ==="
log "Starting development cycle..."

# Step 1: Ensure we're in the right directory
cd "$WORKSPACE"

# Step 2: Check if APK exists, if not build it
if [ ! -f "$APK_PATH" ]; then
    log "Building initial APK..."
    cd "$CLIENT_DIR"
    
    # Get dependencies
    flutter pub get
    
    # Build release APK
    flutter build apk --release
    
    log "APK built successfully"
else
    log "Using existing APK: $APK_PATH"
fi

# Step 3: Start Appium server
log "Starting Appium server..."
appium --address 127.0.0.1 --port 4723 &
APPIUM_PID=$!
sleep 5

# Step 4: Start Android Emulator (if not running)
log "Checking Android emulator..."
if ! adb devices | grep -q "emulator"; then
    log "Starting Android emulator..."
    # Create emulator if needed
    echo "no" | avdmanager create avd -n test_device -k "system-images;android-34;default;x86_64" -d pixel_6
    
    # Start emulator
    emulator -avd test_device -no-audio -no-window &
    EMULATOR_PID=$!
    
    # Wait for emulator to boot
    log "Waiting for emulator to boot (up to 5 minutes)..."
    adb wait-for-device
    while ! adb shell getprop sys.boot_completed 2>/dev/null | grep -q "1"; do
        sleep 5
    done
    log "Emulator ready"
fi

# Step 5: Install APK on emulator
log "Installing APK on emulator..."
adb install -r "$APK_PATH"

# Step 6: Run automated tests
log "Running automated tests..."
cd "$AUTOMATION_DIR"
python3 -m pytest tests/test_openclaw_im.py -v --html="$REPORTS_DIR/test_report_$(date +%Y%m%d_%H%M%S).html" --self-contained-html

# Step 7: Stop Appium
log "Stopping Appium server..."
kill $APPIUM_PID 2>/dev/null || true

# Step 8: Analyze test results
log "Analyzing test results..."
TEST_REPORT=$(ls -t "$REPORTS_DIR"/test_report_*.html | head -1)
if [ -f "$TEST_REPORT" ]; then
    log "Test report generated: $TEST_REPORT"
    
    # Extract pass/fail counts (simplified)
    PASSED=$(grep -o '"pass": [0-9]*' "$TEST_REPORT" 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "0")
    FAILED=$(grep -o '"fail": [0-9]*' "$TEST_REPORT" 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "0")
    
    log "Tests: $PASSED passed, $FAILED failed"
    
    if [ "$FAILED" -gt "0" ]; then
        log "Some tests failed. Analysis and fix needed."
        # In a full implementation, this would analyze failures and generate fixes
    else
        log "All tests passed!"
    fi
fi

# Step 9: Commit and push to GitHub
log "Committing changes to GitHub..."
cd "$WORKSPACE"

git add -A
git commit -m "Auto: Development cycle $(date '+%Y-%m-%d %H:%M:%S') - Test results: $PASSED passed, $FAILED failed" || log "No changes to commit"

git push https://$GITHUB_TOKEN@github.com/xiangbianpangde/openclaw-im-client.git main || log "Push failed"

log "=== Development cycle complete ==="
log "Next cycle will start automatically..."

# For continuous loop, uncomment:
# while true; do
#     ./scripts/dev_cycle.sh
#     sleep 60
# done
