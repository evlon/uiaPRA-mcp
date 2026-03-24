"""
MCP 工具测试：语义化查找 UI 元素
演示 LLM 如何通过 MCP 工具灵活地查找和定位 UI 元素
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_mcp_semantic_search():
    """
    测试通过 MCP 工具进行语义化搜索
    
    场景：查找"微信左边的搜一搜按钮"
    
    步骤：
    1. set_focus_window - 设置微信为焦点窗口
    2. get_ui_tree_data - 获取完整的 UI 树数据
    3. filter_ui_elements - 根据语义条件过滤
    4. build_selector_for_element - 为目标元素构建 selector
    5. highlight_element - 高亮显示验证
    """
    
    print("=" * 80)
    print("MCP 工具测试：语义化查找 UI 元素")
    print("=" * 80)
    
    # 模拟 MCP 工具调用（实际使用时通过 MCP 客户端调用）
    from tools.grid_picker import register_grid_picker
    from mcp.server.fastmcp import FastMCP
    
    # 创建 MCPP 实例
    mcp = FastMCP("test")
    
    # 用于存储 scanner 引用
    scanner_ref = {}
    
    # 注册工具
    register_grid_picker(mcp, scanner_ref)
    
    # 获取工具函数
    set_focus_window = None
    get_ui_tree_data = None
    filter_ui_elements = None
    build_selector_for_element = None
    highlight_element = None
    
    # 从 mcp.tools 中获取工具
    for tool in mcp._tool_handlers.values():
        if tool.name == 'set_focus_window':
            set_focus_window = tool.fn
        elif tool.name == 'get_ui_tree_data':
            get_ui_tree_data = tool.fn
        elif tool.name == 'filter_ui_elements':
            filter_ui_elements = tool.fn
        elif tool.name == 'build_selector_for_element':
            build_selector_for_element = tool.fn
        elif tool.name == 'highlight_element':
            highlight_element = tool.fn
    
    try:
        # ========== 步骤 1: 设置焦点窗口 ==========
        print("\n[步骤 1] 设置微信为焦点窗口...")
        result = await set_focus_window(process_name="WeChat.exe")
        
        if result.get('success'):
            print(f"[OK] 窗口设置成功:")
            print(f"  标题：{result['window']['title']}")
            print(f"  矩形：{result['window']['rect']}")
            print(f"  网格：{result['grid_info']['total_grids']} 个 ({result['grid_info']['rows']}x{result['grid_info']['cols']})")
        else:
            print(f"[错误] {result.get('error')}")
            return
        
        # ========== 步骤 2: 获取 UI 树数据 ==========
        print("\n[步骤 2] 获取完整的 UI 树数据...")
        ui_tree_result = await get_ui_tree_data(max_depth=15, include_raw_elements=False)
        
        if ui_tree_result.get('success'):
            ui_data = ui_tree_result['ui_tree']
            print(f"[OK] 扫描到 {ui_data['statistics']['total_elements']} 个元素")
            print(f"     有网格位置的：{ui_data['statistics']['elements_with_grid']} 个")
            
            print("\n按网格分布:")
            for pos, count in sorted(ui_data['statistics']['by_grid_position'].items()):
                print(f"  - {pos}: {count} 个")
            
            print("\n按控件类型分布:")
            for ctrl_type, count in sorted(ui_data['statistics']['by_control_type'].items())[:5]:
                print(f"  - {ctrl_type}: {count} 个")
        else:
            print(f"[错误] {ui_tree_result.get('error')}")
            return
        
        # ========== 步骤 3: LLM 语义化推理并过滤 ==========
        print("\n" + "=" * 80)
        print("[步骤 3] LLM 语义化推理")
        print("=" * 80)
        print("""
LLM 思考过程:
用户说："微信左边的搜一搜按钮"

1. 分析关键词:
   - "微信" → 窗口已设置
   - "左边" → 网格位置应该是 ['左上', '左中', '左下']
   - "搜一搜" → 名称包含"搜"
   - "按钮" → 控件类型是 ButtonControl

2. 构造过滤条件:
   - grid_positions: ['左上', '左中', '左下']
   - name_contains: '搜'
   - control_types: ['ButtonControl']
""")
        
        filter_result = await filter_ui_elements(
            grid_positions=['左上', '左中', '左下'],
            name_contains='搜',
            control_types=['ButtonControl'],
            sort_by='name'
        )
        
        if filter_result.get('success'):
            print(f"\n[OK] 过滤结果:")
            print(f"  找到 {filter_result['result_count']} 个匹配的元素")
            
            if filter_result['elements']:
                print("\n前 5 个结果:")
                for i, elem in enumerate(filter_result['elements'][:5]):
                    print(f"  {i+1}. [{elem['grid_position']}] {elem['name']}")
                    print(f"      类型：{elem['control_type']}")
                    print(f"      位置：{elem['bounding_rect']}")
        else:
            print(f"[错误] {filter_result.get('error')}")
            return
        
        # ========== 步骤 4: 构建 selector ==========
        if filter_result['elements']:
            print("\n" + "=" * 80)
            print("[步骤 4] 为第 1 个元素构建 selector")
            print("=" * 80)
            
            selector_result = await build_selector_for_element(
                element_index=0,
                grid_position=filter_result['elements'][0]['grid_position'],
                element_name=filter_result['elements'][0]['name']
            )
            
            if selector_result.get('success'):
                elem_info = selector_result['element']
                selector_info = selector_result['selector']
                
                print(f"[OK] 元素信息:")
                print(f"  名称：{elem_info['name']}")
                print(f"  类型：{elem_info['control_type']}")
                print(f"  位置：{elem_info['grid_position']}")
                print(f"  矩形：{elem_info['bounding_rect']}")
                
                print(f"\n[OK] Selector:")
                print(f"  简单版：{selector_info['simple']}")
                print(f"  完整版：{selector_info['full_with_window']}")
                
                # ========== 步骤 5: 高亮验证 ==========
                print("\n" + "=" * 80)
                print("[步骤 5] 高亮显示验证")
                print("=" * 80)
                
                highlight_result = await highlight_element(
                    selector_string=selector_info['full_with_window'],
                    duration=5.0,
                    color='red'
                )
                
                if highlight_result.get('success'):
                    hl_elem = highlight_result['element']
                    hl_info = highlight_result['highlight_info']
                    print(f"[OK] 高亮成功!")
                    print(f"  元素：{hl_elem['name']}")
                    print(f"  位置：{hl_elem['bounding_rect']}")
                    print(f"  颜色：{hl_info['color']}")
                    print(f"  持续时间：{hl_info['duration']}秒")
                    print(f"  跟随模式：{hl_info['follow_mode']}")
                else:
                    print(f"[提示] 高亮失败：{highlight_result.get('error')}")
            else:
                print(f"[错误] {selector_result.get('error')}")
    
    except Exception as e:
        print(f"\n[错误] 测试异常：{e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("[测试完成]")
    print("=" * 80)
    print("""
总结新的灵活工作流程:

1. get_ui_tree_data() 
   → 获取完整 UI 树，按网格分组，不做任何过滤
   
2. LLM 分析自然语言描述
   → 解析出 grid_positions, name_contains, control_types 等条件
   
3. filter_ui_elements(...)
   → 应用 LLM 构造的过滤条件
   
4. build_selector_for_element(...)
   → 为选中的元素生成 tdSelector
   
5. highlight_element(...)
   → 高亮显示验证结果

这种设计让 LLM 有足够的灵活性处理各种复杂的 UI 查找场景！
""")


if __name__ == '__main__':
    asyncio.run(test_mcp_semantic_search())
