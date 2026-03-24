"""
tdRPA-mcp: 基于 tdrpa 的 UIA 元素查找 MCP 服务
"""
from .core.grid_manager import GridManager, GridRect
from .core.cv_prefilter import CVPreFilter
from .core.uia_region_scanner import UIARegionScanner, ElementInfo
from .core.focus_diffusion import FocusDiffusionScanner, ScanResult

__version__ = '1.0.0'
__all__ = [
    'GridManager',
    'GridRect', 
    'CVPreFilter',
    'UIARegionScanner',
    'ElementInfo',
    'FocusDiffusionScanner',
    'ScanResult'
]
