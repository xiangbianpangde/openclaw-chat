"""
数据查询接口（NL2SQL）
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Any
import time

from config.settings import settings

router = APIRouter()


class QueryRequest(BaseModel):
    """自然语言查询请求"""
    query: str  # 自然语言问题
    company_code: Optional[str] = None
    report_year: Optional[int] = None
    top_k: int = 5


class QueryResponse(BaseModel):
    """查询响应"""
    query: str
    sql: Optional[str]
    data: List[Any]
    total: int
    execution_time_ms: float
    source: str  # nl2sql / rule / rag


@router.post("/natural-language", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest):
    """自然语言查询（NL2SQL）"""
    
    start_time = time.time()
    
    # TODO: 实现 NL2SQL 引擎
    # 当前返回示例数据
    generated_sql = f"SELECT * FROM financial_data WHERE company_code = '{request.company_code}' LIMIT {request.top_k}"
    
    # 模拟查询结果
    sample_data = [
        {
            "company_code": request.company_code or "600519",
            "report_year": request.report_year or 2023,
            "metric_name": "营业收入",
            "metric_value": 123456789.00,
            "unit": "元"
        }
    ]
    
    execution_time = (time.time() - start_time) * 1000
    
    return QueryResponse(
        query=request.query,
        sql=generated_sql,
        data=sample_data,
        total=len(sample_data),
        execution_time_ms=execution_time,
        source="nl2sql"
    )


@router.post("/sql")
async def execute_sql(sql: str):
    """直接执行 SQL 查询"""
    
    start_time = time.time()
    
    # TODO: 实现 SQL 执行器
    # 注意：需要 SQL 注入防护
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        "sql": sql,
        "data": [],
        "total": 0,
        "execution_time_ms": execution_time
    }


@router.get("/financial/{company_code}")
async def get_financial_data(
    company_code: str,
    year: Optional[int] = None,
    metric: Optional[str] = None
):
    """获取公司财务数据"""
    
    # TODO: 从数据库查询
    return {
        "company_code": company_code,
        "year": year,
        "metrics": [
            {"name": "营业收入", "value": 123456.78, "unit": "万元", "year": 2023},
            {"name": "净利润", "value": 23456.78, "unit": "万元", "year": 2023},
            {"name": "总资产", "value": 345678.90, "unit": "万元", "year": 2023},
        ]
    }


@router.get("/compare")
async def compare_companies(
    companies: str,  # 逗号分隔的公司代码
    metric: str,
    year: Optional[int] = None
):
    """比较多家公司的财务指标"""
    
    company_codes = [c.strip() for c in companies.split(",")]
    
    # TODO: 从数据库查询并比较
    return {
        "metric": metric,
        "year": year,
        "comparison": [
            {"company_code": code, "value": 0, "rank": i + 1}
            for i, code in enumerate(company_codes)
        ]
    }
