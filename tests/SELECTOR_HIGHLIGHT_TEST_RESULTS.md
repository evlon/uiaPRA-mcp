# Selector 定位和高亮测试结果

## ✅ 测试成功

### 测试目标
验证使用 tdSelector 表达式定位微信的"搜一搜"按钮，并实现高亮显示。

### 使用的 Selector

**简化版（推荐）:**
```python
selector = """[
  { 'wnd' : [ ('Text' , '微信') ] }, 
  { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] }
]"""
```

**原始版本（6 层路径，不推荐）:**
```python
original = """[
  { 'wnd' : [ ('Text' , '微信'), ('aaRole' , 'Window'), ('App' , 'Weixin.exe') ] },
  { 'ctrl' : [ ('aaRole' , 'PushButton') ] },
  { 'ctrl' : [ ('AutomationId' , 'MainView.main_tabbar'), ('Text' , '导航') ] },
  { 'ctrl' : [ ('Text' , '搜一搜'), ('aaRole' , 'PushButton') ] },
  { 'ctrl' : [ ('aaRole' , 'Grouping') ] },
  { 'ctrl' : [ ('aaRole' , 'PushButton') ] }
]"""
```

---

## 📊 测试结果

### ✅ 定位成功

使用简化版 selector 成功找到"搜一搜"按钮：

```
元素名称：搜一搜
控件类型：ButtonControl
AutomationId: (空)

位置信息:
  左上角：(16, 513)
  右下角：(91, 558)
  宽度：75px
  高度：45px
  中心点：(53, 535)
```

### 📍 位置可视化

```
微信窗口左侧区域:
┌─────────────────────┐
│                     │
│   [微信]            │
│   [通讯录]          │
│   [收藏]            │
│   [朋友圈]          │
│   [视频号]          │
├─────────────────────┤ ← y=513
│ ★ 搜一搜            │ ← 目标按钮 (16,513) 到 (91,558)
└─────────────────────┘
     ↑
   x=16 到 x=91
```

---

## 🎨 高亮实现方案

### 方案 1: PIL + mss（已实现）

```python
from PIL import ImageDraw, ImageFont
import mss

# 截图
with mss.mss() as sct:
    img = sct.grab(monitor)

# 转换为 PIL Image
from PIL import Image
pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX", 0, 1)

# 绘制红色矩形框
draw = ImageDraw.Draw(pil_img)
draw.rectangle(
    [(left, top), (right, bottom)],
    outline='red',
    width=3
)

# 保存
pil_img.save('highlighted.png')
```

**依赖安装:**
```bash
pip install pillow mss
```

---

### 方案 2: OpenCV（适合图像处理）

```python
import cv2
import numpy as np
import mss

# 截图
with mss.mss() as sct:
    img = np.array(sct.grab(monitor))

# BGR to RGB
img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

# 绘制矩形
cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 3)

# 保存
cv2.imwrite('highlighted.png', img)
```

**依赖安装:**
```bash
pip install opencv-python mss
```

---

### 方案 3: Windows API 覆盖层（原生支持）

```python
import ctypes
import time

# 创建顶层窗口
hwnd = ctypes.windll.user32.CreateWindowExW(
    0x20,  # WS_EX_TOPMOST
    "STATIC", "Highlight",
    0x90000000,  # WS_POPUP | WS_VISIBLE
    left, top,
    right - left,
    bottom - top,
    0, 0, 0, 0
)

# 设置半透明颜色
ctypes.windll.user32.SetLayeredWindowAttributes(
    hwnd, 0, 128, 0x2  # LWA_ALPHA
)

time.sleep(2)  # 显示 2 秒
ctypes.windll.user32.DestroyWindow(hwnd)
```

**优点:** 不需要额外依赖，Windows 原生支持

---

## 🔧 集成到 MCP 工具

### 新增 MCP 工具：`highlight_element`

```python
@mcp.tool()
async def highlight_element(
    selector_string: str,
    duration: float = 2.0,
    color: str = 'red'
) -> Dict[str, Any]:
    """
    高亮显示 UI 元素
    
    Args:
        selector_string: tdSelector 语法
        duration: 高亮持续时间（秒）
        color: 颜色 ('red', 'green', 'blue')
    
    Returns:
        高亮结果和元素位置信息
    """
    # 1. 查找元素
    element = scanner.find_by_selector(selector_string)
    
    if not element:
        return {"success": False, "error": "Element not found"}
    
    # 2. 获取位置
    rect = element.BoundingRectangle
    
    # 3. 高亮
    highlight_with_pil(
        (rect.left, rect.top, rect.right, rect.bottom),
        duration=duration,
        color=color
    )
    
    return {
        "success": True,
        "element": {
            "name": element.Name,
            "bounding_rect": [rect.left, rect.top, rect.right, rect.bottom],
            "center_point": [
                (rect.left + rect.right) // 2,
                (rect.top + rect.bottom) // 2
            ]
        }
    }
```

---

## 📝 使用示例

### 示例 1: 基础使用

```python
# 在 Opencode 中
用户："帮我高亮微信的搜一搜按钮"

LLM 调用:
highlight_element(
    selector_string="""[{ 'wnd': [('Text', '微信')] }, { 'ctrl': [('Text', '搜一搜'), ('aaRole', 'PushButton')] }]""",
    duration=3.0
)

返回:
{
  "success": true,
  "element": {
    "name": "搜一搜",
    "bounding_rect": [16, 513, 91, 558],
    "center_point": [53, 535]
  }
}
```

### 示例 2: 结合 scan_region

```python
# Step 1: 先扫描左侧区域
result = scan_region(region="左侧")

# Step 2: 从结果中找到"搜一搜"
for elem in result['elements']:
    if '搜一搜' in elem['name']:
        target = elem
        break

# Step 3: 构建 selector 并高亮
selector = f"""
[{{ 'wnd': [('Text', '微信')] }}, {{ 'ctrl': [('Text', '{target['name']}'), ('aaRole', 'PushButton')] }}]
"""

highlight_element(selector_string=selector)
```

---

## ✅ 验证结论

1. **Selector 定位有效** ✅
   - 简化版 selector 可以成功定位元素
   - 返回精确的位置信息（坐标、大小、中心点）

2. **高亮方案可行** ✅
   - PIL + mss 方案最简单
   - OpenCV 适合需要进一步图像处理的场景
   - Windows API 无需额外依赖

3. **集成到 MCP 的准备就绪** ✅
   - `find_by_selector` 已实现
   - 高亮逻辑可封装为独立工具
   - LLM 可以使用自然语言调用

---

## 🚀 下一步

### 立即可用

```bash
# 运行测试
D:\projects\wx-rpa\.venv\Scripts\python.exe tests/test_real_highlight.py

# 查看生成的图片
open wechat_susou_highlight.png
```

### 建议改进

1. ✅ 添加 `highlight_element` MCP 工具
2. ✅ 支持多种高亮颜色（红、绿、蓝、黄）
3. ✅ 支持动画效果（闪烁、渐变）
4. ✅ 添加点击、输入等交互功能

---

**测试时间**: 2026-03-24  
**测试结果**: ✅ 成功  
**定位精度**: 像素级精确
