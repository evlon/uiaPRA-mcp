"""
UI 元素语义化过滤器
允许 LLM 根据自然语言描述灵活筛选和排序 UI 元素
"""
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class SemanticQuery:
    """语义化查询条件"""
    # 网格位置过滤
    grid_positions: Optional[List[str]] = None  # ['左上', '左中', '左下']
    grid_ids: Optional[List[int]] = None  # [0, 3, 6]
    
    # 名称匹配（支持正则）
    name_contains: Optional[str] = None  # 包含"搜"
    name_regex: Optional[str] = None  # 正则表达式
    
    # 控件类型过滤
    control_types: Optional[List[str]] = None  # ['ButtonControl', 'TextControl']
    
    # 尺寸过滤
    min_width: int = 0
    min_height: int = 0
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    
    # 优先级排序
    priority_field: str = 'name'  # 按哪个字段排序
    priority_order: str = 'desc'  # 'asc' or 'desc'
    
    # 自定义过滤函数（高级用法）
    custom_filter: Optional[Callable] = None


class SemanticFilter:
    """语义化过滤器"""
    
    def __init__(self, ui_elements: List[Any]):
        """
        Args:
            ui_elements: UIElement 对象列表（来自 UITreeScanner）
        """
        self.ui_elements = ui_elements
        self.filtered_results: List[Any] = []
    
    def apply_query(self, query: SemanticQuery) -> List[Any]:
        """
        应用语义化查询
        
        Args:
            query: 语义化查询条件
        
        Returns:
            过滤后的元素列表
        """
        results = self.ui_elements.copy()
        
        # 1. 网格位置过滤
        if query.grid_positions or query.grid_ids:
            results = self._filter_by_grid(results, query)
        
        # 2. 名称过滤
        if query.name_contains or query.name_regex:
            results = self._filter_by_name(results, query)
        
        # 3. 控件类型过滤
        if query.control_types:
            results = self._filter_by_control_type(results, query)
        
        # 4. 尺寸过滤
        results = self._filter_by_size(results, query)
        
        # 5. 自定义过滤
        if query.custom_filter:
            results = [elem for elem in results if query.custom_filter(elem)]
        
        # 6. 排序
        results = self._sort_results(results, query)
        
        self.filtered_results = results
        return results
    
    def _filter_by_grid(self, elements: List[Any], query: SemanticQuery) -> List[Any]:
        """按网格位置过滤"""
        filtered = []
        
        target_grid_ids = set()
        
        if query.grid_ids:
            target_grid_ids.update(query.grid_ids)
        
        if query.grid_positions:
            from core.grid_manager import GridManager
            # 动态导入避免循环引用
            position_to_id = {
                '左上': 0, '上中': 1, '右上': 2,
                '左中': 3, '中间': 4, '右中': 5,
                '左下': 6, '下中': 7, '右下': 8,
                '中心': 4, '中央': 4, '正中': 4,
            }
            for pos_name in query.grid_positions:
                grid_id = position_to_id.get(pos_name)
                if grid_id is not None:
                    target_grid_ids.add(grid_id)
        
        for elem in elements:
            if elem.grid_id in target_grid_ids:
                filtered.append(elem)
        
        return filtered
    
    def _filter_by_name(self, elements: List[Any], query: SemanticQuery) -> List[Any]:
        """按名称过滤"""
        filtered = []
        
        for elem in elements:
            name = elem.name or ''
            
            # 包含匹配
            if query.name_contains and query.name_contains in name:
                filtered.append(elem)
                continue
            
            # 正则匹配
            if query.name_regex:
                try:
                    if re.search(query.name_regex, name):
                        filtered.append(elem)
                        continue
                except re.error:
                    logger.warning(f"Invalid regex: {query.name_regex}")
        
        return filtered
    
    def _filter_by_control_type(self, elements: List[Any], query: SemanticQuery) -> List[Any]:
        """按控件类型过滤"""
        return [
            elem for elem in elements
            if elem.control_type in query.control_types
        ]
    
    def _filter_by_size(self, elements: List[Any], query: SemanticQuery) -> List[Any]:
        """按尺寸过滤"""
        filtered = []
        
        for elem in elements:
            left, top, right, bottom = elem.bounding_rect
            width = right - left
            height = bottom - top
            
            # 检查最小尺寸
            if width < query.min_width or height < query.min_height:
                continue
            
            # 检查最大尺寸
            if query.max_width and width > query.max_width:
                continue
            if query.max_height and height > query.max_height:
                continue
            
            filtered.append(elem)
        
        return filtered
    
    def _sort_results(self, elements: List[Any], query: SemanticQuery) -> List[Any]:
        """排序结果"""
        
        def get_sort_key(elem):
            if query.priority_field == 'name':
                # 按名称长度排序（通常更短的更精确）
                return len(elem.name or '')
            elif query.priority_field == 'grid_id':
                return elem.grid_id or 999
            elif query.priority_field == 'size':
                # 按面积排序
                left, top, right, bottom = elem.bounding_rect
                return (right - left) * (bottom - top)
            else:
                return 0
        
        reverse = (query.priority_order == 'desc')
        return sorted(elements, key=get_sort_key, reverse=reverse)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_elements': len(self.ui_elements),
            'filtered_elements': len(self.filtered_results),
            'by_grid': self._count_by_grid(),
            'by_control_type': self._count_by_control_type(),
        }
    
    def _count_by_grid(self) -> Dict[str, int]:
        """按网格统计"""
        counts = {}
        for elem in self.filtered_results:
            pos_name = elem.grid_position or 'unknown'
            counts[pos_name] = counts.get(pos_name, 0) + 1
        return counts
    
    def _count_by_control_type(self) -> Dict[str, int]:
        """按控件类型统计"""
        counts = {}
        for elem in self.filtered_results:
            ctrl_type = elem.control_type
            counts[ctrl_type] = counts.get(ctrl_type, 0) + 1
        return counts


