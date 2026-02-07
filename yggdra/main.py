import time
import sys
import os
import argparse
from dataclasses import dataclass

sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import GameController
from assets_config import ASSETS
from core import log, setup_logger, enable_datetime
import core
import config


class YggdraBot:
    def __init__(self, opts: "CLIOptions"):
        self.opts = opts
        # dynamic setup: reconfigure logger according to CLI
        setup_logger(debug_mode=opts.debug_mode, show_datetime=opts.show_datetime)
        enable_datetime(opts.show_datetime)
        # update core DEBUG_MODE so other modules that import it read the intended value
        try:
            core.DEBUG_MODE = opts.debug_mode
        except Exception:
            pass

        self.bot = GameController(
            config.WINDOW_TITLE, config.ASSETS_DIR, scale=config.SCALE, exact_match=True
        )
        self.bot.set_regions(config.REGIONS)
        # 预加载所有要查找的文件名列表 (排除 404 的)
        self.targets = [k for k, v in ASSETS.items() if "(404)" not in v["desc"]]
        # for k, v in ASSETS.items():
        # log.debug("%s %s", k, v["name"])

    def maybe_click(self, target, offset=(0, 0)):
        if self.opts.disable_click:
            log.info("[DryRun] Not Click -> %s", getattr(target, "name", target))
            return
        self.bot.click(target, offset=offset)

    def run(self):
        log.info("Bot started for %s. Press Ctrl+C to stop.", config.WINDOW_TITLE)
        frame_count = 0
        try:
            while True:
                # 操作之间间隔时间，防止重复点击
                time.sleep(1)
                # --- 第一步：获取当前帧 (截图 1 次) ---
                screen = self.bot.capture_window()

                if screen is None:
                    time.sleep(5)  # 窗口可能没了，多等等
                    frame_count = 0
                    continue

                frame_count += 1
                log.debug("Frame #%d captured", frame_count)
                if core.DEBUG_MODE or 1 == 1:
                    results = self.bot.find_all(screen, self.targets, 0.5)

                # --------------------------------------------------
                # 1. 查找所有目标
                # results = self.bot.find_all(screen, self.targets)
                #
                # 2. 建立映射并注入配置信息
                # res_map = {}
                # for item in results:
                #     filename = item["name"]  # 这里的 name 是文件名
                #     asset = ASSETS.get(filename)
                #
                #     if asset:
                #         # [关键] 把配置里的中文 name 注入到结果对象里，供 controller 打印日志用
                #         item["alias"] = asset["name"]
                #         item["desc"] = asset["desc"]
                #         item["click_type"] = asset["click"]
                #         item["type"] = asset["type"]
                #
                #     res_map[filename] = item
                #
                # 3. 逻辑决策 (直接用 filename 做 key，方便索引)
                #
                # 示例：处理 "battle_prepare.png"
                # if "battle_prepare.png" in res_map:
                #     btn = res_map["battle_prepare.png"]
                #     # 日志会自动打印: [Action] Click -> Battle Prepare @ (x, y)
                #     self.bot.click(btn)
                #     continue
                #
                # 示例：通用处理所有类型为 'button' 的点击 (如果逻辑简单的话)
                # for fname, item in res_map.items():
                #     if item.get('type') == 'button' and item.get('click_type') == 'single':
                #          self.bot.click(item)
                #          break
                # --------------------------------------------------

                # 简化业务逻辑示例
                res1 = self.bot.find(screen, "battle_prepare.png")
                res2 = self.bot.find(screen, "battle_prepare2.png")
                if res1 or res2:
                    log.info("[逻辑] 发现战斗准备，点击开始")
                    self.maybe_click(res1 or res2)
                    continue

                res = self.bot.find(screen, "battle_start.png")
                if res:
                    log.info("[逻辑] 战斗开始")
                    self.maybe_click(res)
                    continue

                if not self.opts.disable_next:
                    res = self.bot.find(screen, "next_chapter.png")
                    if res:
                        log.info("[逻辑] 下一章")
                        self.maybe_click(res)
                        continue

                res = self.bot.find(screen, "battle_again.png")
                if res:
                    log.info("[逻辑] 再次战斗")
                    self.maybe_click(res)
                    continue

                res = self.bot.find(screen, "area_clear.png")
                if res:
                    log.info("[逻辑] 区域通关，点击空白处关闭")
                    self.maybe_click(res, offset=(0, -400))
                    continue

                res = self.bot.find(screen, "new_content.png")
                if res:
                    log.info("[逻辑] 新区域解锁，点击空白处关闭")
                    self.maybe_click(res, offset=(0, -400))
                    continue

                # 关卡选择，找头像或者五角星
                res = self.bot.find(screen, "body.png")
                if res:
                    log.info("[逻辑] 点击头像，进入新关卡")
                    self.maybe_click(res)
                    continue

                map_icon = self.bot.find(screen, "map_icon.png")
                chapter_arrow = self.bot.find(screen, "chapter_arrow.png")
                if chapter_arrow or map_icon:
                    res = self.bot.find(screen, "body.png", 0.7)
                    if res:
                        log.info("[逻辑] 点击头像，进入新关卡")
                        self.maybe_click(res)

                    res = self.bot.find(screen, "stars.png", 0.7)
                    if res:
                        log.info("[逻辑] 点击关卡，进入新关卡")
                        self.maybe_click(res)
                    continue

                # 剧情跳过，优先点击好的
                ok = self.bot.find(screen, "skip_confirm_ok.png")
                if ok:
                    log.info("[逻辑] 剧情跳过，点击好的")
                    self.maybe_click(ok)
                    continue

                # 确认按钮，好的
                ok = self.bot.find(screen, "ok.png")
                if ok:
                    log.info("[逻辑] 按钮，点击好的1")
                    self.maybe_click(ok)
                    continue

                ok = self.bot.find(screen, "ok2.png")
                if ok:
                    log.info("[逻辑] 按钮，点击好的2")
                    self.maybe_click(ok)
                    continue

                # 返回按钮
                back = self.bot.find(screen, "back.png")
                back2 = self.bot.find(screen, "back2.png")
                if back or back2:
                    log.info("[逻辑] 按钮，点击返回")
                    self.maybe_click(back or back2)
                    continue

                # 跳过剧情
                skip = self.bot.find(screen, "skip2.png")
                if skip:
                    log.info("[逻辑] SKIP按钮，跳过剧情")
                    self.maybe_click(skip)
                    continue

                # 事件界面，点击空白处关闭
                event = self.bot.find(screen, "event.png")
                if event:
                    log.info("[逻辑] 点击空白处关闭")
                    self.maybe_click(event, offset=(0, 100))
                    continue

                # 等级提升界面
                click_close = self.bot.find(screen, "click_close.png")
                if click_close:
                    log.info("[逻辑] 点击空白处关闭")
                    self.maybe_click(click_close, offset=(0, 100))
                    continue

                # 兑换界面，优先点击最大数量
                redeem_max = self.bot.find(screen, "label_max.png")
                button_redeem = self.bot.find(screen, "button_redeem.png")
                if redeem_max and button_redeem:
                    log.info("[逻辑] 兑换数目，点击最大")
                    self.maybe_click(redeem_max)
                    time.sleep(0.5)
                    log.info("[逻辑] 发现兑换按钮，点击兑换")
                    self.maybe_click(button_redeem)
                    continue

                # 点击屏幕关闭
                click_any = self.bot.find(screen, "click_any_position.png")
                if click_any:
                    log.info("[逻辑] 兑换完成，点击空白处关闭")
                    self.maybe_click(click_any)
                    continue

                # 成就界面全部领取
                claim_all = self.bot.find(screen, "claim_all.png")
                if claim_all:
                    log.info("[逻辑] 发现成就全部领取，点击领取")
                    self.maybe_click(claim_all)
                    continue

                # 装备强化界面，先点击选择，再点击强化，最后关闭界面
                equip_select = self.bot.find(screen, "equip_select.png")
                if equip_select:
                    log.info("[逻辑] 装备强化界面，自动选择")
                    self.maybe_click(equip_select)
                    time.sleep(0.5)
                    # 刷新截图，找强化按钮
                    screen = self.bot.capture_window()
                    equip_enforce = self.bot.find(screen, "equip_enforce.png")
                    if equip_enforce:
                        log.info("[逻辑] 装备强化界面，点击强化")
                        self.maybe_click(equip_enforce)
                    back = self.bot.find(screen, "back.png")
                    if back:
                        log.info("[逻辑] 装备强化界面，点击返回")
                        self.maybe_click(back)
                    time.sleep(0.5)
                    # 刷新截图，找关闭按钮
                    screen = self.bot.capture_window()
                    close = self.bot.find(screen, "close.png")
                    if close:
                        log.info("[逻辑] 装备强化界面，点击关闭")
                        self.maybe_click(close)
                    continue

        except KeyboardInterrupt:
            log.info("Bot stopped.")


def run():
    opts = parse_args(sys.argv[1:])
    log.info(opts)
    game = YggdraBot(opts)
    game.run()


@dataclass
class CLIOptions:
    disable_click: bool = False
    disable_next: bool = False
    debug_mode: bool = False
    show_datetime: bool = False


def parse_args(argv=None) -> CLIOptions:
    p = argparse.ArgumentParser(description="Run the Yggdra bot")
    p.add_argument(
        "--disable-click",
        action="store_true",
        help="Disable performing real clicks (dry-run)",
    )
    p.add_argument(
        "--disable-next",
        action="store_true",
        help="Disable auto next chapter",
    )
    p.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    p.add_argument(
        "--show-datetime", action="store_true", help="Include date/time in logs"
    )

    args, unknown = p.parse_known_args(argv)
    if unknown:
        try:
            log.debug("Ignoring unknown CLI args: %s", unknown)
        except Exception:
            pass
    return CLIOptions(
        disable_click=args.disable_click or args.debug,
        disable_next=args.disable_next,
        debug_mode=args.debug,
        show_datetime=args.show_datetime,
    )


if __name__ == "__main__":
    print("argv:", sys.argv)
    run()
