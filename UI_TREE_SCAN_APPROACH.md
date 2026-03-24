# UI 树扫描方法 - 更可靠的元素查找

## 问题背景

传统的 `scan_grid` 方法的问题：
1. ❌ 只扫描区域内的扁平元素列表
2. ❌ 没有层次结构信息
3. ❌ 大量重复元素（父子重叠）
4. ❌ 难以理解界面整体结构

## 新的解决方案

### 核心思路

```
1. 获取完整的 UI 树（所有元素，不过滤）
   ↓
2. 将每个元素映射到对应的 9 宫格位置
   ↓
3. 按宫格分组排序（同一位置的元素去重）
   ↓
4. 返回结构化的元素列表
```

---

## 实现架构

### 新增模块：`core/ui_tree_scanner.py`

```python
class UITreeScanner:
    """UI 树扫描器"""
    
    def scan_full_tree(max_depth=15):
        """扫描完整的 UI 树"""
        
    def get_elements_by_grid():
        """按宫格分组返回元素"""
        
    def get_sorted_elements(deduplicate=True):
        """获取排序并去重后的元素列表"""
```

### 关键特性

#### 1. 完整扫描
```python
def scan_full_tree(max_depth=15):
    # 遍历整个 UI 树
    traverse(root_element, depth=0)
    
    # 保留所有有实际尺寸的元素
    if width > 0 and height > 0:
        elements.append(ui_elem)
```

#### 2. 宫格映射
```python
def _assign_to_grid(ui_elem):
    # 根据元素中心点确定所属宫格
    x, y = ui_elem.center_point
    grid = grid_manager.get_grid_by_position(x, y)
    ui_elem.grid_id = grid.id
    ui_elem.grid_position = "左上" / "中间" / "右下" ...
```

#### 3. 智能去重
```python
def _deduplicate_elements(elements):
    # 计算 IoU (Intersection over Union)
    overlap = calculate_overlap(rect1, rect2)
    
    # 如果重叠度 > 90%，认为是重复
    if overlap > 0.9:
        remove_duplicate()
```

---

## 使用示例

### 在 MCP 工具中

```python
@mcp.tool()
async def scan_region(
    region: str = "左中",
    use_ui_tree: bool = True  # 默认启用 UI 树扫描
):
    # 使用 UI 树扫描
    ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
    all_elements = ui_scanner.scan_full_tree()
    
    # 过滤出目标宫格的元素
    target_elements = [
        e for e in all_elements 
        if e.grid_id == target_grid_id
    ]
    
    return {"elements": target_elements}
```

### 调用示例

```python
# 扫描左侧区域
result = scan_region(region="左侧")

# 返回结果包含宫格信息
{
  "scanned_grids": [
    {"id": 0, "position_name": "左上"},
    {"id": 3, "position_name": "左中"},
    {"id": 6, "position_name": "左下"}
  ],
  "element_count": 17,
  "elements": [
    {
      "name": "搜一搜",
      "control_type": "ButtonControl",
      "grid_id": 3,
      "grid_position": "左中",
      "bounding_rect": [16, 513, 91, 558]
    },
    ...
  ]
}
```

---

## 测试结果对比

### 测试场景：微信窗口

| 指标 | scan_grid | UI 树扫描 |
|------|-----------|-----------|
| **元素总数** | 131 个 | 77 个 |
| **去重后** | N/A | 47 个 |
| **有宫格位置** | N/A | 77 个 (100%) |
| **找到"搜一搜"** | ✅ | ✅ |
| **层次结构** | ❌ | ✅ |
| **执行速度** | 快 | 中等 |

### 关键发现

```
UI 树扫描成功找到 "搜一搜" 按钮:
  名称：'搜一搜'
  所在宫格：左中 (Grid 3)  ← 正确！
  位置：(16, 513, 91, 558)
  中心点：(53, 535)
```

---

## 优势分析

### ✅ UI 树扫描的优势

1. **完整的层次结构**
   - 知道元素的父子关系
   - 可以理解界面组织方式

2. **自动去重**
   - 移除重叠的冗余元素
   - 返回更精确的结果

3. **宫格分组**
   - 元素按位置自然分组
   - 符合人类的空间认知

4. **更好的可解释性**
   - 每个元素都有明确的宫格位置
   - 可以说"左上角的按钮"而不是"第 5 个元素"

5. **更智能的搜索**
   - 可以基于位置推理（"应该在左边"）
   - 可以结合父子关系判断

### ⚠️ 注意事项

1. **性能考虑**
   - UI 树扫描稍慢（需要遍历整棵树）
   - 但对于一般界面（<1000 元素）影响很小

2. **深度选择**
   - `max_depth` 太大可能包含太多无用元素
   - 建议值：10-15

3. **回退机制**
   - 保留了旧的 `scan_grid` 方法
   - 可以通过 `use_ui_tree=False` 切换

---

## 最佳实践

### 推荐用法

```python
# ✅ 推荐：使用 UI 树扫描
result = scan_region(region="左上", use_ui_tree=True)

# 查找特定元素
buttons = [e for e in result['elements'] if 'Button' in e['control_type']]

# 按宫格查看
from collections import defaultdict
by_grid = defaultdict(list)
for elem in result['elements']:
    by_grid[elem['grid_position']].append(elem)
```

### 调试技巧

```python
# 获取统计信息
stats = ui_scanner.get_statistics()
print(f"总元素数：{stats['total_elements']}")
print(f"按宫格分布：{stats['by_grid']}")
print(f"按类型分布：{stats['by_control_type']}")

# 查看某个宫格的所有元素
grid_elements = ui_scanner.get_elements_by_grid()[target_grid_id]
for elem in grid_elements:
    print(f"  - {elem.name} ({elem.control_type})")
```

---

## 未来改进

- [ ] 支持增量扫描（只扫描变化的部分）
- [ ] 添加更多去重策略（基于相似度）
- [ ] 支持语义分组（如"导航栏"、"内容区"）
- [ ] 缓存 UI 树结构，提高性能
- [ ] 可视化 UI 树结构

---

## 总结

| 特性 | 传统方法 | UI 树扫描 |
|------|----------|-----------|
| 层次结构 | ❌ | ✅ |
| 去重 | ❌ | ✅ |
| 宫格分组 | 手动 | 自动 |
| 可解释性 | 低 | 高 |
| 性能 | 快 | 中等 |

**结论**: UI 树扫描提供了更可靠、更可解释的元素查找方式，特别适合作为 LLM 的工具使用。
