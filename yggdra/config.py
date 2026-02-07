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

# 窗口内相对区域配置 (x_offset, y_offset, width, height)
# 长宽各加200
REGIONS_OLD = {
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

# 长宽各加100
REGIONS = {
    "chapter_arrow.png": (102, 56, 329, 168),
    # 角色横向位置不固定，可移动，所以放宽限制
    "head.png": (225, 804, 1800, 220),
    "body.png": (225, 836, 1800, 292),
    "stars.png": (1148, 948, 291, 163),
    "battle_prepare.png": (1405, 1257, 326, 168),
    "battle_start.png": (2094, 1369, 276, 222),
    "battle_again.png": (643, 1458, 315, 161),
    "my_team.png": (533, 1195, 293, 152),
    "change_team.png": (233, 64, 293, 156),
    "action_count.png": (1158, 50, 269, 143),
    "wave.png": (194, 52, 216, 134),
    "next_chapter.png": (1580, 1447, 396, 179),
    "win.png": (978, 112, 628, 309),
    "skip.png": (2224, 56, 211, 228),
    "ok.png": (1532, 917, 216, 167),
    "close.png": (2028, 1262, 218, 164),
    "cancel.png": (848, 923, 212, 164),
    "award_text.png": (210, 1194, 344, 142),
    "area_clear.png": (834, 658, 912, 247),
    "new_content.png": (1140, 618, 303, 150),
    "button_redeem.png": (1178, 1099, 228, 174),
    "redeem_confirm.png": (1121, 378, 345, 168),
    "redeem_place.png": (113, 60, 365, 164),
    "label_max.png": (1630, 846, 212, 153),
}
