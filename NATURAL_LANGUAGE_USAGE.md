# tdRPA-mcp 自然语言使用指南

## 设计理念

符合人类自然的查找顺序：

```
1. 程序/窗口标题（第一眼看到的）
   ↓
2. 当前激活的区域（微信浏览器 = 当前标签）
   ↓
3. 大致方位（左上、右下、中间 - 9 宫格）
   ↓
4. 显示的文字/图片内容
   ↓
5. selector 精确定位
```

---

## 9 宫格布局

```
┌─────────┬─────────┬─────────┐
│  左上   │  上中   │  右上   │
├─────────┼─────────┼─────────┤
│  左中   │  中间   │  右中   │
├─────────┼─────────┼─────────┤
│  左下   │  下中   │  右下   │
└─────────┴─────────┴─────────┘
```

### 支持的方位词

| 类型 | 方位词 |
|------|--------|
| **标准** | 左上、上中、右上、左中、中间、右中、左下、下中、右下 |
| **别名** | 中心、中央、正中 → 都映射到"中间" |
| **简化** | 左边、右边、上边、下边 |
| **区域** | 上面、下面、左侧、右侧、左上角、右下角 |

---

## MCP 工具使用

### 1. `scan_region(region="...")` - 扫描区域

**最常用！** 使用自然语言描述扫描区域。

#### 示例 1: 扫描左上角
```python
scan_region(region="左上")
```

返回：
```json
{
  "success": true,
  "region_query": "左上",
  "scanned_grids": [0],
  "position_names": ["左上"],
  "element_count": 5,
  "elements": [
    {"name": "微信", "control_type": "ButtonControl", "grid_id": 0},
    {"name": "通讯录", "control_type": "ButtonControl", "grid_id": 0},
    ...
  ]
}
```

#### 示例 2: 扫描上面一整行
```python
scan_region(region="上面")
```

返回 3 个宫格（左上、上中、右上）的所有元素。

#### 示例 3: 扫描中间
```python
scan_region(region="中间")
```

#### 示例 4: 使用宫格编号（精确控制）
```python
scan_region(grid_id=4)  # 中间宫格
```

---

### 2. `find_element_selector(selector="...")` - 精确查找

使用 tdSelector 语法精确定位元素。

#### 示例：查找微信的搜一搜按钮
```python
find_element_selector("""
[
  { 'wnd' : [ ('Text' , '微信') ] },
  { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }
]
""")
```

返回：
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

---

## LLM 使用流程

### 场景 1: "帮我找微信左上角的按钮"

**Step 1:** LLM 调用 `scan_region(region="左上")`

**Step 2:** 分析返回的元素列表
```json
{
  "elements": [
    {"name": "微信", "control_type": "ButtonControl"},
    {"name": "通讯录", "control_type": "ButtonControl"},
    {"name": "收藏", "control_type": "ButtonControl"}
  ]
}
```

**Step 3:** LLM 识别出有"微信"、"通讯录"、"收藏"三个按钮

**Step 4:** LLM 回复用户：
> "在微信窗口的左上角，我找到了以下按钮：
> - 微信
> - 通讯录
> - 收藏
> 
> 您想点击哪一个？"

---

### 场景 2: "点击微信的搜一搜按钮"

**Step 1:** LLM 先扫描相关区域
```python
scan_region(region="左侧")  # 搜一搜通常在左侧
```

**Step 2:** 从返回结果中找到"搜一搜"按钮的信息

**Step 3:** 构建 selector 精确定位
```python
find_element_selector("""
[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]
""")
```

**Step 4:** 获取位置信息后，执行点击操作

---

### 场景 3: "微信浏览器当前标签页的内容"

**Step 1:** 设置目标窗口
```python
set_focus_window(process_name="Weixin.exe")
```

**Step 2:** 扫描中间区域（通常是主要内容区）
```python
scan_region(region="中间")
```

**Step 3:** 分析返回的元素，提取文本内容

**Step 4:** 回复用户看到的内容

---

