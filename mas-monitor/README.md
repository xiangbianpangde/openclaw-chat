# MAS Monitor - MAS 库独立监控 Agent

🤖 **MAS 库独立分析报告生成系统**

## 模型配置

| 用途 | 模型 |
|------|------|
| 默认监控 | `qwen-plus` |
| 代码深度分析 | `qwen-coder-plus` |
| 快速变更检测 | `qwen-turbo` |

## 功能模块

### 1. 代码架构分析 (`scripts/analyze-architecture.js`)
- 项目结构分析
- 模块识别
- 依赖关系图
- 复杂度评估

### 2. 更新日志跟踪 (`scripts/track-changelog.js`)
- Commits 监控
- Releases 跟踪
- 自动生成摘要

### 3. 依赖关系分析 (`scripts/analyze-dependencies.js`)
- 直接依赖
- 开发依赖
- 安全漏洞检测
- 更新建议

### 4. 重大变更检测 (`scripts/detect-major-changes.js`)
- API 变更检测
- 破坏性变更识别
- 风险评估

### 5. 上下文压缩 (`scripts/context-compressor.js`)
- 四层归档：实时 → 小时 → 日 → 周
- Token 优化目标：80%+

## 安装

```bash
cd mas-monitor
npm install
```

## 配置

编辑 `config/agent-config.json`:

```json
{
  "github": {
    "targetRepo": "xiangbianpangde/MAS",
    "analysisRepo": "xiangbianpangde/MAS-Analysis",
    "pollIntervalMinutes": 5
  }
}
```

### GitHub Token 配置

```bash
export GH_TOKEN=your_github_token
```

## 使用

### 启动监控（持续运行）
```bash
npm start
```

### 单次分析
```bash
npm run once
```

### 单独运行模块
```bash
npm run analyze   # 代码架构分析
npm run track     # 更新日志跟踪
npm run deps      # 依赖分析
npm run detect    # 变更检测
npm run compress  # 上下文压缩
```

## 输出目录

```
reports/
├── realtime/     # 实时报告（保留 1 天）
├── hourly/       # 小时报告（保留 7 天）
├── daily/        # 日报（保留 30 天）
└── weekly/       # 周报（保留 90 天）
```

## 创建 GitHub 仓库

```bash
# 手动创建或使用 gh CLI
gh repo create xiangbianpangde/MAS-Analysis --public --description "MAS 库独立分析报告"
```

## 状态监控

查看最新报告：
```bash
cat reports/realtime/summary.json
```

## License

MIT
