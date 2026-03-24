# tdRPA-mcp 日志系统 - 快速开始

## 🎯 为什么需要日志？

在使用 tdRPA-mcp 过程中，您可能会遇到各种问题：
- ❌ 找不到目标窗口
- ❌ Selector 匹配失败
- ❌ 扫描结果为空
- ❌ 元素定位不准确

**有了详细的日志，您可以：**
- ✅ 看到完整的执行过程
- ✅ 了解每一步的详细信息
- ✅ 快速定位问题所在
- ✅ 通过分享日志让 AI 助手帮您分析问题

## 🚀 快速开始（3 步）

### 步骤 1: 运行测试自动生成日志

```bash
# 运行任意测试，会自动生成日志
python tests/test_logging.py
```

### 步骤 2: 查看日志文件

日志自动保存在 `logs/` 目录：

```
d:/projects/wx-rpa/tdRPA-mcp/logs/
├── tdrpa_20260325_143022.log    # 按时间戳命名
└── latest.log                    # 最新日志的快捷方式
```

### 步骤 3: 分析日志

**方法 A: 使用一键分析脚本**
```bash
# Windows
analyze_log.bat

# 或者手动运行
python -m core.log_analyzer
```

**方法 B: 在代码中分析**
```python
from core.log_analyzer import LogAnalyzer, find_latest_log

log_file = find_latest_log()  # 获取最新日志
analyzer = LogAnalyzer(log_file)

# 查看统计
stats = analyzer.get_statistics()
print(f"错误数：{stats['error_count']}")

# 查看所有错误
for error in analyzer.get_errors():
    print(f"[{error.timestamp}] {error.message}")
```

## 📝 在代码中使用日志

### 最简单的用法

```python
from core.logger import get_logger

# 获取 logger
logger = get_logger('my_module', level='DEBUG')

# 记录日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告")
logger.error("错误")
```

### 自动记录函数调用（推荐）

```python
from core.logger import get_logger, log_function_call

logger = get_logger('my_module', level='DEBUG')

# 使用装饰器，自动记录函数名、参数、返回值、执行时间
@log_function_call(logger=logger)
def find_element(selector: str, timeout: float = 5.0):
    """查找元素"""
    # 你的代码
    return result
```

**日志输出示例：**
```
2026-03-25 14:30:22 | DEBUG | ▶️ 调用 my_module.find_element(selector={'ctrl': [...]}, timeout=5.0)
2026-03-25 14:30:23 | DEBUG | ✅ my_module.find_element 返回 [0.125s]: <ElementInfo object>
```

### 记录代码块执行

```python
from core.logger import LogContext

with LogContext(logger, "处理复杂业务逻辑") as ctx:
    ctx.logger.info("步骤 1: 准备数据...")
    # 代码...
    
    ctx.logger.info("步骤 2: 执行操作...")
    # 代码...
```

**日志输出示例：**
```
2026-03-25 14:30:22 | DEBUG | ▶️ 开始：处理复杂业务逻辑
2026-03-25 14:30:23 | INFO  | 步骤 1: 准备数据...
2026-03-25 14:30:24 | INFO  | 步骤 2: 执行操作...
2026-03-25 14:30:25 | DEBUG | ✅ 完成：处理复杂业务逻辑 [3.125s]
```

### 敏感数据脱敏

```python
@log_function_call(
    logger=logger,
    mask_args=['password', 'token']  # 这些参数会自动脱敏
)
def login(username, password, token=None):
    pass
```

**日志输出：**
```
▶️ 调用 module.login(username='admin', password='***', token='***')
```

## 🔍 常见问题分析示例

### 问题 1: 找不到微信窗口

**运行测试：**
```bash
python tests/test_find_susou_button.py
```

**分析日志：**
```bash
python -m core.log_analyzer | findstr "window\|find"
```

**日志可能显示：**
```
[14:30:22] INFO  | Using Desktop as root element
[14:30:23] DEBUG | 遍历了 15 个顶级窗口
[14:30:23] WARNING | 未找到名称为'微信'的窗口
```

**结论：** 微信窗口未打开或标题不匹配

### 问题 2: Selector 匹配失败

**分析日志：**
```bash
python -m core.log_analyzer | findstr "selector\|match"
```

