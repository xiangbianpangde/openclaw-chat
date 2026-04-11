# 中书省奏折

## 关于开发 OpenClaw IM 客户端 v2 之技术方案（修订版）

**奏呈：** 皇上陛下  
**呈奏：** 中书省  
**日期：** 2026 年 3 月 25 日  
**密级：** 机密  
**版本：** v2.0 Rev.1（奉门下省审核意见修订）

---

## 一、奉旨事由

臣等奉皇上旨意，研拟 OpenClaw IM 客户端 v2 开发技术方案。新客户端需直接集成 OpenClaw Gateway WebSocket 协议（端口 18789），实现登录、聊天、内置浏览器、远程桌面四大核心功能，采用 Flutter 3.x 技术栈，交付 APK 及源代码。

臣等已详查 OpenClaw Gateway 协议规范、Flutter 生态组件及 noVNC 集成方案，并依门下省审核意见补充完善，现呈报完整技术方案，恭请皇上圣鉴。

---

## 二、门下省审核意见及修订说明

### 2.1 审核意见汇总

门下省于 2026 年 3 月 24 日呈递审核意见，共四项需补充修改内容：

1. **Flutter 兼容性测试计划** - 补充大版本升级兼容性测试方案
2. **WebSocket SLA 监控指标** - 明确连接成功率、延迟、重连指标
3. **风险缓冲预留** - 从 35 周中预留 4-5 周作为风险缓冲
4. **里程碑审查节点** - 每 8 周设置阶段性审查节点

### 2.2 修订说明

臣等已逐项补充完善，主要变更如下：

- 新增 **第十三章 Flutter 兼容性测试计划**
- 新增 **第十四章 WebSocket SLA 监控指标**
- 调整 **第五章 开发排期**，加入风险缓冲 5 周
- 调整 **第九章 版本演进路线**，设置里程碑审查节点
- 调整 **第八章 预算估算**，因排期延长增加人力成本

---

## 三、技术架构

### 3.1 整体架构图

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

### 3.2 模块划分

| 模块 | 职责 | 关键技术 |
|------|------|----------|
| **认证模块** | Gateway 地址配置、Token 管理、设备配对、Agent 选择 | `web_socket_channel`、`SharedPreferences` |
| **会话模块** | WebSocket 连接管理、心跳保活、断线重连 | `StreamController`、`ConnectivityPlus` |
| **消息模块** | 消息收发、解析、本地缓存、已读状态 | `Isolate`（重型解析）、`Hive` |
| **聊天 UI 模块** | 消息列表、输入框、表情、文件传输 | `flutter_bloc`、`cached_network_image` |
| **浏览器模块** | 内嵌 WebView、URL 拦截、JavaScript 桥接 | `webview_flutter` |
| **远程桌面模块** | noVNC 集成、VNC 协议适配、触控映射 | `flutter_inappwebview`、noVNC JS |
| **状态管理** | 全局状态、Agent 切换、连接状态 | `flutter_bloc` 或 `Riverpod` |

### 3.3 数据流设计

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

## 四、技术选型

### 4.1 核心框架

| 组件 | 选型 | 理由 | 备选方案 |
|------|------|------|----------|
| **跨平台框架** | Flutter 3.x | 一套代码多端运行、性能优异、生态成熟 | React Native、Kotlin Multiplatform |
| **WebSocket** | `web_socket_channel` | 官方推荐、支持 WSS、API 简洁 | `web_socket_client` |
| **状态管理** | `flutter_bloc` | 可测试性强、结构清晰、团队熟悉 | Riverpod、Provider |
| **本地存储** | `Hive` | 轻量级、高性能、支持加密 | SharedPreferences、Isar |
| **WebView** | `webview_flutter` | 官方维护、支持 JS 桥接 | `flutter_inappwebview` |
| **网络连接** | `connectivity_plus` | 检测网络变化、自动重连 | `network_info_plus` |
| **JSON 解析** | `json_serializable` | 编译时生成、类型安全 | `freezed`、手动解析 |

### 4.2 选型理由详述

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

### 4.3 noVNC 集成方案

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

## 五、人力估算

### 5.1 团队配置

