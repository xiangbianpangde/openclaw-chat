"""
健康检查接口
"""

from fastapi import APIRouter
from datetime import datetime
import psutil

router = APIRouter()


@router.get("/")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }


@router.get("/detailed")
async def detailed_health_check():
    """详细健康检查"""
    
    # 系统资源
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / 1024 / 1024,
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / 1024 / 1024 / 1024
        },
        "services": {
            "api": "up",
            "database": "pending_check",
            "redis": "pending_check",
            "minio": "pending_check"
        }
    }


@router.get("/metrics")
async def metrics():
    """Prometheus 格式指标"""
    # 简化版本，实际应使用 prometheus_client 库
    return {
        "app_uptime_seconds": 0,
        "app_requests_total": 0,
        "app_errors_total": 0
    }
