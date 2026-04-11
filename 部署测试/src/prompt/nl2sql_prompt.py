"""
NL2SQL Prompt 模板模块
财务领域专用 Prompt 模板，支持 Few-shot 示例
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class FewShotExample:
    """Few-shot 示例"""
    question: str
    sql: str
    explanation: Optional[str] = None


class NL2SQLPrompt:
    """NL2SQL Prompt 模板类"""
    
    def __init__(self):
        # 数据库 Schema
        self.schema = """
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
        
        # Few-shot 示例（20 个）
        self.few_shot_examples: List[FewShotExample] = []
        self._init_examples()
    
    def _init_examples(self):
        """初始化 Few-shot 示例"""
        
        # 简单查询（10 个）
        self.few_shot_examples.extend([
            FewShotExample(
                question="贵州茅台 2024 年的营业收入是多少？",
                sql="SELECT revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'",
                explanation="单表查询，JOIN 公司名称过滤"
            ),
            FewShotExample(
                question="五粮液 2023 年的净利润是多少？",
                sql="SELECT net_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '五粮液' AND financial_reports.period = '2023'",
                explanation="单表查询，净利润字段"
            ),
            FewShotExample(
                question="查询贵州茅台的基本信息",
                sql="SELECT company_id, name, industry, listed_date FROM companies WHERE name = '贵州茅台'",
                explanation="查询 companies 表"
            ),
            FewShotExample(
                question="2024 年营收最高的公司是哪家？",
                sql="SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2024' ORDER BY financial_reports.revenue DESC LIMIT 1",
                explanation="ORDER BY + LIMIT 取最高"
            ),
            FewShotExample(
                question="查询所有白酒行业的公司",
                sql="SELECT * FROM companies WHERE industry = '白酒'",
                explanation="WHERE 条件过滤行业"
            ),
            FewShotExample(
                question="贵州茅台 2024 年的毛利率是多少？",
                sql="SELECT gross_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'",
                explanation="毛利率字段查询"
            ),
            FewShotExample(
                question="2023 年净利润超过 100 亿的公司有哪些？",
                sql="SELECT companies.name, financial_reports.net_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2023' AND financial_reports.net_profit > 10000000000",
                explanation="数值条件过滤"
            ),
            FewShotExample(
                question="查询贵州茅台 2024 年的总资产",
                sql="SELECT total_assets FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'",
                explanation="总资产字段查询"
            ),
            FewShotExample(
                question="2024 年有多少家上市公司？",
                sql="SELECT COUNT(*) FROM companies",
                explanation="COUNT 聚合查询"
            ),
            FewShotExample(
                question="贵州茅台是什么时候上市的？",
                sql="SELECT listed_date FROM companies WHERE name = '贵州茅台'",
                explanation="上市日期查询"
            ),
        ])
        
        # 复杂查询（10 个）
        self.few_shot_examples.extend([
            FewShotExample(
                question="对比贵州茅台和五粮液 2024 年的营收",
                sql="SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name IN ('贵州茅台', '五粮液') AND financial_reports.period = '2024'",
                explanation="IN 条件多公司对比"
            ),
            FewShotExample(
                question="查询白酒行业 2024 年平均毛利率",
                sql="SELECT AVG(financial_reports.gross_profit) FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024'",
                explanation="AVG 聚合 + 行业过滤"
            ),
            FewShotExample(
                question="找出营收最高的 5 家公司",
                sql="SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id ORDER BY financial_reports.revenue DESC LIMIT 5",
                explanation="ORDER BY + LIMIT 排名"
            ),
            FewShotExample(
                question="贵州茅台近 5 年的营收趋势如何？",
                sql="SELECT period, revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' ORDER BY period DESC LIMIT 5",
                explanation="趋势查询，ORDER BY 时间"
            ),
            FewShotExample(
                question="2024 年净利润增长率超过 20% 的公司有哪些？",
                sql="SELECT companies.name FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE financial_reports.period = '2024' AND financial_reports.net_profit > financial_reports.gross_profit * 0.2",
                explanation="计算字段条件过滤"
            ),
            FewShotExample(
                question="各行业的平均营收是多少？",
                sql="SELECT companies.industry, AVG(financial_reports.revenue) as avg_revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id GROUP BY companies.industry",
                explanation="GROUP BY 分组聚合"
            ),
            FewShotExample(
                question="贵州茅台 2024 年的资产负债率是多少？",
                sql="SELECT (total_liabilities / total_assets) * 100 as debt_ratio FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND financial_reports.period = '2024'",
                explanation="计算字段（负债率）"
            ),
            FewShotExample(
                question="2024 年营收超过 1000 亿的白酒公司有哪些？",
                sql="SELECT companies.name, financial_reports.revenue FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024' AND financial_reports.revenue > 100000000000",
                explanation="多条件过滤（行业 + 营收）"
            ),
            FewShotExample(
                question="对比贵州茅台 2023 年和 2024 年的净利润",
                sql="SELECT period, net_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.name = '贵州茅台' AND period IN ('2023', '2024')",
                explanation="多期间对比"
            ),
            FewShotExample(
                question="2024 年毛利率最高的白酒公司是哪家？",
                sql="SELECT companies.name, financial_reports.gross_profit FROM financial_reports JOIN companies ON financial_reports.company_id = companies.company_id WHERE companies.industry = '白酒' AND financial_reports.period = '2024' ORDER BY financial_reports.gross_profit DESC LIMIT 1",
                explanation="多条件 + 排序 + LIMIT"
            ),
        ])
    
    def build_prompt(self, question: str, use_few_shot: bool = True, num_examples: int = 10) -> str:
        """
        构建 NL2SQL Prompt
        
        :param question: 用户问题
        :param use_few_shot: 是否使用 Few-shot
        :param num_examples: Few-shot 示例数量
        :return: 完整的 Prompt
        """
        prompt_parts = []
        
        # 系统指令
        prompt_parts.append("""你是一个财务 SQL 专家。根据数据库 schema 和用户问题，生成正确的 SQL 查询。

数据库 Schema:
""")
        prompt_parts.append(self.schema)
        
        # Few-shot 示例
        if use_few_shot:
            prompt_parts.append("\n示例:\n")
            examples = self.few_shot_examples[:num_examples]
            for i, ex in enumerate(examples, 1):
                prompt_parts.append(f"示例 {i}:\n")
                prompt_parts.append(f"问题：{ex.question}\n")
                prompt_parts.append(f"SQL：{ex.sql}\n")
                if ex.explanation:
                    prompt_parts.append(f"说明：{ex.explanation}\n")
                prompt_parts.append("\n")
        
        # 用户问题
        prompt_parts.append(f"问题：{question}\n")
        prompt_parts.append("SQL：")
        
        return "".join(prompt_parts)
    
    def get_example_count(self) -> int:
        """获取示例数量"""
        return len(self.few_shot_examples)
    
    def add_example(self, question: str, sql: str, explanation: Optional[str] = None):
        """添加新示例"""
        self.few_shot_examples.append(FewShotExample(question, sql, explanation))


# 全局实例
nl2sql_prompt = NL2SQLPrompt()


def build_nl2sql_prompt(question: str, use_few_shot: bool = True, num_examples: int = 10) -> str:
    """便捷函数：构建 NL2SQL Prompt"""
    return nl2sql_prompt.build_prompt(question, use_few_shot, num_examples)


def get_prompt_template() -> NL2SQLPrompt:
    """便捷函数：获取 Prompt 模板实例"""
    return nl2sql_prompt
