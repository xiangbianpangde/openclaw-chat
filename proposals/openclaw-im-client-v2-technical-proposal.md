# 中书省奏折

## 关于开发 OpenClaw IM 客户端 v2 之技术方案

**奏呈：** 皇上陛下  
**呈奏：** 中书省  
**日期：** 2026 年 3 月 25 日  
**密级：** 机密  

---

## 一、奉旨事由

臣等奉皇上旨意，研拟 OpenClaw IM 客户端 v2 开发技术方案。新客户端需直接集成 OpenClaw Gateway WebSocket 协议（端口 18789），实现登录、聊天、内置浏览器、远程桌面四大核心功能，采用 Flutter 3.x 技术栈，交付 APK 及源代码。

臣等已详查 OpenClaw Gateway 协议规范、Flutter 生态组件及 noVNC 集成方案，现呈报完整技术方案，恭请皇上圣鉴。

---

## 二、技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw IM Client v2 (Flutter)               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │  登录模块   │  │  聊天模块   │  │  浏览器模块 │  │ 远程桌面││
│  │  LoginView  │  │  ChatView   │  │  WebView    │  │  noVNC  ││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬────┘│
│         │                │                │               │     │
│         └────────────────┴────────────────┴───────────────┘     │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │   WebSocket 服务层  │                        │
│                    │  (Gateway 协议适配) │                        │
│                    └─────────┬─────────┘                        │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │   本地数据持久化   │                        │
│                    │  (SharedPreferences)│                       │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket (ws://gateway:18789)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OpenClaw Gateway (Node.js)                      │
│                      Port: 18789                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

| 模块 | 职责 | 关键技术 |
|------|------|----------|
| **认证模块** | Gateway 地址配置、Token 管理、设备配对、Agent 选择 | `web_socket_channel`、`SharedPreferences` |
| **会话模块** | WebSocket 连接管理、心跳保活、断线重连 | `StreamController`、`ConnectivityPlus` |
| **消息模块** | 消息收发、解析、本地缓存、已读状态 | `Isolate`（重型解析）、`Hive` |
| **聊天 UI 模块** | 消息列表、输入框、表情、文件传输 | `flutter_bloc`、`cached_network_image` |
| **浏览器模块** | 内嵌 WebView、URL 拦截、JavaScript 桥接 | `webview_flutter` |
| **远程桌面模块** | noVNC 集成、VNC 协议适配、触控映射 | `flutter_inappwebview`、noVNC JS |
| **状态管理** | 全局状态、Agent 切换、连接状态 | `flutter_bloc` 或 `Riverpod` |

### 2.3 数据流设计

```
用户操作 → UI 事件 → BLoC/Riverpod → WebSocket 服务 → Gateway
                                        ↓
                                  本地缓存 (Hive)
                                        ↓
                                  响应解析 → UI 更新
```

**核心协议消息类型：**

| 消息类型 | 方向 | 描述 |
|----------|------|------|
| `auth.token` | C→S | 认证令牌提交 |
| `session.create` | C→S | 创建新会话 |
| `session.message` | C→S | 发送消息 |
| `session.message` | S→C | 接收消息 |
| `node.list` | C→S | 获取可用 Agent 列表 |
| `node.invoke` | C→S | 调用节点能力（远程桌面等） |
| `presence.update` | S→C | 在线状态更新 |
| `ping/pong` | 双向 | 心跳保活 |

---

## 三、技术选型

### 3.1 核心框架

| 组件 | 选型 | 理由 | 备选方案 |
|------|------|------|----------|
| **跨平台框架** | Flutter 3.x | 一套代码多端运行、性能优异、生态成熟 | React Native、Kotlin Multiplatform |
| **WebSocket** | `web_socket_channel` | 官方推荐、支持 WSS、API 简洁 | `web_socket_client` |
| **状态管理** | `flutter_bloc` | 可测试性强、结构清晰、团队熟悉 | Riverpod、Provider |
| **本地存储** | `Hive` | 轻量级、高性能、支持加密 | SharedPreferences、Isar |
| **WebView** | `webview_flutter` | 官方维护、支持 JS 桥接 | `flutter_inappwebview` |
| **网络连接** | `connectivity_plus` | 检测网络变化、自动重连 | `network_info_plus` |
| **JSON 解析** | `json_serializable` | 编译时生成、类型安全 | `freezed`、手动解析 |

### 3.2 选型理由详述

**为何选择 Flutter？**
- 皇上旨意明确要求 Flutter 3.x，臣等深表赞同
- 跨平台能力：一套代码同时生成 Android APK 及 iOS IPA
- 性能优势：Skia 引擎直接渲染，60fps 流畅体验
- 生态成熟：WebSocket、WebView、状态管理均有高质量插件
- 开发效率：热重载 (Hot Reload) 加速迭代

**为何选择 flutter_bloc？**
- 结构清晰：Event → BLoC → State 单向数据流
- 可测试性强：纯 Dart 代码，无需 Widget 测试环境
- 社区活跃：大量现成示例和最佳实践

**为何选择 Hive？**
- 性能优异：比 SharedPreferences 快 10 倍以上
- 支持加密：可加密存储敏感 Token
- 类型安全：编译时生成适配器

### 3.3 noVNC 集成方案

noVNC 为基于 HTML5 的 VNC 客户端，需通过 WebView 加载：

```
┌─────────────────────────────────────┐
│  Flutter App                        │
│  ┌───────────────────────────────┐  │
│  │  flutter_inappwebview         │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  noVNC (HTML5 + JS)     │  │  │
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │  WebSocket → VNC  │  │  │  │
│  │  │  │  Server           │  │  │  │
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**集成步骤：**
1. 将 noVNC 静态资源打包至 Flutter assets
2. 使用 `flutter_inappwebview` 加载本地 noVNC 页面
3. 通过 `JavaScriptChannel` 实现 Flutter ↔ noVNC 通信
4. VNC 服务器地址由 Gateway 提供（需额外部署 VNC Server）

---

## 四、人力估算

### 4.1 团队配置

| 角色 | 人数 | 技能要求 | 投入时间 |
|------|------|----------|----------|
| **Flutter 主程** | 1 人 | 3 年以上 Flutter 经验、熟悉 WebSocket、状态管理 | 全程 |
| **Flutter 开发** | 1 人 | 2 年以上 Flutter 经验、UI 开发 | 全程 |
| **后端协作者** | 0.5 人 | 熟悉 OpenClaw Gateway 协议、Node.js | 前期 2 周 |
| **测试工程师** | 0.5 人 | 移动端测试、自动化测试 | 后期 3 周 |
| **UI/UX 设计** | 0.5 人 | Flutter UI 设计、Material Design | 前期 2 周 |

**总计：** 3.5 人 × 8 周 ≈ **28 人周**

### 4.2 技能矩阵

```
Flutter 3.x          ████████████████████  必须
Dart 语言            ████████████████████  必须
WebSocket 协议       ████████████████░░░░  重要
状态管理 (BLoC)      ████████████████░░░░  重要
WebView 集成         ██████████████░░░░░░  重要
noVNC/VNC 协议       ████████░░░░░░░░░░░░  了解
REST API             ██████████████░░░░░░  了解
Git 版本控制         ████████████████████  必须
```

---

## 五、开发排期

### 5.1 里程碑规划

```
Week 1-2: 基础架构搭建
Week 3-4: 核心功能开发
Week 5-6: 高级功能开发
Week 7:   测试与优化
Week 8:   发布准备
```

### 5.2 详细排期

| 阶段 | 时间 | 任务 | 交付物 |
|------|------|------|--------|
| **Phase 1: 启动** | Week 1 | 需求确认、技术预研、环境搭建 | 项目脚手架、技术文档 |
| **Phase 2: 基础** | Week 2 | 登录模块、WebSocket 连接、协议解析 | 可登录测试版 |
| **Phase 3: 核心** | Week 3-4 | 聊天模块、消息收发、Agent 切换 | MVP 版本 |
| **Phase 4: 高级** | Week 5 | WebView 浏览器模块 | 内置浏览器功能 |
| **Phase 5: 高级** | Week 6 | noVNC 远程桌面集成 | 远程桌面功能 |
| **Phase 6: 测试** | Week 7 | 功能测试、性能优化、Bug 修复 | 测试报告 |
| **Phase 7: 发布** | Week 8 | APK 打包、GitHub Release、文档 | 正式发布 |

### 5.3 MVP 范围

**MVP（Minimum Viable Product）定义：** Week 4 结束时可用的最小功能集

- ✅ 登录页面（Gateway 地址、Token 输入）
- ✅ WebSocket 连接与保活
- ✅ Agent 列表获取与切换
- ✅ 聊天页面（文本消息收发）
- ✅ 本地消息缓存
- ❌ 内置浏览器（Phase 4）
- ❌ 远程桌面（Phase 5）
- ❌ 文件传输、图片预览（后续迭代）

### 5.4 完整版本功能清单

| 功能 | 优先级 | 预计工时 |
|------|--------|----------|
| 登录认证 | P0 | 3 天 |
| WebSocket 连接管理 | P0 | 3 天 |
| Agent 选择与切换 | P0 | 2 天 |
| 文本消息收发 | P0 | 5 天 |
| 消息本地缓存 | P1 | 2 天 |
| 已读/未读状态 | P1 | 2 天 |
| 内置浏览器 | P1 | 5 天 |
| 远程桌面 (noVNC) | P2 | 7 天 |
| 图片/文件传输 | P2 | 5 天 |
| 推送通知 | P2 | 3 天 |
| 深色模式 | P3 | 2 天 |
| 多语言支持 | P3 | 3 天 |

---

## 六、风险评估

### 6.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| **WebSocket 协议变更** | 中 | 高 | 与 Gateway 团队保持沟通、协议版本协商 |
| **noVNC 集成困难** | 中 | 中 | 提前技术预研、准备备选方案（如 RustDesk SDK） |
| **Flutter WebView 性能** | 低 | 中 | 使用 `flutter_inappwebview`、优化资源加载 |
| **Android 兼容性** | 中 | 中 | 覆盖 Android 8.0+ 主流机型测试 |
| **Token 安全存储** | 低 | 高 | 使用 `flutter_secure_storage` 加密存储 |

### 6.2 依赖项风险

| 依赖 | 风险 | 应对 |
|------|------|------|
| **OpenClaw Gateway** | 协议未完全文档化 | 请求 Gateway 团队提供协议文档、进行联调 |
| **noVNC** | 需额外部署 VNC Server | 明确 VNC Server 部署方案、或改用其他远程桌面方案 |
| **Flutter 插件** | 插件维护状态 | 选择官方或高星插件、准备备选方案 |

### 6.3 备选方案

**若 noVNC 集成受阻：**
- 方案 A：使用 `flutter_rust_bridge` + Rust VNC 客户端
- 方案 B：集成 RustDesk Flutter SDK（如有）
- 方案 C：简化为 WebView 加载远程桌面 URL

**若 WebSocket 协议复杂：**
- 方案 A：请求 Gateway 团队提供 Dart SDK
- 方案 B：使用代码生成工具从 TypeScript 协议生成 Dart 代码
- 方案 C：手动实现核心协议、简化高级功能

### 6.4 风险缓解时间表

```
Week 1:   完成 WebSocket 协议验证（关键路径）
Week 2:   完成 noVNC 技术预研（关键路径）
Week 3:   完成 Android 兼容性测试
Week 5:   完成安全审计（Token 存储、通信加密）
```

---

## 七、交付物清单

### 7.1 代码交付

- [x] Flutter 源代码（GitHub 仓库）
- [x] Android APK（Release 版本）
- [x] iOS IPA（可选，需 Apple Developer 账号）
- [x] 技术文档（README.md、API 文档）
- [x] 构建脚本（CI/CD 配置）

### 7.2 GitHub Release 内容

```yaml
Release Tag: v2.0.0
Title: OpenClaw IM Client v2.0.0 - Initial Release
Assets:
  - openclaw-im-v2.0.0.apk
  - openclaw-im-v2.0.0-source.zip
  - CHANGELOG.md
  - INSTALLATION.md
```

### 7.3 文档清单

| 文档 | 内容 |
|------|------|
| README.md | 项目介绍、快速开始 |
| ARCHITECTURE.md | 技术架构详解 |
| API.md | Gateway 协议适配说明 |
| BUILD.md | 构建指南 |
| CHANGELOG.md | 版本更新日志 |

---

## 八、预算估算

### 8.1 人力成本

| 角色 | 人周 | 单价（元/周） | 小计（元） |
|------|------|---------------|------------|
| Flutter 主程 | 8 | 30,000 | 240,000 |
| Flutter 开发 | 8 | 20,000 | 160,000 |
| 后端协作者 | 2 | 25,000 | 50,000 |
| 测试工程师 | 3 | 15,000 | 45,000 |
| UI/UX 设计 | 2 | 20,000 | 40,000 |
| **合计** | **23** | - | **535,000** |

### 8.2 其他成本

| 项目 | 金额（元） |
|------|------------|
| Apple Developer 账号（年） | 688 |
| Google Play 开发者账号（一次性） | 180 |
| 测试设备采购 | 10,000 |
| 云服务（CI/CD、测试） | 5,000 |
| **合计** | **15,868** |

### 8.3 总预算

**人民币 550,868 元**（约 55 万元）

---

## 九、版本演进路线

### 9.1 版本总览

| 版本 | 代号 | 功能主题 | 预计时间 | 人力 | 发布形式 |
|------|------|----------|----------|------|----------|
| **v2.0** | Foundation | MVP（登录 + 聊天） | 8 周 | 3.5 人 | GitHub Release |
| **v2.1** | Notification | 推送通知 + 文件传输 | 4 周 | 2 人 | GitHub Release + Play Store |
| **v2.2** | Media | 语音消息 + 图片预览 | 5 周 | 2.5 人 | GitHub Release + Play Store |
| **v2.3** | Cloud | 多账号 + 云端同步 | 6 周 | 3 人 | GitHub Release + Play Store + App Store |
| **v3.0** | Universal | 桌面端 + 插件系统 | 12 周 | 4 人 | 全平台发布 |

---

### 9.2 v2.1 版本详案（推送通知 + 文件传输）

**发布时间：** v2.0 发布后 4 周  
**人力投入：** 2 人 × 4 周 = 8 人周

#### 功能清单

| 功能 | 优先级 | 描述 | 工时 |
|------|--------|------|------|
| Firebase 推送通知 | P0 | 集成 FCM，支持消息推送 | 5 天 |
| 后台消息接收 | P0 | WebSocket 后台保活 | 3 天 |
| 通知栏交互 | P1 | 点击通知跳转会话 | 2 天 |
| 文件选择器 | P0 | 系统文件选择器集成 | 3 天 |
| 文件上传 | P0 | 图片/文档上传至 Gateway | 4 天 |
| 文件下载 | P1 | 文件下载至本地 | 3 天 |
| 文件预览 | P1 | 图片/文档预览 | 3 天 |

#### 技术变更

```
变更类型：增量开发（无需重构）

新增依赖：
- firebase_core: ^2.24.0
- firebase_messaging: ^14.7.0
- flutter_local_notifications: ^16.3.0
- file_picker: ^6.1.1
- flutter_downloader: ^1.11.5

架构调整：
- 新增 NotificationService 单例
- 新增 FileTransferService 服务层
- BLoC 新增 FileTransferEvent/State
```

#### 开发排期

| 周次 | 任务 | 交付物 |
|------|------|--------|
| Week 1 | FCM 集成、通知权限申请 | 可接收推送测试版 |
| Week 2 | 通知栏交互、后台保活 | 完整推送功能 |
| Week 3 | 文件选择器、上传功能 | 文件上传测试版 |
| Week 4 | 文件下载、预览、测试 | v2.1 Release |

#### 风险评估

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| FCM 国内不可用 | 高 | 高 | 集成华为/小米/OPPO 推送联盟 |
| 后台 WebSocket 断开 | 中 | 高 | 使用 WorkManager 保活 |
| 大文件上传失败 | 中 | 中 | 分片上传、断点续传 |

---

### 9.3 v2.2 版本详案（语音消息 + 图片预览）

**发布时间：** v2.1 发布后 5 周  
**人力投入：** 2.5 人 × 5 周 = 12.5 人周

#### 功能清单

| 功能 | 优先级 | 描述 | 工时 |
|------|--------|------|------|
| 语音录制 | P0 | 按住说话、录音功能 | 5 天 |
| 语音播放 | P0 | 语音消息播放、暂停 | 3 天 |
| 语音转文字 | P1 | 集成语音识别 API | 5 天 |
| 图片选择 | P0 | 相册选择、拍照 | 3 天 |
| 图片压缩 | P1 | 上传前压缩 | 2 天 |
| 图片预览 | P0 | 大图预览、缩放 | 3 天 |
| 图片编辑 | P2 | 裁剪、涂鸦 | 4 天 |
| 消息撤回 | P1 | 2 分钟内撤回 | 2 天 |
| 消息删除 | P1 | 本地/服务器删除 | 2 天 |

#### 技术变更

```
变更类型：模块扩展（轻微重构）

新增依赖：
- record: ^5.0.4
- just_audio: ^0.9.36
- speech_to_text: ^6.6.0
- image_picker: ^1.0.5
- image_cropper: ^5.0.1
- photo_view: ^0.14.0

架构调整：
- 新增 MediaFeature 模块
- 新增 AudioService、ImageService
- Message 模型扩展 mediaUrl、mediaType 字段
- 数据库迁移：Hive Box 版本升级 v1→v2
```

#### 开发排期

| 周次 | 任务 | 交付物 |
|------|------|--------|
| Week 1 | 语音录制、播放功能 | 语音消息测试版 |
| Week 2 | 语音转文字、UI 优化 | 完整语音功能 |
| Week 3 | 图片选择、压缩、上传 | 图片消息测试版 |
| Week 4 | 图片预览、编辑功能 | 完整图片功能 |
| Week 5 | 消息撤回/删除、测试 | v2.2 Release |

#### 风险评估

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 语音权限被拒 | 中 | 中 | 引导用户手动授权 |
| 大图片 OOM | 中 | 高 | 缩略图 + 分页加载 |
| 语音转文字准确率 | 高 | 中 | 提供手动编辑入口 |

---

### 9.4 v2.3 版本详案（多账号 + 云端同步）

**发布时间：** v2.2 发布后 6 周  
**人力投入：** 3 人 × 6 周 = 18 人周

#### 功能清单

| 功能 | 优先级 | 描述 | 工时 |
|------|--------|------|------|
| 多账号登录 | P0 | 支持多 Gateway 账号 | 5 天 |
| 账号切换 | P0 | 快速切换账号 | 2 天 |
| 账号管理 | P1 | 添加/删除/编辑账号 | 3 天 |
| 云端配置同步 | P0 | 设置、主题云端备份 | 5 天 |
| 消息漫游 | P1 | 云端拉取历史消息 | 5 天 |
| 联系人同步 | P1 | 云端联系人备份 | 3 天 |
| 数据导出 | P2 | 导出聊天记录 | 4 天 |
| 数据导入 | P2 | 从备份恢复 | 4 天 |

#### 技术变更

```
变更类型：架构重构（中等规模）

新增依赖：
- flutter_secure_storage: ^9.0.0（多账号 Token 隔离）
- encrypt: ^5.0.3（本地数据加密）
- share_plus: ^7.2.1（数据导出）

架构调整：
- 新增 AccountManager 单例
- 新增 SyncService 云端同步服务
- 数据库迁移：Hive Box 版本升级 v2→v3
- 新增 Account 模型，支持多实例
- 所有 BLoC 支持 accountId 参数

重构范围：
- AuthModule 重构为 AccountModule
- 所有数据访问层支持多账号隔离
- UI 层支持账号切换动画
```

#### 开发排期

| 周次 | 任务 | 交付物 |
|------|------|--------|
| Week 1 | AccountManager 设计实现 | 多账号基础框架 |
| Week 2 | 账号登录、切换功能 | 多账号登录测试版 |
| Week 3 | 云端配置同步 | 配置同步测试版 |
| Week 4 | 消息漫游、联系人同步 | 完整同步功能 |
| Week 5 | 数据导出/导入 | 数据管理功能 |
| Week 6 | 全量测试、性能优化 | v2.3 Release |

#### 风险评估

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 多账号数据混淆 | 中 | 高 | 严格隔离测试、代码审查 |
| 云端同步冲突 | 中 | 中 | 最后写入优先 + 冲突提示 |
| 迁移导致数据丢失 | 低 | 高 | 迁移前备份、可回滚 |

---

### 9.5 v3.0 版本详案（桌面端 + 插件系统）

**发布时间：** v2.3 发布后 12 周  
**人力投入：** 4 人 × 12 周 = 48 人周

#### 功能清单

| 功能 | 优先级 | 描述 | 工时 |
|------|--------|------|------|
| Windows 桌面端 | P0 | Windows 10/11 支持 | 15 天 |
| macOS 桌面端 | P0 | macOS 12+ 支持 | 15 天 |
| Linux 桌面端 | P1 | Ubuntu/Debian 支持 | 10 天 |
| 插件系统 | P0 | 第三方插件加载 | 20 天 |
| 插件市场 | P1 | 插件浏览、安装 | 10 天 |
| 快捷键支持 | P1 | 全局快捷键 | 5 天 |
| 系统托盘 | P1 | 后台运行、托盘菜单 | 5 天 |
| 多窗口支持 | P2 | 多会话窗口 | 5 天 |

#### 技术变更

```
变更类型：重大架构升级（大规模重构）

新增依赖：
- flutter_desktop: ^1.0.0（桌面端支持）
- window_manager: ^0.3.8（窗口控制）
- tray_manager: ^0.2.2（系统托盘）
- hotkey_manager: ^0.1.8（快捷键）
- plugin_platform_interface: ^2.1.6（插件接口）

架构调整：
- 新增 PluginManager 插件管理器
- 新增 PluginLoader 动态加载器
- 新增 DesktopFeature 桌面特性模块
- 核心业务逻辑抽象为 Platform-Agnostic 层
- UI 层适配桌面端交互（鼠标、键盘）

代码组织：
- lib/
  ├── core/           # 平台无关核心逻辑
  ├── features/       # 功能模块
  ├── platform/       # 平台特定实现
  │   ├── mobile/
  │   └── desktop/
  └── plugins/        # 插件系统
```

#### 开发排期

| 周次 | 任务 | 交付物 |
|------|------|--------|
| Week 1-2 | 桌面端基础框架 | 可运行桌面版 |
| Week 3-4 | 窗口管理、系统托盘 | 桌面端基础功能 |
| Week 5-6 | 快捷键、多窗口 | 桌面端完整功能 |
| Week 7-9 | 插件系统设计实现 | 插件系统测试版 |
| Week 10 | 插件市场、文档 | 插件生态基础 |
| Week 11-12 | 全平台测试、优化 | v3.0 Release |

#### 风险评估

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 桌面端性能问题 | 中 | 中 | 性能分析、针对性优化 |
| 插件安全问题 | 高 | 高 | 沙箱机制、权限审查 |
| 多平台兼容性问题 | 中 | 中 | 持续集成、多平台测试 |

---

### 9.6 版本演进总预算

| 版本 | 人力成本 | 其他成本 | 合计 |
|------|----------|----------|------|
| v2.0 | 535,000 元 | 15,868 元 | 550,868 元 |
| v2.1 | 160,000 元 | 5,000 元 | 165,000 元 |
| v2.2 | 200,000 元 | 5,000 元 | 205,000 元 |
| v2.3 | 270,000 元 | 10,000 元 | 280,000 元 |
| v3.0 | 720,000 元 | 30,000 元 | 750,000 元 |
| **总计** | **1,885,000 元** | **65,868 元** | **1,950,868 元** |

---

## 十、架构扩展性设计

### 10.1 模块化设计

**设计原则：** 高内聚、低耦合、可插拔

```
┌─────────────────────────────────────────────────────────────┐
│                      App Shell (启动器)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Auth      │  │    Chat     │  │   Browser   │  ...     │
│  │   Module    │  │   Module    │  │   Module    │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                   │
│         └────────────────┴────────────────┘                   │
│                          │                                    │
│              ┌───────────▼───────────┐                       │
│              │   Core Services       │                       │
│              │   - WebSocket         │                       │
│              │   - Storage           │                       │
│              │   - Navigation        │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**模块边界定义：**

| 模块 | 职责 | 对外接口 | 依赖 |
|------|------|----------|------|
| AuthModule | 认证、账号管理 | `AuthService.login()`, `AuthService.switchAccount()` | CoreServices |
| ChatModule | 消息收发、会话管理 | `ChatService.send()`, `ChatService.listen()` | AuthModule, CoreServices |
| BrowserModule | WebView 浏览器 | `BrowserService.openUrl()` | CoreServices |
| DesktopModule | 桌面端特性 | `DesktopService.setTray()` | CoreServices |
| PluginModule | 插件加载 | `PluginService.load()`, `PluginService.unload()` | CoreServices |

### 10.2 插件化架构

**插件系统设计：**

```
┌─────────────────────────────────────────────────────────────┐
│                      插件管理器                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  插件加载器  │  │  权限管理器  │  │  生命周期   │          │
│  │  PluginLoader│  │ Permission  │  │ Lifecycle   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                      插件接口层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  IPlugin    │  │  IMessageHook│  │  IUIExtension│         │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                      第三方插件                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  翻译插件   │  │  表情包插件  │  │  主题插件   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

**插件接口定义（Dart）：**

```dart
abstract class IPlugin {
  String get id;
  String get name;
  String get version;
  
  Future<void> onLoad(PluginContext context);
  Future<void> onUnload();
  
  // 可选钩子
  void onMessageReceived(Message message) {}
  void onMessageSent(Message message) {}
  Widget? buildMessageExtension(Message message) => null;
}
```

**插件包结构：**

```
plugin-example/
├── plugin.yaml          # 插件元数据
├── lib/
│   └── plugin.dart      # 插件入口
├── assets/              # 插件资源
└── README.md
```

### 10.3 扩展点设计

**系统预留扩展点：**

| 扩展点 | 类型 | 描述 | 版本 |
|--------|------|------|------|
| `MessageRenderer` | 接口 | 自定义消息渲染 | v2.2 |
| `AuthProvider` | 接口 | 自定义认证方式 | v2.3 |
| `StorageBackend` | 接口 | 自定义存储后端 | v2.3 |
| `TransportProtocol` | 接口 | 自定义传输协议 | v3.0 |
| `UIComponent` | 接口 | 自定义 UI 组件 | v3.0 |

### 10.4 配置驱动设计

**功能开关配置：**

```yaml
features:
  chat:
    enabled: true
    maxMessageLength: 2000
    enableTyping: true
  
  media:
    enabled: true
    maxImageSize: 10MB
    maxVideoSize: 50MB
  
  voice:
    enabled: false  # v2.2 开启
    maxDuration: 300s
  
  desktop:
    enabled: false  # v3.0 开启
    systemTray: true
    globalShortcut: true
  
  plugins:
    enabled: false  # v3.0 开启
    allowThirdParty: false
    sandboxMode: true
```

---

## 十一、数据迁移方案

### 11.1 本地数据库版本管理

**Hive Box 版本演进：**

| 版本 | 引入版本 | 变更内容 | 迁移脚本 |
|------|----------|----------|----------|
| v1 | v2.0 | 初始版本：消息、会话 | - |
| v2 | v2.2 | 新增 mediaUrl、mediaType 字段 | migrate_v1_to_v2.dart |
| v3 | v2.3 | 新增 accountId 字段、多账号支持 | migrate_v2_to_v3.dart |
| v4 | v3.0 | 新增插件数据 Box | migrate_v3_to_v4.dart |

### 11.2 数据迁移策略

**迁移原则：**

1. **向后兼容**：新版本可读旧版本数据
2. **渐进迁移**：启动时检测版本、自动迁移
3. **可回滚**：迁移前备份、失败可恢复
4. **用户无感**：迁移过程不阻塞 UI

**迁移流程：**

```
App 启动
    │
    ▼
读取当前数据库版本
    │
    ▼
版本比对
    │
    ├── 版本一致 ──→ 正常使用
    │
    └── 版本过旧 ──→ 执行迁移
            │
            ▼
        备份当前数据
            │
            ▼
        执行迁移脚本
            │
            ├── 成功 ──→ 更新版本号、正常使用
            │
            └── 失败 ──→ 恢复备份、提示用户
```

### 11.3 迁移脚本示例

```dart
// migrate_v1_to_v2.dart
Future<void> migrateV1ToV2() async {
  final messageBox = Hive.box<Message>('messages');
  final messages = messageBox.values.toList();
  
  for (var message in messages) {
    // 新增字段设置默认值
    message.mediaUrl ??= '';
    message.mediaType ??= MessageType.text;
    await message.save();
  }
  
  // 更新版本号
  await SettingsBox.put('dbVersion', 2);
}

// migrate_v2_to_v3.dart
Future<void> migrateV2ToV3() async {
  // 创建新的多账号数据结构
  final accounts = await AccountBox.getAll();
  final currentAccount = accounts.first;
  
  // 迁移所有数据到新结构
  for (var message in await MessageBox.getAll()) {
    message.accountId = currentAccount.id;
    await message.save();
  }
  
  await SettingsBox.put('dbVersion', 3);
}
```

### 11.4 云端同步策略

**同步模型：**

```
┌─────────────────────────────────────────────────────────────┐
│                      本地数据库                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Messages  │  │  Accounts   │  │   Settings  │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                   │
│         └────────────────┴────────────────┘                   │
│                          │                                    │
│              ┌───────────▼───────────┐                       │
│              │    SyncService        │                       │
│              │    - 增量同步          │                       │
│              │    - 冲突解决          │                       │
│              │    - 离线队列          │                       │
│              └───────────┬───────────┘                       │
│                          │                                    │
│              ┌───────────▼───────────┐                       │
│              │   云端数据库           │                       │
│              │   (Gateway 存储)       │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**同步规则：**

| 数据类型 | 同步策略 | 冲突解决 |
|----------|----------|----------|
| 消息 | 双向同步 | 服务器时间戳优先 |
| 账号配置 | 双向同步 | 最后修改优先 |
| 本地设置 | 仅上传 | 本地优先 |
| 联系人 | 双向同步 | 合并去重 |

### 11.5 数据备份与恢复

**备份策略：**

```yaml
backup:
  autoBackup: true
  interval: daily
  maxBackups: 7
  storage:
    - local: ~/.openclaw/im-client/backup/
    - cloud: gateway:/user/backup/
  
restore:
  confirmBeforeRestore: true
  mergeMode: false  # true=合并，false=覆盖
```

---

## 十二、臣等建议

### 12.1 优先级建议

1. **首保 MVP**：优先完成登录、聊天核心功能，确保 4 周内可用
2. **渐进增强**：浏览器、远程桌面作为后续迭代功能
3. **协议优先**：Week 1 即与 Gateway 团队联调，避免后期返工
4. **架构先行**：v2.0 即预留扩展点，避免后续重构

### 12.2 技术债务防控

- 建立代码审查机制，确保代码质量
- 编写单元测试，覆盖率目标 70%+
- 使用静态分析工具（dart analyze、flutter lint）
- 定期重构，避免技术债务累积
- **每个版本预留 20% 时间用于技术债务清理**

### 12.3 版本发布策略

| 版本类型 | 发布周期 | 质量要求 | 发布渠道 |
|----------|----------|----------|----------|
| 大版本 (v2.x) | 4-6 周 | 完整测试 | GitHub + Store |
| 小版本 (v2.x.y) | 1-2 周 | 回归测试 | GitHub |
| 热修复 (v2.x.y.z) | 随时 | 关键 Bug | GitHub |

### 12.4 长期演进建议

1. **v2.x 系列**：完善移动端功能，积累用户
2. **v3.0**：跨平台突破，建立插件生态
3. **v4.0+**：AI 深度集成、多模态交互

---

## 十三、结语

臣等谨遵皇上旨意，详查技术细节，研拟此方案。OpenClaw IM 客户端 v2 之开发，技术可行、人力可及、风险可控。版本演进路线清晰，架构扩展性充足，数据迁移方案完备。若蒙皇上恩准，臣等即刻招募人手，启动项目，按期交付。

**伏乞皇上圣鉴！**

---

**中书省 谨奏**  
2026 年 3 月 25 日

---

## 十、结语

臣等谨遵皇上旨意，详查技术细节，研拟此方案。OpenClaw IM 客户端 v2 之开发，技术可行、人力可及、风险可控。若蒙皇上恩准，臣等即刻招募人手，启动项目，按期交付。

**伏乞皇上圣鉴！**

---

**中书省 谨奏**  
2026 年 3 月 25 日

---

## 附录

### 附录 A：Flutter 项目结构

```
openclaw_im_client_v2/
├── lib/
│   ├── main.dart
│   ├── app/
│   │   ├── app.dart
│   │   └── routes.dart
│   ├── features/
│   │   ├── auth/
│   │   │   ├── presentation/
│   │   │   ├── domain/
│   │   │   └── data/
│   │   ├── chat/
│   │   │   ├── presentation/
│   │   │   ├── domain/
│   │   │   └── data/
│   │   ├── browser/
│   │   └── remote_desktop/
│   ├── core/
│   │   ├── websocket/
│   │   ├── storage/
│   │   └── utils/
│   └── shared/
│       ├── widgets/
│       └── theme/
├── assets/
│   ├── noVNC/
│   └── images/
├── test/
├── pubspec.yaml
└── README.md
```

### 附录 B：核心依赖清单 (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # WebSocket
  web_socket_channel: ^2.4.0
  
  # 状态管理
  flutter_bloc: ^8.1.3
  equatable: ^2.0.5
  
  # 本地存储
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  flutter_secure_storage: ^9.0.0
  
  # WebView
  webview_flutter: ^4.4.2
  
  # 网络
  connectivity_plus: ^5.0.2
  
  # JSON 解析
  json_annotation: ^4.8.1
  
  # 工具
  dio: ^5.4.0
  logger: ^2.0.2+1
  intl: ^0.18.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
  build_runner: ^2.4.7
  json_serializable: ^6.7.1
  hive_generator: ^2.0.1
```

### 附录 C：Gateway WebSocket 协议参考

基于 OpenClaw README 及 node-connect skill 分析：

```typescript
// 认证消息
{
  type: "auth.token",
  token: "<bootstrap_token_or_password>"
}

// 创建会话
{
  type: "session.create",
  agent: "<agent_name>"
}

// 发送消息
{
  type: "session.message",
  sessionId: "<session_id>",
  content: "<message_content>"
}

// 获取节点列表
{
  type: "node.list"
}

// 调用节点能力
{
  type: "node.invoke",
  nodeId: "<node_id>",
  method: "<method_name>",
  params: {}
}

// 心跳
{
  type: "ping",
  timestamp: 1234567890
}

// 响应
{
  type: "pong",
  timestamp: 1234567890
}
```

---

**【奏折结束】**
