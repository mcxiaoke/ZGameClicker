# GameClicker

## 项目简介

GameClicker 是一个面向 Windows 的游戏自动化框架。它通过截取游戏窗口、使用 OpenCV 模板匹配检测界面元素，并通过
`pyautogui` 执行鼠标操作以实现自动化脚本。仓库中包含一个示例子项目
`yggdra`（为 YGGDRA 游戏实现的脚本），以后可以添加更多游戏的子实现。

## 架构概览

- `core/`：核心运行时与工具
    - `core/window.py`：`WindowManager`，负责查找/跟踪目标窗口与 HWND（包括 DPI 处理、最小化恢复）。
    - `core/vision.py`：`VisionEngine`，模板加载（带缓存）、三种匹配模式（`color`、`gray`、`edge`）以及置信度阈值逻辑。
    - `core/controller.py`：`GameController`，负责截图（`mss`/`pyautogui`/可选
      `BitBlt`）、区域裁剪、并行匹配 (`find_all`)、点击封装等。
    - `core/logger_config.py`：统一日志配置，提供 `from core import log`、`debug/info/warn/error`
      等接口；默认短格式（无时间戳），可运行时开启时间戳。
- `yggdra/`：示例游戏实现
    - `yggdra/main.py`：业务逻辑示例，使用 `GameController`、读取 `yggdra/assets_config.py` 与
      `yggdra/config.py`。
    - `yggdra/assets_config.py`：资源到元数据的映射（文件名 -> name/desc/type/click）。

## 运行与依赖

- 要求：Python >= 3.12（详见 `pyproject.toml`）。
- 依赖示例（在 `pyproject.toml` 中）：`mss`, `opencv-python`, `pillow`, `pyautogui`, `pywin32` 等。
- 运行示例（开发）：

```
python -m yggdra.main
```

或仓库安装后可使用包入口 `yggdra`（参见 `pyproject.toml` 的 `scripts`）。

## 调试与日志

- 启用 debug 模式：在启动命令中加入 `--debug` 或 `-d`，项目会在 `core`
  初始化阶段将根日志级别设置为 DEBUG。
- 日志系统：默认短格式（例如 `[D] yggdra.main: message`），级别使用单字母标签 `[D]/[I]/[W]/[E]`。
- 若需包含时间戳：
    - 启动时传入 `show_datetime=True` 给 `core.logger_config.setup_logger()`，或
    - 运行时切换：

```
from core import enable_datetime
enable_datetime(True)
```

## 主要配置点

- `yggdra/config.py`：包含 `WINDOW_TITLE`, `ASSETS_DIR`, `SCALE`, `CONFIDENCE`,
  `REGIONS`（窗口相对区域）。
    - `REGIONS` 用于限制模板匹配的搜索区域以提高性能与稳定性，格式 `(x, y, w, h)`。
- 资源目录：`assets/<game>/` 存放模板图片（PNG），`yggdra/assets_config.py`
  列出资产及其元数据键（文件名作为 key）。

## 捕获方法说明

- `mss`（默认、推荐）：跨屏幕稳定，返回 BGRA，需要剔除 alpha 通道。
- `pyautogui`：可作为备用截屏方法，返回 RGB（需转换为 BGR）。
- `BitBlt`：可选，可能产生标题栏偏移（需要在目标 Windows 环境中验证），不建议随意启用。

## 视觉/匹配说明

- `VisionEngine.load_template(path)`：带缓存，修改模板后需要重启进程以刷新缓存。
- `VisionEngine.match(screen, template, method)`：三种模式：`color`（默认）、`gray`（灰度增强）、`edge`（Canny 边缘）。
- 置信度阈值：`VisionEngine.confidence` 控制命中阈值，`GameController.find()`
  支持为单次调用临时覆盖阈值。

## 控制器接口要点

- `GameController(window_title, assets_dir, scale, exact_match, method)`：构造并设置截图/匹配行为。
- `set_regions(regions_dict)`：注入 `REGIONS`，键为文件名（例如 `"battle_start.png"`）。
- `set_capture_method(method)`：在运行时切换截屏方法：`"mss"|"pyautogui"|"bitblt"`。
- `capture_window()`：截取当前窗口返回 OpenCV BGR 图像。
- `find(screen_img, image_name, threshold=None, method="color")`：在图像中查找单一模板，返回
  `{name,pos,confidence}`。
- `find_all(screen_img, image_names, threshold=None, method="color")`：并行批量查找，返回结果列表。
- `click(target, offset=(0,0))`：根据 `find()` 的返回或坐标进行点击。

## 扩展与添加新游戏

- 添加新游戏实现：复制 `yggdra` 目录为新子项目（例如 `mygame/`），实现 `main.py` 负责业务决策，提供
  `config.py` 与 `assets_config.py`。
- 资产生成辅助：使用 `tools/gen_assets.py <game_name>` 扫描 `assets/<game_name>` 并生成
  `assets_config.py`。

## 调试技巧与常见问题

- 坐标偏差常见原因：DPI 缩放、BitBlt 标题栏偏移、错误的 `REGIONS`。优先使用 `mss`
  并启用 DPI 适配（`core` 模块已尝试设置）。
- 若模板匹配失败：尝试 `method='edge'` 或调节 `VisionEngine.confidence`，或扩大 `REGIONS`。

## 许可证与贡献

此项目使用 Apache-2.0 风格许可（请参考仓库 LICENSE，如无则联系作者）。欢迎提交 issue 或 PR，添加新游戏实现或改进匹配策略。
