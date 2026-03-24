# 微信"搜一搜"按钮分析

## ✅ 确认找到

使用以下 selector 可以成功定位"搜一搜"按钮：

```python
selector = """[
  { 'wnd' : [ ('Text' , '微信') ] }, 
  { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }
]"""
```

---

## 📊 元素详细属性

| 属性 | 值 | 说明 |
|------|-----|------|
| **Name** | `'搜一搜'` | ✅ 文本标签 |
| **ControlType** | `ButtonControl` | ✅ 按钮类型 |
| **AutomationId** | `''` | ❌ 空（无唯一标识） |
| **ClassName** | `mmui::XTabBarItem` | ⚠️ 微信自定义选项卡 |
| **IsEnabled** | `True` | ✅ 可用状态 |
| **IsVisible** | `None` | - |
| **IsKeyboardFocusable** | `False` | ❌ 不支持键盘聚焦 |

---

## 📍 位置信息

```
左上角：(16, 513)
右下角：(91, 558)
宽度：75px
高度：45px
中心点：(53, 535)
```

**可视化：**

```
微信窗口左侧区域:
┌─────────────────────┐
│                     │
│   [其他按钮]        │
│                     │
├─────────────────────┤ ← y=513
│ ★ 搜一搜            │ ← 目标 (16,513)-(91,558)
│   (75x45px)         │
│   中心点：(53,535)  │
└─────────────────────┘
     ↑
   x=16 到 x=91
```

---

## 🔍 关键发现

### 1. 不是纯图标按钮

- ✅ **有文字标签**：Name 属性 = "搜一搜"
- ⚠️ **但不是标准按钮**：ClassName = `mmui::XTabBarItem`
- ❌ **没有 AutomationId**：无法通过 ID 定位

### 2. 子元素结构

```
搜一搜 (ButtonControl)
├── GroupControl (无名称)
└── GroupControl (无名称)
```

可能是：
- 一个 Group 包含图标
- 另一个 Group 包含文字

### 3. 控件类型映射

tdSelector 中的 `aaRole='PushButton'` 可以匹配到：
- `ButtonControl` ✅
- 即使 ClassName 是自定义的 `mmui::XTabBarItem`

这是因为我们的映射逻辑将 `ControlTypeName='ButtonControl'` 映射为 `aaRole='Button'`，然后特殊处理了 `PushButton` → `Button` 的映射。

---

## 💡 使用建议

### 最佳实践

```python
# ✅ 推荐：使用 Text + aaRole 组合
selector = """[
  { 'wnd' : [ ('Text' , '微信') ] }, 
  { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }
]"""

# 调用 MCP 工具高亮
highlight_element(
    selector_string=selector,
    duration=3.0,
    color='red'
)
```

### 备选方案

如果上述 selector 失效（微信版本更新），可以尝试：

```python
# 方案 2: 只通过名称查找
selector = """[
  { 'wnd' : [ ('Text' , '微信') ] }, 
  { 'ctrl' : [ ('Text' , '搜一搜') ] }
]"""

# 方案 3: 通过 ClassName
selector = """[
  { 'wnd' : [ ('Text' , '微信') ] }, 
  { 'ctrl' : [ ('ClassName' , 'mmui::XTabBarItem'), ('Text' , '搜一搜') ] }
]"""

# 方案 4: 通过位置推断（左侧特定区域）
# 先扫描左侧区域，然后找第 N 个按钮
result = scan_region(region="左侧")
# 从结果中识别"搜一搜"
```

---

## ⚠️ 注意事项

### 1. 微信版本差异

不同版本的微信可能有不同的：
- ClassName（如 `mmui::Button`、`CefWindow` 等）
- 界面布局（左侧、顶部、底部）
- 文字内容（可能显示"搜索"而不是"搜一搜"）

### 2. 界面状态影响

"搜一搜"按钮可能在以下情况不显示：
- 微信未登录
- 最小化状态
- 某些特定的聊天或功能界面
- 被其他 UI 元素遮挡

### 3. 纯图标模式

某些微信版本可能：
- 只显示图标，没有文字标签（Name 为空）
- 需要使用图像识别（OCR 或模板匹配）

---

## 🛠️ 调试技巧

### 如果找不到"搜一搜"

```python
# Step 1: 确认微信窗口存在
root = scanner.auto.GetRootControl()
for child in root.GetChildren():
    if '微信' in getattr(child, 'Name', ''):
        print(f"找到微信窗口：{child.Name}")

# Step 2: 扫描整个窗口查看所有按钮
elements = scanner.scan_grid(wechat_rect, search_depth=5)
buttons = [e for e in elements if 'Button' in e.control_type]

print(f"找到 {len(buttons)} 个按钮:")
for btn in buttons:
    print(f"  - Name='{btn.name}', Class={btn.class_name}")

# Step 3: 查找所有包含"搜"的元素
susou = [b for b in buttons if '搜' in (b.name or '')]
if susou:
    print(f"找到 {len(susou)} 个相关按钮")
else:
    print("当前界面没有'搜一搜'按钮")
```

---

## 📝 总结

| 问题 | 答案 |
|------|------|
| "搜一搜"是纯图标吗？ | ❌ 不是，有 Name 属性="搜一搜" |
| 可以用 Text 定位吗？ | ✅ 可以，Name 属性就是"搜一搜" |
| 需要图像识别吗？ | ❌ 不需要，UIA 可以直接访问 |
| AutomationId 是什么？ | ❌ 空，不能使用 ID 定位 |
| ClassName 是什么？ | `mmui::XTabBarItem`（自定义） |
| 最佳 selector 是什么？ | `[{ 'wnd': [...] }, { 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]` |

---

**测试时间**: 2026-03-24  
**测试结果**: ✅ 成功定位  
**元素类型**: 自定义选项卡按钮（有文字标签）
