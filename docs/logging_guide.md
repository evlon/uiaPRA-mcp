# tdRPA-mcp 日志系统使用指南

## 概述

tdRPA-mcp 提供了详细的日志系统，用于记录所有关键操作、函数调用、参数、返回值和异常。这使得在使用过程中遇到问题时，可以通过分析日志来快速定位问题。

## 日志特性

### ✅ 自动记录

- **函数调用**: 自动记录函数名、参数、返回值
- **执行时间**: 记录每个函数的执行耗时
- **异常信息**: 完整记录异常堆栈
- **关键步骤**: UIA 操作、窗口查找、元素扫描等

### ✅ 多级日志

- **DEBUG**: 详细调试信息（函数调用、参数等）
- **INFO**: 一般信息（操作完成、结果统计等）
- **WARNING**: 警告信息（非致命问题）
- **ERROR**: 错误信息（操作失败、异常等）
- **CRITICAL**: 严重错误

### ✅ 双输出

- **控制台输出**: 彩色显示，方便实时查看
- **文件输出**: 完整记录，便于事后分析

## 日志文件位置

日志文件默认保存在项目的 `logs` 目录：

```
d:/projects/wx-rpa/tdRPA-mcp/logs/
├── tdrpa_20260325_143022.log    # 按时间戳命名的日志文件
├── tdrpa_20260325_145611.log
└── latest.log                    # 指向最新日志的符号链接
```

## 使用方法

### 1. 在代码中使用日志装饰器

```python
from core.logger import get_logger, log_function_call, LogContext

# 获取 logger
logger = get_logger('my_module', level='DEBUG', detailed=True)

# 使用装饰器自动记录函数调用
@log_function_call(logger=logger, log_args=True, log_return=True)
def find_element(selector: str, timeout: float = 5.0):
    """查找元素"""
    with LogContext(logger, f"查找元素：{selector}"):
        # 实现代码
        result = do_something()
        return result

# 手动记录日志
logger.info("操作开始")
logger.debug(f"参数详情：{params}")
try:
    result = process()
    logger.info(f"处理成功：{result}")
except Exception as e:
    logger.error(f"处理失败：{e}", exc_info=True)
```

### 2. 查看和分析日志

#### 方法 A: 使用日志分析工具

```bash
# 分析最新日志
python -m core.log_analyzer

# 分析指定日志文件
python -m core.log_analyzer logs/tdrpa_20260325_143022.log
```

#### 方法 B: 在代码中分析

```python
from core.log_analyzer import LogAnalyzer, find_latest_log

# 获取最新日志文件
log_file = find_latest_log()

# 创建分析器
analyzer = LogAnalyzer(log_file)

# 获取统计信息
stats = analyzer.get_statistics()
print(f"总条目数：{stats['total_entries']}")
print(f"错误数：{stats['error_count']}")

# 查看所有错误
errors = analyzer.get_errors()
for error in errors:
    print(f"[{error.timestamp}] {error.function_name}: {error.message}")

# 搜索特定关键字
results = analyzer.search("搜一搜")
for entry in results:
    print(f"{entry.level}: {entry.message}")

# 按级别过滤
warnings = analyzer.filter_by_level('WARNING')

# 按函数过滤
scanner_calls = analyzer.filter_by_function('scan')

# 导出为 JSON
analyzer.export_to_json(Path('analysis_result.json'))
```

### 3. 在测试中使用日志

```python
"""测试文件中使用日志"""
import sys
sys.path.insert(0, '.')

from core.logger import get_logger, log_function_call

# 创建 logger
logger = get_logger('test.my_test', level='DEBUG', detailed=True)

@log_function_call(logger=logger)
def test_find_button():
    """测试查找按钮"""
    logger.info("开始测试...")
    
    try:
        # 测试代码
        result = find_element("button")
        
        if result:
            logger.info("✅ 测试通过")
        else:
            logger.warning("⚠️ 未找到元素")
            
    except Exception as e:
        logger.error(f"❌ 测试失败：{e}", exc_info=True)
        raise

if __name__ == '__main__':
    test_find_button()
```

## 日志格式

### 控制台输出（彩色）

```
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ▶️ 调用 tdrpa.scanner.UIARegionScanner.__init__(process_name=WeChat.exe, timeout=5.0)
2026-03-25 14:30:22 | INFO     | tdrpa.scanner | uia_region_scanner.py:74 | _get_root_element | Found root element: 微信
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ✅ tdrpa.scanner.UIARegionScanner.__init__ 返回 [0.125s]: None
```

### 文件输出（详细）

```
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ▶️ 调用 tdrpa.scanner.UIARegionScanner.__init__(process_name=WeChat.exe, timeout=5.0)
2026-03-25 14:30:22 | INFO     | tdrpa.scanner | uia_region_scanner.py:74 | _get_root_element | Found root element: 微信
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ✅ tdrpa.scanner.UIARegionScanner.__init__ 返回 [0.125s]: None
```

## 日志级别说明

### DEBUG
最详细的调试信息，包括：
- 所有函数调用和返回
- 参数和返回值详情
- 内部状态变化
- 详细的执行路径

**使用场景**: 开发调试、问题排查

### INFO
一般信息，包括：
- 操作开始和完成
- 重要的状态变化
- 结果统计

**使用场景**: 日常使用、功能验证

