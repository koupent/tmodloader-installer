#!/usr/bin/env python3
"""
定数定義
"""

# デフォルト設定
DEFAULT_GITHUB_URL = (
    "https://github.com/tModLoader/tModLoader/releases/tag/v2025.02.3.2"
)
DEFAULT_INSTALL_PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\tModLoader"

# ウィンドウサイズ
WINDOW_SIZE = "600x350"
LOG_WINDOW_SIZE = "700x500"
BACKUP_DIALOG_SIZE = "600x400"

# プログレスバー設定
PROGRESS_MAX = 100


# 進捗段階の定数
class ProgressStage:
    """インストール進捗段階"""

    BACKUP_START = 10
    DOWNLOAD_PREP = 20
    DOWNLOAD_START = 30
    DOWNLOAD_COMPLETE = 70
    EXTRACT_START = 80
    FINAL_PROCESS = 95
    COMPLETE = 100

    # 復元進捗段階
    RESTORE_PREP = 20
    RESTORE_DELETE = 40
    RESTORE_COPY = 60
    RESTORE_FINAL = 90
    RESTORE_COMPLETE = 100
