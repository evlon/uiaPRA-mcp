"""
综合示例：16 宫格扫描 UI 元素
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.grid_manager import GridManager
from core.uia_region_scanner import UIARegionScanner
from core.cv_prefilter import CVPreFilter
import time


def demo_grid_scan():
    """演示宫格扫描"""
    print("=" * 70)
    print(" tdRPA-mcp 演示：16 宫格 UI 元素扫描")
    print("=" * 70)

    # 1. 创建扫描器
    print("\n[1/5] 初始化 UIA 扫描器...")
    scanner = UIARegionScanner()
    print(f"[OK] 根元素：{scanner.root_element.Name}")

    # 2. 获取窗口矩形
    print("\n[2/5] 获取窗口区域...")
    window_rect = scanner.get_window_rect()
    print(f"[OK] 窗口矩形：{window_rect}")
    print(f"  宽度：{window_rect[2] - window_rect[0]}")
    print(f"  高度：{window_rect[3] - window_rect[1]}")

    # 3. 创建宫格管理器
    print("\n[3/5] 创建 16 宫格...")
    grid_manager = GridManager(window_rect, rows=4, cols=4)
    print(f"[OK] 宫格数量：{len(grid_manager.get_all_grids())}")

    # 显示宫格布局
    print("\n宫格布局 (4x4):")
    print("┌────┬────┬────┬────┐")
    for row in range(4):
        line = "│"
        for col in range(4):
            grid_id = row * 4 + col
            line += f" {grid_id:2d} │"
        print(line)
        if row < 3:
            print("├────┼────┼────┼────┤")
    print("└────┴────┴────┴────┘")

    # 4. CV 预筛选 (演示)
    print("\n[4/5] CV 预筛选演示...")
    cv = CVPreFilter(threshold=0.01)

    # 使用桌面截图测试 (注意：实际截图可能失败)
    try:
        grids = [grid.to_tuple() for grid in grid_manager.get_all_grids()]

        # 测试前 4 个宫格
        print("\n前 4 个宫格的活跃度:")
        for i in range(4):
            try:
                img = cv.screenshot_grid(grids[i])
                if img.size > 0:
                    score = cv.detect_ui_activity(img)
                    print(
                        f"  Grid {i}: {score:.4f} {'(活跃)' if score > 0.01 else '(低活跃)'}"
                    )
                else:
                    print(f"  Grid {i}: 无法截图")
            except Exception as e:
                print(f"  Grid {i}: 错误 - {e}")
    except Exception as e:
        print(f"CV 预筛选跳过：{e}")

    # 5. 扫描宫格
    print("\n[5/5] 扫描宫格元素...")

    # 演示焦点扩散扫描
    focus_grid = 5  # 中心区域
    print(f"\n设置焦点为 Grid {focus_grid}")

    diffusion_order = grid_manager.get_diffusion_order(focus_grid)
    print(f"扩散顺序：{diffusion_order}")

    # 扫描前 3 个宫格
    print("\n开始扫描...")
    total_elements = 0

    for i, grid_id in enumerate(diffusion_order[:3], 1):
        grid = grid_manager.get_grid_by_id(grid_id)

        start_time = time.time()
        elements = scanner.scan_grid(grid.to_tuple(), search_depth=2)
        elapsed = (time.time() - start_time) * 1000

        total_elements += len(elements)

        print(f"\n  [{i}] Grid {grid_id}:")
        print(f"      矩形：{grid.to_tuple()}")
        print(f"      中心：{grid.center}")
        print(f"      元素数：{len(elements)}")
        print(f"      耗时：{elapsed:.1f}ms")

        # 显示前 3 个元素
        if elements:
            print(f"      元素示例:")
            for j, elem in enumerate(elements[:3], 1):
                print(
                    f"        {j}. {elem.name[:30] if elem.name else 'N/A':30s} ({elem.control_type})"
                )

    # 总结
    print("\n" + "=" * 70)
    print(f"扫描完成!")
    print(f"  扫描宫格数：3")
    print(f"  总元素数：{total_elements}")
    print(f"  平均每宫格：{total_elements / 3:.1f} 个元素")
    print("=" * 70)

    return scanner, grid_manager
    """演示焦点扩散策略"""
    print("\n\n" + "=" * 70)
    print("焦点扩散策略演示")
    print("=" * 70)

    window_rect = (0, 0, 1920, 1080)
    grid_manager = GridManager(window_rect, rows=4, cols=4)

    print("\n不同焦点的扩散顺序:")

    for focus_id in [0, 5, 15]:
        order = grid_manager.get_diffusion_order(focus_id)

        print(f"\n焦点 Grid {focus_id}:")
        print(f"  Layer 0 (焦点): [{order[0]}]")
        print(f"  Layer 1 (相邻): {order[1:9]}")
        print(f"  Layer 2 (外围): {order[9:]}")

    print("\n" + "=" * 70)


def demo_focus_diffusion():
    """演示焦点扩散策略"""
    print("\n\n" + "=" * 70)
    print("焦点扩散策略演示")
    print("=" * 70)

    window_rect = (0, 0, 1920, 1080)
    grid_manager = GridManager(window_rect, rows=4, cols=4)

    print("\n不同焦点的扩散顺序:")

    for focus_id in [0, 5, 15]:
        order = grid_manager.get_diffusion_order(focus_id)

        print(f"\n焦点 Grid {focus_id}:")
        print(f"  Layer 0 (焦点): [{order[0]}]")
        print(f"  Layer 1 (相邻): {order[1:9]}")
        print(f"  Layer 2 (外围): {order[9:]}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        # 运行演示
        scanner, grid_manager = demo_grid_scan()
        demo_focus_diffusion()

        print("\n[OK] 所有演示完成!")
        print("\n提示:")
        print("  - 要扫描特定窗口，使用：UIARegionScanner(process_name='notepad.exe')")
        print("  - 要增加扫描深度，使用：scan_grid(..., search_depth=5)")
        print("  - 要启用并行扫描，参考 focus_diffusion.py 中的 FocusDiffusionScanner")

    except Exception as e:
        print(f"\n[ERROR] 错误：{e}")
        import traceback

        traceback.print_exc()
