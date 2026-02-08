"""
Project: core
Created: 2026-02-06 20:54:48
Modified: 2026-02-06 20:54:48
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

import time


class ScopeTimer:
    def __init__(self, name, threshold=0.01):
        """
        :param name: 计时块名称
        :param threshold: 只有超过这个时间(秒)才打印，防止刷屏
        """
        self.name = name
        self.threshold = threshold
        self.start = 0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cost = time.perf_counter() - self.start
        if cost > self.threshold:
            print(f"[Perf] {self.name}: {cost:.4f}s")
            pass
