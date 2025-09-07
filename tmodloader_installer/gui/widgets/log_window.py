#!/usr/bin/env python3
"""
ログ表示ウィンドウ
"""

import tkinter as tk
from tkinter import ttk
from ...utils import LOG_WINDOW_SIZE


class LogWindow:
    """ログ表示ウィンドウ"""

    def __init__(self, parent, log_messages):
        """初期化"""
        self.parent = parent
        self.log_messages = log_messages
        self.window = None
        self.log_text = None

    def show(self):
        """ログウィンドウを表示"""
        # 既にログウィンドウが開いている場合はフォーカスを移す
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("ログ")
        self.window.geometry(LOG_WINDOW_SIZE)
        self.window.transient(self.parent)

        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        """UIをセットアップ"""
        # ログ表示フレーム
        log_frame = ttk.Frame(self.window, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        # ログテキスト
        self.log_text = tk.Text(log_frame, height=25, width=80, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ボタン
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="閉じる", command=self.close).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="クリア", command=self.clear).pack(
            side=tk.RIGHT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="更新", command=self._update_display).pack(
            side=tk.RIGHT, padx=(0, 10)
        )

    def _update_display(self):
        """ログ表示を更新"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
            for message in self.log_messages:
                self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)

    def clear(self):
        """ログをクリア"""
        self.log_messages.clear()
        if self.log_text:
            self.log_text.delete(1.0, tk.END)

    def close(self):
        """ログウィンドウを閉じる"""
        if self.window:
            self.window.destroy()
            self.window = None
