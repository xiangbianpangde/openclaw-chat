"""
研报提取器
支持元数据提取、表格识别、核心观点抽取
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class ReportMetadata:
    """研报元数据"""
    title: str = ""                    # 报告标题
    institution: str = ""              # 发布机构
    analysts: List[str] = None         # 分析师列表
    publish_date: str = ""             # 发布日期
    rating: str = ""                   # 投资评级
    target_price: Optional[float] = None  # 目标价
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "institution": self.institution,
            "analysts": self.analysts or [],
            "publish_date": self.publish_date,
            "rating": self.rating,
            "target_price": self.target_price
        }


class ResearchReportExtractor:
    """研报提取器"""
    
    def __init__(self):
        # 常见机构名称
        self.institutions = [
            '中信证券', '中金公司', '国泰君安', '华泰证券',
            '招商证券', '广发证券', '海通证券', '申万宏源',
            '天风证券', '长江证券', '光大证券', '东方证券',
            '中信建投', '银河证券', '平安证券', '兴业证券'
        ]
        
        # 投资评级关键词
        self.rating_keywords = {
            '买入': ['买入', '强烈推荐', '推荐', 'Buy', '增持'],
            '增持': ['增持', '优于大市', 'Outperform', '审慎增持'],
            '中性': ['中性', '持有', '大市同步', 'Hold', '观望'],
            '减持': ['减持', '弱于大市', 'Underperform', 'Sell', '卖出']
        }
        
        # 财务指标关键词
        self.metric_keywords = {
            "营业收入": ["营业收入", "营业总收入", "总收入", "营收"],
            "净利润": ["净利润", "归母净利润", "归属于母公司股东的净利润", "净利"],
            "每股收益": ["每股收益", "EPS", "基本每股收益"],
            "市盈率": ["市盈率", "PE", "估值"],
            "市净率": ["市净率", "PB"],
            "净资产收益率": ["净资产收益率", "ROE"],
            "毛利率": ["毛利率", "营业毛利率"],
            "净利率": ["净利率", "销售净利率"],
        }
    
    def extract_metadata(self, text: str) -> ReportMetadata:
        """
        提取研报元数据
        
        :param text: 研报全文
        :return: 元数据对象
        """
        metadata = ReportMetadata()
        
        # 1. 提取标题（通常在第一行）
        metadata.title = self._extract_title(text)
        
        # 2. 提取机构
        metadata.institution = self._extract_institution(text)
        
        # 3. 提取分析师
        metadata.analysts = self._extract_analysts(text)
        
        # 4. 提取日期
        metadata.publish_date = self._extract_date(text)
        
        # 5. 提取评级
        metadata.rating = self._extract_rating(text)
        
        # 6. 提取目标价
        metadata.target_price = self._extract_target_price(text)
        
        logger.info(f"元数据提取完成：{metadata.institution or '未知机构'} - {metadata.title[:30]}...")
        
        return metadata
    
    def _extract_title(self, text: str) -> str:
        """提取标题"""
        lines = text.split('\n')
        # 标题通常在开头，且较短（<100 字符）
        for line in lines[:10]:
            line = line.strip()
            if 10 < len(line) < 100 and not line.endswith(('：', ':')):
                return line
        return lines[0].strip() if lines else ""
    
    def _extract_institution(self, text: str) -> str:
        """提取机构名称"""
        # 在开头 500 字搜索机构名
        for inst in self.institutions:
            if inst in text[:500]:
                return inst
        
        # 尝试正则匹配
        match = re.search(r'([^\s]+证券|[^\s]+研究所)', text[:500])
        if match:
            return match.group(1)
        
        return "未知机构"
    
    def _extract_analysts(self, text: str) -> List[str]:
        """提取分析师"""
        analysts = []
        
        # 常见格式："分析师：张三" 或 "证券分析师：李四"
        patterns = [
            r'分析师 [：:]\s*([^\n]+)',
            r'证券分析师 [：:]\s*([^\n]+)',
            r'报告作者 [：:]\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:1000])
            if match:
                raw = match.group(1)
                # 分割多个分析师
                analysts = re.split(r'[,，\s]+', raw.strip())
                analysts = [a.strip() for a in analysts if a.strip()]
                break
        
        return analysts
    
    def _extract_date(self, text: str) -> str:
        """提取发布日期"""
        # 常见日期格式
        patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{4}/\d{1,2}/\d{1,2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:500])
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_rating(self, text: str) -> str:
        """提取投资评级"""
        for rating, keywords in self.rating_keywords.items():
            for keyword in keywords:
                if keyword in text[:1000]:  # 评级通常在摘要部分
                    return rating
        return ""
    
    def _extract_target_price(self, text: str) -> Optional[float]:
        """提取目标价"""
        # 常见格式："目标价 XX 元" 或 "TP: XX"
        patterns = [
            r'目标价 [：:]?\s*(\d+(?:\.\d+)?)\s*元',
            r'TP[：:]?\s*(\d+(?:\.\d+)?)',
            r'目标价位 [：:]?\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:1000])
            if match:
                return float(match.group(1))
        
        return None
    
    def extract_financial_metrics(self, text: str) -> List[Dict]:
        """
        提取财务指标
        
        :param text: 研报全文
        :return: 财务指标列表
        """
        metrics = []
        
        for metric_name, keywords in self.metric_keywords.items():
            for keyword in keywords:
                # 查找模式：指标名 + 数值
                pattern = rf'{keyword}.*?(\d+(?:\.\d+)?)\s*(亿元 | 万元 | 元|%)'
                match = re.search(pattern, text)
                
                if match:
                    value = float(match.group(1))
                    unit = match.group(2)
                    
                    # 单位转换
                    if unit == '亿元':
                        value *= 100000000
                    elif unit == '万元':
                        value *= 10000
                    
                    metrics.append({
                        "metric_name": metric_name,
                        "metric_value": value,
                        "unit": "元" if unit != '%' else "",
                        "source": "text"
                    })
                    break
        
        logger.info(f"提取到 {len(metrics)} 条财务指标")
        return metrics
    
    def extract_core_views(self, text: str, max_sentences: int = 5) -> List[str]:
        """
        提取核心观点（简化版：规则 + 位置加权）
        
        :param text: 研报全文
        :param max_sentences: 最多返回的核心观点数量
        :return: 核心观点列表
        """
        core_views = []
        
        # 1. 定位核心观点章节
        core_section = self._locate_core_section(text)
        if not core_section:
            return []
        
        # 2. 句子分割
        sentences = self._split_sentences(core_section)
        if len(sentences) <= max_sentences:
            return sentences
        
        # 3. 位置加权（靠前的句子更重要）
        weighted_sentences = []
        for i, sent in enumerate(sentences):
            weight = 1.0 - (i / len(sentences)) * 0.5  # 线性衰减
            weighted_sentences.append((sent, weight))
        
        # 4. 选择 Top-N 句子
        weighted_sentences.sort(key=lambda x: x[1], reverse=True)
        core_views = [sent for sent, _ in weighted_sentences[:max_sentences]]
        
        logger.info(f"提取到 {len(core_views)} 条核心观点")
        return core_views
    
    def _locate_core_section(self, text: str) -> str:
        """定位核心观点章节"""
        keywords = ['核心观点', '投资摘要', '主要结论', 'Key Points', '投资要点', '摘要']
        lines = text.split('\n')
        
        start_idx = -1
        for i, line in enumerate(lines[:30]):  # 前 30 行
            if any(kw in line for kw in keywords):
                start_idx = i
                break
        
        if start_idx == -1:
            return text[:2000]  # 默认取前 2000 字
        
        # 提取章节内容（到下一章节前）
        section_lines = []
        for line in lines[start_idx:start_idx + 50]:  # 最多 50 行
            if self._is_new_section(line):
                break
            section_lines.append(line)
        
        return '\n'.join(section_lines)
    
    def _is_new_section(self, line: str) -> bool:
        """判断是否为新章节"""
        section_keywords = ['目录', '正文', '风险提示', '附录', '免责声明']
        return any(kw in line for kw in section_keywords)
    
    def _split_sentences(self, text: str) -> List[str]:
        """句子分割"""
        # 简单分割：按句号、问号、感叹号
        sentences = re.split(r'[.!?!.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences
    
    def extract_tables_from_text(self, text: str) -> List[Dict]:
        """
        从文本中提取表格数据（简化版）
        
        :param text: 研报全文
        :return: 表格数据列表
        """
        tables = []
        
        # 查找表格模式：多行数据，每行有相似的分隔符
        lines = text.split('\n')
        current_table = []
        
        for line in lines:
            # 检测是否为表格行（有多个数值或制表符分隔）
            if '\t' in line or (line.count(' ') > 3 and re.search(r'\d+', line)):
                current_table.append(line)
            else:
                if len(current_table) >= 2:  # 至少 2 行才可能是表格
                    tables.append({
                        "rows": current_table,
                        "source": "text"
                    })
                current_table = []
        
        logger.info(f"提取到 {len(tables)} 个表格")
        return tables


# 全局提取器实例
report_extractor = ResearchReportExtractor()


def extract_report_metadata(text: str) -> Dict:
    """便捷函数：提取研报元数据"""
    metadata = report_extractor.extract_metadata(text)
    return metadata.to_dict()


def extract_report_financial_metrics(text: str) -> List[Dict]:
    """便捷函数：提取财务指标"""
    return report_extractor.extract_financial_metrics(text)


def extract_report_core_views(text: str, max_sentences: int = 5) -> List[str]:
    """便捷函数：提取核心观点"""
    return report_extractor.extract_core_views(text, max_sentences)