### WARNING
警告信息，包括：
- 非致命问题
- 降级处理
- 性能提示

**使用场景**: 需要注意但不影响功能的情况

### ERROR
错误信息，包括：
- 操作失败
- 异常抛出
- 无法恢复的问题

**使用场景**: 需要立即关注的问题

## 常见问题排查

### 问题 1: 找不到目标窗口

**查看日志中的关键信息**:

```bash
# 搜索窗口查找相关日志
python -m core.log_analyzer | grep -i "window\|find"
```

**日志示例**:
```
[14:30:22] INFO  | Found root element: 微信
[14:30:23] DEBUG | Searching node 0: type=wnd, conditions=1
[14:30:23] WARNING | No elements matched node 0
```

### 问题 2: Selector 匹配失败

**查看 selector 解析和匹配过程**:

```bash
# 搜索 selector 相关日志
python -m core.log_analyzer | grep -i "selector\|match"
```

**日志示例**:
```
[14:30:25] INFO  | Parsed selector: [{'type': 'ctrl', 'conditions': [...]}]
[14:30:25] DEBUG | Matched element: 搜一搜，ControlType: ButtonControl
[14:30:25] INFO  | Found element: 搜一搜，ControlType: ButtonControl
```

### 问题 3: 扫描结果为空

**查看扫描过程和统计**:

```bash
# 查看扫描相关日志
python -m core.log_analyzer | grep -i "scan\|element"
```

**日志示例**:
```
[14:30:26] INFO  | Scanned 77 elements from UI tree
[14:30:26] DEBUG | Found 39 elements in grid 3 (左中)
[14:30:26] INFO  | Filtering by name_contains='搜'
[14:30:26] DEBUG | Filtered to 1 elements
```

## 性能优化建议

### 1. 调整日志级别

生产环境使用 INFO 级别减少开销：

```python
logger = get_logger('tdrpa', level='INFO', detailed=False)
```

### 2. 选择性记录

只对关键函数使用装饰器：

```python
# 关键函数 - 详细记录
@log_function_call(logger=logger, log_args=True, log_return=True)
def critical_operation():
    pass

# 一般函数 - 简单记录
def normal_function():
    logger.debug("Processing...")
```

### 3. 定期清理日志

```bash
# 删除 7 天前的日志
find logs/ -name "*.log" -mtime +7 -delete
```

## 最佳实践

### ✅ 推荐做法

1. **在关键路径使用日志装饰器**
   ```python
   @log_function_call(logger=logger)
   def find_element(...):
       pass
   ```

2. **使用上下文管理器记录代码块**
   ```python
   with LogContext(logger, "复杂操作"):
       # do something
   ```

3. **记录异常时包含堆栈信息**
   ```python
   try:
       ...
   except Exception as e:
       logger.error(f"失败：{e}", exc_info=True)
   ```

4. **使用不同的 logger 名称区分模块**
   ```python
   logger = get_logger('tdrpa.scanner')   # 扫描器
   logger = get_logger('tdrpa.filter')    # 过滤器
   logger = get_logger('tdrpa.selector')  # Selector
   ```

### ❌ 避免的做法

1. **不要在循环中大量记录 DEBUG 日志**
   ```python
   # 不推荐
   for elem in elements:
       logger.debug(f"Processing {elem}")  # 可能产生数千条日志
   
   # 推荐
   logger.debug(f"Processing {len(elements)} elements")
   ```

2. **不要记录敏感信息**
   ```python
   # 不推荐
   logger.debug(f"用户登录：{username}, 密码：{password}")
   
   # 推荐
   logger.debug(f"用户登录：{username}, 密码：***")
   ```

3. **不要忘记设置日志级别**
   ```python
   # 不推荐 - 默认可能是 DEBUG，产生大量日志
   logger = get_logger('my_module')
   
   # 推荐
   logger = get_logger('my_module', level='INFO')
   ```

## 日志分析示例

### 完整的问题排查流程

假设用户报告"找不到微信的搜一搜按钮"：

**步骤 1: 查看最新日志**
```bash
python -m core.log_analyzer
```

**步骤 2: 查看错误信息**
```
[错误日志]
[14:30:25] ERROR | find_by_selector: Element not found
```

**步骤 3: 搜索相关操作**
```python
analyzer = LogAnalyzer(find_latest_log())

# 查找 selector 解析
selector_logs = analyzer.search("selector")
for log in selector_logs:
    print(f"[{log.level}] {log.message}")

# 查找扫描过程
scan_logs = analyzer.search("scan")
for log in scan_logs:
    print(f"[{log.level}] {log.message}")
```

**步骤 4: 分析问题**
从日志中发现：
- ✅ 窗口查找成功："Found root element: 微信"
- ✅ UI 树扫描成功："Scanned 77 elements"
- ⚠️ 过滤后为空："Filtered to 0 elements"
- ❌ 结论：元素存在但过滤条件不匹配

**步骤 5: 解决问题**
调整过滤条件或 selector 语法

## 总结

完善的日志系统让您能够：

1. ✅ **快速定位问题** - 通过详细的执行记录
2. ✅ **分析执行流程** - 了解代码实际运行路径
3. ✅ **性能调优** - 识别耗时操作
4. ✅ **远程调试** - 无需现场即可分析问题
5. ✅ **持续改进** - 基于日志数据优化代码

记住：**好的日志是解决问题的第一线索！**
