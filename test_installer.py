#!/usr/bin/env python3
"""
tModLoader インストーラーのテストスクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from tmodloader_installer.config import Config
from tmodloader_installer.logger import setup_logger
from tmodloader_installer.steam import SteamManager
from tmodloader_installer.backup import BackupManager
from tmodloader_installer.downloader import DownloadManager
from tmodloader_installer.version import VersionChecker
from tmodloader_installer.utils import get_system_info, print_banner


def test_config():
    """設定ファイルのテスト"""
    print_banner("設定ファイルテスト")
    
    try:
        config = Config("config.yaml")
        print("✓ 設定ファイルの読み込み成功")
        print(f"  - ダウンロードディレクトリ: {config.download.download_dir}")
        print(f"  - バックアップディレクトリ: {config.backup.backup_dir}")
        print(f"  - ログレベル: {config.logging.level}")
        return True
    except Exception as e:
        print(f"✗ 設定ファイルの読み込み失敗: {e}")
        return False


def test_logger():
    """ロガーのテスト"""
    print_banner("ロガーテスト")
    
    try:
        config = Config("config.yaml")
        logger = setup_logger(config)
        logger.info("テストログメッセージ")
        print("✓ ロガーの初期化成功")
        return True
    except Exception as e:
        print(f"✗ ロガーの初期化失敗: {e}")
        return False


def test_steam_manager():
    """Steam管理のテスト"""
    print_banner("Steam管理テスト")
    
    try:
        config = Config("config.yaml")
        logger = setup_logger(config)
        steam_manager = SteamManager(config, logger)
        
        # tModLoaderパスの検索
        tmodloader_path = steam_manager.find_tmodloader_path()
        if tmodloader_path:
            print(f"✓ tModLoaderパス発見: {tmodloader_path}")
        else:
            print("⚠ tModLoaderパスが見つかりません（正常な場合があります）")
        
        # Steam実行確認
        is_running = steam_manager.is_steam_running()
        print(f"  - Steam実行中: {is_running}")
        
        return True
    except Exception as e:
        print(f"✗ Steam管理テスト失敗: {e}")
        return False


def test_backup_manager():
    """バックアップ管理のテスト"""
    print_banner("バックアップ管理テスト")
    
    try:
        config = Config("config.yaml")
        logger = setup_logger(config)
        backup_manager = BackupManager(config, logger)
        
        # バックアップ一覧の取得
        backups = backup_manager.list_backups()
        print(f"✓ バックアップ一覧取得成功: {len(backups)}個")
        
        return True
    except Exception as e:
        print(f"✗ バックアップ管理テスト失敗: {e}")
        return False


def test_download_manager():
    """ダウンロード管理のテスト"""
    print_banner("ダウンロード管理テスト")
    
    try:
        config = Config("config.yaml")
        logger = setup_logger(config)
        download_manager = DownloadManager(config, logger)
        
        # ダウンロードURLの取得テスト
        download_url = download_manager._get_download_url()
        if download_url:
            print(f"✓ ダウンロードURL取得成功: {download_url}")
        else:
            print("⚠ ダウンロードURLの取得に失敗")
        
        return True
    except Exception as e:
        print(f"✗ ダウンロード管理テスト失敗: {e}")
        return False


def test_version_checker():
    """バージョン確認のテスト"""
    print_banner("バージョン確認テスト")
    
    try:
        config = Config("config.yaml")
        logger = setup_logger(config)
        version_checker = VersionChecker(config, logger)
        
        # バージョン正規化のテスト
        test_versions = ["v2025.02.3.2", "2025.02.3.2", "v2025.2.3.2"]
        for version in test_versions:
            normalized = version_checker._normalize_version(version)
            print(f"  - {version} -> {normalized}")
        
        print("✓ バージョン確認テスト成功")
        return True
    except Exception as e:
        print(f"✗ バージョン確認テスト失敗: {e}")
        return False


def test_utils():
    """ユーティリティのテスト"""
    print_banner("ユーティリティテスト")
    
    try:
        # システム情報の取得
        system_info = get_system_info()
        print("✓ システム情報取得成功")
        print(f"  - プラットフォーム: {system_info['platform']}")
        print(f"  - Pythonバージョン: {system_info['python_version']}")
        
        return True
    except Exception as e:
        print(f"✗ ユーティリティテスト失敗: {e}")
        return False


def main():
    """メインテスト関数"""
    print_banner("tModLoader インストーラーテスト", "=")
    
    tests = [
        ("設定ファイル", test_config),
        ("ロガー", test_logger),
        ("Steam管理", test_steam_manager),
        ("バックアップ管理", test_backup_manager),
        ("ダウンロード管理", test_download_manager),
        ("バージョン確認", test_version_checker),
        ("ユーティリティ", test_utils),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}テストを実行中...")
        if test_func():
            passed += 1
        print()
    
    print_banner("テスト結果", "=")
    print(f"成功: {passed}/{total}")
    print(f"失敗: {total - passed}/{total}")
    
    if passed == total:
        print("✓ すべてのテストが成功しました！")
        return 0
    else:
        print("✗ 一部のテストが失敗しました。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