| 角色 | 人数 | 技能要求 | 投入时间 |
|------|------|----------|----------|
| **Flutter 主程** | 1 人 | 3 年以上 Flutter 经验、熟悉 WebSocket、状态管理 | 全程 |
| **Flutter 开发** | 1 人 | 2 年以上 Flutter 经验、UI 开发 | 全程 |
| **后端协作者** | 0.5 人 | 熟悉 OpenClaw Gateway 协议、Node.js | 前期 2 周 |
| **测试工程师** | 0.5 人 | 移动端测试、自动化测试 | 后期 3 周 |
| **UI/UX 设计** | 0.5 人 | Flutter UI 设计、Material Design | 前期 2 周 |

**总计：** 3.5 人 × 8 周 ≈ **28 人周**

### 5.2 技能矩阵

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

## 六、开发排期（含风险缓冲）

### 6.1 里程碑规划（调整后）

```
Week 1-2:  基础架构搭建
Week 3-4:  核心功能开发
Week 5-6:  高级功能开发
Week 7:    测试与优化
Week 8:    发布准备
Week 9:    【风险缓冲】
```

### 6.2 详细排期（v2.0 基础版）

| 阶段 | 时间 | 任务 | 交付物 |
|------|------|------|--------|
| **Phase 1: 启动** | Week 1 | 需求确认、技术预研、环境搭建 | 项目脚手架、技术文档 |
| **Phase 2: 基础** | Week 2 | 登录模块、WebSocket 连接、协议解析 | 可登录测试版 |
| **Phase 3: 核心** | Week 3-4 | 聊天模块、消息收发、Agent 切换 | MVP 版本 |
| **Phase 4: 高级** | Week 5 | WebView 浏览器模块 | 内置浏览器功能 |
| **Phase 5: 高级** | Week 6 | noVNC 远程桌面集成 | 远程桌面功能 |
| **Phase 6: 测试** | Week 7 | 功能测试、性能优化、Bug 修复 | 测试报告 |
| **Phase 7: 发布** | Week 8 | APK 打包、GitHub Release、文档 | 正式发布 |
| **Phase 8: 缓冲** | Week 9 | 【风险缓冲】应对延期、突发问题 | - |

### 6.3 MVP 范围

**MVP（Minimum Viable Product）定义：** Week 4 结束时可用的最小功能集

- ✅ 登录页面（Gateway 地址、Token 输入）
- ✅ WebSocket 连接与保活
- ✅ Agent 列表获取与切换
- ✅ 聊天页面（文本消息收发）
- ✅ 本地消息缓存
- ❌ 内置浏览器（Phase 4）
- ❌ 远程桌面（Phase 5）
- ❌ 文件传输、图片预览（后续迭代）

### 6.4 完整版本功能清单

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

## 七、风险评估

### 7.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| **WebSocket 协议变更** | 中 | 高 | 与 Gateway 团队保持沟通、协议版本协商 |
| **noVNC 集成困难** | 中 | 中 | 提前技术预研、准备备选方案（如 RustDesk SDK） |
| **Flutter WebView 性能** | 低 | 中 | 使用 `flutter_inappwebview`、优化资源加载 |
| **Android 兼容性** | 中 | 中 | 覆盖 Android 8.0+ 主流机型测试 |
| **Token 安全存储** | 低 | 高 | 使用 `flutter_secure_storage` 加密存储 |

### 7.2 依赖项风险

| 依赖 | 风险 | 应对 |
|------|------|------|
| **OpenClaw Gateway** | 协议未完全文档化 | 请求 Gateway 团队提供协议文档、进行联调 |
| **noVNC** | 需额外部署 VNC Server | 明确 VNC Server 部署方案、或改用其他远程桌面方案 |
| **Flutter 插件** | 插件维护状态 | 选择官方或高星插件、准备备选方案 |

### 7.3 备选方案

**若 noVNC 集成受阻：**
- 方案 A：使用 `flutter_rust_bridge` + Rust VNC 客户端
- 方案 B：集成 RustDesk Flutter SDK（如有）
- 方案 C：简化为 WebView 加载远程桌面 URL

