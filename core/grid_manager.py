"""
宫格管理器
支持 9 宫格 (3x3) 和 16 宫格 (4x4)，支持自然语言方位描述
"""
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


# 9 宫格的自然语言方位映射
POSITION_NAMES_3X3 = {
    (0, 0): '左上', (0, 1): '上中', (0, 2): '右上',
    (1, 0): '左中', (1, 1): '中间', (1, 2): '右中',
    (2, 0): '左下', (2, 1): '下中', (2, 2): '右下',
}

# 反向映射：自然语言 -> 宫格 ID
POSITION_NAME_TO_ID = {
    '左上': 0, '上中': 1, '右上': 2,
    '左中': 3, '中间': 4, '右中': 5,
    '左下': 6, '下中': 7, '右下': 8,
    # 别名支持
    '中心': 4, '中央': 4, '正中': 4,
    '左边': 3, '右边': 5, '上边': 1, '下边': 7,
}


@dataclass
class GridRect:
    """宫格矩形"""
    id: int
    left: int
    top: int
    right: int
    bottom: int
    
    @property
    def width(self) -> int:
        return self.right - self.left
    
    @property
    def height(self) -> int:
        return self.bottom - self.top
    
    @property
    def center(self) -> Tuple[int, int]:
        return ((self.left + self.right) // 2, 
                (self.top + self.bottom) // 2)
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.left, self.top, self.right, self.bottom)


