"""
MCP 工具返回结果格式化工具

提供统一的返回结果格式化、summary 生成和自动截断功能。
"""
from typing import Dict, Any, List, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


def build_summary(elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    构建元素列表的摘要信息
    
    Args:
        elements: 元素列表
    
    Returns:
        摘要字典，包含：
        - total_elements: 总数
        - by_control_type: 按控件类型分组
        - by_grid_position: 按网格位置分组
        - has_clickable: 是否有可点击元素
        - has_input: 是否有输入元素
        - top_5_names: 最常见的 5 个名称
    """
    if not elements:
        return {
            "total_elements": 0,
            "by_control_type": {},
            "by_grid_position": {},
            "has_clickable": False,
            "has_input": False,
            "top_5_names": []
        }
    
    # 统计控件类型
    control_types = Counter(elem.get('control_type', 'Unknown') for elem in elements)
    
    # 统计网格位置
    grid_positions = Counter(
        elem.get('grid_position', 'unknown') 
        for elem in elements 
        if elem.get('grid_position')
    )
    
    # 检查特殊元素类型
    has_clickable = any(
        'Button' in ctrl or 'Hyperlink' in ctrl or 'MenuItem' in ctrl
        for ctrl in control_types.keys()
    )
    
    has_input = any(
        'Edit' in ctrl or 'Text' in ctrl or 'ComboBox' in ctrl
        for ctrl in control_types.keys()
    )
    
    # 最常见的名称
    names = Counter(
        elem.get('name', '') 
        for elem in elements 
        if elem.get('name')
    )
    top_5_names = [name for name, _ in names.most_common(5)]
    
    return {
        "total_elements": len(elements),
        "by_control_type": dict(control_types),
        "by_grid_position": dict(grid_positions),
        "has_clickable": has_clickable,
        "has_input": has_input,
        "top_5_names": top_5_names
    }


def truncate_results(
    elements: List[Dict[str, Any]], 
    max_count: int = 50,
    include_truncation_info: bool = True
) -> tuple:
    """
    截断结果集并返回截断信息
    
    Args:
        elements: 元素列表
        max_count: 最大返回数量（默认 50）
        include_truncation_info: 是否包含截断信息
    
    Returns:
        (truncated_elements, truncation_info) 元组
        - truncated_elements: 截断后的列表
        - truncation_info: 截断信息字典（如果启用）
    """
    if len(elements) <= max_count:
        if include_truncation_info:
            return elements, {
                "truncated": False,
                "total_available": len(elements),
                "returned": len(elements)
            }
        return elements, None
    
    # 截断
    truncated = elements[:max_count]
    
    if include_truncation_info:
        truncation_info = {
            "truncated": True,
            "total_available": len(elements),
            "returned": max_count,
            "message": f"结果已截断：显示前 {max_count} 个，共 {len(elements)} 个元素",
            "how_to_get_all": "使用 include_raw_elements=True 或增加 max_return 参数"
        }
        return truncated, truncation_info
    
    return truncated, None


def format_tool_response(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    message: Optional[str] = None,
    elements: Optional[List[Dict[str, Any]]] = None,
    include_summary: bool = True,
    auto_truncate: bool = True,
    max_elements: int = 50
) -> Dict[str, Any]:
    """
    格式化工具响应
    
    Args:
        success: 是否成功
        data: 主要数据字典
        error: 错误消息
        message: 普通消息
        elements: 元素列表（自动添加 summary 和截断）
        include_summary: 是否包含 summary
        auto_truncate: 是否自动截断
        max_elements: 最大元素数量
    
    Returns:
        标准化的响应字典
    """
    response = {"success": success}
    
    # 处理错误
    if error:
        response["error"] = error
    
    # 处理元素列表（带 summary 和截断）
    if elements is not None:
        # 截断
        if auto_truncate and len(elements) > max_elements:
            elements, truncation_info = truncate_results(
                elements, 
                max_count=max_elements
            )
            if truncation_info:
                response["truncation"] = truncation_info
        
        # 添加 summary
        if include_summary:
            response["summary"] = build_summary(elements)
        
        response["elements"] = elements
        response["element_count"] = len(elements)
    
    # 添加主要数据
    if data:
        response.update(data)
    
    # 添加消息
    if message:
        response["message"] = message
    
    return response


def add_quick_actions(response: Dict[str, Any], actions: List[str]) -> Dict[str, Any]:
    """
    添加快速操作建议到响应中
    
    Args:
        response: 原始响应
        actions: 快速操作列表
    
    Returns:
        增强后的响应
    
    Example:
        actions = [
            "filter_ui_elements(name_contains='按钮')",
            "scan_region(region='左侧')"
        ]
    """
    if actions:
        response["quick_actions"] = actions
    return response


def create_pagination_info(
    current_page: int,
    page_size: int,
    total_items: int,
    show_page_controls: bool = True
) -> Dict[str, Any]:
    """
    创建分页信息
    
    Args:
        current_page: 当前页码（从 1 开始）
        page_size: 每页大小
        total_items: 总项数
        show_page_controls: 是否显示分页控件建议
    
    Returns:
        分页信息字典
    """
    total_pages = (total_items + page_size - 1) // page_size
    
    pagination = {
        "current_page": current_page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_previous": current_page > 1
    }
    
    if show_page_controls and total_pages > 1:
        suggestions = []
        if pagination["has_previous"]:
            suggestions.append(f"page={current_page - 1} (上一页)")
        if pagination["has_next"]:
            suggestions.append(f"page={current_page + 1} (下一页)")
        pagination["suggestions"] = suggestions
    
    return pagination