**若 WebSocket 协议复杂：**
- 方案 A：请求 Gateway 团队提供 Dart SDK
- 方案 B：使用代码生成工具从 TypeScript 协议生成 Dart 代码
- 方案 C：手动实现核心协议、简化高级功能

### 7.4 风险缓解时间表

```
Week 1:   完成 WebSocket 协议验证（关键路径）
Week 2:   完成 noVNC 技术预研（关键路径）
Week 3:   完成 Android 兼容性测试
Week 5:   完成安全审计（Token 存储、通信加密）
```

---

## 八、交付物清单

### 8.1 代码交付

- [x] Flutter 源代码（GitHub 仓库）
- [x] Android APK（Release 版本）
- [x] iOS IPA（可选，需 Apple Developer 账号）
- [x] 技术文档（README.md、API 文档）
- [x] 构建脚本（CI/CD 配置）

### 8.2 GitHub Release 内容

```yaml
Release Tag: v2.0.0
Title: OpenClaw IM Client v2.0.0 - Initial Release
Assets:
  - openclaw-im-v2.0.0.apk
  - openclaw-im-v2.0.0-source.zip
  - CHANGELOG.md
  - INSTALLATION.md
```

### 8.3 文档清单

| 文档 | 内容 |
|------|------|
| README.md | 项目介绍、快速开始 |
| ARCHITECTURE.md | 技术架构详解 |
| API.md | Gateway 协议适配说明 |
| BUILD.md | 构建指南 |
| CHANGELOG.md | 版本更新日志 |

---

## 九、预算估算（调整后）

### 9.1 人力成本（v2.0 基础版）

因加入 1 周风险缓冲，人力成本相应调整：

| 角色 | 人周 | 单价（元/周） | 小计（元） |
|------|------|---------------|------------|
| Flutter 主程 | 9 | 30,000 | 270,000 |
| Flutter 开发 | 9 | 20,000 | 180,000 |
| 后端协作者 | 2 | 25,000 | 50,000 |
| 测试工程师 | 4 | 15,000 | 60,000 |
| UI/UX 设计 | 2 | 20,000 | 40,000 |
| **合计** | **26** | - | **600,000** |

### 9.2 其他成本

| 项目 | 金额（元） |
|------|------------|
| Apple Developer 账号（年） | 688 |
| Google Play 开发者账号（一次性） | 180 |
| 测试设备采购 | 10,000 |
| 云服务（CI/CD、测试） | 5,000 |
| **合计** | **15,868** |

### 9.3 v2.0 总预算

**人民币 615,868 元**（约 62 万元）

### 9.4 版本演进总预算（调整后）

因各版本加入风险缓冲及审查节点，总预算调整如下：

| 版本 | 原人力成本 | 调整后人力成本 | 其他成本 | 合计 |
|------|------------|----------------|----------|------|
| v2.0 | 535,000 元 | 600,000 元 | 15,868 元 | 615,868 元 |
| v2.1 | 160,000 元 | 180,000 元 | 5,000 元 | 185,000 元 |
| v2.2 | 200,000 元 | 220,000 元 | 5,000 元 | 225,000 元 |
| v2.3 | 270,000 元 | 300,000 元 | 10,000 元 | 310,000 元 |
| v3.0 | 720,000 元 | 780,000 元 | 30,000 元 | 810,000 元 |
| **总计** | **1,885,000 元** | **2,080,000 元** | **65,868 元** | **2,145,868 元** |

**预算增加说明：** 因加入风险缓冲（约 10-15% 时间预留）及里程碑审查，总预算增加约 195,000 元（约 9%）。

---

## 十、版本演进路线（含里程碑审查）

### 10.1 版本总览（调整后）

