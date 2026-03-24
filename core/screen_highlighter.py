"""
屏幕高亮覆盖层 - 使用 tkinter 实现
在屏幕上实时绘制红框，跟随 UI 元素移动
"""
import time
from typing import Optional, Any


class ScreenHighlighter:
    """屏幕高亮覆盖类 - 使用 tkinter"""
    
    def __init__(self):
        self.overlay_window = None
        self.running = False
        self.canvas = None
        
    def create_highlight_overlay(self, rect, color: str = 'red'):
        """
        创建高亮覆盖层（使用 tkinter）
        
        Args:
            rect: (left, top, right, bottom)
            color: 颜色 ('red', 'green', 'blue', 'yellow', 'orange')
        """
        try:
            import tkinter as tk
            
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            margin = 5
            
            # 创建顶层窗口
            self.overlay_window = tk.Tk()
            
            # 移除标题栏，设置为置顶
            self.overlay_window.overrideredirect(True)
            self.overlay_window.attributes('-topmost', True)
            
            # 设置背景透明（白色作为透明色）
            self.overlay_window.attributes('-transparentcolor', 'white')
            
            # 设置窗口位置和大小
            self.overlay_window.geometry(f"{width + margin * 2}x{height + margin * 2}+{left - margin}+{top - margin}")
            
            # 创建画布
            self.canvas = tk.Canvas(
                self.overlay_window,
                width=width + margin * 2,
                height=height + margin * 2,
                bg='white',
                highlightthickness=0
            )
            self.canvas.pack()
            
            # 颜色映射
            outline_color = {
                'red': '#FF0000',
                'green': '#00FF00',
                'blue': '#0000FF',
                'yellow': '#FFFF00',
                'orange': '#FFA500',
            }.get(color.lower(), '#FF0000')
            
            # 绘制粗边框（多层矩形）
            for i in range(3, 0, -1):
                self.canvas.create_rectangle(
                    margin - i, margin - i,
                    width + margin + i, height + margin + i,
                    outline=outline_color,
                    width=i
                )
            
            # 添加文字标签
            self.canvas.create_text(
                margin, margin - 15,
                text="Highlighted",
                fill=outline_color,
                font=('Arial', 10, 'bold'),
                anchor='sw'
            )
            
            self.running = True
            
            # 刷新窗口
            self.overlay_window.update()
            
            return True
            
        except Exception as e:
            print(f"创建高亮层失败：{e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_position(self, rect):
        """
        更新高亮框的位置（跟随元素移动）
        
        Args:
            rect: (left, top, right, bottom)
        """
        if not self.overlay_window or not self.running:
            return
        
        try:
            import tkinter as tk
            
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            margin = 5
            
            # 移动和调整大小
            self.overlay_window.geometry(f"{width + margin * 2}x{height + margin * 2}+{left - margin}+{top - margin}")
            
            # 强制重绘
            self.overlay_window.update_idletasks()
            self.overlay_window.update()
            
        except Exception as e:
            print(f"更新位置失败：{e}")
    
    def hide(self):
        """隐藏高亮框"""
        if self.overlay_window and self.running:
            self.overlay_window.withdraw()
            self.running = False
    
    def show(self):
        """显示高亮框"""
        if self.overlay_window and not self.running:
            self.overlay_window.deiconify()
            self.running = True
    
    def destroy(self):
        """销毁高亮窗口"""
        self.running = False
        
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
            self.overlay_window = None
        self.canvas = None


def highlight_element(element, duration: float = 3.0, 
                     color: str = 'red', follow: bool = True):
    """
    高亮显示 UI 元素
    
    Args:
        element: uiautomation.Control 元素
        duration: 持续时间（秒），0 表示持续直到手动关闭
        color: 颜色 ('red', 'green', 'blue', 'yellow', 'orange')
        follow: 是否跟随元素移动
    
    Returns:
        ScreenHighlighter 实例
    """
    highlighter = ScreenHighlighter()
    
    try:
        rect = element.BoundingRectangle
        rect_tuple = (rect.left, rect.top, rect.right, rect.bottom)
        
        # 创建高亮窗口
        success = highlighter.create_highlight_overlay(rect_tuple, color=color)
        
        if not success:
            raise RuntimeError("Failed to create highlight overlay")
        
        print(f"\n[高亮] 已创建高亮框:")
        print(f"  元素：{getattr(element, 'Name', 'Unknown')}")
        print(f"  位置：{rect_tuple}")
        print(f"  颜色：{color}")
        print(f"  持续时间：{duration}秒")
        print(f"  跟随模式：{follow}")
        
        # 如果需要跟随
        if follow and duration > 0:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    # 重新获取元素位置
                    new_rect = element.BoundingRectangle
                    new_rect_tuple = (new_rect.left, new_rect.top, 
                                     new_rect.right, new_rect.bottom)
                    
                    # 如果位置变化，更新高亮框
                    if new_rect_tuple != rect_tuple:
                        highlighter.update_position(new_rect_tuple)
                        rect_tuple = new_rect_tuple
                    
                    time.sleep(0.1)  # 100ms 更新一次
                    
                    # 处理 GUI 事件
                    if highlighter.overlay_window:
                        highlighter.overlay_window.update_idletasks()
                        
                except Exception as e:
                    print(f"跟随更新失败：{e}")
                    break
        else:
            # 不跟随，只显示固定时间
            if duration > 0:
                time.sleep(duration)
                if highlighter.overlay_window:
                    highlighter.overlay_window.update()
        
        # 自动销毁
        highlighter.destroy()
        
    except Exception as e:
        print(f"[错误] 高亮失败：{e}")
        highlighter.destroy()
        raise
    
    return highlighter


# 简单的测试函数
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加父目录到路径
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.uia_region_scanner import UIARegionScanner
    
    print("=" * 70)
    print(" 屏幕高亮测试")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 查找微信的搜一搜按钮
    selector = """[{ 'wnd' : [ ('Text' , '微信') ] }, { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }]"""
    
    print("\n查找元素...")
    result = scanner.find_by_selector(selector, timeout=5.0)
    
    if result:
        print(f"[OK] 找到：{result.Name}")
        
        print("\n开始高亮（3 秒后自动消失）...")
        print("注意：应该在屏幕上看到一个红色框围绕'搜一搜'按钮")
        highlight_element(result, duration=3.0, color='red', follow=True)
        
        print("\n[完成]")
    else:
        print("[失败] 未找到元素")
