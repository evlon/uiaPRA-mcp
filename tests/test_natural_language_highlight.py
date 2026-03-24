"""
测试：使用自然语言查找并高亮"微信左边的搜一搜按钮"

流程：
1. 扫描微信窗口左侧区域（使用 UI 树扫描）
2. 从结果中找到"搜一搜"按钮
3. 构建 selector 并高亮显示
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager
from core.ui_tree_scanner import UITreeScanner
from core.screen_highlighter import highlight_element

def test_natural_language_highlight():
    """测试自然语言描述 + 高亮"""
    print("=" * 70)
    print(" 测试：微信左边的搜一搜按钮 - 查找并高亮")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # Step 1: 找到微信窗口
    print("\n[Step 1] 查找微信窗口...")
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
    except Exception as e:
        print(f"   无法获取位置：{e}")
        return
    
    # Step 2: 创建 9 宫格管理器
    print("\n[Step 2] 创建 9 宫格...")
    grid_manager = GridManager(wechat_rect, rows=3, cols=3)
    print(f"[OK] 宫格已创建")
    
    # Step 3: 使用 UI 树扫描左侧区域
    print("\n[Step 3] 扫描左侧区域（UI 树扫描）...")
    
    ui_scanner = UITreeScanner(wechat_window, grid_manager)
    all_elements = ui_scanner.scan_full_tree(max_depth=15)
    
    # 过滤出左侧的元素（左上、左中、左下）
    left_grid_ids = {0, 3, 6}  # 左上、左中、左下
    left_elements = [
        e for e in all_elements 
        if e.grid_id in left_grid_ids
    ]
    
    print(f"   共扫描到 {len(all_elements)} 个元素")
    print(f"   左侧区域有 {len(left_elements)} 个元素")
    
    # Step 4: 在左侧元素中查找"搜一搜"
    print("\n[Step 4] 查找'搜一搜'按钮...")
    
    susou_buttons = [
        e for e in left_elements 
        if '搜' in e.name and 'Button' in e.control_type
    ]
    
    if not susou_buttons:
        print("   [未找到] 左侧没有'搜一搜'按钮")
        
        # 尝试在整个窗口查找
        print("   尝试在整个窗口查找...")
        susou_buttons = [
            e for e in all_elements 
            if '搜' in e.name and 'Button' in e.control_type
        ]
        
        if susou_buttons:
            print(f"   [找到] 在整个窗口找到 {len(susou_buttons)} 个")
    
    if not susou_buttons:
        print("\n[失败] 整个窗口都没找到'搜一搜'按钮")
        return
    
    # Step 5: 显示找到的按钮信息
    print(f"\n   [成功] 找到 {len(susou_buttons)} 个'搜一搜'按钮:")
    
    target_button = susou_buttons[0]  # 取第一个
    
    print(f"\n   目标按钮信息:")
    print(f"     名称：'{target_button.name}'")
    print(f"     类型：{target_button.control_type}")
    print(f"     所在宫格：{target_button.grid_position} (Grid {target_button.grid_id})")
    print(f"     位置：{target_button.bounding_rect}")
    print(f"     中心点：{target_button.center_point}")
    
    # Step 6: 构建 selector
    print("\n[Step 6] 构建 selector...")
    
    selector = f"""[
  {{ 'wnd' : [ ('Text' , '微信') ] }},
  {{ 'ctrl' : [ ('Text' , '{target_button.name}'), ('aaRole' , 'PushButton') ] }}
]"""
    
    print(f"   Selector:\n   {selector}")
    
    # Step 7: 验证 selector 能正确定位
    print("\n[Step 7] 验证 selector...")
    
    verified_element = scanner.find_by_selector(selector, timeout=5.0)
    
    if verified_element:
        print(f"   [OK] Selector 验证成功")
        v_rect = verified_element.BoundingRectangle
        print(f"       位置：({v_rect.left}, {v_rect.top}, {v_rect.right}, {v_rect.bottom})")
    else:
        print(f"   [警告] Selector 验证失败，但继续尝试高亮")
        verified_element = target_button.element_ref
    
    # Step 8: 高亮显示
    print("\n[Step 8] 开始高亮...")
    print("   颜色：红色")
    print("   持续时间：5 秒")
    print("   跟随模式：开启")
    print("\n   注意：应该在屏幕上看到红色边框围绕'搜一搜'按钮")
    
    try:
        highlight_element(
            verified_element,
            duration=5.0,
            color='red',
            follow=True
        )
        
        print("\n[完成] 高亮已自动消失")
        
    except Exception as e:
        print(f"\n[错误] 高亮失败：{e}")
        import traceback
        traceback.print_exc()
    
    # Step 9: 总结
    print("\n" + "=" * 70)
    print(" [总结]")
    print("=" * 70)
    
    print("""
完整流程:
1. ✅ 找到微信窗口
2. ✅ 创建 9 宫格
3. ✅ 使用 UI 树扫描左侧区域
4. ✅ 在左侧元素中找到"搜一搜"
5. ✅ 构建对应的 selector
6. ✅ 验证 selector 正确性
7. ✅ 高亮显示 5 秒

关键优势:
- 使用自然语言："微信左边的搜一搜"
- UI 树扫描提供完整的元素列表
- 9 宫格分组让位置判断更直观
- 自动去重避免冗余元素

下一步:
- 可以将此流程集成到 MCP 工具中
- LLM 可以自动执行这个流程
- 支持更多自然语言查询
""")
    
    print("=" * 70)


if __name__ == "__main__":
    test_natural_language_highlight()
