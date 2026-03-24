"""
UIA 区域扫描器
基于 uiautomation 实现按区域扫描 UI 元素
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# 使用新的日志系统
from core.logger import get_logger, log_function_call, LogContext

logger = get_logger('tdrpa.scanner', level='DEBUG', detailed=True)


@dataclass
class ElementInfo:
    """元素信息"""
    element: Any  # uiautomation.Control
    name: str
    control_type: str
    automation_id: str
    class_name: str
    bounding_rect: tuple
    grid_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """转换为字典 (用于 JSON 序列化)"""
        return {
            'name': self.name,
            'control_type': self.control_type,
            'automation_id': self.automation_id,
            'class_name': self.class_name,
            'bounding_rect': self.bounding_rect,
            'grid_id': self.grid_id
        }


class UIARegionScanner:
    """UIA 区域扫描器"""
    
    def __init__(self, process_name: str = None, 
                 window_title: str = None,
                 timeout: float = 5.0):
        """
        :param process_name: 限定扫描的进程名 (可选)
        :param window_title: 窗口标题 (可选)
        :param timeout: 超时秒数
        """
        try:
            import uiautomation as auto
            self.auto = auto
        except ImportError as e:
            raise ImportError(f"Please install uiautomation: {e}")
        
        self.process_name = process_name
        self.window_title = window_title
        self.timeout = timeout
        self.root_element = self._get_root_element()
    
    def _get_root_element(self) -> Any:
        """获取扫描根元素"""
        if self.process_name or self.window_title:
            # 从指定进程/窗口开始
            root = self.auto.GetRootControl()
            
            # 查找匹配的窗口
            window = self._find_window(root)
            
            if not window:
                raise RuntimeError(
                    f"Cannot find window: process={self.process_name}, "
                    f"title={self.window_title}"
                )
            
            logger.info(f"Found root element: {window.Name}")
            return window
        else:
            # 从 Desktop 开始
            root = self.auto.GetRootControl()
            logger.info("Using Desktop as root element")
            return root
    
    def _find_window(self, root) -> Optional[Any]:
        """查找匹配的窗口"""
        try:
            children = root.GetChildren()
            for child in children:
                try:
                    # 检查进程名
                    if self.process_name:
                        try:
                            proc_name = child.ProcessName
                            if not proc_name or self.process_name.lower() not in proc_name.lower():
                                continue
                        except:
                            continue
                    
                    # 检查窗口标题
                    if self.window_title:
                        try:
                            name = child.Name
                            if not name or self.window_title.lower() not in name.lower():
                                continue
                        except:
                            continue
                    
                    return child
                except:
                    continue
        except Exception as e:
            logger.error(f"Error finding window: {e}")
        
        return None
    
    def _element_in_region(self, element, region_rect: tuple) -> bool:
        """检查元素是否在区域内 (基于中心点)"""
        try:
            rect = element.BoundingRectangle
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            left, top, right, bottom = region_rect
            return (left <= center_x <= right and 
                    top <= center_y <= bottom)
        except Exception as e:
            logger.debug(f"Error checking element region: {e}")
            return False
    
    def _element_info(self, element, grid_id: int = None) -> ElementInfo:
        """提取元素信息"""
        try:
            rect = element.BoundingRectangle
            bounding_rect = (rect.left, rect.top, rect.right, rect.bottom)
        except:
            bounding_rect = (0, 0, 0, 0)
        
        return ElementInfo(
            element=element,
            name=getattr(element, 'Name', ''),
            control_type=getattr(element, 'ControlTypeName', ''),
            automation_id=getattr(element, 'AutomationId', ''),
            class_name=getattr(element, 'ClassName', ''),
            bounding_rect=bounding_rect,
            grid_id=grid_id
        )
    
    def scan_grid(self, grid_rect: tuple, search_depth: int = 3) -> List[ElementInfo]:
        """扫描单个宫格区域"""
        elements = []
        
        try:
            def traverse(elem, depth=0):
                if depth > search_depth:
                    return
                
                # 检查元素是否在区域内
                if self._element_in_region(elem, grid_rect):
                    info = self._element_info(elem)
                    elements.append(info)
                
                # 遍历子元素
                try:
                    children = elem.GetChildren()
                    for child in children:
                        traverse(child, depth + 1)
                except:
                    pass
            
            traverse(self.root_element)
            logger.info(f"Found {len(elements)} elements in grid {grid_rect}")
            
        except Exception as e:
            logger.error(f"Error scanning grid: {e}")
        
        return elements
    
    def find_by_selector(self, selector: str, timeout: float = None) -> Optional[Any]:
        """使用 selector 查找元素"""
        if timeout is None:
            timeout = self.timeout
        
        try:
            from utils.selector_parser import SelectorParser
            parser = SelectorParser()
            parsed_nodes = parser.parse(selector)
            
            if not parsed_nodes:
                logger.error(f"Failed to parse selector: {selector}")
                return None
            
            logger.info(f"Parsed selector: {parsed_nodes}")
            
            # 从根元素开始查找
            current_elements = [self.root_element]
            
            for i, node in enumerate(parsed_nodes):
                node_type = node.get('type')
                conditions = node.get('conditions', [])
                
                logger.info(f"Searching node {i}: type={node_type}, conditions={len(conditions)}")
                
                next_elements = []
                
                for elem in current_elements:
                    # 遍历当前元素的所有子元素
                    try:
                        children = self._get_all_descendants(elem, max_depth=10)
                        
                        for child in children:
                            if self._match_conditions(child, conditions):
                                next_elements.append(child)
                                logger.debug(f"Matched element: {child.Name}, ControlType: {child.ControlTypeName}")
                    except Exception as e:
                        logger.debug(f"Error getting children: {e}")
                
                if not next_elements:
                    logger.warning(f"No elements matched node {i}")
                    return None
                
                current_elements = next_elements
            
            # 返回第一个匹配的元素
            if current_elements:
                result = current_elements[0]
                logger.info(f"Found element: {result.Name}, ControlType: {result.ControlTypeName}")
                return result
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error in find_by_selector: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _match_conditions(self, element, conditions: List[Dict[str, Any]]) -> bool:
        """检查元素是否满足所有条件"""
        try:
            for cond in conditions:
                prop = cond.get('property')
                expected_value = cond.get('value')
                match_type = cond.get('match_type', 'exact')
                
                # 获取属性值
                actual_value = self._get_property(element, prop)
                
                if actual_value is None:
                    return False
                
                # 特殊处理 aaRole 的匹配
                # tdSelector 中的 "PushButton" 应该匹配到实际的 "Button"
                if prop == 'aaRole':
                    if expected_value.lower() == 'pushbutton' and actual_value.lower() == 'button':
                        continue  # 匹配成功，继续下一个条件
                    elif expected_value.lower() == 'button' and actual_value.lower() == 'pushbutton':
                        continue  # 反向也支持
                
                # 匹配
                if match_type == 'exact':
                    if str(actual_value).lower() != str(expected_value).lower():
                        return False
                elif match_type == 'fuzzy':
                    if str(expected_value).lower() not in str(actual_value).lower():
                        return False
                elif match_type == 'regex':
                    import re
                    if not re.search(str(expected_value), str(actual_value), re.IGNORECASE):
                        return False
            
            return True
        
        except Exception as e:
            logger.debug(f"Error matching conditions: {e}")
            return False
    
    def _get_property(self, element, prop: str) -> Optional[str]:
        """获取元素的属性值"""
        try:
            # 映射常见属性
            prop_map = {
                'Text': 'Name',
                'Name': 'Name',
                'ControlType': 'ControlTypeName',
                'AutomationId': 'AutomationId',
                'ClassName': 'ClassName',
                'App': 'ProcessName',
                'aaRole': 'ControlTypeName',  # tdSelector 特殊属性
            }
            
            attr_name = prop_map.get(prop, prop)
            
            if hasattr(element, attr_name):
                value = getattr(element, attr_name)
                if value is None:
                    return ''
                
                str_value = str(value)
                
                # 特殊处理 aaRole：移除 "Control" 后缀以便匹配
                # 例如：ButtonControl -> Button
                if prop == 'aaRole':
                    if str_value.endswith('Control'):
                        base_type = str_value[:-7]  # 移除 "Control"
                        
                        # tdSelector 使用 "PushButton" 表示按钮，需要映射回 "Button"
                        if base_type == 'PushButton':
                            return 'Button'
                        
                        return base_type
                    return str_value
                
                return str_value
            
            return None
        
        except Exception as e:
            logger.debug(f"Error getting property {prop}: {e}")
            return None
    
    def _get_all_descendants(self, element, max_depth: int = 15) -> List[Any]:
        """获取所有后代元素（包括直接子元素）"""
        descendants = []
        
        try:
            def traverse(elem, depth=0):
                if depth > max_depth:
                    return
                
                try:
                    children = elem.GetChildren()
                    for child in children:
                        descendants.append(child)
                        traverse(child, depth + 1)
                except:
                    pass
            
            traverse(element)
        
        except Exception as e:
            logger.debug(f"Error getting descendants: {e}")
        
        return descendants
    
    def get_window_rect(self) -> tuple:
        """获取根元素的窗口矩形"""
        try:
            rect = self.root_element.BoundingRectangle
            return (rect.left, rect.top, rect.right, rect.bottom)
        except Exception as e:
            logger.error(f"Error getting window rect: {e}")
            return (0, 0, 0, 0)
