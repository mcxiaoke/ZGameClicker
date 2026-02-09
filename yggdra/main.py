import time
import sys
import os
import argparse
from dataclasses import dataclass

sys.path.append(".")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import GameController
from assets_config import ASSETS
from core import log, setup_logger
import core
import config


def item_to_str(item):
    if not item:
        return "None"
    asset = item.get("asset", {})
    name = item.get("name", "Unknown")
    confidence = item.get("confidence", 0)
    return f"{name} {confidence:.2f}|{item.get('pos')}"


class YggdraBot:
    def __init__(self, opts: "CLIOptions"):
        self.opts = opts
        self.bot = GameController(
            config.WINDOW_TITLE, config.ASSETS_DIR, scale=config.SCALE, exact_match=True
        )
        self.bot.set_regions(config.REGIONS)
        self.bot.set_disable_click(opts.disable_click)
        # 预加载所有要查找的文件名列表 (排除 404 的)
        self.targets = [k for k, v in ASSETS.items() if "404" not in v["desc"]]
        # for k, v in ASSETS.items():
        # log.debug("%s %s", k, v["name"])

    def maybe_click(self, target, offset=(0, 0)):
        self.bot.click(target, offset=offset)

    def _capture_and_build_res_map(self):
        """Capture the window, run find_all once and build res_map.
        Returns tuple: (screen, res_map, results)
        需要保存两种，用 0.6 的阈值找到更多候选项，供后续逻辑选择；
        同时也用 0.85 的阈值找到更准确的结果，供直接点击使用。
        TODO
        """
        screen = self.bot.capture_window()
        if screen is None:
            return screen, [], {}

        all_results = self.bot.find_all(screen, self.targets, 0.6)
        results = [
            r for r in all_results if r.get("confidence", 0) >= config.CONFIDENCE
        ]
        # item: {"name": image_name, "pos": (abs_x, abs_y), "confidence": val}
        res_map = {}
        for item in results:
            filename = item.get("name")
            asset = ASSETS.get(filename)
            if asset:
                item["asset"] = asset
            res_map[filename] = item
        return screen, res_map, results

    def run(self):
        log.info("Bot started for %s. Press Ctrl+C to stop.", config.WINDOW_TITLE)
        frame_count = 0
        battle_count = 0
        battle_last_at = 0
        try:
            while True:
                # 操作之间间隔时间，防止重复点击
                time.sleep(1)
                # 一次性批量查找所有目标并构建索引表
                screen, res_map, results = self._capture_and_build_res_map()
                if screen is None:
                    time.sleep(5)  # 窗口可能没了，多等等
                    frame_count = 0
                    continue

                frame_count += 1
                log.debug("Frame #%d captured", frame_count)

                # 战斗界面，跳过其它检测
                wave = res_map.get("wave.png")
                action_count = res_map.get("action_count.png")
                if wave and action_count:
                    log.debug("[UI] 战斗中，跳过其它检测")
                    time.sleep(1)
                    continue

                # 简化业务逻辑示例
                auto_team = res_map.get("auto_team.png")
                if auto_team:
                    log.info("[逻辑] 自动组队 %s", item_to_str(auto_team))
                    self.maybe_click(auto_team)
                    time.sleep(0.5)  # 等界面切换
                    # 不跳过，继续下面的逻辑

                # 关卡信息界面
                battle_info = res_map.get("award_text.png") and res_map.get(
                    "team_power.png"
                )
                if battle_info:
                    # 战斗快速开始，固定队伍
                    battle_quick = res_map.get("battle_start_quick.png")
                    if battle_quick:
                        log.info("[逻辑] 战斗快速开始 %s", item_to_str(battle_quick))
                        self.maybe_click(battle_quick)
                        continue
                    # 点击准备画面
                    battle_prepare = res_map.get("battle_prepare.png") or res_map.get(
                        "battle_prepare2.png"
                    )
                    if battle_prepare:
                        log.info("[逻辑] 战斗准备 %s", item_to_str(battle_prepare))
                        self.maybe_click(battle_prepare)
                        continue

                battle_start = res_map.get("battle_start.png")
                if battle_start:
                    battle_count += 1
                    log.info(
                        "[逻辑] 战斗开始[%03d] %s",
                        battle_count,
                        item_to_str(battle_start),
                    )
                    self.maybe_click(battle_start)
                    continue

                # 关卡通关界面
                battle_win = res_map.get("win.png")
                if battle_win:
                    if not res_map.get("stage_reward.png"):
                        # 通关界面正在显示动画
                        self.bot.click(target=(1200, 1400))
                        continue
                    current_time = time.time()
                    elapsed = (
                        (current_time - battle_last_at) if battle_last_at > 0 else 0
                    )
                    battle_last_at = current_time
                    log.info(f"[UI] 关卡通关界面 通关时间={round(elapsed)}秒")
                    if not self.opts.disable_next:
                        res = res_map.get("next_chapter.png")
                        if res:
                            log.info("[逻辑] 下一章 %s", item_to_str(res))
                            self.maybe_click(res)
                            continue
                    battle_again = res_map.get("battle_again.png") or res_map.get(
                        "battle_again2.png"
                    )
                    if battle_again:
                        log.info("[逻辑] 再次战斗 %s", item_to_str(battle_again))
                        self.maybe_click(battle_again)
                        continue

                area_clear = res_map.get("area_clear.png")
                if area_clear:
                    log.info("[逻辑] 区域通关 %s", item_to_str(area_clear))
                    self.maybe_click(area_clear, offset=(0, -400))
                    continue

                res = res_map.get("new_content.png")
                if res:
                    log.info("[逻辑] 新区域解锁 %s", item_to_str(res))
                    self.maybe_click(res, offset=(0, -400))
                    continue

                # 关卡选择界面
                chapter_select = res_map.get("map_icon.png") or res_map.get(
                    "chapter_arrow.png"
                )
                if chapter_select:
                    # 选择置信度最高的头像候选
                    avatar_candidates = [
                        res_map.get(n)
                        for n in [
                            "body_main.png",
                            "body_main2.png",
                            "head_main.png",
                            "head_main2.png",
                            "head2.png",
                            "body2.png",
                        ]
                        if res_map.get(n)
                    ]
                    avatar = (
                        max(avatar_candidates, key=lambda x: x.get("confidence", 0))
                        if avatar_candidates
                        else None
                    )
                    if avatar:
                        log.info("[UI] 关卡选择界面")
                        log.info(
                            "[逻辑] 进入关卡 %s",
                            item_to_str(avatar),
                        )
                        self.maybe_click(avatar)
                        continue

                sure = res_map.get("sure.png")
                if sure:
                    log.info("[逻辑] 点击确定 %s", item_to_str(sure))
                    self.maybe_click(sure)
                    continue

                # 确认按钮，好的
                ok = res_map.get("ok.png") or res_map.get("ok2.png")
                if ok:
                    log.info("[逻辑] 点击好的 %s", item_to_str(ok))
                    self.maybe_click(ok)
                    continue

                # 返回按钮
                back = res_map.get("back.png") or res_map.get("back2.png")
                if back:
                    log.info("[逻辑] 点击返回 %s", item_to_str(back))
                    self.maybe_click(back)
                    continue

                # 剧情跳过，优先点击好的
                confirm = res_map.get("skip_confirm_ok.png")
                if confirm:
                    log.info("[逻辑] 剧情跳过，好的 %s", item_to_str(confirm))
                    self.maybe_click(confirm)
                    continue

                # 跳过剧情
                skip = res_map.get("skip2.png")
                if skip:
                    log.info("[逻辑] 跳过剧情 %s", item_to_str(skip))
                    self.maybe_click(skip)
                    continue

                # 事件界面，点击空白处关闭
                event = res_map.get("event.png")
                if event:
                    log.info("[逻辑] 事件，点击关闭 %s", item_to_str(event))
                    self.maybe_click(event, offset=(0, 100))
                    continue

                # 等级提升界面
                click_close = res_map.get("click_close.png")
                if click_close:
                    log.info("[逻辑] 点击空白处关闭 %s", item_to_str(click_close))
                    self.maybe_click(click_close, offset=(0, 100))
                    continue

                # 点击屏幕关闭
                click_any = res_map.get("click_any_position.png")
                if click_any:
                    log.info("[逻辑] 点击屏幕关闭 %s", item_to_str(click_any))
                    self.maybe_click(click_any)
                    continue

                # 成就界面全部领取
                claim_all = res_map.get("claim_all.png")
                if claim_all:
                    log.info("[逻辑] 全部领取 %s", item_to_str(claim_all))
                    self.maybe_click(claim_all)
                    continue

        except KeyboardInterrupt:
            log.info("Bot stopped.")


def run():
    opts = parse_args(sys.argv[1:])
    core.DEBUG_MODE = opts.debug_mode or False
    setup_logger(debug_mode=opts.debug_mode)
    log.info(opts)
    game = YggdraBot(opts)
    game.run()


@dataclass
class CLIOptions:
    disable_click: bool = False
    disable_next: bool = False
    debug_mode: bool = False


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
    )


if __name__ == "__main__":
    print("argv:", sys.argv)
    run()
