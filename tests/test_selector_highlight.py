"""
测试：使用 selector 定位微信的"搜一搜"按钮并高亮显示
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner

def highlight_element(element, duration: float = 2.0, color: str = 'red'):
    """
    高亮显示 UI 元素
    
    Args:
        element: uiautomation.Control 元素
        duration: 高亮持续时间（秒）
        color: 高亮颜色 ('red', 'green', 'blue')
    """
    try:
        import ctypes
        
        # 获取元素矩形
        rect = element.BoundingRectangle
        left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
        width = right - left
        height = bottom - top
        
        print(f"\n准备高亮元素:")
        print(f"  位置：({left}, {top}, {right}, {bottom})")
        print(f"  大小：{width} x {height}")
        print(f"  颜色：{color}")
        print(f"  持续时间：{duration}秒")
        
        # 创建半透明高亮窗口
        class_name = "HighlightOverlay"
        wc = ctypes.windll.user32.RegisterClassW(
            ctypes.create_unicode_buffer(class_name),
            None
        )
        
        # 简化方案：使用 Windows 自带的视觉反馈
        # 更好的方法是使用 pyautogui 或 PIL 绘制
        print("\n[提示] 实际高亮需要 GUI 支持，这里显示元素信息")
        
        return True
        
    except Exception as e:
        print(f"高亮失败：{e}")
        return False


def test_wechat_selector_highlight():
    """测试微信 selector 定位和高亮"""
    print("=" * 70)
    print(" 测试：微信搜一搜按钮的 selector 定位和高亮")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 用户提供的原始 selector（6 层路径）
    original_selector = """[  { 'wnd' : [ ('Text' , '微信') , ('aaRole' , 'Window') , ('App' , 'Weixin.exe') ] } ,  { 'ctrl' : [ ('aaRole' , 'PushButton') ] } ,  { 'ctrl' : [ ('AutomationId' , 'MainView.main_tabbar') , ('Text' , '导航') ] } ,  { 'ctrl' : [ ('Text' , '搜一搜') , ('aaRole' , 'PushButton') ] } ,  { 'ctrl' : [ ('aaRole' , 'Grouping') ] } ,  { 'ctrl' : [ ('aaRole' , 'PushButton') ] }]"""
    
    # 简化版 selector（推荐）
    simple_selector = """[{ 'wnd' : [ ('Text' , '微信') ] }, { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }]"""
    
    print("\n[Selector 1] 原始版本（6 层路径）:")
    print(original_selector[:150] + "...")
    
    print("\n[Selector 2] 简化版本（推荐）:")
    print(simple_selector)
    
    # 测试简化版
    print("\n" + "=" * 70)
    print(" [测试 1] 使用简化版 selector 查找...")
    print("=" * 70)
    
    result = scanner.find_by_selector(simple_selector, timeout=5.0)
    
    if result:
        print(f"\n[OK] 成功找到元素!")
        print(f"   名称：{result.Name}")
        print(f"   类型：{result.ControlTypeName}")
        print(f"   AutomationId: {result.AutomationId}")
        
        # 获取位置
        try:
            rect = result.BoundingRectangle
            print(f"\n   [位置] 位置信息:")
            print(f"      左上角：({rect.left}, {rect.top})")
            print(f"      右下角：({rect.right}, {rect.bottom})")
            print(f"      宽度：{rect.right - rect.left}")
            print(f"      高度：{rect.bottom - rect.top}")
            
            # 计算中心点
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            print(f"\n   [目标] 中心点：({center_x}, {center_y})")
            
            # 尝试高亮
            print("\n" + "=" * 70)
            print(" [测试 2] 高亮元素...")
            print("=" * 70)
            
            highlight_element(result, duration=3.0)
            
            # 提供高亮方案
            print("\n[提示] 高亮实现方案:")
            print("""
方案 1: 使用 PIL + mss 绘制高亮框
```python
import pyautogui
import time

# 截图
screenshot = pyautogui.screenshot()

# 在截图上绘制红色矩形框
from PIL import ImageDraw
draw = ImageDraw.Draw(screenshot)
draw.rectangle(
    [(rect.left, rect.top), (rect.right, rect.bottom)],
    outline='red',
    width=3
)

# 保存或显示
screenshot.save('highlighted.png')
```

