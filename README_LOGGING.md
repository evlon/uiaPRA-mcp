# 📝 tdRPA-mcp 日志系统 - 完全指南

## 🎯 快速开始（30 秒上手）

### 1️⃣ 运行测试生成日志
```bash
python tests/test_logging.py
```

### 2️⃣ 查看日志文件
打开 `logs/latest.log` 查看最新日志

### 3️⃣ 分析日志
```bash
# Windows
analyze_log.bat

# 或手动运行
python -m core.log_analyzer
```

**就这么简单！** 🎉

---

## 📚 完整文档导航

### 📖 新手入门
- **[快速开始](docs/LOGGING_QUICKSTART.md)** - 5 分钟上手教程
  - 为什么需要日志
  - 基本用法
  - 常见问题分析示例

### 📖 深入使用
- **[详细指南](docs/logging_guide.md)** - 完整使用手册
  - 所有 API 说明
  - 高级用法
  - 最佳实践
  - 性能优化

### 📖 更新记录
- **[更新日志](docs/CHANGELOG_LOGGING_SYSTEM.md)** - 功能和计划
  - 已实现功能
  - 技术细节
  - 后续迭代计划

---

## 🔧 核心功能速览

### 功能 1: 自动记录函数调用

```python
from core.logger import get_logger, log_function_call

logger = get_logger('my_module')

@log_function_call(logger=logger)
def find_element(selector, timeout=5.0):
    return result

# 日志输出:
# ▶️ 调用 my_module.find_element(selector={'ctrl': [...]}, timeout=5.0)
# ✅ my_module.find_element 返回 [0.125s]: <result>
```

### 功能 2: 代码块上下文记录

```python
from core.logger import LogContext

with LogContext(logger, "复杂的数据处理"):
    logger.info("步骤 1: 准备数据")
    # ... 处理代码
    logger.info("步骤 2: 输出结果")

# 日志输出:
# ▶️ 开始：复杂的数据处理
# 步骤 1: 准备数据
# 步骤 2: 输出结果
# ✅ 完成：复杂的数据处理 [1.234s]
```

### 功能 3: 敏感数据脱敏

```python
@log_function_call(
    logger=logger,
    mask_args=['password', 'token']  # 这些参数会显示为 ***
)
def login(username, password):
    pass

# 日志输出:
# ▶️ 调用 module.login(username='admin', password='***')
```

### 功能 4: 日志分析工具

```python
from core.log_analyzer import LogAnalyzer, find_latest_log

# 获取最新日志
log_file = find_latest_log()

# 创建分析器
analyzer = LogAnalyzer(log_file)

# 查看统计
stats = analyzer.get_statistics()
print(f"错误数：{stats['error_count']}")

# 搜索特定内容
results = analyzer.search("搜一搜")
for log in results:
    print(f"[{log.level}] {log.message}")

# 导出 JSON
analyzer.export_to_json(Path('analysis.json'))
```

---

## 🎨 日志级别说明

| 级别 | 用途 | 何时使用 |
|------|------|----------|
| **DEBUG** | 详细调试信息 | 开发、调试问题 |
| **INFO** | 一般信息 | 正常操作流程 |
| **WARNING** | 警告 | 非致命问题 |
| **ERROR** | 错误 | 操作失败、异常 |
| **CRITICAL** | 严重错误 | 系统级故障 |

---

## 💡 使用场景

### 场景 1: 开发新功能

```python
from core.logger import get_logger

logger = get_logger('my_feature', level='DEBUG')

def new_feature():
    logger.debug("开始执行新功能")
    
    try:
        # 步骤 1
        logger.debug("步骤 1: 准备数据")
        data = prepare_data()
        
        # 步骤 2
        logger.info("步骤 2: 处理数据")
        result = process(data)
        
        logger.info("✅ 新功能执行成功")
        return result
        
    except Exception as e:
        logger.error(f"❌ 新功能执行失败：{e}", exc_info=True)
        raise
```

### 场景 2: 排查问题

```bash
# 1. 运行有问题的代码
python tests/test_find_susou_button.py

# 2. 查看错误
python -m core.log_analyzer | findstr "ERROR"

# 3. 搜索相关操作
python -m core.log_analyzer | findstr "selector\|match"

# 4. 查看详细时间线
python -c "from core.log_analyzer import *; analyze_latest_log()"
```

### 场景 3: 性能优化

```python
@log_function_call(logger=logger, log_level='INFO')
def slow_function():
    """这个函数可能会很慢"""
    pass

# 查看日志中的执行时间:
# ✅ slow_function 返回 [2.345s]: <result>
```

