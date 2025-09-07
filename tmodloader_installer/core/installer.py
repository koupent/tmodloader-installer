#!/usr/bin/env python3
"""
シンプルなtModLoaderインストーラー
指定したGitHubのパッケージをダウンロードして展開するだけ
"""

import os
import sys
import zipfile
import requests
import shutil
from pathlib import Path
from urllib.parse import urlparse
import re
from datetime import datetime


class SimpleInstaller:
    """シンプルなインストーラー"""

    def __init__(self, github_url: str, install_path: str):
        self.github_url = github_url
        self.install_path = Path(install_path)
        self.download_url = self._get_download_url()

    def _get_download_url(self) -> str:
        """GitHub Release URLからダウンロードURLを取得"""
        # URLからバージョンを抽出
        match = re.search(r"/tag/([^/]+)", self.github_url)
        if not match:
            raise ValueError("無効なGitHub Release URLです")

        tag = match.group(1)
        # API URLに変換
        api_url = (
            f"https://api.github.com/repos/tModLoader/tModLoader/releases/tags/{tag}"
        )

        response = requests.get(api_url)
        response.raise_for_status()

        release_data = response.json()

        # AssetsからtModLoader.zipを探す
        for asset in release_data.get("assets", []):
            if asset["name"] == "tModLoader.zip":
                return asset["browser_download_url"]

        raise ValueError("tModLoader.zipが見つかりません")

    def create_backup(self):
        """既存のtModLoaderフォルダをバックアップ"""
        if not self.install_path.exists():
            print(
                "既存のtModLoaderフォルダが見つかりません。バックアップをスキップします。"
            )
            return None

        # バックアップ先ディレクトリを作成（exeファイルと同じディレクトリ）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # PyInstallerでパッケージ化された場合の対応
        if getattr(sys, 'frozen', False):
            # 実行ファイルの場合、実行ファイルと同じディレクトリにbackupsを作成
            base_path = Path(sys.executable).parent
        else:
            # 開発環境の場合
            base_path = Path(__file__).parent.parent
        
        backup_dir = base_path / "backups"
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / f"tModLoader_backup_{timestamp}"

        print(f"バックアップ作成中: {backup_path}")
        shutil.copytree(self.install_path, backup_path)
        print("バックアップ完了")

        return backup_path

    def _download_file(self):
        """ファイルをダウンロード"""
        response = requests.get(self.download_url, stream=True)
        response.raise_for_status()
        
        # 一時ファイルに保存（exeファイルと同じディレクトリ）
        # PyInstallerでパッケージ化された場合の対応
        if getattr(sys, 'frozen', False):
            # 実行ファイルの場合、実行ファイルと同じディレクトリにdownloadsを作成
            base_path = Path(sys.executable).parent
        else:
            # 開発環境の場合
            base_path = Path(__file__).parent.parent
        
        temp_dir = base_path / "downloads"
        temp_dir.mkdir(exist_ok=True)
        self.temp_file = temp_dir / "tModLoader_temp.zip"
        with open(self.temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return response
    
    def _extract_files(self):
        """ZIPファイルを展開"""
        # インストール先ディレクトリを作成
        self.install_path.mkdir(parents=True, exist_ok=True)
        
        # ZIPファイルを展開（上書き配置）
        with zipfile.ZipFile(self.temp_file, "r") as zip_ref:
            zip_ref.extractall(self.install_path)
        
        # 一時ファイルを削除
        self.temp_file.unlink()

    def download_and_install(self):
        """ダウンロードしてインストール"""
        # 1. バックアップ作成
        backup_path = self.create_backup()
        
        # 2. ダウンロード
        print(f"ダウンロード中: {self.download_url}")
        self._download_file()
        print("ダウンロード完了")
        
        # 3. 展開
        print(f"展開中: {self.install_path}")
        self._extract_files()
        
        print("インストール完了！")
        
        if backup_path:
            print(f"バックアップはこちらに保存されました: {backup_path}")


def main():
    """メイン関数"""
    if len(sys.argv) != 3:
        print("使用方法: python simple_installer.py <GitHub_URL> <インストール先パス>")
        print(
            "例: python simple_installer.py https://github.com/tModLoader/tModLoader/releases/tag/v2025.06.3.0 C:/Steam/steamapps/common/tModLoader"
        )
        sys.exit(1)

    github_url = sys.argv[1]
    install_path = sys.argv[2]

    try:
        installer = SimpleInstaller(github_url, install_path)
        installer.download_and_install()
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