| 版本 | 代号 | 功能主题 | 原预计 | 调整后 | 人力 | 审查节点 | 发布形式 |
|------|------|----------|--------|--------|------|----------|----------|
| **v2.0** | Foundation | MVP（登录 + 聊天） | 8 周 | 9 周 | 3.5 人 | Week 8 | GitHub Release |
| **v2.1** | Notification | 推送通知 + 文件传输 | 4 周 | 5 周 | 2 人 | Week 4 | GitHub Release + Play Store |
| **v2.2** | Media | 语音消息 + 图片预览 | 5 周 | 6 周 | 2.5 人 | Week 5 | GitHub Release + Play Store |
| **v2.3** | Cloud | 多账号 + 云端同步 | 6 周 | 7 周 | 3 人 | Week 6 | GitHub Release + Play Store + App Store |
| **v3.0** | Universal | 桌面端 + 插件系统 | 12 周 | 14 周 | 4 人 | Week 8, Week 14 | 全平台发布 |

**总周期：** 原 35 周 → 调整后 **41 周**（含 5 周风险缓冲 + 审查节点）

### 10.2 里程碑审查节点

依门下省意见，每 8 周设置阶段性审查节点：

| 审查节点 | 时间 | 审查内容 | 审查标准 | 参与方 |
|----------|------|----------|----------|--------|
| **Milestone 1** | Week 8 | v2.0 版本验收 | MVP 功能完整、SLA 达标、无 P0 Bug | 皇上、中书省、门下省 |
| **Milestone 2** | Week 16 | v2.1+v2.2 阶段验收 | 推送、文件、语音、图片功能完整 | 皇上、中书省、门下省 |
| **Milestone 3** | Week 24 | v2.3 阶段验收 | 多账号、云端同步功能完整 | 皇上、中书省、门下省 |
| **Milestone 4** | Week 32 | v3.0 中期审查 | 桌面端框架、插件系统原型 | 皇上、中书省、门下省 |
| **Milestone 5** | Week 41 | v3.0 最终验收 | 全平台发布、插件生态就绪 | 皇上、中书省、门下省 |

### 10.3 审查流程

```
审查前 3 天：中书省提交阶段报告
    │
    ▼
审查当日：演示 + 质询（2 小时）
    │
    ├── 通过 ──→ 进入下一阶段
    │
    └── 有条件通过 ──→ 限期整改（≤1 周）→ 复审
            │
            └── 不通过 ──→ 重新规划 → 再次审查
```

### 10.4 审查内容详单

**Milestone 1 审查清单（Week 8）：**

- [ ] 登录功能：支持 Token 认证、设备配对
- [ ] WebSocket 连接：SLA 指标达标（见第十四章）
- [ ] 聊天功能：文本消息收发、本地缓存
- [ ] Agent 切换：支持多 Agent 选择
- [ ] 性能指标：冷启动 <3s、消息延迟 P99 <200ms
- [ ] 兼容性：Android 8.0+ 主流机型测试通过
- [ ] 文档：README、API 文档、构建指南完整
- [ ] 代码质量：单元测试覆盖率 ≥70%

**Milestone 2 审查清单（Week 16）：**

- [ ] 推送通知：FCM 集成、后台保活
- [ ] 文件传输：上传/下载/预览
- [ ] 语音消息：录制/播放/转文字
- [ ] 图片功能：选择/压缩/预览/编辑
- [ ] 消息管理：撤回/删除

**Milestone 3 审查清单（Week 24）：**

- [ ] 多账号：登录/切换/管理
- [ ] 云端同步：配置/消息/联系人
- [ ] 数据管理：导出/导入
- [ ] 安全性：数据加密、权限控制

**Milestone 4 审查清单（Week 32）：**

- [ ] 桌面端框架：Windows/macOS 可运行
- [ ] 插件系统：插件加载器、接口定义
- [ ] 桌面特性：系统托盘、快捷键

**Milestone 5 审查清单（Week 41）：**

- [ ] 桌面端完整：Windows/macOS/Linux
- [ ] 插件市场：插件浏览/安装
- [ ] 全平台测试：移动端 + 桌面端
- [ ] 文档完整：用户手册、开发者文档

---

## 十一、Flutter 兼容性测试计划（新增）

### 11.1 测试范围

依门下省意见，补充 Flutter 大版本升级兼容性测试方案：

