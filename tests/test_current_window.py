"""
快速测试：查看当前桌面活动窗口
"""
import sys
sys.path.insert(0, '.')

from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager
from core.ui_tree_scanner import UITreeScanner

def check_current_window():
    """检查当前桌面的活动窗口"""
    print("=" * 80)
    print(" 检查当前桌面的活动窗口")
    print("=" * 80)
    
    # 尝试获取当前活动窗口（不指定进程名）
    print("\n[步骤 1] 获取当前活动窗口...")
    try:
        scanner = UIARegionScanner()
        
        # 获取根元素
        root = scanner.auto.GetRootControl()
        print(f"[OK] 获取到 UIA 根元素：{root.ClassName}")
        
        # 获取桌面窗口
        desktop = scanner.auto.GetDesktopControl()
        print(f"[OK] 获取到桌面控件：{desktop.ClassName}")
        
        # 获取所有顶级窗口
        print("\n[步骤 2] 获取所有顶级窗口...")
        children = desktop.GetChildren()
        print(f"找到 {len(children)} 个顶级窗口/控件\n")
        
        # 显示前 20 个窗口
        for i, child in enumerate(children[:20]):
            name = getattr(child, 'Name', '')
            control_type = getattr(child, 'ControlTypeName', '')
            class_name = getattr(child, 'ClassName', '')
            
            if name or control_type:
                print(f"{i+1}. 名称：'{name}'")
                print(f"   类型：{control_type}")
                print(f"   类名：{class_name}")
                
                try:
                    rect = child.BoundingRectangle
                    print(f"   位置：({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
                except:
                    print(f"   位置：无法获取")
                print()
        
        # 尝试获取当前焦点窗口
        print("\n[步骤 3] 尝试获取当前焦点窗口...")
        import ctypes
        user32 = ctypes.windll.user32
        
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            window_title = buff.value
            
            print(f"[OK] 当前焦点窗口句柄：{hwnd}")
            print(f"   窗口标题：{window_title}")
            
            # 尝试在 UIA 树中找到这个窗口
            print(f"\n[步骤 4] 在 UIA 树中查找该窗口...")
            for child in children:
                name = getattr(child, 'Name', '')
                if window_title.lower() in name.lower() or name.lower() in window_title.lower():
                    print(f"[匹配] 找到窗口：{name}")
                    try:
                        rect = child.BoundingRectangle
                        print(f"  位置：{rect.left}, {rect.top}, {rect.right}, {rect.bottom}")
                        
                        # 创建宫格并扫描
                        grid_manager = GridManager(
                            (rect.left, rect.top, rect.right, rect.bottom),
                            rows=3, cols=3
                        )
                        
                        print(f"\n[步骤 5] 扫描窗口 UI 树...")
                        ui_scanner = UITreeScanner(child, grid_manager)
                        elements = ui_scanner.scan_full_tree(max_depth=10)
                        
                        print(f"扫描到 {len(elements)} 个元素")
                        
                        # 显示按网格分组
                        ui_data = ui_scanner.get_grouped_ui_tree()
                        print(f"\n按网格分布:")
                        for pos, count in sorted(ui_data['statistics']['by_grid_position'].items()):
                            print(f"  {pos}: {count} 个元素")
                        
                        # 显示一些示例元素
                        print(f"\n前 10 个元素:")
                        for i, elem in enumerate(elements[:10]):
                            print(f"  {i+1}. [{elem.grid_position}] {elem.name or '(无名称)'} "
                                  f"- {elem.control_type}")
                        
                    except Exception as e:
                        print(f"  [错误] {e}")
                    break
            else:
                print(f"[未找到] 未在 UIA 树中找到匹配的窗口")
        else:
            print("[提示] 无法获取当前焦点窗口")
        
    except Exception as e:
        print(f"[错误] {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    check_current_window()
