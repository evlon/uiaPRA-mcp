"""
验证之前找到的"搜一搜"按钮的详细信息
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner

def verify_susou():
    """验证搜一搜按钮"""
    print("=" * 70)
    print(" 验证'搜一搜'按钮的详细信息")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 使用之前的 selector
    selector = """[{ 'wnd' : [ ('Text' , '微信') ] }, { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }]"""
    
    print("\n使用 selector:")
    print(selector)
    
    print("\n查找元素...")
    result = scanner.find_by_selector(selector, timeout=5.0)
    
    if result:
        print(f"\n[OK] 成功找到元素!")
        print(f"\n详细属性:")
        
        # 获取所有可用属性
        attrs_to_check = [
            'Name', 'ControlTypeName', 'AutomationId', 'ClassName',
            'ProcessName', 'Handle', 'NativeWindowHandle',
            'IsEnabled', 'IsVisible', 'IsKeyboardFocusable',
            'HelpText', 'AcceleratorKey', 'HasKeyboardFocus',
            'IsContentElement', 'IsControlElement',
        ]
        
        for attr in attrs_to_check:
            try:
                value = getattr(result, attr, None)
                print(f"  {attr:30s}: {repr(value)}")
            except Exception as e:
                print(f"  {attr:30s}: <无法获取：{e}>")
        
        # 获取位置
        try:
            rect = result.BoundingRectangle
            print(f"\n位置信息:")
            print(f"  左上角：({rect.left}, {rect.top})")
            print(f"  右下角：({rect.right}, {rect.bottom})")
            print(f"  宽度：{rect.right - rect.left}")
            print(f"  高度：{rect.bottom - rect.top}")
            print(f"  中心点：({(rect.left + rect.right) // 2}, {(rect.top + rect.bottom) // 2})")
        except Exception as e:
            print(f"\n无法获取位置：{e}")
        
        # 获取父元素
        print(f"\n父元素信息:")
        try:
            parent = result.GetParent()
            if parent:
                print(f"  名称：{getattr(parent, 'Name', 'N/A')}")
                print(f"  类型：{getattr(parent, 'ControlTypeName', 'N/A')}")
                print(f"  AutoID: {getattr(parent, 'AutomationId', 'N/A')}")
        except Exception as e:
            print(f"  无法获取：{e}")
        
        # 获取子元素
        print(f"\n子元素:")
        try:
            children = result.GetChildren()
            if children:
                print(f"  共 {len(children)} 个子元素:")
                for i, child in enumerate(children[:5]):
                    print(f"    [{i}] 名称：{getattr(child, 'Name', 'N/A')}")
                    print(f"        类型：{getattr(child, 'ControlTypeName', 'N/A')}")
            else:
                print("  (无子元素)")
        except Exception as e:
            print(f"  无法获取：{e}")
        
        print("\n" + "=" * 70)
        print(" [结论]")
        print("=" * 70)
        
        name = getattr(result, 'Name', '')
        auto_id = getattr(result, 'AutomationId', '')
        
        if name == '搜一搜':
            print("""
✅ 确认找到了真正的"搜一搜"按钮！

特征:
- Name 属性 = "搜一搜"
- ControlType = ButtonControl
- 有明确的边界矩形

可以使用的 selector:
""")
            print(selector)
            
        elif not name or name.strip() == '':
            print("""
⚠️ 注意：找到的元素 Name 为空

这可能是一个纯图标按钮，"搜一搜"只是 tooltip 或辅助文字。

如果是这种情况：
1. 需要检查其他属性（如 AutomationId）
2. 或者使用图像识别
3. 或者根据位置推断（通常在左侧导航栏固定位置）
""")
        else:
            print(f"""
⚠️ 找到的元素名称是 '{name}' 而不是 '搜一搜'

可能是:
1. 匹配了错误的元素
2. 微信版本不同，名称有差异
3. 需要更精确的 selector

建议调整 selector 条件。
""")
            
    else:
        print("\n[失败] 未找到元素")
        print("\n可能原因:")
        print("  1. 微信未运行")
        print("  2. 当前微信界面没有'搜一搜'按钮")
        print("  3. '搜一搜'按钮的 Name 属性不是'搜一搜'（可能是空或其他文字）")
        print("  4. 窗口标题不是'微信'")
        
        print("\n建议:")
        print("  1. 确认微信已打开并且显示主界面（不是聊天窗口）")
        print("  2. 使用 Windows 辅助功能检查器查看实际的元素属性")
        print("  3. 尝试扫描整个桌面查找包含'搜'的元素")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    verify_susou()
