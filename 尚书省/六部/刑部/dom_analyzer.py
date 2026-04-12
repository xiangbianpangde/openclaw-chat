"""
DOM 分析器

提供 DOM 快照捕获、元素定位、结构分析等功能
"""

from typing import Optional, Dict, Any, List
try:
    from .cdp_client import CDPSession
except ImportError:
    from cdp_client import CDPSession


class DOMAnalyzer:
    """DOM 分析器"""
    
    def __init__(self, session: CDPSession):
        """
        初始化 DOM 分析器
        
        Args:
            session: CDP 会话
        """
        self.session = session
    
    async def enable(self) -> None:
        """启用 DOM 相关 Domain"""
        await self.session.enable_domain("DOM")
        await self.session.enable_domain("DOMSnapshot")
        await self.session.enable_domain("Runtime")
    
    async def snapshot(self) -> Dict[str, Any]:
        """
        捕获 DOM 快照
        
        Returns:
            DOM 快照数据
        """
        result = await self.session.send(
            "DOMSnapshot.captureSnapshot",
            {
                "computedStyles": [],
                "includeDOMRects": True,
                "includePaintOrder": True
            }
        )
        return result
    
    async def get_document(self) -> Dict[str, Any]:
        """
        获取根文档节点
        
        Returns:
            文档节点信息
        """
        result = await self.session.send("DOM.getDocument", {"depth": -1})
        return result.get("root", {})
    
    async def query_selector(self, selector: str) -> Optional[Dict[str, Any]]:
        """
        查询选择器匹配的元素
        
        Args:
            selector: CSS 选择器
            
        Returns:
            元素节点信息，未找到返回 None
        """
        doc = await self.get_document()
        node_id = doc.get("nodeId")
        
        if not node_id:
            return None
        
        result = await self.session.send(
            "DOM.querySelector",
            {"nodeId": node_id, "selector": selector}
        )
        
        node_id = result.get("nodeId")
        if node_id == 0:
            return None
        
        return await self.get_node_info(node_id)
    
    async def get_node_info(self, node_id: int) -> Dict[str, Any]:
        """
        获取节点详细信息
        
        Args:
            node_id: 节点 ID
            
        Returns:
            节点信息
        """
        result = await self.session.send(
            "DOM.resolveNode",
            {"nodeId": node_id}
        )
        
        object_id = result.get("object", {}).get("objectId")
        if not object_id:
            return {}
        
        props_result = await self.session.send(
            "Runtime.getProperties",
            {
                "objectId": object_id,
                "ownProperties": True
            }
        )
        
        return {
            "nodeId": node_id,
            "objectId": object_id,
            "properties": props_result.get("result", [])
        }
    
    async def check_visibility(self, selector: str) -> bool:
        """
        检查元素可见性
        
        Args:
            selector: CSS 选择器
            
        Returns:
            元素是否可见
        """
        result = await self.session.send(
            "Runtime.evaluate",
            {
                "expression": f"""
                    (function() {{
                        const el = document.querySelector('{selector}');
                        if (!el) return {{ found: false }};
                        
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        
                        return {{
                            found: true,
                            visible: style.display !== 'none' && 
                                     style.visibility !== 'hidden' &&
                                     style.opacity !== '0' &&
                                     rect.width > 0 &&
                                     rect.height > 0
                        }};
                    }})()
                """
            }
        )
        
        value = result.get("result", {}).get("value", {})
        return value.get("visible", False)
    
    async def get_interactive_elements(self) -> List[Dict[str, Any]]:
        """
        获取所有可交互元素
        
        Returns:
            可交互元素列表
        """
        result = await self.session.send(
            "Runtime.evaluate",
            {
                "expression": """
                    (function() {
                        const selectors = [
                            'a', 'button', 'input', 'select', 'textarea',
                            '[onclick]', '[role="button"]', '[tabindex]'
                        ];
                        
                        const elements = [];
                        selectors.forEach(selector => {
                            document.querySelectorAll(selector).forEach(el => {
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    elements.push({
                                        tagName: el.tagName,
                                        id: el.id || null,
                                        className: el.className || null,
                                        text: el.textContent?.slice(0, 100) || null,
                                        rect: {
                                            x: rect.x,
                                            y: rect.y,
                                            width: rect.width,
                                            height: rect.height
                                        }
                                    });
                                }
                            });
                        });
                        
                        return elements;
                    })()
                """
            }
        )
        
        return result.get("result", {}).get("value", [])
    
    async def compare_snapshots(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """
        对比两个 DOM 快照
        
        Args:
            before: 修复前快照
            after: 修复后快照
            
        Returns:
            差异数据
        """
        # 简单实现：比较节点数量
        before_nodes = before.get("documents", [{}])[0].get("nodeCount", 0)
        after_nodes = after.get("documents", [{}])[0].get("nodeCount", 0)
        
        return {
            "before_nodes": before_nodes,
            "after_nodes": after_nodes,
            "node_diff": after_nodes - before_nodes,
            "timestamp": datetime.now().isoformat()
        }
