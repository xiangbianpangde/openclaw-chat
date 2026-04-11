# OpenClaw IM Client v2.0.0+4 发布说明

## 问题修复

### 🐛 网络连接错误修复

**问题描述：**
IM 客户端发送消息时出现网络错误：
```
Connection failed, port = 7891
```

**问题原因：**
- IM 客户端默认配置尝试连接 **18789 端口**（Gateway 直连端口）
- 实际部署中 Gateway 通过 **Nginx 80 端口** 代理访问
- 用户误配置为 7891 端口（Edict 看板端口）导致连接失败

**修复内容：**
1. 更新默认 Gateway 地址从 `ws://localhost:18789` 改为 `ws://YOUR_SERVER_IP/ws`
2. 使用 Nginx 反向代理（80 端口）进行连接
3. 更新界面提示信息，引导用户正确配置

## 代码变更

### 文件：`lib/features/auth/presentation/login_screen.dart`

```dart
// 修改前
_gatewayController.text = savedGateway ?? 'ws://localhost:18789';
hintText: 'ws://localhost:18789',

// 修改后
_gatewayController.text = savedGateway ?? 'ws://YOUR_SERVER_IP/ws';
hintText: 'ws://YOUR_SERVER_IP/ws (通过 Nginx 代理)',
```

### 文件：`pubspec.yaml`

```yaml
# 版本号升级
version: 2.0.0+4
```

## 下载链接

**Android APK:**
```
http://YOUR_SERVER_IP/openclaw/OpenClaw_IM_v2.0.0+4.apk
```

**本地路径：**
```
/var/www/html/openclaw/OpenClaw_IM_v2.0.0+4.apk
```

## 部署说明

1. 用户下载新 APK 覆盖安装
2. 首次登录时 Gateway 地址自动填充为 `ws://YOUR_SERVER_IP/ws`
3. 将 `YOUR_SERVER_IP` 替换为实际服务器 IP 地址
4. 已保存配置的用户不受影响（配置保留）

## 技术细节

### Nginx 配置要求

确保 Nginx 配置包含 WebSocket 代理：

```nginx
location /ws {
    proxy_pass http://localhost:18789;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;
}
```

---

**发布时间：** 2026-03-26 13:12 GMT+8
**尚书省 奉旨执行** 🫡
