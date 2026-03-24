"""
运行所有测试
"""
import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*70}")
    print(f" 运行测试：{test_file.name}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=test_file.parent
    )
    
    if result.returncode == 0:
        print(f"\n[OK] {test_file.name} 通过")
    else:
        print(f"\n[FAIL] {test_file.name} 失败 (退出码：{result.returncode})")
    
    return result.returncode

def main():
    """运行所有测试"""
    tests_dir = Path(__file__).parent
    
    # 查找所有测试文件
    test_files = sorted(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("未找到测试文件")
        return 0
    
    print("="*70)
    print(" tdRPA-mcp 测试套件")
    print("="*70)
    print(f"\n找到 {len(test_files)} 个测试文件:")
    for f in test_files:
        print(f"  - {f.name}")
    
    # 运行所有测试
    failed = []
    for test_file in test_files:
        if run_test(test_file) != 0:
            failed.append(test_file.name)
    
    # 总结
    print("\n" + "="*70)
    print(" 测试总结")
    print("="*70)
    print(f"\n总测试数：{len(test_files)}")
    print(f"通过：{len(test_files) - len(failed)}")
    print(f"失败：{len(failed)}")
    
    if failed:
        print("\n失败的测试:")
        for name in failed:
            print(f"  - {name}")
        return 1
    else:
        print("\n[OK] 所有测试通过!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
