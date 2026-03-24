"""
列出所有微信相关的窗口
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner

def list_wechat_windows():
    """列出所有微信窗口"""
    print("=" * 70)
    print(" 列出所有微信相关的窗口")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    root = scanner.auto.GetRootControl()
    
    # 获取所有顶层窗口
    children = root.GetChildren()
    
    wechat_windows = []
    
    for i, child in enumerate(children):
        try:
            proc_name = getattr(child, 'ProcessName', '')
            name = getattr(child, 'Name', '')
            ctrl_type = getattr(child, 'ControlTypeName', '')
            
            # 检查是否是微信相关
            if 'weixin' in (proc_name or '').lower() or 'wechat' in (proc_name or '').lower():
                wechat_windows.append({
                    'index': i,
                    'name': name,
                    'process_name': proc_name,
                    'control_type': ctrl_type,
                    'element': child
                })
                
                print(f"\n[微信窗口 #{len(wechat_windows)}]")
                print(f"  索引：{i}")
                print(f"  名称：'{name}'")
                print(f"  进程：{proc_name}")
                print(f"  类型：{ctrl_type}")
                
                try:
                    rect = child.BoundingRectangle
                    print(f"  位置：({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
                except:
                    pass
                
        except Exception as e:
            pass
    
    if not wechat_windows:
        print("\n未找到任何微信窗口")
        print("请确保微信已运行")
    else:
        print(f"\n共找到 {len(wechat_windows)} 个微信窗口")
        
        # 扫描每个窗口的按钮
        print("\n" + "=" * 70)
        print(" 扫描每个微信窗口的按钮")
        print("=" * 70)
        
        for i, wx_win in enumerate(wechat_windows):
            print(f"\n[窗口 {i+1}] '{wx_win['name']}'")
            
            elem = wx_win['element']
            rect = elem.BoundingRectangle
            
            # 扫描这个窗口
            elements = scanner.scan_grid(
                (rect.left, rect.top, rect.right, rect.bottom),
                search_depth=3
            )
            
            buttons = [e for e in elements if 'Button' in e.control_type]
            
            print(f"  元素总数：{len(elements)}")
            print(f"  按钮数量：{len(buttons)}")
            
            # 查找包含"搜"的元素
            susou_elems = [b for b in buttons if '搜' in (b.name or '')]
            
            if susou_elems:
                print(f"\n  [找到] 包含'搜'的按钮 ({len(susou_elems)} 个):")
                for btn in susou_elems:
                    print(f"    - 名称：'{btn.name}'")
                    print(f"      位置：{btn.bounding_rect}")
            else:
                # 显示前 10 个按钮
                if buttons:
                    print(f"  前 10 个按钮:")
                    for j, btn in enumerate(buttons[:10]):
                        name = btn.name if btn.name else '(无)'
                        print(f"    {j+1}. '{name}' @ {btn.bounding_rect}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    list_wechat_windows()
