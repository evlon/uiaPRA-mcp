"""
实际高亮 UI 元素 - 使用 PIL + mss
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.uia_region_scanner import UIARegionScanner

def highlight_with_pil(rect, output_file='highlighted.png'):
    """
    使用 PIL + mss 截图并绘制高亮框
    
    Args:
        rect: (left, top, right, bottom)
        output_file: 输出文件名
    """
    try:
        from PIL import ImageDraw, ImageFont
        import mss
        import mss.tools
        
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        
        print(f"\n正在截图并高亮...")
        print(f"  区域：({left}, {top}, {right}, {bottom})")
        print(f"  大小：{width} x {height}")
        
        # 截图（稍微大一点，包含上下文）
        margin = 20
        monitor = {
            "left": max(0, left - margin),
            "top": max(0, top - margin),
            "width": width + margin * 2,
            "height": height + margin * 2
        }
        
        with mss.mss() as sct:
            img = sct.grab(monitor)
        
        # 转换为 PIL Image (使用 PIL.Image.frombytes)
        from PIL import Image
        pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX", 0, 1)
        
        # 绘制红色矩形框
        draw = ImageDraw.Draw(pil_img)
        
        # 计算相对坐标
        rel_left = margin
        rel_top = margin
        rel_right = margin + width
        rel_bottom = margin + height
        
        # 绘制粗边框
        for i in range(3):
            draw.rectangle(
                [(rel_left - i, rel_top - i), (rel_right + i, rel_bottom + i)],
                outline='red',
                width=2
            )
        
        # 添加文字标签
        try:
            font = ImageFont.truetype("simhei.ttf", 16)  # 黑体
        except:
            font = ImageFont.load_default()
        
        label = "搜一搜按钮"
        draw.text(
            (rel_left, rel_top - 25),
            label,
            fill='red',
            font=font
        )
        
        # 保存
        pil_img.save(output_file)
        print(f"\n[OK] 高亮图片已保存到：{output_file}")
        
        # 尝试打开图片
        try:
            pil_img.show()
        except:
            pass
        
        return True
        
    except ImportError as e:
        print(f"\n[错误] 缺少依赖：{e}")
        print("\n请安装:")
        print("  pip install pillow mss")
        return False
    except Exception as e:
        print(f"\n[错误] 高亮失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 70)
    print(" 实战：定位并高亮微信的搜一搜按钮")
    print("=" * 70)
    
    scanner = UIARegionScanner()
    
    # 简化的 selector
    selector = """[{ 'wnd' : [ ('Text' , '微信') ] }, { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }]"""
    
    print(f"\n使用 selector:")
    print(selector)
    
    print("\n查找元素...")
    result = scanner.find_by_selector(selector, timeout=5.0)
    
    if result:
        print(f"[OK] 找到元素：{result.Name}")
        
        try:
            rect = result.BoundingRectangle
            rect_tuple = (rect.left, rect.top, rect.right, rect.bottom)
            
            # 高亮
            highlight_with_pil(rect_tuple, 'wechat_susou_highlight.png')
            
            print("\n[完成]")
            print("  1. 元素已定位")
            print("  2. 高亮图片已生成")
            print("  3. 可以查看 wechat_susou_highlight.png")
            
        except Exception as e:
            print(f"[错误] {e}")
    else:
        print("[失败] 未找到元素")
        print("\n可能原因:")
        print("  1. 微信未运行")
        print("  2. 微信窗口最小化")
        print("  3. 窗口标题不是'微信'")
        print("  4. '搜一搜'按钮不在当前界面")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
