"""
焦点扩散管理器
结合 CV 预筛选和 UIA 扫描，实现智能分层扫描
"""
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

from .grid_manager import GridManager, GridRect
from .cv_prefilter import CVPreFilter
from .uia_region_scanner import UIARegionScanner, ElementInfo

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """扫描结果"""
    grid_id: int
    elements: List[ElementInfo]
    activity_score: float
    scan_time: float  # 毫秒


class FocusDiffusionScanner:
    """焦点扩散扫描器"""
    
    def __init__(self, 
                 process_name: str = None,
                 window_title: str = None,
                 grid_rows: int = 4,
                 grid_cols: int = 4,
                 cv_threshold: float = 0.01,
                 use_cv_prefilter: bool = True,
                 parallel_scan: bool = True):
        """
        :param process_name: 目标进程名
        :param window_title: 窗口标题
        :param grid_rows: 宫格行数
        :param grid_cols: 宫格列数
        :param cv_threshold: CV 活跃度阈值
        :param use_cv_prefilter: 是否使用 CV 预筛选
        :param parallel_scan: 是否并行扫描
        """
        self.use_cv_prefilter = use_cv_prefilter
        self.parallel_scan = parallel_scan
        
        # 初始化扫描器
        self.scanner = UIARegionScanner(
            process_name=process_name,
            window_title=window_title
        )
        
        # 获取窗口矩形
        window_rect = self.scanner.get_window_rect()
        
        # 初始化宫格管理器
        self.grid_manager = GridManager(
            window_rect, 
            rows=grid_rows, 
            cols=grid_cols
        )
        
        # 初始化 CV 预筛选器
        if use_cv_prefilter:
            self.cv_prefilter = CVPreFilter(threshold=cv_threshold)
        else:
            self.cv_prefilter = None
        
        # 缓存
        self.cache: Dict[int, ScanResult] = {}
        self.current_focus: int = 0
    
    def set_focus(self, x: int, y: int) -> int:
        """
        设置焦点位置
        :param x, y: 屏幕坐标
        :return: 焦点宫格 ID
        """
        try:
            grid = self.grid_manager.get_grid_by_position(x, y)
            self.current_focus = grid.id
            logger.info(f"Focus set to grid {self.current_focus} at ({x}, {y})")
            return self.current_focus
        except ValueError as e:
            logger.warning(f"Point outside window: {e}")
            # 使用中心点作为默认焦点
            center_grid = self.grid_manager.get_grid_by_id(7)
            self.current_focus = 7
            return 7
    
    def set_focus_by_grid(self, grid_id: int) -> int:
        """直接设置焦点宫格"""
        if 0 <= grid_id < 16:
            self.current_focus = grid_id
            return grid_id
        raise ValueError(f"Invalid grid_id: {grid_id}")
    
    def scan_all(self, force: bool = False) -> Dict[int, ScanResult]:
        """
        扫描所有宫格
        :param force: 是否强制重新扫描 (忽略缓存)
        :return: {grid_id: ScanResult}
        """
        import time
        
        # 安全检查：确保属性存在
        if not hasattr(self, 'use_cv_prefilter'):
            logger.warning("use_cv_prefilter attribute missing, using default False")
            self.use_cv_prefilter = False
        
        grids = self.grid_manager.get_all_grids()
        grid_rects = [grid.to_tuple() for grid in grids]
        
        # CV 预筛选
        if self.use_cv_prefilter and self.cv_prefilter:
            logger.info("Running CV prefilter...")
            active_grid_ids = self.cv_prefilter.filter_active_grids(
                grid_rects, 
                threshold=self.cv_prefilter.threshold
            )
        else:
            active_grid_ids = list(range(len(grids)))
        
        results = {}
        
        # 按扩散顺序扫描
        scan_order = self.grid_manager.get_diffusion_order(self.current_focus)
        
        for grid_id in scan_order:
            if grid_id not in active_grid_ids and not force:
                logger.debug(f"Skipping inactive grid {grid_id}")
                continue
            
            # 检查缓存
            if grid_id in self.cache and not force:
                results[grid_id] = self.cache[grid_id]
                continue
            
            # 扫描
            start_time = time.time()
            grid = grids[grid_id]
            elements = self.scanner.scan_grid(grid.to_tuple())
            scan_time = (time.time() - start_time) * 1000
            
            # 获取活跃度分数
            if self.cv_prefilter:
                activity_score = self.cv_prefilter.detect_ui_activity(
                    self.cv_prefilter.screenshot_grid(grid.to_tuple())
                )
            else:
                activity_score = 0.0
            
            result = ScanResult(
                grid_id=grid_id,
                elements=elements,
                activity_score=activity_score,
                scan_time=scan_time
            )
            
            results[grid_id] = result
            self.cache[grid_id] = result
            
            logger.info(
                f"Grid {grid_id}: {len(elements)} elements, "
                f"activity={activity_score:.3f}, time={scan_time:.1f}ms"
            )
        
        return results
    
    def scan_focus_area(self, layers: int = 1) -> Dict[int, ScanResult]:
        """
        只扫描焦点附近区域
        :param layers: 扫描层数 (0=只焦点，1=焦点 + 相邻，2=全部)
        :return: {grid_id: ScanResult}
        """
        scan_order = self.grid_manager.get_diffusion_order(self.current_focus)
        
        # 根据 layers 确定扫描范围
        if layers == 0:
            target_grids = [scan_order[0]]
        elif layers == 1:
            target_grids = scan_order[:9]  # 焦点 + 相邻 8 格
        else:
            target_grids = scan_order
        
        results = {}
        for grid_id in target_grids:
            grid = self.grid_manager.get_grid_by_id(grid_id)
            elements = self.scanner.scan_grid(grid.to_tuple())
            
            if self.cv_prefilter:
                activity_score = self.cv_prefilter.detect_ui_activity(
                    self.cv_prefilter.screenshot_grid(grid.to_tuple())
                )
            else:
                activity_score = 0.0
            
            result = ScanResult(
                grid_id=grid_id,
                elements=elements,
                activity_score=activity_score,
                scan_time=0.0  # 简化处理
            )
            results[grid_id] = result
        
        return results
    
    def find_element_in_grids(self, grid_ids: List[int], 
                             element_name: str = None,
                             control_type: str = None
                            ) -> Optional[ElementInfo]:
        """
        在指定宫格中查找元素
        :param grid_ids: 宫格 ID 列表
        :param element_name: 元素名称 (可选)
        :param control_type: 控件类型 (可选)
        :return: 匹配的元素信息
        """
        for grid_id in grid_ids:
            if grid_id in self.cache:
                result = self.cache[grid_id]
                for elem in result.elements:
                    match = True
                    if element_name and element_name.lower() not in elem.name.lower():
                        match = False
                    if control_type and control_type.lower() not in elem.control_type.lower():
                        match = False
                    
                    if match:
                        logger.info(
                            f"Found element '{elem.name}' in grid {grid_id}"
                        )
                        return elem
        
        logger.info(f"Element not found in specified grids")
        return None
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_all_elements(self) -> List[ElementInfo]:
        """获取所有已扫描宫格的元素"""
        elements = []
        for result in self.cache.values():
            elements.extend(result.elements)
        return elements
    
    def get_elements_by_grid(self) -> Dict[int, List[ElementInfo]]:
        """按宫格分组获取元素"""
        return {
            grid_id: result.elements 
            for grid_id, result in self.cache.items()
        }
