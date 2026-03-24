@echo off
REM 分析最新日志
REM 用法：analyze_log.bat [日志文件路径]

echo ================================================================================
echo   tdRPA-mcp 日志分析工具
echo ================================================================================
echo.

if "%~1"=="" (
    echo [信息] 使用最新日志文件...
    python -m core.log_analyzer
) else (
    echo [信息] 分析日志文件：%~1
    python -m core.log_analyzer %~1
)

echo.
echo ================================================================================
echo   常用分析命令:
echo ================================================================================
echo.
echo   # 搜索特定关键字
echo   python -m core.log_analyzer ^| findstr "搜一搜"
echo.
echo   # 只查看错误
echo   python -m core.log_analyzer ^| findstr "ERROR"
echo.
echo   # 导出为 JSON
echo   python -c "from core.log_analyzer import *; analyzer = LogAnalyzer(find_latest_log()); analyzer.export_to_json('analysis.json')"
echo.
echo ================================================================================
pause
