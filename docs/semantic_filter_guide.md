# UI 元素语义化查找指南

## 概述

本系统提供了灵活的 UI 元素查找机制，允许 LLM 根据自然语言描述来筛选、排序和定位 UI 元素。

## 架构设计

```
用户自然语言描述
    ↓
LLM 语义分析
    ↓
构造过滤条件 (SemanticQuery)
    ↓
应用过滤器 (SemanticFilter)
    ↓
构建 Selector (SelectorBuilder)
    ↓
验证/高亮 (highlight_element)
```

## 核心概念

### 1. 9 宫格布局

将窗口分为 9 个区域，每个区域有自然语言名称：

```
┌─────────┬─────────┬─────────┐
│  左上   │  上中   │  右上   │
│ (Grid 0)│ (Grid 1)│ (Grid 2)│
├─────────┼─────────┼─────────┤
│  左中   │  中间   │  右中   │
│ (Grid 3)│ (Grid 4)│ (Grid 5)│
├─────────┼─────────┼─────────┤
│  左下   │  下中   │  右下   │
│ (Grid 6)│ (Grid 7)│ (Grid 8)│
└─────────┴─────────┴─────────┘
```

### 2. UIElement 数据结构

```python
@dataclass
class UIElement:
    name: str                    # 元素名称
    control_type: str            # 控件类型（ButtonControl, TextControl 等）
    automation_id: str           # 自动化 ID
    class_name: str              # 类名
    bounding_rect: Tuple         # 边界矩形 (left, top, right, bottom)
    grid_id: int                 # 所属网格 ID (0-8)
    grid_position: str           # 网格位置名称（如"左上"）
    center_point: Tuple          # 中心点坐标
```

## MCP 工具使用

### 工具 1: `get_ui_tree_data()`

获取完整的 UI 树数据（不做任何过滤）

```python
# MCP 调用
result = await mcp.call_tool('get_ui_tree_data', {
    'max_depth': 15,
    'include_raw_elements': False
})

# 返回结构
{
    "success": True,
    "ui_tree": {
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
}
```

### 工具 2: `filter_ui_elements(...)`

根据语义条件过滤 UI 元素

```python
# MCP 调用
result = await mcp.call_tool('filter_ui_elements', {
    'grid_positions': ['左上', '左中', '左下'],  # 左边所有区域
    'name_contains': '搜',                       # 名称包含"搜"
    'control_types': ['ButtonControl'],          # 按钮类型
    'min_width': 50,                             # 最小宽度
    'min_height': 30,                            # 最小高度
    'sort_by': 'name'                            # 按名称排序
})

# 返回
{
    "success": True,
    "query": {
        "grid_positions": ["左上", "左中", "左下"],
        "name_contains": "搜",
        "control_types": ["ButtonControl"],
        "sort_by": "name"
    },
    "result_count": 3,
    "elements": [
        {
            "name": "搜一搜",
            "control_type": "ButtonControl",
            "grid_position": "左中",
            "bounding_rect": [16, 513, 91, 558],
            "center_point": [53, 535],
            ...
        },
        ...
    ]
}
```

### 工具 3: `build_selector_for_element(...)`

为指定元素构建 tdSelector 字符串

```python
# MCP 调用
result = await mcp.call_tool('build_selector_for_element', {
    'element_index': 0,              # 第几个元素
    'grid_position': '左中',         # 可选：通过位置定位
    'element_name': '搜一搜'         # 可选：通过名称定位
})

# 返回
{
    "success": True,
    "element": {
        "name": "搜一搜",
        "control_type": "ButtonControl",
        "grid_position": "左中",
        "bounding_rect": [16, 513, 91, 558]
    },
    "selector": {
        "simple": "{ 'ctrl': [('Name', '搜一搜'), ('ControlType', 'ButtonControl')] }",
        "full_with_window": "[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Name', '搜一搜'), ('ControlType', 'ButtonControl')] }]"
    }
}
```

### 工具 4: `highlight_element(...)`

高亮显示 UI 元素

```python
# MCP 调用
result = await mcp.call_tool('highlight_element', {
    'selector_string': "[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Name', '搜一搜')] }]",
    'duration': 5.0,
    'color': 'red'
})
```

## 完整工作流程示例

### 场景：查找"微信左边的搜一搜按钮"

#### 步骤 1: LLM 语义分析