class SelectorBuilder:
    """Selector 构造助手"""
    
    @staticmethod
    def from_element(element: Any) -> str:
        """
        从 UIElement 构建 selector 字符串
        
        Args:
            element: UIElement 对象
        
        Returns:
            tdSelector 格式的字符串
        """
        conditions = []
        
        # 优先使用 automation_id
        if element.automation_id:
            conditions.append(f"('AutomationId', '{element.automation_id}')")
        
        # 使用名称
        if element.name:
            conditions.append(f"('Name', '{element.name}')")
        
        # 使用控件类型
        if element.control_type:
            conditions.append(f"('ControlType', '{element.control_type}')")
        
        # 使用 class_name
        if element.class_name:
            conditions.append(f"('ClassName', '{element.class_name}')")
        
        # 构建 selector
        selector_dict = {
            'ctrl': [eval(cond) for cond in conditions]
        }
        
        return str(selector_dict)
    
    @staticmethod
    def from_semantic_match(element: Any, window_title: str = '') -> str:
        """
        从语义匹配结果构建完整的 selector（包含窗口路径）
        
        Args:
            element: UIElement 对象
            window_title: 窗口标题
        
        Returns:
            完整的 tdSelector 字符串
        """
        # 窗口部分
        window_part = f"[{{ 'wnd': [('Text', '{window_title}')] }}" if window_title else "[{ 'wnd': [] }}"
        
        # 控件部分
        ctrl_conditions = []
        
        if element.automation_id:
            ctrl_conditions.append(f"('AutomationId', '{element.automation_id}')")
        
        if element.name:
            ctrl_conditions.append(f"('Name', '{element.name}')")
        
        if element.control_type:
            ctrl_conditions.append(f"('ControlType', '{element.control_type}')")
        
        ctrl_part = "{ 'ctrl': [" + ", ".join(ctrl_conditions) + "] }"
        
        return window_part + ", " + ctrl_part + "]"
    
    @staticmethod
    def build_custom(conditions: Dict[str, Any]) -> str:
        """
        自定义构建 selector
        
        Args:
            conditions: 条件字典
                {
                    'name': '搜一搜',
                    'control_type': 'ButtonControl',
                    'automation_id': '',
                }
        
        Returns:
            tdSelector 字符串
        """
        ctrl_conditions = []
        
        if conditions.get('name'):
            ctrl_conditions.append(f"('Name', '{conditions['name']}')")
        
        if conditions.get('control_type'):
            ctrl_conditions.append(f"('ControlType', '{conditions['control_type']}')")
        
        if conditions.get('automation_id'):
            ctrl_conditions.append(f"('AutomationId', '{conditions['automation_id']}')")
        
        if conditions.get('class_name'):
            ctrl_conditions.append(f"('ClassName', '{conditions['class_name']}')")
        
        return "{ 'ctrl': [" + ", ".join(ctrl_conditions) + "] }"


