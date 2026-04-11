"""
归因分析模块
实现结果溯源和置信度评估
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AttributionSource:
    """归因来源"""
    type: str  # 'sql' or 'document'
    source: str  # SQL statement or document ID
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AttributionTracker:
    """归因追踪器"""
    
    def __init__(self):
        """初始化归因追踪器"""
        self.sources: List[AttributionSource] = []
    
    def add_sql_source(
        self,
        sql: str,
        table_names: List[str],
        row_count: int,
        confidence: Optional[float] = None
    ):
        """
        添加 SQL 数据源
        
        Args:
            sql: SQL 语句
            table_names: 表名列表
            row_count: 结果行数
            confidence: 置信度（可选，自动计算）
        """
        if confidence is None:
            confidence = self._calculate_sql_confidence(sql, row_count)
        
        self.sources.append(AttributionSource(
            type='sql',
            source=sql,
            confidence=confidence,
            metadata={
                'tables': table_names,
                'rows': row_count
            }
        ))
    
    def add_document_source(
        self,
        doc_id: str,
        chunk_ids: List[str],
        relevance_scores: List[float],
        confidence: Optional[float] = None
    ):
        """
        添加文档数据源
        
        Args:
            doc_id: 文档 ID
            chunk_ids: 分块 ID 列表
            relevance_scores: 相关性分数列表
            confidence: 置信度（可选，自动计算）
        """
        if confidence is None:
            confidence = self._calculate_doc_confidence(relevance_scores)
        
        self.sources.append(AttributionSource(
            type='document',
            source=doc_id,
            confidence=confidence,
            metadata={
                'chunks': chunk_ids,
                'relevance_scores': relevance_scores
            }
        ))
    
    def get_attribution(self) -> Dict[str, Any]:
        """获取归因信息"""
        return {
            'sources': [
                {
                    'type': s.type,
                    'source': s.source,
                    'confidence': s.confidence,
                    'metadata': s.metadata
                }
                for s in self.sources
            ],
            'overall_confidence': self._calculate_overall_confidence(),
            'total_sources': len(self.sources)
        }
    
    def _calculate_sql_confidence(self, sql: str, row_count: int) -> float:
        """计算 SQL 置信度"""
        # 基于查询复杂度、结果数量评估
        complexity = len(sql.split())
        
        if row_count == 0:
            return 0.5  # 无结果，置信度降低
        
        if complexity < 10:
            return 0.95  # 简单查询
        elif complexity < 20:
            return 0.85  # 中等复杂度
        else:
            return 0.75  # 复杂查询
    
    def _calculate_doc_confidence(self, relevance_scores: List[float]) -> float:
        """计算文档置信度"""
        if not relevance_scores:
            return 0.5
        
        # 平均相关性分数
        avg_score = sum(relevance_scores) / len(relevance_scores)
        
        # 映射到 0.5-1.0 范围
        return 0.5 + (avg_score * 0.5)
    
    def _calculate_overall_confidence(self) -> float:
        """计算整体置信度"""
        if not self.sources:
            return 0.0
        
        confidences = [s.confidence for s in self.sources]
        return sum(confidences) / len(confidences)
    
    def format_attribution(self) -> str:
        """格式化归因信息"""
        if not self.sources:
            return "无数据来源"
        
        formatted = []
        
        for i, source in enumerate(self.sources, 1):
            if source.type == 'sql':
                tables = source.metadata.get('tables', [])
                rows = source.metadata.get('rows', 0)
                formatted.append(
                    f"[{i}] 财务数据库 - {', '.join(tables)}表（{rows}行数据），"
                    f"置信度：{self._confidence_label(source.confidence)}"
                )
            elif source.type == 'document':
                doc_id = source.source
                chunks = len(source.metadata.get('chunks', []))
                formatted.append(
                    f"[{i}] 文档 {doc_id}（{chunks}个分块），"
                    f"置信度：{self._confidence_label(source.confidence)}"
                )
        
        return '\n'.join(formatted)
    
    def _confidence_label(self, confidence: float) -> str:
        """置信度标签"""
        if confidence >= 0.85:
            return "高"
        elif confidence >= 0.60:
            return "中"
        else:
            return "低"


class ConfidenceEvaluator:
    """置信度评估器"""
    
    def __init__(self):
        """初始化置信度评估器"""
        pass
    
    def evaluate(
        self,
        answer: str,
        sources: List[AttributionSource],
        context_length: int = 0
    ) -> Dict[str, Any]:
        """
        评估答案置信度
        
        Args:
            answer: 答案文本
            sources: 数据来源列表
            context_length: 上下文长度
        
        Returns:
            置信度评估结果
        """
        # 基于来源数量
        source_score = min(1.0, len(sources) / 3.0) * 0.4
        
        # 基于来源置信度
        if sources:
            avg_confidence = sum(s.confidence for s in sources) / len(sources)
            confidence_score = avg_confidence * 0.4
        else:
            confidence_score = 0.0
        
        # 基于答案长度
        answer_length = len(answer)
        if 50 <= answer_length <= 500:
            length_score = 0.2
        elif answer_length < 50:
            length_score = 0.1
        else:
            length_score = 0.15
        
        # 基于上下文长度
        if context_length > 0:
            context_score = 0.1
        else:
            context_score = 0.0
        
        # 总体置信度
        overall_confidence = source_score + confidence_score + length_score + context_score
        
        return {
            'overall_confidence': overall_confidence,
            'confidence_label': self._confidence_label(overall_confidence),
            'breakdown': {
                'source_score': source_score,
                'confidence_score': confidence_score,
                'length_score': length_score,
                'context_score': context_score
            }
        }
    
    def _confidence_label(self, confidence: float) -> str:
        """置信度标签"""
        if confidence >= 0.85:
            return "高"
        elif confidence >= 0.60:
            return "中"
        else:
            return "低"


# 便捷函数
def create_attribution_tracker() -> AttributionTracker:
    """创建归因追踪器"""
    return AttributionTracker()


def create_confidence_evaluator() -> ConfidenceEvaluator:
    """创建置信度评估器"""
    return ConfidenceEvaluator()


    # 兼容方法
    def add_source(self, source_type, content, **kwargs):
        """添加来源（兼容方法）"""
        if source_type == '财报原文':
            return self.add_document_source(content, kwargs.get('url', ''))
        elif source_type == '数据库':
            return self.add_sql_source(content, kwargs.get('table', ''))
        else:
            return self.add_document_source(content, '')
