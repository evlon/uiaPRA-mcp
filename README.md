# tdRPA-mcp

基于 tdrpa 的 UIA 元素查找 MCP 服务，通过 16 宫格分区域扫描 + 焦点扩散策略，显著提升 UI 元素查找速度。

## 核心特性

- **16 宫格分区**: 将窗口区域划分为 4x4 网格，实现分区域扫描
- **焦点扩散**: 从焦点位置开始，按分层顺序向四周扩散 (焦点 → 相邻 8 格 → 外围 7 格)
- **CV 预筛选**: 使用 OpenCV 快速识别 UI 活跃区域，跳过空白宫格
- **双模式查询**: 支持自然语言描述和 tdSelector 语法两种查询方式
- **结果缓存**: 缓存扫描结果，支持增量更新

## 安装

```bash
# 进入项目目录
cd tdRPA-mcp

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 启动 MCP 服务

```bash
python mcp_server.py
```

### 2. 在 MCP 客户端中使用

#### 设置目标窗口

```python
# 通过进程名设置
set_focus_window(process_name="notepad.exe")

# 或通过窗口标题设置
set_focus_window(window_title="无标题 - 记事本")
```

#### 查找元素

```python
# 方式 1: 自然语言描述
result = find_element_natural("记事本的保存按钮")

# 方式 2: 使用 selector 语法
result = find_element_selector(
    "[{'wnd': [('Text', '无标题 - 记事本'), ('App', 'notepad.exe')]}]"
)

# 方式 3: 直接拾取指定宫格的元素
result = pick_grid_element(grid_id=5, element_index=0)
```

#### 扫描宫格

```python
# 扫描所有宫格
result = scan_all_grids(layers=2)  # layers: 0=焦点，1=焦点 + 相邻，2=全部

# 扫描单个宫格
result = scan_grid_region(grid_id=5, search_depth=2)

# 列出所有宫格
result = list_grids(show_elements=True)
```

## 项目结构

```
tdRPA-mcp/
├── mcp_server.py              # MCP 服务入口
├── config.yaml                # 配置文件
├── requirements.txt           # 依赖列表
├── core/
│   ├── grid_manager.py        # 16 宫格管理器
│   ├── cv_prefilter.py        # CV 预筛选模块
│   ├── uia_region_scanner.py  # UIA 区域扫描器
│   └── focus_diffusion.py     # 焦点扩散算法
├── tools/
│   ├── element_finder.py      # 自然语言查找工具
│   ├── selector_query.py      # selector 语法查询工具
│   └── grid_picker.py         # 宫格拾取器
└── utils/
    └── selector_parser.py     # selector 语法解析
```

## MCP 工具列表

| 工具名 | 说明 |
|--------|------|
| `set_focus_window` | 设置目标扫描窗口 |
| `find_element_natural` | 自然语言描述查找元素 |
| `find_element_selector` | tdSelector 语法查找元素 |
| `pick_grid_element` | 拾取指定宫格的元素 |
| `scan_grid_region` | 扫描指定宫格区域 |
| `scan_all_grids` | 扫描所有宫格 |
| `list_grids` | 列出所有宫格信息 |
| `set_focus_point` | 设置焦点坐标 |
| `get_status` | 获取服务状态 |
| `clear_cache` | 清除缓存 |

## 性能优化

### 1. 分层扫描策略

```python
# 只扫描焦点附近区域 (最快)
find_element_natural("按钮", layers=0)  # 只扫描焦点宫格
find_element_natural("按钮", layers=1)  # 扫描焦点 + 相邻 8 宫格 (推荐)
find_element_natural("按钮", layers=2)  # 扫描全部 16 宫格
```

### 2. CV 预筛选

在 `config.yaml` 中启用 CV 预筛选:

```yaml
scanning:
  cv_prefilter: true
  cv_threshold: 0.01  # 活跃度阈值，小于此值的区域将被跳过
```

### 3. 并行扫描

```yaml
scanning:
  parallel_scan: true  # 使用多线程并行扫描
```

## 示例

### 示例 1: 查找记事本的保存按钮

```python
# 1. 设置目标窗口
set_focus_window(process_name="notepad.exe")

# 2. 查找保存按钮
result = find_element_natural("保存按钮", layers=1)

# 输出:
# {
#     "found": true,
#     "element": {
#         "name": "保存",
#         "control_type": "Button",
#         "bounding_rect": [350, 20, 400, 50],
#         "grid_id": 2
#     },
#     "scan_stats": {
#         "scanned_grids": 9,
#         "total_elements": 45,
#         "scan_time_ms": 156.3
#     }
# }
```

### 示例 2: 使用 selector 语法精确查找

```python
result = find_element_selector(
    "[{'wnd': [('Text', '微信'), ('App', 'WeChat.exe')]}, "
    "{'ctrl': [('Text', '发送'), ('ControlType', 'Button')]}]"
)
```

### 示例 3: 遍历宫格查找元素

```python
# 1. 列出所有宫格
grids = list_grids(show_elements=False)

# 2. 逐个宫格拾取元素
for grid_id in range(16):
    result = pick_grid_element(grid_id=grid_id, element_index=0)
    if result['success']:
        print(f"Grid {grid_id}: {result['element']['name']}")
```

## 技术原理

### 16 宫格划分

```
┌───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │
├───┼───┼───┼───┤
│ 4 │ 5 │ 6 │ 7 │
├───┼───┼───┼───┤
│ 8 │ 9 │10 │11 │
├───┼───┼───┼───┤
│12 │13 │14 │15 │
└───┴───┴───┴───┘
```

### 焦点扩散顺序 (以 grid_id=5 为例)

```
Layer 0: [5]              # 焦点
Layer 1: [1,4,6,9,0,2,8,10]  # 相邻 8 格
Layer 2: [3,7,11,13,12,14,15] # 外围 7 格
```

### CV 活跃度检测

使用 Canny 边缘检测算法计算每个宫格的边缘密度:

```python
activity_score = edge_pixels / total_pixels
```

活跃度低于阈值的宫格将被跳过，显著减少扫描时间。

## 依赖

- `mcp`: MCP SDK
- `tdrpa.tdcore`: UIA 元素定位
- `opencv-python`: CV 预筛选
- `pyautogui`: 屏幕截图
- `numpy`: 数值计算
- `pywin32`: Windows API

## 注意事项

1. **首次使用**: 需要先调用 `set_focus_window` 设置目标窗口
2. **权限**: 需要管理员权限访问某些系统应用的 UI 元素
3. **Chrome 应用**: 需要启用 `--force-renderer-accessibility` 参数
4. **性能**: 建议优先使用 `layers=1` 模式，只扫描焦点附近区域

## 故障排查

### 问题 1: 找不到目标窗口

```python
# 检查进程名是否正确
import psutil
[p.info['name'] for p in psutil.process_iter(['name'])]
```

### 问题 2: 扫描结果为空

- 检查 CV 阈值是否过高：降低 `cv_threshold`
- 检查搜索深度：增加 `search_depth` 参数
- 关闭 CV 预筛选：设置 `use_cv_prefilter=False`

### 问题 3: 扫描速度慢

- 启用并行扫描：`parallel_scan: true`
- 减少扫描层数：使用 `layers=0` 或 `layers=1`
- 启用结果缓存：避免重复扫描相同区域

## License

MIT License

## Contact

- Email: thingswell@qq.com
- WeChat: haijun-data
