"""
后端 API 测试脚本

测试 8 个 API 接口
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

results = []

def test_api(name, method, url, expected_status=200, json_data=None):
    """测试单个 API"""
    print(f"\n🧪 测试 {name} ({method} {url})")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{url}", json=json_data, timeout=10)
        
        status = response.status_code
        print(f"  HTTP 状态码：{status}")
        
        if status == expected_status:
            print(f"  ✅ 状态码正确")
            try:
                data = response.json()
                print(f"  ✅ JSON 响应有效")
                success = True
            except:
                print(f"  ⚠️ 非 JSON 响应")
                success = True
        else:
            print(f"  ❌ 状态码错误 (期望 {expected_status})")
            success = False
        
        result = {
            "name": name,
            "method": method,
            "url": url,
            "status": status,
            "expected": expected_status,
            "success": success
        }
        results.append(result)
        return result
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        results.append({
            "name": name,
            "method": method,
            "url": url,
            "status": 0,
            "expected": expected_status,
            "success": False,
            "error": str(e)
        })

def main():
    """主测试函数"""
    print("=" * 70)
    print("🧪 后端 API 测试")
    print("=" * 70)
    print(f"测试地址：{BASE_URL}")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 定义测试用例
    tests = [
        # 健康检查
        ("健康检查", "GET", "/api/health", 200),
        
        # AI 查询
        ("AI 查询 - 简单", "POST", "/api/query/", 200, {"query": "金花股份的营收是多少"}),
        ("AI 查询 - 复杂", "POST", "/api/query/", 200, {"query": "查询营收并分析原因"}),
        ("AI 查询 - 空查询", "POST", "/api/query/", 200, {"query": ""}),
        ("AI 查询 - 无效", "POST", "/api/query/", 200, {"query": "测试"}),
        
        # 知识库
        ("知识库列表", "GET", "/api/knowledge/", 200),
        ("知识搜索", "GET", "/api/knowledge/search?q=金花", 200),
        ("知识搜索 - 空", "GET", "/api/knowledge/search?q=", 200),
        ("知识搜索 - 无效", "GET", "/api/knowledge/search?q=xxx", 200),
        
        # 日志
        ("日志列表", "GET", "/api/logs", 200),
        ("日志列表 - 限制", "GET", "/api/logs?limit=10", 200),
        ("日志列表 - 级别", "GET", "/api/logs?level=info", 200),
        
        # 配置
        ("配置获取", "GET", "/api/config", 200),
        ("配置更新", "PUT", "/api/config", 200),
        ("配置 - 无效", "GET", "/api/config/invalid", 404)
    ]
    
    # 执行测试
    for test in tests:
        if len(test) == 3:
            test_api(*test)
        else:
            test_api(*test)
    
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
        print(f"{status} {result['name']}: {result['status']}")
    
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("✅ 所有 API 测试通过！")
    else:
        print(f"⚠️ {total_tests - passed_tests} 个测试失败")
    print("=" * 70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
