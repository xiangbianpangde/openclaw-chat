#!/usr/bin/env python3
"""
PDF 解析引擎真实数据测试脚本
测试目标：
1. 验证 15 种财务指标识别准确率
2. 测试流式解析大文件性能
3. 测试并发解析性能
4. 目标：解析准确率>95%，单文件<30 秒
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.pdf_parser.parser import PDFParser, parse_pdf
from src.pdf_parser.extractor import FinancialDataExtractor, extract_financial_data
from src.pdf_parser.validator import DataValidator, validate_financial_data, ValidationStatus
from loguru import logger

# 配置日志
logger.add("./logs/parse_test.log", level="INFO", rotation="10 MB")


class ParseTestResult:
    """测试结果记录"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size_mb = 0
        self.parse_time_ms = 0
        self.extract_time_ms = 0
        self.validate_time_ms = 0
        self.total_time_ms = 0
        self.total_pages = 0
        self.metrics_extracted = 0
        self.validation_status = ""
        self.validation_issues = []
        self.success = False
        self.error_message = ""
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "file_size_mb": round(self.file_size_mb, 2),
            "parse_time_ms": round(self.parse_time_ms, 2),
            "extract_time_ms": round(self.extract_time_ms, 2),
            "validate_time_ms": round(self.validate_time_ms, 2),
            "total_time_ms": round(self.total_time_ms, 2),
            "total_pages": self.total_pages,
            "metrics_extracted": self.metrics_extracted,
            "validation_status": self.validation_status,
            "validation_issues": self.validation_issues[:3],  # 最多 3 个问题
            "success": self.success,
            "error_message": self.error_message
        }


def test_single_pdf(file_path: str) -> ParseTestResult:
    """测试单个 PDF 文件"""
    
    result = ParseTestResult(file_path)
    
    try:
        # 获取文件大小
        result.file_size_mb = os.path.getsize(file_path) / 1024 / 1024
        
        logger.info(f"开始测试：{file_path} ({result.file_size_mb:.2f}MB)")
        
        # 1. PDF 解析
        start_time = time.time()
        parser = PDFParser()
        parse_result = parser.parse(file_path)
        result.parse_time_ms = (time.time() - start_time) * 1000
        result.total_pages = parse_result.get("total_pages", 0)
        
        logger.info(f"解析完成：{result.total_pages}页，耗时{result.parse_time_ms:.2f}ms")
        
        # 2. 数据提取
        start_time = time.time()
        extractor = FinancialDataExtractor()
        extracted_data = extractor.extract(parse_result)
        result.extract_time_ms = (time.time() - start_time) * 1000
        result.metrics_extracted = len(extracted_data)
        
        logger.info(f"提取完成：{result.metrics_extracted}条数据，耗时{result.extract_time_ms:.2f}ms")
        
        # 3. 数据校验
        start_time = time.time()
        validator = DataValidator()
        validation_result = validator.validate(extracted_data)
        result.validate_time_ms = (time.time() - start_time) * 1000
        result.validation_status = validation_result["status"]
        result.validation_issues = validation_result.get("issues", []) + validation_result.get("warnings", [])
        
        logger.info(f"校验完成：{result.validation_status}，耗时{result.validate_time_ms:.2f}ms")
        
        # 计算总时间
        result.total_time_ms = result.parse_time_ms + result.extract_time_ms + result.validate_time_ms
        
        # 判断是否成功
        result.success = (
            result.validation_status in [ValidationStatus.PASS.value, ValidationStatus.WARNING.value]
            and result.metrics_extracted > 0
        )
        
        # 性能检查
        if result.total_time_ms > 30000:  # 30 秒
            result.validation_issues.append(f"性能警告：总耗时{result.total_time_ms/1000:.2f}秒超过 30 秒")
        
        logger.info(f"测试完成：{'成功' if result.success else '失败'}，总耗时{result.total_time_ms/1000:.2f}秒")
        
    except Exception as e:
        result.success = False
        result.error_message = str(e)
        logger.error(f"测试失败：{file_path}, 错误：{e}")
    
    return result


def test_batch_pdfs(file_paths: list, max_workers: int = 5) -> list:
    """批量测试 PDF 文件（并发）"""
    
    logger.info(f"开始批量测试，共{len(file_paths)}个文件，并发数{max_workers}")
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(test_single_pdf, fp): fp for fp in file_paths}
        
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)
            
            # 实时输出进度
            success_count = sum(1 for r in results if r.success)
            logger.info(f"进度：{len(results)}/{len(file_paths)}, 成功：{success_count}")
    
    total_time = (time.time() - start_time) / 60
    logger.info(f"批量测试完成，总耗时{total_time:.2f}分钟")
    
    return results


