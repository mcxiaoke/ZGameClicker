'''
Project: GameClicker
Created: 2026-02-06 12:06:51
Modified: 2026-02-06 12:06:51
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
'''

# 游戏窗口标题
WINDOW_TITLE = "YGGDRA"

# 缩放倍率
CURRENT_SCALE = 0.8

# 匹配置信度阈值
CONFIDENCE = 0.8

# 待检查的图片列表
BUTTONS = [
    "battle_prepare.png",
    "next_chapter.png",
    "battle_start.png",
    "close.png",
    "again.png",
    "back.png"
]

# 窗口内相对区域配置 (x_offset, y_offset, width, height)
SEARCH_REGIONS = {
    "battle_prepare.png": (1355, 1207, 426, 268),
    "next_chapter.png": (1530, 1397, 496, 279),
    "battle_start.png":(2044, 1319, 376, 322),
    "close.png": (1978, 1212, 318, 264),
    "again.png": (593, 1408, 415, 261),
    "back.png": (1134, 1408, 318, 266),
}