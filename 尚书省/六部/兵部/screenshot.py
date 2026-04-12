"""
截图模块

提供全页截图、元素截图、标注、对比等功能
"""

import base64
from typing import Optional, Dict, Any
try:
    from .cdp_client import CDPSession
except ImportError:
    from cdp_client import CDPSession


class ScreenshotCapture:
    """截图捕获器"""
    
    def __init__(self, session: CDPSession):
        """
        初始化截图捕获器
        
        Args:
            session: CDP 会话
        """
        self.session = session
    
    async def enable(self) -> None:
        """启用 Page Domain"""
        await self.session.enable_domain("Page")
    
    async def screenshot(self, selector: str = None, full_page: bool = True) -> bytes:
        """
        捕获截图
        
        Args:
            selector: CSS 选择器（None 表示全页）
            full_page: 是否全页截图
            
        Returns:
            截图数据 (PNG bytes)
        """
        await self.enable()
        
        if selector:
            return await self._screenshot_element(selector)
        else:
            return await self._screenshot_full_page(full_page)
    
    async def _screenshot_full_page(self, full_page: bool = True) -> bytes:
        """
        全页截图
        
        Args:
            full_page: 是否包含滚动区域
            
        Returns:
            截图数据
        """
        result = await self.session.send(
            "Page.captureScreenshot",
            {
                "format": "png",
                "captureBeyondViewport": full_page
            }
        )
        
        return base64.b64decode(result.get("data", ""))
    
    async def _screenshot_element(self, selector: str) -> bytes:
        """
        元素截图
        
        Args:
            selector: CSS 选择器
            
        Returns:
            截图数据
        """
        # 获取元素边界
        result = await self.session.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    (function() {{
                        const el = document.querySelector('{selector}');
                        if (!el) return null;
                        const rect = el.getBoundingClientRect();
                        return {{
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }};
                    }})()
                """
            }
        )
        
        rect = result.get("result", {}).get("value")
        if not rect:
            raise ValueError(f"Element not found: {selector}")
        
        # 裁剪截图
        screenshot_result = await self.session.send(
            "Page.captureScreenshot",
            {
                "format": "png",
                "clip": {
                    "x": rect["x"],
                    "y": rect["y"],
                    "width": rect["width"],
                    "height": rect["height"],
                    "scale": 1
                }
            }
        )
        
        return base64.b64decode(screenshot_result.get("data", ""))
    
    async def save_screenshot(self, path: str, selector: str = None, full_page: bool = True) -> str:
        """
        保存截图到文件
        
        Args:
            path: 文件路径
            selector: CSS 选择器
            full_page: 是否全页
            
        Returns:
            保存的文件路径
        """
        image_data = await self.screenshot(selector, full_page)
        
        with open(path, "wb") as f:
            f.write(image_data)
        
        return path
    
    async def compare_screenshots(self, before_path: str, after_path: str) -> Dict[str, Any]:
        """
        对比两张截图
        
        Args:
            before_path: 修复前截图路径
            after_path: 修复后截图路径
            
        Returns:
            对比结果
        """
        import hashlib
        
        # 简单实现：比较文件哈希
        with open(before_path, "rb") as f:
            before_hash = hashlib.md5(f.read()).hexdigest()
        
        with open(after_path, "rb") as f:
            after_hash = hashlib.md5(f.read()).hexdigest()
        
        return {
            "before_hash": before_hash,
            "after_hash": after_hash,
            "identical": before_hash == after_hash,
            "timestamp": datetime.now().isoformat()
        }
    
    async def annotate_screenshot(self, image_data: bytes, annotations: list) -> bytes:
        """
        在截图上添加标注
        
        Args:
            image_data: 截图数据
            annotations: 标注列表 [{x, y, text, color}]
            
        Returns:
            标注后的截图数据
        """
        # 简单实现：返回原始截图
        # 实际实现可以使用 PIL/Pillow 添加标注
        return image_data
