# OpenClaw 对接指南

本指南说明如何将 OpenClaw 接入 OpenClaw Chat 系统。

## 架构概览

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Flutter App    │◄───►│  OpenIM Server  │◄───►│  OpenClaw Bot   │
│  (移动客户端)    │     │  (消息服务)      │     │  (机器人账号)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  OpenClaw API   │
                                                │  (本地/远程)    │
                                                └─────────────────┘
```

## 接入方式

### 方式一：OpenIM Webhook（推荐）

OpenIM 支持 Webhook 回调，可以在收到消息时通知 OpenClaw。

#### 1. 配置 OpenIM Webhook

在 OpenIM Server 配置文件中添加：

```yaml
# config/webhooks.yml
webhooks:
  url: "http://openclaw-api:3000/webhook/openim"
  beforeSendMsg:
    enable: false
  afterSendMsg:
    enable: true
  afterRecvMsg:
    enable: true
```

#### 2. OpenClaw 接收 Webhook

在 OpenClaw 中添加 Webhook 接收端点：

```javascript
// openclaw/extensions/openim-webhook/index.js
module.exports = {
  name: 'openim-webhook',
  
  async init() {
    // 注册 webhook 路由
    this.app.post('/webhook/openim', this.handleWebhook.bind(this));
  },
  
  async handleWebhook(req, res) {
    const { command, data } = req.body;
    
    switch (command) {
      case 'afterRecvMsg':
        // 收到消息
        await this.handleMessage(data);
        break;
    }
    
    res.json({ success: true });
  },
  
  async handleMessage(data) {
    const { senderId, receiverId, content, contentType } = data;
    
    // 只处理发给 OpenClaw 机器人的消息
    if (receiverId !== 'openclaw_bot') return;
    
    // 解析命令
    const response = await this.processCommand(senderId, content);
    
    // 发送回复
    await this.sendReply(senderId, response);
  }
};
```

---

### 方式二：OpenIM API 直接调用

OpenClaw 直接使用 OpenIM API 收发消息。

#### 1. 获取管理员 Token

```bash
# 登录获取 token
curl -X POST http://SERVER_IP:10002/auth/user_token \
  -H "Content-Type: application/json" \
  -d '{
    "userID": "admin",
    "secret": "openIM123"
  }'
```

#### 2. OpenClaw 配置

```yaml
# openclaw/config/openim.yml
enabled: true
server_url: "http://SERVER_IP:10002"
admin_token: "YOUR_ADMIN_TOKEN"
bot_user_id: "openclaw_bot"
```

#### 3. 创建机器人账号

```bash
# 注册 OpenClaw 机器人账号
curl -X POST http://SERVER_IP:10002/user/register \
  -H "Content-Type: application/json" \
  -H "operationID: $(date +%s)" \
  -d '{
    "userID": "openclaw_bot",
    "nickname": "OpenClaw",
    "faceURL": "https://example.com/avatar.png"
  }'
```

#### 4. OpenClaw 扩展代码

```javascript
// openclaw/extensions/openim/index.js
const axios = require('axios');

class OpenIMExtension {
  constructor(config) {
    this.config = config;
    this.api = axios.create({
      baseURL: config.server_url,
      headers: {
        'operationID': Date.now().toString(),
        'token': config.admin_token
      }
    });
  }
  
  // 发送消息
  async sendMessage(userId, content) {
    const response = await this.api.post('/msg/send_msg', {
      recvID: userId,
      sendID: this.config.bot_user_id,
      senderPlatformID: 1,
      contentType: 101, // 文本消息
      content: JSON.stringify({ content }),
      sessionType: 1 // 单聊
    });
    return response.data;
  }
  
  // 获取消息列表
  async getMessages(userId, count = 50) {
    const response = await this.api.post('/msg/get_history_msg', {
      userID: userId,
      count
    });
    return response.data.data;
  }
}

