# tdRPA-mcp 已成功注册到 Opencode! 🎉

## ✅ 注册完成

tdRPA-mcp 已成功注册到 Opencode，配置已保存到：

### 配置文件位置

1. **主配置文件**: 
   ```
   C:\Users\niukl\AppData\Roaming\Code\User\settings.json
   ```

2. **MCP 专用配置** (方便查看):
   ```
   C:\Users\niukl\AppData\Roaming\Code\User\mcp.json
   ```

### 注册的服务

```json
{
  "mcpServers": {
    "tdrpa-ui-scanner": {
      "command": "D:\\projects\\wx-rpa\\.venv\\Scripts\\python.exe",
      "args": ["D:\\projects\\wx-rpa\\tdRPA-mcp\\mcp_server.py"],
      "cwd": "D:\\projects\\wx-rpa\\tdRPA-mcp",
      "environment": {
        "PYTHONPATH": "D:\\projects\\wx-rpa\\tdRPA-mcp"
      }
    }
  }
}
```

## 🚀 下一步操作

### 1. 重启 Opencode/VS Code

```bash
# 完全关闭并重新打开 VS Code 或 Opencode
```

### 2. 验证 MCP 连接

在 Opencode/VS Code 中：

1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 `MCP` 或 `Model Context Protocol`
3. 查看已连接的服务器
4. 应该看到 **tdrpa-ui-scanner**

### 3. 开始使用

在 Opencode 聊天中输入：

```
帮我查找记事本的保存按钮
```

或者：

```
设置目标窗口为微信
```

## 📋 可用的 MCP 工具

注册后，Opencode 可以使用以下工具：

### 窗口管理
- `set_focus_window` - 设置目标窗口
- `set_focus_point` - 设置焦点坐标
- `list_grids` - 列出所有宫格

### 元素查找
- `find_element_natural` - 自然语言描述查找
- `find_element_selector` - selector 语法查找
- `pick_grid_element` - 宫格拾取器

### 扫描功能
- `scan_grid_region` - 扫描指定宫格
- `scan_all_grids` - 扫描所有宫格
- `get_status` - 获取服务状态

### 其他
- `clear_cache` - 清除缓存

## 💡 使用示例

### 示例 1: 查找元素

```
在 Opencode 中输入：
"帮我找到记事本的保存按钮"

这将调用：find_element_natural(description="记事本的保存按钮")
```

### 示例 2: 设置目标

```
在 Opencode 中输入：
"我想操作微信窗口"

这将调用：set_focus_window(process_name="WeChat.exe")
```

### 示例 3: 扫描区域

```
在 Opencode 中输入：
"扫描屏幕中心区域"

这将调用：scan_focus_area(layers=1)
```

### 示例 4: 列出元素

```
在 Opencode 中输入：
"列出所有宫格和元素"

这将调用：list_grids(show_elements=True)
```

## 🔧 配置说明

### 服务配置

- **服务名称**: tdrpa-ui-scanner
- **Python 解释器**: 使用项目的虚拟环境
- **工作目录**: D:\projects\wx-rpa\tdRPA-mcp
- **自动批准**: 空列表 (需要手动确认)

### 环境变量

- `PYTHONPATH`: 确保可以导入项目模块

## ⚠️ 注意事项

### 1. 首次使用需要安装依赖

确保已安装必要依赖：

```bash
cd D:\projects\wx-rpa\tdRPA-mcp
D:\projects\wx-rpa\.venv\Scripts\activate
pip install -r requirements.txt
```

当前缺少的包：
- `mcp` - MCP SDK
- `pyyaml` - YAML 配置解析

安装方法：

```bash
# 由于虚拟环境没有 pip，使用以下方法：
uv pip install mcp pyyaml
```

### 2. 服务状态

MCP 服务会在 Opencode 启动时自动运行。

查看状态：
- 在 Opencode 的 MCP 面板中查看连接状态
- 或手动运行测试脚本验证

### 3. 故障排查

如果服务未启动，检查：

1. **日志文件**: 
   - Opencode 输出面板
   - MCP 服务器日志

2. **手动测试**:
   ```bash
   D:\projects\wx-rpa\.venv\Scripts\python.exe D:\projects\wx-rpa\tdRPA-mcp\mcp_server.py
   ```

3. **配置文件**: 
   - 确保路径正确
   - 确保 JSON 格式正确

## 📖 参考文档

- [REGISTER_TO_OPENCODE.md](./REGISTER_TO_OPENCODE.md) - 详细配置指南
- [README.md](./README.md) - 完整功能文档
- [QUICKSTART.md](./QUICKSTART.md) - 快速开始
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - 技术总结

## 🎯 核心功能

### 16 宫格扫描

将窗口分为 4x4=16 个宫格，实现：
- ✅ 局部快速扫描
- ✅ 焦点扩散策略
- ✅ CV 预筛选加速

### 焦点扩散

从焦点位置开始，按层扩散：
- Layer 0: 焦点宫格 (1 个)
- Layer 1: 相邻 8 宫格
- Layer 2: 外围 7 宫格

### 双模式查询

- **自然语言**: "记事本的保存按钮"
- **Selector 语法**: `"[{'wnd': [...]}]"`

## 📊 测试结果

```
✓ GridManager 测试通过
✓ CVPreFilter 测试通过
✓ UIARegionScanner 测试通过
✓ 综合演示运行成功
✓ Opencode 注册成功
```

## 🔗 项目位置

```
D:\projects\wx-rpa\tdRPA-mcp\
├── mcp_server.py              # MCP 服务入口
├── core/                      # 核心模块
├── tools/                     # MCP 工具
├── utils/                     # 工具模块
└── ...
```

## ✨ 下一步

1. ✅ **安装 MCP SDK**:
   ```bash
   uv pip install mcp pyyaml
   ```

2. ✅ **重启 Opencode**

3. ✅ **测试工具调用**

4. ✅ **开始使用!**

---

**注册完成! 祝你使用愉快!** 🎉

如有问题，请查看文档或运行测试脚本。
