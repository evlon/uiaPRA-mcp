"""
测试语义化过滤 UI 元素
演示如何灵活地使用 LLM 来筛选和排序 UI 元素
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.uia_region_scanner import UIARegionScanner
from core.grid_manager import GridManager
from core.ui_tree_scanner import UITreeScanner
from core.semantic_filter import SemanticFilter, SemanticQuery, SelectorBuilder, quick_filter


def test_semantic_filter():
    """测试语义化过滤器"""
    
    print("=" * 80)
    print("测试语义化过滤器 - 查找微信左边的搜一搜按钮")
    print("=" * 80)
    
    # 1. 设置窗口
    print("\n[步骤 1] 设置焦点窗口为微信...")
    scanner = UIARegionScanner(
        process_name="WeChat.exe",
        window_title=None,
        timeout=5.0
    )
    
    window_rect = scanner.get_window_rect()
    print(f"窗口矩形：{window_rect}")
    
    # 2. 创建宫格管理器（9 宫格）
    print("\n[步骤 2] 创建 9 宫格布局...")
    grid_manager = GridManager(window_rect, rows=3, cols=3)
    
    # 3. 扫描完整 UI 树（不做任何过滤）
    print("\n[步骤 3] 扫描完整 UI 树...")
    ui_scanner = UITreeScanner(scanner.root_element, grid_manager)
    all_elements = ui_scanner.scan_full_tree(max_depth=15)
    print(f"扫描到 {len(all_elements)} 个元素")
    
    # 4. 获取分组数据（让 LLM 决定如何处理）
    print("\n[步骤 4] 获取分组数据...")
    ui_data = ui_scanner.get_grouped_ui_tree()
    print(f"按网格分组的统计信息:")
    for pos_name, count in ui_data['statistics']['by_grid_position'].items():
        print(f"  - {pos_name}: {count} 个元素")
    
    # 5. 【LLM 介入】根据自然语言描述构造查询
    print("\n" + "=" * 80)
    print("[步骤 5] LLM 语义化筛选")
    print("=" * 80)
    
    # 示例 1: 使用 quick_filter 快速过滤
    print("\n[示例 1] 查找左边区域包含'搜'的按钮...")
    left_positions = ['左上', '左中', '左下']
    filtered_results = quick_filter(
        all_elements,
        grid_positions=left_positions,
        name_contains='搜',
        control_types=['ButtonControl'],
        sort_by='name'
    )
    
    print(f"找到 {len(filtered_results)} 个匹配的元素:")
    for i, elem in enumerate(filtered_results[:5]):
        print(f"  {i+1}. [{elem.grid_position}] {elem.name} "
              f"({elem.control_type}) - {elem.bounding_rect}")
    
    # 6. 构建 selector
    if filtered_results:
        print("\n" + "=" * 80)
        print("[步骤 6] 为找到的元素构建 selector")
        print("=" * 80)
        
        target_elem = filtered_results[0]
        
        # 构建简单 selector
        simple_selector = SelectorBuilder.from_element(target_elem)
        print(f"\n简单 Selector:")
        print(f"  {simple_selector}")
        
        # 构建完整 selector（包含窗口）
        window_title = getattr(scanner.root_element, 'Name', '')
        full_selector = SelectorBuilder.from_semantic_match(target_elem, window_title)
        print(f"\n完整 Selector (包含窗口):")
        print(f"  {full_selector}")
        
        # 7. 测试高亮
        print("\n" + "=" * 80)
        print("[步骤 7] 测试高亮显示")
        print("=" * 80)
        
        try:
            from core.screen_highlighter import highlight_element
            print(f"准备高亮元素：{target_elem.name} at {target_elem.bounding_rect}")
            print("高亮将持续 5 秒...")
            
            # 实际高亮需要在有 GUI 环境运行
            # highlight_element(target_elem.element_ref, duration=5.0, color='red')
            print("[OK] 高亮代码已准备好（需要 GUI 环境执行）")
            
        except Exception as e:
            print(f"[提示] 高亮功能：{e}")
    
    # 8. 展示更灵活的用法
    print("\n" + "=" * 80)
    print("[示例 2] 展示更多灵活用法")
    print("=" * 80)
    
    # 用法 A: 先获取某个区域的所有元素，再手动筛选
    print("\n[用法 A] 获取'左中'区域的所有元素，然后手动筛选...")
    left_middle_elems = [
        e for e in all_elements 
        if e.grid_position == '左中'
    ]
    print(f"左中区域有 {len(left_middle_elems)} 个元素")
    
    # LLM 可以在此处添加任意逻辑
    # 例如：找出所有有名字的按钮
    named_buttons = [
        e for e in left_middle_elems 
        if e.name and 'Button' in e.control_type
    ]
    print(f"其中有名字的按钮：{len(named_buttons)} 个")
    
    # 用法 B: 使用正则表达式匹配
    print("\n[用法 B] 使用正则表达式匹配名称...")
    query_with_regex = SemanticQuery(
        grid_positions=['左上', '左中', '左下'],
        name_regex=r'.*搜.*',  # 包含"搜"字
        control_types=['ButtonControl', 'TextControl']
    )
    
    semantic_filter = SemanticFilter(all_elements)
    regex_results = semantic_filter.apply_query(query_with_regex)
    print(f"正则匹配结果：{len(regex_results)} 个元素")
    
    # 用法 C: 自定义过滤函数
    print("\n[用法 C] 使用自定义过滤函数...")
    def custom_size_filter(elem):
        """只保留宽度大于 50 且高度大于 30 的元素"""
        left, top, right, bottom = elem.bounding_rect
        width = right - left
        height = bottom - top
        return width > 50 and height > 30
    
    query_custom = SemanticQuery(
        grid_positions=['左中'],
        custom_filter=custom_size_filter
    )
    
    semantic_filter2 = SemanticFilter(all_elements)
    custom_results = semantic_filter2.apply_query(query_custom)
    print(f"自定义过滤结果：{len(custom_results)} 个元素")
    
    print("\n" + "=" * 80)
    print("[总结]")
    print("=" * 80)
    print("""
新的灵活架构允许 LLM:

1. 获取完整的 UI 树数据（按网格分组）
   → get_ui_tree_data() 返回所有元素和分组信息

2. 根据自然语言描述构造查询条件
   → filter_ui_elements(grid_positions=['左中'], name_contains='搜', ...)

3. 灵活组合多种过滤条件
   - 网格位置：grid_positions=['左上', '左中']
   - 名称匹配：name_contains='搜' 或 name_regex=r'.*搜.*'
   - 控件类型：control_types=['ButtonControl']
   - 尺寸过滤：min_width=50, min_height=30
   - 自定义函数：custom_filter=my_func

4. 为选定元素构建 selector
   → build_selector_for_element(element_index=0)

5. 调用高亮功能验证
   → highlight_element(selector_string=...)

这种设计让 LLM 有足够的灵活性来处理各种复杂的 UI 查找场景！
""")
    
    print("\n[OK] 测试完成！")


if __name__ == '__main__':
    try:
        test_semantic_filter()
    except Exception as e:
        print(f"\n[错误] 测试失败：{e}")
        import traceback
        traceback.print_exc()
