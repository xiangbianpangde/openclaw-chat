"""
数据校验器
校验提取的财务数据完整性、一致性、合理性
"""

import re
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from loguru import logger
from enum import Enum

from config.settings import settings


class ValidationStatus(Enum):
    """校验状态"""
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRule:
    """校验规则基类"""
    
    def __init__(self, name: str, description: str, priority: int = 1):
        self.name = name
        self.description = description
        self.priority = priority  # 1=最高优先级
    
    def validate(self, data: List[Dict]) -> Tuple[ValidationStatus, str]:
        """
        执行校验
        
        Returns:
            (状态，错误信息)
        """
        raise NotImplementedError


class CompletenessRule(ValidationRule):
    """完整性校验规则"""
    
    def __init__(self):
        super().__init__(
            name="completeness",
            description="检查核心财务指标是否完整",
            priority=1
        )
        
        # 核心指标（必须存在）
        self.required_metrics = [
            "营业收入",
            "净利润",
            "总资产",
            "净资产"
        ]
    
    def validate(self, data: List[Dict]) -> Tuple[ValidationStatus, str]:
        if not data:
            return ValidationStatus.CRITICAL, "未提取到任何财务数据"
        
        # 提取所有指标名称
        metrics = set(item["metric_name"] for item in data)
        
        # 检查缺失的指标
        missing = []
        for metric in self.required_metrics:
            if metric not in metrics:
                missing.append(metric)
        
        if len(missing) == len(self.required_metrics):
            return ValidationStatus.CRITICAL, f"核心指标全部缺失：{missing}"
        
        if missing:
            return ValidationStatus.WARNING, f"部分核心指标缺失：{missing}"
        
        return ValidationStatus.PASS, "核心指标完整"


class ConsistencyRule(ValidationRule):
    """一致性校验规则"""
    
    def __init__(self):
        super().__init__(
            name="consistency",
            description="检查数据一致性（如资产=负债 + 所有者权益）",
            priority=1
        )
    
    def validate(self, data: List[Dict]) -> Tuple[ValidationStatus, str]:
        # 构建指标字典
        metrics = {}
        for item in data:
            metric_name = item["metric_name"]
            metric_value = item["metric_value"]
            
            if metric_name in metrics:
                # 检查同一指标是否有多个值
                if abs(metrics[metric_name] - metric_value) > 0.01:
                    logger.warning(
                        f"指标 {metric_name} 存在多个值："
                        f"{metrics[metric_name]} vs {metric_value}"
                    )
            else:
                metrics[metric_name] = metric_value
        
        # 检查会计恒等式：资产 = 负债 + 所有者权益
        if "总资产" in metrics and "净资产" in metrics:
            assets = metrics["总资产"]
            equity = metrics["净资产"]
            
            # 负债 = 资产 - 所有者权益
            if "总负债" in metrics:
                liabilities = metrics["总负债"]
                expected_assets = equity + liabilities
                
                # 允许 1% 的误差
                if abs(assets - expected_assets) / max(assets, 1) > 0.01:
                    return ValidationStatus.WARNING, (
                        f"会计恒等式不成立：资产 ({assets}) ≠ "
                        f"负债 ({liabilities}) + 所有者权益 ({equity})"
                    )
        
        return ValidationStatus.PASS, "数据一致性校验通过"


class ReasonabilityRule(ValidationRule):
    """合理性校验规则"""
    
    def __init__(self):
        super().__init__(
            name="reasonability",
            description="检查数据合理性（如利润率不超过 100%）",
            priority=2
        )
        
        # 指标合理范围
        self.metric_ranges = {
            "毛利率": (0, 1),  # 0-100%
            "净利率": (-1, 1),  # -100% 到 100%
            "资产负债率": (0, 1),  # 0-100%
            "流动比率": (0, 10),  # 0-10
            "速动比率": (0, 10),  # 0-10
            "净资产收益率": (-1, 1),  # -100% 到 100%
        }
    
    def validate(self, data: List[Dict]) -> Tuple[ValidationStatus, str]:
        issues = []
        
        for item in data:
            metric_name = item["metric_name"]
            metric_value = item["metric_value"]
            
            if metric_name in self.metric_ranges:
                min_val, max_val = self.metric_ranges[metric_name]
                
                # 检查是否为比率指标（0-1 范围）
                if metric_value < -10 or metric_value > 10:
                    # 可能是百分比格式，转换为小数
                    metric_value = metric_value / 100
                
                if metric_value < min_val or metric_value > max_val:
                    issues.append(
                        f"{metric_name} ({metric_value}) 超出合理范围 "
                        f"[{min_val}, {max_val}]"
                    )
        
        if issues:
            return ValidationStatus.WARNING, "; ".join(issues[:3])  # 最多显示 3 个
        
        return ValidationStatus.PASS, "数据合理性校验通过"


