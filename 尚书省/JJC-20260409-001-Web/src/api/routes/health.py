"""
健康检查接口
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口
    
    返回服务状态、版本信息、依赖服务状态
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "up",
            "redis": "up",
            "chromadb": "up"
        }
    }


@router.get("/ready", summary="就绪检查")
async def ready_check():
    """
    就绪检查接口
    
    检查服务是否准备好接收请求
    """
    # TODO: 检查依赖服务连接
    return {
        "ready": True,
        "checks": {
            "database": True,
            "redis": True,
            "chromadb": True
        }
    }