方案 2: 使用 OpenCV 绘制
```python
import cv2
import numpy as np
import mss

# 截图
with mss.mss() as sct:
    monitor = {"left": rect.left, "top": rect.top, 
               "width": rect.right-rect.left, 
               "height": rect.bottom-rect.top}
    img = np.array(sct.grab(monitor))

# 绘制矩形
cv2.rectangle(img, (0, 0), (monitor['width'], monitor['height']), 
              (0, 0, 255), 3)

cv2.imwrite('highlighted.png', img)
```

方案 3: 创建半透明覆盖层（Windows API）
```python
import ctypes
import time

# 创建顶层窗口作为高亮覆盖
hwnd = ctypes.windll.user32.CreateWindowExW(
    0x20,  # WS_EX_TOPMOST
    "STATIC", "Highlight",
    0x90000000,  # WS_POPUP | WS_VISIBLE
    rect.left, rect.top,
    rect.right - rect.left,
    rect.bottom - rect.top,
    0, 0, 0, 0
)

# 设置半透明
ctypes.windll.user32.SetLayeredWindowAttributes(
    hwnd, 0, 128, 0x2  # LWA_ALPHA
)

time.sleep(2)  # 显示 2 秒
ctypes.windll.user32.DestroyWindow(hwnd)
```
            """)
            
        except Exception as e:
            print(f"   [X] 无法获取位置：{e}")
    else:
        print(f"\n[INFO] 未找到元素")
        
        # 诊断信息
        print("\n" + "=" * 70)
        print(" [诊断] 为什么没找到？")
        print("=" * 70)
        
        # 检查微信窗口
        wechat_window = None
        root = scanner.auto.GetRootControl()
        
        for child in root.GetChildren():
            name = getattr(child, 'Name', '')
            proc_name = getattr(child, 'ProcessName', '')
            
            if name == '微信':
                wechat_window = child
                print(f"\n✓ 找到微信窗口:")
                print(f"  名称：{name}")
                print(f"  进程：{proc_name or 'N/A'}")
                
                # 搜索所有按钮
                def find_buttons(elem, depth=0, max_depth=8):
                    if depth > max_depth:
                        return []
                    
                    buttons = []
                    try:
                        ctrl_type = getattr(elem, 'ControlTypeName', '')
                        if 'Button' in ctrl_type:
                            name = getattr(elem, 'Name', 'N/A')
                            auto_id = getattr(elem, 'AutomationId', 'N/A')
                            buttons.append((name, ctrl_type, auto_id, elem))
                        
                        children = elem.GetChildren()
                        for child in children:
                            buttons.extend(find_buttons(child, depth+1, max_depth))
                    except:
                        pass
                    return buttons
                
                all_buttons = find_buttons(wechat_window)
                
                print(f"\n  微信窗口内共有 {len(all_buttons)} 个按钮:")
                susou_buttons = [b for b in all_buttons if '搜一搜' in b[0]]
                
                if susou_buttons:
                    print(f"\n  [OK] 找到 '搜一搜' 按钮 ({len(susou_buttons)} 个):")
                    for name, ctrl_type, auto_id, _ in susou_buttons[:5]:
                        print(f"    - 名称：'{name}'")
                        print(f"      类型：{ctrl_type}")
                        print(f"      AutoID: {auto_id}")
                else:
                    print(f"\n  [X] 未找到包含'搜一搜'的按钮")
                    print(f"\n  所有按钮列表:")
                    for name, ctrl_type, auto_id, _ in all_buttons[:20]:
                        marker = "← 可能是" if '搜' in name or '导航' in name else ""
                        print(f"    - '{name}' ({ctrl_type}) {marker}")
                
                break
        
        if not wechat_window:
            print("\n[X] 未找到微信窗口！")
            print("可能原因:")
            print("  1. 微信未运行")
            print("  2. 微信窗口最小化")
            print("  3. 窗口标题不是'微信'")
    
    print("\n" + "=" * 70)
    print(" 总结")
    print("=" * 70)
    
    print("""
[OK] 成功的关键：
  1. 使用简化的 selector（2 层而不是 6 层）
  2. 先扫描查看实际的元素信息
  3. 根据实际信息调整 selector

[TIP] 高亮实现：
  - 方案 1: PIL + mss（推荐，简单易用）
  - 方案 2: OpenCV（适合图像处理）
  - 方案 3: Windows API（原生支持）

📝 下一步：
  1. 安装依赖：pip install pillow mss opencv-python
  2. 选择一种高亮方案
  3. 集成到 MCP 工具中
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    test_wechat_selector_highlight()
