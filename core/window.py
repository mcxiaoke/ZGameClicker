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


class WindowManager:
    def __init__(self, title, exact_match=False):
        self.title = title
        self.exact_match = exact_match
        self.rect = None

        # --- 进程黑名单 ---
        # 只要窗口属于这些程序，直接跳过
        self.BLACKLIST_PROCESSES = [
            "explorer.exe",  # 资源管理器 (罪魁祸首)
            "code.exe",  # VS Code
            "pycharm64.exe",  # PyCharm
            "cmd.exe",  # 命令行
            "powershell.exe",  # PowerShell
            "python.exe",  # 脚本自己
        ]

    def _get_process_name(self, hwnd):
        """
        通过窗口句柄 (HWND) 获取 .exe 文件名
        """
        try:
            # 1. 获取窗口的 PID (Process ID)
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            # 2. 通过 PID 获取进程名
            process = psutil.Process(pid.value)
            return process.name().lower()  # 返回如 'explorer.exe'
        except Exception:
            return ""

    def update_rect(self):
        try:
            # 获取所有标题包含关键字的窗口
            wins = gw.getWindowsWithTitle(self.title)

            target_win = None

            for win in wins:
                # 1. 标题检查
                if self.exact_match and win.title != self.title:
                    continue

                # 2. 进程检查 (核心逻辑)
                # win._hWnd 是 pygetwindow 暴露的底层句柄
                proc_name = self._get_process_name(win._hWnd)

                # [Debug] 看看找到了什么妖魔鬼怪
                # print(f"Checking: '{win.title}' | Process: {proc_name}")

                if proc_name in self.BLACKLIST_PROCESSES:
                    # 即使标题一模一样，如果是 explorer.exe 也不要
                    continue

                # 找到了真正的游戏窗口
                target_win = win
                break

            if target_win:
                if target_win.isMinimized:
                    target_win.restore()
                self.rect = (
                    target_win.left,
                    target_win.top,
                    target_win.width,
                    target_win.height,
                )
                return True

        except Exception as e:
            print(f"[Window] Error: {e}")

        self.rect = None
        return False

    def get_rect(self):
        if not self.rect:
            self.update_rect()
        return self.rect
