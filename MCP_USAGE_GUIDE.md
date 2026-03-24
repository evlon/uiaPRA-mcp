# tdRPA-mcp MCP 服务使用指南

## 架构设计

```
用户 (自然语言)
    ↓
LLM (理解意图，决定调用哪个工具)
    ↓
MCP 工具
    ├── scan_grid_region() - 扫描区域获取元素
    └── find_element_selector() - 使用 selector 查找位置
    ↓
返回结果 (位置、中心点、高亮矩形)
    ↓
LLM (解释结果给用户)
```

## 可用工具

### 1. `scan_grid_region(grid_id, search_depth=2)`

扫描指定宫格区域的所有 UI 元素。

**参数:**
- `grid_id`: 0-15，宫格编号
- `search_depth`: 搜索深度，默认 2

**返回:**
```json
{
  "grid_id": 5,
  "element_count": 19,
  "elements": [
    {
      "name": "搜一搜",
      "control_type": "ButtonControl",
      "automation_id": "",
      "bounding_rect": [16, 513, 91, 558]
    }
  ]
}
```

**用途:** LLM 先用这个工具查看某个区域有哪些元素。

---

### 2. `find_element_selector(selector_string, timeout=5.0)`

使用 tdSelector 语法查找 UI 元素。

**参数:**
- `selector_string`: tdSelector 语法字符串

**返回:**
```json
{
  "found": true,
  "element": {
    "name": "搜一搜",
    "control_type": "ButtonControl",
    "bounding_rect": [16, 513, 91, 558],
    "center_point": (53, 535)
  }
}
```

**用途:** LLM 构建 selector 来精确定位元素。

---

### 3. `set_focus_window(process_name, window_title)`

设置目标窗口（未来功能）。

---

## tdSelector 语法

### 基本格式

```python
[
  { 'wnd' : [ ('Text', '窗口标题'), ('App', 'process.exe') ] },
  { 'ctrl' : [ ('Text', '按钮文本'), ('aaRole', 'PushButton') ] }
]
```

### 常用属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `Text` | 元素文本/窗口标题 | `('Text', '微信')` |
| `App` | 进程名 | `('App', 'Weixin.exe')` |
| `AutomationId` | 自动化 ID | `('AutomationId', 'MainView.main_tabbar')` |
| `aaRole` | 控件类型 | `('aaRole', 'PushButton')` |

### aaRole 映射

tdSelector 中的 `aaRole` 会映射到 uiautomation 的 `ControlTypeName`：

| tdSelector | uiautomation |
|------------|--------------|
| `PushButton` | `ButtonControl` |
| `Window` | `WindowControl` |
| `Grouping` | `GroupControl` |
| `Edit` | `EditControl` |
| `Pane` | `PaneControl` |

---

## LLM 使用流程示例

### 场景 1: 用户说"帮我找微信的搜一搜按钮"

**Step 1:** LLM 调用 `scan_grid_region(grid_id=5)` 扫描中心区域

**Step 2:** 收到返回的元素列表，LLM 发现:
```json
{"name": "搜一搜", "control_type": "ButtonControl"}
```

**Step 3:** LLM 构建 selector 调用 `find_element_selector`:
```python
"[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]"
```

**Step 4:** 返回位置信息，LLM 告诉用户:
> "找到了！微信的搜一搜按钮在屏幕左侧，坐标 (53, 535)"

---

### 场景 2: 用户说"点击记事本的保存按钮"

**Step 1:** LLM 调用 `set_focus_window(process_name='notepad.exe')`

**Step 2:** LLM 调用 `scan_all_grids()` 扫描所有区域

**Step 3:** 从扫描结果中找到"保存"按钮的 selector

**Step 4:** 调用 `find_element_selector()` 获取精确位置

**Step 5:** 执行点击操作（未来功能）

---

## 最佳实践

### ✅ 推荐的 selector 写法

1. **尽量简化路径** - 只保留必要的层级
```python
# 推荐：2 层
"[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜')] }]"

# 不推荐：6 层（太严格容易失败）
"[{ 'wnd': [...] }, { 'ctrl': [...] }, { 'ctrl': [...] }, ...]"
```

