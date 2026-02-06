import pyautogui
import numpy as np
import cv2
import time
import os
import random
from .window import WindowManager
from .vision import VisionEngine


class GameController:
    def __init__(self, window_title, assets_dir, scale=1.0, exact_match=False):
        self.win_mgr = WindowManager(window_title, exact_match=exact_match)
        self.vision = VisionEngine(scale=scale)
        self.assets_dir = assets_dir
        self.regions = {}
        # 缓存当前的窗口位置，用于计算绝对坐标
        self.last_win_rect = None

    def set_regions(self, regions_dict):
        self.regions = regions_dict

    def capture_window(self):
        """
        [动作] 截取当前游戏窗口
        :return: (screen_img, win_rect) 返回 opencv 图片和当时的窗口位置
        """
        # 1. 获取最新窗口位置
        if not self.win_mgr.update_rect():
            print(f"\r[Error] Window '{self.win_mgr.title}' not found!")
            return None

        self.last_win_rect = self.win_mgr.get_rect()
        left, top, w, h = self.last_win_rect

        # 2. 截图
        try:
            # 截取整个游戏窗口
            screen = pyautogui.screenshot(region=(left, top, w, h))
            screen_img = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            return screen_img
        except Exception as e:
            print(f"[Controller] Capture failed: {e}")
            return None

    def find(self, screen_img, image_name, threshold=None):
        """
        [感知] 在给定的截图中寻找目标
        :param screen_img: capture_window 返回的图片
        :param image_name: assets 下的文件名
        :return: (x, y) 屏幕绝对坐标中心点，如果没找到返回 None
        """
        if screen_img is None:
            return None

        # 1. 确定搜索区域 (相对于窗口截图的左上角)
        # screen_img 本身就是窗口的全图，所以 (0,0) 就是窗口左上角
        rel_conf = self.regions.get(image_name)

        search_img = screen_img  # 默认搜全图
        offset_x, offset_y = 0, 0  # 裁剪带来的偏移量

        if rel_conf:
            # rel_conf: (x, y, w, h)
            rx, ry, rw, rh = rel_conf
            # 安全检查：防止 region 超出截图范围
            sh, sw = screen_img.shape[:2]
            if rx + rw <= sw and ry + rh <= sh:
                # 裁剪图片: [y:y+h, x:x+w]
                search_img = screen_img[ry : ry + rh, rx : rx + rw]
                offset_x, offset_y = rx, ry
            else:
                test = 1
                # 如果 Region 配置错误，降级为全图搜索
                # print("--")
                # print(f"[Warn] Region for {image_name} out of bounds, please remove region.")

        # 2. 加载模板
        tpl_path = os.path.join(self.assets_dir, image_name)
        template_img = self.vision.load_template(tpl_path)
        if template_img is None:
            return None

        # 3. 视觉匹配
        # 如果调用时传入了特定的 threshold 则使用，否则用 vision 默认的
        original_conf = self.vision.confidence
        if threshold:
            self.vision.confidence = threshold

        found, val, center, dims = self.vision.match(search_img, template_img)

        # 恢复默认置信度
        if threshold:
            self.vision.confidence = original_conf

        if found:
            # center 是相对于 search_img (裁剪后) 的坐标
            # 1. 转为相对于 窗口 (screen_img) 的坐标
            win_rel_x = center[0] + offset_x
            win_rel_y = center[1] + offset_y

            # 2. 转为 屏幕绝对坐标 (Absolute Screen Coordinates)
            if self.last_win_rect:
                win_left, win_top, _, _ = self.last_win_rect
                abs_x = win_left + win_rel_x
                abs_y = win_top + win_rel_y

                # (可选) 打印调试信息，去掉注释可看
                # print(f"[Found] {image_name} ({val:.2f}) -> Pos({abs_x}, {abs_y})")
                return (abs_x, abs_y)

        return None

    def click(self, pos, offset=(0, 0)):
        """
        [动作] 点击指定坐标
        :param pos: (x, y) 绝对坐标，通常由 find 返回
        :param offset: (x, y) 额外的偏移量，比如 (0, -400)
        """
        if not pos:
            return

        target_x = pos[0] + offset[0]
        target_y = pos[1] + offset[1]

        # 简单的防检测：稍微随机一点点位置（可选）
        target_x += random.randint(-5, 5)
        target_y += random.randint(-5, 5)

        pyautogui.moveTo(target_x, target_y, duration=0.1)  # 稍微快一点
        pyautogui.click()
        print(f"[Click] -> ({target_x}, {target_y})")
