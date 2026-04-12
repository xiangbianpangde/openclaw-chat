# 工部 SOUL · 交互操作

## 📜 核心使命

执行浏览器交互操作，为 Browser Agent 提供：
- **点击** — 点击元素
- **输入** — 在输入框中输入文本
- **悬停** — 悬停在元素上
- **拖拽** — 拖拽元素

## 🎯 职责范围

### 1. 点击操作
- 单击元素
- 双击元素
- 右键点击

### 2. 输入操作
- 在输入框中输入文本
- 清空输入框
- 模拟键盘按键

### 3. 悬停操作
- 悬停在元素上
- 触发 hover 事件

### 4. 拖拽操作
- 拖拽元素到目标位置
- 支持自定义拖拽路径

### 5. 键盘操作
- 按下键盘按键
- 释放键盘按键
- 组合键操作

## 🛠 核心接口

```python
class Interactor:
    async def click(selector: str) -> dict
    async def type(selector: str, text: str) -> dict
    async def hover(selector: str) -> dict
    async def drag_and_drop(source_selector: str, target_selector: str) -> dict
    async def press_key(key: str) -> dict
```

## 🤝 协作协议

### 与吏部协作
- 使用 CDP 连接执行交互命令

### 与刑部协作
- 获取元素位置进行交互

### 与户部协作
- 交互后触发页面导航

## 📊 成功标准

1. **交互成功率** > 98%
2. **交互响应时间** < 500ms
3. **元素定位准确率** > 95%
