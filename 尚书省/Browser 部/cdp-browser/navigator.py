"""
导航模块

提供页面导航、等待策略、历史记录等功能
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
try:
    from .cdp_client import CDPSession
except ImportError:
    from cdp_client import CDPSession


class Navigator:
    """导航管理器"""
    
    def __init__(self, session: CDPSession):
        """
        初始化导航管理器
        
        Args:
            session: CDP 会话
        """
        self.session = session
        self.history: List[Dict[str, Any]] = []
    
    async def enable(self) -> None:
        """启用 Page Domain"""
        await self.session.enable_domain("Page")
    
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
        await self.enable()
        
        start_time = datetime.now()
        
        # 导航
        result = await self.session.send("Page.navigate", {"url": url})
        
        # 等待加载完成
        if wait_strategy == "networkidle":
            await self.wait_for_network_idle(timeout)
        elif wait_strategy == "domcontentloaded":
            await self.session.send("Page.setLifecycleEventsEnabled", {"enabled": True})
        
        end_time = datetime.now()
        load_time = (end_time - start_time).total_seconds()
        
        # 记录历史
        self.history.append({
            "url": url,
            "wait_strategy": wait_strategy,
            "timeout": timeout,
            "load_time": load_time,
            "timestamp": start_time.isoformat(),
            "success": result.get("errorText") is None
        })
        
        return result
    
    async def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """
        等待网络空闲
        
        Args:
            timeout: 超时时间 (ms)
        """
        await self.session.enable_domain("Network")
        
        # 等待网络空闲（简化实现）
        await asyncio.sleep(min(timeout / 1000, 5))
    
    async def wait_for_selector(self, selector: str, timeout: int = 5000) -> bool:
        """
        等待元素出现
        
        Args:
            selector: CSS 选择器
            timeout: 超时时间 (ms)
            
        Returns:
            元素是否出现
        """
        import asyncio
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() * 1000 < timeout:
            result = await self.session.send(
                "Runtime.evaluate",
                {
                    "expression": f"document.querySelector('{selector}') !== null"
                }
            )
            
            if result.get("result", {}).get("value", False):
                return True
            
            await asyncio.sleep(0.1)
        
        return False
    
    async def go_back(self) -> Dict[str, Any]:
        """
        返回上一页
        
        Returns:
            导航结果
        """
        return await self.session.send("Page.goBack")
    
    async def go_forward(self) -> Dict[str, Any]:
        """
        前进到下一页
        
        Returns:
            导航结果
        """
        return await self.session.send("Page.goForward")
    
    async def reload(self, ignore_cache: bool = False) -> Dict[str, Any]:
        """
        重新加载页面
        
        Args:
            ignore_cache: 是否忽略缓存
            
        Returns:
            导航结果
        """
        return await self.session.send("Page.reload", {"ignoreCache": ignore_cache})
    
    async def get_current_url(self) -> str:
        """
        获取当前 URL
        
        Returns:
            当前 URL
        """
        result = await self.session.send("Page.getFrameTree")
        return result.get("frameTree", {}).get("frame", {}).get("url", "")
    
    async def get_history(self) -> List[Dict[str, Any]]:
        """
        获取导航历史
        
        Returns:
            导航历史列表
        """
        return self.history.copy()
    
    async def clear_history(self) -> None:
        """清除导航历史"""
        self.history.clear()
