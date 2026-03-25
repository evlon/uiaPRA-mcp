# uiaRPA-mcp 产品改进计划

基于实际使用体验收集的改进建议和实施计划。

**创建日期**: 2026-03-25  
**优先级**: P0 (紧急) - P3 (可选)

---

## 📋 改进建议总览

| 编号 | 类别 | 问题描述 | 优先级 | 状态 |
|------|------|---------|--------|------|
| #1 | 窗口查找与聚焦 | set_focus_window 找不到微信窗口 | P0 | 📝 计划中 |
| #2 | 错误处理 | 报错信息不统一 | P0 | 📝 计划中 |
| #3 | 扫描器状态管理 | 接口依赖关系不明确 | P1 | 📝 计划中 |
| #4 | 可见性过滤 | 默认过滤过严返回 0 元素 | P0 | 🔄 实施中 |
| #5 | 返回结果优化 | 缺少 summary 和自动截断 | P1 | 📝 计划中 |
| #6 | 调试辅助 | 缺少可视化工具 | P2 | 📝 计划中 |
| #7 | 复杂应用支持 | 微信自绘 UI 支持弱 | P1 | 📝 计划中 |

---

## 🔍 详细问题分析

### #1 窗口查找与聚焦

**问题现象**:
```python
# set_focus_window 找不到微信窗口，但桌面能扫描到微信元素
await set_focus_window(process_name="WeChat.exe")
# ❌ Error: Cannot find window
```

**根本原因**:
- 微信可能使用多进程架构，主窗口句柄不易获取
- 窗口标题动态变化（如显示联系人名称）
- 某些窗口可能是子窗口或弹出窗口

**解决方案**:

#### 1.1 增加 `list_windows()` 接口 ✅ 计划实现

```python
@mcp.tool()
async def list_windows(
    process_name: Optional[str] = None,
    window_title_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    列出所有可用的窗口供选择
    
    Args:
        process_name: 可选，按进程名过滤（如 "WeChat.exe"）
        window_title_pattern: 可选，按窗口标题正则匹配
    
    Returns:
        {
            "success": True,
            "windows": [
                {
                    "window_id": "hwnd_12345",
                    "process_name": "WeChat.exe",
                    "title": "微信",
                    "rect": [100, 100, 800, 600],
                    "is_visible": True,
                    "is_topmost": False
                },
                ...
            ],
            "total_count": 5
        }
    """
```

#### 1.2 改进 `set_focus_window()` 的模糊匹配

```python
@mcp.tool()
async def set_focus_window(
    process_name: str = None,
    window_title: str = None,
    fuzzy_match: bool = True  # 新增参数
) -> Dict[str, Any]:
    """
    设置目标扫描窗口（增强版）
    
    改进:
    - 支持进程名 + 窗口标题组合搜索
    - 窗口不存在时返回候选列表
    - 支持模糊匹配（Levenshtein 距离）
    """
```

#### 1.3 智能窗口推荐

当找不到精确匹配的窗口时，返回最相似的 3-5 个候选窗口：

```python
{
    "success": False,
    "error": "No exact match found for 'WeChat.exe'",
    "suggestions": [
        {
            "process_name": "WeChat.exe",
            "title": "微信",
            "similarity": 0.95,
            "reason": "Same process name"
        },
        {
            "process_name": "WeChatAppEx.exe",
            "title": "小程序窗口",
            "similarity": 0.75,
            "reason": "Related WeChat process"
        }
    ]
}
```

---

### #2 错误处理

**问题现象**:
```python
# 错误 1: 简单报错无解决方案
"Scanner not initialized"

# 错误 2: 内部实现细节暴露
"'UIARegionScanner' object has no attribute 'scan_focus_area'"

# 错误 3: 无上下文信息
"Cannot find window"
```

**解决方案**:

#### 2.1 统一错误格式

```python
class MCPToolError(Exception):
    """MCP 工具统一错误基类"""
    def __init__(self, message: str, solution: str = None, details: dict = None):
        self.message = message
        self.solution = solution or "请联系开发者或查看文档"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "solution": self.solution,
            "details": self.details
        }

# 使用示例
class ScannerNotInitializedError(MCPToolError):
    def __init__(self):
        super().__init__(
            message="扫描器未初始化",
            solution="请先调用 set_focus_window() 设置目标窗口",
            details={"required_tool": "set_focus_window"}
        )

# 在工具中捕获异常
try:
    scanner = scanner_ref.get('scanner')
    if not scanner:
        raise ScannerNotInitializedError()
except MCPToolError as e:
    return {
        "success": False,
        **e.to_dict()
    }
```

