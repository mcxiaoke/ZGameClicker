# Copilot instructions for GameClicker

Summary

- This repository is a Windows-focused automation "clicker" that captures a game window, runs
  template-matching using OpenCV, and issues mouse actions via `pyautogui`.

Quick architecture (big picture)

- `core/` — core runtime primitives:
    - `core/window.py`: `WindowManager` — finds and tracks the game window and HWND.
    - `core/vision.py`: `VisionEngine` — template loading (with cache) and `match()` supporting
      `color|gray|edge` modes.
    - `core/controller.py`: `GameController` — screenshot capture (MSS/pyautogui/optional BitBlt),
      matching orchestration, threaded `find_all()`, and click actions.
    - `core/logger_config.py` + `core/__init__.py`: global `DEBUG_MODE` detection (`--debug` / `-d`)
      and logger setup.
- `yggdra/` — bot-specific glue:
    - `yggdra/main.py`: orchestrates logic using `GameController`, reads `yggdra/assets_config.py`
      and `yggdra/config.py`.
    - `yggdra/assets_config.py`: canonical mapping of asset file names -> metadata (alias, type,
      click behavior).

Key developer workflows

- Install / run locally:
    - Requires Python >= 3.12 (see `pyproject.toml`).
    - Install dependencies in `pyproject.toml` (`mss`, `opencv-python`, `pyautogui`, `pywin32`
      etc.).
    - Run bot locally: `python -m yggdra.main` or `python yggdra/main.py`.
    - When installed (via packaging), an entry script `yggdra` is provided per `pyproject.toml`.
- Debugging:
    - Start with `--debug` or `-d` on command line to enable `DEBUG_MODE` (enables extra prints in
      `yggdra/main.py`).
    - `core/logger_config.setup_logger(debug_mode=True)` is used for more verbose logs.

Project-specific conventions and patterns

- Template matching:
    - Use `VisionEngine.match(screen, template, method="color"|"gray"|"edge")`.
    - `VisionEngine` caches loaded templates: modifying template files requires restarting the bot.
- Regions and coordinate system:
    - `yggdra/config.py` exposes `REGIONS` (window-relative `(x,y,w,h)`) used by `GameController` to
      restrict search areas for performance and stability.
    - `GameController` computes absolute screen coordinates by combining window rect (from
      `WindowManager`) + relative offsets.
- Capture methods:
    - Default capture uses `mss` (recommended). `bitblt` is optional and may cause title-bar offset
      issues; only enable when you understand Windows HWND offsets and have tested.
    - Switch at runtime via `GameController.set_capture_method("mss"|"pyautogui"|"bitblt")`.
- Concurrency:
    - `GameController.find_all()` runs matching tasks in a `ThreadPoolExecutor` (max_workers=8) to
      speed bulk searches. Keep CPU/IO implications in mind when changing workers.

Integration points & important files to inspect

- `pyproject.toml` — dependency and entry-point config.
- `core/controller.py` — capture / find / click orchestration (primary area to modify for behavior
  changes).
- `core/vision.py` — matching algorithms and confidence threshold logic.
- `yggdra/config.py` — window title, `ASSETS_DIR`, `SCALE`, `CONFIDENCE`, and `REGIONS` (tunable for
  each game resolution).
- `yggdra/assets_config.py` — asset list: keys are filenames (not full paths). Use these names when
  calling `find()`.

Common edits you may need to make (examples)

- To test a different matching mode for a single call:
    - `res = controller.find(screen_img, "btn.png", method="edge")`
- To increase sensitivity temporarily:
    - `controller.vision.confidence = 0.95` (set back after test).
- To force a different capture method at runtime:
    - `controller.set_capture_method("pyautogui")`

What AI agents should NOT change lightly

- Don't change BitBlt code unless you can test on the target Windows environment — BitBlt often
  needs header offset fixes.
- Avoid removing the `VisionEngine` cache behavior — tests depend on template re-use for
  performance.

If something is unclear or you need more detail (e.g., expected asset naming, window resolutions to
support, or test harnesses), ask and I will expand these instructions.

Logging notes

- Short-format logs are the project default: no timestamp and single-letter level tags
  (`[D]`,`[I]`,`[W]`,`[E]`).
- Import and use the shared logger via `from core import log` (preferred). Example:
  `log.info("message")`.
- Runtime toggle for datetime: call `from core import enable_datetime; enable_datetime(True)` to
  enable timestamped logs, or pass `show_datetime=True` to `core.logger_config.setup_logger()` at
  startup.
- Compatibility helpers: `from core import info, debug, warn, error` are available and resolve to
  the calling module's logger.

Files to check for logging behavior: [core/logger_config.py](core/logger_config.py),
[core/**init**.py](core/__init__.py), [yggdra/main.py](yggdra/main.py).
