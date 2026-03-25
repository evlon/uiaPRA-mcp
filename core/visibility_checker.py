"""
UI 元素可见性检测模块

提供严格的可见性过滤策略，确保只返回视觉上可见且未被遮挡的 UI 元素。
"""
from typing import Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VisibilityChecker:
    """可见性检测器"""
    
    def __init__(self):
        """初始化可见性检测器"""
        try:
            import uiautomation as auto
            self.auto = auto
        except ImportError as e:
            raise ImportError(f"Please install uiautomation: {e}")
    
    def is_element_visible(self, element) -> bool:
        """
        检查元素是否可见
        
        Args:
            element: UIA 元素对象
        
        Returns:
            True 如果元素可见，False 否则
        """
        if not element:
            return False
        
        # 1. 检查基本可见性属性
        if not self._check_basic_visibility(element):
            return False
        
        # 2. 检查是否离屏
        if self._is_offscreen(element):
            return False
        
        # 3. 检查实际像素覆盖
        if not self._check_pixel_coverage(element):
            return False
        
        # 4. 检查是否在前景层
        if not self._is_in_foreground_layer(element):
            return False
        
        return True
    
    def _check_basic_visibility(self, element) -> bool:
        """
        检查基本可见性属性
        
        Args:
            element: UIA 元素对象
        
        Returns:
            True 如果基本可见性通过
        """
        try:
            # 检查 IsOffscreen 属性
            if hasattr(element, 'IsOffscreen'):
                if element.IsOffscreen:
                    logger.debug(f"Element is offscreen: {self._get_element_name(element)}")
                    return False
            
            # 检查 IsEnabled 属性
            if hasattr(element, 'IsEnabled'):
                if not element.IsEnabled:
                    logger.debug(f"Element is disabled: {self._get_element_name(element)}")
                    # 禁用的元素通常也不可见，但这里我们只警告不拒绝
            
            # 检查 IsControlElement
            if hasattr(element, 'IsControlElement'):
                if not element.IsControlElement:
                    # 非控件元素（如纯文本）可能被跳过
                    pass
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking basic visibility: {e}")
            return True  # 出错时保守处理，假设可见
    
    def _is_offscreen(self, element) -> bool:
        """
        检查元素是否离屏（不在屏幕上显示）
        
        Args:
            element: UIA 元素对象
        
        Returns:
            True 如果元素离屏
        """
        try:
            # 方法 1: 使用 IsOffscreen 属性
            if hasattr(element, 'IsOffscreen'):
                return bool(element.IsOffscreen)
            
            # 方法 2: 检查边界矩形
            rect = self._get_bounding_rectangle(element)
            if not rect:
                return True
            
            # 如果矩形完全在屏幕外
            screen_rect = self._get_screen_rect()
            if (rect.right <= screen_rect[0] or 
                rect.left >= screen_rect[2] or
                rect.bottom <= screen_rect[1] or
                rect.top >= screen_rect[3]):
                logger.debug(f"Element is completely offscreen: {self._get_element_name(element)}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking offscreen: {e}")
            return False
    
    def _check_pixel_coverage(self, element, min_coverage: float = 0.5) -> bool:
        """
        检查元素的像素覆盖情况（核心交互区域是否可见）
        
        Args:
            element: UIA 元素对象
            min_coverage: 最小可见比例 (0.0-1.0)
        
        Returns:
            True 如果核心区域可见
        """
        try:
            rect = self._get_bounding_rectangle(element)
            if not rect:
                return False
            
            # 获取元素中心点
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            # 检查中心点是否被其他窗口遮挡
            if self._is_point_occluded(center_x, center_y, element):
                logger.debug(f"Element center is occluded: {self._get_element_name(element)}")
                
                # 尝试检查 clickable 区域（通常是元素的 80% 中心区域）
                clickable_rect = self._shrink_rect(rect, 0.8)
                if not self._rect_is_visible(clickable_rect, element):
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking pixel coverage: {e}")
            return True  # 出错时保守处理
    
    def _is_in_foreground_layer(self, element) -> bool:
        """
        检查元素是否在前景层（未被其他窗口完全遮挡）
        
        Args:
            element: UIA 元素对象
        
        Returns:
            True 如果元素在前景层
        """
        try:
            # 获取元素所在窗口
            window = self._get_parent_window(element)
            if not window:
                return False
            
            # 检查窗口是否是最顶层窗口
            if not self._is_topmost_window(window):
                logger.debug(f"Element's window is not topmost: {self._get_element_name(element)}")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking foreground layer: {e}")
            return True
    
    def _is_point_occluded(self, x: int, y: int, exclude_element=None) -> bool:
        """
        检查某一点是否被其他元素遮挡
        
        Args:
            x: X 坐标
            y: Y 坐标
            exclude_element: 要排除的元素（自身）
        
        Returns:
            True 如果该点被遮挡
        """
        try:
            # 使用 UIA 获取该点的元素
            element_at_point = self.auto.ElementFromPoint(x, y)
            
            if not element_at_point:
                return False
            
            # 如果就是目标元素本身，则未遮挡
            if exclude_element and element_at_point == exclude_element:
                return False
            
            # 检查是否是目标元素的子元素或父元素
            if self._is_same_tree(exclude_element, element_at_point):
                return False
            
            # 被其他元素占据，说明被遮挡
            return True
            
        except Exception as e:
            logger.debug(f"Error checking point occlusion: {e}")
            return False
    
    def _rect_is_visible(self, rect: Tuple[int, int, int, int], exclude_element=None) -> bool:
        """
        检查矩形区域是否可见
        
        Args:
            rect: 矩形 (left, top, right, bottom)
            exclude_element: 要排除的元素
        
        Returns:
            True 如果矩形区域可见
        """
        if not rect:
            return False
        
        left, top, right, bottom = rect
        
        # 采样矩形的多个点进行检查
        sample_points = [
            ((left + right) // 2, (top + bottom) // 2),  # 中心
            (left + (right - left) // 4, top + (bottom - top) // 4),  # 左上 1/4
            (right - (right - left) // 4, bottom - (bottom - top) // 4),  # 右下 1/4
        ]
        
        visible_count = 0
        for x, y in sample_points:
            if not self._is_point_occluded(x, y, exclude_element):
                visible_count += 1
        
        # 至少有 2 个采样点可见
        return visible_count >= 2
    
    def _shrink_rect(self, rect: Tuple[int, int, int, int], ratio: float) -> Tuple[int, int, int, int]:
        """
        缩小矩形到指定比例
        
        Args:
            rect: 原始矩形
            ratio: 缩小比例 (0.0-1.0)
        
        Returns:
            缩小后的矩形
        """
        if not rect:
            return rect
        
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        
        shrink_width = width * (1 - ratio) / 2
        shrink_height = height * (1 - ratio) / 2
        
        return (
            int(left + shrink_width),
            int(top + shrink_height),
            int(right - shrink_width),
            int(bottom - shrink_height)
        )
    
    def _get_bounding_rectangle(self, element) -> Optional[Tuple[int, int, int, int]]:
        """获取元素的边界矩形"""
        try:
            rect = element.BoundingRectangle
            return (rect.left, rect.top, rect.right, rect.bottom)
        except:
            return None
    
    def _get_screen_rect(self) -> Tuple[int, int, int, int]:
        """获取屏幕矩形"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            return (
                0, 0,
                user32.GetSystemMetrics(0),  # SM_CXSCREEN
                user32.GetSystemMetrics(1)   # SM_CYSCREEN
            )
        except:
            return (0, 0, 1920, 1080)  # 默认值
    
    def _get_parent_window(self, element) -> Optional[Any]:
        """获取元素所在的顶级窗口"""
        try:
            parent = element
            while parent and parent.ControlTypeName != 'WindowControl':
                parent = parent.GetParentControl()
            return parent
        except:
            return None
    
    def _is_topmost_window(self, window) -> bool:
        """检查窗口是否是最顶层窗口"""
        try:
            if not window:
                return False
            
            # 检查窗口是否有 WS_EX_TOPMOST 样式
            import ctypes
            from ctypes import wintypes
            
            hwnd = window.NativeWindowHandle
            if not hwnd:
                return False
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
            return bool(style & 0x00000008)  # WS_EX_TOPMOST
            
        except Exception as e:
            logger.debug(f"Error checking topmost window: {e}")
            return True  # 保守处理
    
    def _is_same_tree(self, elem1, elem2) -> bool:
        """检查两个元素是否在同一 UI 树中"""
        if not elem1 or not elem2:
            return False
        
        try:
            # 向上遍历到根，看是否相同
            root1 = elem1
            while root1.GetParentControl():
                root1 = root1.GetParentControl()
            
            root2 = elem2
            while root2.GetParentControl():
                root2 = root2.GetParentControl()
            
            return root1 == root2
            
        except:
            return False
    
    def _get_element_name(self, element) -> str:
        """获取元素名称（用于日志）"""
        try:
            name = getattr(element, 'Name', '')
            ctrl_type = getattr(element, 'ControlTypeName', '')
            return f"'{name}' ({ctrl_type})"
        except:
            return 'Unknown'
    
    def filter_visible_elements(self, elements: List[Any]) -> List[Any]:
        """
        过滤出可见的元素
        
        Args:
            elements: UIA 元素列表
        
        Returns:
            可见的元素列表
        """
        visible = []
        for elem in elements:
            if self.is_element_visible(elem):
                visible.append(elem)
            else:
                logger.debug(f"Filtered out invisible element: {self._get_element_name(elem)}")
        
        logger.info(f"Visibility filter: {len(visible)}/{len(elements)} elements visible")
        return visible


# 便捷函数
def check_visibility(element) -> bool:
    """
    检查元素是否可见
    
    Args:
        element: UIA 元素对象
    
    Returns:
        True 如果元素可见
    """
    checker = VisibilityChecker()
    return checker.is_element_visible(element)


def filter_visible(elements: List[Any]) -> List[Any]:
    """
    过滤出可见的元素
    
    Args:
        elements: UIA 元素列表
    
    Returns:
        可见的元素列表
    """
    checker = VisibilityChecker()
    return checker.filter_visible_elements(elements)