## 最佳实践

### ✅ 推荐做法

1. **先用 `scan_region` 大致扫描**
   ```python
   # 先看左边有什么
   scan_region(region="左侧")
   ```

2. **再用 `find_element_selector` 精确定位**
   ```python
   # 找到具体的按钮
   find_element_selector("[...]")
   ```

3. **使用简单的方位词**
   ```python
   scan_region(region="左上")     # ✓ 好
   scan_region(region="左上方")   # ✓ 也支持
   scan_region(grid_id=0)         # ✓ 精确但不直观
   ```

### ❌ 避免的做法

1. **不要一开始就用复杂的 selector**
   ```python
   # ✗ 不推荐：直接写 6 层 selector
   find_element_selector("[{ 'wnd': [...] }, { 'ctrl': [...] }, ...]")
   
   # ✓ 推荐：先扫描看看有什么
   scan_region(region="中间")
   ```

2. **不要依赖 16 宫格编号**
   ```python
   # ✗ 不直观
   scan_region(grid_id=7)
   
   # ✓ 更自然
   scan_region(region="下中")
   ```

---

## 常见问题

### Q: 为什么用 9 宫格而不是 16 宫格？

**A:** 9 宫格更符合人类直觉：
- 人说"左上角"比说"第 0 号宫格"自然
- 人说"中间"比说"第 4 号宫格"容易理解
- 16 宫格太细，反而不容易精确定位

### Q: 如果 9 宫格不够精确怎么办？

**A:** 可以切换到 16 宫格模式：
```python
# 在 set_focus_window 时指定
set_focus_window(..., grid_rows=4, grid_cols=4)
```

但大多数情况下 9 宫格已经足够。

### Q: 如何知道某个区域有哪些元素？

**A:** 使用 `scan_region`：
```python
# 扫描上面
result = scan_region(region="上面")

# 查看所有元素
for elem in result['elements']:
    print(f"- {elem['name']} ({elem['control_type']})")
```

### Q: 方位词识别不准确怎么办？

**A:** 可以尝试：
1. 使用不同的同义词（"中间"、"中心"、"中央"都可以）
2. 直接使用宫格编号
3. 用区域描述（"上面"、"左侧"会返回多个宫格）

---

## 完整示例代码

### 示例 1: 查找并点击微信的"发现"按钮

```python
# Step 1: 扫描左侧（发现按钮通常在左侧导航栏）
result = scan_region(region="左侧")

# Step 2: 从结果中找到"发现"或"朋友圈"
for elem in result['elements']:
    if '发现' in elem['name'] or '朋友圈' in elem['name']:
        target = elem
        break

# Step 3: 构建 selector 精确定位
selector = f"""
[
  {{ 'wnd' : [ ('Text' , '微信') ] }},
  {{ 'ctrl' : [ ('Text' , '{target['name']}'), ('aaRole' , 'PushButton') ] }}
]
"""

# Step 4: 获取位置
result = find_element_selector(selector)
print(f"找到按钮位置：{result['element']['bounding_rect']}")

# Step 5: 执行点击（未来功能）
# click_at(result['element']['center_point'])
```

### 示例 2: 读取记事本内容

```python
# Step 1: 设置目标窗口
set_focus_window(process_name="notepad.exe")

# Step 2: 扫描中间区域（文本编辑区）
result = scan_region(region="中间")

# Step 3: 提取文本元素
text_elements = [
    elem for elem in result['elements']
    if elem['control_type'] == 'EditControl'
]

if text_elements:
    print(f"找到文本框：{text_elements[0]}")
```

---

## 总结

tdRPA-mcp 的核心设计：

| 工具 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `scan_region` | 扫描区域 | "左上"、"中间"等 | 元素列表 |
| `find_element_selector` | 精确定位 | tdSelector 语法 | 位置信息 |

LLM 的作用：
1. 理解用户的自然语言
2. 决定调用哪个工具
3. 解释返回的结果
4. 回复用户

这种设计让交互更自然，符合人类的认知习惯！
