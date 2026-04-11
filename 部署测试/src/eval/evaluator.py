"""
NL2SQL 评估器模块
评估 NL2SQL 模型的 EX/EM 准确率
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re


@dataclass
class EvalResult:
    """评估结果"""
    question: str
    predicted_sql: str
    gold_sql: str
    ex_correct: bool  # 执行准确率
    em_correct: bool  # 精确匹配
    syntax_valid: bool  # 语法正确


class NL2SQLEvaluator:
    """NL2SQL 评估器"""
    
    def __init__(self):
        self.results: List[EvalResult] = []
    
    def evaluate(self, question: str, predicted_sql: str, gold_sql: str) -> EvalResult:
        """
        评估单个查询
        
        :param question: 用户问题
        :param predicted_sql: 预测的 SQL
        :param gold_sql: 标准答案 SQL
        :return: 评估结果
        """
        # 1. 语法正确性检查
        syntax_valid = self._check_syntax(predicted_sql)
        
        # 2. 精确匹配（EM）
        em_correct = self._check_exact_match(predicted_sql, gold_sql)
        
        # 3. 执行准确率（EX）- 简化版，实际需执行 SQL 对比结果
        ex_correct = self._check_execution_accuracy(predicted_sql, gold_sql)
        
        result = EvalResult(
            question=question,
            predicted_sql=predicted_sql,
            gold_sql=gold_sql,
            ex_correct=ex_correct,
            em_correct=em_correct,
            syntax_valid=syntax_valid
        )
        
        self.results.append(result)
        return result
    
    def _check_syntax(self, sql: str) -> bool:
        """
        检查 SQL 语法
        
        :param sql: SQL 语句
        :return: 语法是否正确
        """
        # 简化检查：检查基本 SQL 结构
        sql = sql.strip().upper()
        
        # 必须包含 SELECT
        if 'SELECT' not in sql:
            return False
        
        # 必须包含 FROM
        if 'FROM' not in sql:
            return False
        
        # 检查括号匹配
        if sql.count('(') != sql.count(')'):
            return False
        
        return True
    
    def _check_exact_match(self, predicted: str, gold: str) -> bool:
        """
        检查精确匹配
        
        :param predicted: 预测 SQL
        :param gold: 标准 SQL
        :return: 是否完全匹配
        """
        # 规范化 SQL（去除多余空格、统一大小写）
        def normalize(sql: str) -> str:
            sql = sql.strip().upper()
            sql = re.sub(r'\s+', ' ', sql)
            return sql
        
        return normalize(predicted) == normalize(gold)
    
    def _check_execution_accuracy(self, predicted: str, gold: str) -> bool:
        """
        检查执行准确率（简化版）
        
        实际应执行 SQL 并对比结果，这里简化为检查关键元素
        
        :param predicted: 预测 SQL
        :param gold: 标准 SQL
        :return: 执行是否准确
        """
        # 提取关键元素
        def extract_elements(sql: str) -> set:
            sql = sql.upper()
            elements = set()
            
            # 提取表名
            tables = re.findall(r'FROM\s+(\w+)', sql)
            elements.update([f'TABLE:{t}' for t in tables])
            
            # 提取字段
            selects = re.findall(r'SELECT\s+([\w\s,\.\(\)]+?)\s+FROM', sql)
            for select in selects:
                for col in select.split(','):
                    elements.add(f'COL:{col.strip()}')
            
            # 提取 WHERE 条件中的表/字段
            where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', sql)
            if where_match:
                elements.add(f'WHERE:{where_match.group(1)}')
            
            return elements
        
        pred_elements = extract_elements(predicted)
        gold_elements = extract_elements(gold)
        
        # 计算相似度
        if not gold_elements:
            return False
        
        overlap = len(pred_elements & gold_elements)
        similarity = overlap / len(gold_elements)
        
        return similarity >= 0.8  # 80% 元素匹配视为正确
    
    def batch_evaluate(self, test_data: List[Dict]) -> Dict:
        """
        批量评估
        
        :param test_data: 测试数据列表 [{'question': ..., 'gold_sql': ...}, ...]
        :return: 评估统计
        """
        for item in test_data:
            # 这里需要实际调用模型生成 SQL，简化为示例
            predicted_sql = f"SELECT * FROM table WHERE condition"  # 占位符
            self.evaluate(item['question'], predicted_sql, item['gold_sql'])
        
        return self.get_summary()
    
    def get_summary(self) -> Dict:
        """
        获取评估摘要
        
        :return: 评估统计
        """
        if not self.results:
            return {
                'total': 0,
                'ex_accuracy': 0.0,
                'em_accuracy': 0.0,
                'syntax_valid_rate': 0.0
            }
        
        total = len(self.results)
        ex_correct = sum(1 for r in self.results if r.ex_correct)
        em_correct = sum(1 for r in self.results if r.em_correct)
        syntax_valid = sum(1 for r in self.results if r.syntax_valid)
        
        return {
            'total': total,
            'ex_accuracy': ex_correct / total,
            'em_accuracy': em_correct / total,
            'syntax_valid_rate': syntax_valid / total,
            'ex_correct_count': ex_correct,
            'em_correct_count': em_correct,
            'syntax_valid_count': syntax_valid
        }
    
    def get_error_cases(self) -> List[EvalResult]:
        """获取错误案例"""
        return [r for r in self.results if not r.ex_correct]
    
    def reset(self):
        """重置评估结果"""
        self.results = []


# 全局实例
evaluator = NL2SQLEvaluator()


def evaluate_nl2sql(question: str, predicted_sql: str, gold_sql: str) -> EvalResult:
    """便捷函数：评估单个查询"""
    return evaluator.evaluate(question, predicted_sql, gold_sql)


def get_eval_summary() -> Dict:
    """便捷函数：获取评估摘要"""
    return evaluator.get_summary()