| 测试维度 | 测试内容 | 测试频率 |
|----------|----------|----------|
| **Flutter 大版本** | Flutter 3.x → 4.x 升级兼容性 | 每大版本发布后 |
| **Dart 语言版本** | Dart 3.x → 4.x 语法兼容性 | 随 Flutter 升级 |
| **Android 系统** | Android 8.0 - 15.0 兼容性 | 每版本发布前 |
| **iOS 系统** | iOS 14 - 18 兼容性 | 每版本发布前 |
| **核心插件** | WebSocket、WebView、存储插件 | 每次依赖升级 |
| **UI 组件** | Material Design 组件渲染 | 每版本发布前 |

### 11.2 测试方法

#### 11.2.1 Flutter 大版本升级测试流程

```
Flutter 新版本发布
    │
    ▼
创建升级分支 (flutter-upgrade-3.x-to-4.x)
    │
    ▼
升级 Flutter SDK (flutter upgrade)
    │
    ▼
修复编译错误 (flutter analyze)
    │
    ▼
运行单元测试 (flutter test)
    │
    ├── 失败 ──→ 修复代码 → 重新测试
    │
    └── 成功 ──→ 继续
            │
            ▼
        运行集成测试 (flutter drive)
            │
            ├── 失败 ──→ 修复代码 → 重新测试
            │
            └── 成功 ──→ 继续
                    │
                    ▼
                真机兼容性测试（10+ 机型）
                    │
                    ├── 失败 ──→ 修复代码 → 重新测试
                    │
                    └── 成功 ──→ 合并主干 → 发布
```

#### 11.2.2 测试环境配置

**CI/CD 自动化测试矩阵：**

```yaml
# .github/workflows/compatibility-test.yml
name: Flutter Compatibility Test

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # 每周一凌晨 2 点

jobs:
  test:
    strategy:
      matrix:
        flutter-version: ['3.24.x', '3.27.x', 'stable', 'beta']
        android-api: [26, 29, 33, 35]
        ios-version: ['14.0', '16.0', '18.0']
    
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: ${{ matrix.flutter-version }}
      
      - name: Run Tests
        run: |
          flutter analyze
          flutter test --coverage
          flutter drive --target=test_integration/app.dart
```

**真机测试矩阵：**

| 品牌 | 机型 | Android 版本 | 屏幕分辨率 | 优先级 |
|------|------|--------------|------------|--------|
| Google | Pixel 8 | 14.0 | 2400×1080 | P0 |
| Samsung | Galaxy S24 | 14.0 | 2340×1080 | P0 |
| Xiaomi | 14 Pro | 14.0 | 3200×1440 | P0 |
| OnePlus | 12 | 14.0 | 3168×1440 | P1 |
| OPPO | Find X7 | 14.0 | 2780×1264 | P1 |
| vivo | X100 | 14.0 | 2800×1260 | P1 |
| Huawei | Mate 60 | HarmonyOS 4.0 | 2688×1216 | P1 |
| Google | Pixel 6 | 13.0 | 2400×1080 | P2 |
| Samsung | Galaxy A54 | 13.0 | 2340×1080 | P2 |
| Xiaomi | Redmi Note 13 | 13.0 | 2400×1080 | P2 |

### 11.3 回滚方案

#### 11.3.1 升级失败回滚流程

```
发现严重兼容性问题
    │
    ▼
立即停止发布流程
    │
    ▼
回滚 Flutter SDK 版本
    │  flutter install <previous-version>
    │
    ▼
恢复代码至升级前分支
    │  git checkout flutter-upgrade-backup
    │
    ▼
重新编译发布
    │
    ▼
记录问题至兼容性知识库
    │
    ▼
等待 Flutter 修复或寻找替代方案
```

#### 11.3.2 版本回滚策略

| 场景 | 回滚方式 | 预计时间 | 负责人 |
|------|----------|----------|--------|
| 编译失败 | 切换 Flutter 版本、恢复代码 | 30 分钟 | Flutter 主程 |
| 测试失败 | 修复代码或回滚依赖 | 2-4 小时 | 测试工程师 |
| 真机兼容性问题 | 针对性修复或回滚 | 1-2 天 | Flutter 开发 |
| 线上严重 Bug | 紧急热修复或回滚版本 | 4-8 小时 | 全体 |

#### 11.3.3 备份策略

