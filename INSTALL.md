# tdRPA-mcp 安装指南

## 环境要求

- Python 3.8+
- Windows 10/11
- 已安装 tdrpa 相关依赖

## 安装步骤

### 1. 激活虚拟环境

```bash
cd D:\projects\wx-rpa
.venv\Scripts\activate
```

### 2. 安装 MCP SDK 和 PyYAML

由于虚拟环境中没有 pip，使用以下方法之一：

#### 方法 A: 使用系统 pip (推荐)

```bash
# 找到系统 Python 的 pip 路径
where pip

# 如果找到 pip
pip install --target=D:\projects\wx-rpa\.venv\Lib\site-packages mcp pyyaml
```

#### 方法 B: 手动下载安装

1. 下载 mcp 和 pyyaml 的 whl 文件:
   - https://pypi.org/project/mcp/#files
   - https://pypi.org/project/PyYAML/#files

2. 解压到虚拟环境:
```bash
# 将 whl 文件解压到 site-packages
cd D:\projects\wx-rpa\.venv\Lib\site-packages
python -m zipfile -e path\to\mcp-*.whl .
python -m zipfile -e path\to\PyYAML-*.whl .
```

#### 方法 C: 不使用 MCP SDK (快速测试)

如果只需要测试核心功能，可以跳过 MCP SDK 安装，直接运行测试脚本。

### 3. 验证安装

```bash
cd D:\projects\wx-rpa\tdRPA-mcp

# 运行测试
python test_grid_manager.py
python test_cv_prefilter.py
python test_uia_scanner.py
```

## 快速开始

### 方式 1: 独立 Python 脚本

```python
import sys
sys.path.insert(0, r'D:\projects\wx-rpa\tdRPA-mcp')

from core.grid_manager import GridManager
from core.uia_region_scanner import UIARegionScanner

# 1. 创建扫描器
scanner = UIARegionScanner()

# 2. 获取窗口矩形
window_rect = scanner.get_window_rect()
print(f"Desktop: {window_rect}")

# 3. 创建宫格管理器
grid_manager = GridManager(window_rect, rows=4, cols=4)

# 4. 扫描第一个宫格
grid = grid_manager.get_grid_by_id(0)
elements = scanner.scan_grid(grid.to_tuple(), search_depth=2)

print(f"Grid 0 找到 {len(elements)} 个元素")
for elem in elements[:5]:
    print(f"  - {elem.name} ({elem.control_type})")
```

### 方式 2: 使用 MCP 服务 (需要安装 mcp 包)

```bash
python mcp_server.py
```

然后在 MCP 客户端中调用工具。

## 故障排查

### 问题 1: ModuleNotFoundError: No module named 'mcp'

解决方法:
- 按照上述步骤安装 mcp 包
- 或者不使用 MCP 功能，直接导入核心模块

### 问题 2: Cannot find window

确保目标应用已启动:
```python
import subprocess
subprocess.Popen(['notepad.exe'])
import time
time.sleep(2)
```

### 问题 3: 扫描结果为空

尝试增加搜索深度:
```python
elements = scanner.scan_grid(grid_rect, search_depth=5)
```

## 下一步

1. 阅读 [README.md](./README.md) 了解完整功能
2. 运行示例脚本查看效果
3. 在 MCP 客户端中集成使用
