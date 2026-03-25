#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可见性过滤功能测试脚本

用于测试和演示可见性过滤策略的效果。
对比启用和禁用可见性过滤时的元素数量差异。

使用方法:
    cd d:/projects/wx-rpa
    .venv/Scripts/python.exe uiaRPA-mcp/test_visibility_filter.py

测试场景:
    1. 打开微信或其他应用窗口
    2. 运行此脚本
    3. 观察启用/禁用可见性过滤的元素数量差异
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def test_visibility_checker():
    """测试可见性检测器基本功能"""
    print("=" * 60)
    print("Test 1: VisibilityChecker Basic Functionality")
    print("=" * 60)
    
    try:
        from core.visibility_checker import VisibilityChecker
        
        checker = VisibilityChecker()
        logger.info("VisibilityChecker initialized successfully")
        
        # 测试便捷函数
        from core.visibility_checker import check_visibility, filter_visible
        logger.info("Convenience functions imported successfully")
        
        print("\n[PASS] VisibilityChecker module test passed\n")
        return True
        
    except Exception as e:
        logger.error(f"VisibilityChecker test failed: {e}")
        return False


def test_ui_tree_scanner_with_visibility():
    """测试 UI 树扫描器的可见性过滤功能"""
    print("=" * 60)
    print("Test 2: UITreeScanner Visibility Filter")
    print("=" * 60)
    
    try:
        import uiautomation as auto
        from core.ui_tree_scanner import UITreeScanner
        from core.grid_manager import GridManager
        
        # 获取桌面窗口作为测试对象
        desktop = auto.GetRootControl()
        logger.info(f"Got desktop root window: {desktop.Name}")
        
        # 创建宫格管理器（使用桌面矩形）
        desktop_rect = desktop.BoundingRectangle
        grid_manager = GridManager(
            (desktop_rect.left, desktop_rect.top, desktop_rect.right, desktop_rect.bottom),
            rows=3,
            cols=3
        )
        logger.info("Created 9-grid manager successfully")
        
        # 测试 1: 启用可见性过滤
        print("\n--- With Visibility Filter Enabled ---")
        scanner_with_filter = UITreeScanner(
            desktop, 
            grid_manager, 
            enable_visibility_filter=True
        )
        scanner_with_filter.scan_full_tree(max_depth=8)
        elements_with_filter = len(scanner_with_filter.all_elements)
        logger.info(f"With visibility filter: {elements_with_filter} elements scanned")
        
        # 测试 2: 禁用可见性过滤
        print("\n--- With Visibility Filter Disabled ---")
        scanner_without_filter = UITreeScanner(
            desktop, 
            grid_manager, 
            enable_visibility_filter=False
        )
        scanner_without_filter.scan_full_tree(max_depth=8)
        elements_without_filter = len(scanner_without_filter.all_elements)
        logger.info(f"Without visibility filter: {elements_without_filter} elements scanned")
        
        # 对比结果
        print("\n--- Comparison Results ---")
        print(f"With visibility filter: {elements_with_filter} elements")
        print(f"Without visibility filter: {elements_without_filter} elements")
        
        if elements_without_filter > 0:
            filtered_out = elements_without_filter - elements_with_filter
            filter_rate = (filtered_out / elements_without_filter) * 100
            print(f"Filtered out: {filtered_out} elements ({filter_rate:.1f}%)")
        
        print("\n[PASS] UITreeScanner visibility filter test passed\n")
        return True
        
    except Exception as e:
        logger.error(f"UITreeScanner test failed: {e}", exc_info=True)
        return False


def test_mcp_tools_integration():
    """测试 MCP 工具集成"""
    print("=" * 60)
    print("Test 3: MCP Tools Visibility Filter Parameters")
    print("=" * 60)
    
    try:
        # 检查工具函数签名
        from tools.grid_picker import register_grid_picker
        import inspect
        
        # 获取注册的函数
        logger.info("grid_picker module imported successfully")
        
        # 由于需要 mcp 实例才能注册，我们直接检查源码
        import ast
        script_dir = os.path.dirname(os.path.abspath(__file__))
        grid_picker_path = os.path.join(script_dir, 'tools', 'grid_picker.py')
        
        with open(grid_picker_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 解析 AST 来检查函数参数
        tree = ast.parse(source)
        
        functions_checked = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                if node.name in ['get_ui_tree_data', 'filter_ui_elements', 'scan_region', 'build_selector_for_element']:
                    # 检查是否有 enable_visibility_filter 参数
                    has_param = any(
                        arg.arg == 'enable_visibility_filter' 
                        for arg in node.args.args
                    )
                    if has_param:
                        logger.info(f"Function {node.name} has enable_visibility_filter parameter")
                        functions_checked += 1
                    else:
                        logger.warning(f"Function {node.name} missing enable_visibility_filter parameter")
        
        if functions_checked >= 4:
            print("\n[PASS] MCP tools integration test passed\n")
            return True
        else:
            logger.error(f"Only {functions_checked}/4 functions updated")
            return False
        
    except Exception as e:
        logger.error(f"MCP tools integration test failed: {e}", exc_info=True)
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Visibility Filter Test Suite")
    print("=" * 60 + "\n")
    
    results = {
        "VisibilityChecker Basic": test_visibility_checker(),
        "UITreeScanner Visibility Filter": test_ui_tree_scanner_with_visibility(),
        "MCP Tools Integration": test_mcp_tools_integration(),
    }
    
    # 打印总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! Visibility filter feature is correctly integrated.\n")
        return True
    else:
        print(f"\n{total - passed} test(s) failed, please check error logs.\n")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
