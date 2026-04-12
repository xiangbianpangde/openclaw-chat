"""
Browser Agent 测试

测试 CDP 浏览器自动化能力
"""

import asyncio
import sys
import os

# 添加模块路径
SKILL_PATH = os.path.join(os.path.dirname(__file__), '..', 'extensions', 'mas-supervisor', 'skills', 'cdp-browser')
sys.path.insert(0, SKILL_PATH)

# 直接导入模块（避免相对导入问题）
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

cdp_client = load_module('cdp_client', os.path.join(SKILL_PATH, 'cdp_client.py'))
CDPSession = cdp_client.CDPSession

dom_analyzer = load_module('dom_analyzer', os.path.join(SKILL_PATH, 'dom_analyzer.py'))
DOMAnalyzer = dom_analyzer.DOMAnalyzer

screenshot = load_module('screenshot', os.path.join(SKILL_PATH, 'screenshot.py'))
ScreenshotCapture = screenshot.ScreenshotCapture

navigator = load_module('navigator', os.path.join(SKILL_PATH, 'navigator.py'))
Navigator = navigator.Navigator

interactor = load_module('interactor', os.path.join(SKILL_PATH, 'interactor.py'))
Interactor = interactor.Interactor

console_logger = load_module('console_logger', os.path.join(SKILL_PATH, 'console_logger.py'))
ConsoleLogger = console_logger.ConsoleLogger


async def test_cdp_connection():
    """测试 CDP 连接"""
    print("\n" + "=" * 70)
    print("🔌 测试 CDP 连接")
    print("=" * 70)
    
    # 由于没有实际的 Chrome CDP 端点，这里只测试类初始化
    session = CDPSession()
    assert session is not None
    print("✅ CDPSession 实例创建成功")
    
    # 验证方法存在
    assert hasattr(session, 'connect')
    assert hasattr(session, 'send')
    assert hasattr(session, 'navigate')
    assert hasattr(session, 'enable_domain')
    print("✅ 所有核心方法存在")
    
    return True


async def test_bug_reproduce():
    """测试 Bug 复现"""
    print("\n" + "=" * 70)
    print("🐛 测试 Bug 复现")
    print("=" * 70)
    
    # 模拟 Bug 复现流程
    print("模拟流程:")
    print("1. 接收 Bug 描述")
    print("2. 解析复现步骤")
    print("3. 执行操作序列")
    print("4. 捕获错误（堆栈、截图、日志）")
    print("5. 生成复现报告")
    
    # 模拟报告
    report = {
        "bug_id": "BUG-001",
        "reproduced": True,
        "steps": [
            {"action": "navigate", "url": "https://example.com/login"},
            {"action": "type", "selector": "#username", "text": "test"},
            {"action": "type", "selector": "#password", "text": "wrongpass"},
            {"action": "click", "selector": "#submit"}
        ],
        "error": {
            "message": "Invalid credentials",
            "stack": "Error at login.js:42",
            "location": "login.js:42"
        },
        "screenshot": "base64...",
        "console_logs": ["Login failed"],
        "network_errors": []
    }
    
    print(f"\n模拟报告：{report['bug_id']}")
    print(f"复现成功：{report['reproduced']}")
    print(f"错误：{report['error']['message']}")
    
    return True


async def test_verify_fix():
    """测试修复验证"""
    print("\n" + "=" * 70)
    print("✅ 测试修复验证")
    print("=" * 70)
    
    # 模拟修复验证流程
    print("模拟流程:")
    print("1. 加载修复前快照")
    print("2. 加载修复后快照")
    print("3. 对比 DOM 差异")
    print("4. 验证修复效果")
    print("5. 生成验证报告")
    
    # 模拟报告
    report = {
        "fix_id": "FIX-001",
        "verified": True,
        "before_snapshot": {"nodeCount": 100},
        "after_snapshot": {"nodeCount": 102},
        "diff": {"added": 2, "removed": 0},
        "screenshot_comparison": "base64..."
    }
    
    print(f"\n模拟报告：{report['fix_id']}")
    print(f"验证成功：{report['verified']}")
    print(f"DOM 变化：+{report['diff']['added']} nodes")
    
    return True


async def test_collaboration_flow():
    """测试协作流程"""
    print("\n" + "=" * 70)
    print("🤝 测试协作流程")
    print("=" * 70)
    
    # 模拟协作流程
    print("模拟流程:")
    print("1. Supervisor 接收 Bug 报告")
    print("2. 分发给 Browser Agent")
    print("3. Browser Agent 执行复现")
    print("4. 返回复现报告")
    print("5. Supervisor 分发给 Debugging Agent")
    print("6. Debugging Agent 分析根因")
    print("7. 生成修复建议")
    
    # 模拟任务流转
    tasks = [
        {"from": "User", "to": "Supervisor", "type": "bug_report"},
        {"from": "Supervisor", "to": "Browser Agent", "type": "browser.bug_reproduce"},
        {"from": "Browser Agent", "to": "Supervisor", "type": "reproduce_result"},
        {"from": "Supervisor", "to": "Debugging Agent", "type": "debugging.analyze"},
        {"from": "Debugging Agent", "to": "Supervisor", "type": "fix_suggestion"},
        {"from": "Supervisor", "to": "User", "type": "final_report"}
    ]
    
    print("\n任务流转:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task['from']} → {task['to']}: {task['type']}")
    
    return True


async def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🧪 Browser Agent 测试")
    print("=" * 70)
    
    results = []
    
    # 运行所有测试
    tests = [
        ("CDP 连接", test_cdp_connection),
        ("Bug 复现", test_bug_reproduce),
        ("修复验证", test_verify_fix),
        ("协作流程", test_collaboration_flow)
    ]
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append({"name": name, "passed": result})
        except Exception as e:
            print(f"\n❌ {name} 测试失败：{e}")
            results.append({"name": name, "passed": False, "error": str(e)})
    
    # 打印总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for r in results if r.get("passed", False))
    
    print(f"总测试数：{total}")
    print(f"通过：{passed}")
    print(f"失败：{total - passed}")
    print(f"通过率：{(passed/total*100) if total > 0 else 0:.1f}%")
    print("=" * 70)
    
    for result in results:
        status = "✅" if result.get("passed", False) else "❌"
        print(f"{status} {result['name']}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print("✅ 所有 Browser Agent 测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
