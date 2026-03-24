# tdRPA-mcp

**智能 UI 自动化交互系统** - 基于语义化理解的 Windows UI 元素查找与操作工具

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange.svg)](https://modelcontextprotocol.io/)

---

## 📖 快速导航

| 文档类型 | 链接 | 说明 |
|---------|------|------|
| 🚀 **快速开始** | [QUICKSTART.md](QUICKSTART.md) | 5 分钟上手教程 |
| 📚 **使用指南** | [README_LOGGING.md](README_LOGGING.md) | 完整功能说明 |
| 🧠 **设计思想** | [docs/DESIGN_PHILOSOPHY.md](docs/DESIGN_PHILOSOPHY.md) | 产品设计理念 |
| 🏗️ **系统架构** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 技术架构详解 |
| 📝 **日志系统** | [docs/logging_guide.md](docs/logging_guide.md) | 日志使用指南 |

---

## 🎯 产品简介

tdRPA-mcp 是一个**智能的 Windows UI 自动化交互系统**，通过创新的**9 宫格空间分割**和**语义化元素过滤**技术，让 AI 助手能够像人类一样理解和操作 Windows 应用程序。

### 核心价值

传统的 UI 自动化需要精确的坐标或复杂的 XPath，而 tdRPA-mcp 允许您使用**自然语言描述**来查找和操作 UI 元素：

- ❌ **传统方式**: `//Window[@title='微信']/Button[@automationid='12345']`
- ✅ **tdRPA 方式**: "微信左边的搜一搜按钮"

---

## ✨ 核心优势

### 1️⃣ **语义化理解**

系统能够理解人类的自然语言描述，自动分析：
- **空间关系**: "左边"、"上面"、"中间"
- **元素特征**: "按钮"、"文本框"、"图标"
- **内容匹配**: "包含'搜'字"、"名称是'发送'"

**示例**：
```python
# 用户说："微信左边的搜一搜按钮"
# 系统自动分析:
#   - "左边" → 网格位置 ['左上', '左中', '左下']
#   - "搜一搜" → 名称包含"搜"
#   - "按钮" → 控件类型 ButtonControl
```

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

每个区域有直观的自然语言名称，如"左上"、"中间"、"右下"等。

### 3️⃣ **灵活的语义过滤**

提供强大的过滤器，支持多种条件组合：

```python
# 示例：查找左侧区域的搜索按钮
filter_ui_elements(
    grid_positions=['左上', '左中', '左下'],  # 左侧所有区域
    name_contains='搜',                       # 名称包含"搜"
    control_types=['ButtonControl'],          # 按钮类型
    min_width=50,                             # 最小宽度 50px
    min_height=30,                            # 最小高度 30px
    sort_by='name'                            # 按名称排序
)
```

### 4️⃣ **实时高亮验证**

找到元素后，可以在屏幕上实时高亮显示，方便验证：

- 🔴 红色边框标记元素位置
- 🔄 跟随元素移动（如果位置变化）
- ⏱️ 可设置持续时间

### 5️⃣ **完整的日志系统**

内置详细的日志记录，方便问题分析和调试：

- 📝 自动记录所有函数调用
- 📊 统计执行时间和性能数据
- 🔍 完整的异常堆栈信息
- 🎨 彩色控制台输出

---

## 🧠 设计思想

### 核心理念：**让 AI 像人类一样思考 UI**

#### 传统 UI 自动化的痛点

1. **过于技术化**: 需要知道精确的 XPath、CSS Selector
2. **脆弱**: UI 稍有变化就失效
3. **不直观**: 人类不会用坐标思考
4. **调试困难**: 失败时不知道原因

#### tdRPA 的创新方法

1. **空间思维优先**
   - 人类首先会说的是"在左边"、"在上面"，而不是坐标
   - 9 宫格符合人类的直觉分区

2. **渐进式精确化**
   ```
   第一步：获取完整 UI 树（不做过滤）
   第二步：LLM 语义分析用户描述
   第三步：构造灵活的过滤条件
   第四步：逐步 refine 直到找到目标
   ```

3. **LLM 驱动决策**
   - 不是硬编码规则
   - LLM 根据上下文决定如何筛选
   - 支持多轮对话 refine

4. **闭环验证**
   - 找到元素后立即高亮显示
   - 用户可以即时确认是否正确
   - 错误时可以快速调整策略

### 详细设计文档
👉 [查看完整设计思想](docs/DESIGN_PHILOSOPHY.md)

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                   MCP Client                         │
│              (Claude Desktop / IDE)                  │
└────────────────────┬────────────────────────────────┘
                     │ MCP Protocol
┌────────────────────▼────────────────────────────────┐
│                  MCP Server                          │
│               (mcp_server.py)                        │
├─────────────────────────────────────────────────────┤
│                   MCP Tools                          │
│  ┌──────────────┬──────────────┬─────────────────┐  │
│  │ set_focus_   │ get_ui_tree_ │ filter_ui_      │  │
│  │ window       │ data         │ elements        │  │
│  └──────────────┴──────────────┴─────────────────┘  │
│  ┌──────────────┬──────────────┬─────────────────┐  │
│  │ build_       │ highlight_   │ scan_region     │  │
│  │ selector     │ element      │                 │  │
│  └──────────────┴──────────────┴─────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  Core Layer                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │UIA Region  │  │ Grid       │  │ UI Tree      │  │
│  │ Scanner    │  │ Manager    │  │ Scanner      │  │
│  └────────────┘  └────────────┘  └──────────────┘  │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ Semantic   │  │ Selector   │  │ Screen       │  │
│  │ Filter     │  │ Builder    │  │ Highlighter  │  │
│  └────────────┘  └────────────┘  └──────────────┘  │
│  ┌────────────┐  ┌────────────┐                    │
│  │ Logger     │  │ Log        │                    │
│  │ System     │  │ Analyzer   │                    │
│  └────────────┘  └────────────┘                    │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Windows UI Automation (UIA)             │
│           (uiautomation library based on             │
│            Microsoft UI Automation API)              │
└─────────────────────────────────────────────────────┘
```

### 核心模块说明

#### 1. **MCP Server 层** (`mcp_server.py`)
- 实现 Model Context Protocol
- 暴露标准化工具接口给 AI 助手
- 处理认证和会话管理

#### 2. **工具层** (`tools/`)
- **`grid_picker.py`**: 宫格拾取器，提供 6 个核心工具
  - `set_focus_window`: 设置目标窗口
  - `get_ui_tree_data`: 获取完整 UI 树
  - `filter_ui_elements`: 语义化过滤
  - `build_selector_for_element`: 构建 selector
  - `highlight_element`: 高亮显示
  - `scan_region`: 扫描指定区域

#### 3. **核心层** (`core/`)
- **`uia_region_scanner.py`**: UIA 区域扫描器
- **`grid_manager.py`**: 9 宫格管理器
- **`ui_tree_scanner.py`**: UI 树扫描器
- **`semantic_filter.py`**: 语义化过滤器
- **`screen_highlighter.py`**: 屏幕高亮器
- **`logger.py` & `log_analyzer.py`**: 日志系统

#### 4. **工具层** (`utils/`)
- **`selector_parser.py`**: Selector 语法解析

### 详细架构文档
👉 [查看完整系统架构](docs/ARCHITECTURE.md)

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

### 基本使用流程

#### 步骤 1: 设置目标窗口

```python
await mcp.call_tool('set_focus_window', {
    'process_name': 'WeChat.exe',
    'window_title': '微信'
})
```

#### 步骤 2: 获取 UI 树数据

```python
ui_data = await mcp.call_tool('get_ui_tree_data', {
    'max_depth': 15
})
```

#### 步骤 3: 语义化过滤

```python
results = await mcp.call_tool('filter_ui_elements', {
    'grid_positions': ['左中', '左上'],
    'name_contains': '搜',
    'control_types': ['ButtonControl']
})
```

#### 步骤 4: 构建并验证

```python
selector_info = await mcp.call_tool('build_selector_for_element', {
    'element_index': 0
})

await mcp.call_tool('highlight_element', {
    'selector_string': selector_info['selector']['full'],
    'duration': 5.0,
    'color': 'red'
})
```

### 详细快速开始教程
👉 [5 分钟上手教程](QUICKSTART.md)

---

## 💡 使用场景

### 场景 1: 自动化测试

测试应用程序的 UI 功能是否正常

### 场景 2: RPA 流程

自动填写表单、点击按钮等操作

### 场景 3: 辅助功能

帮助视障用户定位界面元素

### 场景 4: 批量操作

对多个窗口或元素执行相同操作

---

## 📚 文档导航

### 🎯 入门指南
- **[快速开始](QUICKSTART.md)** - 5 分钟上手
- **[安装指南](INSTALL.md)** - 详细安装步骤
- **[MCP 配置](REGISTER_TO_OPENCODE.md)** - 注册到 OpenCode

### 📖 使用文档
- **[MCP 使用指南](MCP_USAGE_GUIDE.md)** - MCP 工具详细说明
- **[自然语言查询](NATURAL_LANGUAGE_USAGE.md)** - 自然语言语法
- **[UI 树扫描](UI_TREE_SCAN_APPROACH.md)** - UI 树扫描方法
- **[日志系统](README_LOGGING.md)** - 日志功能总览

### 🔧 开发文档
- **[项目结构](PROJECT_STRUCTURE.md)** - 目录组织说明
- **[高亮功能](HIGHLIGHT_FEATURE.md)** - 屏幕高亮实现
- **[日志指南](docs/logging_guide.md)** - 详细日志用法

### 📋 参考文档
- **[设计思想](docs/DESIGN_PHILOSOPHY.md)** - 产品设计理念
- **[架构说明](docs/ARCHITECTURE.md)** - 系统架构详解
- **[API 参考](docs/API_REFERENCE.md)** - 完整 API 文档
- **[更新日志](docs/CHANGELOG_LOGGING_SYSTEM.md)** - 功能更新记录

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

欢迎提交 Issue 和 Pull Request！

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

## 🙏 致谢

感谢以下开源项目：

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议
- [uiautomation](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows) - Windows UI Automation 库
- [Microsoft UI Automation](https://docs.microsoft.com/en-us/windows/win32/winauto/uiautooverview) - Windows UI Automation API

---

## 📞 联系方式

- **Issue**: [GitHub Issues](https://github.com/your-org/tdRPA-mcp/issues)
- **Email**: thingswell@qq.com
- **WeChat**: haijun-data

---

*Last updated: 2026-03-25*