- **代码备份**：升级前创建 `flutter-upgrade-backup` 分支
- **依赖锁定**：pubspec.lock 提交至版本控制
- **构建产物**：每次发布前备份 APK/IPA 至云存储
- **配置备份**：CI/CD 配置、签名密钥独立备份

### 11.4 兼容性测试报告模板

```markdown
## Flutter 兼容性测试报告

**测试版本：** Flutter 3.27.0 → 4.0.0  
**测试日期：** 2026-XX-XX  
**测试人员：** XXX

### 测试结果

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 编译通过 | ✅/❌ | |
| 单元测试 | ✅/❌ (通过率 XX%) | |
| 集成测试 | ✅/❌ | |
| Android 兼容性 | ✅/❌ (XX/10 机型) | |
| iOS 兼容性 | ✅/❌ (XX/3 版本) | |
| UI 渲染 | ✅/❌ | |
| 性能回归 | ✅/❌ (启动时间 +X%) | |

### 发现问题

1. **问题描述**
   - 影响范围：
   - 严重程度：P0/P1/P2
   - 解决方案：

### 结论

- [ ] 建议升级
- [ ] 暂缓升级（原因：XXX）
- [ ] 不建议升级（原因：XXX）
```

### 11.5 兼容性风险预警

| 风险 | 预警信号 | 应对措施 |
|------|----------|----------|
| Flutter 大版本破坏性变更 | 官方发布 Migration Guide | 提前 2 周预研、制定迁移计划 |
| 核心插件停止维护 | 插件 GitHub 3 个月无更新 | 寻找替代插件或自行维护 fork |
| Android/iOS 新系统 API 变更 | 开发者预览版发布 | 参与 Beta 测试、提前适配 |
| 性能回归 | 启动时间/内存占用增加 >10% | 性能分析、针对性优化 |

---

## 十二、WebSocket SLA 监控指标（新增）

### 12.1 SLA 指标定义

依门下省意见，明确 WebSocket 连接服务质量指标：

| 指标 | 目标值 | 测量方法 | 告警阈值 |
|------|--------|----------|----------|
| **连接成功率** | ≥99.9% | 成功连接数/总连接请求数 | <99.5% |
| **消息延迟 P50** | <50ms | 消息发送→接收确认时间 | >100ms |
| **消息延迟 P95** | <150ms | 95% 消息延迟上限 | >300ms |
| **消息延迟 P99** | <200ms | 99% 消息延迟上限 | >500ms |
| **断线率** | <0.1%/小时 | 异常断开次数/连接时长 | >0.5%/小时 |
| **重连成功率** | ≥99.5% | 重连成功次数/总重连次数 | <99% |
| **重连耗时 P95** | <5s | 95% 重连完成时间 | >10s |
| **心跳丢失率** | <0.01% | 丢失心跳数/总心跳数 | >0.1% |

### 12.2 断线重连策略

#### 12.2.1 重连算法（指数退避）

```dart
class WebSocketReconnectStrategy {
  // 基础重连间隔
  static const initialDelay = Duration(seconds: 1);
  
  // 最大重连间隔
  static const maxDelay = Duration(minutes: 5);
  
  // 退避因子
  static const backoffFactor = 2.0;
  
  // 抖动系数（避免同时重连）
  static const jitterFactor = 0.2;
  
  int attempt = 0;
  
  Duration getNextDelay() {
    // 指数退避计算
    final delay = initialDelay * (backoffFactor.pow(attempt));
    
    // 限制最大间隔
    final cappedDelay = delay > maxDelay ? maxDelay : delay;
    
    // 添加抖动（±20%）
    final jitter = cappedDelay * jitterFactor * (random.nextDouble() * 2 - 1);
    
    attempt++;
    return cappedDelay + jitter;
  }
  
  void reset() {
    attempt = 0;
  }
}
```

#### 12.2.2 重连触发条件

| 触发场景 | 重连策略 | 最大重试次数 |
|----------|----------|--------------|
| 网络切换（WiFi→4G） | 立即重连 | 3 次 |
| WebSocket 异常关闭 | 指数退避重连 | 10 次 |
| 心跳超时（30s 无响应） | 指数退避重连 | 10 次 |
| 认证失败（Token 过期） | 刷新 Token 后重连 | 3 次 |
| 服务器主动断开 | 等待 1 分钟后重连 | 5 次 |