module.exports = {
  name: 'openim',
  
  async init(config) {
    this.client = new OpenIMExtension(config);
    
    // 注册命令
    this.registerCommands();
  },
  
  registerCommands() {
    // /scan - 扫码登录
    this.registerCommand('scan', async (ctx) => {
      const qrUrl = await this.generateQRCode(ctx.userId);
      // 发送二维码图片
      await this.client.sendImage(ctx.userId, qrUrl);
    });
    
    // /desktop - 远程桌面
    this.registerCommand('desktop', async (ctx) => {
      const desktopUrl = this.config.novnc_url;
      await this.client.sendMessage(ctx.userId, 
        `远程桌面地址: ${desktopUrl}`);
    });
    
    // /status - 查看状态
    this.registerCommand('status', async (ctx) => {
      const status = await this.getStatus();
      await this.client.sendMessage(ctx.userId, status);
    });
  }
};
```

---

## 消息协议

### 文本消息

```json
{
  "contentType": 101,
  "content": "{\"content\":\"你好\"}"
}
```

### 图片消息

```json
{
  "contentType": 102,
  "content": "{\"sourcePicture\":{\"url\":\"https://...\"}}"
}
```

### 自定义消息（用于 OpenClaw 指令）

```json
{
  "contentType": 101,
  "content": "{\"content\":\"/scan\"}"
}
```

---

## 可视化功能对接

### 扫码登录

当用户在 App 中点击"扫码登录"时：

1. **App** 发送 `/scan` 命令给 OpenClaw Bot
2. **OpenClaw** 生成登录二维码（如 NapCat QQ 登录）
3. **OpenClaw** 发送二维码图片到 App
4. **用户** 在远程桌面中扫码

```
┌─────────────┐    /scan     ┌─────────────┐   生成二维码   ┌─────────────┐
│  Flutter    │ ───────────► │  OpenClaw   │ ────────────► │  QR Image   │
│  App        │ ◄─────────── │  Bot        │ ◄──────────── │             │
└─────────────┘   发送图片    └─────────────┘               └─────────────┘
```

### 远程桌面控制

App 内嵌 WebView 访问 noVNC：

```dart
// Flutter 代码
final novncUrl = 'http://$serverIP:6080/vnc.html';
webViewController.loadRequest(Uri.parse(novncUrl));
```

用户可以在远程桌面中：
- 操作 OpenClaw 管理界面
- 扫描登录二维码
- 查看日志和状态

---

## 部署步骤

### 1. 部署 OpenIM Server

```bash
cd /opt/openim-docker
export OPENIM_IP="YOUR_SERVER_IP"
docker compose up -d
```

### 2. 创建 OpenClaw 机器人账号

```bash
# 使用管理后台创建用户
# 或使用 API 注册
curl -X POST http://SERVER_IP:10002/user/register \
  -H "Content-Type: application/json" \
  -d '{"userID":"openclaw_bot","nickname":"OpenClaw"}'
```

### 3. 配置 OpenClaw

```yaml
# openclaw/config/extensions.yml
extensions:
  - name: openim
    enabled: true
    config:
      server_url: "http://localhost:10002"
      bot_user_id: "openclaw_bot"
```

### 4. 启动 OpenClaw

```bash
openclaw start
```

---

## 测试

### 测试机器人连接

在 App 中打开与 OpenClaw 的对话，发送：

```
/help
```

应该收到 OpenClaw 的帮助信息。

### 测试扫码功能

```
/scan
```

应该收到二维码图片。

---

## 常见问题

### Q: 消息发送失败

检查：
1. OpenIM Server 是否正常运行
2. Bot 账号是否已创建
3. Token 是否正确

### Q: 无法收到消息

检查：
1. Webhook 配置是否正确
2. OpenClaw 是否在运行
3. 防火墙是否允许回调请求

### Q: 远程桌面无法连接

检查：
1. noVNC 服务是否运行
2. 端口是否开放（6080）
3. 服务器是否有桌面环境