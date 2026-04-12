"""
交互模块

提供点击、输入、悬停、拖拽等交互功能
"""

from typing import Optional, Dict, Any
try:
    from .cdp_client import CDPSession
except ImportError:
    from cdp_client import CDPSession


class Interactor:
    """交互管理器"""
    
    def __init__(self, session: CDPSession):
        """
        初始化交互管理器
        
        Args:
            session: CDP 会话
        """
        self.session = session
    
    async def enable(self) -> None:
        """启用 Input 和 Runtime Domain"""
        await self.session.enable_domain("Input")
        await self.session.enable_domain("Runtime")
    
    async def click(self, selector: str) -> Dict[str, Any]:
        """
        点击元素
        
        Args:
            selector: CSS 选择器
            
        Returns:
            交互结果
        """
        await self.enable()
        
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
                            x: rect.x + rect.width / 2,
                            y: rect.y + rect.height / 2
                        }};
                    }})()
                """
            }
        )
        
        point = result.get("result", {}).get("value")
        if not point:
            return {"success": False, "error": f"Element not found: {selector}"}
        
        # 模拟点击
        await self.session.send("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": point["x"],
            "y": point["y"],
            "button": "left",
            "clickCount": 1
        })
        
        await self.session.send("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": point["x"],
            "y": point["y"],
            "button": "left",
            "clickCount": 1
        })
        
        return {"success": True, "point": point}
    
    async def type(self, selector: str, text: str) -> Dict[str, Any]:
        """
        在输入框中输入文本
        
        Args:
            selector: CSS 选择器
            text: 输入文本
            
        Returns:
            交互结果
        """
        await self.enable()
        
        # 先点击元素获得焦点
        click_result = await self.click(selector)
        if not click_result.get("success"):
            return click_result
        
        # 输入文本
        for char in text:
            await self.session.send("Input.dispatchKeyEvent", {
                "type": "char",
                "text": char
            })
        
        return {"success": True, "text": text}
    
    async def hover(self, selector: str) -> Dict[str, Any]:
        """
        悬停在元素上
        
        Args:
            selector: CSS 选择器
            
        Returns:
            交互结果
        """
        await self.enable()
        
        result = await self.session.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    (function() {{
                        const el = document.querySelector('{selector}');
                        if (!el) return null;
                        const rect = el.getBoundingClientRect();
                        return {{
                            x: rect.x + rect.width / 2,
                            y: rect.y + rect.height / 2
                        }};
                    }})()
                """
            }
        )
        
        point = result.get("result", {}).get("value")
        if not point:
            return {"success": False, "error": f"Element not found: {selector}"}
        
        await self.session.send("Input.dispatchMouseEvent", {
            "type": "mouseMoved",
            "x": point["x"],
            "y": point["y"]
        })
        
        return {"success": True, "point": point}
    
    async def drag_and_drop(self, source_selector: str, target_selector: str) -> Dict[str, Any]:
        """
        拖拽元素
        
        Args:
            source_selector: 源元素选择器
            target_selector: 目标元素选择器
            
        Returns:
            交互结果
        """
        await self.enable()
        
        # 获取源元素位置
        source_result = await self.session.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    (function() {{
                        const el = document.querySelector('{source_selector}');
                        if (!el) return null;
                        const rect = el.getBoundingClientRect();
                        return {{
                            x: rect.x + rect.width / 2,
                            y: rect.y + rect.height / 2
                        }};
                    }})()
                """
            }
        )
        
        # 获取目标元素位置
        target_result = await self.session.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    (function() {{
                        const el = document.querySelector('{target_selector}');
                        if (!el) return null;
                        const rect = el.getBoundingClientRect();
                        return {{
                            x: rect.x + rect.width / 2,
                            y: rect.y + rect.height / 2
                        }};
                    }})()
                """
            }
        )
        
        source_point = source_result.get("result", {}).get("value")
        target_point = target_result.get("result", {}).get("value")
        
        if not source_point or not target_point:
            return {"success": False, "error": "Element not found"}
        
        # 按下鼠标
        await self.session.send("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": source_point["x"],
            "y": source_point["y"],
            "button": "left",
            "clickCount": 1
        })
        
        # 移动到目标位置
        await self.session.send("Input.dispatchMouseEvent", {
            "type": "mouseMoved",
            "x": target_point["x"],
            "y": target_point["y"],
            "button": "left"
        })
        
        # 释放鼠标
        await self.session.send("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": target_point["x"],
            "y": target_point["y"],
            "button": "left",
            "clickCount": 1
        })
        
        return {"success": True, "source": source_point, "target": target_point}
    
    async def press_key(self, key: str) -> Dict[str, Any]:
        """
        按下键盘按键
        
        Args:
            key: 按键名称 (Enter, Tab, Escape 等)
            
        Returns:
            交互结果
        """
        await self.enable()
        
        await self.session.send("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "key": key
        })
        
        await self.session.send("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": key
        })
        
        return {"success": True, "key": key}
