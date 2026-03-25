"""
MCP 工具统一错误处理模块

提供标准化的错误类型、错误格式和友好的错误提示。
"""
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MCPToolError(Exception):
    """MCP 工具统一错误基类"""
    
    error_code: str = "UNKNOWN_ERROR"
    default_message: str = "发生未知错误"
    default_solution: str = "请查看文档或联系开发者"
    
    def __init__(
        self, 
        message: Optional[str] = None,
        solution: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        """
        初始化 MCP 工具错误
        
        Args:
            message: 错误消息（可选，使用默认值如果未提供）
            solution: 解决方案（可选）
            details: 详细上下文信息（可选）
            suggestions: 建议的操作列表（可选）
        """
        self.message = message or self.default_message
        self.solution = solution or self.default_solution
        self.details = details or {}
        self.suggestions = suggestions or []
        
        # 添加错误代码到详细信息
        self.details['error_code'] = self.error_code
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（用于 MCP 返回）
        
        Returns:
            标准化的错误响应字典
        """
        result = {
            "success": False,
            "error": self.error_code,
            "message": self.message,
            "solution": self.solution,
            "details": self.details
        }
        
        if self.suggestions:
            result["suggestions"] = self.suggestions
        
        return result
    
    def log_error(self, level: str = "error"):
        """记录错误日志"""
        log_func = getattr(logger, level, logger.error)
        log_func(f"[{self.error_code}] {self.message}")
        if self.details:
            logger.debug(f"Error details: {self.details}")


# ============================================================================
# 具体错误类型定义
# ============================================================================

class ScannerNotInitializedError(MCPToolError):
    """扫描器未初始化错误"""
    error_code = "SCANNER_NOT_INITIALIZED"
    default_message = "扫描器未初始化"
    default_solution = "请先调用 set_focus_window() 设置目标窗口"
    
    def __init__(self, **kwargs):
        super().__init__(
            suggestions=["调用 set_focus_window(process_name='xxx')", "使用 list_windows() 查看可用窗口"],
            **kwargs
        )


class WindowNotFoundError(MCPToolError):
    """窗口未找到错误"""
    error_code = "WINDOW_NOT_FOUND"
    default_message = "未找到匹配的窗口"
    default_solution = "使用 list_windows() 查看所有可用窗口，或检查进程名/窗口标题是否正确"
    
    def __init__(self, process_name: Optional[str] = None, window_title: Optional[str] = None, **kwargs):
        details = {
            "searched_process": process_name,
            "searched_title": window_title
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            "使用 list_windows() 查看所有可用窗口",
            "检查进程名是否正确（如 WeChat.exe vs wxwork.exe）",
            "尝试使用窗口标题的部分匹配"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class ElementNotFoundError(MCPToolError):
    """元素未找到错误"""
    error_code = "ELEMENT_NOT_FOUND"
    default_message = "未找到匹配的 UI 元素"
    default_solution = "尝试放宽搜索条件或使用 get_ui_tree_data() 查看完整元素列表"
    
    def __init__(
        self,
        search_criteria: Optional[Dict[str, Any]] = None,
        region: Optional[str] = None,
        **kwargs
    ):
        details = {
            "search_criteria": search_criteria or {},
            "region": region
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            "使用 get_ui_tree_data() 查看当前所有可用元素",
            "放宽过滤条件（如移除 name_contains 或 control_types）",
            "尝试不同的 grid_positions",
            "检查是否需要禁用可见性过滤（enable_visibility_filter=False）"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class VisibilityFilterTooStrictError(MCPToolError):
    """可见性过滤过严错误"""
    error_code = "VISIBILITY_FILTER_TOO_STRICT"
    default_message = "可见性过滤过严，未找到任何元素"
    default_solution = "尝试降低过滤强度或禁用可见性过滤"
    
    def __init__(
        self,
        current_mode: str = "balanced",
        filtered_count: int = 0,
        **kwargs
    ):
        details = {
            "current_mode": current_mode,
            "filtered_out": filtered_count
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            f"当前使用 '{current_mode}' 模式，尝试改为 'off' 或 'balanced'",
            "设置 visibility_mode='off' 禁用过滤",
            "设置 enable_visibility_filter=False 完全禁用过滤",
            "使用 visibility_mode='balanced' 代替 'strict'"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class InvalidParameterError(MCPToolError):
    """无效参数错误"""
    error_code = "INVALID_PARAMETER"
    default_message = "参数无效或格式错误"
    default_solution = "检查参数类型、取值范围和必填项"
    
    def __init__(
        self,
        param_name: str,
        param_value: Any = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        details = {
            "invalid_parameter": param_name,
            "provided_value": str(param_value),
            "expected_type": expected_type
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            f"检查参数 '{param_name}' 的类型是否正确",
            "查看 API 文档了解参数的取值范围",
            "确保必填参数已提供"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class GridNotFoundError(MCPToolError):
    """宫格未找到错误"""
    error_code = "GRID_NOT_FOUND"
    default_message = "指定的宫格不存在"
    default_solution = "检查宫格 ID（0-8）或位置名称是否正确"
    
    def __init__(
        self,
        grid_id: Optional[int] = None,
        position_name: Optional[str] = None,
        **kwargs
    ):
        details = {
            "searched_grid_id": grid_id,
            "searched_position": position_name,
            "valid_grid_ids": list(range(9)),
            "valid_positions": ["左上", "上中", "右上", "左中", "中间", "右中", "左下", "下中", "右下"]
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            "宫格 ID 范围：0-8",
            "有效的位置名称：左上，上中，右上，左中，中间，右中，左下，下中，右下",
            "使用 list_grids() 查看所有宫格信息"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class SelectorBuildError(MCPToolError):
    """Selector 构建错误"""
    error_code = "SELECTOR_BUILD_ERROR"
    default_message = "无法构建有效的 Selector"
    default_solution = "检查元素信息是否完整，或尝试其他定位方式"
    
    def __init__(
        self,
        element_info: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        details = {
            "element_info": element_info or {},
            "failure_reason": reason
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            "确保元素包含必要的信息（name, control_type, bounding_rect）",
            "尝试使用 grid_position + element_name 定位",
            "使用 build_selector_for_element() 的默认索引定位"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class TimeoutError(MCPToolError):
    """超时错误"""
    error_code = "TIMEOUT_ERROR"
    default_message = "操作超时"
    default_solution = "增加 timeout 参数或检查目标应用是否响应"
    
    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        **kwargs
    ):
        details = {
            "failed_operation": operation,
            "timeout_seconds": timeout_seconds
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            f"操作 '{operation}' 在 {timeout_seconds} 秒内未完成",
            "增加 timeout 参数值",
            "检查目标应用是否卡死或无响应",
            "尝试重新设置聚焦窗口"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


class PermissionError(MCPToolError):
    """权限错误"""
    error_code = "PERMISSION_DENIED"
    default_message = "没有足够的权限执行操作"
    default_solution = "以管理员身份运行或检查 UAC 设置"
    
    def __init__(
        self,
        required_permission: str,
        **kwargs
    ):
        details = {
            "required_permission": required_permission
        }
        details.update(kwargs.get('details', {}))
        
        suggestions = [
            "以管理员身份运行 Python/MCP 服务",
            "检查 Windows UAC（用户账户控制）设置",
            "确保有权限访问目标应用程序"
        ]
        
        super().__init__(details=details, suggestions=suggestions, **kwargs)


# ============================================================================
# 错误处理装饰器
# ============================================================================

def handle_mcp_errors(default_return_on_error: bool = True):
    """
    MCP 工具错误处理装饰器
    
    自动捕获 MCPToolError 并转换为标准返回格式
    
    Args:
        default_return_on_error: 错误时是否返回标准错误格式（默认 True）
    
    Example:
        @mcp.tool()
        @handle_mcp_errors()
        async def my_tool(param1: str) -> Dict[str, Any]:
            ...
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            
            except MCPToolError as e:
                e.log_error()
                if default_return_on_error:
                    return e.to_dict()
                raise
            
            except Exception as e:
                # 未预期的异常 - 转换为通用错误
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                
                unknown_error = MCPToolError(
                    message=f"未预期的错误：{str(e)}",
                    solution="请查看日志文件或联系开发者",
                    details={
                        "exception_type": type(e).__name__,
                        "function": func.__name__
                    }
                )
                
                if default_return_on_error:
                    return unknown_error.to_dict()
                raise
        
        return wrapper
    return decorator


# ============================================================================
# 便捷函数
# ============================================================================

def create_error_response(
    error_code: str,
    message: str,
    solution: Optional[str] = None,
    details: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    快速创建错误响应（不抛出异常）
    
    Args:
        error_code: 错误代码
        message: 错误消息
        solution: 解决方案
        details: 详细信息
    
    Returns:
        标准化的错误响应字典
    """
    return {
        "success": False,
        "error": error_code,
        "message": message,
        "solution": solution or "请查看文档或联系开发者",
        "details": details or {}
    }


def ensure_scanner_initialized(scanner_ref: dict) -> tuple:
    """
    确保扫描器已初始化的辅助函数
    
    Args:
        scanner_ref: 扫描器引用字典
    
    Returns:
        (scanner, grid_manager) 元组
    
    Raises:
        ScannerNotInitializedError: 如果扫描器未初始化
    """
    scanner = scanner_ref.get('scanner')
    grid_manager = scanner_ref.get('grid_manager')
    
    if not scanner or not grid_manager:
        raise ScannerNotInitializedError(
            details={"scanner_exists": scanner is not None, "grid_manager_exists": grid_manager is not None}
        )
    
    return scanner, grid_manager
