#!/usr/bin/env python3
"""
バックアップ選択ダイアログ
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import shutil
from pathlib import Path
from tmodloader_installer.utils import natural_sort_key, BACKUP_DIALOG_SIZE


class BackupSelectionDialog:
    """バックアップ選択ダイアログ"""

    def __init__(self, parent, backup_dirs):
        """初期化"""
        self.parent = parent
        self.backup_dirs = backup_dirs
        self.selected_backup = None
        self.log_callback = None

    def set_log_callback(self, log_callback):
        """ログコールバックを設定"""
        self.log_callback = log_callback

    def log(self, message):
        """ログメッセージを出力"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def show(self):
        """ダイアログを表示"""
        # ダイアログウィンドウを作成
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("バックアップ選択")
        self.dialog.geometry(BACKUP_DIALOG_SIZE)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        self._setup_ui()
        self._populate_list()

        # ウィンドウが閉じられるまで待機
        self.dialog.wait_window()

        return self.selected_backup

    def _setup_ui(self):
        """UIをセットアップ"""
        # リストボックス
        list_frame = ttk.Frame(self.dialog, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(list_frame, text="復元するバックアップを選択してください:").pack(
            anchor=tk.W
        )

        self.listbox = tk.Listbox(list_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # ボタン
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="キャンセル", command=self._on_cancel).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="削除", command=self._on_delete).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

    def _populate_list(self):
        """リストを更新"""
        for backup_dir in self.backup_dirs:
            # 作成日時を表示
            mtime = datetime.datetime.fromtimestamp(backup_dir.stat().st_mtime)
            display_text = f"{backup_dir.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})"
            self.listbox.insert(tk.END, display_text)

    def _on_ok(self):
        """OKボタンの処理"""
        selection = self.listbox.curselection()
        if selection:
            self.selected_backup = self.backup_dirs[selection[0]]
        self.dialog.destroy()

    def _on_cancel(self):
        """キャンセルボタンの処理"""
        self.selected_backup = None
        self.dialog.destroy()

    def _on_delete(self):
        """削除ボタンの処理"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するバックアップを選択してください")
            return

        backup_to_delete = self.backup_dirs[selection[0]]
        backup_name = backup_to_delete.name

        # 確認ダイアログ
        if messagebox.askyesno(
            "確認",
            f"以下のバックアップを削除しますか？\n\n{backup_name}\n\n"
            "この操作は取り消せません。",
        ):
            try:
                shutil.rmtree(backup_to_delete)
                self.log(f"バックアップを削除しました: {backup_name}")

                # リストから削除
                self.listbox.delete(selection[0])
                self.backup_dirs.pop(selection[0])

                messagebox.showinfo("完了", "バックアップを削除しました")
            except Exception as e:
                self.log(f"バックアップの削除に失敗: {e}")
                messagebox.showerror(
                    "エラー", f"バックアップの削除に失敗しました:\n{e}"
                )
