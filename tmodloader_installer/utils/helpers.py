#!/usr/bin/env python3
"""
ヘルパー関数
"""

import re


def natural_sort_key(text):
    """自然ソート用のキー関数"""

    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    return [convert(c) for c in re.split("([0-9]+)", text)]
