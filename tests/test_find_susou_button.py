"""
测试：查找微信的"搜一搜"按钮（图标形式）
带详细日志记录
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager
from core.logger import get_logger, log_function_call, LogContext

# 创建 logger
logger = get_logger('test.find_susou', level='DEBUG', detailed=True)


@log_function_call(logger=logger, log_return=False)
def test_find_susou_button():
    """查找微信的搜一搜按钮"""
    logger.info("=" * 70)
    logger.info(" 测试：查找微信的'搜一搜'按钮（图标形式）")
    logger.info("=" * 70)
    
    print("=" * 70)
    print(" 测试：查找微信的'搜一搜'按钮（图标形式）")
    print("=" * 70)
    
    with LogContext(logger, "初始化扫描器"):
        scanner = UIARegionScanner()
    
    # Step 1: 找到微信窗口
    print("\n[Step 1] 查找微信窗口...")
    logger.info("Step 1: 查找微信窗口")
    
    with LogContext(logger, "查找微信窗口"):
        wechat_window = None
        root = scanner.auto.GetRootControl()
        
        for child in root.GetChildren():
            name = getattr(child, 'Name', '')
            if name == '微信':
                wechat_window = child
                logger.debug(f"找到微信窗口：{name}")
                break
        
        if not wechat_window:
            logger.error("未找到微信窗口")
            print("[失败] 未找到微信窗口")
            return
        
        logger.info(f"✅ 找到微信窗口：{wechat_window.Name}")
    
    try:
        rect = wechat_window.BoundingRectangle
        wechat_rect = (rect.left, rect.top, rect.right, rect.bottom)
        print(f"   位置：{wechat_rect}")
    except Exception as e:
        print(f"   无法获取位置：{e}")
        return
    
    # Step 2: 创建 9 宫格
    print("\n[Step 2] 创建 9 宫格...")
    grid_manager = GridManager(wechat_rect, rows=3, cols=3)
    print(f"[OK] 创建了 {len(grid_manager.grids)} 个宫格")
    
    # Step 3: 扫描左侧区域（通常导航栏在左边）
    print("\n[Step 3] 扫描左侧区域（左中、左上、左下）...")
    
    left_grids = [
        grid_manager.get_grid_by_id(0),  # 左上
        grid_manager.get_grid_by_id(3),  # 左中
        grid_manager.get_grid_by_id(6),  # 左下
    ]
    
    all_buttons = []
    
    for grid in left_grids:
        position_name = grid_manager.get_position_name_by_id(grid.id)
        print(f"\n  扫描 {position_name} (Grid {grid.id})...")
        
        elements = scanner.scan_grid(grid.to_tuple(), search_depth=3)
        
        # 找出所有按钮
        buttons = [e for e in elements if 'Button' in e.control_type]
        
        if buttons:
            print(f"    找到 {len(buttons)} 个按钮:")
            for i, btn in enumerate(buttons[:10]):
                name_text = btn.name if btn.name else '(无文字)'
                auto_id = btn.automation_id if btn.automation_id else '(无 AutoID)'
                
                print(f"      [{i}] 名称：'{name_text}'")
                print(f"          类型：{btn.control_type}")
                print(f"          AutoID: {auto_id}")
                print(f"          位置：{btn.bounding_rect}")
                
                all_buttons.append({
                    'grid': position_name,
                    'element': btn
                })
    
    # Step 4: 分析结果
    print("\n" + "=" * 70)
    print(" [分析] 寻找'搜一搜'按钮")
    print("=" * 70)
    
    # 方法 1: 查找名称包含"搜"的按钮
    susou_by_name = [b for b in all_buttons if '搜' in b['element'].name]
    
    if susou_by_name:
        print(f"\n[方法 1] 通过名称找到 {len(susou_by_name)} 个匹配:")
        for item in susou_by_name:
            btn = item['element']
            print(f"  - 名称：'{btn.name}'")
            print(f"    位置：{item['grid']} 宫格")
            print(f"    坐标：{btn.bounding_rect}")
    else:
        print("\n[方法 1] 未找到名称包含'搜'的按钮")
        print("  说明：这个按钮可能只有图标，没有文字标签")
    
    # 方法 2: 查找可能的图标按钮（无文字但有 AutomationId 或特定位置）
    print("\n[方法 2] 查找图标形式的按钮:")
    
    icon_buttons = [
        b for b in all_buttons 
        if not b['element'].name or b['element'].name.strip() == ''
    ]
    
    if icon_buttons:
        print(f"  找到 {len(icon_buttons)} 个无文字的图标按钮:")
        for i, item in enumerate(icon_buttons[:10]):
            btn = item['element']
            auto_id = btn.automation_id if btn.automation_id else '(无)'
            
            print(f"\n    [{i}] 位置：{item['grid']} 宫格")
            print(f"        坐标：{btn.bounding_rect}")
            print(f"        AutoID: {auto_id}")
            print(f"        ClassName: {btn.class_name}")
            
            # 计算中心点
            rect = btn.bounding_rect
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            print(f"        中心点：({center_x}, {center_y})")
    else:
        print("  未找到无文字的图标按钮")
    
    # 方法 3: 列出所有按钮供人工识别
    print("\n[方法 3] 左侧区域所有按钮列表:")
    for i, item in enumerate(all_buttons):
        btn = item['element']
        name_text = btn.name if btn.name else '(空)'
        print(f"  {i+1}. '{name_text}' @ {item['grid']} - {btn.bounding_rect}")
    
    # Step 5: 尝试使用不同的 selector
    print("\n" + "=" * 70)
    print(" [测试] 使用不同的 selector 策略")
    print("=" * 70)
    
    # 策略 A: 通过 AutomationId 查找
    print("\n策略 A: 查找包含'Search'或'搜'的 AutomationId...")
    for item in all_buttons:
        btn = item['element']
        auto_id = btn.automation_id or ''
        if 'search' in auto_id.lower() or '搜' in auto_id:
            print(f"  [找到] AutoID='{auto_id}', 名称='{btn.name}'")
            print(f"         位置：{item['grid']}")
    
    # 策略 B: 通过 ClassName 查找
    print("\n策略 B: 查找特定 ClassName 的按钮...")
    for item in all_buttons:
        btn = item['element']
        class_name = btn.class_name or ''
        if 'button' in class_name.lower() or 'icon' in class_name.lower():
            print(f"  - ClassName='{class_name}', 名称='{btn.name}'")
    
    # 策略 C: 扫描整个微信窗口
    print("\n策略 C: 扫描整个微信窗口查找'搜一搜'...")
    all_elements = scanner.scan_grid(wechat_rect, search_depth=5)
    
    # 查找名称或 AutoID 包含"搜"的元素
    susou_elements = [
        e for e in all_elements 
        if ('搜' in (e.name or '')) or ('search' in (e.automation_id or '').lower())
    ]
    
    if susou_elements:
        print(f"  [找到] {len(susou_elements)} 个相关元素:")
        for i, elem in enumerate(susou_elements[:5]):
            print(f"    [{i}] 名称：'{elem.name}'")
            print(f"        类型：{elem.control_type}")
            print(f"        AutoID: {elem.automation_id}")
            print(f"        位置：{elem.bounding_rect}")
    else:
        print("  [未找到] 整个窗口都没有名称或 AutoID 包含'搜'的元素")
    
    print("\n" + "=" * 70)
    print(" [结论]")
    print("=" * 70)
    
    if susou_by_name:
        print("""
