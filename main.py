import cv2
import numpy as np
import pyautogui
import time
import os
import ctypes
import pygetwindow as gw
import config

# --- Windows DPI 适配 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass

def get_window_rect(title):
    try:
        wins = gw.getWindowsWithTitle(title)
        if wins:
            win = wins[0]
            if win.isMinimized: win.restore()
            return (win.left, win.top, win.width, win.height)
    except:
        return None

def find_scaled_with_region(image_name, win_rect):
    img_path = os.path.join("assets", image_name)
    if not os.path.exists(img_path): return False

    # 1. 加载并根据 CURRENT_SCALE 缩放模板
    template = cv2.imread(img_path)
    if template is None: return False
    
    if config.CURRENT_SCALE != 1.0:
        new_w = int(template.shape[1] * config.CURRENT_SCALE)
        new_h = int(template.shape[0] * config.CURRENT_SCALE)
        template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    tpl_h, tpl_w = template.shape[:2]

    # 2. 确定搜索范围 (绝对坐标)
    win_x, win_y, win_w, win_h = win_rect
    rel_config = config.SEARCH_REGIONS.get(image_name)

    if rel_config:
        # 使用自定义 Region
        search_x = win_x + rel_config[0]
        search_y = win_y + rel_config[1]
        search_w, search_h = rel_config[2], rel_config[3]
    else:
        # 全窗口扫描
        search_x, search_y, search_w, search_h = win_x, win_y, win_w, win_h

    # 3. 截图并匹配
    try:
        # 安全保护：确保截图区域不小于模板
        if search_w < tpl_w or search_h < tpl_h:
            return False
            
        screen = pyautogui.screenshot(region=(search_x, search_y, search_w, search_h))
        screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    except:
        return False

    res = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= config.CONFIDENCE:
        # 计算在屏幕上的绝对中心点
        abs_center_x = max_loc[0] + tpl_w // 2 + search_x
        abs_center_y = max_loc[1] + tpl_h // 2 + search_y
        
        # 计算相对于窗口左上角的中心位置
        rel_to_win_x = abs_center_x - win_x
        rel_to_win_y = abs_center_y - win_y

        # --- 自动生成建议 Region (核心逻辑) ---
        # 宽度 = 模板宽 + 200, 高度 = 模板高 + 200
        # 左上角坐标 = 中心点 - (模板宽/2 + 100)
        suggest_w = tpl_w + 200
        suggest_h = tpl_h + 200
        suggest_rel_x = max(0, rel_to_win_x - (tpl_w // 2 + 100))
        suggest_rel_y = max(0, rel_to_win_y - (tpl_h // 2 + 100))

        print(f"\n[匹配成功] {image_name} | 置信度: {max_val:.2f}")
        print(f"建议填入 config.py 的配置:")
        print(f'"{image_name}": ({suggest_rel_x}, {suggest_rel_y}, {suggest_w}, {suggest_h}),')
        print("-" * 40)
        
        # 测试模式注释点击
        # pyautogui.click(abs_center_x, abs_center_y)
        return True
    
    return False

if __name__ == "__main__":
    print(f"=== 自动 Region 生成版脚本 ===")
    
    try:
        while True:
            rect = get_window_rect(config.WINDOW_TITLE)
            if rect:
                for btn in config.BUTTONS:
                    find_scaled_with_region(btn, rect)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n脚本停止")