def create_semantic_filter_from_natural_language(
    description: str,
    ui_elements: List[Any]
) -> SemanticFilter:
    """
    从自然语言描述创建语义过滤器
    
    Args:
        description: 自然语言描述，如 "微信左边的搜一搜按钮"
        ui_elements: UIElement 列表
    
    Returns:
        已应用过滤的 SemanticFilter 实例
    
    Example:
        >>> filter = create_semantic_filter_from_natural_language(
        ...     "微信左边的搜一搜按钮",
        ...     ui_elements
        ... )
        >>> results = filter.filtered_results
    """
    # 解析自然语言
    query = SemanticQuery()
    
    # 检测方位词
    position_keywords = {
        '左边': ['左中', '左上', '左下'],
        '左侧': ['左中', '左上', '左下'],
        '右边': ['右中', '右上', '右下'],
        '右侧': ['右中', '右上', '右下'],
        '上面': ['左上', '上中', '右上'],
        '顶部': ['左上', '上中', '右上'],
        '下面': ['左下', '下中', '右下'],
        '底部': ['左下', '下中', '右下'],
        '中间': ['中间'],
        '中心': ['中间'],
        '左上': ['左上'],
        '右上': ['右上'],
        '左下': ['左下'],
        '右下': ['右下'],
    }
    
    for keyword, positions in position_keywords.items():
        if keyword in description:
            query.grid_positions = positions
            break
    
    # 检测控件类型
    control_keywords = {
        '按钮': ['ButtonControl'],
        '按钮': ['ButtonControl'],
        '文本': ['TextControl'],
        '输入框': ['EditControl'],
        '图片': ['ImageControl'],
    }
    
    for keyword, ctrl_types in control_keywords.items():
        if keyword in description:
            query.control_types = ctrl_types
            break
    
    # 提取名称关键词（简单实现：提取引号或特定模式）
    # 例如："搜一搜" 按钮 -> name_contains = "搜一搜"
    import re
    name_matches = re.findall(r'"([^"]+)"', description)
    if name_matches:
        query.name_contains = name_matches[0]
    else:
        # 尝试提取中文名称（简化版）
        # 匹配 "xxx 按钮" 中的 xxx
        match = re.search(r'(.+?) 按钮', description)
        if match:
            query.name_contains = match.group(1)
    
    # 创建过滤器并应用查询
    semantic_filter = SemanticFilter(ui_elements)
    semantic_filter.apply_query(query)
    
    return semantic_filter


# 便捷函数
def quick_filter(
    ui_elements: List[Any],
    grid_positions: Optional[List[str]] = None,
    name_contains: Optional[str] = None,
    control_types: Optional[List[str]] = None,
    sort_by: str = 'name'
) -> List[Any]:
    """
    快速过滤 UI 元素
    
    Args:
        ui_elements: UIElement 列表
        grid_positions: 网格位置列表，如 ['左中', '左上']
        name_contains: 名称包含的字符串
        control_types: 控件类型列表
        sort_by: 排序字段
    
    Returns:
        过滤后的元素列表
    
    Example:
        >>> results = quick_filter(
        ...     ui_elements,
        ...     grid_positions=['左中', '左上'],
        ...     name_contains='搜',
        ...     control_types=['ButtonControl']
        ... )
    """
    query = SemanticQuery(
        grid_positions=grid_positions,
        name_contains=name_contains,
        control_types=control_types,
        priority_field=sort_by
    )
    
    semantic_filter = SemanticFilter(ui_elements)
    return semantic_filter.apply_query(query)
