# OpenClaw Chat 部署指南

## 目录

1. [服务器准备](#服务器准备)
2. [OpenIM 部署](#openim-部署)
3. [可视化环境部署](#可视化环境部署)
4. [Flutter 客户端](#flutter-客户端)
5. [OpenClaw 对接](#openclaw-对接)

---

## 服务器准备

### 系统要求

- Ubuntu 20.04+ / Debian 11+
- 2核 CPU, 4GB 内存
- 20GB+ 磁盘空间

### 安装 Docker

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
apt install docker-compose-plugin -y

# 验证安装
docker --version
docker compose version
```

### 开放端口

```bash
# OpenIM 服务端口
# 10001 - MsgGateway (WebSocket)
# 10002 - API
# 10003 - User service
# 10004 - Group service
# 10005 - Auth service
# 10006 - Push service
# 10007 - Conversation service
# 10008 - Msg service
# 11001 - Web 管理后台
# 11002 - Chat API

# 防火墙配置 (ufw)
ufw allow 10001:10010/tcp
ufw allow 11001:11002/tcp
ufw allow 5900/tcp  # VNC
ufw reload
```

---

## OpenIM 部署

### 1. 克隆 OpenIM Docker 配置

```bash
cd /opt
git clone https://github.com/openimsdk/openim-docker.git
cd openim-docker
```

### 2. 配置环境变量

```bash
# 编辑 .env 文件
export OPENIM_IP="YOUR_SERVER_IP"
export MINIO_EXTERNAL_IP="YOUR_SERVER_IP"
```

### 3. 精简部署（针对 4GB 内存）

编辑 `docker-compose.yml`，移除不必要的组件：

```yaml
# 保留核心服务
services:
  mongo:
    # MongoDB 配置
  redis:
    # Redis 配置
  openim-server:
    # 核心服务
  openim-chat:
    # 聊天服务
  minio:
    # 文件存储
  
# 移除（节省内存）
# zookeeper
# kafka (使用 Redis 替代消息队列)
```

### 4. 启动服务

```bash
docker compose up -d
```

### 5. 验证部署

```bash
# 检查服务状态
docker compose ps

# 查看日志
docker compose logs -f openim-server
```

访问 `http://YOUR_SERVER_IP:11001` 进入管理后台。

---

## 可视化环境部署

为 OpenClaw 提供可视化界面（扫码登录等）。

### 方案 A：noVNC（推荐，纯 Web）

```bash
cd /opt
mkdir novnc && cd novnc

# docker-compose.yml 见 server/docker-compose.novnc.yml
```

### 方案 B：RustDesk（更流畅）

```bash
# 安装 RustDesk Server
docker run -d --name rustdesk-server \
  -p 21115:21115 -p 21116:21116 -p 21116:21116/udp \
  -p 21118:21118 \
  rustdesk/rustdesk-server-s6:latest
```

---

## Flutter 客户端

### 环境准备

```bash
# 安装 Flutter SDK
cd /opt
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:/opt/flutter/bin"
flutter doctor
```

### 构建应用

```bash
cd client/openclaw_chat
flutter pub get
flutter run
```

---

## OpenClaw 对接

### 配置 Webhook

在 OpenClaw 配置中添加 Webhook：

```yaml
# openclaw config
webhooks:
  - url: http://openim-chat:10009/webhook
    events: [message, login, logout]
```

### 创建机器人账号

在 OpenIM 管理后台创建 OpenClaw 机器人账号，用于自动回复和命令执行。