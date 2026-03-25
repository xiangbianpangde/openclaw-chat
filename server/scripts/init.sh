#!/bin/bash
# OpenClaw Chat - 初始化脚本
set -euo pipefail

echo "🚀 OpenClaw Chat 初始化..."

# 检查环境变量
OPENIM_IP="${OPENIM_IP:-$(hostname -I | awk '{print $1}')}"
export OPENIM_IP

echo "📍 服务器 IP: $OPENIM_IP"

# 创建必要目录
mkdir -p data/{mongo,redis,minio,openim/logs,openim/config}

# 生成随机密码（首次运行）
if [ ! -f .env ]; then
    echo "🔐 生成初始配置..."
    cat > .env << ENVEOF
OPENIM_IP=$OPENIM_IP
MONGO_PASSWORD=$(openssl rand -base64 16)
REDIS_PASSWORD=$(openssl rand -base64 16)
MINIO_PASSWORD=$(openssl rand -base64 16)
OPENIM_ADMIN_TOKEN=$(openssl rand -hex 32)
ENVEOF
    echo "✅ 配置文件已生成：.env"
fi

# 加载环境变量
source .env

echo "📦 启动服务..."
docker compose up -d

echo "⏳ 等待服务就绪..."
sleep 10

# 创建 OpenClaw 机器人账号
echo "🤖 创建 OpenClaw 机器人账号..."
curl -s -X POST "http://$OPENIM_IP:10002/user/register" \
  -H "Content-Type: application/json" \
  -H "operationID: $(date +%s)" \
  -d "{
    \"userID\": \"openclaw_bot\",
    \"nickname\": \"OpenClaw 助手\",
    \"faceURL\": \"https://avatars.githubusercontent.com/u/123456\",
    \"ex\": \"OpenClaw 官方机器人\"
  }" || echo "⚠️  账号可能已存在"

echo ""
echo "✅ 初始化完成！"
echo ""
echo "📋 服务状态:"
echo "  - OpenIM API:    http://$OPENIM_IP:10002"
echo "  - OpenIM Web:    http://$OPENIM_IP:11001"
echo "  - noVNC:         http://$OPENIM_IP:6080"
echo "  - MinIO Console: http://$OPENIM_IP:9001"
echo ""
echo "🔑 管理员 Token: $OPENIM_ADMIN_TOKEN"
echo ""
echo "📱 下一步:"
echo "  1. 编译 Flutter 客户端"
echo "  2. 配置 OpenClaw 对接"
echo "  3. 扫码登录测试"
