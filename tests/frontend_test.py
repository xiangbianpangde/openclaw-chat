"""
前端功能测试脚本

测试 8 个页面的功能
"""

import asyncio
import aiohttp
from datetime import datetime

BASE_URL = "http://localhost:3001"

results = []

async def test_page(session, name, url, checks):
    """测试单个页面"""
    print(f"\n🧪 测试 {name} ({url})")
    
    try:
        async with session.get(f"{BASE_URL}{url}") as response:
            status = response.status
            html = await response.text()
            
            print(f"  HTTP 状态码：{status}")
            
            # 执行检查
            passed = 0
            for check_name, check_str in checks:
                if check_str in html:
                    print(f"  ✅ {check_name}")
                    passed += 1
                else:
                    print(f"  ❌ {check_name}")
            
            result = {
                "name": name,
                "url": url,
                "status": status,
                "passed": passed,
                "total": len(checks),
                "success": status == 200 and passed == len(checks)
            }
            results.append(result)
            return result
            
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        results.append({
            "name": name,
            "url": url,
            "status": 0,
            "passed": 0,
            "total": len(checks),
            "success": False,
            "error": str(e)
        })

async def main():
    """主测试函数"""
    print("=" * 70)
    print("🧪 前端功能测试")
    print("=" * 70)
    print(f"测试地址：{BASE_URL}")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 定义测试用例
    tests = [
        # 首页
        ("首页", "/", [
            ("页面标题", "泰迪杯 B 题智能问数助手"),
            ("功能卡片", "feature-card"),
            ("导航按钮", "进入系统")
        ]),
        
        # 登录页
        ("登录页", "/login", [
            ("用户名输入框", "用户名"),
            ("密码输入框", "密码"),
            ("登录按钮", "登录")
        ]),
        
        # 仪表盘
        ("仪表盘", "/dashboard", [
            ("统计卡片", "stat-card"),
            ("页面标题", "仪表盘"),
            ("快捷操作", "快捷操作")
        ]),
        
        # 智能查询
        ("智能查询", "/analysis", [
            ("查询输入框", "textarea"),
            ("查询按钮", "查询"),
            ("页面标题", "智能查询")
        ]),
        
        # 知识库
        ("知识库", "/knowledge", [
            ("文档列表", "knowledge-base"),
            ("搜索框", "搜索"),
            ("页面标题", "知识库")
        ]),
        
        # 归因分析
        ("归因分析", "/analysis", [
            ("指标选择", "指标"),
            ("归因报告", "归因"),
            ("页面标题", "智能查询")
        ]),
        
        # 系统日志
        ("系统日志", "/logs", [
            ("日志列表", "system-logs"),
            ("过滤器", "过滤"),
            ("页面标题", "系统日志")
        ]),
        
        # 系统设置
        ("系统设置", "/settings", [
            ("配置项", "system-config"),
            ("保存按钮", "保存"),
            ("页面标题", "系统设置")
        ])
    ]
    
    # 执行测试
    async with aiohttp.ClientSession() as session:
        for name, url, checks in tests:
            await test_page(session, name, url, checks)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get("success", False))
    
    print(f"总测试数：{total_tests}")
    print(f"通过：{passed_tests}")
    print(f"失败：{total_tests - passed_tests}")
    print(f"通过率：{(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
    print("=" * 70)
    
    for result in results:
        status = "✅" if result.get("success", False) else "❌"
        print(f"{status} {result['name']}: {result['passed']}/{result['total']} 通过")
    
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("✅ 所有前端功能测试通过！")
    else:
        print(f"⚠️ {total_tests - passed_tests} 个测试失败")
    print("=" * 70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
