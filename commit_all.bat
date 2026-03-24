@echo off
REM ===================================
REM tdRPA-mcp Git 自动提交脚本
REM ===================================

echo.
echo ===================================
echo   tdRPA-mcp Git 提交脚本
echo ===================================
echo.

REM 检查 Git 是否安装
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Git，请先安装 Git
    pause
    exit /b 1
)

REM 检查是否在 Git 仓库中
if not exist .git (
    echo [错误] 当前目录不是 Git 仓库
    pause
    exit /b 1
)

echo [信息] 开始 Git 提交流程...
echo.

REM Commit 1: 核心功能
echo [1/9] 提交核心功能增强...
git add core/ui_tree_scanner.py core/semantic_filter.py tools/grid_picker.py 2>nul
if not ERRORLEVEL 1 (
    git commit -m "feat: 实现语义化 UI 元素过滤系统

- 新增 SemanticFilter 模块，支持灵活的语义化查询
- 增强 UITreeScanner，提供 get_grouped_ui_tree() API
- 更新 grid_picker，新增 filter_ui_elements 等 3 个工具
- 支持自然语言描述自动转换为过滤条件
- 改进 scan_region 使用新的灵活 API"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 2: 日志系统
echo [2/9] 提交日志系统...
git add core/logger.py core/log_analyzer.py analyze_log.bat 2>nul
if not ERRORLEVEL 1 (
    git commit -m "feat: 实现完整的日志系统

- 新增 logger 模块，支持多级日志和自动记录
- 新增 log_analyzer 模块，支持日志分析和导出
- 添加 @log_function_call 装饰器
- 添加 LogContext 上下文管理器
- 支持彩色控制台输出和文件输出
- 新增一键日志分析脚本"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 3: 日志集成
echo [3/9] 提交日志集成...
git add core/uia_region_scanner.py tools/grid_picker.py tests/test_find_susou_button.py 2>nul
if not ERRORLEVEL 1 (
    git commit -m "refactor: 集成日志系统到核心模块

- 在 UIARegionScanner 中集成日志
- 在 MCP 工具中集成日志
- 在测试用例中集成日志
- 使用 @log_function_call 装饰器
- 使用 LogContext 记录关键操作"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 4: 测试用例
echo [4/9] 提交测试用例...
git add tests/test_logging.py tests/test_semantic_filter.py tests/test_mcp_semantic_search.py tests/test_current_window.py 2>nul
if not ERRORLEVEL 1 (
    git commit -m "test: 新增日志和语义化过滤测试

- 新增 test_logging.py 测试日志功能
- 新增 test_semantic_filter.py 测试语义过滤
- 新增 test_mcp_semantic_search.py 测试 MCP 集成
- 新增 test_current_window.py 测试窗口检测"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 5: 设计思想
echo [5/9] 提交设计思想文档...
git add docs/DESIGN_PHILOSOPHY.md 2>nul
if not ERRORLEVEL 1 (
    git commit -m "docs: 添加产品设计思想文档

- 详细阐述 4 大核心设计理念
- 说明 4 个创新点和技术选型
- 描述架构演进路线
- 展望未来发展方向"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 6: 系统架构
echo [6/9] 提交系统架构文档...
git add docs/ARCHITECTURE.md 2>nul
if not ERRORLEVEL 1 (
    git commit -m "docs: 添加系统架构详解文档

- 完整的分层架构图
- 6 个核心模块详细说明
- 数据流设计和关键算法
- 性能优化和安全考虑"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 7: 日志文档
echo [7/9] 提交日志文档...
git add docs/logging_guide.md docs/LOGGING_QUICKSTART.md docs/CHANGELOG_LOGGING_SYSTEM.md 2>nul
if not ERRORLEVEL 1 (
    git commit -m "docs: 添加日志系统完整文档

- 详细使用指南
- 快速开始教程
- 更新日志和变更说明"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM Commit 8: 主 README
echo [8/9] 更新主 README...
if exist README.md (
    move README.md README_OLD.md >nul
    echo   [重命名] README.md -> README_OLD.md
)
if exist README_NEW.md (
    move README_NEW.md README.md >nul
    echo   [重命名] README_NEW.md -> README.md
    git add README.md README_OLD.md 2>nul
    git commit -m "docs: 更新主 README

- 全新的产品介绍和核心价值
- 5 大核心优势说明
- 设计思想和系统架构概述
- 完整的文档导航
- 快速开始和使用场景"
    echo   [OK] 提交成功
) else (
    echo   [跳过] README_NEW.md 不存在
)
echo.

REM Commit 9: 清理
echo [9/9] 项目清理...
git add .gitignore 2>nul
if not ERRORLEVEL 1 (
    git commit -m "chore: 项目清理和整理

- 添加 .gitignore 文件
- 清理__pycache__和*.pyc 文件
- 清理临时文件和日志
- 整理项目结构"
    echo   [OK] 提交成功
) else (
    echo   [跳过] 没有文件需要提交
)
echo.

REM 显示提交历史
echo ===================================
echo   最近的提交历史:
echo ===================================
git log --oneline -10
echo.

echo ===================================
echo   ✅ Git 提交流程完成！
echo ===================================
echo.

REM 提示
echo 下一步:
echo 1. 检查提交历史：git log --oneline
echo 2. 查看状态：git status
echo 3. 推送到远程：git push origin main
echo.

pause