✅ 找到了有文字标签的"搜一搜"按钮！

可以使用以下 selector:
""")
        btn = susou_by_name[0]['element']
        selector = f"""[
  {{ 'wnd' : [ ('Text' , '微信') ] }},
  {{ 'ctrl' : [ ('Text' , '{btn.name}'), ('aaRole' , 'PushButton') ] }}
]"""
        print(selector)
        
    elif icon_buttons:
        print("""
⚠️ "搜一搜"可能是纯图标按钮（无文字标签）

建议的查找策略:
1. 使用图像识别（OCR 或模板匹配）
2. 根据位置推断（通常在左侧导航栏的特定位置）
3. 使用 Accessibility 工具查看实际的 AutomationId

可能的候选按钮（无文字）:
""")
        for i, item in enumerate(icon_buttons[:5]):
            btn = item['element']
            print(f"  {i+1}. 位置：{btn.bounding_rect}, AutoID: {btn.automation_id}")
    
    else:
        print("""
❌ 未在左侧区域找到明显的"搜一搜"按钮

可能原因:
1. 微信版本不同，界面结构有差异
2. "搜一搜"不在左侧导航栏
3. 需要更深的搜索深度

建议:
- 手动打开微信的"搜一搜"功能
- 使用 Windows 自带的"辅助功能检查器"查看元素信息
- 或者扫描其他区域（上边、中间等）
""")
    
    print("=" * 70)


if __name__ == "__main__":
    test_find_susou_button()
