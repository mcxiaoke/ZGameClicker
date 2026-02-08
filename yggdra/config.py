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
CONFIDENCE = 0.85

# 窗口内相对区域配置 (x_offset, y_offset, width, height)
# 长宽各加100
REGIONS = {
    "chapter_arrow.png": (102, 56, 329, 168),
    # 角色横向位置不固定，可移动，所以放宽限制
    "head_main.png": (200, 809, 2200, 220),
    # "head_main2.png": (936, 889, 223, 220),
    "body_main.png": (100, 819, 2200, 312),
    # "body_main2.png": (953, 899, 177, 312),
    "head2.png": (296, 907, 2100, 164),
    "body2.png": (289, 901, 2100, 224),
    "stars.png": (1148, 948, 291, 163),
    "battle_prepare.png": (1405, 1257, 326, 168),
    "battle_prepare2.png": (1975, 1223, 324, 157),
    "battle_start.png": (2094, 1369, 276, 222),
    "battle_again.png": (643, 1458, 315, 161),
    "battle_again2.png": (875, 1413, 315, 161),
    "battle_info.png": (1136, 180, 316, 165),
    "my_team.png": (533, 1195, 293, 152),
    "change_team.png": (233, 64, 293, 156),
    "action_count.png": (1158, 50, 269, 143),
    "wave.png": (194, 52, 216, 134),
    "next_chapter.png": (1580, 1447, 396, 179),
    "win.png": (978, 112, 628, 309),
    "win2.png": (980, 190, 624, 301),
    "skip.png": (2224, 56, 211, 228),
    "skip2.png": (2242, 71, 177, 156),
    # ok may in many places, so no restrict
    # "ok.png": (1532, 917, 216, 167),
    "ok2.png": (1184, 1328, 216, 160),
    "sure.png": (1186, 1296, 212, 152),
    # close may in many places, so no restrict
    # "close.png": (2028, 1262, 218, 164),
    "back3.png": (1417, 1413, 216, 164),
    "back2.png": (1181, 1458, 216, 164),
    "cancel.png": (848, 923, 212, 164),
    "award_text.png": (210, 1194, 344, 142),
    "area_clear.png": (834, 658, 912, 247),
    "new_content.png": (1140, 618, 303, 150),
    "button_redeem.png": (1178, 1099, 228, 174),
    "redeem_confirm.png": (1121, 378, 345, 168),
    "redeem_place.png": (113, 60, 365, 164),
    "label_max.png": (1630, 846, 212, 153),
    "equip_enforce.png": (2032, 1426, 220, 164),
    "equip_select.png": (291, 1420, 321, 161),
    "map_icon.png": (2204, 318, 204, 260),
    "claim_all.png": (2151, 1176, 296, 152),
    "skip_confirm_title.png": (1119, 397, 340, 160),
    "skip_confirm_text.png": (1055, 961, 436, 152),
    "skip_confirm_ok.png": (1595, 1099, 209, 156),
    "stage_reward.png": (708, 730, 241, 136),
    "stage_extra_reward.png": (710, 969, 241, 140),
}
