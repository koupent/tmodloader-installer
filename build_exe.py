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
    print("Building tModLoader Installer executable...")

    # PyInstallerコマンド
    cmd = [
        "pyinstaller",
        "--onefile",  # 単一ファイルとして出力
        "--windowed",  # コンソールウィンドウを非表示
        "--name=tModLoaderInstaller",  # 実行ファイル名
        # "--icon=icon.ico",  # アイコンファイル（存在する場合）
        # "--add-data=config.yaml;.",  # 設定ファイルを含める（不要）
        "--hidden-import=requests",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "tmodloader_installer/__main__.py",
    ]

    try:
        # ビルド実行
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed!")
        print(f"Executable: dist/tModLoaderInstaller.exe")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Build error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Install with:")
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
        print("Icon file created: icon.ico")
        return True

    except ImportError:
        print("Pillow not installed. Icon will not be created.")
        return False
    except Exception as e:
        print(f"Icon creation error: {e}")
        return False


def main():
    """メイン関数"""
    print("=" * 50)
    print("tModLoader Installer Build Script")
    print("=" * 50)

    # アイコンファイルの作成
    create_icon()

    # 実行ファイルのビルド
    if build_executable():
        print("\nBuild completed successfully!")
        print("Run dist/tModLoaderInstaller.exe")
    else:
        print("\nBuild failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