class GridManager:
    """宫格管理器"""
    
    def __init__(self, window_rect: Tuple[int, int, int, int], 
                 rows: int = 3, cols: int = 3):  # 默认改为 9 宫格
        """
        :param window_rect: 窗口矩形 (left, top, right, bottom)
        :param rows: 行数 (默认 3)
        :param cols: 列数 (默认 3)
        """
        self.window_rect = window_rect
        self.rows = rows
        self.cols = cols
        self.grids = self._split_to_grids()
        
        # 如果是 3x3 网格，启用自然语言方位支持
        self.use_position_names = (rows == 3 and cols == 3)
    
    def _split_to_grids(self) -> List[GridRect]:
        """将窗口区域划分为网格"""
        left, top, right, bottom = self.window_rect
        width = (right - left) // self.cols
        height = (bottom - top) // self.rows
        
        grids = []
        grid_id = 0
        for row in range(self.rows):
            for col in range(self.cols):
                grid_rect = GridRect(
                    id=grid_id,
                    left=left + col * width,
                    top=top + row * height,
                    right=left + (col + 1) * width,
                    bottom=top + (row + 1) * height
                )
                grids.append(grid_rect)
                grid_id += 1
        return grids
    
    def get_grid_by_id(self, grid_id: int) -> GridRect:
        """根据 ID 获取宫格"""
        if 0 <= grid_id < len(self.grids):
            return self.grids[grid_id]
        raise ValueError(f"Invalid grid_id: {grid_id}")
    
    def get_grid_by_position(self, x: int, y: int) -> GridRect:
        """根据坐标获取宫格"""
        left, top, right, bottom = self.window_rect
        if not (left <= x <= right and top <= y <= bottom):
            raise ValueError(f"Point ({x}, {y}) outside window")
        
        col = (x - left) * self.cols // (right - left)
        row = (y - top) * self.rows // (bottom - top)
        grid_id = row * self.cols + col
        return self.grids[grid_id]
    
    def get_diffusion_order(self, focus_grid_id: int) -> List[int]:
        """
        获取分层扩散扫描顺序
        :param focus_grid_id: 焦点宫格编号 (0-15)
        :return: 扫描顺序列表 [focus, neighbors..., outer...]
        
        分层策略:
        - 第 0 层：焦点宫格
        - 第 1 层：相邻 8 个宫格
        - 第 2 层：外围剩余 7 个宫格
        """
        if not (0 <= focus_grid_id < 16):
            raise ValueError(f"Invalid focus_grid_id: {focus_grid_id}")
        
        row, col = divmod(focus_grid_id, 4)
        layers: List[List[int]] = []
        
        # 第 0 层：焦点
        layers.append([focus_grid_id])
        
        # 第 1 层：相邻 8 格
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 4 and 0 <= nc < 4:
                    neighbors.append(nr * 4 + nc)
        layers.append(neighbors)
        
        # 第 2 层：外围剩余格
        outer = []
        scanned = {focus_grid_id} | set(neighbors)
        for i in range(16):
            if i not in scanned:
                outer.append(i)
        layers.append(outer)
        
        # 扁平化
        return [g for layer in layers for g in layer]
    
    def get_adjacent_grids(self, grid_id: int) -> List[int]:
        """获取相邻宫格 (不包括自己)"""
        row, col = divmod(grid_id, 4)
        adjacent = []
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 4 and 0 <= nc < 4:
                    adjacent.append(nr * 4 + nc)
        return adjacent
    
    def get_all_grids(self) -> List[GridRect]:
        """获取所有宫格"""
        return self.grids.copy()
    
    def get_grid_centers(self) -> List[Tuple[int, int]]:
        """获取所有宫格中心点"""
        return [grid.center for grid in self.grids]
    
    def get_grid_by_position_name(self, position_name: str) -> Optional[GridRect]:
        """
        根据自然语言方位获取宫格
        :param position_name: 方位名称，如 '左上'、'中间'、'右下' 等
        :return: 对应的宫格，如果不存在则返回 None
        
        支持的方位词:
        - 标准：左上、上中、右上、左中、中间、右中、左下、下中、右下
        - 别名：中心、中央、正中 (都映射到中间)
        - 简化：左边、右边、上边、下边
        """
        if not self.use_position_names:
            return None
        
        position_name = position_name.strip()
        
        # 直接匹配
        if position_name in POSITION_NAME_TO_ID:
            grid_id = POSITION_NAME_TO_ID[position_name]
            if grid_id < len(self.grids):
                return self.grids[grid_id]
        
        # 尝试模糊匹配（包含关键词）
        for name, grid_id in POSITION_NAME_TO_ID.items():
            if position_name in name or name in position_name:
                if grid_id < len(self.grids):
                    return self.grids[grid_id]
        
        return None
    
    def get_position_name_by_id(self, grid_id: int) -> Optional[str]:
        """
        根据宫格 ID 获取自然语言方位名称
        :param grid_id: 宫格 ID
        :return: 方位名称，如 '左上'、'中间' 等
        """
        if not self.use_position_names:
            return None
        
        if 0 <= grid_id < len(self.grids):
            row, col = divmod(grid_id, self.cols)
            return POSITION_NAMES_3X3.get((row, col))
        
        return None
    
    def get_grids_by_region_description(self, description: str) -> List[GridRect]:
        """
        根据区域描述获取宫格列表
        :param description: 自然语言描述，如 '上面'、'左侧'、'右下角'
        :return: 匹配的宫格列表
        
        示例:
        - '上面' -> [0, 1, 2] (第一行)
        - '左侧' -> [0, 3, 6] (第一列)
        - '右下角' -> [8]
        - '中间' -> [4]
        """
        if not self.use_position_names:
            return []
        
        desc = description.strip().lower()
        
        # 完整匹配
        if desc in POSITION_NAME_TO_ID:
            grid_id = POSITION_NAME_TO_ID[desc]
            return [self.grids[grid_id]] if grid_id < len(self.grids) else []
        
        # 区域匹配
        result = []
        
        # 上下左右
        if '上' in desc and '左' not in desc and '右' not in desc:
            result = [self.grids[i] for i in [0, 1, 2]]
        elif '下' in desc and '左' not in desc and '右' not in desc:
            result = [self.grids[i] for i in [6, 7, 8]]
        elif '左' in desc and '上' not in desc and '下' not in desc:
            result = [self.grids[i] for i in [0, 3, 6]]
        elif '右' in desc and '上' not in desc and '下' not in desc:
            result = [self.grids[i] for i in [2, 5, 8]]
        
        # 角落
        if '左上' in desc:
            result.append(self.grids[0])
        if '右上' in desc:
            result.append(self.grids[2])
        if '左下' in desc:
            result.append(self.grids[6])
        if '右下' in desc:
            result.append(self.grids[8])
        
        # 中间
        if '中' in desc or '央' in desc:
            if '间' in desc or '心' in desc:
                result.append(self.grids[4])
        
        return result if result else []
