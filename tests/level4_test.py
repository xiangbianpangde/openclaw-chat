#!/usr/bin/env python3
"""
泰迪杯 B 题网站 LEVEL_4 全面测试

LEVEL_4 标准：验证页面有真实数据，不仅仅是元素存在
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

BASE_URL = "https://bright-delaware-join-sri.trycloudflare.com"
SCREENSHOT_DIR = "tests/screenshots_level4"

# LEVEL_4 断言函数
async def assert_page_has_data(page, selector, error_messages=[]):
    """
    LEVEL_4 断言：页面有真实数据
    
    Args:
        page: Playwright page
        selector: CSS 选择器
        error_messages: 额外错误消息列表
    """
    # 1. 检查元素存在
    elements = await page.query_selector_all(selector)
    assert len(elements) > 0, f"应该有{selector}元素"
    
    # 2. 检查没有错误消息
    content = await page.content()
    default_errors = ['暂无数据', '加载失败', '错误', 'Error', 'Failed']
    all_errors = default_errors + error_messages
    
    for error in all_errors:
        assert error not in content, f"不应显示'{error}'"
    
    # 3. 检查有真实数据（表格行数、列表项等）
    if 'table' in selector.lower() or 'tr' in selector.lower():
        rows = await page.query_selector_all('table tr')
        assert len(rows) > 1, "表格应该有数据行（除了表头）"
    
    return True

async def assert_page_not_empty(page, check_selectors=[]):
    """
    LEVEL_4 断言：页面不为空
    
    Args:
        page: Playwright page
        check_selectors: 需要检查的选择器列表
    """
    content = await page.content()
    
    # 检查常见空页面消息
    empty_messages = [
        '暂无数据', '没有数据', '加载失败', 'Error',
        'Failed to load', '空页面', 'Empty'
    ]
    
    for msg in empty_messages:
        assert msg not in content, f"页面不应显示'{msg}'"
    
    # 检查指定选择器有内容
    for selector in check_selectors:
        elements = await page.query_selector_all(selector)
        assert len(elements) > 0, f"页面应该有{selector}元素"
    
    return True

async def test_page_level4(browser, name, url, checks):
    """
    LEVEL_4 测试单个页面
    
    Args:
        browser: Playwright browser
        name: 页面名称
        url: 页面路径
        checks: 检查列表 [(selector, error_messages)]
    """
    print(f"\n🧪 LEVEL_4 测试 {name} ({url})")
    
    try:
        page = await browser.new_page()
        
        # 导航到页面
        await page.goto(f"{BASE_URL}{url}", wait_until="networkidle")
        
        # 等待页面渲染
        await page.wait_for_timeout(3000)
        
        # 获取页面信息
        title = await page.title()
        content = await page.content()
        
        print(f"  页面标题：{title}")
        print(f"  内容长度：{len(content)}")
        
        # 执行 LEVEL_4 检查
        passed = 0
        failed_checks = []
        
        for check_item in checks:
            selector = check_item[0]
            error_messages = check_item[1] if len(check_item) > 1 else []
            
            try:
                await assert_page_has_data(page, selector, error_messages)
                print(f"  ✅ {selector}")
                passed += 1
            except AssertionError as e:
                print(f"  ❌ {selector}: {e}")
                failed_checks.append((selector, str(e)))
        
        # 截图取证
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        screenshot_path = f"{SCREENSHOT_DIR}/{name.replace('/', '_')}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"  📸 截图：{screenshot_path}")
        
        # 如果有失败的检查，在截图上标注
        if failed_checks:
            print(f"  ⚠️ {len(failed_checks)} 个检查失败")
        
        result = {
            "name": name,
            "url": url,
            "title": title,
            "content_length": len(content),
            "passed": passed,
            "total": len(checks),
            "success": len(failed_checks) == 0,
            "failed_checks": failed_checks,
            "screenshot": screenshot_path
        }
        
        await page.close()
        return result
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return {
            "name": name,
            "url": url,
            "title": "",
            "content_length": 0,
            "passed": 0,
            "total": len(checks),
            "success": False,
            "failed_checks": [("error", str(e))],
            "screenshot": ""
        }

async def main():
    """主测试函数"""
    print("=" * 70)
    print("🧪 泰迪杯 B 题网站 LEVEL_4 全面测试")
    print("=" * 70)
    print(f"测试地址：{BASE_URL}")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试标准：LEVEL_4（验证真实数据）")
    print("=" * 70)
    
    # LEVEL_4 测试用例
    tests = [
        # 首页
        ("首页", "/", [
            (".feature-card", ["暂无数据"]),
            ("text=进入系统", []),
            ("text=泰迪杯", [])
        ]),
        
        # 登录页
        ("登录页", "/login", [
            ("input[placeholder='用户名']", []),
            ("input[placeholder='密码']", []),
            ("button:has-text('登录')", [])
        ]),
        
        # 仪表盘
        ("仪表盘", "/dashboard", [
            (".stat-card", ["暂无数据"]),
            ("text=快捷操作", []),
            ("table tr", ["暂无数据"])  # 任务列表应该有数据
        ]),
        
        # 智能查询
        ("智能查询", "/analysis", [
            ("textarea", []),
            ("button:has-text('查询')", []),
            ("text=智能查询", [])
        ]),
        
        # 知识库
        ("知识库", "/knowledge", [
            (".knowledge-base", ["暂无数据", "加载失败"]),
            ("table tr", ["暂无数据"]),  # 文档列表应该有数据
            ("input[placeholder*='搜索']", [])
        ]),
        
        # 归因分析
        ("归因分析", "/attribution", [
            ("text=指标", []),
            ("text=归因", []),
            ("select", [])  # 应该有指标选择下拉框
        ]),
        
        # 系统日志
        ("系统日志", "/logs", [
            (".system-logs", ["暂无数据", "加载失败"]),
            ("table tr", ["暂无数据"]),  # 日志列表应该有数据
            ("text=过滤", [])
        ]),
        
        # 系统设置
        ("系统设置", "/config", [
            (".system-config", ["暂无数据", "空页面"]),
            ("button:has-text('保存')", []),
            ("form", [])  # 应该有配置表单
        ])
    ]
    
    results = []
    
    # 启动浏览器
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 执行测试
        for name, url, checks in tests:
            result = await test_page_level4(browser, name, url, checks)
            results.append(result)
        
        await browser.close()
    
    # 打印总结
    print("\n" + "=" * 70)
    print("📊 LEVEL_4 测试总结")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get("success", False))
    
    print(f"总测试数：{total_tests}")
    print(f"通过：{passed_tests}")
    print(f"失败：{total_tests - passed_tests}")
    print(f"LEVEL_4 通过率：{(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
    print("=" * 70)
    
    for result in results:
        status = "✅" if result.get("success", False) else "❌"
        screenshot = result.get("screenshot", "N/A")
        print(f"{status} {result['name']}: {result['passed']}/{result['total']} (截图：{screenshot})")
        
        # 显示失败详情
        if result.get("failed_checks"):
            for selector, error in result["failed_checks"]:
                print(f"    ❌ {selector}: {error}")
    
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("✅ 所有 LEVEL_4 测试通过！")
    else:
        print(f"⚠️ {total_tests - passed_tests} 个页面未通过 LEVEL_4 标准")
        print("\n发现问题:")
        for result in results:
            if not result.get("success", False):
                print(f"  ⚠️ {result['name']}: {len(result.get('failed_checks', []))} 个问题")
    print("=" * 70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
