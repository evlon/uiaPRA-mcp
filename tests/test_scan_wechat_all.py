"""
扫描微信窗口的所有元素
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner

def scan_wechat_all():
    """扫描微信窗口所有元素"""
    print("=" * 70)
    print(" 扫描微信窗口的所有元素")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 找到微信窗口
    print("\n查找微信窗口...")
    wechat_window = None
    root = scanner.auto.GetRootControl()
    
    for child in root.GetChildren():
        name = getattr(child, 'Name', '')
        if name == '微信':
            wechat_window = child
            break
    
    if not wechat_window:
        print("[失败] 未找到微信窗口")
        return
    
    print(f"[OK] 找到微信窗口")
    
    try:
        rect = wechat_window.BoundingRectangle
        wechat_rect = (rect.left, rect.top, rect.right, rect.bottom)
        print(f"   位置：{wechat_rect}")
        print(f"   大小：{rect.right - rect.left} x {rect.bottom - rect.top}")
    except Exception as e:
        print(f"   无法获取位置：{e}")
        return
    
    # 扫描整个窗口
    print("\n扫描整个微信窗口（深度=5）...")
    all_elements = scanner.scan_grid(wechat_rect, search_depth=5)
    
    print(f"\n共找到 {len(all_elements)} 个元素")
    
    # 分类统计
    print("\n" + "=" * 70)
    print(" [元素分类]")
    print("=" * 70)
    
    by_type = {}
    for elem in all_elements:
        ctrl_type = elem.control_type
        if ctrl_type not in by_type:
            by_type[ctrl_type] = []
        by_type[ctrl_type].append(elem)
    
    print(f"\n按控件类型分类:")
    for ctrl_type, elements in sorted(by_type.items()):
        print(f"  {ctrl_type}: {len(elements)} 个")
    
    # 找出所有按钮
    print("\n" + "=" * 70)
    print(" [所有按钮]")
    print("=" * 70)
    
    buttons = by_type.get('ButtonControl', [])
    
    if buttons:
        print(f"\n找到 {len(buttons)} 个按钮:")
        
        for i, btn in enumerate(buttons):
            name_text = btn.name if btn.name else '(无文字)'
            auto_id = btn.automation_id if btn.automation_id else '(无 AutoID)'
            
            print(f"\n  [{i+1}] 名称：'{name_text}'")
            print(f"      类型：{btn.control_type}")
            print(f"      AutoID: {auto_id}")
            print(f"      ClassName: {btn.class_name}")
            print(f"      位置：{btn.bounding_rect}")
            
            # 检查是否包含"搜"
            if '搜' in (btn.name or '') or 'search' in (btn.automation_id or '').lower():
                print(f"      *** 可能是目标！***")
    else:
        print("\n[未找到] 没有任何 ButtonControl 类型的元素")
    
    # 查找包含"搜"的所有元素（不限类型）
    print("\n" + "=" * 70)
    print(" [查找包含'搜'的元素]")
    print("=" * 70)
    
    susou_elements = [
        e for e in all_elements 
        if '搜' in (e.name or '') or 'search' in (e.automation_id or '').lower()
    ]
    
    if susou_elements:
        print(f"\n找到 {len(susou_elements)} 个相关元素:")
        for i, elem in enumerate(susou_elements):
            print(f"\n  [{i+1}] 名称：'{elem.name}'")
            print(f"      类型：{elem.control_type}")
            print(f"      AutoID: {elem.automation_id}")
            print(f"      位置：{elem.bounding_rect}")
    else:
        print("\n[未找到] 没有任何元素的名称或 AutoID 包含'搜'")
    
    # 显示前 50 个元素供参考
    print("\n" + "=" * 70)
    print(" [元素列表 Top 50]")
    print("=" * 70)
    
    print(f"\n前 50 个元素:")
    for i, elem in enumerate(all_elements[:50]):
        name_text = elem.name[:20] if elem.name else '(空)'
        print(f"  {i+1}. [{elem.control_type:20s}] '{name_text}'")
    
    print("\n" + "=" * 70)
    print(" [结论和建议]")
    print("=" * 70)
    
    if not buttons:
        print("""
微信界面可能使用了非标准的控件类型。

建议:
1. 检查是否有 PaneControl 或 GroupControl 充当按钮
2. 使用图像识别代替 UIA
3. 或者尝试点击特定坐标

可能的替代方案:
- 直接点击坐标 (例如左侧导航栏的固定位置)
- 使用 OCR 识别图标旁边的文字
- 使用模板匹配
""")
    
    print("=" * 70)


if __name__ == "__main__":
    scan_wechat_all()
