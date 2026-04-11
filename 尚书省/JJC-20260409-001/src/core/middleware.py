"""
中间件模块
"""

from fastapi import Request
from fastapi.responses import Response
import time
import json
import logging
from datetime import datetime

from config.settings import settings


# 配置审计日志
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
audit_handler = logging.FileHandler('./logs/audit.log')
audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
audit_logger.addHandler(audit_handler)


class AuditMiddleware:
    """审计日志中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        
        start_time = datetime.utcnow()
        
        # 执行请求
        response = await self.app(scope, receive, send)
        
        # 记录审计日志
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # 简化处理，实际应从 scope 中获取更多信息
        audit_log = {
            'timestamp': start_time.isoformat(),
            'path': scope.get('path', ''),
            'method': scope.get('method', ''),
            'response_time_ms': duration_ms,
        }
        
        audit_logger.info(json.dumps(audit_log))
        
        return response


class MetricsMiddleware:
    """Prometheus 指标采集中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        # 执行请求
        response = await self.app(scope, receive, send)
        
        # 记录指标（实际应使用 prometheus_client）
        duration = time.time() - start_time
        
        # TODO: 记录到 Prometheus
        # REQUEST_COUNT.labels(method=scope['method'], endpoint=scope['path']).inc()
        # REQUEST_LATENCY.labels(method=scope['method'], endpoint=scope['path']).observe(duration)
        
        return response
