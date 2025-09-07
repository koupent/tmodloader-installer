#!/usr/bin/env python3
"""
tModLoader インストーラー メインエントリーポイント
"""

from .gui import MainWindow


def main():
    """メイン関数"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
