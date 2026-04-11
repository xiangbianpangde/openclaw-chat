# OpenClaw IM Client v2.0 - 快速启动指南

## 🚀 5 分钟快速开始

### 前置条件

1. **Android 设备或模拟器**
   - Android 8.0 (API 26) 或更高版本
   - 建议：Android 10+ 用于最佳体验

2. **OpenClaw Gateway**
   - 确保 Gateway 服务已启动
   - 默认端口：18789
   - 获取认证 Token

### 方法一：直接安装 APK（推荐）

#### 步骤 1：下载 APK

APK 位置：
```
/root/.openclaw/workspace-taizi/projects/openclaw-im-client-v2/build/app/outputs/flutter-apk/app-release.apk
```

文件大小：约 50 MB

#### 步骤 2：传输到 Android 设备

```bash
# 使用 ADB
adb install app-release.apk

# 或者手动传输到设备后安装
adb push app-release.apk /sdcard/Download/
```

#### 步骤 3：在设备上安装

1. 打开设备文件管理器
2. 找到 `Download/app-release.apk`
3. 点击安装
4. 允许"未知来源"安装（如提示）

### 方法二：从源代码运行

#### 步骤 1：克隆项目

```bash
cd /root/.openclaw/workspace-taizi/projects/openclaw-im-client-v2
```

#### 步骤 2：安装依赖

```bash
export PATH="/opt/flutter/bin:$PATH"
flutter pub get
```

#### 步骤 3：连接设备

```bash
# 列出连接的设备
adb devices

# 确保至少有一个设备显示
```

#### 步骤 4：运行应用

```bash
flutter run --release
```

---

## 📱 使用指南

### 首次启动

1. **配置 Gateway 地址**
   - 默认：`ws://localhost:18789`
   - 如果 Gateway 在远程服务器，填写完整地址，如：`ws://192.168.1.100:18789`

2. **输入 Token**
   - 从 OpenClaw Gateway 获取认证 Token
   - 可勾选"自动登录"保存 Token

3. **点击登录**

### 聊天功能

1. **选择 Agent**
   - 点击右上角人头图标
   - 从列表中选择 Agent

2. **发送消息**
   - 在底部输入框输入消息
   - 点击发送按钮或按回车

3. **查看消息**
   - 消息以气泡形式显示
   - 蓝色气泡：我发送的
   - 灰色气泡：Agent 回复的

### 内置浏览器

1. 点击右上角菜单
2. 选择"内置浏览器"
3. 在地址栏输入网址
4. 支持前进、后退、刷新

### 远程桌面

1. 点击右上角菜单
2. 选择"远程桌面"
3. 点击"+"添加连接
4. 输入 VNC 服务器地址、端口、密码
5. 点击"连接"

**注意：** 远程桌面功能需要：
- noVNC 静态资源打包到 `assets/noVNC/`
- VNC Server 已部署并可访问

---

## 🔧 故障排查

### 无法连接 Gateway

**问题：** 显示"连接失败"或"连接已断开"

**解决方案：**
1. 检查 Gateway 地址是否正确
2. 确认 Gateway 服务已启动
3. 检查网络连接
4. 尝试使用 `ws://` 而非 `wss://`（如果 Gateway 不支持 HTTPS）

```bash
# 检查 Gateway 是否运行
curl ws://localhost:18789

# 查看 Gateway 日志
journalctl -u openclaw-gateway -f
```

### Token 无效

**问题：** 登录时提示"认证失败"

**解决方案：**
1. 确认 Token 正确（从 Gateway 配置中获取）
2. 检查 Token 是否过期
3. 尝试重新生成 Token

### APK 安装失败

**问题：** "解析包时出现问题"

**解决方案：**
1. 确保 Android 版本 ≥ 8.0
2. 允许"未知来源"安装
3. 重新下载 APK 文件

### 应用闪退

**问题：** 启动后立即关闭

**解决方案：**
1. 清除应用数据后重试
2. 卸载后重新安装
3. 查看日志：
   ```bash
   adb logcat | grep openclaw
   ```

---

## 📊 性能指标

### SLA 监控

在应用内查看连接质量：
- 连接成功率：≥99.9%
- 消息延迟 P99：<200ms
- 断线率：<0.1%/小时

### 资源占用

- APK 大小：~50 MB
- 安装后大小：~150 MB
- 内存占用：~100-200 MB
- 冷启动时间：<3 秒（主流设备）

---

## 🛠️ 开发者工具

### 查看日志

```bash
# 实时日志
adb logcat -s flutter

# 过滤 OpenClaw 日志
adb logcat | grep -i openclaw
```

### 热重载开发

```bash
# 开发模式运行（支持热重载）
flutter run

# 按 r 进行热重载
# 按 R 进行热重启
# 按 q 退出
```

### 构建调试版

```bash
flutter build apk --debug
```

### 性能分析

```bash
# 生成性能报告
flutter build apk --profile

# 使用 DevTools
flutter pub global activate devtools
flutter pub global run devtools
```

---

## 📞 获取帮助

### 文档

- 项目 README：`README.md`
- 进度报告：`PROGRESS_REPORT.md`
- 技术方案：`/root/.openclaw/workspace-taizi/proposals/openclaw-im-client-v2-technical-proposal-revised.md`

### 反馈问题

如遇问题，请提供：
1. 设备型号和 Android 版本
2. Gateway 地址和版本
3. 错误截图或日志
4. 复现步骤

---

**OpenClaw Team** © 2026
