#!/usr/bin/env python3
"""
リリース用スクリプト
"""

import os
import sys
import subprocess
from pathlib import Path


def get_current_version():
    """現在のバージョンを取得"""
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.startswith("version = "):
                    return line.split('"')[1]
    except Exception:
        pass
    return "0.1.0"


def update_version(new_version):
    """バージョンを更新"""
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("version = "):
                lines[i] = f'version = "{new_version}"'
                break
        
        with open("pyproject.toml", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"バージョンを {new_version} に更新しました")
        return True
    except Exception as e:
        print(f"バージョン更新エラー: {e}")
        return False


def create_git_tag(version):
    """Gitタグを作成"""
    try:
        # 変更をコミット
        subprocess.run(["git", "add", "pyproject.toml"], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: bump version to {version}"], check=True)
        
        # タグを作成
        subprocess.run(["git", "tag", f"v{version}"], check=True)
        
        print(f"Gitタグ v{version} を作成しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Gitタグ作成エラー: {e}")
        return False


def push_changes():
    """変更をプッシュ"""
    try:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", "--tags"], check=True)
        print("変更をプッシュしました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"プッシュエラー: {e}")
        return False


def main():
    """メイン関数"""
    if len(sys.argv) != 2:
        print("使用方法: python scripts/release.py <version>")
        print("例: python scripts/release.py 1.0.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    current_version = get_current_version()
    
    print(f"現在のバージョン: {current_version}")
    print(f"新しいバージョン: {new_version}")
    
    # バージョン更新
    if not update_version(new_version):
        sys.exit(1)
    
    # Gitタグ作成
    if not create_git_tag(new_version):
        sys.exit(1)
    
    # プッシュ
    if not push_changes():
        sys.exit(1)
    
    print(f"\nリリース v{new_version} の準備が完了しました！")
    print("GitHub Actionsが自動的にビルドとリリースを実行します。")


if __name__ == "__main__":
    main()
