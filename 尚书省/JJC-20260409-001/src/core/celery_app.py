"""
Celery 任务调度配置
"""

from celery import Celery
from config.settings import settings


# 创建 Celery 应用
celery_app = Celery(
    'caiwu_assistant',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['src.core.tasks']
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 时区
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务确认
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 预取限制
    worker_prefetch_multiplier=1,
    
    # 任务速率限制
    task_rate_limit='10/m',
    
    # 任务超时
    task_soft_time_limit=3600,
    task_time_limit=7200,
    
    # 重试配置
    task_default_retry=True,
    task_default_max_retries=3,
    
    # 结果过期
    result_expires=3600,
)


# 定时任务配置
celery_app.conf.beat_schedule = {
    'cleanup-old-tasks': {
        'task': 'src.core.tasks.cleanup_old_tasks',
        'schedule': 3600.0,  # 每小时执行一次
    },
    'check-parse-failure-rate': {
        'task': 'src.core.tasks.check_parse_failure_rate',
        'schedule': 300.0,  # 每 5 分钟检查一次
    },
}


if __name__ == '__main__':
    celery_app.start()
