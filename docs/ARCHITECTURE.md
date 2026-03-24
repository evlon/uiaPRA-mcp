# tdRPA-mcp 系统架构详解

---

## 📋 目录

1. [整体架构](#-整体架构)
2. [核心层架构](#-核心层架构)
3. [工具层架构](#-工具层架构)
4. [数据流设计](#-数据流设计)
5. [关键技术实现](#-关键技术实现)
6. [性能优化](#-性能优化)

---

## 🏗️ 整体架构

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│                  (MCP Client / IDE)                      │
└───────────────────────┬─────────────────────────────────┘
                        │ MCP Protocol (JSON-RPC)
┌───────────────────────▼─────────────────────────────────┐
│                     Application Layer                    │
│                   (MCP Server + Tools)                   │
├─────────────────────────────────────────────────────────┤
│  set_focus_window  │  get_ui_tree_data  │  filter_...  │
│  build_selector    │  highlight_element │  scan_...    │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                      Core Business Layer                 │
│            (UIA Scanner, Grid Manager, Filter)           │
├─────────────────────────────────────────────────────────┤
│  UIARegionScanner  │  UITreeScanner   │  SemanticFilter │
│  GridManager       │  SelectorBuilder │  Highlighter    │
│  Logger            │  LogAnalyzer     │                 │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   Infrastructure Layer                   │
│            (Windows UI Automation API)                   │
└─────────────────────────────────────────────────────────┘
```

### 模块依赖关系

```
mcp_server.py
    │
    ├──► tools/grid_picker.py
    │       │
    │       ├──► core/uia_region_scanner.py
    │       ├──► core/grid_manager.py
    │       ├──► core/ui_tree_scanner.py
    │       ├──► core/semantic_filter.py
    │       └──► core/screen_highlighter.py
    │
    └──► core/logger.py
```

---

## 🔧 核心层架构

### 1. UIA Region Scanner

**职责**: 基于 Windows UI Automation 的底层扫描器

**关键方法**:
```python
class UIARegionScanner:
    def __init__(self, process_name=None, window_title=None, timeout=5.0):
        """初始化扫描器"""
        
    def _get_root_element(self) -> Control:
        """获取根元素（窗口或桌面）"""
        
    def scan_grid(self, grid_rect: tuple, search_depth: int = 3) -> List[ElementInfo]:
        """扫描指定区域"""
        
    def find_by_selector(self, selector: str, timeout: float = None) -> Optional[Control]:
        """使用 selector 查找元素"""
        
    def get_window_rect(self) -> tuple:
        """获取窗口矩形"""
```

**日志集成**:
```python
from core.logger import get_logger, log_function_call, LogContext

logger = get_logger('tdrpa.scanner', level='DEBUG', detailed=True)

class UIARegionScanner:
    @log_function_call(logger=logger)
    def __init__(self, ...):
        with LogContext(logger, "初始化扫描器"):
            ...
```

### 2. Grid Manager

**职责**: 9 宫格空间管理

**核心数据结构**:
```python
@dataclass
class Grid:
    id: int              # 0-8
    row: int             # 0-2
    col: int             # 0-2
    left: int
    top: int
    right: int
    bottom: int
    center: Tuple[int, int]
    position_name: str   # "左上", "中间", etc.
```

**位置映射**:
```python
POSITION_NAMES_3X3 = {
    (0, 0): '左上', (0, 1): '上中', (0, 2): '右上',
    (1, 0): '左中', (1, 1): '中间', (1, 2): '右中',
    (2, 0): '左下', (2, 1): '下中', (2, 2): '右下',
}

POSITION_NAME_TO_ID = {
    '左上': 0, '上中': 1, '右上': 2,
    '左中': 3, '中间': 4, '右中': 5,
    '左下': 6, '下中': 7, '右下': 8,
}
```

**关键方法**:
```python
class GridManager:
    def get_grid_by_id(self, grid_id: int) -> Grid:
        """通过 ID 获取网格"""
        
    def get_grid_by_position(self, x: int, y: int) -> Grid:
        """通过坐标获取网格"""
        
    def get_grid_by_position_name(self, name: str) -> Grid:
        """通过自然语言名称获取网格"""
        
    def get_grids_by_region_description(self, desc: str) -> List[Grid]:
        """通过区域描述获取多个网格"""
        # 例如："左边" → [Grid 0, Grid 3, Grid 6]
```

### 3. UI Tree Scanner

**职责**: 完整 UI 树遍历和元素分组

**数据结构**:
```python
@dataclass
class UIElement:
    name: str
    control_type: str
    automation_id: str
    class_name: str
    bounding_rect: Tuple[int, int, int, int]
    grid_id: Optional[int]         # 所属网格 ID
    grid_position: Optional[str]   # 网格位置名称
    center_point: Optional[Tuple[int, int]]
    element_ref: Any               # 原始元素引用
    
    def to_dict(self) -> dict:
        """转换为字典"""
```

**扫描流程**:
```python
class UITreeScanner:
    def scan_full_tree(self, max_depth: int = 15) -> List[UIElement]:
        """扫描完整 UI 树"""
        self.all_elements = []
        
        def traverse(element, depth=0):
            if depth > max_depth:
                return
            
            # 提取元素信息
            ui_elem = self._extract_element_info(element)
            
            if ui_elem:
                # 计算所属网格
                self._assign_to_grid(ui_elem)
                self.all_elements.append(ui_elem)
                
                # 遍历子元素
                children = element.GetChildren()
                for child in children:
                    traverse(child, depth + 1)
        
        traverse(self.root_element)
        return self.all_elements
```

**分组数据返回**:
```python
def get_grouped_ui_tree(self) -> Dict[str, Any]:
    """返回分组的 UI 树数据（不做过滤）"""
    return {
        'by_grid': {
            '左上': [elem1, elem2, ...],
            '左中': [...],
            ...
        },
        'by_control_type': {
            'ButtonControl': 5,
            'TextControl': 10,
            ...
        },
        'statistics': {
            'total_elements': 77,
            'by_grid_position': {...},
            'by_control_type': {...}
        }
    }
```

### 4. Semantic Filter

**职责**: 灵活的语义化元素过滤

**查询条件**:
```python
@dataclass
class SemanticQuery:
    # 网格位置过滤
    grid_positions: Optional[List[str]]  # ['左上', '左中']
    grid_ids: Optional[List[int]]        # [0, 3]
    
    # 名称匹配
    name_contains: Optional[str]         # '搜'
    name_regex: Optional[str]            # r'.*搜.*'
    
    # 控件类型
    control_types: Optional[List[str]]   # ['ButtonControl']
    
    # 尺寸过滤
    min_width: int = 0
    min_height: int = 0
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    
    # 排序
    priority_field: str = 'name'
    priority_order: str = 'desc'
    
    # 自定义过滤
    custom_filter: Optional[Callable] = None
```

**过滤流程**:
```python
class SemanticFilter:
    def apply_query(self, query: SemanticQuery) -> List[UIElement]:
        results = self.ui_elements.copy()
        
        # 1. 网格过滤
        if query.grid_positions or query.grid_ids:
            results = self._filter_by_grid(results, query)
        
        # 2. 名称过滤
        if query.name_contains or query.name_regex:
            results = self._filter_by_name(results, query)
        
        # 3. 类型过滤
        if query.control_types:
            results = self._filter_by_control_type(results, query)
        
        # 4. 尺寸过滤
        results = self._filter_by_size(results, query)
        
        # 5. 自定义过滤
        if query.custom_filter:
            results = [e for e in results if query.custom_filter(e)]
        
        # 6. 排序
        results = self._sort_results(results, query)
        
        return results
```

### 5. Selector Builder

**职责**: 自动生成 tdSelector 语法

**构建策略**:
```python
class SelectorBuilder:
    @staticmethod
    def from_element(element: UIElement) -> str:
        """从 UIElement 构建 selector"""
        conditions = []
        
        # 优先级：AutomationId > Name > ControlType > ClassName
        if element.automation_id:
            conditions.append(f"('AutomationId', '{element.automation_id}')")
        
        if element.name:
            conditions.append(f"('Name', '{element.name}')")
        
        if element.control_type:
            conditions.append(f"('ControlType', '{element.control_type}')")
        
        return "{ 'ctrl': [" + ", ".join(conditions) + "] }"
    
    @staticmethod
    def from_semantic_match(element: UIElement, window_title: str) -> str:
        """构建包含窗口路径的完整 selector"""
        window_part = f"[{{ 'wnd': [('Text', '{window_title}')] }}"
        ctrl_part = SelectorBuilder.from_element(element)
        return window_part + ", " + ctrl_part + "]"
```

### 6. Screen Highlighter

**职责**: 实时屏幕高亮显示

**实现原理**:
```python
class ScreenHighlighter:
    def create_highlight_overlay(self, rect, color='red'):
        """创建透明覆盖层"""
        overlay = tk.Toplevel()
        overlay.overrideredirect(True)  # 无边框
        overlay.attributes('-topmost', True)  # 置顶
        overlay.attributes('-transparentcolor', 'white')  # 透明色
        
        # 绘制多层边框
        canvas = tk.Canvas(overlay, highlightthickness=0)
        canvas.create_rectangle(
            border_width, border_width,
            width - border_width, height - border_width,
            outline=color, width=border_width * 2
        )
        
    def update_position(self, rect):
        """跟随元素移动"""
        # 每 100ms 更新一次位置
```

**使用方式**:
```python
def highlight_element(element, duration=3.0, color='red', follow=True):
    """高亮显示元素"""
    highlighter = ScreenHighlighter()
    
    rect = element.BoundingRectangle
    highlighter.create_highlight_overlay(rect, color)
    
    if follow:
        # 启动跟随线程
        threading.Thread(
            target=highlighter.follow_loop,
            args=(element, duration)
        ).start()
```

---

## 🛠️ 工具层架构

### MCP Tools 设计

每个工具的设计原则：

1. **单一职责**: 一个工具只做一件事
2. **自包含**: 工具内部处理所有逻辑
3. **错误处理**: 完善的异常捕获和返回
4. **日志记录**: 自动记录调用信息

**示例：filter_ui_elements**
```python
@mcp.tool()
async def filter_ui_elements(
    grid_positions: Optional[List[str]] = None,
    name_contains: Optional[str] = None,
    control_types: Optional[List[str]] = None,
    min_width: int = 0,
    min_height: int = 0,
    sort_by: str = 'name'
) -> Dict[str, Any]:
    """语义化过滤 UI 元素"""
    
    # 1. 检查初始化
    scanner = scanner_ref.get('scanner')
    if not scanner:
        return {"success": False, "error": "Not initialized"}
    
    # 2. 扫描 UI 树
    ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
    all_elements = ui_scanner.scan_full_tree(max_depth=15)
    
    # 3. 创建查询
    query = SemanticQuery(
        grid_positions=grid_positions,
        name_contains=name_contains,
        control_types=control_types,
        min_width=min_width,
        min_height=min_height,
        priority_field=sort_by
    )
    
    # 4. 应用过滤
    semantic_filter = SemanticFilter(all_elements)
    filtered_results = semantic_filter.apply_query(query)
    
    # 5. 构建返回
    return {
        "success": True,
        "query": {...},
        "result_count": len(filtered_results),
        "elements": [elem.to_dict() for elem in filtered_results[:50]]
    }
```

---

## 🔄 数据流设计

### 典型操作流程

```
用户输入："微信左边的搜一搜按钮"
    │
    ▼
LLM 语义分析
    │
    ├─► grid_positions = ['左上', '左中', '左下']
    ├─► name_contains = '搜'
    └─► control_types = ['ButtonControl']
    │
    ▼
调用 MCP 工具：filter_ui_elements(...)
    │
    ├─► 调用 get_ui_tree_data()
    │   └─► 扫描完整 UI 树
    │       └─► 分配网格位置
    │
    ├─► 创建 SemanticQuery
    │
    ├─► 应用 SemanticFilter
    │   ├─► 网格过滤
    │   ├─► 名称过滤
    │   ├─► 类型过滤
    │   └─► 排序
    │
    └─► 返回过滤结果
        │
        ▼
    用户确认结果
        │
        ▼
    调用 build_selector_for_element()
        │
        └─► 生成 tdSelector 字符串
            │
            ▼
        调用 highlight_element()
            │
            └─► 创建屏幕覆盖层
                └─► 实时高亮显示
```

### 缓存策略

```python
class ScannerCache:
    """扫描结果缓存"""
    
    def __init__(self):
        self.cache = {}  # grid_id -> elements
        self.timestamp = {}  # grid_id -> timestamp
        self.ttl = 300  # 5 分钟过期
    
    def get(self, grid_id: int) -> Optional[List[ElementInfo]]:
        """获取缓存"""
        if grid_id in self.cache:
            if time.time() - self.timestamp[grid_id] < self.ttl:
                return self.cache[grid_id]
        return None
    
    def set(self, grid_id: int, elements: List[ElementInfo]):
        """设置缓存"""
        self.cache[grid_id] = elements
        self.timestamp[grid_id] = time.time()
```

---

## ⚡ 关键技术实现

### 1. 元素去重算法

**问题**: 同一元素可能被多次扫描到

**解决方案**: IoU (Intersection over Union)

```python
def _deduplicate_elements(self, elements: List[UIElement]) -> List[UIElement]:
    """移除重叠度 > 90% 的元素"""
    result = []
    seen_rects = []
    
    for elem in elements:
        rect = elem.bounding_rect
        is_duplicate = False
        
        for seen_rect in seen_rects:
            overlap = self._calculate_overlap(rect, seen_rect)
            if overlap > 0.9:
                is_duplicate = True
                break
        
        if not is_duplicate:
            result.append(elem)
            seen_rects.append(rect)
    
    return result

def _calculate_overlap(self, rect1: Tuple, rect2: Tuple) -> float:
    """计算 IoU"""
    # 计算交集
    inter_left = max(rect1[0], rect2[0])
    inter_top = max(rect1[1], rect2[1])
    inter_right = min(rect1[2], rect2[2])
    inter_bottom = min(rect1[3], rect2[3])
    
    if inter_left >= inter_right or inter_top >= inter_bottom:
        return 0.0
    
    inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
    
    # 计算并集
    area1 = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
    area2 = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])
    
    union_area = area1 + area2 - inter_area
    
    return inter_area / union_area if union_area > 0 else 0.0
```

### 2. 自然语言解析

**支持多种表达方式**:

```python
REGION_MAPPING = {
    '左边': ['左上', '左中', '左下'],
    '左侧': ['左上', '左中', '左下'],
    '右边': ['右上', '右中', '右下'],
    '右侧': ['右上', '右中', '右下'],
    '上面': ['左上', '上中', '右上'],
    '顶部': ['左上', '上中', '右上'],
    '下面': ['左下', '下中', '右下'],
    '底部': ['左下', '下中', '右下'],
    '中间': ['中间'],
    '中心': ['中间'],
    '左上角': ['左上'],
    '右下角': ['右下'],
}

def parse_region_description(desc: str) -> List[str]:
    """解析区域描述"""
    desc = desc.lower()
    
    for keyword, positions in REGION_MAPPING.items():
        if keyword in desc:
            return positions
    
    # 尝试精确匹配
    if desc in POSITION_NAME_TO_ID:
        return [desc]
    
    return []  # 无匹配
```

### 3. 高性能扫描

**优化策略**:

1. **提前终止**: 找到目标立即停止
2. **并发扫描**: 多线程扫描不同网格
3. **CV 预筛选**: 跳过空白区域（可选）

```python
def parallel_scan_grids(grid_ids: List[int]) -> Dict[int, List[ElementInfo]]:
    """并行扫描多个网格"""
    from concurrent.futures import ThreadPoolExecutor
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_grid = {
            executor.submit(scan_single_grid, grid_id): grid_id
            for grid_id in grid_ids
        }
        
        for future in as_completed(future_to_grid):
            grid_id = future_to_grid[future]
            try:
                results[grid_id] = future.result()
            except Exception as e:
                logger.error(f"Grid {grid_id} scan failed: {e}")
    
    return results
```

---

## 📊 性能优化

### 1. 减少扫描深度

```python
# 不推荐：扫描太深，耗时长
elements = scanner.scan_grid(rect, search_depth=10)  # ❌

# 推荐：浅层扫描，快速
elements = scanner.scan_grid(rect, search_depth=3)   # ✅
```

### 2. 使用缓存

```python
# 第一次扫描
if not cache.has(grid_id):
    elements = scanner.scan_grid(grid_rect)
    cache.set(grid_id, elements)

# 后续使用缓存
elements = cache.get(grid_id)
```

### 3. 限制返回数量

```python
# 只返回前 50 个结果
return elements[:50]
```

### 4. 异步处理

```python
# 后台扫描，不阻塞主线程
async def scan_background():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, scanner.scan_full_tree)
```

---

## 🔒 安全考虑

### 1. 权限控制

```python
# 需要管理员权限的应用
if process_name in ['taskmgr.exe', 'regedit.exe']:
    if not is_admin():
        raise PermissionError("需要管理员权限")
```

### 2. 超时保护

```python
def find_by_selector(self, selector: str, timeout: float = 5.0):
    """防止无限循环"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # 查找逻辑
        pass
    
    raise TimeoutError(f"查找超时 ({timeout}s)")
```

### 3. 输入验证

```python
def filter_ui_elements(grid_positions: List[str], ...):
    """验证输入参数"""
    valid_positions = set(POSITION_NAME_TO_ID.keys())
    
    for pos in grid_positions:
        if pos not in valid_positions:
            raise ValueError(f"无效的网格位置：{pos}")
```

---

## 📈 扩展性设计

### 插件化架构（未来）

```python
class PluginManager:
    """插件管理器"""
    
    def register_plugin(self, plugin: BasePlugin):
        """注册插件"""
        
    def load_filters(self) -> List[BaseFilter]:
        """加载所有过滤器插件"""
        
    def load_exporters(self) -> List[BaseExporter]:
        """加载所有导出器插件"""
```

### 配置驱动

```yaml
# config.yaml
scanning:
  default_depth: 3
  max_depth: 15
  parallel: true
  
logging:
  level: DEBUG
  file: true
  console: true
  
ui:
  grid_rows: 3
  grid_cols: 3
  highlight_color: red
  highlight_duration: 3.0
```

---

*Last updated: 2026-03-25*
