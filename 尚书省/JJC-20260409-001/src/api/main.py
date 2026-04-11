"""
FastAPI 应用主入口
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time

from config.settings import settings
from src.api.routes import health, pdf, query, auth, admin
from src.core.middleware import AuditMiddleware, MetricsMiddleware


# 配置日志
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="5 days"
)


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="泰迪杯 B 题：上市公司财报智能问数助手 API",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加中间件
    app.add_middleware(AuditMiddleware)
    app.add_middleware(MetricsMiddleware)
    
    # 注册路由
    app.include_router(health.router, prefix="/api/health", tags=["健康检查"])
    app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
    app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF 管理"])
    app.include_router(query.router, prefix="/api/query", tags=["数据查询"])
    app.include_router(admin.router, prefix="/api/admin", tags=["管理"])
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"全局异常：{exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误", "error": str(exc) if settings.DEBUG else "Internal Server Error"}
        )
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"应用启动：{settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info(f"环境：{settings.ENVIRONMENT}")
        logger.info(f"数据库：{settings.DATABASE_URL}")
        logger.info(f"Redis: {settings.REDIS_URL}")
        logger.info(f"MinIO: {settings.MINIO_ENDPOINT}")
    
    # 关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("应用关闭")
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
