"""
MCP 工具：宫格拾取器

集成统一错误处理机制
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def register_grid_picker(mcp: FastMCP, scanner_ref: dict):
    """注册宫格拾取器工具"""
    
    @mcp.tool()
    async def set_focus_window(
        process_name: str = None,
        window_title: str = None
    ) -> Dict[str, Any]:
        """
        设置目标扫描窗口
        
        指定要扫描的进程或窗口，后续的元素查找将限定在此窗口范围内。
        
        Args:
            process_name: 进程名，如 "notepad.exe", "WeChat.exe"
            window_title: 窗口标题，支持模糊匹配
        
        Returns:
            设置结果和窗口信息
        
        Example:
            >>> set_focus_window(process_name="notepad.exe")
            {
                "success": true,
                "window": {
                    "process_name": "notepad.exe",
                    "title": "无标题 - 记事本",
                    "rect": [100, 100, 500, 400]
                },
                "grid_info": {
                    "rows": 3,
                    "cols": 3,
                    "total_grids": 9
                }
            }
        """
        from core.uia_region_scanner import UIARegionScanner
        from core.grid_manager import GridManager
        from core.error_handler import WindowNotFoundError, ensure_scanner_initialized
        
        try:
            # 创建新的扫描器
            scanner = UIARegionScanner(
                process_name=process_name,
                window_title=window_title,
                timeout=5.0
            )
            
            # 更新引用
            scanner_ref['scanner'] = scanner
            
            # 创建宫格管理器（默认 9 宫格）
            window_rect = scanner.get_window_rect()
            grid_manager = GridManager(window_rect, rows=3, cols=3)  # 改为 9 宫格
            scanner_ref['grid_manager'] = grid_manager
            
            # 获取窗口信息
            try:
                rect = scanner.root_element.BoundingRectangle
                window_info = {
                    "process_name": process_name or "N/A",
                    "title": scanner.root_element.Name if hasattr(scanner.root_element, 'Name') else '',
                    "rect": [rect.left, rect.top, rect.right, rect.bottom]
                }
            except:
                window_info = {
                    "process_name": process_name or "N/A",
                    "title": "Unknown",
                    "rect": [0, 0, 0, 0]
                }
            
            return {
                "success": True,
                "window": window_info,
                "grid_info": {
                    "rows": 3,  # 9 宫格
                    "cols": 3,
                    "total_grids": 9,
                    "window_size": [
                        window_info["rect"][2] - window_info["rect"][0],
                        window_info["rect"][3] - window_info["rect"][1]
                    ]
                }
            }
        
        except Exception as e:
            logger.error(f"Error setting focus window: {e}")
            
            # 使用统一的错误处理
            from core.error_handler import WindowNotFoundError
            
            error = WindowNotFoundError(
                process_name=process_name,
                window_title=window_title,
                message=f"无法找到窗口：{str(e)}",
                details={"exception": str(e)}
            )
            return error.to_dict()
    
    @mcp.tool()
    async def list_windows(
        process_name: Optional[str] = None,
        window_title_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出所有可用的窗口供选择
        
        扫描当前系统中的所有窗口，支持按进程名或窗口标题过滤。
        当 set_focus_window() 找不到窗口时，可使用此函数查看可用窗口列表。
        
        Args:
            process_name: 可选，按进程名过滤（如 "WeChat.exe"）
                - 支持部分匹配（如 "WeChat" 匹配 "WeChat.exe"）
                - 不区分大小写
            window_title_pattern: 可选，按窗口标题正则匹配
                - 使用 Python re 模块进行正则匹配
                - 支持模糊搜索（如 "微信" 匹配包含"微信"的标题）
        
        Returns:
            {
                "success": True,
                "windows": [
                    {
                        "window_id": "hwnd_12345",
                        "process_name": "WeChat.exe",
                        "process_id": 8888,
                        "title": "微信",
                        "rect": [100, 100, 800, 600],
                        "width": 700,
                        "height": 500,
                        "is_visible": True,
                        "is_topmost": False,
                        "control_type": "WindowControl",
                        "automation_id": ""
                    },
                    ...
                ],
                "total_count": 5,
                "filtered_by": {
                    "process_name": "WeChat.exe",
                    "window_title_pattern": null
                },
                "message": "找到 5 个窗口"
            }
        
        Example:
            >>> # 列出所有窗口
            >>> await list_windows()
            
            >>> # 只列出微信相关窗口
            >>> await list_windows(process_name="WeChat")
            
            >>> # 使用正则匹配标题
            >>> await list_windows(window_title_pattern=".*聊天.*")
        """
        import uiautomation as auto
        import re
        from core.error_handler import handle_mcp_errors
        
        try:
            # 获取桌面根元素
            desktop = auto.GetRootControl()
            
            # 获取所有一级子元素（顶级窗口）
            all_windows = desktop.GetChildren()
            
            windows = []
            for window in all_windows:
                try:
                    # 获取窗口信息
                    title = getattr(window, 'Name', '') or ''
                    proc_name = getattr(window, 'ProcessName', '') or ''
                    proc_id = getattr(window, 'ProcessId', 0)
                    control_type = getattr(window, 'ControlTypeName', '')
                    automation_id = getattr(window, 'AutomationId', '')
                    
                    # 获取矩形
                    try:
                        rect = window.BoundingRectangle
                        rect_tuple = (rect.left, rect.top, rect.right, rect.bottom)
                        width = rect.right - rect.left
                        height = rect.bottom - rect.top
                    except:
                        rect_tuple = [0, 0, 0, 0]
                        width = 0
                        height = 0
                    
                    # 应用过滤器
                    if process_name:
                        if process_name.lower() not in proc_name.lower():
                            continue
                    
                    if window_title_pattern:
                        if not re.search(window_title_pattern, title, re.IGNORECASE):
                            continue
                    
                    # 检查是否可见
                    is_visible = width > 0 and height > 0
                    
                    # 检查是否最顶层
                    is_topmost = False
                    try:
                        hwnd = window.NativeWindowHandle
                        if hwnd:
                            import ctypes
                            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
                            is_topmost = bool(style & 0x00000008)  # WS_EX_TOPMOST
                    except:
                        pass
                    
                    window_info = {
                        "window_id": f"hwnd_{proc_id}_{id(window)}",
                        "process_name": proc_name,
                        "process_id": proc_id,
                        "title": title,
                        "rect": list(rect_tuple),
                        "width": width,
                        "height": height,
                        "is_visible": is_visible,
                        "is_topmost": is_topmost,
                        "control_type": control_type,
                        "automation_id": automation_id
                    }
                    
                    windows.append(window_info)
                    
                except Exception as e:
                    logger.debug(f"Error processing window: {e}")
                    continue
            
            # 按进程名和标题排序
            windows.sort(key=lambda w: (w['process_name'], w['title']))
            
            return {
                "success": True,
                "windows": windows,
                "total_count": len(windows),
                "filtered_by": {
                    "process_name": process_name,
                    "window_title_pattern": window_title_pattern
                },
                "message": f"找到 {len(windows)} 个窗口"
            }
        
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            return {
                "success": False,
                "error": "WINDOW_LIST_ERROR",
                "message": f"无法获取窗口列表：{str(e)}",
                "solution": "请确保有足够的权限访问系统窗口"
            }
    
    @mcp.tool()
    async def pick_grid_element(
        grid_id: int,
        element_index: int = 0,
        refresh: bool = True
    ) -> Dict[str, Any]:
        """
        拾取指定宫格内的元素
        
        Args:
            grid_id: 宫格编号 (0-15)
            element_index: 元素索引 (该宫格内第几个元素)
            refresh: 是否重新扫描
        
        Returns:
            拾取的元素信息
        
        Example:
            >>> pick_grid_element(grid_id=5, element_index=0)
            {
                "success": true,
                "element": {
                    "name": "发送",
                    "control_type": "Button",
                    "grid_id": 5,
                    "element_index": 0
                }
            }
        """
        from core.error_handler import ensure_scanner_initialized, GridNotFoundError
        
        # 确保扫描器已初始化
        scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
        
        try:
            # 获取宫格
            try:
                grid = grid_manager.get_grid_by_id(grid_id)
            except ValueError as e:
                raise GridNotFoundError(
                    grid_id=grid_id,
                    message=f"无效的宫格 ID {grid_id}: {str(e)}"
                )
            
            grid_rect = grid.to_tuple()
            
            # 扫描宫格
            if refresh:
                elements = scanner.scan_grid(grid_rect)
            else:
                # 使用缓存
                elements = scanner_ref.get('cache', {}).get(grid_id, [])
            
            if not elements:
                return {
                    "success": False,
                    "grid_id": grid_id,
                    "message": f"No elements found in grid {grid_id}"
                }
            
            if element_index >= len(elements):
                return {
                    "success": False,
                    "grid_id": grid_id,
                    "message": f"Element index {element_index} out of range (0-{len(elements)-1})"
                }
            
            elem = elements[element_index]
            
            return {
                "success": True,
                "element": {
                    "name": elem.name,
                    "control_type": elem.control_type,
                    "automation_id": elem.automation_id,
                    "class_name": elem.class_name,
                    "bounding_rect": list(elem.bounding_rect),
                    "grid_id": grid_id,
                    "element_index": element_index
                },
                "grid_rect": list(grid_rect),
                "total_elements_in_grid": len(elements)
            }
        
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error picking grid element: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def get_ui_tree_data(
        max_depth: int = 15,
        include_raw_elements: bool = False,
        enable_visibility_filter: bool = True
    ) -> Dict[str, Any]:
        """
        获取完整的 UI 树数据（按网格分组，带可见性过滤）
        
        这是最灵活的 API，返回所有 UI 元素及其分组信息，让 LLM 来决定如何筛选。
        默认启用严格的可见性过滤，只返回视觉上可见且未被遮挡的元素。
        
        Args:
            max_depth: 最大搜索深度，默认 15
            include_raw_elements: 是否包含所有元素的详细信息（可能很大），默认 False
            enable_visibility_filter: 是否启用可见性过滤，默认 True
                - 启用时会排除被遮挡、离屏、不在前景层的元素
                - 适用于需要精确匹配用户肉眼可见元素的场景
                - 禁用时返回所有 UIA 检测到的元素（包括后台元素）
        
        Returns:
            UI 树数据结构：
            {
                "by_grid": {
                    "左上": [element1, element2, ...],
                    "左中": [...],
                    ...
                },
                "by_control_type": {
                    "ButtonControl": 5,
                    "TextControl": 10,
                    ...
                },
                "statistics": {
                    "total_elements": 77,
                    "by_grid_position": {"左中": 15, "左上": 8, ...},
                    "by_control_type": {"ButtonControl": 5, ...}
                }
            }
        
        Example:
            >>> ui_data = get_ui_tree_data()  # 默认启用可见性过滤
            >>> left_middle_elements = ui_data['by_grid']['左中']
            >>> # 然后 LLM 可以根据需要筛选这些元素
            
            >>> # 禁用可见性过滤，获取所有元素（包括被遮挡的）
            >>> ui_data = get_ui_tree_data(enable_visibility_filter=False)
        """
        scanner = scanner_ref.get('scanner')
        grid_manager = scanner_ref.get('grid_manager')
        
        if not scanner or not grid_manager:
            return {
                "success": False,
                "error": "Scanner not initialized. Call set_focus_window first."
            }
        
        try:
            from core.ui_tree_scanner import UITreeScanner
            
            ui_scanner = UITreeScanner(
                scanner.root_element, 
                grid_manager,
                enable_visibility_filter=enable_visibility_filter
            )
            ui_scanner.scan_full_tree(max_depth=max_depth)
            
            ui_data = ui_scanner.get_grouped_ui_tree()
            
            # 添加可见性过滤状态到返回结果
            ui_data['visibility_filter_enabled'] = enable_visibility_filter
            
            # 如果不包含原始元素，移除详细列表以减小响应大小
            if not include_raw_elements:
                ui_data.pop('all_elements', None)
            
            return {
                "success": True,
                "ui_tree": ui_data,
                "message": f"Scanned {ui_data['statistics']['total_elements']} elements{' with visibility filter' if enable_visibility_filter else ''}"
            }
        
        except Exception as e:
            logger.error(f"Error getting UI tree data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def filter_ui_elements(
        grid_positions: Optional[List[str]] = None,
        name_contains: Optional[str] = None,
        control_types: Optional[List[str]] = None,
        min_width: int = 0,
        min_height: int = 0,
        sort_by: str = 'name',
        enable_visibility_filter: bool = True,
        visibility_mode: str = "balanced"  # 新增参数
    ) -> Dict[str, Any]:
        """
        语义化过滤 UI 元素
        
        根据自然语言描述的条件筛选元素，支持多种过滤条件组合。
        默认启用可见性过滤（平衡模式），确保只返回用户肉眼可见的元素。
        
        Args:
            grid_positions: 网格位置列表，如 ['左上', '左中', '左下']
            name_contains: 名称包含的字符串，如 '搜'
            control_types: 控件类型列表，如 ['ButtonControl', 'TextControl']
            min_width: 最小宽度（像素）
            min_height: 最小高度（像素）
            sort_by: 排序方式 ('name', 'grid_id', 'size')
            enable_visibility_filter: 是否启用可见性过滤，默认 True
                - 启用时会排除被其他窗口、对话框、控件遮挡的元素
                - 检查元素的核心交互区域是否暴露在前景层
                - 适用于"点击左边按钮"等需要精确匹配可见元素的场景
            visibility_mode: 可见性过滤模式，默认 "balanced"
                - "off": 不过滤
                - "balanced": 平衡模式（推荐）
                - "strict": 严格模式（可能过滤过严）
        
        Returns:
            过滤后的元素列表和统计信息
        
        Example:
            >>> # 查找左侧可见的搜索按钮
            >>> filter_ui_elements(
            ...     grid_positions=['左中', '左上'],
            ...     name_contains='搜',
            ...     control_types=['ButtonControl']
            ... )
            
            >>> # 使用严格模式
            >>> filter_ui_elements(name_contains='菜单', visibility_mode="strict")
            
            >>> # 禁用可见性过滤，获取所有匹配元素（包括被遮挡的）
            >>> filter_ui_elements(name_contains='菜单', enable_visibility_filter=False)
        """
        scanner = scanner_ref.get('scanner')
        grid_manager = scanner_ref.get('grid_manager')
        
        if not scanner or not grid_manager:
            return {
                "success": False,
                "error": "Scanner not initialized. Call set_focus_window first."
            }
        
        try:
            from core.ui_tree_scanner import UITreeScanner
            from core.semantic_filter import SemanticFilter, SemanticQuery
            
            # 扫描 UI 树（带可见性过滤）
            ui_scanner = UITreeScanner(
                scanner.root_element, 
                grid_manager,
                enable_visibility_filter=enable_visibility_filter,
                visibility_mode=visibility_mode
            )
            ui_scanner.scan_full_tree(max_depth=15)
            all_elements = ui_scanner.get_sorted_elements(deduplicate=False)
            
            # 创建语义化查询
            query = SemanticQuery(
                grid_positions=grid_positions,
                name_contains=name_contains,
                control_types=control_types,
                min_width=min_width,
                min_height=min_height,
                priority_field=sort_by
            )
            
            # 应用过滤
            semantic_filter = SemanticFilter(all_elements)
            filtered_results = semantic_filter.apply_query(query)
            
            # 构建结果
            results = [
                {
                    'name': elem.name,
                    'control_type': elem.control_type,
                    'automation_id': elem.automation_id,
                    'bounding_rect': list(elem.bounding_rect),
                    'grid_id': elem.grid_id,
                    'grid_position': elem.grid_position,
                    'center_point': list(elem.center_point) if elem.center_point else None,
                }
                for elem in filtered_results
            ]
            
            stats = semantic_filter.get_statistics()
            stats['visibility_filter_enabled'] = enable_visibility_filter
            stats['visibility_mode'] = visibility_mode if enable_visibility_filter else "off"
            
            # 添加过滤统计
            if enable_visibility_filter:
                stats['filter_statistics'] = ui_scanner.get_visibility_filter_stats()
            
            return {
                "success": True,
                "query": {
                    "grid_positions": grid_positions,
                    "name_contains": name_contains,
                    "control_types": control_types,
                    "min_size": f"{min_width}x{min_height}",
                    "sort_by": sort_by,
                    "visibility_filter": enable_visibility_filter,
                    "visibility_mode": visibility_mode
                },
                "result_count": len(results),
                "statistics": stats,
                "elements": results[:50]  # 限制返回数量
            }
        
        except Exception as e:
            logger.error(f"Error filtering UI elements: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def build_selector_for_element(
        element_index: int,
        grid_position: Optional[str] = None,
        element_name: Optional[str] = None,
        enable_visibility_filter: bool = True
    ) -> Dict[str, Any]:
        """
        为指定元素构建 tdSelector 字符串
        
        Args:
            element_index: 元素索引（在过滤后的列表中）
            grid_position: 可选，指定网格位置来定位元素
            element_name: 可选，指定元素名称来定位元素
            enable_visibility_filter: 是否启用可见性过滤，默认 True
                - 启用时只从可见元素中选择，避免选中被遮挡的后台元素
        
        Returns:
            构建好的 selector 字符串
        
        Example:
            >>> # 先过滤出候选元素
            >>> filtered = filter_ui_elements(grid_positions=['左中'], name_contains='搜')
            >>> # 然后为第 0 个元素构建 selector
            >>> selector_info = build_selector_for_element(element_index=0)
        """
        scanner = scanner_ref.get('scanner')
        grid_manager = scanner_ref.get('grid_manager')
        
        if not scanner or not grid_manager:
            return {
                "success": False,
                "error": "Scanner not initialized"
            }
        
        try:
            from core.ui_tree_scanner import UITreeScanner
            from core.semantic_filter import SelectorBuilder
            
            # 扫描 UI 树（带可见性过滤）
            ui_scanner = UITreeScanner(
                scanner.root_element, 
                grid_manager,
                enable_visibility_filter=enable_visibility_filter
            )
            ui_scanner.scan_full_tree(max_depth=15)
            all_elements = ui_scanner.get_sorted_elements(deduplicate=False)
            
            # 定位元素
            target_elem = None
            
            if grid_position is not None and element_name is not None:
                # 通过网格位置和名称定位
                for elem in all_elements:
                    if elem.grid_position == grid_position and elem.name == element_name:
                        target_elem = elem
                        break
            else:
                # 通过索引定位
                if 0 <= element_index < len(all_elements):
                    target_elem = all_elements[element_index]
            
            if not target_elem:
                return {
                    "success": False,
                    "error": "Element not found with given criteria",
                    "visibility_filter_enabled": enable_visibility_filter
                }
            
            # 构建 selector
            selector_str = SelectorBuilder.from_element(target_elem)
            
            # 获取窗口标题
            window_title = getattr(scanner.root_element, 'Name', '')
            full_selector = SelectorBuilder.from_semantic_match(target_elem, window_title)
            
            return {
                "success": True,
                "element": {
                    "name": target_elem.name,
                    "control_type": target_elem.control_type,
                    "grid_position": target_elem.grid_position,
                    "bounding_rect": list(target_elem.bounding_rect)
                },
                "selector": {
                    "simple": selector_str,
                    "full_with_window": full_selector
                },
                "visibility_filter_enabled": enable_visibility_filter
            }
        
        except Exception as e:
            logger.error(f"Error building selector: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scan_region(
        region: str = None,
        grid_id: int = None,
        search_depth: int = 2,
        use_ui_tree: bool = True,  # 使用 UI 树扫描
        enable_visibility_filter: bool = True,  # 启用可见性过滤
        visibility_mode: str = "balanced"  # 新增：过滤模式
    ) -> Dict[str, Any]:
        """
        扫描指定区域的 UI 元素
        
        支持自然语言方位描述（左上、中间、右下等）或宫格编号。
        默认使用 9 宫格布局，并启用可见性过滤（平衡模式）。
        
        Args:
            region: 自然语言方位描述，如 '左上'、'中间'、'右下'、'上面'、'左侧' 等
            grid_id: 宫格编号 (0-8)，与 region 二选一
            search_depth: 搜索深度，默认 2
            use_ui_tree: 是否使用 UI 树扫描（推荐），默认 True
            enable_visibility_filter: 是否启用可见性过滤，默认 True
                - 启用时排除被遮挡、离屏、不在前景层的元素
                - 确保"左边的按钮"等指令只匹配用户肉眼可见的元素
                - 特别适用于微信等复杂应用，避免误选中被侧边栏遮挡的后台元素
            visibility_mode: 可见性过滤模式，默认 "balanced"
                - "off": 不过滤
                - "balanced": 平衡模式（推荐）
                - "strict": 严格模式（可能过滤过严）
        
        Returns:
            区域内的元素列表和统计信息
        
        Example:
            >>> scan_region(region="左上")
            {
                "region": "左上",
                "grid_id": 0,
                "element_count": 5,
                "elements": [
                    {"name": "微信", "control_type": "ButtonControl"},
                    ...
                ]
            }
            
            >>> scan_region(grid_id=4)  # 中间
            {
                "grid_id": 4,
                "position_name": "中间",
                "element_count": 8,
                "elements": [...]
            }
            
            >>> # 使用严格模式
            >>> scan_region(region="左侧", visibility_mode="strict")
            
            >>> # 禁用可见性过滤，获取所有元素（包括被遮挡的）
            >>> scan_region(region="左侧", enable_visibility_filter=False)
        """
        from core.grid_manager import GridManager
        from core.ui_tree_scanner import UITreeScanner
        
        scanner = scanner_ref.get('scanner')
        grid_manager = scanner_ref.get('grid_manager')
        
        if not scanner or not grid_manager:
            return {
                "success": False,
                "error": "Scanner not initialized. Call set_focus_window first."
            }
        
        try:
            # 确定要扫描的宫格
            target_grids = []
            
            if grid_id is not None:
                # 使用宫格编号
                grid = grid_manager.get_grid_by_id(grid_id)
                target_grids.append(grid)
            elif region:
                # 使用自然语言描述
                # 先尝试精确匹配单个宫格
                grid = grid_manager.get_grid_by_position_name(region)
                if grid:
                    target_grids.append(grid)
                else:
                    # 尝试区域匹配（可能返回多个宫格）
                    target_grids = grid_manager.get_grids_by_region_description(region)
                
                if not target_grids:
                    return {
                        "success": False,
                        "error": f"Unknown region: '{region}'. Use terms like 左上，中间，右下，上面，左侧 etc."
                    }
            else:
                return {
                    "success": False,
                    "error": "Please specify either 'region' or 'grid_id'"
                }
            
            # 扫描方法选择
            if use_ui_tree:
                # 新方法：UI 树扫描 + 宫格过滤（带可见性过滤）
                ui_scanner = UITreeScanner(
                    scanner.root_element, 
                    grid_manager,
                    enable_visibility_filter=enable_visibility_filter,
                    visibility_mode=visibility_mode
                )
                ui_scanner.scan_full_tree(max_depth=search_depth + 10)
                
                # 过滤出目标宫格的元素
                target_grid_ids = {g.id for g in target_grids}
                
                # 去重
                sorted_elements = ui_scanner.get_sorted_elements(deduplicate=True)
                final_elements = [
                    e for e in sorted_elements 
                    if e.grid_id in target_grid_ids
                ]
                
                # 转换为字典格式
                element_dicts = [e.to_dict() for e in final_elements]
                
                # 获取过滤统计
                filter_stats = ui_scanner.get_visibility_filter_stats() if enable_visibility_filter else None
                
            else:
                # 旧方法：scan_grid
                all_elements = []
                for grid in target_grids:
                    elements = scanner.scan_grid(grid.to_tuple(), search_depth=search_depth)
                    for elem in elements:
                        elem_dict = elem.to_dict()
                        elem_dict['grid_id'] = grid.id
                        elem_dict['position_name'] = grid_manager.get_position_name_by_id(grid.id)
                        all_elements.append(elem_dict)
                
                element_dicts = all_elements
                final_elements = element_dicts
                filter_stats = None
            
            # 使用格式化工具构建响应
            from core.result_formatter import format_tool_response, build_summary
            
            # 基础响应数据
            base_data = {
                "region_query": region if region else f"grid_{grid_id}",
                "scanned_grids": [
                    {
                        "id": g.id,
                        "position_name": grid_manager.get_position_name_by_id(g.id)
                    }
                    for g in target_grids
                ],
                "search_depth": search_depth,
                "use_ui_tree": use_ui_tree,
                "visibility_filter_enabled": enable_visibility_filter,
                "visibility_mode": visibility_mode if enable_visibility_filter else "off"
            }
            
            # 添加过滤统计
            message = None
            if enable_visibility_filter and filter_stats:
                base_data["visibility_filter_stats"] = filter_stats
                message = f"Filtered out {filter_stats['filtered_out']} invisible elements (mode={visibility_mode})"
            
            # 使用格式化工具（自动添加 summary 和截断）
            result = format_tool_response(
                success=True,
                data=base_data,
                message=message,
                elements=element_dicts,
                include_summary=True,
                auto_truncate=True,
                max_elements=50  # 增加到 50 个
            )
            
            return result
        
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error scanning region: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def highlight_element(
        selector_string: str,
        duration: float = 3.0,
        color: str = 'red'
    ) -> Dict[str, Any]:
        """
        在屏幕上高亮显示 UI 元素
        
        使用 tkinter 创建半透明覆盖层，在元素周围绘制彩色边框。
        支持跟随元素移动（如果元素位置变化）。
        
        Args:
            selector_string: tdSelector 语法字符串
                示例："[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜')] }]"
            duration: 高亮持续时间（秒），默认 3 秒
            color: 边框颜色，支持 'red', 'green', 'blue', 'yellow', 'orange'
        
        Returns:
            高亮结果和元素位置信息
        
        Example:
            >>> highlight_element(
            ...     selector_string="[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜')] }]",
            ...     duration=5.0,
            ...     color='red'
            ... )
            {
                "success": true,
                "element": {
                    "name": "搜一搜",
                    "bounding_rect": [16, 513, 91, 558],
                    "center_point": [53, 535]
                },
                "highlight_info": {
                    "duration": 5.0,
                    "color": "red",
                    "follow_mode": true
                }
            }
        """
        from core.screen_highlighter import highlight_element as highlight
        
        scanner = scanner_ref.get('scanner')
        
        if not scanner:
            return {
                "success": False,
                "error": "Scanner not initialized"
            }
        
        try:
            # 查找元素
            element = scanner.find_by_selector(selector_string, timeout=5.0)
            
            if not element:
                return {
                    "success": False,
                    "error": "Element not found",
                    "selector": selector_string
                }
            
            # 获取位置
            rect = element.BoundingRectangle
            rect_tuple = (rect.left, rect.top, rect.right, rect.bottom)
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            # 高亮元素
            highlight(element, duration=duration, color=color, follow=True)
            
            return {
                "success": True,
                "element": {
                    "name": getattr(element, 'Name', ''),
                    "control_type": getattr(element, 'ControlTypeName', ''),
                    "bounding_rect": list(rect_tuple),
                    "center_point": [center_x, center_y]
                },
                "highlight_info": {
                    "duration": duration,
                    "color": color,
                    "follow_mode": True
                }
            }
        
        except Exception as e:
            logger.error(f"Error highlighting element: {e}")
            return {
                "success": False,
                "error": str(e),
                "selector": selector_string
            }
    
    @mcp.tool()
    async def list_grids(
        show_elements: bool = False
    ) -> Dict[str, Any]:
        """
        列出所有宫格及其元素
        
        Args:
            show_elements: 是否显示元素详情
        
        Returns:
            所有宫格的信息
        """
        scanner = scanner_ref.get('scanner')
        grid_manager = scanner_ref.get('grid_manager')
        
        if not scanner or not grid_manager:
            return {
                "error": "Scanner not initialized"
            }
        
        try:
            grids = grid_manager.get_all_grids()
            result = {
                "total_grids": len(grids),
                "window_rect": list(scanner.get_window_rect()),
                "grids": []
            }
            
            for grid in grids:
                grid_info = {
                    "grid_id": grid.id,
                    "rect": [grid.left, grid.top, grid.right, grid.bottom],
                    "center": list(grid.center),
                    "size": [grid.width, grid.height]
                }
                
                if show_elements:
                    elements = scanner.scan_grid(grid.to_tuple())
                    grid_info["element_count"] = len(elements)
                    grid_info["elements"] = [
                        {
                            "name": elem.name,
                            "control_type": elem.control_type
                        }
                        for elem in elements[:10]  # 最多显示 10 个
                    ]
                
                result["grids"].append(grid_info)
            
            return result
        
        except Exception as e:
            logger.error(f"Error listing grids: {e}")
            return {
                "error": str(e)
            }
    
    @mcp.tool()
    async def set_focus_point(
        x: int,
        y: int
    ) -> Dict[str, Any]:
        """
        设置焦点为指定坐标所在的宫格
        
        Args:
            x: 屏幕 X 坐标
            y: 屏幕 Y 坐标
        
        Returns:
            设置的焦点宫格信息
        """
        scanner = scanner_ref.get('scanner')
        
        if not scanner:
            return {
                "error": "Scanner not initialized"
            }
        
        try:
            grid_manager = scanner_ref['grid_manager']
            grid_id = scanner.set_focus_by_grid(grid_manager.get_grid_by_position(x, y).id)
            grid = grid_manager.get_grid_by_id(grid_id)
            
            return {
                "success": True,
                "focus_grid_id": grid_id,
                "point": [x, y],
                "grid_rect": [grid.left, grid.top, grid.right, grid.bottom],
                "grid_center": list(grid.center)
            }
        
        except Exception as e:
            logger.error(f"Error setting focus point: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return set_focus_window, pick_grid_element, list_grids, set_focus_point
