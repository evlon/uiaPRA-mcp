# 可见性过滤功能 (Visibility Filter)

## 概述

uiaRPA-mcp 现已实现严格的"可见性过滤"策略，确保在进行基于 9 宫格的区域扫描和元素查找时，系统仅检索对用户视觉上可见且未被遮挡的 UI 元素。

## 核心特性

### 1. 多层可见性检测

`VisibilityChecker` 类实现了 4 层可见性验证：

1. **基本可见性属性检查**
   - 检查 `IsOffscreen` 属性
   - 检查 `IsEnabled` 属性
   - 检查 `IsControlElement` 属性

2. **离屏检测**
   - 使用 UIA 的 `IsOffscreen` 属性
   - 检查元素边界矩形是否完全在屏幕外

3. **像素覆盖分析**
   - 检查元素中心点是否被其他窗口遮挡
   - 对核心交互区域（80% 中心区域）进行多点采样
   - 使用 `ElementFromPoint()` API 检测实际遮挡情况

4. **前景层检测**
   - 检查元素所在窗口是否为最顶层窗口
   - 验证窗口的 `WS_EX_TOPMOST` 样式

### 2. 智能过滤策略

- **父元素被遮挡但子元素可能可见**：继续遍历子元素树
- **保守处理原则**：出错时假设元素可见，避免误过滤
- **高性能优化**：使用采样点检测而非全像素扫描

## 集成到 MCP 工具

以下 MCP 工具已添加 `enable_visibility_filter` 参数（默认 `True`）：

### `get_ui_tree_data`

```python
# 获取 UI 树数据（默认启用可见性过滤）
ui_data = await get_ui_tree_data(
    max_depth=15,
    include_raw_elements=False,
    enable_visibility_filter=True  # 默认启用
)

# 禁用可见性过滤，获取所有元素（包括被遮挡的后台元素）
ui_data = await get_ui_tree_data(enable_visibility_filter=False)
```

### `filter_ui_elements`

```python
# 语义化过滤 UI 元素（默认启用可见性过滤）
result = await filter_ui_elements(
    grid_positions=['左中', '左上'],
    name_contains='搜',
    control_types=['ButtonControl'],
    enable_visibility_filter=True  # 确保只匹配可见元素
)
```

### `scan_region`

```python
# 扫描指定区域（默认启用可见性过滤）
result = await scan_region(
    region="左上",
    enable_visibility_filter=True  # 避免选中被遮挡的后台元素
)
```

### `build_selector_for_element`

```python
# 为元素构建 selector（默认从可见元素中选择）
selector = await build_selector_for_element(
    element_index=0,
    enable_visibility_filter=True  # 避免为被遮挡元素生成 selector
)
```

## 使用场景

### 场景 1: 微信"搜一搜"按钮查找

**问题**：微信侧边栏、聊天列表或其他浮层可能遮挡后台元素，导致错误匹配。

**解决方案**：
```python
# 启用可见性过滤（默认），确保只匹配用户肉眼可见的元素
result = await scan_region(
    region="左侧",
    name_contains="搜一搜",
    enable_visibility_filter=True
)
```

### 场景 2: 模态对话框中的元素

**问题**：模态对话框弹出时，背景窗口的元素应该被排除。

**解决方案**：
```python
# 可见性过滤会自动检测前景层，只返回模态对话框中的可见元素
elements = await filter_ui_elements(
    name_contains="确定",
    enable_visibility_filter=True
)
```

### 场景 3: 下拉菜单和弹出窗口

**问题**：下拉菜单打开时，需要排除被菜单遮挡的背景元素。

**解决方案**：
```python
# 像素覆盖检测会识别被下拉菜单遮挡的区域
ui_tree = await get_ui_tree_data(
    enable_visibility_filter=True
)
```

## 性能对比

测试数据（桌面根窗口，深度 8）：

| 模式 | 元素数量 | 过滤率 |
|------|---------|--------|
| 禁用可见性过滤 | 1681 个 | - |
| 启用可见性过滤 | 14 个 | 99.2% |

**说明**：可见性过滤会显著减少返回的元素数量，只保留对用户真正可见的元素。

## 注意事项

1. **默认行为**：所有工具的 `enable_visibility_filter` 参数默认为 `True`
   
2. **何时禁用**：
   - 需要调试或分析完整 UI 树结构时
   - 需要访问被遮挡的后台元素（特殊自动化场景）
   - 性能敏感场景（可见性检查会增加计算开销）

3. **日志记录**：
   - 启用了可见性过滤时，会记录过滤掉的元素信息
   - 可通过查看日志分析哪些元素被过滤及原因

4. **异常处理**：
   - 可见性检测出错时采用保守策略（假设元素可见）
   - 避免因检测错误导致有效元素被误过滤

## 技术实现

### 核心文件

- `core/visibility_checker.py` - 可见性检测器实现
- `core/ui_tree_scanner.py` - UI 树扫描器（集成可见性过滤）
- `tools/grid_picker.py` - MCP 工具（添加可见性过滤参数）

### 关键算法

```python
# 点遮挡检测
def _is_point_occluded(self, x: int, y: int, exclude_element=None) -> bool:
    element_at_point = self.auto.ElementFromPoint(x, y)
    if not element_at_point:
        return False
    # 检查是否是目标元素本身或同一 UI 树
    if exclude_element and element_at_point == exclude_element:
        return False
    if self._is_same_tree(exclude_element, element_at_point):
        return False
    return True  # 被其他元素占据
```

## 测试

运行测试脚本验证可见性过滤功能：

```bash
cd d:/projects/wx-rpa
.venv/Scripts/python.exe uiaRPA-mcp/test_visibility_filter.py
```

测试项目：
1. VisibilityChecker 基本功能
2. UITreeScanner 可见性过滤对比
3. MCP 工具参数集成验证

## 版本历史

- **v1.0** (2026-03-25)
  - 初始版本
  - 实现 4 层可见性检测
  - 集成到所有主要 MCP 工具
  - 默认启用可见性过滤

## 相关文档

- [9 宫格系统说明](./GRID_SYSTEM.md)
- [MCP 工具使用指南](./TOOLS_GUIDE.md)
- [UI 树扫描器设计](./UI_TREE_SCANNER_DESIGN.md)
