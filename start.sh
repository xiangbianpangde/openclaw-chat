#!/bin/bash
# OpenClaw IM - Main Entry Point for Self-Cycling Development
# Usage: ./start.sh [--continuous] [--skip-build] [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOMATION_DIR="$SCRIPT_DIR/automation"
WORKSPACE="$SCRIPT_DIR"

# Environment setup
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH="/opt/flutter/bin:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:$PATH"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     OpenClaw IM Self-Cycling Development Engine          ║"
echo "║     自循环开发引擎 - 无需人工干预                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo "  - Gateway: ws://38.226.195.166:18789"
echo "  - Repository: https://github.com/xiangbianpangde/openclaw-im-client"
echo "  - Test Cases: 24"
echo "  - Performance Targets:"
echo "    * Startup: <3s"
echo "    * Memory: <200MB"
echo "    * Message Delay: <500ms"
echo ""

# Check dependencies
check_deps() {
    local missing=0
    
    command -v flutter >/dev/null 2>&1 || { echo "❌ Flutter not found"; missing=1; }
    command -v adb >/dev/null 2>&1 || { echo "❌ Android ADB not found"; missing=1; }
    command -v appium >/dev/null 2>&1 || { echo "❌ Appium not found"; missing=1; }
    command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not found"; missing=1; }
    
    if [ $missing -eq 1 ]; then
        echo ""
        echo "Missing dependencies. Please install them first."
        exit 1
    fi
    
    echo "✅ All dependencies found"
}

# Initialize development environment
init_env() {
    echo ""
    echo "Initializing development environment..."
    
    # Create necessary directories
    mkdir -p "$AUTOMATION_DIR/reports"
    mkdir -p "$AUTOMATION_DIR/logs"
    
    # Check Flutter
    flutter doctor -v || true
    
    echo "Environment ready"
}

# Main execution
main() {
    check_deps
    init_env
    
    echo ""
    echo "Starting first development cycle..."
    echo ""
    
    # Run the development cycle
    bash "$AUTOMATION_DIR/scripts/dev_cycle.sh"
}

main "$@"
