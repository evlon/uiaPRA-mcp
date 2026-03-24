"""
CV 预筛选模块
使用 OpenCV 快速识别 UI 活跃区域
"""
import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class CVPreFilter:
    """CV 预筛选器"""
    
    def __init__(self, threshold: float = 0.01):
        """
        :param threshold: 活跃度阈值，小于此值的区域将被跳过
        """
        try:
            import cv2
            self.cv2 = cv2
        except ImportError:
            raise ImportError("Please install opencv-python: pip install opencv-python")
        
        self.threshold = threshold
    
    def screenshot_grid(self, grid_rect: Tuple[int, int, int, int], 
                       capture_cursor: bool = False) -> np.ndarray:
        """
        快速截取宫格区域
        :param grid_rect: (left, top, right, bottom)
        :param capture_cursor: 是否包含光标
        :return: RGB numpy array
        """
        try:
            import pyautogui
        except ImportError:
            raise ImportError("Please install pyautogui")
        
        left, top, right, bottom = grid_rect
        width = right - left
        height = bottom - top
        
        if width <= 0 or height <= 0:
            logger.warning(f"Invalid grid_rect: {grid_rect}")
            return np.array([])
        
        screenshot = pyautogui.screenshot(
            region=(left, top, width, height)
        )
        
        if capture_cursor:
            # TODO: 叠加光标图像
            pass
        
        return np.array(screenshot)
    
    def detect_ui_activity(self, image: np.ndarray) -> float:
        """
        检测 UI 活跃度 (基于边缘检测)
        :param image: RGB numpy array
        :return: 活跃度分数 0-1
        """
        if image.size == 0:
            return 0.0
        
        try:
            # 转灰度图
            if len(image.shape) == 3:
                gray = self.cv2.cvtColor(image, self.cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Canny 边缘检测
            edges = self.cv2.Canny(gray, 50, 150)
            
            # 计算边缘密度
            edge_pixels = np.count_nonzero(edges)
            total_pixels = edges.size
            activity_score = edge_pixels / total_pixels if total_pixels > 0 else 0.0
            
            return activity_score
        except Exception as e:
            logger.error(f"Error detecting UI activity: {e}")
            return 0.0
    
    def detect_ui_contours(self, image: np.ndarray) -> int:
        """
        检测 UI 轮廓数量
        :param image: RGB numpy array
        :return: 轮廓数量
        """
        if image.size == 0:
            return 0
        
        try:
            # 转灰度图
            if len(image.shape) == 3:
                gray = self.cv2.cvtColor(image, self.cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # 二值化
            _, thresh = self.cv2.threshold(gray, 128, 255, self.cv2.THRESH_BINARY_INV)
            
            # 查找轮廓
            contours, _ = self.cv2.findContours(
                thresh, 
                self.cv2.RETR_EXTERNAL,
                self.cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 过滤小轮廓
            min_area = 100
            valid_contours = [c for c in contours 
                            if self.cv2.contourArea(c) > min_area]
            
            return len(valid_contours)
        except Exception as e:
            logger.error(f"Error detecting contours: {e}")
            return 0
    
    def rank_grids_by_activity(self, grids: List[Tuple[int, int, int, int]]
                              ) -> List[Tuple[int, float]]:
        """
        按 UI 活跃度对宫格排序
        :param grids: 宫格矩形列表 [(left, top, right, bottom), ...]
        :return: 按活跃度降序排列的 (grid_index, score) 列表
        """
        scores: List[Tuple[int, float]] = []
        
        for i, grid_rect in enumerate(grids):
            try:
                img = self.screenshot_grid(grid_rect)
                if img.size == 0:
                    scores.append((i, 0.0))
                    continue
                
                score = self.detect_ui_activity(img)
                scores.append((i, score))
            except Exception as e:
                logger.error(f"Error processing grid {i}: {e}")
                scores.append((i, 0.0))
        
        # 按活跃度降序排序
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    
    def filter_active_grids(self, grids: List[Tuple[int, int, int, int]], 
                           threshold: float = None) -> List[int]:
        """
        筛选活跃宫格
        :param grids: 宫格矩形列表
        :param threshold: 活跃度阈值 (使用实例的 threshold 如果为 None)
        :return: 活跃宫格索引列表
        """
        if threshold is None:
            threshold = self.threshold
        
        ranked = self.rank_grids_by_activity(grids)
        active = [idx for idx, score in ranked if score >= threshold]
        
        logger.info(f"Found {len(active)} active grids out of {len(grids)}")
        return active
    
    def get_grid_heatmap(self, grids: List[Tuple[int, int, int, int]]
                        ) -> Dict[int, float]:
        """
        获取宫格热力图
        :param grids: 宫格矩形列表
        :return: {grid_index: activity_score}
        """
        ranked = self.rank_grids_by_activity(grids)
        return {idx: score for idx, score in ranked}
