"""
Project: core
Created: 2026-02-06 16:13:09
Modified: 2026-02-06 16:13:09
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

# core/window.py
# core/window.py
import pygetwindow as gw
import ctypes
import psutil
from .logger_config import error, debug, warn


class WindowManager:
    def __init__(self, title, exact_match=False):
        self.title = title
        self.exact_match = exact_match
        self.rect = None
        self.hwnd = None  # 新增：存储窗口句柄

        self.BLACKLIST_PROCESSES = [
            "explorer.exe",
            "code.exe",
            "cmd.exe",
            "powershell.exe",
            "python.exe",
        ]

    def _get_process_name(self, hwnd):
        try:
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return psutil.Process(pid.value).name().lower()
        except:
            return ""

    def update_rect(self):
        try:
            wins = gw.getWindowsWithTitle(self.title)
            target_win = None

            for win in wins:
                if self.exact_match and win.title != self.title:
                    continue

                # 获取底层句柄 (pygetwindow 对象中通常存储在 _hWnd)
                current_hwnd = win._hWnd
                proc_name = self._get_process_name(current_hwnd)
                if proc_name in self.BLACKLIST_PROCESSES:
                    continue

                target_win = win
                break

            if target_win:
                if target_win.isMinimized:
                    warn(
                        f"[Window] Matched window is minimized: '{target_win.title}' - ignoring (not restoring automatically)"
                    )
                    self.rect = None
                    self.hwnd = None
                    return False

                self.rect = (
                    target_win.left,
                    target_win.top,
                    target_win.width,
                    target_win.height,
                )
                self.hwnd = target_win._hWnd  # 保存句柄
                return True

        except Exception as e:
            error(f"[Window] Error: {e}")

        self.rect = None
        self.hwnd = None
        warn(f"[Window] No window matched title='{self.title}'")
        return False

    def get_rect(self):
        if not self.rect:
            self.update_rect()
        return self.rect

    def get_hwnd(self):
        if not self.hwnd:
            self.update_rect()
        return self.hwnd
