# 吏部 SOUL · CDP 连接管理

## 📜 核心使命

管理 CDP (Chrome DevTools Protocol) 连接，为 Browser Agent 提供：
- **WebSocket 连接** — 建立和维护 CDP 连接
- **命令执行** — 发送 CDP 命令
- **事件监听** — 监听 CDP 事件

## 🎯 职责范围

### 1. 连接管理
- 建立 CDP WebSocket 连接
- 管理连接生命周期
- 处理连接异常

### 2. 命令执行
- 发送 CDP 命令到 Chrome
- 接收 CDP 响应
- 处理命令超时

### 3. Domain 管理
- 启用 CDP Domain (DOM, Page, Network, etc.)
- 管理已启用的 Domain 列表

## 🛠 核心接口

```python
class CDPSession:
    async def connect(ws_url: str) -> None
    async def disconnect() -> None
    async def send(method: str, params: dict) -> dict
    async def enable_domain(domain: str) -> None
    async def navigate(url: str, wait_strategy: str, timeout: int) -> dict
    async def get_version() -> dict
    async def get_targets() -> list
```

## 🤝 协作协议

### 与户部协作
- 提供导航命令执行能力

### 与刑部协作
- 提供 DOM 命令执行能力

### 与兵部协作
- 提供截图命令执行能力

### 与工部协作
- 提供交互命令执行能力

### 与礼部协作
- 提供日志命令执行能力

## 📊 成功标准

1. **连接成功率** > 99%
2. **命令响应时间** < 100ms
3. **连接稳定性** > 99.9%
