"""
日志配置模块
支持详细/普通级别，自动记录函数调用、参数、返回值、异常等
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any
import functools
import json
import traceback


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m',       # 重置
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str = 'tdrpa',
    level: str = 'INFO',
    log_to_file: bool = True,
    log_dir: Optional[Path] = None,
    console_output: bool = True,
    detailed_format: bool = False
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_to_file: 是否写入文件
        log_dir: 日志文件目录（默认在项目根目录的 logs 文件夹）
        console_output: 是否输出到控制台
        detailed_format: 是否使用详细格式（包含文件名、行号、函数名）
    
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已有的 handlers
    logger.handlers = []
    
    # 日志格式
    if detailed_format:
        format_str = '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
    else:
        format_str = '%(asctime)s | %(levelname)-8s | %(message)s'
    
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Windows 终端支持 ANSI 颜色
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
            except ImportError:
                pass
        
        console_formatter = ColoredFormatter(format_str, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_to_file:
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / 'logs'
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 按日期生成日志文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'{name}_{timestamp}.log'
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        
        # 文件日志使用详细格式
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
            datefmt=date_format
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 创建最新日志的符号链接（方便查找）
        latest_link = log_dir / 'latest.log'
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        try:
            latest_link.symlink_to(log_file)
        except (OSError, NotImplementedError):
            # Windows 可能需要管理员权限才能创建符号链接
            logger.debug(f"无法创建符号链接：{latest_link}")
    
    logger.info(f"日志系统初始化完成 [级别={level}, 文件={log_to_file}]")
    
    return logger


def log_function_call(
    logger: Optional[logging.Logger] = None,
    log_level: str = 'DEBUG',
    log_args: bool = True,
    log_kwargs: bool = True,
    log_return: bool = True,
    log_exceptions: bool = True,
    mask_args: Optional[list] = None
):
    """
    函数调用日志装饰器
    
    Args:
        logger: 日志记录器（默认使用函数所在模块的 logger）
        log_level: 日志级别
        log_args: 是否记录位置参数
        log_kwargs: 是否记录关键字参数
        log_return: 是否记录返回值
        log_exceptions: 是否记录异常
        mask_args: 需要脱敏的参数名列表（如密码等敏感信息）
    
    Example:
        @log_function_call()
        def my_function(param1, param2):
            pass
        
        @log_function_call(log_level='INFO', mask_args=['password'])
        def login(username, password):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取 logger
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
            
            func_name = func.__name__
            module_name = func.__module__
            
            # 构建日志消息
            log_args_list = []
            
            if log_args and args:
                for i, arg in enumerate(args):
                    arg_str = _safe_repr(arg, mask=i in (mask_args or []))
                    log_args_list.append(f"args[{i}]={arg_str}")
            
            if log_kwargs and kwargs:
                for key, value in kwargs.items():
                    value_str = _safe_repr(value, mask=key in (mask_args or []))
                    log_args_list.append(f"{key}={value_str}")
            
            # 记录函数调用开始
            if log_args_list:
                logger.log(
                    getattr(logging, log_level.upper()),
                    f"▶️ 调用 {module_name}.{func_name}({', '.join(log_args_list)})"
                )
            else:
                logger.log(
                    getattr(logging, log_level.upper()),
                    f"▶️ 调用 {module_name}.{func_name}()"
                )
            
            start_time = datetime.now()
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # 记录返回值
                if log_return:
                    result_str = _safe_repr(result, max_length=200)
                    logger.log(
                        getattr(logging, log_level.upper()),
                        f"✅ {module_name}.{func_name} 返回 [{elapsed:.3f}s]: {result_str}"
                    )
                else:
                    logger.log(
                        getattr(logging, log_level.upper()),
                        f"✅ {module_name}.{func_name} 完成 [{elapsed:.3f}s]"
                    )
                
                return result
                
            except Exception as e:
                # 计算执行时间
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # 记录异常
                if log_exceptions:
                    error_msg = f"❌ {module_name}.{func_name} 异常 [{elapsed:.3f}s]: {type(e).__name__}: {str(e)}"
                    logger.error(error_msg)
                    logger.debug(f"异常堆栈:\n{traceback.format_exc()}")
                raise
        
        return wrapper
    return decorator


def _safe_repr(obj: Any, max_length: int = 100, mask: bool = False) -> str:
    """
    安全地转换对象为字符串表示
    
    Args:
        obj: 任意对象
        max_length: 最大长度（超过则截断）
        mask: 是否脱敏（显示为 ***）
    
    Returns:
        字符串表示
    """
    if mask:
        return '***'
    
    try:
        # 尝试使用 json.dumps 获得更好的格式
        if isinstance(obj, (dict, list, tuple)):
            repr_str = json.dumps(obj, ensure_ascii=False, default=str)
        else:
            repr_str = repr(obj)
    except:
        repr_str = str(obj)
    
    # 截断过长的字符串
    if len(repr_str) > max_length:
        repr_str = repr_str[:max_length] + '...'
    
    return repr_str


class LogContext:
    """
    日志上下文管理器
    用于记录一段代码块的执行
    
    Example:
        with LogContext(logger, "处理数据"):
            # do something
            pass
        
        with LogContext(logger, "复杂操作", log_level='INFO') as ctx:
            ctx.logger.info("中间步骤...")
            # do something
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        log_level: str = 'DEBUG',
        log_exceptions: bool = True
    ):
        self.logger = logger
        self.operation = operation
        self.log_level = log_level
        self.log_exceptions = log_exceptions
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(
            getattr(logging, self.log_level.upper()),
            f"▶️ 开始：{self.operation}"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is not None:
            # 发生异常
            if self.log_exceptions:
                self.logger.error(
                    f"❌ 失败：{self.operation} [{elapsed:.3f}s] - "
                    f"{exc_type.__name__}: {exc_val}"
                )
                self.logger.debug(f"异常堆栈:\n{traceback.format_exc()}")
            return False  # 不抑制异常
        else:
            self.logger.log(
                getattr(logging, self.log_level.upper()),
                f"✅ 完成：{self.operation} [{elapsed:.3f}s]"
            )
            return False


# 便捷函数
def create_detailed_logger(
    name: str = 'tdrpa',
    level: str = 'DEBUG'
) -> logging.Logger:
    """
    创建详细日志的记录器（推荐用于开发调试）
    
    Args:
        name: 记录器名称
        level: 日志级别
    
    Returns:
        配置好的 Logger
    """
    return setup_logger(
        name=name,
        level=level,
        log_to_file=True,
        console_output=True,
        detailed_format=True
    )


def create_simple_logger(
    name: str = 'tdrpa',
    level: str = 'INFO'
) -> logging.Logger:
    """
    创建简单日志的记录器（推荐用于生产环境）
    
    Args:
        name: 记录器名称
        level: 日志级别
    
    Returns:
        配置好的 Logger
    """
    return setup_logger(
        name=name,
        level=level,
        log_to_file=True,
        console_output=True,
        detailed_format=False
    )


# 全局日志记录器实例
_default_logger: Optional[logging.Logger] = None


def get_logger(
    name: str = 'tdrpa',
    level: str = 'DEBUG',
    detailed: bool = True
) -> logging.Logger:
    """
    获取全局日志记录器
    
    Args:
        name: 记录器名称
        level: 日志级别
        detailed: 是否使用详细格式
    
    Returns:
        Logger 实例
    """
    global _default_logger
    
    if _default_logger is None:
        _default_logger = setup_logger(
            name=name,
            level=level,
            log_to_file=True,
            console_output=True,
            detailed_format=detailed
        )
    
    return _default_logger
