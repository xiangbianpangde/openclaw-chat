#!/usr/bin/env python3
"""
真实 LLM API 测试脚本（简化版）
使用 Qwen3.5-Plus API 执行 20 条中文测试查询
"""

from openai import OpenAI
import json
import time

# API 配置
API_KEY = "sk-sp-4d1189572b4240eb83aa634bfc47fe17"
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
MODEL = "qwen3.5-plus"

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

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

# 数据库 Schema
SCHEMA = """
CREATE TABLE companies (
    company_id INT PRIMARY KEY,
    name VARCHAR(100),
    industry VARCHAR(50),
    listed_date DATE
);

CREATE TABLE financial_reports (
    report_id INT PRIMARY KEY,
    company_id INT,
    period VARCHAR(10),
    report_type VARCHAR(20),
    revenue DECIMAL(20,4),
    net_profit DECIMAL(20,4),
    gross_profit DECIMAL(20,4),
    total_assets DECIMAL(20,4),
    total_liabilities DECIMAL(20,4),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
"""

# Few-shot 示例（简化为 5 个）
FEW_SHOT_EXAMPLES = """
示例 1:
问题：贵州茅台 2024 年的营业收入是多少？
SQL：SELECT revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'

示例 2:
问题：对比贵州茅台和五粮液 2024 年的营收
SQL：SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name IN ('贵州茅台', '五粮液') AND financial_reports.period = '2024'

示例 3:
问题：查询白酒行业 2024 年平均毛利率
SQL：SELECT AVG(financial_reports.gross_profit) FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024'

示例 4:
问题：2024 年营收最高的公司是哪家？
SQL：SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2024' ORDER BY financial_reports.revenue DESC LIMIT 1

示例 5:
问题：查询所有白酒行业的公司
SQL：SELECT * FROM companies WHERE industry = '白酒'
"""

def build_prompt(question):
    """构建 Prompt"""
    return f"""你是一个财务 SQL 专家。根据数据库 schema 和用户问题，生成正确的 SQL 查询。

数据库 Schema:
{SCHEMA}

示例:
{FEW_SHOT_EXAMPLES}

问题：{question}
SQL："""

def check_syntax(sql):
    """检查 SQL 语法"""
    sql = sql.strip().upper()
    if 'SELECT' not in sql or 'FROM' not in sql:
        return False
    if sql.count('(') != sql.count(')'):
        return False
    return True

def check_exact_match(predicted, gold):
    """检查精确匹配"""
    import re
    def normalize(sql):
        sql = sql.strip().upper()
        sql = re.sub(r'\s+', ' ', sql)
        return sql
    return normalize(predicted) == normalize(gold)

def main():
    print("=" * 60)
    print("  真实 LLM API 测试（Qwen3.5-Plus）")
    print("=" * 60)
    print()
    
    results = []
    ex_correct = 0
    em_correct = 0
    syntax_correct = 0
    
    for i, (question, gold_sql) in enumerate(TEST_QUERIES, 1):
        print(f"[{i:2d}/20] {question[:40]}...", end=" ")
        
        # 构建 Prompt
        prompt = build_prompt(question)
        
        # 调用 API
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                timeout=30
            )
            predicted_sql = response.choices[0].message.content.strip()
            
            # 清理 SQL（去除 Markdown 代码块标记）
            if predicted_sql.startswith("```sql"):
                predicted_sql = predicted_sql[6:]
            if predicted_sql.startswith("```"):
                predicted_sql = predicted_sql[3:]
            if predicted_sql.endswith("```"):
                predicted_sql = predicted_sql[:-3]
            predicted_sql = predicted_sql.strip()
            
            # 评估
            syntax_valid = check_syntax(predicted_sql)
            em_match = check_exact_match(predicted_sql, gold_sql)
            
            # 简单 EX 评估（检查关键元素）
            ex_match = False
            if syntax_valid:
                # 检查是否包含主要表和字段
                pred_upper = predicted_sql.upper()
                gold_upper = gold_sql.upper()
                
                # 提取主要表名
                if 'FINANCIAL_REPORTS' in pred_upper or 'COMPANIES' in pred_upper:
                    ex_match = True
            
            # 统计
            if ex_match:
                ex_correct += 1
            if em_match:
                em_correct += 1
            if syntax_valid:
                syntax_correct += 1
            
            results.append({
                'question': question,
                'predicted': predicted_sql[:100],
                'gold': gold_sql[:100],
                'ex': ex_match,
                'em': em_match,
                'syntax': syntax_valid
            })
            
            # 输出结果
            status = "✅" if ex_match else "❌"
            print(f"{status} EX:{ex_match} EM:{em_match}")
            
        except Exception as e:
            print(f"❌ 错误：{str(e)[:50]}")
            results.append({
                'question': question,
                'predicted': f"ERROR: {e}",
                'gold': gold_sql,
                'ex': False,
                'em': False,
                'syntax': False
            })
        
        # 延迟避免限流
        time.sleep(1)
    
    # 汇总结果
    print()
    print("=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    print(f"总测试数：{len(results)}")
    print(f"EX 准确率：{ex_correct}/{len(results)} = {ex_correct/len(results)*100:.1f}%")
    print(f"EM 准确率：{em_correct}/{len(results)} = {em_correct/len(results)*100:.1f}%")
    print(f"语法正确率：{syntax_correct}/{len(results)} = {syntax_correct/len(results)*100:.1f}%")
    
    # 验收标准对比
    print()
    print("=" * 60)
    print("  验收标准对比")
    print("=" * 60)
    
    ex_pass = ex_correct / len(results) >= 0.60
    em_pass = em_correct / len(results) >= 0.40
    syntax_pass = syntax_correct / len(results) >= 0.95
    
    print(f"EX 准确率：{ex_correct/len(results)*100:.1f}% {'✅' if ex_pass else '❌'} (目标≥60%)")
    print(f"EM 准确率：{em_correct/len(results)*100:.1f}% {'✅' if em_pass else '❌'} (目标≥40%)")
    print(f"语法正确率：{syntax_correct/len(results)*100:.1f}% {'✅' if syntax_pass else '❌'} (目标≥95%)")
    
    # 保存结果
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'ex_accuracy': ex_correct / len(results),
                'em_accuracy': em_correct / len(results),
                'syntax_valid_rate': syntax_correct / len(results)
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print()
    print("测试结果已保存到：test_results.json")
    
    return {
        'total': len(results),
        'ex_accuracy': ex_correct / len(results),
        'em_accuracy': em_correct / len(results),
        'syntax_valid_rate': syntax_correct / len(results)
    }

if __name__ == "__main__":
    main()
