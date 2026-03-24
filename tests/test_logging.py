"""
测试日志系统功能
展示日志记录的各种用法
"""
import sys
sys.path.insert(0, '.')

from core.logger import (
    get_logger, 
    log_function_call, 
    LogContext,
    create_detailed_logger,
    create_simple_logger
)
from pathlib import Path


def test_basic_logging():
    """测试基本日志功能"""
    print("\n" + "=" * 80)
    print(" 测试 1: 基本日志功能")
    print("=" * 80)
    
    # 获取 logger
    logger = get_logger('test.basic', level='DEBUG', detailed=True)
    
    # 测试各级别日志
    logger.debug("这是一条 DEBUG 日志（详细调试信息）")
    logger.info("这是一条 INFO 日志（一般信息）")
    logger.warning("这是一条 WARNING 日志（警告）")
    logger.error("这是一条 ERROR 日志（错误）")
    
    print("\n[OK] 基本日志测试完成")
    print(f"[提示] 日志文件位置：查看 logs/ 目录")


@log_function_call(log_args=True, log_return=True, log_level='INFO')
def add_with_logging(a: int, b: int) -> int:
    """带日志的加法函数"""
    return a + b


@log_function_call(log_args=True, log_exceptions=True)
def divide_with_logging(a: int, b: int) -> float:
    """带日志的除法函数（可能抛出异常）"""
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


def test_decorator():
    """测试装饰器功能"""
    print("\n" + "=" * 80)
    print(" 测试 2: 日志装饰器")
    print("=" * 80)
    
    logger = get_logger('test.decorator', level='DEBUG', detailed=True)
    
    # 测试正常调用
    print("\n调用 add_with_logging(3, 5)...")
    result = add_with_logging(3, 5)
    print(f"结果：{result}")
    
    # 测试异常
    print("\n调用 divide_with_logging(10, 0)...")
    try:
        result = divide_with_logging(10, 0)
    except Exception as e:
        print(f"捕获异常：{e}")
    
    print("\n[OK] 装饰器测试完成")


def test_context_manager():
    """测试上下文管理器"""
    print("\n" + "=" * 80)
    print(" 测试 3: 日志上下文管理器")
    print("=" * 80)
    
    logger = get_logger('test.context', level='DEBUG', detailed=True)
    
    # 使用上下文管理器
    with LogContext(logger, "复杂的数据处理流程", log_level='INFO') as ctx:
        ctx.logger.info("步骤 1: 准备数据...")
        # 模拟处理
        data = list(range(10))
        
        ctx.logger.info(f"步骤 2: 处理 {len(data)} 个数据项...")
        # 模拟处理
        
        ctx.logger.info("步骤 3: 输出结果...")
        # 模拟输出
    
    # 测试异常情况
    print("\n测试异常情况的日志记录...")
    try:
        with LogContext(logger, "可能失败的操作", log_level='INFO') as ctx:
            ctx.logger.info("开始执行...")
            raise ValueError("模拟的错误")
    except Exception as e:
        print(f"捕获异常：{e}")
    
    print("\n[OK] 上下文管理器测试完成")


def test_nested_logging():
    """测试嵌套日志"""
    print("\n" + "=" * 80)
    print(" 测试 4: 嵌套日志调用")
    print("=" * 80)
    
    logger = get_logger('test.nested', level='DEBUG', detailed=True)
    
    @log_function_call(logger=logger)
    def outer_function(x):
        logger.info(f"外部函数收到参数：{x}")
        
        @log_function_call(logger=logger)
        def inner_function(y):
            logger.info(f"内部函数收到参数：{y}")
            return y * 2
        
        result = inner_function(x + 1)
        logger.info(f"外部函数结果：{result}")
        return result
    
    print("\n调用嵌套函数...")
    result = outer_function(5)
    print(f"最终结果：{result}")
    
    print("\n[OK] 嵌套日志测试完成")


def test_sensitive_data_masking():
    """测试敏感数据脱敏"""
    print("\n" + "=" * 80)
    print(" 测试 5: 敏感数据脱敏")
    print("=" * 80)
    
    logger = get_logger('test.masking', level='DEBUG', detailed=True)
    
    @log_function_call(
        logger=logger,
        log_args=True,
        mask_args=['password', 'secret']  # 指定需要脱敏的参数
    )
    def login(username, password, secret=None):
        logger.info(f"用户登录：{username}")
        return True
    
    print("\n调用 login 函数（密码会自动脱敏）...")
    login("admin", password="super_secret_123", secret="my_secret_key")
    
    print("\n[OK] 脱敏测试完成")


def analyze_logs():
    """分析刚生成的日志"""
    print("\n" + "=" * 80)
    print(" 分析日志文件")
    print("=" * 80)
    
    from core.log_analyzer import find_latest_log, LogAnalyzer
    
    log_file = find_latest_log()
    
    if not log_file:
        print("[错误] 未找到日志文件")
        return
    
    print(f"\n最新日志文件：{log_file}")
    
    analyzer = LogAnalyzer(log_file)
    stats = analyzer.get_statistics()
    
    print(f"\n统计信息:")
    print(f"  总条目数：{stats['total_entries']}")
    print(f"  错误数：{stats['error_count']}")
    print(f"  警告数：{stats['warning_count']}")
    
    print(f"\n按级别分布:")
    for level, count in sorted(stats['by_level'].items()):
        print(f"  {level}: {count}")
    
    # 显示最近的日志
    print("\n最近 10 条日志:")
    analyzer.print_timeline(limit=10)


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print(" tdRPA-mcp 日志系统功能测试")
    print("=" * 80)
    
    try:
        # 运行测试
        test_basic_logging()
        test_decorator()
        test_context_manager()
        test_nested_logging()
        test_sensitive_data_masking()
        
        # 分析日志
        analyze_logs()
        
        print("\n" + "=" * 80)
        print(" ✅ 所有测试完成！")
        print("=" * 80)
        print("\n[提示] 可以使用以下命令查看日志:")
        print("  python -m core.log_analyzer")
        print(f"  或直接运行：analyze_log.bat")
        print("\n[提示] 日志文件位置：logs/")
        
    except Exception as e:
        print(f"\n[错误] 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
