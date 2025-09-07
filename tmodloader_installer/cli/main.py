#!/usr/bin/env python3
"""
コマンドラインインターフェース
"""

import argparse
import sys
from ..core import SimpleInstaller


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="tModLoader インストーラー")
    parser.add_argument(
        "github_url",
        help="GitHub Release URL (例: https://github.com/tModLoader/tModLoader/releases/tag/v2025.06.3.0)",
    )
    parser.add_argument(
        "install_path",
        help="インストール先パス (例: C:\\Program Files (x86)\\Steam\\steamapps\\common\\tModLoader)",
    )

    args = parser.parse_args()

    try:
        installer = SimpleInstaller(args.github_url, args.install_path)
        installer.download_and_install()
        print("インストールが正常に完了しました！")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
