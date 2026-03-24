"""
简单查找微信的搜一搜按钮
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner

def find_susou():
    scanner = UIARegionScanner()
    
    # 找到微信窗口
    root = scanner.auto.GetRootControl()
    wechat_window = None
    
    for child in root.GetChildren():
        if getattr(child, 'Name', '') == '微信':
            wechat_window = child
            break
    
    if not wechat_window:
        print("未找到微信窗口")
        return
    
    print("找到微信窗口，开始扫描...")
    
    # 获取窗口矩形
    rect = wechat_window.BoundingRectangle
    wechat_rect = (rect.left, rect.top, rect.right, rect.bottom)
    
    # 扫描所有元素
    all_elements = scanner.scan_grid(wechat_rect, search_depth=5)
    print(f"共找到 {len(all_elements)} 个元素")
    
    # 找出所有按钮
    buttons = [e for e in all_elements if 'Button' in e.control_type]
    print(f"其中 {len(buttons)} 个是按钮")
    
    # 查找包含"搜"的按钮
    susou_buttons = [b for b in buttons if '搜' in (b.name or '')]
    
    print(f"\n包含'搜'的按钮：{len(susou_buttons)} 个")
    
    if susou_buttons:
        print("\n找到了！")
        for btn in susou_buttons:
            print(f"  名称：{repr(btn.name)}")
            print(f"  位置：{btn.bounding_rect}")
            print(f"  AutoID: {btn.automation_id}")
            print(f"  ClassName: {btn.class_name}")
    else:
        print("\n没找到名称包含'搜'的按钮")
        
        # 显示所有按钮的名称
        print("\n所有按钮列表:")
        for i, btn in enumerate(buttons[:30]):
            name = repr(btn.name) if btn.name else '(无)'
            print(f"  {i+1}. {name:30s} @ {btn.bounding_rect}")


if __name__ == "__main__":
    find_susou()
