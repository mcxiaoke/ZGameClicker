import cv2
import numpy as np
import pyautogui
import time
import os
import ctypes

# --- 配置区 ---
CURRENT_SCALE = 0.8  
BUTTONS = ["battle_prepare.png", "next_chapter.png", "battle_start.png", "close.png", "again.png", "back.png"]

# 定义搜索区域 (x, y, width, height)
# 如果不确定坐标，可以先填 None，脚本会自动全屏搜索
# 示例：{"close.png": (1500, 0, 420, 300)} 仅在屏幕右上角找关闭按钮
SEARCH_REGIONS = {
    "close.png": None,          # 暂时全屏
    "battle_prepare.png": None, 
}

# 修复 Windows 缩放坐标偏移
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass

def find_and_click_scaled(image_name, scale=1.0, confidence=0.8):
    img_path = os.path.join("assets", image_name)
    if not os.path.exists(img_path):
        return False

    template = cv2.imread(img_path)
    if template is None:
        print(f"[错误] 无法解析图片: {img_path}")
        return False

    # 1. 确定搜索区域
    region = SEARCH_REGIONS.get(image_name)
    
    # 2. 截图
    # 如果指定了 region，pyautogui 截图会非常快
    screen = pyautogui.screenshot(region=region)
    screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    # 3. 缩放处理模板
    if scale != 1.0:
        new_w = int(template.shape[1] * scale)
        new_h = int(template.shape[0] * scale)
        template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    h, w = template.shape[:2]

    # 4. 模板匹配
    res = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= confidence:
        # 如果使用了 region，最终坐标需要加上 region 的偏移量
        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0
        
        center_x = max_loc[0] + w // 2 + offset_x
        center_y = max_loc[1] + h // 2 + offset_y
        
        print(f"[匹配成功] {image_name.ljust(20)} | 置信度: {max_val:.2f} | 目标坐标: ({center_x}, {center_y})")
        
        # 测试阶段注释掉点击
        # pyautogui.click(center_x, center_y)
        return True
    
    return False

if __name__ == "__main__":
    print(f"=== 测试模式启动 (已禁用点击) ===")
    print(f"当前缩放率: {CURRENT_SCALE}")
    time.sleep(2)
    
    try:
        while True:
            for btn in BUTTONS:
                find_and_click_scaled(btn, scale=CURRENT_SCALE)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n已停止")