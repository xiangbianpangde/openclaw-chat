#!/bin/bash

# OpenClaw Chat 服务器初始化脚本
# 适用于 Ubuntu 20.04+ / Debian 11+

set -e

echo "========================================"
echo "  OpenClaw Chat 服务器初始化"
echo "========================================"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. 更新系统
echo ""
echo ">>> 更新系统..."
apt update && apt upgrade -y
print_step "系统更新完成"

# 2. 安装 Docker
echo ""
echo ">>> 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    print_step "Docker 安装完成"
else
    print_step "Docker 已安装: $(docker --version)"
fi

# 3. 安装 Docker Compose
echo ""
echo ">>> 检查 Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo "安装 Docker Compose 插件..."
    apt install docker-compose-plugin -y
    print_step "Docker Compose 安装完成"
else
    print_step "Docker Compose 已安装: $(docker compose version)"
fi

# 4. 获取服务器 IP
echo ""
echo ">>> 检测服务器 IP..."
SERVER_IP=$(curl -s ifconfig.me || curl -s ip.sb || echo "")
if [ -z "$SERVER_IP" ]; then
    print_warn "无法自动检测 IP，请手动输入"
    read -p "请输入服务器公网 IP: " SERVER_IP
fi
print_step "服务器 IP: $SERVER_IP"

# 5. 配置防火墙
echo ""
echo ">>> 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow ssh
    ufw allow 10001:10100/tcp
    ufw allow 11001:11002/tcp
    ufw allow 5900:5901/tcp
    ufw allow 6080:6081/tcp
    ufw allow 9000:9001/tcp
    ufw reload
    print_step "防火墙配置完成"
else
    print_warn "ufw 未安装，跳过防火墙配置"
fi

# 6. 创建环境变量文件
echo ""
echo ">>> 创建环境变量..."
cat > .env << EOF
# OpenClaw Chat 环境配置
# 生成时间: $(date)

# 服务器 IP
OPENIM_IP=${SERVER_IP}
MINIO_EXTERNAL_IP=${SERVER_IP}

# MongoDB
MONGO_USERNAME=openim
MONGO_PASSWORD=openim123_$(openssl rand -hex 4)

# Redis
REDIS_PASSWORD=redis_$(openssl rand -hex 4)

# MinIO
MINIO_ROOT_USER=openim
MINIO_ROOT_PASSWORD=openim123_$(openssl rand -hex 4)

# VNC 密码
VNC_PASSWORD=openclaw_$(openssl rand -hex 3)
EOF
print_step "环境变量已保存到 .env 文件"

# 7. 创建数据目录
echo ""
echo ">>> 创建数据目录..."
mkdir -p /data/openclaw/{mongo,redis,minio,logs,config}
print_step "数据目录创建完成"

# 8. 系统优化（针对 4GB 内存）
echo ""
echo ">>> 系统优化..."
# 增加 swap（如果不存在）
if [ ! -f /swapfile ]; then
    print_step "创建 2GB swap..."
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
else
    print_step "Swap 已存在"
fi

# 调整 swappiness
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf

print_step "系统优化完成"

# 完成
echo ""
echo "========================================"
echo -e "${GREEN}初始化完成！${NC}"
echo "========================================"
echo ""
echo "下一步："
echo "1. 检查 .env 文件中的配置"
echo "2. 运行: docker compose up -d"
echo "3. 访问管理后台: http://${SERVER_IP}:11001"
echo ""
echo "重要：请保存以下密码"
cat .env | grep PASSWORD