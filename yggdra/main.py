import time
import sys
import os

sys.path.append(".")
# 确保能导入 core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import GameController
import config


class YggdraBot:
    def __init__(self):
        self.bot = GameController(
            config.WINDOW_TITLE, config.ASSETS_DIR, scale=config.SCALE, exact_match=True
        )
        self.bot.set_regions(config.REGIONS)

    def run(self):
        print(f"Bot started for {config.WINDOW_TITLE}. Press Ctrl+C to stop.")
        frame_count = 0
        try:
            while True:
                # --- 第一步：获取当前帧 (截图 1 次) ---
                screen = self.bot.capture_window()

                if screen is None:
                    time.sleep(5)  # 窗口可能没了，多等等
                    frame_count = 0
                    continue

                frame_count += 1
                results = self.bot.find_all(screen, config.BUTTONS, 0.3)

                # --- 第二步：逻辑判断链 (基于同一张截图查找多个目标) ---
                res = self.bot.find(screen, "battle_prepare.png")
                if res:
                    print(f"[逻辑] 发现战斗准备，点击开始")
                    self.bot.click(res)
                    continue

                # 下一章 (优先级低于战斗准备)
                res = self.bot.find(screen, "next_chapter.png")
                if res:
                    print(f"[逻辑] 发现下一章")
                    self.bot.click(res)
                    continue
                # 重复刷副本，再次战斗
                res = self.bot.find(screen, "battle_again.png")
                if res:
                    print(f"[逻辑] 再次战斗")
                    self.bot.click(res)
                    continue

                # 点击开始
                res = self.bot.find(screen, "battle_start.png")
                if res:
                    print(f"[逻辑] 战斗开始")
                    self.bot.click(res)
                    continue

                # 区域通关 (需要偏移点击)
                res = self.bot.find(screen, "area_clear.png")
                if res:
                    print(f"[逻辑] 区域通关，点击空白处关闭")
                    # 这里演示了如何只利用 find 的结果，自己决定怎么点
                    # 比如往上偏移 400 像素点击空白处
                    self.bot.click(res, offset=(0, -400))
                    continue

                # 新地图解锁 (需要偏移点击)
                res = self.bot.find(screen, "new_content.png")
                if res:
                    print(f"[逻辑] 区域通关，点击空白处关闭")
                    self.bot.click(res, offset=(0, -400))
                    continue

                # 位于关卡选择界面
                chapter_arrow = self.bot.find(screen, "chapter_arrow.png")
                if chapter_arrow:
                    # 战斗关卡选择，找头像
                    res = self.bot.find(screen, "body.png", 0.7)
                    if res:
                        print(f"[逻辑] 点击头像，进入新关卡")
                        self.bot.click(res)

                    # 战斗关卡选择，找五角星
                    res = self.bot.find(screen, "stars.png", 0.7)
                    if res:
                        print(f"[逻辑] 点击关卡，进入新关卡")
                        self.bot.click(res)
                    continue

                # 检测是否位于战斗场景
                wave = self.bot.find(screen, "wave.png")
                action_count = self.bot.find(screen, "action_count.png.png")

                if not (wave or action_count):
                    skip = self.bot.find(screen, "skip.png")
                    if skip:
                        print(f"[逻辑] 跳过剧情，点击跳过")
                        self.bot.click(skip)
                        continue
                    ok = self.bot.find(screen, "ok.png")
                    if ok:
                        print(f"[逻辑] 跳过剧情，点击好的")
                        self.bot.click(ok)
                        continue

                # --- 如果什么都没找到 ---
                # print("\r......", end="")
                time.sleep(1)  # 降低循环频率，省 CPU

        except KeyboardInterrupt:
            print("\nBot stopped.")


if __name__ == "__main__":
    game = YggdraBot()
    game.run()
