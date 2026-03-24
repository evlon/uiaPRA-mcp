"""
测试 UI 树扫描器（完整扫描 + 9 宫格排序）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager
from core.ui_tree_scanner import UITreeScanner, scan_ui_tree

def test_ui_tree_scan():
    """测试 UI 树扫描"""
    print("=" * 70)
    print(" UI 树扫描测试（完整扫描 + 9 宫格排序）")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 找到微信窗口
    print("\n查找微信窗口...")
    wechat_window = None
    root = scanner.auto.GetRootControl()
    
    for child in root.GetChildren():
        if getattr(child, 'Name', '') == '微信':
            wechat_window = child
            break
    
    if not wechat_window:
        print("[失败] 未找到微信窗口")
        return
    
    print(f"[OK] 找到微信窗口：{wechat_window.Name}")
    
    try:
        rect = wechat_window.BoundingRectangle
        wechat_rect = (rect.left, rect.top, rect.right, rect.bottom)
        print(f"   位置：{wechat_rect}")
    except Exception as e:
        print(f"   无法获取位置：{e}")
        return
    
    # 创建 9 宫格管理器
    print("\n创建 9 宫格管理器...")
    grid_manager = GridManager(wechat_rect, rows=3, cols=3)
    print(f"[OK] 创建了 {len(grid_manager.grids)} 个宫格")
    
    # 显示 9 宫格布局
    print("\n9 宫格布局:")
    print("┌─────────┬─────────┬─────────┐")
    for row in range(3):
        line = "│"
        for col in range(3):
            grid_id = row * 3 + col
            position_name = grid_manager.get_position_name_by_id(grid_id)
            line += f" {position_name:6s} │"
        print(line)
        if row < 2:
            print("├─────────┼─────────┼─────────┤")
    print("└─────────┴─────────┴─────────┘")
    
    # 扫描 UI 树
    print("\n" + "=" * 70)
    print(" [扫描 UI 树]")
    print("=" * 70)
    
    ui_scanner = UITreeScanner(wechat_window, grid_manager)
    all_elements = ui_scanner.scan_full_tree(max_depth=15)
    
    print(f"\n共扫描到 {len(all_elements)} 个元素")
    
    # 统计信息
    stats = ui_scanner.get_statistics()
    print(f"\n统计信息:")
    print(f"  - 有宫格位置的元素：{stats['elements_with_grid']} 个")
    print(f"  - 无宫格位置的元素：{stats['elements_without_grid']} 个")
    
    print(f"\n按控件类型分布:")
    for ctrl_type, count in sorted(stats['by_control_type'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {ctrl_type:25s}: {count} 个")
    
    print(f"\n按宫格分布:")
    for pos_name, count in sorted(stats['by_grid'].items()):
        print(f"  {pos_name:10s}: {count} 个")
    
    # 按宫格分组查看
    print("\n" + "=" * 70)
    print(" [按宫格分组查看]")
    print("=" * 70)
    
    grid_groups = ui_scanner.get_elements_by_grid()
    
    for grid_id in range(9):
        if grid_id in grid_groups:
            elements = grid_groups[grid_id]
            position_name = grid_manager.get_position_name_by_id(grid_id)
            
            print(f"\n{position_name} (Grid {grid_id}): {len(elements)} 个元素")
            
            # 显示前 5 个元素
            for i, elem in enumerate(elements[:5]):
                name_text = elem.name[:20] if elem.name else '(无)'
                print(f"  [{i+1}] '{name_text}' ({elem.control_type})")
                
                # 如果是按钮且包含"搜"，高亮显示
                if 'Button' in elem.control_type and '搜' in elem.name:
                    print(f"      *** 找到目标！位置：{elem.bounding_rect} ***")
    
    # 去重后的元素列表
    print("\n" + "=" * 70)
    print(" [去重后的元素列表]")
    print("=" * 70)
    
    sorted_elements = ui_scanner.get_sorted_elements(deduplicate=True)
    
    print(f"\n去重后剩余 {len(sorted_elements)} 个元素")
    
    # 查找"搜一搜"按钮
    print("\n查找'搜一搜'按钮...")
    susou_buttons = [
        e for e in sorted_elements 
        if '搜' in e.name and 'Button' in e.control_type
    ]
    
    if susou_buttons:
        print(f"\n[成功] 找到 {len(susou_buttons)} 个'搜一搜'按钮:")
        for btn in susou_buttons:
            print(f"\n  名称：'{btn.name}'")
            print(f"  所在宫格：{btn.grid_position} (Grid {btn.grid_id})")
            print(f"  位置：{btn.bounding_rect}")
            print(f"  中心点：{btn.center_point}")
            print(f"  AutoID: {btn.automation_id}")
            print(f"  ClassName: {btn.class_name}")
    else:
        print("\n[未找到] 没有发现名称包含'搜'的按钮")
        
        # 显示所有按钮
        print("\n所有按钮列表:")
        buttons = [e for e in sorted_elements if 'Button' in e.control_type]
        for i, btn in enumerate(buttons[:20]):
            name_text = btn.name[:20] if btn.name else '(无)'
            pos = btn.grid_position or '未知'
            print(f"  {i+1}. '{name_text}' @ {pos}")
    
    # 对比：使用旧的 scan_grid 方法
    print("\n" + "=" * 70)
    print(" [对比] 传统 scan_grid 方法")
    print("=" * 70)
    
    old_method_elements = scanner.scan_grid(wechat_rect, search_depth=5)
    print(f"\nscan_grid 找到 {len(old_method_elements)} 个元素")
    
    print(f"\n差异分析:")
    print(f"  - UI 树扫描：{len(all_elements)} 个元素（完整树）")
    print(f"  - scan_grid: {len(old_method_elements)} 个元素（区域扫描）")
    print(f"  - 差值：{len(all_elements) - len(old_method_elements)} 个")
    
    print("\n" + "=" * 70)
    print(" [结论]")
    print("=" * 70)
    
    print("""
UI 树扫描的优势:
1. ✅ 获取完整的 UI 层次结构
2. ✅ 可以按宫格分组和排序
3. ✅ 自动去重（移除重叠元素）
4. ✅ 保留父子关系信息
5. ✅ 更适合复杂的界面分析

适用场景:
- 需要理解界面整体结构
- 需要根据位置推断元素
- 需要去重和排序
- 需要分析父子关系

下一步建议:
1. 将 scan_region 改为使用 UI 树扫描
2. 添加更多去重策略（如相似度判断）
3. 支持按宫格顺序返回元素
""")
    
    print("=" * 70)


if __name__ == "__main__":
    test_ui_tree_scan()
