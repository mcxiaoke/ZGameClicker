'''
Project: core
Created: 2026-02-06 16:12:53
Modified: 2026-02-06 16:12:53
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
'''

# core/__init__.py
import ctypes

# 全局 DPI 适配，防止坐标偏移
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass