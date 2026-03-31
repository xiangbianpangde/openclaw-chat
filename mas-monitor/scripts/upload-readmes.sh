#!/bin/bash
# MAS README 上传脚本
# 需要配置 GitHub Token 后运行

set -e

MAS_REPO="xiangbianpangde/MAS"
MAS_ANALYSIS_REPO="xiangbianpangde/MAS-Analysis"
WORKSPACE="/root/.openclaw/workspace-taizi/mas-monitor"

echo "🚀 MAS README 上传脚本"
echo "========================"

# 检查 GitHub Token
if [ -z "$GH_TOKEN" ]; then
    echo "❌ 错误：GH_TOKEN 未配置"
    echo ""
    echo "请先配置 GitHub Token:"
    echo "  export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx"
    echo ""
    echo "创建 Token: https://github.com/settings/tokens"
    echo "需要权限：repo, read:org"
    exit 1
fi

echo "✅ GitHub Token 已配置"

# 克隆/更新 MAS 仓库
echo ""
echo "📦 处理 MAS 仓库..."
MAS_DIR="/tmp/MAS"

if [ -d "$MAS_DIR/.git" ]; then
    echo "  更新现有仓库..."
    cd "$MAS_DIR"
    git pull origin main
else
    echo "  克隆仓库..."
    git clone "https://$GH_TOKEN@github.com/$MAS_REPO.git" "$MAS_DIR"
    cd "$MAS_DIR"
    git config user.email "mas-monitor@openclaw.local"
    git config user.name "MAS Monitor"
fi

# 复制 README 到 MAS 仓库
echo "  复制 README.md..."
cp "$WORKSPACE/MAS_README.md" "$MAS_DIR/README.md"

# 提交并推送
cd "$MAS_DIR"
if ! git diff --quiet README.md; then
    git add README.md
    git commit -m "docs: 更新 README - AutoMAS 项目说明

- 添加三零原则说明
- 添加 OODA Evolution Loop 流程图
- 添加快速启动指南
- 添加免责声明

Powered by MAS Monitor Agent"
    git push origin main
    echo "  ✅ MAS README 已推送"
else
    echo "  ⏭️  README 无变更，跳过"
fi

# 克隆/更新 MAS-Analysis 仓库
echo ""
echo "📦 处理 MAS-Analysis 仓库..."
MAS_ANALYSIS_DIR="/tmp/MAS-Analysis"

if [ -d "$MAS_ANALYSIS_DIR/.git" ]; then
    echo "  更新现有仓库..."
    cd "$MAS_ANALYSIS_DIR"
    git pull origin main
else
    echo "  克隆仓库..."
    git clone "https://$GH_TOKEN@github.com/$MAS_ANALYSIS_REPO.git" "$MAS_ANALYSIS_DIR"
    cd "$MAS_ANALYSIS_DIR"
    git config user.email "mas-monitor@openclaw.local"
    git config user.name "MAS Monitor"
fi

# 复制 README 到 MAS-Analysis 仓库
echo "  复制 README.md..."
cp "$WORKSPACE/MAS_ANALYSIS_README.md" "$MAS_ANALYSIS_DIR/README.md"

# 提交并推送
cd "$MAS_ANALYSIS_DIR"
if ! git diff --quiet README.md; then
    git add README.md
    git commit -m "docs: 创建 README - MAS 独立分析报告库说明

- 添加报告目录结构说明
- 添加分析内容介绍
- 添加监控配置信息
- 添加使用示例

Powered by MAS Monitor Agent"
    git push origin main
    echo "  ✅ MAS-Analysis README 已推送"
else
    echo "  ⏭️  README 无变更，跳过"
fi

echo ""
echo "========================"
echo "✅ 所有 README 上传完成!"
echo ""
echo "📊 仓库地址:"
echo "  MAS:           https://github.com/$MAS_REPO"
echo "  MAS-Analysis:  https://github.com/$MAS_ANALYSIS_REPO"