#### 2.2 错误类型定义

```python
ERROR_TYPES = {
    "SCANNER_NOT_INITIALIZED": {
        "message": "扫描器未初始化",
        "solution": "请先调用 set_focus_window() 设置目标窗口",
        "http_status": 400
    },
    "WINDOW_NOT_FOUND": {
        "message": "未找到匹配的窗口",
        "solution": "使用 list_windows() 查看所有可用窗口",
        "http_status": 404
    },
    "ELEMENT_NOT_FOUND": {
        "message": "未找到匹配的 UI 元素",
        "solution": "尝试放宽搜索条件或使用 get_ui_tree_data() 查看完整元素列表",
        "http_status": 404
    },
    "VISIBILITY_FILTER_TOO_STRICT": {
        "message": "可见性过滤过严，未找到任何元素",
        "solution": "尝试设置 enable_visibility_filter=False 或调整搜索区域",
        "http_status": 200
    }
}
```

---

### #3 扫描器状态管理

**问题现象**:
- 有时需要先 `set_focus_window()` 才能扫描
- 但 `scan_all_grids` 又不需要
- 用户不清楚各接口的依赖关系

**解决方案**:

#### 3.1 自动初始化扫描器

```python
class ScannerManager:
    """扫描器管理器 - 自动处理初始化"""
    
    def __init__(self):
        self._scanner = None
        self._grid_manager = None
        self._auto_init = True  # 自动初始化标志
    
    def get_scanner(self, auto_create=True):
        """获取扫描器（自动创建如果不存在）"""
        if self._scanner is None and auto_create:
            # 自动使用桌面作为默认扫描目标
            import uiautomation as auto
            self._scanner = UIARegionScanner(
                root_element=auto.GetRootControl()
            )
            logger.info("Auto-initialized scanner with desktop root")
        
        return self._scanner
    
    def ensure_initialized(self):
        """确保扫描器已初始化"""
        if self._scanner is None:
            self.get_scanner(auto_create=True)
```

#### 3.2 明确文档说明依赖关系

```markdown
## API 依赖关系图

```
┌─────────────────────┐
│   set_focus_window  │ ← 必须首先调用（可选，有默认值）
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  get_ui_tree_data   │ ← 可直接调用（使用默认桌面扫描器）
│  filter_ui_elements │
│  scan_region        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ build_selector_for  │ ← 依赖前面的扫描结果
│ highlight_element   │
└─────────────────────┘
```
```

---

### #4 可见性过滤 ⭐ 当前重点

**问题现象**:
```python
# 启用可见性过滤时返回 0 元素
result = await scan_region(region="左侧", enable_visibility_filter=True)
# {"element_count": 0, "elements": []}

# 关闭后正常
result = await scan_region(region="左侧", enable_visibility_filter=False)
# {"element_count": 15, "elements": [...]}
```

**根本原因**:
- 可见性检测过于严格（4 层检查全部通过才认为可见）
- `_is_in_foreground_layer()` 对非顶层窗口误判
- 像素覆盖检测采样点不足

**解决方案**:

#### 4.1 提供三级过滤强度

```python
@mcp.tool()
async def scan_region(
    region: str = None,
    grid_id: int = None,
    visibility_filter: str = "balanced"  # 新增："off" | "balanced" | "strict"
) -> Dict[str, Any]:
    """
    扫描指定区域的 UI 元素
    
    Args:
        visibility_filter: 可见性过滤强度
            - "off": 不过滤（返回所有元素）
            - "balanced": 平衡模式（默认，只检查 IsOffscreen）
            - "strict": 严格模式（4 层检查全开）
    """
```

#### 4.2 改进 VisibilityChecker

```python
class VisibilityChecker:
    def __init__(self, mode: str = "balanced"):
        self.mode = mode
        
        if mode == "off":
            self.checks = []
        elif mode == "balanced":
            # 只检查关键项
            self.checks = [
                self._check_basic_visibility,
                self._is_offscreen
            ]
        elif mode == "strict":
            # 全部检查
            self.checks = [
                self._check_basic_visibility,
                self._is_offscreen,
                self._check_pixel_coverage,
                self._is_in_foreground_layer
            ]
    
    def is_element_visible(self, element) -> bool:
        for check in self.checks:
            if not check(element):
                return False
        return True
```

