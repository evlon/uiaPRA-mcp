"""
日志分析工具
用于查看、过滤、分析日志文件
"""
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: str
    logger_name: str
    file_path: str
    line_number: int
    function_name: str
    message: str
    raw_line: str
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'logger_name': self.logger_name,
            'file': f"{self.file_path}:{self.line_number}",
            'function': self.function_name,
            'message': self.message
        }


class LogAnalyzer:
    """日志分析器"""
    
    # 日志行正则表达式
    LOG_PATTERN = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| '
        r'(?P<level>[A-Z]+) \| '
        r'(?P<logger>[^\|]+) \| '
        r'(?P<file>[^:]+):(?P<line>\d+) \| '
        r'(?P<function>[^\|]+) \| '
        r'(?P<message>.+)'
    )
    
    def __init__(self, log_file: Path):
        """
        Args:
            log_file: 日志文件路径
        """
        self.log_file = log_file
        self.entries: List[LogEntry] = []
        self._load_logs()
    
    def _load_logs(self):
        """加载日志文件"""
        self.entries = []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                match = self.LOG_PATTERN.match(line)
                if match:
                    try:
                        entry = LogEntry(
                            timestamp=datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S'),
                            level=match.group('level'),
                            logger_name=match.group('logger').strip(),
                            file_path=match.group('file'),
                            line_number=int(match.group('line')),
                            function_name=match.group('function').strip(),
                            message=match.group('message'),
                            raw_line=line
                        )
                        self.entries.append(entry)
                    except Exception as e:
                        # 解析失败的行跳过
                        pass
    
    def filter_by_level(self, level: str) -> List[LogEntry]:
        """按日志级别过滤"""
        return [e for e in self.entries if e.level == level.upper()]
    
    def filter_by_time_range(
        self,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[LogEntry]:
        """按时间范围过滤"""
        if end is None:
            return [e for e in self.entries if e.timestamp >= start]
        return [e for e in self.entries if start <= e.timestamp <= end]
    
    def filter_by_function(self, function_name: str) -> List[LogEntry]:
        """按函数名过滤（支持模糊匹配）"""
        return [e for e in self.entries if function_name.lower() in e.function_name.lower()]
    
    def filter_by_file(self, file_pattern: str) -> List[LogEntry]:
        """按文件名过滤（支持模糊匹配）"""
        return [e for e in self.entries if file_pattern in e.file_path]
    
    def search(self, keyword: str) -> List[LogEntry]:
        """搜索包含关键字的日志"""
        return [e for e in self.entries if keyword.lower() in e.message.lower()]
    
    def get_errors(self) -> List[LogEntry]:
        """获取所有错误日志"""
        return self.filter_by_level('ERROR') + self.filter_by_level('CRITICAL')
    
    def get_warnings(self) -> List[LogEntry]:
        """获取所有警告日志"""
        return self.filter_by_level('WARNING')
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'total_entries': len(self.entries),
            'by_level': {},
            'by_file': {},
            'time_range': {
                'start': min(e.timestamp for e in self.entries).isoformat() if self.entries else None,
                'end': max(e.timestamp for e in self.entries).isoformat() if self.entries else None,
            },
            'error_count': len(self.get_errors()),
            'warning_count': len(self.get_warnings())
        }
        
        # 按级别统计
        for entry in self.entries:
            level = entry.level
            stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
        
        # 按文件统计
        for entry in self.entries:
            file_name = Path(entry.file_path).name
            stats['by_file'][file_name] = stats['by_file'].get(file_name, 0) + 1
        
        return stats
    
    def print_timeline(self, limit: int = 50):
        """打印时间线（最近的日志）"""
        print(f"\n{'='*80}")
        print(f" 日志时间线 (最近 {limit} 条)")
        print(f"{'='*80}\n")
        
        for entry in self.entries[-limit:]:
            time_str = entry.timestamp.strftime('%H:%M:%S')
            print(f"[{time_str}] {entry.level:8s} | {entry.function_name:20s} | {entry.message[:60]}")
    
    def print_errors(self):
        """打印所有错误日志"""
        errors = self.get_errors()
        
        if not errors:
            print("\n[OK] 没有错误日志")
            return
        
        print(f"\n{'='*80}")
        print(f" 错误日志 ({len(errors)} 条)")
        print(f"{'='*80}\n")
        
        for entry in errors:
            print(f"[{entry.timestamp.strftime('%H:%M:%S')}] {entry.function_name}")
            print(f"  文件：{entry.file_path}:{entry.line_number}")
            print(f"  消息：{entry.message}")
            print()
    
    def export_to_json(self, output_file: Path):
        """导出为 JSON 格式"""
        data = {
            'log_file': str(self.log_file),
            'export_time': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'entries': [e.to_dict() for e in self.entries]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 已导出到：{output_file}")


def find_latest_log(log_dir: Optional[Path] = None) -> Optional[Path]:
    """
    查找最新的日志文件
    
    Args:
        log_dir: 日志目录（默认使用项目 logs 目录）
    
    Returns:
        最新日志文件路径
    """
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / 'logs'
    
    if not log_dir.exists():
        return None
    
    # 尝试通过符号链接获取
    latest_link = log_dir / 'latest.log'
    if latest_link.is_symlink():
        try:
            return latest_link.resolve()
        except:
            pass
    
    # 查找最新的日志文件
    log_files = list(log_dir.glob('*.log'))
    if not log_files:
        return None
    
    return max(log_files, key=lambda f: f.stat().st_mtime)


def analyze_latest_log():
    """分析最新的日志文件（便捷函数）"""
    log_file = find_latest_log()
    
    if not log_file:
        print("[错误] 未找到日志文件")
        return
    
    print(f"[信息] 分析日志文件：{log_file}")
    
    analyzer = LogAnalyzer(log_file)
    
    # 打印统计信息
    stats = analyzer.get_statistics()
    print(f"\n{'='*80}")
    print(f" 日志统计信息")
    print(f"{'='*80}")
    print(f"总条目数：{stats['total_entries']}")
    print(f"时间范围：{stats['time_range']['start']} - {stats['time_range']['end']}")
    print(f"错误数：{stats['error_count']}")
    print(f"警告数：{stats['warning_count']}")
    
    print(f"\n按级别分布:")
    for level, count in sorted(stats['by_level'].items()):
        print(f"  {level}: {count}")
    
    print(f"\n按文件分布 (Top 5):")
    sorted_files = sorted(stats['by_file'].items(), key=lambda x: x[1], reverse=True)[:5]
    for file_name, count in sorted_files:
        print(f"  {file_name}: {count}")
    
    # 显示错误
    analyzer.print_errors()
    
    # 显示时间线
    analyzer.print_timeline(limit=30)
    
    return analyzer


# CLI 入口
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 指定日志文件
        log_file = Path(sys.argv[1])
    else:
        # 使用最新日志
        log_file = find_latest_log()
    
    if log_file:
        analyze_latest_log()
    else:
        print("[错误] 未找到日志文件")
        print("用法：python -m core.log_analyzer [日志文件路径]")
