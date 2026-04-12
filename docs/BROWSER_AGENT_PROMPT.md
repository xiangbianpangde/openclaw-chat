# Browser Agent Skill — Chrome DevTools 协议集成

## 任务概述

创建基于 Chrome DevTools Protocol (CDP) 的 Browser Agent，专门处理 UI 自动化、DOM 快照、屏幕截图、页面导航和 UI 行为推理任务。

---

## 背景

团队已接入 Chrome DevTools 协议到智能体运行时，需要创建专门的 Browser Agent 来：
- 复现错误
- 验证修复
- 直接推理 UI 行为
- 执行浏览器自动化任务

---

## 需求清单

### 1. 创建 Browser Agent SOUL

**文件路径：** `mas_agents/browser/SOUL.md`

**核心职责：**
- CDP 驱动管理
- DOM 快照捕获
- 屏幕截图（全页/元素级）
- 页面导航控制
- UI 行为推理

**必需能力：**

| 能力 | 方法 | 说明 |
|------|------|------|
| DOM 快照 | `cdp_snapshot()` | 获取完整 DOM 树，包含元素位置、样式、可见性 |
| 屏幕截图 | `cdp_screenshot(selector=None, full_page=True)` | 全页截图或指定元素截图 |
| 导航控制 | `cdp_navigate(url, wait_strategy=None, timeout=30000)` | URL 跳转 + 等待策略 |
| 交互操作 | `click(selector)`, `type(selector, text)`, `hover(selector)` | 模拟用户行为 |
| JavaScript 执行 | `cdp_evaluate(js_code)` | 在页面上下文执行 JS |
| 控制台捕获 | `cdp_console()` | 捕获 console.log/error/warn |

**SOUL 结构要求：**
```markdown
# Browser Agent SOUL

## 身份
你是 Browser Agent，专门负责浏览器自动化和 UI 测试任务。

## 能力
- Chrome DevTools Protocol 连接
- DOM 快照捕获
- 屏幕截图
- 页面导航
- 用户交互模拟
- UI 行为推理

## 工作流程
1. 接收任务（task_type="browser"）
2. 建立 CDP 连接
3. 执行浏览器操作
4. 捕获结果（DOM/截图/日志）
5. 输出结构化报告

## 约束
- 必须先启动 Chrome（--remote-debugging-port=9222）
- 所有操作需要超时保护
- 敏感信息不记录
```

---

### 2. 创建 CDP Skill

**文件路径：** `extensions/mas-supervisor/skills/cdp-browser/__init__.py`

**核心功能：**
- Python CDP 客户端实现
- WebSocket 连接管理
- CDP Domain 启用
- 事件监听

**必需模块：**

| 模块 | 文件 | 功能 |
|------|------|------|
| CDP Client | `cdp_client.py` | WebSocket 连接、命令发送、事件监听 |
| DOM Analyzer | `dom_analyzer.py` | DOM 解析、元素查询、可见性检查 |
| Screenshot | `screenshot.py` | 截图捕获、保存、标注 |
| Navigator | `navigator.py` | URL 跳转、等待策略、历史管理 |
| Interactor | `interactor.py` | click/type/hover 实现 |
| Console | `console_logger.py` | 控制台日志捕获 |

**CDP Client 接口要求：**
```python
class CDPSession:
    async def __aenter__(self) -> 'CDPSession':
        """建立 CDP 连接"""
        pass
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """断开连接"""
        pass
    
    async def navigate(self, url: str, wait_strategy: str = None, timeout: int = 30000):
        """导航到 URL"""
        pass
    
    async def snapshot(self) -> DOMSnapshot:
        """获取 DOM 快照"""
        pass
    
    async def screenshot(self, selector: str = None, full_page: bool = True) -> bytes:
        """截图"""
        pass
    
    async def click(self, selector: str):
        """点击元素"""
        pass
    
    async def type(self, selector: str, text: str):
        """输入文本"""
        pass
    
    async def evaluate(self, js_code: str) -> any:
        """执行 JavaScript"""
        pass
    
    async def console(self) -> List[ConsoleMessage]:
        """获取控制台消息"""
        pass
```

---

### 3. 更新 Supervisor SOUL

**文件路径：** `supervisor/SOUL.md`

**新增任务类型：** `browser`

**调度逻辑：**
```markdown
## 任务类型

### browser
- **描述**: 浏览器自动化任务
- **执行者**: Browser Agent
- **前置条件**: Chrome 已启动（--remote-debugging-port=9222）
- **超时**: 300 秒
- **重试**: 2 次

### 协作流程
```
Supervisor
 └── task_type="browser"
     └── Browser Agent (CDP Session)
         ├── 复现 Bug → Code Agent 生成修复
         ├── 截图对比 → Review Agent 验证
         └── 输出结构化报告 → Supervisor 聚合
```
```

**新增字段：**
- `task_type`: 支持 "browser"
- `browser_config`: CDP 配置（host, port, timeout）

---

### 4. 测试协作流程

**测试脚本路径：** `tests/browser_agent_test.py`

**测试场景：**