class StatisticalAnomalyRule(ValidationRule):
    """统计异常检测规则"""
    
    def __init__(self):
        super().__init__(
            name="statistical_anomaly",
            description="检测统计异常值（3σ原则）",
            priority=3
        )
    
    def validate(self, data: List[Dict]) -> Tuple[ValidationStatus, str]:
        # 按指标分组
        metrics_data = {}
        for item in data:
            metric_name = item["metric_name"]
            if metric_name not in metrics_data:
                metrics_data[metric_name] = []
            metrics_data[metric_name].append(item["metric_value"])
        
        anomalies = []
        
        for metric_name, values in metrics_data.items():
            if len(values) < 3:
                continue  # 数据量不足，跳过
            
            # 计算均值和标准差
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std = variance ** 0.5
            
            if std == 0:
                continue
            
            # 检测异常值（3σ原则）
            for value in values:
                if abs(value - mean) > 3 * std:
                    anomalies.append(f"{metric_name}: {value} (均值={mean:.2f}, σ={std:.2f})")
        
        if anomalies:
            return ValidationStatus.WARNING, f"检测到异常值：{'; '.join(anomalies[:3])}"
        
        return ValidationStatus.PASS, "未检测到统计异常"


class DataValidator:
    """数据校验器"""
    
    def __init__(self):
        self.rules = [
            CompletenessRule(),
            ConsistencyRule(),
            ReasonabilityRule(),
            StatisticalAnomalyRule(),
        ]
        
        # 失败率阈值
        self.failure_rate_threshold = settings.DATA_FAILURE_RATE_THRESHOLD
    
    def validate(self, data: List[Dict]) -> Dict:
        """
        执行完整校验
        
        Args:
            data: 财务数据列表
            
        Returns:
            校验结果报告
        """
        if not data:
            return {
                "status": ValidationStatus.CRITICAL.value,
                "total_rules": len(self.rules),
                "passed_rules": 0,
                "failed_rules": len(self.rules),
                "issues": ["未提供数据进行校验"],
                "data_count": 0
            }
        
        results = {
            "status": ValidationStatus.PASS.value,
            "total_rules": len(self.rules),
            "passed_rules": 0,
            "failed_rules": 0,
            "issues": [],
            "warnings": [],
            "data_count": len(data)
        }
        
        worst_status = ValidationStatus.PASS
        
        # 按优先级执行校验规则
        sorted_rules = sorted(self.rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            try:
                status, message = rule.validate(data)
                
                if status == ValidationStatus.PASS:
                    results["passed_rules"] += 1
                elif status == ValidationStatus.WARNING:
                    results["warnings"].append(f"{rule.name}: {message}")
                    results["passed_rules"] += 1
                    if worst_status.value < ValidationStatus.WARNING.value:
                        worst_status = ValidationStatus.WARNING
                elif status == ValidationStatus.ERROR:
                    results["issues"].append(f"{rule.name}: {message}")
                    results["failed_rules"] += 1
                    if worst_status.value < ValidationStatus.ERROR.value:
                        worst_status = ValidationStatus.ERROR
                elif status == ValidationStatus.CRITICAL:
                    results["issues"].append(f"{rule.name}: {message}")
                    results["failed_rules"] += 1
                    worst_status = ValidationStatus.CRITICAL
                    break  # 严重错误，终止校验
                    
            except Exception as e:
                logger.error(f"校验规则 {rule.name} 执行失败：{e}")
                results["issues"].append(f"{rule.name}: 执行错误 - {str(e)}")
                results["failed_rules"] += 1
        
        results["status"] = worst_status.value
        
        # 记录校验日志
        self._log_validation_result(results)
        
        return results
    
    def _log_validation_result(self, results: Dict):
        """记录校验结果日志"""
        status = results["status"]
        passed = results["passed_rules"]
        total = results["total_rules"]
        
        if status == ValidationStatus.CRITICAL.value:
            logger.error(f"数据校验失败（严重）: {passed}/{total} 规则通过")
        elif status == ValidationStatus.ERROR.value:
            logger.error(f"数据校验失败：{passed}/{total} 规则通过")
        elif status == ValidationStatus.WARNING.value:
            logger.warning(f"数据校验警告：{passed}/{total} 规则通过")
        else:
            logger.info(f"数据校验通过：{passed}/{total} 规则通过")
    
    def validate_batch(self, all_data: Dict[str, List[Dict]]) -> Dict:
        """
        批量校验（用于多个 PDF 文件）
        
        Args:
            all_data: {文件路径：财务数据列表}
            
        Returns:
            批量校验报告
        """
        total_files = len(all_data)
        failed_files = 0
        failure_rate = 0.0
        
        file_results = {}
        
        for file_path, data in all_data.items():
            result = self.validate(data)
            file_results[file_path] = result
            
            if result["status"] in [ValidationStatus.ERROR.value, ValidationStatus.CRITICAL.value]:
                failed_files += 1
        
        if total_files > 0:
            failure_rate = failed_files / total_files
        
        report = {
            "total_files": total_files,
            "failed_files": failed_files,
            "success_files": total_files - failed_files,
            "failure_rate": failure_rate,
            "threshold": self.failure_rate_threshold,
            "exceeds_threshold": failure_rate > self.failure_rate_threshold,
            "file_results": file_results
        }
        
        if report["exceeds_threshold"]:
            logger.error(
                f"批量校验失败率 {failure_rate:.2%} 超过阈值 "
                f"{self.failure_rate_threshold:.2%}"
            )
        
        return report


# 全局校验器实例
validator = DataValidator()


def validate_financial_data(data: List[Dict]) -> Dict:
    """便捷函数：校验财务数据"""
    return validator.validate(data)


def validate_batch_data(all_data: Dict[str, List[Dict]]) -> Dict:
    """便捷函数：批量校验"""
    return validator.validate_batch(all_data)
