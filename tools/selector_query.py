"""
MCP 工具：Selector 语法查询
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def register_selector_query(mcp: FastMCP, scanner_ref: dict):
    """注册 selector 语法查询工具"""
    
    @mcp.tool()
    async def find_element_selector(
        selector_string: str,
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        使用 tdSelector 语法查找 UI 元素
        
        使用 tdRPA 的 selector 语法精确查找元素，支持完整的查询条件。
        
        Args:
            selector_string: tdSelector 语法字符串
                格式示例："[{'wnd': [('Text', '窗口'), ('App', 'notepad.exe')]}, {'ctrl': [('Text', '按钮')]}]"
            timeout: 超时秒数，默认 5 秒
        
        Returns:
            找到的元素信息字典：
            - found: bool
            - element: 元素详细信息
            - selector: 使用的 selector
        
        Example:
            >>> find_element_selector(
            ...     "[{'wnd': [('Text', '无标题 - 记事本'), ('App', 'notepad.exe')]}]"
            ... )
            {
                "found": true,
                "element": {
                    "name": "无标题 - 记事本",
                    "control_type": "Window",
                    "automation_id": "",
                    "class_name": "Notepad",
                    "bounding_rect": [100, 100, 500, 400]
                },
                "selector": "[...]"
            }
        """
        scanner = scanner_ref.get('scanner')
        if not scanner:
            return {
                "found": False,
                "error": "Scanner not initialized"
            }
        
        try:
            # 使用 scanner 查找元素
            element = scanner.find_by_selector(selector_string, timeout=timeout)
            
            if element:
                try:
                    rect = element.BoundingRectangle
                    bounding_rect = [rect.left, rect.top, rect.right, rect.bottom]
                except:
                    bounding_rect = [0, 0, 0, 0]
                
                return {
                    "found": True,
                    "element": {
                        "name": element.Name if hasattr(element, 'Name') else '',
                        "control_type": element.ControlTypeName if hasattr(element, 'ControlTypeName') else '',
                        "automation_id": element.AutomationId if hasattr(element, 'AutomationId') else '',
                        "class_name": element.ClassName if hasattr(element, 'ClassName') else '',
                        "bounding_rect": bounding_rect
                    },
                    "selector": selector_string
                }
            else:
                return {
                    "found": False,
                    "selector": selector_string,
                    "timeout": timeout,
                    "message": f"未找到元素 (timeout={timeout}s)"
                }
        
        except Exception as e:
            logger.error(f"Error in find_element_selector: {e}")
            return {
                "found": False,
                "error": str(e),
                "selector": selector_string
            }
    
    @mcp.tool()
    async def scan_grid_region(
        grid_id: int,
        search_depth: int = 2
    ) -> Dict[str, Any]:
        """
        扫描指定宫格区域的所有 UI 元素
        
        Args:
            grid_id: 宫格编号 (0-15)
                布局:
                0  1  2  3
                4  5  6  7
                8  9  10 11
                12 13 14 15
            search_depth: 搜索深度，默认 2
        
        Returns:
            宫格内所有元素的列表和统计信息
        """
        scanner = scanner_ref.get('scanner')
        grid_manager = scanner_ref.get('grid_manager')
        
        if not scanner or not grid_manager:
            return {
                "error": "Scanner not initialized"
            }
        
        try:
            # 获取宫格矩形
            grid = grid_manager.get_grid_by_id(grid_id)
            grid_rect = grid.to_tuple()
            
            # 扫描宫格
            elements = scanner.scan_grid(grid_rect, search_depth=search_depth)
            
            # 转换为可序列化格式
            element_list = []
            for elem in elements:
                element_list.append(elem.to_dict())
            
            return {
                "grid_id": grid_id,
                "grid_rect": list(grid_rect),
                "element_count": len(element_list),
                "search_depth": search_depth,
                "elements": element_list
            }
        
        except Exception as e:
            logger.error(f"Error scanning grid {grid_id}: {e}")
            return {
                "error": str(e),
                "grid_id": grid_id
            }
    
    return find_element_selector, scan_grid_region