#### 场景 1：Bug 复现
```python
async def test_bug_reproduce():
    """测试 Bug 复现流程"""
    async with CDPSession() as cdp:
        # 导航到登录页
        await cdp.navigate("https://example.com/login")
        
        # 输入错误密码
        await cdp.type("#username", "test")
        await cdp.type("#password", "wrongpass")
        await cdp.click("#submit")
        
        # 等待错误消息
        await cdp.wait_for(".error-message", timeout=5000)
        
        # 捕获 DOM 和截图
        snapshot = await cdp.snapshot()
        screenshot = await cdp.screenshot()
        errors = await cdp.console()
        
        # 生成复现报告
        report = {
            "url": "https://example.com/login",
            "steps": [
                {"action": "navigate", "url": "..."},
                {"action": "type", "selector": "#username", "text": "test"},
                {"action": "type", "selector": "#password", "text": "wrongpass"},
                {"action": "click", "selector": "#submit"},
            ],
            "error": {
                "message": "Invalid credentials",
                "selector": ".error-message",
            },
            "dom_snapshot": snapshot.dom_tree,
            "screenshot": screenshot,
            "console_errors": errors,
        }
        
        return report
```

#### 场景 2：修复验证
```python
async def test_fix_verification():
    """测试修复验证流程"""
    # 修复前截图
    before = await cdp.screenshot()
    
    # 执行修复（Code Agent 生成）
    await apply_fix()
    
    # 修复后截图
    after = await cdp.screenshot()
    
    # 对比验证
    diff = compare_screenshots(before, after)
    assert diff.has_changes
    assert not diff.has_errors
    
    return {"status": "verified", "diff": diff}
```

---

### 5. GitHub 同步要求

**提交规范：**
```bash
# 1. Browser Agent SOUL
git add mas_agents/browser/SOUL.md
git commit -m "feat(browser): 创建 Browser Agent SOUL

- 添加 CDP 驱动能力
- 支持 DOM 快照、截图、导航
- UI 行为推理
"

# 2. CDP Skill
git add extensions/mas-supervisor/skills/cdp-browser/
git commit -m "feat(skill): 创建 CDP Browser Skill

- Python CDP 客户端
- DOM Analyzer
- Screenshot 模块
- Navigator 模块
"

# 3. Supervisor 更新
git add supervisor/SOUL.md
git commit -m "feat(supervisor): 添加 browser 任务类型

- 支持 task_type='browser'
- Browser Agent 调度
- 协作流程定义
"

# 4. 测试
git add tests/browser_agent_test.py
git commit -m "test(browser): 添加 Browser Agent 测试

- Bug 复现测试
- 修复验证测试
- 协作流程测试
"

# 5. 统一推送
git push origin main
```

**提交后汇报：**
```markdown
## GitHub 同步完成

**提交哈希：** `<commit_hash>`

**修改文件：**
- mas_agents/browser/SOUL.md
- extensions/mas-supervisor/skills/cdp-browser/*
- supervisor/SOUL.md
- tests/browser_agent_test.py

**仓库：** https://github.com/Nanako-Arasaka/teddy-cup-b
```

---

## 执行顺序

1. **创建 Browser Agent SOUL** (15 分钟)
2. **创建 CDP Skill** (30 分钟)
3. **更新 Supervisor SOUL** (10 分钟)
4. **编写测试** (20 分钟)
5. **测试协作流程** (20 分钟)
6. **GitHub 同步** (5 分钟)

**总计：** 100 分钟

---

## 验收标准

| 标准 | 验证方式 |
|------|---------|
| Browser Agent SOUL 创建 | 文件存在，结构完整 |
| CDP Skill 可用 | 可建立连接，执行命令 |
| Supervisor 调度 | task_type="browser" 可触发 |
| Bug 复现 | 可复现指定 Bug，生成报告 |
| 修复验证 | 可对比修复前后，验证效果 |
| GitHub 同步 | 所有文件已提交并推送 |

---

## 前置要求

**启动 Chrome：**
```bash
google-chrome --remote-debugging-port=9222 --no-first-run --no-default-browser-check
```

**或 macOS：**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

---

## 使用示例

```python
from mas_agents.browser import BrowserAgent

async def main():
    agent = BrowserAgent()
    
    async with agent.cdp_session() as cdp:
        # 导航
        await cdp.navigate("https://example.com/login")
        
        # 等待元素
        await cdp.wait_for("#username", timeout=5000)
        
        # 交互
        await cdp.type("#username", "test@example.com")
        await cdp.type("#password", "password123")
        await cdp.click("#submit")
        
        # 捕获结果
        snapshot = await cdp.snapshot()
        screenshot = await cdp.screenshot()
        errors = await cdp.console()
        
        # 输出报告
        print(f"DOM 节点数：{snapshot.node_count}")
        print(f"控制台错误：{len(errors)}")
        print(f"截图大小：{len(screenshot)} bytes")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 注意事项

1. **Chrome 必须预先启动**
2. **所有操作需要超时保护**
3. **敏感信息（密码等）不记录到日志**
4. **截图使用 base64 编码存储**
5. **DOM 快照使用结构化格式**

---

## 相关文件

- `mas_agents/browser/SOUL.md` — Browser Agent SOUL
- `extensions/mas-supervisor/skills/cdp-browser/` — CDP Skill
- `supervisor/SOUL.md` — Supervisor 配置
- `tests/browser_agent_test.py` — 测试脚本
- `docs/BROWSER_AGENT.md` — 使用文档

---

**任务完成条件：** 所有文件创建完成，测试通过，GitHub 同步完成。
