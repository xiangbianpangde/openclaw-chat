# OpenClaw Chat

基于 OpenIM 的专用聊天客户端，集成 OpenClaw 可视化管理界面。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)](https://flutter.dev)
[![OpenIM](https://img.shields.io/badge/OpenIM-Latest-green)](https://openim.io)

## 功能特性

- 🔐 **OpenClaw 可视化管理** — 扫码登录、状态监控、任务管理
- 💬 **即时通讯** — 基于 OpenIM 的企业级聊天功能
- 🌐 **内嵌浏览器** — WebView 访问 OpenClaw 管理后台
- 🖥️ **远程桌面** — noVNC 集成，服务器可视化操作
- 🤖 **AI 助手** — 集成 OpenClaw 多 Agent 系统

## 项目结构

```
openclaw-chat/
├── README.md
├── docs/
│   ├── deployment.md          # 部署指南
│   └── openclaw-integration.md # OpenClaw 对接文档
├── server/
│   ├── docker-compose.yml     # 服务编排
│   ├── scripts/
│   │   └── init.sh           # 初始化脚本
│   └── openclaw-extension/
│       └── index.js          # OpenIM 集成扩展
├── client/
│   └── openclaw_chat/
│       ├── lib/
│       │   ├── main.dart
│       │   ├── screens/
│       │   │   ├── home_screen.dart
│       │   │   ├── login_screen.dart
│       │   │   └── chat_screen.dart
│       │   └── services/
│       │       └── openim_service.dart
│       └── pubspec.yaml
└── integration/
    └── openclaw-config.yml   # OpenClaw 对接配置
```

## 快速开始

### 服务器要求

- **CPU**: 2 核
- **内存**: 4GB
- **存储**: 20GB
- **系统**: Ubuntu 20.04+ / Debian 11+
- **软件**: Docker 20+, Docker Compose 2+

### 1. 部署服务端

```bash
# 克隆仓库
git clone https://github.com/xiangbianpangde/openclaw-chat.git
cd openclaw-chat

# 设置服务器 IP（替换为你的公网 IP）
export OPENIM_IP="38.226.195.166"

# 运行初始化脚本
cd server
./scripts/init.sh
```

初始化完成后，访问：
- **OpenIM Web**: http://38.226.195.166:11001
- **noVNC**: http://38.226.195.166:6080
- **MinIO Console**: http://38.226.195.166:9001

### 2. 配置 OpenClaw 对接

编辑 `server/openclaw-extension/config.json`:

```json
{
  "serverUrl": "http://localhost:10002",
  "botUserId": "openclaw_bot",
  "adminToken": "YOUR_ADMIN_TOKEN",
  "openclawUrl": "http://localhost:18789"
}
```

启动扩展服务:

```bash
cd server/openclaw-extension
npm install
node index.js
```

### 3. 编译客户端

```bash
cd client/openclaw_chat

# 安装依赖
flutter pub get

# 编译 Android APK
flutter build apk --release

# 编译 iOS
flutter build ios --release
```

### 4. 登录测试

1. 打开 App，输入服务器地址
2. 使用 OpenIM Web 后台创建的账号登录
3. 与 `OpenClaw 助手` 对话测试

## 可用命令

在聊天中发送以下命令：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/scan` | 获取扫码登录二维码 |
| `/status` | 查看系统状态 |
| `/desktop` | 获取远程桌面地址 |

## API 参考

### OpenIM API

```bash
# 获取用户 Token
curl -X POST http://SERVER_IP:10002/auth/user_token \
  -H "Content-Type: application/json" \
  -d '{"userID":"admin","secret":"openIM123"}'

# 发送消息
curl -X POST http://SERVER_IP:10002/msg/send_msg \
  -H "Content-Type: application/json" \
  -H "operationID: 123456" \
  -H "token: YOUR_TOKEN" \
  -d '{
    "recvID": "user123",
    "sendID": "openclaw_bot",
    "contentType": 101,
    "content": "{\"content\":\"Hello\"}",
    "sessionType": 1
  }'
```

### Webhook 回调

OpenClaw 扩展接收 OpenIM Webhook:

```bash
POST /webhook/openim
Content-Type: application/json

{
  "command": "afterRecvMsg",
  "data": {
    "sendID": "user123",
    "recvID": "openclaw_bot",
    "content": "{\"content\":\"/help\"}",
    "contentType": 101
  }
}
```

## 开发

### 添加新功能

1. **服务端扩展**: `server/openclaw-extension/`
2. **客户端页面**: `client/openclaw_chat/lib/screens/`
3. **API 服务**: `client/openclaw_chat/lib/services/`

### 调试

```bash
# 查看服务端日志
docker logs openclaw-server -f

# 查看扩展服务日志
cd server/openclaw-extension
DEBUG=* node index.js

# 客户端调试
flutter run --verbose
```

## 常见问题

### Q: 消息发送失败？

检查：
1. OpenIM Server 是否运行：`docker ps | grep openim`
2. Bot 账号是否创建
3. Token 是否正确

### Q: 无法连接服务器？

检查防火墙：
```bash
sudo ufw allow 10001:10010/tcp
sudo ufw allow 11001/tcp
sudo ufw allow 6080/tcp
```

### Q: 如何重置管理员密码？

```bash
docker exec openclaw-mongo mongosh \
  -u openim -p openim123 \
  --eval "db.user.updateOne({userID:'admin'}, {\$set:{password:'new_password'}})"
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- **GitHub**: https://github.com/xiangbianpangde/openclaw-chat
- **OpenClaw**: https://github.com/openclaw/openclaw
- **OpenIM**: https://github.com/openimsdk/open-im-server
