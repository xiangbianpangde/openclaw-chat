#!/bin/bash
# Auto-commit script for OpenClaw IM testing
# Automatically commits and pushes changes to GitHub

set -e

WORKSPACE="/root/.openclaw/workspace-taizi"
GITHUB_TOKEN="${GITHUB_TOKEN:-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}"
REPO="https://github.com/xiangbianpangde/openclaw-im-client"

cd "$WORKSPACE"

# Configure git
git config user.email "testbot@openclaw.ai"
git config user.name "OpenClaw Test Bot"

# Check for changes
if git status --porcelain | grep -q "."; then
    echo "📝 Changes detected, committing..."
    
    # Add automation changes
    git add -f automation/ 2>/dev/null || true
    git add mas-monitor/reports/ 2>/dev/null || true
    
    # Commit if there are staged changes
    if git status --porcelain | grep -q "^M\|^A\|^D"; then
        git commit -m "Auto: 测试进度更新 $(date '+%Y-%m-%d %H:%M')" || echo "No changes to commit"
        
        # Push to GitHub
        echo "🚀 Pushing to GitHub..."
        git push "$REPO" main 2>&1 | tail -5 || echo "Push failed"
        
        echo "✅ Commit and push completed!"
    else
        echo "ℹ️  No staged changes"
    fi
else
    echo "ℹ️  No changes detected"
fi
