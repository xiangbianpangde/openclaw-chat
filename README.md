# OpenClaw Chat

基于 OpenIM 的专用聊天客户端，集成 OpenClaw 可视化管理界面。

## 功能特性

- 🔐 **OpenClaw 可视化管理** — 扫码登录、状态监控
- 💬 **即时通讯** — 基于 OpenIM 的聊天功能
- 🌐 **内嵌浏览器** — WebView 访问管理后台
- 🖥️ **远程桌面** — noVNC/RustDesk 集成，服务器可视化

## 项目结构

```
openclaw-chat/
├── README.md
├── docs/                    # 文档
│   └── deployment.md        # 部署指南
├── server/                  # 服务器端配置
│   ├── docker-compose.yml  # OpenIM + noVNC 部署
│   └── scripts/            # 初始化脚本
├── client/                  # Flutter 客户端
│   └── openclaw_chat/
└── integration/            # OpenClaw 对接配置
```

## 快速开始

### 服务器要求

- 2核 CPU
- 4GB 内存
- Docker + Docker Compose
- 开放端口：10001-10010, 11001

### 部署步骤

1. 克隆仓库
```bash
git clone https://github.com/YOUR_USERNAME/openclaw-chat.git
cd openclaw-chat
```

2. 启动服务
```bash
cd server
./scripts/init.sh
docker compose up -d
```

3. 访问管理后台
```
http://YOUR_SERVER_IP:11001
```

## 技术栈

- **后端**: OpenIM Server + MongoDB + Redis
- **前端**: Flutter (Android/iOS/Web/Desktop)
- **远程桌面**: noVNC + x11vnc 或 RustDesk
- **AI 对接**: OpenClaw API

## 许可证

MIT License