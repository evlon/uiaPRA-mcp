# tdRPA-mcp 快速开始

## 5 分钟快速体验

### 1. 运行演示脚本

```bash
cd D:\projects\wx-rpa\tdRPA-mcp
D:\projects\wx-rpa\.venv\Scripts\python.exe demo_grid_scan.py
```

你将看到 16 宫格扫描的完整过程演示。

### 2. 核心功能测试

```bash
# 测试宫格管理
D:\projects\wx-rpa\.venv\Scripts\python.exe test_grid_manager.py

# 测试 CV 预筛选
D:\projects\wx-rpa\.venv\Scripts\python.exe test_cv_prefilter.py

# 测试 UIA 扫描
D:\projects\wx-rpa\.venv\Scripts\python.exe test_uia_scanner.py
```

### 3. 代码示例

创建一个简单的 Python 脚本:

```python
# my_test.py
import sys
sys.path.insert(0, r'D:\projects\wx-rpa\tdRPA-mcp')

from core.grid_manager import GridManager
from core.uia_region_scanner import UIARegionScanner
import time

print("=== 16 宫格元素扫描 ===\n")

# 1. 扫描整个桌面
print("[1] 初始化扫描器...")
scanner = UIARegionScanner()
print(f"    根元素：{scanner.root_element.Name}\n")

# 2. 创建宫格
print("[2] 创建 16 宫格...")
window_rect = scanner.get_window_rect()
grid_manager = GridManager(window_rect, rows=4, cols=4)
print(f"    窗口大小：{window_rect[2]-window_rect[0]} x {window_rect[3]-window_rect[1]}\n")

# 3. 扫描中心 4 个宫格
print("[3] 扫描中心区域 (Grid 5,6,9,10)...")
for grid_id in [5, 6, 9, 10]:
    grid = grid_manager.get_grid_by_id(grid_id)
    
    start = time.time()
    elements = scanner.scan_grid(grid.to_tuple(), search_depth=2)
    elapsed = (time.time() - start) * 1000
    
    print(f"    Grid {grid_id}: {len(elements)} 个元素，耗时 {elapsed:.0f}ms")
    
    # 显示找到的第一个元素
    if elements:
        elem = elements[0]
        print(f"           示例：{elem.name} ({elem.control_type})")

print("\n=== 完成 ===")
```

运行:
```bash
D:\projects\wx-rpa\.venv\Scripts\python.exe my_test.py
```

### 4. 扫描特定窗口

```python
import subprocess
import time

# 启动记事本
print("打开记事本...")
subprocess.Popen(['notepad.exe'])
time.sleep(2)  # 等待窗口打开

# 扫描记事本窗口
from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager

scanner = UIARegionScanner(process_name='notepad.exe')
print(f"找到窗口：{scanner.root_element.Name}")

# 创建宫格
window_rect = scanner.get_window_rect()
grid_manager = GridManager(window_rect)

# 扫描第一个宫格
grid = grid_manager.get_grid_by_id(0)
elements = scanner.scan_grid(grid.to_tuple(), search_depth=3)

print(f"\n左上角宫格找到 {len(elements)} 个元素:")
for elem in elements[:5]:
    print(f"  - {elem.name} ({elem.control_type})")
```

## 核心 API 速查

### GridManager (宫格管理)

```python
from core.grid_manager import GridManager

# 创建
grid_manager = GridManager(window_rect=(0,0,1920,1080), rows=4, cols=4)

# 获取宫格
grid = grid_manager.get_grid_by_id(5)
grid = grid_manager.get_grid_by_position(x=960, y=540)

# 获取扩散顺序
order = grid_manager.get_diffusion_order(focus_grid_id=5)
# 返回：[5, 0, 1, 2, 4, 6, 8, 9, 10, 3, 7, 11, 12, 13, 14, 15]

# 获取所有宫格
grids = grid_manager.get_all_grids()
```

### UIARegionScanner (UIA 扫描)

```python
from core.uia_region_scanner import UIARegionScanner

# 创建扫描器
scanner = UIARegionScanner()  # 从 Desktop 开始
scanner = UIARegionScanner(process_name='notepad.exe')  # 指定进程

# 扫描宫格
elements = scanner.scan_grid(grid_rect, search_depth=2)

# 获取窗口矩形
rect = scanner.get_window_rect()
```

### CVPreFilter (CV 预筛选)

```python
from core.cv_prefilter import CVPreFilter
import pyautogui

cv = CVPreFilter(threshold=0.01)

# 截图
img = cv.screenshot_grid((0, 0, 480, 270))

# 检测活跃度
score = cv.detect_ui_activity(img)

# 筛选活跃区域
grids = [(0,0,480,270), (480,0,960,270), ...]
active_ids = cv.filter_active_grids(grids)
```

## 常见问题

### Q1: 如何指定扫描特定窗口？
```python
scanner = UIARegionScanner(process_name='WeChat.exe')
# 或
scanner = UIARegionScanner(window_title='微信')
```

### Q2: 扫描速度太慢怎么办？
1. 减少 search_depth: `scan_grid(..., search_depth=1)`
2. 只扫描焦点区域：使用 `scan_focus_area(layers=1)` 而非全量扫描
3. 启用 CV 预筛选：跳过空白宫格

### Q3: 找不到元素？
1. 增加 search_depth: `scan_grid(..., search_depth=5)`
2. 检查窗口是否正确：确保进程名/窗口标题匹配
3. 关闭其他窗口：避免干扰

### Q4: 如何使用 MCP 服务？
需要先安装 mcp 包:
```bash
pip install mcp
python mcp_server.py
```

然后在支持的 MCP 客户端中调用工具。

## 参考资料

- [完整文档](README.md)
- [安装指南](INSTALL.md)
- [项目总结](PROJECT_SUMMARY.md)
- [测试脚本](test_*.py)
