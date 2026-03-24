# 屏幕高亮功能

## 概述

tdRPA-mcp 现在支持在屏幕上**实时高亮** UI 元素，使用彩色边框跟随元素移动。

## 核心特性

✅ **实时跟随** - 高亮框会自动跟随元素位置变化  
✅ **多色支持** - 红色、绿色、蓝色、黄色、橙色  
✅ **可配置时长** - 自定义高亮持续时间  
✅ **自动消失** - 时间到了自动关闭高亮框  

---

## MCP 工具：`highlight_element`

### 函数签名

```python
@mcp.tool()
async def highlight_element(
    selector_string: str,
    duration: float = 3.0,
    color: str = 'red'
) -> Dict[str, Any]:
    """
    在屏幕上高亮显示 UI 元素
    
    Args:
        selector_string: tdSelector 语法字符串
        duration: 高亮持续时间（秒），默认 3 秒
        color: 边框颜色 ('red', 'green', 'blue', 'yellow', 'orange')
    
    Returns:
        高亮结果和元素位置信息
    """
```

---

## 使用示例

### 示例 1: 基础使用（红色高亮）

```python
# 在 Opencode 中
用户："帮我高亮微信的搜一搜按钮"

LLM 调用:
highlight_element(
    selector_string="""[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]""",
    duration=3.0,
    color='red'
)

返回:
{
  "success": true,
  "element": {
    "name": "搜一搜",
    "bounding_rect": [16, 513, 91, 558],
    "center_point": [53, 535]
  },
  "highlight_info": {
    "duration": 3.0,
    "color": "red",
    "follow_mode": true
  }
}
```

**效果**: 在"搜一搜"按钮周围显示红色边框，持续 3 秒后自动消失。

---

### 示例 2: 不同颜色

```python
# 绿色高亮
highlight_element(
    selector_string="[{ 'wnd': [('Text', '记事本')] }, { 'ctrl': [('Text', '文件')] }]",
    duration=5.0,
    color='green'
)

# 蓝色高亮
highlight_element(
    selector_string="[...]",
    color='blue'
)

# 黄色高亮
highlight_element(
    selector_string="[...]",
    color='yellow'
)

# 橙色高亮
highlight_element(
    selector_string="[...]",
    color='orange'
)
```

---

### 示例 3: 结合 scan_region 使用

```python
# Step 1: 先扫描左侧区域
result = scan_region(region="左侧")

# Step 2: 从结果中找到目标元素
target_name = "搜一搜"
for elem in result['elements']:
    if target_name in elem.get('name', ''):
        # Step 3: 构建 selector 并高亮
        selector = f"""
        [{{ 'wnd': [('Text', '微信')] }}, {{ 'ctrl': [('Text', '{elem['name']}'), ('aaRole', 'PushButton')] }}]
        """
        
        highlight_element(
            selector_string=selector,
            duration=5.0,
            color='red'
        )
        break
```

---

## 技术实现

### 架构

```
用户请求
    ↓
LLM 理解意图
    ↓
调用 highlight_element(selector, duration, color)
    ↓
1. 使用 find_by_selector() 查找元素
2. 获取元素位置 (BoundingRectangle)
3. 创建 tkinter 覆盖层窗口
4. 绘制彩色边框
5. 启动跟随循环（100ms 更新一次）
6. 时间到后自动销毁
    ↓
返回高亮结果
```

### 核心技术

- **tkinter** - Python 内置 GUI 库，用于创建覆盖层
- **置顶窗口** - `attributes('-topmost', True)` 确保在最上层
- **透明背景** - `attributes('-transparentcolor', 'white')`
- **实时更新** - 每 100ms 检查元素位置是否变化

---

## 代码结构

```
core/
└── screen_highlighter.py      # 高亮核心模块
    ├── ScreenHighlighter       # 高亮管理类
    └── highlight_element()     # 便捷函数

tools/
└── grid_picker.py
    └── highlight_element()     # MCP 工具封装
```

---

## 完整测试流程

### 步骤 1: 运行测试

```bash
D:\projects\wx-rpa\.venv\Scripts\python.exe tests/test_live_highlight.py
```

### 步骤 2: 观察效果

应该在微信窗口的"搜一搜"按钮周围看到红色边框，持续 5 秒后自动消失。

### 步骤 3: 在 Opencode 中使用

```
用户："高亮微信的搜一搜按钮"
```

Opencode 会调用 `highlight_element` 工具，你应该能看到高亮效果。

---

## 常见问题

### Q: 高亮框不显示？

**A:** 可能的原因：
1. tkinter 未安装（通常 Python 自带）
2. 元素未找到（检查 selector）
3. 窗口被其他全屏应用遮挡

**解决:** 
```python
# 先测试元素是否能找到
result = find_element_selector(selector_string)
if result['found']:
    print("元素位置:", result['element']['bounding_rect'])
    # 然后再高亮
```

---

### Q: 高亮框不跟随元素？

**A:** 跟随模式默认开启，但如果元素移动太快可能跟不上。

**解决:** 缩短更新间隔（修改源码中的 `sleep(0.1)`）

---

### Q: 如何让高亮框持续更久？

**A:** 增加 `duration` 参数：

```python
highlight_element(
    selector_string="...",
    duration=10.0  # 持续 10 秒
)
```

---

### Q: 如何手动关闭高亮？

**A:** 当前实现是自动关闭。如果需要手动控制，可以使用底层 API：

```python
from core.screen_highlighter import ScreenHighlighter

highlighter = ScreenHighlighter()
highlighter.create_highlight_overlay(rect, color='red')

# ... 做其他操作 ...

highlighter.destroy()  # 手动关闭
```

---

## 未来改进

- [ ] 支持动画效果（闪烁、渐变）
- [ ] 支持点击高亮元素
- [ ] 支持在高亮框上显示文字说明
- [ ] 支持多个元素同时高亮
- [ ] 添加声音提示

---

## 总结

| 功能 | 状态 |
|------|------|
| 实时高亮 | ✅ 已实现 |
| 跟随元素 | ✅ 已实现 |
| 多色支持 | ✅ 5 种颜色 |
| 可调时长 | ✅ 已实现 |
| 自动消失 | ✅ 已实现 |
| MCP 工具集成 | ✅ 已完成 |

**下一步**: 在 Opencode 中测试实际使用场景！