---

## 🛠️ 常用命令

### 查看日志
```bash
# 分析最新日志
python -m core.log_analyzer

# 分析指定日志
python -m core.log_analyzer logs/tdrpa_20260325_143022.log

# Windows 快捷方式
analyze_log.bat
```

### 搜索日志
```bash
# 搜索关键字
python -m core.log_analyzer | findstr "搜一搜"

# 只看错误
python -m core.log_analyzer | findstr "ERROR"

# 只看某个函数的日志
python -m core.log_analyzer | findstr "scan_grid"
```

### 管理日志
```bash
# 删除 7 天前的日志 (Windows)
forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path"

# 查看日志目录大小
du -sh logs/
```

---

## 📁 文件结构

```
tdRPA-mcp/
├── core/
│   ├── logger.py              # 日志核心模块 ✨ NEW
│   └── log_analyzer.py        # 日志分析工具 ✨ NEW
├── docs/
│   ├── logging_guide.md       # 详细使用指南 ✨ NEW
│   ├── LOGGING_QUICKSTART.md  # 快速开始 ✨ NEW
│   └── CHANGELOG_LOGGING_SYSTEM.md  # 更新日志 ✨ NEW
├── tests/
│   ├── test_logging.py        # 日志功能测试 ✨ NEW
│   └── test_find_susou_button.py     # 已更新带日志
├── logs/                       # 日志文件目录 ✨ NEW
│   ├── tdrpa_20260325_*.log   # 按时间戳命名的日志
│   └── latest.log             # 指向最新日志的链接
└── analyze_log.bat            # Windows 一键分析脚本 ✨ NEW
```

---

## 🎓 学习路径

### 初学者
1. 阅读 [快速开始](docs/LOGGING_QUICKSTART.md)
2. 运行 `python tests/test_logging.py`
3. 使用 `analyze_log.bat` 查看日志
4. 尝试在自己的代码中添加 logger

### 进阶用户
1. 阅读 [详细指南](docs/logging_guide.md)
2. 学习使用装饰器和上下文管理器
3. 掌握日志分析工具的各种过滤方法
4. 在关键路径添加性能监控

### 高级用户
1. 自定义日志格式和输出
2. 集成到 CI/CD 流程
3. 配置日志告警
4. 参与后续迭代开发

---

## ❓ 常见问题

### Q: 日志太多怎么办？
**A:** 调整日志级别：
```python
# 生产环境使用 INFO 级别
logger = get_logger('my_module', level='INFO')
```

### Q: 如何关闭日志？
**A:** 设置级别为 CRITICAL：
```python
logger = get_logger('my_module', level='CRITICAL')
```

### Q: 日志文件太大怎么办？
**A:** 定期清理旧日志：
```bash
# Windows
forfiles /p logs /s /m *.log /d -7 /c "cmd /c del @path"
```

### Q: 如何在控制台看到彩色日志？
**A:** 默认就是彩色的！如果看不到，安装 colorama：
```bash
pip install colorama
```

### Q: 日志文件在哪里？
**A:** 默认在 `logs/` 目录，最新的是 `latest.log`

---

## 🔮 后续计划

### Phase 2 (计划中)
- [ ] 结构化日志（JSON 格式）
- [ ] 日志轮转和自动清理
- [ ] 性能剖析（热点函数统计）
- [ ] 实时日志流

### Phase 3 (未来)
- [ ] 异常模式识别
- [ ] 性能瓶颈自动检测
- [ ] AI 辅助问题诊断
- [ ] 日志聚类和去重

---

## 🤝 反馈和支持

### 遇到问题？
1. 查看 [快速开始](docs/LOGGING_QUICKSTART.md)
2. 运行 `python tests/test_logging.py` 测试功能
3. 分析日志：`python -m core.log_analyzer`
4. 提交 Issue 时附上相关日志片段

### 日志位置
- 默认目录：`d:/projects/wx-rpa/tdRPA-mcp/logs/`
- 最新日志：`logs/latest.log`

---

## 🎉 总结

tdRPA-mcp 现在拥有完整的日志系统，让您能够：

✅ **快速定位问题** - 详细的执行记录  
✅ **高效调试代码** - 自动记录函数调用  
✅ **远程协助简单** - 一份日志说明一切  
✅ **持续改进优化** - 基于日志数据分析  

**记住：好的日志是解决问题的第一线索！** ✨

---

*最后更新：2026-03-25*
