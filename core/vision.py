'''
Project: core
Created: 2026-02-06 16:13:33
Modified: 2026-02-06 16:13:33
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
'''

# core/vision.py
import cv2
import numpy as np
import os

class VisionEngine:
    def __init__(self, scale=1.0, confidence=0.8):
        self.scale = scale
        self.confidence = confidence

    def load_template(self, path):
        """加载模板并根据 scale 缩放"""
        if not os.path.exists(path):
            print(f"[Vision] File not found: {path}")
            return None
            
        img = cv2.imread(path)
        if img is None: return None

        if self.scale != 1.0:
            w = int(img.shape[1] * self.scale)
            h = int(img.shape[0] * self.scale)
            img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        
        return img

    def preprocess(self, img, method="gray"):
        """图像预处理：支持 gray (灰度增强) 或 edge (Canny边缘)"""
        if method == "edge":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            return cv2.Canny(blurred, 50, 150)
        
        # 默认灰度增强 (gray)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 对比度增强: alpha=1.2
        return cv2.convertScaleAbs(gray, alpha=1.2, beta=0)

    def match(self, screen_img, template_img):
        """
        核心匹配逻辑
        :return: (matched: bool, max_val: float, center: tuple, dimensions: tuple)
        """
        # 1. 预处理
        # 这里默认用 gray，你可以根据需要在参数里透传 method
        p_screen = self.preprocess(screen_img)
        p_template = self.preprocess(template_img)

        # 2. 尺寸检查
        th, tw = p_template.shape[:2]
        sh, sw = p_screen.shape[:2]
        if sw < tw or sh < th:
            return False, 0.0, (0,0), (tw, th)

        # 3. 匹配
        res = cv2.matchTemplate(p_screen, p_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= self.confidence:
            center_x = max_loc[0] + tw // 2
            center_y = max_loc[1] + th // 2
            return True, max_val, (center_x, center_y), (tw, th)
        
        return False, max_val, (0,0), (tw, th)