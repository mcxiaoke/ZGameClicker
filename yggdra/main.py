import time
import sys
import os

sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import GameController
from assets_config import ASSETS
from core import DEBUG_MODE, log
import config

# 全局开关：是否实际执行点击操作，True 则只打印日志不点击
DISABLE_CLICK = False
# 全局开关：是否禁用点击下一章，True 则检测到下一章时只打印日志不点击
DISABLE_NEXT_CHAPTER = False


class YggdraBot:
    def __init__(self):
        self.bot = GameController(
            config.WINDOW_TITLE, config.ASSETS_DIR, scale=config.SCALE, exact_match=True
        )
        self.bot.set_regions(config.REGIONS)
        if DISABLE_CLICK or DEBUG_MODE:
            self.bot.set_disable_click(True)
            log.info("DISABLE_CLICK is ON: No actual clicks will be performed.")
        # 预加载所有要查找的文件名列表 (排除 404 的)
        self.targets = [k for k, v in ASSETS.items() if "(404)" not in v["desc"]]

    def run(self):
        log.info("Bot started for %s. Press Ctrl+C to stop.", config.WINDOW_TITLE)
        if DEBUG_MODE:
            log.info("Running in DEBUG MODE. No actual clicks will be performed.")
        frame_count = 0
        try:
            while True:
                # 操作之间间隔时间，防止重复点击
                time.sleep(1.5)
                # --- 第一步：获取当前帧 (截图 1 次) ---
                screen = self.bot.capture_window()

                if screen is None:
                    time.sleep(5)  # 窗口可能没了，多等等
                    frame_count = 0
                    continue

                frame_count += 1
                if DEBUG_MODE:
                    results = self.bot.find_all(screen, self.targets, 0.5)
                    for r in results:
                        log.debug("FOUND %s %.2f", r["name"], r["confidence"])

                # 1. 查找所有目标
                # results = self.bot.find_all(screen, self.targets)

                # 2. 建立映射并注入配置信息
                # res_map = {}
                # for item in results:
                #     filename = item["name"]  # 这里的 name 是文件名
                #     asset = ASSETS.get(filename)

                #     if asset:
                #         # [关键] 把配置里的中文 name 注入到结果对象里，供 controller 打印日志用
                #         item["alias"] = asset["name"]
                #         item["desc"] = asset["desc"]
                #         item["click_type"] = asset["click"]
                #         item["type"] = asset["type"]

                #     res_map[filename] = item

                # 3. 逻辑决策 (直接用 filename 做 key，方便索引)

                # 示例：处理 "battle_prepare.png"
                # if "battle_prepare.png" in res_map:
                #     btn = res_map["battle_prepare.png"]
                #     # 日志会自动打印: [Action] Click -> Battle Prepare @ (x, y)
                #     self.bot.click(btn)
                #     continue

                # 示例：通用处理所有类型为 'button' 的点击 (如果逻辑简单的话)
                # for fname, item in res_map.items():
                #     if item.get('type') == 'button' and item.get('click_type') == 'single':
                #          self.bot.click(item)
                #          break

                res = self.bot.find(screen, "battle_prepare.png")
                if res:
                    log.info("[逻辑] 发现战斗准备，点击开始")
                    self.bot.click(res)
                    continue

                # 点击开始
                res = self.bot.find(screen, "battle_start.png")
                if res:
                    log.info("[逻辑] 战斗开始")
                    self.bot.click(res)
                    continue

                if not DISABLE_NEXT_CHAPTER:
                    # 下一章 (优先级低于战斗准备)
                    res = self.bot.find(screen, "next_chapter.png")
                    if res:
                        log.info("[逻辑] 发现下一章")
                        self.bot.click(res)
                        continue
                # 重复刷副本，再次战斗
                res = self.bot.find(screen, "battle_again.png")
                if res:
                    log.info("[逻辑] 再次战斗")
                    self.bot.click(res)
                    continue

                # 区域通关 (需要偏移点击)
                res = self.bot.find(screen, "area_clear.png")
                if res:
                    log.info("[逻辑] 区域通关，点击空白处关闭")
                    # 这里演示了如何只利用 find 的结果，自己决定怎么点
                    # 比如往上偏移 400 像素点击空白处
                    self.bot.click(res, offset=(0, -400))
                    continue

                # 新地图解锁 (需要偏移点击)
                res = self.bot.find(screen, "new_content.png")
                if res:
                    log.info("[逻辑] 区域通关，点击空白处关闭")
                    self.bot.click(res, offset=(0, -400))
                    continue

                # 兑换界面，优先点击最大数量
                redeem_max = self.bot.find(screen, "label_max.png")
                button_redeem = self.bot.find(screen, "button_redeem.png")
                if redeem_max and button_redeem:
                    log.info("[逻辑] 兑换数目，点击最大")
                    self.bot.click(redeem_max)
                    time.sleep(0.5)
                    log.info("[逻辑] 发现兑换按钮，点击兑换")
                    self.bot.click(button_redeem)
                    continue

                click_any = self.bot.find(screen, "click_any_position.png")
                if click_any:
                    log.info("[逻辑] 兑换完成，点击空白处关闭")
                    self.bot.click(click_any)

                # 位于关卡选择界面
                chapter_arrow = self.bot.find(screen, "chapter_arrow.png")
                if chapter_arrow:
                    # 战斗关卡选择，找头像
                    res = self.bot.find(screen, "body.png", 0.7)
                    if res:
                        log.info("[逻辑] 点击头像，进入新关卡")
                        self.bot.click(res)

                    # 战斗关卡选择，找五角星
                    res = self.bot.find(screen, "stars.png", 0.7)
                    if res:
                        log.info("[逻辑] 点击关卡，进入新关卡")
                        self.bot.click(res)
                    continue

                # 检测是否位于战斗场景
                wave = self.bot.find(screen, "wave.png")
                action_count = self.bot.find(screen, "action_count.png.png")

                if not (wave or action_count):
                    ok = self.bot.find(screen, "ok.png")
                    if ok:
                        log.info("[逻辑] 跳过剧情，点击好的")
                        self.bot.click(ok)
                        continue
                    skip = self.bot.find(screen, "skip.png")
                    if skip:
                        log.info("[逻辑] 跳过剧情，点击跳过")
                        self.bot.click(skip)
                        continue

                # --- 如果什么都没找到 ---
                # print("\r......", end="")

        except KeyboardInterrupt:
            log.info("Bot stopped.")


def run():
    game = YggdraBot()
    game.run()


if __name__ == "__main__":
    # --click --no-click
    # --next --no-next
    # --debug --no-debug
    args = sys.argv[1:]
    if "--no-click" in args:
        DISABLE_CLICK = True
        log.info("DISABLE_CLICK is ON: No actual clicks will be performed.")
    if "--no-next" in args:
        DISABLE_NEXT_CHAPTER = True
        log.info("DISABLE_NEXT_CHAPTER is ON: Next chapter will not be clicked.")
    if "--debug" in args:
        DEBUG_MODE = True
        log.info("DEBUG_MODE is ON: Running in debug mode with extra logs.")
    if "--no-debug" in args:
        DEBUG_MODE = False
        log.info("DEBUG_MODE is OFF: Running in normal mode.")
    run()