```python
# LLM 分析用户输入："微信左边的搜一搜按钮"
# 提取关键信息:
# - "微信" → 窗口标题
# - "左边" → 网格位置 ['左上', '左中', '左下']
# - "搜一搜" → 名称包含"搜"
# - "按钮" → 控件类型 ButtonControl
```

#### 步骤 2: 设置窗口并获取 UI 树

```python
await mcp.call_tool('set_focus_window', {'process_name': 'WeChat.exe'})
ui_data = await mcp.call_tool('get_ui_tree_data', {'max_depth': 15})
```

#### 步骤 3: 应用语义过滤

```python
filtered = await mcp.call_tool('filter_ui_elements', {
    'grid_positions': ['左上', '左中', '左下'],
    'name_contains': '搜',
    'control_types': ['ButtonControl'],
    'sort_by': 'name'
})
```

#### 步骤 4: 构建 Selector

```python
selector_info = await mcp.call_tool('build_selector_for_element', {
    'element_index': 0
})
```

#### 步骤 5: 高亮验证

```python
highlight_result = await mcp.call_tool('highlight_element', {
    'selector_string': selector_info['selector']['full_with_window'],
    'duration': 5.0,
    'color': 'red'
})
```

## Python API 直接使用

除了 MCP 工具，也可以直接使用 Python API：

### 快速过滤

```python
from core.semantic_filter import quick_filter

results = quick_filter(
    ui_elements,
    grid_positions=['左中', '左上'],
    name_contains='搜',
    control_types=['ButtonControl'],
    sort_by='name'
)
```

### 自定义 SemanticQuery

```python
from core.semantic_filter import SemanticFilter, SemanticQuery

# 创建查询
query = SemanticQuery(
    grid_positions=['左中'],
    name_regex=r'.*搜.*',  # 正则表达式
    control_types=['ButtonControl'],
    min_width=50,
    min_height=30,
    priority_field='size',
    priority_order='desc'
)

# 应用过滤
semantic_filter = SemanticFilter(all_elements)
results = semantic_filter.apply_query(query)
```

### 自定义过滤函数

```python
def custom_filter(elem):
    """只保留正方形元素"""
    left, top, right, bottom = elem.bounding_rect
    width = right - left
    height = bottom - top
    return abs(width - height) < 10  # 宽高差小于 10

query = SemanticQuery(
    grid_positions=['左中'],
    custom_filter=custom_filter
)

semantic_filter = SemanticFilter(all_elements)
results = semantic_filter.apply_query(query)
```

### Selector 构建

```python
from core.semantic_filter import SelectorBuilder

# 从元素构建
selector_str = SelectorBuilder.from_element(element)

# 构建包含窗口的完整 selector
window_title = "微信"
full_selector = SelectorBuilder.from_semantic_match(element, window_title)

# 自定义构建
custom_selector = SelectorBuilder.build_custom({
    'name': '搜一搜',
    'control_type': 'ButtonControl',
    'automation_id': ''
})
```

## 高级用法

### 多轮对话 refine

```python
# 第一轮：宽泛搜索
results1 = await filter_ui_elements(
    grid_positions=['左中'],
    name_contains='搜'
)

# LLM 分析结果后，第二轮：精确化
if len(results1) > 1:
    results2 = await filter_ui_elements(
        grid_positions=['左中'],
        name_contains='搜一搜',  # 更精确的名称
        min_width=50  # 添加尺寸限制
    )
```

### 组合多个条件

```python
# 查找左侧区域所有带图标的按钮
results = await filter_ui_elements(
    grid_positions=['左上', '左中', '左下'],
    control_types=['ButtonControl'],
    min_width=40,
    min_height=40
)

# LLM 可以进一步筛选有图片的元素
icon_buttons = [
    e for e in results 
    if 'Image' in e.get('class_name', '')
]
```

## 测试示例

运行测试查看实际效果：

```bash
# 测试语义化过滤器
python tests/test_semantic_filter.py

# 测试 MCP 工具集成
python tests/test_mcp_semantic_search.py
```

## 总结

这种设计的优势：

1. **灵活性**: LLM 可以根据不同的自然语言描述动态构造查询
2. **可扩展性**: 支持添加新的过滤条件和排序规则
3. **透明性**: 返回完整的 UI 树数据，让 LLM 做决策
4. **验证闭环**: 提供高亮功能即时验证结果

与之前的硬编码方式相比，现在 LLM 有足够的工具来处理各种复杂的 UI 查找场景！
