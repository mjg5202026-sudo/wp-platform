"""
日志工具模块。

统一管理日志输出（文件 + 控制台）。
不允许业务代码直接使用 print() 或 logging.basicConfig()。
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import LOGS_DIR, log_config


def setup_logger(
    name: str = "document-reader",
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    配置并返回命名日志记录器。

    Args:
        name: 日志记录器名称。
        level: 日志级别（默认取自 config.LogConfig）。
        log_file: 日志文件路径（默认自动生成在 LOGS_DIR）。

    Returns:
        配置好的 Logger 实例。
    """
    logger = logging.getLogger(name)

    # 避免重复配置
    if logger.handlers:
        return logger

    level = level or log_config.level
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt=log_config.format,
        datefmt=log_config.date_format,
        style="{",
    )

    # ── 控制台 Handler ──
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── 文件 Handler ──
    try:
        file_path = log_file or (LOGS_DIR / f"{name}.log")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(file_path),
            maxBytes=log_config.max_bytes,
            backupCount=log_config.backup_count,
            encoding=log_config.encoding,
            delay=True,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as e:
        logger.warning("无法创建日志文件: %s", e)

    return logger


def get_logger(name: str) -> logging.Logger:
    """获取已配置的日志记录器。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
