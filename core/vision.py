"""
Project: core
Created: 2026-02-06 16:13:33
Modified: 2026-02-06 16:13:33
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

# core/vision.py
import cv2
import numpy as np
import os


class VisionEngine:
    def __init__(self, scale=1.0, confidence=0.8):
        self.scale = scale
        self.confidence = confidence
        self.cache = {}

    def load_template(self, path):
        """加载模板（带缓存机制）"""
        # 1. 如果缓存里有，直接返回（极速）
        if path in self.cache:
            return self.cache[path]

        # 2. 如果文件不存在，返回 None
        if not os.path.exists(path):
            # print(f"[Vision] Warn: File not found {path}")
            return None

        # 3. 第一次读取：从硬盘加载 (慢)
        img = cv2.imread(path)
        if img is None:
            return None

        # 4. 缩放处理
        if self.scale != 1.0:
            w = int(img.shape[1] * self.scale)
            h = int(img.shape[0] * self.scale)
            img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)

        # 5. 存入缓存
        self.cache[path] = img
        return img

    def match(self, screen_img, template_img, method="color"):
        """
        核心匹配逻辑
        :param method: "color" (默认, 原汁原味), "gray" (灰度增强), "edge" (边缘检测)
        """
        # 1. 根据模式进行预处理
        if method == "edge":
            # Canny 边缘检测 (适合扁平化/黑白按钮)
            s_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
            t_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
            s_blur = cv2.GaussianBlur(s_gray, (3, 3), 0)
            t_blur = cv2.GaussianBlur(t_gray, (3, 3), 0)
            p_screen = cv2.Canny(s_blur, 50, 150)
            p_template = cv2.Canny(t_blur, 50, 150)

        elif method == "gray":
            # 灰度 + 对比度增强 (适合受光照影响的按钮)
            s_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
            t_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
            p_screen = cv2.convertScaleAbs(s_gray, alpha=1.2, beta=0)
            p_template = cv2.convertScaleAbs(t_gray, alpha=1.2, beta=0)

        else:
            # [默认] 彩色匹配 (最稳，兼容旧代码逻辑)
            p_screen = screen_img
            p_template = template_img

        # 2. 尺寸检查
        th, tw = p_template.shape[:2]
        sh, sw = p_screen.shape[:2]

        # 只有当搜索区域特别大（比如宽度大于 500）时才报警
        if sw > 500 or sh > 500:
            pass
            # print(f"[Warn] Big Search! Screen: {sw}x{sh}, Template: {tw}x{th}")

        if sw < tw or sh < th:
            return False, 0.0, (0, 0), (tw, th)

        # 3. 匹配
        res = cv2.matchTemplate(p_screen, p_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= self.confidence:
            center_x = max_loc[0] + tw // 2
            center_y = max_loc[1] + th // 2
            return True, max_val, (center_x, center_y), (tw, th)

        return False, max_val, (0, 0), (tw, th)
