"""
测试实时跟随高亮功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.screen_highlighter import highlight_element, ScreenHighlighter
from core.uia_region_scanner import UIARegionScanner

def test_live_highlight():
    """测试实时高亮"""
    print("=" * 70)
    print(" 实时跟随高亮测试")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 查找微信的搜一搜按钮
    selector = """[{ 'wnd' : [ ('Text' , '微信') ] }, { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }]"""
    
    print("\n[步骤 1] 查找元素...")
    result = scanner.find_by_selector(selector, timeout=5.0)
    
    if not result:
        print("[失败] 未找到元素")
        return
    
    print(f"[OK] 找到：{result.Name}")
    print(f"   类型：{result.ControlTypeName}")
    
    try:
        rect = result.BoundingRectangle
        print(f"   位置：({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
    except Exception as e:
        print(f"   无法获取位置：{e}")
        return
    
    print("\n[步骤 2] 创建实时高亮框...")
    print("   颜色：红色")
    print("   持续时间：5 秒")
    print("   跟随模式：开启")
    print("\n注意：应该在屏幕上看到一个红色的框围绕'搜一搜'按钮")
    
    # 高亮
    highlighter = highlight_element(
        result,
        duration=5.0,
        color='red',
        follow=True  # 开启跟随
    )
    
    print("\n[完成] 高亮已自动消失")
    print("\n提示：如果要手动控制，使用:")
    print("""
highlighter = ScreenHighlighter()
highlighter.create_highlight_window(rect)
time.sleep(2)
highlighter.update_position(new_rect)  # 移动到新位置
highlighter.destroy()  # 手动销毁
    """)


if __name__ == "__main__":
    test_live_highlight()
