"""
MCP 工具：元素操作接口

提供点击、输入、键盘操作等 UI 元素交互功能
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def register_element_actions(mcp: FastMCP, scanner_ref: dict):
    """注册元素操作工具"""
    
    @mcp.tool()
    async def click_element(
        selector_string: str = None,
        element_index: int = None,
        grid_position: str = None,
        element_name: str = None,
        click_type: str = "click"
    ) -> Dict[str, Any]:
        """
        点击指定的 UI 元素
        
        支持多种定位方式：selector 字符串、索引、网格位置 + 名称。
        默认使用鼠标中键点击（避免触发某些应用的特殊行为）。
        
        Args:
            selector_string: tdSelector 语法字符串（优先级最高）
                示例："[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜')] }]"
            element_index: 元素索引（在过滤后的列表中）
            grid_position: 网格位置（如 '左上'、'左中'）
            element_name: 元素名称（与 grid_position 配合使用）
            click_type: 点击类型，支持：
                - "click": 左键单击（默认）
                - "right_click": 右键单击
                - "double_click": 双击
                - "middle_click": 中键单击
        
        Returns:
            {
                "success": true,
                "element": {
                    "name": "发送",
                    "control_type": "ButtonControl",
                    "bounding_rect": [100, 200, 150, 230],
                    "center_point": [125, 215]
                },
                "action": "click",
                "message": "Successfully clicked element"
            }
        
        Example:
            >>> # 使用 selector 点击
            >>> click_element(
            ...     selector_string="[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '发送')] }]"
            ... )
            
            >>> # 使用网格位置点击
            >>> click_element(
            ...     grid_position="左中",
            ...     element_name="发送"
            ... )
            
            >>> # 右键点击
            >>> click_element(element_name="文件", click_type="right_click")
        """
        import pyautogui
        from core.error_handler import ensure_scanner_initialized
        from core.semantic_filter import SelectorBuilder
        
        scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
        
        try:
            # 定位元素
            target_elem = None
            
            if selector_string:
                # 使用 selector 定位
                target_elem = scanner.find_by_selector(selector_string, timeout=5.0)
            else:
                # 使用网格位置 + 名称定位
                from core.ui_tree_scanner import UITreeScanner
                
                ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
                ui_scanner.scan_full_tree(max_depth=15)
                all_elements = ui_scanner.get_sorted_elements(deduplicate=False)
                
                if grid_position and element_name:
                    # 通过网格位置和名称定位
                    for elem in all_elements:
                        if elem.grid_position == grid_position and elem.name == element_name:
                            target_elem = elem.element
                            break
                elif element_index is not None:
                    # 通过索引定位
                    if 0 <= element_index < len(all_elements):
                        target_elem = all_elements[element_index].element
            
            if not target_elem:
                return {
                    "success": False,
                    "error": "ELEMENT_NOT_FOUND",
                    "message": "无法找到指定的元素",
                    "search_criteria": {
                        "selector": selector_string,
                        "grid_position": grid_position,
                        "element_name": element_name,
                        "element_index": element_index
                    }
                }
            
            # 获取元素位置
            rect = target_elem.BoundingRectangle
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            # 执行点击
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            
            if click_type == "click":
                pyautogui.click()
            elif click_type == "right_click":
                pyautogui.rightClick()
            elif click_type == "double_click":
                pyautogui.doubleClick()
            elif click_type == "middle_click":
                pyautogui.middleClick()
            else:
                pyautogui.click()
            
            return {
                "success": True,
                "element": {
                    "name": getattr(target_elem, 'Name', ''),
                    "control_type": getattr(target_elem, 'ControlTypeName', ''),
                    "bounding_rect": [rect.left, rect.top, rect.right, rect.bottom],
                    "center_point": [center_x, center_y]
                },
                "action": click_type,
                "message": f"Successfully {click_type.replace('_', ' ')}ed element"
            }
        
        except Exception as e:
            logger.error(f"Error clicking element: {e}", exc_info=True)
            return {
                "success": False,
                "error": "CLICK_ERROR",
                "message": f"点击失败：{str(e)}",
                "solution": "请确保目标元素可见且可交互"
            }
    
    @mcp.tool()
    async def input_text(
        text: str,
        selector_string: str = None,
        element_index: int = None,
        grid_position: str = None,
        element_name: str = None,
        clear_first: bool = True,
        append_enter: bool = False
    ) -> Dict[str, Any]:
        """
        向指定的输入框元素输入文本
        
        自动聚焦到目标元素，然后使用键盘输入文本。
        支持先清空再输入，或追加输入。
        
        Args:
            text: 要输入的文本内容
            selector_string: tdSelector 语法字符串（优先级最高）
            element_index: 元素索引
            grid_position: 网格位置
            element_name: 元素名称
            clear_first: 是否先清空现有内容（默认 True）
            append_enter: 是否在最后按 Enter 键（默认 False）
        
        Returns:
            {
                "success": true,
                "element": {
                    "name": "搜索框",
                    "control_type": "EditControl",
                    "previous_text": "旧内容",
                    "input_text": "新内容"
                },
                "action": "input_text",
                "message": "Successfully input text"
            }
        
        Example:
            >>> # 在搜索框输入
            >>> input_text(
            ...     text="人工智能",
            ...     grid_position="右上",
            ...     element_name="搜索"
            ... )
            
            >>> # 清空后输入并按回车
            >>> input_text(
            ...     text="Hello World",
            ...     selector_string="[...]",
            ...     clear_first=True,
            ...     append_enter=True
            ... )
        """
        import pyautogui
        from core.error_handler import ensure_scanner_initialized
        
        scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
        
        try:
            # 定位元素（复用 click_element 的逻辑）
            target_elem = None
            
            if selector_string:
                target_elem = scanner.find_by_selector(selector_string, timeout=5.0)
            else:
                from core.ui_tree_scanner import UITreeScanner
                
                ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
                ui_scanner.scan_full_tree(max_depth=15)
                all_elements = ui_scanner.get_sorted_elements(deduplicate=False)
                
                if grid_position and element_name:
                    for elem in all_elements:
                        if elem.grid_position == grid_position and elem.name == element_name:
                            target_elem = elem.element
                            break
                elif element_index is not None:
                    if 0 <= element_index < len(all_elements):
                        target_elem = all_elements[element_index].element
            
            if not target_elem:
                return {
                    "success": False,
                    "error": "ELEMENT_NOT_FOUND",
                    "message": "无法找到指定的输入框元素"
                }
            
            # 获取元素信息
            rect = target_elem.BoundingRectangle
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            # 获取原有文本（如果支持）
            previous_text = ""
            try:
                if hasattr(target_elem, 'Value'):
                    previous_text = str(target_elem.Value)
                elif hasattr(target_elem, 'Name'):
                    previous_text = str(target_elem.Name)
            except:
                pass
            
            # 聚焦到元素
            pyautogui.moveTo(center_x, center_y, duration=0.2)
            pyautogui.click()
            
            # 清空现有内容
            if clear_first and previous_text:
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
            
            # 输入文本
            pyautogui.write(text, interval=0.05)
            
            # 按 Enter
            if append_enter:
                pyautogui.press('enter')
            
            return {
                "success": True,
                "element": {
                    "name": getattr(target_elem, 'Name', ''),
                    "control_type": getattr(target_elem, 'ControlTypeName', ''),
                    "bounding_rect": [rect.left, rect.top, rect.right, rect.bottom],
                    "previous_text": previous_text,
                    "input_text": text
                },
                "action": "input_text",
                "message": f"Successfully input '{text[:20]}{'...' if len(text) > 20 else ''}'"
            }
        
        except Exception as e:
            logger.error(f"Error inputting text: {e}", exc_info=True)
            return {
                "success": False,
                "error": "INPUT_ERROR",
                "message": f"输入失败：{str(e)}",
                "solution": "请确保目标元素是可编辑的输入框"
            }
    
    @mcp.tool()
    async def send_keys(
        keys: str,
        interval: float = 0.05
    ) -> Dict[str, Any]:
        """
        向当前焦点元素发送键盘按键
        
        支持特殊按键组合，如 Ctrl+C、Alt+F4 等。
        
        Args:
            keys: 按键字符串，支持：
                - 普通字符：直接输入
                - 特殊按键：{enter}, {esc}, {tab}, {backspace}, {delete}
                - 组合键：{ctrl c}, {alt f4}, {shift home}
            interval: 按键间隔（秒），默认 0.05
        
        Returns:
            {
                "success": true,
                "keys_sent": "Ctrl+C",
                "message": "Successfully sent keys"
            }
        
        Example:
            >>> # 发送 Ctrl+C 复制
            >>> send_keys(keys="{ctrl c}")
            
            >>> # 发送 Alt+F4 关闭窗口
            >>> send_keys(keys="{alt f4}")
            
            >>> # 发送 Enter
            >>> send_keys(keys="{enter}")
            
            >>> # 发送文本
            >>> send_keys(keys="Hello World")
        """
        import pyautogui
        
        try:
            # 解析特殊按键
            key_map = {
                "{enter}": "enter",
                "{esc}": "esc",
                "{escape}": "esc",
                "{tab}": "tab",
                "{backspace}": "backspace",
                "{delete}": "delete",
                "{del}": "delete",
                "{home}": "home",
                "{end}": "end",
                "{pageup}": "pageup",
                "{pagedown}": "pagedown",
                "{up}": "up",
                "{down}": "down",
                "{left}": "left",
                "{right}": "right",
                "{f1}": "f1",
                "{f2}": "f2",
                "{f3}": "f3",
                "{f4}": "f4",
                "{f5}": "f5",
                "{f6}": "f6",
                "{f7}": "f7",
                "{f8}": "f8",
                "{f9}": "f9",
                "{f10}": "f10",
                "{f11}": "f11",
                "{f12}": "f12",
            }
            
            # 处理组合键
            combo_keys = []
            remaining = keys
            
            # 检查花括号内的组合键
            if keys.startswith("{") and "}" in keys:
                end_brace = keys.index("}")
                combo_str = keys[1:end_brace].lower()
                
                # 映射修饰键
                modifier_map = {
                    "ctrl": "command" if pyautogui.platform == "darwin" else "ctrl",
                    "alt": "option" if pyautogui.platform == "darwin" else "alt",
                    "shift": "shift",
                    "win": "command" if pyautogui.platform == "darwin" else "win",
                }
                
                parts = combo_str.split()
                for part in parts:
                    if part in modifier_map:
                        combo_keys.append(modifier_map[part])
                    elif part in key_map:
                        combo_keys.append(key_map[part])
                    else:
                        combo_keys.append(part)
                
                # 执行组合键
                if len(combo_keys) > 1:
                    pyautogui.hotkey(*combo_keys)
                else:
                    pyautogui.press(combo_keys[0])
                
                message = f"Sent hotkey: {keys}"
            else:
                # 普通文本或单个按键
                if keys in key_map:
                    pyautogui.press(key_map[keys], interval=interval)
                    message = f"Sent key: {keys}"
                else:
                    pyautogui.write(keys, interval=interval)
                    message = f"Typed: {keys[:30]}{'...' if len(keys) > 30 else ''}"
            
            return {
                "success": True,
                "keys_sent": keys,
                "message": message
            }
        
        except Exception as e:
            logger.error(f"Error sending keys: {e}")
            return {
                "success": False,
                "error": "SEND_KEYS_ERROR",
                "message": f"发送按键失败：{str(e)}"
            }
    
    @mcp.tool()
    async def scroll_element(
        clicks: int = 3,
        selector_string: str = None,
        element_index: int = None,
        grid_position: str = None,
        element_name: str = None
    ) -> Dict[str, Any]:
        """
        滚动指定的可滚动元素
        
        将鼠标移动到目标元素上，然后执行滚轮操作。
        
        Args:
            clicks: 滚动次数，正数向上/向右，负数向下/向左
            selector_string: tdSelector 语法字符串
            element_index: 元素索引
            grid_position: 网格位置
            element_name: 元素名称
        
        Returns:
            {
                "success": true,
                "element": {
                    "name": "列表",
                    "control_type": "ListControl"
                },
                "scroll_amount": clicks,
                "message": "Successfully scrolled element"
            }
        
        Example:
            >>> # 向下滚动 3 格
            >>> scroll_element(clicks=-3, grid_position="中间", element_name="消息列表")
            
            >>> # 向上滚动
            >>> scroll_element(clicks=5, selector_string="[...]")
        """
        import pyautogui
        from core.error_handler import ensure_scanner_initialized
        
        scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
        
        try:
            # 定位元素
            target_elem = None
            
            if selector_string:
                target_elem = scanner.find_by_selector(selector_string, timeout=5.0)
            else:
                from core.ui_tree_scanner import UITreeScanner
                
                ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
                ui_scanner.scan_full_tree(max_depth=15)
                all_elements = ui_scanner.get_sorted_elements(deduplicate=False)
                
                if grid_position and element_name:
                    for elem in all_elements:
                        if elem.grid_position == grid_position and elem.name == element_name:
                            target_elem = elem.element
                            break
                elif element_index is not None:
                    if 0 <= element_index < len(all_elements):
                        target_elem = all_elements[element_index].element
            
            if not target_elem:
                return {
                    "success": False,
                    "error": "ELEMENT_NOT_FOUND",
                    "message": "无法找到指定的元素"
                }
            
            # 获取元素位置
            rect = target_elem.BoundingRectangle
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            # 移动鼠标并滚动
            pyautogui.moveTo(center_x, center_y, duration=0.2)
            pyautogui.scroll(clicks)
            
            return {
                "success": True,
                "element": {
                    "name": getattr(target_elem, 'Name', ''),
                    "control_type": getattr(target_elem, 'ControlTypeName', ''),
                    "bounding_rect": [rect.left, rect.top, rect.right, rect.bottom]
                },
                "scroll_amount": clicks,
                "message": f"Scrolled {'up' if clicks > 0 else 'down'} by {abs(clicks)} clicks"
            }
        
        except Exception as e:
            logger.error(f"Error scrolling element: {e}", exc_info=True)
            return {
                "success": False,
                "error": "SCROLL_ERROR",
                "message": f"滚动失败：{str(e)}"
            }
    
    @mcp.tool()
    async def drag_drop(
        start_selector: str = None,
        start_grid: str = None,
        start_name: str = None,
        end_selector: str = None,
        end_grid: str = None,
        end_name: str = None,
        duration: float = 1.0
    ) -> Dict[str, Any]:
        """
        执行拖放操作
        
        从起始元素拖拽到目标元素。
        
        Args:
            start_selector: 起始元素的 selector
            start_grid: 起始元素的网格位置
            start_name: 起始元素的名称
            end_selector: 目标元素的 selector
            end_grid: 目标元素的网格位置
            end_name: 目标元素的名称
            duration: 拖拽持续时间（秒）
        
        Returns:
            {
                "success": true,
                "start_element": {...},
                "end_element": {...},
                "message": "Successfully dragged and dropped"
            }
        
        Example:
            >>> # 拖动文件到文件夹
            >>> drag_drop(
            ...     start_grid="左中",
            ...     start_name="文件.txt",
            ...     end_grid="右中",
            ...     end_name="文件夹"
            ... )
        """
        import pyautogui
        from core.error_handler import ensure_scanner_initialized
        
        scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
        
        def find_element_by_criteria(selector, grid_pos, name):
            """辅助函数：定位元素"""
            if selector:
                return scanner.find_by_selector(selector, timeout=3.0)
            else:
                from core.ui_tree_scanner import UITreeScanner
                ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
                ui_scanner.scan_full_tree(max_depth=15)
                all_elements = ui_scanner.get_sorted_elements(deduplicate=False)
                
                for elem in all_elements:
                    if grid_pos and name and elem.grid_position == grid_pos and elem.name == name:
                        return elem.element
                return None
        
        try:
            # 查找起始元素
            start_elem = find_element_by_criteria(start_selector, start_grid, start_name)
            if not start_elem:
                return {
                    "success": False,
                    "error": "START_ELEMENT_NOT_FOUND",
                    "message": "无法找到起始元素"
                }
            
            # 查找目标元素
            end_elem = find_element_by_criteria(end_selector, end_grid, end_name)
            if not end_elem:
                return {
                    "success": False,
                    "error": "END_ELEMENT_NOT_FOUND",
                    "message": "无法找到目标元素"
                }
            
            # 获取位置
            start_rect = start_elem.BoundingRectangle
            start_x = (start_rect.left + start_rect.right) // 2
            start_y = (start_rect.top + start_rect.bottom) // 2
            
            end_rect = end_elem.BoundingRectangle
            end_x = (end_rect.left + end_rect.right) // 2
            end_y = (end_rect.top + end_rect.bottom) // 2
            
            # 执行拖放
            pyautogui.moveTo(start_x, start_y, duration=0.2)
            pyautogui.dragTo(end_x, end_y, button='left', duration=duration)
            
            return {
                "success": True,
                "start_element": {
                    "name": getattr(start_elem, 'Name', ''),
                    "bounding_rect": [start_rect.left, start_rect.top, start_rect.right, start_rect.bottom]
                },
                "end_element": {
                    "name": getattr(end_elem, 'Name', ''),
                    "bounding_rect": [end_rect.left, end_rect.top, end_rect.right, end_rect.bottom]
                },
                "message": "Successfully dragged and dropped"
            }
        
        except Exception as e:
            logger.error(f"Error in drag-drop: {e}", exc_info=True)
            return {
                "success": False,
                "error": "DRAG_DROP_ERROR",
                "message": f"拖放失败：{str(e)}"
            }
    
    return click_element, input_text, send_keys, scroll_element, drag_drop
