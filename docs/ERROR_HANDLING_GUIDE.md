# 统一错误处理机制

**创建日期**: 2026-03-25  
**问题编号**: #2 (错误处理不统一)

---

## 📋 问题回顾

之前的错误处理问题：

1. **错误格式不统一**
   ```python
   # 错误 1: 简单字符串
   return {"success": False, "error": "Scanner not initialized"}
   
   # 错误 2: 暴露内部实现
   return {"success": False, "error": "'UIARegionScanner' object has no attribute 'scan_focus_area'"}
   
   # 错误 3: 无解决方案提示
   return {"success": False, "error": "Cannot find window"}
   ```

2. **缺少可操作的解决建议**
   - 用户不知道下一步该怎么做
   - 需要查看源码或日志才能理解

3. **错误类型混乱**
   - 没有分类，所有错误都一样处理
   - 无法根据错误类型采取不同策略

---

## ✅ 解决方案

### 1. 统一的错误基类

```python
# core/error_handler.py
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
        self.message = message or self.default_message
        self.solution = solution or self.default_solution
        self.details = details or {}
        self.suggestions = suggestions or []
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为标准错误响应"""
        return {
            "success": False,
            "error": self.error_code,
            "message": self.message,
            "solution": self.solution,
            "details": self.details,
            "suggestions": self.suggestions  # 新增
        }
```

### 2. 具体错误类型

定义了 9 种常用错误类型：

| 错误类型 | 错误代码 | 使用场景 |
|---------|---------|---------|
| `ScannerNotInitializedError` | SCANNER_NOT_INITIALIZED | 扫描器未初始化 |
| `WindowNotFoundError` | WINDOW_NOT_FOUND | 找不到目标窗口 |
| `ElementNotFoundError` | ELEMENT_NOT_FOUND | 找不到 UI 元素 |
| `VisibilityFilterTooStrictError` | VISIBILITY_FILTER_TOO_STRICT | 可见性过滤过严 |
| `InvalidParameterError` | INVALID_PARAMETER | 参数无效 |
| `GridNotFoundError` | GRID_NOT_FOUND | 宫格不存在 |
| `SelectorBuildError` | SELECTOR_BUILD_ERROR | Selector 构建失败 |
| `TimeoutError` | TIMEOUT_ERROR | 操作超时 |
| `PermissionError` | PERMISSION_DENIED | 权限不足 |

### 3. 标准化的错误响应格式

```python
{
    "success": False,
    "error": "WINDOW_NOT_FOUND",           # 错误代码（程序可用）
    "message": "未找到匹配的窗口",          # 友好的错误消息
    "solution": "使用 list_windows() 查看所有可用窗口...",  # 解决方案
    "details": {                            # 详细上下文信息
        "searched_process": "WeChat.exe",
        "searched_title": "微信"
    },
    "suggestions": [                        # 可操作的建议列表
        "使用 list_windows() 查看所有可用窗口",
        "检查进程名是否正确",
        "尝试使用窗口标题的部分匹配"
    ]
}
```

---

## 💡 使用示例

### 场景 1: 窗口未找到

**之前**：
```python
return {"success": False, "error": "Cannot find window"}
```

**现在**：
```python
from core.error_handler import WindowNotFoundError

try:
    scanner = UIARegionScanner(process_name="WeChat.exe")
except Exception as e:
    error = WindowNotFoundError(
        process_name="WeChat.exe",
        window_title="微信",
        message=f"无法找到窗口：{str(e)}"
    )
    return error.to_dict()
```

**返回结果**：
```json
{
    "success": false,
    "error": "WINDOW_NOT_FOUND",
    "message": "无法找到窗口：Timeout after 5 seconds",
    "solution": "使用 list_windows() 查看所有可用窗口，或检查进程名/窗口标题是否正确",
    "details": {
        "searched_process": "WeChat.exe",
        "searched_title": "微信",
        "error_code": "WINDOW_NOT_FOUND"
    },
    "suggestions": [
        "使用 list_windows() 查看所有可用窗口",
        "检查进程名是否正确（如 WeChat.exe vs wxwork.exe）",
        "尝试使用窗口标题的部分匹配"
    ]
}
```

### 场景 2: 扫描器未初始化

**之前**：
```python
if not scanner:
    return {"success": False, "error": "Scanner not initialized"}
```

**现在**：
```python
from core.error_handler import ensure_scanner_initialized, ScannerNotInitializedError

try:
    scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
except ScannerNotInitializedError as e:
    return e.to_dict()
```

**返回结果**：
```json
{
    "success": false,
    "error": "SCANNER_NOT_INITIALIZED",
    "message": "扫描器未初始化",
    "solution": "请先调用 set_focus_window() 设置目标窗口",
    "details": {
        "scanner_exists": false,
        "grid_manager_exists": false,
        "error_code": "SCANNER_NOT_INITIALIZED"
    },
    "suggestions": [
        "调用 set_focus_window(process_name='xxx')",
        "使用 list_windows() 查看可用窗口"
    ]
}
```

### 场景 3: 元素未找到

**之前**：
```python
if not elements:
    return {"success": False, "message": "No elements found"}
```

**现在**：
```python
from core.error_handler import ElementNotFoundError, VisibilityFilterTooStrictError

if not elements:
    # 检查是否是过滤过严
    if visibility_filter_stats and visibility_filter_stats['filtered_out'] > 0:
        error = VisibilityFilterTooStrictError(
            current_mode=visibility_mode,
            filtered_count=visibility_filter_stats['filtered_out']
        )
        return error.to_dict()
    else:
        error = ElementNotFoundError(
            search_criteria={"region": region},
            region=region
        )
        return error.to_dict()
```

