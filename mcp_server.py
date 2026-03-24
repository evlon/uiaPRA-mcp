"""
uiaRPA-mcp: 基于 uiautomation 的 UIA 元素查找 MCP 服务

通过 9 宫格分区域扫描 + 语义化过滤，提升 UI 元素查找速度。
"""
import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 MCP 实例
mcp = FastMCP(
    name="uiaRPA-ui-scanner",
    instructions="""
    uiaRPA-mcp 提供基于 uiautomation 的 UIA 元素查找能力。
    
    核心特性:
    - 9 宫格分区域扫描
    - 语义化元素过滤
    - UI 树完整扫描
    - 支持自然语言和 selector 语法两种查询方式
    
    使用流程:
    1. 调用 set_focus_window 设置目标窗口
    2. 使用 get_ui_tree_data 获取 UI 树数据
    3. 使用 filter_ui_elements 语义化过滤
    4. 使用 highlight_element 高亮验证
    """
)

# 全局状态
scanner_state: Dict[str, Any] = {
    'scanner': None,
    'grid_manager': None,
    'cache': {}
}


def load_config() -> dict:
    """加载配置文件"""
    config_path = project_root / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


@mcp.tool()
async def get_status() -> Dict[str, Any]:
    """
    获取服务状态
    
    Returns:
        当前服务状态信息
    """
    scanner = scanner_state.get('scanner')
    grid_manager = scanner_state.get('grid_manager')
    
    if scanner and grid_manager:
        try:
            window_rect = scanner.get_window_rect()
            return {
                "status": "ready",
                "has_target": True,
                "window_rect": list(window_rect),
                "total_grids": 9,
                "cache_size": len(scanner_state.get('cache', {}))
            }
        except:
            pass
    
    return {
        "status": "idle",
        "has_target": False,
        "message": "No target window set. Call set_focus_window first."
    }


@mcp.tool()
async def scan_all_grids(
    force: bool = False,
    layers: int = 2
) -> Dict[str, Any]:
    """
    扫描所有宫格区域
    
    Args:
        force: 是否强制重新扫描 (忽略缓存)
        layers: 扫描层数 (0=焦点，1=焦点 + 相邻，2=全部)
    
    Returns:
        扫描结果统计
    """
    from core.focus_diffusion import FocusDiffusionScanner
    
    scanner = scanner_state.get('scanner')
    if not scanner:
        return {"error": "Scanner not initialized"}
    
    try:
        import time
        start_time = time.time()
        
        # 创建扩散扫描器
        diffusion_scanner = FocusDiffusionScanner.__new__(FocusDiffusionScanner)
        diffusion_scanner.scanner = scanner
        diffusion_scanner.grid_manager = scanner_state['grid_manager']
        diffusion_scanner.cache = scanner_state.get('cache', {})
        
        # 扫描
        if layers == 2 or force:
            results = diffusion_scanner.scan_all(force=force)
        else:
            results = diffusion_scanner.scan_focus_area(layers=layers)
        
        # 更新缓存
        scanner_state['cache'] = {
            result.grid_id: result 
            for result in results.values()
        }
        
        scan_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "scanned_grids": len(results),
            "total_elements": sum(
                len(r.elements) for r in results.values()
            ),
            "scan_time_ms": round(scan_time, 2),
            "cache_size": len(scanner_state['cache'])
        }
    
    except Exception as e:
        logger.error(f"Error scanning grids: {e}")
        return {"error": str(e)}


@mcp.tool()
async def clear_cache() -> Dict[str, Any]:
    """
    清除扫描缓存
    
    Returns:
        操作结果
    """
    scanner_state['cache'] = {}
    return {"success": True, "message": "Cache cleared"}


def register_all_tools():
    """注册所有工具"""
    from tools.element_finder import register_element_finder
    from tools.selector_query import register_selector_query
    from tools.grid_picker import register_grid_picker
    
    # 注册工具
    register_element_finder(mcp, scanner_state)
    register_selector_query(mcp, scanner_state)
    register_grid_picker(mcp, scanner_state)


def main():
    """主函数"""
    # 加载配置
    config = load_config()
    logger.info("Configuration loaded")
    
    # 注册所有工具
    register_all_tools()
    logger.info("Tools registered")
    
    # 启动 MCP 服务
    logger.info("Starting MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
