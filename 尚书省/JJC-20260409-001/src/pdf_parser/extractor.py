"""
财务数据提取器
从 PDF 解析结果中提取结构化财务数据
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from loguru import logger

from config.settings import settings


class DataExtractionError(Exception):
    """数据提取异常"""
    pass


class FinancialDataExtractor:
    """财务数据提取器"""
    
    def __init__(self):
        # 财务指标关键词映射
        self.metric_keywords = {
            "营业收入": ["营业收入", "营业总收入", "总收入", "营收"],
            "净利润": ["净利润", "归母净利润", "归属于母公司股东的净利润", "净利"],
            "总资产": ["总资产", "资产总计", "资产总额"],
            "净资产": ["净资产", "所有者权益", "股东权益"],
            "毛利率": ["毛利率", "营业毛利率"],
            "净利率": ["净利率", "销售净利率"],
            "资产负债率": ["资产负债率", "负债率"],
            "流动比率": ["流动比率"],
            "速动比率": ["速动比率"],
            "每股收益": ["每股收益", "EPS", "基本每股收益"],
            "净资产收益率": ["净资产收益率", "ROE", "加权平均净资产收益率"],
            "经营活动现金流": ["经营活动产生的现金流量净额", "经营现金流", "经营性现金流"],
            "投资活动现金流": ["投资活动产生的现金流量净额", "投资现金流"],
            "筹资活动现金流": ["筹资活动产生的现金流量净额", "筹资现金流"],
        }
        
        # 单位映射
        self.unit_mapping = {
            "元": 1,
            "万元": 10000,
            "亿元": 100000000,
            "千元": 1000,
            "百万": 1000000,
        }
        
        # 数字正则表达式（支持中文数字格式）
        self.number_pattern = re.compile(
            r'[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|[-+]?\d+\.?\d*'
        )
    
    def extract(self, parse_result: Dict) -> List[Dict]:
        """
        从 PDF 解析结果中提取财务数据
        
        Args:
            parse_result: PDF 解析结果
            
        Returns:
            财务数据列表
        """
        extracted_data = []
        
        # 提取文本中的财务数据
        text_data = self._extract_from_text(parse_result.get("text", ""))
        extracted_data.extend(text_data)
        
        # 提取表格中的财务数据
        table_data = self._extract_from_tables(parse_result.get("tables", []))
        extracted_data.extend(table_data)
        
        logger.info(f"从 PDF 中提取到 {len(extracted_data)} 条财务数据")
        
        return extracted_data
    
    def _extract_from_text(self, text: str) -> List[Dict]:
        """从文本中提取财务数据"""
        data = []
        
        # 按行分割
        lines = text.split('\n')
        
        for line in lines:
            # 尝试匹配财务数据模式
            match = self._parse_financial_line(line)
            if match:
                data.append(match)
        
        return data
    
    def _parse_financial_line(self, line: str) -> Optional[Dict]:
        """解析包含财务数据的行"""
        
        # 查找指标名称
        metric_name = None
        for standard_name, keywords in self.metric_keywords.items():
            for keyword in keywords:
                if keyword in line:
                    metric_name = standard_name
                    break
            if metric_name:
                break
        
        if not metric_name:
            return None
        
        # 查找数值
        numbers = self.number_pattern.findall(line)
        if not numbers:
            return None
        
        # 查找单位
        unit = "元"  # 默认单位
        for unit_name in self.unit_mapping.keys():
            if unit_name in line:
                unit = unit_name
                break
        
        # 解析数值
        try:
            # 移除逗号
            value_str = numbers[0].replace(',', '')
            value = Decimal(value_str) * self.unit_mapping[unit]
            
            return {
                "metric_name": metric_name,
                "metric_value": float(value),
                "unit": "元",
                "original_value": numbers[0],
                "original_unit": unit,
                "source": "text"
            }
        except Exception as e:
            logger.warning(f"解析数值失败：{numbers[0]}, 错误：{e}")
            return None
    
    def _extract_from_tables(self, tables: List[Dict]) -> List[Dict]:
        """从表格中提取财务数据"""
        data = []
        
        for table in tables:
            table_data = self._parse_table(table)
            data.extend(table_data)
        
        return data
    
    def _parse_table(self, table: Dict) -> List[Dict]:
        """解析单个表格"""
        data = []
        
        table_data = table.get("data", [])
        if not table_data:
            return data
        
        # 识别表头
        header = table_data[0] if table_data else []
        header_str = " ".join(str(cell) for cell in header if cell)
        
        # 判断是否为财务数据表
        is_financial_table = False
        for keywords in self.metric_keywords.values():
            if any(keyword in header_str for keyword in keywords):
                is_financial_table = True
                break
        
        if not is_financial_table:
            return data
        
        # 提取数据行
        for row_idx, row in enumerate(table_data[1:], start=1):
            if len(row) < 2:
                continue
            
            # 第一列通常是指标名称
            metric_cell = str(row[0]) if row else ""
            metric_name = self._match_metric_name(metric_cell)
            
            if not metric_name:
                continue
            
            # 提取数值列
            for cell_idx, cell in enumerate(row[1:], start=1):
                if cell is None:
                    continue
                
                cell_str = str(cell).strip()
                value = self._parse_value(cell_str)
                
                if value is not None:
                    data.append({
                        "metric_name": metric_name,
                        "metric_value": value,
                        "unit": "元",
                        "source": "table",
                        "table_index": table.get("page_num", 0),
                        "row_index": row_idx,
                        "col_index": cell_idx
                    })
        
        return data
    
    def _match_metric_name(self, text: str) -> Optional[str]:
        """匹配指标名称"""
        for standard_name, keywords in self.metric_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return standard_name
        return None
    
    def _parse_value(self, value_str: str) -> Optional[float]:
        """解析数值字符串"""
        if not value_str:
            return None
        
        # 移除空格和特殊字符
        value_str = value_str.strip().replace(',', '').replace(' ', '')
        
        # 过滤年份（1900-2100 范围内的整数视为年份，不是财务数据）
        try:
            potential_year = int(float(value_str))
            if 1900 <= potential_year <= 2100:
                return None  # 这是年份，不是财务数据
        except (ValueError, TypeError):
            pass  # 不是整数，继续处理
        
        # 处理百分比
        is_percentage = '%' in value_str
        if is_percentage:
            value_str = value_str.replace('%', '')
        
        # 提取数值
        match = self.number_pattern.match(value_str)
        if not match:
            return None
        
        try:
            value = float(match.group())
            
            # 过滤明显不合理的值（如 1900-2100 范围内的整数）
            if value == int(value) and 1900 <= value <= 2100:
                return None
            
            if is_percentage:
                value = value / 100  # 转换为小数
            return value
        except ValueError:
            return None
    
    def extract_with_context(self, parse_result: Dict, company_code: str, 
                            report_year: int, report_type: str) -> List[Dict]:
        """
        提取财务数据并添加上下文信息
        
        Args:
            parse_result: PDF 解析结果
            company_code: 公司代码
            report_year: 报告年份
            report_type: 报告类型（年报/季报等）
            
        Returns:
            带有上下文的财务数据列表
        """
        data = self.extract(parse_result)
        
        # 添加上下文信息
        for item in data:
            item["company_code"] = company_code
            item["report_year"] = report_year
            item["report_type"] = report_type
        
        return data


# 全局提取器实例
extractor = FinancialDataExtractor()


def extract_financial_data(parse_result: Dict) -> List[Dict]:
    """便捷函数：提取财务数据"""
    return extractor.extract(parse_result)


def extract_with_context(parse_result: Dict, company_code: str, 
                        report_year: int, report_type: str) -> List[Dict]:
    """便捷函数：提取带上下文的财务数据"""
    return extractor.extract_with_context(parse_result, company_code, report_year, report_type)