#### 4.3 添加过滤统计信息

```python
return {
    "success": True,
    "element_count": len(final_elements),
    "filtered_out_count": filtered_count,  # 新增
    "visibility_filter_mode": visibility_filter,  # 新增
    "filter_statistics": {  # 新增详细统计
        "total_scanned": total_scanned,
        "passed_basic_visibility": basic_passed,
        "passed_offscreen": offscreen_passed,
        "passed_pixel_coverage": pixel_passed,
        "passed_foreground_layer": foreground_passed,
        "final_visible": len(final_elements)
    },
    "elements": final_elements[:30]
}
```

#### 4.4 默认配置调整

```python
# mcp_server.py 或 config.yaml
DEFAULT_VISIBILITY FILTER = "balanced"  # 从 "strict" 改为 "balanced"

# 在返回结果中添加提示信息
if filtered_count > 0:
    result["message"] = f"已过滤 {filtered_count} 个不可见元素 (mode={visibility_filter})"
```

---

### #5 返回结果优化

**解决方案**:

#### 5.1 添加 summary 字段

```python
def _build_result_summary(elements: List[dict]) -> dict:
    """构建结果摘要"""
    from collections import Counter
    
    summary = {
        "total_elements": len(elements),
        "by_control_type": {},
        "by_grid_position": {},
        "has_clickable": False,
        "has_input": False
    }
    
    control_types = Counter(e.get('control_type', 'Unknown') for e in elements)
    grid_positions = Counter(e.get('grid_position', 'Unknown') for e in elements)
    
    summary["by_control_type"] = dict(control_types)
    summary["by_grid_position"] = dict(grid_positions)
    
    # 标记特殊元素
    for elem in elements:
        ctrl_type = elem.get('control_type', '')
        if 'Button' in ctrl_type or 'Hyperlink' in ctrl_type:
            summary["has_clickable"] = True
        if 'Edit' in ctrl_type or 'Text' in ctrl_type:
            summary["has_input"] = True
    
    return summary

# 在所有返回结果中添加
result["summary"] = _build_result_summary(final_elements)
```

#### 5.2 大结果集自动截断

```python
MAX_RETURN_ELEMENTS = 50  # 配置项

if len(elements) > MAX_RETURN_ELEMENTS:
    result["truncated"] = True
    result["total_available"] = len(elements)
    result["returned"] = MAX_RETURN_ELEMENTS
    result["message"] = f"结果已截断：显示前 {MAX_RETURN_ELEMENTS} 个，共 {len(elements)} 个元素"
    result["how_to_get_all"] = "使用 include_raw_elements=True 或增加 max_return 参数"
    elements = elements[:MAX_RETURN_ELEMENTS]
else:
    result["truncated"] = False
```

#### 5.3 按应用/窗口分组

```python
@mcp.tool()
async def get_ui_tree_data(
    group_by: str = "grid"  # "grid" | "application" | "window"
) -> Dict[str, Any]:
    """
    获取 UI 树数据（支持多种分组方式）
    
    Args:
        group_by: 分组方式
            - "grid": 按 9 宫格分组（默认）
            - "application": 按应用程序分组
            - "window": 按窗口分组
    """
```

---

### #6 调试辅助

**解决方案**:

#### 6.1 高亮窗口边框

```python
@mcp.tool()
async def highlight_window(
    duration: float = 3.0,
    color: str = 'blue',
    window_id: str = None
) -> Dict[str, Any]:
    """
    高亮显示当前聚焦窗口的边框
    
    Args:
        duration: 持续时间（秒）
        color: 边框颜色
        window_id: 可选，指定窗口 ID（默认使用当前聚焦窗口）
    
    Returns:
        {
            "success": True,
            "window": {...},
            "highlight_info": {...}
        }
    """
```

#### 6.2 屏幕截图

```python
@mcp.tool()
async def snapshot(
    region: str = None,
    save_path: str = None,
    include_ui_overlay: bool = True
) -> Dict[str, Any]:
    """
    截取当前屏幕或指定区域的截图
    
    Args:
        region: 可选，指定区域（如 "左上"）
        save_path: 可选，保存路径
        include_ui_overlay: 是否包含 UI 元素标注覆盖层
    
    Returns:
        {
            "success": True,
            "image_base64": "data:image/png;base64,...",
            "save_path": "/path/to/saved.png",
            "timestamp": "2026-03-25T10:30:00"
        }
    """
```

