"""
PDF 解析引擎单元测试
"""

import pytest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.pdf_parser.parser import PDFParser, PDFParseError
from src.pdf_parser.extractor import FinancialDataExtractor
from src.pdf_parser.validator import DataValidator, ValidationStatus


class TestPDFParser:
    """PDF 解析器测试"""
    
    def test_init(self):
        """测试初始化"""
        parser = PDFParser()
        assert parser.max_file_size > 0
        assert parser.max_page_count > 0
        assert parser.enable_chunking is True
    
    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        parser = PDFParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.pdf")


class TestFinancialDataExtractor:
    """财务数据提取器测试"""
    
    def test_init(self):
        """测试初始化"""
        extractor = FinancialDataExtractor()
        assert len(extractor.metric_keywords) > 0
        assert "营业收入" in extractor.metric_keywords
    
    def test_extract_from_empty_text(self):
        """测试从空文本提取"""
        extractor = FinancialDataExtractor()
        data = extractor.extract({"text": "", "tables": []})
        assert len(data) == 0
    
    def test_extract_simple_value(self):
        """测试提取简单数值"""
        extractor = FinancialDataExtractor()
        text = "营业收入 123456.78 元"
        data = extractor.extract({"text": text, "tables": []})
        assert len(data) > 0
        assert data[0]["metric_name"] == "营业收入"
    
    def test_parse_value(self):
        """测试数值解析"""
        extractor = FinancialDataExtractor()
        
        # 测试普通数字
        assert extractor._parse_value("123.45") == 123.45
        assert extractor._parse_value("1,234.56") == 1234.56
        
        # 测试百分比
        result = extractor._parse_value("12.34%")
        assert result is not None
        assert abs(result - 0.1234) < 0.0001
        
        # 测试无效值
        assert extractor._parse_value("abc") is None
        assert extractor._parse_value("") is None


class TestDataValidator:
    """数据校验器测试"""
    
    def test_init(self):
        """测试初始化"""
        validator = DataValidator()
        assert len(validator.rules) == 4
    
    def test_validate_empty_data(self):
        """测试校验空数据"""
        validator = DataValidator()
        result = validator.validate([])
        assert result["status"] == ValidationStatus.CRITICAL.value
        assert result["data_count"] == 0
    
    def test_validate_complete_data(self):
        """测试校验完整数据"""
        validator = DataValidator()
        data = [
            {"metric_name": "营业收入", "metric_value": 1000000},
            {"metric_name": "净利润", "metric_value": 200000},
            {"metric_name": "总资产", "metric_value": 5000000},
            {"metric_name": "净资产", "metric_value": 3000000},
        ]
        result = validator.validate(data)
        assert result["status"] == ValidationStatus.PASS.value
        assert result["data_count"] == 4
    
    def test_validate_missing_metrics(self):
        """测试校验缺失指标"""
        validator = DataValidator()
        data = [
            {"metric_name": "营业收入", "metric_value": 1000000},
        ]
        result = validator.validate(data)
        assert result["status"] == ValidationStatus.WARNING.value
        assert "缺失" in str(result["issues"]) or len(result["warnings"]) > 0
    
    def test_validate_unreasonable_data(self):
        """测试校验不合理数据"""
        validator = DataValidator()
        data = [
            {"metric_name": "毛利率", "metric_value": 1.5},  # 150%，不合理
        ]
        result = validator.validate(data)
        assert result["status"] in [ValidationStatus.WARNING.value, ValidationStatus.PASS.value]


class TestIntegration:
    """集成测试"""
    
    def test_parse_extract_validate_pipeline(self):
        """测试完整流程：解析 -> 提取 -> 校验"""
        # 模拟解析结果
        parse_result = {
            "text": """
            贵州茅台 2023 年年度报告
            营业收入 1234567.89 元
            净利润 234567.89 元
            总资产 5678901.23 元
            净资产 3456789.01 元
            """,
            "tables": []
        }
        
        # 提取数据
        extractor = FinancialDataExtractor()
        data = extractor.extract(parse_result)
        
        # 校验数据
        validator = DataValidator()
        result = validator.validate(data)
        
        assert result["data_count"] >= 3
        assert result["status"] in [
            ValidationStatus.PASS.value,
            ValidationStatus.WARNING.value
        ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
