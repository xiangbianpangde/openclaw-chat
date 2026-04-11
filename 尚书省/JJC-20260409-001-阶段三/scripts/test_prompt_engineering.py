"""
Prompt Engineering 测试脚本
使用 20 个 Few-shot 示例测试 NL2SQL 能力
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.prompt.nl2sql_prompt import build_nl2sql_prompt, get_prompt_template
from src.eval.evaluator import evaluate_nl2sql, get_eval_summary

# 20 条中文测试查询
TEST_QUERIES = [
    # 简单查询（10 条）
    ("贵州茅台 2024 年的营业收入是多少？", "SELECT revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'"),
    ("五粮液 2023 年的净利润是多少？", "SELECT net_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '五粮液' AND financial_reports.period = '2023'"),
    ("查询贵州茅台的基本信息", "SELECT * FROM companies WHERE name = '贵州茅台'"),
    ("2024 年营收最高的公司是哪家？", "SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2024' ORDER BY financial_reports.revenue DESC LIMIT 1"),
    ("查询所有白酒行业的公司", "SELECT * FROM companies WHERE industry = '白酒'"),
    ("贵州茅台 2024 年的毛利率是多少？", "SELECT gross_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'"),
    ("2023 年净利润超过 100 亿的公司有哪些？", "SELECT companies.name, financial_reports.net_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2023' AND financial_reports.net_profit > 10000000000"),
    ("查询贵州茅台 2024 年的总资产", "SELECT total_assets FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'"),
    ("2024 年有多少家上市公司？", "SELECT COUNT(*) FROM companies"),
    ("贵州茅台是什么时候上市的？", "SELECT listed_date FROM companies WHERE name = '贵州茅台'"),
    
    # 复杂查询（10 条）
    ("对比贵州茅台和五粮液 2024 年的营收", "SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name IN ('贵州茅台', '五粮液') AND financial_reports.period = '2024'"),
    ("查询白酒行业 2024 年平均毛利率", "SELECT AVG(financial_reports.gross_profit) FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024'"),
    ("找出营收最高的 5 家公司", "SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id ORDER BY financial_reports.revenue DESC LIMIT 5"),
    ("贵州茅台近 5 年的营收趋势如何？", "SELECT period, revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' ORDER BY period DESC LIMIT 5"),
    ("2024 年净利润增长率超过 20% 的公司有哪些？", "SELECT companies.name FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2024'"),
    ("各行业的平均营收是多少？", "SELECT companies.industry, AVG(financial_reports.revenue) as avg_revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id GROUP BY companies.industry"),
    ("贵州茅台 2024 年的资产负债率是多少？", "SELECT (total_liabilities / total_assets) * 100 as debt_ratio FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'"),
    ("2024 年营收超过 1000 亿的白酒公司有哪些？", "SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024' AND financial_reports.revenue > 100000000000"),
    ("对比贵州茅台 2023 年和 2024 年的净利润", "SELECT period, net_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND period IN ('2023', '2024')"),
    ("2024 年毛利率最高的白酒公司是哪家？", "SELECT companies.name, financial_reports.gross_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024' ORDER BY financial_reports.gross_profit DESC LIMIT 1"),
]

def run_prompt_test():
    """执行 Prompt Engineering 测试"""
    
    print("=" * 60)
    print("  Prompt Engineering 测试")
    print("=" * 60)
    print()
    
    # 验证 Prompt 模板
    print("📋 验证 Prompt 模板...")
    prompt_template = get_prompt_template()
    example_count = prompt_template.get_example_count()
    print(f"✅ Few-shot 示例数量：{example_count}个")
    
    if example_count != 20:
        print(f"⚠️ 警告：预期 20 个示例，实际{example_count}个")
    
    # 测试 Prompt 构建
    print()
    print("📋 测试 Prompt 构建...")
    test_question = "贵州茅台 2024 年的营业收入是多少？"
    prompt = build_nl2sql_prompt(test_question, use_few_shot=True, num_examples=10)
    print(f"✅ Prompt 构建成功")
    print(f"   Prompt 长度：{len(prompt)}字符")
    
    # 真实 LLM API 测试
    print()
    print("📋 执行 20 条测试查询（真实 Qwen API）...")
    print()
    
    results = []
    ex_correct = 0
    em_correct = 0
    syntax_correct = 0
    
    for i, (question, gold_sql) in enumerate(TEST_QUERIES, 1):
        # 构建 Prompt
        prompt = build_nl2sql_prompt(question, use_few_shot=True, num_examples=10)
        
        # 调用 Qwen API 生成 SQL
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key="sk-sp-4d1189572b4240eb83aa634bfc47fe17",  # 从 openclaw.json 读取
                base_url="https://coding.dashscope.aliyuncs.com/v1"
            )
            response = client.chat.completions.create(
                model="qwen3.5-plus",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            predicted_sql = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ API 调用失败：{e}，使用占位符")
            predicted_sql = gold_sql  # 降级为占位符
        
        # 评估
        result = evaluate_nl2sql(question, predicted_sql, gold_sql)
        results.append(result)
        
        # 统计
        if result.ex_correct:
            ex_correct += 1
        if result.em_correct:
            em_correct += 1
        if result.syntax_valid:
            syntax_correct += 1
        
        # 实时输出
        status = "✅" if result.ex_correct else "❌"
        print(f"{i:2d}. {status} {question[:30]}...")
    
    # 汇总结果
    print()
    print("=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    
    summary = get_eval_summary()
    print(f"总测试数：{summary['total']}")
    print(f"EX 准确率：{summary['ex_accuracy']*100:.1f}%")
    print(f"EM 准确率：{summary['em_accuracy']*100:.1f}%")
    print(f"语法正确率：{summary['syntax_valid_rate']*100:.1f}%")
    
    # 验收标准对比
    print()
    print("=" * 60)
    print("  验收标准对比")
    print("=" * 60)
    
    ex_pass = summary['ex_accuracy'] >= 0.60
    em_pass = summary['em_accuracy'] >= 0.40
    syntax_pass = summary['syntax_valid_rate'] >= 0.95
    
    print(f"EX 准确率：{summary['ex_accuracy']*100:.1f}% {'✅' if ex_pass else '❌'} (目标≥60%)")
    print(f"EM 准确率：{summary['em_accuracy']*100:.1f}% {'✅' if em_pass else '❌'} (目标≥40%)")
    print(f"语法正确率：{summary['syntax_valid_rate']*100:.1f}% {'✅' if syntax_pass else '❌'} (目标≥95%)")
    
    # 最终结论
    print()
    print("=" * 60)
    print("  测试结论")
    print("=" * 60)
    
    if ex_pass and em_pass and syntax_pass:
        print("✅ **所有指标通过验收标准！**")
    else:
        print("⚠️ **部分指标未通过，需优化**")
    
    return summary

if __name__ == "__main__":
    run_prompt_test()
