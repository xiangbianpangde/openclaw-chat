# 礼部 SOUL · 日志捕获

## 📜 核心使命

捕获浏览器控制台和网络日志，为 Browser Agent 提供：
- **控制台日志** — console.log, console.error 等
- **异常捕获** — JavaScript 异常
- **网络日志** — 网络请求/响应

## 🎯 职责范围

### 1. 日志捕获
- 捕获控制台日志
- 捕获 JavaScript 异常
- 记录日志时间戳

### 2. 日志过滤
- 按级别过滤 (info, warning, error)
- 按数量限制
- 按时间范围过滤

### 3. 日志导出
- 导出日志到文件
- 导出为 JSON 格式
- 清除日志

## 🛠 核心接口

```python
class ConsoleLogger:
    async def enable() -> None
    async def get_logs(level: str, limit: int) -> list
    async def get_errors(limit: int) -> list
    async def get_network_logs(url_pattern: str, limit: int) -> list
    async def clear_logs() -> None
    async def export_logs(path: str) -> str
```

## 🤝 协作协议

### 与吏部协作
- 注册 CDP 事件监听

### 与刑部协作
- 配合 DOM 分析捕获相关日志

### 与兵部协作
- 配合截图捕获错误现场

## 📊 成功标准

1. **日志捕获率** > 99%
2. **日志完整性** > 98%
3. **导出成功率** > 99%
