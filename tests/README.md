# tdRPA-mcp 测试目录

本目录包含所有测试代码，用于验证 MCP 服务的各项功能。

## 测试文件组织

### 核心功能测试
- `test_wechat_9grid.py` - 测试微信窗口的 9 宫格划分和方位查找逻辑

### 运行测试

```bash
# 运行单个测试
D:\projects\wx-rpa\.venv\Scripts\python.exe tests/test_wechat_9grid.py

# 运行所有测试
D:\projects\wx-rpa\.venv\Scripts\python.exe -m pytest tests/
```

## 测试分类

### 1. 窗口定位测试
测试如何找到并定位目标窗口（如微信、记事本等）。

### 2. 宫格划分测试
测试将窗口划分为 9 宫格的逻辑，验证方位映射是否正确。

### 3. 元素查找测试
测试使用 selector 或自然语言描述查找 UI 元素。

### 4. 集成测试
测试完整的 MCP 工具链。

## 添加新测试

创建新的测试文件时，请遵循以下命名规范：
- 文件名以 `test_` 开头
- 描述清晰，如 `test_wechat_search.py`
- 包含必要的注释和输出说明

示例：
```python
"""
测试：XXX 功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.xxx import XXX

def test_xxx():
    print("测试说明...")
    # 测试代码
    
if __name__ == "__main__":
    test_xxx()
```

## 清理测试

测试完成后，可以删除临时的测试文件，保持目录整洁。
重要的测试应该保留并添加到文档中作为示例。