2. **优先使用 AutomationId** - 最稳定
```python
"[{ 'ctrl': [('AutomationId', 'MainView.main_tabbar')] }]"
```

3. **组合使用 Text + aaRole** - 提高准确性
```python
"[{ 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]"
```

### ❌ 避免的写法

1. **不要依赖 App 属性** - UWP 应用可能没有进程名
```python
# 可能失败
"[{ 'wnd': [('Text', '微信'), ('App', 'Weixin.exe')] }]"

# 更好
"[{ 'wnd': [('Text', '微信')] }]"
```

2. **不要过深的层级** - 容易匹配失败
```python
# 避免超过 3 层
```

---

## 调试技巧

### 1. 先用 `scan_grid_region` 查看元素

不确定 selector 怎么写？先扫描看看有什么元素：

```python
scan_grid_region(grid_id=5)
# 返回元素列表，找到目标的 name 和 control_type
```

### 2. 逐步构建 selector

```python
# Step 1: 只匹配窗口
find_element_selector("[{ 'wnd': [('Text', '微信')] }]")

# Step 2: 添加按钮条件
find_element_selector("[{ 'wnd': [...] }, { 'ctrl': [('Text', '搜一搜')] }]")

# Step 3: 添加类型条件
find_element_selector("[{ 'wnd': [...] }, { 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]")
```

### 3. 使用模糊匹配（未来功能）

```python
"[{ 'ctrl': [('Text', '保存', 'fuzzy')] }]"  # 匹配"保存"、"另存为"等
```

---

## 完整示例

### 示例 1: 查找微信联系人按钮

```python
# 扫描微信窗口所在区域 (假设 grid_id=0)
result = scan_grid_region(grid_id=0)

# LLM 分析返回的元素，发现:
# {"name": "通讯录", "control_type": "ButtonControl"}

# 构建 selector
selector = """[
  { 'wnd' : [ ('Text' , '微信') ] } ,
  { 'ctrl' : [ ('Text' , '通讯录') , ('aaRole' , 'PushButton') ] }
]"""

# 查找位置
result = find_element_selector(selector)

# 返回:
# {
#   "found": true,
#   "element": {
#     "name": "通讯录",
#     "bounding_rect": [16, 300, 91, 345],
#     "center_point": (53, 322)
#   }
# }
```

### 示例 2: 查找记事本菜单

```python
# 扫描记事本窗口
selector = """[
  { 'wnd' : [ ('Text' , '无标题 - 记事本') , ('App' , 'notepad.exe') ] } ,
  { 'ctrl' : [ ('Text' , '文件') , ('aaRole' , 'MenuItem') ] }
]"""

result = find_element_selector(selector)
```

---

## 故障排查

### 问题 1: "找不到元素"

**原因:** selector 路径太长或条件太严格

**解决:** 
1. 减少层级（2-3 层即可）
2. 移除 `App` 条件（UWP 应用没有进程名）
3. 先用 `scan_grid_region` 确认元素存在

### 问题 2: "aaRole 不匹配"

**原因:** tdSelector 的 `aaRole` 与实际控件类型名称不同

**解决:** 
- `PushButton` → `ButtonControl` (自动映射)
- `Window` → `WindowControl` (自动映射)
- 使用 `scan_grid_region` 查看实际的 `control_type`

### 问题 3: "窗口找不到"

**原因:** 窗口标题不完全匹配

**解决:** 
1. 用 `scan_grid_region` 查看实际的窗口标题
2. 使用模糊匹配（未来支持）
3. 只用部分标题文本

---

## 总结

tdRPA-mcp 提供两个核心能力：

1. **扫描** (`scan_grid_region`) - 获取区域内的所有元素信息
2. **查找** (`find_element_selector`) - 使用 selector 精确定位

LLM 负责：
- 理解用户意图
- 决定调用哪个工具
- 构建合适的 selector
- 解释结果给用户

这种设计让 LLM 可以灵活地使用工具，而不需要硬编码复杂的逻辑。
