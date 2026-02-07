"""
Project: core
Created: 2026-02-06 16:13:09
Modified: 2026-02-06 16:13:09
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

# core/controller.py
import pyautogui
import numpy as np
import cv2
import time
import os
import mss
from concurrent.futures import ThreadPoolExecutor, as_completed

# 只有当你确认需要 BitBlt 时才取消注释下面的导入，防止报错
try:
    import win32gui, win32ui, win32con

    HAS_BITBLT = True
except ImportError:
    HAS_BITBLT = False

from .window import WindowManager
from .vision import VisionEngine
from .helper import ScopeTimer
from .logger_config import info, debug, warn, error


class GameController:
    METHOD_MSS = "mss"
    METHOD_BITBLT = "bitblt"
    METHOD_PYAUTOGUI = "pyautogui"

    # 默认改回 mss，因为 BitBlt 可能有 30px 的标题栏偏差导致 Region 失效
    def __init__(
        self, window_title, assets_dir, scale=1.0, exact_match=False, method="mss"
    ):
        self.win_mgr = WindowManager(window_title, exact_match=exact_match)
        self.vision = VisionEngine(scale=scale)
        self.assets_dir = assets_dir
        self.regions = {}
        self.disable_click = False
        self.last_win_rect = None
        self.method = method
        self.sct = None
        if self.method == self.METHOD_MSS:
            self.sct = mss.mss()
        self.executor = ThreadPoolExecutor(max_workers=8)

    def __del__(self):
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)

    def set_regions(self, regions_dict):
        self.regions = regions_dict

    def set_disable_click(self, disable):
        self.disable_click = disable

    def set_capture_method(self, method):
        self.method = method
        if method == self.METHOD_MSS and self.sct is None:
            self.sct = mss.mss()

    def capture_window(self):
        if not self.win_mgr.update_rect():
            warn(f"Window not found: {self.win_mgr.title}")
            return None

        self.last_win_rect = self.win_mgr.get_rect()
        left, top, w, h = self.last_win_rect

        try:
            if self.method == self.METHOD_BITBLT and HAS_BITBLT:
                hwnd = self.win_mgr.get_hwnd()
                return self._capture_bitblt(hwnd, w, h)
            elif self.method == self.METHOD_MSS:
                return self._capture_mss(left, top, w, h)
            else:
                return self._capture_pyautogui(left, top, w, h)
        except Exception as e:
            error(f"Capture Error: {e}")
            return None

    def _capture_mss(self, left, top, w, h):
        monitor = {"top": top, "left": left, "width": w, "height": h}
        sct_img = self.sct.grab(monitor)
        img_np = np.array(sct_img)
        # MSS 返回 BGRA，OpenCV imread 是 BGR
        # 只要去掉 Alpha 通道，颜色就和原来一模一样了
        return img_np[:, :, :3]

    def _capture_pyautogui(self, left, top, w, h):
        screen_pil = pyautogui.screenshot(region=(left, top, w, h))
        # PyAutoGUI 返回 RGB，需要转 BGR
        return cv2.cvtColor(np.array(screen_pil), cv2.COLOR_RGB2BGR)

    def _capture_bitblt(self, hwnd, w, h):
        # ... (BitBlt 代码太长，保持你之前的实现即可) ...
        # 注意：BitBlt 截取的可能是“去头去尾”的内容，如果发现坐标对不上，
        # 请坚持使用 MSS。
        pass  # 这里省略具体实现，保持原样

    def find(self, screen_img, image_name, threshold=None, method="color"):
        """
        :param method: 匹配模式，默认 "color" (恢复了旧版行为)
        """
        if screen_img is None:
            return None

        rel_conf = self.regions.get(image_name)
        search_img = screen_img
        offset_x, offset_y = 0, 0

        if rel_conf:
            rx, ry, rw, rh = rel_conf
            sh, sw = screen_img.shape[:2]
            # 增加越界保护
            if rx + rw <= sw and ry + rh <= sh:
                search_img = screen_img[ry : ry + rh, rx : rx + rw]
                offset_x, offset_y = rx, ry
            else:
                # 只有调试时开启，防止刷屏
                # print(f"[Warn] Region mismatch for {image_name}. Capture size: {sw}x{sh}, Region end: {rx+rw}x{ry+rh}")
                pass

        tpl_path = os.path.join(self.assets_dir, image_name)
        with ScopeTimer(f"vision.load {image_name}", 0.5):
            template_img = self.vision.load_template(tpl_path)
        if template_img is None:
            return None

        original_conf = self.vision.confidence
        if threshold:
            self.vision.confidence = threshold

        # --- 关键修正：传入 method 参数 ---
        with ScopeTimer(f"vision.match {image_name}", 0.6):
            found, val, center, dims = self.vision.match(
                search_img, template_img, method=method
            )

        if threshold:
            self.vision.confidence = original_conf

        if found:
            # 1. 计算相对于窗口的坐标
            win_rel_x = center[0] + offset_x
            win_rel_y = center[1] + offset_y

            # 先初始化默认值为 0，防止 if 没进去导致报错
            abs_x, abs_y = 0, 0
            win_left, win_top = 0, 0

            # 只有获取到窗口位置时，才计算绝对坐标
            if self.last_win_rect:
                win_left, win_top, _, _ = self.last_win_rect
                abs_x = win_left + win_rel_x
                abs_y = win_top + win_rel_y

            debug(
                "Found %s %.2f (%d, %d)|(%d, %d)",
                image_name,
                val,
                win_rel_x,
                win_rel_y,
                abs_x,
                abs_y,
            )

            # 2. 自动生成建议 Region 逻辑
            if not rel_conf and val > 0.6:
                tpl_w, tpl_h = dims
                # 宽度和高度改为只增加 100
                suggest_w = tpl_w + 100
                suggest_h = tpl_h + 100

                # 计算左上角坐标：中心点 - (模板大小/2 + 50)
                # 这样正好能让 search_region 居中包裹住模板
                suggest_rel_x = max(0, win_rel_x - (tpl_w // 2 + 50))
                suggest_rel_y = max(0, win_rel_y - (tpl_h // 2 + 50))

                debug(f"[Region 建议] 图片: {image_name} | 置信度: {val:.2f}")
                # 打印顺序是 (x, y, w, h)
                info(
                    '"%s": (%d, %d, %d, %d),'
                    % (
                        image_name,
                        int(suggest_rel_x),
                        int(suggest_rel_y),
                        suggest_w,
                        suggest_h,
                    )
                )
                debug("-" * 30)

            # 3. 返回结构化对象 (现在的缩进确保了 abs_x/y 总是可访问的)
            return {"name": image_name, "pos": (abs_x, abs_y), "confidence": val}
        return None

    def find_all(self, screen_img, image_names, threshold=None, method="color"):
        """
        [感知] 并行查找，大幅提升批量识别速度
        """
        results = []
        if screen_img is None:
            return results

        # 使用线程池并发执行 find 任务
        # 我们把每个 find 任务提交给线程池
        futures = {
            self.executor.submit(self.find, screen_img, name, threshold, method): name
            for name in image_names
        }

        with ScopeTimer(f"find_all", 0.05):
            for future in as_completed(futures):
                try:
                    res = future.result()
                    if res:
                        results.append(res)
                except Exception as e:
                    name = futures[future]
                    error(f"[Thread Error] {name} matching failed: {e}")

        return results

    def find_best(self, screen_img, image_names, threshold=None, method="color"):
        """
        [感知] 并行查找，只返回置信度最高的那一个
        """
        # 复用已经多线程化的 find_all
        results = self.find_all(screen_img, image_names, threshold, method)
        if not results:
            return None
        return max(results, key=lambda x: x["confidence"])

    def click(self, target, offset=(0, 0)):
        """
        [动作] 点击目标
        :param target: 可以是 find() 返回的结果对象，或者是 assets_config 中的配置项(需包含 pos)
        """
        if not target:
            return

        pos = None
        log_name = "Unknown Target"

        # case 1: target 是 find/find_all 返回的结果字典 {'name':..., 'pos':...}
        if isinstance(target, dict):
            if "pos" in target:
                pos = target["pos"]
            # 尝试获取用于显示的名字
            if "alias" in target:  # 如果我们在 main 里注入了 alias
                log_name = target["alias"]
            elif "name" in target:  # 文件名
                log_name = target["name"]

        # case 2: target 是纯坐标
        elif isinstance(target, (tuple, list)):
            pos = target
            log_name = f"Pos{pos}"

        if not pos:
            return

        target_x = pos[0] + offset[0]
        target_y = pos[1] + offset[1]

        if self.disable_click:
            info(f"[DISABLED] Not Click -> {log_name}@({target_x}, {target_y})")
            return

        # 打印人性化日志
        info(f"[Click] {log_name}@({target_x}, {target_y})")
        pyautogui.moveTo(target_x, target_y, duration=0.1)
        pyautogui.click()