#### 12.2.3 重连状态机

```
┌─────────────┐
│  Connected  │
└──────┬──────┘
       │ 断开
       ▼
┌─────────────┐
│ Disconnect  │───→ 检测网络可用？
└──────┬──────┘       │
       │              ├── 否 ──→ 等待网络恢复
       │ 是           │
       ▼              └── 是 ──→ 进入重连队列
┌─────────────┐
│ Reconnecting│───→ 发起连接
└──────┬──────┘
       │
       ├── 成功 ──→ Connected
       │
       └── 失败 ──→ 计算下次重连间隔 ──→ 等待 ──→ Reconnecting
```

### 12.3 监控实现方案

#### 12.3.1 客户端埋点

```dart
class WebSocketMonitor {
  final _metrics = WebSocketMetrics();
  
  // 记录连接尝试
  void recordConnectionAttempt(bool success, Duration duration) {
    _metrics.connectionAttempts++;
    if (success) {
      _metrics.successfulConnections++;
    }
    _metrics.connectionLatency.add(duration.inMilliseconds);
  }
  
  // 记录消息延迟
  void recordMessageLatency(Duration latency) {
    _metrics.messageLatency.add(latency.inMilliseconds);
  }
  
  // 记录断线
  void recordDisconnection(Duration connectionDuration) {
    _metrics.disconnections++;
    _metrics.connectionDurations.add(connectionDuration.inSeconds);
  }
  
  // 记录重连
  void recordReconnect(bool success, Duration duration) {
    _metrics.reconnectAttempts++;
    if (success) {
      _metrics.successfulReconnects++;
    }
    _metrics.reconnectLatency.add(duration.inMilliseconds);
  }
  
  // 计算 SLA 指标
  SLAReport generateReport() {
    return SLAReport(
      connectionSuccessRate: _metrics.successfulConnections / _metrics.connectionAttempts,
      messageLatencyP50: _metrics.messageLatency.percentile(50),
      messageLatencyP95: _metrics.messageLatency.percentile(95),
      messageLatencyP99: _metrics.messageLatency.percentile(99),
      disconnectionRate: _metrics.disconnections / _metrics.totalConnectionHours,
      reconnectSuccessRate: _metrics.successfulReconnects / _metrics.reconnectAttempts,
      reconnectLatencyP95: _metrics.reconnectLatency.percentile(95),
    );
  }
}
```

#### 12.3.2 监控数据上报

```yaml
# 上报配置
monitoring:
  enabled: true
  reportInterval: 5m  # 每 5 分钟上报一次
  endpoint: https://monitoring.openclaw.io/api/v1/metrics
  batchSize: 100      # 批量上报条数
  
  # 本地缓存（网络不可用时）
  localCache:
    enabled: true
    maxSize: 10000
    flushOnNetworkRestore: true
```

#### 12.3.3 告警规则

```yaml
# 告警配置
alerts:
  - name: 连接成功率下降
    metric: connectionSuccessRate
    condition: "< 99.5%"
    window: 5m
    severity: P1
    notify: [slack, email]
  
  - name: 消息延迟过高
    metric: messageLatencyP99
    condition: "> 500ms"
    window: 5m
    severity: P2
    notify: [slack]
  
  - name: 断线率异常
    metric: disconnectionRate
    condition: "> 0.5%/hour"
    window: 10m
    severity: P1
    notify: [slack, email, sms]
  
  - name: 重连失败率高
    metric: reconnectSuccessRate
    condition: "< 99%"
    window: 5m
    severity: P2
    notify: [slack]
```

### 12.4 SLA 达标保障措施

| 措施 | 实施方法 | 预期效果 |
|------|----------|----------|
| **多节点冗余** | Gateway 多实例部署、负载均衡 | 单点故障不影响连接 |
| **智能路由** | 根据延迟选择最优节点 | 降低 P99 延迟 |
| **连接池** | 预建立连接、快速切换 | 减少重连耗时 |
| **消息队列** | 本地队列缓存、批量发送 | 降低丢包率 |
| **心跳优化** | 自适应心跳间隔（15-30s） | 及时检测断线 |
| **网络感知** | 监听网络变化、主动重连 | 减少断线时长 |

