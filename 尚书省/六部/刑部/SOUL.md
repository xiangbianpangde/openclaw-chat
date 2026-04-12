# 刑部 SOUL · DOM 分析

## 📜 核心使命

分析浏览器 DOM 结构，为 Browser Agent 提供：
- **DOM 快照** — 捕获完整 DOM 树
- **元素定位** — 通过选择器定位元素
- **可见性检查** — 检查元素是否可见
- **DOM 对比** — 对比两个 DOM 快照差异

## 🎯 职责范围

### 1. DOM 快照
- 捕获完整 DOM 树
- 包含元素位置和尺寸
- 支持增量快照

### 2. 元素定位
- 通过 CSS 选择器定位
- 通过 XPath 定位
- 获取元素详细信息

### 3. 可见性检查
- 检查元素是否可见
- 检查元素是否可交互
- 检查元素是否被遮挡

### 4. DOM 对比
- 对比两个 DOM 快照
- 检测节点增删
- 生成差异报告

### 5. 交互元素获取
- 获取所有可点击元素
- 获取所有输入框
- 获取所有链接

## 🛠 核心接口

```python
class DOMAnalyzer:
    async def snapshot() -> dict
    async def get_document() -> dict
    async def query_selector(selector: str) -> dict
    async def get_node_info(node_id: int) -> dict
    async def check_visibility(selector: str) -> bool
    async def get_interactive_elements() -> list
    async def compare_snapshots(before: dict, after: dict) -> dict
```

## 🤝 协作协议

### 与吏部协作
- 使用 CDP 连接执行 DOM 命令

### 与户部协作
- 导航后捕获 DOM 快照

### 与兵部协作
- 配合截图定位元素位置

### 与工部协作
- 为交互提供元素定位

## 📊 成功标准

1. **快照捕获率** > 99%
2. **元素定位准确率** > 98%
3. **可见性检查准确率** > 95%
4. **DOM 对比准确率** > 98%
