"""
CDP 客户端

提供 Chrome DevTools Protocol WebSocket 连接和命令执行能力
"""

import asyncio
import json
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import websockets


class CDPSession:
    """CDP 会话管理类"""
    
    def __init__(self, ws_url: str = None):
        """
        初始化 CDP 会话
        
        Args:
            ws_url: Chrome DevTools WebSocket URL
        """
        self.ws_url = ws_url
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.message_id = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}
        self.enabled_domains: List[str] = []
        
    async def connect(self, ws_url: str = None) -> None:
        """
        连接到 CDP WebSocket
        
        Args:
            ws_url: Chrome DevTools WebSocket URL
        """
        url = ws_url or self.ws_url
        if not url:
            raise ValueError("WebSocket URL 未提供")
        
        self.ws = await websockets.connect(url)
        print(f"✅ CDP 已连接：{url}")
        
        # 启动消息接收循环
        asyncio.create_task(self._receive_messages())
    
    async def disconnect(self) -> None:
        """断开 CDP 连接"""
        if self.ws:
            await self.ws.close()
            print("❌ CDP 已断开连接")
    
    async def send(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送 CDP 命令
        
        Args:
            method: CDP 方法名
            params: 方法参数
            
        Returns:
            CDP 响应
        """
        self.message_id += 1
        message_id = self.message_id
        
        # 创建等待未来的对象
        future = asyncio.Future()
        self.pending_requests[message_id] = future
        
        # 构建消息
        message = {
            "id": message_id,
            "method": method,
            "params": params or {}
        }
        
        # 发送消息
        await self.ws.send(json.dumps(message))
        
        # 等待响应
        try:
            result = await asyncio.wait_for(future, timeout=30)
            return result
        except asyncio.TimeoutError:
            del self.pending_requests[message_id]
            raise TimeoutError(f"CDP 命令超时：{method}")
    
    async def _receive_messages(self) -> None:
        """接收 CDP 消息循环"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                
                # 处理响应
                if "id" in data and data["id"] in self.pending_requests:
                    future = self.pending_requests.pop(data["id"])
                    if "error" in data:
                        future.set_exception(Exception(data["error"]["message"]))
                    else:
                        future.set_result(data.get("result", {}))
                
                # 处理事件
                elif "method" in data:
                    await self._handle_event(data["method"], data.get("params", {}))
                    
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ CDP 连接已关闭")
    
    async def _handle_event(self, method: str, params: Dict[str, Any]) -> None:
        """
        处理 CDP 事件
        
        Args:
            method: 事件方法名
            params: 事件参数
        """
        if method in self.event_listeners:
            for callback in self.event_listeners[method]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(params)
                    else:
                        callback(params)
                except Exception as e:
                    print(f"⚠️ 事件处理错误：{method} - {e}")
    
    def on(self, event: str, callback: Callable) -> None:
        """
        注册事件监听器
        
        Args:
            event: 事件名
            callback: 回调函数
        """
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        self.event_listeners[event].append(callback)
    
    async def enable_domain(self, domain: str) -> None:
        """
        启用 CDP Domain
        
        Args:
            domain: Domain 名称
        """
        if domain not in self.enabled_domains:
            await self.send(f"{domain}.enable")
            self.enabled_domains.append(domain)
            print(f"✅ Domain 已启用：{domain}")
    
    async def navigate(self, url: str, wait_strategy: str = "networkidle", timeout: int = 30000) -> Dict[str, Any]:
        """
        导航到 URL
        
        Args:
            url: 目标 URL
            wait_strategy: 等待策略 (load, domcontentloaded, networkidle)
            timeout: 超时时间 (ms)
            
        Returns:
            导航结果
        """
        # 启用 Page Domain
        await self.enable_domain("Page")
        
        # 导航
        result = await self.send("Page.navigate", {"url": url})
        
        # 等待加载完成
        if wait_strategy == "networkidle":
            await self.wait_for_network_idle(timeout)
        elif wait_strategy == "domcontentloaded":
            await self.send("Page.domContentEventFired")
        
        return result
    
    async def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """
        等待网络空闲
        
        Args:
            timeout: 超时时间 (ms)
        """
        await asyncio.sleep(timeout / 1000)
    
    async def get_version(self) -> Dict[str, Any]:
        """获取浏览器版本信息"""
        return await self.send("Browser.getVersion")
    
    async def get_targets(self) -> List[Dict[str, Any]]:
        """获取所有目标页面"""
        result = await self.send("Target.getTargets")
        return result.get("targetInfos", [])
