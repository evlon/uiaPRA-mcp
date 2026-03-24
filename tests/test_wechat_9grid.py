"""
测试：微信窗口的 9 宫格划分
验证"微信左边的搜一搜按钮"这个逻辑
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager

def test_wechat_9grid():
    """测试微信窗口的 9 宫格"""
    print("=" * 70)
    print(" 测试：微信窗口的 9 宫格划分")
    print("=" * 70)
    
    # Step 1: 找到微信窗口
    print("\n[Step 1] 查找微信窗口...")
    scanner = UIARegionScanner()
    
    wechat_window = None
    root = scanner.auto.GetRootControl()
    
    for child in root.GetChildren():
        name = getattr(child, 'Name', '')
        if name == '微信':
            wechat_window = child
            break
    
    if not wechat_window:
        print("[ERROR] 未找到微信窗口")
        return
    
    print(f"[OK] 找到微信窗口：{wechat_window.Name}")
    
    try:
        rect = wechat_window.BoundingRectangle
        wechat_rect = (rect.left, rect.top, rect.right, rect.bottom)
        print(f"   位置：{wechat_rect}")
        print(f"   大小：{rect.right - rect.left} x {rect.bottom - rect.top}")
    except Exception as e:
        print(f"[ERROR] 无法获取窗口矩形：{e}")
        return
    
    # Step 2: 为微信窗口创建 9 宫格
    print("\n[Step 2] 将微信窗口分成 9 份...")
    grid_manager = GridManager(wechat_rect, rows=3, cols=3)
    print(f"[OK] 创建了 {len(grid_manager.grids)} 个宫格")
    
    # 显示 9 宫格布局（相对于微信窗口）
    print("\n微信窗口的 9 宫格:")
    print("┌─────────────┬─────────────┬─────────────┐")
    for row in range(3):
        line = "│"
        for col in range(3):
            grid_id = row * 3 + col
            position_name = grid_manager.get_position_name_by_id(grid_id)
            line += f" {position_name:6s} │"
        print(line)
        if row < 2:
            print("├─────────────┼─────────────┼─────────────┤")
    print("└─────────────┴─────────────┴─────────────┘")
    
    # 显示每个宫格的绝对坐标和相对位置
    print("\n每个宫格的详细信息:")
    for grid in grid_manager.grids:
        position_name = grid_manager.get_position_name_by_id(grid.id)
        
        # 计算相对于微信窗口的位置
        rel_left = grid.left - wechat_rect[0]
        rel_top = grid.top - wechat_rect[1]
        
        print(f"\n  {position_name} (Grid {grid.id}):")
        print(f"    绝对坐标：{grid.to_tuple()}")
        print(f"    相对微信窗口：({rel_left}, {rel_top}) 偏移")
        print(f"    大小：{grid.width} x {grid.height}")
    
    # Step 3: 理解"左边"的含义
    print("\n" + "=" * 70)
    print(" [Step 3] 理解'微信左边的搜一搜按钮'")
    print("=" * 70)
    
    print("\n用户说'微信左边'，指的是:")
    print("  - 在微信窗口内部的左侧区域")
    print("  - 不是整个屏幕的左侧！")
    
    # 获取"左边"的宫格
    left_grids = grid_manager.get_grids_by_region_description("左侧")
    
    print(f"\n'左侧' 包含 {len(left_grids)} 个宫格:")
    for grid in left_grids:
        position_name = grid_manager.get_position_name_by_id(grid.id)
        print(f"  - {position_name} (Grid {grid.id})")
    
    # Step 4: 在这些宫格中查找"搜一搜"
    print("\n[Step 4] 在左侧宫格中查找'搜一搜'按钮...")
    
    found_button = None
    for grid in left_grids:
        elements = scanner.scan_grid(grid.to_tuple(), search_depth=3)
        
        for elem in elements:
            if '搜一搜' in elem.name:
                found_button = elem
                found_grid = grid
                break
        
        if found_button:
            break
    
    if found_button:
        print(f"[OK] 找到了！")
        print(f"   按钮名称：{found_button.name}")
        print(f"   控件类型：{found_button.control_type}")
        print(f"   所在宫格：{grid_manager.get_position_name_by_id(found_grid.id)}")
        print(f"   宫格编号：Grid {found_grid.id}")
        
        try:
            rect = found_button.bounding_rect
            print(f"   位置：{rect}")
            
            # 计算中心点
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            print(f"   中心点：({center_x}, {center_y})")
        except:
            pass
    else:
        print(f"[INFO] 在左侧未找到'搜一搜'按钮")
        
        # 扩大搜索范围到所有宫格
        print("\n尝试在所有宫格中搜索...")
        all_elements = scanner.scan_grid(wechat_rect, search_depth=5)
        
        susou_elems = [e for e in all_elements if '搜一搜' in e.name]
        
        if susou_elems:
            print(f"找到 {len(susou_elems)} 个包含'搜一搜'的元素:")
            for elem in susou_elems[:3]:
                # 找出在哪个宫格
                for grid in grid_manager.grids:
                    try:
                        rect = elem.bounding_rect
                        center_x = (rect[0] + rect[2]) // 2
                        center_y = (rect[1] + rect[3]) // 2
                        
                        containing_grid = grid_manager.get_grid_by_position(center_x, center_y)
                        if containing_grid.id == grid.id:
                            pos_name = grid_manager.get_position_name_by_id(grid.id)
                            print(f"  - '{elem.name}' 在 {pos_name} (Grid {grid.id})")
                            break
                    except:
                        pass
        else:
            print("整个微信窗口都没找到'搜一搜'")
    
    print("\n" + "=" * 70)
    print(" 结论")
    print("=" * 70)
    print("""
当用户说"微信左边的搜一搜按钮"时：

1. 首先定位到"微信窗口"
2. 把微信窗口分成 9 宫格
3. "左边" = 左上 + 左中 + 左下 (3 个宫格)
4. 在这 3 个宫格内查找"搜一搜"按钮

关键：9 宫格是针对目标窗口（微信），不是整个屏幕！
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    test_wechat_9grid()
