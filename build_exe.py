#!/usr/bin/env python3
"""
tModLoader インストーラー実行ファイルビルドスクリプト
"""

import os
import sys
import subprocess
from pathlib import Path


def build_executable():
    """実行ファイルをビルド"""
    print("tModLoader インストーラー実行ファイルをビルドしています...")

    # PyInstallerコマンド
    cmd = [
        "pyinstaller",
        "--onefile",  # 単一ファイルとして出力
        "--windowed",  # コンソールウィンドウを非表示
        "--name=tModLoaderInstaller",  # 実行ファイル名
        "--icon=icon.ico",  # アイコンファイル（存在する場合）
        "--add-data=config.yaml;.",  # 設定ファイルを含める
        "--hidden-import=win32api",  # Windows API
        "--hidden-import=win32con",
        "--hidden-import=win32gui",
        "--hidden-import=win32process",
        "--hidden-import=psutil",
        "--hidden-import=requests",
        "--hidden-import=yaml",
        "--hidden-import=colorama",
        "--hidden-import=tqdm",
        "tmodloader_installer/__main__.py",
    ]

    try:
        # ビルド実行
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("ビルドが完了しました！")
        print(f"実行ファイル: dist/tModLoaderInstaller.exe")
        return True

    except subprocess.CalledProcessError as e:
        print(f"ビルドエラー: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstallerが見つかりません。以下のコマンドでインストールしてください:")
        print("uv add pyinstaller")
        return False


def create_icon():
    """アイコンファイルを作成（簡単な例）"""
    try:
        from PIL import Image, ImageDraw

        # 32x32のアイコンを作成
        size = (32, 32)
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 簡単なアイコンを描画
        draw.ellipse([2, 2, 30, 30], fill=(0, 100, 200, 255))
        draw.text((8, 8), "T", fill=(255, 255, 255, 255))

        # アイコンファイルとして保存
        image.save("icon.ico", format="ICO")
        print("アイコンファイルを作成しました: icon.ico")
        return True

    except ImportError:
        print("Pillowがインストールされていません。アイコンは作成されません。")
        return False
    except Exception as e:
        print(f"アイコン作成エラー: {e}")
        return False


def main():
    """メイン関数"""
    print("=" * 50)
    print("tModLoader インストーラー ビルドスクリプト")
    print("=" * 50)

    # アイコンファイルの作成
    create_icon()

    # 実行ファイルのビルド
    if build_executable():
        print("\nビルドが正常に完了しました！")
        print("dist/tModLoaderInstaller.exe を実行してください。")
    else:
        print("\nビルドに失敗しました。")
        sys.exit(1)


if __name__ == "__main__":
    main()
