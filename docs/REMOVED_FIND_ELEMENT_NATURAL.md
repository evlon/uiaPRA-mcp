# 移除 find_element_natural 接口说明

## 决策日期
2026-03-25

## 决策原因

经过分析，决定**移除** `find_element_natural()` 接口，理由如下：

### 1. ❌ LLM 不需要自然语言转换层

**问题**: `find_element_natural()` 试图将自然语言（如"微信的发送按钮"）转换为 selector，但这个转换层对 LLM 来说是多余的。

**原因**:
- LLM 完全有能力自己生成结构化的过滤条件
- 黑盒转换过程不透明，LLM 无法控制转换逻辑
- 转换错误时难以调试和修正

**更好的方式**:
```python
# ❌ 不推荐：黑盒转换
result = await find_element_natural("微信的发送按钮")

# ✅ 推荐：LLM 自主生成结构化条件
result = await filter_ui_elements(
    grid_positions=["左中", "左上"],
    name_contains="发送",
    control_types=["ButtonControl"]
)
```

---

### 2. ❌ 实现复杂且容易出错

**当前实现的问题**:

```python
# 从描述中提取关键词（过于简单）
keywords = description.lower().split()

# 硬编码的控件类型映射
if '按钮' in description and 'Button' in elem.control_type:
    match = True
elif '菜单' in description and 'Menu' in elem.control_type:
    match = True
elif '编辑' in description and 'Edit' in elem.control_type:
    match = True
```

**问题清单**:
- 关键词分割过于粗糙（"发送按钮" → ["发送按钮"]，无法拆分）
- 控件类型映射不完整（只有 3 种）
- 不支持否定条件（"不是红色的按钮"）
- 不支持复合条件（"左侧的保存或取消按钮"）
- 中文/英文混合处理困难

**维护成本**: 每支持一种新的控件类型或语义模式，都需要修改代码。

---

### 3. ✅ `get_ui_tree_data() + filter_ui_elements()` 组合更灵活精确

**优势对比**:

| 特性 | find_element_natural | get_ui_tree_data + filter |
|------|---------------------|---------------------------|
| 透明度 | 黑盒，不可控 | 白盒，完全可控 |
| 灵活性 | 固定匹配逻辑 | 任意条件组合 |
| 精确度 | 低（简单关键词匹配） | 高（结构化过滤） |
| 可调试性 | 差（错误难定位） | 好（每步可验证） |
| LLM 友好度 | 低（被动接受结果） | 高（主动生成条件） |
| 维护成本 | 高（需持续优化） | 低（规则通用） |

**示例对比**:

```python
# ❌ find_element_natural - 不精确
result = await find_element_natural("左边那个绿色的发送按钮")
# → 可能匹配失败，因为"绿色"、"左边"等语义无法解析

# ✅ filter_ui_elements - 精确控制
result = await filter_ui_elements(
    grid_positions=["左中", "左上"],
    name_contains="发送",
    control_types=["ButtonControl"]
)
# → LLM 可以明确指定所有已知条件
```

---

### 4. ✅ 减少接口数量，降低维护成本

**接口精简前后对比**:

**之前** (7 个查找接口):
```python
set_focus_window()
list_windows()
get_ui_tree_data()
filter_ui_elements()
find_element_natural()      # ← 移除
scan_region()
pick_grid_element()
```

**之后** (6 个查找接口):
```python
set_focus_window()
list_windows()
get_ui_tree_data()
filter_ui_elements()
scan_region()
pick_grid_element()
```

**维护成本降低**:
- 减少 1 个接口的测试和维护
- 减少 1 份文档需要更新
- 减少用户选择困惑（少一个容易出错的选项）

---

## LLM 应该如何做

### 推荐模式：LLM 自主生成过滤条件

```python
# Step 1: 获取 UI 树数据
ui_data = await get_ui_tree_data(max_depth=15)

# Step 2: LLM 分析并生成过滤条件
# （LLM 根据用户描述和 UI 树结构，自主决定过滤条件）
conditions = {
    "grid_positions": ["左中"],
    "name_contains": "发送",
    "control_types": ["ButtonControl"]
}

# Step 3: 执行过滤
result = await filter_ui_elements(**conditions)

# Step 4: 执行操作
if result["result_count"] > 0:
    await click_element(element_index=0)
```

### 为什么这样更好？

1. **透明**: LLM 完全知道使用了什么条件
2. **可控**: 可以随时调整过滤策略
3. **可学习**: 从成功/失败案例中学习改进条件生成
4. **可组合**: 可以多次调用、组合结果

---

## 迁移指南

### 如果你之前使用 `find_element_natural()`:

**旧代码**:
```python
result = await find_element_natural("微信的搜索按钮")
```

**新代码**:
```python
# 方案 A: 直接过滤（推荐）
result = await filter_ui_elements(
    name_contains="搜索",
    control_types=["ButtonControl"]
)

# 方案 B: 先获取 UI 树，再让 LLM 决定如何过滤
ui_data = await get_ui_tree_data()
# LLM 分析后生成更精确的条件
result = await filter_ui_elements(
    grid_positions=["右上"],
    name_contains="搜"
)
```

---

## 相关文件修改

### 已删除
- `tools/element_finder.py` - 整个文件删除

### 已修改
- `mcp_server.py` - 移除 `register_element_finder()` 调用
- `mcp_server.py` - 更新 MCP instructions，移除"自然语言"描述

### 需要更新（后续）
- `README.md` - 移除相关示例
- 测试文件 - 删除依赖此接口的测试

---

## 总结

**核心思想**: 

> 让 LLM 做它擅长的事（理解语义、生成结构化条件），  
> 让工具做它擅长的事（执行精确过滤、提供可靠结果）。

**不要**:
- 在工具里封装复杂的语义理解逻辑
- 替 LLM 做决策
- 创建不透明的黑盒接口

**要**:
- 提供透明、可控的基础接口
- 让 LLM 自主生成查询条件
- 保持接口的简单性和可组合性

---

**决策者**: Lingma AI Assistant  
**依据**: 用户反馈 + 架构优化分析  
**状态**: ✅ 已完成移除