### 12.5 SLA 报告模板

```markdown
## WebSocket SLA 周报

**报告周期：** 2026-XX-XX 至 2026-XX-XX  
**生成时间：** 2026-XX-XX

### 核心指标

| 指标 | 目标值 | 实际值 | 达标 |
|------|--------|--------|------|
| 连接成功率 | ≥99.9% | 99.95% | ✅ |
| 消息延迟 P99 | <200ms | 165ms | ✅ |
| 断线率 | <0.1%/h | 0.08%/h | ✅ |
| 重连成功率 | ≥99.5% | 99.7% | ✅ |

### 趋势分析

- 连接成功率：环比 +0.02%
- 消息延迟：环比 -10ms
- 断线率：环比 -0.01%/h

### 异常事件

| 时间 | 事件 | 影响 | 处理 |
|------|------|------|------|
| XX-XX 14:30 | Gateway 节点重启 | 连接成功率降至 99.2% | 5 分钟内恢复 |

### 改进建议

1. 优化重连算法，降低 P95 重连耗时
2. 增加 Gateway 节点，提升冗余度
```

---

## 十三、臣等建议

### 13.1 优先级建议

1. **首保 MVP**：优先完成登录、聊天核心功能，确保 4 周内可用
2. **渐进增强**：浏览器、远程桌面作为后续迭代功能
3. **协议优先**：Week 1 即与 Gateway 团队联调，避免后期返工
4. **架构先行**：v2.0 即预留扩展点，避免后续重构
5. **监控先行**：SLA 监控与功能开发同步进行

### 13.2 技术债务防控

- 建立代码审查机制，确保代码质量
- 编写单元测试，覆盖率目标 70%+
- 使用静态分析工具（dart analyze、flutter lint）
- 定期重构，避免技术债务累积
- **每个版本预留 20% 时间用于技术债务清理**
- **每次 Flutter 大版本升级前完成兼容性测试**

### 13.3 版本发布策略

| 版本类型 | 发布周期 | 质量要求 | 发布渠道 |
|----------|----------|----------|----------|
| 大版本 (v2.x) | 4-6 周 | 完整测试 + SLA 验证 | GitHub + Store |
| 小版本 (v2.x.y) | 1-2 周 | 回归测试 | GitHub |
| 热修复 (v2.x.y.z) | 随时 | 关键 Bug | GitHub |

### 13.4 长期演进建议

1. **v2.x 系列**：完善移动端功能，积累用户
2. **v3.0**：跨平台突破，建立插件生态
3. **v4.0+**：AI 深度集成、多模态交互

---

## 十四、结语

臣等谨遵皇上旨意，详查技术细节，并依门下省审核意见补充完善：

1. **Flutter 兼容性测试计划** - 已制定完整测试方案、回滚策略
2. **WebSocket SLA 监控指标** - 已明确连接成功率、延迟、重连指标
3. **风险缓冲预留** - 已从 35 周中预留 5 周作为风险缓冲
4. **里程碑审查节点** - 已设置每 8 周阶段性审查节点

OpenClaw IM 客户端 v2 之开发，技术可行、人力可及、风险可控。版本演进路线清晰，架构扩展性充足，数据迁移方案完备，兼容性测试计划周全，SLA 监控指标明确。若蒙皇上恩准，臣等即刻招募人手，启动项目，按期交付。

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
│   │   │   ├── websocket_service.dart
│   │   │   ├── websocket_monitor.dart  # SLA 监控
│   │   │   └── reconnect_strategy.dart # 重连策略
│   │   ├── storage/
│   │   └── utils/
│   └── shared/
│       ├── widgets/
│       └── theme/
├── assets/
│   ├── noVNC/
│   └── images/
├── test/
│   ├── unit/
│   ├── integration/
│   └── compatibility/  # 兼容性测试
├── .github/
│   └── workflows/
│       └── compatibility-test.yml  # CI/CD 兼容性测试
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
