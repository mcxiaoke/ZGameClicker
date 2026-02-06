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

        try:
            while True:
                # --- 第一步：获取当前帧 (截图 1 次) ---
                screen = self.bot.capture_window()

                if screen is None:
                    time.sleep(5)  # 窗口可能没了，多等等
                    continue

                # --- 第二步：逻辑判断链 (基于同一张截图查找多个目标) ---

                # 场景 A: 战斗准备
                pos = self.bot.find(screen, "battle_prepare.png")
                if pos:
                    print(f"[逻辑] 发现战斗准备，点击开始")
                    self.bot.click(pos)
                    time.sleep(2)  # 动作后的硬直时间
                    continue  # 这一帧处理完了，重新截图

                # 场景 B: 下一章 (优先级低于战斗准备)
                pos = self.bot.find(screen, "next_chapter.png")
                if pos:
                    print(f"[逻辑] 发现下一章")
                    self.bot.click(pos)
                    time.sleep(1.5)
                    continue
                else:
                    # 重复刷副本，再次战斗
                    pos = self.bot.find(screen, "battle_again.png")
                    if pos:
                        print(f"[逻辑] 再次战斗")
                        self.bot.click(pos)
                        time.sleep(1.5)
                        continue
                # 点击开始
                pos = self.bot.find(screen, "battle_start.png")
                if pos:
                    print(f"[逻辑] 战斗开始")
                    self.bot.click(pos)
                    time.sleep(1)
                    continue

                # 场景 C: 区域通关 (需要偏移点击)
                pos = self.bot.find(screen, "area_clear.png")
                if pos:
                    print(f"[逻辑] 区域通关，点击空白处关闭")
                    # 这里演示了如何只利用 find 的结果，自己决定怎么点
                    # 比如往上偏移 400 像素点击空白处
                    self.bot.click(pos, offset=(0, -400))
                    time.sleep(1)
                    continue

                # 场景 D: 弹窗确认
                pos = self.bot.find(screen, "ok.png")
                if pos:
                    self.bot.click(pos)
                    time.sleep(1)
                    continue

                # 战斗关卡选择，找头像
                pos = self.bot.find(screen, "head.png")
                if pos:
                    self.bot.click(pos)
                    time.sleep(1)
                    continue

                # --- 如果什么都没找到 ---
                # print("\r......", end="")
                time.sleep(1)  # 降低循环频率，省 CPU

        except KeyboardInterrupt:
            print("\nBot stopped.")


if __name__ == "__main__":
    game = YggdraBot()
    game.run()