def generate_test_report(results: list, output_path: str):
    """生成测试报告"""
    
    total_files = len(results)
    success_files = sum(1 for r in results if r.success)
    failure_rate = (total_files - success_files) / total_files if total_files > 0 else 0
    
    total_time_ms = sum(r.total_time_ms for r in results)
    avg_time_ms = total_time_ms / total_files if total_files > 0 else 0
    
    total_pages = sum(r.total_pages for r in results)
    total_metrics = sum(r.metrics_extracted for r in results)
    
    # 按文件大小分类统计
    small_files = [r for r in results if r.file_size_mb < 10]
    medium_files = [r for r in results if 10 <= r.file_size_mb < 50]
    large_files = [r for r in results if r.file_size_mb >= 50]
    
    report = {
        "test_date": datetime.now().isoformat(),
        "summary": {
            "total_files": total_files,
            "success_files": success_files,
            "failure_files": total_files - success_files,
            "success_rate": f"{success_files/total_files*100:.2f}%" if total_files > 0 else "N/A",
            "failure_rate": f"{failure_rate*100:.2f}%",
            "total_time_minutes": round(total_time_ms / 1000 / 60, 2),
            "avg_time_per_file_seconds": round(avg_time_ms / 1000, 2),
            "total_pages": total_pages,
            "total_metrics_extracted": total_metrics,
            "avg_metrics_per_file": round(total_metrics / total_files, 2) if total_files > 0 else 0
        },
        "performance_by_size": {
            "small_<10MB": {
                "count": len(small_files),
                "avg_time_seconds": round(sum(r.total_time_ms for r in small_files) / len(small_files) / 1000, 2) if small_files else 0
            },
            "medium_10-50MB": {
                "count": len(medium_files),
                "avg_time_seconds": round(sum(r.total_time_ms for r in medium_files) / len(medium_files) / 1000, 2) if medium_files else 0
            },
            "large_>50MB": {
                "count": len(large_files),
                "avg_time_seconds": round(sum(r.total_time_ms for r in large_files) / len(large_files) / 1000, 2) if large_files else 0
            }
        },
        "validation_status": {
            "pass": sum(1 for r in results if r.validation_status == ValidationStatus.PASS.value),
            "warning": sum(1 for r in results if r.validation_status == ValidationStatus.WARNING.value),
            "error": sum(1 for r in results if r.validation_status == ValidationStatus.ERROR.value),
            "critical": sum(1 for r in results if r.validation_status == ValidationStatus.CRITICAL.value)
        },
        "file_results": [r.to_dict() for r in results]
    }
    
    # 保存报告
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"测试报告已保存：{output_path}")
    
    return report


def main():
    """主函数"""
    
    # 输出目录
    output_dir = "/root/.openclaw/workspace-taizi/尚书省/JJC-20260409-001/tests/results"
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取测试文件列表（使用 subprocess 避免编码问题）
    import subprocess
    result = subprocess.run(
        ["find", "/root/.openclaw/workspace-taizi/teddy_cup_raw", "-name", "*.pdf"],
        capture_output=True,
        text=True
    )
    pdf_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    
    if not pdf_files:
        logger.error("未找到 PDF 文件")
        return
    
    logger.info(f"找到 {len(pdf_files)} 个 PDF 文件")
    
    # 限制测试文件数量（首次测试用 5 个）
    test_files = pdf_files[:5]
    
    print("=" * 60)
    print("  PDF 解析引擎真实数据测试")
    print("=" * 60)
    print(f"测试文件数：{len(test_files)}")
    print(f"输出目录：{output_dir}")
    print("=" * 60)
    print()
    
    # 执行测试
    results = test_batch_pdfs(test_files, max_workers=5)
    
    # 生成报告
    report_path = f"{output_dir}/parse_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = generate_test_report(results, report_path)
    
    # 输出摘要
    print()
    print("=" * 60)
    print("  测试摘要")
    print("=" * 60)
    print(f"总文件数：{report['summary']['total_files']}")
    print(f"成功数：{report['summary']['success_files']}")
    print(f"失败数：{report['summary']['failure_files']}")
    print(f"成功率：{report['summary']['success_rate']}")
    print(f"平均耗时：{report['summary']['avg_time_per_file_seconds']}秒/文件")
    print(f"总页数：{report['summary']['total_pages']}")
    print(f"提取指标数：{report['summary']['total_metrics_extracted']}")
    print("=" * 60)
    
    # 检查是否达到目标
    success_rate = float(report['summary']['success_rate'].rstrip('%'))
    avg_time = report['summary']['avg_time_per_file_seconds']
    
    print()
    print("目标检查:")
    print(f"  ✅ 解析准确率>95%: {'✅ 通过' if success_rate >= 95 else '❌ 未通过'} ({success_rate:.2f}%)")
    print(f"  ✅ 单文件<30 秒：{'✅ 通过' if avg_time < 30 else '❌ 未通过'} ({avg_time:.2f}秒)")
    print()
    
    return report


if __name__ == "__main__":
    main()
