"""
MCP 工具：自然语言元素查找
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def register_element_finder(mcp: FastMCP, scanner_ref: dict):
    """注册自然语言查找工具"""
    
    @mcp.tool()
    async def find_element_natural(
        description: str,
        layers: int = 1
    ) -> Dict[str, Any]:
        """
        使用自然语言描述查找 UI 元素
        
        从焦点位置开始，按分层顺序扫描宫格区域，查找匹配的 UI 元素。
        
        Args:
            description: 自然语言描述，如 "微信的发送按钮"、"记事本的保存菜单"
            layers: 扫描层数 (0=只焦点宫格，1=焦点 + 相邻 8 宫格，2=全部 16 宫格)
        
        Returns:
            找到的元素信息字典，包括：
            - found: bool, 是否找到
            - element: 元素信息 (name, control_type, automation_id 等)
            - grid_id: 元素所在宫格编号
            - scan_stats: 扫描统计信息
        
        Example:
            >>> find_element_natural("记事本的保存按钮")
            {
                "found": true,
                "element": {
                    "name": "保存",
                    "control_type": "Button",
                    "automation_id": "",
                    "bounding_rect": [100, 200, 150, 230],
                    "grid_id": 5
                },
                "scan_stats": {
                    "scanned_grids": 9,
                    "total_elements": 45,
                    "scan_time_ms": 234.5
                }
            }
        """
        import time
        from utils.selector_parser import natural_to_selector
        
        start_time = time.time()
        
        scanner = scanner_ref.get('scanner')
        if not scanner:
            return {
                "found": False,
                "error": "Scanner not initialized"
            }
        
        try:
            # 转换自然语言为 selector
            selector = natural_to_selector(description)
            logger.info(f"Converted '{description}' to selector: {selector}")
            
            # 扫描指定层数的宫格
            scan_results = scanner.scan_focus_area(layers=layers)
            
            # 从描述中提取关键词
            keywords = description.lower().split()
            
            # 在扫描结果中查找匹配元素
            found_element = None
            found_grid_id = None
            
            for grid_id, result in scan_results.items():
                for elem in result.elements:
                    # 简单匹配：检查名称是否包含关键词
                    match = False
                    for keyword in keywords:
                        if keyword in elem.name.lower():
                            match = True
                            break
                    
                    # 也检查控件类型
                    if '按钮' in description and 'Button' in elem.control_type:
                        match = True
                    elif '菜单' in description and 'Menu' in elem.control_type:
                        match = True
                    elif '编辑' in description and 'Edit' in elem.control_type:
                        match = True
                    
                    if match:
                        found_element = elem
                        found_grid_id = grid_id
                        break
                
                if found_element:
                    break
            
            scan_time = (time.time() - start_time) * 1000
            
            if found_element:
                return {
                    "found": True,
                    "element": {
                        "name": found_element.name,
                        "control_type": found_element.control_type,
                        "automation_id": found_element.automation_id,
                        "class_name": found_element.class_name,
                        "bounding_rect": list(found_element.bounding_rect),
                        "grid_id": found_grid_id
                    },
                    "selector_used": selector,
                    "scan_stats": {
                        "scanned_grids": len(scan_results),
                        "total_elements": sum(
                            len(r.elements) for r in scan_results.values()
                        ),
                        "scan_time_ms": round(scan_time, 2)
                    }
                }
            else:
                return {
                    "found": False,
                    "description": description,
                    "selector_used": selector,
                    "scan_stats": {
                        "scanned_grids": len(scan_results),
                        "total_elements": sum(
                            len(r.elements) for r in scan_results.values()
                        ),
                        "scan_time_ms": round(scan_time, 2)
                    },
                    "message": f"未找到匹配的元素：{description}"
                }
        
        except Exception as e:
            logger.error(f"Error in find_element_natural: {e}")
            return {
                "found": False,
                "error": str(e)
            }
    
    return find_element_natural