#### 6.3 增强日志输出

```python
# 在扫描开始时输出详细信息
logger.info(f"""
=== UI 扫描开始 ===
扫描范围：{region or f'Grid {grid_id}'}
可见性过滤：{enable_visibility_filter}
最大深度：{search_depth}
当前聚焦窗口：{current_window_title or 'Desktop'}
==================
""")

# 在返回结果中添加调试信息
result["_debug_info"] = {
    "scan_duration_ms": scan_duration,
    "visibility_filter_applied": enable_visibility_filter,
    "elements_before_filter": before_filter_count,
    "elements_after_filter": after_filter_count,
    "filter_details": filter_stats
}
```

---

### #7 微信等复杂应用支持

**问题分析**:
- 微信使用 Direct2D/DirectWrite 自绘 UI
- 标准 UIA API 只能获取有限的控件信息
- 部分按钮、图标没有 AutomationId 或 Name

**解决方案**:

#### 7.1 图像识别后备方案

```python
class HybridScanner:
    """混合扫描器：UIA + CV"""
    
    def __init__(self):
        self.uia_scanner = UIAScanner()
        self.cv_engine = CVEngine()  # OpenCV / template matching
    
    def find_element(self, description: dict):
        # 优先尝试 UIA
        elements = self.uia_scanner.find(description)
        
        if not elements:
            # UIA 失败，降级到 CV
            logger.info("UIA failed, falling back to CV")
            elements = self.cv_engine.find(description)
        
        return elements
```

#### 7.2 OCR 文本识别

```python
@mcp.tool()
async def scan_with_ocr(
    region: str = None,
    text_pattern: str = None
) -> Dict[str, Any]:
    """
    使用 OCR 扫描区域内的文本
    
    Args:
        region: 扫描区域
        text_pattern: 可选，文本正则匹配
    
    Returns:
        {
            "text_blocks": [
                {
                    "text": "搜一搜",
                    "confidence": 0.98,
                    "bounding_rect": [16, 513, 91, 558]
                },
                ...
            ]
        }
    """
```

#### 7.3 配置混合模式

```yaml
# config.yaml
scanner:
  mode: "hybrid"  # "uia_only" | "cv_only" | "hybrid"
  
  hybrid:
    priority: "uia_first"  # "uia_first" | "cv_first"
    fallback_enabled: true
    cache_enabled: true
  
  cv:
    engine: "opencv"  # "opencv" | "tesseract" | "azure_cv"
    ocr_enabled: true
    template_matching: true
```

---

## 📅 实施计划

### Phase 1: 紧急修复 (Week 1)

- [x] **#4 可见性过滤优化** - 提供三级过滤强度
- [ ] **#2 统一错误处理** - 实现 MCPToolError 体系
- [ ] **#1 窗口查找增强** - 实现 list_windows()

### Phase 2: 用户体验 (Week 2)

- [ ] **#5 返回结果优化** - 添加 summary 和截断
- [ ] **#3 扫描器状态管理** - 自动初始化
- [ ] **#6 调试辅助** - highlight_window(), snapshot()

### Phase 3: 高级功能 (Week 3-4)

- [ ] **#7 复杂应用支持** - 混合扫描器原型
- [ ] 性能优化和缓存机制
- [ ] 完整的文档更新

---

## 📊 进度追踪

| 任务 | 开始日期 | 预计完成 | 实际完成 | 状态 |
|------|---------|---------|---------|------|
| #4 可见性过滤优化 | 2026-03-25 | 2026-03-26 | - | 🔄 实施中 |
| #2 统一错误处理 | 2026-03-26 | 2026-03-27 | - | 📝 计划中 |
| #1 窗口查找增强 | 2026-03-27 | 2026-03-28 | - | 📝 计划中 |
| #5 返回结果优化 | 2026-03-28 | 2026-03-29 | - | 📝 计划中 |
| #3 扫描器状态管理 | 2026-03-29 | 2026-03-30 | - | 📝 计划中 |
| #6 调试辅助 | 2026-03-30 | 2026-03-31 | - | 📝 计划中 |
| #7 复杂应用支持 | 2026-04-01 | 2026-04-05 | - | 📝 计划中 |

---

## 📝 变更记录

### 2026-03-25
- 创建产品改进计划文档
- 开始实施 #4 可见性过滤优化

---

*本文档将持续更新，反映最新的开发进度和决策变更。*