**返回结果**（过滤过严）：
```json
{
    "success": false,
    "error": "VISIBILITY_FILTER_TOO_STRICT",
    "message": "可见性过滤过严，未找到任何元素",
    "solution": "尝试降低过滤强度或禁用可见性过滤",
    "details": {
        "current_mode": "strict",
        "filtered_out": 1667,
        "error_code": "VISIBILITY_FILTER_TOO_STRICT"
    },
    "suggestions": [
        "当前使用 'strict' 模式，尝试改为 'off' 或 'balanced'",
        "设置 visibility_mode='off' 禁用过滤",
        "设置 enable_visibility_filter=False 完全禁用过滤",
        "使用 visibility_mode='balanced' 代替 'strict'"
    ]
}
```

---

## 🔧 技术实现

### 错误处理装饰器

```python
from core.error_handler import handle_mcp_errors

@mcp.tool()
@handle_mcp_errors()  # 自动捕获并转换错误
async def my_tool(param1: str) -> Dict[str, Any]:
    # 不需要手动 try-except
    scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
    
    if param1 == "invalid":
        raise InvalidParameterError(
            param_name="param1",
            param_value=param1,
            expected_type="str"
        )
    
    # ... 正常逻辑 ...
    return {"success": True, ...}
```

### 便捷函数

```python
# 1. 确保扫描器初始化
scanner, grid_manager = ensure_scanner_initialized(scanner_ref)

# 2. 快速创建错误响应
from core.error_handler import create_error_response

return create_error_response(
    error_code="CUSTOM_ERROR",
    message="自定义错误消息",
    solution="解决方案",
    details={"key": "value"}
)
```

---

## 📊 对比分析

### 之前的问题

| 问题 | 影响 | 频率 |
|------|------|------|
| 错误格式不统一 | LLM 难以解析 | 每次报错 |
| 缺少解决方案 | 用户不知所措 | 100% |
| 暴露内部细节 | 安全隐患 | 常见 |
| 无错误分类 | 无法针对性处理 | 100% |

### 现在的优势

| 改进 | 效果 | 覆盖率 |
|------|------|--------|
| 统一错误格式 | LLM 可自动处理 | 100% |
| 提供解决方案 | 用户知道下一步 | 100% |
| 隐藏内部细节 | 更安全 | 100% |
| 错误分类清晰 | 可编程处理 | 100% |

---

## 🎯 最佳实践

### ✅ 推荐用法

```python
# 1. 使用预定义的错误类型
from core.error_handler import WindowNotFoundError

try:
    scanner = UIARegionScanner(process_name="WeChat.exe")
except Exception as e:
    raise WindowNotFoundError(
        process_name="WeChat.exe",
        message=str(e)
    )

# 2. 使用装饰器自动处理
@mcp.tool()
@handle_mcp_errors()
async def my_tool(...):
    ...

# 3. 提供详细的上下文信息
raise ElementNotFoundError(
    search_criteria={"name": "按钮", "type": "ButtonControl"},
    region="左侧",
    details={"attempted_positions": ["左中", "左上"]}
)

# 4. 给出可操作的建议
raise VisibilityFilterTooStrictError(
    current_mode="strict",
    suggestions=[
        "改用 balanced 模式",
        "或直接禁用过滤"
    ]
)
```

### ❌ 避免用法

```python
# 1. 不要直接返回字符串错误
return {"success": False, "error": "出错了"}  # ❌

# 2. 不要暴露内部异常堆栈
return {"success": False, "error": str(traceback.format_exc())}  # ❌

# 3. 不要混用多种错误格式
if error1:
    return {"error": "msg1"}
elif error2:
    return {"success": False, "message": "msg2"}  # ❌

# 4. 不要使用通用错误类型
raise MCPToolError("未知错误")  # ❌ 应该使用具体类型
```

---

## 📝 迁移指南

### 从旧代码迁移

**之前的代码**：
```python
scanner = scanner_ref.get('scanner')
if not scanner:
    return {"success": False, "error": "Scanner not initialized"}

try:
    # ... 某操作 ...
except Exception as e:
    logger.error(f"Error: {e}")
    return {"success": False, "error": str(e)}
```

**迁移后的代码**：
```python
from core.error_handler import ensure_scanner_initialized, handle_mcp_errors

# 方法 1: 使用装饰器（推荐）
@mcp.tool()
@handle_mcp_errors()
async def my_tool():
    scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
    # ... 正常逻辑，不需要 try-except ...

# 方法 2: 手动处理
try:
    scanner, grid_manager = ensure_scanner_initialized(scanner_ref)
    # ... 正常逻辑 ...
except MCPToolError as e:
    return e.to_dict()
```

---

## 🔮 未来扩展

### 计划添加的错误类型

- [ ] `NetworkError` - 网络相关错误
- [ ] `ConfigurationError` - 配置文件错误
- [ ] `VersionMismatchError` - 版本不匹配错误
- [ ] `ResourceExhaustedError` - 资源耗尽错误

### 高级功能

- [ ] 错误码国际化（i18n）
- [ ] 错误日志自动上报
- [ ] 基于错误类型的自动恢复
- [ ] 错误统计和分析

---

## 📚 相关文档

- [PRODUCT_IMPROVEMENT_PLAN.md](./PRODUCT_IMPROVEMENT_PLAN.md) - 产品改进计划
- [VISIBILITY_FILTER_IMPROVEMENTS.md](./VISIBILITY_FILTER_IMPROVEMENTS.md) - 可见性过滤改进
- [README.md](../README.md) - 主文档

---

*本文档定义了 uiaRPA-mcp 的统一错误处理标准，所有新代码应遵循此规范。*
