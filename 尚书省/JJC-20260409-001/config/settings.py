"""
配置管理模块
支持多环境配置（开发/测试/生产）
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "泰迪杯 B 题 - 财报智能问数助手"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:caiwu123@localhost:3306/caiwu_assistant"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MinIO 配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "caiwu"
    MINIO_SECRET_KEY: str = "caiwu123456"
    MINIO_BUCKET: str = "pdf-storage"
    MINIO_SECURE: bool = False
    
    # JWT 配置
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_HOURS: int = 24
    
    # PDF 解析配置
    PDF_MAX_FILE_SIZE_MB: int = 200
    PDF_MAX_PAGE_COUNT: int = 500
    PDF_ENABLE_CHUNKING: bool = True
    PDF_CHUNK_SIZE_PAGES: int = 100
    PDF_WORKER_CONCURRENCY: int = 8
    
    # NL2SQL 配置
    NL2SQL_MODEL_NAME: str = "codellama/CodeLlama-7b-hf"
    NL2SQL_LORA_R: int = 16
    NL2SQL_LORA_ALPHA: int = 32
    NL2SQL_MAX_SEQ_LENGTH: int = 512
    
    # RAG 配置
    RAG_VECTOR_DB_PATH: str = "./data/chroma_db"
    RAG_EMBEDDING_MODEL: str = "bge-large-zh-v1.5"
    RAG_TOP_K_RESULTS: int = 5
    
    # 任务调度配置
    TASK_MAX_CONCURRENT: int = 5
    TASK_MAX_QUEUE_SIZE: int = 100
    TASK_TIMEOUT_SECONDS: int = 3600
    TASK_RETRY_MAX_ATTEMPTS: int = 3
    
    # 数据质量配置
    DATA_FAILURE_RATE_THRESHOLD: float = 0.05
    DATA_AUTO_PAUSE_ON_FAILURE: bool = True
    DATA_ERROR_SAMPLE_SIZE: int = 100
    
    # 网络重试配置
    NETWORK_RETRY_MAX_ATTEMPTS: int = 3
    NETWORK_RETRY_INITIAL_DELAY: int = 2
    NETWORK_RETRY_MAX_DELAY: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # 监控配置
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8000
    
    # 安全配置
    CORS_ORIGINS: list = ["*"]
    API_RATE_LIMIT: str = "100/minute"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """开发环境配置"""
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"


class TestSettings(Settings):
    """测试环境配置"""
    DEBUG: bool = True
    ENVIRONMENT: str = "test"
    DATABASE_URL: str = "mysql+pymysql://root:caiwu123@localhost:3306/caiwu_assistant_test"
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """生产环境配置"""
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    MINIO_SECURE: bool = True
    LOG_LEVEL: str = "INFO"


# 配置工厂
def get_settings() -> Settings:
    """根据环境变量获取对应配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()


# 全局配置实例
settings = get_settings()
