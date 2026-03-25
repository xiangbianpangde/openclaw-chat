# OpenClaw Chat 🦞

> **这是一个公开的开源库** - 任何人都可以免费使用

基于 OpenIM 的企业级聊天客户端，集成 OpenClaw AI 多 Agent 系统。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)](https://flutter.dev)
[![OpenIM](https://img.shields.io/badge/OpenIM-Latest-green)](https://openim.io)
[![Stars](https://img.shields.io/github/stars/xiangbianpangde/openclaw-chat)](https://github.com/xiangbianpangde/openclaw-chat/stargazers)

---

## 🚀 快速开始

### 1. 部署服务端（5 分钟）

```bash
# SSH 登录你的服务器
ssh root@YOUR_SERVER_IP

# 克隆项目
git clone https://github.com/xiangbianpangde/openclaw-chat.git
cd openclaw-chat

# 设置服务器 IP（替换为你的公网 IP）
export OPENIM_IP="你的服务器 IP"

# 一键部署
cd server && ./scripts/init.sh
```

**部署完成后访问：**
- 🌐 OpenIM Web: `http://YOUR_IP:11001`
- 🖥️ noVNC: `http://YOUR_IP:6080`
- 📊 Edict 看板：`http://YOUR_IP:7891`

### 2. 创建账号

访问 `http://YOUR_IP:11001` → 用户管理 → 创建用户

### 3. 下载客户端

**Android:**
```bash
# 方式 1：直接下载 APK
访问：https://github.com/xiangbianpangde/openclaw-chat/releases

# 方式 2：自行编译
cd client/openclaw_chat
flutter pub get
flutter build apk --release
```

**iOS:**
```bash
cd client/openclaw_chat
flutter build ios --release
```

**Web 版（无需安装）:**
```
http://YOUR_IP:8080
```

---

## 📱 功能特性

### 即时通讯
- ✅ 单聊/群聊
- ✅ 文本/图片/文件
- ✅ 消息已读回执
- ✅ 历史消息同步

### AI 集成
- 🤖 OpenClaw 多 Agent 系统
- 🧠 11 个专用 AI 助手
- 💬 自然语言对话
- 🔧 命令支持（/help, /scan, /status）

### 管理功能
- 📊 实时任务看板
- 👥 用户管理后台
- 🖥️ 远程桌面访问
- 📈 Token 使用统计

---

## 🏗️ 架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Flutter App    │◄───►│  OpenIM Server  │◄───►│  OpenClaw Bot   │
│  (Android/iOS)  │     │  (消息服务)      │     │  (AI 助手)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  11 AI Agents   │
                                              │  - 太子          │
                                              │  - 中书省        │
                                              │  - 门下省        │
                                              │  - 尚书省        │
                                              │  - 六部          │
                                              └─────────────────┘
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [部署指南](docs/deployment.md) | 完整部署步骤 |
| [OpenClaw 集成](docs/openclaw-integration.md) | AI 对接文档 |
| [API 参考](docs/api.md) | REST API 文档 |

---

## 🛠️ 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENIM_IP` | 服务器 IP | 自动获取 |
| `MONGO_PASSWORD` | MongoDB 密码 | 随机生成 |
| `REDIS_PASSWORD` | Redis 密码 | 随机生成 |
| `OPENIM_ADMIN_TOKEN` | 管理员 Token | 随机生成 |

### 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 10001-10010 | OpenIM | 消息服务 |
| 11001 | OpenIM Web | 管理后台 |
| 6080 | noVNC | 远程桌面 |
| 7891 | Edict | OpenClaw 看板 |
| 27017 | MongoDB | 数据库 |
| 6379 | Redis | 缓存 |
| 9000-9001 | MinIO | 对象存储 |

---

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker compose up -d

# 停止服务
docker compose down

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f openclaw-server

# 重启服务
docker compose restart
```

### 用户管理

```bash
# 创建用户
curl -X POST "http://$OPENIM_IP:10002/user/register" \
  -H "Content-Type: application/json" \
  -d '{"userID":"user001","nickname":"测试用户","secret":"123456"}'

# 删除用户
curl -X POST "http://$OPENIM_IP:10002/user/delete" \
  -H "Content-Type: application/json" \
  -d '{"userID":"user001"}'

# 获取用户列表
curl -X POST "http://$OPENIM_IP:10002/user/get_page_users" \
  -H "Content-Type: application/json" \
  -d '{"pageNumber":1,"showNumber":10}'
```

### 消息测试

```bash
# 发送测试消息
curl -X POST "http://$OPENIM_IP:10002/msg/send_msg" \
  -H "Content-Type: application/json" \
  -H "operationID: 123456" \
  -H "token: YOUR_TOKEN" \
  -d '{
    "recvID": "user001",
    "sendID": "openclaw_bot",
    "contentType": 101,
    "content": "{\"content\":\"Hello\"}",
    "sessionType": 1
  }'
```

---

## ❓ 常见问题

### Q: 服务启动失败？

```bash
# 检查 Docker 状态
docker compose ps

# 查看详细日志
docker compose logs -f

# 清理重建
docker compose down
docker compose up -d
```

### Q: 无法访问 Web 界面？

```bash
# 检查防火墙
sudo ufw status
sudo ufw allow 11001/tcp

# 检查服务
curl http://localhost:11001
```

### Q: 如何备份数据？

```bash
# 备份 MongoDB
docker exec openclaw-mongo mongodump --out /backup

# 备份配置文件
tar -czf backup.tar.gz server/data .env
```

### Q: 如何升级？

```bash
# 拉取最新代码
git pull

# 更新镜像
docker compose pull

# 重启服务
docker compose down
docker compose up -d
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 📞 联系方式

- **GitHub**: https://github.com/xiangbianpangde/openclaw-chat
- **OpenClaw**: https://github.com/openclaw/openclaw
- **OpenIM**: https://github.com/openimsdk/open-im-server
- **Discord**: 加入 OpenClaw 社区

---

## 🙏 致谢

感谢以下开源项目：

- [OpenIM](https://github.com/openimsdk/open-im-server) - 企业级即时通讯
- [OpenClaw](https://github.com/openclaw/openclaw) - AI 多 Agent 系统
- [Flutter](https://flutter.dev) - 跨平台 UI 框架
- [Docker](https://docker.com) - 容器化部署

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
