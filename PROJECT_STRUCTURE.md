# tdRPA-mcp 项目目录结构

```
tdRPA-mcp/
│
├── 📄 核心文件
│   ├── mcp_server.py              # MCP 服务主入口
│   ├── __init__.py                # 包初始化
│   ├── config.yaml                # 配置文件
│   └── opencode-mcp-config.json   # Opencode MCP 配置
│
├── 📦 核心模块 (core/)
│   ├── __init__.py
│   ├── grid_manager.py            # 9 宫格管理器（支持自然语言方位）
│   ├── uia_region_scanner.py      # UIA 区域扫描器
│   ├── cv_prefilter.py            # CV 预筛选（可选）
│   └── focus_diffusion.py         # 焦点扩散扫描（可选）
│
├── 🛠️ 工具模块 (tools/)
│   ├── __init__.py
│   ├── grid_picker.py             # 宫格拾取工具（含 scan_region）
│   ├── element_finder.py          # 自然语言元素查找
│   └── selector_query.py          # Selector 语法查询
│
├── 🔧 工具类 (utils/)
│   ├── __init__.py
│   └── selector_parser.py         # Selector 解析器
│
├── 🧪 测试目录 (tests/)
│   ├── README.md                  # 测试说明
│   ├── run_all_tests.py           # 运行所有测试
│   └── test_wechat_9grid.py       # 微信 9 宫格测试示例
│
├── 📖 文档
│   ├── README.md                      # 项目说明
│   ├── INSTALL.md                     # 安装指南
│   ├── QUICKSTART.md                  # 快速开始
│   ├── MCP_USAGE_GUIDE.md             # MCP 使用指南
│   ├── NATURAL_LANGUAGE_USAGE.md      # 自然语言使用指南 ⭐
│   ├── PROJECT_SUMMARY.md             # 项目总结
│   ├── REGISTER_TO_OPENCODE.md        # 注册到 Opencode
│   └── OPENCODE_REGISTRATION_COMPLETE.md
│
├── 📝 示例代码
│   ├── demo_grid_scan.py          # 宫格扫描演示
│   └── register_to_opencode.py    # 注册脚本
│
└── 📦 其他
    └── requirements.txt           # Python 依赖
```

---

## 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `mcp_server.py` | MCP 服务主入口，启动服务器 |
| `config.yaml` | 配置文件（宫格数、CV 阈值等） |
| `opencode-mcp-config.json` | Opencode 的 MCP 配置 |

### core/ - 核心模块

| 文件 | 说明 | 状态 |
|------|------|------|
| `grid_manager.py` | 9 宫格管理器，支持自然语言方位 | ✅ 核心 |
| `uia_region_scanner.py` | UIA 扫描器，实现 find_by_selector | ✅ 核心 |
| `cv_prefilter.py` | CV 图像预筛选 | ⚠️ 可选 |
| `focus_diffusion.py` | 焦点扩散扫描策略 | ⚠️ 可选 |

### tools/ - MCP 工具

| 文件 | 说明 | 提供的工具 |
|------|------|-----------|
| `grid_picker.py` | 宫格相关工具 | `scan_region()`, `set_focus_window()`, `pick_grid_element()` |
| `element_finder.py` | 自然语言查找 | `find_element_natural()` |
| `selector_query.py` | Selector 查询 | `find_element_selector()`, `scan_grid_region()` |

### utils/ - 工具类

| 文件 | 说明 |
|------|------|
| `selector_parser.py` | 解析 tdSelector 语法 |

### tests/ - 测试目录

| 文件 | 说明 |
|------|------|
| `README.md` | 测试说明 |
| `run_all_tests.py` | 批量运行测试 |
| `test_*.py` | 各种测试用例 |

---

## 关键特性

### ✅ 9 宫格 + 自然语言方位

- 默认使用 3x3 宫格（9 宫格）
- 支持方位词：左上、上中、右上、左中、中间、右中、左下、下中、右下
- 支持区域描述：上面、下面、左侧、右侧、左上角等

### ✅ 两种查找方式

1. **scan_region(region="左上")** - 扫描区域获取元素列表
2. **find_element_selector(selector="...")** - 使用 selector 精确定位

### ✅ LLM 友好设计

```
用户："帮我找微信左边的搜一搜按钮"
    ↓
LLM: scan_region(region="左侧")
    ↓
返回：[{"name": "微信", ...}, {"name": "搜一搜", ...}]
    ↓
LLM: find_element_selector("[...]")
    ↓
返回：位置信息
    ↓
LLM: "找到了！搜一搜按钮在微信窗口左侧，坐标 (x, y)"
```

---

## 快速开始

### 1. 安装依赖

```bash
cd tdRPA-mcp
D:\projects\wx-rpa\.venv\Scripts\pip.exe install -r requirements.txt
```

### 2. 配置 Opencode

编辑 `opencode-mcp-config.json`，然后复制到 Opencode 配置目录。

### 3. 运行测试

```bash
D:\projects\wx-rpa\.venv\Scripts\python.exe tests/run_all_tests.py
```

### 4. 启动 MCP 服务

```bash
D:\projects\wx-rpa\.venv\Scripts\python.exe mcp_server.py
```

---

## 清理缓存

定期清理 Python 缓存：

```bash
# Windows PowerShell
Remove-Item -Recurse -Force __pycache__

# 或使用 Python
python -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
```

---

## 添加新功能

1. **核心功能** → 添加到 `core/`
2. **MCP 工具** → 添加到 `tools/`，并在 `mcp_server.py` 中注册
3. **工具函数** → 添加到 `utils/`
4. **测试** → 添加到 `tests/`
5. **文档** → 添加到根目录，更新 `README.md`

---

## 命名规范

- 文件名：小写 + 下划线（如 `grid_manager.py`）
- 类名：大驼峰（如 `GridManager`）
- 函数名：小写 + 下划线（如 `get_grid_by_id`）
- 测试文件：`test_*.py`
