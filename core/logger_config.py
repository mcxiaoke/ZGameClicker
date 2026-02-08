"""
Project: core
Created: 2026-02-06
Author: mcxiaoke
License: Apache License 2.0
"""

import logging
import sys
import inspect
from typing import Optional

# 初始化日志配置
SHOW_DATETIME = True


def setup_logger(debug_mode: bool = False):
    """
    配置日志格式和级别
    :param debug_mode: True 显示DEBUG及以上日志，False 只显示INFO及以上
    """
    # 根据开关选择日志格式
    if SHOW_DATETIME:
        # 包含日期时间
        log_format = "%(asctime)s|%(levelname).1s %(name)s: %(message)s"
        date_format = "%H:%M:%S"
    else:
        # 不包含日期时间，级别使用首字母缩写
        log_format = "[%(levelname).1s] %(name)s: %(message)s"

    # 设置根日志级别
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    # 清除已存在的处理器（避免重复输出）
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    if SHOW_DATETIME:
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
    else:
        console_handler.setFormatter(logging.Formatter(log_format))

    # 友好模块名过滤器：当记录的 logger 名不具信息量时，使用 pathname 计算更友好的模块名
    import os

    class FriendlyNameFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            try:
                name = record.name
                # 如果记录的名字是内置或 logger_config，自行映射为文件相对路径的模块名
                if name in ("core.logger_config", "__main__") or name.startswith(
                    "core.logger_config"
                ):
                    pathname = getattr(record, "pathname", None)
                    if pathname:
                        try:
                            rel = os.path.relpath(pathname, start=os.getcwd())
                        except Exception:
                            rel = os.path.basename(pathname)
                        modname = rel.replace(os.sep, ".")
                        if modname.endswith(".py"):
                            modname = modname[:-3]
                        record.name = modname
            except Exception:
                pass
            return True

    console_handler.addFilter(FriendlyNameFilter())
    root_logger.addHandler(console_handler)


class _ProxyLogger:
    """A lightweight proxy that resolves the real logger based on caller module.

    Usage: import from core import log; call log.info(...)
    The proxy will dispatch to logging.getLogger(caller_module).
    """

    def __getattr__(self, name: str):
        # stack[1] is the caller of the proxy attribute access
        stack = inspect.stack()
        try:
            caller_frame = stack[1].frame
            module_name = caller_frame.f_globals.get("__name__", "")
        finally:
            # avoid reference cycles
            del stack

        real_logger = logging.getLogger(module_name)
        return getattr(real_logger, name)


# 导出一个 proxy logger，供外部统一导入使用
log = _ProxyLogger()


# 兼容导出：提供方便的函数形式（如果代码直接从 logger_config 导入 debug/info）
def _caller_logger():
    stack = inspect.stack()
    try:
        # stack[0] == _caller_logger, stack[1] == wrapper (debug/info), stack[2] == original caller
        caller_index = 2 if len(stack) > 2 else 1
        caller_frame = stack[caller_index].frame
        module_name = caller_frame.f_globals.get("__name__", "")
    finally:
        del stack
    return logging.getLogger(module_name)


def debug(msg, *args, **kwargs):
    _caller_logger().debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    _caller_logger().info(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    _caller_logger().warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    _caller_logger().error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    _caller_logger().critical(msg, *args, **kwargs)
