#!/bin/bash
# Continuous testing runner for OpenClaw IM
# Runs tests continuously and auto-commits results

set -e

WORKSPACE="/root/.openclaw/workspace-taizi"
AUTOMATION_DIR="$WORKSPACE/automation"
REPORTS_DIR="$AUTOMATION_DIR/reports"
LOGS_DIR="$AUTOMATION_DIR/logs"
APK_PATH="$WORKSPACE/projects/openclaw-im-client-v2/build/app/outputs/flutter-apk/app-release.apk"

# Environment
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH="$PATH:/opt/android-sdk/platform-tools:/opt/android-sdk/emulator"

# Create directories
mkdir -p "$REPORTS_DIR" "$LOGS_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGS_DIR/runner.log"
}

# Start Appium if not running
start_appium() {
    if ! pgrep -f "appium" > /dev/null; then
        log "🚀 Starting Appium server..."
        export ANDROID_HOME=/opt/android-sdk
        export ANDROID_SDK_ROOT=/opt/android-sdk
        nohup node /root/.nvm/versions/node/v22.22.1/bin/appium --address 127.0.0.1 --port 4723 > /tmp/appium.log 2>&1 &
        sleep 5
        # Verify Appium is running
        if curl -s http://127.0.0.1:4723/status > /dev/null; then
            log "✅ Appium started successfully"
        else
            log "❌ Appium failed to start"
            return 1
        fi
    else
        log "✅ Appium already running"
    fi
}

# Start emulator if not running
start_emulator() {
    if ! pgrep -f "qemu-system-x86_64" > /dev/null; then
        log "🚀 Starting Android emulator..."
        emulator -avd test_device_small -no-audio -no-window &
        sleep 30
        adb wait-for-device
        sleep 10
        log "✅ Emulator started"
    else
        log "✅ Emulator already running"
    fi
}

# Install APK if needed
install_apk() {
    if ! adb shell pm list packages | grep -q "io.openclaw.openclaw_im_client"; then
        log "📦 Installing APK..."
        adb install -r "$APK_PATH" 2>&1 | tail -5
        log "✅ APK installed"
    else
        log "✅ APK already installed"
    fi
}

# Run tests
run_tests() {
    log "🧪 Running tests..."
    cd "$AUTOMATION_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    pytest tests/test_openclaw_im.py -v --tb=line --html="$REPORTS_DIR/test_report_$TIMESTAMP.html" 2>&1 | tee "$LOGS_DIR/test_$TIMESTAMP.log"
    
    # Update latest report symlink
    cp "$REPORTS_DIR/test_report_$TIMESTAMP.html" "$REPORTS_DIR/test_report.html"
    
    log "📊 Test report saved to $REPORTS_DIR/test_report_$TIMESTAMP.html"
}

# Auto-commit
auto_commit() {
    log "💾 Committing changes to GitHub..."
    cd "$WORKSPACE"
    bash automation/scripts/auto-commit.sh
}

# Main loop
main() {
    log "🔄 Starting continuous testing runner..."
    
    # Setup
    start_appium
    start_emulator
    install_apk
    
    # Run tests and auto-commit in loop
    while true; do
        run_tests
        auto_commit
        
        # Wait 5 minutes before next run
        log "⏳ Waiting 5 minutes before next test run..."
        sleep 300
    done
}

# Run main
main
