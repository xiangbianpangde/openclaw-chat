# MAS-Analysis: 独立分析报告库

[![Powered By OpenClaw](https://img.shields.io/badge/Powered%20By-OpenClaw-blue?logo=openclaw)](https://github.com/openclaw)
[![Monitor: Active](https://img.shields.io/badge/Monitor-Active-brightgreen)](.)
[![Analysis: Auto](https://img.shields.io/badge/Analysis-Automatic-blue)](.)

> **MAS 库的独立分析与监控报告生成系统**

---

## 📋 概述

本仓库是 **AutoMAS** 项目的独立分析报告库，由 MAS Monitor Agent 自动生成并维护。

- **监控目标**: [xiangbianpangde/MAS](https://github.com/xiangbianpangde/MAS)
- **报告类型**: 代码架构、更新日志、依赖分析、变更检测
- **更新频率**: 每 5 分钟自动轮询
- **模型配置**: qwen-plus / qwen-coder-plus / qwen-turbo

---

## 📊 报告目录

```
reports/
├── realtime/         # 实时报告（保留 1 天）
│   ├── summary.json              # 综合摘要
│   ├── architecture-analysis.json # 代码架构
│   └── major-changes.json        # 重大变更
├── hourly/           # 小时报告（保留 7 天）
│   └── changelog.json            # 更新日志
├── daily/            # 日报（保留 30 天）
│   └── dependency-analysis.json  # 依赖分析
└── weekly/           # 周报（保留 90 天）
    └── weekly-summary.json       # 周度总结
```

---

## 🔍 分析内容

### 1. 代码架构分析
- 项目结构可视化
- 模块依赖关系图
- 代码复杂度评估
- 架构演进追踪

### 2. 更新日志跟踪
- Commits 自动摘要
- Releases 版本对比
- 关键变更提取
- 趋势分析

### 3. 依赖关系分析
- 直接/间接依赖图谱
- 安全漏洞检测
- 版本更新建议
- 兼容性评估

### 4. 重大变更检测
- API 破坏性变更
- 配置格式变更
- 核心逻辑重构
- 风险评估报告

---

## ⚙️ 监控配置

| 参数 | 值 |
|------|-----|
| 轮询间隔 | 5 分钟 |
| 默认模型 | qwen-plus |
| 代码分析模型 | qwen-coder-plus |
| 变更检测模型 | qwen-turbo |
| 上下文压缩 | 80%+ Token 优化 |
| 归档层级 | 实时 → 小时 → 日 → 周 |

---

## 📈 查看最新报告

### 实时摘要
```bash
cat reports/realtime/summary.json
```

### 最新架构分析
```bash
cat reports/realtime/architecture-analysis.json
```

### 重大变更
```bash
cat reports/realtime/major-changes.json
```

---

## 🤖 MAS Monitor Agent

本仓库由 **MAS Monitor Agent** 自动维护：

- **会话名称**: `mas-monitor`
- **运行模式**: 独立运行
- **工作目录**: `/root/.openclaw/workspace-taizi/mas-monitor`

### Agent 架构

```
mas-monitor/
├── index.js                  # 主监控程序
├── config/
│   ├── agent-config.json     # Agent 配置
│   └── session-config.json   # 会话配置
├── scripts/
│   ├── analyze-architecture.js   # 架构分析
│   ├── track-changelog.js        # 日志跟踪
│   ├── analyze-dependencies.js   # 依赖分析
│   ├── detect-major-changes.js   # 变更检测
│   └── context-compressor.js     # 上下文压缩
└── reports/                  # 报告输出
```

---

## 📅 报告时间线

| 报告类型 | 生成频率 | 保留时间 |
|----------|----------|----------|
| 实时报告 | 每 5 分钟 | 24 小时 |
| 小时报告 | 每小时 | 7 天 |
| 日报 | 每天 | 30 天 |
| 周报 | 每周 | 90 天 |

---

## 🔔 通知机制

当检测到以下内容时，将触发特别报告：

- ⚠️ **破坏性变更** (Breaking Changes)
- 🔴 **高危漏洞** (Critical Vulnerabilities)
- 🚀 **重大版本发布** (Major Releases)
- 📉 **架构退化** (Architecture Degradation)

---

## 📝 使用示例

### 查看最近 24 小时变更
```bash
jq '.changes | map(select(.timestamp > (now - 86400)))' reports/realtime/major-changes.json
```

### 生成周报摘要
```bash
node scripts/context-compressor.js
```

### 手动触发分析
```bash
cd /root/.openclaw/workspace-taizi/mas-monitor
npm run once
```

---

## 🌐 相关链接

| 仓库 | 描述 |
|------|------|
| [MAS](https://github.com/xiangbianpangde/MAS) | AutoMAS 主仓库 |
| [OpenClaw](https://github.com/openclaw) | 底层框架 |
| [MAS Monitor](../mas-monitor/) | 监控 Agent 源码 |

---

## 📜 许可证

MIT License - 与 MAS 主仓库保持一致

---

<div align="center">

**MAS-Analysis —— 洞察每一次进化**

[🔍 查看实时报告](reports/realtime/summary.json) | [📖 MAS 主仓库](https://github.com/xiangbianpangde/MAS) | [⚙️ Monitor 配置](config/agent-config.json)

</div>
