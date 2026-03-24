# tdRPA-mcp 注册到 Opencode 指南

## 快速注册（推荐）

### 方式 1: 自动注册（运行脚本）

```bash
cd D:\projects\wx-rpa\tdRPA-mcp
D:\projects\wx-rpa\.venv\Scripts\python.exe register_to_opencode.py
```

脚本会自动：
1. 检测 Opencode 配置目录
2. 复制 MCP 配置到正确位置
3. 验证配置是否正确

### 方式 2: 手动复制配置

1. 打开 Opencode 配置目录：
   ```
   %APPDATA%\opencode\
   ```
   
2. 复制 `opencode-mcp-config.json` 内容到：
   - `%APPDATA%\opencode\settings.json`
   - 或 `%APPDATA%\opencode\mcp.json`

3. 重启 Opencode

## 手动配置步骤

### 步骤 1: 找到配置文件

Opencode 的配置文件通常在以下位置之一：

**Windows:**
- `%APPDATA%\Code\User\settings.json` (VS Code)
- `%APPDATA%\opencode\settings.json` (独立应用)
- `~/.opencode/settings.json`

**macOS:**
- `~/Library/Application Support/Code/User/settings.json`
- `~/.opencode/settings.json`

**Linux:**
- `~/.config/Code/User/settings.json`
- `~/.opencode/settings.json`

### 步骤 2: 添加 MCP 配置

在配置文件中添加以下内容：

```json
{
  "mcp": {
    "servers": {
      "tdrpa-ui-scanner": {
        "command": "D:\\projects\\wx-rpa\\.venv\\Scripts\\python.exe",
        "args": [
          "D:\\projects\\wx-rpa\\tdRPA-mcp\\mcp_server.py"
        ],
        "cwd": "D:\\projects\\wx-rpa\\tdRPA-mcp",
        "environment": {
          "PYTHONPATH": "D:\\projects\\wx-rpa\\tdRPA-mcp"
        }
      }
    }
  }
}
```

### 步骤 3: 验证配置

1. 重启 Opencode
2. 打开 MCP 面板或设置
3. 查看是否显示 "tdrpa-ui-scanner" 服务
4. 状态应为 "Running" 或 "Connected"

## 配置说明

### 配置项详解

```json
{
  "mcpServers": {
    "tdrpa-ui-scanner": {
      // Python 解释器路径（使用虚拟环境中的）
      "command": "D:\\projects\\wx-rpa\\.venv\\Scripts\\python.exe",
      
      // MCP 服务器脚本
      "args": [
        "D:\\projects\\wx-rpa\\tdRPA-mcp\\mcp_server.py"
      ],
      
      // 工作目录
      "cwd": "D:\\projects\\wx-rpa\\tdRPA-mcp",
      
      // 是否禁用（false=启用）
      "disabled": false,
      
      // 自动批准的操作列表
      "autoApprove": [],
      
      // 环境变量
      "environment": {
        // 添加项目路径到 PYTHONPATH
        "PYTHONPATH": "D:\\projects\\wx-rpa\\tdRPA-mcp"
      }
    }
  }
}
```

### 路径说明

确保所有路径都使用**绝对路径**：

- ❌ 相对路径：`./mcp_server.py`
- ✅ 绝对路径：`D:\\projects\\wx-rpa\\tdRPA-mcp\\mcp_server.py`

Windows 路径中的反斜杠需要转义：`D:\\path\\to\\file`

## 故障排查

### 问题 1: Opencode 找不到 MCP 服务

**解决方案:**
1. 检查配置文件位置是否正确
2. 确保 JSON 格式正确（使用 JSON 验证工具）
3. 重启 Opencode
4. 查看 Opencode 日志

### 问题 2: Python 解释器找不到

**解决方案:**
1. 确认虚拟环境路径正确
2. 检查 `D:\\projects\\wx-rpa\\.venv\\Scripts\\python.exe` 是否存在
3. 使用完整路径，不要使用相对路径

### 问题 3: 模块导入错误

**解决方案:**
1. 确保已安装依赖：`pip install -r requirements.txt`
2. 检查 `PYTHONPATH` 环境变量是否正确设置
3. 确保工作目录 (`cwd`) 设置正确

### 问题 4: MCP 服务启动失败

**查看日志:**
```bash
# 手动运行 MCP 服务器查看错误
D:\projects\wx-rpa\.venv\Scripts\python.exe D:\projects\wx-rpa\tdRPA-mcp\mcp_server.py
```

**常见问题:**
- 缺少依赖包：安装 `pip install mcp pyyaml`
- 端口被占用：修改配置文件中的端口
- 权限问题：以管理员身份运行

## 验证安装

### 测试 MCP 连接

在 Opencode 中：

1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "MCP" 或 "Model Context Protocol"
3. 查看已连接的服务器列表
4. 应该看到 "tdrpa-ui-scanner"

### 测试工具调用

在 Opencode 聊天中输入：

```
查找记事本的保存按钮
```

如果配置正确，Opencode 会调用 `find_element_natural` 工具。

## 使用示例

### 示例 1: 设置目标窗口

在 Opencode 中说：

```
设置目标窗口为记事本
```

这会调用 `set_focus_window(process_name="notepad.exe")`

### 示例 2: 查找元素

```
帮我找到微信的发送按钮
```

这会调用 `find_element_natural("微信的发送按钮")`

### 示例 3: 扫描区域

```
扫描屏幕中心区域
```

这会调用 `scan_focus_area(layers=1)`

## 高级配置

### 自定义端口

如果默认端口被占用，可以在 `mcp_server.py` 中修改：

```python
mcp = FastMCP(
    name="tdrpa-ui-scanner",
    port=8888  # 自定义端口
)
```

### 添加更多工具

在 `tools/` 目录中创建新的工具模块，然后在 `mcp_server.py` 中注册。

### 配置日志级别

在 `config.yaml` 中：

```yaml
logging:
  level: DEBUG  # INFO, WARNING, ERROR
```

## 卸载

### 从 Opencode 移除

1. 打开 Opencode 配置文件
2. 删除 `tdrpa-ui-scanner` 配置段
3. 重启 Opencode

### 删除项目

```bash
# 删除整个项目
rmdir /s D:\projects\wx-rpa\tdRPA-mcp
```

## 更新

### 更新代码

```bash
cd D:\projects\wx-rpa\tdRPA-mcp
git pull  # 如果使用 git
```

### 更新依赖

```bash
D:\projects\wx-rpa\.venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

## 参考资料

- [Opencode 文档](https://opencode.ai/docs/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [本项目 README.md](./README.md)
- [快速开始指南](./QUICKSTART.md)

## 获取帮助

如遇到问题：

1. 查看 [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
2. 检查测试脚本是否能正常运行
3. 查看 Opencode 日志
4. 联系项目维护者

---

**配置完成！祝你使用愉快！** 🎉
