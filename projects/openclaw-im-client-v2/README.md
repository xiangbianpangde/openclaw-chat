# OpenClaw IM Client v2.0

官方 Flutter 客户端 - 直连 OpenClaw Gateway WebSocket 协议

## 核心功能

- ✅ **登录认证** - Gateway 地址配置、Token 输入、Agent 选择
- ✅ **聊天功能** - WebSocket 连接、消息收发、Agent 切换
- ✅ **内置浏览器** - WebView 集成
- 🚧 **远程桌面** - noVNC 集成（待完善）

## 技术栈

- **Flutter** 3.x
- **Dart** 3.11+
- **WebSocket**: `web_socket_channel`
- **状态管理**: `flutter_bloc`
- **本地存储**: `Hive` + `flutter_secure_storage`
- **WebView**: `webview_flutter`

## 快速开始

### 环境要求

- Flutter 3.24+
- Dart 3.11+
- Android SDK 26+ (用于 APK 构建)

### 安装依赖

```bash
flutter pub get
```

### 运行应用

```bash
flutter run
```

### 构建 APK

```bash
flutter build apk --release
```

输出位置：`build/app/outputs/flutter-apk/app-release.apk`

## 项目结构

```
lib/
├── main.dart                      # 应用入口
├── app/
│   └── app.dart                   # 应用配置
├── features/
│   ├── auth/                      # 认证模块
│   │   └── presentation/
│   │       ├── auth_bloc.dart
│   │       └── login_screen.dart
│   ├── chat/                      # 聊天模块
│   │   └── presentation/
│   │       ├── chat_bloc.dart
│   │       └── chat_screen.dart
│   ├── browser/                   # 浏览器模块
│   │   └── browser_screen.dart
│   └── remote_desktop/            # 远程桌面模块
│       └── remote_desktop_screen.dart
├── core/
│   ├── websocket/
│   │   └── websocket_service.dart # WebSocket 服务（Gateway 协议）
│   └── storage/
│       └── storage_service.dart   # 本地存储服务
└── shared/
    └── theme/
        └── app_theme.dart         # 主题配置
```

## Gateway WebSocket 协议

### 连接

```
ws://<gateway-host>:18789
```

### 认证消息

```json
{
  "type": "auth.token",
  "payload": {
    "token": "<your_token>"
  }
}
```

### 创建会话

```json
{
  "type": "session.create",
  "payload": {
    "agent": "<agent_name>"
  }
}
```

### 发送消息

```json
{
  "type": "session.message",
  "sessionId": "<session_id>",
  "content": "<message_content>"
}
```

### 获取 Agent 列表

```json
{
  "type": "node.list"
}
```

### 心跳

```json
{
  "type": "ping",
  "payload": {
    "timestamp": 1234567890
  }
}
```

## 配置说明

### Gateway 地址

默认：`ws://localhost:18789`

可在登录页面修改。

### Token

从 OpenClaw Gateway 获取的认证 Token。

支持自动登录（勾选"自动登录"后保存 Token）。

## 开发计划

### Week 1-2: 基础架构 ✅

- [x] 项目脚手架
- [x] WebSocket 服务层
- [x] 存储服务
- [x] 登录页面
- [x] 聊天页面基础

### Week 3-4: 核心功能

- [ ] WebSocket 协议完整实现
- [ ] 消息历史缓存
- [ ] Agent 列表动态获取
- [ ] 连接状态监控（SLA）

### Week 5-6: 增强功能

- [ ] 图片/文件传输
- [ ] 消息已读状态
- [ ] 推送通知

### Week 7: 浏览器 + 远程桌面

- [ ] noVNC 资源集成
- [ ] VNC 连接管理

### Week 8-9: 测试 + 发布

- [ ] 单元测试
- [ ] 真机测试
- [ ] GitHub Release

## SLA 监控指标

| 指标 | 目标值 |
|------|--------|
| 连接成功率 | ≥99.9% |
| 消息延迟 P99 | <200ms |
| 断线率 | <0.1%/小时 |
| 重连成功率 | ≥99.5% |

## 已知问题

1. **noVNC 集成** - 需要将 noVNC 静态资源打包到 assets
2. **VNC Server** - 需要额外部署 VNC Server

## 构建产物

- **APK**: `build/app/outputs/flutter-apk/app-release.apk`
- **源代码**: GitHub 仓库

## 许可证

MIT License

---

**OpenClaw Team** © 2026
