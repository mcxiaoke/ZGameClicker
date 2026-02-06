'''
Project: GameClicker
Created: 2026-02-06 12:18:33
Modified: 2026-02-06 12:18:33
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
'''

import pygetwindow as gw
import pyautogui
import time
import os
import ctypes

# 确保坐标计算与缩放一致
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass

def get_relative_config(window_title):
    print(f"=== 坐标拾取助手 ===")
    print(f"目标窗口: {window_title}")
    print("-" * 30)
    print("操作指南:")
    print("1. 请确保游戏窗口处于【非最小化】状态。")
    print("2. 将鼠标移动到按钮的【中心】。")
    print("3. 按下 Ctrl + C 或等待倒计时，脚本会记录当前坐标。")
    print("-" * 30)

    try:
        while True:
            # 获取窗口实时位置
            wins = gw.getWindowsWithTitle(window_title)
            if not wins:
                print(f"\r未找到窗口 '{window_title}'...", end="")
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
            print(f"\r{status}  ", end="", flush=True)
            
            # 每隔 2 秒打印一次可以直接复制的配置格式
            time.sleep(2)
            print(f"\n\n[建议配置项] -> ({reg_x}, {reg_y}, 200, 200)")
            print(f"请检查按钮是否在上述范围中心，继续移动鼠标或 Ctrl+C 退出...")

    except KeyboardInterrupt:
        print("\n\n已停止记录。")

if __name__ == "__main__":
    # 这里填你 config.py 里的窗口标题
    TARGET_TITLE = "YGGDRA" 
    get_relative_config(TARGET_TITLE)