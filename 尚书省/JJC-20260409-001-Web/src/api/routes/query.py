"""
查询接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any, Dict

from src.api.error_codes import bad_request, internal_error

router = APIRouter()


# 请求模型
class QueryRequest(BaseModel):
    """查询请求"""
    query: str
    intent: Optional[str] = "auto"
    n_results: Optional[int] = 5


# 响应模型
class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    sql_result: Optional[Any] = None
    document_context: Optional[List[str]] = None
    confidence: float
    attribution: Optional[Dict[str, Any]] = None


@router.post("/query", response_model=QueryResponse, summary="自然语言查询")
async def query_endpoint(request: QueryRequest):
    """
    自然语言查询接口
    
    - **query**: 用户查询文本
    - **intent**: 查询意图（auto/fact/analysis/explanation）
    - **n_results**: 返回结果数量
    
    返回查询结果，包括答案、SQL 结果、文档上下文等
    """
    try:
        # TODO: 调用 NL2SQL+RAG 引擎
        # 模拟响应
        return QueryResponse(
            answer="贵州茅台 2024 年的营业收入为 1234.56 亿元。",
            sql_result={"revenue": 123456000000, "period": "2024"},
            document_context=["贵州茅台 2024 年年度报告显示..."],
            confidence=0.95,
            attribution={"type": "hybrid", "sql": "SELECT...", "docs": 1}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/batch", summary="批量查询")
async def query_batch(queries: List[str]):
    """
    批量查询接口
    
    - **queries**: 查询文本列表
    
    返回多个查询结果
    """
    results = []
    for query in queries:
        # TODO: 调用查询引擎
        results.append({
            "query": query,
            "answer": "模拟回答",
            "confidence": 0.9
        })
    
    return {"results": results, "total": len(queries)}