**日志可能显示：**
```
[14:30:25] INFO  | Parsed selector: [{'type': 'ctrl', 'conditions': [...]}]
[14:30:25] DEBUG | 尝试匹配条件：Name='搜一搜'
[14:30:25] DEBUG | 找到 3 个候选元素
[14:30:25] DEBUG | 元素 1: Name='', ControlType='ButtonControl'
[14:30:25] DEBUG | 元素 2: Name='搜索', ControlType='ButtonControl'
[14:30:25] DEBUG | 元素 3: Name='搜一搜', ControlType='ImageControl'
[14:30:25] WARNING | 无完全匹配的元素
```

**结论：** 按钮可能是纯图标（无文字），需要调整查找策略

### 问题 3: 扫描结果为空

**分析日志：**
```bash
python -m core.log_analyzer | findstr "scan\|element"
```

**日志可能显示：**
```
[14:30:26] INFO  | Scanned 77 elements from UI tree
[14:30:26] DEBUG | 按网格分布：左上 (8), 左中 (15), 右中 (12)...
[14:30:26] INFO  | 过滤条件：grid_positions=['左中'], name_contains='搜'
[14:30:26] DEBUG | 过滤后剩余：0 个元素
```

**结论：** 左侧区域没有名称包含"搜"的元素，可能在其他区域

## 🛠️ 高级用法

### 调整日志级别

```python
# 开发调试 - 详细日志
logger = get_logger('my_module', level='DEBUG', detailed=True)

# 生产环境 - 简洁日志
logger = get_logger('my_module', level='INFO', detailed=False)
```

### 自定义日志格式

```python
from core.logger import setup_logger

logger = setup_logger(
    name='custom',
    level='DEBUG',
    log_to_file=True,
    log_dir=Path('my_logs'),  # 自定义日志目录
    console_output=True,
    detailed_format=True
)
```

### 导出日志为 JSON

```python
from core.log_analyzer import LogAnalyzer, find_latest_log

analyzer = LogAnalyzer(find_latest_log())
analyzer.export_to_json(Path('analysis_result.json'))

# 可以用其他工具进一步分析
```

## 📊 日志文件格式

### 控制台输出（彩色）

```
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ▶️ 调用 ...
2026-03-25 14:30:22 | INFO     | tdrpa.scanner | uia_region_scanner.py:74 | _get_root_element | Found...
2026-03-25 14:30:22 | ERROR    | tdrpa.filter  | semantic_filter.py:123 | apply_query | 过滤失败...
```

### 文件输出（详细）

```
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ▶️ 调用 tdrpa.scanner.UIARegionScanner.__init__(process_name=WeChat.exe, timeout=5.0)
2026-03-25 14:30:22 | INFO     | tdrpa.scanner | uia_region_scanner.py:74 | _get_root_element | Found root element: 微信
2026-03-25 14:30:22 | DEBUG    | tdrpa.scanner | uia_region_scanner.py:57 | __init__ | ✅ tdrpa.scanner.UIARegionScanner.__init__ 返回 [0.125s]: None
```

## 💡 最佳实践

### ✅ 推荐

1. **在关键函数上使用装饰器**
   ```python
   @log_function_call(logger=logger)
   def critical_operation():
       pass
   ```

2. **使用上下文管理器记录复杂流程**
   ```python
   with LogContext(logger, "多步骤处理"):
       # steps...
   ```

3. **异常时记录完整堆栈**
   ```python
   try:
       ...
   except Exception as e:
       logger.error(f"失败：{e}", exc_info=True)
   ```

4. **定期清理旧日志**
   ```bash
   # 删除 7 天前的日志
   forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path"
   ```

### ❌ 避免

1. **不要在循环中大量记录**
   ```python
   # ❌ 不推荐
   for elem in elements:
       logger.debug(f"Processing {elem}")  # 可能产生数千条日志
   
   # ✅ 推荐
   logger.debug(f"Processing {len(elements)} elements")
   ```

2. **不要记录敏感信息**
   ```python
   # ❌ 不推荐
   logger.debug(f"密码：{password}")
   
   # ✅ 推荐
   logger.debug(f"密码：***", extra={'masked': True})
   ```

## 🎓 学习资源

- **完整文档**: [`docs/logging_guide.md`](docs/logging_guide.md)
- **测试示例**: [`tests/test_logging.py`](tests/test_logging.py)
- **分析工具**: `python -m core.log_analyzer`

## 📞 获取帮助

遇到问题时：

1. **查看日志文件** - `logs/latest.log`
2. **运行分析工具** - `python -m core.log_analyzer`
3. **搜索关键字** - 在日志中搜索相关操作名称
4. **分享日志** - 将日志内容分享给 AI 助手获取帮助

---

**记住：好的日志是解决问题的第一线索！** ✨
