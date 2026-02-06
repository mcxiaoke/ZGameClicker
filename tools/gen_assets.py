"""
Project: tools
Created: 2026-02-06 21:08:11
Modified: 2026-02-06 21:08:11
Author: mcxiaoke (github@mcxiaoke.com)
License: Apache License 2.0
"""

import os
import sys
import ast


def format_name(filename):
    """battle_start.png -> Battle Start"""
    name = os.path.splitext(filename)[0]
    return name.replace("_", " ").title()


def run_gen(game_name):
    # --- 1. 路径定义 ---
    assets_dir = os.path.join("assets", game_name)
    output_dir = game_name
    output_file = os.path.join(output_dir, "assets_config.py")

    if not os.path.exists(assets_dir):
        print(f"[Error] Assets dir not found: {assets_dir}")
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- 2. 扫描文件系统 ---
    # 获取所有 .png 文件名
    real_files = set(f for f in os.listdir(assets_dir) if f.endswith(".png"))

    # --- 3. 解析旧配置 ---
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                # 提取 ASSETS = {...} 的部分
                start_index = content.find("ASSETS = {")
                if start_index != -1:
                    dict_str = content[start_index + 9 :]  # 跳过 "ASSETS = "
                    # 使用 ast.literal_eval 安全解析 Python 字典字符串
                    existing_data = ast.literal_eval(dict_str)
        except Exception as e:
            print(f"[Warn] Failed to parse existing config: {e}")

    # --- 4. 合并与逻辑处理 ---
    new_data = {}

    # A. 处理真实存在的文件
    for filename in sorted(list(real_files)):
        if filename in existing_data:
            # 旧文件：保留所有原有字段
            item = existing_data[filename]
            # 如果之前标记了 404，现在文件回来了，去掉 404 标记
            if "(404)" in item.get("desc", ""):
                item["desc"] = item["desc"].replace("(404 File Missing)", "").strip()
            new_data[filename] = item
        else:
            # 新文件：生成默认模板
            print(f"[New] Found: {filename}")
            new_data[filename] = {
                "name": format_name(filename),  # 自动生成可读名字
                "desc": "",  # 留给你手动写
                "type": "button",  # 默认为按钮
                "click": "single",  # 默认单击
            }

    # B. 处理文件已丢失的配置 (404 逻辑)
    for key, item in existing_data.items():
        if key not in real_files:
            # 文件不在了，但配置还在
            # 标记 desc 为 404，保留条目以防是误删
            current_desc = item.get("desc", "")
            if "(404)" not in current_desc:
                item["desc"] = f"(404 File Missing) {current_desc}"
            new_data[key] = item
            print(f"[Missing] Marked as 404: {key}")

    # --- 5. 生成代码文件 ---
    lines = []
    lines.append(f"# Auto-generated config for {game_name}")
    lines.append("# You can edit 'name', 'desc', 'type', 'click'. Do not change keys.")
    lines.append("ASSETS = {")

    # 自定义格式化输出，保持整洁
    for key in sorted(new_data.keys()):
        val = new_data[key]
        # 404 的条目排在最后或是加注释？这里直接按字母序排

        # 构造 value 字符串
        val_str = (
            f'{{"name": "{val["name"]}", '
            f'"desc": "{val["desc"]}", '
            f'"type": "{val.get("type", "button")}", '
            f'"click": "{val.get("click", "single")}"}}'
        )
        lines.append(f'    "{key}": {val_str},')

    lines.append("}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[Success] Updated {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/gen_assets.py <game_name>")
    else:
        run_gen(sys.argv[1])
