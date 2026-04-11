"""
Celery 任务定义
"""

from celery import Task
from loguru import logger
import time

from src.core.celery_app import celery_app
from config.settings import settings


@celery_app.task(bind=True, max_retries=3)
def parse_pdf_task(self, file_path: str, task_id: str):
    """
    PDF 解析任务
    
    Args:
        file_path: PDF 文件路径
        task_id: 任务 ID
    """
    try:
        logger.info(f"开始解析 PDF: {file_path}")
        
        # TODO: 实现 PDF 解析逻辑
        # 1. 使用 PyMuPDF 解析 PDF
        # 2. 提取文本和表格
        # 3. 提取财务数据
        # 4. 校验数据
        # 5. 保存到数据库
        
        # 模拟解析过程
        time.sleep(2)
        
        logger.info(f"PDF 解析完成：{file_path}")
        
        return {
            "status": "success",
            "file_path": file_path,
            "pages_parsed": 100,
            "tables_extracted": 20
        }
        
    except Exception as e:
        logger.error(f"PDF 解析失败：{file_path}, 错误：{e}")
        
        # 重试逻辑
        try:
            self.retry(exc=e, countdown=60)  # 60 秒后重试
        except self.MaxRetriesExceededError:
            logger.error(f"PDF 解析任务达到最大重试次数：{file_path}")
            
            return {
                "status": "failed",
                "file_path": file_path,
                "error": str(e)
            }


@celery_app.task
def cleanup_old_tasks():
    """清理旧任务（定时任务）"""
    logger.info("执行旧任务清理")
    # TODO: 清理超过 30 天的已完成任务
    return {"status": "success"}


@celery_app.task
def check_parse_failure_rate():
    """检查解析失败率（定时任务）"""
    logger.info("检查解析失败率")
    
    # TODO: 从数据库查询最近任务的失败率
    # 如果失败率超过阈值，触发告警
    
    failure_rate = 0.02  # 示例数据
    
    if failure_rate > settings.DATA_FAILURE_RATE_THRESHOLD:
        logger.error(f"解析失败率 {failure_rate:.2%} 超过阈值 {settings.DATA_FAILURE_RATE_THRESHOLD:.2%}")
        # TODO: 发送告警通知
    
    return {
        "failure_rate": failure_rate,
        "threshold": settings.DATA_FAILURE_RATE_THRESHOLD,
        "status": "normal" if failure_rate <= settings.DATA_FAILURE_RATE_THRESHOLD else "alert"
    }


@celery_app.task
def batch_parse_pdfs(file_paths: list, task_id: str):
    """
    批量 PDF 解析任务
    
    Args:
        file_paths: PDF 文件路径列表
        task_id: 任务 ID
    """
    logger.info(f"开始批量解析 {len(file_paths)} 个 PDF 文件")
    
    results = []
    for i, file_path in enumerate(file_paths):
        try:
            # 调用单个解析任务
            result = parse_pdf_task.delay(file_path, task_id)
            results.append({
                "file": file_path,
                "status": "queued",
                "task_id": result.id
            })
            
            # 每处理 10 个文件记录一次进度
            if (i + 1) % 10 == 0:
                logger.info(f"已提交 {i + 1}/{len(file_paths)} 个解析任务")
                
        except Exception as e:
            logger.error(f"提交解析任务失败：{file_path}, 错误：{e}")
            results.append({
                "file": file_path,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "task_id": task_id,
        "total": len(file_paths),
        "results": results
    }
