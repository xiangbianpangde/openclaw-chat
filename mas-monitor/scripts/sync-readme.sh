#!/bin/bash
# MAS README 自动同步脚本
# 当 MAS 库更新时，检查并创建 README

set -e

MAS_REPO="xiangbianpangde/MAS"
WORKSPACE="/root/.openclaw/workspace-taizi/mas-monitor"
MAS_DIR="/tmp/MAS"

echo "🔄 MAS README 自动同步检查"
echo "=========================="

# 检查 GitHub Token
if [ -z "$GH_TOKEN" ]; then
    echo "⚠️  GH_TOKEN 未配置，跳过同步"
    exit 0
fi

# 克隆/更新 MAS 仓库
if [ -d "$MAS_DIR/.git" ]; then
    cd "$MAS_DIR"
    git fetch origin
else
    git clone "https://$GH_TOKEN@github.com/$MAS_REPO.git" "$MAS_DIR"
    cd "$MAS_DIR"
    git config user.email "mas-monitor@openclaw.local"
    git config user.name "MAS Monitor"
fi

# 检查 README 是否存在
cd "$MAS_DIR"
if [ ! -f "README.md" ]; then
    echo "⚠️  README.md 不存在，创建中..."
    cp "$WORKSPACE/MAS_README.md" "$MAS_DIR/README.md"
    
    git add README.md
    git commit -m "docs: 自动创建 README - MAS Monitor Agent

由自动同步系统创建，包含:
- 项目核心理念
- OODA Evolution Loop
- 快速启动指南
- 免责声明"
    
    git push origin main
    echo "✅ README.md 已创建并推送"
else
    echo "✅ README.md 已存在，无需创建"
    
    # 可选：检查 README 内容是否需要更新
    # 这里可以添加内容对比逻辑
fi

echo ""
echo "=========================="
echo "同步检查完成"
