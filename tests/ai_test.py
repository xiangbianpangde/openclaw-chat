"""
AI 功能测试脚本

测试 NL2SQL、意图识别、归因分析、知识库检索
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'teddy_cup_project', 'src'))

results = []

def test_nl2sql():
    """测试 NL2SQL"""
    print("\n🧪 测试 NL2SQL")
    
    try:
        from task2.sql_generator import SQLGenerator
        generator = SQLGenerator()
        
        # 测试问题
        questions = [
            "金花股份 2025 年的营收是多少",
            "查询同仁堂的净利润"
        ]
        
        passed = 0
        for q in questions:
            result = generator.generate_sql(q)
            if result.get("sql") or result.get("need_clarification"):
                print(f"  ✅ {q[:20]}...")
                passed += 1
            else:
                print(f"  ❌ {q[:20]}...")
        
        results.append({
            "name": "NL2SQL",
            "passed": passed,
            "total": len(questions),
            "success": passed == len(questions)
        })
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        results.append({
            "name": "NL2SQL",
            "passed": 0,
            "total": 2,
            "success": False,
            "error": str(e)
        })

def test_intent_recognition():
    """测试意图识别"""
    print("\n🧪 测试意图识别")
    
    try:
        from task3.intent_planner import IntentPlanner
        planner = IntentPlanner()
        
        # 测试问题
        questions = [
            "金花股份的营收是多少",
            "查询营收并分析原因"
        ]
        
        passed = 0
        for q in questions:
            intents = planner.parse_intent(q)
            if len(intents) > 0:
                print(f"  ✅ {q[:20]}... ({len(intents)} 意图)")
                passed += 1
            else:
                print(f"  ❌ {q[:20]}...")
        
        results.append({
            "name": "意图识别",
            "passed": passed,
            "total": len(questions),
            "success": passed == len(questions)
        })
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        results.append({
            "name": "意图识别",
            "passed": 0,
            "total": 2,
            "success": False,
            "error": str(e)
        })

def test_attribution():
    """测试归因分析"""
    print("\n🧪 测试归因分析")
    
    try:
        from task3.attribution import AttributionAnalyzer
        analyzer = AttributionAnalyzer()
        
        # 测试归因
        result = analyzer.analyze_change(
            stock="金花股份",
            metric="利润",
            period="2025 年 Q3",
            current_value=1.2,
            previous_value=1.15
        )
        
        if len(result.factors) > 0:
            print(f"  ✅ 归因分析成功 ({len(result.factors)} 因素)")
            passed = 1
        else:
            print(f"  ❌ 归因分析失败")
            passed = 0
        
        results.append({
            "name": "归因分析",
            "passed": passed,
            "total": 1,
            "success": passed == 1
        })
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        results.append({
            "name": "归因分析",
            "passed": 0,
            "total": 1,
            "success": False,
            "error": str(e)
        })

def test_knowledge_retrieval():
    """测试知识库检索"""
    print("\n🧪 测试知识库检索")
    
    try:
        from task3.knowledge_base import KnowledgeBase, create_sample_knowledge_base
        kb = create_sample_knowledge_base()
        
        # 测试查询
        queries = [
            "金花股份",
            "财务指标"
        ]
        
        passed = 0
        for q in queries:
            results_search = kb.search(q, top_k=3)
            if len(results_search) > 0:
                print(f"  ✅ {q[:20]}... ({len(results_search)} 结果)")
                passed += 1
            else:
                print(f"  ❌ {q[:20]}...")
        
        results.append({
            "name": "知识库检索",
            "passed": passed,
            "total": len(queries),
            "success": passed == len(queries)
        })
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        results.append({
            "name": "知识库检索",
            "passed": 0,
            "total": 2,
            "success": False,
            "error": str(e)
        })

def main():
    """主测试函数"""
    print("=" * 70)
    print("🧪 AI 功能测试")
    print("=" * 70)
    print(f"测试时间：2026-04-12 09:17")
    print("=" * 70)
    
    # 执行测试
    test_nl2sql()
    test_intent_recognition()
    test_attribution()
    test_knowledge_retrieval()
    
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
        print(f"{status} {result['name']}: {result['passed']}/{result['total']}")
    
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("✅ 所有 AI 功能测试通过！")
    else:
        print(f"⚠️ {total_tests - passed_tests} 个测试失败")
    print("=" * 70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
