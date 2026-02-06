"""
Project: GameClicker
Created: 2026-02-06 12:06:51
Modified: 2026-02-06 12:06:51
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

# 游戏窗口标题
WINDOW_TITLE = "YGGDRA REFRAIN"

ASSETS_DIR = "assets/yggdra"

# 缩放倍率
SCALE = 0.8

# 匹配置信度阈值
CONFIDENCE = 0.9

# 待检查的图片列表
BUTTONS = [
    "battle_prepare.png",
    "next_chapter.png",
    "battle_start.png",
    "close.png",
    "battle_again.png",
    "back.png",
    "skip.png",
    "ok.png",
    "stars.png",
    "area_clear.png",
    "new_content.png",
    "click_close.png",
    "cancel.png",
    "action_count.png",
    "wave.png",
    "head.png",
    "body.png",
    "chapter_arrow.png",
    "change_team.png",
    "my_team.png",
    "award_text.png",
    "win.png",
]

CLICK_BUTTONS = [
    "battle_prepare.png",
    "next_chapter.png",
    "battle_start.png",
    "ok.png",
    "stars.png",
    # "action_count.png",
    # "wave.png",
    "head.png",
    "body.png",
    "area_clear.png",
    "new_content.png",
    "click_close.png",
    "skip.png",
    "battle_again.png",
    # "chapter_arrow.png",
    # "change_team.png",
    # "my_team.png",
    # "award_text.png",
    # "win.png",
]

# 窗口内相对区域配置 (x_offset, y_offset, width, height)
REGIONS = {
    "chapter_arrow.png": (52, 6, 429, 268),
    "head.png": (892, 754, 323, 320),
    "body.png": (175, 786, 301, 392),
    "stars.png": (1098, 898, 391, 263),
    "battle_prepare.png": (1355, 1207, 426, 268),
    "battle_start.png": (2044, 1319, 376, 322),
    "battle_again.png": (593, 1408, 415, 261),
    "my_team.png": (483, 1145, 393, 252),
    "change_team.png": (183, 14, 393, 256),
    "action_count.png": (1108, 0, 369, 243),
    "wave.png": (144, 2, 316, 234),
    "next_chapter.png": (1530, 1397, 496, 279),
    "win.png": (928, 62, 728, 409),
    "skip.png": (2174, 6, 311, 328),
    "ok.png": (1482, 867, 316, 267),
    "cancel.png": (798, 873, 312, 264),
    "area_clear.png": (784, 608, 1012, 347),
    "new_content.png": (1090, 568, 403, 250),
}
