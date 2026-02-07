"""
Project: core
Created: 2026-02-06 16:12:53
Modified: 2026-02-06 16:12:53
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

# core/__init__.py
import ctypes
import sys
from .logger_config import (
    setup_logger,
    log,
    debug,
    info,
    warn,
    error,
    critical,
    enable_datetime,
    SHOW_DATETIME,
)

# 全局 DPI 适配，防止坐标偏移
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception as e:
        warn(f"Failed to set DPI awareness: {e}")

# 从命令行参数识别 debug 模式（支持 --debug / -d）
DEBUG_MODE = "--debug" in sys.argv or "-d" in sys.argv
# 初始化日志
setup_logger(debug_mode=DEBUG_MODE)

# 导出核心模块
from .window import WindowManager
from .vision import VisionEngine
from .controller import GameController

__all__ = [
    "WindowManager",
    "VisionEngine",
    "GameController",
    "log",
    "debug",
    "info",
    "warn",
    "error",
    "critical",
    "DEBUG_MODE",
]
