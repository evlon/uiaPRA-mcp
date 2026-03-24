# uiaRPA-mcp

**智能 UI 自动化交互系统** - 基于语义化理解的 Windows UI 元素查找与操作工具

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange.svg)](https://modelcontextprotocol.io/)

---

## 🎯 产品简介

uiaRPA-mcp 是一个**智能的 Windows UI 自动化交互系统**，通过创新的**9 宫格空间分割**和**语义化元素过滤**技术，让 AI 助手能够像人类一样理解和操作 Windows 应用程序。

### 核心价值

传统的 UI 自动化需要精确的坐标或复杂的 XPath，而 uiaRPA-mcp 允许您使用**自然语言描述**来查找和操作 UI 元素：

- ❌ **传统方式**: `//Window[@title='微信']/Button[@automationid='12345']`
- ✅ **uiaRPA 方式**: "微信左边的搜一搜按钮"

---

## ✨ 核心优势

### 1️⃣ **语义化理解**

系统能够理解人类的自然语言描述，自动分析：
- **空间关系**: "左边"、"上面"、"中间"
- **元素特征**: "按钮"、"文本框"、"图标"
- **内容匹配**: "包含'搜'字"、"名称是'发送'"

### 2️⃣ **9 宫格空间分割**

将窗口智能划分为 9 个区域，符合人类的空间认知习惯：

```
┌─────────┬─────────┬─────────┐
│  左上   │  上中   │  右上   │
│ (Grid 0)│ (Grid 1)│ (Grid 2)│
├─────────┼─────────┼─────────┤
│  左中   │  中间   │  右中   │
│ (Grid 3)│ (Grid 4)│ (Grid 5)│
├─────────┼─────────┼─────────┤
│  左下   │  下中   │  右下   │
│ (Grid 6)│ (Grid 7)│ (Grid 8)│
└─────────┴─────────┴─────────┘
```

### 3️⃣ **灵活的语义过滤**

支持多种条件组合：
```python
filter_ui_elements(
    grid_positions=['左上', '左中'],  # 左侧区域
    name_contains='搜',               # 名称包含"搜"
    control_types=['ButtonControl']   # 按钮类型
)
```

### 4️⃣ **实时高亮验证**

找到元素后，可以在屏幕上实时高亮显示：
- 🔴 红色边框标记
- 🔄 跟随元素移动
- ⏱️ 可设置持续时间

### 5️⃣ **完整的日志系统**

内置详细日志记录：
- 📝 自动记录函数调用
- 📊 统计执行时间
- 🔍 完整异常堆栈
- 🎨 彩色控制台输出

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 MCP

```bash
python register_to_opencode.py
```

### 基本使用

```python
# 1. 设置目标窗口
await mcp.call_tool('set_focus_window', {
    'process_name': 'WeChat.exe'
})

# 2. 获取 UI 树数据
ui_data = await mcp.call_tool('get_ui_tree_data', {
    'max_depth': 15
})

# 3. 语义化过滤
results = await mcp.call_tool('filter_ui_elements', {
    'grid_positions': ['左中', '左上'],
    'name_contains': '搜',
    'control_types': ['ButtonControl']
})

# 4. 高亮验证
await mcp.call_tool('highlight_element', {
    'selector_string': results['elements'][0]['selector'],
    'duration': 5.0,
    'color': 'red'
})
```

---

## 📁 项目结构

```
uiaRPA-mcp/
├── README.md                    # 本文件
├── requirements.txt             # Python 依赖
├── config.yaml                  # 配置文件
├── mcp_server.py                # MCP 服务入口
│
├── core/                        # 核心模块
│   ├── logger.py               # 日志系统
│   ├── log_analyzer.py         # 日志分析
│   ├── grid_manager.py         # 9 宫格管理器
│   ├── semantic_filter.py      # 语义化过滤
│   ├── ui_tree_scanner.py      # UI 树扫描
│   └── screen_highlighter.py   # 屏幕高亮
│
├── tools/                       # MCP 工具
│   └── grid_picker.py          # 宫格拾取器
│
├── utils/                       # 工具类
│   └── selector_parser.py      # Selector 解析
│
├── tests/                       # 测试用例
│   ├── test_logging.py         # 日志测试
│   ├── test_semantic_filter.py # 语义过滤测试
│   └── ...
│
└── docs/                        # 文档
    ├── logging_guide.md        # 日志系统指南
    ├── LOGGING_QUICKSTART.md   # 日志快速开始
    └── semantic_filter_guide.md # 语义过滤指南
```

---

## 📚 文档导航

### 入门
- **[README_LOGGING.md](README_LOGGING.md)** - 日志系统总览
- **[docs/logging_guide.md](docs/logging_guide.md)** - 详细日志指南

### 进阶
- **[docs/semantic_filter_guide.md](docs/semantic_filter_guide.md)** - 语义化过滤完全指南
- **[docs/LOGGING_QUICKSTART.md](docs/LOGGING_QUICKSTART.md)** - 5 分钟上手日志

### 历史文档
- **[docs_archive/](docs_archive/)** - 归档的历史文档（不提交到 Git）

---

## 🔧 开发和测试

### 运行测试

```bash
# 测试日志功能
python tests/test_logging.py

# 测试语义化过滤
python tests/test_semantic_filter.py

# 测试 MCP 工具集成
python tests/test_mcp_semantic_search.py
```

### 分析日志

```bash
# 一键分析最新日志
analyze_log.bat

# 或手动运行
python -m core.log_analyzer
```

---

## 🤝 贡献指南

### 代码规范

- 遵循 PEP 8 规范
- 使用 type hints
- 编写单元测试
- 添加详细的 docstring

### 提交规范

```bash
# 功能新增
git commit -m "feat: 添加 XXX 功能"

# Bug 修复
git commit -m "fix: 修复 XXX 问题"

# 文档更新
git commit -m "docs: 更新 XXX 文档"

# 重构
git commit -m "refactor: 重构 XXX 模块"
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **GitHub**: https://github.com/evlon/uiaPRA-mcp

---

*Last updated: 2026-03-25*
