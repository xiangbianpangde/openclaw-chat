"""
控制台日志模块

提供控制台日志、错误、网络日志捕获等功能
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
try:
    from .cdp_client import CDPSession
except ImportError:
    from cdp_client import CDPSession


class ConsoleLogger:
    """控制台日志捕获器"""
    
    def __init__(self, session: CDPSession):
        """
        初始化日志捕获器
        
        Args:
            session: CDP 会话
        """
        self.session = session
        self.logs: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.exceptions: List[Dict[str, Any]] = []
        self.network_logs: List[Dict[str, Any]] = []
    
    async def enable(self) -> None:
        """启用日志相关 Domain"""
        await self.session.enable_domain("Log")
        await self.session.enable_domain("Runtime")
        await self.session.enable_domain("Network")
        
        # 注册事件监听
        self.session.on("Log.entryAdded", self._on_log_entry)
        self.session.on("Runtime.consoleAPICalled", self._on_console_api)
        self.session.on("Runtime.exceptionThrown", self._on_exception)
        self.session.on("Network.requestWillBeSent", self._on_network_request)
        self.session.on("Network.responseReceived", self._on_network_response)
    
    def _on_log_entry(self, params: Dict[str, Any]) -> None:
        """处理日志条目事件"""
        entry = params.get("entry", {})
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "source": entry.get("source"),
            "level": entry.get("level"),
            "text": entry.get("text"),
            "url": entry.get("url"),
            "lineNumber": entry.get("lineNumber")
        }
        
        self.logs.append(log_data)
    
    def _on_console_api(self, params: Dict[str, Any]) -> None:
        """处理控制台 API 调用事件"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "type": params.get("type"),
            "args": [arg.get("value", str(arg)) for arg in params.get("args", [])],
            "url": params.get("url"),
            "lineNumber": params.get("lineNumber")
        }
        
        self.logs.append(log_data)
        
        # 如果是错误类型，也记录到 errors
        if params.get("type") in ["error", "assert"]:
            self.errors.append(log_data)
    
    def _on_exception(self, params: Dict[str, Any]) -> None:
        """处理异常事件"""
        exception = params.get("exceptionDetails", {})
        exception_data = {
            "timestamp": datetime.now().isoformat(),
            "exceptionId": exception.get("exceptionId"),
            "text": exception.get("text"),
            "lineNumber": exception.get("lineNumber"),
            "columnNumber": exception.get("columnNumber"),
            "url": exception.get("url"),
            "stackTrace": exception.get("stackTrace", {})
        }
        
        self.exceptions.append(exception_data)
        self.errors.append(exception_data)
    
    def _on_network_request(self, params: Dict[str, Any]) -> None:
        """处理网络请求事件"""
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "requestId": params.get("requestId"),
            "url": params.get("request", {}).get("url"),
            "method": params.get("request", {}).get("method"),
            "headers": params.get("request", {}).get("headers", {})
        }
        
        self.network_logs.append(request_data)
    
    def _on_network_response(self, params: Dict[str, Any]) -> None:
        """处理网络响应事件"""
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "requestId": params.get("requestId"),
            "status": params.get("response", {}).get("status"),
            "statusText": params.get("response", {}).get("statusText"),
            "mimeType": params.get("response", {}).get("mimeType")
        }
        
        # 更新对应的请求
        for log in self.network_logs:
            if log.get("requestId") == response_data.get("requestId"):
                log.update(response_data)
                break
    
    async def get_logs(self, level: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取日志列表
        
        Args:
            level: 日志级别过滤
            limit: 返回数量限制
            
        Returns:
            日志列表
        """
        logs = self.logs[-limit:]
        
        if level:
            logs = [l for l in logs if l.get("level") == level]
        
        return logs
    
    async def get_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取错误列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            错误列表
        """
        return self.errors[-limit:]
    
    async def get_network_logs(self, url_pattern: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取网络日志
        
        Args:
            url_pattern: URL 过滤模式
            limit: 返回数量限制
            
        Returns:
            网络日志列表
        """
        logs = self.network_logs[-limit:]
        
        if url_pattern:
            logs = [l for l in logs if url_pattern in l.get("url", "")]
        
        return logs
    
    async def clear_logs(self) -> None:
        """清除所有日志"""
        self.logs.clear()
        self.errors.clear()
        self.network_logs.clear()
    
    async def export_logs(self, path: str) -> str:
        """
        导出日志到文件
        
        Args:
            path: 文件路径
            
        Returns:
            保存的文件路径
        """
        import json
        
        data = {
            "logs": self.logs,
            "errors": self.errors,
            "network_logs": self.network_logs,
            "exported_at": datetime.now().isoformat()
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return path
