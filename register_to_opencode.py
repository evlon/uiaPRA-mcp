"""
自动注册 tdRPA-mcp 到 Opencode
"""

import json
import os
import sys
from pathlib import Path


def find_opencode_config_dir():
    """查找 Opencode 配置目录"""
    # 可能的配置目录
    possible_dirs = [
        # Windows
        Path(os.environ.get("APPDATA", "")) / "opencode",
        Path(os.environ.get("APPDATA", "")) / "Code" / "User",
        # macOS
        Path.home() / "Library" / "Application Support" / "opencode",
        Path.home() / "Library" / "Application Support" / "Code" / "User",
        # Linux
        Path.home() / ".config" / "opencode",
        Path.home() / ".config" / "Code" / "User",
    ]

    # 查找存在的目录
    for dir_path in possible_dirs:
        if dir_path.exists():
            print(f"[INFO] 找到可能的配置目录：{dir_path}")
            return dir_path

    # 如果都不存在，创建一个
    default_dir = Path(os.environ.get("APPDATA", "")) / "opencode"
    print(f"[INFO] 配置目录不存在，将创建：{default_dir}")
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir


def create_mcp_config():
    """创建 MCP 配置"""
    project_root = Path(__file__).parent.absolute()
    venv_python = Path(r"D:\projects\wx-rpa\.venv\Scripts\python.exe")

    # 检查 Python 是否存在
    if not venv_python.exists():
        print(f"[ERROR] 找不到 Python: {venv_python}")
        print("[ERROR] 请确认虚拟环境路径正确")
        return None

    config = {
        "mcpServers": {
            "tdrpa-ui-scanner": {
                "command": str(venv_python),
                "args": [str(project_root / "mcp_server.py")],
                "cwd": str(project_root),
                "disabled": False,
                "autoApprove": [],
                "environment": {"PYTHONPATH": str(project_root)},
            }
        }
    }

    return config


def register_to_opencode():
    """注册到 Opencode"""
    print("=" * 60)
    print(" tdRPA-mcp 注册到 Opencode")
    print("=" * 60)

    # 1. 查找配置目录
    print("\n[1/4] 查找 Opencode 配置目录...")
    config_dir = find_opencode_config_dir()

    if not config_dir:
        print("[ERROR] 无法找到或创建配置目录")
        return False

    # 2. 创建配置
    print(f"\n[2/4] 创建 MCP 配置...")
    config = create_mcp_config()

    if not config:
        print("[ERROR] 无法创建 MCP 配置")
        return False

    # 3. 保存配置
    print(f"\n[3/4] 保存配置到 {config_dir}...")

    # 尝试写入 settings.json
    settings_file = config_dir / "settings.json"
    mcp_file = config_dir / "mcp.json"

    config_json = json.dumps(config, indent=2, ensure_ascii=False)

    try:
        # 检查是否已有配置文件
        if settings_file.exists():
            print(f"[INFO] 发现现有配置文件：{settings_file}")

            # 读取现有配置
            with open(settings_file, "r", encoding="utf-8") as f:
                existing_config = json.load(f)

            # 合并配置
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}

            existing_config["mcpServers"].update(config["mcpServers"])

            # 备份原文件
            backup_file = settings_file.with_suffix(".json.bak")
            settings_file.rename(backup_file)
            print(f"[INFO] 已备份原配置文件为：{backup_file}")

            # 保存新配置
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(existing_config, f, indent=2, ensure_ascii=False)

            print(f"[OK] 配置已保存到：{settings_file}")

        else:
            # 创建新文件
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"[OK] 配置已保存到：{settings_file}")

        # 同时保存到 mcp.json (方便查找)
        with open(mcp_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"[INFO] 配置也保存到：{mcp_file} (方便手动复制)")

    except Exception as e:
        print(f"[ERROR] 保存配置失败：{e}")
        print(f"[ERROR] 请手动复制以下内容到 Opencode 配置文件:")
        print("\n" + config_json + "\n")
        return False

    # 4. 验证
    print(f"\n[4/4] 验证配置...")

    if settings_file.exists() or mcp_file.exists():
        print("[OK] 配置文件已创建")

        print("\n" + "=" * 60)
        print(" 注册完成!")
        print("=" * 60)

        print("\n下一步:")
        print("  1. 重启 Opencode")
        print("  2. 打开 MCP 面板查看 'tdrpa-ui-scanner'")
        print("  3. 尝试使用自然语言查找元素")

        print("\n配置文件位置:")
        if settings_file.exists():
            print(f"  - {settings_file}")
        if mcp_file.exists():
            print(f"  - {mcp_file}")

        print("\n示例用法:")
        print('  在 Opencode 中输入："查找记事本的保存按钮"')

        return True
    else:
        print("[ERROR] 配置文件创建失败")
        return False


if __name__ == "__main__":
    success = register_to_opencode()
    sys.exit(0 if success else 1)
