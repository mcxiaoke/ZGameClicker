"""
Project: GameClicker
Created: 2026-02-06 12:18:33
Modified: 2026-02-06 12:18:33
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

import pygetwindow as gw
import pyautogui
import time
import os
import ctypes
from core import log

# 确保坐标计算与缩放一致
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass


def get_relative_config(window_title):
    log.info("=== 坐标拾取助手 ===")
    log.info("目标窗口: %s", window_title)
    log.info("%s", "-" * 30)
    log.info("操作指南:")
    log.info("1. 请确保游戏窗口处于【非最小化】状态。")
    log.info("2. 将鼠标移动到按钮的【中心】。")
    log.info("3. 按下 Ctrl + C 或等待倒计时，脚本会记录当前坐标。")
    log.info("%s", "-" * 30)

    try:
        while True:
            # 获取窗口实时位置
            wins = gw.getWindowsWithTitle(window_title)
            if not wins:
                log.info("未找到窗口 '%s'...", window_title)
                time.sleep(1)
                continue

            win = wins[0]
            win_x, win_y = win.left, win.top

            # 获取鼠标当前绝对坐标
            abs_x, abs_y = pyautogui.position()

            # 计算相对偏移
            rel_x = abs_x - win_x
            rel_y = abs_y - win_y

            # 模拟生成一个 200x200 的 Region (让按钮处于 Region 中心)
            # 格式: (x_start, y_start, width, height)
            reg_x = rel_x - 100
            reg_y = rel_y - 100

            status = f"鼠标位置: ({abs_x}, {abs_y}) | 相对窗口: ({rel_x}, {rel_y})"
            log.info(status)

            # 每隔 2 秒打印一次可以直接复制的配置格式
            time.sleep(2)
            log.info("[建议配置项] -> (%d, %d, 200, 200)", reg_x, reg_y)
            log.info("请检查按钮是否在上述范围中心，继续移动鼠标或 Ctrl+C 退出...")

    except KeyboardInterrupt:
        log.info("\n\n已停止记录。")


if __name__ == "__main__":
    # 这里填你 config.py 里的窗口标题
    TARGET_TITLE = "YGGDRA"
    get_relative_config(TARGET_TITLE)
