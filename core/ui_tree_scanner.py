"""
UI 树扫描器
获取完整的 UI 树，并按 9 宫格位置排序和去重
添加严格的可见性过滤策略
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class UIElement:
    """UI 元素信息"""
    name: str
    control_type: str
    automation_id: str
    class_name: str
    bounding_rect: Tuple[int, int, int, int]
    grid_id: Optional[int] = None  # 所属宫格 ID
    grid_position: Optional[str] = None  # 宫格位置名称（如"左上"）
    center_point: Optional[Tuple[int, int]] = None  # 中心点坐标
    element_ref: Any = field(default=None, repr=False)  # 原始元素引用
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'name': self.name,
            'control_type': self.control_type,
            'automation_id': self.automation_id,
            'class_name': self.class_name,
            'bounding_rect': list(self.bounding_rect),
            'grid_id': self.grid_id,
            'grid_position': self.grid_position,
            'center_point': list(self.center_point) if self.center_point else None,
        }


class UITreeScanner:
    """UI 树扫描器"""
    
    def __init__(self, root_element, grid_manager, enable_visibility_filter: bool = True, visibility_mode: str = "balanced"):
        """
        Args:
            root_element: UIA 根元素
            grid_manager: 宫格管理器（9 宫格）
            enable_visibility_filter: 是否启用可见性过滤（默认 True）
            visibility_mode: 可见性过滤模式
                - "off": 不过滤
                - "balanced": 平衡模式（默认，只检查基本可见性和离屏）
                - "strict": 严格模式（4 层检查全开）
        """
        self.root_element = root_element
        self.grid_manager = grid_manager
        self.all_elements: List[UIElement] = []
        self.enable_visibility_filter = enable_visibility_filter
        self.visibility_mode = visibility_mode if enable_visibility_filter else "off"
        
        # 初始化可见性检测器
        if self.enable_visibility_filter:
            try:
                from core.visibility_checker import VisibilityChecker
                self.visibility_checker = VisibilityChecker(mode=self.visibility_mode)
                logger.info(f"Visibility filter enabled (mode={self.visibility_mode})")
            except Exception as e:
                logger.warning(f"Failed to initialize visibility checker: {e}")
                self.enable_visibility_filter = False
                self.visibility_mode = "off"
    
    def scan_full_tree(self, max_depth: int = 15) -> List[UIElement]:
        """
        扫描完整的 UI 树（带可见性过滤）
        
        Args:
            max_depth: 最大搜索深度
        
        Returns:
            所有可见 UI 元素的列表
        """
        self.all_elements = []
        
        # 重置过滤统计
        if self.enable_visibility_filter and hasattr(self, 'visibility_checker'):
            self.visibility_checker.reset_statistics()
        
        def traverse(element, depth=0):
            if depth > max_depth:
                return
            
            try:
                # 提取元素信息
                ui_elem = self._extract_element_info(element)
                
                if ui_elem:
                    # 可见性检查（如果启用）
                    if self.enable_visibility_filter:
                        if hasattr(self, 'visibility_checker'):
                            is_visible = self.visibility_checker.is_element_visible(element)
                            if not is_visible:
                                logger.debug(f"Filtered out invisible element: {ui_elem.name or 'Unknown'}")
                                # 继续遍历子元素，因为父元素可能被遮挡但子元素可能可见
                                children = element.GetChildren()
                                for child in children:
                                    traverse(child, depth + 1)
                                return
                    
                    # 计算所属宫格
                    self._assign_to_grid(ui_elem)
                    self.all_elements.append(ui_elem)
                
                # 遍历子元素
                children = element.GetChildren()
                for child in children:
                    traverse(child, depth + 1)
                    
            except Exception as e:
                logger.debug(f"Error traversing element at depth {depth}: {e}")
        
        traverse(self.root_element)
        
        if self.enable_visibility_filter:
            stats = self.get_visibility_filter_stats()
            logger.info(f"Scanned {len(self.all_elements)} visible elements from UI tree (mode={self.visibility_mode}, filtered={stats['filtered_out']})")
        else:
            logger.info(f"Scanned {len(self.all_elements)} elements from UI tree (visibility filter disabled)")
        
        return self.all_elements
    
    def get_visibility_filter_stats(self) -> Dict[str, Any]:
        """
        获取可见性过滤统计信息
        
        Returns:
            统计数据字典
        """
        if self.enable_visibility_filter and hasattr(self, 'visibility_checker'):
            stats = self.visibility_checker.get_filter_statistics()
            total_checked = stats.get('total_checked', 0)
            passed = stats.get('passed_visibility', 0)
            return {
                "mode": stats["mode"],
                "total_checked": total_checked,
                "passed_visibility": passed,
                "filtered_out": total_checked - passed,
                "details": stats
            }
        return {
            "mode": "off",
            "total_checked": 0,
            "passed_visibility": 0,
            "filtered_out": 0,
            "details": {}
        }
    
    def _extract_element_info(self, element) -> Optional[UIElement]:
        """提取元素信息"""
        try:
            # 获取基本信息
            name = getattr(element, 'Name', '') or ''
            control_type = getattr(element, 'ControlTypeName', '') or ''
            automation_id = getattr(element, 'AutomationId', '') or ''
            class_name = getattr(element, 'ClassName', '') or ''
            
            # 获取位置信息
            try:
                rect = element.BoundingRectangle
                bounding_rect = (rect.left, rect.top, rect.right, rect.bottom)
                
                # 计算中心点
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                center_point = (center_x, center_y)
                
            except:
                # 无法获取矩形的元素跳过
                return None
            
            # 过滤掉无效元素
            # 保留条件：有实际尺寸的元素
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            
            if width <= 0 or height <= 0:
                return None
            
            # 创建 UIElement
            ui_elem = UIElement(
                name=name,
                control_type=control_type,
                automation_id=automation_id,
                class_name=class_name,
                bounding_rect=bounding_rect,
                center_point=center_point,
                element_ref=element
            )
            
            return ui_elem
            
        except Exception as e:
            logger.debug(f"Error extracting element info: {e}")
            return None
    
    def _assign_to_grid(self, ui_elem: UIElement):
        """将元素分配到对应的宫格"""
        if not ui_elem.center_point:
            return
        
        try:
            x, y = ui_elem.center_point
            grid = self.grid_manager.get_grid_by_position(x, y)
            
            ui_elem.grid_id = grid.id
            ui_elem.grid_position = self.grid_manager.get_position_name_by_id(grid.id)
            
        except Exception as e:
            # 元素在窗口外部
            logger.debug(f"Element outside window: {ui_elem.name}")
            ui_elem.grid_id = None
            ui_elem.grid_position = None
    
    def get_elements_by_grid(self) -> Dict[int, List[UIElement]]:
        """
        按宫格分组返回元素
        
        Returns:
            {grid_id: [elements]}
        """
        result = {}
        
        for elem in self.all_elements:
            if elem.grid_id is not None:
                if elem.grid_id not in result:
                    result[elem.grid_id] = []
                result[elem.grid_id].append(elem)
        
        return result
    
    def get_sorted_elements(self, deduplicate: bool = False) -> List[UIElement]:
        """
        获取排序后的元素列表
        
        Args:
            deduplicate: 是否去重（移除完全重叠的元素），默认 False（让 LLM 决定）
        
        Returns:
            排序后的元素列表
        """
        # 按宫格排序
        sorted_elems = sorted(
            self.all_elements,
            key=lambda e: (e.grid_id or 999, e.center_point[1] if e.center_point else 0, e.center_point[0] if e.center_point else 0)
        )
        
        if not deduplicate:
            return sorted_elems
        
        # 去重：移除完全重叠的元素
        return self._deduplicate_elements(sorted_elems)
    
    def get_grouped_ui_tree(self) -> Dict[str, Any]:
        """
        获取分组后的 UI 树数据（不做任何过滤）
        
        Returns:
            完整的分组数据，包括：
            - by_grid: 按网格分组的元素
            - by_control_type: 按控件类型分组的元素
            - all_elements: 所有元素（带完整信息）
            - statistics: 统计信息
        
        Example:
            >>> ui_data = scanner.get_grouped_ui_tree()
            >>> ui_data['by_grid']['左中']  # 获取左边中间的所有元素
            >>> ui_data['statistics']['total_elements']  # 总元素数
        """
        result = {
            'by_grid': {},
            'by_control_type': {},
            'all_elements': [],
            'statistics': {
                'total_elements': len(self.all_elements),
                'elements_with_grid': sum(1 for e in self.all_elements if e.grid_id is not None),
                'by_grid_position': {},
                'by_control_type': {},
            }
        }
        
        # 按网格分组
        grid_groups = {}
        for elem in self.all_elements:
            pos_name = elem.grid_position or 'unknown'
            if pos_name not in grid_groups:
                grid_groups[pos_name] = []
            grid_groups[pos_name].append(elem)
            
            # 统计
            result['statistics']['by_grid_position'][pos_name] = \
                result['statistics']['by_grid_position'].get(pos_name, 0) + 1
        
        result['by_grid'] = {
            pos: [e.to_dict() for e in elems]
            for pos, elems in grid_groups.items()
        }
        
        # 按控件类型分组
        ctrl_groups = {}
        for elem in self.all_elements:
            ctrl_type = elem.control_type or 'Unknown'
            if ctrl_type not in ctrl_groups:
                ctrl_groups[ctrl_type] = []
            ctrl_groups[ctrl_type].append(elem)
            
            # 统计
            result['statistics']['by_control_type'][ctrl_type] = \
                result['statistics']['by_control_type'].get(ctrl_type, 0) + 1
        
        result['by_control_type'] = {
            ctrl_type: len(elems)
            for ctrl_type, elems in ctrl_groups.items()
        }
        
        # 所有元素（转换为字典）
        result['all_elements'] = [e.to_dict() for e in self.all_elements]
        
        return result
    
    def get_elements_by_grids(self, grid_ids: List[int]) -> List[UIElement]:
        """
        获取指定网格 ID 的元素（不做其他过滤）
        
        Args:
            grid_ids: 网格 ID 列表
        
        Returns:
            符合条件的元素列表
        
        Example:
            >>> elements = scanner.get_elements_by_grids([0, 3, 6])  # 左侧所有网格
        """
        target_ids = set(grid_ids)
        return [e for e in self.all_elements if e.grid_id in target_ids]
    
    def get_elements_by_position_names(self, position_names: List[str]) -> List[UIElement]:
        """
        获取指定位置名称的元素（不做其他过滤）
        
        Args:
            position_names: 位置名称列表，如 ['左上', '左中', '左下']
        
        Returns:
            符合条件的元素列表
        
        Example:
            >>> elements = scanner.get_elements_by_position_names(['左中', '左上'])
        """
        return [e for e in self.all_elements if e.grid_position in position_names]
    
    def _deduplicate_elements(self, elements: List[UIElement]) -> List[UIElement]:
        """
        去重：移除完全重叠的元素
        
        策略：
        1. 同一宫格内，如果两个元素完全重叠，保留外层元素
        2. 如果父子关系，保留父元素
        """
        if not elements:
            return []
        
        result = []
        seen_rects = []
        
        for elem in elements:
            rect = elem.bounding_rect
            
            # 检查是否与已存在的元素重叠
            is_duplicate = False
            
            for seen_rect in seen_rects:
                overlap = self._calculate_overlap(rect, seen_rect)
                
                # 如果重叠度 > 90%，认为是重复
                if overlap > 0.9:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                result.append(elem)
                seen_rects.append(rect)
        
        return result
    
    def _calculate_overlap(self, rect1: Tuple, rect2: Tuple) -> float:
        """计算两个矩形的重叠度 (IoU)"""
        left1, top1, right1, bottom1 = rect1
        left2, top2, right2, bottom2 = rect2
        
        # 计算交集
        inter_left = max(left1, left2)
        inter_top = max(top1, top2)
        inter_right = min(right1, right2)
        inter_bottom = min(bottom1, bottom2)
        
        if inter_left >= inter_right or inter_top >= inter_bottom:
            return 0.0
        
        inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
        
        # 计算并集
        area1 = (right1 - left1) * (bottom1 - top1)
        area2 = (right2 - left2) * (bottom2 - top2)
        
        union_area = area1 + area2 - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'total_elements': len(self.all_elements),
            'elements_with_grid': sum(1 for e in self.all_elements if e.grid_id is not None),
            'elements_without_grid': sum(1 for e in self.all_elements if e.grid_id is None),
            'by_control_type': {},
            'by_grid': {},
        }
        
        # 按控件类型统计
        for elem in self.all_elements:
            ctrl_type = elem.control_type
            if ctrl_type not in stats['by_control_type']:
                stats['by_control_type'][ctrl_type] = 0
            stats['by_control_type'][ctrl_type] += 1
        
        # 按宫格统计
        grid_counts = {}
        for elem in self.all_elements:
            if elem.grid_id is not None:
                pos_name = elem.grid_position or f'Grid_{elem.grid_id}'
                if pos_name not in grid_counts:
                    grid_counts[pos_name] = 0
                grid_counts[pos_name] += 1
        
        stats['by_grid'] = grid_counts
        
        return stats


# 便捷函数
def scan_ui_tree(root_element, grid_manager, max_depth: int = 15, 
                 deduplicate: bool = True) -> List[UIElement]:
    """
    扫描 UI 树并返回排序去重后的元素列表
    
    Args:
        root_element: UIA 根元素
        grid_manager: 宫格管理器
        max_depth: 最大搜索深度
        deduplicate: 是否去重
    
    Returns:
        UIElement 列表
    """
    scanner = UITreeScanner(root_element, grid_manager)
    scanner.scan_full_tree(max_depth=max_depth)
    return scanner.get_sorted_elements(deduplicate=deduplicate)
