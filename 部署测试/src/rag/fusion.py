"""
RAG+NL2SQL 融合模块
实现检索增强生成
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class FusionResult:
    """融合结果"""
    answer: str
    sql_result: Optional[Any]
    document_context: List[str]
    confidence: float
    attribution: Dict[str, Any]


class RAGNL2SQLFusion:
    """RAG+NL2SQL 融合引擎"""
    
    def __init__(self, nl2sql_engine, rag_retriever, llm_client):
        """
        初始化融合引擎
        
        Args:
            nl2sql_engine: NL2SQL 引擎
            rag_retriever: RAG 检索器
            llm_client: LLM 客户端
        """
        self.nl2sql = nl2sql_engine
        self.rag = rag_retriever
        self.llm = llm_client
    
    def query(self, user_query: str, intent: str = 'auto') -> FusionResult:
        """
        融合查询
        
        Args:
            user_query: 用户查询
            intent: 查询意图（auto/fact/analysis/explanation）
        
        Returns:
            融合结果
        """
        # 自动识别意图
        if intent == 'auto':
            intent = self._classify_intent(user_query)
        
        # 根据意图路由
        if intent == 'fact':
            return self._fact_query(user_query)
        elif intent == 'analysis':
            return self._analysis_query(user_query)
        elif intent == 'explanation':
            return self._explanation_query(user_query)
        else:
            return self._hybrid_query(user_query)
    
    def _classify_intent(self, query: str) -> str:
        """分类查询意图"""
        query_lower = query.lower()
        
        # 事实查询关键词
        fact_keywords = ['多少', '是什么', '查询', '数值', '数据']
        if any(kw in query_lower for kw in fact_keywords):
            return 'fact'
        
        # 解释查询关键词
        explanation_keywords = ['为什么', '如何', '原因', '解释', '分析']
        if any(kw in query_lower for kw in explanation_keywords):
            return 'explanation'
        
        # 分析查询
        analysis_keywords = ['对比', '趋势', '比较', '排名', '平均']
        if any(kw in query_lower for kw in analysis_keywords):
            return 'analysis'
        
        # 默认混合查询
        return 'hybrid'
    
    def _fact_query(self, user_query: str) -> FusionResult:
        """事实查询（纯 NL2SQL）"""
        # 生成 SQL
        sql = self.nl2sql.generate(user_query)
        
        # 执行 SQL
        sql_result = self.nl2sql.execute(sql)
        
        # 格式化结果
        answer = self._format_sql_result(sql_result)
        
        return FusionResult(
            answer=answer,
            sql_result=sql_result,
            document_context=[],
            confidence=0.95,
            attribution={'type': 'sql', 'sql': sql}
        )
    
    def _analysis_query(self, user_query: str) -> FusionResult:
        """分析查询（NL2SQL+RAG）"""
        # 生成 SQL
        sql = self.nl2sql.generate(user_query)
        
        # 执行 SQL
        db_result = self.nl2sql.execute(sql)
        
        # 检索相关文档
        context = self.rag.retrieve(user_query, n_results=3)
        context_texts = [doc['document'] for doc in context] if context else []
        
        # 融合结果
        answer = self._fuse_result(user_query, db_result, context_texts)
        
        return FusionResult(
            answer=answer,
            sql_result=db_result,
            document_context=context_texts,
            confidence=0.90,
            attribution={'type': 'hybrid', 'sql': sql, 'docs': len(context_texts)}
        )
    
    def _explanation_query(self, user_query: str) -> FusionResult:
        """解释查询（纯 RAG）"""
        # 检索相关文档
        context = self.rag.retrieve(user_query, n_results=5)
        context_texts = [doc['document'] for doc in context] if context else []
        
        # 生成回答
        answer = self._generate_answer(user_query, context_texts)
        
        return FusionResult(
            answer=answer,
            sql_result=None,
            document_context=context_texts,
            confidence=0.85,
            attribution={'type': 'rag', 'docs': len(context_texts)}
        )
    
    def _hybrid_query(self, user_query: str) -> FusionResult:
        """混合查询（RAG→NL2SQL）"""
        # 先检索文档
        context = self.rag.retrieve(user_query, n_results=3)
        context_texts = [doc['document'] for doc in context] if context else []
        
        # 增强查询
        enhanced_query = self._enhance_query(user_query, context_texts)
        
        # 生成 SQL
        sql = self.nl2sql.generate(enhanced_query)
        
        # 执行 SQL
        result = self.nl2sql.execute(sql)
        
        # 融合结果
        answer = self._fuse_result(user_query, result, context_texts)
        
        return FusionResult(
            answer=answer,
            sql_result=result,
            document_context=context_texts,
            confidence=0.88,
            attribution={'type': 'hybrid', 'sql': sql, 'docs': len(context_texts)}
        )
    
    def _fuse_result(self, query: str, db_result: Any, context: List[str]) -> str:
        """融合数据库结果和文档上下文"""
        prompt = f"""你是一个财务分析助手。根据数据库查询结果和文档上下文，回答用户问题。

用户问题：{query}

数据库查询结果：
{db_result}

相关文档：
{chr(10).join(context)}

请综合以上信息，给出完整回答。回答中需标注信息来源。
"""
        
        response = self.llm.generate(prompt)
        return response
    
    def _generate_answer(self, query: str, context: List[str]) -> str:
        """根据文档上下文生成回答"""
        prompt = f"""你是一个财务分析助手。根据文档上下文，回答用户问题。

用户问题：{query}

相关文档：
{chr(10).join(context)}

请根据以上文档，给出完整回答。回答中需标注信息来源。
"""
        
        response = self.llm.generate(prompt)
        return response
    
    def _enhance_query(self, query: str, context: List[str]) -> str:
        """增强查询"""
        # 从上下文中提取关键信息
        context_summary = ' '.join(context[:2]) if context else ''
        
        # 增强查询
        enhanced = f"{query}。相关背景：{context_summary}"
        
        return enhanced
    
    def _format_sql_result(self, result: Any) -> str:
        """格式化 SQL 结果"""
        if result is None:
            return "无数据"
        
        if isinstance(result, list):
            if len(result) == 0:
                return "无数据"
            elif len(result) == 1:
                return str(result[0])
            else:
                return f"共{len(result)}条数据：" + ', '.join(str(r) for r in result[:5])
        
        return str(result)


# 便捷函数
def create_fusion_engine(nl2sql_engine, rag_retriever, llm_client) -> RAGNL2SQLFusion:
    """创建融合引擎"""
    return RAGNL2SQLFusion(nl2sql_engine, rag_retriever, llm_client)


# 别名兼容
RAGFusionEngine = RAGFusion


# 别名兼容（用于测试导入）
RAGFusionEngine = RAGNL2SQLFusion
