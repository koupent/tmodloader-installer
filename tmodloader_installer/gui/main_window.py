#!/usr/bin/env python3
"""
メインGUIウィンドウ
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import shutil
import sys
from pathlib import Path

from tmodloader_installer.core import SimpleInstaller
from tmodloader_installer.utils import (
    DEFAULT_GITHUB_URL,
    DEFAULT_INSTALL_PATH,
    WINDOW_SIZE,
    PROGRESS_MAX,
    ProgressStage,
    natural_sort_key,
)
from tmodloader_installer.gui.dialogs import BackupSelectionDialog
from tmodloader_installer.gui.widgets import LogWindow


class MainWindow:
    """メインGUIウィンドウ"""

    def __init__(self):
        """初期化"""
        self.root = tk.Tk()
        self.root.title("tModLoader インストーラー")
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        # プログレスバーのスタイル設定
        self._setup_styles()

        # 設定ファイルのパス
        self.config_file = self._get_config_file_path()

        # ログメッセージの保存用
        self.log_messages = []

        self.setup_gui()
        self.load_config()

        # ウィンドウが閉じられる時の処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_styles(self):
        """GUIスタイルの設定"""
        style = ttk.Style()
        style.configure("TProgressbar", thickness=20)

    def _get_config_file_path(self):
        """設定ファイルのパスを取得"""
        # PyInstallerでパッケージ化された場合の対応
        if getattr(sys, 'frozen', False):
            # 実行ファイルの場合、実行ファイルと同じディレクトリにconfigを作成
            base_path = Path(sys.executable).parent
        else:
            # 開発環境の場合
            base_path = Path(__file__).parent.parent
        
        config_dir = base_path / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "gui_config.json"

    def setup_gui(self):
        """GUIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = ttk.Label(
            main_frame, text="tModLoader インストーラー", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # GitHub URL設定
        url_frame = ttk.LabelFrame(main_frame, text="GitHub Release URL", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        self.url_var = tk.StringVar(value=DEFAULT_GITHUB_URL)
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(fill=tk.X)
        # 入力変更時に自動保存
        self.url_var.trace("w", lambda *args: self.save_config())

        # インストール先パス設定
        path_frame = ttk.LabelFrame(main_frame, text="インストール先パス", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 10))

        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X)

        self.path_var = tk.StringVar(value=DEFAULT_INSTALL_PATH)
        path_entry = ttk.Entry(path_input_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # 入力変更時に自動保存
        self.path_var.trace("w", lambda *args: self.save_config())

        browse_button = ttk.Button(
            path_input_frame, text="参照", command=self.browse_path
        )
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))

        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        self.install_button = ttk.Button(
            button_frame,
            text="インストール開始",
            command=self.start_install,
            style="Accent.TButton",
        )
        self.install_button.pack(side=tk.LEFT)

        self.restore_button = ttk.Button(
            button_frame, text="バックアップから復元", command=self.start_restore
        )
        self.restore_button.pack(side=tk.LEFT, padx=(10, 0))

        self.log_button = ttk.Button(
            button_frame, text="ログ表示", command=self.show_log_window
        )
        self.log_button.pack(side=tk.LEFT, padx=(10, 0))

        # プログレスバー
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(20, 0))

        self.progress_var = tk.StringVar(value="準備完了")
        progress_label = ttk.Label(
            progress_frame, textvariable=self.progress_var, font=("Arial", 10, "bold")
        )
        progress_label.pack(pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=500,
            style="TProgressbar",
            maximum=PROGRESS_MAX,
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

    def browse_path(self):
        """パス選択ダイアログ"""
        path = filedialog.askdirectory(title="tModLoaderフォルダを選択")
        if path:
            self.path_var.set(path)

    def log(self, message):
        """ログにメッセージを追加"""
        self.log_messages.append(message)
        # ログウィンドウが開いている場合はリアルタイム更新
        if hasattr(self, "log_text") and self.log_text.winfo_exists():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.root.update_idletasks()

    def show_log_window(self):
        """ログ表示ウィンドウを開く"""
        log_window = LogWindow(self.root, self.log_messages)
        log_window.show()

    def start_install(self):
        """インストール開始"""
        github_url = self.url_var.get().strip()
        install_path = self.path_var.get().strip()

        if not github_url or not install_path:
            messagebox.showerror(
                "エラー", "GitHub URLとインストール先パスを入力してください"
            )
            return

        # ボタンを無効化
        self.install_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_var.set("インストール開始...")

        # 別スレッドでインストール実行
        thread = threading.Thread(
            target=self.run_install, args=(github_url, install_path)
        )
        thread.daemon = True
        thread.start()

    def run_install(self, github_url, install_path):
        """インストール実行"""
        try:
            self.log("=== tModLoader インストール開始 ===")
            self._update_progress_async(
                ProgressStage.BACKUP_START, "バックアップ作成中..."
            )

            installer = SimpleInstaller(github_url, install_path)

            # バックアップ作成
            self.log("既存フォルダのバックアップを作成中...")
            backup_path = installer.create_backup()
            if backup_path:
                self.log(f"バックアップ完了: {backup_path}")
            else:
                self.log("既存フォルダが見つかりません。新規インストールします。")

            self._update_progress_async(
                ProgressStage.DOWNLOAD_PREP, "ダウンロード準備中..."
            )

            # ダウンロード
            self.log(f"ダウンロード中: {installer.download_url}")
            self._update_progress_async(
                ProgressStage.DOWNLOAD_START, "ダウンロード中..."
            )
            response = installer._download_file()
            self.log("ダウンロード完了")

            self._update_progress_async(
                ProgressStage.DOWNLOAD_COMPLETE, "ダウンロード完了"
            )

            # 展開
            self.log(f"展開中: {install_path}")
            self._update_progress_async(
                ProgressStage.EXTRACT_START, "ファイル展開中..."
            )
            installer._extract_files()
            self.log("展開完了")

            self._update_progress_async(ProgressStage.FINAL_PROCESS, "最終処理中...")

            self.log("=== インストール完了！ ===")
            if backup_path:
                self.log(f"バックアップ: {backup_path}")

            # UI更新
            self._update_progress_async(ProgressStage.COMPLETE, "インストール完了！")
            self.root.after(0, self.install_complete)

        except Exception as e:
            self.log(f"エラー: {e}")
            self.root.after(0, self.install_error)

    def _update_progress_async(self, value, message):
        """プログレスバーとメッセージを非同期で更新"""
        self.root.after(0, lambda: self.update_progress(value, message))

    def update_progress(self, value, message):
        """プログレスバーとメッセージを更新"""
        self.progress_bar["value"] = value
        self.progress_var.set(f"{message} ({value}%)")

    def install_complete(self):
        """インストール完了"""
        self.progress_bar["value"] = 100
        self.progress_var.set("インストール完了！ (100%)")
        self.install_button.config(state="normal")
        messagebox.showinfo("完了", "インストールが正常に完了しました！")

    def install_error(self):
        """インストールエラー"""
        self.progress_bar["value"] = 0
        self.progress_var.set("エラーが発生しました")
        self.install_button.config(state="normal")
        messagebox.showerror(
            "エラー", "インストール中にエラーが発生しました。ログを確認してください。"
        )

    def save_config(self):
        """設定を保存"""
        config = {"github_url": self.url_var.get(), "install_path": self.path_var.get()}

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            self.log(f"設定の保存に失敗: {e}")
        except Exception as e:
            self.log(f"予期しないエラーが発生しました: {e}")

    def load_config(self):
        """設定を読み込み"""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            if "github_url" in config:
                self.url_var.set(config["github_url"])
            if "install_path" in config:
                self.path_var.set(config["install_path"])

        except (OSError, IOError) as e:
            self.log(f"設定ファイルの読み込みに失敗: {e}")
        except json.JSONDecodeError as e:
            self.log(f"設定ファイルの形式が正しくありません: {e}")
        except Exception as e:
            self.log(f"予期しないエラーが発生しました: {e}")

    def on_closing(self):
        """ウィンドウが閉じられる時の処理"""
        self.save_config()
        self.root.destroy()

    def start_restore(self):
        """バックアップから復元開始"""
        install_path = self.path_var.get().strip()

        if not install_path:
            messagebox.showerror("エラー", "インストール先パスを入力してください")
            return

        # バックアップフォルダを検索
        backup_dirs = self.find_backup_dirs(install_path)

        if not backup_dirs:
            messagebox.showinfo("情報", "バックアップフォルダが見つかりません")
            return

        # バックアップ選択ダイアログ
        dialog = BackupSelectionDialog(self.root, backup_dirs)
        dialog.set_log_callback(self.log)
        backup_path = dialog.show()

        if not backup_path:
            return

        # 確認ダイアログ
        if not messagebox.askyesno(
            "確認",
            f"以下のバックアップから復元しますか？\n\n{backup_path}\n\n"
            f"現在のフォルダ: {install_path}\n\n"
            "現在のフォルダは上書きされます。",
        ):
            return

        # 復元実行
        self.restore_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_var.set("復元開始...")

        thread = threading.Thread(
            target=self.run_restore, args=(backup_path, install_path)
        )
        thread.daemon = True
        thread.start()

    def find_backup_dirs(self, install_path):
        """バックアップフォルダを検索"""
        # exeファイルと同じディレクトリのbackupsフォルダを検索
        # PyInstallerでパッケージ化された場合の対応
        if getattr(sys, 'frozen', False):
            # 実行ファイルの場合、実行ファイルと同じディレクトリにbackupsを作成
            base_path = Path(sys.executable).parent
        else:
            # 開発環境の場合
            base_path = Path(__file__).parent.parent
        
        backup_dir = base_path / "backups"

        if not backup_dir.exists():
            return []

        backup_dirs = []
        for item in backup_dir.iterdir():
            if item.is_dir() and item.name.startswith("tModLoader_backup_"):
                backup_dirs.append(item)

        # 自然ソートでソート（新しい順）
        backup_dirs.sort(key=lambda x: natural_sort_key(x.name), reverse=True)
        return backup_dirs

    def run_restore(self, backup_path, install_path):
        """バックアップから復元実行"""
        try:
            self.log("=== バックアップから復元開始 ===")
            self.log(f"復元元: {backup_path}")
            self.log(f"復元先: {install_path}")
            self._update_progress_async(ProgressStage.RESTORE_PREP, "復元準備中...")

            # 既存のインストール先を削除
            install_path = Path(install_path)
            if install_path.exists():
                self.log("既存のフォルダを削除中...")
                self._update_progress_async(
                    ProgressStage.RESTORE_DELETE, "既存フォルダ削除中..."
                )
                shutil.rmtree(install_path)

            # バックアップから復元
            self.log("バックアップから復元中...")
            self._update_progress_async(
                ProgressStage.RESTORE_COPY, "バックアップから復元中..."
            )
            shutil.copytree(backup_path, install_path)
            self._update_progress_async(ProgressStage.RESTORE_FINAL, "復元処理中...")

            self.log("=== 復元完了！ ===")

            # UI更新
            self._update_progress_async(ProgressStage.RESTORE_COMPLETE, "復元完了！")
            self.root.after(0, self.restore_complete)

        except Exception as e:
            self.log(f"復元エラー: {e}")
            self.root.after(0, self.restore_error)

    def restore_complete(self):
        """復元完了"""
        self.progress_bar["value"] = 100
        self.progress_var.set("復元完了！ (100%)")
        self.restore_button.config(state="normal")
        messagebox.showinfo("完了", "バックアップからの復元が正常に完了しました！")

    def restore_error(self):
        """復元エラー"""
        self.progress_bar["value"] = 0
        self.progress_var.set("復元エラー")
        self.restore_button.config(state="normal")
        messagebox.showerror(
            "エラー", "復元中にエラーが発生しました。ログを確認してください。"
        )

    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()
